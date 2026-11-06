# sim — play with the Lovophon without FreeCAD

Two things live here: a Python model of the current design and a browser page
that runs it. The design of record is
`outputs/Lovophone_Lab_Frame_Ratio_Review.FCStd`.

## The model: `sim/lovophon`

A standard-library Python package that answers two questions: when does each
string get plucked, and where is every moving part at time *t*.

```sh
python3 -m sim.lovophon                      # table of the twelve voices
python3 -m sim.lovophon --csv --midi         # 480 s schedule into outputs/
python3 -m sim.lovophon --rpm 6 --csv        # faster shaft, 240 s repeat
python3 -m sim.lovophon --tune C3=128 --midi # retune a string
python3 -m unittest discover -s sim/tests    # checks
```

`design.json` is a snapshot of the FreeCAD document's `Motion.LinkageGeometry`
rows and properties, so nothing downstream has to parse a `.FCStd`. A test
proves it still equals the FreeCAD file; refresh it with
`python3 -m sim.lovophon --snapshot` after a CAD revision.

The kinematics are a port of `Animate_Lovophone_Lab_Ratio_Review.FCMacro`; the
pluck convention (two `beta_mid` crossings per cam revolution) is the one in
`work/make_lovophone_midi.py`. Voice C3's crossings are checked against the
archived 160-minute CSV, the one voice whose follower geometry survived the
ratio correction. Generated `.mid` files are gitignored upstream and should be
regenerated, not committed.

## The page: `sim/page`

A standalone page that draws the exported CAD meshes moving and plays the
strings. Serve the repository root (the page fetches the model and the design
snapshot from `../lovophon/`) and open `sim/page/`:

```sh
python3 -m http.server 8765
# then http://localhost:8765/sim/page/
```

It needs a network connection for two CDN libraries, three.js and Pyodide.
First load is a few seconds while Pyodide starts.

| Layer | Where | Role |
|---|---|---|
| Python in Pyodide | `sim/lovophon` unchanged | poses for the 48 moving groups every frame; plucks in a short lookahead |
| three.js | `assets/lovophon.glb` | the CAD, one node per moving group, one per third bridge, one static |
| Faust in an AudioWorklet | `lovophon.dsp` → `dsp/lovophon.wasm` | twelve Karplus-Strong nylon strings, plucks scheduled on the audio clock |

Controls: play, pause, reset; shaft speed in rpm (the machine's one real knob:
faster means the same pattern in less time); volume, decay and brightness of
the strings; a tuning preset menu (the design's 5-limit just pentatonic,
12-tone equal temperament, Pythagorean, just minor pentatonic, Hirajoshi,
Slendro, as cents offsets per degree, with Custom once a slider is moved); per
voice, a tuning offset in cents and the third-bridge position in mm. Moving a
bridge changes the speaking length and so the pitch, while the cam ratio stays
fixed by the pulleys. That is the real machine detuning from its own rhythm,
and the point of the slider.

A brass crank on the free end of the input shaft (the end away from the tuner
block) turns with the C3 driver so the shaft speed can be read at a glance.
Inboard of it a single-start worm drives a 24-tooth wheel carrying a needle
over a dial with 24 ticks: one tick per shaft turn, one needle turn per
480 s cycle. The 24:1 comes in one step because 24 is the least common
multiple of the ratio denominators, so no further reduction is needed.
Each voice has its own colour, shown as a swatch in the panel and painted on
its whole drivetrain (driver pulley, driven pulley and cam, follower, arm and
pick); the string itself stays nylon-coloured and a halo in the voice colour
flashes around it when plucked. The crank, the dial and the colours are visual
aids the real machine does not have.

The model is always evaluated at the reference 3 rpm in "machine time"; the
page advances machine time at rpm/3 of wall time, so a speed change never makes
a cam jump.

### Rebuilding the assets

```sh
# meshes, with FreeCAD's headless interpreter (macOS path shown)
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd \
    -c "exec(open('sim/export_meshes.py').read())"
# strings, with the Faust compiler (brew install faust)
faust -lang wasm -o sim/page/dsp/lovophon.wasm sim/page/lovophon.dsp
```

The exporter reads colours and visibility from the saved document, so hidden
presentation parts (motor, obsolete tray) are left out. The GLB is about 3 MB
at 0.5 mm / 0.6 rad deflection.

This is ideal kinematics and a listening model. It models no belt ripple,
pick compliance, string acoustics or motor regulation, and proves nothing
about a physical machine.
