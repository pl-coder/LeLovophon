import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,json
p=(_LOVOPHON_WORKSPACE + '/outputs/Harpe_d_Amour_Clockwork.FCStd');d=App.openDocument(p)
for key in ['Driver','Output','LongArmRotor','Rocker']:
 g=d.getObject('C_'+key);print(key)
 for o in g.Group:
  if o.TypeId=='Part::Feature':print(o.Name,str(o.Shape.BoundBox))
print('fixed',[(o.Name,str(o.Shape.BoundBox)) for o in d.Structure.Group if o.TypeId=='Part::Feature' and not o.Name.startswith(('C_','D_','E_','F_','G_','A_'))])
