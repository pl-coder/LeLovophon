import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,math,json,ast
from FreeCAD import Vector as V
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
doc=App.openDocument(OUT+'/Harpe_d_Amour_Low_Nylon.FCStd');src=App.openDocument(OUT+'/Harpe_d_Amour_Portable.FCStd');rows=json.loads(doc.Motion.LinkageGeometry);original={r['note']:r for r in json.loads(src.Motion.LinkageGeometry)}
code=ast.parse(open(OUT+'/Animate_Open_Harpe.FCMacro').read());exec(compile(ast.Module(body=[n for n in code.body if isinstance(n,ast.FunctionDef) and n.name in ['harpe_live_beta','harpe_live_roots']],type_ignores=[]),'motion','exec'))
code=ast.parse(open(OUT+'/../work/build_wide_swing.py').read());exec(compile(ast.Module(body=[n for n in code.body if isinstance(n,ast.FunctionDef) and n.name=='wire'],type_ignores=[]),'belt','exec'))
def bx(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def cy(r,h,p):return Part.makeCylinder(r,h,p,V(1,0,0))
def strap(x,y1,z1,y2,z2):
 d=V(0,y2-y1,z2-z1);d.normalize();p=V(0,-d.z,d.y)*3;a=V(x,y1,z1);b=V(x,y2,z2)
 return Part.Face(Part.makePolygon([a+p,b+p,b-p,a-p,a+p])).extrude(V(4,0,0))
for r in rows:
 n=r['note'];orig=original[n]
 for key in ['follower_y','follower_z','lever_length','beta_mid','swing_half_angle_deg']:r[key]=orig[key]
 s=r['station'];uy=r['pivot_y'];fy=r['follower_y'];fz=r['follower_z'];z=r['pivot_z']
 for suffix in ['_FollowerLever','_FollowerRoller','_RollerPin']:doc.getObject(n+suffix).Shape=src.getObject(n+suffix).Shape.copy()
 for j,off in enumerate([-5.5,0]):
  x=s+off
  shape=bx(4,fy+119,8,x,-109,-154).fuse(bx(4,20,z+164,x,fy-10,-154)).fuse(bx(4,fy-uy+20,20,x,uy-10,z-10))
  if j==0:shape=shape.fuse(strap(x,-60,-150,fy-8,z-12))
  shape=shape.cut(cy(6.05,6,V(x-1,uy,z))).cut(cy(6.05,6,V(x-1,fy,fz)))
  doc.getObject(n+'_PendulumBracket'+str(j)).Shape=shape
  doc.getObject(n+'_FollowerPivotBearing'+str(j)).Shape=src.getObject(n+'_FollowerPivotBearing'+str(j)).Shape.copy()
 A=V(s+5.25,fy,fz);B=V(s+5.25,uy,z);ra=64/math.pi;rb=16/math.pi
 doc.getObject(n+'_SwingStepUpBelt').Shape=Part.Face(wire(A,B,ra+.8,rb+.8)).cut(Part.Face(wire(A,B,ra+.1,rb+.1))).extrude(V(3,0,0))
 for kind,p in harpe_live_roots(r,0).items():doc.getObject(n+'_'+kind).Placement=p
doc.Motion.LinkageGeometry=json.dumps(rows);doc.Motion.Status='18 mm nylon string bed; arm pivots lowered while cam followers retain their original height and amplitudes. Offset 64:16 step-up belts. Rounded end guides and external screw-pull nylon tensioners; prototype mechanical detail and string loads remain unverified.'
doc.recompute();doc.save();report=json.load(open(OUT+'/low_nylon_geometry.json'));report['rows']=rows;report['status']=doc.Motion.Status;json.dump(report,open(OUT+'/low_nylon_geometry.json','w'),indent=2)
print('Restored follower heights and original wide swings; dropped front bearing lugs; offset step-up belts saved.')
