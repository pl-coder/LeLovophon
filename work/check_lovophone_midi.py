import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
from pathlib import Path
import struct,json
O=Path((_LOVOPHON_WORKSPACE + '/outputs'))
def readvlq(b,i):
 n=0
 for _ in range(4):
  x=b[i];i+=1;n=(n<<7)|(x&127)
  if not x&128:return n,i
 raise AssertionError('VLQ too long')
for name in ['Lovophone_160min_Just_Intonation.mid','Lovophone_160min_Equal_Temperament.mid']:
 b=(O/name).read_bytes();assert b[:4]==b'MThd';length,fmt,nt,ppq=struct.unpack('>IHHH',b[4:14]);assert (length,fmt,nt,ppq)==(6,1,13,960);i=14;counts=[];ends=[]
 for track in range(nt):
  assert b[i:i+4]==b'MTrk';sz=struct.unpack('>I',b[i+4:i+8])[0];i+=8;end=i+sz;t=0;active=set();n=0
  while i<end:
   dt,i=readvlq(b,i);t+=dt;status=b[i];i+=1
   if status==255:
    typ=b[i];i+=1;ln,i=readvlq(b,i);val=b[i:i+ln];i+=ln
    if typ==0x2f:assert i==end
    if typ==0x51:assert int.from_bytes(val,'big')==500000
   else:
    assert status>=0x80
    ln=1 if status&0xf0 in [0xc0,0xd0] else 2;vals=b[i:i+ln];i+=ln
    if status&0xf0==0x90 and vals[1]>0:
     key=(status&15,vals[0]);assert key not in active;active.add(key);n+=1
    if status&0xf0==0x80 or (status&0xf0==0x90 and vals[1]==0):active.remove((status&15,vals[0]))
  assert not active;assert t==18_432_000,(track,t);counts.append(n);ends.append(t)
 assert i==len(b);assert sum(counts)==16150
 print(name,{'duration_seconds':ends[0]*.5/ppq,'note_ons':sum(counts),'tracks':nt,'balanced_note_offs':True})
p=O/'Lovophone_MIDI_Readme.md';p.write_text(p.read_text().replace('17,150','16,150'))
