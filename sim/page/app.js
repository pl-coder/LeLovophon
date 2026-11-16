// Le Lovophon in the browser.
//
// Three layers, each owned by one place:
//   - Python (sim/lovophon via Pyodide): the kinematic models. Called once per
//     frame for the moving-part poses and in a short lookahead for plucks.
//   - three.js: the exported CAD meshes. Node names match the Python poses.
//   - Faust (AudioWorklet): twelve plucked strings. Plucks are scheduled on
//     the audio clock with AudioParam automation.
//
// Two designs share the page as tabs: Paul's current Plucking Layout R5
// (sim/lovophon/r5.py, assets/lovophon_r5.glb) and the earlier Lab Frame
// Ratio Review (sim/lovophon/model.py, assets/lovophon.glb). Each has its own
// model, meshes and pose adapter; strings, tuning, presets and transport are
// shared. Switching tabs returns the machine to turn 0.
//
// Time: the model is always evaluated at the reference 3 rpm. "Machine time"
// T advances at rpm/3 times wall time, so changing the input speed never makes
// a cam jump, and the 480 s repeat stays 480 units of T.

import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const REFERENCE_RPM = 3;

// The two designs. `kinds` are the per-voice node suffixes the adapter poses
// and tints; `minLength` keeps the third bridge on the far side of the pick.
const DESIGNS = {
  r5: {
    key: "r5",
    label: "Plucking Layout R5",
    note: "current, 11 Nov 2026",
    glb: "./assets/lovophon_r5.glb",
    module: "r5",
    kinds: ["crank", "rocker", "coupler"],
    maxLength: 600,
    minLength: (row) => Math.ceil(321 - row.pick_x + 6),
  },
  lab: {
    key: "lab",
    label: "Lab Frame review",
    note: "earlier study, 6 Nov 2026",
    glb: "./assets/lovophon.glb",
    module: "model",
    kinds: ["Driver", "Output", "LongArmRotor", "Rocker"],
    maxLength: 330,
    minLength: (row) => Math.max(40, Math.ceil(320 - row.station + 6)),
  },
};
const DEFAULT_DESIGN = "r5";

// Tuning presets as cents offsets per pentatonic degree (C D E G A) from the
// design's 5-limit just intonation (1, 9/8, 5/4, 3/2, 5/3). Octave voices
// share their degree's offset. Values are rounded to the cent.
const DEGREE_OF_VOICE = [0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1];
const PRESETS = {
  "Just pentatonic (design)": [0, 0, 0, 0, 0],
  "12-tone equal temperament": [0, -4, 14, -2, 16],
  "Pythagorean (3-limit)": [0, 0, 22, 0, 22],
  "Minor pentatonic, just (C Eb F G Bb)": [0, 112, 112, 0, 133],
  "Hirajoshi, just (C D Eb G Ab)": [0, 0, -71, 0, -71],
  "Slendro, five equal steps": [0, 36, 94, 18, 76],
};
const CUSTOM = "Custom";

// One colour per string, used for the glow and the panel swatch.
function voiceColour(v) {
  return new THREE.Color().setHSL(((v * 137.5) % 360) / 360, 0.75, 0.55);
}
const LOOKAHEAD_WALL = 0.5; // seconds of wall clock scheduled ahead
const TRIG_PULSE = 0.006; // seconds the trigger param stays high
const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.27.5/full/";

const ui = {
  status: document.getElementById("status"),
  overlay: document.getElementById("overlay"),
  tabs: document.getElementById("tabs"),
  play: document.getElementById("play"),
  reset: document.getElementById("reset"),
  time: document.getElementById("time"),
  cycle: document.getElementById("cycle"),
  rpm: document.getElementById("rpm"),
  rpmValue: document.getElementById("rpm-value"),
  repeat: document.getElementById("repeat"),
  gain: document.getElementById("gain"),
  t60: document.getElementById("t60"),
  bright: document.getElementById("bright"),
  preset: document.getElementById("preset"),
  voices: document.getElementById("voices"),
  canvas: document.getElementById("view"),
};

