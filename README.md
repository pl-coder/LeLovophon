# Le Lovophon

A portable, mechanically driven plucked-string instrument by **Paul Love**. Pitch and mechanical rhythm share the same exact pentatonic ratios. The current twelve-voice design has an **eight-minute ideal mechanical repeat** at a 3 rpm input.

This repository contains the CAD, technical drawings, parts lists, tuning data, calculations and generation scripts. **Media files are intentionally excluded:** no rendered images, videos, Blender scenes, audio/MIDI exports or bundled media archives.

## Current revision — 11 November 2026

**Current CAD: [Plucking Layout R5](outputs/LeLovophon_Pluck_Layout_R5/README.md). Nominal geometry checks pass; physical operation and drive effort remain unverified.**

Open [LeLovophon_Pluck_Layout_R5.FCStd](outputs/LeLovophon_Pluck_Layout_R5/LeLovophon_Pluck_Layout_R5.FCStd). Four identical flat-cut curved rear ribs leave the pendulums and strings exposed. The hollow700×220×60mm protokoto body carries twelve equal-gauge nominal1.05mm PVDF strings and movable third bridges. Picks now lie25–47% of speaking length from the nearer end; C4 moved from6.18mm to75mm from its bridge. Exact pitch/drive ratios, proportional arms and the480-second ideal cycle remain.

The [verification summary](outputs/LeLovophon_Pluck_Layout_R5/Verification_Summary.json) records1101 valid single-solid parts,605550 saved-pose pairs, no unexpected contacts in the recorded static/motion/adjustment scope, and a3mm minimum phase-independent gap between neighbouring moving station envelopes. These nominal checks do not establish manufactured fits, elastic pick release, friction, stiffness, fatigue or physical performance.

**Design goal: a school-age child should comfortably start and continuously hand-crank the complete instrument.** This is a force/load/friction requirement. It is not yet verified, and no numerical hand-force acceptance threshold has been agreed. The [force budget](outputs/LeLovophon_Pluck_Layout_R5/Drive_Effort/README.md) and [gear/armature assessment](outputs/LeLovophon_Pluck_Layout_R5/Drivetrain_Assessment/README.md) separate conditional plucking loads from actual drivetrain resistance. The model contains12 gear meshes,59 rolling bearings and24 dry link bushes. Real startup/running torque, alignment, release and peak coincidence loads require measurement.

[R5 reproduction notes](docs/R5_REPRODUCTION.md) cover CAD, checks, portable Exudyn calculations and the local sixteen-minute Paris studio film. Rendered media and sound remain excluded from this repository. [R3](outputs/LeLovophon_Protokoto_R3/README.md) and [R4](outputs/LeLovophon_Monopole_R4/README.md) are retained as the checked source geometry and preceding rear-frame revision; the older R2 and failed studies remain provenance.

## Earlier studies

| Purpose | File |
|---|---|
| Earlier slender proportional upper-bank study | [CAD and clearance findings](outputs/LeLovophon_Slender_Bank/README.md) |
| Earlier full twelve-voice Lab Frame review | [FreeCAD model](outputs/Lovophone_Lab_Frame_Ratio_Review.FCStd) |
| Build status and supplier routes | [Lab Frame engineering review](outputs/Lovophone_Lab_Frame_Build_Review.md) |
| Ratio audit | [Per-voice CSV](outputs/Lovophone_Lab_Frame_Ratio_Audit.csv) |
| One-string and high-ratio physical test fixtures | [Prototype A FreeCAD](outputs/Lovophone_Prototype_A/Lovophone_Prototype_A.FCStd) |
| Dimensioned prototype drawings and test procedure | [Eight-page PDF](outputs/Lovophone_Prototype_A/Prototype_A_Drawings.pdf) |
| Prototype bought/custom parts | [BOM](outputs/Lovophone_Prototype_A/Prototype_A_BOM.csv) |
| Full Lab Frame component inventory | [Procurement inventory](outputs/Lovophone_Lab_Frame_Procurement_Inventory.csv) |
| What is current, archived or still unproved | [Design status](docs/DESIGN_STATUS.md) |
| Play the earlier Lab Frame review in a browser, no FreeCAD (a simulation with labelled additions, not a hardware test; it does not model the direct-gear prototype) | [sim/README.md](sim/README.md) |

## What it does

