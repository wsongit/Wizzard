import * as T from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { TrackedRunner } from "./vr.js";
import { Octree } from "three/examples/jsm/math/Octree.js";
import { Capsule } from "three/examples/jsm/math/Capsule.js";

const data = window.BELLWAKE,
  $ = (id) => document.getElementById(id);
const graph = data.story,
  store = "wizzard.bellwake.desktop.v1";
let number = 0,
  leaves = 0,
  muted = false,
  ring = null,
  ringTime = 0,
  initialAngle = 0,
  gestureEnd = 0;
try {
  const value = JSON.parse(localStorage.getItem(store));
  if (value && Number.isInteger(value.number) && graph.states[value.number]) {
    number = value.number;
    leaves = value.leaves & 31;
    muted = !!value.muted;
  }
} catch {}
const state = () => graph.states[number];
function save() {
  try {
    localStorage.setItem(store, JSON.stringify({ number, leaves, muted }));
  } catch {}
}
function fail(error) {
  $("error").textContent = String(error);
  $("error").hidden = false;
}
window.addEventListener("unhandledrejection", (e) => fail(e.reason));
const canvas = $("world"),
  renderer = new T.WebGLRenderer({ canvas, antialias: true, powerPreference: "high-performance" });
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
const scene = new T.Scene(),
  camera = new T.PerspectiveCamera(64, 1, 0.05, 115);
camera.rotation.order = "YXZ";
const hemi = new T.HemisphereLight(0xfff6db, 0x8f896f, 1.35),
  sun = new T.DirectionalLight(0xffedc5, 1.65);
sun.position.set(-9, 15, 8);
scene.add(hemi, sun);
const horizons = ["#d9caa8", "#aec3a1", "#b1c8bd", "#ccab90", "#9996b1"];
const sky = new T.Mesh(
  new T.SphereGeometry(96, 32, 16),
  new T.MeshBasicMaterial({ side: T.BackSide, depthWrite: false, fog: false }),
);
scene.add(sky);
const loader = new GLTFLoader(),
  look = new T.Vector3(),
  forward = new T.Vector3(),
  side = new T.Vector3(),
  step = new T.Vector3();
const capsule = new Capsule(new T.Vector3(), new T.Vector3(), 0.26);
const tracks = new Map();
let music = null;
function track(name) {
  if (!tracks.has(name)) {
    const a = new Audio("data:audio/ogg;base64," + data.sounds[name]);
    tracks.set(name, a);
  }
  return tracks.get(name);
}
function playMusic() {
  if (music) music.pause();
  music = track(state().ending ? "Morning" : graph.rooms[state().room]);
  music.loop = true;
  music.volume = 0.35;
  music.muted = muted;
  music.play().catch(() => {});
}
function tone(i) {
  const a = track(["Leaf", "Ember", "Tide", "Toll"][i]);
  a.currentTime = 0;
  a.volume = 0.5;
  a.muted = muted;
  a.play().catch(() => {});
}
let group = null,
  nodes = {},
  markers = [],
  tree,
  onFloor = true,
  vy = 0,
  yaw = 0,
  pitch = 0,
  started = false,
  busy = true,
  book = false,
  focus = "",
  timer = 0,
  speechEnd = 0,
  restartEnd = 0;
const keys = new Set(),
  ray = new T.Raycaster();
function bytes(key) {
  let b = atob(data.models[key]),
    array = new Uint8Array(b.length);
  for (let i = 0; i < b.length; i++) array[i] = b.charCodeAt(i);
  return array.buffer;
}
function resetFeet() {
  if (vr.session) vr.reset();
  const p = nodes.Spawn.position;
  capsule.start.copy(p).y += 0.26;
  capsule.end.copy(p).y += 1.4;
  vy = 0;
  onFloor = false;
  yaw = 0;
  pitch = 0;
  updateCamera();
}
renderer.xr.enabled = true;
const vr = new TrackedRunner(
  scene,
  camera,
  renderer,
  async (name) => (await loader.parseAsync(bytes(name), "")).scene,
  () => ({ tree, spawn: nodes.Spawn?.position }),
  () => {
    if (!book) interact(focus);
  },
  () => toggleBook(!book),
  () => {
    toggleBook(false);
    resetFeet();
  },
);
navigator.xr
  ?.isSessionSupported("immersive-vr")
  .then((on) => {
    $("vr").hidden = $("reenter").hidden = !on;
  })
  .catch(() => {});
