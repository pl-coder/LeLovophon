import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import os,json,numpy as np,math
os.environ['MPLCONFIGDIR']=(_LOVOPHON_WORKSPACE + '/work/mpl')
from PIL import Image,ImageDraw,ImageFont
from matplotlib.font_manager import findfont
ROOT=(_LOVOPHON_WORKSPACE + '')
meshes=json.load(open(ROOT+'/work/clockwork_mesh.json'))
BG=(246,241,231)
def font(size,serif=False):return ImageFont.truetype(findfont('DejaVu Serif' if serif else 'DejaVu Sans'),size)
def render(ms,W,H,elev,azim):
 vAll=np.concatenate([np.array(m['vertices'])[:,[0,2,1]]*np.array([1,-1,1]) for m in ms]);center=(vAll.min(0)+vAll.max(0))/2
 e,a=np.radians([elev,azim]);eye=np.array([math.cos(e)*math.cos(a),math.cos(e)*math.sin(a),math.sin(e)]);right=np.cross([0,0,1],eye);right=right/np.linalg.norm(right);up=np.cross(eye,right);rot=np.array([right,up,eye]).T
 pv=(vAll-center)@rot;span=pv.max(0)-pv.min(0);scale=min((W-35)/span[0],(H-35)/span[1]);offset=(pv.max(0)+pv.min(0))/2
 rgb=np.full((H,W,3),BG,dtype=np.uint8);depth=np.full((H,W),-np.inf,dtype=np.float32);light=np.array([-.2,-.5,.84]);light/=np.linalg.norm(light)
 for m in ms:
  v=np.array(m['vertices'])[:,[0,2,1]]*np.array([1,-1,1]);p=(v-center)@rot;p[:,:2]-=offset[:2];p[:,0]=p[:,0]*scale+W/2;p[:,1]=H/2-p[:,1]*scale
  color=np.array(m['color'])*255
  for ids in m['triangles']:
   t=p[ids];xmin=max(0,int(np.floor(t[:,0].min())));xmax=min(W-1,int(np.ceil(t[:,0].max())));ymin=max(0,int(np.floor(t[:,1].min())));ymax=min(H-1,int(np.ceil(t[:,1].max())))
   if xmax<xmin or ymax<ymin:continue
   den=(t[1,1]-t[2,1])*(t[0,0]-t[2,0])+(t[2,0]-t[1,0])*(t[0,1]-t[2,1])
   if abs(den)<1e-7:continue
   yy,xx=np.mgrid[ymin:ymax+1,xmin:xmax+1];xx=xx+.5;yy=yy+.5
   b0=((t[1,1]-t[2,1])*(xx-t[2,0])+(t[2,0]-t[1,0])*(yy-t[2,1]))/den;b1=((t[2,1]-t[0,1])*(xx-t[2,0])+(t[0,0]-t[2,0])*(yy-t[2,1]))/den;b2=1-b0-b1
   zz=b0*t[0,2]+b1*t[1,2]+b2*t[2,2];sub=depth[ymin:ymax+1,xmin:xmax+1];mask=(b0>=-1e-7)&(b1>=-1e-7)&(b2>=-1e-7)&(zz>sub)
   if not mask.any():continue
   vv=v[ids];n=np.cross(vv[1]-vv[0],vv[2]-vv[0]);norm=np.linalg.norm(n)
   shade=.55+.45*abs(np.dot(n/norm,light)) if norm>0 else .8
   sub[mask]=zz[mask];rgb[ymin:ymax+1,xmin:xmax+1][mask]=np.clip(color*shade,0,255).astype(np.uint8)
 im=Image.fromarray(rgb)
 if any(m['name']=='ClockBarrelWheel' for m in ms):
  draw=ImageDraw.Draw(im);corners=[]
  for x in [235,283]:
   for zz in [104,157]:
    for yy in [-109,-7]:
     pv=(np.array([x,zz,yy])-center)@rot;corners.append((int((pv[0]-offset[0])*scale+W/2),int(H/2-(pv[1]-offset[1])*scale)))
  for i in range(8):
   for bit in [1,2,4]:
    j=i^bit
    if j>i:draw.line([corners[i],corners[j]],fill=(125,180,186),width=1)
 return im
canvas=Image.new('RGB',(1800,1080),BG);d=ImageDraw.Draw(canvas)
d.text((65,35),'L’Harpe d’Amour',font=font(39,True),fill='#372d24');d.text((65,96),'Simple clockwork • a clear case • an antique brass-style key',font=font(20),fill='#6a6054')
canvas.paste(render(meshes,1120,700,24,-57),(10,180))
clock=[m for m in meshes if m['clock']];canvas.paste(render(clock,640,690,17,-27),(1140,185))
d=ImageDraw.Draw(canvas);d.text((65,920),'WIND  →  STORE  →  TURN  →  PLUCK',font=font(27),fill='#805d2c');d.text((65,969),'Key → contained spring → three wheels → harp axle',font=font(19),fill='#554c42');d.text((1170,890),'Inside the clear clockwork case',font=font(18),fill='#367c86');d.text((1170,945),'Educational layout study',font=font(18),fill='#554c42');d.text((1170,978),'Spring and escapement sizing pending',font=font(15),fill='#766c60');canvas.save(ROOT+'/outputs/Harpe_Clockwork_Preview.png')
k=render([m for m in meshes if m['name']=='AntiquePiercedWindingKey'],1000,680,15,-20);ImageDraw.Draw(k).text((35,20),'Antique-style removable winding key',font=font(27,True),fill='#372d24');k.save(ROOT+'/outputs/Antique_Winding_Key.png')
print('Offline shaded previews saved',flush=True)
