import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App, FreeCADGui as Gui, Part, math, json, csv
from FreeCAD import Vector as V
doc=App.ActiveDocument
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
try: harpe_timer.stop()
except NameError: pass
doc.Motion.Time=0;doc.recompute()
silver=(0.74,0.78,0.82); brass=(0.82,0.64,0.29); wood=(0.38,0.23,0.12)
colors=[(0.75,0.30,0.28),(0.82,0.55,0.22),(0.35,0.65,0.45),(0.28,0.53,0.76),(0.59,0.38,0.72)]
created=[];checks=[];rows=[]
def add(name,shape,color,parent):
    obj=doc.getObject(name) or doc.addObject('Part::Feature',name)
    obj.Shape=shape;obj.ViewObject.ShapeColor=color
    parent.addObject(obj);created.append(obj);return obj
def length(obj,key,val,description):
    if key not in obj.PropertiesList:obj.addProperty('App::PropertyLength',key,'String geometry',description)
    setattr(obj,key,val)
def cyl(r,h,x,y,z):return Part.makeCylinder(r,h,V(x,y,z),V(1,0,0))
def rod(p,q,r=.18):
    d=q-p;return Part.makeCylinder(r,d.Length,p,d)
def box(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def ring(ro,ri,h,x,y,z):return cyl(ro,h,x,y,z).cut(cyl(ri,h+2,x-1,y,z))
base=Part.makeBox(310,200,6,V(-30,-45,-115))
for xx in [-20,270]:
    for yy in [-35,145]:base=base.cut(Part.makeCylinder(2.75,8,V(xx,yy,-116)))
doc.Baseplate_310x170x6.Shape=base
doc.Baseplate_310x170x6.Label='Baseplate — 310 x 200 x 6 mm'
for o in list(doc.Structure.Group):
    if 'Pedestal' in o.Name:
        bb=o.Shape.BoundBox
        add(o.Name+'_Riser',box(bb.XLength,bb.YLength,25,bb.XMin,bb.YMin,-109),wood,doc.Structure)
for i,(note,a,b) in enumerate(zip('CDEFG',[40,36,40,32,36],[40,32,32,24,24])):
    inv=b/a; L=120*inv;R=50*inv;x=55*i;y=(a+b)/2;d=.8*R;sy=y+d
    ou=doc.getObject(note+'_Output')
    length(ou,'EffectiveArmRadius',R,'Axis to plectrum contact centre; scales with inverse pitch ratio')
    length(ou,'SpeakingLength',L,'Saddle crown to saddle crown; excludes afterlength')
    length(ou,'StringOffset',d,'Transverse distance from arm axis to string')
    # Retain original parts for reversibility; hide their reference geometry.
    for suffix in ['StringReference','BridgeReference','BridgeReference001','CircularFrame_D130','FrameFoot','PlectrumReference']:
        obj=doc.getObject(note+'_'+suffix)
        if obj:obj.Visibility=False
    frame=doc.getObject(note+'_StringModule') or doc.addObject('App::DocumentObjectGroup',note+'_StringModule')
    frame.Label='%s — %.2f mm speaking length'%(note,L)
    # Each fixed ring has space for speaking span, 12 mm afterlengths and pin blocks.
    ri=math.hypot(d,L/2+17)+3;ro=ri+5
    add(note+'_SizedFrame',ring(ro,ri,4,x+34,y,0),brass,frame)
    add(note+'_SizedFrameFoot',box(10,16,109-ro+2,x+31,y-8,-109),wood,frame)
    arm=box(3,4,R-2,24,-2,0).fuse(cyl(6,3,24,0,0))
    arm=arm.cut(cyl(3.05,5,23,0,0))
    obj=doc.getObject(note+'_RotatingArm');obj.Shape=arm
    length(obj,'EffectiveRadius',R,'Contact centre radius, including plectrum')
    # Thin projecting blade: arm body stays behind string plane.
    pick=box(3.3,1,4,27,-.5,R-2)
    add(note+'_FlexiblePlectrum',pick,(.92,.88,.73),ou)
    speaking=add(note+'_SpeakingString',rod(V(x+30,sy,-L/2),V(x+30,sy,L/2)),silver,frame)
    length(speaking,'SpeakingLength',L,'Ideal distance between saddle contact points')
    for side in [-1,1]:
        tag='Lower' if side<0 else 'Upper';z=side*L/2
        chord=math.sqrt(ri**2-z**2)
        # Flat cross bridge behind the string, positively joined to both ring sides.
        rail=box(4,2*chord+8,6,x+34,y-chord-4,z-3)
        for yy in [y-chord+1,y+chord-1]:rail=rail.cut(cyl(1.35,6,x+33,yy,z))
        add(note+'_'+tag+'BridgeRail',rail,wood,frame)
        block=box(4,9,6,x+31,sy-4.5,z-3)
        block=block.cut(cyl(1.1,6,x+30,sy-3,z)).cut(cyl(1.1,6,x+30,sy+3,z))
        add(note+'_'+tag+'SaddleCarrier',block,brass,frame)
        # Polished transverse cylindrical crown; front tangent is exactly x+30.
        saddle=Part.makeCylinder(1.5,5,V(x+31.5,sy-2.5,z),V(0,1,0))
        add(note+'_'+tag+'SaddleCrown',saddle,silver,frame)
        for yy in [sy-3,sy+3]:
            add(note+'_'+tag+'BridgeScrew',cyl(1,6,x+31,yy,z).fuse(cyl(1.8,1,x+30,yy,z)),silver,frame)
        # Ring-spanning anchor / tuning block, with 12 mm free afterlength.
        pz=side*(L/2+12);pc=math.sqrt(ri**2-pz**2)
        pinrail=box(12,2*pc+8,10,x+34,y-pc-4,pz-5)
        # Zither-style tuning pin: tapered shank engages a replaceable wood block.
        pinrail=pinrail.cut(Part.makeCone(1.98,1.85,12,V(x+34,sy,pz),V(1,0,0)))
        add(note+'_'+tag+'PinBlock',pinrail,wood,frame)
        if side>0:
            pin=Part.makeCone(2.02,1.9,12,V(x+34,sy,pz),V(1,0,0)).fuse(cyl(2,7,x+27,sy,pz))
            pin=pin.fuse(box(4,4,4,x+46,sy-2,pz-2))
            pin=pin.cut(Part.makeCylinder(.5,6,V(x+30,sy,pz-3),V(0,0,1)))
            obj=add(note+'_TuningPin',pin,silver,frame)
            obj.addProperty('App::PropertyString','DesignNote','Hardware') if 'DesignNote' not in obj.PropertiesList else None
            obj.DesignNote='Zither-style tapered tuning pin concept; final pilot bore, engagement and holding torque require supplier specification and load test'
        else:
            pin=cyl(2,15,x+31,sy,pz).fuse(cyl(3.5,2,x+29,sy,pz))
            pin=pin.cut(Part.makeCylinder(.5,6,V(x+32,sy,pz-3),V(0,0,1)))
            add(note+'_AnchorPin',pin,silver,frame)
        # String bends back toward the frame after each saddle, providing downbearing.
        add(note+'_'+tag+'StringAfterlength',rod(V(x+30,sy,z),V(x+32,sy,pz)),silver,frame)
    # Geometric intersections of nominal plectrum circle with speaking segment.
    cross=math.sqrt(R*R-d*d)
    checks.append({'note':note,'speaking_mm':L,'arm_radius_mm':R,'length_ratio':inv,'offset_mm':d,'crossings_z_mm':[-cross,cross],'end_margin_mm':L/2-cross,'arm_to_string_plane_clearance_mm':3,'note_on_plucking':'Two crossings per revolution; a one-way or retracting pick is still needed for one pluck per turn.'})
    rows.append([note,a/b,inv,L,R,d])
doc.recompute()
invalid=[o.Name for o in created if o.Shape.isNull() or not o.Shape.isValid()]
assert not invalid,invalid
assert all(c['end_margin_mm']>0 for c in checks)
doc.Motion.Status='CONCEPT v2: inverse pitch string/arm lengths; bridge crowns and tapered tuning pins. One-way pick, loads, acoustic tuning, pin fits and mountings remain unvalidated.'
doc.Label="L'Harpe d'Amour — proportioned strings and bridges"
Gui.Selection.clearSelection();Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll()
doc.saveAs(OUT+'/Harpe_d_Amour_Strings_v2.FCStd')
with open(OUT+'/string_geometry_v2.json','w') as f:json.dump({'invalid_shapes':invalid,'assumptions':'C speaking length 120 mm, C arm radius 50 mm; inverse pitch ratios for equal string linear density and equal tension. Absolute tuning unspecified.','geometry':checks},f,indent=2)
with open(OUT+'/string_dimensions_v2.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['Note','Pitch_and_speed_ratio','Inverse_length_ratio','Speaking_length_mm','Arm_contact_radius_mm','String_offset_mm']);w.writerows(rows)
App.Console.PrintMessage('Strings v2 saved: valid solids; all plectrum crossings lie inside speaking lengths.\n')
