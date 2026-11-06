import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App, FreeCADGui as Gui, Part, math, json
from FreeCAD import Vector as V
doc=App.ActiveDocument
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
bank_created=[];bank_fixed=[];bank_rows=[]
def bank_box(dx,dy,dz,x,y,z):return Part.makeBox(dx,dy,dz,V(x,y,z))
def bank_cyl(r,h,p,axis=V(1,0,0)):return Part.makeCylinder(r,h,p,axis)
def bank_rod(p,q,r=.18):
    v=q-p;return bank_cyl(r,v.Length,p,v)
def bank_part(name,shape,color,parent,fixed=False):
    obj=doc.addObject('Part::Feature',name);obj.Shape=shape;obj.ViewObject.ShapeColor=color;parent.addObject(obj)
    bank_created.append(obj)
    if fixed:bank_fixed.append(obj)
    return obj
def remove_bank_group(group):
    for obj in list(group.Group):
        if obj.TypeId=='App::DocumentObjectGroup':remove_bank_group(obj)
        else:doc.removeObject(obj.Name)
    doc.removeObject(group.Name)
def prepare_vertical_bank():
    doc.Motion.Time=0;doc.recompute()
    if doc.getObject('AxialStringBank'):remove_bank_group(doc.AxialStringBank)
    if doc.getObject('VerticalLongStrings'):remove_bank_group(doc.VerticalLongStrings)
    # Rebuild fixed supports in X / Y-up / Z-depth coordinates.
    for obj in list(doc.Structure.Group):
        if obj.Name not in ['Baseplate_310x170x6','CommonInputShaft_D6']:doc.removeObject(obj.Name)
    base=bank_box(370,6,200,-30,-115,-155)
    for xx in [-20,330]:
        for zz in [-145,35]:base=base.cut(bank_cyl(2.75,8,V(xx,-116,zz),V(0,1,0)))
    doc.Baseplate_310x170x6.Shape=base;doc.Baseplate_310x170x6.Label='Existing base — X 370 x Z 200 mm; Y vertical'
    doc.CommonInputShaft_D6.Shape=bank_cyl(3,294,V(-22,0,0))
    for i,x in enumerate([-17,257]):
        stand=bank_box(8,113,18,x,-109,-9).cut(bank_cyl(6.05,10,V(x-1,0,0)))
        bank_part('MainBearingStand'+str(i),stand,(.18,.23,.28),doc.Structure,True)
        bush=bank_cyl(6,6,V(x+1,0,0)).cut(bank_cyl(3.1,8,V(x,0,0)))
        bank_part('MainBearing'+str(i),bush,(.74,.78,.82),doc.Structure,True)
    group=doc.addObject('App::DocumentObjectGroup','VerticalLongStrings')
    group.Label='Long strings parallel to X, stacked in Y'
    doc.recompute();print('Existing base retained; Y is vertical')
