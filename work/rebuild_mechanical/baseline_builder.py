"""Geometry revision R2. Native axes X string length, Y up, Z string lanes.
Nominal threads are clearance cores, not simulated thread contact.
"""
import sys, math, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import FreeCAD as A, FreeCADGui as G, Part
from FreeCAD import Vector as V
from PySide import QtWidgets
from direct_gear_math import ROWS, DRIVE, MODULE, linkage, report, ROOT
OUT=ROOT/'outputs/LeLovophon_Mechanical_Revision_R2'; OUT.mkdir(exist_ok=True)
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
G.showMainWindow(); G.getMainWindow().hide()
d=A.newDocument('LeLovophonR2'); d.Label='Le Lovophon R2 — geometry revision / bench prototype'
groups={n:d.addObject('App::DocumentObjectGroup',n) for n in ['Soundbox','StringsAndBridges','Tensioners','Frame','InputDrive','Voices']}
STEEL=(.65,.70,.72); BRASS=(.67,.48,.22); TEAL=(.10,.43,.38); WOOD=(.38,.18,.08); NYLON=(.88,.85,.72); BLACK=(.17,.18,.19)
def cyl(r,h,p,axis=V(1,0,0)): return Part.makeCylinder(r,h,p,axis)
def box(x,y,z,p): return Part.makeBox(x,y,z,p)
def bar(p,q,r): v=q-p; return cyl(r,v.Length,p,v)
def tube(p,q,ro=2,ri=1):
 v=q-p;u=v/v.Length;return bar(p,q,ro).cut(cyl(ri,v.Length+2,p-u,v))
def point(x,p):return V(x,p[0],p[1])
def ring(ro,ri,h,p,axis=V(1,0,0)):return cyl(ro,h,p,axis).cut(cyl(ri,h+2,p-axis,axis))
def add(n,sh,g,col=STEEL,motion='Fixed',voice=0,role='',note=''):
 o=d.addObject('Part::Feature',n);o.Shape=sh;g.addObject(o);o.ViewObject.ShapeColor=col
 for prop,value in [('Motion',motion),('Role',role),('DesignNote',note)]:o.addProperty('App::PropertyString',prop);setattr(o,prop,value)
 o.addProperty('App::PropertyInteger','Voice');o.Voice=voice
 return o
def capsule(x,p,q,w=9,thick=3.5):
 v=V(0,q[0]-p[0],q[1]-p[1]);u=v/v.Length;n=V(0,-u.z,u.y)*w/2;a=point(x,p);b=point(x,q)
 return Part.Face(Part.makePolygon([a+n,b+n,b-n,a-n,a+n])).extrude(V(thick,0,0)).fuse(cyl(w/2,thick,a)).fuse(cyl(w/2,thick,b))
def hex_prism(r,h,p,axis=V(1,0,0)):
 sh=Part.Face(Part.makePolygon([V(0,r*math.cos(j*math.pi/3),r*math.sin(j*math.pi/3)) for j in range(7)])).extrude(V(h,0,0))
 sh.rotate(V(),V(1,0,0).cross(axis) if abs(axis.x)<.99 else V(0,0,1),math.degrees(math.acos(axis.x)))
 sh.translate(p);return sh
def cs_screw(x,p,length=3.5):
 # M1.6 countersunk reference: head and minor core only.
 a=point(x,p);return Part.makeCone(1.45,.75,.9,a,V(1,0,0)).fuse(cyl(.75,length-.9,a+V(.9,0,0)))
def gear(teeth,x,p,phase=0,bore=3.04):
 # 20° involute reference. Each tooth narrowed 0.04 mm at pitch circle.
 rp=MODULE*teeth/2;rb=rp*math.cos(math.radians(20));ra=rp+MODULE;rf=rp-1.25*MODULE
 half=math.pi/(2*teeth)-.04/(2*rp);invp=math.tan(math.radians(20))-math.radians(20);pts=[]
 def inv(r):a=math.acos(rb/r);return math.tan(a)-a
 for k in range(teeth):
  c=phase+2*math.pi*k/teeth
  def vv(r,a):return V(x,p[0]+r*math.cos(a),p[1]+r*math.sin(a))
  rootang=half+invp;pts.extend([vv(rf,c-rootang),vv(max(rf,rb),c-rootang)])
  for j in range(1,9):
   r=max(rb,rf)+(ra-max(rb,rf))*j/8;pts.append(vv(r,c-(half+invp-inv(r))))
  for j in range(1,5):pts.append(vv(ra,c-(half+invp-inv(ra))+2*(half+invp-inv(ra))*j/4))
  for j in range(1,9):
   r=ra-(ra-max(rb,rf))*j/8;pts.append(vv(r,c+half+invp-inv(r)))
  pts.append(vv(rf,c+rootang))
 pts.append(pts[0]);return Part.Face(Part.makePolygon(pts)).extrude(V(4,0,0)).cut(cyl(bore/2,6,point(x-1,p)))

