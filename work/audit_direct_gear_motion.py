import FreeCAD as A,Part,math,json
from FreeCAD import Vector as V
from pathlib import Path
from direct_gear_math import ROWS,linkage,angle
R=Path(__file__).resolve().parents[1];O=R/'outputs/LeLovophon_Direct_Gear_Prototype/Reality_Audit';O.mkdir(exist_ok=True);d=A.openDocument(str(R/'outputs/LeLovophon_Direct_Gear_Prototype/Axle_Clearance_Revision/LeLovophon_Direct_Gear_Prototype.FCStd'))
def world(o):
 s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return s
def overlap(a,b):
 return min(a.XMax,b.XMax)-max(a.XMin,b.XMin)>1e-7 and min(a.YMax,b.YMax)-max(a.YMin,b.YMin)>1e-7 and min(a.ZMax,b.ZMax)-max(a.ZMin,b.ZMin)>1e-7
moving_tags=['_Crank','_Rocker','_POMCoupler','_PinRetainingWasher','_PendulumHub','_TubeArm','_TipSocket','_PETPick','_DriverGear','_OutputGear']
fixed=[(o.Name,world(o)) for o in d.Objects if o.TypeId=='Part::Feature' and not any(t in o.Name for t in moving_tags) and o.Name not in ['HandInputWheel','HandleJournal','FreeTurningHandGrip']]
hits={};own_pick_contacts={};mins={};prefixes=['C','Cs','D','Eb','E','F','Fs','G','Ab','A','Bb','B']
for row,prefix in zip(ROWS,prefixes):
 n=f"V{row['index']:02d}";a0,b0,_=linkage(row,row['phase_rad']);r0=math.atan2(b0[1]-a0[1],b0[0]-a0[0]);parts=[(n+t,world(d.getObject(n+t))) for t in ['_PendulumHub','_TubeArm','_TipSocket','_PETPick','_POMCoupler']]
 for j in range(360):
  t=row['phase_rad']+j*2*math.pi/360;a,b,_=linkage(row,t)
  for name,base in parts:
   sh=base.copy()
   if name.endswith('_POMCoupler'):
    r=math.atan2(b[1]-a[1],b[0]-a[0]);sh.rotate(V(0,*a0),V(1,0,0),math.degrees(r-r0));sh.translate(V(0,a[0]-a0[0],a[1]-a0[1]))
   else:sh.rotate(V(0,*row['pivot_yz']),V(1,0,0),math.degrees(angle(row,t)))
   for fn,f in fixed:
    if not overlap(sh.BoundBox,f.BoundBox):continue
    vol=sh.common(f).Volume
    if vol<1e-5:continue
    intended=name.endswith('_PETPick') and fn==prefix+'_KotoSpeakingString'
    store=own_pick_contacts if intended else hits;key=(name,fn)
    if key not in store:store[key]=dict(voice=n,note=row['note'],moving=name,fixed=fn,first_phase_deg=j,poses_with_intersection=0,maximum_intersection_mm3=0)
    store[key]['poses_with_intersection']+=1;store[key]['maximum_intersection_mm3']=max(store[key]['maximum_intersection_mm3'],vol)
 print('MOTION',n,'unexpected pairs',len(hits),flush=True)
r=dict(poses_per_voice=360,scope='Pendulum hub, tube, socket, pick and POM connecting rod against every stationary solid plus invariant common/pivot shafts and bearing envelopes. Integral crank-shaft flanges remain excluded with the crank group. Gear tooth meshing, moving fastener-to-moving link contacts, flex, load and physical release remain outside this sweep. Each voice swept independently; other non-circular moving groups are omitted rather than frozen.',unexpected_intersection_pairs=list(hits.values()),intended_own_pick_string_contacts=list(own_pick_contacts.values()),physical_pass=False)
(O/'Motion_to_Stationary_Audit.json').write_text(json.dumps(r,indent=2));print('MOTION_COMPLETE',len(hits),flush=True)
