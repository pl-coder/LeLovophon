import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
from pathlib import Path
R=Path((_LOVOPHON_WORKSPACE + ''))
s=(R/'work/build_lovophone_studio.py').read_text();prefix=s[:s.index("data=json.loads")]
prefix=prefix.replace("scene.frame_end=11520","scene.frame_end=230400")
body=r'''
import sys
sys.path.insert(0,str(R/'work'))
from unified_design import chain_layout,route_point,RELEASE_ANGLE,BASE_PERIOD,PITCH
meta=json.loads((O/'Lovophone_Unified_Design.json').read_text());data=json.loads((R/'work/unified_motion_map.json').read_text());meshes=json.loads((R/'work/unified_mesh.json').read_text());membership={};parents={}
for g in data['groups']:
 M=Matrix([g['matrix'][j:j+4] for j in range(0,16,4)]);g['inv']=M.inverted();o=bpy.data.objects.new('Motion_'+g['prefix']+'_'+g['kind'],None);scene.collection.objects.link(o);o.location=world(M.translation)
 angle=math.atan2(M[1][0],M[0][0]);o.rotation_euler=(0,-angle,0);parents[(g['prefix'],g['kind'])]=o
 for n in g['members']:membership[n]=g

def choose_new(n):
 if 'PickWheel' in n:return pickmat
 if any(k in n for k in ['SpeakingString','BackString','NylonOverEdge','TieKnot']):return nylon
 if 'SoundboxShell' in n:return walnut
 if 'SoundboxFoot' in n:return black
 if n=='Baseplate':return spruce
 if any(k in n for k in ['ThirdBridge','AnchorBlock','TunerBlock','GuidePedestal','SoundboxEnd','MountRib']):return maplewood
 if 'Bearing' in n:return seal
 if any(k in n for k in ['Hub','Clamp','AxleBlock','Saddle','NylonGuide','SlidingNut','InputKnob']):return brass
 if n.startswith('Frame') or n=='SharedIdlerRail':return aluminium
 if 'Sprocket' in n:return brass
 return steel
for m in meshes:
 n=m['name']
 if 'ChainPlates' in n or 'ChainRollers' in n:continue
 g=membership.get(n);verts=m['vertices']
 if g:verts=[local(g['inv']@Vector(v)) for v in verts]
 else:verts=[world(v) for v in verts]
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(verts,[],m['triangles']);mesh.update();o=bpy.data.objects.new(n,mesh);scene.collection.objects.link(o)
 if g:o.parent=parents[(g['prefix'],g['kind'])]
 mesh.materials.append(choose_new(n));o['FreeCAD_part']=n
 for p in mesh.polygons:p.use_smooth=True
 mesh.set_sharp_from_angle(angle=math.radians(35))
 if any(k in n for k in ['SoundboxShell','Baseplate','PickWheel']):
  mod=o.modifiers.new('Tiny presentation edge bevel','BEVEL');mod.width=.00015;mod.segments=2

def keycurve(owner,path,index,fr,values,action=None):
 if action is None:
  action=bpy.data.actions.new(owner.name+' — exact unified rotation');owner.animation_data_create();owner.animation_data.action=action
 f=action.fcurves.new(data_path=path,index=index);f.keyframe_points.add(len(fr));f.keyframe_points.foreach_set('co',np.column_stack((fr,values)).astype(np.float32).ravel())
 for p in f.keyframe_points:p.interpolation='LINEAR'
 f.update();owner.animation_data.action_slot=action.slots[0];return f
for r in data['rows']:
 n=r['prefix'];end=230399/24;base=2*math.pi*end/400
 for kind,factor,initial in [('Driver',1,0),('Wheel',r['ratio'],RELEASE_ANGLE),('Idler',r['driver_teeth']/12,0)]:
  keycurve(parents[(n,kind)],'rotation_euler',1,[1,230400],[-initial,-initial-base*factor])
# Self-contained moving chains: 32 interpolation poses over one link-pitch of travel.
# At the wrap, identical links exchange positions, so the visible geometry stays continuous.
def chain_geometry(row,phase,part):
 N,iy,path=chain_layout(row['driver_teeth'],row['driven_teeth']);z=row['lane_z'];pts=[route_point(path,k*PITCH+phase*PITCH) for k in range(N)];verts=[];faces=[]
 def prism(poly,z0,h):
  start=len(verts);L=len(poly)
  for zz in [z0,z0+h]:verts.extend([world((x,y,zz)) for x,y in poly])
  faces.append(tuple(start+j for j in reversed(range(L))));faces.append(tuple(start+L+j for j in range(L)))
  faces.extend([(start+j,start+(j+1)%L,start+L+(j+1)%L,start+L+j) for j in range(L)])
 for p,q in zip(pts,pts[1:]+pts[:1]):
  if part=='Rollers':
   poly=[(p[0]+1.1*math.cos(a*2*math.pi/12),p[1]+1.1*math.sin(a*2*math.pi/12)) for a in range(12)];prism(poly,z+4.7,3.2)
  else:
   dx,dy=q[0]-p[0],q[1]-p[1];D=math.hypot(dx,dy);ux,uy=dx/D,dy/D;vx,vy=-uy,ux;poly=[]
   for center,a0 in [(p,math.pi/2),(q,-math.pi/2)]:
    for j in range(9):
     a=a0+j*math.pi/8;poly.append((center[0]+1.45*(ux*math.cos(a)+vx*math.sin(a)),center[1]+1.45*(uy*math.cos(a)+vy*math.sin(a))))
   for zz in [z+3.9,z+7.9]:prism(poly,zz,.8)
 return verts,faces
for row in data['rows']:
 for part in ['Plates','Rollers']:
  n=row['prefix']+'_Chain'+part;verts,faces=chain_geometry(row,0,part);me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(n,me);scene.collection.objects.link(o);me.materials.append(steel if part=='Rollers' else seal)
  o['Reference_geometry']='Chain pitch-path approximation; tooth engagement is not a manufacturing simulation.'
  o.shape_key_add(name='Basis');action=None;period_frames=400/row['driver_teeth']*24
  for j in range(1,33):
   key=o.shape_key_add(name=f'Travel {j:02d}');vs,_=chain_geometry(row,j/32,part);key.data.foreach_set('co',np.array(vs,dtype=np.float32).ravel())
   if action is None:
    keys=o.data.shape_keys;keys.animation_data_create();action=bpy.data.actions.new(n+' — one-link travel');keys.animation_data.action=action
   points=[(1,0),(1+(j-1)*period_frames/32,0),(1+j*period_frames/32,1)]
   if j<32:points.extend([(1+(j+1)*period_frames/32,0),(1+period_frames,0)])
   unique={f:v for f,v in points};fr=sorted(unique);vals=[unique[f] for f in fr]
   f=keycurve(keys,f'key_blocks["{key.name}"].value',0,fr,vals,action);f.modifiers.new('CYCLES')
 print('Moving reference chain',row['note'],flush=True)
scene['CAD_source']='Lovophone_Unified_160min.FCStd';scene['MIDI_sync']='Frame 1 = MIDI zero; 24 fps; DAW 120 BPM';scene['Full_pattern_repeat_seconds']=9600
scene['Scope']='Rigid CAD geometry with procedural studio materials. Moving chains are regenerated reference pitch-path meshes; not exact production tooth/link engagement. Pick elasticity is not simulated.'
'''
suffix=s[s.index('# Neutral seamless tabletop'):s.index("scene['CAD_source']")]
suffix=suffix.replace("-.0004","-.0064").replace("(.62,-.91,.52)","(.65,-.95,.53)").replace("(0,0,.095)","(0,-.025,.065)").replace("camdata.lens=75","camdata.lens=74")
end=r'''
camdata.dof.use_dof=False;scene.frame_set(1);scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.cycles.samples=48
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Lovophone_Unified_Studio.blend'),compress=True)
scene.render.filepath=str(O/'Lovophone_Unified_Studio.png');bpy.ops.render.render(write_still=True)
cam.location=(1,-.025,.08);aim(cam,(0,-.025,.08));camdata.type='ORTHO';camdata.ortho_scale=.215
scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.filepath=str(O/'Lovophone_Unified_Right.png');bpy.ops.render.render(write_still=True)
print('UNIFIED_STUDIO_COMPLETE',flush=True)
'''
(R/'work/build_unified_studio.py').write_text(prefix+body+suffix+end)
