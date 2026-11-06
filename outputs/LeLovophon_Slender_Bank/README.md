# Le Lovophon - slender proportional pendulum bank

This is a **separate upper-bank layout study**, not a completed replacement machine. It retains the musical pitch/drive ratios and proportional arm lengths. It does not install the full twelve-voice drive or prove a working pick under load.

## Layout

| Parameter | Previous Lab Frame | This study |
|---|---:|---:|
| Longest pivot-to-string radius |67.197 mm|109 mm|
| Shortest pivot-to-string radius |14.933 mm|24.222 mm|
| Longitudinal pivot pitch |24 mm|13.5 mm|
| Longitudinal bank span |264 mm|148.5 mm|
| Swing target |approximately +/-17-18 degrees|+/-45 degrees,90 total|
| Upper arm support |Individual bulky hanger/follower assemblies|Two straight4 mm tube spines and paired small carrier cheeks|
| Arm tube |Solid rectangular model arms|4 mm OD /2 mm ID aluminium tube|
| Pivot bearings |Larger6 mm shaft bearings|Two3 x6 x2.5 mm bearings per pivot|

All twelve arms scale up by the same factor,62.21%. Their radii are109 divided by the exact pitch ratio. Speaking lengths remain330 divided by the same ratio. String heights, lane pitch, third bridges and tuning targets are retained. Longitudinal pick positions are brought towards the midpoints of their speaking lengths while remaining inside them.

Static CAD envelope:394 x201 x195.57 mm (length xwidth xheight). Reference swept-envelope estimate, including0.3 mm tessellation allowance per side: approximately394.6 x206.2 x196.2 mm. The wide sweep therefore occupies slightly more lateral space than the stationary picture. The previous full Lab Frame envelope was approximately394 x203 x197 mm.

Proportional radii with strings at one height require different pivot heights. The pivots therefore follow a stepped bank; a shared straight pivot shaft would change those geometric constraints. Two straight rails can still support the bank via short carrier cheeks.

## Checks performed

-181 positions per voice, half-degree increments through-45 to+45 degrees.
-No sampled moving-part contact with fixed geometry, apart from the intended flexible-pick contact with its own string.
-All twelve picks contact their own strings; no sampled wrong-string contacts.
-The rigid moving assemblies occupy disjoint longitudinal slabs, with7.5 mm minimum separation, so their relative phases cannot cause rotor-to-rotor contact in this reference geometry.
-The tightest longitudinal rotor-to-next-support allowance is1 mm in the assumed stack. Real groove retainers, fit tolerances and fittings must be checked before fixing production pitch.
-Valid native solids. Exact pitch/drive ratios and proportional string/arm dimensions retained.

The full eight-minute phase pattern remains a design target at3 rpm input. This file is not a completed timed mechanism: no full drive or coupler layout is installed, and no matching new animation/MIDI is claimed.

## What changed during the clearance work

The first layout touched neighbouring strings and one rail. The final design narrows the pick tips to1 mm and places their tips0.15 mm above the nominal string centreline, producing0.25 mm overlap with the upper surface of the modeled0.8 mm nylon. This includes string thickness in the contact check. Rear shaft overhangs were shortened, the rear rail shifted, and M3 clamp orientation changed to clear the rail at the wide swing.

This is a *reference pick setting*, not proof of adequate loudness or reliable release. The close10 mm string lanes limit how deeply a long circular pick path can engage without reaching another string. Pick compliance, string deflection, adjustment tolerance, wear and return-stroke release need a physical test. Do not simply increase intrusion to get more volume without another cross-string check.

## Parts and manufacturing direction

-24 miniature bearings with a verified catalogue size: [MR63-ZZ /673-ZZ,3 x6 x2.5 mm](https://www.123roulement.com/roulement-palier/roulement-bille/simple-rangee/mr63-zz). This is a dimensional sourcing candidate, not a load-life approval or final brand selection.
-3 mm precision steel shafts; cut lengths, retaining grooves, bearing inner/outer race retention and fits require detail.
-4 x1 mm aluminium tube for arms and shared support rails; straight cut stock, with custom end fittings and carrier cheeks.
-M3 socket-head routine adjustment provision, with2.5 mm Allen tool. Captive threads/nuts, clamp travel, preload and service access remain manufacturing details.
-The model depicts tube/pivot-hub and pick-socket interfaces geometrically. It does not provide a finished joining method, screw schedule or release drawings for these small fittings.

A109 mm4 x1 aluminium tube has a reference end-load bending compliance of about0.531 mm/N using69 GPa elastic modulus and an ideal fixed root. The actual hub, pick and joints add compliance. This estimate is not a structural test or fatigue validation.

## Required next engineering work

Repackage the complete positive drive around this bank; preserve all exact rate ratios and the eight-minute ideal repeat. Bought timing pulleys, bearings, collars, crank pins and coupler motion must fit the real13.5 mm pitch or force a documented change. The previous prototype drivetrain must not be assumed to fit this closer bank.

Then finish shaft/bearing retention, carrier-to-rail clamps, tube-to-hub joints, pick sockets, new frame attachment holes and soundbox mounting reliefs. Check the full coupled sweep and measure forces/torque/release in hardware. This study is not fabrication released and has not been physically tested.

The original Lab Frame and Prototype A are preserved. Local preview images illustrate this study but are intentionally excluded from GitHub under the author's no-media instruction.
