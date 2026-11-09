import bpy,math,random
from mathutils import Vector
random.seed(70)
def material(name,color,metal=0,rough=.5):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
def cube(name,loc,size,mat,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 if bevel:b=o.modifiers.new('Soft hand-finished edges','BEVEL');b.width=bevel;b.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def curve(name,pts,r,mat,closed=False):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=12;c.bevel_depth=r;c.bevel_resolution=3;sp=c.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
 for bp,co in zip(sp.bezier_points,pts):bp.co=co;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
 sp.use_cyclic_u=closed;o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);return o
def lathe_path(name,pts,radii,mat):
 vs=[];faces=[];sides=16
 for j,(p,rad) in enumerate(zip(pts,radii)):
  p=Vector(p);t=Vector(pts[min(j+1,len(pts)-1)])-Vector(pts[max(0,j-1)]);t.normalize();a=t.cross(Vector((0,1,0)));a.normalize();b=t.cross(a)
  for k in range(sides):vs.append(p+rad*(math.cos(k*2*math.pi/sides)*a+math.sin(k*2*math.pi/sides)*b))
 for j in range(len(pts)-1):
  for k in range(sides):a=j*sides+k;b=j*sides+(k+1)%sides;faces.append((a,b,b+sides,a+sides))
 faces.extend([tuple(range(sides-1,-1,-1)),tuple((len(pts)-1)*sides+k for k in range(sides))]);me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat)
 for p in me.polygons:p.use_smooth=True
 sub=o.modifiers.new('Carved smooth profile','SUBSURF');sub.levels=2;return o
