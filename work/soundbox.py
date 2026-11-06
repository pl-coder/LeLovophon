import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App, FreeCADGui as Gui, Part, math, json
from FreeCAD import Vector as V
doc=App.ActiveDocument
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
wood=(.46,.29,.15);light=(.64,.45,.24);brass=(.82,.64,.29);silver=(.74,.78,.82)
def sb(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def sc(r,h,p,axis=V(1,0,0)):return Part.makeCylinder(r,h,p,axis)
def rod(p,q,r=.18):
    v=q-p;return sc(r,v.Length,p,v)
def add(name,shape,color,parent):
    o=doc.addObject('Part::Feature',name);o.Shape=shape;o.ViewObject.ShapeColor=color;parent.addObject(o);return o
def make_soundbox():
    g=doc.addObject('App::DocumentObjectGroup','Soundbox');g.Label='Hollow soundbox below the existing mechanism'
    shell=sb(370,66,200,-30,-181,-155).cut(sb(354,61,184,-22,-175,-147))
    for x in [164,200,236]:shell=shell.cut(sc(11,12,V(x,-146,36),V(0,0,1)))
    add('SoundboxShell',shell,wood,g)
    # The existing six-millimetre platform becomes the soundbox lid.
    doc.Baseplate_310x170x6.ViewObject.ShapeColor=light
    doc.Baseplate_310x170x6.Label='Soundbox top — 370 x 200 x 6 mm'
    for i,x in enumerate([-24,326]):
        add('SoundboxEndBlock'+str(i),sb(14,60,184,x,-175,-147),wood,g)
    for i,(x,z) in enumerate([(-18,-140),(-18,22),(310,-140),(310,22)]):
        add('SoundboxFoot'+str(i),sb(20,8,20,x,-189,z),(.14,.12,.10),g)
    doc.recompute();print('Hollow soundbox added below the mechanism')
def make_common_ends(count=5):
    g=doc.addObject('App::DocumentObjectGroup','CommonStringEnds');g.Label='Two shared load-bearing end frames'
    for tag,x in [('Anchor',-22),('Tuner',320)]:
        # Solid hardwood bulkhead and broad foot carry the complete string bank.
        frame=sb(16,151,30,x-8,-109,-72).fuse(sb(16,10,54,x-8,-109,-80))
        add('Shared'+tag+'Frame',frame,wood,g)
        add('Shared'+tag+'SaddleRail',sb(10,60,8,x-5,-18,-43),brass,g)
        for j,z in enumerate([-70,-48]):
            add('Shared'+tag+'Bolt'+str(j),sc(2.5,16,V(x,-114,z),V(0,1,0)).fuse(sc(4,2,V(x,-99,z),V(0,1,0))),silver,g)
    print('Shared end frames installed')
def convert_string(i):
    n='CDEFGA'[i];st=doc.getObject(n+'_LongSpeakingString');h=st.VerticalY.Value;L=st.SpeakingLength.Value;bridge_x=320-L
    group=doc.getObject(n+'_LongStringModule')
    # Retain each arm-side bridge and its support, removing its old anchor pin.
    for suffix in ['PinBlock','Pin','Afterlength']:
        doc.removeObject(n+'_Anchor'+suffix)
    for obj in list(group.Group):
        if obj.Name.startswith(n+'_Tuner'):doc.removeObject(obj.Name)
    for obj in group.Group:
        if obj.Name.startswith(n+'_Anchor'):obj.Label=n+' third bridge — '+obj.Name.split('_Anchor')[1]
    st.Label=n+' speaking segment — %.2f mm'%L
    extra=add(n+'_BackStringSegment',sc(.18,bridge_x+22,V(-22,h,-34)),silver,group)
    extra.Label=n+' string behind third bridge'
    for tag,x in [('Anchor',-22),('Tuner',320)]:
        # Individual saddle notches on a single shared structural end frame.
        tri=Part.makePolygon([V(x-2,h-2,-36),V(x,h,-36),V(x+2,h-2,-36),V(x-2,h-2,-36)])
        add(n+'_Shared'+tag+'Saddle',Part.Face(tri).extrude(V(0,0,4)),silver,doc.CommonStringEnds)
        add(n+'_Shared'+tag+'SaddleSeat',sb(8,3,12,x-4,h-5,-44),brass,doc.CommonStringEnds)
        # Pegs point backwards, allowing ten-millimetre vertical spacing.
        pin=sc(2,30,V(x,h-5,-72),V(0,0,1)).fuse(sb(7,4,3,x-3.5,h-7,-75))
        pin=pin.cut(sc(.5,6,V(x-3,h-5,-47)))
        add(n+'_Shared'+tag+'Peg',pin,silver,doc.CommonStringEnds)
        add(n+'_Shared'+tag+'Tail',rod(V(x,h,-34),V(x,h-5,-47)),silver,doc.CommonStringEnds)
    st.addProperty('App::PropertyLength','TotalStraightSpan','Geometry');st.TotalStraightSpan=342
    st.addProperty('App::PropertyString','BridgeArrangement','Geometry');st.BridgeArrangement='Common end supports at X -22 and 320; intermediate bridge sets speaking length'
    doc.recompute();print(n,'equal end-to-end span: 342 mm; speaking length:',L)
def sixth_voice():
    n='A';s=120;R=doc.C_LongArmRotor.ContactRadius.Value*.6;h=doc.G_LongSpeakingString.VerticalY.Value-10
    for suffix,template in [('_Driver','C_Driver'),('_Output','F_Output')]:
        group=doc.addObject('App::Part',n+suffix)
        lowz=-131 if suffix=='_Driver' else -99
        group.Placement=App.Placement(V(s,-83,lowz),App.Rotation(V(1,0,0),90))
        group.setExpression('Placement.Rotation.Angle','Motion.InputAngle + 90 deg' if suffix=='_Driver' else '-Motion.InputAngle * 5 / 3 + 90 deg')
        src=doc.getObject(template)
        gear=[o for o in src.Group if 'Gear' in o.Name][0]
        add(n+('_DrivingGear' if suffix=='_Driver' else '_DrivenGear'),gear.Shape.copy(),brass,group)
    doc.A_Output.addProperty('App::PropertyFloat','SpeedRatio','Timing');doc.A_Output.SpeedRatio=5/3
    add('A_LowOutputShaft',sc(3,23.5,V(-12,0,0)),silver,doc.A_Output)
    add('A_LowerTimingPulley',doc.G_LowerTimingPulley.Shape.copy(),brass,doc.A_Output)
    rotor=doc.addObject('App::Part','A_LongArmRotor');rotor.addProperty('App::PropertyLength','ContactRadius','Geometry');rotor.ContactRadius=R
    rotor.Placement=App.Placement(V(s,h-R,-34),App.Rotation(V(1,0,0),-90));rotor.setExpression('Placement.Rotation.Angle','-Motion.InputAngle * 5 / 3 - 90 deg')
    add('A_RaisedArmShaft',sc(3,22,V(-6.5,0,0)),silver,rotor)
    add('A_UpperTimingPulley',doc.G_UpperTimingPulley.Shape.copy(),brass,rotor)
    arm=sb(3,4,R-.5,12,-2,0).fuse(sc(6,3,V(12,0,0))).cut(sc(3.05,5,V(11,0,0)))
    add('A_ExtendedArm',arm,(.25,.69,.69),rotor);add('A_ExtendedPick',sb(3.3,.6,1.5,15,-.3,R-1),(.92,.88,.73),rotor)
    group=doc.addObject('App::DocumentObjectGroup','A_LongStringModule');doc.VerticalLongStrings.addObject(group)
    for src in doc.G_LongStringModule.Group:
        if not src.Name.startswith('G_Anchor'):continue
        shape=src.Shape.copy();shape.translate(V(22,-10,0))
        add('A'+src.Name[1:],shape,src.ViewObject.ShapeColor,group)
    doc.A_AnchorFoot.Shape=sb(8,3,10,117,-109,-107)
    doc.A_AnchorTower.Shape=sb(6,h+105,6,118,-109,-105)
    st=add('A_LongSpeakingString',sc(.18,198,V(122,h,-34)),silver,group)
    for prop,value in [('VerticalY',h),('SpeakingLength',198),('ArmRadius',R)]:st.addProperty('App::PropertyLength',prop,'Geometry');setattr(st,prop,value)
    doc.CommonInputShaft_D6.Shape=sc(3,164,V(-22,-83,-131))
    for name in ['LowInputStand1','LowInputBearing1']:
        obj=doc.getObject(name);shape=obj.Shape.copy();shape.translate(V(24,0,0));obj.Shape=shape
    doc.LowGearboxTray.Shape=sb(159,3,86,-20,-109,-154).fuse(sb(159,6,3,-20,-106,-154)).fuse(sb(159,6,3,-20,-106,-71))
    for j,x in enumerate([109,114.5]):
        stand=sb(4,30,18,x,-109,-108).cut(sc(6.05,6,V(x-1,-83,-99)))
        bush=sc(6,4,V(x,-83,-99)).cut(sc(3.1,6,V(x-1,-83,-99)))
        add('A_LowerBearingStand'+str(j),stand,(.18,.23,.28),doc.Structure);add('A_LowerBearing'+str(j),bush,silver,doc.Structure)
    doc.recompute();print('Sixth voice A added, 5:3 ratio')
def relocate_arms():
    # Put the string plane tangent to each arm's circle, clearing all back-string segments.
    # Shift string bank forward 14 mm so the largest circular sweep stays inside the base depth.
    for n in 'CDEFGA':
        group=doc.getObject(n+'_LongStringModule')
        for obj in group.Group:
            shape=obj.Shape.copy();shape.translate(V(0,0,14));obj.Shape=shape
    for obj in doc.CommonStringEnds.Group:
        shape=obj.Shape.copy();shape.translate(V(0,0,14));obj.Shape=shape
    report=[]
    for i,n in enumerate('CDEFGA'):
        s=24*i;rotor=doc.getObject(n+'_LongArmRotor');R=rotor.ContactRadius.Value;h=doc.getObject(n+'_LongSpeakingString').VerticalY.Value;z=-20-R
        rotor.setExpression('Placement.Rotation.Angle',None)
        rotor.Placement=App.Placement(V(s,h,z),App.Rotation(V(1,0,0),0))
        ratio=['1','9 / 8','5 / 4','4 / 3','3 / 2','5 / 3'][i]
        rotor.setExpression('Placement.Rotation.Angle','-Motion.InputAngle * '+ratio)
        for j,offset in enumerate([-5.5,0]):
            x=s+offset
            stand=sb(4,h+113,18,x,-109,z-9).cut(sc(6.05,6,V(x-1,h,z)))
            bush=sc(6,4,V(x,h,z)).cut(sc(3.1,6,V(x-1,h,z)))
            for suffix,shape in [('BearingStand',stand),('Bearing',bush)]:
                name=n+'_Raised'+suffix+str(j);obj=doc.getObject(name)
                if obj:obj.Shape=shape
                else:add(name,shape,(.18,.23,.28) if suffix=='BearingStand' else silver,doc.Structure)
        low=doc.getObject(n+'_Output').Placement.Base;A=V(s+5.25,low.y,low.z);B=V(s+5.25,h,z)
        d=B-A;d.normalize();p=V(0,-d.z,d.y)
        def wire(r):return Part.Wire([Part.makeLine(A+p*r,B+p*r),Part.Arc(B+p*r,B+d*r,B-p*r).toShape(),Part.makeLine(B-p*r,A-p*r),Part.Arc(A-p*r,A-d*r,A+p*r).toShape()])
        belt=Part.Face(wire(8.8)).cut(Part.Face(wire(8.1))).extrude(V(6,0,0))
        obj=doc.getObject(n+'_TimingBeltEnvelope')
        if obj:obj.Shape=belt
        else:add(n+'_TimingBeltEnvelope',belt,(.12,.13,.15),doc.RaisedArmTransmission)
        report.append({'note':n,'axis_y':h,'axis_z':z,'radius':R,'speaking_length':doc.getObject(n+'_LongSpeakingString').SpeakingLength.Value})
    # Extend common bridge rails down to cover the sixth string as well.
    for tag,x in [('Anchor',-22),('Tuner',320)]:
        doc.getObject('Shared'+tag+'SaddleRail').Shape=sb(10,70,8,x-5,-28,-29)
    doc.recompute();return report

def check_soundbox(rows):
    rotating=set()
    for n in 'CDEFGA':
        for suffix in ['_Driver','_Output','_LongArmRotor']:
            rotating.update(o.Name for o in doc.getObject(n+suffix).Group if o.TypeId=='Part::Feature')
    fixed=[o for o in doc.Objects if o.TypeId=='Part::Feature' and o.Name not in rotating]
    clashes=[];contacts=[]
    for i,row in enumerate(rows):
        n=row['note'];s=24*i;R=row['radius'];h=row['axis_y'];z=row['axis_z']
        arm=sc(math.hypot(R-.5,2),3,V(s+12,h,z)).cut(sc(3.05,5,V(s+11,h,z)))
        pick=sc(math.hypot(R+.5,.3),3.3,V(s+15,h,z)).cut(sc(R-1,5.3,V(s+14,h,z)))
        for obj in fixed:
            for tag,envelope in [('arm',arm),('pick',pick)]:
                if envelope.BoundBox.intersect(obj.Shape.BoundBox) and envelope.common(obj.Shape).Volume>1e-5:
                    item={'voice':n,'part':obj.Name,'sweep':tag}
                    if tag=='pick' and obj.Name==n+'_LongSpeakingString':contacts.append(item)
                    else:clashes.append(item)
    invalid=[o.Name for o in doc.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())]
    print('Sweep clashes:',clashes,'Intended string contacts:',len(contacts),'Invalid shapes:',invalid)
    with open(OUT+'/soundbox_geometry.json','w') as f:json.dump({'strings':6,'equal_end_span_mm':342,'ratios':[1,8/9,4/5,3/4,2/3,3/5],'geometry':rows,'sweep_clashes':clashes,'contacts':contacts,'invalid_shapes':invalid,'scope':'Geometric concept; string tension, structural sizing and acoustic performance require engineering validation.'},f,indent=2)
    return clashes
