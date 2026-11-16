# Le Lovophon — plucking layout R5

This revision puts all twelve picks clear of the string ends while preserving the complete exact-ratio musical drive. **The actual operating hand-crank force remains unmeasured.**

Rendered media are retained locally and intentionally excluded from Git.
## What changed

- The six bass voices pluck one quarter of their own speaking length from the third bridge. The six higher voices progress toward the middle: all positions are25–47% of speaking length from the nearer end. Treble positions approach the middle to leave clearance for the standard gears, bearings and carriers. This is a practical tone/compliance compromise, not a universal or acoustically tested optimum.
- Complete gear/link/arm stations slide along X; no extra offset arms, universal joints or new gear stages are added. A single station gap was widened2mm to fit its standard input-bearing support. Minimum nominal separation between neighbouring moving envelopes is 3.0mm, independent of phase.
- C4 moves from6.18mm to75mm from its third bridge. Exact pentatonic pitches, inverse-ratio speaking lengths, proportional arm lengths, gear tooth counts, phases and nominal3rpm input are retained. Ideal repeat remains480seconds /24 input turns.
- Rear support ribs are relocated toX−210,−28,150,272mm. The four identical8mm flat-cut ribs, stock flange clamps, angle feet and32mm hand crank remain. Rear shaft is590mm of solidØ8mm steel; input shaft is575mm ofØ5mm steel, with only the required phased cross-pin bores.

The body remains700×220×60mm. Saved-pose overall envelope is 768.5×281.7×293.0mm. Nominal CAD material mass is 4.69kg, before case, glue, finish and material variation.

Plucking-position diagram (local media omitted) · [Exact position table](Plucking_Positions.csv) · [Assembly changes](Assembly_Guide.md)

## Hand-crank force

The conditional plucking-force sensitivity at the all-12 shared centre crossing falls by about 60%. If every string is deflected sideways by0.2mm together, the calculated pluck-only hand force is 4.03N, versus10.03N inR4. **This is a scenario, not the measured operating force or full-cycle peak.** Pick flex/release and drivetrain losses are absent from that number. Ideal gravity/inertia alone gives0.363N absolute peak at constant3rpm; this also does not establish real effort.

[Detailed force budget and physical test procedure](Drive_Effort/README.md) supplies independent Exudyn checks, conditional full-cycle force envelopes and a blank test record. A calibrated measurement through pick release in both directions, plus a complete instrument torque/hand-force trace through the480-second cycle and startup, is required to settle the actual number. No physical load test, motor sizing or manufacturing release is claimed.

## Checks and their limits

All1101 saved solids are valid and each contains one connected solid. All605550 stationary pairs have been considered; recorded unexpected intersections are zero. Whole local mechanisms were copied unchanged from the finalR3 geometry and translated along X; reverse-translation numerical geometry fingerprints check the copy. Prior local moving-pair evidence is retained under `Checks/Inherited_R3`. New fixed-world clearance uses conservative continuous motion envelopes; overlapping bounds are checked at one-degree local crank intervals. Neighbour moving axial slabs have positive separation. Intentional PET/string contact is listed separately and needs elastic release testing. Tensioner clearance is inherited for the unchanged system, with23 travel poses checked against new/changed geometry.

These nominal checks do not establish tolerance margins, bearing alignment, friction, pick reliability, acoustic quality, impact/jam resistance, stiffness under service loads or safe real-world performance. The preliminary stiffness estimate assumes ideal joints; it is not a load test or FEA validation. [Verification summary](Verification_Summary.json) records the final hash and limitations.

## Files

`LeLovophon_Pluck_Layout_R5.FCStd` is the new model. R4 is preserved separately. `Cutting_Preview/` provides quotation-preview plate STEP/DXF files and updated mounting coordinates; the plate shapes are inheritedR4 parts, so their original part identifiers remain. These are not released fabrication drawings. Complete woodshop sheets remain a later design requirement.

CAD SHA256 `8b5322026e943034589d3b90ea17b8ebd58bd06830b3c0050511e0693e0f7148`. No live FreeCAD session was restarted or modified, no supplier was contacted, and CAD and documentation are updated separately from local media.


Drivetrain follow-up: [Gear/armature loads and friction assessment](Drivetrain_Assessment/README.md) records the59 rolling bearings,24 dry link bushes, per-voice tooth/pin/link loads, ideal shaft twist and an incremental drivetrain test. This adds no physical validation or CAD change.


Child-powered drivetrain requirement: A school-age child should be able to start and continuously hand-crank the complete instrument comfortably at its nominal operating speed. Size the drivetrain for combined plucking load, starting/running gear and bearing friction, linkage resistance and alignment sensitivity. No numerical acceptance force has been agreed and no assembled torque/effort measurement has yet established this goal.
