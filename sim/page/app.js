// Le Lovophon in the browser.
//
// Three layers, each owned by one place:
//   - Python (sim/lovophon via Pyodide): the kinematic model. Called once per
//     frame for the 48 moving-part poses and in a short lookahead for plucks.
//   - three.js: the exported CAD meshes. Node names match sim/lovophon poses.
//   - Faust (AudioWorklet): twelve plucked strings. Plucks are scheduled on
//     the audio clock with AudioParam automation.
//
// Time: the model is always evaluated at the reference 3 rpm. "Machine time"
// T advances at rpm/3 times wall time, so changing the input speed never makes
// a cam jump, and the 480 s repeat stays 480 units of T.

import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const REFERENCE_RPM = 3;
const KINDS = ["Driver", "Output", "LongArmRotor", "Rocker"];
const LOOKAHEAD_WALL = 0.5; // seconds of wall clock scheduled ahead
const TRIG_PULSE = 0.006; // seconds the trigger param stays high
const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.27.5/full/";

const ui = {
  status: document.getElementById("status"),
  overlay: document.getElementById("overlay"),
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
  voices: document.getElementById("voices"),
  canvas: document.getElementById("view"),
};

const state = {
  design: null,
  py: null,
  model: null,
  rpm: 3,
  playing: false,
  T: 0, // machine time at reference rpm
  T0: 0,
  elapsed: 0, // wall seconds played, for the readout only
  wall0: 0, // audio-context time when T0 was set
  scheduledT: 0,
  voices: [], // per-voice UI state: tuningHz, lengthMm
  nodes: new Map(),
  audio: null,
  node: null,
  flashTimers: [],
};

function setStatus(text) {
  ui.status.textContent = text;
}

// ---------------------------------------------------------------- Python

async function loadModel() {
  setStatus("Loading Pyodide…");
  const pyodide = await loadPyodide({ indexURL: PYODIDE_URL });
  setStatus("Loading sim/lovophon…");
  pyodide.FS.mkdirTree("/sim/lovophon");
  for (const name of ["__init__.py", "model.py", "design.json"]) {
    const text = await (await fetch(`../lovophon/${name}`)).text();
    pyodide.FS.writeFile(`/sim/lovophon/${name}`, text);
  }
  pyodide.runPython("import sys; sys.path.insert(0, '/')\nfrom sim.lovophon import model\ndesign = model.load_design()");
  state.py = pyodide;
  state.model = pyodide.globals.get("model");
  state.design = JSON.parse(pyodide.runPython("import json; json.dumps(design)"));
  state.pyDesign = pyodide.globals.get("design");
  state.repeatT = state.model.repeat_seconds(state.pyDesign, REFERENCE_RPM);
}

function posesFlat(T) {
  const proxy = state.model.poses_flat(state.pyDesign, T, REFERENCE_RPM);
  const arr = proxy.toJs();
  proxy.destroy();
  return arr;
}

function eventsFlat(T0, T1) {
  const proxy = state.model.events_flat(state.pyDesign, T0, T1, REFERENCE_RPM);
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

async function loadMeshes() {
  setStatus("Loading CAD meshes…");
  const gltf = await new GLTFLoader().loadAsync("./assets/lovophon.glb");
  const root = gltf.scene;
  // A glTF node with several primitives becomes a Group named after the node
  // with one Mesh per primitive, so register every named object, not meshes.
  root.traverse((o) => {
    if (o.name && !state.nodes.has(o.name)) state.nodes.set(o.name, o);
  });
  scene.add(root);
  const box = new THREE.Box3().setFromObject(root);
  const centre = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3()).length();
  camera.position.copy(centre).add(new THREE.Vector3(0.45, 0.5, 1.0).multiplyScalar(size * 0.95));
  controls.target.copy(centre);
  controls.update();
}

function applyPoses(T) {
  const flat = posesFlat(T);
  const voices = state.design.voices;
  for (let v = 0; v < voices.length; v++) {
    for (let k = 0; k < KINDS.length; k++) {
      const node = state.nodes.get(`${voices[v].note}_${KINDS[k]}`);
      if (!node) continue;
      const i = (v * KINDS.length + k) * 4;
      node.position.set(flat[i] / 1000, flat[i + 1] / 1000, flat[i + 2] / 1000);
      node.rotation.set(THREE.MathUtils.degToRad(flat[i + 3]), 0, 0);
    }
  }
}

