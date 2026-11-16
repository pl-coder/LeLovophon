import FreeCAD as A,Part,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'outputs/LeLovophon_Direct_Gear_Prototype/Reality_Audit';d=A.openDocument(str(R/'outputs/LeLovophon_Direct_Gear_Prototype/Axle_Clearance_Revision/LeLovophon_Direct_Gear_Prototype.FCStd'))
def sh(n):
 o=d.getObject(n);s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return s
report={};deck=sh('Baseplate_310x170x6');report['actual_deck_bounds_mm']=[deck.BoundBox.XMin,deck.BoundBox.XMax,deck.BoundBox.YMin,deck.BoundBox.YMax,deck.BoundBox.ZMin,deck.BoundBox.ZMax];report['outer_bridges']=[]
for prefix,note in [('C','C3'),('B','D5')]:
 b=sh(prefix+'_KotoThirdBridge');others=[]
 for name in ['Baseplate_310x170x6','SoundboxShell','KotoAnchorBlock','KotoTunerBlock']:
  q=sh(name);others.append(dict(part=name,minimum_distance_mm=b.distToShape(q)[0],overlap_volume_mm3=b.common(q).Volume))
 report['outer_bridges'].append(dict(note=note,bridge=prefix+'_KotoThirdBridge',body_contacts=others))
report['string_bridge_height_geometry']=[]
for prefix in ['C','Cs','D','Eb','E','F','Fs','G','Ab','A','Bb','B']:
 main=sh(prefix+'_KotoSpeakingString').BoundBox;back=sh(prefix+'_KotoBackString').BoundBox;c=sh(prefix+'_NylonBridgeCrown');left=sh(prefix+'_AnchorNylonSaddle');right=sh(prefix+'_TunerNylonSaddle')
 report['string_bridge_height_geometry'].append(dict(prefix=prefix,speaking_centre_height_Y_mm=(main.YMin+main.YMax)/2,back_centre_height_Y_mm=(back.YMin+back.YMax)/2,bridge_crown_top_Y_mm=c.BoundBox.YMax,left_saddle_top_Y_mm=left.BoundBox.YMax,right_saddle_top_Y_mm=right.BoundBox.YMax,crown_faces=len(c.Faces),crown_surface_types=[type(f.Surface).__name__ for f in c.Faces],nominal_string_break_angle_deg=0))
(O/'String_Support_and_Height_Audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
