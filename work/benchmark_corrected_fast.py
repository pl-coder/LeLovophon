import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,time
from pathlib import Path
s=bpy.context.scene
s.display.shading.show_shadows=False;s.display.shading.show_cavity=False;s.render.resolution_x=1008;s.render.resolution_y=720
# Merge rigid CAD parts within each moving assembly and fixed scenery; keep all baked motion parents.
groups={}
for o in list(s.objects):
 if o.type=='MESH' and not o.hide_render:
  groups.setdefault(o.parent.name if o.parent else 'STATIC',[]).append(o)
for key,objs in groups.items():
 if len(objs)<2:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:
  o.select_set(True)
  for mod in list(o.modifiers):o.modifiers.remove(mod)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join()
bpy.ops.wm.save_as_mainfile(filepath=(_LOVOPHON_WORKSPACE + '/work/lab_corrected_fast.blend'),compress=True)
t=time.time()
for i in range(5):
 s.frame_set(1000+i);s.render.filepath=(_LOVOPHON_WORKSPACE + '/work/corrected_benchmark.jpg');bpy.ops.render.render(write_still=True)
print('BENCHMARK_SECONDS',time.time()-t,flush=True)
