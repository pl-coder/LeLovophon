import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import os,json,numpy as np
os.environ['MPLCONFIGDIR']=(_LOVOPHON_WORKSPACE + '/work/mpl')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import LightSource
ROOT=(_LOVOPHON_WORKSPACE + '');meshes=json.load(open(ROOT+'/work/clockwork_mesh.json'))
def paint(ax,subset,bounds,elev=23,azim=-57):
 faces=[];cols=[]
 for m in subset:
  v=np.array(m['vertices'])[:,[0,2,1]];v[:,1]*=-1;fs=v[np.array(m['triangles'])];faces.extend(fs);cols.extend([m['color']]*len(fs))
 p=Poly3DCollection(np.array(faces),facecolors=cols,edgecolors=cols,linewidths=0,shade=True,lightsource=LightSource(azdeg=320,altdeg=50));ax.add_collection3d(p)
 ax.set_xlim(*bounds[0]);ax.set_ylim(*bounds[1]);ax.set_zlim(*bounds[2]);ax.set_box_aspect([b[1]-b[0] for b in bounds]);ax.set_proj_type('ortho');ax.view_init(elev=elev,azim=azim);ax.set_axis_off();ax.set_facecolor('#f6f1e7')
def case_edges(ax):
 for x in [235,283]:
  for z in [104,157]:ax.plot([x,x],[z,z],[-109,-7],color='#3b9ca7',alpha=.6,lw=.8)
 for y in [-109,-7]:
  for x in [235,283]:ax.plot([x,x],[104,157],[y,y],color='#3b9ca7',alpha=.6,lw=.8)
  for z in [104,157]:ax.plot([235,283],[z,z],[y,y],color='#3b9ca7',alpha=.6,lw=.8)
fig=plt.figure(figsize=(15,8.5),dpi=150,facecolor='#f6f1e7')
fig.text(.05,.94,"L’Harpe d’Amour",fontsize=27,fontfamily='serif',color='#372d24');fig.text(.05,.89,'See-through clockwork • a winding key with two open butterfly bows',fontsize=12,color='#6a6054')
a=fig.add_axes([.01,.13,.63,.72],projection='3d');paint(a,meshes,[(-45,360),(-48,160),(-166,20)]);case_edges(a)
b=fig.add_axes([.59,.24,.4,.57],projection='3d');paint(b,[m for m in meshes if m['clock']],[(228,310),(100,160),(-112,-2)],elev=17,azim=-27);case_edges(b)
fig.text(.66,.20,'CLEAR CLOCKWORK MODULE',fontsize=11,color='#367c86',weight='bold')
fig.text(.05,.10,'WIND  →  STORE  →  TURN  →  PLUCK',fontsize=16,color='#805d2c',weight='bold')
fig.text(.05,.055,'Key     •     contained spring     •     three visible wheels     •     existing harp axle',fontsize=11,color='#554c42')
fig.text(.66,.10,'Balance escapement: the proposed “tick”.',fontsize=10,color='#554c42')
fig.text(.66,.055,'Educational CAD concept — spring and escapement sizing pending.',fontsize=9,color='#766c60')
fig.savefig(ROOT+'/outputs/Harpe_Clockwork_Preview.png',facecolor=fig.get_facecolor())
# Dedicated key close-up.
fig=plt.figure(figsize=(7,5),dpi=170,facecolor='#f6f1e7');a=fig.add_subplot(111,projection='3d');paint(a,[m for m in meshes if m['name']=='AntiquePiercedWindingKey'],[(283,308),(102,160),(-50,-20)],elev=15,azim=-20);fig.suptitle('Removable antique-style brass winding key',fontfamily='serif',fontsize=15,color='#372d24');fig.savefig(ROOT+'/outputs/Antique_Winding_Key.png',facecolor=fig.get_facecolor(),bbox_inches='tight')
