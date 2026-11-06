import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App, FreeCADGui as Gui, Part, math, json, csv
from FreeCAD import Vector as V
doc=App.ActiveDocument
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
axial_created=[]
axial_rows=[]
axial_hardware=[]
def axial_part(name,shape,color,parent,hardware=True):
    obj=doc.addObject('Part::Feature',name)
    obj.Shape=shape;obj.ViewObject.ShapeColor=color;parent.addObject(obj)
    axial_created.append(obj)
    if hardware:axial_hardware.append(obj)
    return obj
def axial_rod(p,q,r=.18):
    v=q-p;return Part.makeCylinder(r,v.Length,p,v)
def axial_box(dx,dy,dz,x,y,z):return Part.makeBox(dx,dy,dz,V(x,y,z))
def axial_length(obj,name,value,description):
    obj.addProperty('App::PropertyLength',name,'String geometry',description);setattr(obj,name,value)
def prepare_axial_layout():
    doc.Motion.Time=0;doc.recompute()
    # Delete the superseded rings and transverse string fittings in this undoable edit.
    for n in 'CDEFG':
        group=doc.getObject(n+'_StringModule')
        if group:
            for obj in list(group.Group):doc.removeObject(obj.Name)
            doc.removeObject(group.Name)
        for suffix in ['CircularFrame_D130','FrameFoot','StringReference','BridgeReference','BridgeReference001','PlectrumReference','FlexiblePlectrum']:
            obj=doc.getObject(n+'_'+suffix)
            if obj:doc.removeObject(obj.Name)
    base=Part.makeBox(370,200,6,V(-30,-45,-115))
    for xx in [-20,330]:
        for yy in [-35,145]:base=base.cut(Part.makeCylinder(2.75,8,V(xx,yy,-116)))
    doc.Baseplate_310x170x6.Shape=base
    doc.Baseplate_310x170x6.Label='Baseplate — 370 x 200 x 6 mm'
    group=doc.addObject('App::DocumentObjectGroup','AxialStringBank')
    group.Label='Five strings parallel to the main axle'
    doc.recompute()
    print('Rings removed; base extended for longitudinal strings')
