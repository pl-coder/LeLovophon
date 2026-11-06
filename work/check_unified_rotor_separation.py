import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as A,math,json,itertools
from pathlib import Path
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs';d=A.openDocument(str(O/'Lovophone_Unified_160min.FCStd'));rows=json.loads(d.Motion.UnifiedGeometry);rotors=[]
for r in rows:
 for k in ['Driver','Wheel','Idler']:
  g=d.getObject(r['prefix']+'_'+k)
  if g is None:continue
  c=g.Placement.Base;radius=0;zlo=1e9;zhi=-1e9
  for o in g.Group:
   s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());v,t=s.tessellate(.05)
   radius=max(radius,max(math.hypot(p.x-c.x,p.y-c.y) for p in v)+.1);zlo=min(zlo,s.BoundBox.ZMin);zhi=max(zhi,s.BoundBox.ZMax)
  rotors.append(dict(name=g.Name,x=c.x,y=c.y,radius_upper_mm=radius,z_min=zlo,z_max=zhi))
unproven=[];axial=radial=0
for a,b in itertools.combinations(rotors,2):
 if min(a['z_max'],b['z_max'])<max(a['z_min'],b['z_min']):axial+=1;continue
 D=math.hypot(a['x']-b['x'],a['y']-b['y'])
 if D>a['radius_upper_mm']+b['radius_upper_mm']:radial+=1
 else:unproven.append([a['name'],b['name']])
report=dict(rigid_rotors=len(rotors),pairs_proven_by_axial_separation=axial,pairs_proven_by_radial_separation=radial,unproven_pairs=unproven,tessellation_deflection_mm=.05,added_radial_margin_mm=.1,scope='Conservative swept-circle/axial bounds for independently rotating rigid wheel, drive and idler groups. Excludes intended shaft couplings, deformable picks and reference chain engagement.')
(O/'Lovophone_Unified_Rotor_Separation_Check.json').write_text(json.dumps(report,indent=2));print(report,flush=True);assert not unproven
