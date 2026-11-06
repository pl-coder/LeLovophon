# Rearward shared axle and outboard belt lanes clear the bridge towers.
doc.CommonIntermediateAxle.Shape=cyl(3,168,V(-26,-59,-116))
for j,x in enumerate([-25,134]):
    doc.getObject('IntermediateAxleStand'+str(j)).Shape=box(6,54,18,x,-109,-125).cut(cyl(3.05,8,V(x-1,-59,-116)))
for i,n in enumerate(notes):
    s=24*i;ou=doc.getObject(n+'_Output');p=ou.Placement;p.Base=V(s,-59,-116);ou.Placement=p
    doc.getObject(n+'_CompoundPulleyHub').Shape=cyl(6,17,V(-12,0,0)).cut(cyl(5.05,19,V(-13,0,0)))
    doc.getObject(n+'_IndependentPulleyBearing').Shape=cyl(5,15,V(-10.25,0,0)).cut(cyl(3.1,17,V(-11.25,0,0)))
    doc.getObject(n+'_LowerTimingPulley').Shape=cyl(8,6,V(-12,0,0)).cut(cyl(5.05,8,V(-13,0,0)))
    doc.getObject(n+'_UpperTimingPulley').Shape=cyl(8,6,V(-12,0,0)).cut(cyl(3.05,8,V(-13,0,0)))
    doc.getObject(n+'_RaisedArmShaft').Shape=cyl(3,27.5,V(-12,0,0))
    doc.getObject(n+'_RatioBelt').Shape=belt(V(s,-83,-131),V(s,-59,-116),drivers[i]*.3,driven[i]*.3,5)
    top=doc.getObject(n+'_LongArmRotor').Placement.Base
    doc.getObject(n+'_TimingBeltEnvelope').Shape=belt(V(s-12,-59,-116),V(s-12,top.y,top.z),8,8,6)
doc.recompute();doc.save();check_two_axles()
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
