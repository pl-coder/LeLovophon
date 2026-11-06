// AudioWorklet host for the Faust-compiled Lovophon strings (dsp/lovophon.wasm).
//
// The main thread compiles the wasm to a WebAssembly.Module and passes it in
// processorOptions with the Faust JSON. Memory layout follows Faust's own
// wasm wrapper: the DSP struct sits at address 0, the audio heap starts at
// json.size (output pointer table, then one 128-sample float buffer per
// channel). Every Faust slider is exposed as a k-rate AudioParam so the page
// can schedule plucks sample-block accurately with setValueAtTime.

const BLOCK = 128;
const VOICES = 12;

function descriptors() {
  const d = [
    { name: "gain", defaultValue: 0.4, minValue: 0, maxValue: 1, automationRate: "k-rate" },
    { name: "t60", defaultValue: 3.0, minValue: 0.2, maxValue: 12, automationRate: "k-rate" },
    { name: "bright", defaultValue: 5200, minValue: 500, maxValue: 12000, automationRate: "k-rate" },
  ];
  for (let i = 0; i < VOICES; i++) {
    d.push({ name: `freq${i}`, defaultValue: 220, minValue: 20, maxValue: 4000, automationRate: "k-rate" });
    d.push({ name: `trig${i}`, defaultValue: 0, minValue: 0, maxValue: 1, automationRate: "k-rate" });
    d.push({ name: `dir${i}`, defaultValue: 1, minValue: -1, maxValue: 1, automationRate: "k-rate" });
  }
  return d;
}

class LovophonProcessor extends AudioWorkletProcessor {
  static get parameterDescriptors() {
    return descriptors();
  }

  constructor(options) {
    super();
    const { module, json } = options.processorOptions;
    this.instance = new WebAssembly.Instance(module, { env: { _powf: Math.pow, _tanf: Math.tan } });
    const ex = this.instance.exports;
    this.ex = ex;
    this.numOut = ex.getNumOutputs(0);
    const ptrSize = 4;
    const sampleSize = 4;
    const heap = parseInt(json.size, 10);
    this.outsPtr = heap; // pointer table
    const firstBuffer = heap + this.numOut * ptrSize;
    const needed = firstBuffer + this.numOut * BLOCK * sampleSize;
    if (ex.memory.buffer.byteLength < needed) {
      ex.memory.grow(Math.ceil((needed - ex.memory.buffer.byteLength) / 65536));
    }
    this.heap32 = new Int32Array(ex.memory.buffer);
    this.heapF = new Float32Array(ex.memory.buffer);
    this.outViews = [];
    for (let c = 0; c < this.numOut; c++) {
      const addr = firstBuffer + c * BLOCK * sampleSize;
      this.heap32[(this.outsPtr >> 2) + c] = addr;
      this.outViews.push(this.heapF.subarray(addr >> 2, (addr >> 2) + BLOCK));
    }
    this.index = {};
    const walk = (items) => {
      for (const it of items) {
        if (it.items) walk(it.items);
        else this.index[it.label] = it.index;
      }
    };
    walk(json.ui);
    ex.init(0, sampleRate);
    this.last = {};
    this.port.onmessage = (e) => {
      if (e.data && e.data.type === "clear") ex.instanceClear(0);
    };
  }

  process(inputs, outputs, parameters) {
    const ex = this.ex;
    for (const name in this.index) {
      const p = parameters[name];
      if (!p) continue;
      const v = p[0];
      if (this.last[name] !== v) {
        ex.setParamValue(0, this.index[name], v);
        this.last[name] = v;
      }
    }
    ex.compute(0, BLOCK, this.outsPtr, this.outsPtr);
    const out = outputs[0];
    for (let c = 0; c < out.length; c++) {
      out[c].set(this.outViews[Math.min(c, this.numOut - 1)]);
    }
    return true;
  }
}

registerProcessor("lovophon-faust", LovophonProcessor);
