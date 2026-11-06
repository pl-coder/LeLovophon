import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,time,json,subprocess,os
from pathlib import Path
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs';D=R/'work/right_open_drive_frames';D.mkdir(exist_ok=True);s=bpy.context.scene
# More temporal samples than the speed test; retain fixed studio camera.
s.eevee.taa_render_samples=32;s.use_nodes=False;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=95
s.frame_start=1;s.frame_end=11520;s.render.fps=24
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Lovophone_Right_Open_Drive_No_Motor.blend'))
def encode(count,name):
 target=O/name;tmp=R/'work'/name
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-y','-framerate','24','-i',str(D/'%05d.jpg'),'-frames:v',str(count),'-vf','nlmeans=s=2.5:p=7:r=15,hqdn3d=1:1:2:2','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 os.replace(tmp,target)
start=time.time()
for f in range(1,11521):
 p=D/f'{f:05d}.jpg'
 if not p.exists():
  s.frame_set(f);s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
 if f==480:
  encode(480,'Lovophone_Right_Open_Drive_No_Motor_Preview.mp4')
 if f%24==0:
  (R/'work/right_open_drive_progress.json').write_text(json.dumps(dict(frame=f,total=11520,elapsed_seconds=time.time()-start,complete=False)))
encode(11520,'Lovophone_Right_Open_Drive_No_Motor_8min.mp4')
metadata=dict(duration_seconds=480,fps=24,resolution=[1008,900],frames=11520,camera='Fixed orthographic right view matching reference',hidden_motor_and_controls=True,near_drive_plate_hidden=True,engine='Blender EEVEE',samples=32,midi_offset_seconds=0,midi_tempo_bpm=120,audio='Silent; align existing pentatonic MIDI at zero',scope='Actual CAD geometry with procedural presentation materials and studio lighting; light temporal noise reduction.')
(O/'Lovophone_Right_Open_Drive_Video_Details.json').write_text(json.dumps(metadata,indent=2))
(R/'work/right_open_drive_progress.json').write_text(json.dumps(dict(frame=11520,total=11520,elapsed_seconds=time.time()-start,complete=True)))
print('FULL_FILM_COMPLETE',flush=True)
