import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,json
from pathlib import Path
R=Path((_LOVOPHON_WORKSPACE + ''));s=bpy.context.scene;hidden=[]
for o in bpy.data.objects:
 if o.name=='DriveFrameRightCheek' or o.name.startswith(('DriveFrameRightCheekBolt','DriveFrameRightCheekWasher','DriveFrameRightCheekNut','DriveFrameRightInputRetainer')):
  o.hide_render=True;hidden.append(o.name)
s['Presentation_cutaway']='Near drive end plate and its fasteners hidden to reveal transmission; engineering CAD unchanged.'
s.frame_set(1);s.render.image_settings.file_format='PNG';s.render.filepath=str(R/'outputs/Lovophone_Open_Drive_Right_View.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/Lovophone_Right_Open_Drive.blend'))
(R/'work/right_open_drive_hidden.json').write_text(json.dumps(hidden,indent=2))
