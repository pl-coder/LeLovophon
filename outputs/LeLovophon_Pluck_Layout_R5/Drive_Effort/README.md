# R5 hand-crank force — calculated transfer, physical release/drag still unknown

**The actual required peak hand force is not yet known.** This report does not call an assumed pick deflection, force cap or friction torque a measurement. The previous 32 mm throw is retained.

## Geometry improvement

Twelve equal-gauge nominal 1.05 mm PVDF strings remain at nominal 37.98 N each. Speaking lengths and third bridges, tuning, proportional arm lengths, gear ratios, phase settings and 480-second ideal repeat are unchanged. Whole stations have moved along X. The six bass stations pluck one quarter of their own speaking length from the third bridge. The other six progress toward the middle. All positions are 25–47% of speaking length from the nearer end, avoiding near-end stiffness. This is a practical tone/compliance choice; sound is not physically evaluated.

C4 changes from 6.18 to75 mm from the third bridge. Its small-deflection lateral stiffness falls from 6.273 to 0.675 N/mm. Its inverse-ratio speaking length remains300 mm.

## What the current numbers mean

For sideways deflection d and nominal fixed tension T, `F = T d (1/a + 1/b)`. Exact gear/four-bar leverage reflects each tip force to the common input shaft. At the all-12 shared centre crossing, equal sideways string deflection gives:

| Assumed displacement of each string | R4 pluck-only hand force | R5 pluck-only hand force |
|---|---:|---:|
| 0.1 mm | 5.01 N | 2.02 N |
| 0.2 mm | 10.03 N | 4.03 N |
| 0.5 mm | 25.07 N | 10.08 N |

This is a 59.8% reduction in that sensitivity. These rows are **conditional centre-crossing scenarios, not a predicted operating-force range or the full-cycle peak**. They omit PET bending/release, contact dynamics, friction and tolerance/alignment effects. Arm travel and nominal pick overlap are not the same as string displacement.

The ideal mechanism with no string forces or friction has 0.363 N absolute peak hand force at constant3 rpm. Moving CAD mass is 0.434 kg across37 rigid groups. Exudyn1.13.6 independently reproduces the full480-second ideal dynamics within 1.23e-07 N·m. Its independent static0.2 mm shared-crossing load case agrees within 1.41e-11 N·m. Neither agreement establishes omitted real-world loads.

## A force budget we can actually test

For a measured maximum tangential resistance at each pick and a maximum total reflected drivetrain loss torque **under those working loads**, the conservative constant-speed model envelope is:

`F_hand ≲ Σ(J_i,max × F_pick_i,max) /0.032 + τ_loss,max/0.032 +0.363 N`

J is tip travel in metres per input radian. Each voice's maximum leverage is independently refined over a complete local crank revolution and rounded upward. Summing those separate maxima deliberately overestimates simultaneous load: it even allows pick force where the arm is not touching the string. The phase-preserving full-cycle sample gives a smaller bound. This is a numerical rigid-body envelope, not a formally certified bound or a claim about startup, jams or impact.

If every pick has the same measured force cap f, this becomes approximately:

`F_hand ≲ 30.71 × f +31.25 × τ_loss,max +0.363 N`

Here f is in newtons and τ is in N·m. For example, **if** each tip stays below0.10 N and total reflected drag stays below0.020 N·m, the conditional envelope is 4.06 N. These are proposed test conditions, not measured or assumed-to-be-achievable properties of this machine. With0.15 N per tip and the same drag, it is 5.59 N. Every extra0.01 N·m of drag costs0.3125 N at the current handle. A64 mm crank would halve hand force but would not reduce shaft/link/gear loads.

The PET tongue thickness is0.3 mm and its unsupported length approximately4.85 mm. Unknown sheet stiffness, clamping, tip finish, overlap, friction, creep and direction of travel control release. Nominal dimensions alone do not identify its force curve. Drivetrain drag also depends on alignment, bearing preload, lubrication and load; a dry unloaded reading alone does not prove loaded drag.

## Minimum physical test needed to settle the number

1. Use the specified line, tension and actual replaceable PET tongue/holder. A one-string fixture needs adjustable end anchors at the distances in `Pick_Test_Record.csv`; the unused string behind its third bridge must also be tensioned as in the instrument. Anchor test loads securely and keep eyes clear of tensioned line.
2. Record a **force-versus-travel trace through contact and complete release in both directions**, using a calibrated low-force load cell or gauge with suitable range and resolution;0.01 N or finer is useful near the0.1 N test condition. Move the real arm/tip along its actual arc and at its operating crossing speed, about24 mm/s at the shared centre crossing. A slow static pull alone will not capture impacts or stick-slip. Include repeat trials and intended pick adjustment extremes. Fill the blank CSV measurements; do not infer force from apparent string travel.
3. Use those measured curves with the preserved twelve phases in the dynamics model to estimate the combined torque waveform, and measure the assembled drivetrain's loaded losses, starting drag and alignment sensitivity. Simple dry spin-down is supplementary, not sufficient.
4. **The decisive check is the complete instrument.** Measure tangential force at the32 mm crank radius (or input torque with a calibrated torque sensor), capture starts, both plucking directions and every coincidence through at least one full480-second cycle at3 rpm. Keep the tangential lever arm known; a handheld gauge at an arbitrary pull angle will under-read. Repeat the highest-load events and intended adjustment extremes. Report peak force, sustained force and measurement uncertainty. Convert force to torque with τ=0.032F. Five newtons corresponds to0.160 N·m; ten newtons to0.320 N·m. Those are conversions, not performance claims.

The whole-machine trace checks both plucking and mechanical loss together. No physical test has been performed in this assessment. A peak-force target should be agreed before selecting a reduction stage or a final hand-crank throw.

## Free software and reproducibility

[Exudyn](https://github.com/jgerstmayr/EXUDYN) / [documentation](https://exudyn.readthedocs.io/en/latest/) was used here. [Project Chrono](https://github.com/projectchrono/chrono) and [MBDyn](https://www.mbdyn.org/) are other free multibody tools; no paid licence is needed. Their usefulness still depends on measured contact and loss inputs. [SKF](https://evolution.skf.com/en/using-a-friction-model-as-an-engineering-tool-3/) explains why friction depends on conditions. [UNSW string acoustics](https://phys.unsw.edu.au/jw/strings.html) and this [ASA research summary](https://acoustics.org/pressroom/httpdocs/167th/1pMU5_Ramsey.html) explain the connection between plucking position and harmonics; no universal best tone is claimed.

CAD SHA256 `8b5322026e943034589d3b90ea17b8ebd58bd06830b3c0050511e0693e0f7148`. All numerical inputs, per-voice transfer, independent solver checks and standalone reproduction files accompany this note. This remains an unbuilt design, with operating force unresolved and no manufacturing release.
