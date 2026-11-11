import sys,math,json,hashlib,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from config import *
import FreeCAD as A,FreeCADGui as G,Part
from FreeCAD import Vector as V
from PySide import QtWidgets
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([]);G.showMainWindow();G.getMainWindow().hide()
source=A.openDocument(str(ROOT/'outputs/LeLovophon_Mechanical_Revision_R2/LeLovophon_R2.FCStd'))
d=A.newDocument('LeLovophonProtokotoR3');d.Label='Le Lovophon - Protokoto R3 / engineering prototype'
groups={n:d.addObject('App::DocumentObjectGroup',n) for n in ['WoodenBody','StringsAndBridges','Tensioners','FourCornerFrame','InputDrive','Voices','HandCrank']}
AL=(.66,.72,.75);STEEL=(.55,.60,.63);BRASS=(.72,.51,.20);WOOD=(.40,.20,.075);SPRUCE=(.72,.54,.28);BLACK=(.12,.13,.14);NYLON=(.90,.88,.75);POLY=(.27,.25,.20);TEAL=(.06,.38,.32)
def cyl(r,h,p,axis=V(1,0,0)):return Part.makeCylinder(r,h,p,axis)
def box(x,y,z,p):return Part.makeBox(x,y,z,p)
def ring(ro,ri,h,p,axis=V(1,0,0)):return cyl(ro,h,p,axis).cut(cyl(ri,h+2,p-axis,axis))
def bar(p,q,r):v=q-p;return cyl(r,v.Length,p,v)
def tube(p,q,ro,ri):v=q-p;u=v/v.Length;return bar(p,q,ro).cut(cyl(ri,v.Length+2,p-u,v))
def pt(x,p):return V(x,p[0],p[1])
def capsule(x,p,q,w,t):
 a=pt(x,p);b=pt(x,q);u=b-a;u.normalize();n=V(0,-u.z,u.y)*w/2
 return Part.Face(Part.makePolygon([a+n,b+n,b-n,a-n,a+n])).extrude(V(t,0,0)).fuse(cyl(w/2,t,a)).fuse(cyl(w/2,t,b))
def hex_prism(r,h,p,axis=V(1,0,0)):
 sh=Part.Face(Part.makePolygon([V(0,r*math.cos(j*math.pi/3),r*math.sin(j*math.pi/3)) for j in range(7)])).extrude(V(h,0,0))
 if axis!=V(1,0,0):sh.rotate(V(),V(1,0,0).cross(axis) if abs(axis.x)<.99 else V(0,0,1),math.degrees(math.acos(axis.x)))
 sh.translate(p);return sh
inventory=[]
def add(n,sh,g,col=AL,motion='Fixed',voice=0,role='',note='',material='Aluminium'):
 ob=d.addObject('Part::Feature',n);ob.Shape=sh;g.addObject(ob);ob.ViewObject.ShapeColor=col
 for prop,val in [('Motion',motion),('Role',role),('DesignNote',note),('MaterialName',material)]:ob.addProperty('App::PropertyString',prop);setattr(ob,prop,val)
 ob.addProperty('App::PropertyInteger','Voice');ob.Voice=voice
 return ob
# Hollow, serviceable later-build body. The optional first solid base remains a separate route.
top=box(700,4,220,V(-350,-116,-130));bottom=box(700,4,220,V(-350,-172,-130))
left=box(40,52,196,V(-350,-168,-118));right=box(60,52,196,V(290,-168,-118))
rail0=box(700,52,12,V(-350,-168,-130));rail1=box(700,52,12,V(-350,-168,78))
# Open end tuning well: the nut pedestal bridges a short overhang from the solid part of the block.
right=right.cut(box(31,53,188.2,V(319,-168.1,-118.1)))
for i in range(12):
 z=-102+14*i
 for target in ['top','left']:
  if target=='top':top=top.cut(cyl(1.1,60,V(ANCHOR_X,-172,z),V(0,1,0)))
  else:left=left.cut(cyl(1.1,60,V(ANCHOR_X,-172,z),V(0,1,0)))
 bottom=bottom.cut(cyl(3,6,V(ANCHOR_X,-173,z),V(0,1,0)))
 bottom=bottom.cut(cyl(4,6,V(334.5+TUNER_DX,-173,z),V(0,1,0)))
 top=top.cut(cyl(2.15,2.1,V(334.5+TUNER_DX,-116.1,z),V(0,1,0)))
 top=top.cut(cyl(1.1,6,V(321+PATH_R,-117,z),V(0,1,0)))
