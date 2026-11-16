import json,hashlib,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'outputs/LeLovophon_Pluck_Layout_R5/Drivetrain_Assessment';d=json.loads((O/'Drivetrain_Loads.json').read_text());rows=d['per_voice']
maxrow=lambda k:max(rows,key=lambda r:r[k])
rod=maxrow('case_rocker_pin_reaction_N');gear=maxrow('case_gear_tangential_tooth_force_N');buck=min(rows,key=lambda r:r['ideal_steel_link_Euler_weak_axis_load_N']);roll=d['rolling_equal_per_bearing_torque_sensitivity'];mu=d['dry_bush_first_order_shared_crossing_sensitivity']
(O/'README.md').write_text(f'''# R5 gears, links, armatures and drivetrain resistance

The concern is justified: **the string-only4.03N scenario does not include actual gear, bearing, bush or arm-clamp losses**. The load-transfer calculation is useful, but the assembled drivetrain has not been tested. No CAD dimensions have been changed by this assessment.

## What the mechanism contains

There are12 separate gear meshes, each driving one crank/connecting-link/rocker/pendulum station. A voice passes through one gear mesh; it does not pass through all12 in series. The common shaft supplies their combined reflected loads.

The saved CAD contains59 rolling bearings:24 local crank bearings,24 local rocker bearings,9 common-input-shaft bearings including the crank console, and2 grip bearings. In addition,24 dry polymer link bushes and their thrust washers must move freely. The commonØ5mm shaft is supported by9 bearings whose centres need to be coaxial. Clearance in a CAD file does not establish alignment, running drag or freedom from binding.

## Conditional forces through the actual mechanism

The same nominal38N-per-string, all12 strings deflected0.2mm shared-crossing case was applied to the independent Exudyn rigid-body model. This time it includes moving-part gravity and applies the tip forces against positive input motion. It remains a conditional snapshot, not the measured operating load or an impact/jam calculation.

| Quantity | Calculated value in that case |
|---|---:|
| Largest tangential tooth force | {d['case_max_gear_tangential_tooth_force_N']:.3f}N ({gear['note']}) |
| Largest connecting-link end reaction | {d['case_max_link_end_reaction_N']:.3f}N |
| Total input torque, with gravity but without friction | {d['case_input_torque_with_gravity_Nm']:.4f}N·m |
| Equivalent tangential hand force at32mm | {d['case_input_torque_with_gravity_Nm']/.032:.2f}N |
| Largest nominal arm-tube bending stress from tip load | {d['case_max_ideal_arm_tube_bending_stress_MPa']:.2f}MPa |
| Largest ideal tube-only tip deflection from tip load | {d['case_max_ideal_arm_tube_tip_deflection_mm']:.3f}mm |
| Largest ideal common-shaft twist relative to crank | {d['case_max_solid5mm_common_shaft_twist_deg']:.3f}° |

The arm estimate treats a perfectly clamped, straightØ4/2mm brass tube of length equal to the entire arm radius, E=100GPa. It excludes hub slip, brazed/soldered joints, actual material grade and local notches. Shaft twist assumes solidØ5mm steel, G=80GPa, and the distributed branch torques; it excludes cross-hole weakening and joint compliance. These are idealised elastic estimates, not material allowables or safety factors. They identify a modest reference-case structural demand, not a certified capacity.

TheØ0.98mm cross-pin nominal double-shear stresses and link gross axial stresses are listed per voice in the CSV. They exclude hole stress concentration, plastic-gear bearing/tear-out, pin retention, grooves, wear and fatigue. Ideal straight2×1.5mm steel-link Euler loads range from {min(r['ideal_steel_link_Euler_weak_axis_load_N'] for r in rows):.0f} to {max(r['ideal_steel_link_Euler_weak_axis_load_N'] for r in rows):.0f}N with pinned ends and E=200GPa. That screen excludes initial bow, eccentric force application and weak eye sections; it is not an allowable compressive rating.

`Per_Voice_Loads.csv` also gives peak rod/tooth load per1N tangential tip force over each complete local crank revolution. Those normalized coefficients allow a measured release force to replace the arbitrary equal-string-deflection scenario. The reaction torques reflected through the exact gear ratios agree with the common drive reaction, after the shared input group's gravity correction.

## Why the gears and armatures can still feel stiff

A sensitivity calculation reflects rolling-bearing drag through the actual speed ratios and rocker velocities over the full480-second cycle. If **every one of the59 rolling bearings** had the same constant resisting torque, the additional peak hand force would be:

| Assigned drag per bearing | Additional peak hand force |
|---|---:|
| 0.1N·mm | {roll['scenarios'][0]['additional_peak_handle_force_N']:.2f}N |
| 0.5N·mm | {roll['scenarios'][1]['additional_peak_handle_force_N']:.2f}N |
| 1.0N·mm | {roll['scenarios'][2]['additional_peak_handle_force_N']:.2f}N |

**Those bearing torques are sensitivity inputs, not published ratings or measured values.** Different bearings, loads, lubrication, shields, preload and starting conditions will give different torques. At low speed, starting drag and binding can matter despite small inertial loads. [SKF's friction model](https://evolution.skf.com/us/using-a-friction-model-as-an-engineering-tool-2/) separates rolling, sliding, seals and lubricant drag; count alone cannot establish total torque.

For the specified dry link bushes, applying the [igus G dynamic friction range against steel](https://www.igus.eu/plain-bearing/materials/universal-use/iglidur-g-material-data) µ=0.08–0.15 to this snapshot's radial pin reactions gives a first-order extra {mu[0]['first_order_radial_dry_bush_hand_force_N']:.2f}–{mu[1]['first_order_radial_dry_bush_hand_force_N']:.2f}N at the handle. This uses the actual relative angular speeds and1.5mm journal radius. It omits startup/stiction, axial washer preload and the way friction changes reactions; it is not a prediction of assembled joint drag. A pin/washer stack tightened into contact can add much more resistance than this ideal radial-bush calculation.

No generic gear efficiency has been assigned. At these small torques, assigning an optimistic percentage would conceal the uncertain low-speed mesh and support drag. Plastic tooth strength and wear also depend on the actual tooth root, grade, finish, alignment and duty. The [gear manufacturer's Lewis-formula explanation](https://www.rushgears.com/tech-tools/gear-set-design-engine/instructions) treats tooth capacity separately from transmitted torque. The current CAD's faceted reference involute and unspecified root fillet have **not** received a production tooth-strength or wear rating.

## Priorities before changing sizes

1. **Measure and align the common shaft supports.** All9 bearings must share one straight axis without being forced into position. Use an alignment fixture/dummy shaft and measure unloaded torque before and after tightening each mount. Do not remove supports merely to reduce bearing count: shaft bending and gear centre-distance control must be rechecked first.
2. **Check the link joint stacks.** Shoulder journals, bush flanges, washers and end screws must preserve running clearance after tightening. They must remain free in both directions without excessive side play.
3. **Use a real gear-maker's tooth/root and hub design.** Confirm grade, permitted torque, bore/pin attachment and retention, backlash, face runout and wear. Current0.5mm-module,4mm-face geometry is a reference, not a rated production gear set. Increasing gear size or switching material is not yet justified by the reference-case forces alone.
4. **Prove the arm connections.** Test split-hub clamp holding/slip and the manufactured tube/hub/tip joints. A low tube stress does not prove those connections. Check loaded deflection and the acceptable timing error: exact tooth-count ratios do not eliminate elastic twist and backlash.
5. **Build and measure one complete station first.** Measure breakaway/running torque without string contact, then with the real string and pick, in both directions and through a full revolution. Add the other stations progressively, recording the torque increase. Finish with an instrumented whole-machine startup/full480-second cycle. A longer hand crank reduces hand effort but does not reduce internal tooth, pin or linkage loads.

The present evidence points toward **checking friction, alignment and connections before adding structural bulk**. It does not rank a weakest component by safety factor: supplier load ratings, final material grades, manufactured fits and measured peak pick/jam loads are missing. Neither the gears nor armatures are signed off for fabrication or physical performance.

CAD SHA256 `{d['cad_sha256']}`. Geometry and earlier R5 nominal collision evidence are unchanged. Physical test: not performed. Manufacturing release: false.
''')
# Small portable evidence bundle; local calculations refer to the separately supplied R5 reproduction data.
with zipfile.ZipFile(O/'R5_Drivetrain_Assessment.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in O.iterdir():
  if p.is_file() and p.suffix!='.zip':z.write(p,p.name)
print('DRIVETRAIN_NOTE_READY',O,flush=True)
