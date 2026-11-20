// Run from the baked project with node Tools/bellwake/web/standing_check.mjs.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { Ray, Vector3 } from "three";
import { Capsule } from "three/examples/jsm/math/Capsule.js";
import { loadCollision, separateBody } from "./collision.js";
import { TrackedRunner } from "./vr.js";

const down = new Vector3(0, -1, 0);
const normal = new Vector3();
const motion = new Vector3();
const scenes = [
  ["Bellmarket", -11.95, -10.43], // In front of the painted shop window.
  ["Wrenfall", -4.8, -2.4],
  ["RootChoir", 7, 4],
  ["Glasscut", -19, 8], // Shared edge between sloping terrain triangles.
  ["SillwaterEbb", 30, -16.5],
];

for (const [scene, x, z] of scenes) {
  const data = readFileSync(new URL("../.web-assets/" + scene + ".bvh", import.meta.url));
  const tree = loadCollision(data.buffer.slice(data.byteOffset, data.byteOffset + data.byteLength));
  const floor = tree.rayIntersect(new Ray(new Vector3(x, 10, z), down), 20);
  assert.ok(floor && floor.triangle.getNormal(normal).y > 0.65, scene + " needs a walkable test point");
  for (const mode of ["desktop", "VR"]) {
    const tracked = mode === "VR";
    const radius = tracked ? 0.23 : 0.26;
    for (const hz of [36, 72, 90]) {
      const dt = 1 / hz;
      const bottom = new Vector3(x, floor.position.y + radius + 0.22, z);
      const body = new Capsule(bottom, bottom.clone().add(new Vector3(0, 1.1, 0)), radius);
      const runner = { body, step: new Vector3() };
      let speed = 0;
      for (let frame = 0; frame < hz * 120; frame++) {
        speed -= (tracked ? 11 : 12) * dt;
        const before = body.start.y;
        motion.set(0, speed * dt, 0);
        if (tracked) {
          TrackedRunner.prototype.sweep.call(runner, tree, motion, true);
          if (body.start.y - before > motion.y + 0.001) speed = -0.5;
        } else {
          body.translate(motion);
          const hit = tree.capsuleIntersect(body);
          if (hit) {
            separateBody(body, hit, true);
            if (hit.normal.y > 0) speed = 0;
          }
        }
      }
      assert.ok(Math.hypot(body.start.x - x, body.start.z - z) < 0.001, scene + " idle drift on " + mode);
      assert.ok(Math.abs(body.start.y - floor.position.y - radius) < 0.1, scene + " lost floor support");
    }
  }
}

// Wall contacts and deliberately pushing off a slope keep the full contact normal.
for (const [settling, ny, expectedX] of [[true, 0, 0.2], [true, 0.6, 0.16], [false, 0.8, 0.12], [true, 0.8, 0]]) {
  const body = new Capsule(new Vector3(), new Vector3(0, 1, 0), 0.26);
  const hit = { normal: new Vector3(Math.sqrt(1 - ny * ny), ny, 0), depth: 0.2 };
  separateBody(body, hit, settling);
  assert.ok(Math.abs(body.start.x - expectedX) < 1e-7);
  assert.ok(Math.abs(body.start.dot(hit.normal) - hit.depth) < 1e-7);
  assert.ok(Math.abs(body.end.y - body.start.y - 1) < 1e-7);
}
console.log("Passed 30 two-minute idle runs, wall, steep slope and active push.");
