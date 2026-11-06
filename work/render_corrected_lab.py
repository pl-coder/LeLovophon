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
# A clean CAD studio render makes the full corrected sequence practical to view now.
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.studiolight_rotate_z=.3;s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.show_specular_highlight=True;s.display.shading.background_type='WORLD';s.world.color=(.055,.065,.075);s.display.render_aa='FXAA'
# Workbench reads diffuse colors rather than Principled shader colors.
for m in bpy.data.materials:
 if m.use_nodes:
  p=m.node_tree.nodes.get('Principled BSDF')
  if p:m.diffuse_color=p.inputs['Base Color'].default_value
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0
s.render.resolution_x=1008;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=11520;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=92
cam=s.camera;cam.data.type='PERSP';cam.data.dof.use_dof=False;cam.location=(.60,-.85,.46);cam.rotation_euler=(Vector((0,0,.09))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=70
s['Full_mechanical_repeat_seconds']=480;s['Timing']='Corrected pentatonic pitch=cam ratios.3 rpm input. Not synchronized to older MIDI.';s['Geometry_scope']='Lab Frame ratio-review visualization; obsolete tray and colliding right feet hidden. This is not the separate four-bar physical prototype or production clearance approval.'
s.frame_set(1);initial={o.name:o.matrix_world.copy() for o in s.objects if o.name.startswith('Motion_') and any(o.name.startswith('Motion_'+r['note']+'_') for r in rows)};s.frame_set(11521)
error=max(max(abs(float(a-b)) for ra,rb in zip(initial[n],bpy.data.objects[n].matrix_world) for a,b in zip(ra,rb)) for n in initial)
assert error<.0002,error
(O/'Lovophone_Lab_Frame_Corrected_Video_Check.json').write_text(json.dumps(dict(voices=12,repeat_seconds=480,frame_count=11520,fps=24,end_matrix_error=error,normal_speed=True,physical_validation=False),indent=2))
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(O/'Lovophone_Lab_Frame_Corrected_Animation.blend'),compress=True)
start=time.time()
for f in range(1,5761):
 s.frame_set(2*f-1);s.render.filepath=str(D/f'{f:05d}.jpg');bpy.ops.render.render(write_still=True)
 if f==1:
  import shutil;shutil.copyfile(D/'00001.jpg',O/'Lovophone_Lab_Frame_Corrected.jpg')
 if f%24==0:
  (R/'work/lab_corrected_video_progress.json').write_text(json.dumps(dict(frame=f,total=5760,elapsed=time.time()-start)))
 if f==5:print('FIVE_FRAME_SECONDS',time.time()-start,flush=True)
 if f==120:
  subprocess.run(['/opt/homebrew/bin/ffmpeg','-y','-framerate','12','-i',str(D/'%05d.jpg'),'-frames:v','240','-vf','fps=24','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(O/'Lovophone_Lab_Frame_Corrected_10sec.mp4')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
subprocess.run(['/opt/homebrew/bin/ffmpeg','-y','-framerate','12','-i',str(D/'%05d.jpg'),'-frames:v','11520','-vf','fps=24','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(O/'Lovophone_Lab_Frame_Corrected_8min.mp4')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print('CORRECTED_VIDEO_COMPLETE',flush=True)
