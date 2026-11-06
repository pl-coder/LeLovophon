import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,json
from FreeCAD import Vector as V
O=(_LOVOPHON_WORKSPACE + '/outputs');d=App.openDocument(O+'/Harpe_d_Amour_Twelve_Electric.FCStd');rows=json.loads(d.Motion.LinkageGeometry)
def world(o):s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return s
contact={};poses={}
for r in rows:
 n=r['note'];o=d.getObject(n+'_LongArmRotor');poses[n]=o.Placement;o.Placement=App.Placement(V(r['station'],r['pivot_y'],r['pivot_z']),App.Rotation(V(1,0,0),90));d.recompute();contact[n]=world(d.getObject(n+'_ExtendedPick')).common(world(d.getObject(n+'_KotoSpeakingString'))).Volume;o.Placement=poses[n]
 for suffix,teeth in [('_RatioDrivePulley',r['driver_teeth']),('_RatioDrivenPulley',r['driven_teeth'])]:
  obj=d.getObject(n+suffix)
  for prop,kind,val in [('ReferenceTeeth','App::PropertyInteger',teeth),('ReferencePitch','App::PropertyLength',2)]:
   if prop not in obj.PropertiesList:obj.addProperty(kind,prop,'Belt')
   setattr(obj,prop,val)
# Make actual openings around the external switch and supply connector.
d.ElectricClearTop.Shape=d.ElectricClearTop.Shape.cut(Part.makeBox(7.4,5,8.4,V(328.8,-76,-148.2)))
d.ElectricClearRear.Shape=d.ElectricClearRear.Shape.cut(Part.makeBox(7.4,5.4,5,V(327.8,-103.2,-155)))
d.recompute();invalid=[o.Name for o in d.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())]
assert not invalid,invalid;assert all(v>0 for v in contact.values()),contact
assert len(rows)==12 and not d.getObject('Clockwork') and not d.getObject('AntiquePiercedWindingKey')
assert all(abs(r['driver_teeth']/r['driven_teeth']-r['ratio'])<1e-9 for r in rows)
d.save();json.dump({'exact_own_string_contact_volumes_mm3':contact,'scale_ratios_match_reference_pulleys':True,'clockwork_removed':True,'invalid_shapes':invalid,'string_count':12},open(O+'/twelve_final_checks.json','w'),indent=2);print('Twelve exact pick contacts, ratios and valid geometry verified.')
