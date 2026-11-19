// Run with node --expose-gc after baking the district .bvh files.
import fs from "node:fs";
import path from "node:path";
import { performance } from "node:perf_hooks";
import { Box3, Ray, Sphere, Triangle, Vector3 } from "three";
import { Octree } from "three/examples/jsm/math/Octree.js";
import { Capsule } from "three/examples/jsm/math/Capsule.js";
import { loadCollision } from "./collision.js";

function reference(buffer) {
  const words = new Float32Array(buffer);
  let cursor = 0;
  function vector() {
    const v = new Vector3().fromArray(words, cursor);
    cursor += 3;
    return v;
  }
  function branch() {
    const node = new Octree(new Box3(vector(), vector()));
    const count = words[cursor++];
    if (count === 0) node.subTrees.push(branch(), branch());
    else for (let i = 0; i < count; i++) node.triangles.push(new Triangle(vector(), vector(), vector()));
    return node;
  }
  const root = new Octree();
  root.subTrees.push(branch());
  return root;
}
function measure(build, buffer) {
  global.gc();
  const heap = process.memoryUsage().heapUsed,
    start = performance.now();
  const world = build(buffer),
    ms = performance.now() - start;
  global.gc();
  return { world, ms, heap: process.memoryUsage().heapUsed - heap };
}
let seed = 74011;
function random() {
  seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
  return seed / 4294967296;
}
function compare(key, old, packed, metric) {
  if (!!old !== !!packed || (old && Math.abs(old[metric] - packed[metric]) > 0.000001))
    throw Error(key + " " + metric + " result differs");
  if (old && (old.normal || old.position).distanceTo(packed.normal || packed.position) > 0.000001)
    throw Error(key + " hit vector differs");
}
const report = [];
for (const file of process.argv.slice(2)) {
  const bin = fs.readFileSync(file),
    buffer = bin.buffer.slice(bin.byteOffset, bin.byteOffset + bin.byteLength);
  const baseline = measure(reference, buffer),
    candidate = measure(loadCollision, buffer);
  const key = path.basename(file, ".bvh");
  const box = baseline.world.subTrees[0].box;
  const width = Math.min(60, Math.max(20, (box.max.x - box.min.x) / 2 - 1));
  const counts = { capsule: 0, sphere: 0, ray: 0 };
  let visibilityQueries = 0;
  for (let i = 0; i < 768; i++) {
    const p = new Vector3((2 * random() - 1) * width, random() * 3, (2 * random() - 1) * width);
    const direction = new Vector3(random() - 0.5, i % 2 ? -1 : random() - 0.5, random() - 0.5).normalize();
    const ray = new Ray(p, direction),
      sphere = new Sphere(p, 0.16 + random() * 0.35);
    const cap = new Capsule(p, p.clone().add(new Vector3(0, 1.18, 0)), 0.25);
    const a = baseline.world.rayIntersect(ray),
      b = candidate.world.rayIntersect(ray);
    compare(key, a, b, "distance");
    const cutoff = random() * 12;
    compare(
      key,
      a && a.distance <= cutoff ? a : false,
      candidate.world.rayIntersect(ray, cutoff),
      "distance",
    );
    const limits = [0, cutoff, Infinity];
    if (a) limits.push(a.distance, a.distance + 1e-7, a.distance - 1e-7);
    for (const limit of limits) {
      const expected = !!a && a.distance < limit;
      if (candidate.world.rayBlocked(ray, limit) !== expected)
        throw Error(key + " wall visibility differs at " + limit);
      visibilityQueries++;
    }
    const s = baseline.world.sphereIntersect(sphere),
      c = baseline.world.capsuleIntersect(cap);
    compare(key, s, candidate.world.sphereIntersect(sphere), "depth");
    compare(key, c, candidate.world.capsuleIntersect(cap), "depth");
    if (a) counts.ray++;
    if (s) counts.sphere++;
    if (c) counts.capsule++;
  }
  report.push({
    room: key,
    queries: 3072,
    visibilityQueries,
    hits: counts,
    packedBytes: buffer.byteLength,
    referenceHeap: baseline.heap,
    packedHeap: candidate.heap,
    referenceLoadMs: baseline.ms,
    packedLoadMs: candidate.ms,
  });
  baseline.world.clear();
  candidate.world.clear();
}
console.log(JSON.stringify(report, null, 2));
