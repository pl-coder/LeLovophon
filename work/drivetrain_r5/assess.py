import sys,json,math,csv
from pathlib import Path
from fractions import Fraction
import numpy as np
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'work/pluck_r5'))
from force_model import ROWS,geometry,DRIVE,OMEGA,transfer_at_zero,groups,GRAV
O=R/'outputs/LeLovophon_Pluck_Layout_R5/Drivetrain_Assessment';D=O.parent/'Drive_Effort'
raw=json.loads((O/'Exudyn_Shared_Crossing_Reactions.json').read_text());budget=json.loads((D/'CAD_Force_Budget.json').read_text());transfer=transfer_at_zero();rows=[]
cross=lambda a,b:a[0]*b[1]-a[1]*b[0]
def jd(r,q):
 e=1e-6;a,b,p,s=geometry(r,q);_,_,pm,sm=geometry(r,q-e);_,_,pp,sp=geometry(r,q+e)
 return (pp-pm)/(2*e),np.arctan2(np.sin(sp-sm),np.cos(sp-sm))/(2*e)
# All rolling bearing friction torques set equal for this explicitly conditional sensitivity.
qglobal=np.linspace(0,480*OMEGA,144001);rolling_factor=np.full(qglobal.shape,11.)
bush_coeff=0.;shaftloads=[]
for r,t,re in zip(ROWS,transfer,raw['reactions']):
 rat=float(Fraction(r['ratio']));q=np.linspace(0,2*math.pi/rat,20001);a,b,phi,psi=geometry(r,q);P=np.array(r['pivot_yz'])[:,None]/1000;Q=np.array(r['crank_yz'])[:,None]/1000;u=(a-b)/(r['ground_mm']/1000)
 arm=(r['arm_radius_mm']-.15)/1000;lever=cross(b-P,u);rod=np.abs(arm/lever);crankmoment=np.abs(cross(a-Q,-u)*rod);gearFt=crankmoment/(.00025*r['driven_teeth']);maxrod=float(rod.max());maxgear=float(gearFt.max())
 # Euler pinned-pinned weakest axis for an ideal straight2x1.5mm steel strip.
 L=r['ground_mm'];I=2*1.5**3/12;pcr=math.pi**2*200000*I/L**2
 tor=abs(re['gear_constraint_output']);tooth=tor/(.00025*r['driven_teeth']);forceA=np.linalg.norm(re['crank_pin_reaction_N'][:2]);forceB=np.linalg.norm(re['rocker_pin_reaction_N'][:2]);fp=float(t['string_stiffness_N_per_mm']*.2)
 phip,psip=jd(r,0.);bush_coeff+=.0015*(forceA*abs(float(psip)+rat)+forceB*abs(float(psip-phip)))
 phiall,_=jd(r,qglobal);rolling_factor+=2*rat+2*np.abs(phiall)
 # First-pass gross stresses only, not supplier ratings / material allowables.
 tubeI=math.pi*(4**4-2**4)/64;tubestress=fp*r['arm_radius_mm']*2/tubeI;tubedefl=fp*r['arm_radius_mm']**3/(3*100000*tubeI)
 commonpin_shear=(tor*rat*1000/2.5)/(2*math.pi*.98**2/4)
 outputpin_shear=(tor*1000/1.5)/(2*math.pi*.98**2/4)
 rows.append(dict(voice=r['index'],note=r['note'],ratio=r['ratio'],arm_radius_mm=r['arm_radius_mm'],rod_pin_centre_length_mm=L,rod_force_N_per_1N_tangential_tip_force_peak_over_local_cycle=maxrod,gear_tangential_force_N_per_1N_tangential_tip_force_peak_over_local_cycle=maxgear,ideal_steel_link_Euler_weak_axis_load_N=pcr,case_tip_force_N=fp,case_driven_shaft_torque_Nm=tor,case_gear_tangential_tooth_force_N=tooth,case_gear_normal_tooth_force_N=tooth/math.cos(math.radians(20)),case_gear_radial_separating_force_N=tooth*math.tan(math.radians(20)),case_crank_pin_reaction_N=float(forceA),case_rocker_pin_reaction_N=float(forceB),case_link_gross_axial_stress_MPa=max(forceA,forceB)/(2*1.5),case_arm_tube_nominal_root_bending_stress_MPa=tubestress,case_arm_ideal_tube_only_tip_deflection_mm=tubedefl,case_input_gear_crosspin_nominal_double_shear_MPa=commonpin_shear,case_output_gear_crosspin_nominal_double_shear_MPa=outputpin_shear))
 shaftloads.append((r['station_x']-5.5,tor*rat))