# Anchor backing bar is loaded directly against the underside of the solid end block.
anchor=box(12,2,174,V(ANCHOR_X-6,-170,-112))
bottom=bottom.cut(box(12.1,2.1,174.1,V(ANCHOR_X-6.05,-170.05,-112.05)))
for i in range(12):anchor=anchor.cut(cyl(1.05,4,V(ANCHOR_X,-171,-102+14*i),V(0,1,0)))
for z in [-110,60]:
 for shape_name in ['anchor','left','bottom']:
  sh=locals()[shape_name];sh=sh.cut(cyl(1.65,10,V(ANCHOR_X+3,-174,z),V(0,1,0)));locals()[shape_name]=sh
# Tuner mounting holes into the solid portion of the right end block.
for yy in [-121,-149]:
 for zz in [-112,62]:right=right.cut(cyl(1.65,12,V(309,yy,zz)))
# Four gantry feet bolt into the end blocks/rims, through soundboard compression sleeves.
for x in [-328,328]:
 for z in [-124,84]:
  for xx in [x-5,x+5]:
   top=top.cut(cyl(3.1,6,V(xx,-117,z),V(0,1,0)))
   block=left if x<0 else right;block=block.cut(cyl(2.2,56,V(xx,-170,z),V(0,1,0)))
   if x<0:left=block
   else:right=block
   if z<0:rail0=rail0.cut(cyl(2.2,56,V(xx,-170,z),V(0,1,0)))
   else:rail1=rail1.cut(cyl(2.2,56,V(xx,-170,z),V(0,1,0)))
   bottom=bottom.cut(cyl(5,6,V(xx,-173,z),V(0,1,0)))
# Bottom panel fasteners use inserts in the structural rims/end blocks.
for x in [-285,-150,50,230,285]:
 for z in [-124,84]:
  bottom=bottom.cut(cyl(1.65,6,V(x,-173,z),V(0,1,0)))
  sh=rail0 if z<0 else rail1;sh=sh.cut(cyl(2.5,6,V(x,-168,z),V(0,1,0)))
  if z<0:rail0=sh
  else:rail1=sh
  add('BottomM3Insert',ring(2.5,1.5,6,V(x,-168,z),V(0,1,0)),groups['WoodenBody'],BRASS,role='Insert',material='Brass',note='Nominal threaded insert envelope. Final insert pilot and timber fit follow supplier.')
  add('BottomM3Screw',cyl(1.4,10,V(x,-172,z),V(0,1,0)).fuse(cyl(2.75,3,V(x,-175,z),V(0,1,0))),groups['WoodenBody'],STEEL,role='Fastener',material='Steel')
# End saddle and speaking nut are bolted rails, not unsupported trim.
low_crown=cyl(CROWN_R,174,V(LOW_X,LOW_Y,-112),V(0,0,1));high_crown=cyl(CROWN_R,174,V(NUT_X,NUT_Y,-112),V(0,0,1))
# Lower return crown sits in a matching cradle in the thick end region.
top=top.cut(low_crown);left=left.cut(low_crown)
high_base=box(23,NUT_Y-CROWN_R+112+.5,174,V(302,-112,-112))
for x,z in [(305,-110),(305,60),(LOW_X,-110),(LOW_X,60)]:
 top=top.cut(cyl(1.65,12,V(x,-122,z),V(0,1,0)))
 block=left if x<0 else right;block=block.cut(cyl(2.5,6,V(x,-122,z),V(0,1,0)))
 if x<0:left=block
 else:right=block
 high_base=high_base.cut(cyl(1.65,25,V(x,-123,z),V(0,1,0)))
 low_crown=low_crown.cut(cyl(1.65,25,V(x,-123,z),V(0,1,0)))
 # Head is above the saddle surface but outside all twelve string lanes.
 heady=-102 if x<0 else NUT_Y-CROWN_R+3
 if x<0:low_crown=low_crown.cut(cyl(2.8,6,V(x,-106,z),V(0,1,0)))
 body=cyl(1.4,heady+122,V(x,-122,z),V(0,1,0));head=cyl(2.75,3,V(x,heady,z),V(0,-1,0))
 saddle_screw=body.fuse(head)
 if x>0:saddle_screw.translate(V(0,.5,0))
 add('SaddleM3Screw',saddle_screw,groups['StringsAndBridges'],STEEL,role='Fastener',material='Steel')
 add('SaddleM3Insert',ring(2.5,1.5,6,V(x,-122,z),V(0,1,0)),groups['WoodenBody'],BRASS,role='Insert',material='Brass')
