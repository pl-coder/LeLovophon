import FreeCAD as A,FreeCADGui as G,Part,math,json,csv
from FreeCAD import Vector as V
from PySide import QtWidgets
from direct_gear_math import *
OUT=OUT/'Axle_Clearance_Revision'
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([]);G.showMainWindow();G.getMainWindow().hide();OUT.mkdir(exist_ok=True)
src=A.openDocument(str(ROOT/'outputs/LeLovophon_Slender_Bank/LeLovophon_Slender_Bank.FCStd'));d=A.newDocument('LeLovophonDirectGearPrototype');d.Label='Le Lovophon — complete direct-gear drive — prototype, bench test required'
groups={n:d.addObject('App::DocumentObjectGroup',n) for n in ['Soundbox','RearStructure','CommonDrive','VoiceMechanisms']}
steel=(.68,.72,.74);brass=(.65,.46,.18);teal=(.12,.42,.38);black=(.15,.17,.18)
def cyl(r,h,p,axis=V(1,0,0)):return Part.makeCylinder(r,h,p,axis)
def box(x,y,z,p):return Part.makeBox(x,y,z,p)
def bar(p,q,r):v=q-p;return cyl(r,v.Length,p,v)
def tube(p,q,ro=2,ri=1):v=q-p;u=v/v.Length;return bar(p,q,ro).cut(cyl(ri,v.Length+2,p-u,v))
def add(n,sh,g,col=steel,status=None):
 o=d.addObject('Part::Feature',n);o.Shape=sh;g.addObject(o);o.ViewObject.ShapeColor=col;o.ViewObject.LineColor=(.12,.14,.15)
 if status:o.addProperty('App::PropertyString','EngineeringStatus');o.EngineeringStatus=status
 return o
for o in src.Objects:
 if o.TypeId!='Part::Feature':continue
 if any(o in getattr(g,'Group',[]) for g in [src.getObject('SoundboxAndStrings'),src.getObject('BaseFrame')]):
  sh=o.Shape.copy();sh.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());prefixes=['C','Cs','D','Eb','E','F','Fs','G','Ab','A','Bb','B']
  for lane,prefix in enumerate(prefixes):
   if o.Name.startswith(prefix+'_'):sh.translate(V(0,0,4*(lane-5.5)));break
  if o.Name in ['KotoAnchorBlock','KotoTunerBlock']:
   xx=-30 if 'Anchor' in o.Name else 312;sh=box(16,16.4,176,V(xx,-109,-113))
  if o.Name in ['KotoAnchorSaddleRail','KotoTunerSaddleRail']:
   xx=-24 if 'Anchor' in o.Name else 318;sh=box(4,1.2,174,V(xx,-92.6,-112))
  if o.Name in ['NylonLeftGuidePedestal','NylonRightGuidePedestal']:
   xx=-30 if 'Left' in o.Name else 330;sh=box(8 if 'Left' in o.Name else 10,12,174,V(xx,-109,-112))
  if o.Name=='NylonTensionerEndPlate':
   sh=box(4,41,176,V(340,-153,-112)).fuse(box(16,4,176,V(340,-153,-112)))
   for lane in range(12):
    z=-102+14*lane;sh=sh.cut(box(6,27,4,V(339,-145,z-2))).cut(cyl(2.2,6,V(351,-154,z),V(0,1,0)))
   for y in [-119,-145]:
    for z in [-87,39]:sh=sh.cut(cyl(2.2,6,V(339,y,z)))
  if o.Name=='NylonAnchorEndPlate':
   sh=box(4,31,176,V(-38,-143,-112))
   for lane in range(12):sh=sh.cut(cyl(1.1,6,V(-39,-130,-102+14*lane)))
   for y in [-119,-139]:
    for z in [-87,39]:sh=sh.cut(cyl(2.2,6,V(-39,y,z))).fuse(cyl(3,4,V(-34,y,z)).cut(cyl(2.2,6,V(-35,y,z))))
  add(o.Name,sh,groups['Soundbox'],tuple(o.ViewObject.ShapeColor[:3]))
def point(x,p):return V(x,p[0],p[1])
def plate_between(x,p,q,w=7,thick=3):
 # Capsule flat plate, axial X thickness.
 vv=V(0,q[0]-p[0],q[1]-p[1]);ll=vv.Length;u=vv/ll;n=V(0,-u.z,u.y)*w/2;a=point(x,p);b=point(x,q)
 poly=Part.makePolygon([a+n,b+n,b-n,a-n,a+n]);return Part.Face(poly).extrude(V(thick,0,0)).fuse(cyl(w/2,thick,a)).fuse(cyl(w/2,thick,b))
