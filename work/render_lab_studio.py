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
scene.render.fps=24;scene.frame_start=1;scene.frame_end=11520
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
 if n.startswith(('LabRailClamp','LabBaseClamp')):return brass
 if n.startswith('LabRearFootPad'):return black
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
data=json.loads((R/'work/lab_frame_motion_map.json').read_text());meshes=json.loads((R/'work/lab_frame_mesh.json').read_text());rows={r['note']:r for r in data['rows']};membership={};parents={}
for g in data['groups']:
 M=Matrix([g['matrix'][j:j+4] for j in range(0,16,4)]);g['inv']=M.inverted();empty=bpy.data.objects.new('Motion_'+g['note']+'_'+g['kind'],None);scene.collection.objects.link(empty);empty.location=world(M.translation);empty.rotation_euler=(math.atan2(M[2][1],M[1][1]),0,0);empty.empty_display_size=.008;parents[(g['note'],g['kind'])]=empty
 for n in g['members']:membership[n]=g
for m in meshes:
 n=m['name'];verts=m['vertices'];g=membership.get(n)
 if g:verts=[local(g['inv']@Vector(v)) for v in verts]
 else:verts=[world(v) for v in verts]
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(verts,[],m['triangles']);mesh.update();obj=bpy.data.objects.new(n,mesh);scene.collection.objects.link(obj);obj['FreeCAD_part']=n
 if g:obj.parent=parents[(g['note'],g['kind'])]
 mat=choose(n);mesh.materials.append(mat)
 for p in mesh.polygons:p.use_smooth=True
 mesh.set_sharp_from_angle(angle=math.radians(35))
 if any(s in n for s in ['Soundbox','Baseplate','ThirdBridge','DriveFrameLeftCheek','DriveFrameRightCheek','Angle','ExtendedArm']):
  mod=obj.modifiers.new('Small edge highlights','BEVEL');mod.width=.00018 if mat not in [walnut,spruce,maplewood] else .0003;mod.segments=2;mod.limit_method='ANGLE';mod.angle_limit=math.radians(35)
  mod=obj.modifiers.new('Planar face normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=50
print('CAD objects imported:',len(meshes),'elapsed',round(time.time()-start,1),flush=True)
# Bake the exact approved motion. Frame 1 corresponds to MIDI time zero at 120 BPM.
frames=np.arange(1,11521,dtype=np.float32);times=(frames-1)/24

def keycurve(o,fr,values):
 action=bpy.data.actions.new(o.name+' — approved motion');o.animation_data_create();o.animation_data.action=action
 f=action.fcurves.new(data_path='rotation_euler',index=0);f.keyframe_points.add(len(fr));f.keyframe_points.foreach_set('co',np.column_stack((fr,values)).astype(np.float32).ravel())
 for p in f.keyframe_points:p.interpolation='LINEAR'
 f.update()
 o.animation_data.action_slot=action.slots[0]
for n,r in rows.items():
 th=-np.radians(18*times*r['ratio']);fy,fz=r['follower_y'],r['follower_z'];vy=-59-4*np.sin(th)-fy;vz=-116+4*np.cos(th)-fz;dist=np.hypot(vy,vz);vy/=dist;vz/=dist;a=(r['lever_length']**2-225+dist*dist)/(2*dist);h=np.sqrt(np.maximum(0,r['lever_length']**2-a*a));py=fy+vy*a;pz=fz+vz*a;b1y=py-vz*h;b2y=py+vz*h;take=b1y>b2y;by=np.where(take,b1y,b2y);bz=np.where(take,pz+vy*h,pz-vy*h);beta=np.arctan2(-(by-fy),bz-fz);da=np.arctan2(np.sin(beta-r['beta_mid']),np.cos(beta-r['beta_mid']))
 keycurve(parents[(n,'Driver')],np.array([1,11520]),np.radians(-18*np.array([0,11519/24])))
 keycurve(parents[(n,'Output')],np.array([1,11520]),np.radians(-18*np.array([0,11519/24])*r['ratio']))
 keycurve(parents[(n,'Rocker')],frames,beta);keycurve(parents[(n,'LongArmRotor')],frames,np.pi/2+4*da)
# The motor shaft/coupling can be rotated independently about their shared X axis.
for name in ['N20OutputShaft','ElectricShaftCoupling']:
 obj=bpy.data.objects.get(name)
 if obj:
  center=world((0,-83,-131));empty=bpy.data.objects.new('Motion_'+name,None);scene.collection.objects.link(empty);empty.location=center
  # Rebase world-space vertices to the shaft axis before assigning the moving parent.
  for vert in obj.data.vertices:vert.co-=Vector(center)
  obj.parent=empty;obj.matrix_parent_inverse=Matrix.Identity(4);keycurve(empty,np.array([1,11520]),np.radians(-18*np.array([0,11519/24])))
print('Eight-minute exact motion baked.',round(time.time()-start,1),flush=True)
# Neutral seamless tabletop and five large studio sources.
floor,p=material('Warm grey studio surface',(.16,.155,.145),0,.72)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.0004));bpy.context.object.name='Studio ground';bpy.context.object.data.materials.append(floor)

