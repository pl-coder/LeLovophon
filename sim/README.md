# sim — play Le Lovophon in a browser, without FreeCAD

A page that draws Paul's designs moving, straight from the CAD, and plays
their strings. Behind it are small Python models of each design that also run
on their own. Nothing here changes a CAD file.

**Two designs, two tabs.** The first tab is [Plucking Layout R5](../outputs/LeLovophon_Pluck_Layout_R5/README.md),
the current proposal as of 11 November 2026: gears, cranks, pushrods and
rockers on a 700 mm body. The second is the earlier Lab Frame Ratio Review of
6 November: belts, eccentric cams and spring followers. Ratios, pitches,
tooth counts' ratios and the 24-turn repeat are the same in both; the motion
and the pluck schedule are each design's own.

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
4. On the Lab Frame tab, look at the tuning end of the input shaft: the crank
   handle and the small dial whose needle goes round once per 24-turn cycle.
   On R5 the hand crank at the treble end is Paul's own.
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

Everything that moves, and when each string is plucked, comes from Paul's
files. Several things on the page do not, and are labelled here so nobody
takes them for the design. (A vibrato mechanism was tried on this branch and
removed on 16 November; the diary has it.)

| On the page | Source |
|---|---|
| **R5:** body, ribs, strings, gears, cranks, pushrods, rockers, pendulums, picks, hand crank | Exported from `LeLovophon_Pluck_Layout_R5.FCStd`, colours as saved, grouped by its `Motion` and `Voice` properties |
| **R5:** motion of the 37 rigid groups | Port of the four-bar closure in `work/direct_gear_math.py`, rows from `Drive_Effort/Reproduction/kinematics.json` |
| **R5:** pluck times | Rocker centre crossings, outward and return, as in `work/make_direct_gear_sound.py`; all 1350 match his event list |
| **Lab Frame:** frame, soundbox, strings, pulleys, belts, cams, followers, arms, picks | Exported from `Lovophone_Lab_Frame_Ratio_Review.FCStd`, colours and hidden parts as saved |
| **Lab Frame:** motion of the 48 moving groups | Port of `Animate_Lovophone_Lab_Ratio_Review.FCMacro` reading `Motion.LinkageGeometry` |
| **Lab Frame:** pluck times | Two `beta_mid` crossings per cam revolution, the convention in `work/make_lovophone_midi.py` |
| Ratios, tooth counts, lengths, pitches in the panel | Each design's own rows |
| String sound | **Added.** A synthesised nylon string, tuned by ear; not a measurement |
| Per-voice colours and pluck halos | **Added.** Visual aids |
| Crank handle on the Lab Frame's tuning end | **Added.** A concept, to read shaft speed at a glance |
| Worm, 24-tooth wheel and cycle dial on the Lab Frame | **Added.** A concept: one needle turn per 480 s cycle |
| Tuning presets, per-voice tuning and bridge sliders | **Added.** Experiments; the design's values are the defaults |

Lab Frame belts are static, as in the FreeCAD animation. R5's flexible PET
picks are rigid here; their release is one of Paul's open physical questions.

### The cycle dial

A single-start worm on the input shaft drives a 24-tooth wheel carrying a
needle over 24 ticks: one tick per shaft turn, one needle turn per cycle. It
needs no further reduction because 24 is the least common multiple of the
ratio denominators, so the dial is the repeat by construction.

## The controls

| Control | Does |
|---|---|
| Play / Pause, Reset | Start, hold, or return to turn 0. The readout shows seconds played and the shaft turn out of 24 |
| shaft | Input speed, 0.5 to 12 rpm. The design speed is 3 |
| volume, decay, bright | The synthesised strings: level, ring time, brightness |
| preset | Cents offsets per pentatonic degree: the design's 5-limit just tuning, 12-tone equal temperament, Pythagorean, just minor pentatonic, Hirajoshi, Slendro. Shows Custom once a tuning slider is moved by hand |
| tuning (per voice) | ±150 cents on that string |
| bridge (per voice) | Third-bridge position as speaking length in mm |

## The models: `sim/lovophon`

A standard-library Python package (3.11 or newer, like the repository checks)
that answers two questions for each design: when is each string plucked, and
where is every moving part at time *t*. `model.py` is the Lab Frame,
`r5.py` is Plucking Layout R5; the CLI below drives the Lab Frame.

```sh
python3 -m sim.lovophon                      # table of the twelve voices
python3 -m sim.lovophon --csv --midi         # 480 s schedule into outputs/
python3 -m sim.lovophon --rpm 6 --csv        # faster shaft, 240 s repeat
python3 -m sim.lovophon --tune C3=128 --midi # retune a string
python3 -m sim.lovophon --snapshot-r5        # refresh r5_design.json from Paul's kinematics.json
python3 -m unittest discover -s sim/tests    # 26 checks
```

`design.json` is a snapshot of the FreeCAD document's `Motion.LinkageGeometry`
rows and properties, so nothing downstream has to parse a `.FCStd`. A test
proves it still equals the FreeCAD file. **After a CAD revision**, refresh it
with `python3 -m sim.lovophon --snapshot` and re-export the meshes (below).

How far the Lab Frame model is checked: voice C3's crossings match the
archived 160-minute CSV, the one voice whose follower geometry survived the
ratio correction. The other eleven are checked by invariants: exact ratios,
two plucks per cam revolution, `2 × 24 × ratio` plucks per cycle (1350 in
all), and exact repetition after 480 s. Generated `.mid` files are gitignored
and should be regenerated, not committed.

How far the R5 model is checked: `r5_design.json` is a snapshot of Paul's
`kinematics.json` (its hash and the CAD's are recorded and tested); the rows
are recomputed from his formulas in the tests; the saved CAD pose is the
shared centre crossing at *t* = 0; and all 1350 plucks match his
`LeLovophon_8min_Pluck_Times.csv` in time and direction. The coupler keeps
its length and the rockers stay within his half-swing.

## How the page is put together

| Layer | Where | Role |
|---|---|---|
| Python in the browser (Pyodide) | `sim/lovophon`, unchanged | Poses for the moving groups every frame; plucks in a half-second lookahead |
| three.js | `page/assets/lovophon_r5.glb`, `page/assets/lovophon.glb` | The CAD: one node per moving group, per third bridge and per string, one for everything static. R5 nodes sit at their rotation centres |
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
    -c "exec(open('sim/export_meshes_r5.py').read())"     # R5, 10.6 MB
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd \
    -c "exec(open('sim/export_meshes.py').read())"        # Lab Frame, 3.2 MB
# strings, with the Faust compiler (brew install faust)
faust -lang wasm -o sim/page/dsp/lovophon.wasm sim/page/lovophon.dsp
```

The exporters read colours and visibility from the saved document, so hidden
presentation parts are left out, at 0.5 mm / 0.6 rad deflection. R5's 1101
solids (327 of them fasteners) make the larger file; the wasm is 32 KB.

## Before this goes anywhere near `main`

Everything on this branch lives under `sim/` plus one workflow file,
`.github/workflows/sim-tests.yml`; none of the files pinned by
`docs/asset-manifest.json` is changed, so `scripts/verify_project.py` passes
unmodified. Three things for Paul to decide, none of them blocking a try on
this branch.

- **Generated files.** The repository excludes generated meshes and media.
  The two GLBs under `page/assets/` are generated meshes and
  `page/dsp/lovophon.wasm` a compiled binary. They could be left out and
  rebuilt by whoever runs the page, at the cost of needing FreeCAD and Faust.
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
