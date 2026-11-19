import * as T from "three";
import { Underworks } from "./underworks.js";
import { Passage } from "./passage.js";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { TrackedRunner } from "./vr.js";
import { loadCollision } from "./collision.js";
import { Capsule } from "three/examples/jsm/math/Capsule.js";

const data = window.BELLWAKE,
  $ = (id) => document.getElementById(id);
const graph = data.story,
  store = "wizzard.bellwake.desktop.v1";
let savedPassage, savedWorks, lastCheckpoint;
let secondsByPlace = {};
let number = 0,
  leaves = 0,
  muted = false,
  ring = null,
  ringTime = 0,
  initialAngle = 0,
  gestureEnd = 0;
try {
  lastCheckpoint = localStorage.getItem(store);
  const value = JSON.parse(lastCheckpoint);
  if (value && Number.isInteger(value.number) && graph.states[value.number]) {
    number = value.number;
    leaves = value.leaves & 31;
    muted = !!value.muted;
    savedPassage = value.passage;
    savedWorks = value.works;
    for (const [key, t] of Object.entries(value.secondsByPlace || {}))
      if (Number.isFinite(t) && t >= 0) secondsByPlace[key] = t;
  }
} catch {}
const state = () => graph.states[number];
let passage = new Passage(data.regions, savedPassage, state().room, state().ending);
const openingWard = data.works.rooms.findIndex((r) => r.early);
const savedEarly = !!data.works.rooms[savedWorks?.chamber]?.early;
let works = new Underworks(
  data.works,
  savedWorks,
  savedEarly ? state().room === 1 && !state().ending : state().room === 3 && state().solved,
);
const roomRadius = () => (works.active && works.room.halfSpan) || 20;
const locationKey = () =>
  works.active ? works.room.key : passage.active ? passage.region.key : graph.rooms[state().room];
const hasFloodBook = () =>
  !works.active && (state().room === 4 || state().ending !== 0) && !!works.signals.landed;
const locationName = () =>
  works.active ? works.room.title : passage.active ? passage.region.title : graph.titles[state().room];
const objective = () =>
  works.active ? works.objective() : passage.active ? passage.objective() : state().objective;
