import sys,math,json,hashlib,csv
from pathlib import Path
R=Path(__file__).resolve().parents[2]; O=R/'outputs/LeLovophon_Pluck_Layout_R5'; W=R/'work/pluck_r5'
sys.path.insert(0,str(W));from config import ROWS,OLD_ROWS,DRIVE,BEARINGS,OLD_BEARINGS
import FreeCAD as A,FreeCADGui as G,Part
from FreeCAD import Vector as V
from PySide import QtWidgets
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([]);G.showMainWindow();G.getMainWindow().hide()
src=R/'outputs/LeLovophon_Protokoto_R3/LeLovophon_Protokoto_R3.FCStd';d=A.openDocument(str(src));d.Label='Le Lovophon — balanced plucking layout R5 / unbuilt prototype'
old=d.getObject('FourCornerFrame');removed=[o.Name for o in old.Group]
for n in removed:d.removeObject(n)
d.removeObject(old.Name)
g=d.addObject('App::DocumentObjectGroup','CurvedRearFrame');g.Label='R4 — four curved ribs, one rear support line'
AL=(.66,.72,.75);ST=(.52,.58,.62);BLACK=(.13,.15,.16)
def cy(r,h,p,axis=V(1,0,0)):return Part.makeCylinder(r,h,p,axis)
def box(x,y,z,p):return Part.makeBox(x,y,z,p)
def ring(ro,ri,h,p,axis=V(1,0,0)):return cy(ro,h,p,axis).cut(cy(ri,h+2,p-axis,axis))
def add(n,sh,material='Aluminium',role='Frame',note='',col=AL):
 ob=d.addObject('Part::Feature',n);ob.Shape=sh.removeSplitter();g.addObject(ob);ob.ViewObject.ShapeColor=col
 for k,v in [('Motion','Fixed'),('Role',role),('DesignNote',note),('MaterialName',material)]:ob.addProperty('App::PropertyString',k);setattr(ob,k,v)
 ob.addProperty('App::PropertyInteger','Voice');ob.Voice=0
 return ob
# Flat-cut profiles lie in native YZ; sheet thickness is X.
def plate(x,t,pts,holes=()):
 wire=Part.makePolygon([V(x,*p) for p in pts+[pts[0]]]);s=Part.Face(wire).extrude(V(t,0,0))
 for y,z,r in holes:s=s.cut(cy(r,t+2,V(x-1,y,z)))
 return s
profiles={}
def cut_export(name,shape,x,t):
 cp=shape.copy();cp.translate(V(-x,0,0));Part.export([temporary(name,cp)],str(O/'Cutting_Preview'/f'{name}.step'))
 # Through profile from the planar X=0 face. All DXF entities in mm, (drawing X,Y)=(native Z,Y).
 face=max([f for f in cp.Faces if all(abs(v.Point.x)<1e-6 for v in f.Vertexes)],key=lambda f:f.Area)
 lines=['0','SECTION','2','HEADER','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','ENTITIES']
 for wire in face.Wires:
  # Closed edge segments/chorded curves: tessellated manufacturing preview, not kerf compensated.
  pts=[]
  for e in wire.OrderedEdges:
   p=e.discretize(Deflection=.015)
   if pts and (p[-1]-pts[-1]).Length<(p[0]-pts[-1]).Length:p.reverse()
   pts.extend(p[:-1])
  lines+=['0','LWPOLYLINE','100','AcDbEntity','8','CUT','100','AcDbPolyline','90',str(len(pts)),'70','1']
  for p in pts:lines+=['10',f'{p.z:.6f}','20',f'{p.y:.6f}']
 lines+=['0','ENDSEC','0','EOF'];(O/'Cutting_Preview'/f'{name}.dxf').write_text('\n'.join(lines)+'\n')
 profiles[name]=dict(thickness_mm=t,area_mm2=shape.Volume/t,bbox_mm=[shape.BoundBox.YLength,shape.BoundBox.ZLength],dxf_chord_tolerance_mm=.015)
def temporary(n,sh):
 # STEP export object is discarded immediately after the batch, never part of the delivered assembly.
 ob=d.addObject('Part::Feature','EXPORT_'+n);ob.Shape=sh;return ob

