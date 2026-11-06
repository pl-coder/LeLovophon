from pathlib import Path
from fractions import Fraction
import struct,json,math
O=Path('outputs');mapping=json.loads((O/'Lovophone_Pentatonic_Note_Map.json').read_text())['voices']
for p in sorted(O.glob('Lovophone_Pentatonic_*min_*.mid')):
 b=p.read_bytes();assert b[:4]==b'MThd';assert struct.unpack('>IHHH',b[4:14])==(6,1,13,960);i=14;total=0;duration=480 if '_8min_' in p.name else 9600
 def vlq():
  global i
  n=0
  while True:
   x=b[i];i+=1;n=n*128+(x&127)
   if x<128:return n
 for tr in range(13):
  assert b[i:i+4]==b'MTrk';end=i+8+int.from_bytes(b[i+4:i+8],'big');i+=8;t=0;active=set();bend=None;cc={}
  while i<end:
   t+=vlq();s=b[i];i+=1
   if s==255:
    k=b[i];i+=1;n=vlq();v=b[i:i+n];i+=n
    if k==81:assert int.from_bytes(v,'big')==500000
    continue
   n=1 if s&240 in (192,208) else 2;v=b[i:i+n];i+=n
   if s&240==224:bend=v[0]+128*v[1]
   if s&240==176:cc[v[0]]=v[1]
   if s&240==144:
    assert v[0]==mapping[tr-1]['midi_note'] and v[0]%12 in [0,2,4,7,9];assert v[0] not in active;active.add(v[0]);total+=1
   if s&240==128:active.remove(v[0])
  assert not active and t==duration*1920
  if tr:
   assert cc[6]==2 and cc[38]==0
   if '_Bitwig' in p.name:assert bend==8192
   else:
    v=mapping[tr-1];f=440*2**((v['midi_note']-69+(bend-8192)*2/8192)/12)
    assert abs(1200*math.log2(f/v['frequency_hz']))<.013
 assert i==len(b);assert total==(809 if duration==480 else 16150)
 print(p.name,': timing, note map, tuning and note-offs passed')
s=[x for x in (O/'Lovophone_Pentatonic_Bitwig.scl').read_text().splitlines() if x and not x.startswith('!')];assert int(s[1])==len(s[2:])==12
c=[1200*math.log2(float(Fraction(x))) if '/' in x else float(x) for x in s[2:]];assert c==sorted(c) and c[-1]==1200
for v in mapping:
 sem=v['midi_note']%12;off=0 if sem==0 else c[sem-1]-100*sem
 assert abs(off-v['correction_cents'])<1e-8
print('Scala: 12 ascending entries; all MIDI pitches match intended pentatonic ratios.')
