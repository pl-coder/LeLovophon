import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as A,Part,math,json,sys
from FreeCAD import Vector as V
from pathlib import Path
from unified_design import *
from unified_sprocket_webs import open_web
ROOT=Path((_LOVOPHON_WORKSPACE + ''));O=ROOT/'outputs';src=A.openDocument(str(O/'Lovophone_Hardware_Frame.FCStd'));d=A.newDocument('LovophoneUnified');d.Label='Le Lovophone — unified 160-minute picking wheels'
colors={};groups={};new=[];mechanism_rows=rows();music=json.loads((O/'Lovophone_Unified_Music.json').read_text())
def group(n,label):g=d.addObject('App::DocumentObjectGroup',n);g.Label=label;groups[n]=g;return g
wood=group('Soundbox','Centred timber soundbox');strings=group('Strings','Twelve just-pentatonic nylon strings');frame=group('Frame','Open triangular laboratory support');drive=group('Transmission','Twelve exact-ratio miniature chain drives');hardware=group('Hardware','Single-key fasteners and bearing supports')
def cy(r,h,p=V(),axis=V(0,0,1)):return Part.makeCylinder(r,h,p,axis)
def bx(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def world(o):s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return s

def put(n,sh,g,label=None,col=(.7,.73,.76)):
 o=d.addObject('Part::Feature',n);o.Shape=sh;o.Label=label or n;g.addObject(o);colors[n]=col;return o

def copy(o,g,dz=0):s=world(o);s.translate(V(0,0,dz));return put(o.Name,s,g,o.Label)
def tube(p,q,r=3,ri=2):v=q-p;return cy(r,v.Length,p,v).cut(cy(ri,v.Length+2,p-v/v.Length,v))
def rod(p,q,r):v=q-p;return cy(r,v.Length,p,v)
def hexcut(p,axis,h,af=2.5):
 # Axial sockets share a 2.5 mm Allen key.
 axis=V(axis);axis.normalize();u=axis.cross(V(0,0,1))
 if u.Length<.1:u=axis.cross(V(0,1,0))
 u.normalize();v=axis.cross(u);rr=af/math.sqrt(3);pts=[p+rr*(math.cos(k*math.pi/3)*u+math.sin(k*math.pi/3)*v) for k in range(6)]
 return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(axis*h)
def screw(n,p,axis,length,g=hardware):
 axis=V(axis);axis.normalize();sh=cy(1.5,length,p-axis*length,axis).fuse(cy(2.75,3,p,axis));sh=sh.cut(hexcut(p+axis*1.1,axis,2.1));o=put(n,sh,g,'M3 socket cap — 2.5 mm Allen key');o.addProperty('App::PropertyLength','AllenKeyAF','Adjustment');o.AllenKeyAF=2.5;return o
# Fresh narrow soundbox, retaining the existing 330 mm longest speaking length.
put('SoundboxShell',bx(370,45,170,-30,-157,-110).cut(bx(358,42,158,-24,-154,-104)),wood,'170 mm soundbox centred beneath string bank',(.43,.24,.11))
lid=bx(370,3,170,-30,-112,-110)
for j,x in enumerate([-24,326]):put('SoundboxEndBlock'+str(j),bx(14,41,158,x,-153,-104),wood,'Common string-load end block',(.48,.29,.14))
for j,x in enumerate([66.35,214.35]):put('SoundboxMountRib'+str(j),bx(6,41,158,x,-153,-104),wood,'Soundboard mounting rib',(.48,.29,.14))
for j,(x,z) in enumerate([(-8,-94),(-8,44),(320,-94),(320,44)]):put('SoundboxFoot'+str(j),cy(7,6,V(x,-163,z),V(0,1,0)),wood,'Replaceable rubber foot',(.08,.09,.1))
# Copy the complete string paths and screw tensioners, with 12 mm lane spacing.
for tag,x in [('Anchor',-22),('Tuner',320)]:
 put('Koto'+tag+'Block',bx(16,16.4,158,x-8,-109,-104),strings,'Common load-bearing '+tag.lower()+' block',(.57,.37,.17))
 put('Koto'+tag+'SaddleRail',bx(4,1.2,154,x-2,-92.6,-102),strings,'Rounded common saddle support',(.75,.56,.24))
for side,x,w in [('Left',-30,8),('Right',330,10)]:put('Nylon'+side+'GuidePedestal',bx(w,12,154,x,-109,-102),strings,'Common over-edge guide pedestal',(.48,.29,.14))
# Tuner retaining plate extends to the new outer lanes.
plate=bx(4,41,156,340,-153,-103).fuse(bx(16,4,156,340,-153,-103))
for r in mechanism_rows:
 z=r['lane_z'];plate=plate.cut(bx(6,27,4,339,-145,z-2)).cut(cy(2.2,6,V(351,-154,z),V(0,1,0)))
for y in [-119,-145]:
 for z in [-100,50]:plate=plate.cut(cy(2.2,6,V(339,y,z),V(1,0,0)))
put('NylonTunerSupportPlate',plate,strings,'Common tuner end plate',(.7,.73,.76))
oldrows=json.loads(src.Motion.LinkageGeometry)
keep_suffixes=['_KotoSpeakingString','_KotoBackString','_KotoThirdBridge','_NylonBridgeCrown','_LeftNylonGuide','_LeftNylonOverEdge','_RightNylonGuide','_RightNylonOverEdge','_NylonTieShuttle','_NylonTensionScrew','_NylonTieKnotEnvelope','_AnchorNylonSaddle','_TunerNylonSaddle']
for r,old in zip(mechanism_rows,oldrows):
 n=old['note'];r['prefix']='V'+str(r['index']).zfill(2);z=r['lane_z'];dz=z-old['pivot_z'];r['source_prefix']=n
 for suf in keep_suffixes:
  so=src.getObject(n+suf)
  if so:
   o=copy(so,strings,dz);o.Label=r['note']+' — '+suf[1:].replace('_',' ')
   if suf=='_NylonTensionScrew':o.Shape=o.Shape.cut(hexcut(V(351,-157,z),V(0,1,0),2.7));o.Label=r['note']+' — M4 pull screw with 2.5 mm hex socket'
 # Clamp bridges through a short soundboard slot, preserving the exact crown position.
 b=d.getObject(n+'_KotoThirdBridge');b.Shape=b.Shape.fuse(bx(18,1.5,5,r['bridge_x']-6,-109,z-2.5));cx=r['bridge_x']+9
 b.Shape=b.Shape.cut(cy(1.7,10,V(cx,-114,z),V(0,1,0)))
 lid=lid.cut(bx(14,6,3.4,cx-7,-114,z-1.7))
 screw(r['prefix']+'_BridgeLock',V(cx,-107.5,z),V(0,1,0),8.5)
 nut=bx(6,3,6,cx-3,-115,z-3).cut(cy(1.25,5,V(cx,-116,z),V(0,1,0)))
 put(r['prefix']+'_BridgeSlidingNut',nut,hardware,'Captive sliding M3 nut — guide detail pending',(.73,.55,.25))
 # Extend the existing anchor relief to include the bridge foot.
 for nn in ['KotoAnchorBlock','KotoTunerBlock']:
  o=d.getObject(nn);o.Shape=o.Shape.cut(bx(19,19,6.8,r['bridge_x']-6.5,-109.4,z-3.4))
put('Baseplate',lid,wood,'Spruce soundboard — short bridge-adjustment slots',(.62,.42,.2))
# Two common axles, across the twelve parallel strings.
put('CommonInputShaft',cy(3,180,V(DRIVE_X,AXLE_Y,-113)),hardware,'6 mm common input shaft — target 0.15 rpm')
put('CommonFixedAxle',cy(3,170,V(PICK_X,AXLE_Y,-109)),hardware,'6 mm stationary picking-wheel axle')
# Triangulated end supports and one shared idler-carrier rail.
for j,z in enumerate([-104,54]):
 for k,x in enumerate([DRIVE_X,PICK_X]):
  put(f'FramePost{j}{k}',tube(V(x,-106,z),V(x,AXLE_Y,z)),frame,'6 × 1 mm removable aluminium post')
  foot=bx(14,3,8,x-7,-109,z-4)
  for dx in [-5,5]:foot=foot.cut(cy(1.7,8,V(x+dx,-112,z),V(0,1,0)));lid=lid.cut(cy(1.7,8,V(x+dx,-115,z),V(0,1,0)))
  put(f'FrameFoot{j}{k}',foot,frame,'Two-screw frame foot')
  for q,dx in enumerate([-5,5]):screw(f'FrameFootBolt{j}{k}{q}',V(x+dx,-106,z),V(0,1,0),10)
  put(f'FrameUpperStay{j}{k}',tube(V(x,AXLE_Y,z),V(230,5,z),2.5,1.5),frame,'5 × 1 mm aluminium triangular stay')
 put('FrameTie'+str(j),tube(V(DRIVE_X,-106,z),V(PICK_X,-106,z)),frame,'6 × 1 mm aluminium base tie')
 put('FrameDiagonal'+str(j),tube(V(DRIVE_X,-106,z),V(PICK_X,AXLE_Y,z),2,1),frame,'4 × 1 mm aluminium diagonal stay')
 put('FrameCrossbar'+str(j),tube(V(DRIVE_X,AXLE_Y,z),V(PICK_X,AXLE_Y,z)),frame,'6 × 1 mm removable axle crossbar')
 # Visible bearing blocks have standard M3 clamp screws, not inaccessible nuts.
 for k,x in enumerate([DRIVE_X,PICK_X]):
  block=bx(18,18,7,x-9,AXLE_Y-9,z-3.5);bore=6.05 if k==0 else 3.05
  block=block.cut(cy(bore,10,V(x,AXLE_Y,z-5)))
  put(f'AxleBlock{j}{k}',block,hardware,'Input bearing housing' if k==0 else 'Fixed axle split clamp',(.74,.56,.25))
  if k==0:put('InputBearing'+str(j),cy(6,4,V(x,AXLE_Y,z-2)).cut(cy(3.05,6,V(x,AXLE_Y,z-3))),hardware,'MR126 6 × 12 × 4 mm input bearing',(.17,.19,.21))
  screw(f'AxleBlockClamp{j}{k}',V(x,AXLE_Y+9,z),V(0,1,0),12)
put('SharedIdlerRail',tube(V(230,5,-104),V(230,5,60),4,3),frame,'8 × 1 mm shared idler-carrier rail')
# All toothed parts below are reference chain profiles, not manufacturing drawings.
def sprocket(teeth,z,bore):
 rp=pitch_radius(teeth);sh=cy(rp+.75,2,V(0,0,z)).cut(cy(bore,4,V(0,0,z-1)))
 cuts=[cy(1.2,4,V(rp*math.cos(k*2*math.pi/teeth),rp*math.sin(k*2*math.pi/teeth),z-1)) for k in range(teeth)]
 return open_web(sh.cut(Part.makeCompound(cuts)),rp,bore,z)
def capsule(p,q,r,z,h):
 dx,dy=q[0]-p[0],q[1]-p[1];D=math.hypot(dx,dy);u=V(dx/D,dy/D,0);v=V(-u.y,u.x,0);P=V(p[0],p[1],z);Q=V(q[0],q[1],z)
 w=Part.Wire([Part.makeLine(P+v*r,Q+v*r),Part.Arc(Q+v*r,Q+u*r,Q-v*r).toShape(),Part.makeLine(Q-v*r,P-v*r),Part.Arc(P-v*r,P-u*r,P+v*r).toShape()]);return Part.Face(w).extrude(V(0,0,h))
def rotor(n,label,p,angle):g=d.addObject('App::Part',n);g.Label=label;g.Placement=A.Placement(p,A.Rotation(V(0,0,1),angle));drive.addObject(g);return g
for r in mechanism_rows:
 n=r['prefix'];z=r['lane_z'];nt,dt=r['driver_teeth'],r['driven_teeth'];N,iy,path=chain_layout(nt,dt);r.update(chain_links_reference=N,idler_y=iy,chain_pitch_mm=PITCH,chain_path_length_mm=N*PITCH,chain_profile_scope='Smooth pitch-path and scalloped sprocket reference; real link engagement and tensioner setup pending')
 direct=r['index']==1;r['direct_input']=direct;r['pick_x']=DRIVE_X if direct else PICK_X
 if direct:r.update(chain_links_reference=0,chain_path_length_mm=0,idler_y=None)
 if not direct:
  driver=rotor(n+'_Driver',r['note']+' — common input sprocket',V(DRIVE_X,AXLE_Y,z),0)
  put(n+'_DriveSprocket',sprocket(nt,5.3,3.05),driver,f'{nt}-tooth input chain sprocket reference',(.65,.48,.2))
  put(n+'_DriveHub',cy(5,9.8,V(0,0,-.5)).cut(cy(3.05,12,V(0,0,-1.5))),driver,'6 mm input hub — key/retention detail pending')
  screw(n+'_DriveHubScrew',V(0,5,2),V(0,1,0),4,driver)
 wheel=rotor(n+'_Wheel',r['note']+' — identical 19/32 picking wheel',V(r['pick_x'],AXLE_Y,z),math.degrees(RELEASE_ANGLE))
 # One cut sheet part integrates all nineteen flexible picking fingers.
 sh=cy(26,1.2,V(0,0,-.6)).cut(cy(20,3,V(0,0,-1)))
 sh=sh.fuse(cy(12,1.2,V(0,0,-.6)).cut(cy(6.55,3,V(0,0,-1))))
 for k in range(3):
  spoke=bx(15,4,1.2,9,-2,-.6);spoke.rotate(V(),V(0,0,1),k*120);sh=sh.fuse(spoke)
 for slot in SLOTS:
  finger=bx(PICK_RADIUS-25.4,.7,1.2,25.4,-.35,-.6);finger.rotate(V(),V(0,0,1),slot*360/32);sh=sh.fuse(finger)
 for k in range(3):
  a=k*2*math.pi/3;sh=sh.cut(cy(1.7,4,V(8.7*math.cos(a),8.7*math.sin(a),-2)))
 put(n+'_PickWheel',sh,wheel,'One replaceable sheet wheel — nineteen integral flexible fingers',(.79,.76,.63))
 hub=cy(6.5,10,V(0,0,-2.5)).fuse(cy(11,1.5,V(0,0,-2.1))).cut(cy(3.1,14,V(0,0,-4)))
 if not direct:
  for zz in [-2.5,4.5]:hub=hub.cut(cy(5.05,3,V(0,0,zz)))
 for k in range(3):
  a=k*2*math.pi/3;xx,yy=8.7*math.cos(a),8.7*math.sin(a);hub=hub.cut(cy(1.25,4,V(xx,yy,-3)))
  screw(n+'_WheelBolt'+str(k),V(xx,yy,.6),V(0,0,1),4,wheel)
 put(n+'_WheelHub',hub,wheel,'Direct input wheel hub' if direct else 'Independent dual-bearing wheel cartridge',(.72,.53,.23))
 if direct:
  axis=V(.5,math.sqrt(3)/2,0);screw(n+'_DirectHubScrew',axis*6.5+V(0,0,4),axis,4,wheel)
 else:
  for k,zz in enumerate([-2.5,4.5]):put(n+'_WheelBearing'+str(k),cy(5,3,V(0,0,zz)).cut(cy(3.025,5,V(0,0,zz-1))),wheel,'MR106 6 × 10 × 3 mm bearing',(.16,.18,.2))
  put(n+'_DrivenSprocket',sprocket(dt,5.3,6.5),wheel,f'{dt}-tooth output sprocket — exact speed ratio {r["ratio_exact"]}',(.65,.48,.2))
  put(n+'_SprocketCollar',cy(7.8,1,V(0,0,7.3)).cut(cy(6.5,3,V(0,0,6))),wheel,'Sprocket retainer — key/retention detail pending')
  # A small free idler takes up the chain; it does not change the speed ratio.
  idler=rotor(n+'_Idler',r['note']+' — free 12-tooth chain tensioner',V(230,iy,z),0)
  put(n+'_IdlerSprocket',sprocket(12,5.3,1.55),idler,'12-tooth idler reference',(.65,.48,.2))
  screw(n+'_IdlerPin',V(230,iy,z+5.3),V(0,0,-1),8)
  nut=bx(6,6,2.4,227,iy-3,z+12).cut(cy(1.25,4,V(230,iy,z+11)))
  put(n+'_IdlerCaptiveNut',nut,hardware,'Captive M3 idler nut — anti-rotation guide detail pending',(.72,.53,.23))
  stem=bx(5,10-iy,3,227.5,iy-5,z+8.9).cut(capsule((230,iy-3),(230,iy+3),1.6,z+8.4,4.5))
  put(n+'_IdlerHanger',stem,frame,'Slotted idler hanger — 6 mm nominal tensioning travel')
  clamp=bx(12,12,8,224,-1,z+9.0).cut(cy(4.1,10,V(230,5,z+8.0)))
  put(n+'_IdlerClamp',clamp,frame,'M3 split idler-rail clamp',(.72,.53,.23));screw(n+'_IdlerClampScrew',V(230,11,z+12.4),V(0,1,0),8)
  # Roller/link display follows a closed pitch-length path. It is intentionally a reference chain model.
  pts=[route_point(path,k*PITCH) for k in range(N)];plates=[];rollers=[]
  for k,(p,q) in enumerate(zip(pts,pts[1:]+pts[:1])):
   for zz in [z+3.9,z+7.9]:plates.append(capsule(p,q,1.45,zz,.8))
   rollers.append(cy(1.1,3.2,V(p[0],p[1],z+4.7)))
  put(n+'_ChainPlates',Part.makeCompound(plates),drive,f'{N}-link chain reference — 3.75 mm nominal pitch',(.19,.21,.22))
  put(n+'_ChainRollers',Part.makeCompound(rollers),drive,'Miniature chain rollers — display envelope',(.53,.55,.58))
 print('Built',r['note'],'rotation=pitch',r['ratio_exact'],'chain',N,flush=True)
# Clamp-on removable input knob; a motor must drive this shaft at 0.15 rpm for a 160-minute cycle.
put('InputKnob',cy(8,5,V(DRIVE_X,AXLE_Y,55)).cut(cy(3.05,7,V(DRIVE_X,AXLE_Y,54))),hardware,'Input coupling/hand knob — motor selection pending',(.72,.53,.23));screw('InputKnobClamp',V(DRIVE_X,AXLE_Y+8,57.5),V(0,1,0),7)
d.Baseplate.Shape=lid
motion=d.addObject('App::FeaturePython','Motion');motion.addProperty('App::PropertyString','UnifiedGeometry','Design');motion.UnifiedGeometry=json.dumps(mechanism_rows);motion.addProperty('App::PropertyFloat','BasePeriodSeconds','Timing');motion.BasePeriodSeconds=400;motion.addProperty('App::PropertyFloat','FullCycleMinutes','Timing');motion.FullCycleMinutes=160;motion.addProperty('App::PropertyString','Status','Design');motion.Status='Unified pentatonic pitch and rotation. Two common axles, one direct wheel and eleven chain ratios, identical integral 19/32 picking wheels. Nominal geometric release timing only; chain engagement, joints, flexible pick action and motor torque remain prototype work.'
d.recompute();bad=[o.Name for o in d.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())];assert not bad,bad
bounds=A.BoundBox()
for o in d.Objects:
 if o.TypeId=='Part::Feature':bounds.add(world(o).BoundBox)
