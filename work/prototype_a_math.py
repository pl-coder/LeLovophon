import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import math,json
from pathlib import Path
ROOT=Path((_LOVOPHON_WORKSPACE + ''));OUT=ROOT/'outputs/Lovophone_Prototype_A'
def belt_length(c,a,b,p=2):
 r=p*a/(2*math.pi);s=p*b/(2*math.pi);v=(r-s)/c
 return 2*math.sqrt(c*c-(r-s)**2)+math.pi*(r+s)+2*(r-s)*math.asin(v)
def center(a,b,L):
 lo=abs(a-b)/math.pi+.001;hi=L
 for _ in range(80):
  mid=(lo+hi)/2
  if belt_length(mid,a,b)<L:lo=mid
  else:hi=mid
 return (lo+hi)/2
C1=center(60,20,160);C2=center(30,20,160)
def linkage(t):
 # XY plane. Crank Q, rocker O. A and B are moving pin centres.
 Q=(30.,110.);O=(110.,110.);r=4.;l=80.;s=14.
 A=(Q[0]+r*math.cos(t),Q[1]+r*math.sin(t));dx=A[0]-O[0];dy=A[1]-O[1];d=math.hypot(dx,dy)
 a=(s*s-l*l+d*d)/(2*d);h=math.sqrt(s*s-a*a);ux=dx/d;uy=dy/d
 B=(O[0]+a*ux+h*uy,O[1]+a*uy-h*ux)
 beta=math.atan2(B[1]-O[1],B[0]-O[0]);return Q,O,A,B,beta
vals=[linkage(2*math.pi*j/10000)[4] for j in range(10001)];MID=(min(vals)+max(vals))/2
RLOW=67.19693845669907;RHIGH=RLOW/4.5
if __name__=='__main__':
 errors=[];angles=[];tips=[]
 for j in range(10001):
  q,o,a,b,beta=linkage(j*2*math.pi/10000)
  errors.append(abs(math.dist(a,b)-80));v=(a[0]-b[0],a[1]-b[1]);w=(o[0]-b[0],o[1]-b[1]);ang=math.degrees(math.acos(max(-1,min(1,(v[0]*w[0]+v[1]*w[1])/(80*14)))));angles.append(min(ang,180-ang))
  d=beta-MID;tips.append((60+RLOW*math.sin(d),110-RLOW*math.cos(d)))
 data=dict(stage1=dict(driver=60,driven=20,belt_pitch_mm=2,belt_teeth=80,center_mm=C1),stage2=dict(driver=30,driven=20,belt_pitch_mm=2,belt_teeth=80,center_mm=C2),ratio_exact='9/2',input_rpm=3,output_rpm=13.5,ground_mm=80,crank_mm=4,coupler_mm=80,rocker_mm=14,arm_low_radius_mm=RLOW,arm_high_radius_mm=RHIGH,rocker_mid_radians=MID,swing_half_angle_deg=math.degrees((max(vals)-min(vals))/2),minimum_transmission_angle_deg=min(angles),max_closure_error_mm=max(errors),samples=10001,physical_test_performed=False,full_machine_repeat_seconds=480)
 for key in ['stage1','stage2']:
  s=data[key];alpha=math.asin((s['driver']-s['driven'])/math.pi/s['center_mm']);s['small_wrap_deg']=180-2*math.degrees(alpha);s['engaged_teeth_reference']=s['driven']*s['small_wrap_deg']/360
 assert data['max_closure_error_mm']<1e-10
 (OUT/'Prototype_A_Calculations.json').write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))
