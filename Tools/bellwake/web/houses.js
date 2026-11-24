import * as T from "three";
import { Octree } from "three/examples/jsm/math/Octree.js";
import { mergeGeometries } from "three/examples/jsm/utils/BufferGeometryUtils.js";

const note = new T.Vector3(0, 1.12, -2.5),
  exit = new T.Vector3(0, 1.24, 3.27);
export const houseSpawn = new T.Vector3(0, 0.06, 1.95);

function panel(point, normal, width, height, cell, columns, rows) {
  const g = new T.PlaneGeometry(width, height);
  const uv = g.attributes.uv;
  for (let i = 0; i < uv.count; i++) {
    const x = ((cell % columns) + 0.025 + 0.95 * uv.getX(i)) / columns;
    const y =
      1 - (Math.floor(cell / columns) + 0.975 - 0.95 * uv.getY(i)) / rows;
    uv.setXY(i, x, y);
  }
  g.rotateY(Math.atan2(normal.x, normal.z));
  g.translate(point.x, point.y, point.z);
  return g;
}
export class HouseVisits {
  constructor(data, scene) {
    this.data = data;
    this.scene = scene;
    this.addresses = [];
    this.boards = new T.Group();
    scene.add(this.boards);
    this.ray = new T.Ray();
    this.delta = new T.Vector3();
  }
  async texture(key) {
    const path = this.data.houseImages[key];
    const url = this.data.streamed ? path : "data:image/png;base64," + path;
    const map = await new T.TextureLoader().loadAsync(url);
    map.colorSpace = T.SRGBColorSpace;
    map.anisotropy = 2;
    return new T.MeshBasicMaterial({
      map,
      side: T.DoubleSide,
      toneMapped: false,
    });
  }
  clearBoards() {
    for (const o of [...this.boards.children]) {
      o.geometry.dispose();
      o.material.map.dispose();
      o.material.dispose();
      this.boards.remove(o);
    }
    this.addresses = [];
  }
  async district(key) {
    this.clearBoards();
    const district = this.data.houses.districts.find(
      (d) => d.key === (key === "Highroad" ? "HighroadBrowser" : key),
    );
    if (!district) return;
    this.addresses = district.doors.map((d) => ({
      ...d,
      p: new T.Vector3(...d.point),
      n: new T.Vector3(...d.normal),
    }));
    const signs = [],
      wood = [],
      rows =
        2 ** Math.ceil(Math.log2(Math.ceil(this.data.houses.signs.length / 4)));
    for (const d of this.addresses) {
      if (d.millPassage) {
        const stone = d.p.clone().addScaledVector(d.n, -0.035);
        wood.push(panel(stone, d.n, 2.25, 2.18, 3, 8, 4));
        stone.y += 1.22;
        wood.push(panel(stone, d.n, 2.52, 0.32, 16, 8, 4));
        stone.y += 0.25;
        wood.push(panel(stone, d.n, 2.26, 0.22, 3, 8, 4));
      }
      if (d.paintDoor) wood.push(panel(d.p, d.n, 1.16, 2.09, 22, 8, 4));
      if (d.sign < 0) continue;
      const p = d.p.clone().addScaledVector(d.n, d.openSpace ? 0.065 : 0.24);
      p.y += d.openSpace ? 0.54 : 1.56;
      if (d.openSpace) {
        const post = p.clone();
        post.y -= 0.92;
        wood.push(panel(post, d.n, 0.18, 1.9, 1, 8, 4));
      }
      signs.push(panel(p, d.n, 1.86, 0.81, d.sign, 4, rows));
    }
    for (const [pieces, key] of [
      [wood, "room"],
      [signs, "signs"],
    ]) {
      if (!pieces.length) continue;
      const g = mergeGeometries(pieces);
      pieces.forEach((p) => p.dispose());
      this.boards.add(new T.Mesh(g, await this.texture(key)));
    }
  }
  target(origin, forward, tree) {
    let best = null,
      score = -Infinity;
    for (const d of this.addresses) {
      this.delta.copy(d.p).sub(origin);
      const distance = this.delta.length();
      if (distance > 3.25 || distance < 0.01 || this.delta.dot(d.n) > 0.18)
        continue;
      const alignment = this.delta.multiplyScalar(1 / distance).dot(forward);
      if (alignment < 0.71 || alignment - distance * 0.035 <= score) continue;
      this.ray.set(origin, this.delta);
      if (tree.rayBlocked(this.ray, Math.max(0, distance - 0.48))) continue;
      best = d;
      score = alignment - distance * 0.035;
    }
    return best;
  }
  async enter(d) {
    const path = this.data.houseRooms[d.layout];
    let room;
    if (this.data.streamed) {
      const res = await fetch(path);
      if (!res.ok) throw Error("Could not load " + d.layout);
      room = await res.json();
    } else room = JSON.parse(atob(path));
    const m = await this.texture("room");
    m.vertexColors = true;
    const g = new T.BufferGeometry();
    g.setAttribute("position", new T.Float32BufferAttribute(room.pos, 3));
    g.setAttribute("uv", new T.Float32BufferAttribute(room.uv, 2));
    g.setAttribute(
      "color",
      new T.Float32BufferAttribute(
        room.light.flatMap((l) => [l, l, l]),
        3,
      ),
    );
    g.setIndex(room.indices);
    this.shell = new T.Mesh(g, m);
    this.scene.add(this.shell);
    this.collision = new Octree().fromGraphNode(this.shell);
    this.collision.rayBlocked = (ray, range) => {
      const hit = this.collision.rayIntersect(ray);
      return hit && hit.distance <= range;
    };
    this.active = d;
    this.reading = false;
    this.boards.visible = false;
  }
  indoorTarget(p, forward) {
    for (const [name, at] of [
      ["exit", exit],
      ["note", note],
    ]) {
      this.delta.copy(at).sub(p);
      const len = this.delta.length();
      if (len < 2.85 && this.delta.normalize().dot(forward) > 0.55) return name;
    }
    return "";
  }
  leave() {
    this.scene.remove(this.shell);
    this.shell.geometry.dispose();
    this.shell.material.map.dispose();
    this.shell.material.dispose();
    this.collision = null;
    this.shell = null;
    this.active = null;
    this.reading = false;
    this.boards.visible = true;
  }
}
