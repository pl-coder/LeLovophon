import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,math,json,ast
from FreeCAD import Vector as V
OUT=(_LOVOPHON_WORKSPACE + '/outputs');doc=App.openDocument(OUT+'/../work/Harpe_d_Amour_Shared_Gantry.FCStd')
oldrows={r['note']:r for r in json.loads(doc.Motion.LinkageGeometry)};C=oldrows['C'];baseR=C['radius']
# Remove the superseded clockwork and the six-voice gantry before rebuilding the shared support.
for group in ['SharedGantry','Clockwork']:
 root=doc.getObject(group)
 if root:
  def clear(g):
   for o in list(g.Group):
    if o.TypeId=='App::DocumentObjectGroup':clear(o)
    elif o.TypeId=='Part::Feature':doc.removeObject(o.Name)
   doc.removeObject(g.Name)
  clear(root)
code=ast.parse(open(OUT+'/Animate_Open_Harpe.FCMacro').read());exec(compile(ast.Module(body=[n for n in code.body if isinstance(n,ast.FunctionDef) and n.name in ['harpe_live_beta','harpe_live_roots']],type_ignores=[]),'motion','exec'))
code=ast.parse(open(OUT+'/../work/build_wide_swing.py').read());exec(compile(ast.Module(body=[n for n in code.body if isinstance(n,ast.FunctionDef) and n.name=='wire'],type_ignores=[]),'belt','exec'))
def bx(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def cy(r,h,p,axis=V(1,0,0)):return Part.makeCylinder(r,h,p,axis)
def rod(p,q,r=.4):v=q-p;return cy(r,v.Length,p,v)
def tri(pts,depth):return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,depth))
def put(name,shape,parent,label=None):
 o=doc.getObject(name) or doc.addObject('Part::Feature',name);o.Shape=shape;parent.addObject(o)
 if label:o.Label=label
 return o
scale=[('C','C',1,40,40),('Cs','C♯',16/15,32,30),('D','D',9/8,36,32),('Eb','E♭',6/5,36,30),('E','E',5/4,40,32),('F','F',4/3,32,24),('Fs','F♯',45/32,45,32),('G','G',3/2,36,24),('Ab','A♭',8/5,40,25),('A','A',5/3,40,24),('Bb','B♭',9/5,36,20),('B','B',15/8,45,24)]
# Clone only local geometry and containers for the extra voices, then regenerate all ratio-dependent shapes.
for n,label,ratio,nt,dt in scale:
 if n in oldrows:continue
 for kind in ['Driver','Output','LongArmRotor','Rocker']:
  src=doc.getObject('C_'+kind);g=doc.addObject('App::Part',n+'_'+kind);g.Label=label+' '+kind
  for child in src.Group:
   if child.TypeId=='Part::Feature':put(n+child.Name[1:],child.Shape.copy(),g)
  if kind=='LongArmRotor':g.addProperty('App::PropertyLength','ContactRadius','Geometry')
  if kind=='Output':g.addProperty('App::PropertyFloat','SpeedRatio','Timing')
 g=doc.addObject('App::DocumentObjectGroup',n+'_KotoStringModule');doc.FlatKotoStrings.addObject(g)
 for child in doc.C_KotoStringModule.Group:
  if child.TypeId=='Part::Feature':put(n+child.Name[1:],child.Shape.copy(),g)
 for suffix in ['_PendulumBearing0','_PendulumBearing1','_FollowerPivotBearing0','_FollowerPivotBearing1']:
  put(n+suffix,doc.getObject('C'+suffix).Shape.copy(),doc.Structure)
 # External string fittings are repeated at the established 10 mm lane pitch.
 for child in list(doc.NylonEndTensioners.Group):
  if child.TypeId=='Part::Feature' and child.Name.startswith('C_'):put(n+child.Name[1:],child.Shape.copy(),doc.NylonEndTensioners)
 for child in list(doc.KotoEndSupports.Group):
  if child.TypeId=='Part::Feature' and child.Name.startswith('C_'):put(n+child.Name[1:],child.Shape.copy(),doc.KotoEndSupports)