# New body: ALL bridge feet lie on the real 355 x 178 mm top panel.
top=box(355,3,178,V(-34,-115,-114));bottom=box(355,3,178,V(-34,-157,-114))
walls=box(355,39,6,V(-34,-154,-114)).fuse(box(355,39,6,V(-34,-154,58)))
walls=walls.fuse(box(6,39,166,V(-34,-154,-108))).fuse(box(6,39,166,V(315,-154,-108)))
for i in range(12):top=top.cut(cyl(1.05,5,V(-26.3,-116,-102+14*i),V(0,1,0)))
for x in [16,112,208,320]:
 # Last frame foot uses an end mounting ear beyond the case; moved inward below.
 pass
FRAME_X=[6,89.75,185.75,281.75]
for x in FRAME_X:
 for y in [-121,-137]:walls=walls.cut(cyl(1.65,10,V(x,y,-116),V(0,0,1)))
for z,sgn in [(-114,1),(64,-1)]:walls=walls.cut(cyl(1.1,12,V(-21.5,-137.5,z),V(0,0,sgn)))
add('Soundboard_355x178x3',top,groups['Soundbox'],WOOD,role='Soundboard')
add('RemovableBottom_355x178x3',bottom,groups['Soundbox'],WOOD,role='Body')
add('SoundboxWalls_6mm',walls,groups['Soundbox'],WOOD,role='Body',note='Glued side/end frame; bottom panel removable. Wood joints and bottom screws require shop drawing.')
for fx in [-14,299]:
 for fz in [-102,52]:add('RubberFoot',box(10,11,10,V(fx-5,-168,fz-5)),groups['Soundbox'],BLACK,role='Foot',note='Adhesive elastomer foot; raises tuning screw heads 4 mm clear of table.')
# Lower non-speaking saddle, high speaking nut: both R2 crowns, nylon radius .4.
left_support=box(4,4.7,174,V(-25,-112,-112));right_support=box(4,16.7,174,V(318,-112,-112))
add('LeftSaddlePedestal',left_support,groups['StringsAndBridges'],WOOD)
add('RightNutPedestal',right_support,groups['StringsAndBridges'],WOOD)
left_crown=cyl(2,174,V(-24,-105.3,-112),V(0,0,1));right_crown=cyl(2,174,V(321,-93.3,-112),V(0,0,1))
# Guide grooves are cylindrical cuts centred on each string path, with 0.05 mm radial clearance.
def arc_points(cx,cy,r,a0,a1,z,steps=32):return [V(cx+r*math.cos(a0+(a1-a0)*j/steps),cy+r*math.sin(a0+(a1-a0)*j/steps),z) for j in range(steps+1)]
def string_path(points):
 edges=[Part.makeLine(p,q) for p,q in zip(points,points[1:]) if (q-p).Length>1e-8]
 wire=Part.Wire(edges);t=(points[1]-points[0]);circle=Part.Wire([Part.makeCircle(.4,points[0],t)])
 return wire.makePipeShell([circle],True,False,2)
def round_path(points,r):
 sh=None
 for a,b in zip(points,points[1:]):
  if (b-a).Length<1e-8:continue
  seg=bar(a,b,r);sh=seg if sh is None else sh.fuse(seg)
 return sh
# Anchor bar inside the soundbox: strings pass through actual top and bar holes.
anchor=box(10,3,166,V(-28,-139,-108))
for i in range(12):anchor=anchor.cut(cyl(1.05,5,V(-26.3,-140,-102+14*i),V(0,1,0)))
for z,sgn in [(-108,1),(58,-1)]:anchor=anchor.cut(cyl(1.1,5,V(-21.5,-137.5,z),V(0,0,sgn)))
add('TwelveStringAnchorBar',anchor,groups['StringsAndBridges'],STEEL,role='Anchor',note='Nylon passes through 2.1 mm holes; stopper knot bears below bar. Side screws retain the bar.')
for z,sgn in [(-116,1),(66,-1)]:
 axis=V(0,0,sgn);p=V(-21.5,-137.5,z);head=cyl(1.8,2,p,axis);core=cyl(.95,11,p+axis*2,axis)
 add('AnchorBarSideScrew',head.fuse(core),groups['StringsAndBridges'],STEEL,role='Fastener',note='M2 socket-head reference; threads omitted.')

