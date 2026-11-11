import sys,json,math,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import check as a
from check import A,Part,V,ROOT,OUT,ROWS,DRIVE,pose,bb_overlap
from fractions import Fraction
C=OUT/'Checks';old=A.openDocument(str(ROOT/'outputs/LeLovophon_Protokoto_R3/LeLovophon_Protokoto_R3.FCStd'))
def same_geometry(x,y):
 # The builder copies the saved station and applies only an X translation.
 # Verify reverse translation by topology, metric invariants and five samples per edge.
 if (len(x.Solids),len(x.Faces),len(x.Edges),len(x.Vertexes))!=(len(y.Solids),len(y.Faces),len(y.Edges),len(y.Vertexes)):return False
 if abs(x.Volume-y.Volume)>1e-5 or abs(x.Area-y.Area)>1e-5:return False
 def fingerprint(sh):
  def pt(v):return tuple(round(t,6) for t in (v.x,v.y,v.z))
  vertices=sorted(pt(v.Point) for v in sh.Vertexes)
  edges=[]
  for e in sh.Edges:
   points=[pt(e.valueAt(e.FirstParameter+(e.LastParameter-e.FirstParameter)*f)) for f in (0,.25,.5,.75,1)]
   try:curve=str(type(e.Curve))
   except TypeError:curve='DegenerateEdge'
   edges.append((curve,round(e.Length,6),min(tuple(points),tuple(reversed(points)))))
  faces=sorted((str(type(f.Surface)),round(f.Area,5),len(f.Wires),len(f.Edges)) for f in sh.Faces)
  return vertices,sorted(edges),faces
 return fingerprint(x)==fingerprint(y)
same=[];changed=[];new=[];translated=[]
from config import OLD_ROWS
localnames={ob.Name for i in range(1,13) for ob in old.getObject(f'V{i:02d}').Group}
for p in a.parts:
 prior=old.getObject(p['name'])
 if not prior:new.append(p);continue
 target=a.d.getObject(p['name']).Shape.copy()
 if p['name'] in localnames:
  row=ROWS[p['voice']-1];priorrow=OLD_ROWS[p['voice']-1];target.translate(V(priorrow['station_x']-row['station_x'],0,0))
  assert same_geometry(prior.Shape,target),p['name']
  translated.append(p['name'])
 elif same_geometry(prior.Shape,target):same.append(p['name'])
 else:changed.append(p)
assert not [p['name'] for p in changed+new if p['motion']!='Fixed' and p['name'] not in ['Common5mmInputShaft','InputPinnedCollar','CollarFlushPin','InputRearThrustShim']]
(C/'R3_Local_Geometry_Inheritance.json').write_text(json.dumps(dict(cad_sha256=a.CAD_HASH,source_sha256=hashlib.sha256((ROOT/'outputs/LeLovophon_Protokoto_R3/LeLovophon_Protokoto_R3.FCStd').read_bytes()).hexdigest(),local_kinematics_and_local_pairs_unchanged_after_pure_X_translation=True,geometry_check='Copy-and-translate construction; inverse translation verified by topology,volume,area,vertices,five parameter samples per curve edge and face surface types/areas. Coordinates rounded to1e-6mm. This is a numerical fingerprint, not a Boolean symmetric-difference proof.',translated_local_shapes=translated,unchanged_shapes=same,changed_other_shapes=[p['name'] for p in changed],new_parts=[p['name'] for p in new],scope='Exact local station geometry retained after inverse X translation. R3 local moving-pair evidence applies within each station; new fixed-world and neighbouring-station clearance checked separately.'),indent=2))
print('IDENTITY',len(same),'translated',len(translated),'changed',len(changed),'new',len(new),flush=True)
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

fixed=[p for p in a.parts if p['motion']=='Fixed'];fallback=[];hits=[];contain=[];mins=[];contacts=[]
for row in ROWS:
 for p in [p for p in a.parts if p['voice']==row['index'] and p['motion']!='Fixed']:
  e=env(p,row);outside=p['shape'].cut(e).Volume;assert outside<1e-6,(p['name'],outside)
  for f in fixed:
   if f['name'] in localnames and f['voice']==row['index']:continue # Exact local relative shapes inherited.
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
 if worst>1e-5:
  rec=dict(moving=p['name'],fixed=f['name'],phase_deg=phase,volume_mm3=worst,reason=a.intended(p,f))
  (contacts if rec['reason'] else hits).append(rec)
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
  for f in changed+new:
   if f['name']==p['name']:continue
   if not bb_overlap(sh.BoundBox,f['bb']):continue
   travelpairs+=1;v=sh.common(f['shape']).Volume
   if v>1e-5:travel.append(dict(moving=p['name'],fixed=f['name'],offset_mm=dy,volume_mm3=v))
slabs=[]
for row in ROWS:
 bs=[p['bb'] for p in a.parts if p['voice']==row['index'] and p['motion']!='Fixed'];slabs.append(dict(voice=row['index'],xmin=min(b.XMin for b in bs),xmax=max(b.XMax for b in bs)))
gaps=[dict(a=x['voice'],b=y['voice'],gap_mm=y['xmin']-x['xmax']) for x,y in zip(slabs,slabs[1:])]
assert min(g['gap_mm'] for g in gaps)>0
report=dict(moving_station_x_slabs=slabs,neighbour_moving_slab_gaps=gaps,intended_contacts=contacts,cad_sha256=a.CAD_HASH,translated_local_moving_pairs_inherit_R3=True,changed_fixed_parts_count=len(fixed),voice_envelopes_contain_actual_shapes=True,continuous_disjoint_bounds_used=True,fallback_pairs=[dict(moving=p['name'],fixed=f['name']) for p,f in fallback],fallback_phase_samples_per_pair=360,shared_input_continuous_bounds=True,unexpected_motion_intersections=hits,tensioner_travel_mm=21.8,tensioner_samples=23,tensioner_candidates=travelpairs,unexpected_tensioner_intersections=travel,physical_test_passed=False,manufacturing_release=False,limits='Exact nominal solids. Conservative continuous envelopes; one-degree samples only for overlapping bounds. R3 local moving pairs unchanged after pure X translation; fixed-world pairs checked again. No flex, friction, torque, preload, wear, manufacturing tolerances or pick release test.')
(C/'R5_Motion_and_Tensioner_Clearance.json').write_text(json.dumps(report,indent=2));print('MOTION_DONE',len(hits),'travel',len(travel),flush=True)