rows=[];sfirst=6.35
for i,(n,label,ratio,nt,dt) in enumerate(scale):
 s=sfirst+24*i;z=-80+10*i;R=baseR/ratio;uy=-91+R;fy=uy+18;fz=z-30;L=330/ratio;left=320-L
 r=dict(oldrows.get(n,C));r.update(note=n,display_note=label,station=s,pivot_y=uy,pivot_z=z,radius=R,ratio=ratio,speaking_length=L,follower_y=fy,follower_z=fz,swing_gain=4,driver_teeth=nt,driven_teeth=dt)
 D=(V(0,fy,fz)-V(0,-59,-116)).Length;r['lever_length']=D
 vals=[harpe_live_beta(r,math.radians(j*.5)) for j in range(720)];ref=vals[0];vals=[ref+math.atan2(math.sin(b-ref),math.cos(b-ref)) for b in vals];r['beta_mid']=(max(vals)+min(vals))/2;r['swing_half_angle_deg']=4*math.degrees((max(vals)-min(vals))/2)
 doc.getObject(n+'_LongArmRotor').ContactRadius=R
 if 'SpeedRatio' in doc.getObject(n+'_Output').PropertiesList:doc.getObject(n+'_Output').SpeedRatio=ratio
 for kind in ['Driver','Output','LongArmRotor','Rocker']:
  g=doc.getObject(n+'_'+kind);g.setExpression('Placement.Rotation.Angle',None);g.Label=label+' — '+kind
 put(n+'_RatioDrivePulley',cy(nt/math.pi,5,V(0,0,0)).cut(cy(3.05,7,V(-1,0,0))),doc.getObject(n+'_Driver'),label+' timing drive — '+str(nt)+' teeth reference')
 put(n+'_RatioDrivenPulley',cy(dt/math.pi,5,V(0,0,0)).cut(cy(5.05,7,V(-1,0,0))),doc.getObject(n+'_Output'),label+' timing driven — '+str(dt)+' teeth reference')
 arm=bx(3,4,R-.5,12,-2,0).fuse(cy(6,3,V(12,0,0))).cut(cy(3.05,5,V(11,0,0)))
 doc.getObject(n+'_ExtendedArm').Shape=arm;doc.getObject(n+'_ExtendedPick').Shape=bx(3.3,.5,.9,15,-.25,R-.8)
 doc.getObject(n+'_FollowerLever').Shape=bx(2.5,4,D,8.75,-2,0).fuse(cy(6,2.5,V(8.75,0,0))).fuse(cy(4,2.5,V(8.75,0,D))).cut(cy(3.05,4.5,V(7.75,0,0)))
 doc.getObject(n+'_FollowerRoller').Shape=cy(3,3,V(5.25,0,D)).cut(cy(1.05,5,V(4.25,0,D)));doc.getObject(n+'_RollerPin').Shape=cy(1,6,V(5.25,0,D))
 for j,off in enumerate([-5.5,0]):
  for kind,y,zz in [('Pendulum',uy,z),('FollowerPivot',fy,fz)]:put(n+'_'+kind+'Bearing'+str(j),cy(6,4,V(s+off,y,zz)).cut(cy(3.1,6,V(s+off-1,y,zz))),doc.Structure)
 A=V(s,-83,-131);B=V(s,-59,-116);ra=nt/math.pi;rb=dt/math.pi
 belt=Part.Face(wire(A,B,ra+.8,rb+.8)).cut(Part.Face(wire(A,B,ra+.1,rb+.1))).extrude(V(5,0,0));put(n+'_RatioBelt',belt,doc.RatioBeltDrives)
 A=V(s+5.25,fy,fz);B=V(s+5.25,uy,z);ra=64/math.pi;rb=16/math.pi
 belt=Part.Face(wire(A,B,ra+.8,rb+.8)).cut(Part.Face(wire(A,B,ra+.1,rb+.1))).extrude(V(3,0,0));put(n+'_SwingStepUpBelt',belt,doc.RatioBeltDrives)
 st=doc.getObject(n+'_KotoSpeakingString');st.Shape=rod(V(left,-91,z),V(320,-91,z));doc.getObject(n+'_KotoBackString').Shape=rod(V(-22,-91,z),V(left,-91,z))
 for prop,kind,val in [('SpeakingLength','App::PropertyLength',L),('EqualEndSpan','App::PropertyLength',342),('StringMaterial','App::PropertyString','Unwound nylon, nominal 0.8 mm model diameter; final gauge and tension pending'),('NominalDiameter','App::PropertyLength',.8),('SoundboardClearance','App::PropertyLength',18)]:
  if prop not in st.PropertiesList:st.addProperty(kind,prop,'String design')
  setattr(st,prop,val)
 bridge=tri([V(left-6,-109,z-3),V(left,-91.6,z-3),V(left+6,-109,z-3)],6);window=tri([V(left-2.8,-106,z-4),V(left,-97,z-4),V(left+2.8,-106,z-4)],8)
 doc.getObject(n+'_KotoThirdBridge').Shape=bridge.cut(window);doc.getObject(n+'_NylonBridgeCrown').Shape=cy(.65,6,V(left,-92.05,z-3),V(0,0,1))
 # The repeated end fittings contain no longitudinal changes: only their lane moves.
 oldz=oldrows[n]['pivot_z'] if n in oldrows else C['pivot_z']
 for parent in [doc.NylonEndTensioners,doc.KotoEndSupports]:
  for o in parent.Group:
   if o.TypeId=='Part::Feature' and o.Name.startswith(n+'_'):
    sh=o.Shape.copy();sh.translate(V(0,0,z-oldz));o.Shape=sh
 for kind,p in harpe_live_roots(r,0).items():doc.getObject(n+'_'+kind).Placement=p
 rows.append(r);print('Built',label,round(ratio,6),'swing +/-',round(r['swing_half_angle_deg'],1),flush=True)
