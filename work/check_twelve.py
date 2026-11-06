import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,math,json,ast
from FreeCAD import Vector as V
OUT=(_LOVOPHON_WORKSPACE + '/outputs');doc=App.openDocument(OUT+'/Harpe_d_Amour_Twelve_Electric.FCStd');rows=json.loads(doc.Motion.LinkageGeometry)
code=ast.parse(open(OUT+'/Animate_Open_Harpe.FCMacro').read());defs=ast.Module(body=[n for n in code.body if isinstance(n,ast.FunctionDef) and n.name in ['harpe_live_beta','harpe_live_roots']],type_ignores=[]);exec(compile(defs,'kinematics','exec'))
def world(o):
 s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return s
moving=set()
for row in rows:
 for kind in ['Driver','Output','LongArmRotor','Rocker']:moving.update(o.Name for o in doc.getObject(row['note']+'_'+kind).Group if o.TypeId=='Part::Feature')
fixed={o.Name:world(o) for o in doc.Objects if o.TypeId=='Part::Feature' and o.Name not in moving}
clashes=set();contacts=set()
for row in rows:
 n=row['note']
 for step in range(72):
  t=step*20/row['ratio']/72;poses=harpe_live_roots(row,t)
  for kind,p in poses.items():doc.getObject(n+'_'+kind).Placement=p
  doc.recompute()
  for kind in ['Driver','Output','LongArmRotor','Rocker']:
   for o in doc.getObject(n+'_'+kind).Group:
    if o.TypeId!='Part::Feature':continue
    s=world(o)
    for name,fs in fixed.items():
     if s.BoundBox.intersect(fs.BoundBox) and s.common(fs).Volume>1e-5:
      if o.Name==n+'_ExtendedPick' and name==n+'_KotoSpeakingString':contacts.add(n)
      else:clashes.add((o.Name,name))
 print('Checked',n,flush=True)
 for kind,p in harpe_live_roots(row,0).items():doc.getObject(n+'_'+kind).Placement=p
invalid=[o.Name for o in doc.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())]
report={'sampled_positions_per_cycle':72,'moving_fixed_clashes':sorted(clashes),'sampled_own_string_contacts':sorted(contacts),'invalid_shapes':invalid,'scope':'Sampled kinematic geometry only; structural, fatigue, fastener, tension and acoustic design remain unverified.'}
with open(OUT+'/twelve_clearance_check.json','w') as f:json.dump(report,f,indent=2)
print(report,flush=True)
doc.recompute();doc.save()
