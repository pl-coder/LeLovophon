"""Package R2 only when saved-pose, motion and adjustment checks agree."""
from pathlib import Path
import json,csv,hashlib,math
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs/LeLovophon_Mechanical_Revision_R2';C=O/'Checks'
sha=hashlib.sha256((O/'LeLovophon_R2.FCStd').read_bytes()).hexdigest()
static=json.loads((C/'Static_All_Pairs.json').read_text());dims=json.loads((C/'Dimensions_and_Tensioners.json').read_text());motion=json.loads((C/'Motion_Audit.json').read_text());calc=json.loads((O/'Drive_Calculations.json').read_text())
shared=json.loads((C/'Shared_Input_Continuous_Clearance.json').read_text());assert shared['all_angles_covered'] and not shared['unexpected']
assert all(x['cad_sha256']==sha for x in [static,dims,motion,shared]),'Stale check against a different CAD file'
assert not static['unexpected'] and not motion['unexpected'] and not dims['tensioner_unexpected_intersections']
assert not dims['invalid_shapes'] and all(x['fully_on_soundboard'] for x in dims['bridge_support'])
assert dims['max_speaking_length_error_mm']<1e-8
assert min(x['gap_mm'] for x in motion['neighbour_moving_slab_gaps'])>.99
summary=dict(revision='R2',cad_sha256=sha,status='PASS recorded nominal-geometry checks / UNBUILT',parts=static['parts'],all_pairs_tested=static['pair_count'],unexpected_saved_pose_intersections=0,unexpected_sampled_motion_intersections=0,unexpected_tensioner_travel_intersections=0,invalid_shapes=0,poses_per_voice=motion['poses_per_voice'],independent_gear_tooth_phase_samples=64,neighbour_moving_axial_gap_mm=min(x['gap_mm'] for x in motion['neighbour_moving_slab_gaps']),flange_to_front_carrier_mm=min(x['flange_to_fixed_carrier_mm'] for x in dims['measured_clearances']),crank_flange_to_rod_axial_gap_mm=1,journal_to_washer_axial_gap_mm=.1,usable_tensioner_travel_mm=21.8,minimum_back_break_angle_deg=dims['minimum_back_break_angle_deg'],all_bridge_feet_supported=True,max_speaking_length_error_mm=dims['max_speaking_length_error_mm'],repeat_seconds=480,input_rpm=3,physical_test_passed=False,manufacturing_release=False)
(O/'Verification_Summary.json').write_text(json.dumps(summary,indent=2))
with (O/'Tuning_and_Drive.csv').open('w',newline='') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['Voice','Note','Exact pitch and speed ratio','Frequency Hz (C3=130.81278265)','Speaking length mm','Arm radius mm','Driver teeth','Driven teeth','Crank rpm','Bridge X mm','Pick X mm'])
 for r in calc['voices']:
  ratio=float(Fraction(r['ratio']));w.writerow([r['index'],r['note'],r['ratio'],130.81278265*ratio,330/ratio,r['arm_radius_mm'],r['driver_teeth'],r['driven_teeth'],3*ratio,r['bridge_x'],r['pick_x']])
