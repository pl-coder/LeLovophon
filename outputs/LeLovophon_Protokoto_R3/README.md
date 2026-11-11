# Le Lovophon — Protokoto R3

10 November 2026. Revised engineering CAD, not a physically tested machine or manufacturing release. Open **LeLovophon_Protokoto_R3.FCStd** in FreeCAD. The R2 file and films remain unchanged; those films do not show this revision.

## What changed

- **Four corner posts**, with two end-plane diagonal braces and a removable open aluminium gantry. Nothing stands through the central string bed. Intermediate bearings hang from the upper rear beam; they are not extra floor-to-beam posts.
- **Longer protokoto:** 700 × 220 × 60 mm hollow wooden body, 600 mm bass speaking length. Named top, bottom, rims, end blocks and braces preserve the future wood-shop route. A solid test base remains an option; no cutting sheet has been issued.
- **Twelve equal-gauge strings:** provisional 1.05 mm PVDF monofilament. The lower return saddle, movable third bridges and common speaking nut have rounded 5 mm crowns with shallow grooves. String tails pass over the edge to accessible screw tensioners; stopper knots bear on a steel backing bar against the solid left end block.
- **Slender links:** 1.5 mm steel sheet, 2 mm centre width and 7 mm eye diameter. Replaceable polymer bushes run on the 3 mm journals, with thrust washers and axial running gaps. Voice 5 uses a compact 6.6 mm crank eye and a stock bush whose flange is faced to 6.6 mm; this gives 0.2 mm nominal continuous clearance to the main shaft. The original crank, rocker, tooth ratios, proportional arm lengths and phases are retained; voice assemblies move along the longer body as rigid units.
- **Less mass and friction:** carrier windows remove approximately 97 g of aluminium. Acetal gear blanks save approximately 263 g compared with these same shapes in brass. Shielded bearings, dry-running link bushes and a freely rotating crank grip avoid unnecessary sliding interfaces. These are design provisions, not a measured friction result.
- **Hand crank included:** removable 32 mm throw crank on the common input shaft; outboard bearing console carried by the end beam, without a fifth post. Its 16 mm grip has two MR105ZZ bearings, internal outer-race retainers and an inner-race spacer stack. Tightening the end screw does not clamp the grip shell. The full crank sweep clears the fixed structure.

Approximate saved-pose envelope, including the crank: **769 × 268 × 306 mm**. Allow more room for moving parts, fingers, carrying case and padding. Nominal model mass is about **4.4 kg**, excluding case, adhesive, finish and unmodelled race details. This longer version is larger than the earlier briefcase study.

## Ratios and timing

Pitch and crank rotation use the same exact ratios:

`1, 9/8, 5/4, 3/2, 5/3, 2, 9/4, 5/2, 3, 10/3, 4, 9/2`

The notes are C3–D3–E3–G3–A3, repeated upwards through D5. Speaking lengths are `600 / ratio` mm; arm radii remain `109 / ratio` mm. All twelve speaking sections are horizontal and all bridge feet sit on the soundboard.

The common phase repeats after **24 input turns**: eight minutes at **3 rpm**. Hand cranking preserves the mathematical relationships, but the player's speed sets elapsed time. A hand crank alone cannot regulate an eight-minute recording.

## Mechanical checks and limits

See **Verification_Summary.json** and **Checks/** for results, CAD fingerprints, inherited R2 checks and the scope of each verification. Inspection PNGs show the actual revised CAD geometry.

Nominal-solid checks cover all saved-pose part pairs, changed linkage motion, new fixed supports, continuous shared-input rotation envelopes, bridge support and 21.8 mm tensioner travel. Local geometry inherited from R2 is checked against the recorded source transformations. Sampled motion uses one-degree crank increments; a sampled pass is not proof of clearance between every pair of samples. Conservative continuous bounds are used where they establish clearance. Pick/string contact is intentional; physical release is not simulated.

Preliminary string theory gives about **38 N per string**, or **456 N total**, assuming PVDF density 1780 kg/m³, the nominated gauge and C3. Actual line diameter, density, stretch, knots and losses must be measured. Load estimates in Checks/ are simplified calculations, not tested ratings.

Before machining, settle gear-maker tooth/root geometry and backlash, retained spring-pin fits, bearing fits and coaxial alignment, weld distortion, timber joints and insert details. The long input shaft needs careful alignment: assemble supports loosely on a straight shaft/jig, shim to a free-running line, then tighten progressively and measure breakaway torque. The CAD core envelopes do not define final thread or press-fit dimensions.

The first loaded prototype must establish drive torque, link stability, backlash, pin retention, tuning/creep, bridge stability, pick flex/release, soundboard behaviour and repeatability. No physical performance or acoustic result is established by this file. The existing sampled-harp audio remains illustrative.

Link-bush reference: [igus iglide G300 metric flanged-bush dimensions](https://www.igus.com/ContentData/Products/Downloads/iglide_G300_FM_USen.pdf), GFM-0304-02. Order against the current supplier drawing; its actual housing OD is 4.5 mm and total length is 2 mm including its flange.