function applyBridge(v) {
  const row = state.design.voices[v];
  const node = state.nodes.get(`${row.note}_bridge`);
  if (node) node.position.x = (row.speaking_length - state.voices[v].lengthMm) / 1000;
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
  const row = state.design.voices[v];
  const s = state.voices[v];
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
  const T = currentT();
  const horizon = T + LOOKAHEAD_WALL * (state.rpm / REFERENCE_RPM);
  if (state.scheduledT >= horizon) return;
  const from = Math.max(state.scheduledT, T);
  const flat = eventsFlat(from, horizon);
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

// ---------------------------------------------------------------- UI

function flash(v) {
  const row = ui.voices.children[v];
  if (!row) return;
  row.classList.add("pluck");
  setTimeout(() => row.classList.remove("pluck"), 180);
}

function buildVoiceRows() {
  ui.voices.innerHTML = "";
  state.design.voices.forEach((row, v) => {
    state.voices[v] = { tuningHz: row.frequency_hz, lengthMm: row.speaking_length };
    const minLength = Math.max(40, Math.ceil(320 - row.station + 6));
    const el = document.createElement("div");
    el.className = "voice";
    el.innerHTML = `
      <div class="voice-head">
        <b>${row.display_note}</b>
        <span class="ratio">${row.ratio_exact}</span>
        <span class="teeth">${row.driver_teeth}/${row.driven_teeth}</span>
        <span class="hz" id="hz-${v}"></span>
      </div>
      <label>tuning <input type="range" id="tune-${v}" min="-100" max="100" step="1" value="0"><span id="tune-val-${v}">0 ¢</span></label>
      <label>bridge <input type="range" id="len-${v}" min="${minLength}" max="330" step="0.5" value="${row.speaking_length}"><span id="len-val-${v}">${row.speaking_length.toFixed(1)} mm</span></label>`;
    ui.voices.appendChild(el);
    const tune = el.querySelector(`#tune-${v}`);
    const len = el.querySelector(`#len-${v}`);
    const refresh = () => {
      const cents = parseFloat(tune.value);
      state.voices[v].tuningHz = row.frequency_hz * Math.pow(2, cents / 1200);
      state.voices[v].lengthMm = parseFloat(len.value);
      el.querySelector(`#tune-val-${v}`).textContent = `${cents >= 0 ? "+" : ""}${cents} ¢`;
      el.querySelector(`#len-val-${v}`).textContent = `${state.voices[v].lengthMm.toFixed(1)} mm`;
      el.querySelector(`#hz-${v}`).textContent = `${voiceFrequency(v).toFixed(2)} Hz`;
      applyBridge(v);
      if (state.node) param(`freq${v}`).setValueAtTime(voiceFrequency(v), state.audio.currentTime);
    };
    tune.addEventListener("input", refresh);
    len.addEventListener("input", refresh);
    refresh();
  });
}

function updateReadouts() {
  const T = currentT();
  const turns = T / (60 / REFERENCE_RPM);
  const repeatTurns = state.repeatT / (60 / REFERENCE_RPM);
  const repeatWall = state.repeatT * (REFERENCE_RPM / state.rpm);
  ui.time.textContent = `${state.elapsed.toFixed(1)} s · turn ${(turns % repeatTurns).toFixed(2)} / ${repeatTurns}`;
  ui.cycle.style.width = `${((T % state.repeatT) / state.repeatT) * 100}%`;
  ui.repeat.textContent = `repeat ${repeatWall.toFixed(0)} s at ${state.rpm} rpm`;
}

async function ensureAudio() {
  // Memoised so two quick clicks cannot build two audio engines.
  if (!state.audioReady) state.audioReady = loadAudio();
  await state.audioReady;
  if (state.audio.state !== "running") await state.audio.resume();
}

ui.play.addEventListener("click", async () => {
  if (state.busy) return;
  state.busy = true;
  try {
    await ensureAudio();
  } finally {
    state.busy = false;
  }
  if (state.playing) {
    state.T = currentT();
    state.playing = false;
    cancelScheduled();
    ui.play.textContent = "Play";
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

ui.reset.addEventListener("click", () => {
  state.T = 0;
  state.T0 = 0;
  state.elapsed = 0;
  if (state.audio) {
    state.wall0 = state.audio.currentTime;
    cancelScheduled();
    state.node.port.postMessage({ type: "clear" });
  }
  state.scheduledT = 0;
});

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
    state.lastFrame = now;
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
    await loadMeshes();
    await loadModel();
    buildVoiceRows();
    applyPoses(0);
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
window.lovophon = state;

main();
