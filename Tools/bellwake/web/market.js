import * as T from "three";


const up = new T.Vector3(0,1,0);
const localTurn = new T.Quaternion();
const position = o => o.getWorldPosition(new T.Vector3());
const restRotation = o => o.getWorldQuaternion(new T.Quaternion());
const smooth = (x,a,b) => T.MathUtils.smoothstep(x,a,b);

function bird(nodes, prefix, time, period) {
  const body=nodes[prefix], far=nodes[prefix+"Far"], end=position(nodes[prefix+"Trail"]);
  const origin=position(body);
  const right=up.clone().cross(end.clone().sub(origin)).normalize();
  const joints=["Head","Left","Right"].map(key => {
    const part=nodes[prefix+key];
    const axis=right.clone().applyQuaternion(restRotation(part).invert());
    body.attach(part);
    return {part, axis, rest:part.quaternion.clone()};
  });
  const legHeight=position(joints[1].part).y-origin.y;
  const stepUp=body.parent.worldToLocal(origin.clone().add(up));
  body.parent.worldToLocal(origin);
  stepUp.sub(origin).multiplyScalar(legHeight);
  body.parent.worldToLocal(end);
  const facing=body.quaternion.clone();
  const vertical=up.clone().applyQuaternion(restRotation(body.parent).invert());
  const world=new T.Vector3();
  let distant=false;
  far.visible=false;
  return (dt,ear) => {
    time=(time+dt)%period;
    const t=time/period;
    body.position.lerpVectors(origin,end,smooth(t,.13,.4)-smooth(t,.64,.91));
    const turn=Math.PI*(smooth(t,.46,.61)+smooth(t,.92,1));
    body.quaternion.setFromAxisAngle(vertical,turn).multiply(facing);
    const limit=distant ? 12 : 14;
    distant=body.getWorldPosition(world).distanceToSquared(ear)>limit*limit;
    body.visible=!distant;
    far.visible=distant;
    if(distant){
      far.position.copy(body.position);
      far.quaternion.copy(body.quaternion);
      return;
    }
    const walk=t>.13 && t<.4 ? (t-.13)/.27 : t>.64 && t<.91 ? (t-.64)/.27 : 0;
    const gait=Math.sin(walk*8*Math.PI)*Math.sin(walk*Math.PI)*24;
    const angle=Math.abs(gait)*Math.PI/180;
    body.position.addScaledVector(stepUp,1.025*(Math.cos(angle)-1)+.62*Math.sin(angle));
    const peck=walk>0 ? 3*Math.sin(walk*16*Math.PI) : 30*Math.pow(Math.max(0,Math.cos(t*14*Math.PI)),4);
    for(let i=0;i<joints.length;i++){
      const {part,axis,rest}=joints[i];
      const degrees=i===0 ? peck : i===1 ? gait : -gait;
      part.quaternion.copy(rest).multiply(localTurn.setFromAxisAngle(axis,degrees*Math.PI/180));
    }
  };
}

export function marketLife(nodes,soundURL) {
  const sails=nodes.MillSails;
  if (!sails) return null;
  const axis=position(nodes.MillAxis).sub(position(sails)).normalize()
    .applyQuaternion(restRotation(sails).invert());
  const birds=[bird(nodes,"MarshHen",0,15),bird(nodes,"ReedHen",7.7,19)];
  const mill=position(sails), yard=position(nodes.MarshHen), voices=new Map();
  let age=0, nextMill=0, nextHen=2.8, nextListen=0;
  function voice(key,volume,loop=false) {
    let audio=voices.get(key);
    if(!audio) {
      audio=new Audio(soundURL(key));audio.loop=loop;voices.set(key,audio);
    }
    audio.volume=volume;
    if(!loop || audio.paused) audio.play().catch(()=>{});
  }
  return {
    update(dt,night,ear,muted) {
      sails.rotateOnAxis(axis,dt*13*Math.PI/180);
      for (const step of birds) step(dt*(1-.92*night),ear);
      age+=dt;
      if(age<nextListen)return;
      nextListen=age+.2;
      const byYard=Math.max(0,1-ear.distanceTo(yard)/16);
      const byMill=Math.max(0,1-ear.distanceTo(mill)/48);
      voices.forEach(a=>a.muted=muted);
      if(age>=nextHen) {
        if(!muted && byYard>0 && night<.45) voice("YardHen",.21*byYard);
        nextHen=age+5+3*Math.abs(Math.sin(age*1.26));
      }
      if(age>=nextMill) {
        if(!muted && byMill>0) voice("MillBearing",.15*byMill);
        nextMill=age+360/(4*13);
      }
      if(!muted && byYard>0 && night>.15) voice("YardDusk",night*.08*byYard,true);
      else voices.get("YardDusk")?.pause();
    },
    release() {
      for (const audio of voices.values()){
        audio.pause();audio.removeAttribute("src");audio.load();
      }
      voices.clear();
    },
  };
}

