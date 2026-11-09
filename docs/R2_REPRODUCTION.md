# R2 geometry / verification reproduction

Use a separate checkout and background FreeCAD Python. Do not execute builders against a document open in the live FreeCAD UI. Scripts overwrite their own generated R2 outputs. No renderer binary, mesh cache or media is distributed.

`work/rebuild_mechanical/build.py` creates the final native document and nominal inventory. It imports exact ratio/four-bar functions from `work/direct_gear_math.py` and does not use inherited Lab Frame body geometry.

Run these with a FreeCAD-enabled Python (offscreen Qt for the builder):

1. `work/rebuild_mechanical/build.py`
2. `work/rebuild_mechanical/audit.py static`
3. `work/rebuild_mechanical/audit.py motion` — a fresh full twelve-voice check on the generated current model. It is computationally expensive. Shared input is verified separately below.
4. `work/rebuild_mechanical/check_input_envelopes.py` — continuous clearance of verified containing rotational envelopes.
5. `work/rebuild_mechanical/check_dimensions.py` — bridge support, lengths, measured face gaps and tensioner travel.
6. `work/rebuild_mechanical/finalize.py`
7. `work/rebuild_mechanical/export_reference.py` (reference STEP only).

These checks establish nominal geometry only. They do not establish thread engagement, fit tolerances, preload, force, elastic release, acoustic performance or physical safety.

The delivered result used completed full-motion baselines while the fixed bearing mounts were refined. All 283 saved moving BREPs were identical. `delta_envelopes.py` proves the revised fixed mounts clear verified motion envelopes, with actual 360-pose fallback for conservative-envelope overlaps. `combine_motion.py` records that evidence and resolves the two old mount contacts only because their replacement checks pass. The three `Baseline_Motion` files retain their original CAD hash; final reports carry the final CAD hash. `baseline_builder.py` is the exact earlier geometry recipe retained for provenance, not the current builder. To reproduce the incremental path, generate that baseline in an isolated checkout, save it as `work/rebuild_mechanical/clearance_baseline.FCStd`, run its voice checks, then build final R2 and run the delta check. Do not substitute a different baseline.

The delivered neutral views and all older films/audio remain local, per the author's instruction to keep media off GitHub. The current project status is unbuilt, not released for fabrication.
