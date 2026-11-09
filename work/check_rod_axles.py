import FreeCAD as A,math,json,sys
from FreeCAD import Vector as V
from direct_gear_math import ROWS,linkage
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'outputs/LeLovophon_Direct_Gear_Prototype/Axle_Clearance_Revision/LeLovophon_Direct_Gear_Prototype.FCStd'
out=Path(sys.argv[2]) if len(sys.argv)>2 else ROOT/'outputs/LeLovophon_Direct_Gear_Prototype/Axle_Clearance_Revision/Rod_Axle_Clearance.json'
d=A.openDocument(str(path))
def shape(o):
 s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return s
axles=[(o.Name,shape(o)) for o in d.Objects if o.TypeId=='Part::Feature' and ('_3mmShaft_' in o.Name or '_CrankShaftOnePiece' in o.Name or o.Name=='Common5mmInputShaft')]
hits=[];mins={};rows=[]
for row in ROWS:
 n='V%02d'%row['index'];obj=d.getObject(n+'_POMCoupler');base=shape(obj);a0,b0,_=linkage(row,row['phase_rad']);r0=math.atan2(b0[1]-a0[1],b0[0]-a0[0]);minc=1e6
 for j in range(360):
  t=row['phase_rad']+2*math.pi*j/360;a,b,_=linkage(row,t);ang=math.atan2(b[1]-a[1],b[0]-a[0]);s=base.copy();s.rotate(V(0,*a0),V(1,0,0),math.degrees(ang-r0));s.translate(V(0,a[0]-a0[0],a[1]-a0[1]))
  for name,f in axles:
   # Exact3D distance includes axial separation; circular shafts are unchanged by rotation.
   gap=max(f.BoundBox.XMin-s.BoundBox.XMax,s.BoundBox.XMin-f.BoundBox.XMax,0)
   dist=gap if gap>0 else s.distToShape(f)[0];minc=min(minc,dist);mins[name]=min(mins.get(name,1e6),dist)
   if s.BoundBox.intersect(f.BoundBox):
    vol=s.common(f).Volume
    if vol>1e-5:hits.append(dict(voice=n,pose=j,axle=name,volume_mm3=vol))
 rows.append(dict(voice=n,minimum_axle_clearance_mm=minc));print(n,'minimum',minc,flush=True)
r=dict(model=str(path),poses_per_voice=360,rod_axle_intersections=hits,voice_minimum_clearances=rows,minimum_clearance_mm=min(r['minimum_axle_clearance_mm'] for r in rows),physical_test_passed=False)
out.write_text(json.dumps(r,indent=2));print('INTERSECTIONS',len(hits),flush=True)
