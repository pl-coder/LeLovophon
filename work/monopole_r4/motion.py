import sys,json,math,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import check as a
from check import A,Part,V,ROOT,OUT,ROWS,DRIVE,pose,bb_overlap
from fractions import Fraction
C=OUT/'Checks';old=A.openDocument(str(ROOT/'outputs/LeLovophon_Protokoto_R3/LeLovophon_Protokoto_R3.FCStd'))
def same_brep(x,y):
 if x==y:return True
 aa=x.split();bb=y.split()
 if len(aa)!=len(bb):return False
 for u,v in zip(aa,bb):
  if u==v:continue
  try:
   if abs(float(u)-float(v))>1e-10:return False
  except ValueError:return False
 return True
same=[];changed=[];new=[]
for p in a.parts:
 prior=old.getObject(p['name'])
 if not prior:new.append(p);continue
 if same_brep(prior.Shape.exportBrepToString(),a.d.getObject(p['name']).Shape.exportBrepToString()):same.append(p['name'])
 else:changed.append(p)
assert not [p['name'] for p in changed+new if p['motion']!='Fixed']
(C/'R3_Geometry_Inheritance.json').write_text(json.dumps(dict(cad_sha256=a.CAD_HASH,source_sha256=hashlib.sha256((ROOT/'outputs/LeLovophon_Protokoto_R3/LeLovophon_Protokoto_R3.FCStd').read_bytes()).hexdigest(),all_moving_shapes_unchanged=True,brep_roundtrip_tolerance=1e-10,unchanged_shapes=same,changed_existing_fixed_shapes=[p['name'] for p in changed],new_fixed_parts=[p['name'] for p in new],scope='Every moving part, string, bridge and all precision bearing carriers retained at their original coordinates. R3 kinematics/local moving-pair checks inherited; changed/new fixed shapes checked separately.'),indent=2))
print('IDENTITY',len(same),'changed',len(changed),'new',len(new),flush=True)
def cy(radius,x0,x1,centre):return Part.makeCylinder(radius,x1-x0,V(x0,*centre),V(1,0,0))
def hull(points):
 points=sorted(set(points))
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[];hi=[]
 for p in points:
  while len(lo)>1 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
  lo.append(p)
 for p in reversed(points):
  while len(hi)>1 and cross(hi[-2],hi[-1],p)<=0:hi.pop()
  hi.append(p)
 return lo[:-1]+hi[:-1]
def env(p,row):
 bb=p['bb'];x0,x1=bb.XMin,bb.XMax;s=row['station_x'];P=row['pivot_yz'];Q=row['crank_yz'];mot=p['motion'];n=p['name']
 if n.endswith('CrankShaftOnePiece'):return cy(1.5,s-13,s+2,Q).fuse(cy(2,s+1.2,s+2,Q)).fuse(cy(12,s+2,s+4,Q))
 if n.endswith('RockerShaftOnePiece'):return cy(1.5,s-13,s+10,P).fuse(cy(2,s+1.2,s+2,P)).fuse(cy(17.5,s+2,s+4,P))
 if mot=='Coupler':
  pts=[]
  for cp,rad in [(Q,13.75),(P,17.75)]:
   rad=rad/math.cos(math.pi/64)+1e-6;pts.extend([(cp[0]+rad*math.cos(j*math.tau/64),cp[1]+rad*math.sin(j*math.tau/64)) for j in range(64)])
  poly=[V(x0,*v) for v in hull(pts)];return Part.Face(Part.makePolygon(poly+[poly[0]])).extrude(V(x1-x0,0,0))
 cp=DRIVE if mot=='Input' else Q if mot=='Crank' else P
 radius=math.hypot(max(abs(bb.YMin-cp[0]),abs(bb.YMax-cp[0])),max(abs(bb.ZMin-cp[1]),abs(bb.ZMax-cp[1])))+1e-6
 return cy(radius,x0,x1,cp)

