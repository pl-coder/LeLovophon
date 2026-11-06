import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,time,json,subprocess,os,shutil
from pathlib import Path
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs';D=R/'work/lab_corrected_final_frames';D.mkdir(exist_ok=True);s=bpy.context.scene
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=94
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(O/'Lovophone_Lab_Frame_Corrected_Animation.blend'),compress=True)
start=time.time()
def encode(count,target):
 tmp=R/'work'/target
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-y','-framerate','12','-i',str(D/'%05d.jpg'),'-frames:v',str(count*2),'-vf','fps=24','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);os.replace(tmp,O/target)
for f in range(1,5761):
 s.frame_set(2*f-1);s.render.filepath=str(D/f'{f:05d}.jpg');bpy.ops.render.render(write_still=True)
 if f==1:shutil.copyfile(D/'00001.jpg',O/'Lovophone_Lab_Frame_Corrected.jpg')
 if f%120==0:(R/'work/lab_corrected_video_progress.json').write_text(json.dumps(dict(frame=f,total=5760,elapsed=time.time()-start)))
 if f==120:encode(120,'Lovophone_Lab_Frame_Corrected_10sec.mp4')
encode(5760,'Lovophone_Lab_Frame_Corrected_8min.mp4')
metadata=dict(duration_seconds=480,fps=24,unique_motion_samples_per_second=12,resolution=[1008,720],normal_speed=True,ratios=['1','9/8','5/4','3/2','5/3','2','9/4','5/2','3','10/3','4','9/2'],input_rpm=3,audio='Silent',old_midi_compatible=False,scope='Corrected timing visualization of Lab Frame ratio review. Obsolete tray/right-foot hardware hidden. Four-bar test prototype not installed. Not physical validation.')
(O/'Lovophone_Lab_Frame_Corrected_Video_Details.json').write_text(json.dumps(metadata,indent=2));print('CORRECTED_VIDEO_COMPLETE',flush=True)