def cap(x,p,q,w,t):
 u=V(0,q[0]-p[0],q[1]-p[1]);u.normalize();n=V(0,-u.z,u.y)*w/2;a=V(x,*p);b=V(x,*q)
 return Part.Face(Part.makePolygon([a+n,b+n,b-n,a-n,a+n])).extrude(V(t,0,0)).fuse(cy(w/2,t,a)).fuse(cy(w/2,t,b))
def hexbody(r,h,p,axis=V(1,0,0)):
 pts=[V(0,r*math.cos(j*math.pi/3),r*math.sin(j*math.pi/3)) for j in range(7)];sh=Part.Face(Part.makePolygon(pts)).extrude(V(h,0,0))
 if axis!=V(1,0,0):sh.rotate(V(),V(1,0,0).cross(axis) if abs(axis.x)<.99 else V(0,0,1),math.degrees(math.acos(axis.x)))
 sh.translate(p);return sh

def bolt(n,p,length,diam,axis=V(1,0,0)):
 # Grip core and socket head; nominal metric clearances, thread form omitted.
 sh=cy(diam/2-.15,length,p,axis).fuse(cy(diam*.85,diam,p-axis*diam,axis))
 sh=sh.cut(hexbody(diam*.40,diam*.65,p-axis*diam,axis))
 return add(n,sh,'Steel','Fastener',col=ST)
def washer(n,p,diam,axis=V(1,0,0)):return add(n,ring(diam,2.65 if diam>4.5 else 2.15,1,p,axis),'Steel','Washer',col=ST)
def nut(n,p,diam,axis=V(1,0,0)):return add(n,hexbody(diam*.81,diam*.8,p,axis).cut(cy(diam/2+.1,diam+2,p-axis,axis)),'Steel','Fastener',col=ST)

# New-build body omits the abandoned R3 top-mounted gantry holes.
for name,rad in [('Soundboard_700x220x4',3.1),('RemovableBottom_700x220x4',5),('RearRim_700x52x12',2.2),('FrontRim_700x52x12',2.2)]:
 ob=d.getObject(name);bb=ob.Shape.BoundBox;stock=box(bb.XLength,bb.YLength,bb.ZLength,V(bb.XMin,bb.YMin,bb.ZMin));sh=ob.Shape
 for xx in [-333,-323,323,333]:
  for zz in [-124,84]:
   plug=cy(rad,80,V(xx,-180,zz),V(0,1,0)).common(stock)
   if not plug.isNull() and plug.Volume>1e-7:sh=sh.fuse(plug)
 ob.Shape=sh.removeSplitter();ob.DesignNote+=' R4: old gantry mounting holes omitted; rear feet attach through structural rim with crush sleeves and backing plates.'
# Four identical swept ribs. 8mm 5083 aluminium; curvature has no welded or bent joints.
def bez(t):
 P=[(-143,-153),(-65,-195),(43,-189),(65,-130)]
 return tuple(sum(math.comb(3,i)*(1-t)**(3-i)*t**i*P[i][j] for i in range(4)) for j in [0,1])
cs=[bez(i/100) for i in range(101)];a=[];b=[]
for i,p in enumerate(cs):
 u=cs[min(i+1,100)];v=cs[max(i-1,0)];dy=u[0]-v[0];dz=u[1]-v[1];ll=math.hypot(dy,dz);w=11+3*(1-i/100)**3
 a.append((p[0]-dz/ll*w,p[1]+dy/ll*w));b.append((p[0]+dz/ll*w,p[1]-dy/ll*w))
ribbon=a+b[::-1]
# SHF flange mounting holes lie on the shaft centreline,32mm apart.
mount=[(49,-125,2.75),(81,-125,2.75)]
xlist=[-210,-28,150,272]
def cap_profile(x,t):
 s=box(t,32,10,V(x,49,-130)).fuse(cy(5,t,V(x,49,-125))).fuse(cy(5,t,V(x,81,-125)))
 return s.fuse(cy(10,t,V(x,65,-125)))
