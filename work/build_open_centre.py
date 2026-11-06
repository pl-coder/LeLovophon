import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,math,json
from FreeCAD import Vector as V
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
doc=App.openDocument(OUT+'/Harpe_d_Amour_Wide_Swing_Live.FCStd')
rows=json.loads(doc.Motion.LinkageGeometry)
shift=78.35
old_rows=[dict(r) for r in rows]
def cy(r,h,p,axis=V(1,0,0)):return Part.makeCylinder(r,h,p,axis)
def bx(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def add(name,shape,parent,label=None):
 o=doc.getObject(name) or doc.addObject('Part::Feature',name);o.Shape=shape;parent.addObject(o)
 if label:o.Label=label
 return o
def strap(x,y1,z1,y2,z2,width=6):
 d=V(0,y2-y1,z2-z1);d.normalize();p=V(0,-d.z,d.y)*width/2;a=V(x,y1,z1);b=V(x,y2,z2)
 return Part.Face(Part.makePolygon([a+p,b+p,b-p,a-p,a+p])).extrude(V(4,0,0))
# Remove the transparent enclosure from this open-frame version.
if doc.getObject('DriveGuard'):
 for o in list(doc.DriveGuard.Group):doc.removeObject(o.Name)
 doc.removeObject('DriveGuard')
fixed_names=['CommonInputShaft_D6','CommonIntermediateAxle','LowGearboxTray','ClockworkInputCoupling','LowInputStand0','LowInputStand1','LowInputBearing0','LowInputBearing1','IntermediateAxleStand0','IntermediateAxleStand1']
for row in rows:
 n=row['note']
 for suffix in ['_Driver','_Output','_LongArmRotor','_Rocker']:
  o=doc.getObject(n+suffix);p=o.Placement;p.Base.x+=shift;o.Placement=p
 for suffix in ['_RatioBelt','_SwingStepUpBelt']:
  fixed_names.append(n+suffix)
 for j in range(2):
  fixed_names.extend([n+'_PendulumBearing'+str(j),n+'_FollowerPivotBearing'+str(j)])
 row['station']+=shift
for name in fixed_names:
 o=doc.getObject(name)
 if o:
  sh=o.Shape.copy();sh.translate(V(shift,0,0));o.Shape=sh
# Strengthened bearing rails with two closed bores and an outboard triangular brace.
for row in rows:
 n=row['note'];s=row['station'];uy=row['pivot_y'];z=row['pivot_z'];fz=row['follower_z']
 for j,off in enumerate([-5.5,0]):
  x=s+off;post=bx(4,uy+119,8,x,-109,-154);beam=bx(4,20,z+164,x,uy-10,-154)
  shape=post.fuse(beam)
  if j==0:shape=shape.fuse(strap(x,-60,-150,uy-8,z-12))
  shape=shape.cut(cy(6.05,6,V(x-1,uy,z))).cut(cy(6.05,6,V(x-1,uy,fz)))
  o=doc.getObject(n+'_PendulumBracket'+str(j));o.Shape=shape;o.Label=n+' 4 mm aluminium bearing plate'+(' — braced' if j==0 else '')
  if 'MaterialIntent' not in o.PropertiesList:o.addProperty('App::PropertyString','MaterialIntent','Design')
  o.MaterialIntent='4 mm aluminium plate; closed bearing bores with ten-millimetre half-height webs; bolted removable module. Strength and fatigue sizing pending.'
 # Removable mounting shoe; pockets locate the two vertical plates.
 shoe=bx(16,3,22,s-7,-109,-155)
 for xx in [s-5,s+5]:shoe=shoe.cut(cy(2.25,5,V(xx,-110,-139),V(0,1,0)))
 for off in [-5.5,0]:shoe=shoe.cut(bx(4.1,2,8.1,s+off-.05,-107,-154.05))
 add(n+'_CassetteMountShoe',shoe,doc.Structure,n+' removable module shoe — two M4 fixing holes')
# Shallow plywood soundbox: three-millimetre lid, six-millimetre sides and four-millimetre bottom.
lid=bx(370,3,200,-30,-112,-155)
for x in [-20,330]:
 for z in [-145,35]:lid=lid.cut(cy(2.75,5,V(x,-113,z),V(0,1,0)))
doc.Baseplate_310x170x6.Shape=lid;doc.Baseplate_310x170x6.Label='3 mm soundboard lid — removable from plywood rim'
shell=bx(370,45,200,-30,-157,-155).cut(bx(358,42,188,-24,-153,-149))
for x in [164,200,236]:shell=shell.cut(cy(8,12,V(x,-134,36),V(0,0,1)))
doc.SoundboxShell.Shape=shell;doc.SoundboxShell.Label='Shallow plywood soundbox — 6 mm sides, 4 mm bottom'
for i,x in enumerate([-24,326]):doc.getObject('SoundboxEndBlock'+str(i)).Shape=bx(14,41,188,x,-153,-149)
for i,(x,z) in enumerate([(-18,-140),(-18,22),(310,-140),(310,22)]):doc.getObject('SoundboxFoot'+str(i)).Shape=bx(20,6,20,x,-163,z)
# Perforated internal ribs take mounting loads to the rim rather than relying on the thin lid.
for i,x in enumerate([shift-12,shift+136]):
 rib=bx(6,41,188,x,-153,-149).cut(bx(8,25,156,x-1,-145,-133))
 add('SoundboxMountRib'+str(i),rib,doc.Soundbox,'Plywood mounting rib — lightened frame')
# Record the unchanged lengths, ratios and independent swing angles.
doc.Motion.LinkageGeometry=json.dumps(rows)
doc.Motion.Status='Open, centred, serviceable briefcase-scale study. Removable modules, 4 mm aluminium bearing plates, shallow plywood soundbox. Travel layout, fastener retention, belt selection, string loads and structural validation remain provisional.'
doc.Label="L'Harpe d'Amour — open centred bank"
doc.recompute();doc.saveAs(OUT+'/Harpe_d_Amour_Open_Centred.FCStd')
with open(OUT+'/open_centred_geometry.json','w') as f:json.dump({'rows':rows,'bank_shift_mm':shift,'bank_pick_centre_x_mm':155,'operating_base_mm':[370,200],'provisional_briefcase_internal_mm':[400,280,100],'scope':doc.Motion.Status},f,indent=2)
print('Open centred model saved; modules shifted',shift,'mm')