def build_axial_voice(i):
    n='CDEFG'[i];a=[40,36,40,32,36][i];b=[40,32,32,24,24][i]
    scale=b/a;L=120*scale;R=50*scale;x=55*i;sy=(a+b)/2;sz=R
    # Pick is 3.3 mm thick along the axle, centred at x + 28.65 mm.
    pluck=x+28.65;left=pluck-L/4;right=left+L
    group=doc.addObject('App::DocumentObjectGroup',n+'_AxialString')
    group.Label='%s — %.2f mm — parallel to axle'%(n,L)
    doc.AxialStringBank.addObject(group)
    silver=(.74,.78,.82);wood=(.38,.23,.12);brass=(.82,.64,.29)
    st=axial_part(n+'_LongitudinalString',axial_rod(V(left,sy,sz),V(right,sy,sz)),silver,group,False)
    axial_length(st,'SpeakingLength',L,'Distance between the two knife-edge saddle apexes')
    axial_length(st,'PluckDistanceFromLeft',L/4,'Quarter of the speaking span')
    axial_length(st,'HeightAboveOutputAxis',R,'String tangent to the nominal plectrum path')
    for sign,bx in [(-1,left),(1,right)]:
        tag='AnchorEnd' if sign<0 else 'TuningEnd';px=bx+sign*12
        lo=min(bx,px)-5;hi=max(bx,px)+5;ty=sy+30;tx=(bx+px)/2
        # End supports sit to the side of the gear train; no circular frame.
        foot=axial_box(18,18,3,tx-9,ty-9,-109)
        tower=axial_box(10,8,sz+97,tx-5,ty-4,-109)
        beam=axial_box(hi-lo,38,6,lo,sy-4,sz-16)
        axial_part(n+'_'+tag+'_Foot',foot,brass,group)
        axial_part(n+'_'+tag+'_Tower',tower,wood,group)
        axial_part(n+'_'+tag+'_CrossBridge',beam,wood,group)
        carrier=axial_box(8,8,8,bx-4,sy-4,sz-10)
        for yy in [sy-3,sy+3]:carrier=carrier.cut(Part.makeCylinder(1.1,9,V(bx,yy,sz-10)))
        axial_part(n+'_'+tag+'_SaddleCarrier',carrier,brass,group)
        tri=Part.makePolygon([V(bx-2,sy-2.5,sz-2),V(bx,sy-2.5,sz),V(bx+2,sy-2.5,sz-2),V(bx-2,sy-2.5,sz-2)])
        saddle=Part.Face(tri).extrude(V(0,5,0))
        axial_part(n+'_'+tag+'_KnifeEdgeSaddle',saddle,silver,group)
        for k,yy in enumerate([sy-3,sy+3]):
            screw=Part.makeCylinder(1,8,V(bx,yy,sz-10)).fuse(Part.makeCylinder(1.8,1,V(bx,yy,sz-3)))
            axial_part(n+'_'+tag+'_SaddleScrew'+str(k),screw,silver,group)
        block=axial_box(8,8,14,px-4,sy-4,sz-21)
        if sign>0:
            block=block.cut(Part.makeCone(1.8,1.95,14,V(px,sy,sz-21)))
            pin=Part.makeCone(1.85,2,14,V(px,sy,sz-21)).fuse(Part.makeCylinder(2,4,V(px,sy,sz-7)))
            pin=pin.fuse(axial_box(4,4,3,px-2,sy-2,sz-3))
            name=n+'_VerticalTuningPin'
        else:
            block=block.cut(Part.makeCylinder(2.05,14,V(px,sy,sz-21)))
            pin=Part.makeCylinder(2,18,V(px,sy,sz-21)).fuse(Part.makeCylinder(3,2,V(px,sy,sz-3)))
            name=n+'_FixedAnchorPin'
        pin=pin.cut(Part.makeCylinder(.5,6,V(px-3,sy,sz-5),V(1,0,0)))
        axial_part(n+'_'+tag+'_PinBlock',block,wood,group)
        peg=axial_part(name,pin,silver,group)
        peg.addProperty('App::PropertyString','Status','Design')
        peg.Status='Concept hardware: final holding torque, fits, fastenings and string load not specified'
        axial_part(n+'_'+tag+'_Afterlength',axial_rod(V(bx,sy,sz),V(px,sy,sz-5)),silver,group,False)
    # Rebuild the blade removed with the previous fittings; same inverse-ratio radius.
    axial_part(n+'_AxialPlectrum',axial_box(3.3,1,4,27,-.5,R-2),(.92,.88,.73),doc.getObject(n+'_Output'),False)
    ou=doc.getObject(n+'_Output');ou.StringOffset=0
    doc.recompute()
    bad=[o.Name for o in axial_created if not o.Shape.isValid() or o.Shape.isNull()]
    assert not bad,bad
    axial_rows.append({'note':n,'speaking_mm':L,'arm_radius_mm':R,'left_saddle_x_mm':left,'right_saddle_x_mm':right,'string_y_mm':sy,'string_z_mm':sz,'pluck_x_mm':pluck,'length_ratio':scale})
    print(n,'axial string built, length',round(L,3),'mm')
def verify_axial_layout():
    collisions=[]
    # Conservative full-turn envelopes for each arm and blade, against new fixed hardware.
    for i,n in enumerate('CDEFG'):
        x=i*55;R=50*[1,8/9,4/5,3/4,2/3][i];y=([40,36,40,32,36][i]+[40,32,32,24,24][i])/2
        arm=Part.makeCylinder(max(6,R-2),3,V(x+24,y,0),V(1,0,0))
        arm=arm.cut(Part.makeCylinder(3.05,5,V(x+23,y,0),V(1,0,0)))
        blade=Part.makeCylinder(math.hypot(R+2,.5),3.3,V(x+27,y,0),V(1,0,0)).cut(Part.makeCylinder(R-2,5.3,V(x+26,y,0),V(1,0,0)))
        for obj in axial_hardware:
            for label,envelope in [('arm',arm),('blade',blade)]:
                if not envelope.BoundBox.intersect(obj.Shape.BoundBox):continue
                vol=envelope.common(obj.Shape).Volume
                if vol>1e-5:collisions.append({'voice':n,'part':obj.Name,'envelope':label,'volume_mm3':vol})
    doc.Motion.Status='Axial strings, inverse pitch lengths, one nominal pick encounter per revolution; prescribed motion only. Final pin fits, load capacity and acoustic tuning unvalidated.'
    doc.Label="L'Harpe d'Amour — axial strings, no rings"
    Gui.Selection.clearSelection();Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll()
    doc.recompute();doc.save()
    with open(OUT+'/axial_string_geometry.json','w') as f:json.dump({'geometry':axial_rows,'conservative_full_turn_hardware_collisions':collisions,'assumption':'Same string linear density and equal tension; absolute pitch unspecified. 120 mm C speaking length and 50 mm C arm contact radius are provisional.'},f,indent=2)
    print('Full-turn arm/blade envelope collisions:',collisions)
    return collisions
