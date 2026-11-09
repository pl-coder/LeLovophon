# Direct-gear revision and local music/render workflow

Current native CAD: `outputs/LeLovophon_Direct_Gear_Prototype/Axle_Clearance_Revision/LeLovophon_Direct_Gear_Prototype.FCStd`.

This checkout contains corrected CAD, a reference assembly STEP, candidate BOM, tuning/event data, geometric checks and scripts. It deliberately contains no images, Blender scenes, frame caches, audio, MIDI, video, external samples, impulse responses or renderer binaries. Files named in export reports describe local outputs, not promised repository downloads. Nothing here is a manufacturing release.

## CAD and checks

Use a Python environment with FreeCAD, FreeCADGui, Part and PySide, with Qt offscreen support. The author used the installed FreeCAD application on macOS. Run from the checkout root, in a separate process, without closing or automating the live FreeCAD window:

1. `work/build_direct_gear_axle_fix.py` reads the included Slender Bank and generates the corrected assembly, STEP, calculations and ignored mesh cache `work/direct_gear_mesh_axle_fix.json`.
2. `work/check_direct_gear_math.py` checks nominal linkage geometry and ideal repeat. Its historical output remains in the parent direct-gear folder; the copied revision result is the recorded check of the unchanged linkage dimensions.
3. `work/check_direct_gear_cad_axle_fix.py` checks the recorded frame/support scope.
4. `work/check_rod_axles.py` defaults to the corrected assembly and checks every rod against every individual axle and the common input shaft at 360 poses per voice. CLI arguments can select another model/report. The continuous 1 mm crank/rod axial separation is explained in the recorded report and revision README.

These scripts recompute/replace generated files. They do not certify threads, fits, thrust spacing, locking, string release, load, wear or physical safety. Do not order or machine the full assembly without resolving the engineering gates in the design README and completing a single-channel bench test.

## Audio and MIDI

Use Python with NumPy, and FFmpeg/FFprobe on PATH. The audio scripts also run with Blender's bundled Python/NumPy. Output is under the revision's `Sound/` folder.

1. `work/make_direct_gear_sound.py` derives two centre-crossing plucks per actual crank-rocker cycle, writes twelve-track MIDI variants, event CSV and Scala mapping. It also writes an earlier synthetic audition; that audition is superseded by the sampled harp below.
2. `work/check_direct_gear_sound.py` checks MIDI events, duration, pitch-bend offsets and the synthetic audition's export. It does not measure the sample library's tuning.
3. Download [FreePats Concert Harp 2020-07-02](https://freepats.zenvoid.org/OrchestralStrings/harp.html), SFZ/WAV edition, and extract under `work/harp_samples/ConcertHarp-SFZ-20200702/`. Original recordings: K. Smith / Versilian Community Sample Library; mapping/editing: FreePats. CC0; source credits are retained in `Sound/Concert_Harp_Sample_Credits.txt`. Do not substitute an unrelated library silently.
4. `work/render_sampled_harp.py` follows the library's key/velocity regions and fine-tuning compensation, then applies our just-intonation offsets. It renders a sampled stereo WAV/MP3 from the same event CSV. An older-view movie is assembled only if that local video exists.
5. Download the [Voxengo IM Reverbs pack](https://www.voxengo.com/impulses/) and extract under `work/studio_ir/`. Read its licence. The used response is **French 18th Century Salon**, created with Impulse Modeler, not a measurement of the pictured studio. Royalty-free audio processing is permitted; raw redistribution has additional terms. This repository does not include that IR.
6. `work/convolve_harp_salon.py` writes the eight-minute room-treated WAV/MP3 into `Paris_Close_Studio/`. Wet RMS is 16 dB below dry, with 12 ms predelay, wet-only 180 Hz highpass / 6.5 kHz lowpass, and circular decay tails. Dry event timing is unchanged.

Set the DAW to **120 BPM**, with zero matching video zero. The eight-minute loop is 240 bars of 4/4. In Bitwig, use the Scala MIDI variant with the supplied C-based Scala map on each of twelve instruments. Alternatively use the just-intonation pitch-bend MIDI with instruments honoring each channel and a ±2-semitone bend range. Do not combine both tuning methods.

The current renderer includes the same pose at both ends of 5760 samples. Event times use the matching `5759/5760` clock scale, less than a 0.02% adjustment; there is no extra duplicate note on the closing zero frame. Actual flexible-pick release under load remains unmeasured.

## Final close-focus Paris studio film

Blender 4.5 LTS was used; no other version is claimed tested. Run Blender in background mode, giving `work/render_lovophon_paris_close.py` frame ranges after `--`. It requires the generated mesh and imports `direct_gear_math.py`, `direct_gear_studio_materials.py` and `lovophon_paris_close_studio.py` from `work/`.

The recorded render used two jobs: frames `1 2880` and `2881 5759`. Both share `work/lovophon_paris_close_final_frames/`; never mix caches from different settings or revisions. The first job also generates still previews and a scene snapshot. The snapshot is not a baked animation delivery. Render scripts skip existing frame files, so use a new/empty cache when changing the shot.

The approved shot uses a 50 mm lens, 0.95 m orbit radius, elevation `16 ± 5°`, and f/1.8 focus at the Lovophon core: a very narrow sharp plane with strongly blurred foreground/background. This is a miniature-like selective-focus effect, not a claim of an actual tilted lens plane. The Louis XV-style table and Parisian-inspired studio are procedural scenery; the parquet is dark stained. No people are present. Warm side/rim light, cool low fill, indirect-light capture and reflection tracing refine the render; tiny visual edge bevels do not change CAD.

Run `work/check_paris_close_pose.py` to verify endpoint transforms and instrument bounds over 97 poses. Then `work/encode_paris_close_16min.py` exports a 1600×900, 24 fps H.264/AAC movie. Twelve motion samples per second are duplicated into the delivery frame rate. Two identical eight-minute cycles give **sixteen minutes and two rotations**; the sampled harp plus salon convolution repeats with them. The encoder performs full decode and duration/frame-count checks. The recorded report is included; media is local.

`work/make_lovophon_short_edit.py` produces a thirty-second, 32× version, preserving audio pitch while accelerating its rhythm. It processes audio and picture separately before muxing to avoid the combined-filter stall observed locally. This short edit is not a demonstration of attainable physical mechanism speed.

All audio is an audition, not a recording or acoustic prediction of the unbuilt instrument. A clean render does not validate its mechanics.
