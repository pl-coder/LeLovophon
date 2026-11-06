import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,math,json
from FreeCAD import Vector as V
OUT=(_LOVOPHON_WORKSPACE + '/outputs');doc=App.openDocument(OUT+'/Harpe_d_Amour_Low_Nylon.FCStd')
clock=doc.addObject('App::DocumentObjectGroup','Clockwork');clock.Label='Clockwork — WIND → SPRING → GEARS → HARP'
case=doc.addObject('App::DocumentObjectGroup','ClockworkClearCase');case.Label='Clear clockwork case — see the energy path';clock.addObject(case)
colors={}
def bx(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def cy(r,h,x,y,z):return Part.makeCylinder(r,h,V(x,y,z),V(1,0,0))
def add(n,s,label,col=(.72,.57,.26),group=clock):
 o=doc.addObject('Part::Feature',n);o.Shape=s;o.Label=label;group.addObject(o);colors[n]=col;return o
def gear(N,m,x,y,z,phase=0,width=3,spokes=True):
 rp=N*m/2;rb=rp*math.cos(math.radians(20));rr=rp-1.25*m;ra=rp+m;invp=math.tan(math.radians(20))-math.radians(20);half=math.pi/(2*N)-.025/(2*rp);pts=[]
 def pt(r,a):return V(x,y+r*math.cos(a),z+r*math.sin(a))
 def h(r):t=math.sqrt(max(0,(r/rb)**2-1));return half+invp-(t-math.atan(t))
 for k in range(N):
  a=phase+2*math.pi*k/N;basehalf=h(max(rb,rr));pts.append(pt(rr,a-basehalf))
  for j in range(7):r=max(rb,rr)+(ra-max(rb,rr))*j/6;pts.append(pt(r,a-h(r)))
  for j in range(1,5):pts.append(pt(ra,a-h(ra)+2*h(ra)*j/4))
  for j in range(1,7):r=ra-(ra-max(rb,rr))*j/6;pts.append(pt(r,a+h(r)))
  pts.append(pt(rr,a+basehalf));end=a+2*math.pi/N-basehalf
  for j in range(1,5):pts.append(pt(rr,(a+basehalf)+(end-a-basehalf)*j/4))
 s=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(width,0,0));s=s.cut(cy(3.1,width+2,x-1,y,z))
 if spokes and rp>8:
  for k in range(6):
   a=2*math.pi*k/6;r=rp*.6;s=s.cut(cy(rp*.23,width+2,x-1,y+r*math.cos(a),z+r*math.sin(a)))
 return s
# Large readable three-wheel train. Existing harp input remains coaxial with the output wheel.
for n,N,y,phase in [('ClockBarrelWheel',60,-35,0),('ClockIdlerWheel',24,-66.5,-math.pi/24),('ClockOutputWheel',20,-83,0)]:
 o=add(n,gear(N,.75,244,y,-131,phase),('2 — Spring barrel wheel, 60 teeth' if N==60 else '3 — Idler, 24 teeth' if N==24 else '4 — Output to harp, 20 teeth'))
 for p,k,v in [('Teeth','App::PropertyInteger',N),('Module','App::PropertyLength',.75),('PressureAngle','App::PropertyAngle',20)]:o.addProperty(k,p,'Gear');setattr(o,p,v)
# The contained spring barrel has a steel rim/rear and a transparent inspection face.
add('ClockSpringBarrel',cy(20,17,247,-35,-131).cut(cy(18.7,17,248,-35,-131)),'2 — Contained mainspring cartridge; load-rated specification pending',(.43,.46,.48))
add('ClockBarrelHub',cy(4,20,244,-35,-131).cut(cy(2.6,22,243,-35,-131)),'Barrel hub — outer spring end drives wheel')
add('ClockBarrelInspectionFace',cy(18.7,1.5,264,-35,-131).cut(cy(2.7,4,263,-35,-131)),'Clear barrel inspection face — educational cartridge envelope',(.66,.84,.88),case)
# Illustrative spiral ribbon: no spring material, energy capacity or life rating implied.
pts1=[];pts2=[]
for j in range(1001):
 a=2*math.pi*4.5*j/1000;r=4+13.9*j/1000
 pts1.append(V(250,-35+(r-.1)*math.cos(a),-131+(r-.1)*math.sin(a)))
 pts2.append(V(250,-35+(r+.1)*math.cos(a),-131+(r+.1)*math.sin(a)))
