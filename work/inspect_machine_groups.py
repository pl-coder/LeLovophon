import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as A
D=A.openDocument((_LOVOPHON_WORKSPACE + '/outputs/Harpe_d_Amour_Twelve_Electric.FCStd'))
for n in ['Structure','RaisedArmTransmission','RatioBeltDrives','SharedGantry','ElectricDrive']:
 g=D.getObject(n);print(n,[(o.Name,o.TypeId) for o in g.Group])
