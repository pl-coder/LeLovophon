"""Neutral CAD inspection views, not a physical validation or presentation film."""
import bpy,json,math
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'outputs/LeLovophon_Pluck_Layout_R5'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE_NEXT';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.render_aa='16';s.display.shading.background_type='WORLD';s.world.color=(.055,.065,.075);s.view_settings.view_transform='Standard'
def p(v):return (v[0]/1000,(-v[2]-20)/1000,(v[1]+168)/1000)
for m in json.loads((R/'work/pluck_r5/mesh.json').read_text()):
 mesh=bpy.data.meshes.new(m['name']);mesh.from_pydata([p(v) for v in m['vertices']],[],m['triangles']);mesh.update();ob=bpy.data.objects.new(m['name'],mesh);s.collection.objects.link(ob)
 mat=bpy.data.materials.new(m['name']);mat.diffuse_color=(*m['color'],1);mesh.materials.append(mat)
 for f in mesh.polygons:f.use_smooth=True
 mesh.set_sharp_from_angle(angle=math.radians(35))

# Restrained studio materials; geometry remains the exact saved CAD mesh.
inv={p['name']:p for p in json.loads((O/'Part_Inventory.json').read_text())}
for ob in s.objects:
 kind=inv[ob.name]['material'];mat=ob.data.materials[0];mat.use_nodes=True;nd=mat.node_tree.nodes.get('Principled BSDF')
 col=mat.diffuse_color
 nd.inputs['Base Color'].default_value=col
 nd.inputs['Metallic'].default_value=.75 if kind in ['Aluminium','Steel','Brass','Bearing steel','Spring steel'] else 0
 nd.inputs['Roughness'].default_value=.28 if kind=='Aluminium' else .31 if kind in ['Steel','Brass','Bearing steel'] else .40
 if kind in ['Beech','Birch plywood','Spruce']:
  nd.inputs['Roughness'].default_value=.40
  tex=mat.node_tree.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5;tex.inputs['Detail'].default_value=3
  coord=mat.node_tree.nodes.new('ShaderNodeTexCoord');mapping=mat.node_tree.nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(3,55,4)
  mat.node_tree.links.new(coord.outputs['Generated'],mapping.inputs[0]);mat.node_tree.links.new(mapping.outputs[0],tex.inputs['Vector'])
  ramp=mat.node_tree.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[1].position=.8
  if kind=='Spruce':lo=(.28,.13,.035,1);hi=(.62,.38,.14,1)
  else:lo=(.055,.016,.006,1);hi=(.25,.095,.028,1)
  ramp.color_ramp.elements[0].color=lo;ramp.color_ramp.elements[1].color=hi;mat.node_tree.links.new(tex.outputs['Fac'],ramp.inputs[0]);mat.node_tree.links.new(ramp.outputs['Color'],nd.inputs['Base Color'])
 if 'PendulumAssembly' in ob.name or ob.name=='FreelyRotatingGrip':nd.inputs['Base Color'].default_value=(.014,.19,.15,1);nd.inputs['Metallic'].default_value=.3
 # Tiny edge bevel catches the light; it is a visual finish, not a change to load-bearing CAD geometry.
 if kind in ['Aluminium','Steel','Brass','Beech','Birch plywood','Spruce']:
  mod=ob.modifiers.new('Deburred edge highlight','BEVEL');mod.width=.00022;mod.segments=2;mod.limit_method='ANGLE'
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.75,.8,.9,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
for loc,power,size in [((.4,-.65,1.3),150,1.1),((-.75,-.2,.65),90,.8),((.1,.75,1),180,.8)]:
 ld=bpy.data.lights.new('Large softbox','AREA');ld.energy=power;ld.shape='DISK';ld.size=size;ob=bpy.data.objects.new('Softbox',ld);s.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,.1))-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.016));floor=bpy.context.object;fm=bpy.data.materials.new('Warm white studio');fm.use_nodes=True;fm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.055,.065,.075,1);fm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8;floor.data.materials.append(fm)
s.view_settings.view_transform='AgX';s.view_settings.exposure=-1.1;s.view_settings.look='AgX - Medium High Contrast';s.render.image_settings.color_mode='RGBA';s.eevee.taa_render_samples=64
cd=bpy.data.cameras.new('Protokoto R3 inspection');cam=bpy.data.objects.new('Camera',cd);s.collection.objects.link(cam);s.camera=cam;cd.type='ORTHO';cd.ortho_scale=.50
def render(name,loc,target,width,height,scale):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale
 s.render.resolution_x=width;s.render.resolution_y=height;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(O/name);bpy.ops.render.render(write_still=True)
render('R5_Studio_Overview.png',(.67,-1.05,.53),(0,.005,.14),1800,1100,.89)
render('R5_Studio_Rear.png',(-.68,1.05,.45),(0,.025,.14),1800,1100,.91)