backingcuts=[]
for i,x in enumerate(xlist,1):
 rib=plate(x,8,ribbon).fuse(cap(x,(-152,-151),(-128,-151),28,8)).fuse(cap(x,(49,-125),(81,-125),18,8)).fuse(cy(11,8,V(x,65,-125)))
 for y,z,r in [(65,-125,4.6),*mount,(-149,-151,2.75),(-128,-151,2.75)]:rib=rib.cut(cy(r,10,V(x-1,y,z)))
 ob=add(f'R4_CurvedRib_{i}',rib,note='8mm 5083 flat profile, identical x4. All holes are clearance holes. Deburr and round exposed edges; no precision bearing seat or welding in the rib.')
 if i==1:cut_export('R4_CurvedRib_8mm_x4',ob.Shape,x,8)
 # SHF8 stock flange clamp: catalogue envelope; purchased variant must be confirmed before cut release.
 # Plate face x+8; housing/base occupies x+8..18; flange mounting line is17.5mm behind shaft.
 flange=cap_profile(x+8,5)
 boss=cy(10,10,V(x+8,65,-125)).fuse(box(10,18,6,V(x+8,56,-139)))
 clamp=flange.fuse(boss).cut(cy(4.0,12,V(x+7,65,-125))).cut(box(12,1.2,15,V(x+7,64.4,-140)))
 for y,z,r in mount:clamp=clamp.cut(cy(r,12,V(x+7,y,z)))
 add(f'R4_SHF8_Clamp_{i}',clamp,role='ShaftClamp',note='Nominal SHF8 43x24x10mm;32mm M5 mounting pitch. Stock clamp, not a bearing. Confirm selected supplier drawing and pinch-screw access.',col=AL)
 # Pinch bolt crosses slit, with a nominal clearance bore cut into the housing.
 housing=d.getObject(f'R4_SHF8_Clamp_{i}');housing.Shape=housing.Shape.cut(cy(2.15,20,V(x+14,55,-136.5),V(0,1,0)))
 bolt(f'R4_SHF8_PinchM4_{i}',V(x+14,56,-136.5),18,4,V(0,1,0))
 for j,(y,z,_) in enumerate(mount):
  washer(f'R4_FlangeWasher_{i}_{j}',V(x-1,y,z),5)
  bolt(f'R4_FlangeM5_{i}_{j}',V(x-1,y,z),20,5)
  nut(f'R4_FlangeNut_{i}_{j}',V(x+13,y,z),5)
 # Cut-to-length stock 40x40x3 aluminium angle, 48mm long; drill on two perpendicular faces.
 leftward=(i==4)
 ax=x-3 if leftward else x+8; bx=x-30 if leftward else x+8
 angle=box(3,48,30,V(ax,-166,-160)).fuse(box(30,48,3,V(bx,-166,-133)))
 for y in [-149,-128]:angle=angle.cut(cy(2.75,5,V(ax-1,y,-151)))
 holesx=[bx+8,bx+22]
 for xx in holesx:
  for yy in [-158,-134]:angle=angle.cut(cy(2.2,5,V(xx,yy,-134),V(0,0,1)))
 add(f'R4_StockAngleFoot_{i}',angle,role='FootBracket',note='30x30x3 stock aluminium angle,48mm cut length. Drill2x5.5 and4x4.4 holes to supplied template; alternatively a supplier-finished angle. Model omits extrusion root radius; rib clears root by4mm.')
 for j,y in enumerate([-149,-128]):
  bp=x-4 if leftward else x-1; np=x+8 if leftward else x+11
  washer(f'R4_RootWasher_{i}_{j}',V(bp,y,-151),5);bolt(f'R4_RootM5_{i}_{j}',V(bp,y,-151),20,5);nut(f'R4_RootNut_{i}_{j}',V(np,y,-151),5)
 backing=box(30,48,2,V(bx,-166,-118))
 for j,xx in enumerate(holesx):
  for k,yy in enumerate([-158,-134]):
   h=cy(3.05,14,V(xx,yy,-131),V(0,0,1));d.getObject('RearRim_700x52x12').Shape=d.getObject('RearRim_700x52x12').Shape.cut(h)
   backing=backing.cut(cy(2.2,4,V(xx,yy,-119),V(0,0,1)))
   # Compression tube is entirely in the12mm structural rear rim.
   add(f'R4_RimCrushTube_{i}_{j}_{k}',ring(3,2.2,12,V(xx,yy,-130),V(0,0,1)),'Steel','Spacer',col=ST)
   washer(f'R4_WoodBoltWasher_{i}_{j}_{k}',V(xx,yy,-134),4.5,V(0,0,1));bolt(f'R4_WoodM4_{i}_{j}_{k}',V(xx,yy,-134),25,4,V(0,0,1))
   washer(f'R4_WoodNutWasher_{i}_{j}_{k}',V(xx,yy,-116),4.5,V(0,0,1));nut(f'R4_WoodNut_{i}_{j}_{k}',V(xx,yy,-115),4,V(0,0,1))
   # Side drilling also passes any structural endblock occupying the same hole.
   for n in ['LeftEndBlock_40x196x52','TunerEndBlock_60x196x52']:d.getObject(n).Shape=d.getObject(n).Shape.cut(cy(2.2,22,V(xx,yy,-131),V(0,0,1)))
 add(f'R4_RimBackingPlate_{i}',backing,'Steel','BackingPlate',note='2mm stainless backing plate; four M4 through-bolts and12mm crush sleeves keep preload out of the timber.',col=ST);backingcuts.append(backing)
 # Full nut/tool pocket in the adjacent endblock/brace, accessible with bottom removed.
 pocket=box(32,52,10,V(bx-1,-169,-118))
 for n in ['LeftEndBlock_40x196x52','TunerEndBlock_60x196x52']+[o.Name for o in d.Objects if o.Name.startswith('LightTransverseBrace')]:d.getObject(n).Shape=d.getObject(n).Shape.cut(pocket)

