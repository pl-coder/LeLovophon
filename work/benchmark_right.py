import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,time
from pathlib import Path
s=bpy.context.scene;s.eevee.taa_render_samples=16
for f in [2,25,121]:
 s.frame_set(f);s.render.filepath=f'{_LOVOPHON_WORKSPACE}/work/right_test_{f}.png';t=time.time();bpy.ops.render.render(write_still=True);print('FRAME_SECONDS',f,time.time()-t,flush=True)