bom=[
 ('683ZZ shielded miniature bearing',48,'3 x 7 x 3 mm','Catalogue','Open 683 is narrower; match NSK abutment dimensions.'),
 ('MR105ZZ shielded bearing',4,'5 x 10 x 4 mm','Catalogue','Open MR105 is 3 mm wide; EZO ZZ dimensions used.'),
 ('Common input shaft',1,'5 mm diameter; 327 mm nominal length','Stock shaft + drilling','Cross-pin positions/clocking from CAD; finish fit shop drawing required.'),
 ('Module 0.5, 20 degree spur gears',24,'4 mm face; exact counts in Tuning_and_Drive.csv','Matched catalogue/custom family','0.08 mm nominal pair backlash; jig drill 1 mm pin bores after phasing. Supplier tooth geometry governs.'),
 ('Flush transverse drive pins',26,'1 mm nominal diameter','Stock pin stock cut/fit','24 gear pins plus two common-input retention pins; final fit and retention proof required.'),
 ('Paired carrier plates',24,'3.5 mm plate; 3 mm bearing pocket','CNC aluminium candidate','Same concept with voice-specific P/Q locations; local pockets, shoulders and countersinks in CAD.'),
 ('Crank shaft / flange',12,'3 mm journals; R12 flange; 10 mm crank throw','Custom turning + drilling','Retaining-ring groove and flush gear pin; integral flange avoids rod/axle clash.'),
 ('Rocker shaft / lever',12,'3 mm journals; 14 mm rocker','Custom machining','One-piece torque path; removable split-clamp visible arm.'),
 ('POM connecting links',12,'2 mm plate; 3.04 mm journal holes','CNC/laser service + finish ream','Lengths in Drive_Calculations.json; no glued pins.'),
 ('Shoulder journals',24,'3 mm journal; internal M1.6 end screw','Custom turned pins','Journal stops before washer; fit to flange/rocker must be reviewed.'),
 ('Journal washers',24,'1.7 mm ID; 5.6 mm OD; 0.5 mm thick','Catalogue/custom shim','Beyond end of 3 mm journal, over M1.6 screw only.'),
 ('Journal end screws',24,'M1.6','Catalogue','Socket-head reference; nominal thread core only in CAD.'),
 ('Rear shaft E-clips',24,'3 mm shaft nominal; reference groove','Catalogue to final drawing','Final clip manufacturer groove/clearance must be substituted/rechecked.'),
 ('Bearing outer-race retainers',48,'1.2 mm plate; ID6.4','Custom sheet part','Two countersunk M2 screws each; clamp outer race only.'),
 ('M2 female standoffs + 0.5 mm shim',24,'6 mm length; 6.5 mm assembled gap','Catalogue + shim','Two per carrier pair; M2 countersunk screws from both sides.'),
 ('Visible arm assemblies',12,'R109 / ratio; 4 mm OD tube','Brass soldered subassembly candidate','Hub/tube/tip block are one removable assembly. Material and solder joint require test; not aluminium-to-brass brazing.'),
 ('PET spring tongues',12,'0.3 mm sheet; free tongue ~4.85 mm','Cut from stock sheet','Thin direction follows pluck; countersunk M1.6 tip screw. Physical two-way release test essential.'),
 ('Rear tube frame',1,'8 mm OD / 6 mm ID tube','Stock tube + welded fabrication','Posts behind swing paths; welded module removes from body via eight M3 bolts.'),
 ('Soundbox top/bottom',2,'355 x 178 x 3 mm','Plywood cut service','Body walls 6 mm; joints, bottom retention and bridge-seat finish require woodworking drawings.'),
 ('Nylon strings',12,'0.8 mm nominal unwound nylon','String/leader stock','Gauge, material density, creep, knot strength and final tension measured on bench.'),
 ('Third bridges',12,'12 x 8 mm feet; R2 crowns','Custom wood/brass candidate','Wedge bodies, supported feet, seated 0.1 mm crown grooves; 12 mm back-saddle drop.'),
 ('Lead screws',12,'M4 x 45 socket-head nominal','Catalogue','Each with two jam nuts, thrust washer, captured M4 carriage nut.'),
 ('Tensioner carriages',12,'21.8 mm tested usable travel','CNC/printed-metal candidate','Rounded/hand-finished nylon hole and stopper knot; shop to approve material.'),
 ('Slotted tensioner angle',1,'3 mm sheet with bottom flange','Laser + brake service','Four spacer mounts outside outer carriage lanes.'),
 ('Hand test wheel with stepped hub',1,'50 mm diameter; flush 1 mm pin','Machined or fabricated','Manual bench input. 480 seconds requires a regulated 3 rpm input; motor not selected or rated.'),
]
with (O/'Candidate_BOM.csv').open('w',newline='') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['Part family','Quantity','Nominal specification','Procurement route','Release note']);w.writerows(bom)
notes=f'''# Le Lovophon R2 — corrected mechanical layout

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
| Zero bridge downbearing | Back saddle 12 mm lower than the speaking plane; modeled break angles {dims['minimum_back_break_angle_deg']:.3f}–{dims['maximum_back_break_angle_deg']:.3f} degrees. Grooves seat the nominal strings. |
| Washer over full-size pin | A 3 mm shouldered journal ends 0.1 mm before the washer; only the M1.6 end screw passes through its 1.7 mm bore. |
| Undefined rotating face clearance | Crank flange to fixed front carrier: 0.5 mm. Flange to rod: 1 mm. Bearing thrust load is routed through specified inner-race shims. |
| Implied torque/phase coupling | Integral crank and rocker shafts, flush gear cross-pins, split-clamp arm hubs, two standoffs tying each carrier pair. Gear phase is set in a jig before cross-drilling. |
| Pick stiff in the plucking direction | Replaceable 0.3 mm PET tongues face their thin direction into the pluck, fastened in brass tip blocks. |

## Recorded checks

- {static['parts']} valid saved part shapes; {static['pair_count']:,} saved-pose pairs examined with bounding-box filtering and native solid intersections: **zero unintended intersections**.
- Every voice swept at 360 crank phases. All moving parts checked against fixed solids; all independently moving local groups checked against one another. Gear-to-support tests use 5-degree intervals, and gear-to-gear tests use **64 distinct relative tooth phases** per pair.
- Shared input assembly checked continuously using containing rotational envelopes. Neighbouring moving station slabs have a phase-independent 1 mm minimum axial gap.
- All twelve tensioner carriages/nuts/knots checked at 23 positions through **21.8 mm usable travel**: zero unintended intersections.
- All bridge feet supported; maximum speaking-length error {dims['max_speaking_length_error_mm']:.3g} mm. Ideal rates and proportional radii retained; **480 seconds at 3 rpm**, 24 common-input turns.

The full voice sweep is retained as a baseline. Every final moving solid has the same exact saved BREP hash; all modified fixed mounts are rechecked with verified containing motion envelopes and actual poses wherever needed. This avoids treating any old pass as evidence for changed geometry.

Checks are tied to CAD SHA-256 `{sha}`. Raw results are in `Checks/`; `Verification_Summary.json` provides the compact result. Intentional own pick/string contact and tied knot/string envelopes are reported separately.

The assembly is approximately {calc['envelope_mm'][0]:.0f} x {calc['envelope_mm'][1]:.0f} x {calc['envelope_mm'][2]:.0f} mm at the saved pose. Allow additional working clearance for the swing. It is a small tabletop instrument, not a 100 mm-deep briefcase mechanism.

## What remains physical engineering

Retainer mounting holes are nominal **M2 threaded-envelope reservations**, not tap-drill diameters. The final drawing must call out the M2 tap and its correct pilot; a clearance-sized cylinder displayed in a simplified thread model is not a drilling instruction. The same rule applies to M1.6 journal/tip and M4 nut/screw thread envelopes.


The gear teeth are faceted involute reference solids; root transitions, final backlash, fit classes, edge radii and thread geometry require the gear maker/machine shop's drawings. Threads in this model use clear nominal envelopes, so the collision check does not prove thread engagement, preload or load capacity. Bearing internals and real race tolerances are not simulated. Catalogue retention rings must be chosen with their actual groove specification and then rechecked.

Before ordering twelve channels, build one low voice and one high-ratio voice. Tune real nylon; test anchors, tensioners and creep; set pick engagement; confirm clean release in both directions; measure hub/pin slip, bridge stability, frame flex and required starting/running torque. Run the worst simultaneous crossing and an endurance test. Select and regulate a motor only from measured loads. The hand wheel is the bench input; it cannot by itself guarantee an eight-minute wall-clock recording.

The fixed rear frame is a removable welded subassembly. Arm assemblies can be soldered brass tube/hub/tip units; the PET tongues, clamps, links, shafts, bearings, tensioners and strings remain serviceable. Final workshop drawings must detail the soundbox joints, bottom panel retention, material/fit choices and fastener access. Nothing here claims a prototype has been built or tested.

## Bearing references

The **shielded** suffix matters. R2 uses 48 683ZZ bearings (3 x 7 x 3 mm), with nominal inner shoulder OD4 and outer shoulder ID6.4 from [NSK's miniature bearing table](https://www.nsk.com/content/dam/nsk/common/catalogs/ctrgPdf/bearings/e1103c_partc.pdf). The four common-shaft bearings are **MR105ZZ**, 5 x 10 x 4 mm, with inner abutment OD5.9 and an outer shoulder ID8.6 within the 8.5–8.8 range in [EZO's MR105ZZ drawing](https://www.ezo-brg.co.jp/english/product/spec.php?eid=00457&unit=mm). Open versions have different widths. Confirm the exact ordered part drawing before cutting seats.

`Candidate_BOM.csv` separates catalogue stock from custom finishing. It is a review list, not an accepted supplier quote or order.
'''
(O/'README.md').write_text(notes)
print(json.dumps(summary,indent=2))
