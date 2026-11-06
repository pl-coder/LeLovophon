import FreeCAD as App,FreeCADGui as Gui
print('methods',[n for n in dir(Gui) if any(k in n.lower() for k in ['setup','without','showmain'])])
Gui.setupWithoutGUI()
d=App.newDocument('Test');o=d.addObject('Part::Feature','Test');print('view',o.ViewObject)
