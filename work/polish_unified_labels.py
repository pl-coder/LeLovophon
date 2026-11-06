import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as A,FreeCADGui as G
from PySide import QtWidgets
from pathlib import Path
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([]);G.showMainWindow();G.getMainWindow().hide();p=Path((_LOVOPHON_WORKSPACE + '/outputs/Lovophone_Unified_160min.FCStd'));d=A.openDocument(str(p));d.V01_WheelHub.Label='C3 — direct input wheel hub, no bearings'
if 'InputRPM' not in d.Motion.PropertiesList:d.Motion.addProperty('App::PropertyFloat','InputRPM','Timing')
d.Motion.InputRPM=.15
if 'AllenKeyAF' not in d.Motion.PropertiesList:d.Motion.addProperty('App::PropertyLength','AllenKeyAF','Adjustment')
d.Motion.AllenKeyAF=2.5;d.recompute();d.save();print('Saved input-speed and adjustment properties.')