# Extend the shared end fittings, shallow box and drive bed within the existing body length.
for tag,x in [('Anchor',-22),('Tuner',320)]:
 doc.getObject('Koto'+tag+'Block').Shape=bx(16,16.4,136,x-8,-109,-93)
 doc.getObject('Koto'+tag+'SaddleRail').Shape=bx(4,1.2,130,x-2,-92.6,-90)
for n,x,w in [('NylonRightGuidePedestal',330,10),('NylonLeftGuidePedestal',-30,8)]:doc.getObject(n).Shape=bx(w,12,130,x,-109,-90)
plate=bx(4,41,132,340,-153,-90).fuse(bx(16,4,132,340,-153,-90))
for r in rows:
 z=r['pivot_z'];plate=plate.cut(bx(6,27,4,339,-145,z-2)).cut(cy(2.2,6,V(351,-154,z),V(0,1,0)))
for y in [-119,-145]:
 for z in [-87,39]:plate=plate.cut(cy(2.2,6,V(339,y,z)))
doc.NylonTensionerEndPlate.Shape=plate
plate=bx(4,31,132,-38,-143,-90)
for r in rows:plate=plate.cut(cy(1.1,6,V(-39,-130,r['pivot_z'])))
for y in [-119,-139]:
 for z in [-87,39]:plate=plate.cut(cy(2.2,6,V(-39,y,z))).fuse(cy(3,4,V(-34,y,z)).cut(cy(2.2,6,V(-35,y,z))))
doc.NylonAnchorEndPlate.Shape=plate
for right in [False,True]:
 block=doc.getObject('SoundboxEndBlock'+('1' if right else '0'));bs=block.Shape.copy();ss=doc.SoundboxShell.Shape.copy()
 for y in ([-119,-145] if right else [-119,-139]):
  for z in [-87,39]:hole=cy(2.2,21 if right else 31,V(325 if right else -39,y,z));bs=bs.cut(hole);ss=ss.cut(hole)
 block.Shape=bs;doc.SoundboxShell.Shape=ss
last=rows[-1]['station'];doc.CommonInputShaft_D6.Shape=cy(3,last-sfirst+54,V(sfirst-22,-83,-131));doc.CommonIntermediateAxle.Shape=cy(3,last-sfirst+48,V(sfirst-26,-59,-116))
for j,s in enumerate([sfirst,last+7]):
 for n,start in [('LowInputStand',-17),('LowInputBearing',-16),('IntermediateAxleStand',-25)]:
  o=doc.getObject(n+str(j));sh=o.Shape.copy();target=sfirst-17 if n=='LowInputStand' and j==0 else last+14 if n=='LowInputStand' else sfirst-16 if n=='LowInputBearing' and j==0 else last+15 if n=='LowInputBearing' else sfirst-25 if j==0 else last+14
  sh.translate(V(target-sh.BoundBox.XMin,0,0));o.Shape=sh
