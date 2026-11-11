import sys,math,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'outputs/LeLovophon_Pluck_Layout_R5';C=O/'Cutting_Preview'
import FreeCAD as A,Part
from FreeCAD import Vector as V
d=A.openDocument(str(O/'LeLovophon_Pluck_Layout_R5.FCStd'));records=[]
def export(n,sh,t):
 sh=sh.copy();bb=sh.BoundBox;sh.translate(V(-bb.XMin,-bb.YMin,-bb.ZMin));ob=d.addObject('Part::Feature','EXPORT_'+n);ob.Shape=sh;Part.export([ob],str(C/(n+'.step')))
 faces=[f for f in sh.Faces if all(abs(v.Point.x)<1e-6 for v in f.Vertexes)];face=max(faces,key=lambda f:f.Area)
 lines=['0','SECTION','2','HEADER','9','$ACADVER','1','AC1015','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','ENTITIES'];loops=[]
 for wire in face.Wires:
  if len(wire.Edges)==1 and isinstance(wire.Edges[0].Curve,Part.Circle):
   circle=wire.Edges[0].Curve;p=circle.Center;r=circle.Radius;lines+=['0','CIRCLE','8','CUT','10',f'{p.z:.9f}','20',f'{p.y:.9f}','30','0','40',f'{r:.9f}'];loops.append(dict(type='circle',x=p.z,y=p.y,r=r));continue
  pts=wire.discretize(Deflection=.015)
  if (pts[-1]-pts[0]).Length<1e-6:pts=pts[:-1]
  coords=[(p.z,p.y) for p in pts]
  lines+=['0','LWPOLYLINE','100','AcDbEntity','8','CUT','100','AcDbPolyline','90',str(len(pts)),'70','1']
  for x,y in coords:lines+=['10',f'{x:.9f}','20',f'{y:.9f}']
  loops.append(dict(type='polyline',points=coords))
 lines+=['0','ENDSEC','0','EOF'];p=C/(n+'.dxf');p.write_text('\n'.join(lines)+'\n')
 # Validate closure, simple loops and total signed-independent silhouette area against the actual CAD plate.
 areas=[];valid=[]
 for loop in loops:
  if loop['type']=='circle':areas.append(math.pi*loop['r']**2);valid.append(True)
  else:
   pts=loop['points'];areas.append(abs(sum(x*v-y*u for (x,y),(u,v) in zip(pts,pts[1:]+pts[:1]))/2));wire=Part.makePolygon([V(0,y,x) for x,y in pts]+[V(0,pts[0][1],pts[0][0])]);valid.append(Part.Face(wire).isValid())
 profile_area=max(areas)-(sum(areas)-max(areas));error=profile_area-sh.Volume/t
 assert all(valid),(n,valid)
 assert abs(error)<1.0,(n,error)
 records.append(dict(part=n,thickness_mm=t,closed_valid_contours=True,area_from_dxf_mm2=profile_area,area_from_step_mm2=sh.Volume/t,area_difference_mm2=error,dxf_chord_tolerance_mm=.015,units='mm',bounds_mm=[sh.BoundBox.ZLength,sh.BoundBox.YLength],loops=loops))
 return sh
export('R4_CurvedRib_8mm_x4',d.getObject('R4_CurvedRib_1').Shape,8)
export('R4_CrankOuTrigger_6mm_x1',d.getObject('R4_CrankOuTrigger_6mm').Shape,6)
back=Part.makeBox(2,48,30)
for y in [8,32]:
 for z in [8,22]:back=back.cut(Part.makeCylinder(2.2,4,V(-1,y,z),V(1,0,0)))
export('R4_BackingPlate_2mm_x4',back,2)
# The two drill templates are 1:1 plane faces, not bend developments.
root=Part.makeBox(3,48,30)
for y in [17,38]:root=root.cut(Part.makeCylinder(2.75,5,V(-1,y,9),V(1,0,0)))
export('R4_Angle_RibFace_DrillingTemplate',root,3)
body=Part.makeBox(3,48,30)
for y in [8,32]:
 for z in [8,22]:body=body.cut(Part.makeCylinder(2.2,5,V(-1,y,z),V(1,0,0)))
export('R4_Angle_BodyFace_DrillingTemplate',body,3)
for name,obname in [('R4_StockAngle_Right_x3','R4_StockAngleFoot_1'),('R4_StockAngle_Left_x1','R4_StockAngleFoot_4')]:
 sh=d.getObject(obname).Shape.copy();bb=sh.BoundBox;sh.translate(V(-bb.XMin,-bb.YMin,-bb.ZMin));ob=d.addObject('Part::Feature','EXPORT_'+name);ob.Shape=sh;Part.export([ob],str(C/(name+'.step')))
(C/'Profile_Verification.json').write_text(json.dumps(dict(source_cad_sha256=hashlib.sha256((O/'LeLovophon_Pluck_Layout_R5.FCStd').read_bytes()).hexdigest(),profiles=records,manufacturing_release=False),indent=2))
print('EXPORTED',[(r['part'],r['area_difference_mm2']) for r in records],flush=True)
