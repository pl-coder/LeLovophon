import FreeCAD as A,FreeCADGui as G,Part,math,json,csv
from FreeCAD import Vector as V
from PySide import QtWidgets
from slender_bank_math import *
q=QtWidgets.QApplication.instance() or QtWidgets.QApplication([]);G.showMainWindow();G.getMainWindow().hide()
OUT.mkdir(exist_ok=True);src=A.openDocument(str(ROOT/'outputs/Lovophone_Lab_Frame_Ratio_Review.FCStd'));d=A.newDocument('LeLovophonSlenderBank');d.Label='Le Lovophon — slender proportional pendulum bank — layout study'
groups={}
for name in ['SoundboxAndStrings','BaseFrame','SlenderFrame','PivotBank','Pendula']:
 groups[name]=d.addObject('App::DocumentObjectGroup',name)
def cy(r,h,p=V(),axis=V(1,0,0)):return Part.makeCylinder(r,h,p,axis)
def bx(w,h,t,p=V()):return Part.makeBox(w,h,t,p)
def tube(p,q,ro=2,ri=1):
 v=q-p;u=v/v.Length;return cy(ro,v.Length,p,v).cut(cy(ri,v.Length+2,p-u,v))
def bar(p,q,r):v=q-p;return cy(r,v.Length,p,v)
def add(n,s,g,col=(.7,.73,.76),label=None):
 o=d.addObject('Part::Feature',n);o.Shape=s;g.addObject(o);o.Label=label or n;o.ViewObject.ShapeColor=col;o.ViewObject.LineColor=(.13,.16,.17);o.ViewObject.DisplayMode='Flat Lines';return o
def children(g):
 out=[]
 for o in getattr(g,'Group',[]):
  if o.TypeId=='Part::Feature':out.append(o)
  else:out.extend(children(o))
 return out
keep={o.Name for name in ['FlatKotoStrings','NylonEndTensioners','KotoEndSupports'] for o in children(src.getObject(name)) if src.getObject(name)}
for o in src.Objects:
 if o.TypeId!='Part::Feature':continue
 if o.Name in keep or o.Name.startswith(('Soundbox','Baseplate','NylonLeftGuidePedestal','NylonRightGuidePedestal')) or o.Name in ['NylonTensionerEndPlate','NylonAnchorEndPlate','KotoAnchorBlock','KotoTunerBlock','KotoAnchorSaddleRail','KotoTunerSaddleRail']:
  sh=o.Shape.copy();sh.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());obj=add(o.Name,sh,groups['SoundboxAndStrings'],tuple(o.ViewObject.ShapeColor[:3]),o.Label)
 elif o.Name.startswith(('LabBaseTransom','LabBaseLongeron','LabBaseClamp','LabRearFoot')):
  add(o.Name,o.Shape.copy(),groups['BaseFrame'],tuple(o.ViewObject.ShapeColor[:3]),o.Label)
# Two straight4x1 rails above the non-collinear pivots.
x0=FIRST-6.25;x1=ROWS[-1]['station_x']-3.25
for i,zoff in enumerate([-10,8]):add('PivotSpine'+str(i),tube(V(*rail(x0,zoff)),V(*rail(x1,zoff))),groups['SlenderFrame'])
for i,(x,y) in enumerate([(FIRST-16,rail(x0)[1]),(ROWS[-1]['station_x']+14,rail(x1)[1])]):
 for j,z in enumerate([-94,44]):
  add(f'EndPost{i}_{j}',tube(V(x,-109,z),V(x,y,z)),groups['SlenderFrame'])
  foot=bx(14,3,6,V(x-7,-112,z-3))
  for dx in [-5,5]:foot=foot.cut(cy(1.7,5,V(x+dx,-113,z),V(0,1,0)))
  add(f'PostFoot{i}_{j}',foot,groups['SlenderFrame'])
 add('EndCrosshead'+str(i),tube(V(x,y,-94),V(x,y,44)),groups['SlenderFrame'])
 add('EndDiagonal'+str(i),tube(V(x,-99,-94),V(x,y,44),1.5,.75),groups['SlenderFrame'])
 endx=x0 if i==0 else x1
 for j,zoff in enumerate([-10,8]):
  p=V(*rail(endx,zoff));add(f'SpineEndTie{i}_{j}',tube(V(x,y,p.z),p),groups['SlenderFrame'])