routes=[]
for row in ROWS:
 i=row['index']-1;n=f'V{i+1:02d}';z=-102+14*i;bx=row['bridge_x']+1;foot=Part.Face(Part.makePolygon([V(bx-6,-112,z-4),V(bx+6,-112,z-4),V(bx+1,-93.3,z-4),V(bx-1,-93.3,z-4),V(bx-6,-112,z-4)])).extrude(V(0,0,8))
 # Crown top = -91.4; loaded string centre = -91.0.
 crown=cyl(2,8,V(bx,-93.3,z-4),V(0,0,1))
 # Equal-radius common tangent, plus arcs around real saddles. Main length unchanged.
 dx=bx+24;dy=12;aa=math.atan2(dy,dx)+math.pi/2
 pts=[V(-26.3,-140.6,z)]+arc_points(-24,-105.3,2.3,math.pi,aa,z)
 pts+=arc_points(bx,-93.3,2.3,aa,math.pi/2,z)
 # Above includes the straight common tangent between its two arc endpoint lists.
 pts += [V(321,-91,z)] + arc_points(321,-93.3,2.3,math.pi/2,0,z)[1:]+[V(323.3,-146.6,z)]
 # Smooth tangent wire: seven analytic edges, not a polygonal chain.
 def arc(cx,cy,a0,a1):
  def p(a):return V(cx+2.3*math.cos(a),cy+2.3*math.sin(a),z)
  return Part.Arc(p(a0),p((a0+a1)/2),p(a1)).toShape()
 lc=V(-24+2.3*math.cos(aa),-105.3+2.3*math.sin(aa),z)
 bc=V(bx+2.3*math.cos(aa),-93.3+2.3*math.sin(aa),z)
 edges=[Part.makeLine(V(-26.3,-140.6,z),V(-26.3,-105.3,z)),arc(-24,-105.3,math.pi,aa),Part.makeLine(lc,bc),arc(bx,-93.3,aa,math.pi/2),Part.makeLine(V(bx,-91,z),V(321,-91,z)),arc(321,-93.3,math.pi/2,0),Part.makeLine(V(323.3,-93.3,z),V(323.3,-146.6,z))]
 wire=Part.Wire(edges);profile=Part.Wire([Part.makeCircle(.4,V(-26.3,-140.6,z),V(0,1,0))]);st=wire.makePipeShell([profile],True,False)
 add(n+'_NylonString',st,groups['StringsAndBridges'],NYLON,role='String',voice=i+1)
 cutter=st.copy() # Nominal seated contact; 0.1 mm-deep retaining groove.
 print('STRING',i+1,flush=True)
 crown=crown.cut(cutter);left_crown=left_crown.cut(cutter);right_crown=right_crown.cut(cutter)
 add(n+'_ThirdBridge',foot.fuse(crown).cut(cutter),groups['StringsAndBridges'],BRASS,voice=i+1,role='Bridge',note='8 mm foot fully supported. Nominal seated 0.4 mm-radius groove, 0.1 mm deep in R2 crown. Final action/pick flex must be bench set.')
 for end,x,y in [('Anchor',-26.3,-140.6),('Tuner',323.3,-146.6)]:
  add(n+'_'+end+'StopperKnot',Part.makeSphere(1.6,V(x,y,z)),groups['StringsAndBridges'],NYLON,voice=i+1,role='Knot',note='Knot envelope only. Tie and pull-test actual nylon; not a molded ball end.')
 routes.append(dict(note=row['note'],bridge_x=bx,speaking_length_mm=321-bx,back_break_angle_deg=math.degrees(math.atan2(dy,dx)),speaking_y=-91,lane_z=z,bridge_support_margin_z_mm=min(z-4+114,64-z-4),anchor_hole_diameter_mm=2.1))
