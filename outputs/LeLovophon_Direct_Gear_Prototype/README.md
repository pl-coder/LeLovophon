# Le Lovophon — direct-gear engineering prototype

**NOT A PROVEN WORKING MACHINE. NOT RELEASED FOR MANUFACTURE.**

This proposal replaces the undriven Slender Bank with an explicit twelve-channel transmission. It is a route to a physical prototype, not another claim that rendered motion proves a machine works. No orders, supplier messages or purchases have been made.

Use the current [axle-clearance revision](Axle_Clearance_Revision/README.md). The original direct-gear CAD is superseded and is not included here. The original sweep missed the individual crank axles; the revised check covers every axle.

## Power path

Hand input -> one continuous5 mm shaft -> one external spur-gear pair per voice -> rotating crank -> pinned POM connecting rod -> rocker shaft -> visible tube pendulum -> flexible pick -> nylon string.

There are12 gear pairs,12 cranks,12 connecting rods and12 rocker levers. The shared input removes intermediate ratio shafts and timing belts. Each voice still requires a crank shaft and its pendulum pivot. Positive pinned links drive both directions; there are no spring-loaded cam followers or friction speed ratios. A motor is deferred until torque is measured. The hand input makes the first test independent of an unverified motor selection.

All spur pairs use module0.5 and20 degree pressure angle. The actual calculated involute flank geometry is present in CAD; simplified root transitions are not approved manufacturing geometry. Obtain the gear maker's root fillet, quality, material and locking drawings. Do not machine the assembly STEP as a bag of finished parts.

## Visibility and size

Long proportional pendula are retained:109 mm down to24.222 mm pivot-to-string. The connecting rods, bearing carriers and gears sit behind/above the visible arms. No front crossbar or front vertical stand is added. Shaft supports are routed behind the moving linkages.

Pivot stations are24 mm apart, rather than the undriven study's13.5 mm. This accommodates an actual axial stack. String lanes are14 mm apart, rather than10 mm; both load-bearing end plates and guide rails have been widened to match. Speaking lengths remain330/ratio mm. The string fittings are inherited geometry candidates, not independently validated tensioner designs.

The static CAD envelope is approximately394 x221 x253 mm (length xwidth xheight); this is substantially taller than the briefcase-depth goal. It is not a100 mm-deep packing solution. The moving envelope and transport disassembly remain to be specified.

## Timing and movement

Ratios:1,9/8,5/4,3/2,5/3,2,9/4,5/2,3,10/3,4,9/2.

Notes:C3,D3,E3,G3,A3,C4,D4,E4,G4,A4,C5,D5.

Each output makes one crank revolution per complete arm oscillation, nominally two centre passes. The repeat is exactly24 input revolutions. At a regulated3 rpm this is480 seconds. A hand crank does not hold an exact eight-minute wall-clock duration. Gear tooth counts set average cycle rates, not instantaneous sinusoidal motion. This linkage has its own non-sinusoidal motion; the previous Slender Bank animation is not its motion or MIDI timing.

Crank radius10 mm, rocker radius14 mm. Each coupling rod has the same centre length as its own fixed crank-to-rocker distance. This gives roughly91 degrees total swing. The common musical zero is established by the per-voice crank and arm phase settings listed in the calculation file; working shaft locks must preserve those phases.

## What was actually checked

-12 exact rational tooth-count ratios and480-second mathematical phase return.
-10,001 crank positions per voice: linkage closure and transmission angle.
-Projected pick polygon against neighbouring string centres, using0.8 mm model strings.
-Rod/crank clearance from the common drive shaft.
-A separate72-pose native-solid sweep checks moving rigid components against carrier plates, rear supports and the input shaft. See Drive_CAD_Check.json for the result and exclusions.
-All native solid validity.

These checks do not prove force, wear, assembly access, strength, gear meshing quality, flexible pick behaviour or sound. Small calculated clearances require physical testing, including out-of-plane pick bending.

## Release blockers — do not order the full machine yet

1. Design and model the torque-transmitting shaft locks, phase adjustment, axial shaft retainers and spacers. Current round bores do not transmit torque by themselves. The power-path geometry is present; these joints are not finished.
2. Specify real crank/rocker journal shoulders, fasteners and positive retention. The current cylindrical pins and retaining-washer reservations are not a complete fastening specification.
3. Finish carrier bearing fits, retainer fixing threads and all tube-to-frame joints. Supports that touch in CAD are not automatically joined in reality.
4. Confirm actual standard bearings and obtain gear supplier drawings. Review tooth-root strength and bore/hub dimensions under measured load. A compatible module/pressure angle alone is not a complete procurement specification.
5. Build a single-voice bench mechanism with the longest arm, and test the shortest-arm/highest-ratio configuration. Prove free rotation before fitting nylon. Set minimal pick intrusion and prove clean release in both directions without touching neighbours.
6. Record peak input torque under string tension, shaft/frame deflection and1000 plucks in each configuration. Inspect picks, journals and gears. Then validate all-twelve simultaneous peak load and choose a motor with measured margin.
7. Provide local rear gear/pinch guarding for any powered or classroom version while leaving the front pendula visible. Add a stop control and measured torque limiting. No powered classroom safety approval is claimed.

The immediate build decision is to finish and test one channel, not purchase twelve unproven channels. An engineer/machinist must resolve the listed release blockers before that channel is fabricated. No claim is made that this folder is a ready-to-order kit.

## Current files and reproduction

Current CAD, reference STEP, revised candidate BOM and checks are in `Axle_Clearance_Revision/`. The integral crank shaft/flange now terminates 1 mm behind the rod plane; 360 sampled poses per voice show no rod–axle intersections. That axial crank/rod separation also follows continuously from their disjoint X extents. This does not resolve the other release gates above.

See [reproduction notes](../../docs/DIRECT_GEAR_REPRODUCTION.md). Sound timing is regenerated from exact linkage crossings, not the earlier picking-wheel MIDI. The current mechanical repeat is eight minutes at a regulated 3 rpm. The local studio film repeats this cycle twice for sixteen minutes; its thirty-second version is 32x faster. Media and third-party sound downloads are deliberately excluded.
