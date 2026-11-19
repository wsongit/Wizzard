// Project the source onto the tracked listener's horizontal plane. Browsers and
// native XR use the same 14-degree acceptance cone, including in silent mode.
export function callAngle(ear, heading, source) {
  const dx=source.x-ear.x, dz=source.z-ear.z;
  return Math.atan2(-heading.z*dx+heading.x*dz, heading.x*dx+heading.z*dz);
}

export class ForestCall {
  start(url, muted) {
    this.stop();
    this.context ||= new AudioContext();
    const ctx=this.context;
    this.audio=new Audio(url);
    this.audio.loop=true;
    this.audio.muted=muted;
    this.audio.volume=.8;
    this.source=ctx.createMediaElementSource(this.audio);
    this.pan=ctx.createPanner();
    this.pan.panningModel="HRTF";
    this.pan.refDistance=3;
    this.source.connect(this.pan).connect(ctx.destination);
    ctx.resume().catch(()=>{});
    this.audio.play().catch(()=>{});
  }
  turn(angle) {
    if (!this.pan) return;
    this.pan.positionX.value=3*Math.sin(angle);
    this.pan.positionZ.value=-3*Math.cos(angle);
  }
  stop() {
    if (!this.audio) return;
    this.audio.pause();
    this.source.disconnect();
    this.pan.disconnect();
    this.audio.removeAttribute("src");
    this.audio.load();
    this.audio=this.source=this.pan=null;
  }
  release() {
    this.stop();
    this.context?.close().catch(()=>{});
    this.context=null;
  }
}
