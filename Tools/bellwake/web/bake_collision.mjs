// Bake the collision hierarchy once during packaging, using the exported Blender geometry.
import fs from "node:fs";
import { Group, Vector3, Box3 } from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { Octree } from "three/examples/jsm/math/Octree.js";
globalThis.self = globalThis;
const names = ["Terrain", "Rim", "Set", "C_Solids"];

for (const file of process.argv.slice(2)) {
  const buf = fs.readFileSync(file), length = buf.readUInt32LE(12);
  const gltf = JSON.parse(buf.toString("utf8", 20, 20 + length));
  delete gltf.materials; delete gltf.images; delete gltf.textures;
  for (const mesh of gltf.meshes)
    for (const prim of mesh.primitives) delete prim.material;
  const header = Buffer.from(JSON.stringify(gltf));
  const padded = (header.length + 3) & ~3;
  const blob = Buffer.concat([buf.subarray(0,20),header,Buffer.alloc(padded-header.length,32),buf.subarray(20+length)]);
  blob.writeUInt32LE(padded,12);
  blob.writeUInt32LE(blob.length,8);
  const scene = (await new GLTFLoader().parseAsync(blob.buffer.slice(blob.byteOffset,blob.byteOffset+blob.length),"")).scene;
  const solids = new Group();
  scene.updateMatrixWorld(true);
  for (const key of names) solids.attach(scene.getObjectByName(key));

  const out = [];
  class Baker extends Octree {
    build() {
      const centres = new Map();
      for (const t of this.triangles) centres.set(t,t.getMidpoint(new Vector3()));
      const split = (tris) => {
        const box = new Box3(), spread = new Box3();
        for (const t of tris) {
          box.expandByPoint(t.a).expandByPoint(t.b).expandByPoint(t.c);
          spread.expandByPoint(centres.get(t));
        }
        out.push(...box.min.toArray(),...box.max.toArray());
        if (tris.length<=12) {
          out.push(tris.length);
          for(const t of tris) out.push(...t.a.toArray(),...t.b.toArray(),...t.c.toArray());
        } else {
          out.push(0);
          const d=spread.getSize(new Vector3()), axis=d.x>d.y && d.x>d.z?"x":d.y>d.z?"y":"z";
          tris.sort((a,b)=>centres.get(a)[axis]-centres.get(b)[axis]);
          const mid=tris.length>>1;
          split(tris.slice(0,mid)); split(tris.slice(mid));
        }
      };
      split(this.triangles);
    }
  }
  new Baker().fromGraphNode(solids);
  fs.writeFileSync(file.replace(/\.glb$/, ".bvh"), new Uint8Array(Float32Array.from(out).buffer));
}
