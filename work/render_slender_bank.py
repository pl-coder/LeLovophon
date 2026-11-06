import bpy,json,math
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'outputs/LeLovophon_Slender_Bank'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.render_aa='16';s.display.shading.background_type='WORLD';s.world.color=(.055,.065,.075);s.view_settings.view_transform='Standard'
def p(v):return ((v[0]-155)/1000,(-v[2]-55)/1000,(v[1]+157)/1000)
for m in json.loads((R/'work/slender_bank_mesh.json').read_text()):
 mesh=bpy.data.meshes.new(m['name']);mesh.from_pydata([p(v) for v in m['vertices']],[],m['triangles']);mesh.update();ob=bpy.data.objects.new(m['name'],mesh);s.collection.objects.link(ob)
 mat=bpy.data.materials.new(m['name']);mat.diffuse_color=(*m['color'],1);mesh.materials.append(mat)
 for f in mesh.polygons:f.use_smooth=True
 mesh.set_sharp_from_angle(angle=math.radians(35))
cd=bpy.data.cameras.new('Upper-bank study');cam=bpy.data.objects.new('Camera',cd);s.collection.objects.link(cam);s.camera=cam;cam.location=(.62,-.83,.48);cam.rotation_euler=(Vector((.015,0,.09))-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='PERSP';cd.lens=68
s.render.resolution_x=1400;s.render.resolution_y=950;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(O/'LeLovophon_Slender_Bank_Study.png');bpy.ops.render.render(write_still=True)
cam.location=(1,0,.10);cam.rotation_euler=(Vector((0,0,.10))-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=.238;s.render.resolution_x=1008;s.render.resolution_y=900;s.render.filepath=str(O/'LeLovophon_Slender_Bank_Right.png');bpy.ops.render.render(write_still=True)
print('Upper-bank previews saved; drivetrain not shown or validated',flush=True)
