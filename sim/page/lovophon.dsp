// Le Lovophon — twelve plucked nylon strings for the browser page.
//
// Each voice is a Karplus-Strong string: a fractional delay line tuned to
// freq, fed back through a gentle one-pole low-pass so high partials die
// first (nylon rather than steel), excited by a short filtered noise burst
// whose sign follows the pick direction. The decay is set by a T60 so it does
// not change with pitch the way raw feedback gain would.
//
// Parameters per voice i (0..11), addressed by path from the page:
//   freq%i   Hz          string pitch
//   trig%i   0/1         rising edge plucks; the page schedules it as an AudioParam
//   dir%i    -1/+1       pick direction, flips the excitation polarity
// Global:
//   gain     0..1        master
//   t60      seconds     decay to -60 dB
//   bright   Hz          loop low-pass cutoff
//
// Build:  faust -lang wasm-e -o sim/page/dsp/lovophon.wasm sim/page/lovophon.dsp
// This is a listening model, not a measurement of any real string.

import("stdfaust.lib");

declare name "lovophon";
declare author "Langford and Love's Musical Doohickey Corporation";

gain   = hslider("gain", 0.4, 0, 1, 0.001) : si.smoo;
t60    = hslider("t60", 3.0, 0.2, 12, 0.01);
bright = hslider("bright", 5200, 500, 12000, 1);

maxDelay = 8192;

voice(i) = excitation : string
with {
    freq = hslider("freq%i", 220, 20, 4000, 0.001) : si.smoo;
    trig = hslider("trig%i", 0, 0, 1, 1);
    dir  = hslider("dir%i", 1, -1, 1, 2);

    // Delay in samples for one period, minus the loop filter's own delay.
    period = ma.SR / freq;
    loopDelay = max(2, period - 1.0);
    // Per-pass feedback gain for a T60 of t60 seconds at this pitch.
    feedback = pow(0.001, period / (ma.SR * t60));

    // Short noise burst, low-passed so the attack is round rather than clicky.
    burst = no.noise : fi.lowpass(1, 7000) * en.ar(0.0004, 0.004, trig) * dir * 0.8;
    excitation = burst;

    loop = fi.lowpass(1, bright) * feedback;
    string = (+ : de.fdelay4(maxDelay, loopDelay)) ~ loop : fi.dcblocker;
};

process = par(i, 12, voice(i)) :> _ * gain <: _, _;