add('LowerBackSaddleGrooved',left_crown,groups['StringsAndBridges'],BRASS)
add('SpeakingEndNutGrooved',right_crown,groups['StringsAndBridges'],BRASS)

# Twelve screw tensioners outside the end wall. M4 carriage travel is visible.
plate=box(3,41,186,V(326,-157,-118)).fuse(box(18,3,186,V(326,-160,-118)))
for i in range(12):
 z=-102+14*i;plate=plate.cut(box(5,31,8,V(325,-153,z-4))).cut(cyl(2.1,5,V(334.5,-161,z),V(0,1,0)))
for y in [-121,-149]:
 for z in [-112,62]:
  plate=plate.cut(cyl(1.65,5,V(325,y,z)));walls_obj=d.getObject('SoundboxWalls_6mm')
  walls_obj.Shape=walls_obj.Shape.cut(cyl(1.65,9,V(314,y,z)))
  add('TunerMountSpacer',ring(3,1.65,5,V(321,y,z)),groups['Tensioners'])
  bolt=cyl(1.4,13,V(316,y,z)).fuse(cyl(2.75,3,V(329,y,z)))
  add('TunerMountM3Screw',bolt,groups['Tensioners'],role='Fastener',note='M3 socket-head nominal core; tapped side/end block required.')
add('SlottedTensionerAngle',plate,groups['Tensioners'],STEEL,role='TensionerFrame')
for i in range(12):
 z=-102+14*i;n=f'V{i+1:02d}';c=box(3.7,4,11,V(322,-145,z-5.5)).fuse(box(3.6,4,7,V(325.7,-145,z-3.5))).fuse(box(10.7,4,11,V(329.3,-145,z-5.5)))
 c=c.cut(cyl(1.05,6,V(323.3,-146,z),V(0,1,0))).cut(cyl(2.1,6,V(334.5,-146,z),V(0,1,0)))
 # A real captured hex nut, clear bore envelope; contact threads deliberately omitted.
 pocket=hex_prism(4.16,2.5,V(334.5,-145.01,z),V(0,1,0));c=c.cut(pocket)
 add(n+'_TunerCarriage',c,groups['Tensioners'],voice=i+1,role='Carriage')
 nut=hex_prism(4.04,2.4,V(334.5,-145,z),V(0,1,0)).cut(cyl(2.05,4,V(334.5,-146,z),V(0,1,0)))
 add(n+'_CapturedM4Nut',nut,groups['Tensioners'],BRASS,voice=i+1,role='Fastener')
 shaft=cyl(1.95,45,V(334.5,-160.5,z),V(0,1,0));head=cyl(3.5,3.5,V(334.5,-164,z),V(0,1,0))
 head=head.cut(hex_prism(1.73,2.5,V(334.5,-164.1,z),V(0,1,0)))
 add(n+'_M4TensionScrew',shaft.fuse(head),groups['Tensioners'],voice=i+1,role='LeadScrew',note='M4x45 socket screw reference; nominal smooth thread envelope. 23 mm usable carriage travel. Washer/collar gives axial capture; pull test required.')
 add(n+'_TensionThrustWasher',ring(3.5,2.05,.5,V(334.5,-160.5,z),V(0,1,0)),groups['Tensioners'])
 for yy in [-156.8,-154.8]:
  add(n+'_TensionJamNut',hex_prism(4.04,2,V(334.5,yy,z),V(0,1,0)).cut(cyl(2.05,4,V(334.5,yy-1,z),V(0,1,0))),groups['Tensioners'],role='Fastener',note='Two M4 jam nuts locked together; 0.2 mm running axial clearance above angle.')

# Single welded rear tube frame; no diagonal ever enters the string bed.
rear=(65,-125);frame=tube(V(-3,*rear),V(337,*rear),4,3)
for x in FRAME_X:
 frame=frame.fuse(tube(V(x,-109,-145),V(x,65,-145),4,3)).fuse(tube(V(x,65,-145),V(x,65,-125),4,3))
 foot=box(18,3,39,V(x-9,-112,-153)).fuse(box(18,34,3,V(x-9,-140,-117)))
 for y in [-121,-137]:foot=foot.cut(cyl(1.65,5,V(x,y,-118),V(0,0,1)))
 frame=frame.fuse(foot)
 for y in [-121,-137]:
  bolt=cyl(1.45,12,V(x,y,-117),V(0,0,1)).fuse(cyl(2.75,3,V(x,y,-120),V(0,0,1)))
  nut=hex_prism(3.1,2.4,V(x,y,-108),V(0,0,1)).cut(cyl(1.55,4,V(x,y,-109),V(0,0,1)))
  add('FrameWallM3Screw',bolt,groups['Frame'],role='Fastener');add('FrameWallM3Nut',nut,groups['Frame'],role='Fastener')
