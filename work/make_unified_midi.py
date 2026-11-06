import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
from pathlib import Path
from fractions import Fraction as F
import csv,json,math,struct,ast
from unified_design import *
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs'
tree=ast.parse((R/'work/make_pentatonic.py').read_text());exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ['vlq','meta','track']],type_ignores=[]),'midi','exec'))
voices=rows();channels=[1,2,3,4,5,6,7,8,9,11,12,13];csvrows=[]
for v,ch,ratio in zip(voices,channels,RATIOS):
 v['channel']=ch;v['correction_cents']=1200*math.log2(float(ratio))-100*(v['midi_note']-48)
 v['events_160min']=len(events(ratio,F(9600)))
 for t,slot in events(ratio,F(9600)):csvrows.append(dict(string=v['index'],note=v['note'],seconds=f'{float(t):.9f}',exact_seconds=str(t),slot=slot))
csvrows.sort(key=lambda r:(F(r['exact_seconds']),r['string']))
with (O/'Lovophone_Unified_160min_Pluck_Times.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=csvrows[0]);w.writeheader();w.writerows(csvrows)
for duration in [480,9600]:
 for ji in [False,True]:
  end=duration*1920
  ts=[track([(0,0,meta(3,'Lovophone unified pentatonic pitch and rotation')),(0,1,meta(81,(500000).to_bytes(3,'big'))),(0,2,meta(88,bytes([4,2,24,8]))),(0,3,meta(1,'400 second C3 revolution; identical 19 of 32 picking pattern; 160 minute full repeat.')),(end,99,meta(47,b''))])]
  count=0
  for v,ratio in zip(voices,RATIOS):
   ch=v['channel']-1;n=v['midi_note'];bend=round(8192+v['correction_cents']/200*8192) if ji else 8192
   es=[(0,0,meta(3,f"String {v['index']:02d} - {v['note']} - rotation {v['ratio_exact']}")),(0,1,meta(32,bytes([ch]))),(0,2,bytes([192|ch,24]))]
   for j,(cc,val) in enumerate([(101,0),(100,0),(6,2),(38,0),(101,127),(100,127)]):es.append((0,3+j,bytes([176|ch,cc,val])))
   es.append((0,10,bytes([224|ch,bend&127,bend>>7])))
   for t,slot in events(ratio,F(duration)):
    tick=round(t*1920);es.extend([(tick,30,bytes([144|ch,n,84])),(min(end,tick+3840),20,bytes([128|ch,n,0]))]);count+=1
   es.extend([(end,90,bytes([176|ch,123,0])),(end,99,meta(47,b''))]);ts.append(track(es))
  name=f"Lovophone_Unified_{duration//60}min_{'Just_Intonation' if ji else 'Bitwig'}.mid";(O/name).write_bytes(b'MThd'+struct.pack('>IHHH',6,1,13,960)+b''.join(ts));print(name,count)
(O/'Lovophone_Unified_Bitwig.scl').write_text((O/'Lovophone_Pentatonic_Bitwig.scl').read_text().replace('Lovophone_Pentatonic_Bitwig.scl','Lovophone_Unified_Bitwig.scl'))
metadata=dict(voices=voices,slot_count=32,occupied_slots=SLOTS,pegs_per_wheel=19,base_period_seconds=400,base_rpm=.15,full_repeat_input_revolutions=24,full_repeat_seconds=9600,full_event_count=len(csvrows),average_events_per_second=len(csvrows)/9600,tempo_bpm=120,midi_zero_matches_model_zero=True,all_voices_release_at_zero=True,rotation_equals_pitch_ratio=True,old_midi_superseded=True)
(O/'Lovophone_Unified_Music.json').write_text(json.dumps(metadata,indent=2))
