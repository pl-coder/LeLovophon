import FreeCAD as A,FreeCADGui as G,Part,json,math
from FreeCAD import Vector as V
from PySide import QtWidgets
from prototype_a_math import *
q=QtWidgets.QApplication.instance() or QtWidgets.QApplication([]);G.showMainWindow();G.getMainWindow().hide()
d=A.openDocument(str(OUT/'Lovophone_Prototype_A.FCStd'));OFF=V(230,0,0)
def cy(r,h,x=0,y=0,z=0,axis=V(0,0,1)):return Part.makeCylinder(r,h,V(x,y,z),axis)
def bx(w,h,t,x=0,y=0,z=0):return Part.makeBox(w,h,t,V(x,y,z))
def clamp(sh,r=9):
 sh=sh.cut(bx(.8,r+1,6,-.4,0,0))
 sh=sh.cut(cy(1.25,2*r,-r,6,3,V(1,0,0)))
 sh=sh.cut(cy(1.7,r,-r,6,3,V(1,0,0)))
 return sh
cr=cy(10,12).cut(cy(2.5,6)).cut(cy(1.25,4,4,0,8));cr=clamp(cr,10)
d.P02_BlindCrank.Shape=cr;cr.exportStep(str(OUT/'P02_BlindCrank.step'))
rock=bx(14,10,6,0,-5).fuse(cy(9,12)).fuse(cy(5,12,14,0)).cut(cy(2.5,14,0,0,-1)).cut(cy(1.25,4,14,0,8));rock=clamp(rock)
d.P03_Rocker.Shape=rock;rock.exportStep(str(OUT/'P03_Rocker.step'))
for i,r in enumerate([RLOW,RHIGH]):
 sh=bx(6,r-1,3,-3,-(r-1)).fuse(cy(9,8)).cut(cy(2.5,10,0,0,-1)).cut(cy(1.7,5,0,-(r-5),-1));sh=clamp(sh)
 d.getObject('P05_Arm_'+str(i)).Shape=sh;sh.exportStep(str(OUT/('P05_Arm_'+str(i)+'.step')))
for i,(xx,y) in enumerate([(260,110),(340,110)]):d.getObject('P_Shaft_'+str(i)).Shape=cy(2.5,96,xx,y,-44)
# Identical threaded journal pins. Threads drawn at minor/pilot diameters, specified in drawings.
q0,o,pa,pb,beta=linkage(0)
pin=cy(1.5,4,0,0,-4).fuse(cy(2.5,1)).fuse(cy(1.5,9,0,0,1)).fuse(cy(1,3,0,0,10))
pin.exportStep(str(OUT/'P07_JournalPin.step'))
for i,p in enumerate([pa,pb]):
 obj=d.getObject('P_JournalPinReview_'+str(i));obj.Shape=pin;obj.Placement=A.Placement(OFF+V(*p,58),A.Rotation());obj.Label='P07 — threaded journal pin, 3 h6 x 9, M3 root / M2 tip';obj.Status='Custom turned steel pin. M3 x4 root, 5 x1 flange, 3 h6 x9 journal, M2 x3 end; threads per drawing. 3 mm + 1.9 mm spacers retain 4 mm POM link with 0.1 mm axial float.'
for i,r in enumerate([RLOW,RHIGH]):
 s=bx(6,7.3,.5,-3,-(r+.3)).cut(cy(1.7,2,0,-(r-5),-.5))
 s.translate(OFF+V(110 if i==0 else 150,110,-32))
 ob=d.addObject('Part::Feature','P_Pick_'+str(i));ob.Shape=s;d.Pluck_Test.addObject(ob);ob.ViewObject.ShapeColor=(.9,.75,.4)
# Retainers for pluck bearings, same 27 mm disk, with screw positions at +/-11.
ret=cy(13.5,1).cut(cy(4,3,0,0,-1))
for x in [-11,11]:ret=ret.cut(cy(1.1,3,x,0,-1))
for side,z in enumerate([0,36]):
 ob=d.getObject('P01_LinkageCheek_'+str(side));s=ob.Shape.copy()
 for xx,y in [(260,110),(340,110)]:
  for dx in [-11,11]:s=s.cut(cy(.8,8,xx+dx,y,z-1))
 ob.Shape=s
 for j,(xx,y) in enumerate([(260,110),(340,110)]):
  for k,rz in enumerate([z-1,z+6]):
   rr=ret.copy();rr.translate(V(xx,y,rz));obj=d.addObject('Part::Feature','P_BearingRetainer_'+str(side)+'_'+str(j)+'_'+str(k));obj.Shape=rr;d.Pluck_Test.addObject(obj)
# Export corrected local cheek with retainer screw pilots.
s=d.P01_LinkageCheek_0.Shape.copy();s.translate(-OFF);s.exportStep(str(OUT/'P01_LinkageCheek_0.step'))
d.recompute();bad=[o.Name for o in d.Objects if o.TypeId=='Part::Feature' and not o.Shape.isValid()];assert not bad,bad
d.save();Part.makeCompound([o.Shape for o in d.Objects if o.TypeId=='Part::Feature']).exportStep(str(OUT/'Prototype_A_Assembly_REFERENCE.step'))
print('Finished clamps, positive pin retention, flexible pick reservations and bearing retainers. Valid solids.',flush=True)
