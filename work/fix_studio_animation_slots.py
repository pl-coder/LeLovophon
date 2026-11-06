import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy
from pathlib import Path
p=Path((_LOVOPHON_WORKSPACE + '/outputs/Lovophone_Textured_Studio.blend'))
n=0
for o in bpy.context.scene.objects:
 if o.animation_data and o.animation_data.action and len(o.animation_data.action.slots):o.animation_data.action_slot=o.animation_data.action.slots[0];n+=1
bpy.context.scene.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);print('Bound and saved',n,'motion actions',flush=True)
exec(compile(Path((_LOVOPHON_WORKSPACE + '/work/check_lovophone_studio.py')).read_text(),'validate','exec'))
