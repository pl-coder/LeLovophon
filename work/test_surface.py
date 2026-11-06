import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,time
s=bpy.context.scene;s.use_nodes=False;s.eevee.taa_render_samples=8
for m in bpy.data.materials:
 if m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type=='BUMP':n.inputs['Strength'].default_value=.025
   if n.type=='VECT_MATH' and n.operation=='MULTIPLY':
    v=n.inputs[1].default_value
    if v[1]>200:n.inputs[1].default_value=(4,60,60)
s.frame_set(1);s.render.filepath=(_LOVOPHON_WORKSPACE + '/work/right_surface.jpg');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=(_LOVOPHON_WORKSPACE + '/work/Lovophone_Right_Final.blend'))