$("reenter").onclick = $("vr").onclick = async () => {
  if (busy) return;
  if (book) toggleBook(false);
  try {
    if (!started) $("start").click();
    await vr.enter();
  } catch (e) {
    say("Headset", e.message, 12);
  }
};
function updateCamera() {
  if (vr.session) return;
  camera.position.copy(capsule.end).y += 0.22;
  camera.rotation.set(pitch, yaw, 0, "YXZ");
}
function say(title, line, seconds = 8) {
  $("act").textContent = title;
  $("words").textContent = line;
  $("speech").hidden = false;
  speechEnd = performance.now() + seconds * 1000;
}
function label(id) {
  if (id.startsWith("A_Key")) return state().keys[+id.slice(-1)];
  return {
    A_Talk: state().room === 4 && state().solved ? "Ina" : graph.speakers[state().room],
    A_Letter: "Witness leaf",
    A_Gate: state().ending ? "Begin again" : "Way arch",
    A_Ina: "Ina",
    A_Roster: "Watch roster",
    A_End0: "Share the watch",
    A_End1: "Free the voice",
    A_Lens: "Casting cup",
    A_Meadow: "Long Meadow trail",
  }[id];
}
function dispose(old) {
  const geos = new Set(),
    materials = new Set(),
    textures = new Set();
  old.traverse((o) => {
    if (!o.isMesh) return;
    geos.add(o.geometry);
    materials.add(o.material);
    if (o.material.map) textures.add(o.material.map);
  });
  geos.forEach((x) => x.dispose());
  materials.forEach((x) => x.dispose());
  textures.forEach((x) => x.dispose());
  scene.remove(old);
}
async function room() {
  busy = true;
  $("veil").style.opacity = 1;
  const s = state(),
    k = s.room;
  const gltf = await loader.parseAsync(bytes(graph.rooms[k]), "");
  if (group) dispose(group);
  group = gltf.scene;
  nodes = {};
  markers = [];
  const palette = new Map(),
    solids = new T.Group();
  group.traverse((o) => {
    if (o.name) nodes[o.name] = o;
    if (o.name.startsWith("A_")) markers.push(o);
    if (o.isMesh) {
      const old = o.material;
      if (!palette.has(old)) {
        const paint = new T.MeshLambertMaterial({ map: old.map, color: old.color, side: T.DoubleSide });
        if (old.map) {
          old.map.magFilter = T.LinearFilter;
          old.map.minFilter = T.LinearMipmapLinearFilter;
          old.map.anisotropy = 2;
        }
        if (["SeaGlass", "Amber"].includes(old.name)) {
          paint.emissive.copy(old.color).multiplyScalar(0.38);
          paint.emissiveMap = old.map;
        }
        palette.set(old, paint);
      }
      o.material = palette.get(old);
    }
  });
  palette.forEach((_, old) => old.dispose());
  group.updateMatrixWorld(true);
  for (const id of ["Terrain", "Rim", "Set", "C_Solids"]) solids.add(nodes[id].clone(true));
  tree = new Octree().fromGraphNode(solids);
  nodes.C_Solids.visible = false;
  scene.add(group);
  const color = s.ending ? "#efd3a7" : horizons[k];
  scene.fog = new T.Fog(color, 19, 65);
  const panorama = await new T.TextureLoader().loadAsync(
    "data:image/jpeg;base64," + data.skies[s.ending ? "Morning" : graph.rooms[k]],
  );
  panorama.colorSpace = T.SRGBColorSpace;
  if (sky.material.map) sky.material.map.dispose();
  sky.material.map = panorama;
  sky.material.needsUpdate = true;
  ring = null;
  resetFeet();
  sync();
  timer = 32;
  focus = "";
  $("prompt").hidden = true;
  $("chapter").textContent = s.ending
    ? "Epilogue"
    : k
      ? "Chapter " + ["", "I", "II", "III", "IV"][k]
      : "The Long Meadow";
  $("location").textContent = graph.titles[k];
  if (started) playMusic();
  save();
  busy = false;
  $("veil").style.opacity = 0;
}
function sync() {
  const s = state();
  nodes.GateLight.visible = s.room === 0 ? s.commissioned : s.solved && s.room !== 4;
  for (const [name, on] of [
    ["Ina", s.ending === 2],
    ["A_Ina", s.ending === 2],
    ["Roster", s.ending === 1],
    ["A_Roster", s.ending === 1],
    ["HushWave", s.room === 4 && s.challenged && !s.solved],
  ])
    if (nodes[name]) nodes[name].visible = on;
  for (let i = 0; i < 3; i++) {
    if (nodes["Stray" + i]) nodes["Stray" + i].visible = s.beam === i + 1;
    if (nodes["Call" + i]) nodes["Call" + i].visible = s.challenged && !s.solved && s.called === i;
    if (nodes["Flow" + i]) nodes["Flow" + i].visible = !!(s.water & (1 << i));
    if (nodes["Choice" + i]) {
      nodes["Choice" + i].visible = s.solved;
      nodes["A_End" + i].visible = s.solved;
    }
    if (s.room === 3) nodes["Rotor" + i].rotation.y = s.lenses & (1 << i) ? 0 : Math.PI / 2;
  }
  if (s.room === 4) nodes.A_Gate.visible = false;
  for (let i = 0; i < 4; i++) if (nodes["Ray" + i]) nodes["Ray" + i].visible = i < s.beam;
}
function welcome() {
  const s = state();
  if (s.ending)
    say(
      "Epilogue",
      s.ending === 1
        ? "The long watch is over. Tonight the whole market takes its turn at the bell."
        : "At dawn the river sings with a human voice. Tavi has set two places for breakfast.",
      12,
    );
  else say(graph.titles[s.room], s.objective, 6);
}
async function interact(id) {
  if (!started || busy || book || !id) return;
  if (id === "A_Meadow") {
    say(
      "Long Meadow trail",
      "Beyond this sign lie the rolling meadow and Mossbell Village. Explore them in the Unity edition.",
    );
    return;
  }
  const prev = state(),
    name = id === "Toll" ? "The hollow toll" : label(id);
  if (prev.ending && id === "A_Gate") {
    if (performance.now() > restartEnd) {
      restartEnd = performance.now() + 4000;
      say("Way arch", "Use the arch again within four seconds to begin a fresh journey.");
      return;
    }
    number = 0;
    leaves = 0;
    await room();
    welcome();
    return;
  }
  if (id === "A_Talk") gestureEnd = performance.now() + 3000;
  const move = prev.moves[id];
  if (!move) return;
  if (id.startsWith("A_Key") && [1, 2].includes(prev.room)) {
    if (ring && prev.room === 1) ring.rotation.z = 0;
    ring = nodes["Rotor" + id.slice(-1)];
    ringTime = performance.now();
    initialAngle = ring.rotation.y;
  }
  number = move[0];
  if (id === "A_Letter") leaves |= 1 << prev.room;
  if (prev.room !== state().room) {
    await room();
    welcome();
    return;
  }
  if (id.startsWith("A_Key") || id === "Toll") {
    tone(id === "Toll" || state().hearts < prev.hearts ? 3 : +id.slice(-1));
    if (prev.room === 4) timer = 24;
  }
  if (!prev.challenged && state().challenged) timer = 32;
  sync();
  save();
  say(name, move[1], id === "A_Talk" || id === "A_Letter" ? 12 : 6);
}
function pick() {
  focus = "";
  let best = Infinity;
  const origin = vr.session ? vr.head : camera.position;
  if (vr.session) forward.copy(vr.direction);
  else camera.getWorldDirection(forward);
  for (const o of markers) {
    if (!o.visible) continue;
    look.copy(o.position).sub(origin);
    const distance = look.length();
    if (distance > 4.1) continue;
    look.normalize();
    const dot = forward.dot(look);
    if (dot < 0.64) continue;
    ray.set(origin, look);
    ray.far = Math.max(0.01, distance - 0.45);
    // Check the nearest wall rather than ray-testing every decorative triangle.
    const hit = tree.rayIntersect(ray.ray);
    if (hit && hit.distance < ray.far) continue;
    const weight = distance + 4 * (1 - dot);
    if (weight < best) {
      best = weight;
      focus = o.name;
    }
  }
  $("prompt").hidden = !focus;
  if (focus) $("prompt").textContent = "E   ·   " + label(focus);
}
function move(dt) {
  yaw += ((keys.has("ArrowLeft") ? 1 : 0) - (keys.has("ArrowRight") ? 1 : 0)) * dt * 1.75;
  pitch = T.MathUtils.clamp(
    pitch + ((keys.has("ArrowUp") ? 1 : 0) - (keys.has("ArrowDown") ? 1 : 0)) * dt * 1.15,
    -1.25,
    1.25,
  );
  forward.set(-Math.sin(yaw), 0, -Math.cos(yaw));
  side.set(Math.cos(yaw), 0, -Math.sin(yaw));
  step
    .set(0, 0, 0)
    .addScaledVector(forward, +keys.has("KeyW") - +keys.has("KeyS"))
    .addScaledVector(side, +keys.has("KeyD") - +keys.has("KeyA"))
    .normalize()
    .multiplyScalar(dt * (keys.has("ShiftLeft") ? 6.5 : 4));
  vy = Math.max(-22, vy - 12 * dt);
  step.y = vy * dt;
  capsule.translate(step);
  const hit = tree.capsuleIntersect(capsule);
  onFloor = false;
  if (hit) {
    capsule.translate(hit.normal.multiplyScalar(hit.depth));
    if (hit.normal.y > 0 && vy < 0) {
      onFloor = true;
      vy = 0;
    }
  }
  if (capsule.start.y < -1 || Math.max(Math.abs(capsule.start.x), Math.abs(capsule.start.z)) > 20.65)
    resetFeet();
  updateCamera();
}
function toggleBook(open) {
  if (!started || busy) return;
  book = open;
  keys.clear();
  $("book").hidden = !open;
  $("hud").hidden = open;
  if (open) {
    document.exitPointerLock?.();
    $("booktitle").textContent = graph.titles[state().room];
    $("objective").textContent = state().objective + "   ·   " + state().seals + " of 3 vows";
    $("leaves").replaceChildren();
    for (let i = 0; i < 5; i++)
      if (leaves & (1 << i)) {
        const li = document.createElement("li");
        li.textContent = graph.states
          .find((x) => x.room === i)
          .moves.A_Letter[1][1].split(" / ")
          .pop();
        $("leaves").append(li);
      }
    if (!leaves) {
      const li = document.createElement("li");
      li.textContent = "Look for a witness leaf on the stone lectern in each district.";
      $("leaves").append(li);
    }
  }
}
$("start").onclick = () => {
  if (busy) return;
  started = true;
  resetFeet();
  $("cover").hidden = true;
  $("hud").hidden = false;
  playMusic();
  welcome();
};
$("journal").onclick = () => toggleBook(true);
$("close").onclick = () => toggleBook(false);
$("sound").onclick = () => {
  muted = !muted;
  tracks.forEach((a) => (a.muted = muted));
  $("sound").textContent = muted ? "Enable sound" : "Mute sound";
  save();
};
$("sound").textContent = muted ? "Enable sound" : "Mute sound";
addEventListener("keydown", (e) => {
  if (!started) return;
  if (["Space", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.code)) e.preventDefault();
  if (e.repeat) return;
  if (e.code === "KeyJ" || (e.code === "Escape" && book)) {
    toggleBook(!book);
    return;
  }
  if (book || busy) return;
  keys.add(e.code);
  if (e.code === "KeyE") interact(focus);
  if (e.code === "Space" && onFloor) {
    vy = 4.5;
    onFloor = false;
  }
});
addEventListener("keyup", (e) => keys.delete(e.code));
addEventListener("blur", () => keys.clear());
let drag = false;
canvas.onpointerdown = (e) => {
  if (!started || book) return;
  drag = true;
  canvas.setPointerCapture(e.pointerId);
};
canvas.onpointerup = () => (drag = false);
canvas.onpointercancel = () => (drag = false);
canvas.ondblclick = () => {
  if (started && !book) canvas.requestPointerLock?.()?.catch(() => {});
};
addEventListener("pointermove", (e) => {
  if (started && !book && (drag || document.pointerLockElement === canvas)) {
    yaw -= e.movementX * 0.0035;
    pitch = T.MathUtils.clamp(pitch - e.movementY * 0.0035, -1.25, 1.25);
  }
});
function resize() {
  renderer.setSize(innerWidth, innerHeight, false);
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
}
addEventListener("resize", resize);
resize();
let previous = 0,
  accum = 0,
  frameWindow = 0,
  slow = 0,
  fast = 0;
