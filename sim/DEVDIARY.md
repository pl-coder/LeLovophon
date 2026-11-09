# sim — dev diary

Newest first. One entry per piece of work on the `sim/browser` branch: what
changed, what was learned, what is true afterwards. Short and honest; where
something was not checked, it says so. Commit hashes are on
`pl-coder/LeLovophon`.

The work was done by Peter Langford directing Claude (Anthropic's AI model),
which wrote the code and these entries. Nothing here has touched hardware.

---

## 2026-11-09 — packaged for Paul

**Changed:** merged Paul's `main` twice so switching to this branch does not
hide his newest work: the Slender Bank study (`ed24372`, merge `bf5ce92`) and,
landing the same evening while the documentation was being written, the
direct-gear prototype (`b6513ea`, merge `ffcd022`). Neither merge touched
anything under `sim/` or the Lab Frame document. Rewrote `sim/README.md` to
open with a quick start and to separate what comes from the CAD from what the
page adds; added this diary; added one row to the top-level README's table.

**The important one:** the direct-gear commit makes a different architecture
the current proposal and relabels the Lab Frame Ratio Review, which is all
this page models, as an earlier study. So the page is now a simulation of the
previous machine. The README says so at the top. What carries over unchanged:
the ratios, pitches, speaking lengths, the 24-turn repeat, and so the cycle
dial; a hand crank is now part of Paul's own proposal. What does not: the
motion and the pluck times, which come from a crank-rocker instead of a cam
and follower. The direct-gear folder ships its own 1350-pluck event list,
which would be an oracle for all twelve voices, where the Lab Frame had one.

**Learned:** reading CONTRIBUTING properly at this point, not at the start,
turned up two things that should have been raised earlier. The repository
excludes generated meshes, and the page commits one (the 3.2 MB GLB) plus a
compiled wasm. And no licence is selected, which CONTRIBUTING says must be
settled before third-party contributions. Both are written up in the README
as decisions for Paul. Neither stops anyone trying the branch.

**Now true:** branch is Paul's `main` as of `b6513ea` plus the sim. Repository
checks pass (323 packaged files) and the 17 model tests pass. No pull request
opened.

**Open:** whether to port the page to the direct-gear CAD, which is where it
would be useful to Paul now. Whether Paul wants any of this as a pull request,
a long-lived branch, or not at all. Peter's observation from playing it: 3 rpm
by hand is peaceful but hard to hold steady, which bears on a hand-cranked
prototype.

---

## 2026-11-07 — vibrato: 30:1, 0.6 mm, all gearing on the tuning end

**Changed:** three commits (`7bd43b5`, `c6e6d30`, `dc1a9df`). Peter asked for a
vibrato driven from the end of the input shaft, with the whole end bridge
floating and a lever to push it.

First cut: the tuner block, saddle rail and twelve saddles became one node the
page can slide; a sealed housing stood in for the step-up, with its ratio on a
slider from 1:1 to 200:1 so Peter could listen before choosing. He chose 30:1
and 0.6 mm of travel end to end, and asked for the crank and cycle dial to
move from the far end so all the gearing is on one side, handle outermost.

Second cut: the housing became two gear stages, 60/10 then 50/10, with the
pinions' standing angles solved so the drawn teeth interleave. Eccentric on
the output axle, bell crank on a vertical pin, tab on the block, return spring
to the lab post. Ratio and depth moved into the Python model as constants with
a test; the sliders went.

The sound: the string synthesiser takes each voice's speaking length and bends
pitch continuously from the bridge offset, so the same millimetres give more
cents on the short strings.

**Learned:** at 3 rpm the shaft turns once in 20 s, so an eccentric straight
on the shaft is a slow drift, not a vibrato; any musical rate needs a large
step-up, and the first proposal of 100:1 would be hard to drive by hand.
The compiled string needs each maths function it uses supplied by the page;
adding a sine without supplying it made the sound engine fail with no visible
error. A cheek plate big enough to look sturdy hid the whole gear train.
I first built ±0.6 mm; Peter meant 0.6 mm end to end.

**Checked:** pitch against bridge offset, by running the compiled string
offline and measuring its period by autocorrelation: ±2 mm on a 100 mm string
gave ratios 1.0197 and 0.9804 against 1.0204 and 0.9804 expected. In the
browser: the synthesiser receives 1.5 Hz, the block swings by the set amount.

**Not checked:** anything mechanical. No slide for the block, tension change
ignored, one bearing on the eccentric axle, 10-tooth pinions that would be
undercut. Also noticed and left: the string plays slightly flat at low
brightness (documented in the README).

---

## 2026-11-06 — worm, halos, drivetrain colours

**Changed:** one commit (`143ee14`). The worm rebuilt as a screw surface and
moved clear of the shaft's end collar; the string glow replaced by a
transparent halo that appears only on a pluck; each voice's four moving groups
painted in the voice's colour.

**Learned:** two mistakes caught by Peter. The CAD shaft ends in a collar
exactly where the worm had been put, so it was buried. And scaling a mesh
that is stored in world coordinates scales it about the world origin, which
is why strings appeared to fly up from below. A tube wound along a helix
reads as a spring, not a worm.

---

## 2026-11-06 — the cycle dial

**Changed:** one commit (`a03f3ba`). A worm on the input shaft, a 24-tooth
wheel above it, a needle over a 24-tick dial. Asked for as "one rotation per
cycle, may need multiple reductions".

**Learned:** it needs none. A single-start worm with a 24-tooth wheel is 24:1
in one step, and 24 is the least common multiple of the ratio denominators, so
the dial shows the repeat by construction. This is a part the real machine
could carry. Checked in the browser: shaft-to-needle ratio reads exactly 24.

---

## 2026-11-06 — presets, crank, glow

**Changed:** one commit (`7e5af45`). A menu of tunings as cents offsets per
pentatonic degree; a crank on the shaft so its speed can be read; each
speaking string exported as its own mesh so it can light when plucked.

**Learned:** Hirajoshi was first written with E raised 112 cents; it lowers E
and A by 71. All five tables were checked numerically before committing
(E3 reads 164.84 Hz under equal temperament).

---

## 2026-11-06 — the page

**Changed:** one commit (`fa4af41`). `sim/export_meshes.py` runs in headless
FreeCAD and writes a glTF binary with one node per moving group and per third
bridge, colours read from the saved document. `sim/page/` is three.js for the
picture, Pyodide running `sim/lovophon` unchanged for the motion and the
plucks, and a Faust string compiled to WebAssembly for the sound. The model
gained windowed pluck queries and flat pose arrays for the page.

**Learned:** the first export was 56 MB; a 0.5 mm / 0.6 rad tessellation with
shared vertices gives 119 thousand triangles in 3.2 MB. FreeCAD's own glTF
export skips shapes it has not triangulated, hence the hand-written writer.
FreeCAD 1.x stores colours in small binary files inside the document, not in
its XML. A reviewer pass found that two quick clicks on Play built two sound
engines; fixed. A background tab stops animation frames, so plucks are also
scheduled from a timer.

**Checked:** in a browser: motion, colours, sound output, continuous motion
through a speed change, bridge and tuning sliders, pause, resume, reset.
**Not checked:** the timbre, beyond listening.

---

## 2026-11-06 — the model, without FreeCAD

**Changed:** two commits (`172f5b2`, `78c9594`). `sim/lovophon/` is a
standard-library Python package. `model.py` reads the twelve
`LinkageGeometry` rows out of the `.FCStd` archive and ports the animation
macro's kinematics and the two-crossings-per-cam-revolution pluck search;
`midi.py` generalises the existing MIDI writer; `__main__.py` is the command
line. `design.json` snapshots the CAD rows. The 480 s pluck schedule (1350
plucks) is committed as a CSV, and the CI workflow also runs the tests.

**Learned:** the archived 160-minute pluck CSV came from the earlier chromatic
motion map. Only voice C's follower geometry survived the ratio correction,
so it is the only numeric oracle; the other eleven voices are checked by
invariants. A reviewer pass found one real defect, a MIDI header that ignored
a retuning for a voice with no events in a short run; fixed with a test.

---

## 2026-11-06 — forked and branched

**Changed:** forked `paullove89/LeLovophon` to `pl-coder/LeLovophon` and cut
`sim/browser` from Paul's `main` at `f564772`. The aim: make the instrument
easy to play with for someone without FreeCAD.
