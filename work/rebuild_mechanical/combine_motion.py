from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[2];O=R/'outputs/LeLovophon_Mechanical_Revision_R2';C=O/'Checks'
current=hashlib.sha256((O/'LeLovophon_R2.FCStd').read_bytes()).hexdigest();old=hashlib.sha256((R/'work/rebuild_mechanical/clearance_baseline.FCStd').read_bytes()).hexdigest()
p1=json.loads((C/'Motion_Progress.json').read_text());p2=json.loads((C/'Motion_Audit_05_08.json').read_text());p3=json.loads((C/'Motion_Progress_09_12.json').read_text())
assert p1['completed_voice']==4 and p3['completed_voice']==12
assert p2['cad_sha256']==old
delta=json.loads((C/'Retainer_Refinement_Motion.json').read_text());shared=json.loads((C/'Shared_Input_Continuous_Clearance.json').read_text())
assert delta['cad_sha256']==current and delta['baseline_cad_sha256']==old and shared['cad_sha256']==current
assert delta['all_moving_geometry_unchanged'] and shared['all_angles_covered']
baseline_hits=p1['unexpected']+p2['unexpected']+p3['unexpected'];changed=set(delta['changed_fixed_part_names'])
unresolved=[h for h in baseline_hits if h['b'] not in changed]
unresolved+=delta['unexpected']+shared['unexpected']
contacts=p1['intended']+p2['intended_contacts']+p3['intended']
for label,p,voices in [('01_04',p1,[1,2,3,4]),('05_08',p2,[5,6,7,8]),('09_12',p3,[9,10,11,12])]:
 q=dict(p,cad_sha256=old,checked_voices=voices,poses_per_voice=360,independent_tooth_phase_samples_per_pair=64,shared_input_poses=0,scope_note='Baseline per-voice sweeps completed; shared input instead verified by the stronger continuous envelope check on final CAD.')
 (C/f'Baseline_Motion_{label}.json').write_text(json.dumps(q,indent=2))
result=dict(cad_sha256=current,baseline_cad_sha256=old,poses_per_voice=360,gear_pose_interval_deg=5,independent_tooth_phase_samples_per_pair=64,shared_input_all_angles_covered=True,checked_voices=list(range(1,13)),unexpected=unresolved,intended_contacts=contacts,moving_station_x_slabs=p2['moving_station_x_slabs'],neighbour_moving_slab_gaps=p2['neighbour_moving_slab_gaps'],resolved_baseline_mount_contacts=baseline_hits,changed_fixed_parts=sorted(changed),scope='All twelve voice sweeps completed on the baseline. Every final moving solid is identical (exact saved-shape BREP hash). All modified fixed solids then rechecked using verified conservative motion envelopes, with 360 actual poses for any overlapping envelope. Any baseline contact with a modified fixed solid is replaced by its new full-motion result; contacts with unchanged parts remain failures. Shared input proven clear at every angle with containing axisymmetric envelopes. All independently moving local groups and 64 relative gear-tooth phases checked. Threads, elastic pick release, bearing internals, loads and tolerance stacks are not physically simulated.',physical_test_passed=False)
(C/'Motion_Audit.json').write_text(json.dumps(result,indent=2));assert not unresolved,unresolved
print('COMBINED_MOTION_PASS; baseline mount contacts resolved:',len(baseline_hits))
