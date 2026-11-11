import sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work'))
from direct_gear_math import ROWS as OLD_ROWS,DRIVE,linkage,angle,report
from fractions import Fraction
OUT=ROOT/'outputs/LeLovophon_Protokoto_R3'
ROWS=copy.deepcopy(OLD_ROWS)
for r in ROWS:
 r['old_station_x']=r['station_x'];r['station_x']=321+(r['station_x']-321)*600/330
 r['bridge_x']=321-600/float(Fraction(r['ratio']));r['pick_x']=r['station_x']+8
 assert r['bridge_x']+5.5<r['pick_x']<321
BEARINGS=[-224]+[ROWS[i]['station_x']+12 for i in [0,2,4,6,8,10]]+[300]
YTOP=-112;CASE=(-350,350,-130,90,-172,-112);LINE_R=.525;CROWN_R=5.;PATH_R=CROWN_R+LINE_R-.1
NUT_X=321.;LOW_X=-324.;NUT_Y=-91-PATH_R;LOW_Y=NUT_Y-12
ANCHOR_X=LOW_X-PATH_R;TUNER_DX=(NUT_X+PATH_R)-323.3
