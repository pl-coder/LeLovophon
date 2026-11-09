import bpy,math,json,sys,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'outputs/LeLovophon_Direct_Gear_Prototype/Axle_Clearance_Revision/Paris_Close_Studio';O.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(R/'work'))
from direct_gear_math import ROWS,DRIVE,linkage,angle
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];start=int(args[0]) if args else 1;end=int(args[1]) if len(args)>1 else 5760
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.render_aa='16';s.display.shading.background_type='WORLD';s.world.color=(.055,.065,.075);s.view_settings.view_transform='Standard';s.render.film_transparent=True
s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.fps=12;s.frame_start=1;s.frame_end=5760
frames=R/'work/lovophon_paris_close_final_frames';frames.mkdir(exist_ok=True)
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
cd=bpy.data.cameras.new('Level constant-radius slow right orbit');cam=bpy.data.objects.new('Camera',cd);s.collection.objects.link(cam);s.camera=cam;cd.type='PERSP';cd.lens=50;cd.sensor_width=36;cd.shift_y=0;cd.clip_start=.005;cd.clip_end=10
centre=p(((mins[0]+maxs[0])/2,-91,(mins[2]+maxs[2])/2));radius=.95
from fractions import Fraction
# Native and Blender axes both useX for rotation. Arm rotations follow exact circle-closure, not sine curves.
def pose(t):
 t=t%480
 common.rotation_euler.x=-2*math.pi*t/20
 for obj in parts.values():
  row=obj['row'];theta=row['phase_rad']+2*math.pi*t*float(Fraction(row['ratio']))/20;a,b,beta=linkage(row,theta);obj['crank'].rotation_euler.x=theta-row['phase_rad'];obj['rocker'].rotation_euler.x=angle(row,theta);obj['rod'].location=p((0,*a));obj['rod'].rotation_euler.x=math.atan2(b[1]-a[1],b[0]-a[0])-obj['rod_angle']
 az=math.radians(-53+360*t/480);elev=math.radians(16+5*math.sin(2*math.pi*t/480));target=Vector((centre.x,centre.y,.075));cam.location=target+radius*Vector((math.cos(elev)*math.cos(az),math.cos(elev)*math.sin(az),math.sin(elev)));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
from direct_gear_studio_materials import apply_studio
apply_studio()
from lovophon_paris_close_studio import setup
staging=setup()
s.use_nodes=False
s.eevee.taa_render_samples=64
# Focus follows the instrument centre; the distant room falls out of focus.
focal=bpy.data.objects.new('Lovophon focus',None);s.collection.objects.link(focal);focal.location=Vector((centre.x,centre.y,.11));cd.dof.use_dof=True;cd.dof.focus_object=focal;cd.dof.aperture_fstop=1.8;cd.dof.aperture_blades=9
s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=32;s.eevee.use_raytracing=True
pose(0)
# Static room reflections and indirect studio bounce supplement screen-space tracing.
probe=bpy.data.lightprobes.new('Studio reflection capture','SPHERE');probe.influence_distance=1.4;probe.clip_start=.025;ob=bpy.data.objects.new('Studio reflection capture',probe);s.collection.objects.link(ob);ob.location=Vector((centre.x,centre.y,.14))
vol=bpy.data.lightprobes.new('Local studio bounce','VOLUME');vol.resolution_x=5;vol.resolution_y=5;vol.resolution_z=4;vol.bake_samples=64;vol.capture_world=True;ob=bpy.data.objects.new('Local studio bounce',vol);s.collection.objects.link(ob);ob.location=(0,0,.10);ob.scale=(.60,.52,.43)
bpy.context.view_layer.objects.active=ob;ob.select_set(True)
try:bpy.ops.object.lightprobe_cache_bake(subset='ACTIVE')
except Exception as err:print('BOUNCE_BAKE',err,flush=True)
for m in data:
 ob=bpy.data.objects.get(m['name'])
 if ob and ob.type=='MESH' and any(x in ob.name for x in ['Gear','Shaft','Crank','Saddle','Tube','Carrier','Rocker','Hub','Socket','Bearing']):
  be=ob.modifiers.new('Subtle machined edge highlights','BEVEL');be.width=.00010;be.segments=2;be.limit_method='ANGLE';be.angle_limit=.65
if start==1 and not (O/'LeLovophon_Paris_Studio.blend').exists():bpy.ops.wm.save_as_mainfile(filepath=str(O/'LeLovophon_Paris_Studio.blend'))
# Preview endpoints before the long render, at the exact same height, radius and lens.
for t,label in ([(0,'Start'),(60,'045'),(120,'090'),(180,'135'),(240,'180'),(300,'225'),(360,'270'),(420,'315'),(480,'End')] if start==1 and not (O/'Orbit_360_End.png').exists() else []):
 pose(t);s.render.filepath=str(O/('Orbit_360_'+label+'.png'));bpy.ops.render.render(write_still=True)
metadata=dict(duration_seconds=480,unique_motion_fps=12,delivery_fps=24,width=1600,height=900,input_rpm=3,ratios=[r['ratio'] for r in ROWS],camera=dict(target_world=[centre.x,centre.y,.075],radius_metres=radius,height_range_metres=[.075+radius*math.sin(math.radians(a)) for a in [11,21]],azimuth_start_deg=-53,azimuth_end_deg=307,elevation_mid_deg=16,elevation_arc_deg=5,roll_deg=0,lens_mm=50,vertical_lens_shift=0,note='A gentle vertical arc accompanies the 360-degree orbit; camera looks towards the staged model and table.'),motion='Exact crank-rocker closure; all gear/crank/rod/rocker/pick motions driven from one input phase. Rigid kinematic depiction, not physical proof.',background=staging,depth_of_field=dict(fstop=1.8,focus='Lovophon centre',background='Optically softened studio'),lighting='Warm side key, cool low fill, warm rim; local indirect-light bake, captured room reflections and screen-space ray tracing; subtle visual edge bevels do not change the CAD.',physical_test_passed=False,endpoint_sampling='5760 uniformly spaced samples including both0 and480 seconds; final camera and mechanism pose reset exactly to the opening pose.')
if start==1:(O/'Orbit_360_Details.json').write_text(json.dumps(metadata,indent=2))
for f in range(start,end+1):
 path=frames/('frame_%05d.png'%f)
 if path.exists():continue
 t=(f-1)*480/5759;pose(t);s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 if f%60==0:print('PROGRESS',f,'/',end,flush=True)
print('CYCLE_RENDER_COMPLETE',flush=True)
