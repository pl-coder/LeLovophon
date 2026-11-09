import math,json
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/LeLovophon_Direct_Gear_Prototype'
RATIOS=list(map(Fraction,['1','9/8','5/4','3/2','5/3','2','9/4','5/2','3','10/3','4','9/2']))
PAIRS=[(36,36),(36,32),(40,32),(48,32),(40,24),(48,24),(54,24),(60,24),(60,20),(80,24),(80,20),(90,20)]
NOTES=['C3','D3','E3','G3','A3','C4','D4','E4','G4','A4','C5','D5']
MODULE=.5;CRANK=10.;ROCKER=14.;DRIVE=(65.,-25.)
def linkage(row,t):
 # Coordinates in native YZ. Equal ground/coupler length, positive crank-rocker branch.
 q=row['crank_yz'];o=row['pivot_yz'];l=row['ground_mm'];a=(q[0]+CRANK*math.cos(t),q[1]+CRANK*math.sin(t));dx=a[0]-o[0];dy=a[1]-o[1];d=math.hypot(dx,dy);v=(ROCKER*ROCKER-l*l+d*d)/(2*d);h=math.sqrt(max(0,ROCKER*ROCKER-v*v));ux=dx/d;uy=dy/d
 b=(o[0]+v*ux-h*uy,o[1]+v*uy+h*ux);beta=math.atan2(b[1]-o[1],b[0]-o[0]);return a,b,beta
ROWS=[]
for i,(ratio,pair,note) in enumerate(zip(RATIOS,PAIRS,NOTES)):
 assert Fraction(*pair)==ratio
 radius=109/float(ratio);p=(-91+radius,-102+14*i);c=MODULE*sum(pair)/2;pd=math.dist(p,DRIVE);q=tuple(DRIVE[k]+c*(p[k]-DRIVE[k])/pd for k in range(2));g=math.dist(p,q)
 row=dict(index=i+1,note=note,ratio=str(ratio),driver_teeth=pair[0],driven_teeth=pair[1],station_x=35+24*i,pivot_yz=p,crank_yz=q,ground_mm=g,coupler_mm=g,arm_radius_mm=radius,pick_x=44+24*i,bridge_x=320-330/float(ratio))
 vals=[linkage(row,j*2*math.pi/10000)[2] for j in range(10001)]
 # Unwrap around branch reference.
 ref=vals[0];vals=[ref+math.atan2(math.sin(v-ref),math.cos(v-ref)) for v in vals];mid=(min(vals)+max(vals))/2;row['rocker_mid_rad']=mid;row['half_swing_deg']=math.degrees((max(vals)-min(vals))/2)
 # Find centre-crossing phase; a physical adjustable hub sets this phase.
 def f(t):return math.atan2(math.sin(linkage(row,t)[2]-mid),math.cos(linkage(row,t)[2]-mid))
 for j in range(10000):
  lo=j*2*math.pi/10000;hi=(j+1)*2*math.pi/10000
  if f(lo)<=0<f(hi):
   for _ in range(50):
    m=(lo+hi)/2
    if f(m)>0:hi=m
    else:lo=m
   row['phase_rad']=(lo+hi)/2;break
 assert 'phase_rad' in row
 row['grashof_margin_mm']=sum(sorted([g,g,CRANK,ROCKER])[1:3])-sum([min(g,g,CRANK,ROCKER),max(g,g,CRANK,ROCKER)])
 assert row['bridge_x']<row['pick_x']<320
 ROWS.append(row)
def angle(row,t):return math.atan2(math.sin(linkage(row,t)[2]-row['rocker_mid_rad']),math.cos(linkage(row,t)[2]-row['rocker_mid_rad']))
def report():
 errors=[];trans=[]
 for row in ROWS:
  for j in range(10001):
   a,b,beta=linkage(row,j*2*math.pi/10000);errors.append(abs(math.dist(a,b)-row['ground_mm']));o=row['pivot_yz'];u=(a[0]-b[0],a[1]-b[1]);v=(o[0]-b[0],o[1]-b[1]);c=sum(x*y for x,y in zip(u,v))/(row['ground_mm']*ROCKER);mu=math.degrees(math.acos(max(-1,min(1,c))));trans.append(min(mu,180-mu))
 return dict(scope='Full 12-channel drive architecture with explicit gears, shafts, bearings and crank-rockers; engineering prototype, not physically tested or released for manufacture.',module_mm=MODULE,pressure_angle_deg=20,crank_mm=CRANK,rocker_mm=ROCKER,drive_yz=DRIVE,input_rpm=3,repeat_seconds=480,voices=ROWS,minimum_transmission_angle_deg=min(trans),max_link_closure_error_mm=max(errors),half_swing_range_deg=[min(r['half_swing_deg'] for r in ROWS),max(r['half_swing_deg'] for r in ROWS)],physical_test_passed=False,machining_release=False)
if __name__=='__main__':
 OUT.mkdir(exist_ok=True);(OUT/'Drive_Calculations.json').write_text(json.dumps(report(),indent=2));print(json.dumps({k:v for k,v in report().items() if k!='voices'},indent=2))
