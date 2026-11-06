import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,json
p=(_LOVOPHON_WORKSPACE + '/outputs/Harpe_d_Amour_Open_Centred.FCStd')
doc=App.openDocument(p)
parts=[o for o in doc.Objects if o.TypeId=='Part::Feature']
print({'native_reopen':True,'part_count':len(parts),'invalid_shapes':[o.Name for o in parts if o.Shape.isNull() or not o.Shape.isValid()],'cover_present':doc.getObject('DriveGuard') is not None,'stations':[r['station'] for r in json.loads(doc.Motion.LinkageGeometry)]})
