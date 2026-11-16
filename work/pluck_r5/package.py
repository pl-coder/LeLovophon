import sys,json,csv,hashlib,zipfile,shutil
from pathlib import Path
from fractions import Fraction
from config import ROOT as R,ROWS,BEARINGS
O=R/'outputs/LeLovophon_Pluck_Layout_R5';W=R/'work/pluck_r5';D=O/'Drive_Effort';C=O/'Checks';P=O/'Cutting_Preview'
cad=O/'LeLovophon_Pluck_Layout_R5.FCStd';sha=hashlib.sha256(cad.read_bytes()).hexdigest()
s=json.loads((C/'Static_All_Pairs.json').read_text());m=json.loads((C/'R5_Motion_and_Tensioner_Clearance.json').read_text());g=json.loads((O/'Geometry_Summary.json').read_text());masses=json.loads((C/'Preliminary_Stiffness_and_Mass.json').read_text());f=json.loads((D/'CAD_Force_Budget.json').read_text());pl=json.loads((O/'Plucking_Layout.json').read_text());pr=json.loads((P/'Profile_Verification.json').read_text());inv=json.loads((O/'Part_Inventory.json').read_text())
assert all(h==sha for h in [s['cad_sha256'],m['cad_sha256'],f['cad_sha256'],g['cad_sha256'],pl['cad_sha256'],pr['source_cad_sha256']])
assert not s['unexpected'] and not m['unexpected_motion_intersections'] and not m['unexpected_tensioner_intersections']
assert all(p['valid'] and p['solids']==1 for p in inv)
I=C/'Inherited_R3';I.mkdir(exist_ok=True)
for name in ['Motion_Clearance_R3.json','Final_Refinement_Inheritance.json','Motion_Baseline_Before_Compact_Eye.json','Source_Geometry_Identity.json']:shutil.copy2(R/'outputs/LeLovophon_Protokoto_R3/Checks'/name,I/name)
shutil.copytree(R/'outputs/LeLovophon_Protokoto_R3/Checks/Inherited_R2',I/'Inherited_R2',dirs_exist_ok=True)
summary=dict(revision='Plucking Layout R5',status='Nominal geometry checks recorded; operating force and physical release unverified',cad_sha256=sha,parts=len(inv),invalid_parts=0,disconnected_part_shapes=0,static_pairs=s['pair_count'],unexpected_saved_pose_intersections=0,unexpected_motion_intersections=0,unexpected_tensioner_intersections=0,local_station_geometry_copied_and_translated=True,minimum_phase_independent_neighbour_moving_gap_mm=min(x['gap_mm'] for x in m['neighbour_moving_slab_gaps']),rear_support_ribs=4,front_support_posts=0,rear_rib_x_mm=[-210,-28,150,272],largest_rear_support_span_mm=182,nominal_mass_kg=masses['nominal_total_mass_kg'],input_shaft_cut_length_mm=575,rear_carrier_rail_cut_length_mm=590,input_bearing_x_mm=BEARINGS,handle_throw_mm=32,input_rpm=3,ideal_repeat_seconds=480,body_length_width_height_mm=[700,220,60],saved_pose_length_width_height_mm=g['saved_pose_length_width_height_mm'],first_six_pluck_fraction_from_third_bridge=.25,all_pluck_nearest_end_fraction_range=[min(x['fraction_from_nearest_end'] for x in pl['voices']),max(x['fraction_from_nearest_end'] for x in pl['voices'])],shared_zero_crossing_hand_force_N_per_mm_common_string_deflection=f['all_12_simultaneous_hand_force_N_per_mm_common_string_deflection'],operating_crank_force_N=None,force_status='Actual peak force unresolved: measured pick release and loaded drivetrain friction required. Conditional scenarios in Drive_Effort are not measured force.',physical_test_passed=False,manufacturing_release=False,limits=m['limits'])
summary['child_hand_drive_design_goal']='A school-age child should be able to start and continuously crank the complete instrument comfortably, accounting for load and friction.'
summary['child_hand_drive_goal_verified']=False
summary['hand_force_acceptance_target_N']=None
(O/'Verification_Summary.json').write_text(json.dumps(summary,indent=2))
new=f['all_12_simultaneous_hand_force_N_per_mm_common_string_deflection'];old=50.1351391552166;improvement=1-new/old
(O/'README.md').write_text(f'''# Le Lovophon — plucking layout R5

This revision puts all twelve picks clear of the string ends while preserving the complete exact-ratio musical drive. **The actual operating hand-crank force remains unmeasured.**

![R5 CAD render](R5_Studio_Overview.png)

## What changed

- The six bass voices pluck one quarter of their own speaking length from the third bridge. The six higher voices progress toward the middle: all positions are25–47% of speaking length from the nearer end. Treble positions approach the middle to leave clearance for the standard gears, bearings and carriers. This is a practical tone/compliance compromise, not a universal or acoustically tested optimum.
- Complete gear/link/arm stations slide along X; no extra offset arms, universal joints or new gear stages are added. A single station gap was widened2mm to fit its standard input-bearing support. Minimum nominal separation between neighbouring moving envelopes is {summary['minimum_phase_independent_neighbour_moving_gap_mm']:.1f}mm, independent of phase.
- C4 moves from6.18mm to75mm from its third bridge. Exact pentatonic pitches, inverse-ratio speaking lengths, proportional arm lengths, gear tooth counts, phases and nominal3rpm input are retained. Ideal repeat remains480seconds /24 input turns.
- Rear support ribs are relocated toX−210,−28,150,272mm. The four identical8mm flat-cut ribs, stock flange clamps, angle feet and32mm hand crank remain. Rear shaft is590mm of solidØ8mm steel; input shaft is575mm ofØ5mm steel, with only the required phased cross-pin bores.

The body remains700×220×60mm. Saved-pose overall envelope is {g['saved_pose_length_width_height_mm'][0]:.1f}×{g['saved_pose_length_width_height_mm'][1]:.1f}×{g['saved_pose_length_width_height_mm'][2]:.1f}mm. Nominal CAD material mass is {masses['nominal_total_mass_kg']:.2f}kg, before case, glue, finish and material variation.

[Plucking-position diagram](Plucking_Layout.png) · [Exact position table](Plucking_Positions.csv) · [Assembly changes](Assembly_Guide.md)

## Hand-crank force

The conditional plucking-force sensitivity at the all-12 shared centre crossing falls by about {improvement*100:.0f}%. If every string is deflected sideways by0.2mm together, the calculated pluck-only hand force is {new*.2:.2f}N, versus10.03N inR4. **This is a scenario, not the measured operating force or full-cycle peak.** Pick flex/release and drivetrain losses are absent from that number. Ideal gravity/inertia alone gives0.363N absolute peak at constant3rpm; this also does not establish real effort.

[Detailed force budget and physical test procedure](Drive_Effort/README.md) supplies independent Exudyn checks, conditional full-cycle force envelopes and a blank test record. A calibrated measurement through pick release in both directions, plus a complete instrument torque/hand-force trace through the480-second cycle and startup, is required to settle the actual number. No physical load test, motor sizing or manufacturing release is claimed.

## Checks and their limits

All1101 saved solids are valid and each contains one connected solid. All605550 stationary pairs have been considered; recorded unexpected intersections are zero. Whole local mechanisms were copied unchanged from the finalR3 geometry and translated along X; reverse-translation numerical geometry fingerprints check the copy. Prior local moving-pair evidence is retained under `Checks/Inherited_R3`. New fixed-world clearance uses conservative continuous motion envelopes; overlapping bounds are checked at one-degree local crank intervals. Neighbour moving axial slabs have positive separation. Intentional PET/string contact is listed separately and needs elastic release testing. Tensioner clearance is inherited for the unchanged system, with23 travel poses checked against new/changed geometry.

These nominal checks do not establish tolerance margins, bearing alignment, friction, pick reliability, acoustic quality, impact/jam resistance, stiffness under service loads or safe real-world performance. The preliminary stiffness estimate assumes ideal joints; it is not a load test or FEA validation. [Verification summary](Verification_Summary.json) records the final hash and limitations.

## Files

`LeLovophon_Pluck_Layout_R5.FCStd` is the new model. R4 is preserved separately. `Cutting_Preview/` provides quotation-preview plate STEP/DXF files and updated mounting coordinates; the plate shapes are inheritedR4 parts, so their original part identifiers remain. These are not released fabrication drawings. Complete woodshop sheets remain a later design requirement.

CAD SHA256 `{sha}`. No live FreeCAD session was restarted or modified, no supplier was contacted, and no GitHub update was made for this revision.
''')
(O/'Assembly_Guide.md').write_text('''# R5 assembly changes — unbuilt prototype

Use the saved R5 CAD and position table together. This note replaces R4's mounting locations; the physical assembly, alignment and release checks remain outstanding.

1. Confirm the actual purchased SHF8 clamp, bearing, insert and stock-angle drawings before cutting. R4-named flat profiles in this folder are unchanged part shapes. Obtain supplier deburring/edge breaking. Laser-cut clearance holes are not precision bearing seats.
2. Locate the four identical rear rib starts at native X−210,−28,150,272mm. Y is up, Z across strings, X along strings. Three angle feet face right; the last faces left. Through-bolt the structural rear rim using its compression sleeves, backing plates and accessible nuts. Do not tighten directly through unsupported soundboard skin. R5 body bores/pockets differ from R4; do not reuse an old drill map.
3. Fit the solidØ8×590mm rear rail fromX−221 to369 atY65,Z−125. Assemble the unchanged precision carriers onto that rail at the voice stations in `Plucking_Positions.csv`. Leave clamps loose while aligning the bearing axes. Ribs carry the rail, not the plucking strings.
4. Place the eight input bearing starts/centres in the supplied coordinate CSV. Fit theØ5×575mm input shaft fromX−194 to381. Its left positive-retention pin is atX−188; the right crank pin remainsX376. Phase/jig-drill the twelve gear cross-pin bores at stationX−5.5 along their original local axes; no abandoned holes are allowed. Final shaft/bearing fits, pin retention and coaxial alignment require shop detail and measurement.
5. Keep the exact original gear pairs, four-bar geometry, proportional arm radii and phase settings. All picks lie at stationX+8; strings/third bridges and the common nut stay in their original positions. The relocated bearing forD4 lies atX123.3. Its gap to the following station was increased2mm; do not move it into a neighbouring carrier.
6. Retain the rear-mounted crank outrigger, console and freely rotating grip. The32mm throw and its input speed/reference remain unchanged. Tune/tension the strings gradually and symmetrically, then check unloaded travel, tolerances and alignment before adjusting PET engagement.
7. Test a single real pick/string assembly first. Establish two-way release and actual force traces, then measure the whole mechanism through a full cycle. See `Drive_Effort/README.md`. Any rub, binding or unstable release invalidates a simple ideal-force prediction. A smooth-looking CAD animation is not a loaded performance test.

The body, full manufacturing fits and woodshop drawings are not released. This is a development/quotation model.
''')
p=O/'README.md';p.write_text(p.read_text()+'\n\nChild-powered drivetrain requirement: comfortable starting and continuous hand cranking by a school-age child; combined plucking, friction and linkage loads must be measured. This goal remains unverified.\n')
# Updated actual mounting coordinates and cut lengths; R4 flat-profile part names remain valid.
mount=[]
for i,x in enumerate([-210,-28,150,272],1):
 bx=x-30 if i==4 else x+8
 for xx in [bx+8,bx+22]:
  for yy in [-158,-134]:mount.append(dict(rib=i,rib_start_x_mm=x,body_bore_x_mm=xx,body_bore_y_mm=yy,axis='Z',compression_sleeve_z_start_mm=-130,compression_sleeve_length_mm=12))
