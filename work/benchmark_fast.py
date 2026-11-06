import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,time
s=bpy.context.scene;s.eevee.taa_render_samples=8
for o in bpy.data.objects:
 if o.type=='LIGHT':o.data.use_shadow_jitter=False
s.render.resolution_x=1008;s.render.resolution_y=900
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=95
for f in [1,100,200]:
 s.frame_set(f);s.render.filepath=f'{_LOVOPHON_WORKSPACE}/work/right_fast_{f}.jpg';t=time.time();bpy.ops.render.render(write_still=True);print('FRAME_SECONDS',f,time.time()-t,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=(_LOVOPHON_WORKSPACE + '/work/Lovophone_Right_Fast.blend'))
