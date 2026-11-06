import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,math,json,ast,time,os
from FreeCAD import Vector as V
from pathlib import Path
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs';d=App.openDocument(str(R/'work/Lovophone_Pentatonic_Base.FCStd'));rows=json.loads(d.Motion.LinkageGeometry)
code=ast.parse((O/'Animate_Open_Harpe.FCMacro').read_text());exec(compile(ast.Module(body=[n for n in code.body if isinstance(n,ast.FunctionDef) and n.name in ['harpe_live_beta','harpe_live_roots']],type_ignores=[]),'motion','exec'))
def world(o):s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return s
moving=set();groups={}
for r in rows:
 groups[r['note']]=[]
 for kind in ['Driver','Output','LongArmRotor','Rocker']:
  for o in d.getObject(r['note']+'_'+kind).Group:
   if o.TypeId=='Part::Feature':moving.add(o.Name);groups[r['note']].append(o)
fixed={o.Name:world(o) for o in d.Objects if o.TypeId=='Part::Feature' and o.Name not in moving}
fbounds={n:s.BoundBox for n,s in fixed.items()}
clashes=set();contacts=set();exact={};wrongstrings=set();phasechecks=[];start=time.time()
old=json.loads((O/'twelve_motor_geometry.json').read_text())['rows']
for r,orig in zip(rows,old):
 n=r['note']
 if os.environ.get('PENTATONIC_CHECK_VOICES') and n not in os.environ['PENTATONIC_CHECK_VOICES'].split(','):continue
 # Prove timing-relevant follower/cam dimensions remain identical.
 for k in ['ratio','follower_y','follower_z','lever_length','beta_mid','swing_gain','driver_teeth','driven_teeth']:assert r[k]==orig[k],(n,k)
 # Check phases over every original pluck in one normal-speed cycle.
 for t in [j*20/r['ratio']/144 for j in range(144)]:assert abs(harpe_live_beta(r,-math.radians(18*t*r['ratio']))-harpe_live_beta(orig,-math.radians(18*t*orig['ratio'])))<1e-12
 phasechecks.append(n)
 for step in range(144):
  t=step*20/r['ratio']/144
  for kind,p in harpe_live_roots(r,t).items():d.getObject(n+'_'+kind).Placement=p
  d.recompute()
  for o in groups[n]:
   sh=world(o);sb=sh.BoundBox
   for name,fs in fixed.items():
    if sb.intersect(fbounds[name]) and sh.common(fs).Volume>1e-5:
     if o.Name==n+'_ExtendedPick' and name==n+'_KotoSpeakingString':contacts.add(n)
     else:
      clashes.add((o.Name,name))
      if 'String' in name:wrongstrings.add((o.Name,name))
  if step in [47,95]:print('Checking',r['display_note'],step+1,'/144;',round(time.time()-start,1),'s',flush=True)
 # Explicitly check each pick at its centre crossing, which a coarse sweep could miss.
 arm=d.getObject(n+'_LongArmRotor');arm.Placement=App.Placement(V(r['station'],r['pivot_y'],r['pivot_z']),App.Rotation(V(1,0,0),90));d.recompute()
 exact[n]=world(d.getObject(n+'_ExtendedPick')).common(fixed[n+'_KotoSpeakingString']).Volume
 assert exact[n]>1e-5,(n,exact[n])
 for kind,p in harpe_live_roots(r,0).items():d.getObject(n+'_'+kind).Placement=p
 print('Checked',r['display_note'],'clashes so far',len(clashes),flush=True)
invalid=[o.Name for o in d.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())]
# Fixed-part check restricted to the parts whose geometry or mounting interface changed.
newparts=[r['note']+suffix for r in rows for suffix in ['_ArmHangingFork','_SwingStepUpBelt','_KotoThirdBridge']]+['ElectricMotorBracket']
staticclashes=set()
intentional={tuple(sorted([r['note']+'_KotoThirdBridge',r['note']+'_NylonBridgeCrown'])) for r in rows}
intentionalcontacts=set()
for name in newparts:
 sh=fixed[name];sb=sh.BoundBox
 for other,fs in fixed.items():
  if other==name:continue
  if sb.intersect(fbounds[other]) and sh.common(fs).Volume>1e-5:
   pair=tuple(sorted([name,other]));(intentionalcontacts if pair in intentional else staticclashes).add(pair)
report={'sampled_positions_per_voice_cycle':144,'moving_fixed_clashes':sorted(clashes),'changed_fixed_part_intersections':sorted(staticclashes),'intentional_bridge_crown_seats':sorted(intentionalcontacts),'sampled_own_string_contacts':sorted(contacts),'exact_own_string_contact_volume_mm3':exact,'timing_geometry_matches_approved_midi':phasechecks,'invalid_shapes':invalid,'scope':'Geometric and kinematic checks, not load, acoustic, fatigue, motor-sizing or safety certification.'}
(O/os.environ.get('PENTATONIC_CHECK_REPORT','Lovophone_Pentatonic_Clearance_Check.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
assert not invalid
assert not clashes,clashes
assert not staticclashes,staticclashes
print('All pentatonic geometric checks passed.',flush=True)
