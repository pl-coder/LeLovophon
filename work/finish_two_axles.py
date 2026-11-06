import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
# Shorten intermediate bridge supports toward the string plane, clear of belt wraps.
for n in notes:
    tower=doc.getObject(n+'_AnchorTower');bb=tower.Shape.BoundBox
    tower.Shape=box(bb.XLength,bb.YLength,6,bb.XMin,bb.YMin,-39)
    foot=doc.getObject(n+'_AnchorFoot');bb=foot.Shape.BoundBox
    foot.Shape=box(bb.XLength,3,10,bb.XMin,-109,-41)
    beam=doc.getObject(n+'_AnchorBeam');bb=beam.Shape.BoundBox
    beam.Shape=box(bb.XLength,4,23,bb.XMin,bb.YMin,-39)
doc.recompute();check_two_axles()
exec(open((_LOVOPHON_WORKSPACE + '/work/clear_two_axles.py')).read().split('# Check all fixed belt envelopes')[1])
assert not belt_clashes
with open(OUT+'/two_axle_drive_geometry.json') as f:r=json.load(f)
r['belt_fixed_hardware_clashes']=belt_clashes
with open(OUT+'/two_axle_drive_geometry.json','w') as f:json.dump(r,f,indent=2)
doc.recompute();doc.save()
