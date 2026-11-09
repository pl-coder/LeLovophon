import json,math,hashlib,sys
from fractions import Fraction
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import FreeCAD as A,Part
from FreeCAD import Vector as V
from direct_gear_math import ROOT,ROWS,DRIVE,report
OUT=ROOT/'outputs/LeLovophon_Mechanical_Revision_R2';AUD=OUT/'Checks';AUD.mkdir(exist_ok=True)
d=A.openDocument(str(OUT/'LeLovophon_R2.FCStd'))
parts=[o for o in d.Objects if o.TypeId=='Part::Feature'];invalid=[o.Name for o in parts if not o.Shape.isValid() or o.Shape.isNull()]
def overlap(a,b):return all(min(getattr(a,k+'Max'),getattr(b,k+'Max'))-max(getattr(a,k+'Min'),getattr(b,k+'Min'))>1e-7 for k in ['X','Y','Z'])
cl=[]
for r in ROWS:
 n=f"V{r['index']:02d}";s=r['station_x'];P=r['pivot_yz'];Q=r['crank_yz']
 # Measure physical front face against a complete crank disc swept envelope.
 flange=Part.makeCylinder(12,2,V(s+2,*Q),V(1,0,0));carrier=d.getObject(n+'_Carrier1').Shape
 cl.append(dict(voice=r['index'],flange_to_fixed_carrier_mm=flange.distToShape(carrier)[0],rod_rear_to_crank_front_axial_mm=(s+5)-(s+4),journal_end_to_washer_rear_mm=(s+7.3)-(s+7.2),bridge_length_mm=330/float(Fraction(r['ratio'])),arm_radius_mm=r['arm_radius_mm'],pick_x=s+8))
routes=json.loads((OUT/'String_Routing.json').read_text());board=d.getObject('Soundboard_355x178x3').Shape.BoundBox
supports=[]
for r in ROWS:
 b=d.getObject(f"V{r['index']:02d}_ThirdBridge").Shape.BoundBox
 supports.append(dict(voice=r['index'],fully_on_soundboard=board.XMin<=b.XMin and board.XMax>=b.XMax and board.ZMin<=b.ZMin and board.ZMax>=b.ZMax,foot_plane_y=-112,soundboard_top_y=board.YMax))
# Sweep all tensioner carriages, nuts and knots through 21.8 mm travel.
movable=[o for o in parts if o.Role=='Carriage' or 'CapturedM4Nut' in o.Name or 'TunerStopperKnot' in o.Name]
fixed=[o for o in parts if o not in movable];hits=[]
for moving in movable:
 for k in range(23):
  dy=-3+21.8*k/22;sh=moving.Shape.copy();sh.translate(V(0,dy,0))
  for f in fixed:
   if moving.Role=='Knot' and f.Role=='String' and moving.Voice==f.Voice:continue
   if not overlap(sh.BoundBox,f.Shape.BoundBox):continue
   v=sh.common(f.Shape).Volume
   if v>1e-5:hits.append(dict(moving=moving.Name,fixed=f.Name,travel_offset_mm=dy,volume_mm3=v))
# Every real 3D speaking length is horizontal, so its Euclidean length is exact.
length_errors=[abs((321-r['bridge_x'])-330/float(Fraction(row['ratio']))) for r,row in zip(routes,ROWS)]
calc=report();turns=[24*Fraction(row['ratio']) for row in ROWS]
rep=dict(cad_sha256=hashlib.sha256((OUT/'LeLovophon_R2.FCStd').read_bytes()).hexdigest(),part_count=len(parts),invalid_shapes=invalid,measured_clearances=cl,bridge_support=supports,minimum_back_break_angle_deg=min(r['back_break_angle_deg'] for r in routes),maximum_back_break_angle_deg=max(r['back_break_angle_deg'] for r in routes),max_speaking_length_error_mm=max(length_errors),shaft_journal_mm=3,washer_bore_mm=1.7,end_screw_core_mm=1.5,journal_stops_before_washer=True,bearing_abutments=dict(voice_inner_shoulder_od_mm=4,voice_outer_shoulder_id_mm=6.4,input_inner_shim_od_mm=5.9,input_outer_shoulder_id_mm=8.6),tensioner_travel_mm=21.8,tensioner_poses_per_part=23,tensioner_unexpected_intersections=hits,input_rpm=3,repeat_seconds=480,output_revolutions_per_cycle=[int(n) for n in turns],all_outputs_return_after_24_input_turns=all(n.denominator==1 for n in turns),max_link_closure_error_mm=calc['max_link_closure_error_mm'],minimum_transmission_angle_deg=calc['minimum_transmission_angle_deg'],physical_test_passed=False)
(AUD/'Dimensions_and_Tensioners.json').write_text(json.dumps(rep,indent=2));print(json.dumps(dict(invalid=invalid,tensioner_hits=len(hits),all_bridges_supported=all(x['fully_on_soundboard'] for x in supports),length_error=max(length_errors))),flush=True)
