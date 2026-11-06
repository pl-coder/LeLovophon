import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as A,json,csv,math
from pathlib import Path
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs';d=A.openDocument(str(R/'work/Lovophone_Lab_Frame_Base.FCStd'));p=json.loads((O/'Lovophone_Lab_Frame_Design.json').read_text());out=[]
for n in p['new_parts']:
 o=d.getObject(n);label=o.Label;length='';stock='Prototype joint component'
 for size in [8,6,4]:
  if label.startswith(str(size)+' × 1 mm aluminium'):
   stock=f'Aluminium tube {size} mm OD × 1 mm wall';length=round(o.Shape.Volume/(math.pi*((size/2)**2-(size/2-1)**2)),2)
 if '2.5 mm steel' in label:stock='Steel rod 2.5 mm';length=round(o.Shape.Volume/(math.pi*1.25**2),2)
 out.append(dict(part=n,description=label,stock=stock,nominal_cut_length_mm=length))
with (O/'Lovophone_Lab_Frame_Parts.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
print('Wrote',len(out),'frame components')
