# Le Lovophon R2 — corrected mechanical layout

**The saved CAD passes the recorded nominal-geometry checks. It is unbuilt and is not a manufacturing release.**

Open `LeLovophon_R2.FCStd`. The failed axle-clearance revision is preserved separately; R2 replaces its body, string routes, bearing supports and joints. The soundtrack and old film do not demonstrate this revision's physical sound or operation.

## What changed

| Earlier failure | R2 correction |
|---|---|
| Supports through strings | Rear frame and carrier load paths are outside the string bed; posts moved behind the swing paths. |
| Tubes through rotating axles/bearings | Explicit bored housings, outer-race shoulders/retainers and inner-race thrust shims. No support ends at a shaft axis. |
| Arms hitting the next pivot shaft | Short, clipped shaft ends and arm planes shifted rearward. All neighbouring moving X slabs have at least 1 mm separation at every phase. |
| Blocked anchor tails | Continuous tangent string routes through real anchor holes, with stopper-knot envelopes. Right tails clear the body edge. |
| Unsupported outer bridges | A real 355 x 178 mm soundboard supports every 12 x 8 mm bridge foot. |
| Zero bridge downbearing | Back saddle 12 mm lower than the speaking plane; modeled break angles 2.529–38.660 degrees. Grooves seat the nominal strings. |
| Washer over full-size pin | A 3 mm shouldered journal ends 0.1 mm before the washer; only the M1.6 end screw passes through its 1.7 mm bore. |
| Undefined rotating face clearance | Crank flange to fixed front carrier: 0.5 mm. Flange to rod: 1 mm. Bearing thrust load is routed through specified inner-race shims. |
| Implied torque/phase coupling | Integral crank and rocker shafts, flush gear cross-pins, split-clamp arm hubs, two standoffs tying each carrier pair. Gear phase is set in a jig before cross-drilling. |
| Pick stiff in the plucking direction | Replaceable 0.3 mm PET tongues face their thin direction into the pluck, fastened in brass tip blocks. |

## Recorded checks

- 803 valid saved part shapes; 322,003 saved-pose pairs examined with bounding-box filtering and native solid intersections: **zero unintended intersections**.
- Every voice swept at 360 crank phases. All moving parts checked against fixed solids; all independently moving local groups checked against one another. Gear-to-support tests use 5-degree intervals, and gear-to-gear tests use **64 distinct relative tooth phases** per pair.
- Shared input assembly checked continuously using containing rotational envelopes. Neighbouring moving station slabs have a phase-independent 1 mm minimum axial gap.
- All twelve tensioner carriages/nuts/knots checked at 23 positions through **21.8 mm usable travel**: zero unintended intersections.
- All bridge feet supported; maximum speaking-length error 1.42e-14 mm. Ideal rates and proportional radii retained; **480 seconds at 3 rpm**, 24 common-input turns.

The full voice sweep is retained as a baseline. Every final moving solid has the same exact saved BREP hash; all modified fixed mounts are rechecked with verified containing motion envelopes and actual poses wherever needed. This avoids treating any old pass as evidence for changed geometry.

Checks are tied to CAD SHA-256 `264084afcb461bb55a4e22db9f73d9ee841b749e00c6255b3f3264debac94e67`. Raw results are in `Checks/`; `Verification_Summary.json` provides the compact result. Intentional own pick/string contact and tied knot/string envelopes are reported separately.

The assembly is approximately 378 x 221 x 258 mm at the saved pose. Allow additional working clearance for the swing. It is a small tabletop instrument, not a 100 mm-deep briefcase mechanism.

## What remains physical engineering

Retainer mounting holes are nominal **M2 threaded-envelope reservations**, not tap-drill diameters. The final drawing must call out the M2 tap and its correct pilot; a clearance-sized cylinder displayed in a simplified thread model is not a drilling instruction. The same rule applies to M1.6 journal/tip and M4 nut/screw thread envelopes.


The gear teeth are faceted involute reference solids; root transitions, final backlash, fit classes, edge radii and thread geometry require the gear maker/machine shop's drawings. Threads in this model use clear nominal envelopes, so the collision check does not prove thread engagement, preload or load capacity. Bearing internals and real race tolerances are not simulated. Catalogue retention rings must be chosen with their actual groove specification and then rechecked.

Before ordering twelve channels, build one low voice and one high-ratio voice. Tune real nylon; test anchors, tensioners and creep; set pick engagement; confirm clean release in both directions; measure hub/pin slip, bridge stability, frame flex and required starting/running torque. Run the worst simultaneous crossing and an endurance test. Select and regulate a motor only from measured loads. The hand wheel is the bench input; it cannot by itself guarantee an eight-minute wall-clock recording.

The fixed rear frame is a removable welded subassembly. Arm assemblies can be soldered brass tube/hub/tip units; the PET tongues, clamps, links, shafts, bearings, tensioners and strings remain serviceable. Final workshop drawings must detail the soundbox joints, bottom panel retention, material/fit choices and fastener access. Nothing here claims a prototype has been built or tested.

## Bearing references

The **shielded** suffix matters. R2 uses 48 683ZZ bearings (3 x 7 x 3 mm), with nominal inner shoulder OD4 and outer shoulder ID6.4 from [NSK's miniature bearing table](https://www.nsk.com/content/dam/nsk/common/catalogs/ctrgPdf/bearings/e1103c_partc.pdf). The four common-shaft bearings are **MR105ZZ**, 5 x 10 x 4 mm, with inner abutment OD5.9 and an outer shoulder ID8.6 within the 8.5–8.8 range in [EZO's MR105ZZ drawing](https://www.ezo-brg.co.jp/english/product/spec.php?eid=00457&unit=mm). Open versions have different widths. Confirm the exact ordered part drawing before cutting seats.

`Candidate_BOM.csv` separates catalogue stock from custom finishing. It is a review list, not an accepted supplier quote or order.
