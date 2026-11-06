doc.openTransaction('Thin flexible picks')
for i,n in enumerate('CDEFG'):
    a=[40,36,40,32,36][i];b=[40,32,32,24,24][i];R=30*b/a;az=-(a+b)/2
    phase=math.degrees(math.asin((-34-az)/R))
    arm=bank_box(3,4,R-.5,12,-2,0).fuse(bank_cyl(6,3,V(12,0,0))).cut(bank_cyl(3.05,5,V(11,0,0)))
    blade=bank_box(3.3,.6,1.5,15,-.3,R-1)
    arm.rotate(V(),V(1,0,0),phase);blade.rotate(V(),V(1,0,0),phase)
    doc.getObject(n+'_BankArm').Shape=arm;doc.getObject(n+'_BankPlectrum').Shape=blade
doc.recompute();doc.commitTransaction()
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

long_bank_clashes=verify_long_bank()