function save(timerOnly = false) {
  try {
    if (timerOnly && localStorage.getItem(store) !== lastCheckpoint) return;
    const checkpoint = JSON.stringify({
      number,
      leaves,
      muted,
      passage: passage.progress,
      works: works.progress,
      secondsByPlace,
    });
    localStorage.setItem(store, checkpoint);
    lastCheckpoint = checkpoint;
  } catch {}
}
function playTime() {
  const minutes = Math.floor(Object.values(secondsByPlace).reduce((s, t) => s + t, 0) / 60);
  return Math.floor(minutes / 60) + "h " + (minutes % 60) + "m";
}
window.addEventListener("pagehide", () => {
  if (started && !busy) save(true);
});
document.addEventListener("visibilitychange", () => {
  if (document.hidden && started && !busy) save(true);
});
function fail(error) {
  $("error").textContent = String(error);
  if (busy) {
    const retry = document.createElement("button");
    retry.textContent = "Reload last checkpoint";
    retry.onclick = () => location.reload();
    $("error").append(" ", retry);
  }
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
const effects = new Map();
let music = null,
  musicTheme = "",
  musicGeneration = 0;
const themeKey = () => (state().ending ? "Morning" : works.active ? works.room.theme : locationKey());
function assetURL(kind, name, mime) {
  return data.streamed ? data[kind][name] : "data:" + mime + ";base64," + data[kind][name];
}
function dropMusic() {
  if (!music) return;
  music.pause();
  music.removeAttribute("src");
  music.load();
  music = null;
  musicTheme = "";
}
function playMusic() {
  if (music && musicTheme === themeKey()) return;
  dropMusic();
  musicTheme = themeKey();
  musicGeneration++;
  music = new Audio(assetURL("sounds", musicTheme, "audio/ogg"));
  music.loop = true;
  music.volume = 0.35;
  music.muted = muted;
  music.play().catch(() => {});
}
function tone(i) {
  const key = ["Leaf", "Ember", "Tide", "Toll"][i];
  if (!effects.has(key)) effects.set(key, new Audio(assetURL("sounds", key, "audio/ogg")));
  const a = effects.get(key);
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
  guide = null,
  surveyImage = null,
  roadPage = 0,
  journalPage = 0,
  journalText = [],
  focus = "",
  timer = 0,
  speechEnd = 0,
  restartEnd = 0;
const keys = new Set(),
  ray = new T.Raycaster();
async function loadModel(key) {
  if (data.streamed) return (await loader.loadAsync(data.models[key])).scene;
  return (await loader.parseAsync(bytes(data.models[key]), "")).scene;
}
function bytes(encoded) {
  let b = atob(encoded),
    array = new Uint8Array(b.length);
  for (let i = 0; i < b.length; i++) array[i] = b.charCodeAt(i);
  return array.buffer;
}
function arrival() {
  const camp = works.active && works.progress.camp;
  return (camp && camp.startsWith("Rest") && nodes[camp]?.position) || nodes.Spawn?.position;
}
function resetFeet() {
  if (vr.session) vr.reset();
  const p = arrival();
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
  loadModel,
  () => ({ tree, spawn: arrival(), radius: roomRadius() }),
  () => {
    if (book) journalPage = (journalPage + 1) % journalText.length;
    else interact(focus);
  },
  () => toggleBook(!book),
  () => {
    toggleBook(false);
    if (!busy && nodes.Spawn) resetFeet();
  },
  callGuide,
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
  if (works.active) return works.station(id).label;
  if (passage.active) return passage.label(id);
  if (id.startsWith("A_Key")) return state().keys[+id.slice(-1)];
  return {
    A_Talk: state().room === 4 && state().solved ? "Ina" : graph.speakers[state().room],
    A_Letter: "Witness leaf",
    A_Gate: state().ending ? "Begin again" : "Way arch",
    A_Ina: "Ina",
    A_Roster: "Watch roster",
    A_RoadBook: "Letters from the public road",
    A_Nameplate: "Fourth hand",
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
    for (const material of [].concat(o.material)) {
      materials.add(material);
      for (const value of Object.values(material)) if (value?.isTexture) textures.add(value);
    }
  });
  geos.forEach((x) => x.dispose());
  materials.forEach((x) => x.dispose());
  const images = new Set();
  textures.forEach((x) => {
    images.add(x.source.data);
    x.dispose();
  });
  images.forEach((img) => img?.close?.());
  scene.remove(old);
}
let resolveFrame, retired;
function loadingFrame() {
  return new Promise((resolve) => {
    resolveFrame = resolve;
  });
}
async function room() {
  try {
    await loadRoom();
    return true;
  } catch (error) {
    fail(error);
    return false;
  }
}
async function loadRoom() {
  busy = true;
  $("veil").style.opacity = 1;
  const s = state(),
    k = s.room;
  if (group) {
    if (__TEST__) retired = [group, tree, sky.material.map].map((value) => new WeakRef(value));
    dispose(group);
    group = null;
    tree.clear();
    tree = null;
    ring = null;
    sky.material.map.dispose();
    sky.material.map = null;
    renderer.renderLists.dispose();
    if (musicTheme !== themeKey()) dropMusic();
  }
  movingTrail = null;
  roadPage = 0;
  fixtures = [];
  observation = null;
  surveyImage = null;
  guide = null;
  passage.book = null;
  nodes = {};
  markers = [];
  focus = "";
  // Submit an opaque frame in the headset as well as the desktop canvas.
  await loadingFrame();
  const key = locationKey(),
    theme = themeKey();
  const [model, collision, panorama, booklet] = await Promise.all([
    loadModel(key),
    data.streamed
      ? new T.FileLoader().setResponseType("arraybuffer").loadAsync(data.collision[key])
      : bytes(data.collision[key]),
    new T.TextureLoader().loadAsync(assetURL("skies", theme, "image/jpeg")),
    passage.active
      ? data.streamed
        ? new T.FileLoader().setResponseType("json").loadAsync(data.charts[key])
        : JSON.parse(new TextDecoder().decode(bytes(data.charts[key])))
      : null,
  ]);
  if (booklet) passage.bind(booklet);
  group = model;
  tree = loadCollision(collision);
  const palette = new Map();
  group.traverse((o) => {
    if (o.name) nodes[o.name] = o;
    if (o.name.startsWith("A_")) markers.push(o);
    if (o.isMesh) {
      const old = o.material;
      if (works.active && works.room.early && old.name === key + "Survey") surveyImage = old.map.source.data;
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

  nodes.C_Solids.visible = false;
  scene.add(group);
  if (works.active && works.room.early) {
    const body = new T.Group();
    group.add(body);
    for (const key of ["GuideBird", "GuideLeft", "GuideRight"]) body.attach(nodes[key]);
    guide = {
      body,
      points: [],
      cells: [],
      leg: 0,
      pos: new T.Vector3(),
      heading: new T.Vector3(),
      left: nodes.GuideLeft.rotation.z,
      right: nodes.GuideRight.rotation.z,
    };
    body.visible = false;
  }
  const color =
    key === "Wrenfall"
      ? "#b7d2c2"
      : s.ending
        ? "#efd3a7"
        : passage.active
          ? ["#d3cd9d", "#c7dada", "#af9eab"][k]
          : horizons[k];
  const radius = roomRadius();
  scene.fog = new T.Fog(color, radius * 0.95, radius * 3.25);
  camera.far = Math.max(115, radius * 4);
  camera.updateProjectionMatrix();
  sky.scale.setScalar(camera.far / 115);
  panorama.colorSpace = T.SRGBColorSpace;
  sky.material.map = panorama;
  sky.material.needsUpdate = true;
  // Spread texture uploads over loading frames before returning control to the player.
  const maps = new Set([panorama]);
  palette.forEach((material) => {
    if (material.map) maps.add(material.map);
  });
  let slice = performance.now();
  for (const map of maps) {
    renderer.initTexture(map);
    if (performance.now() - slice >= 3) {
      await loadingFrame();
      slice = performance.now();
    }
  }
  await renderer.compileAsync(scene, camera);
  ring = null;
  resetFeet();
  if (works.active) {
    fixtures = works.room.visuals.map((v) => ({
      v,
      obj: nodes[v.node],
      pos: nodes[v.node].position.clone(),
      rot: nodes[v.node].rotation.clone(),
    }));
    animateWorks(1);
  }
  sync();
  timer = 32;
  focus = "";
  $("prompt").hidden = true;
  $("speech").hidden = true;
  $("chapter").textContent = works.active
    ? works.room.chapter || "The Lower Works"
    : passage.active
      ? "The witness road"
      : s.ending
        ? "Epilogue"
        : k
          ? "Chapter " + ["", "I", "II", "III", "IV"][k]
          : "The Long Meadow";
  $("location").textContent = locationName();
  if (started) playMusic();
  save();
  busy = false;
  $("veil").style.opacity = 0;
}
let movingTrail = null,
  trailTime = 0;
const trailStart = new T.Vector3(),
  fromTile = new T.Vector3(),
  toTile = new T.Vector3();
function chartPoint(out, tile) {
  out.copy(nodes.NW.position);
  out.addScaledVector(step.subVectors(nodes.NE.position, nodes.NW.position), (tile % 7) / 6);
  return out.addScaledVector(
    step.subVectors(nodes.SW.position, nodes.NW.position),
    Math.floor(tile / 7) / 6,
  );
}
let fixtures = [],
  observation = null,
  voyageFraction = 0;
function animateWorks(mix, dt = 0) {
  for (const fixture of fixtures) {
    const { v, obj, pos, rot } = fixture;
    const n = works.signals[v.signal];
    if (v.kind === "show") {
      obj.visible = n === v.match && (v.node !== "CrewAshore" || voyageFraction >= 1);
      continue;
    }
    if (v.kind === "voyage") {
      const t = mix === 1 ? n : Math.min(n, (fixture.fraction || 0) + dt / v.amount);
      fixture.fraction = voyageFraction = t;
      const a = 1 - t;
      obj.position
        .copy(pos)
        .multiplyScalar(a * a)
        .addScaledVector(nodes[v.node + "Turn"].position, 2 * a * t)
        .addScaledVector(nodes[v.node + "Berth"].position, t * t);
      continue;
    }
    if (v.kind === "lift") obj.position.y += (pos.y + n * v.amount - obj.position.y) * mix;
    else {
      const axis = v.kind === "turn" ? "y" : "z",
        target = rot[axis] + (n * v.amount * Math.PI) / 180;
      const diff = target - obj.rotation[axis];
      obj.rotation[axis] += Math.atan2(Math.sin(diff), Math.cos(diff)) * mix;
    }
  }
}
function sync() {
  if (works.active) {
    animateWorks(0);
    return;
  }
  if (passage.active) {
    const page = passage.page,
      pos = passage.piece;
    const map = nodes.Chart.material.map;
    map.repeat.set(1 / 3, 1 / 3);
    map.offset.set((page % 3) / 3, Math.floor(page / 3) / 3);
    chartPoint(nodes.Pawn.position, pos.p);
    nodes.Cargo.visible = pos.c >= 0;
    if (nodes.Cargo.visible) chartPoint(nodes.Cargo.position, pos.c);
    nodes.GateLight.visible = passage.done;
    return;
  }
  const s = state();
  nodes.GateLight.visible = s.room === 0 ? s.commissioned : s.solved && s.room !== 4;
  for (const [name, on] of [
    ["Ina", s.ending === 2],
    ["A_Ina", s.ending === 2],
    ["RoadBook", !!s.ending && !!works.signals.RainCourtArch],
    ["A_RoadBook", !!s.ending && !!works.signals.RainCourtArch],
    ["NightRoll", !!s.ending && !!works.signals.named],
    ["A_Nameplate", !!s.ending && !!works.signals.named],
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
  else say(locationName(), objective(), 8);
}
async function interact(id) {
  if (!started || busy || book || !id) return;
  if (works.active) {
    const station = works.station(id);
    if (id === "A_Book" && nodes.Linnet && works.signals.landed && voyageFraction < 1) {
      say(
        station.label,
        "Her sail is rounding the last stone. Elin will have the book when she makes fast.",
      );
      return;
    }
    if (station.sight && works.signals.charter && !works.signals[station.evidence]) {
      if (observation !== station) {
        observation = station;
        say(station.label, station.direction, 18);
        return;
      }
      if (!bearingClear()) {
        say(station.label, "The mark is outside the sight. " + station.direction, 12);
        return;
      }
      observation = null;
    }
    const name = label(id),
      result = works.use(id);
    if (result.to?.startsWith("#")) {
      resetFeet();
      save();
      say(name, result.line);
      return;
    }
    if (result.to) {
      if (result.to === "@choir") works.progress.active = false;
      if (result.to === "@final") {
        works.progress.active = false;
        number = state().moves.A_Gate[0];
      }
      if (await room()) welcome();
    } else {
      tone(works.station(id).note);
      sync();
      save();
      say(name, result.line, 10);
    }
    return;
  }
  if (id === "A_RoadBook" && state().ending && works.signals.RainCourtArch) {
    const leaf = data.works.roadLeaves[roadPage];
    say(
      leaf.name,
      (state().ending === 1 ? leaf.shared : leaf.freed) + "   •   E / trigger for the next letter.",
      12,
    );
    roadPage = (roadPage + 1) % data.works.roadLeaves.length;
    return;
  }
  if (id === "A_Nameplate" && state().ending && works.signals.named) {
    say(
      "Night roll",
      "Ina, fourth hand of the flood watch. Paid in full. Below the engraving hangs a left-handed pilot’s knot.",
    );
    return;
  }
  if (passage.active) {
    if (id === "A_Gate" && passage.done) {
      number = state().moves.A_Gate[0];
      passage.leave();
      if (state().room === 1) {
        works.progress.chamber = openingWard;
        works.progress.camp = "";
        works.progress.active = true;
      }
      if (await room()) welcome();
      return;
    }
    trailStart.copy(nodes.Pawn.position);
    const line = passage.use(id);
    movingTrail = passage.travel;
    trailTime = performance.now();
    if (id === "A_Talk") gestureEnd = performance.now() + 3000;
    if (id.startsWith("A_Key") || id === "A_Stamp") tone(passage.piece.win ? 0 : 1);
    sync();
    save();
    say(label(id), line, 10);
    return;
  }
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
    secondsByPlace = {};
    passage = new Passage(data.regions, null, 0, 0);
    works = new Underworks(data.works, null, false);
    if (await room()) welcome();
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
  if (
    id === "A_Gate" &&
    graph.states[move[0]].room !== prev.room &&
    prev.room < data.regions.length &&
    prev.room === passage.progress.completed
  ) {
    passage.progress.active = true;
    if (await room()) welcome();
    return;
  }
  if (id === "A_Gate" && prev.room === 3 && graph.states[move[0]].room === 4) {
    works.progress.active = true;
    works.progress.chamber = 0;
    works.progress.camp = "";
    if (await room()) welcome();
    return;
  }
  number = move[0];
  if (id === "A_Letter") leaves |= 1 << prev.room;
  if (prev.room !== state().room) {
    if (await room()) welcome();
    return;
  }
  if (id.startsWith("A_Key") || id === "Toll") {
    tone(id === "Toll" || state().hearts < prev.hearts ? 3 : +id.slice(-1));
    if (prev.room === 4) timer = 24;
  }
  if (!prev.challenged && state().challenged) timer = 32;
  sync();
  save();
  const dedication =
    (id === "A_Roster" || id === "A_Ina") && works.signals.named
      ? " Below it hangs a new brass plate: Ina, fourth hand of the night shift."
      : "";
  const pilotLine =
    (id === "A_Ina" || id === "A_Roster") && state().ending && hasFloodBook()
      ? " " + data.works.logEndings[state().ending - 1]
      : "";
  say(name, move[1] + pilotLine + dedication, id === "A_Talk" || id === "A_Letter" ? 12 : 6);
}
function bearingClear() {
  const origin = vr.session ? vr.head : camera.position;
  if (vr.session) forward.copy(vr.direction);
  else camera.getWorldDirection(forward);
  look.copy(nodes[observation.sight].position).sub(origin);
  const distance = look.length();
  look.normalize();
  if (forward.dot(look) < 0.9984) return false;
  // The near section contains the instrument's barrel and sight rings.
  ray.set(origin, look);
  ray.ray.origin.addScaledVector(look, 3.2);
  const obstacle = tree.rayIntersect(ray.ray);
  if (!obstacle || obstacle.distance >= distance - 4.3) return true;
  // The tall invisible rim prevents climbing out of the map. Distant marks remain visible across it.
  const hit = obstacle.position;
  return Math.max(Math.abs(hit.x), Math.abs(hit.z)) >= roomRadius() - 0.35;
}
function pick() {
  focus = "";
  let best = Infinity;
  const origin = vr.session ? vr.head : camera.position;
  if (vr.session) forward.copy(vr.direction);
  else camera.getWorldDirection(forward);
  if (observation) {
    if (nodes[observation.id].position.distanceTo(origin) <= 4.3) {
      focus = observation.id;
      $("prompt").hidden = false;
      $("prompt").textContent = bearingClear() ? "E   ·   Record this bearing" : "Sight the offshore mark";
      return;
    }
    observation = null;
  }
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
    const hit = tree.rayIntersect(ray.ray, ray.far);
    if (hit && hit.distance < ray.far) continue;
    const weight = passage.active || state().ending ? distance * 0.025 + 20 * (1 - dot) : distance + 4 * (1 - dot);
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
  if (
    capsule.start.y < -1 ||
    Math.max(Math.abs(capsule.start.x), Math.abs(capsule.start.z)) > roomRadius() + 0.65
  )
    resetFeet();
  updateCamera();
}
function callGuide() {
  if (!guide || book || busy) return;
  const origin = nodes.MapSW.position,
    east = nodes.MapSE.position,
    north = nodes.MapNW.position;
  const head = vr.session ? vr.head : camera.position;
  const col = T.MathUtils.clamp(Math.floor((15 * (head.x - origin.x)) / (east.x - origin.x)), 0, 14);
  const row = T.MathUtils.clamp(Math.floor((15 * (head.z - origin.z)) / (north.z - origin.z)), 0, 14);
  const cells = works.guideTrail(col + 15 * row);
  if (!cells.length) return;
  guide.cells = cells;
  guide.points = cells.map(
    (id) =>
      new T.Vector3(
        origin.x + (east.x - origin.x) * (((id % 15) + 0.5) / 15),
        works.room.ground[id] + 1.66,
        origin.z + (north.z - origin.z) * ((Math.floor(id / 15) + 0.5) / 15),
      ),
  );
  guide.leg = 0;
  guide.pos
    .copy(head)
    .addScaledVector(vr.session ? vr.direction : camera.getWorldDirection(guide.heading), 0.55);
  guide.body.visible = true;
  guide.body.position.copy(guide.pos);
}
function flyGuide(dt, t) {
  const { pos, body, points, heading } = guide,
    target = points[guide.leg];
  if (target) {
    heading.subVectors(target, pos);
    const distance = heading.length();
    if (heading.x * heading.x + heading.z * heading.z > 0.002)
      body.rotation.y = Math.atan2(-heading.x, -heading.z);
    if (distance <= 3.4 * dt) {
      pos.copy(target);
      guide.leg++;
    } else pos.addScaledVector(heading, (3.4 * dt) / distance);
  }
  body.position.copy(pos);
  body.position.y += 0.05 * Math.sin(t * 5);
  const flap = 0.49 * Math.sin(t * 18);
  nodes.GuideLeft.rotation.z = guide.left + flap;
  nodes.GuideRight.rotation.z = guide.right - flap;
}
function drawSurvey() {
  const canvas = $("survey");
  canvas.hidden = !surveyImage;
  canvas.closest("article").classList.toggle("survey-open", !!surveyImage);
  if (!surveyImage) return;
  const origin = nodes.MapSW.position,
    east = nodes.MapSE.position,
    north = nodes.MapNW.position;
  const pos = vr.session ? vr.head : capsule.start;
  const u = (pos.x - origin.x) / (east.x - origin.x),
    v = (pos.z - origin.z) / (north.z - origin.z);
  const c = canvas.getContext("2d");
  c.drawImage(surveyImage, 0, 0, 768, 544);
  const x = 16 + 480 * u,
    y = 512 - 480 * v;
  c.fillStyle = "#c83422";
  c.strokeStyle = "#fff8d6";
  c.lineWidth = 3;
  c.beginPath();
  c.arc(x, y, 7, 0, Math.PI * 2);
  c.fill();
  c.stroke();
  c.fillStyle = "#9d211b";
  c.font = "bold 14px sans-serif";
  c.fillText("●  You are here", 515, 443);
  vr.surveyChanged();
}
function toggleBook(open) {
  if (!started || busy) return;
  book = open;
  if (book) observation = null;
  keys.clear();
  $("book").hidden = !open;
  $("hud").hidden = open;
  if (open) {
    document.exitPointerLock?.();
    drawSurvey();
    $("booktitle").textContent = locationName() + "   ·   " + playTime();
    $("objective").textContent = objective() + "   ·   " + state().seals + " of 3 vows";
    $("leaves").replaceChildren();
    if (hasFloodBook()) {
      const page = document.createElement("li");
      page.textContent = data.works.logTitle + "   ·   " + data.works.logEntry;
      $("leaves").append(page);
    }
    if (works.active && !works.room.early) {
      const item = document.createElement("li");
      item.textContent = works.register();
      $("leaves").append(item);
    }
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
    journalPage = 0;
    journalText = [
      $("objective").textContent + "   •   Trigger for next page. A/X to close.",
      ...Array.from($("leaves").children, (li) => li.textContent),
    ];
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
  effects.forEach((a) => (a.muted = muted));
  if (music) music.muted = muted;
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
  if (e.code === "KeyQ") callGuide();
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
  severe = 0,
  slow = 0,
  fast = 0;
function adapt(interval) {
  // UI stays at native resolution. Scale only the 3D buffer on a slow renderer.
  if (interval > 1200 || interval <= 0 || document.hidden) return;
  severe = interval > 100 ? severe + 1 : 0;
  frameWindow++;
  if (interval > 26) slow++;
  if (interval < 19) fast++;
  if (frameWindow < 42 && severe < 8) return;
  let ratio = renderer.getPixelRatio(),
    next = ratio;
  if (severe >= 8 || slow > 23) next = Math.max(0.5, ratio * 0.8);
  else if (fast > 39) next = Math.min(Math.min(devicePixelRatio, 1.5), ratio + 0.05);
  if (Math.abs(next - ratio) > 0.025) {
    renderer.setPixelRatio(next);
    resize();
  }
  frameWindow = 0;
  severe = 0;
  slow = 0;
  fast = 0;
}
function loop(time, frame) {
  const interval = time - previous;
  if (
    started &&
    !busy &&
    !book &&
    !state().ending &&
    interval > 0 &&
    interval < 1000 &&
    (vr.session ? vr.session.visibilityState === "visible" : !document.hidden && document.hasFocus())
  ) {
    const key = locationKey();
    secondsByPlace[key] = (secondsByPlace[key] || 0) + interval / 1000;
  }
  if (previous && !busy && !book && !vr.session) adapt(time - previous);
  const delta = Math.min(0.066, Math.max(0, (time - previous) / 1000));
  previous = time;
  if (busy) {
    renderer.clear();
    if (resolveFrame) {
      const ready = resolveFrame;
      resolveFrame = null;
      ready();
    }
    return;
  }
  if (!group) return;
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
  if (guide?.body.visible && !book) flyGuide(delta, time / 1000);
  if (works.active) animateWorks(1 - Math.exp(-delta * 8), delta);
  if (passage.active && movingTrail) {
    const t = Math.max(0, (time - trailTime) / 90),
      leg = Math.floor(t);
    if (leg < movingTrail.length) {
      const a = leg === 0 ? trailStart : chartPoint(fromTile, movingTrail.charCodeAt(leg - 1) - 65);
      nodes.Pawn.position.lerpVectors(a, chartPoint(toTile, movingTrail.charCodeAt(leg) - 65), t - leg);
    } else {
      chartPoint(nodes.Pawn.position, passage.piece.p);
      movingTrail = null;
    }
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
      ? journalText[journalPage]
      : !$("speech").hidden
        ? $("words").textContent
        : focus
          ? "Press a trigger to interact."
          : !$("clock").hidden
            ? $("clock").textContent
            : "";
    const title = book
      ? "Witness book   ·   " + (journalPage + 1) + "/" + journalText.length
      : !$("speech").hidden
        ? $("act").textContent
        : focus
          ? label(focus)
          : "The keeper calls";
    if (book && surveyImage && journalPage === 0) vr.showSurvey($("survey"));
    else vr.caption(title, text);
  }
  sky.position.copy(vr.session ? vr.head : camera.position);
  renderer.render(scene, camera);
}
if (__TEST__)
  window.bellProbe = () => ({
    number,
    gpu: { ...renderer.info.memory, programs: renderer.info.programs.length },
    retiredAlive: retired?.filter((ref) => ref.deref()).length || 0,
    trees: tree ? 1 : 0,
    music: music ? 1 : 0,
    musicTheme,
    musicGeneration,
    effects: effects.size,
    sets: group && scene.children.includes(group) ? 1 : 0,
    secondsByPlace: { ...secondsByPlace },
    room: state().room,
    district: locationKey(),
    roadBook: !!nodes.RoadBook?.visible,
    dedication: !!nodes.NightRoll?.visible,
    works: works.active ? { ...works.progress, signals: { ...works.signals } } : null,
    passage:
      passage.active && passage.book
        ? { ...passage.progress, hint: passage.piece.hint, win: passage.piece.win }
        : null,
    sight: observation
      ? { target: nodes[observation.sight].position.toArray(), linedUp: bearingClear() }
      : null,
    guide: guide?.body.visible ? { cells: guide.cells, pos: guide.body.position.toArray() } : null,
    vrMap: !!vr.mapMode,
    vessel: nodes.Linnet?.position.toArray(),
    crew: nodes.CrewAshore?.visible,
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
    journalPage,
    journalCaption: book ? journalText[journalPage] : "",
  });
if (__TEST__)
  window.bellTravel = async (index) => {
    if (busy) throw Error("Travel already in progress");
    const expansion = index - graph.rooms.length;
    const chamber = expansion - data.regions.length;
    const early = data.works.rooms[chamber]?.early;
    const base = chamber >= 0 ? (early ? 1 : 3) : expansion >= 0 ? expansion : index;
    const target = graph.states.findIndex(
      (s) => s.room === base && (expansion < 0 || s.commissioned) && (chamber < 0 || early || s.solved),
    );
    if (target < 0 || chamber >= data.works.rooms.length) throw Error("Unknown district");
    number = target;
    passage = new Passage(data.regions, null, base, 0);
    passage.progress.active = expansion >= 0 && chamber < 0;
    works = new Underworks(data.works, { active: chamber >= 0, chamber }, true);
    await room();
  };
renderer.setAnimationLoop(loop);
room()
  .then((loaded) => {
    if (!loaded) return;
    $("start").disabled = $("vr").disabled = false;
    $("start").textContent = number ? "Continue journey" : "Begin journey";
  })
  .catch(fail);
