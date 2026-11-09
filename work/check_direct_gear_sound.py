import shutil
from pathlib import Path
import json,struct,csv,wave,subprocess
import numpy as np
O=Path(__file__).resolve().parents[1]/'outputs/LeLovophon_Direct_Gear_Prototype/Axle_Clearance_Revision/Sound'
report=json.loads((O/'Sound_Details.json').read_text());csvrows=list(csv.DictReader((O/'LeLovophon_8min_Pluck_Times.csv').open()));checks={}
def vlq(b,i):
 n=0
 while True:
  x=b[i];i+=1;n=(n<<7)|(x&127)
  if not x&128:return n,i
for variant in ['Bitwig_Scala','Just_Intonation']:
 b=(O/f'LeLovophon_8min_{variant}.mid').read_bytes();assert b[:4]==b'MThd';assert struct.unpack('>IHHH',b[4:14])==(6,1,13,960);i=14;allons=[];ends=[];bend_errors=[]
 for tr in range(13):
  assert b[i:i+4]==b'MTrk';size=struct.unpack('>I',b[i+4:i+8])[0];i+=8;end=i+size;t=0;active=set();on=[];bend=None
  while i<end:
   dt,i=vlq(b,i);t+=dt;status=b[i];i+=1
   if status==255:
    typ=b[i];i+=1;length,i=vlq(b,i);val=b[i:i+length];i+=length
    if typ==81:assert val==bytes([7,161,32])
   else:
    ln=1 if status&240 in [192,208] else 2;v=b[i:i+ln];i+=ln;key=(status&15,v[0])
    if status&240==224:bend=v[0]+128*v[1]
    if status&240==144:
     assert key not in active,(tr,t);active.add(key);on.append(t);assert v[0]==report['voices'][tr-1]['midi_note']
    elif status&240==128:assert key in active;active.remove(key)
  assert not active;assert t==921600;ends.append(t)
  if tr:
   v=report['voices'][tr-1];expected=[round(float(e['video_audio_seconds'])*1920) for e in csvrows if int(e['string'])==tr];assert on==expected;allons+=on
   if variant=='Just_Intonation':bend_errors.append(abs((bend-8192)/8192*200-v['correction_cents']))
   else:assert bend==8192
 assert len(allons)==1350 and i==len(b);checks[variant]=dict(note_ons=len(allons),string_tracks=12,duration_seconds=ends[0]/1920,balanced_notes=True,maximum_pitch_bend_error_cents=max(bend_errors,default=0),maximum_timing_rounding_ms=max(abs(round(float(e['video_audio_seconds'])*1920)/1920-float(e['video_audio_seconds']))*1000 for e in csvrows))
p=O/'LeLovophon_8min_Nylon_Preview.wav';peak=0;energy=0;count=0
with wave.open(str(p),'rb') as w:
 assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(2,3,48000,23040000)
 while True:
  raw=w.readframes(480000)
  if not raw:break
  x=np.frombuffer(raw,np.uint8).reshape(-1,3).astype(np.int32);v=x[:,0]|(x[:,1]<<8)|(x[:,2]<<16);v=(v^8388608)-8388608;peak=max(peak,int(np.max(np.abs(v))));energy+=float(np.sum((v.astype(float)/8388607)**2));count+=len(v)
assert 0<peak<8388607
checks['audio']=dict(duration_seconds=480,sample_rate=48000,bit_depth=24,channels=2,peak_dbfs=float(20*np.log10(peak/8388607)),rms_dbfs=float(10*np.log10(energy/count)),clipping=False)
subprocess.run([(shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'),'-v','error','-i',str(O/'LeLovophon_8min_Nylon_Preview.mp3'),'-f','null','-'],check=True)
(O/'Sound_Verification.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
