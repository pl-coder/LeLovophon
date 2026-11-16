"""Continuous conservative sweep bounds at revised fixed mounts.

Saved moving BREP identities inherit the completed full-motion/gear baseline.
An axisymmetric containing solid contains every rigid rotation of its source.
The rod bound is the convex hull of circumscribed endpoint-motion disks:
Q radius 10+2 and P radius 14+2. Every capsule joining A and B is inside it.
Only envelope intersections fall back to actual 1-degree poses.
"""
import json,math,hashlib
import audit as a
from audit import A,Part,V,ROOT,ROWS,DRIVE,pose,bb_overlap
O=a.OUT;C=a.AUD;bp=ROOT/'work/rebuild_mechanical/clearance_baseline.FCStd';old=A.openDocument(str(bp))
def sha(sh):return hashlib.sha256(sh.exportBrepToString().encode()).hexdigest()
changed=[];unchanged=[];moving=[];identities=[]
for p in a.parts:
 before=sha(old.getObject(p['name']).Shape);after=sha(a.d.getObject(p['name']).Shape)
 if p['motion']!='Fixed':
  assert before==after,('Changed moving solid',p['name'])
  moving.append(p);identities.append(dict(name=p['name'],baseline_brep_sha256=before,current_brep_sha256=after,geometrically_identical=True))
 if before==after:unchanged.append(p['name'])
 else:changed.append(p)
print('IDENTITY',len(moving),len(changed),flush=True)
def cy(r,x0,x1,p):return Part.makeCylinder(r,x1-x0,V(x0,*p),V(1,0,0))
def hull(points):
 pts=sorted(set(points))
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[];hi=[]
 for p in pts:
  while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
  lo.append(p)
 for p in reversed(pts):
  while len(hi)>=2 and cross(hi[-2],hi[-1],p)<=0:hi.pop()
  hi.append(p)
 return lo[:-1]+hi[:-1]
def envelope(p,row):
 n=p['name'];s=row['station_x'];P=row['pivot_yz'];Q=row['crank_yz'];bb=p['bb'];x0=bb.XMin;x1=bb.XMax;mot=p['motion']
 if n.endswith('CrankShaftOnePiece'):
  return cy(1.5,s-13,s+2,Q).fuse(cy(2,s+1.2,s+2,Q)).fuse(cy(12,s+2,s+4,Q)),'piecewise circular shaft/flange superset'
 if n.endswith('RockerShaftOnePiece'):
  return cy(1.5,s-13,s+10,P).fuse(cy(2,s+1.2,s+2,P)).fuse(cy(17.5,s+2,s+4,P)),'shaft + full 14+3.5 mm lever disk'
 if mot=='Coupler':
  pts=[]
  for centre,r in [(Q,12),(P,16)]:
   r=r/math.cos(math.pi/64)+1e-6
   pts.extend([(centre[0]+r*math.cos(j*math.tau/64),centre[1]+r*math.sin(j*math.tau/64)) for j in range(64)])
  poly=[V(x0,*v) for v in hull(pts)];return Part.Face(Part.makePolygon(poly+[poly[0]])).extrude(V(x1-x0,0,0)),'convex hull of circumscribed Q12 / P16 disks'
 centre=DRIVE if mot=='Input' else Q if mot=='Crank' else P
 if 'CrankShoulderJournal' in n or 'CrankPinEndScrew' in n or 'CrankPinWasher' in n:
  r=10+(2.2 if 'Shoulder' in n else 2.8 if 'Washer' in n else 1.4)
 elif 'RockerShoulderJournal' in n or 'RockerPinEndScrew' in n or 'RockerPinWasher' in n:
  r=14+(2.2 if 'Shoulder' in n else 2.8 if 'Washer' in n else 1.4)
 else:r=math.hypot(max(abs(bb.YMin-centre[0]),abs(bb.YMax-centre[0])),max(abs(bb.ZMin-centre[1]),abs(bb.ZMax-centre[1])))
 return cy(r+1e-6,x0,x1,centre),'axisymmetric bound about motion axis'
containment=[];fallback=[];hits=[];pair_count=0
for row in ROWS:
 for p in [p for p in moving if p['voice']==row['index']]:
  env,method=envelope(p,row);outside=p['shape'].cut(env).Volume
  assert outside<1e-7,(p['name'],outside)
  containment.append(dict(name=p['name'],method=method,base_volume_outside_envelope_mm3=outside))
  bb=env.BoundBox
  for f in changed:
   if not bb_overlap(bb,f['bb']):continue
   pair_count+=1;v=env.common(f['shape']).Volume
   if v>1e-5:fallback.append((p,f))
 print('ENVELOPES',row['index'],'fallback pairs',len(fallback),flush=True)
for p,f in fallback:
 row=ROWS[p['voice']-1]
 for j in range(360):
  sh=pose(p,row,row['phase_rad']+math.tau*j/360)
  if not bb_overlap(sh.BoundBox,f['bb']):continue
  v=sh.common(f['shape']).Volume
  if v>1e-5:hits.append(dict(a=p['name'],b=f['name'],phase_deg=j,volume_mm3=v))
result=dict(cad_sha256=a.CAD_HASH,baseline_cad_sha256=hashlib.sha256(bp.read_bytes()).hexdigest(),all_moving_geometry_unchanged=True,moving_identity=identities,unchanged_part_names=unchanged,changed_fixed_part_names=[p['name'] for p in changed],continuous_envelope_containment=containment,envelope_fixed_pairs_tested=pair_count,conservative_envelope_overlap_pairs=[dict(a=p['name'],b=f['name']) for p,f in fallback],fallback_actual_poses_per_pair=360,unexpected=hits,intended_contacts=[],scope=__doc__,physical_test_passed=False)
(C/'Retainer_Refinement_Motion.json').write_text(json.dumps(result,indent=2));print('DELTA_ENVELOPES_DONE',len(hits),'fallback',len(fallback),flush=True)
