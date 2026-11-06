import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import runpy
ns=runpy.run_path((_LOVOPHON_WORKSPACE + '/work/koto_cam_drive.py'),run_name='definitions')
globals().update(ns)
def world(o):
    sh=o.Shape.copy();sh.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return sh
# A removable clear cover encloses the drive and picks; only string-sized exit holes remain.
guard=doc.addObject('App::DocumentObjectGroup','DriveGuard');guard.Label='Removable clear guard — fastener and impact specification pending'
back=bx(172,123,2,-30,-109,-156)
front=bx(172,123,2,-30,-109,-14)
roof=bx(172,2,144,-30,14,-156)
left=bx(2,123,144,-30,-109,-156).cut(bx(4,36,76,-31,-109,-93))
right=bx(2,123,144,140,-109,-156)
for row in rows:right=right.cut(Part.makeCylinder(1.3,4,V(139,-73,row['pivot_z']),V(1,0,0)))
for y,z in [(-83,-131),(-59,-116)]:right=right.cut(cy(4.5,4,V(139,y,z)))
for name,shape in [('GuardBack',back),('GuardFront',front),('GuardRoof',roof),('GuardLeft',left),('GuardRight',right)]:add(name,shape,guard)
# A plain coupling is the interface to a separately selected low-torque clockwork power unit.
doc.CommonInputShaft_D6.Shape=cy(3,174,V(-22,-83,-131))
add('ClockworkInputCoupling',cy(5,10,V(144,-83,-131)).cut(cy(3.05,12,V(143,-83,-131))),doc.Structure)
report={'sampled_positions_per_cycle':72,'arm_clashes':[],'linkage_clashes':[],'own_string_contacts':[],'cam_contact_max_error_mm':0,'limits':'Rigid-body sampled checks; no strength, compliance, wear or certified safety assessment. Guard fastening, flexible pick, tuning hardware and clockwork power unit require detail design.'}
moving=set()
for n in notes:
    for suffix in ['_Driver','_Output','_LongArmRotor','_Rocker']:
        moving.update(o.Name for o in doc.getObject(n+suffix).Group if o.TypeId=='Part::Feature')
fixed={o.Name:world(o) for o in doc.Objects if o.TypeId=='Part::Feature' and o.Name not in moving}
arm_clashes=set();link_clashes=set();contacts=set();contact_errors=[]
for row in rows:
    n=row['note']
    for step in range(72):
        t=step*20/row['ratio']/72;update_cams(t)
        beta,C,B=solve_cam(row,-math.radians(18*t*row['ratio']));contact_errors.append(abs((B-C).Length-15))
        for suffix in ['_ExtendedArm','_ExtendedPick','_FollowerLever','_FollowerRoller','_EccentricCam']:
            sh=world(doc.getObject(n+suffix))
            for name,fs in fixed.items():
                if sh.BoundBox.intersect(fs.BoundBox) and sh.common(fs).Volume>1e-5:
                    if suffix=='_ExtendedPick' and name==n+'_KotoSpeakingString':contacts.add(n)
                    elif suffix in ['_ExtendedArm','_ExtendedPick']:arm_clashes.add((n,suffix,name))
                    else:link_clashes.add((n,suffix,name))
    # Confirm intended pick contact at the bottom of its arc.
    rotor=doc.getObject(n+'_LongArmRotor');rotor.Placement=App.Placement(V(row['station'],row['pivot_y'],row['pivot_z']),App.Rotation(V(1,0,0),90));doc.recompute()
    if world(doc.getObject(n+'_ExtendedPick')).common(fixed[n+'_KotoSpeakingString']).Volume>1e-5:contacts.add(n)
    print('Checked cam cycle',n,flush=True)
report.update({'arm_clashes':sorted(arm_clashes),'linkage_clashes':sorted(link_clashes),'own_string_contacts':sorted(contacts),'cam_contact_max_error_mm':max(contact_errors),'invalid_shapes':[o.Name for o in doc.Objects if o.TypeId=='Part::Feature' and not o.Shape.isValid()]})
with open(OUT+'/koto_pendulum_checks.json','w') as f:json.dump(report,f,indent=2)
print(report,flush=True)
update_cams(0)
doc.Motion.Status+=' Removable guard with 2.6 mm string exits modeled; spring contact force and guard integrity unverified.'
doc.recompute();doc.save()
# Export a coloured triangle mesh for an independent review image.
meshes=[]
for o in doc.Objects:
    if o.TypeId!='Part::Feature':continue
    if 'Profile' in o.Name:continue
    sh=world(o);verts,tris=sh.tessellate(.6)
    if not tris:continue
    name=o.Name
    color=[.25,.30,.34];alpha=1
    if any(k in name for k in ['Soundbox','Baseplate','KotoAnchorBlock','KotoTunerBlock','ThirdBridge']):color=[.48,.30,.16]
    elif 'Guard' in name:color=[.65,.84,.88];alpha=.10
    elif 'String' in name or 'Tail' in name:color=[.92,.96,1]
    elif any(k in name for k in ['Pulley','Cam','Lever','Saddle','Spring']):color=[.80,.63,.30]
    elif 'Belt' in name:color=[.10,.11,.12]
    elif any(k in name for k in ['Shaft','Bearing','Pin','Coupling']):color=[.73,.77,.80]
    elif 'ExtendedArm' in name:
        colors=[[.75,.30,.28],[.82,.55,.22],[.35,.65,.45],[.28,.53,.76],[.59,.38,.72],[.25,.69,.69]];color=colors[notes.index(name[0])]
    meshes.append({'name':name,'vertices':[[v.x,v.y,v.z] for v in verts],'triangles':tris,'color':color,'alpha':alpha})
with open(OUT+'/koto_review_mesh.json','w') as f:json.dump(meshes,f)