fixed=changed+new;fallback=[];hits=[];contain=[];mins=[]
for row in ROWS:
 for p in [p for p in a.parts if p['voice']==row['index'] and p['motion']!='Fixed']:
  e=env(p,row);outside=p['shape'].cut(e).Volume;assert outside<1e-6,(p['name'],outside)
  for f in fixed:
   if not bb_overlap(e.BoundBox,f['bb']):continue
   v=e.common(f['shape']).Volume
   if v>1e-5:fallback.append((p,f))
 print('CONTINUOUS_ENVELOPES',row['index'],len(fallback),flush=True)
for idx,(p,f) in enumerate(fallback):
 row=ROWS[p['voice']-1];worst=0;phase=None;minclear=1e9
 for j in range(360):
  sh=pose(p,row,row['phase_rad']+math.tau*j/360)
  if not bb_overlap(sh.BoundBox,f['bb']):continue
  v=sh.common(f['shape']).Volume
  if v>worst:worst=v;phase=j
  if v>1e-5:break
 if worst>1e-5:hits.append(dict(moving=p['name'],fixed=f['name'],phase_deg=phase,volume_mm3=worst))
 if idx%10==0:print('SAMPLED_PAIR',idx,len(fallback),'hits',len(hits),flush=True)
shared=[p for p in a.parts if not p['voice'] and p['motion']=='Input']
for p in shared:
 bb=p['bb'];n=p['name'];x0,x1=bb.XMin,bb.XMax
 if n=='Common5mmInputShaft':e=cy(2.5,x0,x1,DRIVE)
 elif n.startswith('InputPinnedCollar'):e=cy(4,x0,x1,DRIVE).cut(cy(2.52,x0-1,x1+1,DRIVE))
 elif n.startswith('InputRearThrust') or n.startswith('InputFrontThrust'):e=cy(2.95,x0,x1,DRIVE).cut(cy(2.55,x0-1,x1+1,DRIVE))
 elif n=='HandCrank32mm':e=cy(7,373,381,DRIVE).cut(cy(2.52,372,382,DRIVE)).fuse(cy(37,381,384,DRIVE))
 else:
  rad=math.hypot(max(abs(bb.YMin-65),abs(bb.YMax-65)),max(abs(bb.ZMin+25),abs(bb.ZMax+25)))+1e-6;e=cy(rad,x0,x1,DRIVE)
 assert p['shape'].cut(e).Volume<1e-6,n
 for f in fixed:
  if bb_overlap(e.BoundBox,f['bb']):
   vol=e.common(f['shape']).Volume
   if vol>1e-5:hits.append(dict(moving=n,fixed=f['name'],continuous_volume_mm3=vol))
travel=[];travelpairs=0
for p in [p for p in a.parts if p['role']=='Carriage' or 'CapturedM4Nut' in p['name'] or 'TunerStopperKnot' in p['name']]:
 for k in range(23):
  dy=-3+21.8*k/22;sh=p['shape'].copy();sh.translate(V(0,dy,0))
  for f in fixed:
   if not bb_overlap(sh.BoundBox,f['bb']):continue
   travelpairs+=1;v=sh.common(f['shape']).Volume
   if v>1e-5:travel.append(dict(moving=p['name'],fixed=f['name'],offset_mm=dy,volume_mm3=v))
report=dict(cad_sha256=a.CAD_HASH,unchanged_moving_geometry_inherits_R3=True,changed_fixed_parts_count=len(fixed),voice_envelopes_contain_actual_shapes=True,continuous_disjoint_bounds_used=True,fallback_pairs=[dict(moving=p['name'],fixed=f['name']) for p,f in fallback],fallback_phase_samples_per_pair=360,shared_input_continuous_bounds=True,unexpected_motion_intersections=hits,tensioner_travel_mm=21.8,tensioner_samples=23,tensioner_candidates=travelpairs,unexpected_tensioner_intersections=travel,physical_test_passed=False,manufacturing_release=False,limits='Exact nominal solids. Conservative continuous envelopes; one-degree samples only for overlapping bounds. R3 local moving pairs unchanged. No flex, friction, torque, preload, wear, manufacturing tolerances or pick release test.')
(C/'R4_Motion_and_Tensioner_Clearance.json').write_text(json.dumps(report,indent=2));print('MOTION_DONE',len(hits),'travel',len(travel),flush=True)
