import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as A,json
from pathlib import Path
R=Path((_LOVOPHON_WORKSPACE + ''));d=A.openDocument(str(R/'outputs/Lovophone_Lab_Frame_Ratio_Review.FCStd'));rows=json.loads(d.Motion.LinkageGeometry);out=[]
for r in rows:
 for k in ['RatioDrivePulley','RatioDrivenPulley','RatioBelt']:
  o=d.getObject(r['note']+'_'+k);s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());v,t=s.tessellate(.2);out.append(dict(name=o.Name,vertices=[[p.x,p.y,p.z] for p in v],triangles=t))
(R/'work/lab_corrected_render_mesh.json').write_text(json.dumps(out));(R/'work/lab_corrected_render_rows.json').write_text(json.dumps(rows));print('Exported',len(out),'corrected drive envelopes',flush=True)
