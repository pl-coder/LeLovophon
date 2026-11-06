import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,zipfile
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
d=App.openDocument(OUT+'/Harpe_Koto_Geometry_Rescue.FCStd');parts=[o for o in d.Objects if o.TypeId=='Part::Feature'];expected=sum(o.Shape.Volume for o in parts)
s=Part.read(OUT+'/Harpe_Koto_Geometry_Rescue.step')
print('Recovered native features:',len(parts),'all valid:',all(o.Shape.isValid() for o in parts))
print('STEP valid:',s.isValid(),'volume difference:',round(abs(s.Volume-expected),6))
for f in ['Harpe_Koto_Geometry_Rescue.FCStd','Harpe_d_Amour_Koto_Recovered.FCStd']:
 with zipfile.ZipFile(OUT+'/'+f) as z: print(f,'CRC',z.testzip() or 'OK','GUI metadata present:', 'GuiDocument.xml' in z.namelist())
