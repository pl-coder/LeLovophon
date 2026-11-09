# Le Lovophon — reality audit, 9 November 2026

**FAIL: the current assembly is not buildable as drawn. Do not fabricate or order the full assembly from it.**

The user identified supports through the strings. Rechecking the saved CAD confirms that and several independent blockers. The earlier checks were too narrow: the moving-to-support sweep excluded strings and the soundbox, and did not check support-to-shaft clashes. The separate rod/axle sweep did not cover arm-to-neighbouring-shaft collisions. The previous reported passes remain true only within their recorded scope; they are not an assembly pass.

## Confirmed findings

| ID | Finding | Count | Evidence / consequence |
|---|---|---:|---|
| F01 | Diagonal supports intersect speaking strings | 7 | Seven solid intersections on the five lowest strings obstruct the modeled vibrating lengths. |
| F02 | Input bearing shelves intersect the common rotating shaft | 4 | The shelf tubes terminate at the shaft axis instead of at a clear outer bearing housing. |
| F03 | Rear pivot stays intersect pivot shafts and bearings | 12 | All twelve pivots are obstructed by their own stationary support tubes. |
| F04 | Moving arms strike neighbouring pivot shafts | 4 | These contacts arise during the swept motion and are absent at common zero. |
| F05 | Anchor string tails run inside the solid end plate | 12 | The routing is not a clear path through the modeled anchor holes. |
| F06 | Retaining washer holes are smaller than the passing pin bodies | 24 | 1.7 mm washer bores overlap 3 mm pins; shoulder/retention design is unfinished. |
| F07 | Outer third bridges miss the soundboard | 2 | Both bridge feet are 4 mm from the board; high D5 has no board underneath, while low C3 also intersects the anchor block. |
| F08 | Zero string break angle at third bridges | 12 | No static downbearing from string tension is defined; a stable speaking-length boundary and reliable soundboard coupling are not established. |
| F09 | Crank flanges have zero separation from fixed front carriers/bearing faces | 12 | Requires a defined bearing/thrust/spacer stack. Zero-volume contact alone does not prove that it will bind or run acceptably. |
| F10 | Shaft torque locking, phase adjustment, fits and fastening not detailed |  | Round bores, overlapping attachment reservations and placeholders are not a complete power-transmitting assembly. |

## Exact support–string intersections

Legacy CAD prefixes are retained from the chromatic model. Their current note mapping is C→C3, Cs→D3, D→E3, Eb→G3, E→A3.

| String object | Support | Overlap, mm³ |
|---|---|---:|
| C_KotoSpeakingString | V01_RearPivotStay | 0.843276 |
| D_KotoSpeakingString | V08_RearPivotStay | 1.268462 |
| E_KotoSpeakingString | V11_RearPivotStay | 1.333475 |
| E_KotoSpeakingString | V12_RearPivotStay | 1.482089 |
| Cs_KotoSpeakingString | V05_RearPivotStay | 1.151151 |
| Cs_KotoSpeakingString | V06_RearPivotStay | 0.534423 |
| Eb_KotoSpeakingString | V10_RearPivotStay | 1.055441 |

## Motion collisions

| Moving part | Stationary part | First sampled crank offset | Poses with interference / 360 | Maximum overlap, mm³ |
|---|---|---:|---:|---:|
| V01_TubeArm | V02_3mmShaft_0 | 235° | 63 | 3.900420 |
| V02_TubeArm | V03_3mmShaft_0 | 253° | 27 | 0.125708 |
| V03_TubeArm | V04_3mmShaft_0 | 223° | 84 | 5.987977 |
| V05_TubeArm | V06_3mmShaft_0 | 242° | 49 | 1.513342 |

## Additional dimensional evidence

The part named `Baseplate_310x170x6` actually has a 370 ×140 ×3 mm bounding envelope in this revision. Its legacy name is not a manufacturing specification. The board width was not increased when string spacing was increased.

Both outer bridge bodies have 4 mm minimum distance to the board. The low C3 bridge additionally intersects the anchor block by 34.8 mm³; the high D5 bridge has no modeled body support under its foot. All twelve strings have straight speaking/back sections at native Y=-91 mm, and crowns/end saddles have tops at Y=-91.4 mm. The crowns are plain cylinders, without a capture feature. Nominal break angle is zero. This provides no tension-generated static downward preload; real vibration/contact/acoustic behavior was not measured.

The new 1 mm crank-to-coupler axial gap is still present. It solves that local collision only. The crank flange begins exactly at the front carrier/bearing end face, giving zero axial clearance there. A specified thrust/spacer stack is required; this report does not assert that every zero-distance face contact is a rigid-motion blockage.

## Scope and limits

The static audit examined every pair of 509 saved-pose solid parts (129,286 pairs) with native OpenCascade intersection tests after bounding-box filtering. It recorded 304 positive-volume overlaps. Many are intended connection/press-fit/joinery reservations and are not counted automatically as faults. Confirmed failures above involve strings, rotating members, unsupported bridges or explicitly incompatible dimensions.

The motion audit samples 360 crank offsets per voice for each hub, tube arm, tip socket, pick and POM rod against all stationary solids plus the common/pivot shafts and bearing envelopes. Integral crank-shaft flanges remain excluded with the crank group. Own pick–string intersections are recorded separately as intended contact geometry; they do not prove clean release. Other non-circular moving groups are omitted rather than frozen. This is not a full gear-mesh or moving-fastener contact simulation. Sampling is not a continuous collision certificate.

Still unresolved: actual supplier gear tooth geometry/backlash, torque/phase locks, pin shoulders and retention, bearing fits/thrust loads, frame joinery, flexible-pick release under tension, nylon gauges/tensions, acoustic performance, stiffness, wear, transport structure and simultaneous twelve-voice starting load. No physical build or powered/classroom approval is recorded.

The movie directly sets part poses from equations and does not enforce collision constraints or prove torque transmission. The sampled-harp soundtrack is an audition, not evidence of the instrument’s sound.

## Required next revision

1. Define the complete string route, positive anchors, real tensioners, elevated bridge crowns and supported feet; use actual 3D speaking lengths for the pitch ratios.
2. Move bearing load paths away from strings and rotating shafts. Attach supports to outer housings/plates, with explicit bores, joints and clearances.
3. Shorten/relocate neighbouring shaft ends or move arm planes so every arm clears all shafts over its full swing.
4. Detail the torque-transmitting joints, adjustable phase locks, shouldered pins, retainers and bearing thrust stacks.
5. Recheck the assembled solids and contact constraints, then build and measure one voice before replicating twelve channels or making another presentation film.

Do not treat the renders, the candidate BOM or reference STEP as a build pack.
