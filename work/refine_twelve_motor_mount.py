import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part
from FreeCAD import Vector as V
O=(_LOVOPHON_WORKSPACE + '/outputs');d=App.openDocument(O+'/../work/Harpe_d_Amour_Twelve_Motor_Base.FCStd')
def cy(r,h,p,axis=V(1,0,0)):return Part.makeCylinder(r,h,p,axis)
def bx(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
d.CommonInputShaft_D6.Shape=cy(3,296-(-15.65),V(-15.65,-83,-131))
for n,x in [('LowInputStand1',277),('LowInputBearing1',278)]:
 o=d.getObject(n);s=o.Shape.copy();s.translate(V(x-s.BoundBox.XMin,0,0));o.Shape=s
d.ElectricShaftCoupling.Shape=cy(5,20.4,V(286,-83,-131)).cut(cy(3.05,11.2,V(285,-83,-131))).cut(cy(1.55,11.2,V(296.2,-83,-131)))
br=bx(3,34,22,303.4,-109,-142).cut(cy(2.1,5,V(302.4,-83,-131))).fuse(bx(34,3,26,303.4,-109,-144))
for x in [310,331]:br=br.cut(cy(1.7,5,V(x,-110,-140),V(0,1,0)))
d.ElectricMotorBracket.Shape=br
d.recompute();d.save();print('Coupling clearances and right input bearing position corrected.')
