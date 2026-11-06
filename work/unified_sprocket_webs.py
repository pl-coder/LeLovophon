import Part,math
from FreeCAD import Vector as V
def open_web(sh,rp,bore,z):
 ri=max(bore+2,7);ro=rp-4.5
 if ro-ri<3:return sh
 cuts=[]
 for j in range(3):
  a=math.radians(j*120+12);b=math.radians(j*120+108);m=(a+b)/2
  def p(r,t):return V(r*math.cos(t),r*math.sin(t),z-1)
  w=Part.Wire([Part.Arc(p(ro,a),p(ro,m),p(ro,b)).toShape(),Part.makeLine(p(ro,b),p(ri,b)),Part.Arc(p(ri,b),p(ri,m),p(ri,a)).toShape(),Part.makeLine(p(ri,a),p(ro,a))]);cuts.append(Part.Face(w).extrude(V(0,0,4)))
 result=sh.cut(Part.makeCompound(cuts));assert result.isValid();return result
