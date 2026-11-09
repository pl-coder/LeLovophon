import math,json
from direct_gear_math import *
def distance(p,a,b):
 v=(b[0]-a[0],b[1]-a[1]);w=(p[0]-a[0],p[1]-a[1]);t=max(0,min(1,sum(x*y for x,y in zip(v,w))/sum(x*x for x in v)));return math.dist(p,(a[0]+t*v[0],a[1]+t*v[1]))
rod_margin=1e6;crank_margin=1e6;closure=0;phase_error=0;wrong_margin=1e6;reports=[]
for row in ROWS:
 P=row['pivot_yz'];Q=row['crank_yz'];crank_margin=min(crank_margin,math.dist(DRIVE,Q)-12-2.5)
 for j in range(10001):
  theta=j*2*math.pi/10000;a,b,beta=linkage(row,theta);rod_margin=min(rod_margin,distance(DRIVE,a,b)-2.5-2)
  delta=angle(row,theta);tip=(P[0]-(row['arm_radius_mm']-.15)*math.cos(delta),P[1]+(row['arm_radius_mm']-.15)*math.sin(delta))
  for other in ROWS:
   if other['index']==row['index']:continue
   # Conservative tip-to-string centre distance in YZ;0.5 mm sheet tip halfwidth plus0.4 mm string radius.
   poly=[]
   for yy,zz in [(-3,row['arm_radius_mm']-6),(3,row['arm_radius_mm']-6),(.5,row['arm_radius_mm']-.15),(-.5,row['arm_radius_mm']-.15)]:
    poly.append((P[0]-zz*math.cos(delta)-yy*math.sin(delta),P[1]-zz*math.sin(delta)+yy*math.cos(delta)))
   target=(-91,other['pivot_yz'][1]);edge=min(distance(target,poly[k],poly[(k+1)%4]) for k in range(4))
   wrong_margin=min(wrong_margin,edge-.4)
 start=angle(row,row['phase_rad']);end=angle(row,row['phase_rad']+2*math.pi*24*float(Fraction(row['ratio'])));phase_error=max(phase_error,abs(start-end));reports.append(dict(note=row['note'],driver=row['driver_teeth'],driven=row['driven_teeth'],coupler_mm=row['ground_mm'],half_swing_deg=row['half_swing_deg']))
r=dict(samples_per_voice=10001,minimum_rod_to_common_shaft_surface_clearance_mm=rod_margin,minimum_crank_disk_to_common_shaft_clearance_mm=crank_margin,minimum_pick_tip_to_other_string_conservative_margin_mm=wrong_margin,maximum_480_second_phase_error_rad=phase_error,independent_rotor_axial_gap_mm=15,parts_detailed=False,physical_pass=False,tests='Exact rigid crank-rocker closure and phase return; conservative projected clearances. Does not test force, flexure, wear, gear quality or all fasteners.',voices=reports)
print(json.dumps({k:v for k,v in r.items() if k!='voices'},indent=2))
assert rod_margin>0 and crank_margin>0 and wrong_margin>0 and phase_error<1e-9
(OUT/'Drive_Mathematical_Check.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='voices'},indent=2))
