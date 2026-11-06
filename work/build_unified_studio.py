import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,math,json,time,os,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs';start=time.time()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for data in list(bpy.data.materials):bpy.data.materials.remove(data)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_denoising=True;scene.cycles.adaptive_threshold=.018;scene.cycles.max_bounces=8;scene.cycles.diffuse_bounces=4;scene.cycles.glossy_bounces=4;scene.cycles.transmission_bounces=8;scene.cycles.transparent_max_bounces=8
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
 prefs.compute_device_type='METAL';prefs.get_devices()
 for device in prefs.devices:device.use=device.type=='METAL'
 scene.cycles.device='GPU'
except Exception:scene.cycles.device='CPU'
scene.render.resolution_x=2400;scene.render.resolution_y=1600;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-2.0
scene.render.fps=24;scene.frame_start=1;scene.frame_end=230400
world=bpy.data.worlds.new('Soft neutral studio');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.36,.40,.46,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.15

def material(name,col,metal=0,rough=.4,coat=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;p.inputs['Coat Weight'].default_value=coat
 return m,p

def wood(name,light,dark):
 m,p=material(name,light,rough=.38,coat=.18);n=m.node_tree.nodes;l=m.node_tree.links
 tex=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(3,100,48);l.new(tex.outputs['Generated'],mapping.inputs[0])
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3;noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.68;l.new(mapping.outputs['Vector'],noise.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.2;ramp.color_ramp.elements[0].color=(*dark,1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(*light,1);l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.00012;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal']);return m
walnut=wood('Oiled walnut — long grain',(.24,.115,.050),(.065,.025,.010))
spruce=wood('Honey spruce soundboard',(.63,.41,.18),(.32,.17,.055))
maplewood=wood('Maple bridge blocks',(.57,.40,.19),(.29,.17,.066))
plywood=wood('Birch plywood drive deck',(.50,.34,.16),(.25,.145,.055))
steel,p=material('Brushed steel stock',(.40,.43,.47),.92,.3)
aluminium,pal=material('Satin aluminium tubing',(.57,.61,.65),.87,.28)
brass,pbr=material('Satin brass fittings',(.54,.32,.095),.86,.27)
teal,pt=material('Satin teal plucker arms',(.025,.20,.17),.55,.28,coat=.15)
black,p=material('Rubber timing belts',(.014,.017,.02),0,.62)
nylon,pn=material('Unwound ivory nylon',(.73,.69,.54),0,.24);pn.inputs['IOR'].default_value=1.53;pn.inputs['Transmission Weight'].default_value=.22
pickmat,p=material('Replaceable cream nylon picks',(.71,.66,.48),0,.37)
seal,p=material('Bearing shields',(.055,.065,.07),.35,.38)
pcb,p=material('Controller PCB green',(.018,.12,.055),.12,.4)
clear,pc=material('Clear acrylic shields',(.94,.98,1),0,.08);pc.inputs['Transmission Weight'].default_value=1;pc.inputs['IOR'].default_value=1.49
for mat,ps in [(steel,bpy.data.materials['Brushed steel stock'].node_tree.nodes['Principled BSDF']),(aluminium,pal),(brass,pbr)]:
 n=mat.node_tree.nodes;l=mat.node_tree.links;t=n.new('ShaderNodeTexCoord');v=n.new('ShaderNodeVectorMath');v.operation='MULTIPLY';v.inputs[1].default_value=(4,550,550);l.new(t.outputs['Generated'],v.inputs[0]);no=n.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=4;no.inputs['Detail'].default_value=2;l.new(v.outputs['Vector'],no.inputs['Vector']);bu=n.new('ShaderNodeBump');bu.inputs['Strength'].default_value=.12;bu.inputs['Distance'].default_value=.000008;l.new(no.outputs['Fac'],bu.inputs['Height']);l.new(bu.outputs['Normal'],ps.inputs['Normal'])
 if 'Anisotropic IOR Level' in ps.inputs:ps.inputs['Anisotropic IOR Level'].default_value=.25

def choose(n):
 if n.startswith('ElectricClear') or n=='ElectricCouplingShield':return clear
 if n=='LowGearboxTray':return plywood
 if 'KotoThirdBridge' in n:return maplewood
 if n.startswith('Baseplate'):return spruce
 if any(s in n for s in ['Soundbox','GuidePedestal']):return walnut
 if 'KotoSpeakingString' in n or 'KotoBackString' in n or 'NylonOverEdge' in n:return nylon
 if 'ExtendedPick' in n:return pickmat
 if 'ExtendedArm' in n:return teal
 if 'Belt' in n:return black
 if any(s in n for s in ['Pulley','NylonGuide','KotoAnchorBlock','KotoTunerBlock','NylonTieShuttle','NylonBridgeCrown']):return brass
 if 'PWMSpeedBoard' in n:return pcb
 if 'Bearing' in n:return seal
 if any(s in n for s in ['Gantry','HangingFork','ClampCap']):return aluminium
 return steel

def world(v):return ((v[0]-155)*.001,(-v[2]-55)*.001,(v[1]+157)*.001)
def local(v):return (v[0]*.001,-v[2]*.001,v[1]*.001)

import sys
sys.path.insert(0,str(R/'work'))
from unified_design import chain_layout,route_point,RELEASE_ANGLE,BASE_PERIOD,PITCH
meta=json.loads((O/'Lovophone_Unified_Design.json').read_text());data=json.loads((R/'work/unified_motion_map.json').read_text());meshes=json.loads((R/'work/unified_mesh.json').read_text());membership={};parents={}
for g in data['groups']:
 M=Matrix([g['matrix'][j:j+4] for j in range(0,16,4)]);g['inv']=M.inverted();o=bpy.data.objects.new('Motion_'+g['prefix']+'_'+g['kind'],None);scene.collection.objects.link(o);o.location=world(M.translation)
 angle=math.atan2(M[1][0],M[0][0]);o.rotation_euler=(0,-angle,0);parents[(g['prefix'],g['kind'])]=o
 for n in g['members']:membership[n]=g

def choose_new(n):
 if 'PickWheel' in n:return pickmat
 if any(k in n for k in ['SpeakingString','BackString','NylonOverEdge','TieKnot']):return nylon
 if 'SoundboxShell' in n:return walnut
 if 'SoundboxFoot' in n:return black
 if n=='Baseplate':return spruce
 if any(k in n for k in ['ThirdBridge','AnchorBlock','TunerBlock','GuidePedestal','SoundboxEnd','MountRib']):return maplewood
 if 'Bearing' in n:return seal
 if any(k in n for k in ['Hub','Clamp','AxleBlock','Saddle','NylonGuide','SlidingNut','InputKnob']):return brass
 if n.startswith('Frame') or n=='SharedIdlerRail':return aluminium
 if 'Sprocket' in n:return brass
 return steel
for m in meshes:
 n=m['name']
 if 'ChainPlates' in n or 'ChainRollers' in n:continue
 g=membership.get(n);verts=m['vertices']
 if g:verts=[local(g['inv']@Vector(v)) for v in verts]
 else:verts=[world(v) for v in verts]
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(verts,[],m['triangles']);mesh.update();o=bpy.data.objects.new(n,mesh);scene.collection.objects.link(o)
 if g:o.parent=parents[(g['prefix'],g['kind'])]
 mesh.materials.append(choose_new(n));o['FreeCAD_part']=n
 for p in mesh.polygons:p.use_smooth=True
 mesh.set_sharp_from_angle(angle=math.radians(35))
 if any(k in n for k in ['SoundboxShell','Baseplate','PickWheel']):
  mod=o.modifiers.new('Tiny presentation edge bevel','BEVEL');mod.width=.00015;mod.segments=2

def keycurve(owner,path,index,fr,values,action=None):
 if action is None:
  action=bpy.data.actions.new(owner.name+' — exact unified rotation');owner.animation_data_create();owner.animation_data.action=action
 f=action.fcurves.new(data_path=path,index=index);f.keyframe_points.add(len(fr));f.keyframe_points.foreach_set('co',np.column_stack((fr,values)).astype(np.float32).ravel())
 for p in f.keyframe_points:p.interpolation='LINEAR'
 f.extrapolation='LINEAR';f.update();owner.animation_data.action_slot=action.slots[0];return f
for r in data['rows']:
 n=r['prefix'];end=230399/24;base=2*math.pi*end/400
 for kind,factor,initial in [('Driver',1,0),('Wheel',r['ratio'],RELEASE_ANGLE),('Idler',r['driver_teeth']/12,0)]:
  if (n,kind) not in parents:continue
  keycurve(parents[(n,kind)],'rotation_euler',1,[1,230400],[-initial,-initial-base*factor])
keycurve(parents[('System','Input')],'rotation_euler',1,[1,230400],[0,-2*math.pi*(230399/24)/400])
# Self-contained moving chains: 32 interpolation poses over one link-pitch of travel.
# At the wrap, identical links exchange positions, so the visible geometry stays continuous.
def chain_geometry(row,phase,part):
 N,iy,path=chain_layout(row['driver_teeth'],row['driven_teeth']);z=row['lane_z'];pts=[route_point(path,k*PITCH+phase*PITCH) for k in range(N)];verts=[];faces=[]
 def prism(poly,z0,h):
  start=len(verts);L=len(poly)
  for zz in [z0,z0+h]:verts.extend([world((x,y,zz)) for x,y in poly])
  faces.append(tuple(start+j for j in reversed(range(L))));faces.append(tuple(start+L+j for j in range(L)))
  faces.extend([(start+j,start+(j+1)%L,start+L+(j+1)%L,start+L+j) for j in range(L)])
 for p,q in zip(pts,pts[1:]+pts[:1]):
  if part=='Rollers':
   poly=[(p[0]+1.1*math.cos(a*2*math.pi/12),p[1]+1.1*math.sin(a*2*math.pi/12)) for a in range(12)];prism(poly,z+4.7,3.2)
  else:
   dx,dy=q[0]-p[0],q[1]-p[1];D=math.hypot(dx,dy);ux,uy=dx/D,dy/D;vx,vy=-uy,ux;poly=[]
   for center,a0 in [(p,math.pi/2),(q,-math.pi/2)]:
    for j in range(9):
     a=a0+j*math.pi/8;poly.append((center[0]+1.45*(ux*math.cos(a)+vx*math.sin(a)),center[1]+1.45*(uy*math.cos(a)+vy*math.sin(a))))
   for zz in [z+3.9,z+7.9]:prism(poly,zz,.8)
 return verts,faces
for row in data['rows']:
 if row.get('direct_input'):continue
 for part in ['Plates','Rollers']:
  n=row['prefix']+'_Chain'+part;verts,faces=chain_geometry(row,0,part);me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(n,me);scene.collection.objects.link(o);me.materials.append(steel if part=='Rollers' else seal)
  o['Reference_geometry']='Chain pitch-path approximation; tooth engagement is not a manufacturing simulation.'
  o.shape_key_add(name='Basis');action=None;period_frames=400/row['driver_teeth']*24
  for j in range(1,33):
   key=o.shape_key_add(name=f'Travel {j:02d}');vs,_=chain_geometry(row,j/32,part);key.data.foreach_set('co',np.array(vs,dtype=np.float32).ravel())
   if action is None:
    keys=o.data.shape_keys;keys.animation_data_create();action=bpy.data.actions.new(n+' — one-link travel');keys.animation_data.action=action
   points=[(1,0),(1+(j-1)*period_frames/32,0),(1+j*period_frames/32,1)]
   if j<32:points.extend([(1+(j+1)*period_frames/32,0),(1+period_frames,0)])
   unique={f:v for f,v in points};fr=sorted(unique);vals=[unique[f] for f in fr]
   f=keycurve(keys,f'key_blocks["{key.name}"].value',0,fr,vals,action);f.modifiers.new('CYCLES')
 print('Moving reference chain',row['note'],flush=True)
scene['CAD_source']='Lovophone_Unified_160min.FCStd';scene['MIDI_sync']='Frame 1 = MIDI zero; 24 fps; DAW 120 BPM';scene['Full_pattern_repeat_seconds']=9600
scene['Scope']='Rigid CAD geometry with procedural studio materials. Moving chains are regenerated reference pitch-path meshes; not exact production tooth/link engagement. Pick elasticity is not simulated.'
# Neutral seamless tabletop and five large studio sources.
floor,p=material('Warm grey studio surface',(.16,.155,.145),0,.72)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.0064));bpy.context.object.name='Studio ground';bpy.context.object.data.materials.append(floor)

def aim(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def area(name,pos,power,size,color,target=(0,0,.08),size_y=None):
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.color=color;data.shape='RECTANGLE';data.size=size;data.size_y=size if size_y is None else size_y;o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=pos;aim(o,target);return o
area('Large soft key',(-.38,-.45,.66),65,.55,(1,.91,.78))
area('Cool fill',(.50,-.08,.40),28,.40,(.76,.86,1))
area('Warm rim',(.12,.40,.60),85,.55,(1,.83,.62),size_y=.22)
area('Overhead silk',(-.03,.02,.92),40,.70,(1,1,1))
area('Metal reflection strip',(-.46,.17,.32),12,.16,(.82,.90,1),size_y=.48)
camdata=bpy.data.cameras.new('Product camera');cam=bpy.data.objects.new('Product camera',camdata);scene.collection.objects.link(cam);scene.camera=cam;cam.location=(.65,-.95,.53);aim(cam,(0,-.025,.065));camdata.lens=74
focus=bpy.data.objects.new('Focus — middle string bank',None);scene.collection.objects.link(focus);focus.location=(0,-.025,.065);camdata.dof.use_dof=True;camdata.dof.focus_object=focus;camdata.dof.aperture_fstop=24

camdata.dof.use_dof=False;scene.frame_set(1);scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.cycles.samples=48
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Lovophone_Unified_Studio.blend'),compress=True)
scene.render.filepath=str(O/'Lovophone_Unified_Studio.png');bpy.ops.render.render(write_still=True)
cam.location=(1,-.025,.08);aim(cam,(0,-.025,.08));camdata.type='ORTHO';camdata.ortho_scale=.215
scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.filepath=str(O/'Lovophone_Unified_Right.png');bpy.ops.render.render(write_still=True)
print('UNIFIED_STUDIO_COMPLETE',flush=True)