const state = {
  py: null,
  designs: {}, // key -> runtime: {cfg, design, model, pyDesign, repeatT, root, nodes, strings, voices, loaded}
  active: null,
  rpm: 3,
  playing: false,
  T: 0, // machine time at reference rpm
  T0: 0,
  elapsed: 0, // wall seconds played, for the readout only
  wall0: 0, // audio-context time when T0 was set
  scheduledT: 0,
  audio: null,
  node: null,
  flashTimers: [],
  switching: false,
};

function setStatus(text) {
  ui.status.textContent = text;
}

// ---------------------------------------------------------------- Python

async function loadModels() {
  setStatus("Loading Pyodide…");
  const pyodide = await loadPyodide({ indexURL: PYODIDE_URL });
  setStatus("Loading sim/lovophon…");
  pyodide.FS.mkdirTree("/sim/lovophon");
  for (const name of ["__init__.py", "model.py", "r5.py", "design.json", "r5_design.json"]) {
    const text = await (await fetch(`../lovophon/${name}`)).text();
    pyodide.FS.writeFile(`/sim/lovophon/${name}`, text);
  }
  pyodide.runPython("import sys, json; sys.path.insert(0, '/')\nfrom sim.lovophon import model, r5");
  state.py = pyodide;
  for (const cfg of Object.values(DESIGNS)) {
    pyodide.runPython(`design_${cfg.key} = ${cfg.module}.load_design()`);
    const D = {
      cfg,
      model: pyodide.globals.get(cfg.module),
      pyDesign: pyodide.globals.get(`design_${cfg.key}`),
      design: JSON.parse(pyodide.runPython(`json.dumps(design_${cfg.key})`)),
      root: null,
      nodes: new Map(),
      strings: [],
      voices: [],
      shaftEnd: null,
      loaded: false,
    };
    D.repeatT = D.model.repeat_seconds(D.pyDesign, REFERENCE_RPM);
    state.designs[cfg.key] = D;
  }
}

function posesFlat(D, T) {
  const proxy = D.model.poses_flat(D.pyDesign, T, REFERENCE_RPM);
  const arr = proxy.toJs();
  proxy.destroy();
  return arr;
}

function eventsFlat(D, T0, T1) {
  const proxy = D.model.events_flat(D.pyDesign, T0, T1, REFERENCE_RPM);
  const arr = proxy.toJs();
  proxy.destroy();
  return arr;
}

