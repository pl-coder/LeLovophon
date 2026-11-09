import bpy
from mathutils import Vector
def apply_studio():
 s=bpy.context.scene;s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=32;s.view_settings.view_transform='AgX';s.view_settings.exposure=-1
 def mat(name,col,metal,rough):
  m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*col,1);n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough;return m
 aluminium=mat('Satin aluminium',(.48,.54,.58),.8,.3);brass=mat('Machined warm brass',(.48,.27,.07),.8,.3);teal=mat('Teal anodised aluminium',(.02,.21,.18),.65,.28);bearing=mat('Bearing steel',(.12,.14,.16),.9,.23);nylon=mat('Natural nylon',(.77,.71,.57),0,.35);pom=mat('Ivory engineering polymer',(.55,.57,.5),0,.36);wood=mat('Oiled walnut',(.24,.08,.025),0,.38)
 nt=wood.node_tree;coord=nt.nodes.new('ShaderNodeTexCoord');scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(2,75,8);tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=4;tex.inputs['Detail'].default_value=3;nt.links.new(coord.outputs['Generated'],scale.inputs[0]);nt.links.new(scale.outputs[0],tex.inputs[0]);ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.035,.009,.003,1);ramp.color_ramp.elements[1].color=(.24,.075,.02,1);nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],nt.nodes.get('Principled BSDF').inputs['Base Color']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.08;bump.inputs['Distance'].default_value=.00015;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],nt.nodes.get('Principled BSDF').inputs['Normal'])
 for ob in bpy.data.objects:
  if ob.type!='MESH':continue
  name=ob.name;m=aluminium
  if any(x in name for x in ['Soundbox','KotoAnchorBlock','KotoTunerBlock','Pedestal','ThirdBridge']):m=wood
  elif any(x in name for x in ['TubeArm','HandGrip']):m=teal
  elif any(x in name for x in ['Gear','Crank','Rocker','PendulumHub','TipSocket','HandInputWheel','Saddle','BridgeCrown']):m=brass
  elif any(x in name for x in ['Bearing','Shaft']):m=bearing
  elif 'Coupler' in name:m=pom
  elif any(x in name for x in ['String','PETPick','TieKnot']):m=nylon
  ob.data.materials.clear();ob.data.materials.append(m)
 s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.25,.29,.36,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
 for name,loc,power,size in [('Soft key',(.3,-.45,.65),24,.55),('Long rim',(-.35,.3,.55),32,.4),('Front fill',(.55,.15,.4),16,.4)]:
  light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;ob=bpy.data.objects.new(name,light);s.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,-.03,.12))-ob.location).to_track_quat('-Z','Y').to_euler()

 # Denoise the studio image; preserve the original coverage mask for clean key edges.
 s.use_nodes=True;nt=s.node_tree;nt.nodes.clear();rl=nt.nodes.new('CompositorNodeRLayers');dn=nt.nodes.new('CompositorNodeDenoise');alpha=nt.nodes.new('CompositorNodeSetAlpha');alpha.mode='REPLACE_ALPHA';out=nt.nodes.new('CompositorNodeComposite');nt.links.new(rl.outputs['Image'],dn.inputs['Image']);nt.links.new(dn.outputs['Image'],alpha.inputs['Image']);nt.links.new(rl.outputs['Alpha'],alpha.inputs['Alpha']);nt.links.new(alpha.outputs['Image'],out.inputs['Image'])
