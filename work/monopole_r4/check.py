import sys,json,math,time,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'protokoto_r3'))
import FreeCAD as A,Part
from FreeCAD import Vector as V
from config import ROOT,ROWS,DRIVE,linkage,angle
OUT=ROOT/'outputs/LeLovophon_Monopole_R4'
AUD=OUT/'Checks';AUD.mkdir(exist_ok=True)
d=A.openDocument(str(OUT/'LeLovophon_Monopole_R4.FCStd'))
CAD_HASH=hashlib.sha256((OUT/'LeLovophon_Monopole_R4.FCStd').read_bytes()).hexdigest()
parts=[dict(name=o.Name,shape=o.Shape.copy(),motion=o.Motion,voice=o.Voice,role=o.Role) for o in d.Objects if o.TypeId=='Part::Feature']
def bb_overlap(a,b):return all(min(getattr(a,k+'Max'),getattr(b,k+'Max'))-max(getattr(a,k+'Min'),getattr(b,k+'Min'))>1e-7 for k in ['X','Y','Z'])
def volume(a,b):return a.common(b).Volume if bb_overlap(a.BoundBox,b.BoundBox) else 0.
for p in parts:p['bb']=p['shape'].BoundBox
def intended(a,b):
 # Only the nylon tied inside its own stopper knots, and intended pick/string contact.
 if a['voice'] and a['voice']==b['voice']:
  if set([a['role'],b['role']])==set(['String','Knot']):return 'tied nylon / stopper-knot envelope'
  if set([a['role'],b['role']])==set(['String','Pick']):return 'flexible pick contact — physical release unproved'
 return None
