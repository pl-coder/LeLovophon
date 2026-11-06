import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App
p=(_LOVOPHON_WORKSPACE + '/outputs/Harpe_d_Amour_Low_Nylon.FCStd');d=App.openDocument(p)
for n in ['CommonInputShaft_D6','ClockworkInputCoupling','LowGearboxTray','LowInputStand0','LowInputBearing0']:
 o=d.getObject(n);print(n,str(o.Shape.BoundBox) if o else None)
