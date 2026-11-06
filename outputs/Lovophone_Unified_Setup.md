# Lovophone — unified pitch and rotation

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

The main box is centred beneath the strings. String spacing is now 12 mm to provide room for chain hardware; speaking lengths and pentatonic pitches are retained. Large sprocket webs have three open spokes rather than solid discs. The low string is plucked at the input-axle position; the other eleven share the picking-axle position. Overall CAD size is about 393 × 180 × 177 mm. The frame and strings remain exposed. Routine fasteners are modelled around one 2.5 mm Allen key, including the pull screws and bridge locks.

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
Validation: Lovophone_Unified_Music_Check.json, Lovophone_Unified_Clearance_Check.json, Lovophone_Unified_Rotor_Separation_Check.json and Lovophone_Unified_Animation_Check.json.

Lovophone_Unified_20sec.mp4 is a silent, normal-speed preview. Align its 0:00 with the new MIDI start at 120 BPM.
