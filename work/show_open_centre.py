import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,FreeCADGui as Gui,json
from PySide import QtCore,QtWidgets
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
for key in ['harpe_koto_timer','harpe_motion_timer','harpe_live_timer']:
 old=globals().get(key)
 if old is not None:
  try:old.stop()
  except:pass
newdoc=App.openDocument(OUT+'/Harpe_d_Amour_Open_Centred.FCStd');App.setActiveDocument(newdoc.Name)
for o in newdoc.Objects:
 if o.TypeId in ['Part::Feature','App::Part','App::DocumentObjectGroup'] and o.ViewObject:o.ViewObject.Visibility=True
 if o.TypeId=='Part::Feature':
  if 'CassetteMountShoe' in o.Name or 'PendulumBracket' in o.Name:o.ViewObject.ShapeColor=(0.72,0.75,0.78)
  if 'MountRib' in o.Name:o.ViewObject.ShapeColor=(0.73,0.52,0.30)
newdoc.Label="L’Harpe d’Amour — centred, open, portable"
newdoc.Motion.Status='Open centred bank; no enclosure. 370 x 200 x 179 mm assembled envelope. Estimated model material mass 2.19 kg, excluding unmodelled clockwork, fasteners and case. Carry assembled in a semi-hard handled case with base support and clearance around the mechanism. Strength, fatigue, string tension, spring and belt selections remain to be engineered.'
newdoc.recompute();newdoc.save()
Gui.Selection.clearSelection()
exec(open(OUT+'/Animate_Open_Harpe.FCMacro').read())
with open(OUT+'/../work/open_centre_loaded.txt','w') as f:f.write(newdoc.FileName)
