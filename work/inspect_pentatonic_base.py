import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as A,json
p=(_LOVOPHON_WORKSPACE + '/outputs/Harpe_d_Amour_Twelve_Electric.FCStd');d=A.openDocument(p)
for key in ['Driver','Output','LongArmRotor','Rocker']:
 g=d.getObject('F_'+key);print(key,'placement',g.Placement)
 for o in g.Group:
  if o.TypeId=='Part::Feature':print(o.Name,str(o.Shape.BoundBox))
for n in ['SoundboxShell','Baseplate_310x170x6','SoundboxEndBlock1','ElectricMotorBracket','NylonTensionerEndPlate','CommonInputShaft_D6','CommonIntermediateAxle','LowInputStand1','LowInputBearing1']:
 o=d.getObject(n);print(n,str(o.Shape.BoundBox))
for o in d.Objects:
 if o.TypeId=='Part::Feature' and (o.Name.startswith('F_') or o.Name.startswith('LowInput') or o.Name.startswith('IntermediateAxle')):print(o.Name,'parents',[p.Name for p in o.InList])