def build_long_voice(i):
    n='CDEFG'[i];a=[40,36,40,32,36][i];b=[40,32,32,24,24][i];inv=b/a
    station=24*i;axis_z=-(a+b)/2;R=30*inv;L=330*inv;string_z=-34.0
    height=math.sqrt(R*R-(string_z-axis_z)**2)
    left=[-10,26,48,72,96][i];right=left+L;pluck=station+16.65
    dr=doc.getObject(n+'_Driver');ou=doc.getObject(n+'_Output')
    dr.setExpression('Placement.Rotation.Angle',None);ou.setExpression('Placement.Rotation.Angle',None)
    dr.Placement=App.Placement(V(station,0,0),App.Rotation(V(1,0,0),-90))
    ou.Placement=App.Placement(V(station,0,axis_z),App.Rotation(V(1,0,0),-90))
    dr.setExpression('Placement.Rotation.Angle','Motion.InputAngle - 90 deg')
    ou.setExpression('Placement.Rotation.Angle','-Motion.InputAngle * %d / %d - 90 deg'%(a,b))
    for obj in list(ou.Group):
        if obj.TypeId=='Part::Feature' and obj.Name!=n+'_DrivenGear':doc.removeObject(obj.Name)
    ou.EffectiveArmRadius=R;ou.SpeakingLength=L;ou.StringOffset=abs(string_z-axis_z)
    silver=(.74,.78,.82);brass=(.82,.64,.29);wood=(.38,.23,.12)
    color=[(.75,.30,.28),(.82,.55,.22),(.35,.65,.45),(.28,.53,.76),(.59,.38,.72)][i]
    bank_part(n+'_BankOutputShaft',bank_cyl(3,22,V(-6.5,0,0)),silver,ou)
    arm=bank_box(3,4,R-.5,12,-2,0).fuse(bank_cyl(6,3,V(12,0,0))).cut(bank_cyl(3.05,5,V(11,0,0)))
    blade=bank_box(3.3,.6,1.5,15,-.3,R-1)
    phase=math.degrees(math.asin((string_z-axis_z)/R))
    arm.rotate(V(),V(1,0,0),phase);blade.rotate(V(),V(1,0,0),phase)
    bank_part(n+'_BankArm',arm,color,ou)
    bank_part(n+'_BankPlectrum',blade,(.92,.88,.73),ou)
    for j,bx in enumerate([station-5.5,station+6]):
        stand=bank_box(4,113,18,bx,-109,axis_z-9).cut(bank_cyl(6.05,6,V(bx-1,0,axis_z)))
        bush=bank_cyl(6,4,V(bx,0,axis_z)).cut(bank_cyl(3.1,6,V(bx-1,0,axis_z)))
        bank_part(n+'_BankBearingStand'+str(j),stand,(.18,.23,.28),doc.Structure,True)
        bank_part(n+'_BankBearing'+str(j),bush,silver,doc.Structure,True)
    group=doc.addObject('App::DocumentObjectGroup',n+'_LongStringModule');doc.VerticalLongStrings.addObject(group)
    group.Label='%s — %.2f mm speaking length'%(n,L)
    string=bank_part(n+'_LongSpeakingString',bank_rod(V(left,height,string_z),V(right,height,string_z)),silver,group)
    for prop,val in [('SpeakingLength',L),('ArmRadius',R),('VerticalY',height)]:
        string.addProperty('App::PropertyLength',prop,'Geometry');setattr(string,prop,val)
    for sign,bx in [(-1,left),(1,right)]:
        tag='Anchor' if sign<0 else 'Tuner'
        # Later short strings begin beyond the preceding arm: compact side anchors.
        after=12 if sign>0 or i==0 else 1
        px=bx+sign*after;pz=string_z-16-10*i;tz=pz-12
        lo=min(bx,px)-(4 if sign<0 and i>0 else 5);hi=max(bx,px)+5
        fw=8 if sign<0 and i>0 else 10
        foot=bank_box(fw,3,10,px-fw/2,-109,tz-5)
        tower=bank_box(6,height+105,6,px-3,-109,tz-3)
        beam=bank_box(hi-lo,4,string_z+4-(tz-3),lo,height-6,tz-3)
        bank_part(n+'_'+tag+'Foot',foot,brass,group,True)
        bank_part(n+'_'+tag+'Tower',tower,wood,group,True)
        bank_part(n+'_'+tag+'Beam',beam,wood,group,True)
        carrier=bank_box(8,3,6,bx-4,height-5,string_z-3)
        for zz in [string_z-2.5,string_z+2.5]:carrier=carrier.cut(bank_cyl(1.1,4,V(bx,height-5,zz),V(0,1,0)))
        bank_part(n+'_'+tag+'SaddleCarrier',carrier,brass,group,True)
        tri=Part.makePolygon([V(bx-2,height-2,string_z-2),V(bx,height,string_z-2),V(bx+2,height-2,string_z-2),V(bx-2,height-2,string_z-2)])
        bank_part(n+'_'+tag+'Saddle',Part.Face(tri).extrude(V(0,0,4)),silver,group,True)
        for j,zz in enumerate([string_z-2.5,string_z+2.5]):
            screw=bank_cyl(1,3,V(bx,height-5,zz),V(0,1,0)).fuse(bank_cyl(1.7,1,V(bx,height-3,zz),V(0,1,0)))
            bank_part(n+'_'+tag+'Screw'+str(j),screw,silver,group,True)
        block=bank_box(8,14,8,px-4,height-21,pz-4)
        if sign>0:
            block=block.cut(Part.makeCone(1.8,1.95,14,V(px,height-21,pz),V(0,1,0)))
            pin=Part.makeCone(1.85,2,14,V(px,height-21,pz),V(0,1,0)).fuse(bank_cyl(2,4,V(px,height-7,pz),V(0,1,0)))
            pin=pin.fuse(bank_box(4,3,4,px-2,height-3,pz-2))
        else:
            block=block.cut(bank_cyl(2.05,14,V(px,height-21,pz),V(0,1,0)))
            pin=bank_cyl(2,18,V(px,height-21,pz),V(0,1,0)).fuse(bank_cyl(3,2,V(px,height-3,pz),V(0,1,0)))
        pin=pin.cut(bank_cyl(.5,6,V(px-3,height-5,pz)))
        bank_part(n+'_'+tag+'PinBlock',block,wood,group,True)
        bank_part(n+'_'+tag+'Pin',pin,silver,group,True)
        bank_part(n+'_'+tag+'Afterlength',bank_rod(V(bx,height,string_z),V(px,height-5,pz)),silver,group)
    doc.recompute()
    invalid=[o.Name for o in bank_created if o.Shape.isNull() or not o.Shape.isValid()]
    assert not invalid,invalid
    bank_rows.append({'note':n,'speaking_mm':L,'ratio':inv,'arm_radius_mm':R,'arm_station_x_mm':pluck,'left_saddle_x_mm':left,'right_saddle_x_mm':right,'string_vertical_y_mm':height,'common_string_z_mm':string_z})
    print(n,'long string:',round(L,3),'mm; arm contact inside span:',left<pluck<right)
