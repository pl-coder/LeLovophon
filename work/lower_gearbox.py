import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App, FreeCADGui as Gui, Part, math, json
from FreeCAD import Vector as V
doc=App.ActiveDocument
if 'harpe_motion_timer' in globals():harpe_motion_timer.stop()
doc.Motion.Time=0;doc.recompute()
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
low_created=[];long_rows=[]
def low_box(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def low_cyl(r,h,p):return Part.makeCylinder(r,h,p,V(1,0,0))
def low_part(name,shape,color,parent):
    obj=doc.addObject('Part::Feature',name);obj.Shape=shape;obj.ViewObject.ShapeColor=color;parent.addObject(obj);low_created.append(obj);return obj
def low_capsule(a,b,r):
    d=b-a;d.normalize();p=V(0,-d.z,d.y)
    e=[Part.makeLine(a+p*r,b+p*r),Part.Arc(b+p*r,b+d*r,b-p*r).toShape(),Part.makeLine(b-p*r,a-p*r),Part.Arc(a-p*r,a-d*r,a+p*r).toShape()]
    return Part.Wire(e)
def prepare_low_gearbox():
    for obj in list(doc.Structure.Group):
        if obj.Name not in ['Baseplate_310x170x6','CommonInputShaft_D6']:doc.removeObject(obj.Name)
    doc.CommonInputShaft_D6.Shape=low_cyl(3,140,V(-22,-83,-131))
    doc.CommonInputShaft_D6.Label='Low gearbox input axle'
    for i,x in enumerate([-17,110]):
        stand=low_box(8,30,18,x,-109,-140).cut(low_cyl(6.05,10,V(x-1,-83,-131)))
        bush=low_cyl(6,6,V(x+1,-83,-131)).cut(low_cyl(3.1,8,V(x,-83,-131)))
        low_part('LowInputStand'+str(i),stand,(.18,.23,.28),doc.Structure)
        low_part('LowInputBearing'+str(i),bush,(.74,.78,.82),doc.Structure)
    tray=low_box(135,3,86,-20,-109,-154)
    tray=tray.fuse(low_box(135,6,3,-20,-106,-154)).fuse(low_box(135,6,3,-20,-106,-71))
    low_part('LowGearboxTray',tray,(.18,.23,.28),doc.Structure)
    g=doc.addObject('App::DocumentObjectGroup','RaisedArmTransmission');g.Label='1:1 belt drives from low gearbox to long arms'
    print('Gearbox moved low and to the rear')
def build_raised_arm(i):
    n='CDEFG'[i];a=[40,36,40,32,36][i];b=[40,32,32,24,24][i];inv=b/a;s=24*i
    st=doc.getObject(n+'_LongSpeakingString');h=st.VerticalY.Value
    top_c=doc.C_LongSpeakingString.VerticalY.Value
    R0=(top_c-(-105))/2;R=R0*inv;upper_y=h-R;upper_z=-34;lower_y=-83;lower_z=-131+(a+b)/2
    dr=doc.getObject(n+'_Driver');ou=doc.getObject(n+'_Output')
    dr.setExpression('Placement.Rotation.Angle',None);ou.setExpression('Placement.Rotation.Angle',None)
    dr.Placement=App.Placement(V(s,lower_y,-131),App.Rotation(V(1,0,0),90))
    ou.Placement=App.Placement(V(s,lower_y,lower_z),App.Rotation(V(1,0,0),90))
    dr.setExpression('Placement.Rotation.Angle','Motion.InputAngle + 90 deg')
    ou.setExpression('Placement.Rotation.Angle','-Motion.InputAngle * %d / %d + 90 deg'%(a,b))
    ou.Label='%s low gearbox output — %d:%d'%(n,a,b)
    for obj in list(ou.Group):
        if obj.TypeId=='Part::Feature' and obj.Name!=n+'_DrivenGear':doc.removeObject(obj.Name)
    ou.EffectiveArmRadius=R
    rotor=doc.addObject('App::Part',n+'_LongArmRotor')
    rotor.Label='%s long arm — %.2f mm'%(n,R)
    rotor.Placement=App.Placement(V(s,upper_y,upper_z),App.Rotation(V(1,0,0),-90))
    rotor.setExpression('Placement.Rotation.Angle','-Motion.InputAngle * %d / %d - 90 deg'%(a,b))
    rotor.addProperty('App::PropertyLength','ContactRadius','Geometry');rotor.ContactRadius=R
    rotor.addProperty('App::PropertyFloat','TransmissionRatio','Motion');rotor.TransmissionRatio=1
    silver=(.74,.78,.82);brass=(.82,.64,.29)
    color=[(.75,.30,.28),(.82,.55,.22),(.35,.65,.45),(.28,.53,.76),(.59,.38,.72)][i]
    low_part(n+'_LowOutputShaft',low_cyl(3,23.5,V(-12,0,0)),silver,ou)
    low_part(n+'_RaisedArmShaft',low_cyl(3,22,V(-6.5,0,0)),silver,rotor)
    pulley=low_cyl(8,6,V(5.25,0,0)).cut(low_cyl(3.05,8,V(4.25,0,0)))
    for name,parent in [(n+'_LowerTimingPulley',ou),(n+'_UpperTimingPulley',rotor)]:
        o=low_part(name,pulley.copy(),brass,parent)
        o.addProperty('App::PropertyString','DesignNote','Design');o.DesignNote='Equal reference pulley envelopes; tooth profile and catalogue belt selection pending'
    arm=low_box(3,4,R-.5,12,-2,0).fuse(low_cyl(6,3,V(12,0,0))).cut(low_cyl(3.05,5,V(11,0,0)))
    low_part(n+'_ExtendedArm',arm,color,rotor)
    low_part(n+'_ExtendedPick',low_box(3.3,.6,1.5,15,-.3,R-1),(.92,.88,.73),rotor)
    # Separate support planes leave the long arm and pick free to sweep.
    for label,yy,zz,positions in [('Lower',lower_y,lower_z,[-11,-5.5]),('Raised',upper_y,upper_z,[-5.5,0])]:
        for j,offset in enumerate(positions):
            x=s+offset
            stand=low_box(4,yy+113,18,x,-109,zz-9).cut(low_cyl(6.05,6,V(x-1,yy,zz)))
            bush=low_cyl(6,4,V(x,yy,zz)).cut(low_cyl(3.1,6,V(x-1,yy,zz)))
            low_part(n+'_'+label+'BearingStand'+str(j),stand,(.18,.23,.28),doc.Structure)
            low_part(n+'_'+label+'Bearing'+str(j),bush,silver,doc.Structure)
    A=V(s+5.25,lower_y,lower_z);B=V(s+5.25,upper_y,upper_z)
    belt=Part.Face(low_capsule(A,B,8.8)).cut(Part.Face(low_capsule(A,B,8.1))).extrude(V(6,0,0))
    obj=low_part(n+'_TimingBeltEnvelope',belt,(.12,.13,.15),doc.RaisedArmTransmission)
    obj.addProperty('App::PropertyFloat','SpeedRatio','Motion');obj.SpeedRatio=1
    obj.addProperty('App::PropertyString','DesignNote','Design');obj.DesignNote='1:1 open timing-belt concept; pitch, tensioner, guarding and load specification pending'
    st.ArmRadius=R
    doc.recompute()
    assert all(o.Shape.isValid() and not o.Shape.isNull() for o in low_created)
    long_rows.append({'note':n,'string_mm':st.SpeakingLength.Value,'arm_radius_mm':R,'output_axis_y_mm':upper_y,'output_axis_z_mm':upper_z,'gearbox_axis_y_mm':lower_y,'gearbox_axis_z_mm':lower_z,'centre_distance_mm':(B-A).Length})
    print(n,'arm radius',round(R,2),'mm; gearbox Y',lower_y)
def verify_raised_arms():
    rotating=set()
    for n in 'CDEFG':
        for suffix in ['_Driver','_Output','_LongArmRotor']:
            rotating.update(o.Name for o in doc.getObject(n+suffix).Group if o.TypeId=='Part::Feature')
    stationary=[o for o in doc.Objects if o.TypeId=='Part::Feature' and o.Name not in rotating]
    clashes=[]
    for i,row in enumerate(long_rows):
        n=row['note'];R=row['arm_radius_mm'];s=24*i;yy=row['output_axis_y_mm'];zz=-34
        arm=low_cyl(math.hypot(R-.5,2),3,V(s+12,yy,zz)).cut(low_cyl(3.05,5,V(s+11,yy,zz)))
        pick=low_cyl(math.hypot(R+.5,.3),3.3,V(s+15,yy,zz)).cut(low_cyl(R-1,5.3,V(s+14,yy,zz)))
        for obj in stationary:
            if obj.Name==n+'_LongSpeakingString':continue
            for label,envelope in [('arm',arm),('pick',pick)]:
                if envelope.BoundBox.intersect(obj.Shape.BoundBox) and envelope.common(obj.Shape).Volume>1e-5:
                    clashes.append({'voice':n,'part':obj.Name,'sweep':label})
    doc.Label="L'Harpe d'Amour — low gearbox, long arms"
    doc.Motion.Status='Low gearbox with prescribed 1:1 timing-belt transmissions; long arms in inverse pitch ratios. Belt tooth form, tensioners, loads and acoustic tuning not yet specified.'
    doc.recompute();doc.save()
    with open(OUT+'/low_gearbox_geometry.json','w') as f:json.dump({'Y_vertical':True,'base_top_y_mm':-109,'sweep_floor_reference_y_mm':-105,'arms':long_rows,'full_turn_stationary_clashes':clashes,'scope':'Geometric concept; transmission is prescribed, not contact/dynamics simulation.'},f,indent=2)
    print('Full-turn long-arm clashes:',clashes)
    return clashes
