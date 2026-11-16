from pathlib import Path
import FreeCAD as A,Part
R=Path(__file__).resolve().parents[2];O=R/'outputs/LeLovophon_Mechanical_Revision_R2'
d=A.openDocument(str(O/'LeLovophon_R2.FCStd'))
Part.makeCompound([o.Shape for o in d.Objects if o.TypeId=='Part::Feature']).exportStep(str(O/'R2_Assembly_REFERENCE_NOT_FOR_MACHINING.step'))
print('Reference STEP saved; not a manufacturing release.',flush=True)
