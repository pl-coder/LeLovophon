# sim — play with the Lovophon without FreeCAD

`sim/lovophon` is a standard-library Python model of the current design,
`outputs/Lovophone_Lab_Frame_Ratio_Review.FCStd`. It answers two questions:
when does each string get plucked, and where is every moving part at time *t*.
It is the seed of a browser-playable page and the oracle for the fabrication
and plugin work.

```sh
python3 -m sim.lovophon                      # table of the twelve voices
python3 -m sim.lovophon --csv --midi         # 480 s schedule into outputs/
python3 -m sim.lovophon --rpm 6 --csv        # faster shaft, 240 s repeat
python3 -m sim.lovophon --tune C3=128 --midi # retune a string
python3 -m unittest discover -s sim/tests    # checks
```

`design.json` is a snapshot of the FreeCAD document's `Motion.LinkageGeometry`
rows and properties, so the browser never has to parse a `.FCStd`. A test
proves it still equals the FreeCAD file; refresh it with
`python3 -m sim.lovophon --snapshot` after a CAD revision.

The kinematics are a port of `Animate_Lovophone_Lab_Ratio_Review.FCMacro`; the
pluck convention (two `beta_mid` crossings per cam revolution) is the one in
`work/make_lovophone_midi.py`. Voice C3's crossings are checked against the
archived 160-minute CSV, the one voice whose follower geometry survived the
ratio correction. Generated `.mid` files are gitignored upstream and should be
regenerated, not committed.

This is ideal kinematics. It models no belt ripple, pick compliance, string
acoustics or motor regulation, and proves nothing about a physical machine.