# Structural wood parts and brace set are separate inspectable pieces.
wood_parts=[('Soundboard_700x220x4',top,SPRUCE,'Spruce'),('RemovableBottom_700x220x4',bottom,WOOD,'Birch plywood'),('LeftEndBlock_40x196x52',left,WOOD,'Beech'),('TunerEndBlock_60x196x52',right,WOOD,'Beech'),('RearRim_700x52x12',rail0,WOOD,'Birch plywood'),('FrontRim_700x52x12',rail1,WOOD,'Birch plywood')]
for n,sh,c,m in wood_parts:add(n,sh,groups['WoodenBody'],c,role='Soundboard' if n.startswith('Soundboard') else 'Body',material=m,note='Later-build acoustic box concept. Nominal stock, not a cutting release; timber/joins/bracing require loaded acoustic trial.')
for x in [-240,-120,0,120,240]:add('LightTransverseBrace',box(8,12,196,V(x-4,-128,-118)),groups['WoodenBody'],SPRUCE,role='Brace',material='Spruce',note='Grain along brace; bonded contact to top and rims. Acoustic trial controls final profile.')
for x in [-340,340]:
 for z in [-110,70]:add('RubberFoot',box(14,11,14,V(x-7,-183,z-7)),groups['WoodenBody'],BLACK,role='Foot',material='Rubber')
add('SteelAnchorBackingBar',anchor,groups['StringsAndBridges'],STEEL,role='Anchor',material='Steel',note='Knot loads bear on this bar against the solid end block, rather than on the thin bottom panel.')
for z in [-110,60]:add('AnchorM3Retainer',cyl(1.4,8,V(ANCHOR_X+3,-172,z),V(0,1,0)).fuse(cyl(2.75,3,V(ANCHOR_X+3,-172,z),V(0,-1,0))),groups['StringsAndBridges'],STEEL,role='Fastener',material='Steel')
# Recreate tangent string routes for 1.05 mm nominal line. All speaking sections horizontal.
routes=[]
for r in ROWS:
 i=r['index'];z=-102+14*(i-1);bx=r['bridge_x'];aa=math.atan2(12,bx-LOW_X)+math.pi/2
 def arc(cx,cy,a0,a1):
  def p(a):return V(cx+PATH_R*math.cos(a),cy+PATH_R*math.sin(a),z)
  return Part.Arc(p(a0),p((a0+a1)/2),p(a1)).toShape()
 lc=V(LOW_X+PATH_R*math.cos(aa),LOW_Y+PATH_R*math.sin(aa),z);bc=V(bx+PATH_R*math.cos(aa),NUT_Y+PATH_R*math.sin(aa),z)
 endx=NUT_X+PATH_R
 edges=[Part.makeLine(V(ANCHOR_X,-172,z),V(ANCHOR_X,LOW_Y,z)),arc(LOW_X,LOW_Y,math.pi,aa),Part.makeLine(lc,bc),arc(bx,NUT_Y,aa,math.pi/2),Part.makeLine(V(bx,-91,z),V(NUT_X,-91,z)),arc(NUT_X,NUT_Y,math.pi/2,0),Part.makeLine(V(endx,NUT_Y,z),V(endx,-146.6,z))]
 wire=Part.Wire(edges);profile=Part.Wire([Part.makeCircle(LINE_R,V(ANCHOR_X,-172,z),V(0,1,0))]);string=wire.makePipeShell([profile],True,False)
 add(f'V{i:02d}_FluorocarbonString',string,groups['StringsAndBridges'],NYLON,voice=i,role='String',material='PVDF',note='Same nominal 1.05 mm gauge on all voices; ideal common tension about 37.98 N at 600 mm/C3. Actual line and terminations must be tested.')
 footprint=Part.Face(Part.makePolygon([V(bx-8,-112,z-5),V(bx+8,-112,z-5),V(bx+1,NUT_Y,z-5),V(bx-1,NUT_Y,z-5),V(bx-8,-112,z-5)])).extrude(V(0,0,10))
 crown=cyl(CROWN_R,10,V(bx,NUT_Y,z-5),V(0,0,1));bridge=footprint.fuse(crown).cut(string)
 add(f'V{i:02d}_ThirdBridge',bridge,groups['StringsAndBridges'],BRASS,voice=i,role='Bridge',material='Acetal',note='16 x 10 mm footprint supported on top. Replaceable rounded crown; nominal groove contact only. Final bridge action and anti-walk retention are a bench setting.')
 low_crown=low_crown.cut(string);high_crown=high_crown.cut(string)
 add(f'V{i:02d}_AnchorStopperKnot',Part.makeSphere(2,V(ANCHOR_X,-172,z)),groups['StringsAndBridges'],NYLON,voice=i,role='Knot',material='PVDF',note='Stopper-knot envelope, not molded ball; tie and pull-test the selected line.')
 add(f'V{i:02d}_TunerStopperKnot',Part.makeSphere(1.9,V(endx,-146.6,z)),groups['StringsAndBridges'],NYLON,voice=i,role='Knot',material='PVDF')
 routes.append(dict(voice=i,note=r['note'],speaking_length_mm=321-bx,bridge_x=bx,pick_x=r['pick_x'],speaking_y=-91,lane_z=z,back_break_angle_deg=math.degrees(math.atan2(12,bx-LOW_X))))
