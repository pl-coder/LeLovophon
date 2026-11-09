# sim — play Le Lovophon in a browser, without FreeCAD

A page that draws the twelve-voice Lab Frame moving, straight from the CAD, and
plays its strings. Behind it is a small Python model of the design that also
runs on its own. The design of record is
`outputs/Lovophone_Lab_Frame_Ratio_Review.FCStd`; nothing here changes it.

Built by Peter Langford, with Claude (Anthropic's AI model) writing the code.
Idea, instrument and CAD by Paul Love. The history of how it got here is in
[DEVDIARY.md](DEVDIARY.md).

## Try it

You need Python 3 and a current Chrome, Edge, Safari or Firefox. No FreeCAD, no
installs. The first load needs the internet for two libraries.

If you already have a clone of the repository:

```sh
git remote add peter https://github.com/pl-coder/LeLovophon.git
git fetch peter
git switch -c sim-browser peter/sim/browser
```

Or start fresh:

```sh
git clone --branch sim/browser https://github.com/pl-coder/LeLovophon.git
cd LeLovophon
```

Then, from the repository root (not from `sim/`):

```sh
python3 -m http.server 8765
```

and open <http://localhost:8765/sim/page/>. Wait a few seconds for "Loading…"
to clear, then press **Play**. Browsers only start sound after a click.
`git switch main` takes you back to your own branch.

Things to try, roughly in order:

1. Drag in the picture to orbit, scroll to zoom, right-drag to pan.
2. Press Play and watch one drivetrain. Each voice has its own colour on its
   pulleys, cam, follower, arm and pick, and a matching dot in the panel. The
   string flashes a halo in that colour when it is plucked.
3. Move **shaft** from 3 rpm upward. The pattern is the same, only faster; the
   line under the transport shows the repeat time.
4. Look at the tuning end of the input shaft: the crank handle, the gear
   step-up for the vibrato, and the small dial whose needle goes round once
   per 24-turn cycle.
5. Pick a **preset** under Tuning, or move one voice's **tuning** slider.
6. Move one voice's **bridge** slider. The third bridge slides, the pitch
   follows the speaking length, and the rhythm does not change, because the
   pulleys fix it. That is the machine detuning from its own ratio.

If something is wrong:

| Symptom | Cause and fix |
|---|---|
| Blank or broken page opened from a file | It must be served over http. Use the `http.server` line above. |
| 404 for `model.py` or `design.json` | The server was started inside `sim/`. Start it from the repository root. |
| Stuck on "Loading…" | The two libraries come from the jsDelivr CDN; check the connection or a content blocker. The browser console says which request failed. |
| Picture moves, no sound | Press Play once more, check the tab is not muted, and that **volume** is up. |
| Old behaviour after `git pull` | The browser cached the page. Hard reload (Cmd-Shift-R, or Ctrl-Shift-R). |

## What is the CAD and what is added

Everything that moves in the twelve drivetrains, and when each string is
plucked, comes from the FreeCAD document. Several things on the page do not,
and are labelled here so nobody takes them for the design.

| On the page | Source |
|---|---|
| Frame, soundbox, strings, pulleys, belts, cams, followers, arms, picks | Exported from the FreeCAD document, colours and hidden parts as saved |
| Motion of the 48 moving groups | Port of `Animate_Lovophone_Lab_Ratio_Review.FCMacro` reading `Motion.LinkageGeometry` |
| Pluck times | Two `beta_mid` crossings per cam revolution, the convention in `work/make_lovophone_midi.py` |
| Ratios, tooth counts, lengths, pitches in the panel | The same twelve `LinkageGeometry` rows |
| String sound | **Added.** A synthesised nylon string, tuned by ear; not a measurement |
| Per-voice colours and pluck halos | **Added.** Visual aids |
| Crank handle on the tuning end | **Added.** A concept, to read shaft speed at a glance |
| Worm, 24-tooth wheel and cycle dial | **Added.** A concept: one needle turn per 480 s cycle |
| Vibrato: gear step-up, eccentric, bell crank, floating tuner block | **Added.** A concept, described below |
| Tuning presets, per-voice tuning and bridge sliders | **Added.** Experiments; the design's values are the defaults |

Belts are static, as in the FreeCAD animation.

### The cycle dial

A single-start worm on the input shaft drives a 24-tooth wheel carrying a
needle over 24 ticks: one tick per shaft turn, one needle turn per cycle. It
needs no further reduction because 24 is the least common multiple of the
ratio denominators, so the dial is the repeat by construction.

### The vibrato

This is a proposal to look at and listen to, not a checked mechanism.

The input shaft stops just short of the tuner block. On a brass extension
beyond it sit, from the machine outward: the worm and dial, the vibrato
step-up, a cheek with the bearings, and the handle. The step-up is two gear
stages, 60/10 then 50/10, 30:1 in all, so its output turns 1.5 times a second
at 3 rpm and scales with shaft speed. The output axle carries an eccentric
disc. A bell crank on a vertical pin rides the disc with one arm and pushes a
tab on the tuner block with the other. The block, its saddle rail and the
twelve saddles float as one piece and slide along the strings by 0.6 mm end to
end, against a return spring to the lab post.

Every string gets the same millimetres, so the depth in cents is larger on the
short strings: ±1.6 ¢ on C3, ±7 ¢ on D5. The panel shows the current values.

This is the one place the page departs from "pitch ratio equals rotation
ratio": the pitch swings around the exact ratio while the rhythm stays exact.
The average pitch moves by less than a fiftieth of a cent.

What has not been done for it: no slide or guide is designed for the floating
block; the change in string tension as the block moves is ignored, only the
length changes; the eccentric's axle hangs from one bearing; 10-tooth pinions
would be undercut as real involute gears; nothing is checked for clearance or
strength beyond looking at it. The ratio and depth were chosen by ear, and
30:1 partly because a higher ratio would be hard to drive by hand.

The constants are `VIBRATO_STEP_UP` and `VIBRATO_DEPTH_MM` in
`sim/lovophon/model.py`.

## The controls

| Control | Does |
|---|---|
| Play / Pause, Reset | Start, hold, or return to turn 0. The readout shows seconds played and the shaft turn out of 24 |
| shaft | Input speed, 0.5 to 12 rpm. The design speed is 3 |
| volume, decay, bright | The synthesised strings: level, ring time, brightness |
| preset | Cents offsets per pentatonic degree: the design's 5-limit just tuning, 12-tone equal temperament, Pythagorean, just minor pentatonic, Hirajoshi, Slendro. Shows Custom once a tuning slider is moved by hand |
| tuning (per voice) | ±150 cents on that string |
| bridge (per voice) | Third-bridge position as speaking length in mm |

## The model: `sim/lovophon`

A standard-library Python package (3.11 or newer, like the repository checks)
that answers two questions: when is each string plucked, and where is every
moving part at time *t*.

```sh
python3 -m sim.lovophon                      # table of the twelve voices
python3 -m sim.lovophon --csv --midi         # 480 s schedule into outputs/
python3 -m sim.lovophon --rpm 6 --csv        # faster shaft, 240 s repeat
python3 -m sim.lovophon --tune C3=128 --midi # retune a string
python3 -m unittest discover -s sim/tests    # 17 checks
```

`design.json` is a snapshot of the FreeCAD document's `Motion.LinkageGeometry`
rows and properties, so nothing downstream has to parse a `.FCStd`. A test
proves it still equals the FreeCAD file. **After a CAD revision**, refresh it
with `python3 -m sim.lovophon --snapshot` and re-export the meshes (below).

How far the model is checked: voice C3's crossings match the archived
160-minute CSV, the one voice whose follower geometry survived the ratio
correction. The other eleven are checked by invariants: exact ratios, two
plucks per cam revolution, `2 × 24 × ratio` plucks per cycle (1350 in all),
and exact repetition after 480 s. Generated `.mid` files are gitignored and
should be regenerated, not committed.

## How the page is put together

| Layer | Where | Role |
|---|---|---|
| Python in the browser (Pyodide) | `sim/lovophon`, unchanged | Poses for the 48 moving groups every frame; plucks in a half-second lookahead |
| three.js | `page/assets/lovophon.glb` | The CAD: one node per moving group, per third bridge and per string, one for the floating tuner block, one for everything static |
| Faust in an AudioWorklet | `page/lovophon.dsp` → `page/dsp/lovophon.wasm` | Twelve Karplus-Strong strings; plucks are scheduled on the audio clock |
| `page/app.js`, `page/index.html` | | Panel, scheduling, and the added parts drawn in three.js |

The model is always evaluated at the reference 3 rpm in "machine time"; the
page advances machine time at rpm/3 of wall time, so a speed change never
makes a cam jump.

### Rebuilding the generated files

Two files under `page/` are build products, committed so the page runs with
nothing installed. Rebuild them after changing the CAD or the string:

```sh
# meshes, with FreeCAD's headless interpreter (macOS path shown)
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd \
    -c "exec(open('sim/export_meshes.py').read())"
# strings, with the Faust compiler (brew install faust)
faust -lang wasm -o sim/page/dsp/lovophon.wasm sim/page/lovophon.dsp
```

The exporter reads colours and visibility from the saved document, so hidden
presentation parts (motor, obsolete tray) are left out. The GLB is 3.2 MB at
0.5 mm / 0.6 rad deflection; the wasm is 37 KB.

## Before this goes anywhere near `main`

Three things for Paul to decide, none of them blocking a try on this branch.

- **Generated files.** The repository excludes generated meshes and media.
  `page/assets/lovophon.glb` is a generated mesh and `page/dsp/lovophon.wasm`
  a compiled binary. They could be left out and rebuilt by whoever runs the
  page, at the cost of needing FreeCAD and Faust.
- **Licence.** No project licence is selected, and CONTRIBUTING asks for that
  to be settled before third-party contributions are accepted. This is one.
- **Dependencies.** three.js (MIT) and Pyodide (MPL 2.0) load from the
  jsDelivr CDN and are not vendored. The string is compiled from Faust's
  standard libraries.

## What this is not

Ideal kinematics and a listening model. It models no belt ripple, pick
compliance, string acoustics or motor regulation, and proves nothing about a
physical machine. An animation is not a hardware test.

One known inaccuracy in the sound: the string loop compensates one sample for
its low-pass filter, so at low **bright** settings it plays slightly flat
(about 2 % at 1500 Hz on C3, 0.2 % at the default 5200 Hz).
