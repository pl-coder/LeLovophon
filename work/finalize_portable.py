import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,json,os
from FreeCAD import Vector as V
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
doc=App.openDocument(OUT+'/Harpe_d_Amour_Open_Centred.FCStd')
rows=json.loads(doc.Motion.LinkageGeometry)
# Clear the twelve module fixing holes through the removable soundboard.
lid=doc.Baseplate_310x170x6
shape=lid.Shape.copy()
for r in rows:
 for dx in [-5,5]:shape=shape.cut(Part.makeCylinder(2.25,5,V(r['station']+dx,-113,-139),V(0,1,0)))
lid.Shape=shape
# Store the carrying and construction intent in the native design itself.
for name,kind,value in [
 ('CarryEnvelope','App::PropertyVector',V(370,200,179)),
 ('EstimatedModelMassKg','App::PropertyFloat',2.19),
 ('InstrumentMassTargetKg','App::PropertyFloat',3.0),
 ('TransportIntent','App::PropertyString','One-handed semi-hard case; carry assembled, support the soundbox, leave the exposed mechanism clear.'),
 ('ConstructionIntent','App::PropertyString','Removable six-module bank; 24 mm pitch; 4 mm braced aluminium bearing plates; shallow plywood soundbox; no protective enclosure.'),
 ('ValidationScope','App::PropertyString','Native shapes checked. Six pick contacts and sampled moving/fixed clearance checked. Manufacturing fasteners, structural loads, compliant plucking, clockwork and acoustic performance require engineering.')]:
 if name not in doc.Motion.PropertiesList:doc.Motion.addProperty(kind,name,'Portable design')
 setattr(doc.Motion,name,value)
doc.Label="L’Harpe d’Amour — portable centred version"
doc.recompute()
invalid=[o.Name for o in doc.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())]
assert not invalid,invalid
assert doc.getObject('DriveGuard') is None
assert abs((rows[0]['station']+rows[-1]['station'])/2+16.65-155)<1e-6
path=OUT+'/Harpe_d_Amour_Portable.FCStd';doc.saveAs(path)
shapes=[]
for o in doc.Objects:
 if o.TypeId=='Part::Feature':
  s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());shapes.append(s)
Part.makeCompound(shapes).exportStep(OUT+'/Harpe_d_Amour_Portable.step')
App.closeDocument(doc.Name)
check=App.openDocument(path)
assert len([o for o in check.Objects if o.TypeId=='Part::Feature'])==222
print('Saved and reopened portable version; all 222 shapes valid; centred bank; no cover; twelve soundboard module fixing holes; STEP exported.')