def setup():
 s=bpy.context.scene;wood=material('Louis XV polished walnut',(.16,.056,.018),0,.25);gold=material('Antique ormolu restrained highlights',(.48,.29,.075),.78,.28);inlay=material('Boxwood marquetry',(.42,.24,.09),0,.34);ivory=material('Warm Paris plaster',(.68,.65,.59),0,.82);trim=material('Cream painted mouldings',(.79,.76,.69),0,.48);white=material('White photographic paper',(.86,.86,.84),0,.82);black=material('Studio black',(.018,.02,.022),.15,.5);steel=material('Chrome light stands',(.3,.34,.36),.85,.22)
 # Fine figured wood, not heavy surface relief.
 nt=wood.node_tree;tc=nt.nodes.new('ShaderNodeTexCoord');mapping=nt.nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(3,45,5);noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5;noise.inputs['Detail'].default_value=3;ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.035,.008,.002,1);ramp.color_ramp.elements[1].color=(.22,.075,.019,1);nt.links.new(tc.outputs['Generated'],mapping.inputs[0]);nt.links.new(mapping.outputs[0],noise.inputs[0]);nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],nt.nodes.get('Principled BSDF').inputs['Base Color'])
 # Serpentine tabletop, 92 x60 cm. Machine feet stay at Z=0.
 outline=[]
 for j in range(128):
  a=2*math.pi*j/128;x=.46*math.copysign(abs(math.cos(a))**.34,math.cos(a));y=.30*math.copysign(abs(math.sin(a))**.34,math.sin(a));x*=1+.014*math.cos(6*a);y*=1+.018*math.cos(6*a);outline.append((x,y))
 verts=[(x,y,z) for z in [-.032,0] for x,y in outline];faces=[tuple(range(127,-1,-1)),tuple(range(128,256))]+[(j,(j+1)%128,(j+1)%128+128,j+128) for j in range(128)];me=bpy.data.meshes.new('Serpentine top');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Louis XV walnut serpentine top',me);s.collection.objects.link(o);o.data.materials.append(wood);b=o.modifiers.new('Rounded tabletop lip','BEVEL');b.width=.004;b.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 for scale,z,r,mat in [(1.0,-.008,.0022,gold),(.94,.001,.0011,inlay),(.88,.001,.00065,inlay)]:curve('Marquetry and ormolu tabletop border',[(x*scale,y*scale,z) for x,y in outline[::2]],r,mat,True)
 # Four sculpted S-curved cabriole legs, gilt knees and scroll feet.
 for sx in [-1,1]:
  for sy in [-1,1]:
   pts=[(sx*.36,sy*.21,-.033),(sx*.39,sy*.24,-.09),(sx*.405,sy*.255,-.17),(sx*.385,sy*.24,-.29),(sx*.335,sy*.20,-.48),(sx*.34,sy*.205,-.63),(sx*.372,sy*.225,-.71)]
   lathe_path('Cabriole walnut leg',pts,[.026,.032,.028,.020,.012,.014,.022],wood)
   curve('Ormolu knee scroll',[(sx*.38,sy*.24,-.055),(sx*.417,sy*.27,-.12),(sx*.414,sy*.267,-.19),(sx*.398,sy*.256,-.23)],.003,gold)
   curve('Gilded hoof scroll',[(sx*.35,sy*.215,-.66),(sx*.39,sy*.24,-.699),(sx*.40,sy*.245,-.714),(sx*.37,sy*.226,-.719)],.004,gold)
 # Scalloped aprons with balanced rocaille scroll ornaments.
 for sy in [-1,1]:
  xs=[-.36+i*.72/48 for i in range(49)];vs=[(x,sy*(.225+.008*math.cos(2*math.pi*x/.72)),z) for z in [-.031] for x in xs]
  vs +=[(x,sy*(.225+.008*math.cos(2*math.pi*x/.72)),-.08-.035*math.cos(math.pi*x/.72)**4) for x in xs];fa=[(i,i+1,50+i,49+i) for i in range(48)];m=bpy.data.meshes.new('Carved apron');m.from_pydata(vs,[],fa);m.update();ob=bpy.data.objects.new('Louis XV scalloped apron',m);s.collection.objects.link(ob);ob.data.materials.append(wood);mod=ob.modifiers.new('Apron depth','SOLIDIFY');mod.thickness=.014
  curve('Gold scalloped apron piping',vs[49:],.0016,gold)
  for sign in [-1,1]:curve('Rocaille foliate scroll',[(sign*.015,sy*.244,-.065),(sign*.065,sy*.244,-.045),(sign*.13,sy*.242,-.065),(sign*.17,sy*.241,-.052),(sign*.14,sy*.242,-.042)],.002,gold)
  # A small shell motif rather than a flat decorative disc.
  for k in range(-3,4):curve('Central shell carving',[(k*.003,sy*.247,-.087),(k*.006,sy*.251,-.065),(k*.004,sy*.247,-.051)],.0013,gold)
 for sx in [-1,1]:
  cube('Walnut side apron',(sx*.37,0,-.065),(.018,.43,.065),wood,.006)
  curve('Side apron gold flourish',[(sx*.382,-.19,-.08),(sx*.382,-.08,-.094),(sx*.382,0,-.07),(sx*.382,.08,-.094),(sx*.382,.19,-.08)],.0018,gold)
 setup.subject_objects=[o.name for o in bpy.data.objects if o.type in ['MESH','CURVE']]
 floor=-.73
 # Parisian studio shell: pale mouldings, tall French windows, empty working set.
 parquet=[material('Oak parquet '+str(i),(.045+.005*i,.019+.0025*i,.007+.0015*i),0,.48) for i in range(8)]
 cube('Parquet subfloor',(0,0,floor-.03),(8,9,.06),parquet[3])
 # Chevron parquet boards, merged per material for economical rendering.
 for mi,mat in enumerate(parquet):
  vs=[];fa=[]
  tile=0
  for i in range(-11,12):
   for j in range(-46,47):
    for side in [0,1]:
     tile+=1
     if (i*17+j*13+side*3)%8!=mi:continue
     span=.198;step=.099;x=i*2*span+side*span;y=j*step
     corners=[(x,y),(x+span,y+(span if side==0 else -span)),(x+span,y+(span if side==0 else -span)+step),(x,y+step)]
     cx=sum(a for a,b in corners)/4;cy=sum(b for a,b in corners)/4;base=len(vs)
     for a,b in corners:vs.append((cx+(a-cx)*.993,cy+(b-cy)*.993,floor+.001))
     fa.append(tuple(base+k for k in range(4)))
  me=bpy.data.meshes.new('Parquet');me.from_pydata(vs,[],fa);me.update();ob=bpy.data.objects.new('Chevron parquet oak',me);s.collection.objects.link(ob);ob.data.materials.append(mat)
 for x in [-4,4]:cube('Studio side wall',(x,0,1.2),(.12,9,3.86),ivory)
 for y in [-4.5,4.5]:cube('Studio end wall',(0,y,1.2),(8,.12,3.86),ivory)
 # Wall panel mouldings and cornices; room remains visible opposite the sweep.
 for y in [-4.42,4.42]:
  for z,h in [(floor+.12,.18),(.1,.035),(2.65,.09),(2.73,.045)]:cube('Haussmann moulding',(0,y,z),(7.9,.045,h),trim,.006)
  for x in [-3,-1.5,0,1.5,3]:
   for z in [-.17,1.25]:
    w=1.28;h=.56 if z<0 else 1.7
    curve('Paris wall panel',[(x-w/2,y-.012,z-h/2),(x+w/2,y-.012,z-h/2),(x+w/2,y-.012,z+h/2),(x-w/2,y-.012,z+h/2)],.009,trim,True)
 for z,h in [(floor+.12,.18),(.1,.035),(2.65,.09),(2.73,.045)]:cube('East wall cornice',(3.92,0,z),(.045,8.9,h),trim,.006)
 for y in [-3,-1.5,0,1.5,3]:
  curve('East wall panel',[(3.90,y-.62,.38),(3.90,y+.62,.38),(3.90,y+.62,2.18),(3.90,y-.62,2.18)],.009,trim,True)
 # Bright tall windows on left wall: exterior light panels, mullions, radiator.
 sky=material('Overcast Paris daylight',(.73,.82,.9),0,.3);p=sky.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.73,.82,.9,1);p.inputs['Emission Strength'].default_value=.8
 for y in [-2.5,0,2.5]:
  cube('Tall luminous French window',(-3.925,y,1.12),(.018,1.55,2.60),sky)
  for yy in [y-.80,y,y+.80]:cube('French window vertical frame',(-3.88,yy,1.12),(.06,.035,2.68),trim,.003)
  for z in [-.22,.45,1.12,1.79,2.46]:cube('Window cross bar',(-3.875,y,z),(.065,1.64,.035),trim,.003)
  for k in range(15):cube('Cast iron radiator flute',(-3.72,y-.63+k*.09,-.45),(.16,.055,.42),trim,.017)
  # Faint zinc roof silhouette outside; no people.
  # Diffuse overcast daylight beyond the glazing.
 # Real single white paper sweep: reverse camera sees the open studio, not a wraparound box.
 # Backdrop to +Y; paper rolls toward the table and under its feet.
 pts=[(-2.6,floor+.006),(2.8,floor+.006)]
 for j in range(1,25):
  a=math.pi/2*j/24;pts.append((2.8+.75*math.sin(a),floor+.006+.75*(1-math.cos(a))))
 pts.append((3.55,2.7));vs=[(x,y,z) for x in [-2.1,2.1] for y,z in pts];n=len(pts);fa=[(j,j+1,n+j+1,n+j) for j in range(n-1)];me=bpy.data.meshes.new('Seamless white paper sweep');me.from_pydata(vs,[],fa);me.update();ob=bpy.data.objects.new('White photographers seamless sheet',me);s.collection.objects.link(ob);ob.data.materials.append(white)
 for p in me.polygons:p.use_smooth=True
 # Paper support, stands, softboxes and a quiet empty stool outside the turntable view.
 def stand(x,y,h):
  curve('Chrome studio upright',[(x,y,floor+.02),(x,y,h)],.013,steel)
  for a in [0,2.094,4.189]:curve('Light stand tripod',[(x,y,floor+.25),(x+.36*math.cos(a),y+.36*math.sin(a),floor+.025)],.01,steel)
 for x in [-2.25,2.25]:stand(x,3.57,2.75)
 curve('Backdrop crossbar',[(-2.3,3.57,2.74),(2.3,3.57,2.74)],.018,steel)
 for x,y in [(2.6,-1.7),(-2.5,-1.5)]:
  stand(x,y,1.8);ob=cube('Photography softbox',(x,y,1.8),(.10,.75,.95),black,.04);ob.rotation_euler.z=math.atan2(y,x)
  ob=cube('Softbox diffusion cloth',(x-.06*(1 if x>0 else -1),y,1.8),(.012,.70,.90),white,.018);ob.rotation_euler.z=math.atan2(y,x)
 cube('Empty studio stool',(2.7,-3.0,-.20),(.42,.42,.06),wood,.025)
 for dx in [-.15,.15]:
  for dy in [-.15,.15]:curve('Stool leg',[(2.7+dx,-3+dy,-.23),(2.7+dx*1.2,-3+dy*1.2,floor)],.018,wood)
 # Replace close product lights with broad studio illumination; keep metal reflections soft.
 for ob in list(bpy.data.objects):
  if ob.type=='LIGHT':bpy.data.objects.remove(ob,do_unlink=True)
 for name,loc,power,size in [('Large window key',(-2.6,-1.0,1.9),450,.8),('Cool low fill',(1.7,-2,1.1),40,1.5),('Warm edge light',(.4,1.6,1.5),300,.65)]:
  l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;l.color=(1,.85,.66) if 'edge' in name else ((.72,.83,1) if 'fill' in name else (1,.96,.88));ob=bpy.data.objects.new(name,l);s.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,-.1))-ob.location).to_track_quat('-Z','Y').to_euler()
 s.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.70,.78,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.12;s.view_settings.exposure=-.3;s.render.film_transparent=False
 return dict(table='Procedurally modelled Louis XV-style walnut, marquetry and ormolu table; cabriole legs and rocaille apron',room='Unoccupied Parisian-inspired photography studio, French windows, cream mouldings, chevron parquet and a single white paper sweep',people=False)
