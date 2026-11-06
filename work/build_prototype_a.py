import FreeCAD as A,FreeCADGui as G,Part,math,json
from FreeCAD import Vector as V
from PySide import QtWidgets
from prototype_a_math import *
q=QtWidgets.QApplication.instance() or QtWidgets.QApplication([]);G.showMainWindow();G.getMainWindow().hide()
d=A.newDocument('LovophonePrototypeA');d.Label='Lovophone — physical test fixtures A (quotation / engineering review)'
custom=[];groups={};colors={}
def group(n):
 o=d.addObject('App::DocumentObjectGroup',n);groups[n]=o;return o
ratio=group('Ratio_Test');pluck=group('Pluck_Test')
def box(w,h,t,x=0,y=0,z=0):return Part.makeBox(w,h,t,V(x,y,z))
def cyl(r,t,x=0,y=0,z=0):return Part.makeCylinder(r,t,V(x,y,z))
def slot(x,y,travel,dia,t,z=0):return box(travel,dia,t,x-travel/2,y-dia/2,z).fuse(cyl(dia/2,t,x-travel/2,y,z)).fuse(cyl(dia/2,t,x+travel/2,y,z))
def part(n,s,g,col=(.72,.75,.77),local=None,description=None):
 o=d.addObject('Part::Feature',n);o.Shape=s;g.addObject(o);o.ViewObject.ShapeColor=col;o.ViewObject.LineColor=(.15,.16,.17);o.ViewObject.DisplayMode='Flat Lines'
 if local is not None:
  local.exportStep(str(OUT/(n+'.step')))
  custom.append(dict(id=n,description=description or n,volume_mm3=local.Volume))
 return o
# Independent bearing carriers keep bearings out of pulley teeth; 6 mm plate + 50 mm spacers.
xs=[30,30+C1,30+C1+C2]
plate=box(180,100,6)
for x in xs:
 plate=plate.cut(slot(x,50,6,32,8,-1))
 for dx in [-10,10]:
  for dy in [-20,20]:plate=plate.cut(slot(x+dx,50+dy,6,3.4,8,-1))
for x in [10,170]:
 for y in [10,90]:plate=plate.cut(cyl(2.25,8,x,y,-1))
for k,z in enumerate([0,56]):
 s=plate.copy();s.translate(V(0,0,z));part('R01_Cheek_'+str(k),s,ratio,local=plate if k==0 else None,description='Two identical 180 x 100 x 6 mm 6061-T6 cheeks; slotted carrier mounting')
carrier=box(30,50,6,-15,-25);carrier=carrier.cut(cyl(4,8,0,0,-1)).cut(cyl(8,5,0,0,1))
for x in [-10,10]:
 for y in [-20,20]:carrier=carrier.cut(cyl(1.7,8,x,y,-1))
for x in [-11,11]:carrier=carrier.cut(cyl(.8,8,x,0,-1))
ret=cyl(13.5,1).cut(cyl(4,3,0,0,-1))
for x in [-11,11]:ret=ret.cut(cyl(1.1,3,x,0,-1))
for i,x in enumerate(xs):
 for side in [0,1]:
  s=carrier.copy()
  if side==0:s.rotate(V(),V(1,0,0),180);s.translate(V(x,50,0))
  else:s.translate(V(x,50,62))
  part('R02_Carrier_'+str(i)+'_'+str(side),s,ratio,local=carrier if i==0 and side==0 else None,description='Six identical bearing carriers, 30 x 50 x 6; 16 H7 pocket depth 5, 8 through; outer race shoulder')
  rr=ret.copy();rr.translate(V(x,50,0 if side==0 else 61));part('R03_Retainer_'+str(i)+'_'+str(side),rr,ratio,local=ret if i==0 and side==0 else None,description='Six 27 OD x 8 ID x 1 stainless retainers; 2 x 2.2 clearance at +/-11')
  z=-5 if side==0 else 63
  part('R_Bearing_'+str(i)+'_'+str(side),cyl(8,5,x,50,z).cut(cyl(2.5,7,x,50,z-1)),ratio)
 part('R_Shaft_'+str(i),cyl(2.5,100,x,50,-20),ratio)
for x in [10,170]:
 for y in [10,90]:part('R_Spacer_'+str(x)+'_'+str(y),cyl(4,50,x,y,6).cut(cyl(2.25,52,x,y,5)),ratio)