# Each moving rotor fits a thin axial slab; supports are entirely behind it.
for r in ROWS:
 n='V%02d'%r['index'];s=r['station_x'];py=r['pivot_y'];z=r['string_z'];P=V(s,py,z);R=r['arm_radius']
 for j,xoff in enumerate([-7.5,-4.5]):
  xx=s+xoff;C=V(xx,py,z)
  bearing=cy(3,2.5,C).cut(cy(1.5,4.5,C-V(1,0,0)))
  add(n+'_Bearing'+str(j),bearing,groups['PivotBank'],(.2,.23,.25))
  fork=cy(5,2.5,C).cut(cy(3.01,4.5,C-V(1,0,0)))
  midx=xx+1.25
  for zo in [-10,8]:
   p=V(*rail(midx,zo));v=p-V(midx,py+4,z)
   strip=bar(V(midx,py+4,z),p,1.25).common(bx(2.5,100,100,V(xx,py-10,z-50)))
   fork=fork.fuse(strip)
  add(n+'_Fork'+str(j),fork,groups['PivotBank'])
 shaft=cy(1.5,14.5,V(s-9,py,z));add(n+'_PivotShaft',shaft,groups['PivotBank'])
 rotor=d.addObject('App::Part',n+'_Rotor');groups['Pendula'].addObject(rotor);rotor.Label=r['note']+' — proportional109 mm base arm'
 hub=cy(5,4).cut(cy(1.5,6,V(-1,0,0)))
 # M3 socket-head clamp provision, local radial slit above the hanging arm.
 hub=hub.cut(bx(6,.6,5,V(-1,-.3,-5))).cut(cy(1.25,12,V(2,-6,-3.5),V(0,1,0))).cut(cy(1.7,6,V(2,-6,-3.5),V(0,1,0)))
 hub.rotate(V(),V(1,0,0),90)
 add(n+'_Hub',hub,rotor,(.65,.49,.24))
 arm=tube(V(2,0,4),V(2,0,R-1.2),2,1);add(n+'_TubeArm',arm,rotor,(.2,.48,.43))
 head=cy(2.75,3,V(2,-6,-3.5),V(0,1,0));head.rotate(V(),V(1,0,0),90);add(n+'_ClampHeadEnvelope',head,rotor)
 # Replaceable tip collar and tapered flexible sheet; fastening remains a prototype detail.
 collar=tube(V(2,0,R-6),V(2,0,R-2),3,2.05);add(n+'_PickSocket',collar,rotor,(.65,.49,.24))
 pts=[V(1.75,-3,R-6),V(1.75,3,R-6),V(1.75,.5,R-.15),V(1.75,-.5,R-.15)]
 pick=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(.5,0,0));add(n+'_FlexiblePick',pick,rotor,(.82,.77,.58))
 rotor.Placement=A.Placement(P,A.Rotation(V(1,0,0),90))
 for k,t,v in [('PitchAndDriveRatio','App::PropertyString',r['ratio']),('ArmRadius','App::PropertyLength',R),('TargetHalfSwing','App::PropertyAngle',HALF_SWING)]:rotor.addProperty(t,k,'Layout');setattr(rotor,k,v)
meta=d.addObject('App::FeaturePython','DesignStatus');meta.addProperty('App::PropertyString','Scope');meta.Scope='Upper bank layout only: proportional longer arms, miniature pivots, wider sweep, slim shared rails. Full12-voice drive is not installed or validated. Pick sockets, fork clamps and fits need manufacture/test detailing.'
meta.addProperty('App::PropertyBool','PhysicalTestPassed');meta.PhysicalTestPassed=False;meta.addProperty('App::PropertyBool','DrivetrainInstalled');meta.DrivetrainInstalled=False
meta.addProperty('App::PropertyString','PitchAndTiming');meta.PitchAndTiming='Original exact pentatonic pitch/drive ratios retained as targets;480 second ideal phase repeat at3 rpm.'
d.recompute();bad=[o.Name for o in d.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())];assert not bad,bad
v=G.getDocument(d.Name).activeView();v.viewAxonometric();v.fitAll();d.saveAs(str(OUT/'LeLovophon_Slender_Bank.FCStd'))
meshes=[];shapes=[];bounds=A.BoundBox()
for o in d.Objects:
 if o.TypeId!='Part::Feature':continue
 sh=o.Shape.copy();sh.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());shapes.append(sh);bounds.add(sh.BoundBox);vv,tt=sh.tessellate(.3);meshes.append(dict(name=o.Name,vertices=[[p.x,p.y,p.z] for p in vv],triangles=tt,color=list(o.ViewObject.ShapeColor[:3])))
Part.makeCompound(shapes).exportStep(str(OUT/'LeLovophon_Slender_Bank.step'))
(ROOT/'work/slender_bank_mesh.json').write_text(json.dumps(meshes));rep=report();rep['envelope_mm']=[bounds.XLength,bounds.ZLength,bounds.YLength];rep['invalid_shapes']=bad;rep['part_count']=len(shapes);(OUT/'Slender_Bank_Layout.json').write_text(json.dumps(rep,indent=2))
with (OUT/'Slender_Bank_Dimensions.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=ROWS[0]);w.writeheader();w.writerows(ROWS)
print(json.dumps(dict(saved=True,envelope=rep['envelope_mm'],parts=len(shapes))),flush=True)
