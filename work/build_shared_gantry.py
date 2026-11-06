import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,math,json
from FreeCAD import Vector as V
OUT=(_LOVOPHON_WORKSPACE + '/outputs');doc=App.openDocument(OUT+'/Harpe_d_Amour_Clockwork.FCStd');rows=json.loads(doc.Motion.LinkageGeometry)
old=[]
for r in rows:
 for j in range(2):old.append(r['note']+'_PendulumBracket'+str(j))
 old.append(r['note']+'_CassetteMountShoe')
oldvol=sum(doc.getObject(n).Shape.Volume for n in old)
for n in old:doc.removeObject(n)
g=doc.addObject('App::DocumentObjectGroup','SharedGantry');g.Label='Shared lightweight gantry — removable hanging bearing forks'
colors={};metal=[]
def bx(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def cy(r,h,p,axis=V(1,0,0)):return Part.makeCylinder(r,h,p,axis)
def tube(p,q,ro=5,ri=4):
 v=q-p;return cy(ro,v.Length,p,v).cut(cy(ri,v.Length+2,p-v/v.Length,v))
def add(n,s,label,col=(.69,.73,.75),al=True):
 o=doc.addObject('Part::Feature',n);o.Shape=s;o.Label=label;g.addObject(o);colors[n]=col
 if al:metal.append(n)
 return o
first,last=rows[0],rows[-1];s0=first['station'];s1=last['station'];slope=(last['follower_y']-first['follower_y'])/(s1-s0)
def level(x):return first['follower_y']+30+slope*(x-s0)
def lane(x,rear=False):return first['pivot_z']+(x-s0)*10/24-(30 if rear else 0)
axis=V(1,slope,10/24);axis.normalize();left=s0-15;right=s1+28
for rear in [False,True]:
 p=V(left,level(left),lane(left,rear));q=V(right,level(right),lane(right,rear));o=add('Gantry'+('Rear' if rear else 'Front')+'Rail',tube(p,q),'Shared 10 × 1 mm aluminium tube — '+('follower' if rear else 'arm')+' rail')
 o.addProperty('App::PropertyString','SectionIntent','Design');o.SectionIntent='10 mm outside diameter, 1 mm wall; stiffness, fatigue and clamp slip require validation.'
# Two end frames; all four feet remain behind the strings.
mountcuts=[]
for tag,x in [('Left',left),('Right',right)]:
 y=level(x);fz=lane(x,False)
 for k,z in enumerate([-148,-112]):
  add('Gantry'+tag+'Post'+str(k),tube(V(x,-106,z),V(x,y,z)),'Gantry '+tag.lower()+' end post — hollow 10 mm tube')
  foot=bx(18,3,12,x-9,-109,z-6)
  for dx in [-7,7]:
   hole=cy(1.7,6,V(x+dx,-110,z),V(0,1,0));foot=foot.cut(hole);mountcuts.append(hole)
  add('Gantry'+tag+'Foot'+str(k),foot,'Removable gantry foot — two M3 mounting holes')
 add('Gantry'+tag+'Crosshead',tube(V(x,y,-148),V(x,y,fz)),'Gantry '+tag.lower()+' crosshead — hollow 10 mm tube')
 add('Gantry'+tag+'Brace',tube(V(x,-55,-112),V(x,y,fz),3.5,2.5),'Gantry '+tag.lower()+' end brace — hollow 7 mm tube')
# Independent clamp-on bearing forks retain both original bearing positions per shaft.
for r in rows:
 n=r['note'];s=r['station'];top=level(s)
 for typ,uy,z in [('Arm',r['pivot_y'],r['pivot_z']),('Follower',r['follower_y'],r['follower_z'])]:
  clamp=bx(12,7.8,22,s-6.5,top-8,z-11);cap=bx(12,7.8,22,s-6.5,top+.2,z-11)
  bore=cy(5.15,32,V(s,top,z)-axis*16,axis);clamp=clamp.cut(bore);cap=cap.cut(bore)
  for off in [-5.5,0]:
   x=s+off
   ring=cy(8.5,4,V(x,uy,z)).cut(cy(6.05,6,V(x-1,uy,z)))
   stem=bx(4,top-uy-13.5,6,x,uy+6,z-3)
   clamp=clamp.fuse(ring.fuse(stem))
  for zz in [z-8,z+8]:
   hole=cy(1.7,20,V(s-.5,top-9,zz),V(0,1,0));clamp=clamp.cut(hole);cap=cap.cut(hole)
   bolt=cy(1.5,16,V(s-.5,top-8,zz),V(0,1,0)).fuse(cy(2.5,2,V(s-.5,top+8,zz),V(0,1,0)))
   # Nominal hex recess to make removable fasteners readable in the model.
   pts=[V(s-.5+1.2*math.cos(k*math.pi/3),top+9,zz+1.2*math.sin(k*math.pi/3)) for k in range(6)]
   recess=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,2,0));bolt=bolt.cut(recess)
   add(n+'_'+typ+'ClampBolt'+('L' if zz<z else 'R'),bolt,n+' '+typ.lower()+' clamp M3 screw — thread envelope',(.45,.48,.51),False)
  o=add(n+'_'+typ+'HangingFork',clamp,n+' '+typ.lower()+' hanging fork — paired bearing cheeks')
  o.addProperty('App::PropertyString','RetentionIntent','Design');o.RetentionIntent='Split clamp with two M3 screws. Original bearing seats retained; axial bearing retention and screw preload still require engineering.'
  add(n+'_'+typ+'ClampCap',cap,n+' '+typ.lower()+' removable clamp cap')
