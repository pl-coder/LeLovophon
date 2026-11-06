import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,FreeCADGui as Gui,Part,json
from FreeCAD import Vector as V
from PySide import QtWidgets
from pathlib import Path
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs'
q=QtWidgets.QApplication.instance() or QtWidgets.QApplication([]);Gui.showMainWindow();Gui.getMainWindow().hide()
doc=App.openDocument(str(R/'work/Lovophone_Hardware_Frame_Base.FCStd'))
colors=json.loads((R/'work/motor_colors.json').read_text());colors.update(json.loads((R/'work/twelve_gantry_colors.json').read_text()))
colors.update(json.loads((R/'work/hardware_frame_colors.json').read_text()))
for o in doc.Objects:
 if o.ViewObject:o.ViewObject.Visibility=o.TypeId in ['Part::Feature','App::Part','App::DocumentObjectGroup']
 if o.TypeId!='Part::Feature':continue
 col=(.70,.73,.76)
 if any(k in o.Name for k in ['Soundbox','Baseplate','KotoThirdBridge','GuidePedestal']):col=(.59,.36,.18)
 if 'Pulley' in o.Name or 'NylonGuide' in o.Name:col=(.76,.59,.27)
 if 'ExtendedArm' in o.Name:col=(.23,.52,.48)
 if 'Belt' in o.Name:col=(.13,.15,.16)
 if any(k in o.Name for k in ['KotoSpeakingString','KotoBackString','NylonOverEdge']):col=(.86,.84,.72)
 if o.Name in colors:col=tuple(colors[o.Name])
 o.ViewObject.ShapeColor=col;o.ViewObject.LineColor=(.15,.16,.17);o.ViewObject.DisplayMode='Flat Lines';o.ViewObject.LineWidth=1
 if o.Name.startswith('ElectricClear') or o.Name=='ElectricCouplingShield':o.ViewObject.Transparency=82
v=Gui.getDocument(doc.Name).activeView();v.setCameraOrientation(App.Rotation(V(1,0,-.25),V(0,1,0),V(.25,.4,1),'ZXY').Q);v.fitAll();doc.recompute()
meshes=[];shapes=[];bounds=App.BoundBox()
for o in doc.Objects:
 if o.TypeId!='Part::Feature':continue
 sh=o.Shape.copy();sh.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());shapes.append(sh);bounds.add(sh.BoundBox)
 # Include clear drive skins for the physically lit scene.
 verts,tris=sh.tessellate(.45);meshes.append(dict(name=o.Name,vertices=[[p.x,p.y,p.z] for p in verts],triangles=tris,color=list(o.ViewObject.ShapeColor[:3]),transparency=o.ViewObject.Transparency,clock=False,motor=o.Name in json.loads((R/'work/motor_colors.json').read_text())))
doc.Motion.CarryEnvelope=V(bounds.XLength,bounds.ZLength,bounds.YLength)
doc.recompute();doc.saveAs(str(O/'Lovophone_Hardware_Frame.FCStd'))
Part.makeCompound(shapes).exportStep(str(O/'Lovophone_Hardware_Frame.step'))
(R/'work/hardware_frame_mesh.json').write_text(json.dumps(meshes))
rows=json.loads(doc.Motion.LinkageGeometry);groups=[]
for r in rows:
 for k in ['Driver','Output','LongArmRotor','Rocker']:
  o=doc.getObject(r['note']+'_'+k);groups.append(dict(note=r['note'],kind=k,matrix=list(o.Placement.toMatrix().A),members=[p.Name for p in o.Group if p.TypeId=='Part::Feature']))
(R/'work/hardware_frame_motion_map.json').write_text(json.dumps(dict(rows=rows,groups=groups)))
p=O/'Lovophone_Hardware_Frame_Design.json';report=json.loads(p.read_text());report.update(part_count=len(shapes),envelope_mm=[bounds.XLength,bounds.ZLength,bounds.YLength],display_settings_saved=True);p.write_text(json.dumps(report,indent=2))
print('Saved visible FreeCAD model, STEP, mesh and motion map.',flush=True);print('Envelope mm:',report['envelope_mm'],flush=True)