def gear(teeth,x,p,phase=0,bore=3):
 # Standard20 degree involute flanks. Root transitions are reference only.
 m=MODULE;rp=m*teeth/2;rb=rp*math.cos(math.radians(20));ra=rp+m;rf=rp-1.25*m;half=math.pi/(2*teeth);invp=math.tan(math.radians(20))-math.radians(20);pts=[]
 def inv(r):a=math.acos(rb/r);return math.tan(a)-a
 for k in range(teeth):
  c=phase+2*math.pi*k/teeth
  def vv(r,a):return V(x,p[0]+r*math.cos(a),p[1]+r*math.sin(a))
  rootang=half+invp
  pts.append(vv(rf,c-rootang));pts.append(vv(max(rf,rb),c-rootang))
  for j in range(1,7):
   r=max(rb,rf)+(ra-max(rb,rf))*j/6;pts.append(vv(r,c-(half+invp-inv(r))))
  for j in range(1,4):
   ang=c-(half+invp-inv(ra))+2*(half+invp-inv(ra))*j/3;pts.append(vv(ra,ang))
  for j in range(1,7):
   r=ra-(ra-max(rb,rf))*j/6;pts.append(vv(r,c+half+invp-inv(r)))
  pts.append(vv(rf,c+rootang))
 pts.append(pts[0]);sh=Part.Face(Part.makePolygon(pts)).extrude(V(4,0,0));return sh.cut(cyl(bore/2,6,point(x-1,p)))
# One continuous5 mm shaft. Four supported locations, not12 gear axles.
shaft_start=10;shaft_end=330
add('Common5mmInputShaft',cyl(2.5,shaft_end-shaft_start,point(shaft_start,DRIVE)),groups['CommonDrive'],steel)
for x in [16,112,208,320]:
 p=point(x,DRIVE);ring=cyl(7,4,p).cut(cyl(5,6,p-V(1,0,0)));add('InputBearingBlock_'+str(x),ring,groups['RearStructure'])
 add('Input105Bearing_'+str(x),cyl(5,4,p).cut(cyl(2.5,6,p-V(1,0,0))),groups['CommonDrive'],black)
 # Back stays terminate behind the string bank and leave the front open.
 anchor=V(x,-109,-115);top=V(x,DRIVE[0],-115);add('RearStay_'+str(x),tube(anchor,top,3,2),groups['RearStructure']);add('InputBearingShelf_'+str(x),tube(top,p,3,2),groups['RearStructure'])
 add('StayFoot_'+str(x),box(14,3,12,anchor+V(-7,-3,-6)).cut(cyl(1.7,6,anchor+V(0,-4,0),V(0,1,0))),groups['RearStructure'])
# Rear longitudinal backbone, no front rail.
add('RearBackbone',tube(V(12,-106,-115),V(324,-106,-115),3,2),groups['RearStructure'])
# Hand input removes premature motor sizing. The shaft accepts a later coupling.
wheel=cyl(25,4,point(330,DRIVE)).cut(cyl(2.5,6,point(329,DRIVE)))
for j in range(3):
 a=2*math.pi*j/3;wheel=wheel.cut(cyl(7,6,V(329,DRIVE[0]+14*math.cos(a),DRIVE[1]+14*math.sin(a))))
