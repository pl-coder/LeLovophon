import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
exec(open((_LOVOPHON_WORKSPACE + '/work/finish_prototype_a.py')).read().split('cr=cy(')[0])
for j,z in enumerate([-74,272]):
 ob=d.getObject('P06_EndPost_'+str(j));s=ob.Shape.copy()
 for yy in [110-RLOW,110-RHIGH]:
  s=s.cut(cy(2.25,6,350,yy,z-1)).cut(cy(2,6,330,yy,z-1))
 ob.Shape=s
 if j==0:
  local=s.copy();local.translate(-OFF-V(90,0,z));local.exportStep(str(OUT/'P06_EndPost.step'))
bar=bx(32,12,10,-16,-6,0).cut(cy(1.65,12,10,0,-1)).cut(cy(2.1,12,-10,0,-1)).cut(cy(1,14,0,-7,5,V(0,1,0)))
bar.exportStep(str(OUT/'P08_TensionDrawbar.step'))
for i,(zz,yy) in enumerate([(-88,110-RLOW),(290,110-RLOW)]):
 ob=d.addObject('Part::Feature','P_TensionDrawbar_'+str(i));ob.Shape=bar;ob.Placement=A.Placement(OFF+V(110,yy,zz),A.Rotation());d.Pluck_Test.addObject(ob);ob.ViewObject.ShapeColor=(.68,.52,.22)
 ob=d.addObject('Part::Feature','P_TensionGuide_'+str(i));ob.Shape=cy(2,50,330,yy,zz-10);d.Pluck_Test.addObject(ob)
base=bx(140,12,400,230,-12,-90);ob=d.addObject('Part::Feature','P_PlywoodTestBase');ob.Shape=base;d.Pluck_Test.addObject(ob);ob.ViewObject.ShapeColor=(.55,.34,.17)
d.recompute();d.save();Part.makeCompound([o.Shape for o in d.Objects if o.TypeId=='Part::Feature']).exportStep(str(OUT/'Prototype_A_Assembly_REFERENCE.step'))
print('String posts and guided M4 tension drawbars saved; base angle mounting to drawing.',flush=True)
