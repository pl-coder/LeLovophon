import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,math,json,ast
from FreeCAD import Vector as V
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
doc=App.openDocument(OUT+'/Harpe_d_Amour_Portable.FCStd');rows=json.loads(doc.Motion.LinkageGeometry)
code=ast.parse(open(OUT+'/Animate_Open_Harpe.FCMacro').read());exec(compile(ast.Module(body=[n for n in code.body if isinstance(n,ast.FunctionDef) and n.name in ['harpe_live_beta','harpe_live_roots']],type_ignores=[]),'motion','exec'))
def bx(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def cy(r,h,p,axis=V(1,0,0)):return Part.makeCylinder(r,h,p,axis)
def rod(p,q,r=.4):v=q-p;return cy(r,v.Length,p,v)
def add(name,sh,g,label=None):
 o=doc.getObject(name) or doc.addObject('Part::Feature',name);o.Shape=sh;g.addObject(o)
 if label:o.Label=label
 return o
def tri(pts,depth):return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,depth))
def strap(x,y1,z1,y2,z2):
 d=V(0,y2-y1,z2-z1);d.normalize();p=V(0,-d.z,d.y)*3;a=V(x,y1,z1);b=V(x,y2,z2)
 return Part.Face(Part.makePolygon([a+p,b+p,b-p,a-p,a+p])).extrude(V(4,0,0))
def quarter_string(x,z,side):
 start=V(x,-91,z);mid=V(x+side*6/math.sqrt(2),-97+6/math.sqrt(2),z);end=V(x+side*6,-97,z)
 path=Part.Wire([Part.Arc(start,mid,end).toShape()]);profile=Part.Wire(Part.makeCircle(.4,start,V(1,0,0)))
 return path.makePipeShell([profile],True,False)
g=doc.addObject('App::DocumentObjectGroup','NylonEndTensioners');g.Label='Over-edge guides, tied nylon anchors and screw-pull tensioners'
Y=-91
for r in rows:
 n=r['note'];s=r['station'];z=r['pivot_z'];left=320-r['speaking_length'];r['pivot_y']-=18;r['follower_y']-=18
 D=(V(0,r['follower_y'],r['follower_z'])-V(0,-59,-116)).Length;r['lever_length']=D
 vals=[harpe_live_beta(r,math.radians(j*.5)) for j in range(720)];ref=vals[0];vals=[ref+math.atan2(math.sin(b-ref),math.cos(b-ref)) for b in vals];r['beta_mid']=(max(vals)+min(vals))/2;r['swing_half_angle_deg']=math.degrees((max(vals)-min(vals))/2)*4
 fy=r['follower_y'];fz=r['follower_z'];uy=r['pivot_y']
 doc.getObject(n+'_FollowerLever').Shape=bx(2.5,4,D,8.75,-2,0).fuse(cy(6,2.5,V(8.75,0,0))).fuse(cy(4,2.5,V(8.75,0,D))).cut(cy(3.05,4.5,V(7.75,0,0)))
 doc.getObject(n+'_FollowerRoller').Shape=cy(3,3,V(5.25,0,D)).cut(cy(1.05,5,V(4.25,0,D)));doc.getObject(n+'_RollerPin').Shape=cy(1,6,V(5.25,0,D))
 for j,off in enumerate([-5.5,0]):
  x=s+off;shape=bx(4,uy+119,8,x,-109,-154).fuse(bx(4,20,z+164,x,uy-10,-154))
  if j==0:shape=shape.fuse(strap(x,-65,-150,uy-8,z-12))
  shape=shape.cut(cy(6.05,6,V(x-1,uy,z))).cut(cy(6.05,6,V(x-1,uy,fz)))
  doc.getObject(n+'_PendulumBracket'+str(j)).Shape=shape
  for suffix in ['_PendulumBearing','_FollowerPivotBearing']:
   o=doc.getObject(n+suffix+str(j));sh=o.Shape.copy();sh.translate(V(0,-18,0));o.Shape=sh
 o=doc.getObject(n+'_SwingStepUpBelt');sh=o.Shape.copy();sh.translate(V(0,-18,0));o.Shape=sh
 for kind,p in harpe_live_roots(r,0).items():doc.getObject(n+'_'+kind).Placement=p
 doc.getObject(n+'_KotoSpeakingString').Shape=rod(V(left,Y,z),V(320,Y,z));doc.getObject(n+'_KotoBackString').Shape=rod(V(-22,Y,z),V(left,Y,z))
 st=doc.getObject(n+'_KotoSpeakingString')
 for prop,kind,val in [('StringMaterial','App::PropertyString','Unwound nylon; nominal 0.8 mm study diameter, final gauge/tension to be selected.'),('NominalDiameter','App::PropertyLength',.8),('SoundboardClearance','App::PropertyLength',18)]:
  if prop not in st.PropertiesList:st.addProperty(kind,prop,'String design')
  setattr(st,prop,val)
 # Low removable third bridge, with a rounded replaceable crown and relieved feet.
 bridge=tri([V(left-6,-109,z-3),V(left,Y-.6,z-3),V(left+6,-109,z-3)],6)
 window=tri([V(left-2.8,-106,z-4),V(left,Y-6,z-4),V(left+2.8,-106,z-4)],8)
 doc.getObject(n+'_KotoThirdBridge').Shape=bridge.cut(window)
 add(n+'_NylonBridgeCrown',cy(.65,6,V(left,Y-.65,z-3),V(0,0,1)),doc.getObject(n+'_KotoStringModule'),n+' rounded third-bridge crown')
 for tag,x in [('Anchor',-22),('Tuner',320)]:
  for suffix in ['Saddle','Pin','Tail']:
   o=doc.getObject(n+'_Koto'+tag+suffix)
   if o:doc.removeObject(o.Name)
 # The end guide carries a 6 mm string-path radius; the nylon leaves without a sharp edge.
 for side,x in [(-1,-30),(1,340)]:
  cap=cy(5.6,7,V(x,-97,z-3.5),V(0,0,1))
  add(n+('_Left' if side<0 else '_Right')+'NylonGuide',cap,g,n+' polished rounded nylon end guide — nominal 6 mm path radius')
  p=V(-22 if side<0 else 320,Y,z);q=V(x,Y,z)
  add(n+('_Left' if side<0 else '_Right')+'NylonOverEdge',rod(p,q).fuse(quarter_string(x,z,side)).fuse(rod(V(x+side*6,-97,z),V(x+side*6,-129,z))),g)
 # Tie-on shuttle, translated by an M4 screw along an external 20 mm working stroke.
 shuttle=bx(10,6,6,344,-133,z-3).fuse(bx(4,6,3.6,342,-133,z-1.8))
 shuttle=shuttle.cut(cy(1.7,8,V(351,-134,z),V(0,1,0))).cut(cy(1.1,8,V(346,-130,z-4),V(0,0,1)))
 add(n+'_NylonTieShuttle',shuttle,g,n+' tie-on nylon shuttle — coarse hand pull, 20 mm screw adjustment')
 screw=cy(2,31,V(351,-153,z),V(0,1,0)).fuse(cy(4.2,4,V(351,-157,z),V(0,1,0)))
 add(n+'_NylonTensionScrew',screw,g,n+' M4 × 0.7 screw-pull tensioner — thread envelope')
 add(n+'_NylonTieKnotEnvelope',cy(1.2,2.2,V(-37.1,-130,z),V(1,0,0)),g,n+' tied nylon anchor knot — illustrative')
 print(n,'half swing',round(r['swing_half_angle_deg'],2),flush=True)
