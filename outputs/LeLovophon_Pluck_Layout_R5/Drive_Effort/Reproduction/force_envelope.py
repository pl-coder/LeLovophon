import json,math
from fractions import Fraction
import numpy as np
from scipy.optimize import minimize_scalar
from model import ROWS,geometry,O,OMEGA,DRIVE
q=np.linspace(0,480*OMEGA,144001);cols=[];per=[]
def jacobian(row,q):
 a,b,_,_=geometry(row,q);P=np.array(row['pivot_yz'])/1000;Q=np.array(row['crank_yz'])/1000
 ac=a-Q.reshape(2,*([1]*np.asarray(q).ndim));br=b-P.reshape(2,*([1]*np.asarray(q).ndim));r=b-a
 return np.abs(float(Fraction(row['ratio']))*(-r[0]*ac[1]+r[1]*ac[0])/(-r[0]*br[1]+r[1]*br[0]))*(row['arm_radius_mm']-.15)/1000
for row in ROWS:
 rat=float(Fraction(row['ratio']));period=2*math.pi/rat;t=np.linspace(0,period,10001);j=jacobian(row,t);k=int(j.argmax());dt=period/10000
 result=minimize_scalar(lambda x:-float(jacobian(row,x)),bounds=(t[k]-dt,t[k]+dt),method='bounded',options={'xatol':1e-13})
 # Round each estimated kinematic maximum upward to the next micrometre/radian.
 upper=math.ceil(-result.fun*1e6)/1e6
 cols.append(jacobian(row,q));per.append(dict(voice=row['index'],note=row['note'],numerically_refined_max_tangential_tip_travel_m_per_input_rad=float(-result.fun),rounded_up_tip_travel_m_per_input_rad=upper,hand_force_N_per_1N_tangential_tip_force=upper/.032))
sumj=np.sum(cols,axis=0);k=int(sumj.argmax());budget=json.loads((O/'CAD_Force_Budget.json').read_text());ideal=math.ceil(budget['ideal_no_pick_no_friction_peak_absolute_hand_force_N']*1000)/1000
a=sum(p['rounded_up_tip_travel_m_per_input_rad'] for p in per)/.032;b=float(sumj[k]/.032)
r=dict(cad_sha256=budget['cad_sha256'],scope='Conservative model-based quasistatic force envelope for bounded tangential tip forces, at constant3rpm. Every arm is allowed its maximum resisting tip force at every phase, including phases when not touching a string. Coincidence is deliberately overestimated; no release force or friction measurement is inferred. Numerical kinematic extrema refined and rounded upward, not a formal interval proof.',handle_throw_mm=32,phase_preserving_input_angle_step_deg=.06,independent_per_voice_global_max_sum_hand_N_per_1N_each_tip=a,phase_preserving_sampled_max_hand_N_per_1N_each_tip=b,phase_preserving_max_time_s=float(q[k]/OMEGA),ideal_unloaded_absolute_peak_hand_force_N=ideal,friction_torque_to_handforce_N_per_Nm=1/.032,conservative_conditional_expression='F_hand <= sum_i(J_i_max * F_tip_i_max)/0.032 + tau_loss_max/0.032 + 0.363 N, within the idealized constant-speed model. Tip force is tangential; loss is total reflected drivetrain drag. No impact, jam or arbitrary acceleration claim.',per_voice=per,scenarios=[dict(each_tip_resisting_force_cap_N=f,assumed_total_reflected_drag_cap_Nm=drag,conditional_hand_force_upper_envelope_N=a*f+drag/.032+ideal) for f,drag in [(.05,.02),(.1,.02),(.15,.02),(.1,.05)]],measured_force_inputs_available=False,operating_force_established=False,physical_test_passed=False)
(O/'Conditional_Force_Envelope.json').write_text(json.dumps(r,indent=2));print('ENVELOPE_COEFFICIENT',a,'N_hand / N_each_tip',flush=True)
