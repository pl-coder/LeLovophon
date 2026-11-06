import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,json
O=(_LOVOPHON_WORKSPACE + '/outputs');d=App.openDocument(O+'/Harpe_d_Amour_Twelve_Electric.FCStd');rows=json.loads(d.Motion.LinkageGeometry);groups=[]
for r in rows:
 for k in ['Driver','Output','LongArmRotor','Rocker']:
  o=d.getObject(r['note']+'_'+k);groups.append({'note':r['note'],'kind':k,'matrix':list(o.Placement.toMatrix().A),'members':[x.Name for x in o.Group if x.TypeId=='Part::Feature']})
json.dump({'rows':rows,'groups':groups},open(O+'/../work/twelve_motion_map.json','w'));print('Motion map saved')
