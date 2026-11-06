import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
from pathlib import Path
R=Path((_LOVOPHON_WORKSPACE + ''))
s=(R/'work/animate_twelve_offline.py').read_text().split('W,H=1120,700;fps=24;seconds=12')[0]
s=s.replace('work/twelve_motion_map.json','work/pentatonic_motion_map.json').replace('work/twelve_mesh.json','work/pentatonic_mesh.json')
exec(compile(s,'renderer','exec'))
W,H=1400,880;fps=24;seconds=20
view=View(meshes,W,710,24,-57)
log=open(ROOT+'/work/pentatonic_video_encode.log','w')
enc=subprocess.Popen(['/opt/homebrew/bin/ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',OUT+'/Lovophone_Pentatonic_Motion.mp4'],stdin=subprocess.PIPE,stderr=log)
start=time.time()
for i in range(seconds*fps):
 t=i/fps;im=Image.new('RGB',(W,H),BG);im.paste(view.frame(t),(0,95));d=ImageDraw.Draw(im)
 d.text((38,20),'Le Lovophone — pentatonic',font=font(34),fill='#372d24')
 d.text((38,63),'C · D · E · G · A   |   twelve nylon strings   |   normal speed',font=font(19),fill='#6a6054')
 d.text((38,829),'Proportional bridges and arms · original rhythm retained · silent motion preview',font=font(18),fill='#766c60')
 d.text((1250,829),f'{t:04.1f} s',font=font(18),fill='#367c86')
 if i==0:im.save(OUT+'/Lovophone_Pentatonic_Preview.png')
 if i in [120,240]:im.save(ROOT+f'/work/pentatonic_frame_{i:03d}.png')
 enc.stdin.write(im.tobytes())
 if i%120==0:print('Rendered',i,'/',seconds*fps,'frames;',round(time.time()-start,1),'s',flush=True)
enc.stdin.close();assert enc.wait()==0
print('Pentatonic motion preview saved.',flush=True)
