import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as A,Part,math,json,time
from FreeCAD import Vector as V
from pathlib import Path
from unified_design import *
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs';d=A.openDocument(str(R/'work/Lovophone_Unified_Base.FCStd'));meta=json.loads((O/'Lovophone_Unified_Design.json').read_text());rows=meta['rows']
def world(o):s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return s
moving=set();groups={}
for r in rows:
 for k in ['Driver','Wheel','Idler']:
  g=d.getObject(r['prefix']+'_'+k)
  if g is None:continue
  groups[g.Name]=g
  moving.update(o.Name for o in g.Group if o.TypeId=='Part::Feature')
fixed={o.Name:world(o) for o in d.Objects if o.TypeId=='Part::Feature' and o.Name not in moving and 'Chain' not in o.Name}
fb={n:s.BoundBox for n,s in fixed.items()};clashes=set();contacts=set();samples=48;start=time.time()
for r in rows:
 for kind in ['Driver','Wheel','Idler']:
  g=d.getObject(r['prefix']+'_'+kind)
  if g is None:continue
  base=g.Placement
  for j in range(samples):
   g.Placement=A.Placement(base.Base,A.Rotation(V(0,0,1),j*360/samples));d.recompute()
   for o in g.Group:
    if o.TypeId!='Part::Feature':continue
    sh=world(o);b=sh.BoundBox
    for n,fs in fixed.items():
     if not b.intersect(fb[n]):continue
     if 'HubScrew' in o.Name and n=='CommonInputShaft':continue
     vol=sh.common(fs).Volume
     if vol>1e-5:
      if 'PickWheel' in o.Name and n==r['source_prefix']+'_KotoSpeakingString':contacts.add(r['note'])
      else:
       pair=(o.Name,n)
       if pair not in clashes:print('CLASH',pair,vol,flush=True)
       clashes.add(pair)
  g.Placement=base
 print('Checked',r['note'],len(clashes),'clashes',round(time.time()-start,1),'s',flush=True)
# Exact nominal release contact, rather than relying on a phase grid.
exact={}
for r in rows:
 g=d.getObject(r['prefix']+'_Wheel');sh=world(d.getObject(r['prefix']+'_PickWheel'));vol=sh.common(fixed[r['source_prefix']+'_KotoSpeakingString']).Volume;exact[r['note']]=vol;assert vol>1e-5,(r['note'],vol)
# Static chain and frame packaging against all actual string paths, crowns, bridges and tuner hardware.
critical={n:s for n,s in fixed.items() if any(k in n for k in ['String','NylonGuide','NylonOverEdge','Bridge','Saddle','TensionScrew','TieShuttle'])}
staticclashes=[]
for o in d.Objects:
 if o.TypeId!='Part::Feature' or not (o.Name.startswith(('Frame','AxleBlock','SharedIdler','V')) and o.Name not in moving):continue
 if any(k in o.Name for k in ['BridgeLock','BridgeSlidingNut']):continue
 sh=world(o);b=sh.BoundBox
 for n,s in critical.items():
  if b.intersect(s.BoundBox) and sh.common(s).Volume>1e-5:staticclashes.append([o.Name,n])
report=dict(sampled_positions_per_rotor=samples,moving_fixed_clashes=sorted(clashes),frame_chain_vs_string_hardware_clashes=staticclashes,exact_nominal_release_contact_mm3=exact,source_rows_identical_pitch_rotation=all(r['pitch_ratio_exact']==r['rotation_ratio_exact'] for r in rows),scope='Rigid package checks only. Same-loop chain/sprocket engagement is excluded because tooth/link geometry is illustrative. Nominal pick/string overlap represents plucking; elastic deflection and release need physical tests. Structural joints and motor loads are not certified.')
(O/'Lovophone_Unified_Clearance_Check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True);assert not clashes;assert not staticclashes;print('UNIFIED PACKAGE CHECK PASSED',flush=True)