add('WeldedRearFrame_8x1Tube',frame.removeSplitter(),groups['Frame'],STEEL,role='Frame',note='8 mm OD / 6 mm ID tube. Welded subassembly removable via eight M3 wall bolts; weld penetration, body crush and stiffness require shop review/test.')
# Four bearing housings bridge to OUTER rail/housing surfaces, with positive bores.
for x in [16,112,208,320]:
 sh=capsule(x,DRIVE,(85,-45),9,5).fuse(capsule(x,(85,-45),(85,-125),9,5)).fuse(capsule(x,(85,-125),rear,9,5)).fuse(cyl(7,5,point(x,DRIVE)))
 for dy in [-6.1,6.1]:sh=sh.fuse(cyl(1.8,5,V(x,65+dy,-25)))
 sh=sh.cut(cyl(5.01,4,point(x,DRIVE))).cut(cyl(4.3,7,point(x-1,DRIVE))).cut(cyl(4.01,7,point(x-1,rear)))
 sh=sh.cut(cyl(1.05,7,V(x+2.5,65,-132),V(0,0,1)))
 add('InputBearingBridge_'+str(x),sh,groups['Frame'])
 add('Input105Bearing_'+str(x),ring(5,2.5,4,point(x,DRIVE)),groups['InputDrive'],BLACK,role='Bearing',note='MR105ZZ shielded 5x10x4; open MR105 is 3 mm wide and is not interchangeable here.')
 ret=ring(8,4.3,1,point(x-1,DRIVE))
 for dy in [-6.1,6.1]:
  p=(65+dy,-25);ret=ret.cut(Part.makeCone(1.45,.85,.9,point(x-1,p),V(1,0,0))).cut(cyl(.85,3,point(x-1,p)))
  ob=d.getObject('InputBearingBridge_'+str(x));ob.Shape=ob.Shape.cut(cyl(.85,4,point(x,p)))
  add('InputRetainerScrew',cs_screw(x-1,p),groups['Frame'],role='Fastener')
 add('InputBearingRetainer_'+str(x),ret,groups['Frame'])
 add('InputRailClampM2_'+str(x),cyl(.95,3,V(x+2.5,65,-132),V(0,0,1)),groups['Frame'],role='Fastener',note='Radial M2 cup screw nominal core; reaches rear rail surface, threads omitted.')

# Shared 5 mm axle, gears locked by flush 1 mm cross-pins; drill after phasing.
input_sh=cyl(2.5,327,point(3,DRIVE)).cut(cyl(.5,12,V(327.5,59,-25),V(0,1,0))).cut(cyl(.5,12,V(14.2,59,-25),V(0,1,0)))
for row in ROWS:
 s=row['station_x'];q=row['crank_yz'];direction=math.atan2(q[1]-DRIVE[1],q[0]-DRIVE[0]);ax=V(0,-math.sin(direction),math.cos(direction));ctr=point(s-5.5,DRIVE)
 input_sh=input_sh.cut(cyl(.5,12,ctr-ax*6,ax))
add('Common5mmInputShaft',input_sh,groups['InputDrive'],motion='Input',role='InputShaft',note='1 mm transverse pin holes phased in assembly jig. Fits and pin stresses require machine-shop review.')
wheel=ring(25,2.52,4,point(330,DRIVE)).fuse(ring(5,2.52,4,point(326,DRIVE))).fuse(ring(3.5,2.52,1.8,point(324.2,DRIVE))).cut(cyl(.5,12,V(327.5,59,-25),V(0,1,0)))
add('HandInputWheelWithHub',wheel,groups['InputDrive'],BRASS,motion='Input',note='One-piece wheel/hub, 5 mm shaft engagement, flush 1 mm transverse pin. Manual test input; no regulated motor speed claimed.')
add('HandWheelFlushPin',cyl(.49,9.6,V(327.5,60.2,-25),V(0,1,0)),groups['InputDrive'],motion='Input',role='DrivePin')
collar=ring(4,2.52,3,point(12.7,DRIVE)).cut(cyl(.5,10,V(14.2,60,-25),V(0,1,0)))
add('InputRearPinnedCollar',collar,groups['InputDrive'],motion='Input',role='Retainer')
add('InputRearCollarFlushPin',cyl(.49,7.6,V(14.2,61.2,-25),V(0,1,0)),groups['InputDrive'],motion='Input',role='DrivePin')
add('InputRearThrustShim',ring(2.95,2.55,.3,point(15.7,DRIVE)),groups['InputDrive'],motion='Input',role='Shim')
add('InputFrontThrustShim',ring(2.95,2.55,.2,point(324,DRIVE)),groups['InputDrive'],motion='Input',role='Shim')