spiral=Part.Face(Part.makePolygon(pts1+list(reversed(pts2))+[pts1[0]])).extrude(V(9,0,0))
add('ClockMainspringIllustration',spiral,'2 — Spring stores winding energy — illustrative spiral',(.24,.28,.32))
add('ClockWindingArbor',cy(2.5,47,236,-35,-131).fuse(bx(6,4,4,283,-37,-133)),'1 — Winding arbor with 4 mm square key end',(.56,.59,.62))
# Ratchet and click prevent the winding arbor unwinding backwards.
pts=[]
for k in range(24):
 for r,a in [(9,2*math.pi*k/24),(10.5,2*math.pi*(k+.72)/24)]:pts.append(V(267,-35+r*math.cos(a),-131+r*math.sin(a)))
ratchet=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(2,0,0)).cut(cy(2.55,4,266,-35,-131));add('ClockWindingRatchet',ratchet,'1 — Winding ratchet')
click=Part.Face(Part.makePolygon([V(267,-20,-117),V(267,-22,-119),V(267,-29,-123),V(267,-27,-121),V(267,-20,-117)])).extrude(V(2,0,0)).fuse(cy(2,2,267,-20,-117)).cut(cy(.9,4,266,-20,-117));add('ClockWindingClick',click,'1 — Ratchet click — anti-return detail pending',(.34,.38,.42))
add('ClockClickPivot',cy(.85,8,264,-20,-117),'Click pivot',(.55,.58,.61))
# Output extension joins the existing coaxial input; bearings are held by the two clear structural plates.
add('ClockOutputArbor',cy(3,51,230.35,-83,-131),'4 — Clockwork output shaft → existing common belt axle',(.56,.59,.62))
add('ClockInputCoupling',cy(5,10,229,-83,-131).cut(cy(3.05,12,228,-83,-131)),'4 — Removable split-coupling envelope',(.42,.45,.48))
add('ClockIdlerArbor',cy(2,42,238,-66.5,-131),'Idler arbor',(.56,.59,.62))
# Balance / lever escapement is a visible regulation concept, not a resolved pallet design.
pts=[]
for k in range(20):
 for rad,a in [(10.7,2*math.pi*k/20),(12.2,2*math.pi*(k+.70)/20),(10.7,2*math.pi*(k+.86)/20)]:pts.append(V(271,-83+rad*math.cos(a),-131+rad*math.sin(a)))
escape=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(1.5,0,0)).cut(cy(3.05,3.5,270,-83,-131));add('ClockEscapeWheel',escape,'5 — Escapement wheel; pallet geometry and load sizing pending')
# Bridge supports a small balance above the escapement, behind the main wheel plane.
add('ClockBalanceBridge',bx(3,5,29,276,-63,-143).fuse(bx(3,16,4,276,-63,-143)),'5 — Balance bridge',(.55,.58,.61))
balance=cy(10,1.5,273.5,-52,-119).cut(cy(8.5,3.5,272.5,-52,-119)).fuse(bx(1.5,18,1.4,273.5,-61,-119.7)).fuse(bx(1.5,1.4,18,273.5,-52.7,-128)).fuse(cy(2,1.5,273.5,-52,-119));add('ClockBalanceWheel',balance,'5 — Balance oscillates to meter the release of energy')
add('ClockBalanceStaff',cy(.8,8,272,-52,-119),'Balance staff',(.55,.58,.61))
pts1=[];pts2=[]
for j in range(401):
 a=2*math.pi*3*j/400;r=2+4*j/400;pts1.append(V(276,-52+(r-.045)*math.cos(a),-119+(r-.045)*math.sin(a)));pts2.append(V(276,-52+(r+.045)*math.cos(a),-119+(r+.045)*math.sin(a)))
