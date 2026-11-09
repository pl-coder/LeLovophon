import FreeCAD as A,Part,math,json
from FreeCAD import Vector as V
from direct_gear_math import *
OUT=OUT/'Axle_Clearance_Revision'
d=A.openDocument(str(OUT/'LeLovophon_Direct_Gear_Prototype.FCStd'))
def shape(o):
 s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return s
def move(sh,p,deg):
 s=sh.copy();s.rotate(V(0,*p),V(1,0,0),deg);return s
fixed=[o for o in d.Objects if o.TypeId=='Part::Feature' and (o.Name.startswith(('RearStay_','InputBearingShelf_','InputBearingBlock_','RearBackbone','StayFoot_')) or '_Carrier' in o.Name or '_RearPivotStay' in o.Name or o.Name=='Common5mmInputShaft')]
fs=[(o.Name,shape(o)) for o in fixed];hits=[]
for row in ROWS:
 n='V%02d'%row['index'];P=row['pivot_yz'];Q=row['crank_yz'];t0=row['phase_rad'];a0,b0,beta0=linkage(row,t0);rod0=math.atan2(b0[1]-a0[1],b0[0]-a0[0]);parts=[]
 for o in d.Objects:
  if o.TypeId!='Part::Feature' or not o.Name.startswith(n+'_'):continue
  if any(k in o.Name for k in ['_Crank','_Rocker','_POMCoupler','_PinRetainingWasher','_PendulumHub','_TubeArm','_TipSocket','_PETPick']):parts.append((o.Name,shape(o)))
 for j in range(72):
  t=t0+2*math.pi*j/72;a,b,beta=linkage(row,t);delta=angle(row,t);rod=math.atan2(b[1]-a[1],b[0]-a[0])
  for name,base in parts:
   if '_Crank' in name:s=move(base,Q,math.degrees(t-t0))
   elif '_POMCoupler' in name:s=move(base,a0,math.degrees(rod-rod0));s.translate(V(0,a[0]-a0[0],a[1]-a0[1]))
   elif '_PinRetainingWasher_0' in name:s=move(base,Q,math.degrees(t-t0))
   elif '_Rocker' in name or '_PinRetainingWasher_1' in name:s=move(base,P,math.degrees(beta-beta0))
   else:s=move(base,P,math.degrees(delta))
   for fn,f in fs:
    if not s.BoundBox.intersect(f.BoundBox):continue
    vol=s.common(f).Volume
    if vol>1e-5:hits.append(dict(voice=n,pose=j,moving=name,fixed=fn,volume_mm3=vol))
 print(n,'checked',flush=True)
r=dict(poses_per_voice=72,rigid_moving_to_support_intersections=hits,invalid_shapes=[o.Name for o in d.Objects if o.TypeId=='Part::Feature' and not o.Shape.isValid()],scope='Moving cranks, rockers, rods, pins, washers and pendula against all cassette carrier plates, rear stays, input blocks and common shaft. Excludes intended bearing/shaft fits, gear meshing, strings and soundbox; these need separate checks.',physical_pass=False)
(OUT/'Drive_CAD_Check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2),flush=True)
