import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
from pathlib import Path
import json,csv,zipfile,math
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs';a=json.loads((O/'Lovophone_Lab_Frame_Ratio_Audit.json').read_text())
rows=a['voices']
notes='''# Lovophone Lab Frame — ratio and manufacturing review

Review date: 5 November 2026. Original Lab Frame and the separate Unified project are preserved. The new native file is `Lovophone_Lab_Frame_Ratio_Review.FCStd`. It is an engineering review, **not a machining release**. Do not send the assembly STEP from the older Lab Frame to a shop as finished production drawings.

## Musical definition

Paul chose the lively motion and 8-minute repeat. Input shaft: 3 rpm (20 seconds/revolution). The twelve pitch and average cam-rotation ratios are exactly identical:

| Voice | Pitch = cam rotation | Speaking length mm | Reference pulley teeth, driver/driven |
|---|---:|---:|---:|
'''
for r in rows:notes+=f"| {r['note']} | {r['pitch_and_rotation_ratio']} | {r['speaking_length_mm']:.3f} | {r['driver_teeth']}/{r['driven_teeth']} |\n"
notes+='''
Denominator LCM = 24; 24 input revolutions × 20 seconds = 480 seconds. This is the common ideal cam phase repeat. The 64:16 follower-to-arm transmission is a separate 4× swing-angle gain, not another musical ratio. Its geometry stays unchanged. Arm radii and string speaking lengths both remain inversely proportional to pitch ratio.

These are forced cam-driven arms. They are not freely oscillating pendulums: free-pendulum frequency would vary as inverse square root of length, not the inverse length used for ideal strings.

All string targets assume the same linear density and tension, C3 = 130.8127826502993 Hz, longest speaking length 330 mm. Real nylon needs tuning under tension; gauge, creep, bridge compliance and inharmonicity are not corrected by CAD. The back-length string portions should be damped if their sympathetic tones are unwanted.

**Old Lab Frame MIDI and videos no longer sync with this corrected drive.** The saved Lab Frame Blender scene also retains old timing. Unified MIDI is not a substitute: that version has a different release mechanism and event pattern. New Lab Frame MIDI must be generated from this cam/follower's release phases after the mechanical arrangement is settled. Do not equate one arm swing with one pluck without testing the pick's return path.

## What the revised model actually contains

All twelve LinkageGeometry ratios and tooth-count labels agree with pitch. Pulley pitch-circle reference discs and belt envelopes were resized to those counts, and Output.SpeedRatio updated. InputPeriodSeconds = 20; FullRepeatSeconds = 480. Valid native solids were checked. Existing frame, bridges, strings, eccentric cams, followers and arms are retained.

The discs are **pitch envelopes**, not real pulley outer diameters or tooth profiles. The belts are geometric references, not selected catalogue belts. No production tooth engagement, flange width, hub retention or belt strength is implied. The animation macro reads the corrected rows and uses 3 rpm; it does not validate an orderable drive.

## Build blockers found

1. The C5 and D5 timing stages intersect the existing tray; D5 also intersects the right angle feet and mounting bolt/washer. Eleven changed-envelope intersection pairs are recorded in the JSON. These cannot be dismissed as intended joints.
2. The 16-tooth, 2 mm pitch output envelope has pitch radius 5.093 mm around a 5.05 mm radius bore: only 0.043 mm radial material even before real teeth are cut. This is not a usable pulley hub. A bearing must sit in an outboard hub, or the stage must use larger pulleys or a compound ratio arrangement.
3. The D5 reference small-pulley wrap is about 102 degrees / 4.5 teeth. Actual profile manufacturer's engagement limits and tensioning design are required; no arbitrary acceptance threshold has been asserted.
4. Standard belt tooth counts and centre distances must be selected together. The current centre distance is 28.302 mm; smooth pitch-path lengths in the CSV are references, not buyable belt lengths. Fit slotted bearing mounts or an appropriate tensioner after selecting catalogue belts.
5. Existing split clamps have no finished splits, clamping bolts/preload or captive-nut details. Frame tube crossings need real joints and the crossed base stays need physical separation. Existing old clearance reports do not certify these interfaces.
6. The N20 motor is an envelope, not a validated selection. Required input is 3 rpm **under load**. Starting torque, string pluck force, spring returns, belt preload and current must be measured. A plain PWM dial will not guarantee exact eight-minute wall-clock timing; closed-loop speed regulation may be needed without changing the mechanical ratios.

The ratio arithmetic is complete; production drive packaging is not. Preserve the visible lab frame and use catalogue pulleys with proper outboard hubs or a compact compound stage rather than machining the reference discs.

## Buy versus make

Prefer bought bearings, precision shaft, shaft collars, matched timing pulleys/belts, metric screws/nuts/washers, springs and electric drive. Use cut stock for tubes and ties. Custom work should be concentrated into repeated flat cheeks/levers, a few properly detailed split clamps/hubs, replaceable picks/bridges and the timber soundbox. Do not turn each rendered object into a unique CNC order.

`Lovophone_Lab_Frame_Procurement_Inventory.csv` accounts for all 636 native solid objects, including hidden motor reservations. Classification is a first-pass routing aid, not 636 confirmed SKUs or 636 separate purchases. Nested groups, multi-piece hardware and obsolete reference details need family consolidation before quoting. Bounding boxes are not cutting dimensions or tolerances.

| Component family | Proposed source/process | Status |
|---|---|---|
| 6 × 12 × 4 mm bearings | [123Roulement MR126-ZZ](https://www.123roulement.com/roulement-palier/roulement-bille/simple-rangee/mr126-zz) | Exact dimensional product verified; confirm every seat separately, especially independent pulley bearings. Supplier drawing and suffix matter. |
| 6 mm smooth shaft stock | [Motedis W6H6](https://www.motedis.com/fr/Arbre-de-precision-6-mm-h6-acier-trempe-et-traite) | Exact stock diameter and h6 tolerance verified. Choose lengths from live configuration. Hardened shaft is not a substitute for easy-to-thread rod ends; use clamping retention or quote end machining. |
| Timing pulleys and belts | [MISUMI catalogue](https://fr.misumi-ec.com/pdf/fa/p1945.pdf) / [HPC technical range](https://www.ctmeca.com/docFichesTechniques/Courroies.pdf) | Product families only; exact tooth counts, profile, widths and hubs NOT selected. A 2 mm pitch alone does not establish compatibility. |
| Tube rails, posts, ties | Standard aluminium tube and steel rod, cut to length | Current 8×1, 6×1, 4×1 mm tube and 2.5 mm ties provisional; exact merchant/grade and real joint lengths not selected. |
| Flat metal cheeks, tabs and levers | [John Steel laser cutting](https://www.john-steel.com/fr/biz) / [current process guidance](https://www.john-steel.com/biz/themes/johnsteel_grandcompte/assets/pdf/guide-pliage-decoupe.pdf) | Good route for 2D cut parts. Supply DXF, thickness, quantity and edge finish. Bearing fits need post-machining, not an assumed laser tolerance. Confirm available thicknesses and delivery in the quote. |
| Precision hubs, split clamps, bearing carriers | [Xometry CNC](https://xometry.eu/fr/usinage-cnc/) | STEP plus dimensioned PDF with threads, fits, finish and quantities. Not ready to upload yet. Xometry says delivery is to the chosen address and supports unit quantities. |
| Alternative CNC service delivered in France | [Protolabs Network France](https://www.hubs.com/fr/usinage-cnc/france/) | France delivery advertised; obtain live quote after drawings are complete. |
| Printed fit-check parts, knobs, nonprecision fittings | [Sculpteo PA12](https://pro.sculpteo.com/fr/materiaux/pa12/) | Suitable prototype route; uploaded watertight STL/OBJ. PA12 stiffness/creep must not be assumed adequate for loaded bearing clamps or string anchors. |
| Timber soundbox | Routed plywood/wood components | Supplier and acoustic construction unresolved; metal CNC services do not automatically cover this work. |

These are sourcing routes checked online, not supplier acceptance of the design, reserved stock or fixed prices. Shipping to a Paris address is the practical plan; collection/hand-over has not been confirmed. No supplier has been contacted and no files uploaded or orders placed.

## Smallest sensible manufacturing release

First complete one representative voice, plus the highest-ratio stage packaging. Select a single compatible belt/profile family, actual bearing drawings and clamp interfaces. Then issue: consolidated bought-parts BOM with exact SKUs and alternatives; per-part STEP and dimensioned drawings for CNC; DXF and material/thickness/quantity for flat parts; genuine cut list after joint allowances; assembly drawing, fits, belt-tension method and fastener schedule. Test pluck/release, return drag, backlash, motor starting torque and tuning stability before multiplying by twelve.

Routine service should target M3 socket-head screws (2.5 mm Allen), captive nuts and removable modules. Catalogue grub screws or collars may need another key; that must be designed out or explicitly documented rather than claimed solved.

## Checks

Exact rational ratios, inverse speaking and arm lengths, minimal common phase return, valid native solids, and changed drive-envelope intersections were checked. No production release, full rigid-body collision sweep of new supplier parts, structural load calculation, acoustic validation or service-life certification is claimed. See the JSON for the computed findings and the CSV for each stage's wrap, pitch-path length and bore warning.
'''
(O/'Lovophone_Lab_Frame_Build_Review.md').write_text(notes)
