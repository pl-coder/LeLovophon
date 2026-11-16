import sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work/protokoto_r3'))
import importlib.util
spec=importlib.util.spec_from_file_location('r3config',ROOT/'work/protokoto_r3/config.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
OLD_ROWS=copy.deepcopy(base.ROWS);OLD_BEARINGS=list(base.BEARINGS)
ROWS=copy.deepcopy(OLD_ROWS);DRIVE=base.DRIVE;linkage=base.linkage;angle=base.angle
PICKS=[-129,-79,-39,21,51,96,122,150,190,216,242,268]
for row,x in zip(ROWS,PICKS):row['station_x']=x-8;row['pick_x']=x
BEARINGS=[-186,-122,-5,60,123.3,189,241,300]
OUT=ROOT/'outputs/LeLovophon_Pluck_Layout_R5'
