import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,time
s=bpy.context.scene;s.use_nodes=True;n=s.node_tree.nodes;n.clear();r=n.new('CompositorNodeRLayers');d=n.new('CompositorNodeDenoise');d.use_hdr=True;c=n.new('CompositorNodeComposite');s.node_tree.links.new(r.outputs['Image'],d.inputs['Image']);s.node_tree.links.new(d.outputs['Image'],c.inputs['Image'])
s.frame_set(1);s.render.filepath=(_LOVOPHON_WORKSPACE + '/work/corrected_right_denoised.png');t=time.time();bpy.ops.render.render(write_still=True);print('DENOISE_FRAME_SECONDS',time.time()-t,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=(_LOVOPHON_WORKSPACE + '/work/corrected_right_denoised.blend'),compress=True)
