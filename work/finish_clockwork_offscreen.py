import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,FreeCADGui as Gui,Part,json
from FreeCAD import Vector as V
from PySide import QtWidgets
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
q=QtWidgets.QApplication.instance() or QtWidgets.QApplication([]);Gui.showMainWindow();Gui.getMainWindow().hide()
doc=App.openDocument(OUT+'/Harpe_d_Amour_Clockwork.FCStd');colors=json.load(open(OUT+'/../work/clockwork_colors.json'))
if doc.getObject('ClockworkInputCoupling'):doc.removeObject('ClockworkInputCoupling')
for o in doc.Objects:
 if o.ViewObject:
  o.ViewObject.Visibility=o.TypeId in ['Part::Feature','App::Part','App::DocumentObjectGroup']
 if o.TypeId=='Part::Feature' and o.Name not in colors:
  o.ViewObject.ShapeColor=(.70,.73,.76)
  if any(k in o.Name for k in ['Soundbox','Baseplate','KotoThirdBridge','GuidePedestal']):o.ViewObject.ShapeColor=(.59,.36,.18)
  if 'Pulley' in o.Name or 'NylonGuide' in o.Name:o.ViewObject.ShapeColor=(.76,.59,.27)
  if 'ExtendedArm' in o.Name:o.ViewObject.ShapeColor=(.23,.52,.48)
  if 'Belt' in o.Name:o.ViewObject.ShapeColor=(.13,.15,.16)
  if any(k in o.Name for k in ['KotoSpeakingString','KotoBackString','NylonOverEdge']):o.ViewObject.ShapeColor=(.86,.84,.72)
 if o.Name in colors:
  o.ViewObject.ShapeColor=tuple(colors[o.Name]);o.ViewObject.LineColor=(.15,.16,.17)
  if o.Name.startswith('ClockClear') or o.Name=='ClockBarrelInspectionFace':o.ViewObject.Transparency=82
  o.ViewObject.DisplayMode='Flat Lines'
  o.ViewObject.LineWidth=1.0
view=Gui.getDocument(doc.Name).activeView();view.setCameraOrientation(App.Rotation(V(1,0,-.25),V(0,1,0),V(.25,.4,1),'ZXY').Q);view.fitAll()
doc.recompute();doc.save()
meshes=[];allshapes=[];bounds=App.BoundBox()
for o in doc.Objects:
 if o.TypeId!='Part::Feature':continue
 s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());allshapes.append(s);bounds.add(s.BoundBox)
 # Hide transparent skins in the offline explanatory render; their edges are shown separately.
 if o.Name.startswith('ClockClear') or o.Name=='ClockBarrelInspectionFace':continue
 verts,tris=s.tessellate(.45)
 meshes.append({'name':o.Name,'vertices':[[v.x,v.y,v.z] for v in verts],'triangles':tris,'color':list(o.ViewObject.ShapeColor[:3]),'clock':o.Name in colors})
doc.Motion.CarryEnvelope=V(bounds.XLength,bounds.ZLength,bounds.YLength)
doc.Motion.EstimatedModelMassKg=0.0
if 'MassEstimateNote' not in doc.Motion.PropertiesList:doc.Motion.addProperty('App::PropertyString','MassEstimateNote','Portable design')
doc.Motion.MassEstimateNote='Clockwork added; mass estimate must be recalculated after selecting a rated spring cartridge and hardware. Zero indicates not yet estimated.'
doc.save()
Part.makeCompound(allshapes).exportStep(OUT+'/Harpe_d_Amour_Clockwork.step')
json.dump(meshes,open(OUT+'/../work/clockwork_mesh.json','w'))
report=json.load(open(OUT+'/clockwork_design_check.json'));report['part_count']=len(allshapes);report['envelope_mm']=[bounds.XLength,bounds.ZLength,bounds.YLength];report['display_settings_saved']=True;json.dump(report,open(OUT+'/clockwork_design_check.json','w'),indent=2)
print('Saved visible native model, STEP and offline rendering mesh; envelope:',report['envelope_mm'],flush=True)