add('LowReturnSaddleGrooved',low_crown,groups['StringsAndBridges'],BRASS,role='Saddle',material='Acetal')
add('SpeakingNutGrooved',high_base.fuse(high_crown),groups['StringsAndBridges'],BRASS,role='Nut',material='Acetal')
# Reuse the proven screw-carriage architecture, shifted to the larger-radius string return.
for old in source.getObject('Tensioners').Group:
 sh=old.Shape.copy();sh.translate(V(TUNER_DX,0,0))
 # Original mount spacers attached to the old case edge; replace with direct end-block mounting.
 if old.Name.startswith('TunerMount'):continue
 add(old.Name,sh,groups['Tensioners'],tuple(old.ViewObject.ShapeColor[:3]),old.Motion,old.Voice,old.Role,old.DesignNote, 'Steel' if old.Role!='Carriage' else 'Aluminium')
# Four ordinary M3 mounts seat the tuner angle into the remaining solid end-block strip.
for y in [-121,-149]:
 for z in [-112,62]:
  x0=319;sp=ring(3,1.65,7+TUNER_DX,V(x0,y,z));bolt=cyl(1.4,19+TUNER_DX,V(310,y,z)).fuse(cyl(2.75,3,V(329+TUNER_DX,y,z)))
  add('TunerMountSpacer',sp,groups['Tensioners'],role='Spacer')
  add('TunerMountM3Screw',bolt,groups['Tensioners'],STEEL,role='Fastener',material='Steel')
# Copy each exact gear/crank/rocker assembly to its new axial station; lighten only fixed webs.
identity=[]
for r,oldrow in zip(ROWS,OLD_ROWS):
 i=r['index'];n=f'V{i:02d}';g=d.addObject('App::DocumentObjectGroup',n);g.Label=r['note']+' - '+r['ratio'];groups['Voices'].addObject(g);dx=r['station_x']-oldrow['station_x'];s=r['station_x'];P=r['pivot_yz'];Q=r['crank_yz'];a,b,_=linkage(r,r['phase_rad'])
 for old in source.getObject(n).Group:
  if old.Role=='Coupler':continue
  sh=old.Shape.copy();sh.translate(V(dx,0,0));before=sh.Volume
  if old.Role=='Carrier':
   for p,q in [(P,Q),(Q,DRIVE),(DRIVE,(65,-125))]:
    v=V(0,q[0]-p[0],q[1]-p[1]);length=v.Length
    if length<30:continue
    u=v/length;aa=V(0,*p)+u*12;bb=V(0,*q)-u*12
    cutter=capsule(sh.BoundBox.XMin-1,(aa.y,aa.z),(bb.y,bb.z),3,sh.BoundBox.XLength+2)
    for cp in [P,Q,DRIVE,(65,-125)]:cutter=cutter.cut(cyl(9,sh.BoundBox.XLength+4,pt(sh.BoundBox.XMin-2,cp)))
    sh=sh.cut(cutter)
  ob=add(old.Name,sh,g,tuple(old.ViewObject.ShapeColor[:3]),old.Motion,i,old.Role,old.DesignNote,'Aluminium' if old.Role=='Carrier' else 'Steel' if old.Role in ['Fastener','DrivePin','ShoulderPin','Washer','Shim','Retainer'] else 'Bearing steel' if old.Role=='Bearing' else 'Brass' if old.Role in ['Gear','Crank','Rocker'] else 'Brass' if old.Role=='Arm' else 'PET' if old.Role=='Pick' else 'Aluminium')
  identity.append(dict(name=ob.Name,source=old.Name,translation_x_mm=dx,source_volume_mm3=old.Shape.Volume,new_volume_mm3=sh.Volume,changed_by_lightening=old.Role=='Carrier'))
 # Slender steel shank with polymer-lined eyes. Igus GFM-0304-02: ID3, OD4.5, flange7.5, total length2 incl flange0.5.
 rod=capsule(s+5.5,a,b,2,1.5)
 for idx,cp in enumerate([a,b]):rod=rod.fuse(cyl(3.3 if i==5 and idx==0 else 3.5,1.5,pt(s+5.5,cp)))
 for cp in [a,b]:rod=rod.cut(cyl(2.25,3.5,pt(s+4.5,cp)))
 rod=rod.removeSplitter();add(n+'_SteelPushrod',rod,g,STEEL,'Coupler',i,'Coupler','Laser-cut 1.5 mm steel plate: 2 mm centre width, OD7 eyes, 4.5 mm polymer-bush seats. Deburr and radius edges. Buckling, fatigue and bush fits require shop review.', 'Steel')
 for tag,cp,mot in [('Crank',a,'Crank'),('Rocker',b,'Rocker')]:
  bush=ring(3.3 if i==5 and tag=='Crank' else 3.75,1.515,.5,pt(s+5,cp)).fuse(ring(2.25,1.515,1.5,pt(s+5.5,cp)))
  add(n+'_'+tag+'DryBush_GFM030402',bush,g,POLY,'Coupler',i,'Bush','Nominal GFM-0304-02 geometry; bore after press-fit 3.014-3.054; housing 4.500-4.512. Manufacturer fit specification governs.','Iglidur G')
  add(n+'_'+tag+'RearJointShim',ring(2.6,1.55,.4,pt(s+4.5,cp)),g,STEEL,mot,i,'Shim',material='Steel')
  add(n+'_'+tag+'FrontPTFEWasher',ring(2.7,1.55,.2,pt(s+7,cp)),g,NYLON,'Coupler',i,'ThrustWasher','0.1 mm nominal axial running gap at each side of complete joint stack. Verify press-fit, wear and free release.','PTFE')
