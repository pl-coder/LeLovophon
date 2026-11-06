import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,numpy as np,math,json,time,subprocess,os
from pathlib import Path
from mathutils import Vector,Matrix
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs';D=R/'work/lab_corrected_quick_frames';D.mkdir(exist_ok=True)
s=bpy.context.scene;rows=json.loads((R/'work/lab_corrected_render_rows.json').read_text());data=json.loads((R/'work/lab_frame_motion_map.json').read_text());membership={}
for g in data['groups']:
 g['inv']=Matrix([g['matrix'][j:j+4] for j in range(0,16,4)]).inverted()
 for n in g['members']:membership[n]=g
for m in json.loads((R/'work/lab_corrected_render_mesh.json').read_text()):
 obj=bpy.data.objects[m['name']];g=membership.get(obj.name)
 verts=[(v[0]*.001,-v[2]*.001,v[1]*.001) for v in [g['inv']@Vector(v) for v in m['vertices']]] if g else [((v[0]-155)*.001,(-v[2]-55)*.001,(v[1]+157)*.001) for v in m['vertices']]
 mesh=bpy.data.meshes.new(obj.name+'_corrected');mesh.from_pydata(verts,[],m['triangles']);mesh.update()
 for mat in obj.data.materials:mesh.materials.append(mat)
 obj.data=mesh
fr=np.arange(1,11522,dtype=np.float64);ts=(fr-1)/24
# All curves include the exact480-second endpoint for closure testing.
def keys(obj,values):
 obj.animation_data_clear();a=bpy.data.actions.new(obj.name+'_matched_ratios');obj.animation_data_create();obj.animation_data.action=a;f=a.fcurves.new(data_path='rotation_euler',index=0);f.keyframe_points.add(len(fr));f.keyframe_points.foreach_set('co',np.column_stack((fr,values)).astype(np.float32).ravel())
 for k in f.keyframe_points:k.interpolation='LINEAR'
 f.extrapolation='LINEAR';f.update();obj.animation_data.action_slot=a.slots[0]
for r in rows:
 n=r['note'];th=-np.radians(18*ts*r['ratio']);fy,fz=r['follower_y'],r['follower_z'];vy=-59-4*np.sin(th)-fy;vz=-116+4*np.cos(th)-fz;dist=np.hypot(vy,vz);vy/=dist;vz/=dist;a=(r['lever_length']**2-225+dist*dist)/(2*dist);h=np.sqrt(np.maximum(0,r['lever_length']**2-a*a));py=fy+vy*a;pz=fz+vz*a;b1y=py-vz*h;b2y=py+vz*h;take=b1y>b2y;by=np.where(take,b1y,b2y);bz=np.where(take,pz+vy*h,pz-vy*h);beta=np.arctan2(-(by-fy),bz-fz);delta=np.arctan2(np.sin(beta-r['beta_mid']),np.cos(beta-r['beta_mid']))
 for kind,val in [('Driver',np.radians(-18*ts)),('Output',th),('Rocker',beta),('LongArmRotor',math.pi/2+4*delta)]:keys(bpy.data.objects['Motion_'+n+'_'+kind],val)
for o in s.objects:
 if o.name.startswith(('N20','Electric','PWM','Speed','Motion_N20','Motion_Electric')):o.hide_render=True
 if o.name in ['DriveFrameRightDeckBolt0','DriveFrameRightDeckWasher0','DriveFrameRightAngle0','DriveFrameRightAngle1','LowGearboxTray']:o.hide_render=True

# Match orthographic right view, retaining procedural materials and studio lights.
s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=16;s.eevee.use_raytracing=False;s.eevee.use_fast_gi=False
for o in s.objects:
 if o.type=='LIGHT':o.data.use_shadow_jitter=False
 if o.name in ['Studio ground','DriveFrameRightCheek'] or o.name.startswith(('DriveFrameRightCheekBolt','DriveFrameRightCheekWasher','DriveFrameRightCheekNut','DriveFrameRightInputRetainer')):o.hide_render=True
s.render.film_transparent=True;s.use_nodes=False
cam=s.camera;cam.location=(1,0,.099);cam.rotation_euler=(Vector((0,0,.099))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.238;cam.data.dof.use_dof=False
s.render.resolution_x=1008;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.image_settings.compression=15;s.frame_start=1;s.frame_end=11520;s.render.fps=24
s['Full_mechanical_repeat_seconds']=480;s['Rendering_scope']='Textured right view of corrected Lab Frame ratio review; motor, obsolete tray and foreground drive plate hidden. Separate four-bar prototype not installed.'
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(O/'Lovophone_Corrected_Right_Transparent.blend'),compress=True)
for f in [1,49,97]:
 s.frame_set(f);s.render.filepath=str(R/'work'/('corrected_right_alpha_'+str(f)+'.png'));t=time.time();bpy.ops.render.render(write_still=True);print('FRAME_SECONDS',f,time.time()-t,flush=True)
