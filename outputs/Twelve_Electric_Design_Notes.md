# Twelve-voice electric harp with a shared gantry

The scale is completed to twelve pitches within one octave: C, C♯, D, E♭, E, F, F♯, G, A♭, A, B♭ and B. This is one conventional five-limit chromatic just-intonation choice; chromatic just intonation is not unique. The six established C–D–E–F–G–A ratios are retained. There is no duplicate octave C.

| Pitch | Pitch / drive-speed ratio to C | Speaking length (mm) | Reference pulley teeth, driver : driven |
|---|---:|---:|---:|
| C | 1 | 330.000 | 40 : 40 |
| C♯ | 16/15 | 309.375 | 32 : 30 |
| D | 9/8 | 293.333 | 36 : 32 |
| E♭ | 6/5 | 275.000 | 36 : 30 |
| E | 5/4 | 264.000 | 40 : 32 |
| F | 4/3 | 247.500 | 32 : 24 |
| F♯ | 45/32 | 234.667 | 45 : 32 |
| G | 3/2 | 220.000 | 36 : 24 |
| A♭ | 8/5 | 206.250 | 40 : 25 |
| A | 5/3 | 198.000 | 40 : 24 |
| B♭ | 9/5 | 183.333 | 36 : 20 |
| B | 15/8 | 176.000 | 45 : 24 |

All twelve strings retain the 342 mm common end span, nominal 0.8 mm unwound nylon model diameter, 18 mm string height and individual third bridges. Full string lengths including the over-edge tails are longer than the common end span. The rounded end guides, tied anchors and screw-pull tensioners are repeated at 10 mm lane spacing. The actual nylon grade, gauge, pitch register, tension, bridge preload and settling behaviour require prototype selection.

The bank keeps 24 mm module spacing. Pick centres run from X=23 to 287 mm, centred at X=155 mm on the existing soundbox. The twelve lane centres run from Z=−80 to +30 mm. Each new voice has its own ratio pulley, eccentric cam, follower, 4:1 step-up belt and pendulum arm. Arm radii and speaking lengths follow the inverse pitch ratios. The longer reach of the forward cam followers changes the swing amplitudes; they range from approximately ±7.8° to ±18°. Each pick still crosses its own string. The clockwork, winding key, mainspring and escapement are removed from this revision.

Two shared hollow aluminium rails replace the individual tall plate frames. Braced end frames stand behind the string bank. Each shaft retains its original paired bearing arrangement in a removable hanging fork with a split clamp. Rails/posts are provisionally 10 mm outside diameter with 1 mm wall; braces are 7 mm outside diameter with 1 mm wall. These sections and clamp sizes are geometric starting points, not structurally qualified sizes. Matching new gantry holes are cut through the soundboard. Previous module mounting holes remain unused; the lid can be remade or plugged after the arrangement is final.

The drive uses a small N20-size low-speed brushed DC gearmotor directly coupled to the long input axle. The motor module includes a stepped 6 mm / 3 mm coupling, a transparent coupling sleeve, an alignment bracket, a clear motor cover, and space for a PWM controller, tempo knob, run/stop switch and low-voltage supply connector. The body envelope is approximately 10 × 12 × 29 mm, plus the output shaft. The dimensional/performance reference is the Pololu #1596: nominal 6 V and 13 rpm no-load. This reference is not a selected purchase or a promise that a cheaper generic motor has the same torque or dimensions.

A commodity N20 motor and compatible PWM module are the low-cost component class intended for this design. The motor needs a running/start-torque test on the complete twelve-voice mechanism before choosing its gearbox and current rating. PWM control varies the motor command; it does not guarantee a constant musical tempo under changing load. Closed-loop speed feedback is not implemented. A nominal 3 rpm common-axle animation is a visualization setting, not a verified operating point. Do not use stall torque as the continuous operating rating.

Use an external regulated low-voltage supply matched to the chosen motor and controller. The controller must accept that supply voltage and include appropriate current limiting, run/stop and wiring retention. The PCB and connector shapes are space reservations. No circuit, mains wiring, battery or certified protective system has been designed. The motor face-hole pattern and coupler clamping details must be matched to purchased hardware before manufacture.

Structural deflection, vibration, bearing retention, clamp preload/slip, tube crushing, body/end-block string loads, compliant pick release, acoustics and fatigue remain unverified. The moving geometry is checked separately in `twelve_clearance_check.json`; sampled clearance is not proof of dynamic or structural operation.

References:
- Pololu #1596 specification and dimensional reference: https://www.pololu.com/product/1596/specs
- Pololu micro metal gearmotor family drawings and performance data: https://www.pololu.com/file/0J1487/pololu-micro-metal-gearmotors-rev-6-2.pdf

The native file is finished using an isolated offscreen FreeCAD writer so that colours, transparent panels, visible parts and camera settings are saved without controlling the unstable interactive app.

The saved assembled envelope is approximately **394 × 202 × 197 mm** (length × depth × height). The overhead rails and clamp screws increase the height relative to the earlier plate frame. The new gantry structural aluminium volume corresponds to approximately 0.44 kg at an assumed density of 2700 kg/m³, excluding clamp screws, bearings and mounting hardware. This is not the total instrument mass. Seventy-two positions per voice showed no unintended moving-to-fixed contact; separate straight-down checks verified all twelve pick/string contacts. All modelled part shapes passed native validity checks.
