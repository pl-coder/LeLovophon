import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
from pathlib import Path
import json,csv
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs';d=json.loads((O/'Lovophone_Unified_Design.json').read_text());music=json.loads((O/'Lovophone_Unified_Music.json').read_text())
with (O/'Lovophone_Unified_Ratios_and_Chains.csv').open('w') as f:
 fields=['string','note','pitch_and_rotation_ratio','driver_teeth','driven_teeth','chain_links_reference','chain_length_mm_reference','wheel_period_seconds','speaking_length_mm','events_160min'];w=csv.DictWriter(f,fields);w.writeheader()
 for r,v in zip(d['rows'],music['voices']):w.writerow(dict(string=r['index'],note=r['note'],pitch_and_rotation_ratio=r['ratio_exact'],driver_teeth='direct' if r['direct_input'] else r['driver_teeth'],driven_teeth='direct' if r['direct_input'] else r['driven_teeth'],chain_links_reference=r['chain_links_reference'],chain_length_mm_reference=r['chain_path_length_mm'],wheel_period_seconds=r['period_seconds'],speaking_length_mm=r['speaking_length_mm'],events_160min=v['events_160min']))
bom=[(12,'Identical 19-finger picking wheels','One thin sheet part per wheel; flexure material/gauge to test'),(1,'Direct input wheel hub','6 mm shaft; key and axial retention detailing pending'),(11,'Independent wheel cartridges','Two 6 × 10 × 3 mm bearings per wheel'),(22,'MR106 bearings','6 × 10 × 3 mm'),(2,'MR126 input bearings','6 × 12 × 4 mm'),(11,'Input chain sprockets','Exact tooth counts in ratio table; profile reference only'),(11,'Output chain sprockets','Exact tooth counts in ratio table; hub keys pending'),(11,'12-tooth idler sprockets','3 mm shoulder screw/plain bearing; reference profile'),(11,'Miniature chain loops','3.75 mm nominal pitch; actual engagement and link count to confirm'),(11,'Slotted tensioner hangers','6 mm nominal adjustment; captive-nut guides pending'),(2,'Common 6 mm shafts','One rotating input, one fixed wheel-support axle'),(12,'M4 string pull screws','Existing 0.7 mm-pitch tensioners, 2.5 mm hex socket head model'),(12,'M3 bridge locks','Short slots and sliding nuts; anti-rotation cage detail pending')]
with (O/'Lovophone_Unified_Main_Parts.csv').open('w') as f:w=csv.writer(f);w.writerow(['quantity','item','specification_or_status']);w.writerows(bom)
(O/'Lovophone_Unified_Setup.md').write_text('''# Lovophone — unified pitch and rotation

This version supersedes the previous chromatic rhythm. Every wheel now uses exactly the same ratio as its string's pentatonic pitch. All twelve wheels use the same balanced 19-of-32 picking pattern. The C3 wheel mounts directly on the input axle. Eleven single-stage chains drive the other wheels; there are no follower levers, rocking arms or swing-amplifying transmissions.

## Audition in Bitwig

Use Lovophone_Unified_8min_Bitwig.mid for an excerpt, or Lovophone_Unified_160min_Bitwig.mid for the full repeat. Keep the DAW at 120 BPM, with MIDI at bar 1 beat 1. Do not quantize. Each string is a separate MIDI track/channel; channel 10 is avoided.

Use Micro-pitch before the instrument on each string track. Load Lovophone_Unified_Bitwig.scl, Root C, Amount 100%, reference 440 Hz. The already-approved Lovophone_Pentatonic_Bitwig.scl has the same tuning and also works. The MIDI uses ordinary C D E G A keys across octaves, with neutral pitch bends. There is no need to retune the pitches again if that setup is already working.

Alternatively, use the Just_Intonation MIDI copies with a pitch-bend-aware instrument configured for ±2 semitones, without Micro-pitch/Scala. Do not combine the two tuning methods.

There are 12,825 plucks in the full 160-minute file and 643 in the eight-minute excerpt. Nominal note durations are two seconds. All voices have a release at time zero, giving an opening chord. The eight-minute excerpt is not a complete repeat. Previous MIDI and videos use different timing and do not sync with this revision.

## Exact cycle

Pitch and rotation ratios to C3: 1, 9/8, 5/4, 3/2, 5/3, 2, 9/4, 5/2, 3, 10/3, 4, 9/2.

The occupied wheel positions are floor(32k/19), k=0…18: 0, 1, 3, 5, 6, 8, 10, 11, 13, 15, 16, 18, 20, 21, 23, 25, 26, 28, 30. The pattern has no shorter rotational symmetry. Because the rotation-ratio denominators have least common multiple 24, the musical wheel configuration repeats after exactly 24 input revolutions. At 400 seconds per input revolution (0.15 rpm), that is 9,600 seconds or 160 minutes. Mean density is 1.3359375 plucks per second; simultaneous plucks occur.

Each higher voice repeats the same rhythmic figure at its pitch-proportional speed. Ideal MIDI event times are calculated as exact rational numbers before rounding to MIDI ticks. The relative mechanism cycle is mechanical; its wall-clock duration requires the input speed to be maintained.

## CAD and motion

Open Lovophone_Unified_160min.FCStd. To animate it in FreeCAD, run Animate_Lovophone_Unified.FCMacro with that document active. It stays in the current session and provides pause/reset and normal, 10× and 60× preview speeds. Native FreeCAD chain paths are static reference geometry; wheel angles are animated.

Lovophone_Unified_Studio.blend includes the full 160-minute ideal motion, at 24 fps (frame 1 = MIDI time zero). Its chain references move, using a periodic interpolation over one link pitch; this is a visual approximation, not a chain-contact simulation. Rigid model geometry comes from the CAD; moving chain display meshes are regenerated along the reference paths. No image-generation model was used.

The main box is centred beneath the strings. String spacing is now 12 mm to provide room for chain hardware; speaking lengths and pentatonic pitches are retained. The low string is plucked at the input-axle position; the other eleven share the picking-axle position. Overall CAD size is about 393 × 180 × 177 mm. The frame and strings remain exposed. Routine fasteners are modelled around one 2.5 mm Allen key, including the pull screws and bridge locks.

## Prototype limits

This is a concept and packaging model, not production drawings. Sprocket profiles, chain dimensions and link counts are references for 3.75 mm-pitch miniature chain; specific catalogue components have not been selected. Scalloped tooth shapes and smooth chain pitch paths do not establish real roller/tooth engagement. Slot travel and captive-nut guides, shaft keys, axial retention, bearing fits and clamp preloads need final detailing.

Integral flexible picking fingers replace separate pegs. Their gauge, tip shape, fatigue, string deflection and release must be proven on one voice. The event convention is the nominal finger-tip crossing of the string plane on the outgoing side; a real flexible pick may release at a different angle. Chain polygonal action also introduces cyclic speed variation, which the ideal proportional-motion MIDI does not model. See Renold's chain design guidance: https://www.renoldjeffrey.com/media/2395948/design-guide-for-chain-renold-jeffrey.pdf . Tooth counts fix average rotation ratios; they do not guarantee zero instantaneous timing ripple.

The motor is not selected or sized. The CAD provides a common input shaft/coupling; a real drive must supply the measured load at 0.15 rpm for the nominal 160-minute duration. Constant-speed regulation is required for wall-clock audio sync. A safe, durable physical build, acoustics and child operation remain unverified.

## Files

Native model and STEP: Lovophone_Unified_160min.FCStd / .step.
Textured scene and stills: Lovophone_Unified_Studio.blend / .png, Lovophone_Unified_Right.png.
Main parts: Lovophone_Unified_Main_Parts.csv.
Per-voice ratios and reference chains: Lovophone_Unified_Ratios_and_Chains.csv.
Exact event list: Lovophone_Unified_160min_Pluck_Times.csv.
Validation: Lovophone_Unified_Music_Check.json and Lovophone_Unified_Clearance_Check.json.
''')
print('Wrote setup, main parts and exact-ratio chain table.')
