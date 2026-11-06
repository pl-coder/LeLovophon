import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
from pathlib import Path
from fractions import Fraction as F
from math import lcm
import ast,struct,json
from unified_design import *
O=Path((_LOVOPHON_WORKSPACE + '/outputs'));tree=ast.parse((O.parent/'work/check_lovophone_midi.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'parser','exec'))
assert lcm(*(r.denominator for r in RATIOS))==24
assert all(F(a,b)==r for (a,b),r in zip(PAIRS,RATIOS))
assert all((FULL_PERIOD/(BASE_PERIOD/r)).denominator==1 for r in RATIOS)
assert len(set(SLOTS))==19 and not any({(s+k)%32 for s in SLOTS}==set(SLOTS) for k in range(1,32))
voices=json.loads((O/'Lovophone_Unified_Music.json').read_text())['voices'];reports=[]
for duration in [480,9600]:
 for version in ['Bitwig','Just_Intonation']:
  name=f'Lovophone_Unified_{duration//60}min_{version}.mid';b=(O/name).read_bytes();assert b[:4]==b'MThd';length,fmt,nt,ppq=struct.unpack('>IHHH',b[4:14]);assert(length,fmt,nt,ppq)==(6,1,13,960);i=14;counts=[]
  for ti in range(nt):
   assert b[i:i+4]==b'MTrk';sz=struct.unpack('>I',b[i+4:i+8])[0];i+=8;end=i+sz;t=0;active=set();ons=[];bends=[]
   while i<end:
    dt,i=readvlq(b,i);t+=dt;status=b[i];i+=1
    if status==255:
     typ=b[i];i+=1;ln,i=readvlq(b,i);val=b[i:i+ln];i+=ln
     if typ==0x51:assert int.from_bytes(val,'big')==500000
     if typ==0x2f:assert i==end
    else:
     ln=1 if status&0xf0 in [0xc0,0xd0] else 2;vals=b[i:i+ln];i+=ln
     if status&0xf0==0x90 and vals[1]>0:
      key=(status&15,vals[0]);assert key not in active;active.add(key);ons.append(t)
      v=voices[ti-1];assert vals[0]==v['midi_note'] and status&15==v['channel']-1
     if status&0xf0==0x80 or(status&0xf0==0x90 and vals[1]==0):active.remove((status&15,vals[0]))
     if status&0xf0==0xe0:bends.append(vals[0]+128*vals[1])
   assert not active;assert t==duration*1920
   if ti:
    expected=[round(t*1920) for t,slot in events(RATIOS[ti-1],F(duration))];assert ons==expected
    v=voices[ti-1];expect=8192 if version=='Bitwig' else round(8192+v['correction_cents']/200*8192);assert bends==[expect]
   counts.append(len(ons))
  assert i==len(b);reports.append(dict(file=name,duration_seconds=duration,notes=sum(counts),tracks=13,exact_event_times_verified=True,balanced_note_offs=True));print(reports[-1])
(O/'Lovophone_Unified_Music_Check.json').write_text(json.dumps(dict(rotation_ratios_equal_pitch=True,full_repeat_seconds=9600,pattern_no_shorter_rotational_symmetry=True,files=reports),indent=2))