for row in ROWS:
 print('VOICE',row['index'],flush=True)
 s=row['station_x'];n=f"V{row['index']:02d}";iv=row['index'];P=row['pivot_yz'];Q=row['crank_yz'];aa,bb,beta=linkage(row,row['phase_rad']);g=d.addObject('App::DocumentObjectGroup',n);g.Label=row['note']+' — '+row['ratio'];groups['Voices'].addObject(g)
 def put(suffix,shape,col=STEEL,motion='Fixed',role='',note=''):return add(n+'_'+suffix,shape,g,col,motion,iv,role,note)
 for j,x in enumerate([s-12,s-2]):
  sh=capsule(x,P,Q).fuse(capsule(x,Q,DRIVE)).fuse(capsule(x,DRIVE,rear,10))
  for p in [P,Q]:
   sh=sh.fuse(cyl(6,3.5,point(x,p))).cut(cyl(3.51,3,point(x,p))).cut(cyl(3.2,5,point(x-1,p)))
   for dy in [-4.5,4.5]:sh=sh.cut(cyl(.85,5,V(x-1,p[0]+dy,p[1])))
  sh=sh.fuse(cyl(7,3.5,point(x,rear))).cut(cyl(4.01,6,point(x-1,rear))).cut(cyl(3,6,point(x-1,DRIVE)))
  # Rail lock cup screw in the carrier's rear boss.
  sh=sh.cut(cyl(.85,4,V(x+1.75,65,-132),V(0,0,1)))
  put('Carrier'+str(j),sh,role='Carrier')
  put('RailLock'+str(j),cyl(.8,3,V(x+1.75,65,-132),V(0,0,1)),role='Fastener')
  for k,p in enumerate([P,Q]):
   put(f'683Bearing_{j}_{k}',ring(3.5,1.5,3,point(x,p)),BLACK,role='Bearing',note='683ZZ shielded 3x7x3; open 683 is narrower. Inner abutment OD4, outer shoulder ID6.4.')
   ret=ring(5.5,3.2,1,point(x-1,p))
   for dy in [-4.5,4.5]:
    cp=(p[0]+dy,p[1]);ret=ret.cut(Part.makeCone(1.45,.85,.9,point(x-1,cp),V(1,0,0))).cut(cyl(.85,3,point(x-1,cp)))
    put(f'RetainerScrew_{j}_{k}',cs_screw(x-1,cp),role='Fastener')
   put(f'OuterRaceRetainer_{j}_{k}',ret,role='Retainer')
 # Pair the carrier plates with two ordinary M2 standoffs, 6 mm + 0.5 mm shim.
 for zz in [-85,-110]:
  cp=(65,zz)
  for jj,xx in enumerate([s-12,s-2]):
   co=d.getObject(n+'_Carrier'+str(jj));co.Shape=co.Shape.cut(cyl(1.05,5,point(xx-1,cp)))
   start=xx if jj==0 else xx+3.5;axis=V(1,0,0) if jj==0 else V(-1,0,0)
   co.Shape=co.Shape.cut(Part.makeCone(1.8,1.05,1.1,point(start,cp),axis))
  put('M2Standoff',ring(2.5,1.05,6,point(s-8.5,cp)),role='Spacer')
  put('StandoffShim',ring(2.5,1.05,.5,point(s-2.5,cp)),role='Shim')
  for start,axis,length in [(s-12,V(1,0,0),6.5),(s+1.5,V(-1,0,0),6)]:
   screw=Part.makeCone(1.8,.95,1.1,point(start,cp),axis).fuse(cyl(.95,length-1.1,point(start,cp)+axis*1.1,axis))
   put('CarrierM2CSKScrew',screw,role='Fastener')
 # One-piece rocker/shaft. Rear E-ring groove eliminates protruding shaft ends.
 def spindle(p):
  sh=cyl(1.5,15,point(s-13,p)).fuse(cyl(2,.8,point(s+1.2,p)))
  return sh.cut(ring(1.6,1.2,.6,point(s-12.8,p)))
 rocker=capsule(s+2,P,bb,7,2).fuse(spindle(P)).fuse(cyl(1.5,8,point(s+2,P)))
 rocker=rocker.cut(cyl(1.51,4,point(s+1,bb)))
 put('RockerShaftOnePiece',rocker,BRASS,'Rocker','Rocker')
 crank=cyl(12,2,point(s+2,Q)).fuse(spindle(Q));crank=crank.cut(cyl(1.51,4,point(s+1,aa)))
 direction=math.atan2(Q[1]-DRIVE[1],Q[0]-DRIVE[0]);ax=V(0,-math.sin(direction),math.cos(direction));pinlen=2*(MODULE*row['driven_teeth']/2-1.25*MODULE-.2)
 crank=crank.cut(cyl(.5,14,point(s-5.5,Q)-ax*7,ax))
 put('CrankShaftOnePiece',crank,BRASS,'Crank','Crank')
 for kind,teeth,p,bore,phase,mot in [('Driver',row['driver_teeth'],DRIVE,5.04,direction,'Input'),('Output',row['driven_teeth'],Q,3.04,direction+math.pi+math.pi/row['driven_teeth'],'Crank')]:
  gp=gear(teeth,s-7.5,p,phase,bore);length=2*(MODULE*teeth/2-1.25*MODULE-.2);center=point(s-5.5,p)
  gp=gp.cut(cyl(.5,length+2,center-ax*(length/2+1),ax));put(kind+'Gear',gp,BRASS,mot,'Gear','0.08 mm nominal pitch-circle pair backlash. Reference faceted involute, root fillets and final tolerances must use gear-maker drawing.')
  put(kind+'FlushCrossPin',cyl(.49,length,center-ax*length/2,ax),STEEL,mot,'DrivePin','1 mm flush cross pin. Jig-drill after phase setting, pin ends below gear root circle. Retention/fit and shear proof required.')
 for tag,p,mot in [('Pivot',P,'Rocker'),('Crank',Q,'Crank')]:
  clip=ring(2.5,1.2,.5,point(s-12.75,p));clip=clip.cut(box(1,1.6,3,V(s-13,p[0]-.8,p[1]+.6)))
  put(tag+'RearEClip',clip,STEEL,mot,'Retainer')
  put(tag+'RearShim',ring(2,1.55,.2,point(s-12.2,p)),STEEL,mot,'Shim')
  put(tag+'FrontThrustShim',ring(2,1.55,.2,point(s+1,p)),STEEL,mot,'Shim')
 for j,p,mot in [('Crank',aa,'Crank'),('Rocker',bb,'Rocker')]:
  # 3 mm journal ENDS at +7.2; M1.6 screw passes a 1.7 mm washer beyond it.
  pin=cyl(1.5,4.2,point(s+3,p)).fuse(cyl(2.2,.5,point(s+4,p))).cut(cyl(.8,1.2,point(s+6.1,p)))
  put(j+'ShoulderJournal',pin,STEEL,mot,'ShoulderPin')
  put(j+'PinEndScrew',cyl(.75,1.7,point(s+6.1,p)).fuse(cyl(1.4,1,point(s+7.8,p))),STEEL,mot,'Fastener')
  put(j+'PinWasher',ring(2.8,.85,.5,point(s+7.3,p)),STEEL,mot,'Washer')
 rod=capsule(s+5,aa,bb,4,2)
 for p in [aa,bb]:rod=rod.cut(cyl(1.52,4,point(s+4,p)))
 put('POMCoupler',rod,(.78,.78,.70),'Coupler','Coupler')
 # Arm moved 1 mm rearward; neighbour's rear clip is now at least 1 mm away.
 origin=point(s+6,P);R=row['arm_radius_mm']
 hub=ring(5,1.52,4,V()).fuse(box(4,4.7,2,V(0,-5,-4.5))).fuse(box(4,4.7,2,V(0,.3,-4.5)));hub=hub.cut(box(6,.6,5,V(-1,-.3,-5))).cut(cyl(1.05,12,V(2,-6,-3.5),V(0,1,0)))
 sh_arm=tube(V(2,0,4),V(2,0,R-6));socket=box(4,4,3,V(0,-2,R-8))
 # Socket/arm are a deliberate brazed assembly, combined rather than colliding parts.
 assembled=hub.fuse(sh_arm).fuse(socket)
 pp=[V(.5,-.15,R-8),V(3.5,-.15,R-8),V(2.5,-.15,R-.15),V(1.5,-.15,R-.15)]
 pick=Part.Face(Part.makePolygon(pp+[pp[0]])).extrude(V(0,.3,0))
 # Cut insertion pocket, leave pick separate and removable.
 assembled=assembled.cut(pick)
 pinhole=cyl(.85,6,V(2,-3,R-6.5),V(0,1,0));assembled=assembled.cut(pinhole).cut(Part.makeCone(1.45,.85,.9,V(2,-2,R-6.5),V(0,1,0)));pick=pick.cut(pinhole)
 tipscrew=Part.makeCone(1.45,.75,.9,V(2,-2,R-6.5),V(0,1,0)).fuse(cyl(.75,3,V(2,-1.1,R-6.5),V(0,1,0)));tipscrew.rotate(V(),V(1,0,0),90);tipscrew.translate(origin);put('PickM1_6Screw',tipscrew,STEEL,'Pendulum','Fastener','Countersunk M1.6 screw through PET into brass tip block; thread form omitted.')
 for suffix,sh,col,role in [('PendulumAssembly',assembled,TEAL,'Arm'),('PETPick',pick,NYLON,'Pick')]:
  sh.rotate(V(),V(1,0,0),90);sh.translate(origin);put(suffix,sh,col,'Pendulum',role)
 clamp=cyl(.95,9,V(2,-5,-3.5),V(0,1,0)).fuse(cyl(1.75,1.5,V(2,-6.5,-3.5),V(0,1,0)))
 clamp.rotate(V(),V(1,0,0),90);clamp.translate(origin);put('ArmClampM2',clamp,STEEL,'Pendulum','Fastener','M2 pinch screw across split hub; phase set with arm at zero; clamp torque and slip must be bench tested.')

