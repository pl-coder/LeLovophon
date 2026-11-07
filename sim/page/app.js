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
  vibNote: document.getElementById("vib-note"),
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
  strings: [], // per voice: {mesh, material, glow}
  shaftEnd: null, // crank, worm wheel, vibrato train and bell crank groups
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
  const staticNode = state.nodes.get("static");
  const extras = (staticNode && staticNode.userData) || {};
  const floating = state.nodes.get("bridge_float");
  buildShaftEnd(extras.input_shaft_mm, floating && floating.userData.bbox_mm, floating);
  const box = new THREE.Box3().setFromObject(root);
  const centre = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3()).length();
  camera.position.copy(centre).add(new THREE.Vector3(0.45, 0.5, 1.0).multiplyScalar(size * 0.95));
  controls.target.copy(centre);
  controls.update();
}

// Everything on the tuning end of the input shaft, outboard of where the CAD
// shaft stops (x_max): a brass extension carrying, in order, the worm for the
// cycle dial, the vibrato train's first wheel, the far cheek bearing and the
// crank handle. The 30:1 step-up (60/10 then 50/10) turns an eccentric; a bell
// crank about a vertical pin rides it and pushes a tab on the floating tuner
// block against a return spring to the lab post. All dimensions in mm; the
// group is scaled once. Visual aids: the real machine has none of this yet.
const WHEEL_TEETH = 24; // worm wheel, one turn per 24-turn cycle
const WHEEL_PITCH_R = 12;
const WORM_PITCH_R = 5;
const GEAR_MODULE = 0.55;
const STAGES = [[60, 10], [50, 10]]; // wheel teeth, pinion teeth: 6:1 then 5:1
const VIB_ARM_IN = 17.5; // bell crank pivot to roller, along X
const VIB_ARM_OUT = 25; // pivot to tab, along Z
const VIB_DISC_R = 8;
const VIB_ROLLER_R = 3;

