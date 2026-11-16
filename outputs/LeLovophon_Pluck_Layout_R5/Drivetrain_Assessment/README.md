# R5 gears, links, armatures and drivetrain resistance

The concern is justified: **the string-only4.03N scenario does not include actual gear, bearing, bush or arm-clamp losses**. The load-transfer calculation is useful, but the assembled drivetrain has not been tested. No CAD dimensions have been changed by this assessment.

## What the mechanism contains

There are12 separate gear meshes, each driving one crank/connecting-link/rocker/pendulum station. A voice passes through one gear mesh; it does not pass through all12 in series. The common shaft supplies their combined reflected loads.

The saved CAD contains59 rolling bearings:24 local crank bearings,24 local rocker bearings,9 common-input-shaft bearings including the crank console, and2 grip bearings. In addition,24 dry polymer link bushes and their thrust washers must move freely. The commonØ5mm shaft is supported by9 bearings whose centres need to be coaxial. Clearance in a CAD file does not establish alignment, running drag or freedom from binding.

## Conditional forces through the actual mechanism

The same nominal38N-per-string, all12 strings deflected0.2mm shared-crossing case was applied to the independent Exudyn rigid-body model. This time it includes moving-part gravity and applies the tip forces against positive input motion. It remains a conditional snapshot, not the measured operating load or an impact/jam calculation.

| Quantity | Calculated value in that case |
|---|---:|
| Largest tangential tooth force | 0.956N (G4) |
| Largest connecting-link end reaction | 0.562N |
| Total input torque, with gravity but without friction | 0.1404N·m |
| Equivalent tangential hand force at32mm | 4.39N |
| Largest nominal arm-tube bending stress from tip load | 1.25MPa |
| Largest ideal tube-only tip deflection from tip load | 0.025mm |
| Largest ideal common-shaft twist relative to crank | 0.412° |

The arm estimate treats a perfectly clamped, straightØ4/2mm brass tube of length equal to the entire arm radius, E=100GPa. It excludes hub slip, brazed/soldered joints, actual material grade and local notches. Shaft twist assumes solidØ5mm steel, G=80GPa, and the distributed branch torques; it excludes cross-hole weakening and joint compliance. These are idealised elastic estimates, not material allowables or safety factors. They identify a modest reference-case structural demand, not a certified capacity.

TheØ0.98mm cross-pin nominal double-shear stresses and link gross axial stresses are listed per voice in the CSV. They exclude hole stress concentration, plastic-gear bearing/tear-out, pin retention, grooves, wear and fatigue. Ideal straight2×1.5mm steel-link Euler loads range from 71 to 251N with pinned ends and E=200GPa. That screen excludes initial bow, eccentric force application and weak eye sections; it is not an allowable compressive rating.

`Per_Voice_Loads.csv` also gives peak rod/tooth load per1N tangential tip force over each complete local crank revolution. Those normalized coefficients allow a measured release force to replace the arbitrary equal-string-deflection scenario. The reaction torques reflected through the exact gear ratios agree with the common drive reaction, after the shared input group's gravity correction.

## Why the gears and armatures can still feel stiff

A sensitivity calculation reflects rolling-bearing drag through the actual speed ratios and rocker velocities over the full480-second cycle. If **every one of the59 rolling bearings** had the same constant resisting torque, the additional peak hand force would be:

| Assigned drag per bearing | Additional peak hand force |
|---|---:|
| 0.1N·mm | 0.34N |
| 0.5N·mm | 1.68N |
| 1.0N·mm | 3.36N |

**Those bearing torques are sensitivity inputs, not published ratings or measured values.** Different bearings, loads, lubrication, shields, preload and starting conditions will give different torques. At low speed, starting drag and binding can matter despite small inertial loads. [SKF's friction model](https://evolution.skf.com/us/using-a-friction-model-as-an-engineering-tool-2/) separates rolling, sliding, seals and lubricant drag; count alone cannot establish total torque.

For the specified dry link bushes, applying the [igus G dynamic friction range against steel](https://www.igus.eu/plain-bearing/materials/universal-use/iglidur-g-material-data) µ=0.08–0.15 to this snapshot's radial pin reactions gives a first-order extra 0.09–0.16N at the handle. This uses the actual relative angular speeds and1.5mm journal radius. It omits startup/stiction, axial washer preload and the way friction changes reactions; it is not a prediction of assembled joint drag. A pin/washer stack tightened into contact can add much more resistance than this ideal radial-bush calculation.

No generic gear efficiency has been assigned. At these small torques, assigning an optimistic percentage would conceal the uncertain low-speed mesh and support drag. Plastic tooth strength and wear also depend on the actual tooth root, grade, finish, alignment and duty. The [gear manufacturer's Lewis-formula explanation](https://www.rushgears.com/tech-tools/gear-set-design-engine/instructions) treats tooth capacity separately from transmitted torque. The current CAD's faceted reference involute and unspecified root fillet have **not** received a production tooth-strength or wear rating.

## Priorities before changing sizes

1. **Measure and align the common shaft supports.** All9 bearings must share one straight axis without being forced into position. Use an alignment fixture/dummy shaft and measure unloaded torque before and after tightening each mount. Do not remove supports merely to reduce bearing count: shaft bending and gear centre-distance control must be rechecked first.
2. **Check the link joint stacks.** Shoulder journals, bush flanges, washers and end screws must preserve running clearance after tightening. They must remain free in both directions without excessive side play.
3. **Use a real gear-maker's tooth/root and hub design.** Confirm grade, permitted torque, bore/pin attachment and retention, backlash, face runout and wear. Current0.5mm-module,4mm-face geometry is a reference, not a rated production gear set. Increasing gear size or switching material is not yet justified by the reference-case forces alone.
4. **Prove the arm connections.** Test split-hub clamp holding/slip and the manufactured tube/hub/tip joints. A low tube stress does not prove those connections. Check loaded deflection and the acceptable timing error: exact tooth-count ratios do not eliminate elastic twist and backlash.
5. **Build and measure one complete station first.** Measure breakaway/running torque without string contact, then with the real string and pick, in both directions and through a full revolution. Add the other stations progressively, recording the torque increase. Finish with an instrumented whole-machine startup/full480-second cycle. A longer hand crank reduces hand effort but does not reduce internal tooth, pin or linkage loads.

The present evidence points toward **checking friction, alignment and connections before adding structural bulk**. It does not rank a weakest component by safety factor: supplier load ratings, final material grades, manufactured fits and measured peak pick/jam loads are missing. Neither the gears nor armatures are signed off for fabrication or physical performance.

CAD SHA256 `8b5322026e943034589d3b90ea17b8ebd58bd06830b3c0050511e0693e0f7148`. Geometry and earlier R5 nominal collision evidence are unchanged. Physical test: not performed. Manufacturing release: false.


## Child-powered drive requirement

A school-age child should be able to start and continuously hand-crank the complete instrument comfortably at its nominal operating speed. Size the drivetrain for combined plucking load, starting/running gear and bearing friction, linkage resistance and alignment sensitivity.

Scope: operating effort, transmitted loads and friction. Assess starting torque, continuous running effort and peak coincidence loads. The operating-force goal remains unverified; the current calculations are conditional and do not establish an achieved child-operable rating.