add('ClockHairspringIllustration',Part.Face(Part.makePolygon(pts1+list(reversed(pts2))+[pts1[0]])).extrude(V(.25,0,0)),'5 — Hairspring illustration; rate and attachments pending',(.25,.35,.44))
lever=bx(1.2,12,2,273,-71,-130).fuse(bx(1.2,2,16,273,-72,-139)).fuse(cy(2,1.2,273,-66,-129));add('ClockEscapementLever',lever,'5 — Escapement lever and pallets — functional geometry unresolved',(.44,.47,.49))
# Clear clockwork-only enclosure: open instrument remains otherwise unchanged.
for n,x in [('ClockClearLeftPlate',235),('ClockClearRightPlate',280)]:
 plate=bx(3,102,53,x,-109,-157)
 for y,z,rad in [(-35,-131,2.7),(-66.5,-131,2.2),(-83,-131,3.2)]:plate=plate.cut(cy(rad,5,x-1,y,z))
 add(n,plate,'Clear clockwork end plate',(.66,.84,.88),case)
for n,s in [('ClockClearBack',bx(48,102,2,235,-109,-157)),('ClockClearFront',bx(48,102,2,235,-109,-106)),('ClockClearTop',bx(48,2,53,235,-9,-157))]:add(n,s,'Clear clockwork case — removable panel',(.66,.84,.88),case)
for y,z in [(-103,-151),(-103,-110),(-14,-151),(-14,-110)]:add('ClockCasePillar_'+str(abs(y))+'_'+str(abs(z)),cy(2,42,238,y,z),'Clockwork plate spacer',(.56,.59,.62))
add('ClockModuleFoot',bx(48,4,53,235,-109,-157),'Removable clockwork module foot',(.36,.39,.42))
# A removable pierced butterfly key: fluted collar, twin open bows and scalloped rims.
key=cy(5,17,285,-35,-131).cut(bx(12,4.2,4.2,284,-37.1,-133.1)).fuse(cy(7,2,298,-35,-131))
bow=cy(6,4,302,-35,-131)
for z in [-144,-118]:
 ring=cy(12,4,302,-35,z).cut(cy(8.2,6,301,-35,z))
 for k in range(12):
  a=2*math.pi*k/12;ring=ring.fuse(cy(1.7,4,302,-35+11.5*math.cos(a),z+11.5*math.sin(a)))
 bow=bow.fuse(ring)
key=key.fuse(bow).removeSplitter();add('AntiquePiercedWindingKey',key,'1 — Removable antique brass winding key — pierced butterfly bow',(.73,.52,.20))
# Native metadata makes the educational scope explicit.
clock.addProperty('App::PropertyString','PowerPath','Educational design');clock.PowerPath='Key → winding arbor / ratchet → contained mainspring barrel → 60T wheel → 24T idler → 20T output → harp belt axle. Balance escapement regulates output in the proposed architecture.'
clock.addProperty('App::PropertyString','ValidationScope','Educational design');clock.ValidationScope='Geometric educational layout. Not a working clock movement: spring capacity, click engagement, pallet locking/impulse, oscillator, torque budget, output clutch and structural containment must be engineered before manufacture.'
clock.addProperty('App::PropertyFloat','BarrelToOutputSpeedRatio','Educational design');clock.BarrelToOutputSpeedRatio=3
clock.addProperty('App::PropertyString','Materials','Educational design');clock.Materials='Brass wheel/key appearance; steel spring cartridge/arbors; transparent polycarbonate case intent, thickness and load rating unverified.'
doc.Motion.Status='Low nylon harp with transparent educational clockwork concept and antique key. Existing harp kinematics unchanged; clockwork is a layout study requiring a resolved spring/escapement and torque budget.'
doc.Label="L’Harpe d’Amour — see-through clockwork and antique key"
doc.recompute();invalid=[o.Name for o in doc.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())];assert not invalid,invalid
path=OUT+'/Harpe_d_Amour_Clockwork.FCStd';doc.saveAs(path)
json.dump(colors,open(OUT+'/../work/clockwork_colors.json','w'))
json.dump({'power_path':clock.PowerPath,'scope':clock.ValidationScope,'existing_harp_geometry_unchanged':True,'new_shapes':list(colors),'invalid_shapes':invalid},open(OUT+'/clockwork_design_check.json','w'),indent=2)
print('Saved clockwork concept:',len(colors),'new valid shapes',flush=True)
