import * as T from "three";

export class PilotFlight {
  constructor(body, left, right, roosts, duration, answer) {
    this.body = body;
    this.roosts = roosts;
    this.duration = duration;
    this.answer = answer;
    this.departure = new T.Vector3();
    this.wings = [left,right];
    this.restYaw = body.rotation.y;
    for (const wing of this.wings) body.attach(wing);
    this.restWings = this.wings.map(w => w.rotation.z);
    this.shown = false;
  }
  update(index, visible, snap, dt) {
    const body = this.body, end = this.roosts[index].position;
    body.visible = visible;
    if (!visible) { this.shown = false; return; }
    if (snap || !this.shown) {
      if (!this.shown) body.rotation.y=this.restYaw+Math.PI;
      body.position.copy(end);
      this.elapsed = this.duration;
      this.index = index;
      this.shown = true;
      this.wings.forEach((w,i) => w.rotation.z=this.restWings[i]);
      return;
    }
    if (index !== this.index) {
      this.answer(body.position);
      this.departure.copy(body.position);
      this.index = index;
      this.elapsed = 0;
      const dx=end.x-this.departure.x, dz=end.z-this.departure.z;
      if (dx*dx+dz*dz>.01) body.rotation.y=this.restYaw+Math.atan2(-dx,-dz);
    }
    if (this.elapsed >= this.duration) return;
    this.elapsed = Math.min(this.duration,this.elapsed+dt);
    const t=this.elapsed/this.duration, arc=Math.sin(Math.PI*t);
    body.position.lerpVectors(this.departure,end,t*t*(3-2*t));
    body.position.y+=arc*Math.min(4,this.departure.distanceTo(end)*.20);
    const beat=arc*(.31+.59*Math.sin(12*Math.PI*t));
    this.wings[0].rotation.z=this.restWings[0]+beat;
    this.wings[1].rotation.z=this.restWings[1]-beat;
  }
}
