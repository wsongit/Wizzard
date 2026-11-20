import { Vector3, Triangle } from "three";
import { Octree } from "three/examples/jsm/math/Octree.js";

// A downward step into a walkable slope can be resolved vertically. A push
// along the contact normal alone nudges an idle player downhill every frame.
export function separateBody(body, hit, settling) {
  if (settling && hit.normal.y >= 0.65) {
    const rise = hit.depth / hit.normal.y;
    body.start.y += rise;
    body.end.y += rise;
  } else {
    body.start.addScaledVector(hit.normal, hit.depth);
    body.end.addScaledVector(hit.normal, hit.depth);
  }
}

// Bounds and triangles stay in the room's packed buffer. Three.js supplies the same
// narrow-phase response used by the palms and body. Only nearby faces become objects.
class PackedCollision extends Octree {
  constructor(buffer) {
    super();
    this.words = new Float32Array(buffer);
    this.pool = [];
    this.face = new Triangle();
    this.hit = new Vector3();
    this.contactNormal = new Vector3();
    this.contactPoint = new Vector3();
    if (this.indexBranch(0, 0) !== this.words.length) throw Error("Invalid room collision data");
  }

  indexBranch(start, depth) {
    const words = this.words,
      count = words[start + 6];
    if (depth > 64 || !Number.isInteger(count) || count > 12) throw Error("Invalid collision node");
    if (count > 0) {
      const end = start + 7 + 9 * count;
      if (end > words.length) throw Error("Truncated collision leaf");
      return end;
    }
    const right = this.indexBranch(start + 7, depth + 1);
    const end = this.indexBranch(right, depth + 1);
    // Internal nodes originally store zero. Cache their skip distance in the same word.
    words[start + 6] = start - end;
    return end;
  }

  visit(shape, leaf, radius = Infinity) {
    const words = this.words,
      bounds = this.bounds;
    let cursor = 0;
    while (cursor < words.length) {
      bounds.min.fromArray(words, cursor);
      bounds.max.fromArray(words, cursor + 3);
      const count = words[cursor + 6];
      const next = count < 0 ? cursor - count : cursor + 7 + count * 9;
      if (
        (radius !== Infinity && bounds.distanceToPoint(shape.origin) > radius) ||
        !shape.intersectsBox(bounds)
      ) {
        cursor = next;
      } else if (count < 0) {
        cursor += 7;
      } else {
        if (leaf(cursor + 7, next)) return true;
        cursor = next;
      }
    }
    return false;
  }

  readFace(offset, face) {
    face.a.fromArray(this.words, offset);
    face.b.fromArray(this.words, offset + 3);
    face.c.fromArray(this.words, offset + 6);
    return face;
  }

  collect(shape, faces) {
    this.visit(shape, (start, end) => {
      for (let i = start; i < end; i += 9) {
        const slot = faces.length;
        if (slot === this.pool.length) this.pool.push(new Triangle());
        faces.push(this.readFace(i, this.pool[slot]));
      }
    });
  }

  getSphereTriangles(sphere, faces) {
    this.collect(sphere, faces);
  }
  getCapsuleTriangles(capsule, faces) {
    this.collect(capsule, faces);
  }
  triangleCapsuleIntersect(capsule, triangle) {
    // On a sloping mesh the capsule's bottom hemisphere can touch a shared
    // edge before its axis projects inside either face. Use the closest
    // point on the triangle so the foot has continuous support at that seam.
    const normal = triangle.getNormal(this.contactNormal);
    if (normal.y >= 0.65 && capsule.start.y <= capsule.end.y) {
      const foot = capsule.start, radius = capsule.radius;
      const distance = normal.dot(foot) - normal.dot(triangle.a);
      if (distance >= 0 && distance < radius) {
        const point = triangle.closestPointToPoint(foot, this.contactPoint);
        const length = normal.subVectors(foot, point).length();
        if (length > 0 && length < radius) {
          return { normal: normal.multiplyScalar(1 / length), point, depth: radius - length };
        }
      }
    }
    return super.triangleCapsuleIntersect(capsule, triangle);
  }
  // Head sweeps and interaction sightlines only need to know whether a wall
  // lies strictly before the target. An intersection at the target stays clear.
  rayBlocked(ray, limit) {
    if (limit <= 0 || ray.direction.lengthSq() === 0) return false;
    return this.visit(ray, (start, end) => {
      for (let i = start; i < end; i += 9) {
        const face = this.readFace(i, this.face);
        if (ray.intersectTriangle(face.a, face.b, face.c, true, this.hit)
          && ray.origin.distanceTo(this.hit) < limit) return true;
      }
      return false;
    }, limit);
  }

  rayIntersect(ray, limit = Infinity) {
    if (ray.direction.lengthSq() === 0) return;
    let best = Infinity,
      index = -1;
    this.visit(
      ray,
      (start, end) => {
        for (let i = start; i < end; i += 9) {
          const face = this.readFace(i, this.face);
          if (ray.intersectTriangle(face.a, face.b, face.c, true, this.hit)) {
            const d = ray.origin.distanceToSquared(this.hit);
            if (d < best && d <= limit * limit) {
              best = d;
              index = i;
            }
          }
        }
      },
      limit,
    );
    if (index < 0) return false;
    const triangle = this.readFace(index, new Triangle());
    const position = ray.intersectTriangle(triangle.a, triangle.b, triangle.c, true, new Vector3());
    return { distance: Math.sqrt(best), triangle, position };
  }

  clear() {
    this.pool.length = 0;
    this.words = null;
  }
}

export function loadCollision(buffer) {
  return new PackedCollision(buffer);
}
