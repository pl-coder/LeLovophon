import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import os,json,math,ctypes,subprocess,time
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=(_LOVOPHON_WORKSPACE + '');OUT=ROOT+'/outputs';data=json.load(open(ROOT+'/work/twelve_motion_map.json'));rows={r['note']:r for r in data['rows']};meshes=json.load(open(ROOT+'/work/twelve_mesh.json'))
lib=ctypes.CDLL(ROOT+'/work/harpe_raster.dylib');P=ctypes.POINTER(ctypes.c_float);B=ctypes.POINTER(ctypes.c_uint8);lib.raster.argtypes=[ctypes.c_int,P,P,ctypes.c_int,ctypes.c_int,B,P]
fontpath='/System/Library/Fonts/Supplemental/Arial.ttf'
def font(sz):return ImageFont.truetype(fontpath,sz)
def pose(y,z,ang,s=0):
 a=math.radians(ang);c=math.cos(a);sn=math.sin(a);m=np.eye(4);m[:3,:3]=[[1,0,0],[0,c,-sn],[0,sn,c]];m[:3,3]=[s,y,z];return m
def beta(r,theta):
 U=np.array([r['follower_y'],r['follower_z']]);C=np.array([-59-4*math.sin(theta),-116+4*math.cos(theta)]);v=C-U;d=np.linalg.norm(v);v=v/d;a=(r['lever_length']**2-225+d*d)/(2*d);h=math.sqrt(max(0,r['lever_length']**2-a*a));p=U+v*a;perp=np.array([-v[1],v[0]]);b1=p+perp*h;b2=p-perp*h;b=b1 if b1[0]>b2[0] else b2;return math.atan2(-(b[0]-U[0]),b[1]-U[1])
member={}
for g in data['groups']:
 g['inv']=np.linalg.inv(np.array(g['matrix']).reshape(4,4))
 for name in g['members']:member[name]=g
clockspin={'ElectricShaftCoupling':(-83,-131,-18),'N20OutputShaft':(-83,-131,-18)}
for m in meshes:
 m['v']=np.array(m['vertices'],dtype=float);m['tri']=np.array(m['triangles'],dtype=np.int32);m['color']=np.array(m['color']);m['moving']=m['name'] in member or m['name'] in clockspin or m['name'] in ['ClockBalanceWheel','ClockEscapementLever']
def delta(m,t):
 name=m['name']
 if name in member:
  g=member[name];r=rows[g['note']];k=g['kind'];th=-math.radians(18*t*r['ratio']);b=beta(r,th);da=math.atan2(math.sin(b-r['beta_mid']),math.cos(b-r['beta_mid']))
  if k=='Driver':p=pose(-83,-131,-18*t,r['station'])
  elif k=='Output':p=pose(-59,-116,math.degrees(th),r['station'])
  elif k=='Rocker':p=pose(r['follower_y'],r['follower_z'],math.degrees(b),r['station'])
  else:p=pose(r['pivot_y'],r['pivot_z'],90+4*math.degrees(da),r['station'])
  return p@g['inv']
 if name in clockspin:
  y,z,w=clockspin[name];return pose(y,z,w*t)@np.linalg.inv(pose(y,z,0))
 if name=='ClockBalanceWheel':return pose(-52,-119,24*math.sin(2*math.pi*t))@np.linalg.inv(pose(-52,-119,0))
 if name=='ClockEscapementLever':return pose(-66,-129,3*math.sin(2*math.pi*t))@np.linalg.inv(pose(-66,-129,0))
 return np.eye(4)
