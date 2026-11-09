import FreeCAD as A,Part,json,math,time
from FreeCAD import Vector as V
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'outputs/LeLovophon_Direct_Gear_Prototype/Reality_Audit';O.mkdir(exist_ok=True)
p=R/'outputs/LeLovophon_Direct_Gear_Prototype/Axle_Clearance_Revision/LeLovophon_Direct_Gear_Prototype.FCStd';d=A.openDocument(str(p))
def world(o):
 s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return s
parts=[(o.Name,world(o)) for o in d.Objects if o.TypeId=='Part::Feature'];inv=[]
for n,s in parts:
 b=s.BoundBox;inv.append(dict(name=n,volume_mm3=s.Volume,bounds_mm=[b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax],solids=len(s.Solids),valid=s.isValid()))
(O/'Part_Inventory.json').write_text(json.dumps(inv,indent=2));print('INVENTORY',len(parts),flush=True)
hits=[];string_tests=[]
for i,(n,s) in enumerate(parts):
 for fn,f in parts[i+1:]:
  if not s.BoundBox.intersect(f.BoundBox):continue
  try:
   common=s.common(f);vol=common.Volume
   if vol>1e-5:
    bb=common.BoundBox;hits.append(dict(a=n,b=fn,volume_mm3=vol,intersection_center_mm=[bb.Center.x,bb.Center.y,bb.Center.z]))
  except Exception as e:hits.append(dict(a=n,b=fn,error=str(e)))
 if i%50==0:print('PAIR_SCAN',i,'hits',len(hits),flush=True)
(O/'Static_All_Pairs_Raw.json').write_text(json.dumps(dict(model=str(p.relative_to(R)),pose='saved common zero',part_count=len(parts),tested_pairs=len(parts)*(len(parts)-1)//2,positive_volume_intersections=hits,warning='Raw intersections include intentional modeled fits and undeveloped attachment reservations; they require interpretation. This is not an assembly clearance pass.'),indent=2))
# Explicit face clearance on the new crank flange against the front stationary carrier and bearing.
critical=[]
for i in range(1,13):
 n=f'V{i:02d}';a=world(d.getObject(n+'_CrankShaftOnePiece'))
 for suffix in ['_Carrier1','_683Bearing_1_1','_POMCoupler']:
  b=world(d.getObject(n+suffix));c=a.common(b);critical.append(dict(a=n+'_CrankShaftOnePiece',b=n+suffix,distance_mm=a.distToShape(b)[0],intersection_volume_mm3=c.Volume,coincident_face_area_mm2=c.Area))
(O/'Critical_Face_Clearances.json').write_text(json.dumps(critical,indent=2));print('STATIC_COMPLETE',len(hits),flush=True)
