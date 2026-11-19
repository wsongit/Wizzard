import { Vector3 } from "three";

// A hand must withdraw beyond the sounding surface before the next stroke.
// Use the swept segment so a fast hand cannot pass through a bell between frames.
export class PalmInstruments {
  constructor() {
    this.previous = [new Vector3(), new Vector3()];
    this.valid = [false, false];
    this.targets = [];
    this.stroke = new Vector3();
    this.offset = new Vector3();
  }

  bind(nodes) {
    this.targets = [];
    this.valid.fill(false);
    for (const key of Object.keys(nodes)) {
      if (!key.startsWith("Hit_")) continue;
      const id = key.slice(4), centre = nodes[key].position;
      this.targets.push({ id: "A_" + id, centre,
        radius: centre.distanceTo(nodes["Edge_" + id].position), armed: [false, false] });
    }
    this.last = "";
  }

  strike(hand, point) {
    if (!point || !this.targets.length) {
      this.valid[hand] = false;
      return null;
    }
    const from = this.previous[hand], stroke = this.stroke.subVectors(point, from);
    const length2 = stroke.lengthSq(), continuous = this.valid[hand] && length2 > 1e-9 && length2 < 1;
    let hit = null;
    for (const target of this.targets) {
      const { centre, radius, armed } = target;
      if (!this.valid[hand] || length2 >= 1) armed[hand] = false;
      if (continuous && armed[hand]) {
        const t = Math.min(1, Math.max(0, this.offset.subVectors(centre, from).dot(stroke) / length2));
        if (this.offset.copy(from).addScaledVector(stroke, t).distanceToSquared(centre) <= radius * radius) {
          hit = target.id;
          armed[hand] = false;
        }
      }
      if (point.distanceToSquared(centre) > (radius + .14) ** 2) armed[hand] = true;
    }
    from.copy(point);
    this.valid[hand] = true;
    return hit;
  }

  accepts(id, time) {
    if (id === this.last && time - this.at < 170) return false;
    this.last = id;
    this.at = time;
    return true;
  }
}