def verify_long_bank():
    hardware_collisions=[];string_collisions=[]
    for i,n in enumerate('CDEFG'):
        s=24*i;R=30*[1,8/9,4/5,3/4,2/3][i];az=-([40,36,40,32,36][i]+[40,32,32,24,24][i])/2
        arm=bank_cyl(max(6,math.hypot(R-.5,2)),3,V(s+12,0,az)).cut(bank_cyl(3.05,5,V(s+11,0,az)))
        blade=bank_cyl(math.hypot(R+.5,.3),3.3,V(s+15,0,az)).cut(bank_cyl(R-1,5.3,V(s+14,0,az)))
        for obj in bank_fixed+[doc.CommonInputShaft_D6,doc.Baseplate_310x170x6]:
            for label,envelope in [('arm',arm),('blade',blade)]:
                if envelope.BoundBox.intersect(obj.Shape.BoundBox) and envelope.common(obj.Shape).Volume>1e-5:
                    hardware_collisions.append({'voice':n,'part':obj.Name,'sweep':label})
        for m in 'CDEFG':
            if m==n:continue
            obj=doc.getObject(m+'_LongSpeakingString')
            for label,envelope in [('arm',arm),('blade',blade)]:
                if envelope.BoundBox.intersect(obj.Shape.BoundBox) and envelope.common(obj.Shape).Volume>1e-5:
                    string_collisions.append({'arm':n,'other_string':m,'sweep':label})
    print('Hardware sweep clashes:',hardware_collisions)
    print('Other-string sweep clashes:',string_collisions)
    doc.Label="L'Harpe d'Amour — long strings, Y vertical"
    doc.Motion.Status='Long strings parallel to X in one Z plane, stacked in Y; prescribed rotation. C span 330 mm. Hardware fits, string loads and absolute acoustic tuning remain conceptual.'
    Gui.Selection.clearSelection();Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll()
    doc.recompute();doc.save()
    with open(OUT+'/long_string_geometry.json','w') as f:json.dump({'coordinates':'X longitudinal axle / Y vertical / Z depth','base_x_limits_mm':[-30,340],'geometry':bank_rows,'full_turn_hardware_clashes':hardware_collisions,'full_turn_other_string_clashes':string_collisions},f,indent=2)
    return hardware_collisions,string_collisions
