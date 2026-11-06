import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,time,json,subprocess,os
from pathlib import Path
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs';D=R/'work/unified_preview_frames';D.mkdir(exist_ok=True);s=bpy.context.scene;s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=16;s.eevee.use_raytracing=False;s.eevee.use_fast_gi=False
for o in s.objects:
 if o.type=='LIGHT':o.data.use_shadow_jitter=False
s.render.resolution_x=1008;s.render.resolution_y=630;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=95
start=time.time()
for f in range(1,481):
 s.frame_set(f);s.render.filepath=str(D/f'{f:05d}.jpg');bpy.ops.render.render(write_still=True)
 if f%24==0:(R/'work/unified_preview_progress.json').write_text(json.dumps(dict(frame=f,total=480,elapsed_seconds=time.time()-start)))
subprocess.run(['/opt/homebrew/bin/ffmpeg','-y','-framerate','24','-i',str(D/'%05d.jpg'),'-frames:v','480','-vf','nlmeans=s=1.8:p=7:r=13,hqdn3d=1:1:2:2','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(R/'work/Lovophone_Unified_20sec.mp4')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
os.replace(R/'work/Lovophone_Unified_20sec.mp4',O/'Lovophone_Unified_20sec.mp4')
(O/'Lovophone_Unified_Preview_Details.json').write_text(json.dumps(dict(duration_seconds=20,fps=24,frames=480,resolution=[1008,630],normal_speed=True,midi_offset_seconds=0,midi_tempo_bpm=120,matching_midi='Lovophone_Unified_8min_Bitwig.mid',chain_motion='Animated smooth pitch-path reference, not validated roller/tooth contact',audio='Silent'),indent=2));print('PREVIEW_COMPLETE',flush=True)