function buildShaftEnd(shaft, bbox, floating) {
  if (!shaft) return;
  const brass = new THREE.MeshStandardMaterial({ color: 0xc29645, metalness: 0.4, roughness: 0.45 });
  const steel = new THREE.MeshStandardMaterial({ color: 0x9aa0a6, metalness: 0.6, roughness: 0.4 });
  const dark = new THREE.MeshStandardMaterial({ color: 0x3a3a3c, roughness: 0.7 });
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
  // Axle positions in the Y-Z plane: A is the input shaft, C the eccentric
  // axle straight in front of it (+Z), B the compound axle between.
  const r = (teeth) => (GEAR_MODULE * teeth) / 2;
  const dAB = r(STAGES[0][0]) + r(STAGES[0][1]);
  const dBC = r(STAGES[1][0]) + r(STAGES[1][1]);
  const dAC = 20;
  const bz = (dAB * dAB - dBC * dBC + dAC * dAC) / (2 * dAC);
  const by = Math.sqrt(dAB * dAB - bz * bz);
  const A = { y: ay, z: az };
  const B = { y: ay + by, z: az + bz };
  const C = { y: ay, z: az + dAC };
  // X stations along the extension.
  const xWorm = x0 + 8;
  const xEcc = x0 + 22;
  const xW1 = x0 + 27;
  const xW2 = x0 + 31;
  const xCheek = x0 + 35.5;
  const xHub = x0 + 40;
  // Shaft extension and everything keyed to it.
  const shaftGroup = new THREE.Group();
  shaftGroup.position.set(0, ay, az);
  mesh(shaftGroup, new THREE.CylinderGeometry(3, 3, xHub - x0 + 2, 20), brass, x0 + (xHub - x0 + 2) / 2, 0, 0, alongX);
  const worm = new THREE.Mesh(wormGeometry(0.008, 0.0036, 0.0016, Math.PI / 1000), brass);
  worm.scale.setScalar(1000); // wormGeometry is in metres
  worm.position.x = xWorm;
  shaftGroup.add(worm);
  shaftGroup.add(gear(STAGES[0][0], 3, brass).at(xW1, 0, 0));
  // Crank: hub, arm, pin and knob beyond the far cheek.
  mesh(shaftGroup, new THREE.CylinderGeometry(6, 6, 6, 24), brass, xHub, 0, 0, alongX);
  mesh(shaftGroup, new THREE.BoxGeometry(4, 36, 8), brass, xHub + 4, 15, 0);
  mesh(shaftGroup, new THREE.CylinderGeometry(2, 2, 12, 16), brass, xHub + 11, 30, 0, alongX);
  mesh(shaftGroup, new THREE.CylinderGeometry(4, 4.5, 16, 20), knobMat, xHub + 23, 30, 0, alongX);
  g.add(shaftGroup);
  // Compound axle B: pinion meshing with W1, wheel driving P2.
  const bGroup = new THREE.Group();
  bGroup.position.set(0, B.y, B.z);
  mesh(bGroup, new THREE.CylinderGeometry(1.5, 1.5, xCheek - xW1 + 6, 12), steel, (xW1 + xCheek + 2) / 2, 0, 0, alongX);
  bGroup.add(gear(STAGES[0][1], 4, steel).at(xW1, 0, 0));
  bGroup.add(gear(STAGES[1][0], 3, brass).at(xW2, 0, 0));
  g.add(bGroup);
  // Axle C: pinion, then the eccentric back toward the dial.
  const cGroup = new THREE.Group();
  cGroup.position.set(0, C.y, C.z);
  mesh(cGroup, new THREE.CylinderGeometry(1.5, 1.5, xCheek - xEcc + 8, 12), steel, (xEcc - 4 + xCheek + 4) / 2, 0, 0, alongX);
  cGroup.add(gear(STAGES[1][1], 4, steel).at(xW2, 0, 0));
  // Tooth phases so each mesh interleaves: with tooth 0 on +Y and angles
  // measured from +Y toward +Z, a wheel tooth at the mesh direction must meet
  // a pinion gap. betaB and deltaC are the pinions' standing offsets.
  const ang = (P, Q) => Math.atan2(Q.z - P.z, Q.y - P.y);
  const aAB = ang(A, B);
  const aBC = ang(B, C);
  const [N1, n1] = STAGES[0];
  const [N2, n2] = STAGES[1];
  const betaB = (Math.PI + (N1 + n1) * aAB) / n1;
  const deltaC = ((n2 + 1) * Math.PI + (N2 + n2) * aBC - N2 * betaB) / n2;
  // The eccentric's throw points along +Y at shaft angle 0 in the world, so
  // it is placed at -deltaC in the axle's own frame.
  const throwMm = VIBRATO_DEPTH_MM() * VIB_ARM_IN / VIB_ARM_OUT;
  const disc = mesh(cGroup, new THREE.CylinderGeometry(VIB_DISC_R, VIB_DISC_R, 5, 48), brass, xEcc, throwMm * Math.cos(deltaC), -throwMm * Math.sin(deltaC), alongX);
  const mark = new THREE.Mesh(new THREE.BoxGeometry(1.2, 5.2, 1), dark);
  mark.position.set(VIB_DISC_R - 1.2, 0, 0);
  disc.add(mark);
  g.add(cGroup);
  // Bell crank: roller on the shaft side of the eccentric, pivot 17.5 mm
  // inboard, output arm forward to the block.
  const px = xEcc - VIB_ARM_IN;
  const pz = C.z - VIB_DISC_R - VIB_ROLLER_R;
  mesh(g, new THREE.CylinderGeometry(1.5, 1.5, 16, 16), steel, px, ay - 6, pz);
  mesh(g, new THREE.BoxGeometry(6, 10, 6), dark, px, ay - 18, pz);
  const crank = new THREE.Group();
  crank.position.set(px, ay, pz);
  mesh(crank, new THREE.BoxGeometry(VIB_ARM_IN - 2, 3, 2.5), brass, (VIB_ARM_IN - 2) / 2, 0, 0);
  mesh(crank, new THREE.CylinderGeometry(0.8, 0.8, 7, 12), steel, VIB_ARM_IN, 0, 0, alongX);
  mesh(crank, new THREE.CylinderGeometry(VIB_ROLLER_R, VIB_ROLLER_R, 4, 24), steel, VIB_ARM_IN, 0, 0, alongX);
  mesh(crank, new THREE.BoxGeometry(2.5, 3, VIB_ARM_OUT), brass, 0, 0, VIB_ARM_OUT / 2);
  mesh(crank, new THREE.CylinderGeometry(1.5, 1.5, 3, 16), steel, -1.5, 0, VIB_ARM_OUT, [Math.PI / 2, 0, 0]);
  mesh(crank, new THREE.CylinderGeometry(3, 3, 3.5, 20), brass, 0, 0, 0);
  g.add(crank);
  // Module deck, a post, and a far cheek just big enough for the three
  // bearings, so the train stays visible from outside.
  const plate = new THREE.MeshStandardMaterial({ color: 0x6f7378, metalness: 0.3, roughness: 0.6 });
  mesh(g, new THREE.BoxGeometry(xCheek + 2 - (x0 + 2), 3, 48), plate, (x0 + 2 + xCheek + 2) / 2, ay - 24.5, az + 10);
  mesh(g, new THREE.BoxGeometry(3, 12, 8), plate, xCheek, ay - 17.5, az);
  mesh(g, new THREE.BoxGeometry(3, 36, 44), plate, xCheek, (A.y + B.y) / 2 + 2, (A.z + C.z) / 2 + 2);
  for (const P of [A, B, C]) mesh(g, new THREE.CylinderGeometry(4, 4, 5, 20), steel, xCheek, P.y, P.z, alongX);
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
  scene.add(g);
  // Lever tab on the block's near end face and the return spring to the lab
  // post, both carried by the floating block.
  if (floating && bbox) {
    const carried = new THREE.Group();
    carried.scale.setScalar(0.001);
    mesh(carried, new THREE.BoxGeometry(4, 22, 4), brass, px - 5, ay - 7, bbox[4] - 2);
    const spring = new THREE.Mesh(springGeometry(13, 2.2, 0.5, 9), steel);
    spring.scale.setScalar(1000);
    spring.position.set(px - 3 + 6.5, ay - 14, bbox[4] - 2);
    carried.add(spring);
    floating.add(carried);
  }
  state.shaftEnd = { shaft: shaftGroup, axleB: bGroup, axleC: cGroup, crank, dial: rotor, bridge: floating, throwMm, betaB, deltaC };
}

