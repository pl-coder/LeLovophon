import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import runpy,json
ns=runpy.run_path((_LOVOPHON_WORKSPACE + '/work/koto_cam_drive.py'),run_name='definitions');globals().update(ns)
def world(o):
    s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return s
moving=set()
for n in notes:
    for suffix in ['_Driver','_Output','_LongArmRotor','_Rocker']:moving.update(o.Name for o in doc.getObject(n+suffix).Group if o.TypeId=='Part::Feature')
belts={n+'_RatioBelt' for n in notes}
fixed={o.Name:world(o) for o in doc.Objects if o.TypeId=='Part::Feature' and o.Name not in moving and o.Name not in belts}
clashes=[]
for n in notes:
    for suffix in ['_RatioDrivePulley','_RatioDrivenPulley','_RatioBelt']:
        o=doc.getObject(n+suffix);s=world(o)
        for name,fs in fixed.items():
            if s.BoundBox.intersect(fs.BoundBox) and s.common(fs).Volume>1e-5:clashes.append((o.Name,name))
print('Standard-pitch drive clashes:',clashes)
assert not clashes
r=json.load(open(OUT+'/koto_pendulum_checks.json'));r['standard_2mm_pitch_drive_clashes']=clashes
with open(OUT+'/koto_pendulum_checks.json','w') as f:json.dump(r,f,indent=2)