# New matching mounting holes through the lid; previous module holes remain available but unused.
sh=doc.Baseplate_310x170x6.Shape.copy()
for cut in mountcuts:sh=sh.cut(cut)
doc.Baseplate_310x170x6.Shape=sh
newvol=sum(doc.getObject(n).Shape.Volume for n in metal)
g.addProperty('App::PropertyString','DesignIntent','Design');g.DesignIntent='Two shared hollow rails on braced end frames. Twelve split-clamp hanging forks, each with the two original bearing seats. Original pivots, harmonic ratios and wide swings are unchanged.'
g.addProperty('App::PropertyString','ValidationScope','Design');g.ValidationScope='Provisional aluminium sections. Bearing retention, clamp preload, tube crushing, deflection, vibration, fatigue and soundboard mounting loads require engineering.'
doc.Label="L’Harpe d’Amour — open shared gantry"
doc.Motion.Status='Shared tube gantry replaces twelve tall bearing plates and six module shoes. Harmonic geometry unchanged. Provisional sections; stiffness, clamp slip and structural load paths remain unverified.'
doc.recompute();invalid=[o.Name for o in doc.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())];assert not invalid,invalid
doc.saveAs(OUT+'/../work/Harpe_d_Amour_Shared_Gantry.FCStd')
json.dump(colors,open(OUT+'/../work/gantry_colors.json','w'))
report={'removed_parts':old,'new_gantry_parts':[o.Name for o in g.Group],'old_support_volume_mm3':oldvol,'new_aluminium_volume_mm3':newvol,'support_aluminium_volume_reduction_percent':100*(oldvol-newvol)/oldvol,'old_support_aluminium_mass_kg':oldvol*2.7e-6,'new_support_aluminium_mass_kg':newvol*2.7e-6,'comparison_scope':'Assumes all old plates/shoes and new structural members are aluminium. New clamp screws, existing bearings and unmodelled mounting hardware excluded. Material-volume comparison, not structural equivalence.','unchanged_pivots_and_ratios':True,'invalid_shapes':invalid,'scope':g.ValidationScope}
json.dump(report,open(OUT+'/gantry_design_check.json','w'),indent=2)
print(json.dumps({k:v for k,v in report.items() if k not in ['removed_parts','new_gantry_parts']},indent=2),flush=True)
