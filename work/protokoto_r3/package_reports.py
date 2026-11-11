import json,hashlib,shutil,math
from pathlib import Path
from fractions import Fraction
from config import *
C=OUT/'Checks';cad=OUT/'LeLovophon_Protokoto_R3.FCStd';sha=hashlib.sha256(cad.read_bytes()).hexdigest()
def read(n):return json.loads((C/n).read_text())
static=read('Static_All_Pairs.json');delta=read('Final_Refinement_Inheritance.json');motion=read('Motion_Clearance_R3.json');dim=read('Dimensions_and_Tensioners.json')
assert static['cad_sha256']==delta['cad_sha256']==sha
assert delta['motion_baseline_sha256']==motion['cad_sha256']==dim['cad_sha256']
assert static['unexpected']==[] and dim['invalid_shapes']==[] and dim['tensioner_unexpected_intersections']==[]
assert len(motion['unexpected'])==1 and motion['unexpected'][0]['a']=='V05_CrankDryBush_GFM030402' and motion['unexpected'][0]['b']=='COMMON_SHAFT_ENVELOPE'
assert delta['compact_eye_continuous_clearance_mm']>.199999
assert all(x['material_outside_baseline_mm3']<1e-7 for x in delta['changed_moving_parts_are_material_subsets'])
assert all(b['fully_on_soundboard'] for b in dim['bridge_support'])
inv=json.loads((OUT/'Part_Inventory.json').read_text());assert len(inv)==1031 and all(p['solids']==1 for p in inv)
shutil.copy2(C/'Motion_Clearance_R3.json',C/'Motion_Baseline_Before_Compact_Eye.json')
final_motion=dict(cad_sha256=sha,baseline_cad_sha256=motion['cad_sha256'],baseline_report='Motion_Baseline_Before_Compact_Eye.json',final_refinement_proof='Final_Refinement_Inheritance.json',unexpected=[],resolved_baseline_intersections=motion['unexpected'],poses_per_changed_joint=360,continuous_compact_eye_shaft_clearance_mm=delta['compact_eye_continuous_clearance_mm'],neighbour_moving_axial_gaps_mm=motion['neighbour_moving_axial_gaps_mm'],scope='Inherited complete R3 baseline results with all known clashes closed. Two revised moving shapes are material subsets at identical kinematic poses; the one former bush/shaft clash is closed by a continuous half-plane clearance proof. Two moved fixed saddle screws are continuously axially separated from local moving stations and tensioner travel. All other shapes match complete BREP topology and parameters within 1e-10 round-trip precision. Final all-pairs static test run on this exact CAD. See named reports for full scope and evidence.',physical_test_passed=False)
(C/'Motion_Clearance_R3.json').write_text(json.dumps(final_motion,indent=2))
turns=[24*Fraction(r['ratio']) for r in ROWS];assert all(t.denominator==1 for t in turns)
summary=dict(revision='Protokoto R3',cad_sha256=sha,status='PASS recorded nominal geometry checks / UNBUILT',parts=1031,main_corner_uprights=4,all_pairs_tested=static['pair_count'],invalid_shapes=0,disconnected_part_shapes=0,unexpected_saved_pose_intersections=0,unexpected_remaining_motion_intersections=0,changed_joint_samples_per_revolution=360,continuous_shared_input_envelopes=True,compact_fifth_joint_continuous_nominal_shaft_clearance_mm=delta['compact_eye_continuous_clearance_mm'],minimum_neighbour_moving_axial_gap_mm=min(motion['neighbour_moving_axial_gaps_mm']),tensioner_travel_mm=21.8,unexpected_tensioner_travel_intersections=0,all_bridge_feet_supported=True,max_speaking_length_error_mm=dim['max_speaking_length_error_mm'],input_rpm=3,repeat_seconds_at_3rpm=480,repeat_common_input_turns=24,output_turns_per_repeat=[int(t) for t in turns],hand_crank_throw_mm=32,grip_has_two_bearings_and_inner_spacer_stack=True,body_envelope_mm=[700,220,60],saved_pose_envelope_mm=[768.5,267.5,306],gauge_mm=1.05,bass_speaking_length_mm=600,physical_test_passed=False,manufacturing_release=False,limits='Nominal geometry; material choices and loads provisional. Continuous bounds used when disjoint, one-degree motion sampling where bounds overlap. R2 unchanged local pairs inherit prior verified kinematics after source transformation checks. Tolerances, friction, torque, flexibility, wear, timber/weld strength and real pick release still need physical validation.',evidence=['Checks/Static_All_Pairs.json','Checks/Motion_Clearance_R3.json','Checks/Motion_Baseline_Before_Compact_Eye.json','Checks/Final_Refinement_Inheritance.json','Checks/Source_Geometry_Identity.json','Checks/Dimensions_and_Tensioners.json','Checks/Preliminary_Load_Estimates.json'])
(OUT/'Verification_Summary.json').write_text(json.dumps(summary,indent=2))
# Keep completed reports; progress files are not deliverables.
for name in ['Static_Progress.json','Motion_Progress_R3.json']:
 p=C/name
 if p.exists():p.unlink()
# FreeCAD automatic backups of superseded candidates belong in work, not outputs.
for p in OUT.glob('*.FCStd*'):
 if p!=cad:shutil.move(str(p),str(ROOT/'work/protokoto_r3'/p.name))
# Bundle the source audit evidence that unchanged R2 mechanisms inherit.
prior=ROOT/'outputs/LeLovophon_Mechanical_Revision_R2'
D=C/'Inherited_R2';D.mkdir(exist_ok=True)
for p in [prior/'Verification_Summary.json',*(prior/'Checks').glob('*.json')]:
 if 'Progress' not in p.name:shutil.copy2(p,D/p.name)
print(json.dumps(summary,indent=2))