# Bought pulley reservations: explicitly not CAD models for tooth manufacture.
for i,(x,z,t) in enumerate([(xs[0],14,60),(xs[1],14,20),(xs[1],38,30),(xs[2],38,20)]):
 r=t/math.pi
 sh=cyl(r-.25,7,x,50,z-3.5).fuse(cyl(r+1.8,1,x,50,z-4.5)).fuse(cyl(r+1.8,1,x,50,z+3.5)).fuse(cyl(min(r,7),9,x,50,z+4.5)).cut(cyl(2.5,22,x,50,z-5))
 o=part('R_PurchasedPulley_'+str(i),sh,ratio,(.68,.52,.22));o.addProperty('App::PropertyString','Status');o.Status='Purchased 5 mm bore, 6 mm belt GT2 pulley. Hub/flange shape is a reservation; confirm supplier batch drawing before fixing spacers.'
def wire(B,C,r,s):
 v=C-B;D=v.Length;v.normalize();p=V(-v.y,v.x,0);k=(r-s)/D;h=math.sqrt(1-k*k);n=v*k+p*h;m=v*k-p*h
 return Part.Wire([Part.makeLine(B+n*r,C+n*s),Part.Arc(C+n*s,C+v*s,C+m*s).toShape(),Part.makeLine(C+m*s,B+m*r),Part.Arc(B+m*r,B-v*r,B+n*r).toShape()])
for i,(a,b,t,u,z) in enumerate([(xs[0],xs[1],60,20,11),(xs[1],xs[2],30,20,35)]):
 B=V(a,50,z);C=V(b,50,z);r=t/math.pi;s=u/math.pi
 sh=Part.Face(wire(B,C,r+1,s+1)).cut(Part.Face(wire(B,C,r+.1,s+.1))).extrude(V(0,0,6));part('R_BeltReservation_'+str(i),sh,ratio,(.12,.14,.15))
# Pluck jig: separate from ratio bench. Coordinates offset for clear side-by-side viewing.
OFF=V(230,0,0)
plate2=box(140,140,6)
for x,y in [(30,110),(110,110)]:plate2=plate2.cut(cyl(8,8,x,y,-1))
for x,y in [(10,10),(130,10),(10,130),(130,130)]:plate2=plate2.cut(cyl(2.25,8,x,y,-1))
for y in [110-RLOW,110-RHIGH]:plate2=plate2.cut(cyl(5,8,110,y,-1))
for j,z in enumerate([0,36]):
 sh=plate2.copy();sh.translate(OFF+V(0,0,z));part('P01_LinkageCheek_'+str(j),sh,pluck,local=plate2 if j==0 else None,description='Two 140 x 140 x 6 cheeks; 16 H7 through seats, centres (30,110)/(110,110); two 10 mm string ports')
for i,(xx,y) in enumerate([(30,110),(110,110)]):
 sh=cyl(2.5,96,xx,y,-44);sh.translate(OFF);part('P_Shaft_'+str(i),sh,pluck)
 for j,z in enumerate([.5,36.5]):
  sh=cyl(8,5,xx,y,z).cut(cyl(2.5,7,xx,y,z-1));sh.translate(OFF);part('P_625Bearing_'+str(i)+'_'+str(j),sh,pluck)
for x in [10,130]:
 for y in [10,130]:
  sh=cyl(4,30,x,y,6).cut(cyl(2.25,32,x,y,5));sh.translate(OFF);part('P_Spacer_'+str(x)+'_'+str(y),sh,pluck)
