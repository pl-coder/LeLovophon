import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,FreeCADGui as Gui,json
from FreeCAD import Vector as V
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
doc=next((d for d in App.listDocuments().values() if d.FileName.endswith('/Harpe_d_Amour_Portable.FCStd')),None)
if doc is None:doc=App.openDocument(OUT+'/Harpe_d_Amour_Portable.FCStd')
App.setActiveDocument(doc.Name)
for o in doc.Objects:
 if o.ViewObject:
  if o.TypeId in ['Part::Feature','App::Part','App::DocumentObjectGroup']:o.ViewObject.Visibility=True
  else:o.ViewObject.Visibility=False
 if o.TypeId=='Part::Feature':
  o.ViewObject.ShapeColor=(0.72,0.75,0.78);o.ViewObject.LineColor=(0.12,0.13,0.15)
  if any(k in o.Name for k in ['Soundbox','Baseplate','KotoEnd']):o.ViewObject.ShapeColor=(0.64,0.39,0.20)
  if 'Pulley' in o.Name or 'Cam' in o.Name:o.ViewObject.ShapeColor=(0.78,0.62,0.30)
  if 'Belt' in o.Name:o.ViewObject.ShapeColor=(0.15,0.17,0.19)
  if 'String' in o.Name:o.ViewObject.ShapeColor=(0.83,0.84,0.87)
  if 'ExtendedArm' in o.Name:o.ViewObject.ShapeColor=(0.26,0.57,0.55)
doc.recompute()
gd=Gui.getDocument(doc.Name)
if not gd.activeView():gd.createView('Gui::View3DInventor')
v=gd.activeView();v.setCameraOrientation(App.Rotation(V(1,0,-.25),V(0,1,0),V(.25,.4,1),'ZXY').Q);v.fitAll()
Gui.activeDocument().activeView().redraw()
doc.save()
v.saveImage(OUT+'/Harpe_Portable_Preview.png',1600,1000,'Current')
with open(OUT+'/../work/portable_visibility_fixed.json','w') as f:json.dump({'file':doc.FileName,'visible_parts':sum(o.TypeId=='Part::Feature' and o.ViewObject.Visibility for o in doc.Objects)},f)