print('VOICES_COPIED',flush=True)
# Four-corner welded aluminium gantry. All load-carrying junctions are joined into one frame solid.
def rect_tube_x(x0,x1,y,z,hy,wz,wall):return box(x1-x0,hy,wz,V(x0,y-hy/2,z-wz/2)).cut(box(x1-x0+2,hy-2*wall,wz-2*wall,V(x0-1,y-hy/2+wall,z-wz/2+wall)))
def rect_tube_z(z0,z1,x,y,wx,hy,wall):return box(wx,hy,z1-z0,V(x-wx/2,y-hy/2,z0)).cut(box(wx-2*wall,hy-2*wall,z1-z0+2,V(x-wx/2+wall,y-hy/2+wall,z0-1)))
frame=rect_tube_x(-334,334,103,-142,30,15,1.5).fuse(rect_tube_x(-334,334,103,102,15,10,1.5))
for x in [-328,328]:
 frame=frame.fuse(rect_tube_z(-142,102,x,103,10,20,1.5))
 for z,inside in [(-142,-124),(102,84)]:
  frame=frame.fuse(tube(V(x,-109,z),V(x,103,z),6,4.5))
  zmin=-150 if z<0 else 80
  foot=box(18,3,30,V(x-9,-112,zmin))
  for xx in [x-5,x+5]:foot=foot.cut(cyl(2.2,5,V(xx,-113,inside),V(0,1,0)))
  frame=frame.fuse(foot)
  for xx in [x-5,x+5]:
   add('FootCompressionSleeve',ring(3,2.2,4,V(xx,-116,inside),V(0,1,0)),groups['FourCornerFrame'],role='Spacer',note='Carries gantry load through acoustic top into the structural rim/end block.')
   add('FootM4ThroughBolt',cyl(1.8,59,V(xx,-168,inside),V(0,1,0)).fuse(cyl(3.5,4,V(xx,-109,inside),V(0,1,0))),groups['FourCornerFrame'],STEEL,role='Fastener',material='Steel')
   add('FootM4Washer',ring(4.5,2.2,1,V(xx,-169,inside),V(0,1,0)),groups['FourCornerFrame'],STEEL,role='Washer',material='Steel')
   add('FootM4Nut',hex_prism(4.04,3.2,V(xx,-172.2,inside),V(0,1,0)).cut(cyl(2.05,5,V(xx,-173,inside),V(0,1,0))),groups['FourCornerFrame'],STEEL,role='Fastener',material='Steel')
 # End-plane triangle is above speaking strings where it crosses their lane range.
 frame=frame.fuse(tube(V(x,-109,-142),V(x,103,102),3,2))
