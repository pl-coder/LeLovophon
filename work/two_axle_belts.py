import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App, FreeCADGui as Gui, Part, math, json
from FreeCAD import Vector as V
doc=App.ActiveDocument
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
notes='CDEFGA';drivers=[40,36,40,32,36,40];driven=[40,32,32,24,24,24]
brass=(.82,.64,.29);silver=(.74,.78,.82);dark=(.18,.23,.28)
def cyl(r,h,p):return Part.makeCylinder(r,h,p,V(1,0,0))
def box(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def part(name,shape,color,group):
    o=doc.addObject('Part::Feature',name);o.Shape=shape;o.ViewObject.ShapeColor=color;group.addObject(o);return o
def belt_wire(A,B,ra,rb):
    d=B-A;D=d.Length;d.normalize();p=V(0,-d.z,d.y);k=(ra-rb)/D;q=math.sqrt(1-k*k)
    n1=d*k+p*q;n2=d*k-p*q
    return Part.Wire([Part.makeLine(A+n1*ra,B+n1*rb),Part.Arc(B+n1*rb,B+d*rb,B+n2*rb).toShape(),Part.makeLine(B+n2*rb,A+n2*ra),Part.Arc(A+n2*ra,A-d*ra,A+n1*ra).toShape()])
def belt(A,B,ra,rb,width):return Part.Face(belt_wire(A,B,ra+.8,rb+.8)).cut(Part.Face(belt_wire(A,B,ra+.1,rb+.1))).extrude(V(width,0,0))
def prepare_two_axles():
    for n in notes:
        for obj in list(doc.Structure.Group):
            if obj.Name.startswith(n+'_LowerBearing'):doc.removeObject(obj.Name)
    part('CommonIntermediateAxle',cyl(3,164,V(-22,-79,-94)),silver,doc.Structure)
    doc.CommonIntermediateAxle.Label='Second long axle — fixed spindle, six independent pulley units'
    doc.CommonIntermediateAxle.addProperty('App::PropertyString','DesignNote','Design');doc.CommonIntermediateAxle.DesignNote='Pulley units rotate independently on bearings; they are not keyed together.'
    for j,x in enumerate([-17,134]):
        stand=box(6,34,18,x,-109,-103).cut(cyl(3.05,8,V(x-1,-79,-94)))
        part('IntermediateAxleStand'+str(j),stand,dark,doc.Structure)
    g=doc.addObject('App::DocumentObjectGroup','RatioBeltDrives');g.Label='Six ratio belts — one driven shaft and one shared fixed axle'
    doc.CommonInputShaft_D6.Label='Long common drive shaft — input pulleys turn together'
    doc.LowGearboxTray.Label='Low belt drive bed'
    print('Two long axles prepared')
def convert_belt_voice(i):
    n=notes[i];s=24*i;a=drivers[i];b=driven[i];r1=a*.3;r2=b*.3
    dr=doc.getObject(n+'_Driver');ou=doc.getObject(n+'_Output');rotor=doc.getObject(n+'_LongArmRotor')
    for parent in [dr,ou]:
        for obj in list(parent.Group):doc.removeObject(obj.Name)
    dr.setExpression('Placement.Rotation.Angle',None);ou.setExpression('Placement.Rotation.Angle',None)
    dr.Placement=App.Placement(V(s,-83,-131),App.Rotation(V(1,0,0),0))
    ou.Placement=App.Placement(V(s,-79,-94),App.Rotation(V(1,0,0),0))
    dr.setExpression('Placement.Rotation.Angle','-Motion.InputAngle')
    ou.setExpression('Placement.Rotation.Angle','-Motion.InputAngle * %d / %d'%(a,b))
    dr.Label=n+' common-shaft drive pulley — '+str(a)+' reference teeth'
    ou.Label=n+' independent pulley unit on shared axle — '+str(b)+' reference teeth'
    rotor.Label=n+' arm — %.3f x input'%(a/b)
    # Reference pitch radii scale with integer tooth counts; final belt pitch/profile remains unspecified.
    p=part(n+'_RatioDrivePulley',cyl(r1,5,V()).cut(cyl(3.05,7,V(-1,0,0))),brass,dr)
    p.addProperty('App::PropertyInteger','ReferenceTeeth','Belt');p.ReferenceTeeth=a
    p=part(n+'_RatioDrivenPulley',cyl(r2,5,V()).cut(cyl(5.05,7,V(-1,0,0))),brass,ou)
    p.addProperty('App::PropertyInteger','ReferenceTeeth','Belt');p.ReferenceTeeth=b
    part(n+'_CompoundPulleyHub',cyl(6,11.25,V()).cut(cyl(5.05,13.25,V(-1,0,0))),brass,ou)
    part(n+'_IndependentPulleyBearing',cyl(5,10.5,V(.25,0,0)).cut(cyl(3.1,12.5,V(-.75,0,0))),silver,ou)
    part(n+'_LowerTimingPulley',cyl(8,6,V(5.25,0,0)).cut(cyl(5.05,8,V(4.25,0,0))),brass,ou)
    A=V(s,-83,-131);B=V(s,-79,-94)
    part(n+'_RatioBelt',belt(A,B,r1,r2,5),(.12,.13,.15),doc.RatioBeltDrives)
    top=rotor.Placement.Base
    A=V(s+5.25,-79,-94);B=V(s+5.25,top.y,top.z)
    doc.getObject(n+'_TimingBeltEnvelope').Shape=belt(A,B,8,8,6)
    doc.recompute();print(n,'belt ratio',a,b,'=',round(a/b,4))
def check_two_axles():
    rows=json.load(open(OUT+'/soundbox_geometry.json'))['geometry']
    rotating=set()
    for n in notes:
        for suffix in ['_Driver','_Output','_LongArmRotor']:
            rotating.update(o.Name for o in doc.getObject(n+suffix).Group if o.TypeId=='Part::Feature')
    fixed=[o for o in doc.Objects if o.TypeId=='Part::Feature' and o.Name not in rotating]
    clashes=[];contacts=[]
    for i,row in enumerate(rows):
        n=row['note'];s=24*i;R=row['radius'];h=row['axis_y'];z=row['axis_z']
        arm=cyl(math.hypot(R-.5,2),3,V(s+12,h,z)).cut(cyl(3.05,5,V(s+11,h,z)))
        pick=cyl(math.hypot(R+.5,.3),3.3,V(s+15,h,z)).cut(cyl(R-1,5.3,V(s+14,h,z)))
        for obj in fixed:
            for tag,envelope in [('arm',arm),('pick',pick)]:
                if envelope.BoundBox.intersect(obj.Shape.BoundBox) and envelope.common(obj.Shape).Volume>1e-5:
                    item={'voice':n,'part':obj.Name,'sweep':tag}
                    if tag=='pick' and obj.Name==n+'_LongSpeakingString':contacts.append(item)
                    else:clashes.append(item)
    invalid=[o.Name for o in doc.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())]
    # Check stationary bearings and supports against the rotating pulley assemblies in world coordinates.
    drive_clashes=[]
    for n in notes:
        for suffix in ['_Driver','_Output']:
            for obj in doc.getObject(n+suffix).Group:
                shape=obj.Shape.transformed(obj.getGlobalPlacement().toMatrix())
                for fixed_obj in fixed:
                    if shape.BoundBox.intersect(fixed_obj.Shape.BoundBox) and shape.common(fixed_obj.Shape).Volume>1e-5:
                        drive_clashes.append({'pulley':obj.Name,'fixed_part':fixed_obj.Name})
    print('Arm clashes:',clashes,'intended contacts:',len(contacts),'drive clashes:',drive_clashes,'invalid:',invalid)
    report={'long_axles':2,'fixed_intermediate_axle':True,'independent_pulley_units':6,'gear_pairs':0,'ratios':[a/b for a,b in zip(drivers,driven)],'arm_clashes':clashes,'contacts':contacts,'drive_clashes':drive_clashes,'invalid':invalid,'scope':'Prescribed motion with pulley/belt envelopes. Belt pitch, tooth profiles, tensioners, bearing fits and loads remain unspecified.'}
    with open(OUT+'/two_axle_drive_geometry.json','w') as f:json.dump(report,f,indent=2)
    assert not clashes and not drive_clashes and not invalid and len(contacts)==6
    doc.Label="L'Harpe d'Amour — two axles, six belt drives"
    doc.Motion.Status=report['scope']
    doc.recompute();doc.save()
