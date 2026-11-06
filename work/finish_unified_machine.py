import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as A,FreeCADGui as G,Part,json
from FreeCAD import Vector as V
from PySide import QtWidgets
from pathlib import Path
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs';app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([]);G.showMainWindow();G.getMainWindow().hide();d=A.openDocument(str(R/'work/Lovophone_Unified_Base.FCStd'));meta=json.loads((O/'Lovophone_Unified_Design.json').read_text());colors=meta['colors'];d.Motion.UnifiedGeometry=json.dumps(meta['rows'])
for r in meta['rows']:
 for suffix in ['_KotoSpeakingString','_KotoThirdBridge']:
  o=d.getObject(r['source_prefix']+suffix)
  for name,typ,value in [('PitchName','App::PropertyString',r['note']),('PitchRatioToC3','App::PropertyString',r['pitch_ratio_exact']),('RotationRatioToInput','App::PropertyString',r['rotation_ratio_exact']),('TargetFrequency','App::PropertyFrequency',r['frequency_hz']),('SpeakingLength','App::PropertyLength',r['speaking_length_mm']),('BridgePositionX','App::PropertyLength',r['bridge_x'])]:
   if name not in o.PropertiesList:o.addProperty(typ,name,'Unified musical design')
   setattr(o,name,value)
 o=d.getObject(r['source_prefix']+'_NylonTensionScrew');o.addProperty('App::PropertyLength','AllenKeyAF','Adjustment');o.AllenKeyAF=2.5
from unified_sprocket_webs import open_web
from unified_design import pitch_radius
for r in meta['rows']:
 if r['direct_input']:continue
 for suffix,teeth,bore in [('_DriveSprocket',r['driver_teeth'],3.05),('_DrivenSprocket',r['driven_teeth'],6.5)]:
  o=d.getObject(r['prefix']+suffix);o.Shape=open_web(o.Shape,pitch_radius(teeth),bore,5.3)
meta['sprocket_webs']='Three open spokes where web dimensions permit'
system=d.addObject('App::Part','SystemInput');system.Label='Common rotating input shaft and coupling'
for name in ['CommonInputShaft','InputKnob','InputKnobClamp']:
 o=d.getObject(name);d.Hardware.removeObject(o);sh=o.Shape.copy();sh.translate(V(-190,60,0));o.Shape=sh;system.addObject(o)
system.Placement=A.Placement(V(190,-60,0),A.Rotation())
meshes=[];shapes=[];bounds=A.BoundBox()
for o in d.Objects:
 if o.ViewObject:o.ViewObject.Visibility=o.TypeId in ['Part::Feature','App::Part','App::DocumentObjectGroup']
 if o.TypeId!='Part::Feature':continue
 col=colors.get(o.Name,[.7,.73,.76])
 if 'NylonGuide' in o.Name or 'Saddle' in o.Name:col=[.76,.59,.27]
 if 'KotoThirdBridge' in o.Name:col=[.64,.44,.23]
 if any(k in o.Name for k in ['SpeakingString','BackString','NylonOverEdge']):col=[.85,.83,.73]
 o.ViewObject.ShapeColor=tuple(col);o.ViewObject.LineColor=(.17,.18,.19);o.ViewObject.DisplayMode='Flat Lines';o.ViewObject.LineWidth=.7
 sh=o.Shape.copy();sh.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());shapes.append(sh);bounds.add(sh.BoundBox)
 verts,tris=sh.tessellate(.35);meshes.append(dict(name=o.Name,vertices=[[p.x,p.y,p.z] for p in verts],triangles=tris,color=list(col)))
v=G.getDocument(d.Name).activeView();v.setCameraOrientation(A.Rotation(V(1,0,-.25),V(0,1,0),V(.25,.4,1),'ZXY').Q);v.fitAll();d.recompute();d.saveAs(str(O/'Lovophone_Unified_160min.FCStd'));Part.makeCompound(shapes).exportStep(str(O/'Lovophone_Unified_160min.step'))
(R/'work/unified_mesh.json').write_text(json.dumps(meshes));groups=[]
for r in meta['rows']:
 for k in ['Driver','Wheel','Idler']:
  g=d.getObject(r['prefix']+'_'+k)
  if g is None:continue
  groups.append(dict(prefix=r['prefix'],kind=k,matrix=list(g.Placement.toMatrix().A),members=[o.Name for o in g.Group if o.TypeId=='Part::Feature']))
g=d.SystemInput;groups.append(dict(prefix='System',kind='Input',matrix=list(g.Placement.toMatrix().A),members=[o.Name for o in g.Group]))
(R/'work/unified_motion_map.json').write_text(json.dumps(dict(rows=meta['rows'],groups=groups)))
meta['display_settings_saved']=True;meta['mesh_objects']=len(meshes);(O/'Lovophone_Unified_Design.json').write_text(json.dumps(meta,indent=2));print('Saved visible model, STEP and meshes:',len(meshes),flush=True)
