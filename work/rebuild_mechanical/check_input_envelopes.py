"""Continuous clearance of the shared input by axisymmetric supersets.
Each superset must first contain its actual solid. Holes only remove material.
This proves clearance for all rotation angles, rather than sampling them.
"""
import json,math
import audit as a
from audit import Part,V,DRIVE
def cylinder(r,h,x):return Part.makeCylinder(r,h,V(x,*DRIVE),V(1,0,0))
def ring(ro,ri,h,x):return cylinder(ro,h,x).cut(cylinder(ri,h+2,x-1))
env={
 'Common5mmInputShaft':cylinder(2.5,327,3),
 'HandInputWheelWithHub':ring(25,2.52,4,330).fuse(ring(5,2.52,4,326)).fuse(ring(3.5,2.52,1.8,324.2)),
 'HandWheelFlushPin':cylinder(math.hypot(4.8,.49),.98,327.01),
 'InputRearPinnedCollar':ring(4,2.52,3,12.7),
 'InputRearCollarFlushPin':cylinder(math.hypot(3.8,.49),.98,13.71),
 'InputRearThrustShim':ring(2.95,2.55,.3,15.7),
 'InputFrontThrustShim':ring(2.95,2.55,.2,324),
}
fixed=[p for p in a.parts if p['motion']=='Fixed'];hits=[];contain=[]
for name,sh in env.items():
 part=next(p for p in a.parts if p['name']==name);outside=part['shape'].cut(sh).Volume
 assert outside<1e-7,(name,outside)
 contain.append(dict(name=name,actual_volume_outside_envelope_mm3=outside))
 bb=sh.BoundBox
 for f in fixed:
  if not a.bb_overlap(bb,f['bb']):continue
  v=sh.common(f['shape']).Volume
  if v>1e-5:hits.append(dict(moving=name,fixed=f['name'],volume_mm3=v))
 print('INPUT_ENVELOPE',name,'hits',len(hits),flush=True)
r=dict(cad_sha256=a.CAD_HASH,scope='Every shared-input solid contained in an exactly axisymmetric envelope about the common shaft. Envelopes checked against all fixed solids. This covers every input angle continuously; interfaces between co-rotating shared parts inherit final static checks. Per-voice gears/pins have separate full motion checks.',containment=contain,unexpected=hits,all_angles_covered=True,physical_test_passed=False)
(a.AUD/'Shared_Input_Continuous_Clearance.json').write_text(json.dumps(r,indent=2));print('INPUT_DONE',len(hits),flush=True)
