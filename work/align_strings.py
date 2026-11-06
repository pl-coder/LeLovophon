import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App, FreeCADGui as Gui, Part, math, json
from FreeCAD import Vector as V
doc=App.ActiveDocument
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
align_rows=[]
def acyl(r,h,p):return Part.makeCylinder(r,h,p,V(1,0,0))
def abox(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def capsule(a,b,r):
    d=b-a;d.normalize();p=V(0,-d.z,d.y)
    return Part.Wire([Part.makeLine(a+p*r,b+p*r),Part.Arc(b+p*r,b+d*r,b-p*r).toShape(),Part.makeLine(b-p*r,a-p*r),Part.Arc(a-p*r,a-d*r,a+p*r).toShape()])
def align_voice(i):
    n='CDEFG'[i];s=24*i;st=doc.getObject(n+'_LongSpeakingString');oldh=st.VerticalY.Value
    h=doc.C_LongSpeakingString.VerticalY.Value-10*i;L=st.SpeakingLength.Value;left=320-L;right=320
    bounds=st.Shape.BoundBox;oldleft=bounds.XMin;oldright=bounds.XMax
    for tag,dx in [('Anchor',left-oldleft),('Tuner',right-oldright)]:
        for obj in doc.getObject(n+'_LongStringModule').Group:
            if obj.Name.startswith(n+'_'+tag):
                shape=obj.Shape.copy();shape.translate(V(dx,h-oldh,0));obj.Shape=shape
        # Extend supports from the unchanged base, rather than moving their feet vertically.
        after=12 if tag=='Tuner' or i==0 else 1
        px=(right+after) if tag=='Tuner' else (left-after)
        tz=-34-16-10*i-12;fw=8 if tag=='Anchor' and i>0 else 10
        doc.getObject(n+'_'+tag+'Foot').Shape=abox(fw,3,10,px-fw/2,-109,tz-5)
        doc.getObject(n+'_'+tag+'Tower').Shape=abox(6,h+105,6,px-3,-109,tz-3)
    st.Shape=acyl(.18,L,V(left,h,-34));st.VerticalY=h
    rotor=doc.getObject(n+'_LongArmRotor');R=rotor.ContactRadius.Value;yy=h-R
    placement=rotor.Placement;placement.Base=V(s,yy,-34);rotor.Placement=placement
    for j,offset in enumerate([-5.5,0]):
        x=s+offset
        doc.getObject(n+'_RaisedBearingStand'+str(j)).Shape=abox(4,yy+113,18,x,-109,-43).cut(acyl(6.05,6,V(x-1,yy,-34)))
        doc.getObject(n+'_RaisedBearing'+str(j)).Shape=acyl(6,4,V(x,yy,-34)).cut(acyl(3.1,6,V(x-1,yy,-34)))
    low=doc.getObject(n+'_Output').Placement.Base
    A=V(s+5.25,low.y,low.z);B=V(s+5.25,yy,-34)
    doc.getObject(n+'_TimingBeltEnvelope').Shape=Part.Face(capsule(A,B,8.8)).cut(Part.Face(capsule(A,B,8.1))).extrude(V(6,0,0))
    align_rows.append({'note':n,'string_y':h,'string_z':-34,'left_x':left,'right_x':right,'length_mm':L,'arm_radius_mm':R,'arm_axis_y':yy,'pick_x':s+16.65})
    doc.recompute();print(n,'string Y',round(h,2),'tuner X',right,'arm axis Y',round(yy,2))
def verify_alignment():
    rotating=set()
    for n in 'CDEFG':
        for suffix in ['_Driver','_Output','_LongArmRotor']:
            rotating.update(o.Name for o in doc.getObject(n+suffix).Group if o.TypeId=='Part::Feature')
    stationary=[o for o in doc.Objects if o.TypeId=='Part::Feature' and o.Name not in rotating]
    clashes=[];contacts=[]
    for i,row in enumerate(align_rows):
        n=row['note'];R=row['arm_radius_mm'];s=24*i;yy=row['arm_axis_y']
        arm=acyl(math.hypot(R-.5,2),3,V(s+12,yy,-34)).cut(acyl(3.05,5,V(s+11,yy,-34)))
        pick=acyl(math.hypot(R+.5,.3),3.3,V(s+15,yy,-34)).cut(acyl(R-1,5.3,V(s+14,yy,-34)))
        for obj in stationary:
            for label,envelope in [('arm',arm),('pick',pick)]:
                if envelope.BoundBox.intersect(obj.Shape.BoundBox) and envelope.common(obj.Shape).Volume>1e-5:
                    item={'voice':n,'part':obj.Name,'sweep':label}
                    if obj.Name==n+'_LongSpeakingString' and label=='pick':contacts.append(item)
                    else:clashes.append(item)
    invalid=[o.Name for o in doc.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())]
    print('Unwanted sweep contacts:',clashes,'Intended contacts:',len(contacts),'Invalid shapes:',invalid)
    assert not clashes and not invalid and len(contacts)==5
    assert all(abs(r['right_x']-320)<1e-7 and r['left_x']<r['pick_x']<r['right_x'] for r in align_rows)
    doc.Label="L'Harpe d'Amour — aligned strings"
    doc.VerticalLongStrings.Label='Strings in one vertical plane — 10 mm spacing, aligned tuning bridges'
    doc.recompute();doc.save()
    with open(OUT+'/aligned_string_geometry.json','w') as f:json.dump({'vertical_axis':'Y','spacing_mm':10,'geometry':align_rows,'unwanted_full_turn_contacts':clashes,'intended_pick_contacts':contacts},f,indent=2)
