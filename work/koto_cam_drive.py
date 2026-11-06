import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App, Part, math, json
from FreeCAD import Vector as V
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
doc=App.openDocument(OUT+'/Harpe_d_Amour_Koto_Pendulums.FCStd')
notes='CDEFGA';rows=json.load(open(OUT+'/koto_pendulum_geometry.json'))['rows']
def cy(r,h,p):return Part.makeCylinder(r,h,p,V(1,0,0))
def bx(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def add(name,shape,group):
    o=doc.addObject('Part::Feature',name);o.Shape=shape;group.addObject(o);return o
def solve_cam(row,theta):
    U=V(0,row['pivot_y'],row['pivot_z']);C=V(0,-59-4*math.sin(theta),-116+4*math.cos(theta))
    v=C-U;d=v.Length;v.normalize();a=(row['lever_length']**2-15**2+d*d)/(2*d);h2=row['lever_length']**2-a*a
    assert h2>0,'Cam unreachable'
    P=U+v*a;perp=V(0,-v.z,v.y);h=math.sqrt(h2);b1=P+perp*h;b2=P-perp*h;B=b1 if b1.y>b2.y else b2
    return math.atan2(-(B.y-U.y),B.z-U.z),C,B

def build_cams():
    for row in rows:
        n=row['note'];row['lever_length']=row['ground']
        for suffix in ['_ConnectingRod','_Crank','_RockerPlate']:
            o=doc.getObject(n+suffix)
            if o:doc.removeObject(o.Name)
        cam=cy(12,3,V(5.25,0,4)).cut(cy(5.05,5,V(4.25,0,0)))
        add(n+'_EccentricCam',cam,doc.getObject(n+'_Output'))
        D=row['lever_length'];g=doc.getObject(n+'_Rocker')
        lever=bx(2.5,4,D,8.75,-2,0).fuse(cy(6,2.5,V(8.75,0,0))).fuse(cy(4,2.5,V(8.75,0,D)))
        lever=lever.cut(cy(3.05,4.5,V(7.75,0,0)))
        add(n+'_FollowerLever',lever,g)
        add(n+'_FollowerRoller',cy(3,3,V(5.25,0,D)).cut(cy(1.05,5,V(4.25,0,D))),g)
        add(n+'_RollerPin',cy(1,6,V(5.25,0,D)),g)
        spring=add(n+'_ReturnSpringEnvelope',cy(5,3,V(5.25,0,0)).cut(cy(3.3,5,V(4.25,0,0))),g)
        spring.addProperty('App::PropertyString','DesignNote','Design');spring.DesignNote='Off-the-shelf torsion spring envelope; preload and rate must be selected to maintain cam contact without excessive plucking force.'
        vals=[solve_cam(row,math.radians(j))[0] for j in range(360)];ref=vals[0];vals=[ref+math.atan2(math.sin(b-ref),math.cos(b-ref)) for b in vals]
        row['beta_mid']=(max(vals)+min(vals))/2;row['swing_half_angle_deg']=math.degrees((max(vals)-min(vals))/2)
        row['drive']='12 mm radius eccentric disk, 4 mm eccentricity, 3 mm roller, spring return'
    doc.PendulumLinkages.Label='Six eccentric cams and spring-return rocking followers'

def update_cams(t):
    doc.Motion.Time=t
    for row in rows:
        theta=-math.radians(18*t*row['ratio']);beta,C,B=solve_cam(row,theta);delta=math.atan2(math.sin(beta-row['beta_mid']),math.cos(beta-row['beta_mid']))
        root=V(row['station'],row['pivot_y'],row['pivot_z'])
        doc.getObject(row['note']+'_LongArmRotor').Placement=App.Placement(root,App.Rotation(V(1,0,0),90+math.degrees(delta)))
        doc.getObject(row['note']+'_Rocker').Placement=App.Placement(root,App.Rotation(V(1,0,0),math.degrees(beta)))
    doc.recompute()

if __name__=='__main__':
    build_cams();update_cams(0)
    doc.Motion.LinkageGeometry=json.dumps(rows)
    doc.Motion.Status='Kinematic concept: six ratio belt drives, eccentric cams and spring-return roller followers. Clockwork power unit, spring rates, load sizing, belt specification and safety validation remain to be selected.'
    doc.Label="L'Harpe d'Amour — koto strings, cam-driven pendulums"
    doc.recompute();doc.save()
    with open(OUT+'/koto_pendulum_geometry.json','w') as f:json.dump({'rows':rows,'scope':doc.Motion.Status},f,indent=2)
    print('Cam followers saved',[(r['note'],round(r['swing_half_angle_deg'],2)) for r in rows])
