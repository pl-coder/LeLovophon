import FreeCAD as A,Part,math,json,time
from FreeCAD import Vector as V
from slender_bank_math import *
d=A.openDocument(str(OUT/'LeLovophon_Slender_Bank.FCStd'))
def world(o):
 s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return s
moving={o.Name for r in ROWS for o in d.getObject('V%02d_Rotor'%r['index']).Group}
fixed={o.Name:world(o) for o in d.Objects if o.TypeId=='Part::Feature' and o.Name not in moving}
bounds={n:s.BoundBox for n,s in fixed.items()};bad=set();own=set();wrong=set();start=time.time()
for r in ROWS:
 n='V%02d'%r['index'];g=d.getObject(n+'_Rotor');members=list(g.Group)
 # Original string object IDs remain historical C/Cs/D...; resolve by lane in the row order.
 original=['C','Cs','D','Eb','E','F','Fs','G','Ab','A','Bb','B'][r['index']-1]
 for j in range(181):
  angle=-45+j*.5;g.Placement=A.Placement(V(r['station_x'],r['pivot_y'],r['string_z']),A.Rotation(V(1,0,0),90+angle));d.recompute()
  for o in members:
   s=world(o);b=s.BoundBox
   for key,t in fixed.items():
    if not b.intersect(bounds[key]):continue
    if s.common(t).Volume>1e-6:
     if o.Name.endswith('_FlexiblePick') and key in [original+'_KotoSpeakingString',original+'_KotoBackString']:own.add(n)
     else:
      bad.add((o.Name,key))
      if 'String' in key:wrong.add((o.Name,key))
 print('Checked',r['note'],'clashes',len(bad),'elapsed',round(time.time()-start,1),flush=True)
 g.Placement=A.Placement(V(r['station_x'],r['pivot_y'],r['string_z']),A.Rotation(V(1,0,0),90))
# Independent moving assemblies have disjoint axial slabs: no relative phase can make them touch.
slabs=[]
for r in ROWS:
 g=d.getObject('V%02d_Rotor'%r['index']);b=A.BoundBox()
 for o in g.Group:b.add(world(o).BoundBox)
 slabs.append((b.XMin,b.XMax))
minsep=min(slabs[j][0]-slabs[i][1] for i in range(12) for j in range(i+1,12))
require=minsep>1
invalid=[o.Name for o in d.Objects if o.TypeId=='Part::Feature' and not o.Shape.isValid()]
rep=dict(poses_per_voice=181,half_swing_degrees=45,moving_fixed_intersections=sorted(bad),wrong_string_intersections=sorted(wrong),own_string_pick_contacts=len(own),minimum_independent_rotor_axial_separation_mm=minsep,independent_rotors_clear_for_any_relative_phase=require,invalid_shapes=invalid,drivetrain_included=False,physical_test_passed=False,scope='Upper-bank reference geometry. Half-degree sampled moving/fixed sweep; analytic disjoint axial slabs for independent rotors. No strength, joints, full drive, load or pick dynamics validation.')
(OUT/'Slender_Bank_Clearance_Check.json').write_text(json.dumps(rep,indent=2));print(json.dumps(rep,indent=2),flush=True)
assert not invalid
assert not bad,bad
assert len(own)==12
assert require
