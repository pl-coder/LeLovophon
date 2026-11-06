import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,time
s=bpy.context.scene
# Retain real timber grain; remove subpixel normal noise from polished metal to avoid sparkle.
for m in bpy.data.materials:
 if m.name.startswith(('Brushed steel','Satin aluminium','Satin brass')) and m.use_nodes:
  p=m.node_tree.nodes.get('Principled BSDF')
  for l in list(p.inputs['Normal'].links):m.node_tree.links.remove(l)
# Join rigid metal components inside the same animated assembly; leave generated timber mapping untouched.
groups={}
for o in list(s.objects):
 if o.type!='MESH' or o.hide_render:continue
 if any(any(k in m.name for k in ['walnut','spruce','Maple','plywood']) for m in o.data.materials if m):continue
 groups.setdefault(o.parent.name if o.parent else 'FIXED',[]).append(o)
for key,objs in groups.items():
 if len(objs)<2:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:
  bpy.context.view_layer.objects.active=o
  for mod in list(o.modifiers):
   try:bpy.ops.object.modifier_apply(modifier=mod.name)
   except Exception:o.modifiers.remove(mod)
  o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join()
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=(_LOVOPHON_WORKSPACE + '/work/corrected_right_optimized.blend'),compress=True)
for f in [1,49,97]:
 s.frame_set(f);s.render.filepath=(_LOVOPHON_WORKSPACE + '/work/corrected_right_polished_')+str(f)+'.png';t=time.time();bpy.ops.render.render(write_still=True);print('OPT_FRAME_SECONDS',f,time.time()-t,flush=True)