# Solid stock shaft avoids hollow-tube crush at clamp joints and carries a rear-mounted crank outrigger.
rail=cy(4,590,V(-221,65,-125))
add('R4_SolidRearCarrierRail_8mm',rail,'Steel','Rail','8mm ground solid steel shaft,590mm stock cut length. Fixed structural rail; supported by four flange clamps. No cross-drilling; align the existing bearing carriers before tightening.',ST)
# Flat6mm crank outrigger, bolted via SHF8 to the extended rail and via spacers to the retained R3 precision bearing console.
def cap(x,p,q,w,t):
 u=V(0,q[0]-p[0],q[1]-p[1]);u.normalize();n=V(0,-u.z,u.y)*w/2;a=V(x,*p);b=V(x,*q)
 return Part.Face(Part.makePolygon([a+n,b+n,b-n,a-n,a+n])).extrude(V(t,0,0)).fuse(cy(w/2,t,a)).fuse(cy(w/2,t,b))
x=353
arm=cap(x,(65,-125),(103,-105),14,6).fuse(cap(x,(103,-105),(103,-25),14,6)).fuse(cap(x,(49,-125),(81,-125),18,6)).fuse(cy(11,6,V(x,65,-125)))
for y,z,r in [(65,-125,4.6),*mount,(103,-34,2.2),(103,-16,2.2)]:arm=arm.cut(cy(r,8,V(x-1,y,z)))
add('R4_CrankOuTrigger_6mm',arm,role='CrankBracket',note='6mm flat-cut aluminium outrigger; stock SHF8 clamps to extended rear carrier rail. Retains R3 precision bearing console and free-spinning crank grip.');cut_export('R4_CrankOuTrigger_6mm_x1',arm,x,6)
clamp=cap_profile(348,5).fuse(cy(10,10,V(343,65,-125))).fuse(box(10,18,6,V(343,56,-139)))
clamp=clamp.cut(cy(4,12,V(342,65,-125))).cut(box(12,1.2,15,V(342,64.4,-140)))
for y,z,r in mount:clamp=clamp.cut(cy(r,12,V(342,y,z)))
clamp=clamp.cut(cy(2.15,20,V(347,55,-136.5),V(0,1,0)))
add('R4_CrankSHF8',clamp,role='ShaftClamp',note='Fifth SHF8 reversed against outrigger; confirm chosen catalogue part before ordering.')
bolt('R4_CrankSHF8PinchM4',V(347,56,-136.5),18,4,V(0,1,0))
for j,(y,z,_) in enumerate(mount):
 bolt(f'R4_CrankFlangeM5_{j}',V(360,y,z),20,5,V(-1,0,0));washer(f'R4_CrankFlangeWasher_{j}',V(359,y,z),5);nut(f'R4_CrankFlangeNut_{j}',V(344,y,z),5)
for j,z in enumerate([-34,-16]):
 add(f'R4_CrankConsoleSpacer_{j}',ring(4,2.2,4,V(359,103,z)),role='Spacer')
 washer(f'R4_CrankConsoleHeadWasher_{j}',V(352,103,z),4.5);bolt(f'R4_CrankConsoleM4_{j}',V(352,103,z),25,4);washer(f'R4_CrankConsoleWasher_{j}',V(369,103,z),4.5);nut(f'R4_CrankConsoleNut_{j}',V(370,103,z),4)
