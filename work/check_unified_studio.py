import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
R=Path((_LOVOPHON_WORKSPACE + ''));sys.path.insert(0,str(R/'work'));from unified_design import chain_layout,route_point,PITCH,RELEASE_ANGLE
s=bpy.context.scene;meta=json.loads((R/'outputs/Lovophone_Unified_Design.json').read_text());assert s.frame_end==230400 and s.render.fps==24
maxchain=0
for f in [1,121,5761,115201,230400,230401]:
 s.frame_set(f);bpy.context.view_layer.update();t=(f-1)/24;deg=bpy.context.evaluated_depsgraph_get()
 for r in meta['rows']:
  for k,factor,initial in [('Driver',1,0),('Wheel',r['ratio'],RELEASE_ANGLE),('Idler',r['driver_teeth']/12,0)]:
   o=bpy.data.objects.get('Motion_'+r['prefix']+'_'+k)
   if o:assert abs(o.rotation_euler.y-(-initial-2*math.pi*t/400*factor))<.0001,(f,r['note'],k)
  if r['direct_input']:continue
  N,iy,path=chain_layout(r['driver_teeth'],r['driven_teeth']);phase=(t*r['driver_teeth']/400)%1;j=min(31,int(phase*32));u=phase*32-j
  for part in ['Plates','Rollers']:
   def first(ph):
    p=route_point(path,ph*PITCH)
    if part=='Rollers':x,y=p[0]+1.1,p[1];z=r['lane_z']+4.7
    else:
     q=route_point(path,PITCH+ph*PITCH);dx,dy=q[0]-p[0],q[1]-p[1];D=math.hypot(dx,dy);x,y=p[0]-1.45*dy/D,p[1]+1.45*dx/D;z=r['lane_z']+3.9
    return Vector(((x-155)*.001,(-z-55)*.001,(y+157)*.001))
   o=bpy.data.objects[r['prefix']+'_Chain'+part];actual=o.evaluated_get(deg).data.vertices[0].co
   expected=[first(j/32+k)*(1-u)+first((j+1)/32+k)*u for k in [-1,0,1]]
   err=min((actual-v).length for v in expected);maxchain=max(maxchain,err);assert err<2e-6,(f,r['note'],part,err)
s.frame_set(1);bpy.context.view_layer.update();maxrigid=0
for m in json.loads((R/'work/unified_mesh.json').read_text()):
 if 'ChainPlates' in m['name'] or 'ChainRollers' in m['name']:continue
 o=bpy.data.objects[m['name']];v=m['vertices'][0];ex=Vector(((v[0]-155)*.001,(-v[2]-55)*.001,(v[1]+157)*.001));a=o.matrix_world@o.data.vertices[0].co;err=(a-ex).length;maxrigid=max(maxrigid,err);assert err<1e-6,(m['name'],err)
report=dict(full_repeat_seconds=9600,fps=24,frame_end=230400,checked_frames=[1,121,5761,115201,230400,230401],max_rigid_vertex_error_m=maxrigid,max_chain_reference_error_m=maxchain,all_voice_rotations_verified=True,moving_chain_reference_verified=True)
(R/'outputs/Lovophone_Unified_Animation_Check.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