// A spur gear as a disc with box teeth, in mm; tooth 0 points along +Y.
function gear(teeth, thick, mat) {
  const pr = (GEAR_MODULE * teeth) / 2;
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.CylinderGeometry(pr - GEAR_MODULE * 0.9, pr - GEAR_MODULE * 0.9, thick, Math.max(24, teeth)), mat);
  body.rotation.z = Math.PI / 2;
  g.add(body);
  const pitch = (2 * Math.PI * pr) / teeth;
  for (let i = 0; i < teeth; i++) {
    const a = (i / teeth) * 2 * Math.PI;
    const t = new THREE.Mesh(new THREE.BoxGeometry(thick, GEAR_MODULE * 2.1, pitch * 0.48), mat);
    t.position.set(0, Math.cos(a) * (pr - GEAR_MODULE * 0.1), Math.sin(a) * (pr - GEAR_MODULE * 0.1));
    t.rotation.x = a;
    g.add(t);
  }
  g.at = (x, y, z) => { g.position.set(x, y, z); return g; };
  return g;
}

function VIBRATO_DEPTH_MM() {
  return state.model ? state.model.VIBRATO_DEPTH_MM : 0.6;
}

function VIBRATO_STEP_UP() {
  return state.model ? state.model.VIBRATO_STEP_UP : 30;
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

// A coil spring along local X: length, coil radius, wire radius, turns (mm).
function springGeometry(length, radius, wire, turns) {
  const pts = [];
  const n = turns * 24;
  for (let i = 0; i <= n; i++) {
    const t = i / n;
    const a = t * turns * 2 * Math.PI;
    pts.push(new THREE.Vector3((t - 0.5) * length / 1000, Math.cos(a) * radius / 1000, Math.sin(a) * radius / 1000));
  }
  return new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), n, wire / 1000, 8, false);
}

// Vibrato phase in turns of the eccentric, from machine time. Faust
// integrates the same rate on the audio clock, so the two agree to a block.
function vibratoPhase() {
  return state.model.vibrato_phase(currentT(), REFERENCE_RPM);
}

function vibratoRate() {
  return state.playing ? (state.rpm / 60) * VIBRATO_STEP_UP() : 0;
}

// Push the current rate to Faust: on any change of rpm or play state.
function setVibratoRate() {
  if (state.node) param("vibhz").setValueAtTime(vibratoRate(), state.audio.currentTime);
}

function applyShaftEnd(shaftDeg) {
  const e = state.shaftEnd;
  if (!e) return;
  const theta = THREE.MathUtils.degToRad(shaftDeg);
  e.shaft.rotation.x = theta;
  // Worm wheel turns 1/24 of the shaft; clockwise seen from the front.
  e.dial.rotation.z = theta / WHEEL_TEETH;
  // Each external mesh reverses the sense; the eccentric turns with the shaft.
  const stage1 = STAGES[0][0] / STAGES[0][1];
  e.axleB.rotation.x = -theta * stage1 + e.betaB;
  e.axleC.rotation.x = theta * VIBRATO_STEP_UP() + e.deltaC;
  // The roller follows the disc rim in Z; the crank turns about Y by
  // -throw sin / arm, and the block follows the model's bridge offset.
  const phi = 2 * Math.PI * vibratoPhase();
  e.crank.rotation.y = -(e.throwMm * Math.sin(phi)) / VIB_ARM_IN;
  if (e.bridge) e.bridge.position.x = state.model.bridge_offset_mm(currentT(), REFERENCE_RPM) / 1000;
}

