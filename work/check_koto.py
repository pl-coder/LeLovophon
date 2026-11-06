import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
source=open((_LOVOPHON_WORKSPACE + '/work/koto_pendulums.py')).read().replace("doc=App.openDocument(OUT+'/Harpe_d_Amour_Two_Axle_Belts.FCStd')","doc=App.openDocument(OUT+'/Harpe_d_Amour_Koto_Pendulums.FCStd')")
exec(source)
pendulum_rows=json.load(open(OUT+'/koto_pendulum_geometry.json'))['rows']
def world(o):
    sh=o.Shape.copy();sh.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return sh
moving=set()
for n in notes:
    for suffix in ['_Driver','_Output','_LongArmRotor','_Rocker']:
        moving.update(o.Name for o in doc.getObject(n+suffix).Group if o.TypeId=='Part::Feature')
    moving.add(n+'_ConnectingRod')
fixed={o.Name:world(o) for o in doc.Objects if o.TypeId=='Part::Feature' and o.Name not in moving}
clashes=set();contacts=set();link_clashes=set()
for row in pendulum_rows:
    n=row['note']
    for step in range(72):
        update_pendulums(step*20/row['ratio']/72)
        for suffix in ['_ExtendedArm','_ExtendedPick','_ConnectingRod','_RockerPlate','_Crank']:
            sh=world(doc.getObject(n+suffix))
            for name,fs in fixed.items():
                if sh.BoundBox.intersect(fs.BoundBox) and sh.common(fs).Volume>1e-5:
                    if suffix=='_ExtendedPick' and name==n+'_KotoSpeakingString':contacts.add(n)
                    elif suffix in ['_ExtendedArm','_ExtendedPick']:clashes.add((n,suffix,name))
                    else:link_clashes.add((n,suffix,name))
    print('Checked cycle',n,flush=True)
invalid=[o.Name for o in doc.Objects if o.TypeId=='Part::Feature' and not o.Shape.isValid()]
report={'sampled_positions_per_cycle':72,'arm_string_hardware_clashes':sorted(clashes),'linkage_fixed_clashes':sorted(link_clashes),'intended_contacts':sorted(contacts),'invalid_shapes':invalid,'limits':'Sampled rigid-body geometry only; no force, wear, compliance or safety certification.'}
print(report,flush=True)
with open(OUT+'/koto_pendulum_checks.json','w') as f:json.dump(report,f,indent=2)
update_pendulums(0);doc.save()