function adapt(interval) {
  // UI stays at native resolution. Scale only the 3D buffer on a slow renderer.
  if (interval > 200 || interval <= 0) return;
  frameWindow++;
  if (interval > 26) slow++;
  if (interval < 19) fast++;
  if (frameWindow < 42) return;
  let ratio = renderer.getPixelRatio(),
    next = ratio;
  if (slow > 23) next = Math.max(0.5, ratio * 0.8);
  else if (fast > 39) next = Math.min(Math.min(devicePixelRatio, 1.5), ratio + 0.05);
  if (Math.abs(next - ratio) > 0.025) {
    renderer.setPixelRatio(next);
    resize();
  }
  frameWindow = 0;
  slow = 0;
  fast = 0;
}
function loop(time, frame) {
  if (previous && !busy && !book && !vr.session) adapt(time - previous);
  const delta = Math.min(0.066, Math.max(0, (time - previous) / 1000));
  previous = time;
  if (!group || busy) return;
  if (vr.session) vr.update(frame, delta, book);
  if (!started) {
    camera.position.set(11 + Math.sin(time * 0.00012) * 1.3, 5.6, 15.8);
    camera.lookAt(-3.5, 2, -3);
  } else if (!book) {
    if (!vr.session) {
      const sub = Math.ceil(delta / 0.016);
      for (let i = 0; i < sub; i++) move(delta / sub);
    }
    accum += delta;
    if (accum >= 0.08) {
      pick();
      accum = 0;
    }
    if (time > speechEnd) $("speech").hidden = true;
    const fight = state().room === 4 && state().challenged && !state().solved;
    $("clock").hidden = !fight;
    if (fight) {
      timer -= delta;
      $("clock").textContent =
        state().keys[state().called] +
        "   ·   " +
        Math.ceil(timer) +
        "s   ·   " +
        state().hearts +
        " breaths";
      if (timer <= 0) interact("Toll");
    }
    if (fight && nodes.HushWave) nodes.HushWave.scale.setScalar(1 + 12 * (1 - Math.min(1, timer / 24)));
    if (nodes.GreatBell) nodes.GreatBell.rotation.z = Math.sin(time * 0.0018) * (fight ? 0.12 : 0.017);
  }
  if (ring) {
    let age = (time - ringTime) / 1000;
    if (state().room === 2) ring.rotation.y = initialAngle + Math.PI * 0.5 * Math.min(1, age * 2);
    else ring.rotation.z = Math.sin(age * 15) * 0.32 * Math.exp(-age * 4);
    if (age > 1.4) ring = null;
  }
  if (nodes.SpeakerHead) {
    const head = nodes.SpeakerHead,
      viewer = vr.session ? vr.head : camera.position;
    look.copy(viewer).sub(head.position);
    const turn = look.lengthSq() < 72 ? T.MathUtils.clamp(Math.atan2(look.x, look.z), -0.56, 0.56) : 0;
    head.rotation.y = T.MathUtils.lerp(head.rotation.y, turn, Math.min(1, delta * 5));
    const remain = Math.max(0, (gestureEnd - time) / 1000),
      amount = Math.min(1, remain) * Math.min(1, (3 - remain) * 4);
    nodes.SpeakerArm.rotation.x =
      0.032 * Math.sin(time * 0.0016) + amount * (0.28 + 0.085 * Math.sin(time * 0.005));
  }
  if (nodes.Familiar) nodes.Familiar.rotation.y = Math.sin(time * 0.00085) * 0.14;
  if (vr.session) {
    const text = book
      ? state().objective + "   •   " + state().seals + " of three vows. Press A/X to close."
      : !$("speech").hidden
        ? $("words").textContent
        : focus
          ? "Press a trigger to interact."
          : !$("clock").hidden
            ? $("clock").textContent
            : "";
    const title = book
      ? "Witness book"
      : !$("speech").hidden
        ? $("act").textContent
        : focus
          ? label(focus)
          : "The keeper calls";
    vr.caption(title, text);
  }
  sky.position.copy(vr.session ? vr.head : camera.position);
  renderer.render(scene, camera);
}
if (__TEST__)
  window.bellProbe = () => ({
    number,
    room: state().room,
    focus,
    busy,
    started,
    leaves,
    ending: state().ending,
    yaw,
    pitch,
    feet: capsule.start.toArray(),
    markers: Object.fromEntries(markers.map((m) => [m.name, m.position.toArray()])),
    vr: !!vr.ready,
    vrHead: vr.head.toArray(),
    vrForward: vr.direction.toArray(),
    palms: vr.hands.map((h) => h.valid),
    planted: vr.hands.map((h) => h.contact),
    ratio: renderer.getPixelRatio(),
    calls: renderer.info.render.calls,
    tris: renderer.info.render.triangles,
    timer,
    book,
  });
room()
  .then(() => {
    $("start").disabled = false;
    $("start").textContent = number ? "Continue journey" : "Begin journey";
    renderer.setAnimationLoop(loop);
  })
  .catch(fail);
