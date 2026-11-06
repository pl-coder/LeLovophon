import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,math,json
from FreeCAD import Vector as V
from pathlib import Path
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs';d=App.openDocument(str(O/'Lovophone_Pentatonic.FCStd'));rows=json.loads(d.Motion.LinkageGeometry)
oldnames=['LowInputStand0','LowInputStand1','LowInputBearing0','LowInputBearing1','IntermediateAxleStand0','IntermediateAxleStand1'];oldvolume=sum(d.getObject(n).Shape.Volume for n in oldnames)
for n in oldnames:d.removeObject(n)
g=d.addObject('App::DocumentObjectGroup','HardwareStoreDriveFrame');g.Label='Drive frame — flat stock, angle, plywood and standard fasteners'
colors={};parts=[];newnames=[]
def bx(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def cy(r,h,p,a=V(1,0,0)):return Part.makeCylinder(r,h,p,a)
def tube(p,q,ro=5,ri=4):
 a=q-p;return cy(ro,a.Length,p,a).cut(cy(ri,a.Length+2,p-a/a.Length,a))
# Move the left gantry end frame 5 mm outward for ordinary bolt-head access, keeping every musical pivot unchanged.
first,last=rows[0],rows[-1];slope=(last['follower_y']-first['follower_y'])/(last['station']-first['station'])
for o in d.ElectricDrive.Group:
 if o.TypeId=='Part::Feature':
  sh=o.Shape.copy();sh.translate(V(2.6,0,0));o.Shape=sh
d.CommonInputShaft_D6.Shape=cy(3,314.6-.35,V(.35,-83,-131))
d.CommonIntermediateAxle.Shape=cy(3,311.2-3.35,V(3.35,-59,-116))
# A little more end clearance for the normal retaining screw heads.
mb=bx(3,34,22,322,-109,-142).cut(cy(2.1,5,V(321,-83,-131))).fuse(bx(18,3,26,322,-109,-144))
for xx in [329,337]:mb=mb.cut(cy(1.7,8,V(xx,-114,-136),V(0,1,0)))
for n in ['GantryRightFoot0','GantryRightFoot1']:mb=mb.cut(d.getObject(n).Shape)
d.ElectricMotorBracket.Shape=mb
d.ElectricCouplingShield.Shape=cy(7,14.1,V(307.6,-83,-131)).cut(cy(6,16.1,V(306.6,-83,-131)))
for n in ['ElectricClearTop','ElectricClearFront','ElectricClearRear']:
 o=d.getObject(n);o.Shape=o.Shape.cut(bx(20,200,200,356,-180,-200))
def level(x):return first['follower_y']+30+slope*(x-first['station'])
def lane(x,rear=False):return first['pivot_z']+(x-first['station'])*10/24-(30 if rear else 0)
left=first['station']-21;right=last['station']+28
for rear in [False,True]:d.getObject('Gantry'+('Rear' if rear else 'Front')+'Rail').Shape=tube(V(left,level(left),lane(left,rear)),V(right,level(right),lane(right,rear)))
for j,z in enumerate([-148,-112]):
 d.getObject('GantryLeftPost'+str(j)).Shape=tube(V(left,-106,z),V(left,level(left),z))
 foot=d.getObject('GantryLeftFoot'+str(j));sh=foot.Shape.copy();sh.translate(V(-6,0,0));foot.Shape=sh
d.GantryLeftCrosshead.Shape=tube(V(left,level(left),-148),V(left,level(left),lane(left)))
d.GantryLeftBrace.Shape=tube(V(left,-55,-112),V(left,level(left),lane(left)),3.5,2.5)
def put(n,s,label,col=(.46,.49,.51),kind='standard hardware',spec=''):
 o=d.addObject('Part::Feature',n);o.Shape=s;o.Label=label;g.addObject(o);colors[n]=col;newnames.append(n)
 for p,v in [('SourceClass',kind),('StockSpecification',spec)]:o.addProperty('App::PropertyString',p,'Replaceability');setattr(o,p,v)
 parts.append(dict(name=n,label=label,source_class=kind,specification=spec));return o
# Hex heads/nuts are nominal envelopes, not thread geometry.
def hexprism(radius,h,p,axis='X'):
 if axis=='X':pts=[p+V(0,radius*math.cos(k*math.pi/3),radius*math.sin(k*math.pi/3)) for k in range(6)];vec=V(h,0,0)
 else:pts=[p+V(radius*math.cos(k*math.pi/3),0,radius*math.sin(k*math.pi/3)) for k in range(6)];vec=V(0,h,0)
 return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(vec)
def washer(n,x,y,z,axis=V(1,0,0),r=3.5,ri=1.7,h=.5):return put(n,cy(r,h,V(x,y,z),axis).cut(cy(ri,h+2,V(x,y,z)-axis,axis)),n.replace('_',' '),spec='M3 plain washer, 3.2/7/0.5 mm nominal' if r==3.5 else 'M4 plain washer, 4.3/9/0.8 mm nominal')
# A plain 6 mm plywood rectangle. No folded lips, precision pockets or proprietary slots.
deck=bx(288,6,78,17.35,-109,-154);mountcuts=[]
for tag,x,inside in [('Left',12.35,1),('Right',300.35,-1)]:
 cheek=bx(4,59,50,x,-103,-151)
 for suffix,y,z in [('Input',-83,-131),('Idler',-59,-116)]:
  if suffix=='Idler':
   cheek=cheek.cut(cy(3.25,6,V(x-1,y,z)))
   continue
  cheek=cheek.cut(cy(6.05,6,V(x-1,y,z)))
  bearing=cy(6,4,V(x,y,z)).cut(cy(3.025,6,V(x-1,y,z)))
  put('DriveFrame'+tag+suffix+'Bearing',bearing,tag+' '+suffix.lower()+' bearing — MR126-2RS, 6 × 12 × 4 mm',(.38,.40,.41),'catalogue bearing','MR126-2RS or MR126ZZ, 6 mm bore / 12 mm OD / 4 mm width; sealed/shielded version, not 3 mm-wide open version')
  for j,yy in enumerate([y-8.7,y+8.7]):
   cheek=cheek.cut(cy(1.7,6,V(x-1,yy,z)))
   base='DriveFrame'+tag+suffix+'Retainer'+str(j)
   washer(base+'FrontWasher',x-.5,yy,z);washer(base+'RearWasher',x+4,yy,z)
   bolt=cy(1.5,10,V(x-.5,yy,z)).fuse(hexprism(3.175,2,V(x-2.5,yy,z)))
   put(base+'Bolt',bolt,'M3 × 10 bolt — bearing retaining washers',spec='M3 × 10 hex bolt, DIN 933 / ISO 4017 envelope')
   put(base+'Nut',hexprism(3.175,2.4,V(x+4.5,yy,z)).cut(cy(1.55,4.4,V(x+3.5,yy,z))),'M3 nut — bearing retainer',spec='M3 hex nut, ISO 4032 envelope; thread not modelled')
 for j,z0 in enumerate([-151,-116]):
  z=z0+7.5;y=-93
  cheek=cheek.cut(cy(2.2,6,V(x-1,y,z)))
  vx=x+4 if inside==1 else x-2;hx=x+4 if inside==1 else x-20
  angle=bx(2,20,15,vx,-103,z0).fuse(bx(20,2,15,hx,-103,z0));angle=angle.cut(cy(2.2,8,V(x-2,y,z)))
  footx=x+14 if inside==1 else x-10
  h=cy(2.2,18,V(footx,-115,z),V(0,1,0));angle=angle.cut(h);deck=deck.cut(h);mountcuts.append(h)
  put('DriveFrame'+tag+'Angle'+str(j),angle,tag+' standard angle foot '+str(j+1)+' — 20 × 20 × 2, cut 15 mm',(.55,.58,.60),'cut and drill hardware stock','20 × 20 × 2 mm equal angle; saw four identical 15 mm lengths; one 4.4 mm hole per leg')
  # Through-bolt across the vertical angle and cheek.
  front=x-.8 if inside==1 else x-2.8;rear=x+6 if inside==1 else x+4
  shank=cy(2,12,V(front,y,z));head=hexprism(4.04,2.8,V(front-2.8,y,z));put('DriveFrame'+tag+'CheekBolt'+str(j),shank.fuse(head),'M4 × 12 bolt — end plate to angle',spec='M4 × 12 hex bolt, nominal thread envelope')
  washer('DriveFrame'+tag+'CheekWasherA'+str(j),front,y,z,r=4.5,ri=2.2,h=.8)
  washer('DriveFrame'+tag+'CheekWasherB'+str(j),rear,y,z,r=4.5,ri=2.2,h=.8)
  put('DriveFrame'+tag+'CheekNut'+str(j),hexprism(4.04,3.2,V(rear+.8,y,z)).cut(cy(2.05,5.2,V(rear-.2,y,z))),'M4 nut — end plate to angle',spec='M4 hex nut, ISO 4032 nominal envelope')
  # Downward through-bolt passes through angle, plywood deck and soundboard; nut is accessible inside the box.
  put('DriveFrame'+tag+'DeckBolt'+str(j),cy(2,20,V(footx,-120.2,z),V(0,1,0)).fuse(hexprism(4.04,2.8,V(footx,-100.2,z),'Y')),'M4 × 20 bolt — removable drive deck',spec='M4 × 20 hex bolt; nominal thread envelope')
  washer('DriveFrame'+tag+'DeckWasher'+str(j),footx,-101,z,axis=V(0,1,0),r=4.5,ri=2.2,h=.8)
  washer('DriveFrame'+tag+'DeckRearWasher'+str(j),footx,-112.8,z,axis=V(0,1,0),r=4.5,ri=2.2,h=.8)
  put('DriveFrame'+tag+'DeckNut'+str(j),hexprism(4.04,3.2,V(footx,-116,z),'Y').cut(cy(2.05,5.2,V(footx,-117,z),V(0,1,0))),'M4 nut — accessible inside soundbox',spec='M4 hex nut; lock with a second nut or a replaceable nyloc after prototype testing')
 put('DriveFrame'+tag+'Cheek',cheek,tag+' identical end plate — 50 × 59 × 4 mm flat stock',(.42,.45,.47),'cut and drill hardware stock','50 × 4 mm flat steel stock, saw two 59 mm lengths. One 12.1 mm bearing hole, one 6.5 mm fixed-axle hole, two 3.4 mm retaining-bolt holes and two 4.4 mm foot holes; identical drilling template.')
d.LowGearboxTray.Shape=deck;d.LowGearboxTray.Label='Drive deck — plain 288 × 78 × 6 mm plywood rectangle';d.Structure.removeObject(d.LowGearboxTray);g.addObject(d.LowGearboxTray);colors['LowGearboxTray']=(.60,.42,.25)
for p,v in [('SourceClass','hardware-store sheet stock'),('StockSpecification','6 mm plywood, cut 288 × 78 mm; four 4.4 mm through holes; seal edges')]:
 if p not in d.LowGearboxTray.PropertiesList:d.LowGearboxTray.addProperty('App::PropertyString',p,'Replaceability')
 setattr(d.LowGearboxTray,p,v)
# Removable collars retain the two common shafts axially without special turned steps.
for tag,x,y,z,rotating in [('InputLeft',1.1,-83,-131,True)]:
 sh=cy(6,8,V(x,y,z)).cut(cy(3.05,10,V(x-1,y,z))).cut(cy(1.65,5,V(x+4,y+2.5,z),V(0,1,0)))
 o=put('DriveFrame'+tag+'Collar',sh,tag+' — standard 6 mm shaft stop collar',(.35,.38,.40),'catalogue shaft hardware','DIN 705 style 6 mm bore stop collar, nominal 12 mm OD × 8 mm wide, radial set screw; check supplier dimensions')
 if rotating:
  sh.translate(V(-rows[0]['station'],83,131));o.Shape=sh;g.removeObject(o);d.C_Driver.addObject(o)
sp=cy(4,3,V(9.1,-83,-131)).cut(cy(3.05,5,V(8.1,-83,-131)));o=put('DriveFrameInputCollarSpacer',sp,'Input collar spacer — 3 mm length of brass tube',(.62,.43,.15),'cut stock spacer','8 mm OD × 1 mm wall brass tube; cut 3 mm; deburr bore for free fit on 6 mm shaft');sp.translate(V(-rows[0]['station'],83,131));o.Shape=sp;g.removeObject(o);d.C_Driver.addObject(o)
# The stationary axle is an ordinary 6 mm rod with M6 threads cut only on its ends.
# Its smooth middle still carries the twelve independent rotating pulley bushes.
for tag,xx in [('Left',7.35),('Right',304.35)]:
 put('DriveFrameIdler'+tag+'Nut',hexprism(5.774,5,V(xx,-59,-116)).cut(cy(3.05,7,V(xx-1,-59,-116))),'M6 nut — stationary axle end fixing',spec='Ordinary M6 hex nut, nominal 10 mm across flats × 5 mm thick. M6 threads must be cut only on the exposed ends of the smooth 6 mm stationary axle; thread envelope shown.')
d.CommonIntermediateAxle.addProperty('App::PropertyString','FabricationIntent','Replaceability');d.CommonIntermediateAxle.FabricationIntent='6 mm smooth steel rod, nominal 308 mm cut length. Cut M6 threads on the exposed end lengths only: about 9 mm left and 7 mm right. Do not put threaded rod under the independent pulley bushes.'
# Drill the four new drive-deck fixings through the soundboard. Keep the existing hole pattern.
lid=d.Baseplate_310x170x6.Shape.copy()
for z in [-148,-112]:
 for dx in [-7,7]:mountcuts.append(cy(1.7,9,V(left+dx,-114,z),V(0,1,0)))
for h in mountcuts:lid=lid.cut(h)
for xx in [329,337]:lid=lid.cut(cy(1.7,9,V(xx,-114,-136),V(0,1,0)))
d.Baseplate_310x170x6.Shape=lid
for p,v in [('DesignIntent','Two identical flat end cheeks, four sawn standard angle feet and one plain plywood deck. Common metric bolts, washers and replaceable catalogue bearings. Musical drive geometry unchanged.'),('SourceLimits','Hardware-store replaceability applies to frame stock, smooth rod, plywood, nuts, bolts and washers. Bearings, collars, belts, pulleys, motor and ratio cams may need motion/hobby suppliers. Ordinary threaded rod is not a bearing journal.')]:g.addProperty('App::PropertyString',p,'Design');setattr(g,p,v)
d.Motion.Status='Approved pentatonic pitches and original timing; simple removable hardware-stock drive frame. Frame holes, bearing fits and supplier parts remain prototype dimensions.'
d.Label='Le Lovophone — pentatonic, simple stock-built drive frame'
d.recompute();invalid=[o.Name for o in d.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())];assert not invalid,invalid
d.saveAs(str(R/'work/Lovophone_Hardware_Frame_Base.FCStd'))
report=dict(removed_custom_supports=oldnames,old_custom_support_volume_mm3=oldvolume,new_parts=parts,new_part_names=newnames,colors=colors,cut_list=[{'part':'Identical end plates','quantity':2,'stock':'50 × 4 mm flat steel','cut_length_mm':59},{'part':'Identical angle feet','quantity':4,'stock':'20 × 20 × 2 mm equal angle','cut_length_mm':15},{'part':'Drive deck','quantity':1,'stock':'6 mm plywood','size_mm':[288,78]}],timing_and_pitch_geometry_unchanged=True,bearing_standard='MR126-2RS / MR126ZZ, 6 × 12 × 4 mm, sealed/shielded version',invalid_shapes=invalid,scope=g.SourceLimits)
(O/'Lovophone_Hardware_Frame_Design.json').write_text(json.dumps(report,indent=2));(R/'work/hardware_frame_colors.json').write_text(json.dumps(colors));print('Simple drive frame saved; valid shapes:',len(newnames),flush=True)
