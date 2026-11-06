import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,json
from FreeCAD import Vector as V
O=(_LOVOPHON_WORKSPACE + '/outputs');d=App.openDocument(O+'/Harpe_d_Amour_Twelve_Electric.FCStd')
def cy(r,h,p,axis=V(1,0,0)):return Part.makeCylinder(r,h,p,axis)
def bx(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
for n,x in [('IntermediateAxleStand0',-26.65),('IntermediateAxleStand1',282)]:
 o=d.getObject(n);s=o.Shape.copy();s.translate(V(x-s.BoundBox.XMin,0,0));o.Shape=s
d.CommonIntermediateAxle.Shape=cy(3,320,V(-27.65,-59,-116))
d.ElectricShaftCoupling.Shape=cy(5,17.2,V(286,-83,-131)).cut(cy(3.05,11.2,V(285,-83,-131))).cut(cy(1.55,8,V(296.2,-83,-131)))
shield=d.addObject('Part::Feature','ElectricCouplingShield');shield.Shape=cy(7,18.2,V(285,-83,-131)).cut(cy(6,20.2,V(284,-83,-131)));shield.Label='Clear sleeve around the removable shaft coupling';d.ElectricDrive.addObject(shield)
d.ElectricClearTop.Shape=bx(32,2,40,307,-74,-154);d.ElectricClearRear.Shape=bx(32,35,2,307,-109,-154);d.ElectricClearFront.Shape=bx(32,35,2,307,-109,-116).cut(cy(2.2,4,V(321.5,-97.5,-117),V(0,0,1)))
br=d.ElectricMotorBracket.Shape.copy()
for n in ['GantryRightFoot0','GantryRightFoot1']:br=br.cut(d.getObject(n).Shape)
d.ElectricMotorBracket.Shape=br
d.recompute();assert all(o.Shape.isValid() for o in d.Objects if o.TypeId=='Part::Feature');d.save()
colors=json.load(open(O+'/../work/motor_colors.json'));colors['ElectricCouplingShield']=[.66,.84,.88];json.dump(colors,open(O+'/../work/motor_colors.json','w'))
print('Motor mount, coupling guard and gantry-foot clearances refined.')
