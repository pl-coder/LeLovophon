import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,json
from FreeCAD import Vector as V
p=(_LOVOPHON_WORKSPACE + '/outputs/Harpe_d_Amour_Low_Nylon.FCStd');d=App.openDocument(p)
for r in json.loads(d.Motion.LinkageGeometry):
 o=d.getObject(r['note']+'_ExtendedPick');o.Shape=Part.makeBox(3.3,.5,.9,V(15,-.25,r['radius']-.8));o.Label=r['note']+' replaceable compliant pick — nominal 0.1 mm string engagement'
d.recompute();d.save()