# Check the gear multiplier interpretation independently against common drive reaction.
reflected=sum(t for x,t in shaftloads);ig=groups[0];input_gravity_moment=ig['mass']*GRAV*(ig['c'][1]-DRIVE[1]/1000);assert abs(reflected-input_gravity_moment-raw['input_torque_Nm'])<1e-8
# Twist relative to the crank's X376 drive plane; solid shaft, no cross-hole weakening.
G=80000.;J=math.pi*5**4/32;twists=[]
for location,_ in shaftloads:
 points=sorted(set([location,376.]+[x for x,t in shaftloads if location<x<376]));theta=0.
 for a,b in zip(points,points[1:]):
  transmitted=sum(t for x,t in shaftloads if x<(a+b)/2);theta+=transmitted*1000*(b-a)/(G*J)
 twists.append(theta*180/math.pi)
for rr,theta in zip(rows,twists):rr['case_common_shaft_ideal_twist_from_handle_deg']=theta
countpeak=float(rolling_factor.max());countmean=float(rolling_factor.mean());mu_cases=[dict(assumed_dynamic_mu=mu,first_order_radial_dry_bush_loss_torque_Nm=mu*bush_coeff,first_order_radial_dry_bush_hand_force_N=mu*bush_coeff/.032) for mu in [.08,.15]]
summary=dict(cad_sha256=raw['cad_sha256'],scope='Conditional shared-crossing load case with moving-part gravity and0.2mm equal sideways string deflection; no contact release, friction iteration, inertia, impact or jam. Full local-cycle force-transfer coefficients separately assume1N tangential tip resistance at any phase.',rolling_bearings_total=59,rolling_bearing_breakdown=dict(local_683ZZ_crank=24,local_683ZZ_rocker=24,common_input_MR105ZZ=9,grip_MR105ZZ=2),dry_link_bushes=24,gear_meshes=12,common_shaft_support_bearings=9,gear_module_mm=.5,gear_face_width_mm=4,gear_pressure_angle_deg=20,case_input_torque_with_gravity_Nm=reflected-input_gravity_moment,shared_input_group_gravity_torque_Nm=input_gravity_moment,gear_reaction_reflection_agreement_error_Nm=abs(reflected-input_gravity_moment-raw['input_torque_Nm']),case_max_gear_tangential_tooth_force_N=max(x['case_gear_tangential_tooth_force_N'] for x in rows),case_max_link_end_reaction_N=max(max(x['case_crank_pin_reaction_N'],x['case_rocker_pin_reaction_N']) for x in rows),case_max_ideal_arm_tube_bending_stress_MPa=max(x['case_arm_tube_nominal_root_bending_stress_MPa'] for x in rows),case_max_ideal_arm_tube_tip_deflection_mm=max(x['case_arm_ideal_tube_only_tip_deflection_mm'] for x in rows),case_max_solid5mm_common_shaft_twist_deg=max(twists),rolling_equal_per_bearing_torque_sensitivity=dict(peak_input_reflection_factor=countpeak,mean_input_reflection_factor=countmean,condition='All59 rolling bearings each assigned the same constant resisting torque; grip held independently. Local crank/rocker speeds reflected to input, actual bearing torques unmeasured.',scenarios=[dict(assumed_each_bearing_drag_Nmm=t,additional_peak_handle_force_N=countpeak*t*.001/.032) for t in [.1,.5,1.0]]),dry_bush_first_order_shared_crossing_sensitivity=mu_cases,critical_unknowns=['Miniature bearing starting/running torque and its preload/fit/alignment dependence','Actual tooth geometry, root radius, material grade, wear rating and shaft-hub attachment rating','PET release, peak forces, impacts, jams and load-dependent friction','Arm split-hub clamp slip, brazed joints, shaft grooves and cross-hole stress concentrations','Tolerance/preload stack across9 common-shaft supports and48 local bearings'],allowable_stresses_or_supplier_load_ratings_applied=False,physical_test_passed=False,manufacturing_release=False,per_voice=rows)
(O/'Drivetrain_Loads.json').write_text(json.dumps(summary,indent=2))
with (O/'Per_Voice_Loads.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps({k:v for k,v in summary.items() if k!='per_voice'},indent=2),flush=True)
