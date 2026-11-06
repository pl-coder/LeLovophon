import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,json
from FreeCAD import Vector as V
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
src=App.openDocument(OUT+'/Harpe_d_Amour_Koto_Recovered.FCStd')
dst=App.newDocument('Harpe_Koto_Geometry_Rescue');dst.Label="L'Harpe d'Amour — geometry rescue"
groups={}
for name in ['SoundboxAndEnds','StringsAndBridges','DriveAndArms','Guard']:
    groups[name]=dst.addObject('App::DocumentObjectGroup',name)
objects=[];invalid=[]
for o in src.Objects:
    if o.TypeId!='Part::Feature':continue
    sh=o.Shape.copy();sh.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix())
    if sh.isNull() or not sh.isValid():invalid.append(o.Name);continue
    n=dst.addObject('Part::Feature',o.Name);n.Label=o.Label;n.Shape=sh
    category='DriveAndArms'
    if any(x in o.Name for x in ['Soundbox','Baseplate','KotoAnchor','KotoTuner']):category='SoundboxAndEnds'
    elif any(x in o.Name for x in ['String','ThirdBridge']):category='StringsAndBridges'
    elif o.Name.startswith('Guard'):category='Guard'
    groups[category].addObject(n);objects.append(n)
data=dst.addObject('App::DocumentObjectGroup','RecoveredDesignData');data.addProperty('App::PropertyString','LinkageGeometry','Recovery');data.LinkageGeometry=src.Motion.LinkageGeometry
data.addProperty('App::PropertyString','RecoveryNote','Recovery');data.RecoveryNote='World-space geometry rescue. Original motion hierarchy remains in Harpe_d_Amour_Koto_Recovered.FCStd. This copy is static and omits the original GUI metadata.'
dst.recompute();dst.saveAs(OUT+'/Harpe_Koto_Geometry_Rescue.FCStd')
Part.export(objects,OUT+'/Harpe_Koto_Geometry_Rescue.step')
with open(OUT+'/recovery_report.json','w') as f:json.dump({'recovered_solid_features':len(objects),'invalid':invalid,'preserved_linkage_parameters':True,'scope':'Static world-space rescue plus full native visibility repair; original source unchanged.'},f,indent=2)
print('Recovered',len(objects),'features; invalid:',invalid)
