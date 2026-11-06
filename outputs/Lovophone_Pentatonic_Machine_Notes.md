# Le Lovophone — pentatonic machine revision

The twelve approved notes are C3 D3 E3 G3 A3 C4 D4 E4 G4 A4 C5 D5 (MIDI 48 50 52 55 57 60 62 64 67 69 72 74). C3 = 130.8127826502993 Hz. Octave names may differ in a DAW.

## Geometry

All twelve strings remain unwound nylon with common load-bearing ends at X = -22 and 320 mm, a 342 mm end span. Each third bridge sits at X = 320 minus its speaking length. The longest speaking section is 330 mm; the shortest is 73.333 mm. Nominal string height remains 18 mm above the soundboard.

Speaking lengths are 330 mm divided by the exact pitch ratio to C3. Arm radii are 67.1969384567 mm divided by the same ratio; their pivots are lowered to retain the same string contact plane. The transmission belts and removable arm-bearing forks are regenerated for those pivots. The three shortest rigid arm bodies have an extra 0.5 mm radial setback, with the flexible pick extended inward to retain its attachment and original outer reach. This prevents the rigid corners grazing the strings during the swing.

The complete mechanism is shifted 16 mm along X toward the tuning end so every pick lies on its speaking section. String end supports and the soundbox retain their positions and dimensions. The motor bracket is revised with its two fixing holes on the existing soundbox lid; new gantry mounting holes are included. Small relief pockets in the common anchor block and low drive-tray lip clear the C3 and D3 bridge feet. Nominal overall envelope remains approximately 394 × 202 × 197 mm.

## Rhythm

The original twelve cam timing ratios, follower geometry, cam phase relationships and 4:1 swing amplification are retained. Pitch ratios and drive timing ratios are explicitly separate properties. This reproduces the approved pentatonic MIDI schedule, including the 160-minute full mechanical repeat at nominal 3 rpm. No new MIDI is needed for this revision.

## Files

- Lovophone_Pentatonic.FCStd: visible native model with named pitches and target frequencies.
- Lovophone_Pentatonic.step: assembled neutral geometry.
- Lovophone_Pentatonic_Bridge_Settings.csv: exact bridge positions, speaking lengths, arm radii and drive settings.
- Lovophone_Pentatonic_Geometry.json: full geometric and tuning metadata.
- Lovophone_Pentatonic_Clearance_Check.json: sampled geometric checks.

## Physical prototype limits

The model represents nominal 0.8 mm nylon. At an assumed density of 1150 kg/m³, an ideal flexible-string calculation gives roughly 4.31 N per string at these lengths and pitches. That is a starting estimate, not a validated string specification. Gauge, actual tension, creep, bridge downforce/break angles, friction, plucking reliability and soundboard response need physical setup and testing. The fork sections, bearings, fasteners and gantry still need load/stiffness validation. N20 motor torque, low-speed stability, supplier mounting dimensions and electrical implementation remain provisional. Geometry and animation are not a build-ready or certified design.

The original chromatic machine and its MIDI files have been preserved.
