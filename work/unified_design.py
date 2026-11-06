from fractions import Fraction as F
import math
RATIOS=list(map(F,['1','9/8','5/4','3/2','5/3','2','9/4','5/2','3','10/3','4','9/2']))
NOTES=[48,50,52,55,57,60,62,64,67,69,72,74]
LABELS=['C3','D3','E3','G3','A3','C4','D4','E4','G4','A4','C5','D5']
PAIRS=[(32,32),(36,32),(40,32),(48,32),(40,24),(48,24),(54,24),(60,24),(60,20),(60,18),(64,16),(72,16)]
SLOTS=[k*32//19 for k in range(19)]
BASE_PERIOD=F(400);FULL_PERIOD=F(9600);PITCH=3.75
PICK_RADIUS=31.3;STRING_Y=-91;AXLE_Y=-60;DRIVE_X=190;PICK_X=270
RELEASE_ANGLE=2*math.pi-math.asin((AXLE_Y-STRING_Y)/PICK_RADIUS)
def rows():
 return [dict(index=i+1,note=label,midi_note=n,ratio_exact=str(r),ratio=float(r),pitch_ratio_exact=str(r),rotation_ratio_exact=str(r),frequency_hz=130.8127826502993*float(r),lane_z=-91+12*i,driver_teeth=a,driven_teeth=b,period_seconds=float(BASE_PERIOD/r),speaking_length_mm=330/float(r),bridge_x=320-330/float(r),slots=SLOTS,release_angle_radians=RELEASE_ANGLE) for i,(r,n,label,(a,b)) in enumerate(zip(RATIOS,NOTES,LABELS,PAIRS))]
def events(ratio,duration):
 period=BASE_PERIOD/ratio;out=[]
 for slot in SLOTS:
  phase=F((-slot)%32,32);k=0
  while (t:=(k+phase)*period)<duration:
   out.append((t,slot));k+=1
 return sorted(out)
def pitch_radius(teeth):return PITCH/(2*math.sin(math.pi/teeth))
# Smooth pitch-path approximation for chain packaging; tooth engagement is not a production profile.
def route(circles):
 normals=[]
 for i,(x,y,r) in enumerate(circles):
  xx,yy,rr=circles[(i+1)%len(circles)];dx,dy=xx-x,yy-y;d=math.hypot(dx,dy);ux,uy=dx/d,dy/d;k=(r-rr)/d;h=math.sqrt(1-k*k);normals.append((ux*k+uy*h,uy*k-ux*h))
 pieces=[]
 for i,(x,y,r) in enumerate(circles):
  ni=normals[i-1];no=normals[i];a=math.atan2(ni[1],ni[0]);b=math.atan2(no[1],no[0]);delta=(b-a)%(2*math.pi)
  pieces.append(('arc',r*delta,(x,y,r,a,delta)))
  xx,yy,rr=circles[(i+1)%len(circles)];p=(x+r*no[0],y+r*no[1]);q=(xx+rr*no[0],yy+rr*no[1]);pieces.append(('line',math.dist(p,q),(p,q)))
 return pieces

def route_point(pieces,s):
 s%=sum(p[1] for p in pieces)
 for kind,L,data in pieces:
  if s<=L:
   u=s/L
   if kind=='line':p,q=data;return (p[0]+(q[0]-p[0])*u,p[1]+(q[1]-p[1])*u)
   x,y,r,a,delta=data;return (x+r*math.cos(a+delta*u),y+r*math.sin(a+delta*u))
  s-=L
 return route_point(pieces,0)
def chain_layout(a,b):
 ra,rb,ri=map(pitch_radius,[a,b,12])
 def get(y):return route([(DRIVE_X,AXLE_Y,ra),(PICK_X,AXLE_Y,rb),(230,y,ri)])
 low=-15.;N=2*math.ceil(sum(p[1] for p in get(low))/PITCH/2);target=N*PITCH;hi=25.
 assert sum(p[1] for p in get(hi))>target
 for _ in range(50):
  mid=(low+hi)/2
  if sum(p[1] for p in get(mid))<target:low=mid
  else:hi=mid
 y=(low+hi)/2;return N,y,get(y)
if __name__=='__main__':
 assert all(F(a,b)==r for (a,b),r in zip(PAIRS,RATIOS));assert len(set(SLOTS))==19
 assert not any({(s+d)%32 for s in SLOTS}==set(SLOTS) for d in range(1,32))
 print('Slots',SLOTS,'release',math.degrees(RELEASE_ANGLE))
 for r in rows():print(r['note'],r['ratio_exact'],chain_layout(r['driver_teeth'],r['driven_teeth'])[:2])
 print('Full event count',sum(len(events(r,F(9600))) for r in RATIOS))