light=np.array([-.2,-.5,.84]);light/=np.linalg.norm(light);BG=(246,241,231)
class View:
 def __init__(self,ms,W,H,elev,azim):
  self.ms=ms;self.W=W;self.H=H;v=np.concatenate([m['v'][:,[0,2,1]]*[1,-1,1] for m in ms]);self.center=(v.max(0)+v.min(0))/2;e,a=np.radians([elev,azim]);eye=np.array([math.cos(e)*math.cos(a),math.cos(e)*math.sin(a),math.sin(e)]);right=np.cross([0,0,1],eye);right/=np.linalg.norm(right);up=np.cross(eye,right);self.rot=np.array([right,up,eye]).T;p=(v-self.center)@self.rot;span=p.max(0)-p.min(0);self.scale=min((W-45)/span[0],(H-45)/span[1]);self.offset=(p.max(0)+p.min(0))/2
  self.base=np.full((H,W,3),BG,np.uint8);self.depth=np.full((H,W),-np.inf,np.float32)
  for m in ms:
   if not m['moving']:self.draw(m,m['v'],self.base,self.depth)
 def draw(self,m,v,rgb,dep):
  v=v[:,[0,2,1]]*[1,-1,1];p=(v-self.center)@self.rot;p[:,:2]-=self.offset[:2];p[:,0]=p[:,0]*self.scale+self.W/2;p[:,1]=self.H/2-p[:,1]*self.scale;t=np.ascontiguousarray(p[m['tri']],np.float32)
  tv=v[m['tri']];n=np.cross(tv[:,1]-tv[:,0],tv[:,2]-tv[:,0]);norm=np.linalg.norm(n,axis=1);norm[norm==0]=1;shade=.55+.45*np.abs((n/norm[:,None])@light);cols=np.ascontiguousarray(shade[:,None]*m['color'][None,:]*255,np.float32)
  lib.raster(len(t),t.ctypes.data_as(P),cols.ctypes.data_as(P),self.W,self.H,rgb.ctypes.data_as(B),dep.ctypes.data_as(P))
 def frame(self,t):
  rgb=self.base.copy();dep=self.depth.copy()
  for m in self.ms:
   if m['moving']:
    mat=delta(m,t);v=m['v']@mat[:3,:3].T+mat[:3,3];self.draw(m,v,rgb,dep)
  im=Image.fromarray(rgb);d=ImageDraw.Draw(im);corn=[]
  for x in [235,283]:
   for zz in [104,157]:
    for yy in [-109,-7]:
     p=(np.array([x,zz,yy])-self.center)@self.rot;corn.append((int((p[0]-self.offset[0])*self.scale+self.W/2),int(self.H/2-(p[1]-self.offset[1])*self.scale)))
  for i in range(0):
   for bit in [1,2,4]:
    j=i^bit
    if j>i:d.line([corn[i],corn[j]],fill=(125,180,186),width=1)
  return im
W,H=1120,700;fps=24;seconds=12
main=View(meshes,720,500,24,-57);detail=View([m for m in meshes if m.get('motor')],390,500,17,-27)
log=open(ROOT+'/work/twelve_video_encode.log','w');enc=subprocess.Popen(['/opt/homebrew/bin/ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',OUT+'/Harpe_Twelve_Electric_Rolling.mp4'],stdin=subprocess.PIPE,stderr=log)
start=time.time();firstangles=None;maxchange=0
for i in range(seconds*fps):
 t=4*i/fps;canvas=Image.new('RGB',(W,H),BG);canvas.paste(main.frame(t),(0,100));canvas.paste(detail.frame(t),(725,100));d=ImageDraw.Draw(canvas);d.text((35,24),'L’Harpe d’Amour — twelve electric voices',font=font(29),fill='#372d24');d.text((35,65),'4× motion preview • shared gantry • variable-speed motor layout',font=font(16),fill='#6a6054');d.text((35,613),'MOTOR → BELTS → TWELVE VOICES',font=font(22),fill='#805d2c');d.text((35,657),'Prescribed motion; motor torque, string vibration and sound are not simulated.',font=font(15),fill='#766c60');d.text((772,613),f'Model time: {t:04.1f} s',font=font(17),fill='#367c86')
 if i in [0,48,144]:canvas.save(ROOT+f'/work/twelve_frame_{i:03d}.png')
 enc.stdin.write(canvas.tobytes())
 if i%48==0:print('Rendered frame',i,'of',seconds*fps,'elapsed',round(time.time()-start,1),flush=True)
enc.stdin.close();rc=enc.wait();assert rc==0,rc;print('Video saved',round(time.time()-start,1),'seconds',flush=True)
json.dump({'duration_seconds':seconds,'fps':fps,'frames':seconds*fps,'model_speed_multiplier':4,'input_axle_degrees_per_model_second':-18,'scope':'Kinematic illustration, not a motor-load, string-vibration or sound simulation.'},open(OUT+'/twelve_animation_info.json','w'),indent=2)
