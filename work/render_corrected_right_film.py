import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,time,json,subprocess,os
from pathlib import Path
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs';D=R/'work/corrected_right_rgba_frames';D.mkdir(exist_ok=True);s=bpy.context.scene
s.use_nodes=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.image_settings.compression=10;s.render.film_transparent=True
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(O/'Lovophone_Corrected_Right_Transparent.blend'),compress=True)
start=time.time()
def encode(count,stem):
 # Denoise RGB lightly, carry the rendered alpha untouched through the filter graph.
 alpha=O/(stem+'_Alpha.mov');blue=O/(stem+'_Blue.mp4')
 filters='[0:v]split[c][a];[a]alphaextract[alpha];[c]format=yuv444p,hqdn3d=3:3:4:4[rgb];[rgb][alpha]alphamerge,fps=24[out]'
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-y','-framerate','12','-i',str(D/'%05d.png'),'-filter_complex',filters,'-map','[out]','-frames:v',str(count*2),'-c:v','prores_ks','-profile:v','4','-pix_fmt','yuva444p10le','-alpha_bits','16','-vendor','apl0',str(alpha)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-y','-f','lavfi','-i','color=c=0x0000FF:s=1008x900:r=24','-i',str(alpha),'-filter_complex','[0:v][1:v]overlay=shortest=1:format=auto,format=yuv420p[out]','-map','[out]','-frames:v',str(count*2),'-c:v','libx264','-preset','fast','-crf','17','-movflags','+faststart',str(blue)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
for f in range(1,5761):
 p=D/f'{f:05d}.png'
 if not p.exists():
  s.frame_set(2*f-1);s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
 if f%24==0:(R/'work/corrected_right_render_progress.json').write_text(json.dumps(dict(frame=f,total=5760,elapsed_seconds=time.time()-start,complete=False)))
 if f==120:
  encode(120,'Lovophone_Corrected_Right_Preview_10sec');print('PREVIEW_READY',flush=True)
encode(5760,'Lovophone_Corrected_Right_8min')
meta=dict(duration_seconds=480,encoded_fps=24,motion_samples_per_second=12,frames=11520,resolution=[1008,900],camera='Orthographic RIGHT (+CAD X), matching reference screenshot',normal_speed=True,input_rpm=3,ratios=['1','9/8','5/4','3/2','5/3','2','9/4','5/2','3','10/3','4','9/2'],audio='Silent',alpha_master='ProRes4444 alpha MOV; use alpha directly, no key required',key_copy='H264 blue background MP4, RGB blue composited after render to avoid key-colour spill',render_engine='EEVEE16 samples, procedural timber/metal materials and studio lighting',scope='Corrected Lab Frame timing visualization. Motor, obsolete tray and foreground/right-foot hardware hidden for presentation; not the separate four-bar physical prototype. Old MIDI does not sync.')
(O/'Lovophone_Corrected_Right_Render_Details.json').write_text(json.dumps(meta,indent=2));(R/'work/corrected_right_render_progress.json').write_text(json.dumps(dict(frame=5760,total=5760,complete=True,elapsed_seconds=time.time()-start)));print('RIGHT_ALPHA_FILM_COMPLETE',flush=True)
