import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,FreeCADGui as Gui,Part
from PySide import QtWidgets
q=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
Gui.showMainWindow();Gui.getMainWindow().hide()
d=App.newDocument('Offline');o=d.addObject('Part::Feature','Block');o.Shape=Part.makeBox(2,2,2);print('VIEW',o.ViewObject is not None,flush=True);d.saveAs((_LOVOPHON_WORKSPACE + '/work/offline_probe.FCStd'))
print('SAVED',flush=True)
