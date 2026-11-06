import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path((_LOVOPHON_WORKSPACE + ''));data=json.loads((R/'work/lab_frame_motion_map.json').read_text());rows=data['rows'];scene=bpy.context.scene
assert scene.frame_end==11520 and scene.render.fps==24
assert len([o for o in scene.objects if o.type=='LIGHT'])==5
for frame in [1,121,5761,11520]:
 scene.frame_set(frame);t=(frame-1)/24
 for r in rows:
  theta=-math.radians(18*t*r['ratio']);fy,fz=r['follower_y'],r['follower_z'];vy=-59-4*math.sin(theta)-fy;vz=-116+4*math.cos(theta)-fz;d=math.hypot(vy,vz);vy/=d;vz/=d;a=(r['lever_length']**2-225+d*d)/(2*d);h=math.sqrt(max(0,r['lever_length']**2-a*a));py=fy+vy*a;pz=fz+vz*a
  b1=(py-vz*h,pz+vy*h);b2=(py+vz*h,pz-vy*h);by,bz=b1 if b1[0]>b2[0] else b2;beta=math.atan2(-(by-fy),bz-fz);da=math.atan2(math.sin(beta-r['beta_mid']),math.cos(beta-r['beta_mid']))
  for kind,expected in [('Driver',-math.radians(18*t)),('Output',theta),('Rocker',beta),('LongArmRotor',math.pi/2+4*da)]:
   got=bpy.data.objects['Motion_'+r['note']+'_'+kind].rotation_euler.x;assert abs(got-expected)<.0001,(frame,r['note'],kind,got,expected)
scene.frame_set(1);bpy.context.view_layer.update();error=0
for m in json.loads((R/'work/lab_frame_mesh.json').read_text()):
 o=bpy.data.objects[m['name']];v=m['vertices'][0];expected=Vector(((v[0]-155)*.001,(-v[2]-55)*.001,(v[1]+157)*.001));actual=o.matrix_world@o.data.vertices[0].co;error=max(error,(actual-expected).length)
assert error<1e-6,error
print('VERIFIED: self-contained studio scene; 8 minutes at 24 fps; all twelve mechanisms match CAD motion at 0, 5, 240 and 479.958 seconds; max imported vertex error',error,flush=True)