Q,O0,pa,pb,beta=linkage(0)
# Crank is a blind-bore two-sided disk: pin and shaft holes cannot break into each other.
crank=cyl(10,12).cut(cyl(2.5,6)).cut(cyl(1.5,4,4,0,8))
o=part('P02_BlindCrank',crank,pluck,(.68,.52,.22),local=crank,description='20 OD x 12 crank; rear 5 H7 blind depth 6; front 3 pin blind depth 4 at 4 radius; 2 mm separating web. Shaft clamp thread to detail.')
o.Placement=A.Placement(OFF+V(*Q,46),A.Rotation())
# Rocker hub/pin lever, both through bores safely separated by 14 mm.
rock=box(14,10,6,0,-5).fuse(cyl(7,6)).fuse(cyl(5,6,14,0)).cut(cyl(2.5,8,0,0,-1)).cut(cyl(1.5,8,14,0,-1))
o=part('P03_Rocker',rock,pluck,(.68,.52,.22),local=rock,description='14 mm rocker pin centres; 5 shaft bore / 3 pin bore; separate shaft clamp to detail')
o.Placement=A.Placement(OFF+V(*O0,46),A.Rotation(V(0,0,1),math.degrees(beta)))
# POM plain-bearing coupling rod: bushes are the replaceable rod itself, retained on journal pins.
link=box(80,10,4,0,-5).fuse(cyl(5,4)).fuse(cyl(5,4,80,0)).cut(cyl(1.52,6,0,0,-1)).cut(cyl(1.52,6,80,0,-1))
o=part('P04_POMCoupler',link,pluck,(.85,.85,.79),local=link,description='POM-C; 80 +/-0.05 centres; 3.02 to 3.04 journal bores; 4 mm thick; replaceable dry plain bearing link')
o.Placement=A.Placement(OFF+V(*pa,62),A.Rotation(V(0,0,1),math.degrees(math.atan2(pb[1]-pa[1],pb[0]-pa[0]))))
# Pin reservations are clearly flagged, not falsely treated as complete standard parts.
for j,p in enumerate([pa,pb]):
 sh=cyl(1.5,14,*p,54);sh.translate(OFF);o=part('P_JournalPinReview_'+str(j),sh,pluck);o.addProperty('App::PropertyString','Status');o.Status='3 h6 journal with positive axial retention and hub attachment to detail; not an approved dowel substitution'
# Replaceable arms; installed long arm, high arm stored alongside. 0.5 mm pick overtravel is adjustable.
for i,r in enumerate([RLOW,RHIGH]):
 arm=box(6,r-1,3,-3,-(r-1)).fuse(cyl(7,3)).cut(cyl(2.5,5,0,0,-1))
 arm=arm.cut(cyl(1.7,5,0,-(r-5),-1))
 sh=arm.copy();sh.translate(OFF+V(110 if i==0 else 150,110,-35));part('P05_Arm_'+str(i),sh,pluck,(.23,.52,.48),local=arm,description=f'Removable aluminium arm; pivot-to-string {r:.6f}; body stops 1 mm short; final flexible pick and hub clamp to test')
# One string shown with the low-C3 bridge; high-D5 configuration is a swap, not simultaneous play.
y=110-RLOW
s=cyl(.4,342,0,0,0);s.rotate(V(),V(0,1,0),0);s.translate(OFF+V(110,y,-70));part('P_NylonString',s,pluck,(.83,.81,.71))
for j,z in enumerate([-74,272]):
 sh=box(40,125,4,90,0,z)
 for yy in [110-RLOW,110-RHIGH]:sh=sh.cut(cyl(2.25,6,110,yy,z-1))
 for x in [95,125]:sh=sh.cut(cyl(2.25,6,x,8,z-1))
 sh.translate(OFF);part('P06_EndPost_'+str(j),sh,pluck,local=None)
# Quote candidate plate only, string anchor/tuning details intentionally excluded from release.
meta=d.addObject('App::FeaturePython','PrototypeScope');meta.addProperty('App::PropertyString','Status');meta.Status='Two independent test fixtures; manual input first. Quotation geometry only. Purchased pulley envelopes, pin retention, shaft clamps, pick and string anchoring remain release gates.'
meta.addProperty('App::PropertyBool','PhysicalTestPassed');meta.PhysicalTestPassed=False
meta.addProperty('App::PropertyString','Ratio');meta.Ratio='(60/20)*(30/20)=9/2; 3 rpm input -> 13.5 rpm crank'
d.recompute();invalid=[o.Name for o in d.Objects if o.TypeId=='Part::Feature' and not o.Shape.isValid()];assert not invalid,invalid
v=G.getDocument(d.Name).activeView();v.viewAxonometric();v.fitAll()
d.saveAs(str(OUT/'Lovophone_Prototype_A.FCStd'))
Part.makeCompound([o.Shape for o in d.Objects if o.TypeId=='Part::Feature']).exportStep(str(OUT/'Prototype_A_Assembly_REFERENCE.step'))
(OUT/'Prototype_A_Custom_Parts.json').write_text(json.dumps(custom,indent=2));print('Prototype saved; valid solids; custom quote candidates:',len(custom),flush=True)
