"""Neutral CAD inspection views, not a physical validation or presentation film."""
import bpy,json,math
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'outputs/LeLovophon_Mechanical_Revision_R2'
assert json.loads((O/'Verification_Summary.json').read_text())['unexpected_sampled_motion_intersections']==0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.render_aa='16';s.display.shading.background_type='WORLD';s.world.color=(.055,.065,.075);s.view_settings.view_transform='Standard'
def p(v):return ((v[0]-155)/1000,(-v[2]-55)/1000,(v[1]+168)/1000)
for m in json.loads((R/'work/rebuild_mechanical/mesh.json').read_text()):
 mesh=bpy.data.meshes.new(m['name']);mesh.from_pydata([p(v) for v in m['vertices']],[],m['triangles']);mesh.update();ob=bpy.data.objects.new(m['name'],mesh);s.collection.objects.link(ob)
 mat=bpy.data.materials.new(m['name']);mat.diffuse_color=(*m['color'],1);mesh.materials.append(mat)
 for f in mesh.polygons:f.use_smooth=True
 mesh.set_sharp_from_angle(angle=math.radians(35))
cd=bpy.data.cameras.new('R2 inspection');cam=bpy.data.objects.new('Camera',cd);s.collection.objects.link(cam);s.camera=cam;cd.type='ORTHO';cd.ortho_scale=.50
def render(name,loc,target,width,height,scale):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale
 s.render.resolution_x=width;s.render.resolution_y=height;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(O/name);bpy.ops.render.render(write_still=True)
render('R2_Inspection_Overview.png',(.48,-.65,.35),(0,-.01,.12),1400,1000,.50)
render('R2_Inspection_Right.png',(1,-.01,.13),(0,-.01,.13),1050,1000,.32)
