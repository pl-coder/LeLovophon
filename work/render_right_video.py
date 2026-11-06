import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import bpy,time,json
from pathlib import Path
from mathutils import Vector
R=Path((_LOVOPHON_WORKSPACE + ''));s=bpy.context.scene
hidden=['N20MotorCan','N20Gearbox','N20OutputShaft','ElectricShaftCoupling','ElectricMotorBracket','PWMSpeedBoard','SpeedPotBody','SpeedPotShaft','SpeedControlKnob','ElectricRunSwitch','ElectricSupplyConnector','ElectricClearTop','ElectricClearRear','ElectricClearFront','ElectricCouplingShield']
for name in hidden:
 o=bpy.data.objects.get(name)
 if o:o.hide_render=True
c=s.camera;c.location=(1,0,.099);c.rotation_euler=(Vector((0,0,.099))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=.238;c.data.dof.use_dof=False
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_x=1120;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.frame_set(1);s.render.filepath=str(R/'work/right_cycles_test.png');t=time.time();bpy.ops.render.render(write_still=True);print('BENCH_SECONDS',time.time()-t,flush=True)
# Probe EEVEE on this machine as a practical full-film renderer.
s.render.engine='CYCLES' if False else 'BLENDER_EEVEE_NEXT'
print('EEVEE_OPTIONS',[(p.identifier) for p in s.eevee.bl_rna.properties],flush=True)
s.eevee.taa_render_samples=32
s.render.filepath=str(R/'work/right_eevee_test.png');t=time.time();bpy.ops.render.render(write_still=True);print('EEVEE_SECONDS',time.time()-t,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/Lovophone_Right_Video.blend'))