add('HandInputWheel',wheel,groups['CommonDrive'],brass,'Prototype hand input;3 rpm target is24 turns in8 min. No constant-speed motor or motor torque rating claimed.')
add('HandleJournal',cyl(2,14,V(334,DRIVE[0]+20,DRIVE[1])),groups['CommonDrive'])
add('FreeTurningHandGrip',cyl(5,11,V(337,DRIVE[0]+20,DRIVE[1])).cut(cyl(2.1,13,V(336,DRIVE[0]+20,DRIVE[1]))),groups['CommonDrive'],teal)
for row in ROWS:
 s=row['station_x'];n='V%02d'%row['index'];P=row['pivot_yz'];Q=row['crank_yz'];a,b,beta=linkage(row,row['phase_rad']);g=d.addObject('App::DocumentObjectGroup',n);g.Label=row['note']+' — '+row['ratio'];groups['VoiceMechanisms'].addObject(g)
 # Two narrow rear plates support both ends of each3 mm output/rocker shaft.
 for j,x in enumerate([s-12,s-1]):
  sh=plate_between(x,P,Q,9,3).fuse(plate_between(x,Q,DRIVE,9,3))
  for p in [P,Q]:sh=sh.cut(cyl(3.51,5,point(x-1,p)))
  sh=sh.cut(cyl(3,5,point(x-1,DRIVE)))
  add(n+'_Carrier'+str(j),sh,g)
  for k,p in enumerate([P,Q]):
   add(n+'_683Bearing_'+str(j)+'_'+str(k),cyl(3.5,3,point(x,p)).cut(cyl(1.5,5,point(x-1,p))),g,black)
   # Positive outer-race retainers with two M2 fixing-hole reservations.
   ret=cyl(5,1,point(x-1,p)).cut(cyl(2,3,point(x-2,p)))
   for z in [-4,4]:ret=ret.cut(cyl(.8,3,V(x-2,p[0],p[1]+z)))
   add(n+'_BearingRetainer_'+str(j)+'_'+str(k),ret,g)
 add(n+'_3mmShaft_0',cyl(1.5,26,point(s-14,P)),g)
 # Crank axle terminates at its flange, 1 mm behind the rod's rear face.
 # A single turned component avoids a shallow hub/shaft engagement.
 # Gear positions are reference geometry; supplier tooth cutters/root fillets govern manufacture.
 direction=math.atan2(Q[1]-DRIVE[1],Q[0]-DRIVE[0])
 for kind,teeth,p,bore,phase in [('Driver',row['driver_teeth'],DRIVE,5,direction),('Output',row['driven_teeth'],Q,3,direction+math.pi+math.pi/row['driven_teeth'])]:
  sh=gear(teeth,s-7,p,phase,bore);add(n+'_'+kind+'Gear',sh,g,brass,'Module0.5,20 degree spur gear; real involute flanks, root transitions and shaft locking require gear-maker drawings. Not a released gear machining file.')
 # Thin crank, pinned rod and rocker live forward of their carrier plates.
 crank=cyl(12,2,point(s+2,Q)).fuse(cyl(1.5,18,point(s-14,Q))).removeSplitter();add(n+'_CrankShaftOnePiece',crank,g,brass,'Integral shaft/flange machining candidate. Shaft ends at flange front; 1 mm axial gap to coupler. Bearing thrust stack, locking and fits remain unreleased.')
 add(n+'_CrankPin',cyl(1.5,7,point(s+3,a)),g)
 rocker=plate_between(s+2,P,b,7,2).cut(cyl(1.5,4,point(s+1,P)));add(n+'_Rocker',rocker,g,brass)
 add(n+'_RockerPin',cyl(1.5,7,point(s+3,b)),g)
 rod=plate_between(s+5,a,b,4,2)
 for p in [a,b]:rod=rod.cut(cyl(1.52,4,point(s+4,p)))
 add(n+'_POMCoupler',rod,g,(.78,.78,.70))
 for k,p in enumerate([a,b]):
  add(n+'_PinRetainingWasher_'+str(k),cyl(2.8,.5,point(s+7.2,p)).cut(cyl(.85,2,point(s+6.5,p))),g)
 rotor=d.addObject('App::Part',n+'_VisiblePendulum');g.addObject(rotor);R=row['arm_radius_mm']
 hub=cyl(5,4,V()).cut(cyl(1.5,6,V(-1,0,0)));add(n+'_PendulumHub',hub,rotor,brass)
 add(n+'_TubeArm',tube(V(2,0,4),V(2,0,R-1.2)),rotor,teal)
 add(n+'_TipSocket',tube(V(2,0,R-6),V(2,0,R-2),3,2.05),rotor,brass)
 pp=[V(1.75,-3,R-6),V(1.75,3,R-6),V(1.75,.5,R-.15),V(1.75,-.5,R-.15)];add(n+'_PETPick',Part.Face(Part.makePolygon(pp+[pp[0]])).extrude(V(.5,0,0)),rotor,(.78,.73,.52))
 rotor.Placement=A.Placement(point(s+7,P),A.Rotation(V(1,0,0),90))
 # A triangulated tube from rear backbone to pivot supports the bank without a front stand.
 add(n+'_RearPivotStay',tube(V(s-10,-106,-100),point(s-10,P),2,1),g)
 for prop,val in [('Ratio',row['ratio']),('GroundAndRod_mm',str(row['ground_mm'])),('CrankPhase_rad',str(row['phase_rad']))]:g.addProperty('App::PropertyString',prop);setattr(g,prop,val)
status=d.addObject('App::FeaturePython','BuildStatus');status.addProperty('App::PropertyString','Scope');status.Scope='Complete12-channel hand-driven architecture. Custom shaft locks, bearing fits, fastener retention, flexible picks and load/strength tests remain engineering gates. No physical pass or manufacturing release.'
d.recompute();bad=[o.Name for o in d.Objects if o.TypeId=='Part::Feature' and not o.Shape.isValid()];assert not bad,bad
v=G.getDocument(d.Name).activeView();v.viewAxonometric();v.fitAll();d.saveAs(str(OUT/'LeLovophon_Direct_Gear_Prototype.FCStd'))
meshes=[];shapes=[];bb=A.BoundBox()
for o in d.Objects:
 if o.TypeId!='Part::Feature':continue
 sh=o.Shape.copy();sh.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());shapes.append(sh);bb.add(sh.BoundBox);vs,ts=sh.tessellate(.25);meshes.append(dict(name=o.Name,vertices=[[p.x,p.y,p.z] for p in vs],triangles=ts,color=list(o.ViewObject.ShapeColor[:3])))
Part.makeCompound(shapes).exportStep(str(OUT/'Assembly_REFERENCE_NOT_FOR_MACHINING.step'));(ROOT/'work/direct_gear_mesh_axle_fix.json').write_text(json.dumps(meshes));rep=report();rep.update(invalid_shapes=bad,part_count=len(shapes),envelope_mm=[bb.XLength,bb.ZLength,bb.YLength]);(OUT/'Drive_Calculations.json').write_text(json.dumps(rep,indent=2))
print(json.dumps(dict(saved=True,parts=len(shapes),envelope=rep['envelope_mm'])),flush=True)
