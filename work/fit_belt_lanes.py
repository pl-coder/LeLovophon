for i,n in enumerate(notes):
    s=24*i
    doc.getObject(n+'_CompoundPulleyHub').Shape=cyl(6,11.25,V()).cut(cyl(5.05,13.25,V(-1,0,0)))
    doc.getObject(n+'_IndependentPulleyBearing').Shape=cyl(5,10.5,V(.25,0,0)).cut(cyl(3.1,12.5,V(-.75,0,0)))
    doc.getObject(n+'_LowerTimingPulley').Shape=cyl(8,6,V(5.25,0,0)).cut(cyl(5.05,8,V(4.25,0,0)))
    doc.getObject(n+'_UpperTimingPulley').Shape=cyl(8,6,V(5.25,0,0)).cut(cyl(3.05,8,V(4.25,0,0)))
    top=doc.getObject(n+'_LongArmRotor').Placement.Base
    doc.getObject(n+'_TimingBeltEnvelope').Shape=belt(V(s+5.25,-59,-116),V(s+5.25,top.y,top.z),8,8,6)
doc.recompute();check_two_axles()
# Check all fixed belt envelopes against stationary frame and bridge hardware.
fixed_belts=[o for o in doc.Objects if o.TypeId=='Part::Feature' and ('_RatioBelt' in o.Name or '_TimingBeltEnvelope' in o.Name)]
rotating_names=set()
for n in notes:
    for suffix in ['_Driver','_Output','_LongArmRotor']:
        rotating_names.update(o.Name for o in doc.getObject(n+suffix).Group if o.TypeId=='Part::Feature')
fixed_hardware=[o for o in doc.Objects if o.TypeId=='Part::Feature' and o.Name not in rotating_names and o not in fixed_belts]
belt_clashes=[]
for obj in fixed_belts:
    for other in fixed_hardware:
        if obj.Shape.BoundBox.intersect(other.Shape.BoundBox) and obj.Shape.common(other.Shape).Volume>1e-5:belt_clashes.append((obj.Name,other.Name))
print('Belt / fixed hardware clashes:',belt_clashes)
