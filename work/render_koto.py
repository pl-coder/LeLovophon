import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import os,json,numpy as np
os.environ['MPLCONFIGDIR']=(_LOVOPHON_WORKSPACE + '/work/mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
root=(_LOVOPHON_WORKSPACE + '/outputs');meshes=json.load(open(root+'/koto_review_mesh.json'))
fig=plt.figure(figsize=(15,9),dpi=160,facecolor='#202124');ax=fig.add_subplot(111,projection='3d');ax.set_facecolor('#202124')
faces=[];colors=[]
for m in meshes:
 if m['name'].startswith('Guard'):continue
 v=np.array(m['vertices']);v=v[:,[0,2,1]];v[:,1]*=-1
 fs=v[np.array(m['triangles'])];faces.extend(fs);colors.extend([m['color']]*len(fs))
p=Poly3DCollection(np.array(faces),facecolors=colors,edgecolors=colors,linewidths=0,shade=True,lightsource=matplotlib.colors.LightSource(azdeg=315,altdeg=55));ax.add_collection3d(p)
# Fine lines mark the transparent guard's outside edges.
for x in [-30,142]:
 for y in [12,156]:ax.plot([x,x],[y,y],[-109,16],color='#8ebbc4',alpha=.35,linewidth=.7)
for z in [-109,16]:
 for x in [-30,142]:ax.plot([x,x],[12,156],[z,z],color='#8ebbc4',alpha=.35,linewidth=.7)
 for y in [12,156]:ax.plot([-30,142],[y,y],[z,z],color='#8ebbc4',alpha=.35,linewidth=.7)
ax.set_xlim(-35,345);ax.set_ylim(-50,160);ax.set_zlim(-192,24);ax.set_box_aspect((380,210,216));ax.view_init(elev=24,azim=-65);ax.set_axis_off();ax.set_proj_type('ortho');fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
fig.savefig(root+'/Harpe_koto_pendulums_preview.png',facecolor=fig.get_facecolor(),bbox_inches='tight',pad_inches=.1)