# Lower common load-bearing end blocks and retain the speaking endpoints.
for tag,x in [('Anchor',-22),('Tuner',320)]:
 doc.getObject('Koto'+tag+'Block').Shape=bx(16,16.4,76,x-8,-109,-93)
 doc.getObject('Koto'+tag+'SaddleRail').Shape=bx(4,1.2,70,x-2,-92.6,-90)
 for r in rows:add(r['note']+'_'+tag+'NylonSaddle',cy(.4,6,V(x,-91.4,r['pivot_z']-3),V(0,0,1)),doc.KotoEndSupports)
# Removable external end plates: loads return to the solid reinforced soundbox ends.
plate=bx(4,41,70,340,-153,-90).fuse(bx(16,4,70,340,-153,-90))
for r in rows:
 z=r['pivot_z'];plate=plate.cut(bx(6,27,4,339,-145,z-2)).cut(cy(2.2,6,V(351,-154,z),V(0,1,0)))
for y in [-119,-145]:
 for z in [-87,-23]:plate=plate.cut(cy(2.2,6,V(339,y,z)))
add('NylonTensionerEndPlate',plate,g,'Removable aluminium end plate and screw thrust shelf')
leftplate=bx(4,31,70,-38,-143,-90)
for r in rows:leftplate=leftplate.cut(cy(1.1,6,V(-39,-130,r['pivot_z'])))
for y in [-119,-139]:
 for z in [-87,-23]:leftplate=leftplate.cut(cy(2.2,6,V(-39,y,z)))
add('NylonAnchorEndPlate',leftplate,g,'Removable tied-string anchor plate')
# End-guide pedestal bars join the rounded guides to the reinforced end blocks.
add('NylonRightGuidePedestal',bx(10,12,70,330,-109,-90),g)
add('NylonLeftGuidePedestal',bx(8,12,70,-30,-109,-90),g)
doc.Motion.LinkageGeometry=json.dumps(rows)
doc.Motion.Status='Low 18 mm nylon string bed; lowered arm/follower pivots with recalculated cam linkage; over-edge rounded guides, tied left anchors and external M4 screw-pull shuttles. Thread, fastener retention, nylon grade, tension and compliant plucking remain prototype design.'
doc.Label="L’Harpe d’Amour — low nylon strings and end tensioners"
doc.recompute();invalid=[o.Name for o in doc.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())];assert not invalid,invalid
doc.saveAs(OUT+'/Harpe_d_Amour_Low_Nylon.FCStd')
json.dump({'rows':rows,'string_height_mm':18,'drop_mm':18,'nominal_nylon_diameter_mm':.8,'tensioner_type':'M4 screw pull, tied shuttle, 20 mm travel; coarse hand take-up before tying','status':doc.Motion.Status},open(OUT+'/low_nylon_geometry.json','w'),indent=2)
print('Saved low nylon version',flush=True)