for x in [-105,115]:frame=frame.fuse(rect_tube_z(-142,102,x,103,10,15,1.5))
# Common input bearing bridges retain the known MR105 outer-race shoulders and retainers.
rear_rail=tube(V(-238,65,-125),V(340,65,-125),4,3)
for j,x in enumerate(BEARINGS):
 dx=x-16
 # R2 named screws have no parent suffix; select via bounding box to recover this mount's fasteners.
 names=['InputBearingBridge_16','Input105Bearing_16','InputBearingRetainer_16','InputRailClampM2_16']
 screws=[o for o in source.Objects if o.Name.startswith('InputRetainerScrew') and abs(o.Shape.BoundBox.XMin-14.8)<.05]
 for old in [source.getObject(n) for n in names]+screws:
  sh=old.Shape.copy();sh.translate(V(dx,0,0));add(f'InputMount{j:02d}_'+old.Name,sh,groups['InputDrive'],tuple(old.ViewObject.ShapeColor[:3]),old.Motion,0,old.Role or 'InputBearingMount',old.DesignNote,'Bearing steel' if old.Role=='Bearing' else 'Aluminium')
 hx=x-9 if j==0 else x+11
 # Positive rear-beam and carrier-rail bolted hanger, with crush sleeves at hollow tube walls.
 hanger=box(8,40,25,V(hx-4,83,-154.5)).cut(box(10,30.1,15.1,V(hx-5,87.95,-149.55)))
 hanger=hanger.fuse(capsule(hx-1.5,(87,-142),(65,-125),10,3)).fuse(box(8,14,14,V(hx-4,58,-132)))
 hanger=hanger.cut(box(10,30.1,15.1,V(hx-5,87.95,-149.55)))
 hanger=hanger.cut(cyl(4.01,10,pt(hx-5,(65,-125))))
 for yy,z0,z1 in [(103,-154.5,-129.5),(65,-132,-118)]:
  hanger=hanger.cut(cyl(1.65 if yy==103 else 2.51,z1-z0+2,V(hx,yy,z0-1),V(0,0,1)))
  hanger=hanger.cut(cyl(2.8,3,V(hx,yy,z0-3),V(0,0,1)))
  tubez0,tubez1=(-149.5,-134.5) if yy==103 else (-129,-121)
  cutter=cyl(2.5,tubez1-tubez0+2,V(hx,yy,tubez0-1),V(0,0,1))
  if yy==103:frame=frame.cut(cutter)
  else:rear_rail=rear_rail.cut(cutter)
  add('HangerCrushSleeve',ring(2.5,1.65,(tubez1-tubez0) if yy==103 else 14,V(hx,yy,tubez0 if yy==103 else -132),V(0,0,1)),groups['FourCornerFrame'],role='Spacer')
  add('HangerM3Bolt',cyl(1.4,z1-z0+3,V(hx,yy,z0),V(0,0,1)).fuse(cyl(2.75,3,V(hx,yy,z0-3),V(0,0,1))),groups['FourCornerFrame'],STEEL,role='Fastener',material='Steel')
  add('HangerM3Nut',hex_prism(3.1,2.4,V(hx,yy,z1),V(0,0,1)).cut(cyl(1.55,4,V(hx,yy,z1-1),V(0,0,1))),groups['FourCornerFrame'],STEEL,role='Fastener',material='Steel')
 add('BoltedRearRailHanger',hanger,groups['FourCornerFrame'],role='Hanger',note='Upper rectangular tube and lower 8 mm rail are positively through-bolted; crush sleeves prevent thin tube walls taking bolt preload.')
add('RearCarrierRail_8x1',rear_rail,groups['FourCornerFrame'],STEEL,role='Rail',material='Steel')
# Hand-crank bearing console suspended from the end beam, not a fifth upright.
console=box(6,51,26,V(363,57,-38)).cut(cyl(5.01,4,V(365,*DRIVE))).cut(cyl(4.3,8,V(362,*DRIVE)))
for z in [-34,-16]:
 console=console.cut(cyl(2.2,8,V(362,103,z)));frame=frame.cut(cyl(3,12,V(322,103,z)))
 add('CrankConsoleCrushSleeve',ring(3,2.2,10,V(323,103,z)),groups['FourCornerFrame'],role='Spacer')
 add('CrankConsoleSpacer',ring(4,2.2,30,V(333,103,z)),groups['FourCornerFrame'],role='Spacer')
 add('CrankConsoleM4Bolt',cyl(1.8,50,V(319,103,z)).fuse(cyl(3.5,4,V(369,103,z))),groups['FourCornerFrame'],STEEL,role='Fastener',material='Steel')
 add('CrankConsoleM4Nut',hex_prism(4.04,3.2,V(319.8,103,z)).cut(cyl(2.05,5,V(319,103,z))),groups['FourCornerFrame'],STEEL,role='Fastener',material='Steel')
for dz in [-8.3,8.3]:
 console=console.fuse(cyl(2.5,6,V(363,65,-25+dz))).cut(cyl(1.05,8,V(362,65,-25+dz)))
 ret=source.getObject('InputBearingRetainer_16').Shape.copy();ret.translate(V(369.2-14.8,0,0))
 # Retainer faces outward; bolts follow the nominal holes below.
