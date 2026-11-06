import FreeCAD as A,Part,math,json
from FreeCAD import Vector as V
from prototype_a_math import *
d=A.openDocument(str(OUT/'Lovophone_Prototype_A.FCStd'))
d.P05_Arm_0.Shape=d.P05_Arm_1.Shape.copy()
sh=d.P_NylonString.Shape.copy();sh.translate(V(0,RLOW-RHIGH,0));d.P_NylonString.Shape=sh
# Exact algebraic closure sampled above; verify new CAD link and rigid arm swept geometry.
names=['P02_BlindCrank','P03_Rocker','P04_POMCoupler','P05_Arm_0'];objs=[d.getObject(n) for n in names];OFF=V(230,0,0)
fixed=[o for o in d.Pluck_Test.Group if o.TypeId=='Part::Feature' and o.Name not in names and not any(t in o.Name for t in ['JournalPin','Pick_','Arm_1'])]
clashes=set()
for j in range(144):
 q,o,a,b,beta=linkage(j*math.tau/144)
 poses=[A.Placement(OFF+V(*q,46),A.Rotation(V(0,0,1),j*360/144)),A.Placement(OFF+V(*o,46),A.Rotation(V(0,0,1),math.degrees(beta))),A.Placement(OFF+V(*a,62),A.Rotation(V(0,0,1),math.degrees(math.atan2(b[1]-a[1],b[0]-a[0])))),A.Placement(OFF+V(110,110,-35),A.Rotation(V(0,0,1),math.degrees(beta-MID)))]
 for ob,p in zip(objs,poses):
  sh=ob.Shape.copy();sh.Placement=p
  for f in fixed:
   if sh.BoundBox.intersect(f.Shape.BoundBox) and sh.common(f.Shape).Volume>1e-5:clashes.add((ob.Name,f.Name))
invalid=[o.Name for o in d.Objects if o.TypeId=='Part::Feature' and not o.Shape.isValid()]
r=dict(sampled_linkage_poses=144,invalid_shapes=invalid,moving_rigid_to_fixed_intersections=sorted(clashes),scope='Swept rigid link-to-fixed geometric check of pluck fixture. Excludes intended pins and deformable picks. Does not validate supplier pulley batch dimensions, motor torque, bearing fits under load, string anchors, or actual release. Base angle brackets and fasteners not fully represented.',physical_test_passed=False)
(OUT/'Prototype_A_High_Arm_Check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2),flush=True)
