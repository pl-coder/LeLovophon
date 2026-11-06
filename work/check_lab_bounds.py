import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as A
from pathlib import Path
R=Path((_LOVOPHON_WORKSPACE + ''));d=A.openDocument(str(R/'work/Lovophone_Lab_Frame_Base.FCStd'))
for o in d.Objects:
 if o.TypeId=='Part::Feature':
  b=o.Shape.BoundBox
  if b.ZMax>47.29 or b.ZMin < -155.001:print(o.Name,b.ZMin,b.ZMax)
