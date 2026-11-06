import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,time
s=bpy.context.scene
print('SETTINGS',s.eevee.use_raytracing,s.eevee.use_fast_gi,s.eevee.use_gtao,flush=True)
s.eevee.use_raytracing=False;s.eevee.use_fast_gi=False;s.eevee.use_gtao=False;s.eevee.taa_render_samples=16
for o in bpy.data.objects:
 if o.type=='LIGHT':
  print(o.name,o.data.use_shadow_jitter,flush=True)
  o.data.use_shadow_jitter=False;o.data.use_shadow=True
s.use_nodes=True;n=s.node_tree.nodes;n.clear();a=n.new('CompositorNodeRLayers');d=n.new('CompositorNodeDenoise');c=n.new('CompositorNodeComposite');s.node_tree.links.new(a.outputs['Image'],d.inputs['Image']);s.node_tree.links.new(d.outputs['Image'],c.inputs['Image'])
for f in [1,121]:
 s.frame_set(f);s.render.filepath=f'{_LOVOPHON_WORKSPACE}/work/right_clean_{f}.jpg';t=time.time();bpy.ops.render.render(write_still=True);print('FRAME_SECONDS',f,time.time()-t,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=(_LOVOPHON_WORKSPACE + '/work/Lovophone_Right_Clean.blend'))
