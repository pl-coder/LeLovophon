import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs';data=json.loads((R/'work/unified_motion_map.json').read_text());membership={}
for g in data['groups']:
 M=Matrix([g['matrix'][j:j+4] for j in range(0,16,4)]);g['inv']=M.inverted()
 for n in g['members']:membership[n]=g
count=0
for m in json.loads((R/'work/unified_mesh.json').read_text()):
 n=m['name']
 if not ('_DriveSprocket' in n or '_DrivenSprocket' in n):continue
 o=bpy.data.objects[n];g=membership[n];vs=[]
 for v in m['vertices']:
  p=g['inv']@Vector(v);vs.append((p.x*.001,-p.z*.001,p.y*.001))
 old=o.data;mesh=bpy.data.meshes.new(n+' — open web');mesh.from_pydata(vs,[],m['triangles']);mesh.update()
 for mat in old.materials:mesh.materials.append(mat)
 for p in mesh.polygons:p.use_smooth=True
 mesh.set_sharp_from_angle(angle=math.radians(35));o.data=mesh;count+=1
s=bpy.context.scene;s.frame_set(1);s.render.engine='CYCLES';s.cycles.samples=48;s.render.resolution_x=1600;s.render.resolution_y=1000
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Lovophone_Unified_Studio.blend'),compress=True)
s.render.filepath=str(O/'Lovophone_Unified_Studio.png');bpy.ops.render.render(write_still=True)
c=s.camera;c.location=(1,-.025,.08);c.rotation_euler=(Vector((0,-.025,.08))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=.215;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.filepath=str(O/'Lovophone_Unified_Right.png');bpy.ops.render.render(write_still=True)
print('UPDATED_OPEN_WEBS',count,flush=True)
