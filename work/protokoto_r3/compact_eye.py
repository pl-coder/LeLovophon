from pathlib import Path
import json,sys,math
from config import *
import FreeCAD as A,FreeCADGui as G,Part
from FreeCAD import Vector as V
from PySide import QtWidgets
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([]);G.showMainWindow();G.getMainWindow().hide()
d=A.openDocument(str(OUT/'LeLovophon_Protokoto_R3.FCStd'));row=ROWS[4];s=row['station_x'];a,b,_=linkage(row,row['phase_rad'])
def cyl(r,h,p):return Part.makeCylinder(r,h,p,V(1,0,0))
def pt(x,p):return V(x,*p)
def capsule(x,a,b,w,t):
 p=pt(x,a);q=pt(x,b);u=q-p;u.normalize();n=V(0,-u.z,u.y)*w/2
 return Part.Face(Part.makePolygon([p+n,q+n,q-n,p-n,p+n])).extrude(V(t,0,0)).fuse(cyl(w/2,t,p)).fuse(cyl(w/2,t,q))
rod=capsule(s+5.5,a,b,2,1.5)
for cp,rad in [(a,3.3),(b,3.5)]:rod=rod.fuse(cyl(rad,1.5,pt(s+5.5,cp)))
for cp in [a,b]:rod=rod.cut(cyl(2.25,3.5,pt(s+4.5,cp)))
o=d.getObject('V05_SteelPushrod');o.Shape=rod.removeSplitter();o.DesignNote+=' Voice 5 compact crank eye OD6.6; same 4.5 bore. Nominal continuous main-shaft clearance 0.2 mm; minimum radial eye wall1.05 mm requires load/fatigue review.'
o=d.getObject('V05_CrankDryBush_GFM030402');sh=o.Shape.cut(cyl(3.76,.5,pt(s+5,a)).cut(cyl(3.3,.7,pt(s+4.9,a))));o.Shape=sh;o.DesignNote+=' Voice 5 only: face flange OD from7.5 to6.6 before pressing. Preserve 4.5 housing diameter, bore and flange thickness. This is a modified stock bush, not an unmodified catalogue part.'
assert all(o.Shape.isValid() and len(o.Shape.Solids)==1 for o in d.Objects if o.TypeId=='Part::Feature');d.recompute();d.save()
meshes=[];inv=[]
for o in d.Objects:
 if o.TypeId!='Part::Feature':continue
 sh=o.Shape;vs,ts=sh.tessellate(.35);meshes.append(dict(name=o.Name,vertices=[[p.x,p.y,p.z] for p in vs],triangles=ts,color=list(o.ViewObject.ShapeColor[:3]),motion=o.Motion,voice=o.Voice));inv.append(dict(name=o.Name,role=o.Role,motion=o.Motion,voice=o.Voice,material=o.MaterialName,volume_mm3=sh.Volume,solids=len(sh.Solids),note=o.DesignNote))
(OUT/'Part_Inventory.json').write_text(json.dumps(inv,indent=2));(ROOT/'work/protokoto_r3/mesh.json').write_text(json.dumps(meshes));print('COMPACT_EYE_SAVED',flush=True)
