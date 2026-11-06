import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,json
from FreeCAD import Vector as V
OUT=(_LOVOPHON_WORKSPACE + '/outputs');doc=App.openDocument(OUT+'/Harpe_d_Amour_Low_Nylon.FCStd')
for right in [False,True]:
 shape=doc.SoundboxShell.Shape.copy();block=doc.getObject('SoundboxEndBlock'+('1' if right else '0'));bs=block.Shape.copy();plate=doc.getObject('NylonTensionerEndPlate' if right else 'NylonAnchorEndPlate');ps=plate.Shape.copy()
 for y in ([-119,-145] if right else [-119,-139]):
  for z in [-87,-23]:
   start=V(325 if right else -39,y,z);hole=Part.makeCylinder(2.2,21 if right else 31,start,V(1,0,0));shape=shape.cut(hole);bs=bs.cut(hole)
   if not right:ps=ps.fuse(Part.makeCylinder(3,4,V(-34,y,z),V(1,0,0)).cut(Part.makeCylinder(2.2,6,V(-35,y,z),V(1,0,0))))
 doc.SoundboxShell.Shape=shape;block.Shape=bs;plate.Shape=ps
for r in json.loads(doc.Motion.LinkageGeometry):
 n=r['note'];o=doc.getObject(n+'_NylonBridgeCrown');s=o.Shape.copy();s.translate(V(0,-.4,0));o.Shape=s
 for tag in ['Anchor','Tuner']:
  o=doc.getObject(n+'_'+tag+'NylonSaddle');s=o.Shape.copy();s.translate(V(0,-.4,0));o.Shape=s
# These simple cylinder/box shapes represent nominal hardware, not a rated assembled load path.
doc.recompute();assert all(o.Shape.isValid() for o in doc.Objects if o.TypeId=='Part::Feature');doc.save()
