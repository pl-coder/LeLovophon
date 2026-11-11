import bpy,math,json,sys,time,hashlib
from pathlib import Path
from mathutils import Vector
from fractions import Fraction
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'work'))
from pluck_r5.config import ROWS,DRIVE,linkage,angle
O=R/'outputs/LeLovophon_Pluck_Layout_R5/Paris_Studio_16min'
args=sys.argv[sys.argv.index('--')+1:];start,end=map(int,args[:2]);F=R/'work/lovophon_r5_paris_frames'
bpy.ops.wm.open_mainfile(filepath=str(O/'LeLovophon_R5_Paris_Studio.blend'))
s=bpy.context.scene;cam=s.camera;common=bpy.data.objects['Common input rotation'];parts={}
for row in ROWS:
 n='V%02d'%row['index'];a,b,_=linkage(row,row['phase_rad'])
 parts[n]=dict(row=row,crank=bpy.data.objects[n+' crank rotation'],rocker=bpy.data.objects[n+' rocker rotation'],rod=bpy.data.objects[n+' coupling rod'],rod_angle=math.atan2(b[1]-a[1],b[0]-a[0]))
def p(v):return Vector((v[0]/1000,(-v[2]-20)/1000,(v[1]+183)/1000))
metadata=json.loads((O/'Orbit_360_Details.json').read_text());centre=Vector(metadata['camera']['target_world']);radius=metadata['camera']['radius_metres']
def pose(t):
 t=t%480
 common.rotation_euler.x=-2*math.pi*t/20
 for obj in parts.values():
  row=obj['row'];theta=row['phase_rad']+2*math.pi*t*float(Fraction(row['ratio']))/20;a,b,beta=linkage(row,theta)
  obj['crank'].rotation_euler.x=theta-row['phase_rad'];obj['rocker'].rotation_euler.x=angle(row,theta);obj['rod'].location=p((0,*a));obj['rod'].rotation_euler.x=math.atan2(b[1]-a[1],b[0]-a[0])-obj['rod_angle']
 az=math.radians(-53+360*t/480);elev=math.radians(16+5*math.sin(2*math.pi*t/480));cam.location=centre+radius*Vector((math.cos(elev)*math.cos(az),math.cos(elev)*math.sin(az),math.sin(elev)));cam.rotation_euler=(centre-cam.location).to_track_quat('-Z','Y').to_euler()
# Check that the saved scene still resolves all 38 motion/camera controls.
assert len(parts)==12 and len([common,cam]+[o[k] for o in parts.values() for k in ['crank','rocker','rod']])==38
# Consolidate only triangles sharing a material, modifier setup and rigid motion parent.
from collections import defaultdict
batches=defaultdict(list)
names={x['name'] for x in json.loads((R/'work/pluck_r5/mesh.json').read_text())}
for ob in list(bpy.data.objects):
 if ob.name in names:batches[(ob.parent.name if ob.parent else '',ob.data.materials[0].name,bool(ob.modifiers))].append(ob)
for batch in batches.values():
 if len(batch)<2:continue
 bpy.ops.object.select_all(action='DESELECT')
 for ob in batch:ob.select_set(True)
 bpy.context.view_layer.objects.active=batch[0];bpy.ops.object.join()
print('RENDER_BATCHES',len(batches),flush=True)
begin=time.monotonic()
def update(scene):
 pose((scene.frame_current-1)*480/5759)
 if scene.frame_current%30==0:
  progress=dict(start=start,end=end,completed_through=scene.frame_current-1,elapsed_seconds=time.monotonic()-begin)
  (R/('work/r5_segment_%d.json'%start)).write_text(json.dumps(progress));print('PROGRESS',progress,flush=True)
bpy.app.handlers.frame_change_pre.append(update)
s.frame_start=start;s.frame_end=end;s.render.use_overwrite=False;s.render.use_file_extension=True;s.render.filepath=str(F/'frame_#####');s.render.use_persistent_data=True
bpy.ops.render.render(animation=True)
print('SEGMENT_COMPLETE',start,end,'elapsed',time.monotonic()-begin,flush=True)