def aim(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def area(name,pos,power,size,color,target=(0,0,.08),size_y=None):
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.color=color;data.shape='RECTANGLE';data.size=size;data.size_y=size if size_y is None else size_y;o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=pos;aim(o,target);return o
area('Large soft key',(-.38,-.45,.66),65,.55,(1,.91,.78))
area('Cool fill',(.50,-.08,.40),28,.40,(.76,.86,1))
area('Warm rim',(.12,.40,.60),85,.55,(1,.83,.62),size_y=.22)
area('Overhead silk',(-.03,.02,.92),40,.70,(1,1,1))
area('Metal reflection strip',(-.46,.17,.32),12,.16,(.82,.90,1),size_y=.48)
camdata=bpy.data.cameras.new('Product camera');cam=bpy.data.objects.new('Product camera',camdata);scene.collection.objects.link(cam);scene.camera=cam;cam.location=(.62,-.91,.52);aim(cam,(0,0,.095));camdata.lens=75
focus=bpy.data.objects.new('Focus — middle string bank',None);scene.collection.objects.link(focus);focus.location=(0,0,.095);camdata.dof.use_dof=True;camdata.dof.focus_object=focus;camdata.dof.aperture_fstop=24
scene['CAD_source']='Lovophone_Lab_Frame.FCStd';scene['MIDI_sync']='Frame 1 = MIDI 0:00; 24 fps, MIDI project 120 BPM';scene['Animation_duration_seconds']=480;scene['Full_mechanical_repeat_seconds']=9600
scene['Materials_scope']='Procedural presentation materials on exact exported CAD meshes. Cosmetic small bevels are render-only; engineering CAD is unchanged.'
scene.frame_set(1)
text=bpy.data.texts.new('ABOUT THE LOVOPHONE SCENE');text.write('Source: Lovophone_Lab_Frame.FCStd. Exact approved pentatonic geometry and retained twelve-voice timing. Frame 1 is MIDI time zero; project tempo 120 BPM. 24 fps, 11520 frames, eight minutes. All grain and brushed surface textures are procedural and self-contained. Camera, five area lights and materials are editable. Tiny render-only edge bevels do not alter the CAD deliverable. Part names match native CAD objects.\n')

for o in scene.objects:
 if o.name.startswith(('N20','Electric','PWM','Speed')):o.hide_render=True
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.cycles.samples=48
camdata.dof.use_dof=False
cam.location=(.58,-.83,.52);aim(cam,(0,0,.09));camdata.lens=70
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Lovophone_Lab_Frame_Studio.blend'),compress=True)
scene.render.filepath=str(O/'Lovophone_Lab_Frame_Studio.png');bpy.ops.render.render(write_still=True)
cam.location=(1,0,.099);aim(cam,(0,0,.099));camdata.type='ORTHO';camdata.ortho_scale=.245
scene.render.resolution_x=1120;scene.render.resolution_y=1000;scene.render.filepath=str(O/'Lovophone_Lab_Frame_Right.png');bpy.ops.render.render(write_still=True)
