from pathlib import Path
from fractions import Fraction as F
import math,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/LeLovophon_Slender_Bank'
RATIOS=list(map(F,['1','9/8','5/4','3/2','5/3','2','9/4','5/2','3','10/3','4','9/2']))
LABELS=['C3','D3','E3','G3','A3','C4','D4','E4','G4','A4','C5','D5']
LONGEST=109.;PITCH=13.5;FIRST=145.;HALF_SWING=45.;STRING_Y=-91.;INTRUSION=-.15
ROWS=[dict(index=i+1,note=n,ratio=str(r),station_x=FIRST+PITCH*i,string_z=-80+10*i,arm_radius=LONGEST/float(r),pivot_y=STRING_Y+LONGEST/float(r),speaking_length=330/float(r),bridge_x=320-330/float(r),pick_x=FIRST+PITCH*i+2,frequency_hz=130.8127826502993*float(r)) for i,(r,n) in enumerate(zip(RATIOS,LABELS))]
SLOPE=(ROWS[-1]['pivot_y']-ROWS[0]['pivot_y'])/(PITCH*11)
def rail(x,zoff=0):return (x,ROWS[0]['pivot_y']+9+SLOPE*(x-FIRST),-80+(x-FIRST)*10/PITCH+zoff)
def report():
 for r in ROWS:
  assert r['bridge_x']<r['pick_x']<320
  r['full_tip_sweep_mm']=2*r['arm_radius']*math.sin(math.radians(HALF_SWING))
  # Conservative contact bound, including1 mm tip width and0.8 mm nylon.
  r['lateral_pick_contact_bound_mm']=math.sqrt((r['arm_radius']+INTRUSION)**2-(r['arm_radius']-.4)**2)+.5+.4
  r['next_string_contact_margin_mm']=10-r['lateral_pick_contact_bound_mm']
  assert r['next_string_contact_margin_mm']>1.5
 x0=FIRST-6.25;x1=ROWS[-1]['station_x']-3.25
 top=rail(x0)[1]+2
 return dict(voices=ROWS,longest_arm_mm=LONGEST,shortest_arm_mm=ROWS[-1]['arm_radius'],previous_longest_arm_mm=67.19693845669907,arm_length_gain_percent=100*(LONGEST/67.19693845669907-1),half_swing_degrees=HALF_SWING,pivot_pitch_x_mm=PITCH,previous_pivot_pitch_x_mm=24,bank_pivot_span_x_mm=PITCH*11,previous_pivot_span_x_mm=264,miniature_bearing_spec_mm=[3,6,2.5],bearing_source='https://www.123roulement.com/roulement-palier/roulement-bille/simple-rangee/mr63-zz',arm_stock='Aluminium tube4 mm OD /2 mm ID (4x1 mm)',backbone_stock='Aluminium tube4 mm OD /2 mm ID',rail_top_y_mm=top,old_model_top_y_mm=34.19693845669906,roof_margin_mm=34.19693845669906-top,axial_stack_clearance_mm=PITCH-7.5-5.0,minimum_wrong_string_margin_bound_mm=min(r['next_string_contact_margin_mm'] for r in ROWS),repeat_seconds=480,input_rpm=3,drivetrain_packaged=False,physical_test_passed=False,scope='Upper-bank geometry and packing study. Does not install a full12-voice drivetrain. No claim of maximum structural efficiency or verified strength. Proportional arms retained.')
if __name__=='__main__':
 OUT.mkdir(exist_ok=True);(OUT/'Slender_Bank_Layout.json').write_text(json.dumps(report(),indent=2));print(json.dumps({k:v for k,v in report().items() if k!='voices'},indent=2))
