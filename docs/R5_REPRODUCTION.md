# Reproducing R5 — 11 November 2026

The current source CAD is `outputs/LeLovophon_Pluck_Layout_R5/LeLovophon_Pluck_Layout_R5.FCStd`. Its SHA256 is `8b5322026e943034589d3b90ea17b8ebd58bd06830b3c0050511e0693e0f7148`. R3 supplies the exact final local gear/link/bearing geometry; R4 supplies the preceding rear-frame design. The current model remains unbuilt and is not a manufacturing release.

## Requirements and numerical checks

Read `docs/Next_Prototype_Requirements.md` and R5's `Design_Requirements.json`. Comfortable starting and continuous hand cranking by a school-age child is the current force/load/friction goal. No numerical force threshold or physical pass is recorded. The ideal 480-second repeat assumes a regulated3rpm input; hand-speed variation changes elapsed time without changing the gear tooth-count ratios.

The checked R5 model has1101 valid single-solid parts. Static pairs, local-geometry inheritance, motion-envelope/fallback checks and tensioner travel are recorded under `Checks/`. Prior local-pair evidence is preserved as provenance. A numerical clearance check is not a real contact, friction, acoustic or endurance test.

## CAD and geometry recipe

The scripts use FreeCAD's bundled Python and Qt libraries. Read their inputs before running them in a separate working checkout; they generate and replace outputs. They do not need the user's live FreeCAD session.

1. Keep the supplied final R3 native model as the checked input. `work/protokoto_r3/config.py` and `work/direct_gear_math.py` define the exact ratios and four-bar geometry.
2. Run `work/pluck_r5/build.py`. It copies complete R3 stations, relocates their X positions, constructs the rear frame, moves input bearing mounts and recuts the required cross-pin bores. It also generates the local tessellation cache used for rendering. The source native file is the final R3 compact-eye revision; do not substitute an earlier R3 build.
3. Run `work/pluck_r5/check.py` for the saved-pose all-pairs check, then `work/pluck_r5/motion.py` for source-geometry comparison, new fixed-world clearance and neighbouring station slabs. Read the scope and tolerance notes in their JSON outputs.
4. Run `work/pluck_r5/export_parts.py` for quotation-preview profiles. The R4 part identifiers remain because those profile shapes are unchanged; use R5 mounting coordinates. Then run `work/pluck_r5/estimates.py` for the explicitly idealised stiffness/mass screen.
5. Preserve final-file hashes when sharing results. Rebuilding and resaving a native CAD file can change its archive hash; never relabel old checks as having run on a different saved file.

The full dimensioned woodshop cutting sheet remains later work. The current part/profile preview is not a release to machine or assemble everything without fit/load review.

## Force calculations without a CAD application

R5's `Drive_Effort/Reproduction/` is a standalone portable calculation package. Create a separate Python environment, install the pinned `requirements.txt`, and run:

```sh
python model.py
python exudyn_check.py 480 .005
python exudyn_coincidence.py .2
python force_envelope.py
```

These use the supplied exact kinematic inputs and CAD-extracted moving masses/inertias. They verify ideal rigid-body load transfer, not measured pick release or friction. `work/pluck_r5/extract.py` regenerates the mass input from a newly built CAD; do not use old mass inputs after changing moving geometry/materials.

`work/drivetrain_r5/reactions.py` evaluates the conditional shared-crossing case with gravity and resisting tip loads. `assess.py` computes tooth/pin/link loads, ideal tube/shaft deformation and clearly labelled bearing/bush-friction sensitivities. It reads the R5 force inputs; supply generated `work/pluck_r5/mass_properties.json` or use the published standalone input. The full-cycle unloaded calculation, the pluck-only static check and the gravity-plus-pluck reaction snapshot are different load cases.

The actual measured maximum startup/running/coincidence torque remains a release gate. Begin with a complete manufactured station, then add stations and measure the assembled mechanism. A larger hand crank does not lower internal tooth/joint loads.

## Local studio film

Media are intentionally omitted from Git. The local film recipe preserves the approved sixteen-minute duration: two repeats of the480-second picture/sound cycle, each with a360-degree camera orbit and gentle vertical arc. It uses a Louis XV-style table, an empty Parisian-inspired studio, dark parquet, a white photographic sweep and f/1.8 depth of field.

- `work/render_lovophon_r5_paris.py` creates the scene from the generated R5 CAD mesh and per-part motion/material inventory. It checks97 camera poses for cropping and verifies identical opening/closing control transforms before saving a local Blender scene.
- `work/render_r5_paris_animation.py` renders frame intervals using exact rigid four-bar closure and tooth-count ratios. It batches triangles only when material/modifier/motion parent match. It does not simulate flexible picks, vibrating strings, gear friction or a physical test.
- `work/encode_r5_paris_16min.py` assembles the film, attaches the approved sampled-harp/salon-convolution track, verifies duration/frame counts and performs a full decode. The excluded source audio must be regenerated using the earlier sampled-harp/convolution recipes and their credits; see `docs/DIRECT_GEAR_REPRODUCTION.md`.

The established render sampling is12 unique picture samples per second delivered at24fps, with an explicit matching endpoint. Rigid-body animation and sampled harp sound are illustrations; they do not establish physical release timing or measured acoustic quality.