for o in list(d.Objects):
 if o.Name.startswith('EXPORT_'):d.removeObject(o.Name)
# R5: translate complete voice stations only. Speaking strings/bridges/tuners stay fixed.
for row, prior in zip(ROWS,OLD_ROWS):
 dx=row['station_x']-prior['station_x']
 for ob in d.getObject(f"V{row['index']:02d}").Group:
  sh=ob.Shape.copy();sh.translate(V(dx,0,0));ob.Shape=sh
  if ob.Role=='Pick':
   ob.addProperty('App::PropertyLength','PluckFromThirdBridge');ob.PluckFromThirdBridge=row['pick_x']-row['bridge_x']
   ob.addProperty('App::PropertyFloat','PluckFraction');ob.PluckFraction=(row['pick_x']-row['bridge_x'])*float(__import__('fractions').Fraction(row['ratio']))/600
   ob.DesignNote+=' R5: longitudinal position balances tone and string compliance; unchanged PET contact geometry. Release force requires a bench test.'
for j,(new,old) in enumerate(zip(BEARINGS,OLD_BEARINGS)):
 for ob in d.Objects:
  if ob.Name.startswith(f'InputMount{j:02d}_'):
   sh=ob.Shape.copy();sh.translate(V(new-old,0,0));ob.Shape=sh
# Move the left positive-retention stack with its bearing; recut all cross-pin bores.
leftshift=BEARINGS[0]-OLD_BEARINGS[0]
for name in ['InputPinnedCollar','CollarFlushPin','InputRearThrustShim']:
 ob=d.getObject(name);sh=ob.Shape.copy();sh.translate(V(leftshift,0,0));ob.Shape=sh
shaft=cy(2.5,381-(-194),V(-194,*DRIVE))
for row in ROWS:
 q=row['crank_yz'];dr=math.atan2(q[1]-DRIVE[1],q[0]-DRIVE[0]);ax=V(0,-math.sin(dr),math.cos(dr));c=V(row['station_x']-5.5,*DRIVE)
 shaft=shaft.cut(cy(.5,12,c-ax*6,ax))
for xx in [-226+leftshift,376]:shaft=shaft.cut(cy(.5,12,V(xx,59,-25),V(0,1,0)))
d.getObject('Common5mmInputShaft').Shape=shaft
d.getObject('Common5mmInputShaft').DesignNote='R5: 575mm diameter5mm ground shaft. Twelve new phased cross-pin positions, relocated left collar, eight aligned MR105ZZ supports plus crank console. No abandoned bores.'

# Existing status must not imply that R3 checks validate the altered frame.
status=d.getObject('EngineeringStatus')
if status:
 status.Label='R5 UNBUILT — revised plucking positions; operating effort unmeasured'
 for prop in status.PropertiesList:
  if prop in ['Status','DesignNote']:
   try:setattr(status,prop,'R5 plucking-layout revision. Physical stiffness, tolerances, bearing alignment, friction and pick release remain unverified. See R5 checks and force assessment.')
   except:pass
d.recompute()
G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll()
path=O/'LeLovophon_Pluck_Layout_R5.FCStd';d.saveAs(str(path))
parts=[o for o in d.Objects if o.TypeId=='Part::Feature' and not o.Shape.isNull()];meshes=[];inv=[]
for o in parts:
 vs,ts=o.Shape.tessellate(.3);meshes.append(dict(name=o.Name,vertices=[[v.x,v.y,v.z] for v in vs],triangles=ts,color=list(o.ViewObject.ShapeColor[:3])))
 inv.append(dict(name=o.Name,motion=o.Motion,voice=o.Voice,role=o.Role,material=o.MaterialName,note=o.DesignNote,volume_mm3=o.Shape.Volume,valid=o.Shape.isValid(),solids=len(o.Shape.Solids)))
(W/'mesh.json').write_text(json.dumps(meshes));(O/'Part_Inventory.json').write_text(json.dumps(inv,indent=2));(O/'Cutting_Preview'/'Profiles.json').write_text(json.dumps(profiles,indent=2))
(W/'build_manifest.json').write_text(json.dumps(dict(source=str(src),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),removed=removed,new=[o.Name for o in g.Group],rib_x_mm=xlist),indent=2))
print('BUILD_DONE',len(parts),'invalid',[p['name'] for p in inv if not p['valid']],'multi',[p['name'] for p in inv if p['solids']!=1],flush=True)