with (P/'R5_Body_Mounting_Coordinates.csv').open('w',newline='') as fobj:
 w=csv.DictWriter(fobj,fieldnames=list(mount[0]));w.writeheader();w.writerows(mount)
with (P/'R5_Input_Bearing_Locations.csv').open('w',newline='') as fobj:
 w=csv.writer(fobj);w.writerow(['mount','bearing_start_x_mm','shaft_y_mm','shaft_z_mm']);w.writerows((i,x,65,-25) for i,x in enumerate(BEARINGS))
(P/'README.md').write_text('''# R5 quotation preview

The R4-named rib, outrigger, backing and stock-angle profiles are unchanged geometries, exported again from the current R5 CAD. Their original part numbers are intentionally retained. STEP is authoritative for shape; DXF contours use mm and0.015mm outer-curve chord tolerance with true circular holes. `Profile_Verification.json` checks closed contours and silhouette area against STEP. Angle templates are face-drilling guides for stock30×30×3mm angle,48mm cut length; they are not bend developments.

**Use the R5 coordinate CSVs, not the R4 body drill map.** Four ribs atX−210,−28,150,272. Stock rear railØ8×590mm and input shaftØ5×575mm. The complete saved R5 CAD defines the new body holes/pockets. Complete woodshop and precision-machining drawings remain later work. Actual clamp dimensions, clearances, material condition, fits, pin retention, edge finish, fastener access and tolerances must be confirmed before production.

No physical test or manufacturing release. Required operating hand force remains unresolved; see `../Drive_Effort/README.md`.
''')
(O/'Render_Metadata.json').write_text(json.dumps(dict(cad_sha256=sha,source='Exact tessellated saved CAD geometry',engine='Blender4.5.15 EEVEE',views=['R5_Studio_Overview.png','R5_Studio_Rear.png'],cosmetic_bevel_mm=.22,materials='Illustrative procedural woods and metals, not material approval',physical_validation=False),indent=2))
# Keep reproduction smoke-test artefacts out of the user-facing package.
results=D/'Reproduction/Results'
if results.exists():
 dest=W/'reproduction_results'
 if dest.exists():shutil.rmtree(dest)
 shutil.move(str(results),str(dest))
for path in O.glob('*.FCStd.*'):path.unlink()
for path in O.glob('*.FCStd1'):path.unlink()
for path in O.glob('*.FCBak'):shutil.move(str(path),str(W/path.name))
for path in (D/'Reproduction').glob('*.npz'):path.unlink()
for path in O.rglob('__pycache__'):shutil.rmtree(path)
for path in C.glob('*Progress*.json'):path.unlink()
with zipfile.ZipFile(D/'R5_Drive_Effort_Assessment.zip','w',zipfile.ZIP_DEFLATED) as z:
 for path in D.rglob('*'):
  if path.is_file() and path.suffix!='.zip':z.write(path,path.relative_to(D))
with zipfile.ZipFile(O/'LeLovophon_R5_Review_Package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for path in O.rglob('*'):
  if path.is_file() and path.suffix!='.zip' and 'Paris_Studio_16min' not in path.relative_to(O).parts:z.write(path,path.relative_to(O))
print(json.dumps(summary,indent=2),flush=True)
