import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
from pathlib import Path
src=Path((_LOVOPHON_WORKSPACE + '/work/animate_twelve_offline.py')).read_text().split('W,H=1120')[0]
exec(src)
# Rendering only the non-axisymmetric pieces is exact for the circular unmarked shafts/pulleys.
active_suffixes=['_EccentricCam','_ExtendedArm','_ExtendedPick','_FollowerLever','_FollowerRoller','_RollerPin']
for m in meshes:m['moving']=any(m['name'].endswith(s) for s in active_suffixes)
lib=ctypes.CDLL(ROOT+'/work/harpe_raster_full.dylib');lib.raster.argtypes=[ctypes.c_int,P,P,ctypes.c_int,ctypes.c_int,B,P];I=ctypes.POINTER(ctypes.c_int32);lib.composite.argtypes=[ctypes.c_int,I,P,B,B,P]
W,H,VH,TOP=1120,700,620,55;fps=24;duration=480;NPHASE=960
view=View(meshes,W,VH,24,-57);voice_meshes={n:[m for m in meshes if m['moving'] and member[m['name']]['note']==n] for n in rows}
def vertices(m,t):mat=delta(m,t);return m['v']@mat[:3,:3].T+mat[:3,3]
def project(v):
 v=v[:,[0,2,1]]*[1,-1,1];p=(v-view.center)@view.rot;p[:,:2]-=view.offset[:2];p[:,0]=p[:,0]*view.scale+W/2;p[:,1]=VH/2-p[:,1]*view.scale;return p
cache={};start=time.time()
for n,r in rows.items():
 ms=voice_meshes[n];period=20/r['ratio'];samples=[]
 for j in range(24):
  for m in ms:samples.append(project(vertices(m,period*j/24))[:,:2])
 bounds=np.concatenate(samples);x0=max(0,int(bounds[:,0].min())-8);x1=min(W,int(bounds[:,0].max())+9);y0=max(0,int(bounds[:,1].min())-8);y1=min(VH,int(bounds[:,1].max())+9);cw,ch=x1-x0,y1-y0;layers=[]
 for j in range(NPHASE):
  t=period*j/NPHASE;rgb=np.zeros((ch,cw,3),np.uint8);dep=np.full((ch,cw),-np.inf,np.float32)
  for m in ms:
   v=vertices(m,t);p=project(v);p[:,0]-=x0;p[:,1]-=y0;tr=np.ascontiguousarray(p[m['tri']],np.float32);vv=v[:,[0,2,1]]*[1,-1,1];tv=vv[m['tri']];normal=np.cross(tv[:,1]-tv[:,0],tv[:,2]-tv[:,0]);norm=np.linalg.norm(normal,axis=1);norm[norm==0]=1;shade=.55+.45*np.abs((normal/norm[:,None])@light);col=np.ascontiguousarray(shade[:,None]*m['color'][None,:]*255,np.float32)
   lib.raster(len(tr),tr.ctypes.data_as(P),col.ctypes.data_as(P),cw,ch,rgb.ctypes.data_as(B),dep.ctypes.data_as(P))
  yy,xx=np.nonzero(np.isfinite(dep));idx=np.ascontiguousarray((yy+y0+TOP)*W+xx+x0,np.int32);zz=np.ascontiguousarray(dep[yy,xx],np.float32);col=np.ascontiguousarray(rgb[yy,xx],np.uint8);layers.append((idx,zz,col))
 cache[n]=layers;print('Cached voice',r.get('display_note',n),'elapsed',round(time.time()-start,1),flush=True)
base=Image.new('RGB',(W,H),BG);base.paste(Image.fromarray(view.base),(0,TOP));d=ImageDraw.Draw(base);d.text((34,14),'Le Lovophone',font=font(28),fill='#372d24');d.text((34,H-21),'Vitesse réelle · 1×',font=font(13),fill='#766c60');base=np.asarray(base).copy();depthbase=np.full((H,W),-np.inf,np.float32);depthbase[TOP:TOP+VH]=view.depth
path=OUT+'/Lovophone_8min_Normal_Speed.mp4';log=open(ROOT+'/work/lovophone_8min_encode.log','w');enc=subprocess.Popen(['/opt/homebrew/bin/ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',path],stdin=subprocess.PIPE,stderr=log)
for i in range(duration*fps):
 t=i/fps;rgb=base.copy();dep=depthbase.copy()
 for n,r in rows.items():
  j=int((t*r['ratio']/20%1)*NPHASE+.5)%NPHASE;idx,zz,col=cache[n][j];lib.composite(len(idx),idx.ctypes.data_as(I),zz.ctypes.data_as(P),col.ctypes.data_as(B),rgb.ctypes.data_as(B),dep.ctypes.data_as(P))
 im=Image.fromarray(rgb);ImageDraw.Draw(im).text((W-140,H-21),f'{int(t)//60:02d}:{int(t)%60:02d} / 08:00',font=font(13),fill='#766c60')
 if i in [0,12*fps,240*fps,(duration-1)*fps]:im.save(ROOT+f'/work/lovophone_8min_frame_{i:05d}.png')
 enc.stdin.write(im.tobytes())
 if i%(fps*60)==0:
  status={'rendered_video_seconds':t,'target_seconds':duration,'elapsed_render_seconds':round(time.time()-start,1)};json.dump(status,open(ROOT+'/work/lovophone_8min_progress.json','w'));print(status,flush=True)
enc.stdin.close();assert enc.wait()==0;json.dump({'duration_seconds':480,'fps':24,'frames':11520,'speed_multiplier':1,'input_axle_rpm':3,'complete_twelve_voice_repeat_seconds':9600,'layout':'Single full-instrument view, no motor inset.','render_phase_samples_per_voice_cycle':NPHASE,'maximum_phase_time_rounding_seconds':20/NPHASE/2,'scope':'Silent prescribed-motion illustration. No force, motor load, string vibration or sound simulation.'},open(OUT+'/Lovophone_8min_Video_Details.json','w'),indent=2);print('Eight-minute normal-speed video saved; elapsed',round(time.time()-start,1),flush=True)
