import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as A,json
from pathlib import Path
R=Path((_LOVOPHON_WORKSPACE + ''));d=A.openDocument(str(R/'work/Lovophone_Pentatonic_Base.FCStd'));rows=json.loads(d.Motion.LinkageGeometry)
def world(o):s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return s
moving=set()
for r in rows:
 for k in ['Driver','Output','LongArmRotor','Rocker']:moving.update(o.Name for o in d.getObject(r['note']+'_'+k).Group if o.TypeId=='Part::Feature')
fixed={o.Name:world(o) for o in d.Objects if o.TypeId=='Part::Feature' and o.Name not in moving}
names=[r['note']+s for r in rows for s in ['_ArmHangingFork','_SwingStepUpBelt','_KotoThirdBridge']]+['ElectricMotorBracket']
intentional={tuple(sorted([r['note']+'_KotoThirdBridge',r['note']+'_NylonBridgeCrown'])) for r in rows}
clashes=set();interfaces=set()
for n in names:
 s=fixed[n]
 for m,t in fixed.items():
  if n==m:continue
  if s.BoundBox.intersect(t.BoundBox) and s.common(t).Volume>1e-5:
   pair=tuple(sorted([n,m]));(interfaces if pair in intentional else clashes).add(pair)
report=dict(changed_fixed_part_clashes=sorted(clashes),intentional_bridge_crown_seats=sorted(interfaces),scope='Changed forks, belt paths, third bridges and motor mount against all stationary model parts. Bridge crowns seated into wooden bridges are intentional interfaces.')
(R/'outputs/Lovophone_Pentatonic_Mount_Check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True);assert not clashes,clashes