def static():
 hits=[];contacts=[];candidates=0
 for i,a in enumerate(parts):
  for b in parts[i+1:]:
   if not bb_overlap(a['bb'],b['bb']):continue
   candidates+=1;v=volume(a['shape'],b['shape'])
   if v<1e-5:continue
   rec=dict(a=a['name'],b=b['name'],volume_mm3=v,reason=intended(a,b))
   (contacts if rec['reason'] else hits).append(rec)
  if i%100==0:
   print('STATIC',i,len(hits),flush=True);(AUD/'Static_Progress.json').write_text(json.dumps(dict(parts_checked=i,unexpected=hits),indent=2))
 res=dict(cad_sha256=CAD_HASH,parts=len(parts),pair_count=len(parts)*(len(parts)-1)//2,bbox_candidates=candidates,unexpected=hits,intended_contacts=contacts)
 (AUD/'Static_All_Pairs.json').write_text(json.dumps(res,indent=2));print('STATIC_DONE',len(hits),flush=True)
def pose(p,row,t):
 sh=p['shape'].copy();delta=t-row['phase_rad'];mot=p['motion']
 if mot=='Input':sh.rotate(V(0,*DRIVE),V(1,0,0),-math.degrees(delta)/float(row['ratio'].split('/')[0] if '/' not in row['ratio'] else __import__('fractions').Fraction(row['ratio'])))
 elif mot=='Crank':sh.rotate(V(0,*row['crank_yz']),V(1,0,0),math.degrees(delta))
 elif mot in ['Rocker','Pendulum']:sh.rotate(V(0,*row['pivot_yz']),V(1,0,0),math.degrees(angle(row,t)))
 elif mot=='Coupler':
  a0,b0,_=linkage(row,row['phase_rad']);a,b,_=linkage(row,t)
  th0=math.atan2(b0[1]-a0[1],b0[0]-a0[0]);th=math.atan2(b[1]-a[1],b[0]-a[0]);sh.rotate(V(0,*a0),V(1,0,0),math.degrees(th-th0));sh.translate(V(0,a[0]-a0[0],a[1]-a0[1]))
 return sh
def motion():
 start=int(sys.argv[2]) if len(sys.argv)>2 else 1;end=int(sys.argv[3]) if len(sys.argv)>3 else 12
 suffix=f'_{start:02d}_{end:02d}' if len(sys.argv)>2 else ''
 fixed_all=[p for p in parts if p['motion']=='Fixed'];hits={};contacts={};COUNT=360
 for row in ROWS[start-1:end]:
  voice=row['index'];moving=[p for p in parts if p['voice']==voice and p['motion']!='Fixed']
  lo=min(p['bb'].XMin for p in moving);hi=max(p['bb'].XMax for p in moving)
  fixed=[p for p in fixed_all if p['bb'].XMin<hi and p['bb'].XMax>lo]
  # Common shaft is circular and its cross holes can only increase clearance; use full envelope.
  invariant=[dict(name='COMMON_SHAFT_ENVELOPE',shape=Part.makeCylinder(2.5,613,V(-232,*DRIVE),V(1,0,0)),motion='Input',voice=0,role='InputShaft')]
  for p in invariant:p['bb']=p['shape'].BoundBox
  for j in range(COUNT):
   t=row['phase_rad']+2*math.pi*j/COUNT;poses=[dict(p,shape=pose(p,row,t)) for p in moving if p['role']!='Gear' or j%5==0]
   for p in poses:p['bb']=p['shape'].BoundBox
   for a in poses:
    # Gear mesh is checked below at every fifth degree; all other pairs every degree.
    if a['role']=='Gear' and j%5:continue
    for b in fixed+invariant:
     if b['name']=='COMMON_SHAFT_ENVELOPE' and a['role']=='DrivePin' and a['motion']=='Input':continue
     if not bb_overlap(a['bb'],b['bb']):continue
     v=a['shape'].common(b['shape']).Volume
     if v<1e-5:continue
     key=(a['name'],b['name']);reason=intended(a,b);target=contacts if reason else hits
     if key not in target:target[key]=dict(a=key[0],b=key[1],first_phase_deg=j,poses=0,max_volume_mm3=0,reason=reason)
     target[key]['poses']+=1;target[key]['max_volume_mm3']=max(target[key]['max_volume_mm3'],v)
   # ALL independently moving local groups; linked-group relative geometry is invariant.
   for ia,a in enumerate(poses):
    for b in poses[ia+1:]:
     if a['role']=='Gear' and b['role']=='Gear':continue
     if a['motion']==b['motion'] or (a['motion'] in ['Rocker','Pendulum'] and b['motion'] in ['Rocker','Pendulum']):continue
     if (a['role']=='Gear' or b['role']=='Gear') and j%5:continue
     if not bb_overlap(a['bb'],b['bb']):continue
     v=a['shape'].common(b['shape']).Volume
     if v<1e-5:continue
     key=(a['name'],b['name']);reason=intended(a,b);target=contacts if reason else hits
     if key not in target:target[key]=dict(a=key[0],b=key[1],first_phase_deg=j,poses=0,max_volume_mm3=0,reason=reason)
     target[key]['poses']+=1;target[key]['max_volume_mm3']=max(target[key]['max_volume_mm3'],v)
   if j%90==0:print('MOTION',voice,j,'hits',len(hits),flush=True)
  # Every possible relative tooth phase, rather than repeated coarse crank phases.
  gears=[p for p in moving if p['role']=='Gear'];ga=next(p for p in gears if p['motion']=='Input');gb=next(p for p in gears if p['motion']=='Crank')
  for k in range(64):
   t=row['phase_rad']+(2*math.pi/row['driven_teeth'])*k/64;v=volume(pose(ga,row,t),pose(gb,row,t))
   if v>1e-5:
    key=(ga['name'],gb['name'])
    if key not in hits:hits[key]=dict(a=key[0],b=key[1],first_tooth_phase_sample=k,poses=0,max_volume_mm3=0,reason=None)
    hits[key]['poses']+=1;hits[key]['max_volume_mm3']=max(hits[key]['max_volume_mm3'],v)
  (AUD/('Motion_Progress'+suffix+'.json')).write_text(json.dumps(dict(completed_voice=voice,unexpected=list(hits.values()),intended=list(contacts.values())),indent=2))
 # Shared input parts versus fixed assembly, independent full revolution.
 shared=[p for p in parts if p['voice']==0 and p['motion']=='Input'] if end==12 else []
 for j in range(360):
  for a in shared:
   sh=a['shape'].copy();sh.rotate(V(0,*DRIVE),V(1,0,0),j)
   for b in fixed_all:
    if not bb_overlap(sh.BoundBox,b['bb']):continue
    v=sh.common(b['shape']).Volume
    if v>1e-5:
     key=(a['name'],b['name'])
     if key not in hits:hits[key]=dict(a=key[0],b=key[1],first_phase_deg=j,poses=0,max_volume_mm3=0,reason=None)
     hits[key]['poses']+=1;hits[key]['max_volume_mm3']=max(hits[key]['max_volume_mm3'],v)
 # Every moving station's X envelope is phase invariant. Prove neighbour clearance independently of phase.
 slabs=[]
 for row in ROWS:
  vp=[p['shape'].BoundBox for p in parts if p['voice']==row['index'] and p['motion']!='Fixed'];slabs.append(dict(voice=row['index'],xmin=min(b.XMin for b in vp),xmax=max(b.XMax for b in vp)))
 gaps=[dict(a=a['voice'],b=b['voice'],gap_mm=b['xmin']-a['xmax']) for a,b in zip(slabs,slabs[1:])]
 result=dict(cad_sha256=CAD_HASH,poses_per_voice=COUNT,gear_pose_interval_deg=5,independent_tooth_phase_samples_per_pair=64,shared_input_poses=360 if end==12 else 0,checked_voices=list(range(start,end+1)),unexpected=list(hits.values()),intended_contacts=list(contacts.values()),moving_station_x_slabs=slabs,neighbour_moving_slab_gaps=gaps,scope='All moving parts versus all fixed solids; all independently moving local groups; gears sampled every 5 crank degrees, other motion every degree. Neighbouring moving stations have phase-independent axial separation. Nominal thread cores, no elastic deformation/contact forces or race internals. Rigid pick/string contact is intentional and needs flex/release bench test.',physical_test_passed=False)
 (AUD/('Motion_Audit'+suffix+'.json')).write_text(json.dumps(result,indent=2));print('MOTION_DONE',len(hits),'min slab gap',min(g['gap_mm'] for g in gaps),flush=True)

if __name__=="__main__":static()