add('FourCornerWeldedGantry',frame.removeSplitter(),groups['FourCornerFrame'],role='Frame',note='Exactly four 12 x 1.5 mm upright tubes. Rear beam 30 x 15 x 1.5; front 15 x 10 x 1.5; two end-plane 6 x 1 mm braces. Welded subassembly removable at eight foot bolts. Weld/process/load proof required.')
add('SuspendedCrankBearingConsole',console,groups['HandCrank'],role='InputBearingMount')
add('CrankSupportMR105ZZ',ring(5,2.5,4,V(365,*DRIVE)),groups['HandCrank'],BLACK,role='Bearing',material='Bearing steel')
# Console outer race is retained at X369; centre hole passes inner-race shim/collar only.
ret=ring(6.5,4.3,1.2,V(369,*DRIVE))
for dz in [-8.3,8.3]:
 ret=ret.fuse(cyl(2.5,1.2,V(369,65,-25+dz))).cut(cyl(1.05,3,V(368,65,-25+dz)))
 add('CrankOuterRetainerM2',cyl(.95,4,V(366.2,65,-25+dz)).fuse(cyl(1.7,1.2,V(370.2,65,-25+dz))),groups['HandCrank'],STEEL,role='Fastener',material='Steel')
add('CrankOuterRaceRetainer',ret,groups['HandCrank'],role='Retainer')
# Positive gear torque coupling and positive axial input retention.
shaft=cyl(2.5,613,V(-232,*DRIVE))
for r in ROWS:
 q=r['crank_yz'];dr=math.atan2(q[1]-DRIVE[1],q[0]-DRIVE[0]);ax=V(0,-math.sin(dr),math.cos(dr));centre=pt(r['station_x']-5.5,DRIVE);shaft=shaft.cut(cyl(.5,12,centre-ax*6,ax))
for x in [-226,376]:shaft=shaft.cut(cyl(.5,12,V(x,59,-25),V(0,1,0)))
add('Common5mmInputShaft',shaft,groups['InputDrive'],STEEL,'Input',role='InputShaft',material='Steel',note='613 mm stock shaft. Pinned gears phased in jig. Eight rail-supported MR105ZZ bearings plus hand-crank console bearing; final coaxial alignment must be measured.')
for x in [-227.5]:
 collar=ring(4,2.52,3,pt(x,DRIVE)).cut(cyl(.5,10,V(x+1.5,60,-25),V(0,1,0)))
 add('InputPinnedCollar',collar,groups['InputDrive'],STEEL,'Input',role='Retainer',material='Steel')
 add('CollarFlushPin',cyl(.49,7.6,V(x+1.5,61.2,-25),V(0,1,0)),groups['InputDrive'],STEEL,'Input',role='DrivePin',material='Steel')
add('InputRearThrustShim',ring(2.95,2.55,.3,V(-224.3,*DRIVE)),groups['InputDrive'],STEEL,'Input',role='Shim',material='Steel')
add('InputFrontThrustSpacer',ring(2.95,2.55,3.8,V(369,*DRIVE)),groups['InputDrive'],STEEL,'Input',role='Shim',material='Steel')
# Removable 32 mm hand crank, positively locked to shaft; grip spins on two shielded bearings.
hub=ring(7,2.52,8,V(373,*DRIVE));hub=hub.cut(cyl(.5,18,V(376,56,-25),V(0,1,0)))
arm=capsule(381,DRIVE,(97,-25),10,3).cut(cyl(2.2,5,V(380,97,-25)))
add('HandCrank32mm',hub.fuse(arm),groups['HandCrank'],BRASS,'Input',role='HandCrank',material='Aluminium',note='32 mm throw. Withdraw retained transverse pin and slide crank off input shaft; grip is independent on two MR105ZZ bearings.')
add('CrankHubFlushPin',cyl(.49,13.6,V(376,58.2,-25),V(0,1,0)),groups['HandCrank'],STEEL,'Input',role='DrivePin',material='Steel')
# Journal flange clamps to crank arm; 5 mm grip journal begins beyond arm.
journal=cyl(1.8,6,V(379,97,-25)).fuse(cyl(3.5,1,V(384,97,-25))).fuse(cyl(2.5,30,V(385,97,-25))).cut(cyl(1.4,6,V(410,97,-25)))
add('FreeGripShoulderJournal',journal,groups['HandCrank'],STEEL,'Input',role='GripJournal',material='Steel')
add('GripJournalM4Nut',hex_prism(4.04,3.2,V(377.8,97,-25)).cut(cyl(2.05,5,V(377,97,-25))),groups['HandCrank'],STEEL,'Input',role='Fastener',material='Steel')
# Open-ended bearing pockets permit assembly; shoulders touch only outer races.
grip=cyl(8,30,V(385.5,97,-25)).cut(cyl(4.3,32,V(384.5,97,-25)))
for x in [385.4,409]:grip=grip.cut(cyl(5.01,5.6 if x<400 else 6.6,V(x,97,-25)))
for x in [385.65,413.25]:grip=grip.cut(cyl(5.45,1.1,V(x,97,-25)))
for x in [387,409]:add('GripMR105ZZ',ring(5,2.5,4,V(x,97,-25)),groups['HandCrank'],BLACK,'Input',role='GripBearing',material='Bearing steel')
for x in [385.7,413.3]:
 clip=ring(5.4,4.3,1,V(x,97,-25)).cut(box(2,3,7,V(x-.5,95.5,-25)))
 add('GripInternalRetainingRing',clip,groups['HandCrank'],STEEL,'Input',role='Retainer',material='Spring steel',note='Nominal 10 mm bore internal C-ring envelope. Select supplier ring first and cut matching groove; final fit not a manufacturing release.')
