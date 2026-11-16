import sys,json,math
from pathlib import Path
from fractions import Fraction
import numpy as np
R=Path(__file__).resolve().parents[2];W=R/'work/pluck_r5';O=R/'outputs/LeLovophon_Pluck_Layout_R5/Drive_Effort';O.mkdir(exist_ok=True)
sys.path.insert(0,str(W));from config import ROWS,DRIVE,linkage,angle
mass_input=W/'mass_properties.json'
if not mass_input.exists():mass_input=O/'Reproduction/mass_properties.json'
raw=json.loads(mass_input.read_text());parts=raw['parts'];GRAV=9.80665;OMEGA=math.pi/10

def aggregate(ps,key,voice,motion):
 m=sum(p['mass_kg'] for p in ps);c=sum(p['mass_kg']*np.array(p['com_m'][1:]) for p in ps)/m
 I=sum(p['Ixx_kg_m2']+p['mass_kg']*np.sum((np.array(p['com_m'][1:])-c)**2) for p in ps)
 return dict(key=key,voice=voice,motion=motion,mass=m,c=c,I=I,parts=[p['name'] for p in ps])
groups=[aggregate([p for p in parts if p['motion']=='Input'],'Input',0,'Input')]
for r in ROWS:
 i=r['index']
 for mot,orig in [('Crank',['Crank']),('Rocker',['Rocker','Pendulum']),('Coupler',['Coupler'])]:groups.append(aggregate([p for p in parts if p['voice']==i and p['motion'] in orig],f'{i:02d}_{mot}',i,mot))

def geometry(r,q):
 rat=float(Fraction(r['ratio']));th=r['phase_rad']-rat*np.asarray(q);Q=np.array(r['crank_yz'])/1000;P=np.array(r['pivot_yz'])/1000;l=r['ground_mm']/1000
 ax=Q[0]+.01*np.cos(th);ay=Q[1]+.01*np.sin(th);dx=ax-P[0];dy=ay-P[1];d=np.hypot(dx,dy);v=(.014**2-l*l+d*d)/(2*d);h=np.sqrt(np.maximum(0,.014**2-v*v));bx=P[0]+v*dx/d-h*dy/d;by=P[1]+v*dy/d+h*dx/d
 beta=np.arctan2(by-P[1],bx-P[0]);phi=np.arctan2(np.sin(beta-r['rocker_mid_rad']),np.cos(beta-r['rocker_mid_rad']))
 a0,b0,_=linkage(r,r['phase_rad']);lam0=math.atan2(b0[1]-a0[1],b0[0]-a0[0]);lam=np.arctan2(by-ay,bx-ax);psi=np.arctan2(np.sin(lam-lam0),np.cos(lam-lam0))
 return np.array([ax,ay]),np.array([bx,by]),phi,psi

def pose(g,q):
 q=np.asarray(q);mot=g['motion'];c=g['c']
 if mot=='Input':cp=np.array(DRIVE)/1000;psi=q;v=c-cp;tr=cp
 else:
  r=ROWS[g['voice']-1];a,b,phi,psi=geometry(r,q)
  if mot=='Crank':cp=np.array(r['crank_yz'])/1000;psi=-float(Fraction(r['ratio']))*q;v=c-cp;tr=cp
  elif mot=='Rocker':cp=np.array(r['pivot_yz'])/1000;psi=phi;v=c-cp;tr=cp
  else:
   a0,b0,_=linkage(r,r['phase_rad']);v=c-np.array(a0)/1000;tr=a
 x=np.cos(psi)*v[0]-np.sin(psi)*v[1];y=np.sin(psi)*v[0]+np.cos(psi)*v[1]
 return np.array([x+tr[0],y+tr[1]]),psi

def loads(q,eps=1e-4):
 q=np.asarray(q);grav=np.zeros_like(q,dtype=float);inert=grav.copy();J=grav.copy()
 for g in groups:
  c,p=pose(g,q);cm,pm=pose(g,q-eps);cp,pp=pose(g,q+eps)
  cq=(cp-cm)/(2*eps);cqq=(cp-2*c+cm)/eps**2;pq=(pp-pm)/(2*eps);pqq=(pp-2*p+pm)/eps**2
  grav+=g['mass']*GRAV*cq[0];inert+=OMEGA**2*(g['mass']*np.sum(cqq*cq,axis=0)+g['I']*pqq*pq);J+=g['mass']*np.sum(cq*cq,axis=0)+g['I']*pq*pq
 return grav,inert,J

def transfer_at_zero():
 T=37.979683569383965;rows=[]
 for r in ROWS:
  i=r['index'];rat=float(Fraction(r['ratio']));eps=1e-6
  _,_,phi1,_=geometry(r,eps);_,_,phi0,_=geometry(r,-eps);gain=abs(float((phi1-phi0)/(2*eps)))
  L=.600/rat;a=(r['pick_x']-r['bridge_x'])/1000;b=(321-r['pick_x'])/1000
  k=T*(1/a+1/b);rp=(r['arm_radius_mm']-.15)/1000
  rows.append(dict(voice=i,note=r['note'],string_stiffness_N_per_mm=k/1000,bridge_to_pick_mm=a*1000,pick_to_nut_mm=b*1000,rocker_radians_per_input_radian=gain,pick_tangential_travel_mm_per_input_radian=rp*gain*1000,input_torque_per_1N_tip_force_Nm=rp*gain,handle_force_per_1mm_string_deflection_N=k*.001*rp*gain/.032))
 return rows
if __name__=='__main__':
 t=np.linspace(0,480,48001);q=t*OMEGA;gv,it,J=loads(q);rr=transfer_at_zero();coeff=sum(x['handle_force_per_1mm_string_deflection_N'] for x in rr)
 out=dict(cad_sha256=raw['cad_sha256'],method='One-degree-of-freedom virtual work/inverse dynamics from actual CAD mass properties and exact gear/four-bar kinematics; finite-difference derivatives. Pick forces are sensitivity inputs, not validated contact/release predictions.',moving_parts=len(parts),moving_mass_kg=sum(g['mass'] for g in groups),rigid_groups=len(groups),input_rpm=3,handle_throw_mm=32,time_step_s=.01,cycle_s=480,ideal_no_pick_no_friction_peak_positive_torque_Nm=float(np.max(gv+it)),ideal_no_pick_no_friction_peak_absolute_torque_Nm=float(np.max(np.abs(gv+it))),ideal_no_pick_no_friction_peak_absolute_hand_force_N=float(np.max(np.abs(gv+it))/.032),ideal_gravity_peak_absolute_torque_Nm=float(np.max(np.abs(gv))),ideal_inertia_peak_absolute_torque_Nm=float(np.max(np.abs(it))),effective_inertia_range_kg_m2=[float(np.min(J)),float(np.max(J))],all_12_simultaneous_hand_force_N_per_mm_common_string_deflection=coeff,simultaneous_string_deflection_scenarios=[dict(deflection_mm=d,pluck_only_hand_force_N=coeff*d) for d in [.1,.2,.5,1.0]],per_voice=rr,unknowns=['Actual pick/string force versus displacement and release, including friction/contact and PET bending','Actual bearing/bush/gear starting and running loss under chosen grease, fits and alignment','Actual crank speed variations and user acceleration'],total_required_operating_force_N=None,physical_test_passed=False,manufacturing_release=False)
 (O/'CAD_Force_Budget.json').write_text(json.dumps(out,indent=2));np.savez(W/'analytical.npz',time=t,q=q,gravity=gv,inertia=it,J=J)
 print(json.dumps({k:v for k,v in out.items() if k!='per_voice'},indent=2),flush=True)
