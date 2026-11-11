# R4 hand-crank effort assessment — 11 November 2026

The required operating hand force is **not yet established**. This is now an explicit unresolved design requirement. The previous 0.1 N·m example was only a lever-arm conversion. The new calculations below use the actual CAD and expose which dimensions drive effort.

## What is calculated

The current 32 mm crank and all 367 moving CAD solids were reduced into 37 rigid groups. Mass, centre of gravity and rotary inertia were taken from the saved geometry using the stated nominal material densities. Exact rational gear constraints and the original four-bar geometry were retained. Gravity and constant-speed inertia were evaluated throughout the full 480-second cycle at 3 rpm.

An independent Exudyn 1.13.6 model uses 37 planar rigid bodies, revolute joints and ideal gear-coordinate constraints. Its full-cycle drive reaction agrees with the separate virtual-work calculation within 1.23e-07 N·m at a 0.005 s integration step. This verifies the ideal rigid-body model, not real friction or pick release. The ideal mechanism with no plucking and no friction reaches about 0.36 N of absolute hand force. Real operating effort cannot be inferred from this small value.

## The important result: pluck sensitivity

At the shared centre crossing, small sideways deflection of a speaking string needs approximately:

`F_string = T × displacement × (1/a + 1/b)`

Here T is the nominal 37.98 N string tension; a and b are the two distances from the picking point to the third bridge and the common speaking nut. The ideal constant-tension, small-deflection assumption excludes string/contact dynamics. Torque is reflected through the exact instantaneous linkage and gear leverage, then divided by the 0.032 m crank throw.

**If all twelve strings are each deflected sideways by the same amount at that shared crossing**, the pluck-only force sensitivity is 50.14 N of hand force per mm of string deflection:

| Assumed common deflection | Current 32 mm throw | Hypothetical 64 mm throw |
|---|---:|---:|
| 0.1 mm | 5.0 N | 2.5 N |
| 0.2 mm | 10.0 N | 5.0 N |
| 0.5 mm | 25.1 N | 12.5 N |

These rows are scenarios, **not a predicted force range or a statement of the actual string displacement**. Friction and actual pick flex/release are not included. A separate Exudyn static load case reproduces the 0.2 mm scenario to within 5.8e-11 N·m. It applies the calculated tip forces at the shared crossing; it does not simulate flexible PET/string contact.

C4 is picked only 6.18 mm from its third bridge. Its local string stiffness is 6.27 N/mm, versus 0.51 N/mm for C3. C4 accounts for roughly 30% of the equal-displacement coincidence force. This placement should be reviewed before finalising the drive. Moving a station requires a fresh clearance check; no geometry has been changed in this assessment.

## What remains to establish the actual number

The missing input is the **measured force-versus-motion and release behaviour of the selected pick on the selected tensioned line**, plus actual bearing/bush/gear losses and breakaway drag. The 0.3 mm PET tongue is flexible, and string displacement is not the same as arm travel or nominal pick overlap. We cannot choose an arbitrary PET modulus/contact coefficient and treat its result as a verified crank force.

A useful first test is one representative string and adjustable pick at its real a/b distances, recording lateral force and string displacement through release. Include C4's present near-bridge position and a position farther from the bridge. Feed that measured force trace into the dynamics model, preserve the phases, and simulate the combined twelve-voice torque. Then measure a complete dry drivetrain's startup and running drag. A spring balance or force gauge pulled tangentially at the known crank radius gives torque as force × radius. The complete mechanism's final test must capture the highest startup/coincidence force, not only average effort.

A longer crank reduces hand force but leaves shaft/gear/link loads unchanged. A reduction stage would change the input reference speed and turns required for the eight-minute cycle; any such change must preserve the intended musical ratios and be checked explicitly.

Until the pick and drivetrain losses are established, the R4 geometry remains a quotation/design candidate rather than a released build. No motor has been sized and no maximum user force is claimed.

## Free/open-source tools checked

| Project | Role in this assessment | Availability/status checked |
|---|---|---|
| [Exudyn](https://github.com/jgerstmayr/EXUDYN) | Recommended immediate tool: rigid/flexible multibody dynamics, constraint reactions and custom force laws | Free/open source per author; version 1.13.6 installed and successfully used in an isolated project environment on this Apple-silicon Mac. [Documentation](https://exudyn.readthedocs.io/en/latest/) |
| [Project Chrono](https://github.com/projectchrono/chrono) | Alternative for detailed flexible picks, strings, springs and contact | BSD-3; supports rigid/flexible mechanics, contact and forces/torques; Python interface available. [Official features](https://www.projectchrono.org/) |
| [MBDyn](https://www.mbdyn.org/) | Alternative established rigid/flexible multibody solver | Free/open source; includes nonlinear rigid/flexible mechanics and constraints. Not installed/tested here |
| [FreeCADMbD](https://github.com/aiksiongkoh/FreeCADMbD) | Possible closer CAD integration | [FreeCAD's article](https://freecad.github.io/Website/news/amazing-multibody-dynamics-with-fem/) calls this integration work in progress; current repository build instructions emphasise Windows. Not installed here |

No paid simulation licence is needed for the calculations already completed. Software still needs the actual friction and contact inputs. [SKF's friction-model explanation](https://evolution.skf.com/en/using-a-friction-model-as-an-engineering-tool-3/) describes the dependence on lubrication, speed and starting conditions. [igus G data](https://www.igus.eu/plain-bearing/materials/universal-use/iglidur-g-material-data) also states that friction changes with operating conditions and mating surfaces; its coefficient range alone is not a complete machine torque model.

## Reproducibility

CAD SHA256: `1eaa9f0972b8fe906b78259f1bb48794cb66ac507e2f8cc8157353e0c2f8c531`. The existing CAD file and all nominal clearance evidence remain unchanged. JSON verification reports, per-voice CSV and the force-sensitivity graphic accompany this note. `Reproduction/` contains the exported mass properties, exact kinematic inputs, the two independent calculation approaches and pinned environment package versions. It does not contain third-party solver binaries. Full flexible-contact simulation and physical validation remain outstanding.
