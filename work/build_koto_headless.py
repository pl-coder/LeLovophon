import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App, FreeCADGui as Gui, Part, math, json, time
from FreeCAD import Vector as V
from PySide import QtCore
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
# Work from the saved belt-drive checkpoint without closing any existing document.
doc=App.openDocument(OUT+'/Harpe_d_Amour_Koto_Pendulums.FCStd')
App.setActiveDocument(doc.Name)
notes='CDEFGA';ratios=[1,9/8,5/4,4/3,3/2,5/3]
wood=(.46,.29,.15);brass=(.82,.64,.29);silver=(.74,.78,.82);dark=(.18,.23,.28)
def bx(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def cy(r,h,p):return Part.makeCylinder(r,h,p,V(1,0,0))
def rod(p,q,r=.18):
    d=q-p;return Part.makeCylinder(r,d.Length,p,d)
def obj(name,shape,col,group):
    o=doc.addObject('Part::Feature',name);o.Shape=shape;group.addObject(o);return o
def remove_group(g):
    for o in list(g.Group):
        if o.TypeId in ['App::DocumentObjectGroup','App::Part']:remove_group(o)
        else:doc.removeObject(o.Name)
    doc.removeObject(g.Name)
def triangle(points,depth):return Part.Face(Part.makePolygon(points+[points[0]])).extrude(V(0,0,depth))
def prepare_koto():
    doc.Motion.Time=0;doc.recompute()
    remove_group(doc.VerticalLongStrings);remove_group(doc.CommonStringEnds)
    for n in notes:
        for o in list(doc.Structure.Group):
            if o.Name.startswith(n+'_RaisedBearing'):doc.removeObject(o.Name)
        doc.removeObject(n+'_TimingBeltEnvelope')
        doc.removeObject(n+'_UpperTimingPulley');doc.removeObject(n+'_LowerTimingPulley')
    bank=doc.addObject('App::DocumentObjectGroup','FlatKotoStrings');bank.Label='Six equal strings above the soundboard, ten millimetre spacing'
    ends=doc.addObject('App::DocumentObjectGroup','KotoEndSupports');ends.Label='Two shared load-bearing end blocks'
    for label,x in [('Anchor',-22),('Tuner',320)]:
        block=bx(16,34,76,x-8,-109,-93)
        obj('Koto'+label+'Block',block,wood,ends)
        obj('Koto'+label+'SaddleRail',bx(6,2,70,x-3,-75,-90),brass,ends)
    g=doc.addObject('App::DocumentObjectGroup','PendulumLinkages');g.Label='Six identical cranks and rockers, adjustable connecting rods'
    print('Flat string bed and two end supports prepared')
pendulum_rows=[]
def build_koto_voice(i):
    n=notes[i];s=24*i;z=-80+10*i;L=330/ratios[i];left=320-L;R=doc.getObject(n+'_LongArmRotor').ContactRadius.Value;uy=-73+R
    g=doc.addObject('App::DocumentObjectGroup',n+'_KotoStringModule');doc.FlatKotoStrings.addObject(g)
    st=obj(n+'_KotoSpeakingString',rod(V(left,-73,z),V(320,-73,z)),silver,g)
    obj(n+'_KotoBackString',rod(V(-22,-73,z),V(left,-73,z)),silver,g)
    for prop,value in [('SpeakingLength',L),('EqualEndSpan',342)]:st.addProperty('App::PropertyLength',prop,'Geometry');setattr(st,prop,value)
    # Repeated flat bridge blanks with an acoustic window; crown/notch detail remains provisional.
    bridge=triangle([V(left-6,-109,z-3),V(left,-73,z-3),V(left+6,-109,z-3)],6)
    window=triangle([V(left-2.8,-105,z-4),V(left,-87,z-4),V(left+2.8,-105,z-4)],8)
    obj(n+'_KotoThirdBridge',bridge.cut(window),wood,g)
    for tag,x in [('Anchor',-22),('Tuner',320)]:
        obj(n+'_Koto'+tag+'Saddle',cy(.7,6,V(x-3,-73,z)),silver,doc.KotoEndSupports)
        pin=Part.makeCylinder(1.8,14,V(x,-91,z),V(0,1,0)).fuse(bx(6,2,4,x-3,-79,z-2))
        obj(n+'_Koto'+tag+'Pin',pin,silver,doc.KotoEndSupports)
        obj(n+'_Koto'+tag+'Tail',rod(V(x,-73,z),V(x,-79,z)),silver,doc.KotoEndSupports)
    rotor=doc.getObject(n+'_LongArmRotor');rotor.setExpression('Placement.Rotation.Angle',None)
    rotor.Placement=App.Placement(V(s,uy,z),App.Rotation(V(1,0,0),90));rotor.Label=n+' pendulum pick — %.2f mm'%R
    # Bearings are carried by brackets above the strings, supported from the rear rail.
    for j,offset in enumerate([-5.5,0]):
        x=s+offset
        post=bx(4,uy+109,8,x,-109,-154)
        beam=bx(4,12,z+160,x,uy-6,-154).cut(cy(6.05,6,V(x-1,uy,z)))
        obj(n+'_PendulumBracket'+str(j),post.fuse(beam),dark,doc.Structure)
        obj(n+'_PendulumBearing'+str(j),cy(6,4,V(x,uy,z)).cut(cy(3.1,6,V(x-1,uy,z))),silver,doc.Structure)
    low=doc.getObject(n+'_Output');low.Label=n+' independent ratio pulley and crank'
    # Repeated five-millimetre crank throw and fourteen-millimetre rocker.
    crank=cy(8,3,V(5.25,0,0)).cut(cy(5.05,5,V(4.25,0,0))).fuse(cy(1.5,3,V(8.25,0,5)))
    obj(n+'_Crank',crank,brass,low)
    U=V(s,uy,z);C0=V(s,-59,-116);D=(U-C0).Length
    row={'note':n,'station':s,'pivot_y':uy,'pivot_z':z,'radius':R,'ground':D,'rod_length':D,'rocker':14,'crank':5,'ratio':ratios[i],'speaking_length':L}
    vals=[solve_beta(row,math.radians(j))[0] for j in range(360)]
    ref=vals[0];vals=[ref+math.atan2(math.sin(v-ref),math.cos(v-ref)) for v in vals]
    row['beta_mid']=(max(vals)+min(vals))/2;row['swing_half_angle_deg']=math.degrees((max(vals)-min(vals))/2)
    rocker=doc.addObject('App::Part',n+'_Rocker');doc.PendulumLinkages.addObject(rocker)
    plate=bx(3,4,14,5.25,-2,0).fuse(cy(6,3,V(5.25,0,0))).fuse(cy(3,3,V(5.25,0,14))).cut(cy(3.05,5,V(4.25,0,0)))
    plate=plate.fuse(cy(1.5,3,V(8.25,0,14)))
    obj(n+'_RockerPlate',plate,brass,rocker)
    link=bx(2.5,4,D,0,-2,0).fuse(cy(3,2.5,V())).fuse(cy(3,2.5,V(0,0,D)))
    link=link.cut(cy(1.55,4.5,V(-1,0,0))).cut(cy(1.55,4.5,V(-1,0,D)))
    obj(n+'_ConnectingRod',link,silver,doc.PendulumLinkages)
    pendulum_rows.append(row);doc.recompute();print(n,'flat string Z',z,'swing +/-',round(row['swing_half_angle_deg'],2),'degrees')
def solve_beta(row,theta):
    U=V(0,row['pivot_y'],row['pivot_z']);C=V(0,-59-5*math.sin(theta),-116+5*math.cos(theta))
    v=C-U;q=v.Length;v.normalize();a=(14*14-row['rod_length']**2+q*q)/(2*q);h2=196-a*a
    assert h2>0,'Linkage toggle or unreachable position'
    perp=V(0,-v.z,v.y);B=U+v*a+perp*math.sqrt(h2)
    beta=math.atan2(-(B.y-U.y),B.z-U.z)
    return beta,C,B

def update_pendulums(t):
    doc.Motion.Time=t
    for row in pendulum_rows:
        n=row['note'];theta=-math.radians(18*t*row['ratio']);beta,C,B=solve_beta(row,theta)
        delta=math.atan2(math.sin(beta-row['beta_mid']),math.cos(beta-row['beta_mid']))
        rotor=doc.getObject(n+'_LongArmRotor');rotor.Placement=App.Placement(V(row['station'],row['pivot_y'],row['pivot_z']),App.Rotation(V(1,0,0),90+math.degrees(delta)))
        rocker=doc.getObject(n+'_Rocker');rocker.Placement=App.Placement(V(row['station'],row['pivot_y'],row['pivot_z']),App.Rotation(V(1,0,0),math.degrees(beta)))
        vec=B-C;angle=math.degrees(math.atan2(-vec.y,vec.z))
        doc.getObject(n+'_ConnectingRod').Placement=App.Placement(V(row['station']+8.75,C.y,C.z),App.Rotation(V(1,0,0),angle))
    doc.recompute()

# Recover the parameters for the first two saved modules.
for i,n in enumerate(notes[:2]):
    s=24*i;z=-80+10*i;R=doc.getObject(n+'_LongArmRotor').ContactRadius.Value;uy=-73+R;D=(V(0,uy,z)-V(0,-59,-116)).Length
    row={'note':n,'station':s,'pivot_y':uy,'pivot_z':z,'radius':R,'ground':D,'rod_length':D,'rocker':14,'crank':5,'ratio':ratios[i],'speaking_length':330/ratios[i]}
    vals=[solve_beta(row,math.radians(j))[0] for j in range(360)];ref=vals[0];vals=[ref+math.atan2(math.sin(v-ref),math.cos(v-ref)) for v in vals]
    row['beta_mid']=(max(vals)+min(vals))/2;row['swing_half_angle_deg']=math.degrees((max(vals)-min(vals))/2);pendulum_rows.append(row)
    for j,offset in enumerate([-5.5,0]):
        x=s+offset;post=bx(4,uy+109,8,x,-109,-154);beam=bx(4,12,z+160,x,uy-6,-154).cut(cy(6.05,6,V(x-1,uy,z)))
        doc.getObject(n+'_PendulumBracket'+str(j)).Shape=post.fuse(beam)
for i in range(2,6):
    build_koto_voice(i);doc.save()
update_pendulums(0)
doc.Label="L'Harpe d'Amour — koto strings and pendulum picks"
doc.Motion.Status='Crank-rocker kinematic concept. Common clockwork input interface; spring/escapement module not yet selected. Belt tooth form, loads, joints, bridge downforce and safety validation remain to be completed.'
if not hasattr(doc.Motion,'LinkageGeometry'):doc.Motion.addProperty('App::PropertyString','LinkageGeometry','Design')
doc.Motion.LinkageGeometry=json.dumps(pendulum_rows)

doc.recompute();doc.save()
with open(OUT+'/koto_pendulum_geometry.json','w') as f:json.dump({'rows':pendulum_rows,'scope':doc.Motion.Status},f,indent=2)
print('Six pendulum modules saved',len(doc.Objects))