// ---------------------------------------------------------------- 3D

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf4efe6);
const camera = new THREE.PerspectiveCamera(35, 1, 0.01, 20);
const renderer = new THREE.WebGLRenderer({ canvas: ui.canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
scene.add(new THREE.HemisphereLight(0xffffff, 0x8a7a66, 1.1));
const key = new THREE.DirectionalLight(0xffffff, 1.6);
key.position.set(0.5, 0.8, 0.9);
scene.add(key);
const fill = new THREE.DirectionalLight(0xffffff, 0.5);
fill.position.set(-0.6, 0.3, -0.4);
scene.add(fill);

function resize() {
  const w = ui.canvas.clientWidth;
  const h = ui.canvas.clientHeight;
  if (ui.canvas.width !== w || ui.canvas.height !== h) {
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
}

async function loadMeshes(D) {
  setStatus(`Loading ${D.cfg.label} meshes…`);
  const gltf = await new GLTFLoader().loadAsync(D.cfg.glb);
  const root = gltf.scene;
  // A glTF node with several primitives becomes a Group named after the node
  // with one Mesh per primitive, so register every named object, not meshes.
  root.traverse((o) => {
    if (o.name && !D.nodes.has(o.name)) D.nodes.set(o.name, o);
  });
  // Nodes placed at their rotation centre keep that as a base position.
  for (const node of D.nodes.values()) node.userData.base = node.position.clone();
  root.visible = false;
  scene.add(root);
  D.root = root;
  if (D.cfg.key === "lab") {
    const staticNode = D.nodes.get("static");
    const extras = (staticNode && staticNode.userData) || {};
    buildShaftEnd(D, extras.input_shaft_mm);
  }
  buildStrings(D);
  D.loaded = true;
}

function frameCamera(D) {
  const box = new THREE.Box3().setFromObject(D.root);
  const centre = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3()).length();
  camera.position.copy(centre).add(new THREE.Vector3(0.45, 0.5, 1.0).multiplyScalar(size * 1.05));
  controls.target.copy(centre);
  controls.update();
}

// The tuning end of the Lab Frame's input shaft, outboard of where the CAD
// shaft stops (x_max): a brass extension carrying the worm for the cycle
// dial, a bearing block, and a crank handle so the shaft speed can be read at
// a glance. All dimensions in mm; the group is scaled once. Visual aids: the
// real machine has none of this. R5 has Paul's own hand crank and gets none.
const WHEEL_TEETH = 24; // worm wheel, one turn per 24-turn cycle
const WHEEL_PITCH_R = 12;
const WORM_PITCH_R = 5;

function buildShaftEnd(D, shaft) {
  if (!shaft) return;
  const brass = new THREE.MeshStandardMaterial({ color: 0xc29645, metalness: 0.4, roughness: 0.45 });
  const steel = new THREE.MeshStandardMaterial({ color: 0x9aa0a6, metalness: 0.6, roughness: 0.4 });
  const plate = new THREE.MeshStandardMaterial({ color: 0x6f7378, metalness: 0.3, roughness: 0.6 });
  const knobMat = new THREE.MeshStandardMaterial({ color: 0x2b2622, roughness: 0.8 });
  const x0 = shaft.x_max;
  const ay = shaft.y;
  const az = shaft.z;
  const g = new THREE.Group();
  g.scale.setScalar(0.001);
  const alongX = [0, 0, Math.PI / 2];
  const mesh = (parent, geom, mat, x, y, z, rot) => {
    const m = new THREE.Mesh(geom, mat);
    m.position.set(x, y, z);
    if (rot) m.rotation.set(rot[0], rot[1], rot[2]);
    parent.add(m);
    return m;
  };
  const xWorm = x0 + 8;
  const xBearing = x0 + 17.5;
  const xHub = x0 + 23;
  // Shaft extension and everything keyed to it.
  const shaftGroup = new THREE.Group();
  shaftGroup.position.set(0, ay, az);
  mesh(shaftGroup, new THREE.CylinderGeometry(3, 3, xHub - x0 + 2, 20), brass, x0 + (xHub - x0 + 2) / 2, 0, 0, alongX);
  const worm = new THREE.Mesh(wormGeometry(0.008, 0.0036, 0.0016, Math.PI / 1000), brass);
  worm.scale.setScalar(1000); // wormGeometry is in metres
  worm.position.x = xWorm;
  shaftGroup.add(worm);
  mesh(shaftGroup, new THREE.CylinderGeometry(6, 6, 6, 24), brass, xHub, 0, 0, alongX);
  mesh(shaftGroup, new THREE.BoxGeometry(4, 36, 8), brass, xHub + 4, 15, 0);
  mesh(shaftGroup, new THREE.CylinderGeometry(2, 2, 12, 16), brass, xHub + 11, 30, 0, alongX);
  mesh(shaftGroup, new THREE.CylinderGeometry(4, 4.5, 16, 20), knobMat, xHub + 23, 30, 0, alongX);
  g.add(shaftGroup);
  // Bearing block on a short post between worm and handle.
  mesh(g, new THREE.CylinderGeometry(4.5, 4.5, 5, 24), steel, xBearing, ay, az, alongX);
  mesh(g, new THREE.BoxGeometry(5, 14, 10), plate, xBearing, ay - 11, az);
  mesh(g, new THREE.BoxGeometry(12, 3, 16), plate, xBearing, ay - 19.5, az);
  // Worm wheel and cycle dial above the worm, face toward the front.
  const dial = new THREE.Group();
  dial.position.set(xWorm, ay + WORM_PITCH_R + WHEEL_PITCH_R, az);
  const rotor = new THREE.Group();
  mesh(rotor, new THREE.CylinderGeometry(WHEEL_PITCH_R - 1, WHEEL_PITCH_R - 1, 4, 48), brass, 0, 0, 0, [Math.PI / 2, 0, 0]);
  for (let i = 0; i < WHEEL_TEETH; i++) {
    const a = (i / WHEEL_TEETH) * 2 * Math.PI;
    mesh(rotor, new THREE.BoxGeometry(1.6, 2.2, 4), brass, Math.cos(a) * (WHEEL_PITCH_R - 0.2), Math.sin(a) * (WHEEL_PITCH_R - 0.2), 0, [0, 0, a]);
  }
  mesh(rotor, new THREE.BoxGeometry(0.8, 10.5, 0.6), new THREE.MeshStandardMaterial({ color: 0xc0392b, roughness: 0.5 }), 0, 4.5, 3.6);
  mesh(rotor, new THREE.CylinderGeometry(1.2, 1.2, 1.2, 16), knobMat, 0, 0, 3.6, [Math.PI / 2, 0, 0]);
  mesh(dial, new THREE.CylinderGeometry(11.8, 11.8, 0.8, 48), new THREE.MeshStandardMaterial({ color: 0xf3ead8, roughness: 0.9 }), 0, 0, 2.6, [Math.PI / 2, 0, 0]);
  const ink = new THREE.MeshStandardMaterial({ color: 0x2b2622 });
  for (let i = 0; i < WHEEL_TEETH; i++) {
    const major = i % 6 === 0;
    const a = Math.PI / 2 - (i / WHEEL_TEETH) * 2 * Math.PI;
    const rr = 10.8 - (major ? 1.1 : 0.6);
    mesh(dial, new THREE.BoxGeometry(0.5, major ? 2.2 : 1.2, 0.4), ink, Math.cos(a) * rr, Math.sin(a) * rr, 3.2, [0, 0, a - Math.PI / 2]);
  }
  mesh(dial, new THREE.CylinderGeometry(1.5, 1.5, 12, 16), brass, 0, 0, 0, [Math.PI / 2, 0, 0]);
  dial.add(rotor);
  g.add(dial);
  D.root.add(g);
  D.shaftEnd = { shaft: shaftGroup, dial: rotor };
}

function wormGeometry(length, rCore, depth, pitch, axial = 96, around = 48) {
  const positions = [];
  const indices = [];
  const radiusAt = (x, phi) => {
    const t = ((x / pitch - phi / (2 * Math.PI)) % 1 + 1) % 1; // 0..1 along one thread
    const tri = 1 - Math.abs(2 * t - 1); // 0 at root, 1 at crest
    const flank = Math.min(1, Math.max(0, (tri - 0.2) / 0.5)); // flat root and crest
    return rCore + depth * flank;
  };
  for (let i = 0; i <= axial; i++) {
    const x = -length / 2 + (i / axial) * length;
    for (let j = 0; j <= around; j++) {
      const phi = (j / around) * 2 * Math.PI;
      const r = radiusAt(x, phi);
      positions.push(x, r * Math.cos(phi), r * Math.sin(phi));
    }
  }
  const row = around + 1;
  for (let i = 0; i < axial; i++) {
    for (let j = 0; j < around; j++) {
      const a = i * row + j;
      indices.push(a, a + row, a + 1, a + 1, a + row, a + row + 1);
    }
  }
  // End caps: a centre vertex fanned to the rim.
  for (const [i, sign] of [[0, -1], [axial, 1]]) {
    const centre = positions.length / 3;
    positions.push(sign * length / 2, 0, 0);
    for (let j = 0; j < around; j++) {
      const a = i * row + j;
      const b = i * row + j + 1;
      if (sign < 0) indices.push(centre, b, a);
      else indices.push(centre, a, b);
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geo.setIndex(indices);
  geo.computeVertexNormals();
  return geo;
}

// Worm wheel, 24 teeth, on a Z axis above the worm, carrying a needle over a
// dial with 24 ticks: one tick per shaft turn, one needle turn per cycle.
// Single-start worm + 24-tooth wheel = 24:1 in one step, which is exactly
// the ratio denominators' LCM, so no second reduction is needed.
function applyShaftEnd(D, shaftDeg) {
  const e = D.shaftEnd;
  if (!e) return;
  const theta = THREE.MathUtils.degToRad(shaftDeg);
  e.shaft.rotation.x = theta;
  // Worm wheel turns 1/24 of the shaft; clockwise seen from the front.
  e.dial.rotation.z = theta / WHEEL_TEETH;
}

// Each speaking string keeps its own material; a transparent coloured halo
// around it, invisible at rest, lights up when the string is plucked. The
// voice's moving groups are tinted in the same colour.
function buildStrings(D) {
  D.design.voices.forEach((row, v) => {
    const tint = new THREE.MeshStandardMaterial({ color: voiceColour(v), metalness: 0.25, roughness: 0.5 });
    for (const kind of D.cfg.kinds) {
      const part = D.nodes.get(`${row.note}_${kind}`);
      if (part) part.traverse((o) => { if (o.isMesh) o.material = tint; });
    }
    const node = D.nodes.get(`${row.note}_string`);
    if (!node) return;
    const box = new THREE.Box3().setFromObject(node);
    const centre = box.getCenter(new THREE.Vector3());
    const length = box.max.x - box.min.x;
    const material = new THREE.MeshBasicMaterial({ color: voiceColour(v), transparent: true, opacity: 0, depthWrite: false });
    const halo = new THREE.Mesh(new THREE.CylinderGeometry(0.0022, 0.0022, length, 12), material);
    halo.rotation.z = Math.PI / 2;
    halo.position.copy(centre);
    halo.visible = false;
    D.root.add(halo);
    D.strings[v] = { halo, material, glow: 0 };
  });
}

function decayGlow(D, dt) {
  for (const s of D.strings) {
    if (!s || !s.halo.visible) continue;
    s.glow *= Math.exp(-dt / 0.35);
    s.material.opacity = 0.85 * s.glow;
    const r = 0.6 + 0.8 * s.glow;
    s.halo.scale.set(r, 1, r);
    if (s.glow < 0.02) s.halo.visible = false;
  }
}

// Pose adapters: how each design's flat pose array maps onto its nodes.
const deg = THREE.MathUtils.degToRad;

function applyPosesLab(D, flat) {
  const voices = D.design.voices;
  const kinds = D.cfg.kinds;
  applyShaftEnd(D, flat[3]);
  for (let v = 0; v < voices.length; v++) {
    for (let k = 0; k < kinds.length; k++) {
      const node = D.nodes.get(`${voices[v].note}_${kinds[k]}`);
      if (!node) continue;
      const i = (v * kinds.length + k) * 4;
      node.position.set(flat[i] / 1000, flat[i + 1] / 1000, flat[i + 2] / 1000);
      node.rotation.set(deg(flat[i + 3]), 0, 0);
    }
  }
}

// R5: per voice [input_deg, crank_deg, rocker_deg, coupler_deg, dy, dz]. Each
// node sits at its own rotation centre, so a pose is a rotation about X; the
// coupler also translates with the crank pin.
function applyPosesR5(D, flat) {
  const voices = D.design.voices;
  const input = D.nodes.get("input");
  if (input) input.rotation.set(deg(flat[0]), 0, 0);
  for (let v = 0; v < voices.length; v++) {
    const i = v * 6;
    const note = voices[v].note;
    const crank = D.nodes.get(`${note}_crank`);
    if (crank) crank.rotation.set(deg(flat[i + 1]), 0, 0);
    const rocker = D.nodes.get(`${note}_rocker`);
    if (rocker) rocker.rotation.set(deg(flat[i + 2]), 0, 0);
    const coupler = D.nodes.get(`${note}_coupler`);
    if (coupler) {
      coupler.rotation.set(deg(flat[i + 3]), 0, 0);
      const b = coupler.userData.base;
      coupler.position.set(b.x, b.y + flat[i + 4] / 1000, b.z + flat[i + 5] / 1000);
    }
  }
}

function applyPoses(T) {
  const D = state.active;
  if (!D || !D.loaded) return;
  const flat = posesFlat(D, T);
  if (D.cfg.key === "lab") applyPosesLab(D, flat);
  else applyPosesR5(D, flat);
}

function applyBridge(v) {
  const D = state.active;
  const row = D.design.voices[v];
  const node = D.nodes.get(`${row.note}_bridge`);
  if (node) node.position.x = (row.speaking_length - D.voices[v].lengthMm) / 1000;
}

// ---------------------------------------------------------------- Audio

async function loadAudio() {
  setStatus("Loading Faust strings…");
  const ctx = new AudioContext();
  const [wasm, json] = await Promise.all([
    fetch("./dsp/lovophon.wasm").then((r) => r.arrayBuffer()),
    fetch("./dsp/lovophon.json").then((r) => r.json()),
  ]);
  const module = await WebAssembly.compile(wasm);
  await ctx.audioWorklet.addModule("./faust-worklet.js");
  const node = new AudioWorkletNode(ctx, "lovophon-faust", {
    numberOfInputs: 0,
    numberOfOutputs: 1,
    outputChannelCount: [2],
    processorOptions: { module, json },
  });
  node.connect(ctx.destination);
  const analyser = ctx.createAnalyser();
  analyser.fftSize = 2048;
  node.connect(analyser);
  state.audio = ctx;
  state.node = node;
  state.analyser = analyser;
  setStatus("");
  param("gain").value = parseFloat(ui.gain.value);
  param("t60").value = parseFloat(ui.t60.value);
  param("bright").value = parseFloat(ui.bright.value);
  for (let v = 0; v < 12; v++) param(`freq${v}`).value = voiceFrequency(v);
}

function param(name) {
  return state.node.parameters.get(name);
}

function voiceFrequency(v) {
  const D = state.active;
  const row = D.design.voices[v];
  const s = D.voices[v];
  return s.tuningHz * row.speaking_length / s.lengthMm;
}

// Machine time T -> audio clock time.
function wallTimeOf(T) {
  return state.wall0 + (T - state.T0) * (REFERENCE_RPM / state.rpm);
}

function currentT() {
  if (!state.playing) return state.T;
  return state.T0 + (state.audio.currentTime - state.wall0) * (state.rpm / REFERENCE_RPM);
}

function scheduleAhead() {
  const D = state.active;
  const T = currentT();
  const horizon = T + LOOKAHEAD_WALL * (state.rpm / REFERENCE_RPM);
  if (state.scheduledT >= horizon) return;
  const from = Math.max(state.scheduledT, T);
  const flat = eventsFlat(D, from, horizon);
  for (let i = 0; i < flat.length; i += 3) {
    const Te = flat[i];
    const v = flat[i + 1] | 0;
    const crossing = flat[i + 2] | 0;
    const at = Math.max(state.audio.currentTime, wallTimeOf(Te));
    param(`dir${v}`).setValueAtTime(crossing === 1 ? 1 : -1, at);
    param(`trig${v}`).setValueAtTime(1, at);
    param(`trig${v}`).setValueAtTime(0, at + TRIG_PULSE);
    const delay = Math.max(0, (at - state.audio.currentTime) * 1000);
    // Pitch is read when the pluck happens, not when it is scheduled, so a
    // slider moved inside the lookahead window still takes effect.
    state.flashTimers.push(setTimeout(() => {
      if (state.node) param(`freq${v}`).setValueAtTime(voiceFrequency(v), state.audio.currentTime);
      flash(v);
    }, Math.max(0, delay - 20)));
  }
  state.scheduledT = horizon;
}

function cancelScheduled() {
  if (!state.node) return;
  const now = state.audio.currentTime;
  for (let v = 0; v < 12; v++) {
    for (const p of [`trig${v}`, `dir${v}`]) {
      param(p).cancelScheduledValues(now);
    }
    param(`trig${v}`).setValueAtTime(0, now);
  }
  for (const t of state.flashTimers) clearTimeout(t);
  state.flashTimers = [];
  state.scheduledT = currentT();
}

// Re-anchor machine time so a speed change is continuous.
function rebase() {
  const T = currentT();
  state.T0 = T;
  state.T = T;
  state.wall0 = state.audio ? state.audio.currentTime : 0;
}

function pause() {
  if (!state.playing) return;
  state.T = currentT();
  state.playing = false;
  cancelScheduled();
  ui.play.textContent = "Play";
}

function resetTime() {
  state.T = 0;
  state.T0 = 0;
  state.elapsed = 0;
  if (state.audio) {
    state.wall0 = state.audio.currentTime;
    cancelScheduled();
    state.node.port.postMessage({ type: "clear" });
  }
  state.scheduledT = 0;
}

// ---------------------------------------------------------------- UI

function flash(v) {
  const row = ui.voices.children[v];
  if (row) {
    row.classList.add("pluck");
    setTimeout(() => row.classList.remove("pluck"), 180);
  }
  const s = state.active.strings[v];
  if (s) {
    s.glow = 1;
    s.material.opacity = 0.85;
    s.halo.scale.set(1.4, 1, 1.4);
    s.halo.visible = true;
  }
}

function applyPreset(name) {
  const offsets = PRESETS[name];
  if (!offsets) return;
  state.active.design.voices.forEach((row, v) => {
    const tune = document.getElementById(`tune-${v}`);
    tune.value = String(offsets[DEGREE_OF_VOICE[v]]);
    tune.dispatchEvent(new Event("input", { bubbles: false }));
  });
  ui.preset.value = name;
}

function buildPresetMenu() {
  ui.preset.innerHTML = "";
  for (const name of [...Object.keys(PRESETS), CUSTOM]) {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    ui.preset.appendChild(opt);
  }
  ui.preset.addEventListener("change", () => {
    if (ui.preset.value !== CUSTOM) applyPreset(ui.preset.value);
  });
}

function buildVoiceRows() {
  const D = state.active;
  ui.voices.innerHTML = "";
  D.design.voices.forEach((row, v) => {
    D.voices[v] = { tuningHz: row.frequency_hz, lengthMm: row.speaking_length };
    const minLength = D.cfg.minLength(row);
    const el = document.createElement("div");
    el.className = "voice";
    el.style.setProperty("--voice", `#${voiceColour(v).getHexString()}`);
    el.innerHTML = `
      <div class="voice-head">
        <i class="swatch"></i>
        <b>${row.display_note}</b>
        <span class="ratio">${row.ratio_exact}</span>
        <span class="teeth">${row.driver_teeth}/${row.driven_teeth}</span>
        <span class="hz" id="hz-${v}"></span>
      </div>
      <label>tuning <input type="range" id="tune-${v}" min="-150" max="150" step="1" value="0"><span id="tune-val-${v}">0 ¢</span></label>
      <label>bridge <input type="range" id="len-${v}" min="${minLength}" max="${D.cfg.maxLength}" step="0.5" value="${row.speaking_length}"><span id="len-val-${v}">${row.speaking_length.toFixed(1)} mm</span></label>`;
    ui.voices.appendChild(el);
    const tune = el.querySelector(`#tune-${v}`);
    const len = el.querySelector(`#len-${v}`);
    const refresh = () => {
      const cents = parseFloat(tune.value);
      D.voices[v].tuningHz = row.frequency_hz * Math.pow(2, cents / 1200);
      D.voices[v].lengthMm = parseFloat(len.value);
      el.querySelector(`#tune-val-${v}`).textContent = `${cents >= 0 ? "+" : ""}${cents} ¢`;
      el.querySelector(`#len-val-${v}`).textContent = `${D.voices[v].lengthMm.toFixed(1)} mm`;
      el.querySelector(`#hz-${v}`).textContent = `${voiceFrequency(v).toFixed(2)} Hz`;
      applyBridge(v);
      if (state.node) param(`freq${v}`).setValueAtTime(voiceFrequency(v), state.audio.currentTime);
    };
    tune.addEventListener("input", refresh);
    // A hand-moved tuning slider turns the preset menu to Custom; applyPreset
    // dispatches a non-bubbling event and then restores its own name.
    tune.addEventListener("input", (e) => {
      if (e.isTrusted) ui.preset.value = CUSTOM;
    });
    len.addEventListener("input", refresh);
    refresh();
  });
  ui.preset.value = Object.keys(PRESETS)[0];
}

function buildTabs() {
  ui.tabs.innerHTML = "";
  for (const cfg of Object.values(DESIGNS)) {
    const b = document.createElement("button");
    b.className = "tab";
    b.dataset.design = cfg.key;
    b.innerHTML = `${cfg.label}<small>${cfg.note}</small>`;
    b.addEventListener("click", () => activate(cfg.key));
    ui.tabs.appendChild(b);
  }
}

// Switch designs: stop, return to turn 0, show the other meshes (loading
// them on first use), rebuild the voice rows and frame the camera.
async function activate(key) {
  if (state.switching) return;
  const D = state.designs[key];
  if (!D || D === state.active) return;
  state.switching = true;
  try {
    pause();
    resetTime();
    if (state.active && state.active.root) state.active.root.visible = false;
    state.active = D;
    if (!D.loaded) {
      ui.overlay.classList.remove("hidden");
      await loadMeshes(D);
      setStatus("");
      ui.overlay.classList.add("hidden");
    }
    D.root.visible = true;
    buildVoiceRows();
    applyPoses(0);
    frameCamera(D);
    for (const b of ui.tabs.children) b.classList.toggle("active", b.dataset.design === key);
    document.body.dataset.design = key;
  } catch (err) {
    console.error(err);
    setStatus(`Failed: ${err.message}`);
  } finally {
    state.switching = false;
  }
}

function updateReadouts() {
  const D = state.active;
  if (!D) return;
  const T = currentT();
  const turns = T / (60 / REFERENCE_RPM);
  const repeatTurns = D.repeatT / (60 / REFERENCE_RPM);
  const repeatWall = D.repeatT * (REFERENCE_RPM / state.rpm);
  ui.time.textContent = `${state.elapsed.toFixed(1)} s · turn ${(turns % repeatTurns).toFixed(2)} / ${repeatTurns}`;
  ui.cycle.style.width = `${((T % D.repeatT) / D.repeatT) * 100}%`;
  ui.repeat.textContent = `repeat ${repeatWall.toFixed(0)} s at ${state.rpm} rpm`;
}

async function ensureAudio() {
  // Memoised so two quick clicks cannot build two audio engines.
  if (!state.audioReady) state.audioReady = loadAudio();
  await state.audioReady;
  if (state.audio.state !== "running") await state.audio.resume();
}

ui.play.addEventListener("click", async () => {
  if (state.busy || state.switching) return;
  state.busy = true;
  try {
    await ensureAudio();
  } finally {
    state.busy = false;
  }
  if (state.playing) {
    pause();
  } else {
    state.T0 = state.T;
    state.wall0 = state.audio.currentTime;
    state.scheduledT = state.T;
    state.playing = true;
    ui.play.textContent = "Pause";
    // Schedule from a timer as well as from frames, so a background tab
    // (where requestAnimationFrame stalls) keeps plucking.
    if (!state.scheduler) state.scheduler = setInterval(() => state.playing && scheduleAhead(), 100);
  }
});

ui.reset.addEventListener("click", resetTime);

ui.rpm.addEventListener("input", () => {
  if (state.audio) {
    rebase();
    cancelScheduled();
  }
  state.rpm = parseFloat(ui.rpm.value);
  ui.rpmValue.textContent = `${state.rpm.toFixed(1)} rpm`;
  if (state.audio) {
    rebase();
    state.scheduledT = state.T;
  }
});

for (const name of ["gain", "t60", "bright"]) {
  ui[name].addEventListener("input", () => {
    if (state.node) param(name).setValueAtTime(parseFloat(ui[name].value), state.audio.currentTime);
  });
}

// ---------------------------------------------------------------- Loop

function frame(now) {
  requestAnimationFrame(frame);
  try {
    resize();
    if (state.playing) {
      if (state.lastFrame !== undefined) state.elapsed += (now - state.lastFrame) / 1000;
      scheduleAhead();
    }
    const dt = state.lastFrame === undefined ? 0 : (now - state.lastFrame) / 1000;
    state.lastFrame = now;
    if (state.active) decayGlow(state.active, Math.min(dt, 0.1));
    applyPoses(currentT());
    updateReadouts();
    controls.update();
    renderer.render(scene, camera);
  } catch (err) {
    console.error("frame", err);
    setStatus(`Frame error: ${err.message}`);
  }
}

async function main() {
  try {
    buildTabs();
    buildPresetMenu();
    await loadModels();
    await activate(DEFAULT_DESIGN);
    ui.rpmValue.textContent = `${state.rpm.toFixed(1)} rpm`;
    setStatus("");
    ui.overlay.classList.add("hidden");
    ui.play.disabled = false;
    ui.reset.disabled = false;
    requestAnimationFrame(frame);
  } catch (err) {
    console.error(err);
    setStatus(`Failed: ${err.message}`);
  }
}

// Peak output level over the last analyser window, for checks from the console.
state.peak = () => {
  if (!state.analyser) return null;
  const buf = new Float32Array(state.analyser.fftSize);
  state.analyser.getFloatTimeDomainData(buf);
  let peak = 0;
  for (const x of buf) peak = Math.max(peak, Math.abs(x));
  return peak;
};
state.activate = activate;
state.camera = camera;
state.controls = controls;
window.lovophon = state;

main();
