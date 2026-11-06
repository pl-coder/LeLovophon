import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,math,json
from FreeCAD import Vector as V
from pathlib import Path
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs';d=App.openDocument(str(O/'Lovophone_Hardware_Frame.FCStd'));rows=json.loads(d.Motion.LinkageGeometry)
def bx(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def cy(r,h,p,a=V(1,0,0)):return Part.makeCylinder(r,h,p,a)
def bar(p,q,r):v=q-p;return cy(r,v.Length,p,v)
def tube(p,q,ro=4,ri=3):v=q-p;return cy(ro,v.Length,p,v).cut(cy(ri,v.Length+2,p-v/v.Length,v))
def world(o):s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return s
oldbounds=App.BoundBox();oldvol={}
for o in d.Objects:
 if o.TypeId=='Part::Feature':oldbounds.add(world(o).BoundBox);oldvol[o.Name]=o.Shape.Volume
new=[];colors={};g=d.addObject('App::DocumentObjectGroup','LabFrame');g.Label='Open laboratory frame — removable tubes, stays and clamps'
def add(n,s,label,col=(.7,.73,.76)):
 o=d.addObject('Part::Feature',n);o.Shape=s;o.Label=label;g.addObject(o);new.append(n);colors[n]=col;return o
# Centre the acoustic body on the unaltered 110 mm string bank: z=-25.
# Rear drive occupies an open outrigger bay, inside the previous footprint.
outer=bx(370,45,140,-30,-157,-95);inner=bx(358,42,128,-24,-154,-89)
d.SoundboxShell.Shape=outer.cut(inner)
for n in ['SoundboxEndBlock0','SoundboxEndBlock1','SoundboxMountRib0','SoundboxMountRib1']:
 d.getObject(n).Shape=d.getObject(n).Shape.common(bx(500,100,128,-60,-180,-89))
d.Baseplate_310x170x6.Shape=d.Baseplate_310x170x6.Shape.common(bx(500,100,140,-60,-180,-95))
# Continuous open subframe carries the rear drive deck and acoustic box together.
for j,x in enumerate([1.35,314.35]):
 add('LabBaseTransom'+str(j),tube(V(x,-114,-151),V(x,-114,42),4,3),'8 × 1 mm aluminium base transom')
for j,z in enumerate([-148,38]):
 add('LabBaseLongeron'+str(j),tube(V(-17,-118,z),V(329,-118,z),4,3),'8 × 1 mm aluminium removable base rail')
# Foot attachment saddles. The front rail engages the wood; rear rail carries open drive deck.
for j,x in enumerate([1.35,314.35]):
 for k,z in enumerate([-148,38]):
  sh=bx(12,10,12,x-6,-123,z-6).cut(cy(4.1,16,V(x-8,-118,z)))
  sh=sh.cut(cy(4.1,16,V(x,-114,z-8),V(0,0,1)))
  add(f'LabBaseClamp{j}{k}',sh,'Split base-rail clamp — prototype machined block',(.69,.53,.23))
# Rear feet now support the exposed base rail rather than floating beneath the narrowed box.
for j,(old,x) in enumerate([('SoundboxFoot0',-8),('SoundboxFoot2',320)]):
 d.removeObject(old)
 add('LabRearFootStem'+str(j),cy(3,39,V(x,-157,-148),V(0,1,0)),'6 mm metal rear foot stem')
 add('LabRearFootPad'+str(j),cy(6,6,V(x,-163,-148),V(0,1,0)),'Replaceable rubber rear foot',(.08,.09,.10))
# Existing followers, rails and hangers retain their precise coordinates.
first,last=rows[0],rows[-1];slope=(last['follower_y']-first['follower_y'])/(last['station']-first['station'])
def level(x):return first['follower_y']+30+slope*(x-first['station'])
# Four slim posts flank the strings symmetrically around z=-25.
removed=[]
for o in list(d.Objects):
 if o.Name.startswith('Gantry') and o.Name not in ['GantryFrontRail','GantryRearRail']:
  removed.append(o.Name);d.removeObject(o.Name)
for j,x in enumerate([-26,334]):
 endx=[1.35,314.35][j]
 y=level(endx)
 for k,z in enumerate([-94,44]):
  add(f'LabPost{j}{k}',tube(V(x,-109,z),V(x,y,z),3,2),'6 × 1 mm aluminium end post')
  # Small flat mounting tab stays within the original envelope.
  foot=bx(14,3,6,x-7,-112,z-3).cut(cy(1.7,6,V(x-5,-114,z),V(0,1,0))).cut(cy(1.7,6,V(x+5,-114,z),V(0,1,0)))
  add(f'LabPostFoot{j}{k}',foot,'M3 bolted post tab')
 # Top bridge and rear projection support both existing diagonal clamp rails.
 add('LabHead'+str(j),tube(V(x,y,-124 if j==0 else -94),V(x,y,44),3,2),'6 × 1 mm aluminium removable top bridge')
 # Two small diagonal stays triangulate each end without a sheet panel.
 add('LabEndStay'+str(j),tube(V(x,-75,-94),V(x,y,44),2,1),'4 × 1 mm aluminium diagonal end stay')
 add('LabRearStay'+str(j),tube(V(endx,-109,-148),V(x,y,44),2,1),'4 × 1 mm aluminium rear drive-bay stay')
 # Telescoping end extensions put the end triangles beyond both string saddles.
 for k in range(2):
  zz=first['pivot_z']+(endx-first['station'])*10/24-(30 if k else 0)
  add(f'LabRailExtension{j}{k}',tube(V(x,y,zz),V(endx,y,zz),4,3),'8 × 1 mm aluminium removable rail end extension')
 # Rail attachments are visible split blocks, bored for both intersecting tubes.
 for k,rail in enumerate(['GantryFrontRail','GantryRearRail']):
  b=d.getObject(rail).Shape.BoundBox
  cx=endx-6 if j else endx
  cyy=level(cx)
  z=first['pivot_z']+(cx-first['station'])*10/24-(30 if k else 0)
  p=V(cx,cyy,z);a=V(1,slope,10/24);a.normalize()
  block=bx(12,12,13,cx-6,cyy-6,z-7).cut(cy(5.1,32,p-a*16,a)).cut(cy(3.1,20,p-V(0,0,10),V(0,0,1)))
  block=block.common(bx(500,300,202.286808,-60,-180,-156))
  add(f'LabRailClamp{j}{k}',block,'Visible split rail clamp — M3 clamping detail pending',(.69,.53,.23))
# A longitudinal tension X below the strings braces the rear bay against racking.
for j,(p,q) in enumerate([(V(1.35,-114,-148),V(314.35,-114,-98)),(V(1.35,-114,-98),V(314.35,-114,-148))]):
 add('LabRackingStay'+str(j),bar(p,q,1.25),'2.5 mm steel diagonal tie — adjustable clevis ends pending')
# Replace opaque low drive plates with open, triangulated end brackets.
for tag,x in [('Left',12.35),('Right',300.35)]:
 A=V(x,-83,-131);B=V(x,-59,-116);C=V(x,-93,-143.5);D=V(x,-93,-108.5)
 sh=cy(12,4,A).cut(cy(6.05,6,A-V(1,0,0))).fuse(cy(7,4,B).cut(cy(3.25,6,B-V(1,0,0))))
 for p in [C,D]:sh=sh.fuse(cy(5,4,p).cut(cy(2.2,6,p-V(1,0,0))))
 for p,q in [(A,B),(A,C),(A,D),(B,D),(C,D)]:sh=sh.fuse(bar(p,q,2).common(bx(4,100,100,x,-120,-170)))
 for p,r in [(A,6.05),(B,3.25),(C,2.2),(D,2.2),(A+V(0,8.7,0),1.7),(A-V(0,8.7,0),1.7)]:sh=sh.cut(cy(r,8,p-V(2,0,0)))
 d.getObject('DriveFrame'+tag+'Cheek').Shape=sh;d.getObject('DriveFrame'+tag+'Cheek').Label=tag+' open triangular drive bracket — 4 mm stock'
# Drill new post tabs through the soundboard.
for x in [-26,334]:
 for z in [-94,44]:
  for dx in [-5,5]:d.Baseplate_310x170x6.Shape=d.Baseplate_310x170x6.Shape.cut(cy(1.7,8,V(x+dx,-115,z),V(0,1,0)))
# Visible members pass through relieved wooden mounting interfaces.
for name in ['SoundboxShell','SoundboxEndBlock0','SoundboxEndBlock1','SoundboxMountRib0','SoundboxMountRib1','Baseplate_310x170x6','KotoAnchorBlock','KotoTunerBlock']:
 o=d.getObject(name);sh=o.Shape.copy()
 for nn in new:
  member=d.getObject(nn).Shape
  if sh.BoundBox.intersect(member.BoundBox):sh=sh.cut(member)
 o.Shape=sh
d.Label='Le Lovophone — open laboratory frame';d.Motion.Status='Open triangulated laboratory frame. Acoustic body centred around original strings; approved musical geometry and timing retained. Structural prototype; joint and load testing pending.'
d.recompute();invalid=[o.Name for o in d.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())];assert not invalid,invalid
bounds=App.BoundBox()
for o in d.Objects:
 if o.TypeId=='Part::Feature':bounds.add(world(o).BoundBox)
report=dict(new_parts=new,removed_parts=removed,colors=colors,previous_envelope_mm=[oldbounds.XLength,oldbounds.ZLength,oldbounds.YLength],envelope_mm=[bounds.XLength,bounds.ZLength,bounds.YLength],string_bank_centre_z_mm=-25,soundbox_centre_z_mm=-25,soundbox_width_mm=140,original_soundbox_width_mm=200,string_positions_unchanged=True,pitch_and_timing_unchanged=True,invalid_shapes=invalid,scope='Concept CAD. Tube dimensions provisional; clamp preload, joint stiffness, acoustic changes, loads, fatigue and physical safety unverified.')
(O/'Lovophone_Lab_Frame_Design.json').write_text(json.dumps(report,indent=2));d.saveAs(str(R/'work/Lovophone_Lab_Frame_Base.FCStd'));print(json.dumps({k:v for k,v in report.items() if k not in ['colors','new_parts','removed_parts']},indent=2),flush=True)