add('FreelyRotatingGrip',grip,groups['HandCrank'],TEAL,'Input',role='Grip',material='Acetal',note='30 mm long, OD16; end-installed MR105ZZ outer races seat at X391 and409 and retain with internal rings. End screw clamps only the inner-race spacer stack; grip independently rotates about its journal.')
for x in [385,413]:add('GripInnerThrustShim',ring(2.95,2.55,2,V(x,97,-25)),groups['HandCrank'],STEEL,'Input',role='Shim',material='Steel')
add('GripInnerSpacer',ring(2.95,2.55,18,V(391,97,-25)),groups['HandCrank'],STEEL,'Input',role='Spacer',material='Steel')
add('GripEndWasher',ring(3.5,1.65,.5,V(415,97,-25)),groups['HandCrank'],STEEL,'Input',role='Washer',material='Steel')
add('GripM3EndScrew',cyl(1.4,4.5,V(411,97,-25)).fuse(cyl(2.75,3,V(415.5,97,-25))),groups['HandCrank'],STEEL,'Input',role='Fastener',material='Steel')
# Engineering data and separately selectable source parts.
status=d.addObject('App::FeaturePython','EngineeringStatus')
for n,v in [('Status','R3 geometry candidate: complete mechanical checks must pass before delivery. UNBUILT; no manufacturing release.'),('Body','Later-build hollow protokoto concept; optional solid test base remains permitted.'),('Ratios','1,9/8,5/4,3/2,5/3,2,9/4,5/2,3,10/3,4,9/2')]:status.addProperty('App::PropertyString',n);setattr(status,n,v)
d.recompute();invalid=[o.Name for o in d.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())]
print('INVALID',invalid,flush=True)
multi=[o.Name for o in d.Objects if o.TypeId=='Part::Feature' and len(o.Shape.Solids)!=1]
print('MULTI_SOLIDS',multi,flush=True)
assert not multi,multi
assert not invalid,invalid
G.getDocument(d.Name).activeView().viewAxonometric();G.getDocument(d.Name).activeView().fitAll()
d.saveAs(str(OUT/'LeLovophon_Protokoto_R3.FCStd'))
meshes=[];inv=[];bb=A.BoundBox()
for o in d.Objects:
 if o.TypeId!='Part::Feature':continue
 sh=o.Shape;bb.add(sh.BoundBox);vs,ts=sh.tessellate(.35)
 meshes.append(dict(name=o.Name,vertices=[[p.x,p.y,p.z] for p in vs],triangles=ts,color=list(o.ViewObject.ShapeColor[:3]),motion=o.Motion,voice=o.Voice))
 inv.append(dict(name=o.Name,role=o.Role,motion=o.Motion,voice=o.Voice,material=o.MaterialName,volume_mm3=sh.Volume,solids=len(sh.Solids),note=o.DesignNote))
(OUT/'Part_Inventory.json').write_text(json.dumps(inv,indent=2));(OUT/'String_Routing.json').write_text(json.dumps(routes,indent=2));(OUT/'Drive_Calculations.json').write_text(json.dumps(dict(voices=ROWS,input_bearing_x=BEARINGS,repeat_seconds=480,input_rpm=3,base_speaking_length_mm=600,string_diameter_mm=1.05,body_envelope_mm=[700,220,60],assembly_envelope_mm=[bb.XLength,bb.ZLength,bb.YLength],hand_crank_radius_mm=32,main_upright_count=4,physical_test_passed=False,manufacturing_release=False),indent=2))
(ROOT/'work/protokoto_r3/mesh.json').write_text(json.dumps(meshes));(ROOT/'work/protokoto_r3/Source_Translations.json').write_text(json.dumps(identity,indent=2))
print('R3_SAVED',len(inv),[bb.XLength,bb.ZLength,bb.YLength],flush=True)