tray=bx(last-sfirst+39,3,86,sfirst-20,-109,-154).fuse(bx(last-sfirst+39,6,3,sfirst-20,-106,-154)).fuse(bx(last-sfirst+39,6,3,sfirst-20,-106,-71));doc.LowGearboxTray.Shape=tray
# A compact direct-drive N20-style gearmotor with visible coupling and separate speed knob.
motor=doc.addObject('App::DocumentObjectGroup','ElectricDrive');motor.Label='N20-size electric drive — low-speed gearmotor and PWM speed knob';motorcolors={}
def mot(n,sh,label,col):o=put(n,sh,motor,label);motorcolors[n]=col;return o
mot('N20MotorCan',bx(16.6,10,12,318.9,-88,-137),'N20-size 6 V motor can — dimensional envelope',(.40,.43,.46))
mot('N20Gearbox',bx(12.5,10,12,306.4,-88,-137),'Low-speed metal gearbox — 10–15 rpm class',(.73,.58,.28))
mot('N20OutputShaft',cy(1.5,10,V(296.4,-83,-131)),'3 mm D-shaft envelope',(.55,.58,.60))
mot('ElectricShaftCoupling',cy(5,12,V(294.4,-83,-131)).cut(cy(3.05,7,V(293.4,-83,-131))).cut(cy(1.55,7,V(300.4,-83,-131))),'Removable stepped coupling, 6 mm harp axle / 3 mm motor shaft',(.42,.46,.48))
# Slotted bracket and base pads allow alignment; exact supplier face holes remain to be matched.
br=bx(3,26,22,304,-109,-142).cut(cy(2.1,5,V(303,-83,-131))).fuse(bx(34,3,26,304,-109,-144))
for x in [310,331]:br=br.cut(cy(1.7,5,V(x,-110,-140),V(0,1,0)))
mot('ElectricMotorBracket',br,'Removable motor bracket — supplier hole pattern and alignment pending',(.55,.59,.61))
mot('PWMSpeedBoard',bx(28,1.6,18,307,-103,-148),'PWM controller space reservation — 5–6 V compatible board to select',(.14,.40,.25))
mot('SpeedPotBody',bx(9,9,7,317,-102,-124),'Speed potentiometer envelope',(.22,.24,.25))
mot('SpeedPotShaft',cy(2,8,V(321.5,-97.5,-117),V(0,0,1)),'Speed-control spindle',(.55,.58,.60))
mot('SpeedControlKnob',cy(6,6,V(321.5,-97.5,-112),V(0,0,1)),'Turn to adjust tempo',(.21,.25,.27))
mot('ElectricRunSwitch',bx(7,4,8,329,-76,-148),'Run / stop switch — electrical rating pending',(.17,.23,.23))
mot('ElectricSupplyConnector',bx(7,5,8,328,-103,-156),'Low-voltage external supply connector envelope',(.22,.24,.25))
for n,sh in [('ElectricClearTop',bx(36,2,40,303,-74,-154)),('ElectricClearRear',bx(36,35,2,303,-109,-154)),('ElectricClearFront',bx(36,35,2,303,-109,-116).cut(cy(2.2,4,V(321.5,-97.5,-117),V(0,0,1))))]:mot(n,sh,'Clear motor / coupling cover',(.66,.84,.88))
motor.addProperty('App::PropertyString','SpecificationIntent','Design');motor.SpecificationIntent='Commodity N20-size 6 V low-speed brushed DC gearmotor, roughly 10–15 rpm no-load class, direct coupling and PWM tempo control. Dimensional reference: Pololu #1596, 13 rpm at 6 V. Generic motors vary; twelve-voice running/start torque, usable low-speed range and current limiting must be measured before supplier selection.'
motor.addProperty('App::PropertyString','ReferenceSource','Design');motor.ReferenceSource='https://www.pololu.com/product/1596/specs'
motor.addProperty('App::PropertyString','ElectricalIntent','Design');motor.ElectricalIntent='External regulated low-voltage supply; compatible PWM module with run/stop, current limit and wiring strain relief to select. No battery or mains wiring modelled. No closed-loop tempo regulation yet.'
doc.Motion.LinkageGeometry=json.dumps(rows);doc.Motion.Status='Twelve-note just-intonation nylon harp; N20-size electric drive replaces clockwork. Shared gantry to regenerate. Motor torque and electrical implementation unverified.'
doc.Label="L’Harpe d’Amour — twelve strings, electric drive"
doc.recompute();invalid=[o.Name for o in doc.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())];assert not invalid,invalid
doc.saveAs(OUT+'/../work/Harpe_d_Amour_Twelve_Motor_Base.FCStd')
json.dump(motorcolors,open(OUT+'/../work/motor_colors.json','w'));json.dump({'rows':rows,'ratios':[r['ratio'] for r in rows],'scale':'One 5-limit chromatic just-intonation choice: C C♯ D E♭ E F F♯ G A♭ A B♭ B. F♯ = 45/32. No octave duplicate.','motor':motor.SpecificationIntent,'invalid_shapes':invalid},open(OUT+'/twelve_motor_geometry.json','w'),indent=2)
print('Twelve-voice motor base saved',flush=True)
