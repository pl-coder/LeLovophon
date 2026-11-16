# Design status — 11 November 2026

| Version | Status | Timing | Physical validation |
|---|---|---|---|
| Plucking Layout R5 | Current nominal geometry; repositioned complete stations and rear frame; recorded checks pass | Exact pentatonic ratios;480s at3rpm; inverse-ratio strings/arms | Unbuilt; child-powered starting/running effort is a goal, not a demonstrated result |
| Monopole R4 | Preceding rear-frame design; poor near-bridge C4 pick position identified | Same ratios and timing | Force/release unverified; R5 improves pick positions |
| Protokoto R3 | Checked source geometry; four-corner frame superseded |600mm bass speaking length; proportional strings/arms;480s | Unbuilt; final compact-eye corrections preserved in R4/R5 |
| Mechanical Revision R2 | Superseded source geometry: recorded clearance checks pass | Exact pentatonic ratios; 480 s at 3 rpm; proportional arms retained | Unbuilt. Final fits, threads, gear maker geometry, pick release, torque, stiffness and endurance remain physical gates |
| Direct gear, axle-clearance revision | FAILED assembly audit; local crank-rod gap corrected, other collisions unresolved | Exact pentatonic rates; 480 s ideal repeat at 3 rpm | Seven support/string clashes,16 shaft/support clashes, four arm/shaft motion clashes and further routing/mounting failures; no build |
| Lab Frame, original | Historical appearance/layout | Earlier chromatic drive ratios, pentatonic pitches; mismatch | None |
| Lab Frame Ratio Review | Earlier twelve-voice review | Pitch and average cam rotation match; 480 s ideal repeat at3 rpm | Known packaging/hub problems remain |
| Slender proportional bank | Upper-bank layout study; full drive not installed |109..24.222 mm arms;13.5 mm pitch;target +/-45 degrees;rates unchanged |181-position sampled sweep; hardware untested |
| Prototype A | Separate one-voice and9:2 test-fixture proposal | Pinned4-bar, compound60/20 and30/20 belt stages | CAD and mathematical checks only; not built |
| Unified160-minute | Parked alternative | 19-finger picking-wheel pattern;9600 s nominal cycle | Not built; not the Lab Frame |
| Earlier Harpe studies | Archive/provenance | Varies by file | Not build releases |

## Known release gates

- Confirm actual matched belt tooth profile; the candidate supplier's current GT2 and older S2M naming conflicts.
- Get supplier pulley dimensions and finish the bearing/shaft/collar stacks.
- Resolve full Lab Frame large-drive/tray/foot interference and small pulley hub/outer-bearing geometry.
- Machine-shop review of blind bores, threads, fit tolerances, clamp grip, pin capture and fastener access.
- Finish base brackets, rounded string eyelets, bridge fit-up and captive tensioner thrust capture.
- Test the flexible pick in both directions; measure actual release phase, string force and torque.
- Test endurance and simultaneous twelve-voice peak load before choosing the motor or claiming reliable real-time synchronization.

The original sampled clearance reports do not certify later supplier parts or manufacturing details. A clean render does not prove a machine works. No physical pass or supplier commitment is recorded.

## Archival source limitations

The working scripts include older revisions and may replace generated files, open documents or start renders when run. Read a script before executing it. They reference generated intermediate files and installed macOS applications not distributed here. Use version control and separate copies for experiments.

Media has been excluded at the author's request. Documents mentioning videos, renders or MIDI exports are historical descriptions of assets retained locally, not missing downloads from a promised release.

## Earlier direct-gear correction (superseded by R2)

The earlier rod/support sweep excluded the individual crank axles and missed a real collision. Reproducing 360 poses per voice found 553 positive-volume rod–crank-axle intersections across twelve channels. The current integral shaft/flange terminates at station X +4 mm; rods occupy X +5..+7 mm. Their axial slabs stay disjoint at every rotation angle, providing a continuous 1 mm gap from that crank component. The all-axle sampled sweep has no rod intersections, and the separate 72-pose support sweep has no intersections or invalid solids within its recorded scope. No tolerance, load, flex, wear, assembly or physical safety proof follows from these results.

The current candidate BOM replaces twelve separate crank disks/shafts with twelve integral crank shaft/flange candidates. Machining details, material, bearing thrust stack, output-gear locking, pin retention and measured torque remain release gates. The previously known Lab Frame belt/pulley problems apply to that older architecture; the direct-gear proposal has its own unresolved joints and gear supplier requirements.

## Earlier 9 November failed reality audit

[Measured audit and part names](../outputs/LeLovophon_Direct_Gear_Prototype/Reality_Audit/README.md). The current direct-gear CAD is not buildable as drawn. The saved-pose all-pairs audit and 360-pose arm/rod sweep find multiple independent failures. Published earlier passes remain limited to their stated exclusions and must not be read as a working-assembly pass. No corrected design or physical validation is claimed by this documentation update.

## Current R2 geometry correction

[R2 model and measured checks](../outputs/LeLovophon_Mechanical_Revision_R2/README.md) replace the failed body/string routes, support layout and joint reservations. All bridge feet are supported; back strings supply nonzero bridge downbearing; pin journals stop before washers; shaft clips, bearing shoulders/shims and positive gear cross-pins are explicit. The 0.3 mm PET tongues flex in the plucking direction. Full checked geometry passes, including new mount contacts caught during the wider review. The baseline/differential evidence is recorded, with exact moving-solid identity and final-file hashes. No physical build or manufacturing release is claimed.

The earlier pulley/belt gates concern historical architectures. R2's hand wheel is a bench input. Regulated 3 rpm operation and the real acoustic timing must be established after measuring the physical mechanism.

## Current R5 requirements and release gates

The current target is comfortable starting and continuous cranking by a school-age child, accounting for transmitted loads and drivetrain friction. No numerical acceptance force has been selected and no physical result is claimed. See [prototype requirements](Next_Prototype_Requirements.md), [R5 nominal checks](../outputs/LeLovophon_Pluck_Layout_R5/Verification_Summary.json), [force budget](../outputs/LeLovophon_Pluck_Layout_R5/Drive_Effort/README.md) and [gear/armature assessment](../outputs/LeLovophon_Pluck_Layout_R5/Drivetrain_Assessment/README.md).

Do not carry historical belt/pulley release gates over as though they describe the current direct-gear design. Current gates include actual gear root/material/hub ratings, bearing coaxiality and preload, journal/bush/washer clearance, clamp and brazed-joint holding, two-way PET release, real string tension and instrumented startup/full-cycle effort. Future woodshop cutting sheets remain a later deliverable.
