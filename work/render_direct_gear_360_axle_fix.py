import bpy,math,json,sys,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'outputs/LeLovophon_Direct_Gear_Prototype/Axle_Clearance_Revision/360_Orbit';O.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(R/'work'))
from direct_gear_math import ROWS,DRIVE,linkage,angle
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];start=int(args[0]) if args else 1;end=int(args[1]) if len(args)>1 else 5760
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.render_aa='16';s.display.shading.background_type='WORLD';s.world.color=(.055,.065,.075);s.view_settings.view_transform='Standard';s.render.film_transparent=True
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.fps=12;s.frame_start=1;s.frame_end=5760
frames=R/'work/direct_gear_studio_360_axle_fix_frames';frames.mkdir(exist_ok=True)
def p(v):return Vector(((v[0]-155)/1000,(-v[2]-55)/1000,(v[1]+157)/1000))
def parent(n,pos):
 ob=bpy.data.objects.new(n,None);s.collection.objects.link(ob);ob.location=p(pos);return ob
common=parent('Common input rotation',(0,*DRIVE));parts={};data=json.loads((R/'work/direct_gear_mesh_axle_fix.json').read_text())
for row in ROWS:
 n='V%02d'%row['index'];x=row['station_x'];a,b,beta=linkage(row,row['phase_rad']);parts[n]=dict(row=row,crank=parent(n+' crank rotation',(0,*row['crank_yz'])),rocker=parent(n+' rocker rotation',(0,*row['pivot_yz'])),rod=parent(n+' coupling rod',(0,*a)),rod_angle=math.atan2(b[1]-a[1],b[0]-a[0]))
mins=[min(v[k] for m in data for v in m['vertices']) for k in range(3)];maxs=[max(v[k] for m in data for v in m['vertices']) for k in range(3)]
for m in data:
 name=m['name'];pa=None
 if name in ['Common5mmInputShaft','HandInputWheel','HandleJournal','FreeTurningHandGrip'] or '_DriverGear' in name:pa=common
 elif name[:3] in parts:
  obj=parts[name[:3]]
  if any(tag in name for tag in ['_OutputGear','_Crank','_PinRetainingWasher_0','_3mmShaft_1']):pa=obj['crank']
  elif '_POMCoupler' in name:pa=obj['rod']
  elif any(tag in name for tag in ['_Rocker','_PinRetainingWasher_1','_PendulumHub','_TubeArm','_TipSocket','_PETPick','_3mmShaft_0']):pa=obj['rocker']
 vs=[p(v)-(pa.location if pa else Vector()) for v in m['vertices']];mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],m['triangles']);mesh.update();ob=bpy.data.objects.new(name,mesh);s.collection.objects.link(ob)
 if pa:ob.parent=pa
 mat=bpy.data.materials.new(name);mat.diffuse_color=(*m['color'],1);mesh.materials.append(mat)
 for f in mesh.polygons:f.use_smooth=True
 mesh.set_sharp_from_angle(angle=math.radians(35))
cd=bpy.data.cameras.new('Level constant-radius slow right orbit');cam=bpy.data.objects.new('Camera',cd);s.collection.objects.link(cam);s.camera=cam;cd.type='PERSP';cd.lens=50;cd.sensor_width=36;cd.shift_y=.10;cd.clip_start=.005;cd.clip_end=10
centre=p(((mins[0]+maxs[0])/2,-91,(mins[2]+maxs[2])/2));radius=.95
from fractions import Fraction
# Native and Blender axes both useX for rotation. Arm rotations follow exact circle-closure, not sine curves.
def pose(t):
 t=t%480
 common.rotation_euler.x=-2*math.pi*t/20
 for obj in parts.values():
  row=obj['row'];theta=row['phase_rad']+2*math.pi*t*float(Fraction(row['ratio']))/20;a,b,beta=linkage(row,theta);obj['crank'].rotation_euler.x=theta-row['phase_rad'];obj['rocker'].rotation_euler.x=angle(row,theta);obj['rod'].location=p((0,*a));obj['rod'].rotation_euler.x=math.atan2(b[1]-a[1],b[0]-a[0])-obj['rod_angle']
 az=math.radians(-53+360*t/480);cam.location=centre+Vector((radius*math.cos(az),radius*math.sin(az),0));cam.rotation_euler=(centre-cam.location).to_track_quat('-Z','Y').to_euler()
from direct_gear_studio_materials import apply_studio
apply_studio()
pose(0)
if start==1 and not (O/'LeLovophon_360_Studio_Scene.blend').exists():bpy.ops.wm.save_as_mainfile(filepath=str(O/'LeLovophon_360_Studio_Scene.blend'))
# Preview endpoints before the long render, at the exact same height, radius and lens.
for t,label in ([(0,'Start'),(60,'045'),(120,'090'),(180,'135'),(240,'180'),(300,'225'),(360,'270'),(420,'315'),(480,'End')] if start==1 and not (O/'Orbit_360_End.png').exists() else []):
 pose(t);s.render.filepath=str(O/('Orbit_360_'+label+'.png'));bpy.ops.render.render(write_still=True)
metadata=dict(duration_seconds=480,unique_motion_fps=12,delivery_fps=24,width=1280,height=720,input_rpm=3,ratios=[r['ratio'] for r in ROWS],camera=dict(target_world=list(centre),radius_metres=radius,height_metres=centre.z,azimuth_start_deg=-53,azimuth_end_deg=307,tilt_deg=0,roll_deg=0,lens_mm=50,vertical_lens_shift=.10,note='Lens shift frames the tall bank while the camera stays horizontal at string height.'),motion='Exact crank-rocker closure; all gear/crank/rod/rocker/pick motions driven from one input phase. Rigid kinematic depiction, not physical proof.',background='Flat blue composited after rendering to prevent blue spill.',physical_test_passed=False,endpoint_sampling='5760 uniformly spaced samples including both0 and480 seconds; final camera and mechanism pose reset exactly to the opening pose.')
if start==1:(O/'Orbit_360_Details.json').write_text(json.dumps(metadata,indent=2))
for f in range(start,end+1):
 path=frames/('frame_%05d.png'%f)
 if path.exists():continue
 t=(f-1)*480/5759;pose(t);s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 if f%60==0:print('PROGRESS',f,'/',end,flush=True)
print('CYCLE_RENDER_COMPLETE',flush=True)
