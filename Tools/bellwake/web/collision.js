import { Box3, Vector3, Triangle } from "three";
import { Octree } from "three/examples/jsm/math/Octree.js";

// Each triangle belongs to one leaf. The Quest CPU never sorts faces or rebuilds spatial partitions.
export function loadCollision(buffer) {
  const values = new Float32Array(buffer);
  let offset = 0;
  function vector() {
    offset += 3;
    return new Vector3().fromArray(values, offset - 3);
  }
  function read() {
    const node = new Octree(new Box3(vector(), vector()));
    const count = values[offset++];
    if (count === 0) node.subTrees.push(read(), read());
    else {
      if (!Number.isInteger(count) || count < 1 || count > 12) throw Error("Invalid collision leaf");
      for (let i = 0; i < count; i++) node.triangles.push(new Triangle(vector(), vector(), vector()));
    }
    return node;
  }
  const root = new Octree();
  root.subTrees.push(read());
  if (offset !== values.length) throw Error("Invalid room collision data");
  return root;
}
