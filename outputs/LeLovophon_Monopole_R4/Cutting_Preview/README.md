# Le Lovophon — R4 rear-frame quotation package

Prepared 11 November 2026. Millimetres throughout. Design/quotation preview; not a released production kit. The free-moving mechanism, musical ratios, arm proportions, strings and 700 mm body come from R3. This package changes the support frame only.

The frame uses four identical curved ribs on the rear side, one straight fixed rail and a small crank outrigger. There are no front posts, overhead gantry, welded joints or bent curved tubes in the new frame. The 8 mm ribs are deliberately thicker through the sheet than thin decorative panels: they must resist sideways movement as well as support weight.

## Ask the cutting shop for

- 4 × curved ribs, 8 mm aluminium 5083, using the rib STEP/DXF.
- 1 × crank outrigger, 6 mm aluminium, using its STEP/DXF.
- 4 × rear backing plates, 2 mm stainless, using their STEP/DXF.
- Optionally 4 finished stock-angle feet: 3 right and 1 left, using their individual STEP files. Otherwise buy 30×30×3 mm aluminium equal angle, saw four 48 mm pieces and drill using the two face templates.

Request deburring and a soft edge break, particularly around hands and strings. Suggested appearance: satin bead-blasted/clear-anodised aluminium and plain stainless fasteners. Confirm alloy, finish, hole tolerances, minimum hole/ligament size and material availability with the chosen shop. Clearance-hole locations should be agreed to about ±0.15 mm; no laser-cut hole is used as a bearing fit. Do not apply a kerf offset yourself; let the supplier compensate its process.

DXFs contain cut contours only, in millimetres, AutoCAD2000 format. Round holes are true circles. Curved outer edges are polylines with 0.015 mm chord tolerance; the accompanying STEP is the solid reference. Profiles were checked for closed valid loops and agreement with solid area; see Profile_Verification.json. The angle drilling templates show two faces of existing angle stock; they are NOT unfolded bend patterns. The two complete angle STEP files settle face orientation and handedness.

## Purchased parts and precision parts

The BOM covers the new rear frame, not the whole instrument. Five SHF8 fixed-shaft clamps accept the rear 8 mm solid rail. Four hold it on the ribs; one carries the outrigger. Their holes are on the shaft centreline, 32 mm apart. SHF8 is a catalogue family, not a guarantee that every seller has identical geometry. Check the selected manufacturer's actual footprint, projecting screw heads and tool access before releasing plate cutting. CAD clamp bodies are nominal catalogue envelopes; internal threads are omitted.

The rotating drive remains the separate 5 mm shaft in R3's bearings. The rear 8 mm rail is structural and fixed; its SHF8 clamps are not rotating bearings. Existing precision bearing carriers, gear fits, bushes and the crank bearing console still require their original precision processes. This package does not make those parts suitable for laser cutting.

Use the 16 metal sleeves to carry M4 clamping preload across the 12 mm structural rear rim, with backing plates on the inside. Fit sleeve length to the actual measured wood thickness. The frame loads the rim rather than the thin soundboard. Rear_Rim_Mounting_Locations.csv gives the hole coordinates from the bass end and body bottom; it is a mounting reference, not a complete wood-shop cutting sheet. R4 CAD includes open-bottom nut-access pockets at nearby braces/endblocks. The future wooden-body cutting package remains a later design requirement.

## European supplier routes checked

- [JohnSteel JSBiz](https://www.john-steel.com/biz/en/): accepts STEP/DXF, offers cutting/bending and machining; states manufacture in France and no minimum invoice amount.
- [Fractory](https://fractory.com/fr/decoupe-laser/): aluminium laser cutting and delivery throughout France. Its [FAQ](https://fractory.com/frequently-asked-questions/) states no minimum order quantity and accepts individual 3D part files.
- [DamenCNC Netherlands SHF8](https://www.damencnc.com/en/shf8-flanged-shaft-support-8mm/a155) and [8 mm ground shaft](https://www.damencnc.com/en/8mm-linear-motion-shaft-precision/a165).
- [Olimex Bulgaria SHF8](https://www.olimex.com/Products/Robot-CNC-Parts/ShaftSupport/SUPPORT-SHF8/) is an alternative clamp source; confirm its detailed drawing before substitution.
- [RAF/MWComponents M0541-4-SS](https://www.mwcomponents.com/shop/m0541-4-ss) documents the 6 mm OD × 4.3 mm ID × 12 mm stainless spacer size; this is a size reference, not a confirmed European stock reservation.

These are plausible quoting/procurement routes, not supplier approvals, quotations or orders. Exact stock, delivery cost, fit and finish must be confirmed against the selected parts. No supplier has received the files.

## Assembly

See [Assembly_Guide.md](../Assembly_Guide.md). CAD clearances and idealised elastic estimates do not establish loaded stiffness, fatigue life, clamp holding torque or reliable pick release. The next build step is a full-size frame/one-voice trial, checking alignment and smooth travel before committing to all twelve voices.
