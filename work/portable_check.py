import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,json,math
from FreeCAD import Vector as V
OUT=(_LOVOPHON_WORKSPACE + '/outputs')
doc=App.openDocument(OUT+'/Harpe_d_Amour_Open_Centred.FCStd');rows=json.loads(doc.Motion.LinkageGeometry)
def world(o):
 s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return s
contacts={}
for r in rows:
 n=r['note'];doc.getObject(n+'_LongArmRotor').Placement=App.Placement(V(r['station'],r['pivot_y'],r['pivot_z']),App.Rotation(V(1,0,0),90));doc.recompute()
 contacts[n]=world(doc.getObject(n+'_ExtendedPick')).common(world(doc.getObject(n+'_KotoSpeakingString'))).Volume
parts=[];bounds=App.BoundBox()
for o in doc.Objects:
 if o.TypeId!='Part::Feature':continue
 sh=world(o);bounds.add(sh.BoundBox);name=o.Name
 if any(k in name for k in ['SoundboxShell','EndBlock','MountRib','Baseplate']):mat,density='plywood',0.00000065
 elif 'Foot' in name:mat,density='rubber',0.0000011
 elif 'Belt' in name or 'Pick' in name:mat,density='polymer',0.0000012
 elif any(k in name for k in ['Shaft','Axle','Bearing','Pin','Tuning','String','Spring','Anchor']):mat,density='steel',0.00000785
 else:mat,density='aluminium',0.0000027
 parts.append({'part':name,'material_assumption':mat,'volume_mm3':sh.Volume,'mass_kg':sh.Volume*density})
report={'straight_down_pick_contact_volumes_mm3':contacts,'stationary_envelope_mm':{'length':bounds.XLength,'depth':bounds.ZLength,'height':bounds.YLength},'model_material_mass_kg':sum(p['mass_kg'] for p in parts),'densities_kg_per_m3':{'plywood':650,'rubber':1100,'polymer':1200,'steel':7850,'aluminium':2700},'parts':parts}
with open(OUT+'/portable_size_and_mass.json','w') as f:json.dump(report,f,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='parts'},indent=2))