function updateVibratoReadouts() {
  const voices = state.design.voices;
  if (!voices || state.voices.length < voices.length) return;
  const hz = (state.rpm / 60) * VIBRATO_STEP_UP();
  const cents = (v) => {
    const L = state.voices[v].lengthMm;
    return 1200 * Math.log2(L / (L - VIBRATO_DEPTH_MM()));
  };
  const lo = voices[0].display_note;
  const hi = voices[voices.length - 1].display_note;
  ui.vibNote.textContent = `${VIBRATO_STEP_UP()}:1 step-up, ±${VIBRATO_DEPTH_MM().toFixed(1)} mm · ${hz.toFixed(2)} Hz at ${state.rpm.toFixed(1)} rpm · ±${cents(0).toFixed(1)} ¢ on ${lo}, ±${cents(voices.length - 1).toFixed(1)} ¢ on ${hi}`;
}

// Each speaking string keeps its own nylon material; a transparent coloured
// halo around it, invisible at rest, lights up when the string is plucked.
function buildStrings() {
  state.design.voices.forEach((row, v) => {
    // Tint the whole drivetrain of this voice (driver pulley, driven pulley
    // and cam, follower, arm and pick) in the string's colour.
    const tint = new THREE.MeshStandardMaterial({ color: voiceColour(v), metalness: 0.25, roughness: 0.5 });
    for (const kind of KINDS) {
      const part = state.nodes.get(`${row.note}_${kind}`);
      if (part) part.traverse((o) => { if (o.isMesh) o.material = tint; });
    }
    const node = state.nodes.get(`${row.note}_string`);
    if (!node) return;
    const box = new THREE.Box3().setFromObject(node);
    const centre = box.getCenter(new THREE.Vector3());
    const length = box.max.x - box.min.x;
    const material = new THREE.MeshBasicMaterial({ color: voiceColour(v), transparent: true, opacity: 0, depthWrite: false });
    const halo = new THREE.Mesh(new THREE.CylinderGeometry(0.0022, 0.0022, length, 12), material);
    halo.rotation.z = Math.PI / 2;
    halo.position.copy(centre);
    halo.visible = false;
    scene.add(halo);
    state.strings[v] = { halo, material, glow: 0 };
  });
}

function decayGlow(dt) {
  for (const s of state.strings) {
    if (!s || !s.halo.visible) continue;
    s.glow *= Math.exp(-dt / 0.35);
    s.material.opacity = 0.85 * s.glow;
    const r = 0.6 + 0.8 * s.glow;
    s.halo.scale.set(r, 1, r);
    if (s.glow < 0.02) s.halo.visible = false;
  }
}

function applyPoses(T) {
  const flat = posesFlat(T);
  const voices = state.design.voices;
  applyShaftEnd(flat[3]);
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
  for (let v = 0; v < 12; v++) {
    param(`freq${v}`).value = voiceFrequency(v);
    param(`len${v}`).value = state.voices[v].lengthMm;
  }
  param("vibmm").value = VIBRATO_DEPTH_MM();
  param("vibhz").value = vibratoRate();
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
  if (row) {
    row.classList.add("pluck");
    setTimeout(() => row.classList.remove("pluck"), 180);
  }
  const s = state.strings[v];
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
  state.design.voices.forEach((row, v) => {
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
  ui.voices.innerHTML = "";
  state.design.voices.forEach((row, v) => {
    state.voices[v] = { tuningHz: row.frequency_hz, lengthMm: row.speaking_length };
    const minLength = Math.max(40, Math.ceil(320 - row.station + 6));
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
      if (state.node) {
        param(`freq${v}`).setValueAtTime(voiceFrequency(v), state.audio.currentTime);
        param(`len${v}`).setValueAtTime(state.voices[v].lengthMm, state.audio.currentTime);
      }
      updateVibratoReadouts();
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
    setVibratoRate();
    ui.play.textContent = "Play";
  } else {
    state.T0 = state.T;
    state.wall0 = state.audio.currentTime;
    state.scheduledT = state.T;
    state.playing = true;
    setVibratoRate();
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
  setVibratoRate();
  updateVibratoReadouts();
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
    decayGlow(Math.min(dt, 0.1));
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
    await loadModel();
    await loadMeshes();
    buildPresetMenu();
    buildVoiceRows();
    buildStrings();
    applyPoses(0);
    updateVibratoReadouts();
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
state.camera = camera;
state.controls = controls;
window.lovophon = state;

main();
