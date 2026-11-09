import sys,json
from pathlib import Path
script=Path(__file__).resolve().parent/'render_lovophon_paris_close.py'
sys.argv.extend(['--','2','1'])
exec(compile(script.read_text().split('for f in range(start,end+1):')[0],str(script),'exec'))
objects=[common,cam]+[o[k] for o in parts.values() for k in ['crank','rocker','rod']]
def snapshot(t):
 pose(t);bpy.context.view_layer.update()
 return {o.name:[v for row in o.matrix_world for v in row] for o in objects}
a=snapshot(0);b=snapshot(480)
errors={name:max(abs(x-y) for x,y in zip(a[name],b[name])) for name in a}
result={'parent_and_camera_objects_checked':len(objects),'maximum_world_matrix_endpoint_error':max(errors.values()),'camera_world_matrix_endpoint_error':errors[cam.name],'camera_target_height_m':.075,'camera_radius_m':radius,'opening_closing_pose_exact':all(e==0 for e in errors.values())}
assert result['opening_closing_pose_exact']
(O/'Orbit_360_Pose_Verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2),flush=True)

from bpy_extras.object_utils import world_to_camera_view
bounds=[1e6,1e6,-1e6,-1e6];outside=[]
for j in range(97):
 pose(j*480/96);bpy.context.view_layer.update()
 for name in [m['name'] for m in data]:
  ob=bpy.data.objects.get(name)
  for v in ob.bound_box:
   q=world_to_camera_view(s,cam,ob.matrix_world@Vector(v));bounds=[min(bounds[0],q.x),min(bounds[1],q.y),max(bounds[2],q.x),max(bounds[3],q.y)]
   if q.x<0 or q.x>1 or q.y<0 or q.y>1 or q.z<=0:outside.append((j,name))
result['subject_screen_bounds']=bounds;result['framing_poses_checked']=97;result['cropped_subject_bounds']=outside;assert not outside,outside[:12]
(O/'Orbit_360_Pose_Verification.json').write_text(json.dumps(result,indent=2));print('FRAMING',bounds,flush=True)
