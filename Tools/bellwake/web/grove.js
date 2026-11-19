import { Box3 } from "three";

// The margin allows the player to walk back across a switch point without
// the trees alternating between their two meshes with every head movement.
export class Grove {
  cells=[];
  bind(nodes) {
    this.cells=[];
    for (const [key, near] of Object.entries(nodes)) {
      if (!/^GroveNear\d\d$/.test(key)) continue;
      const far=nodes[key.replace("Near","Far")];
      const bounds=new Box3().setFromObject(near);
      far.visible=false;
      this.cells.push({near,far,bounds});
    }
  }
  update(eye) {
    for (const {near,far,bounds} of this.cells) {
      const distance=bounds.distanceToPoint(eye);
      const show=distance<(near.visible ? 15 : 11);
      near.visible=show;
      far.visible=!show;
    }
  }
}