Twelve equal-gauge unwound PVDF candidate strings use movable third bridges over a timber soundbox. A shared mechanical drive gives each plucker a rationally related rate. The target is a small, serviceable, exposed mechanism that can be carried in one hand and understood by looking at it.

```mermaid
flowchart LR
    A[Shared input: 3 rpm] --> B[Exact mechanical ratios]
    B --> C[Driven plucking arms]
    C --> D[Equal-gauge strings and third bridges]
    D --> E[Timber soundbox]
```

| Note | Pitch / average crank speed relative to C3 | Speaking length, mm |
|---|---:|---:|
| C3 | 1 | 600.000000 |
| D3 | 9/8 | 533.333333 |
| E3 | 5/4 | 480.000000 |
| G3 | 3/2 | 400.000000 |
| A3 | 5/3 | 360.000000 |
| C4 | 2 | 300.000000 |
| D4 | 9/4 | 266.666667 |
| E4 | 5/2 | 240.000000 |
| G4 | 3 | 200.000000 |
| A4 | 10/3 | 180.000000 |
| C5 | 4 | 150.000000 |
| D5 | 9/2 | 133.333333 |

The denominators have least common multiple 24. At 20 seconds per input revolution, all ideal local crank phases return after `24 × 20 = 480 seconds`. Arm radii and ideal speaking lengths follow inverse pitch ratios. The arms are mechanically forced, not freely swinging pendulums whose natural frequency would obey a different length relationship.

## Real-world status

**This is an engineering project, not a finished or physically validated instrument.**

The Lab Frame review fixes the old pitch/rotation mismatch, but its largest reference pulleys conflict with existing tray/mounting details, and some small pulley hubs cannot house the modeled bearing bore. Those findings are recorded, not claimed solved by the presentation render.

Prototype A is a separate test-fixture proposal. It uses a pinned four-bar linkage instead of a spring-loaded follower and swing-amplifier belt, plus two catalogue timing stages `(60/20) × (30/20) = 9/2`. The calculation and sampled rigid-clearance checks pass; no fixture has been built. Belt tooth-profile compatibility, actual supplier dimensions, fits, tensioner thrust capture, flexible-pick release, starting torque and endurance remain physical release gates.

For the earlier separate fixture, see [the prototype README](outputs/Lovophone_Prototype_A/README.md) and [drawings](outputs/Lovophone_Prototype_A/Prototype_A_Drawings.pdf) before quoting or machining. STEP files show nominal/pilot geometry; specified threads and fits in the drawings govern.

## Open and work on the project

- Open `.FCStd` files in FreeCAD. The project was developed with the installed FreeCAD application on macOS; no cross-version compatibility claim is made.
- Use individual prototype `.step` files with the PDF for machining review. The assembly reference is not an instruction to machine every displayed object.
- `work/` preserves the generation and checking scripts and selected native checkpoints. They require application-specific Python libraries such as FreeCAD or Blender. They are historical working scripts, not a one-command build system.
- Workspace-root strings in the archived scripts have been made relative to this checkout. Override with `LOVOPHON_WORKSPACE` when reconstructing a legacy workspace. Generated meshes, renderer binaries, intermediate frame sequences and logs are not included. Some scripts depend on those generated intermediates; inspect their inputs before running them.
- `outputs/` retains historical filenames so source references and design provenance remain understandable. Some old documents refer to excluded media. Their playback/synchronization instructions do not override the current design status.

Run the lightweight repository checks with Python 3.11 or newer:

```sh
python3 scripts/verify_project.py
```

These check the packaged files, exact ratio mathematics, source syntax and recorded fixture checks. They do not test hardware.

## Manufacturing direction

Prefer catalogue bearings, shafts, collars, matched belts/pulleys and metric fasteners. Concentrate custom work into repeated plates, bearing carriers, clamp hubs, journal pins, wear parts and the soundbox. UCAL Systems is a prospective manufacturing route; no supplier acceptance, order, final price or delivery commitment is claimed.

## Earlier branches of the design

The repository preserves earlier clockwork, electric, chromatic and pentatonic studies. The **Unified 160-minute picking-wheel design is parked**, not the current Lab Frame. Its mechanical layout and event pattern differ. Do not mix the old chromatic timing, the Unified picking pattern and the corrected eight-minute Lab Frame timing.

## Licence

No project licence has been selected yet. Third-party applications and catalogue components retain their own terms. Do not interpret the repository as a tested construction kit.
