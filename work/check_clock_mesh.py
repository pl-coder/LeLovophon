import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,math,json
from FreeCAD import Vector as V
OUT=(_LOVOPHON_WORKSPACE + '/outputs');d=App.openDocument(OUT+'/Harpe_d_Amour_Clockwork.FCStd')
base={n:d.getObject(n).Shape.copy() for n in ['ClockBarrelWheel','ClockIdlerWheel','ClockOutputWheel']};hits=[]
for step in range(16):
 a=step*6/16;ss=[]
 for n,y,angle in [('ClockBarrelWheel',-35,a),('ClockIdlerWheel',-66.5,-2.5*a),('ClockOutputWheel',-83,3*a)]:
  s=base[n].copy();s.rotate(V(0,y,-131),V(1,0,0),angle);ss.append(s)
 for i,j in [(0,1),(1,2)]:
  v=ss[i].common(ss[j]).Volume
  if v>1e-5:hits.append([step,i,j,v])
print('Sampled gear intersections',hits,flush=True)
json.dump({'gear_mesh_samples':16,'positive_volume_tooth_intersections':hits,'scope':'Sampled tooth geometry only, no strength, bearing, spring or escapement validation.'},open(OUT+'/clockwork_mesh_check.json','w'),indent=2)