report=dict(rows=mechanism_rows,pattern_slots=SLOTS,slots=32,picks_per_wheel=19,base_period_seconds=400,full_repeat_seconds=9600,rotation_equals_pitch=True,rotation_matches_tuning=True,chain_pitch_reference_mm=PITCH,reference_sources=['https://shop.sdp-si.com/products/chains-sprockets/sprockets-roller-ladder/roller-chain.html'],string_lane_pitch_mm=12,number_of_chain_loops=11,number_of_main_axles=2,bearing_count=24,allen_key_af_mm=2.5,envelope_mm=[bounds.XLength,bounds.ZLength,bounds.YLength],invalid_shapes=bad,colors=colors,part_count=len([o for o in d.Objects if o.TypeId=='Part::Feature']),scope='Concept CAD and exact ideal wheel timing; not fabrication-ready. Scalloped tooth/chain display envelopes are not validated production chain engagement. Physical flexible-pick release, chain tensioner setup, captive nut guides, hub keys, clamp preloads and motor sizing are pending.')
(O/'Lovophone_Unified_Design.json').write_text(json.dumps(report,indent=2));d.saveAs(str(ROOT/'work/Lovophone_Unified_Base.FCStd'));print('ENVELOPE',report['envelope_mm'],'PARTS',report['part_count'],flush=True)
