import json,hashlib
from pathlib import Path
import FreeCAD as A,Part
R=Path(__file__).resolve().parents[2];P=R/'outputs/LeLovophon_Pluck_Layout_R5/LeLovophon_Pluck_Layout_R5.FCStd';d=A.openDocument(str(P))
rho={'Aluminium':2.7e-6,'Steel':7.85e-6,'Bearing steel':7.8e-6,'Brass':8.5e-6,'Acetal':1.41e-6,'PVDF':1.78e-6,'Birch plywood':.65e-6,'Beech':.7e-6,'Spruce':.45e-6,'Rubber':1.2e-6,'PET':1.38e-6,'PTFE':2.2e-6,'Iglidur G':1.46e-6,'Spring steel':7.85e-6}
parts=[]
# Validate the volume-integral inertia convention against a known solid before using CAD mass properties.
c=Part.makeCylinder(12,2);assert abs(c.MatrixOfInertia.A33-c.Volume*12**2/2)<1e-6
for o in d.Objects:
 if o.TypeId!='Part::Feature' or o.Motion=='Fixed':continue
 sh=o.Shape.Solids[0];rr=rho[o.MaterialName];c=sh.CenterOfMass;b=sh.BoundBox
 parts.append(dict(name=o.Name,motion=o.Motion,voice=o.Voice,role=o.Role,material=o.MaterialName,mass_kg=sh.Volume*rr,com_m=[c.x/1000,c.y/1000,c.z/1000],Ixx_kg_m2=sh.MatrixOfInertia.A11*rr*1e-6,bounds_mm=[b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax]))
out=dict(cad_sha256=hashlib.sha256(P.read_bytes()).hexdigest(),density_assumptions_kg_per_mm3=rho,parts=parts)
(R/'work/pluck_r5/mass_properties.json').write_text(json.dumps(out,indent=2));print('EXTRACTED',len(parts),sum(p['mass_kg'] for p in parts),flush=True)

allparts=[o for o in d.Objects if o.TypeId=='Part::Feature']
bb=A.BoundBox()
for ob in allparts:bb.add(ob.Shape.BoundBox)
(P.parent/'Geometry_Summary.json').write_text(json.dumps(dict(cad_sha256=hashlib.sha256(P.read_bytes()).hexdigest(),saved_pose_length_width_height_mm=[bb.XLength,bb.ZLength,bb.YLength],valid_single_solid_count=sum(ob.Shape.isValid() and len(ob.Shape.Solids)==1 for ob in allparts),parts=len(allparts)),indent=2))