status=d.addObject('App::FeaturePython','EngineeringStatus');status.addProperty('App::PropertyString','Status');status.Status='R2 corrected nominal geometry. Not physically validated; final fits, loads, pick release and acoustic test required. No fabrication release.'
d.recompute();invalid=[o.Name for o in d.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())]
assert not invalid,invalid
view=G.getDocument(d.Name).activeView();view.viewAxonometric();view.fitAll();d.saveAs(str(OUT/'LeLovophon_R2.FCStd'))
inv=[];meshes=[];bb=A.BoundBox()
for o in d.Objects:
 if o.TypeId!='Part::Feature':continue
 sh=o.Shape;bb.add(sh.BoundBox);vs,ts=sh.tessellate(.3)
 inv.append(dict(name=o.Name,motion=o.Motion,voice=o.Voice,role=o.Role,volume_mm3=sh.Volume,design_note=o.DesignNote))
 meshes.append(dict(name=o.Name,vertices=[[p.x,p.y,p.z] for p in vs],triangles=ts,color=list(o.ViewObject.ShapeColor[:3]),motion=o.Motion,voice=o.Voice))
(OUT/'Part_Inventory.json').write_text(json.dumps(inv,indent=2));(OUT/'String_Routing.json').write_text(json.dumps(routes,indent=2));(ROOT/'work/rebuild_mechanical/mesh.json').write_text(json.dumps(meshes))
calc=report();calc['voices']=[dict(r,pick_x=r['station_x']+8,bridge_x=r['bridge_x']+1,speaking_end_x=321) for r in ROWS];calc.update(geometry_revision='R2',invalid_shapes=invalid,part_count=len(inv),envelope_mm=[bb.XLength,bb.ZLength,bb.YLength],arm_axial_envelope_relative_station_mm=[6,10],next_shaft_and_clip_min_relative_station_mm=11,minimum_axial_arm_to_next_shaft_mm=1,notes='Speaking string Y=-91, horizontal length 330/ratio ending at X321. Non-speaking left saddle lowered 12 mm; captured grooves. Nominal thread envelopes omit thread form.')
(OUT/'Drive_Calculations.json').write_text(json.dumps(calc,indent=2));print('R2_SAVED',len(inv),calc['envelope_mm'],flush=True)