export class ValleyLight {
  constructor(sky,hemi,sun,stars,outdoors) {
    this.outdoors=new Set(outdoors);
    this.sky=sky; this.hemi=hemi; this.sun=sun;
    this.azimuth={value:new T.Vector3()};
    this.night={value:0}; this.dusk={value:0}; this.outside={value:0};
    this.nightFog=new T.Color(0x24314a); this.duskFog=new T.Color(0xc4836c);
    this.fogColor=new T.Color(); this.lightColor=new T.Color(0xffedc5);
    this.blueSky=new T.Color(0x9eb2e0); this.warmSky=new T.Color(0xfff6db);
    this.moonlight=new T.Color(0xb1c4ed); this.sunset=new T.Color(0xffb786);
    sky.material.onBeforeCompile = shader => {
      shader.uniforms.valleyOutside=this.outside; shader.uniforms.valleySun=this.azimuth; shader.uniforms.valleyNight=this.night;
      shader.uniforms.valleyDusk=this.dusk; shader.uniforms.valleyStars={value:stars};
      shader.vertexShader="varying vec3 valleyDirection;\n"+shader.vertexShader.replace(
        "#include <begin_vertex>","#include <begin_vertex>\nvalleyDirection=position;");
      shader.fragmentShader="varying vec3 valleyDirection;uniform vec3 valleySun;uniform float valleyNight,valleyDusk,valleyOutside;uniform sampler2D valleyStars;\n"+shader.fragmentShader.replace(
        "#include <map_fragment>",`#include <map_fragment>
        if(valleyOutside>.5){
        vec3 d=normalize(valleyDirection);
        float above=smoothstep(.18,.28,d.y);
        float dusk=valleyDusk*clamp(1.15-2.*abs(d.y),0.,1.);
        diffuseColor.rgb=mix(diffuseColor.rgb,diffuseColor.rgb*vec3(1.04,.59,.56)+vec3(.11,.014,.004),dusk*.72);
        diffuseColor.rgb*=mix(vec3(1.),vec3(.043,.066,.17),valleyNight);
        float solar=dot(d,valleySun);
        diffuseColor.rgb+=above*(smoothstep(.99930,.99952,solar)*(1.-valleyNight)*vec3(.9,.67,.34)
          +smoothstep(.99947,.99965,-solar)*valleyNight*vec3(.58,.67,.79));
        if(valleyNight>.005) diffuseColor.rgb+=texture2D(valleyStars,vMapUv).rgb*above*valleyNight;
        }`);
    };
  }
  release() { this.windows=[]; this.fog=null; }
  bind(theme,fog,palette,minutes) {
    this.exterior=this.outdoors.has(theme);
    this.fog=fog; this.fogColor.copy(fog.color);
    this.windows=[];
    for(const [old,paint] of palette) if(old.name==="WindowLight" || old.name==="WindowDark") {
      // Glazing is a separate mesh from the dark timber crossbars.
      this.windows.push([paint,old.name==="WindowLight" ? .84 : .47]);
    }
    this.outside.value=this.exterior ? 1 : 0;
    this.apply(minutes);
  }
  apply(minutes) {
    const arc=(minutes/1440-.25)*2*Math.PI, h=Math.sin(arc), c=Math.cos(arc);
    const day=this.exterior ? smooth(h,-.25,.32) : 1;
    const night=1-day, dusk=this.exterior ? Math.max(0,1-4*Math.abs(h)) : 0;
    this.azimuth.value.set(.85*c,h,.527*c).normalize(); this.night.value=night; this.dusk.value=dusk;
    this.hemi.color.copy(this.warmSky).lerp(this.blueSky,night); this.hemi.intensity=1.35*(1-.67*night);
    this.sun.intensity=1.65*(1-.72*night);
    this.sun.color.copy(this.lightColor).lerp(this.sunset,dusk).lerp(this.moonlight,night);
    if(this.exterior) this.sun.position.set(.85*c*(2*day-1),Math.max(.24,Math.abs(h)),.527*c*(2*day-1));
    else this.sun.position.set(-9,15,8);
    this.fog.color.copy(this.fogColor).lerp(this.duskFog,dusk*.42).lerp(this.nightFog,night);
    for(const [paint,glow] of this.windows)paint.emissive.setRGB(1,.40,.058).multiplyScalar(glow*night);
  }
}
