import shutil
import sys,math,json,csv,struct,wave,subprocess,shutil
from pathlib import Path
import numpy as np
from direct_gear_math import ROWS,angle
R=Path(__file__).resolve().parents[1];O=R/'outputs/LeLovophon_Direct_Gear_Prototype/Axle_Clearance_Revision/Sound';O.mkdir(exist_ok=True)
SR=48000;DURATION=480;N=SR*DURATION;SCALE=5759/5760;PPQ=960;TPS=1920;END=480*TPS
notes=[48,50,52,55,57,60,62,64,67,69,72,74];channels=[0,1,2,3,4,5,6,7,8,10,11,12]
voices=[];events=[]
for row,note,ch in zip(ROWS,notes,channels):
 phase=row['phase_rad'];roots=[]
 for j in range(1,2001):
  lo=(j-1)*2*math.pi/2000;hi=j*2*math.pi/2000
  if lo<1e-8:lo=1e-8
  if angle(row,phase+lo)*angle(row,phase+hi)<0:
   a=angle(row,phase+lo)
   for _ in range(50):
    mid=(lo+hi)/2
    if a*angle(row,phase+mid)>0:lo=mid
    else:hi=mid
   root=(lo+hi)/2
   if root<2*math.pi-1e-7:roots.append(root)
 assert len(roots)==1,(row['note'],roots)
 ratio=float(__import__('fractions').Fraction(row['ratio']));period=20/ratio;delta=roots[0]/(2*math.pi)*period
 v=dict(string=row['index'],note=row['note'],midi_note=note,channel=ch+1,ratio=row['ratio'],frequency_hz=130.8127826502993*ratio,nominal_period_seconds=period,return_crossing_seconds=delta)
 v['correction_cents']=1200*math.log2(ratio)-100*(note-48);ve=[]
 for k in range(int(math.ceil(480/period))):
  for direction,offset in [('outward',0),('return',delta)]:
   t=k*period+offset
   if t>=480-1e-7:continue
   e=dict(string=row['index'],note=row['note'],direction=direction,mechanism_seconds=t,video_audio_seconds=t*SCALE,frequency_hz=v['frequency_hz']);events.append(e);ve.append(e)
 v['pluck_count']=len(ve);v['events']=ve;voices.append(v)
events.sort(key=lambda e:(e['video_audio_seconds'],e['string']))
with (O/'LeLovophon_8min_Pluck_Times.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=events[0].keys());w.writeheader();w.writerows(events)
def vlq(n):
 b=[n&127];n>>=7
 while n:b.insert(0,(n&127)|128);n>>=7
 return bytes(b)
def meta(k,v):
 if isinstance(v,str):v=v.encode('ascii')
 return bytes([255,k])+vlq(len(v))+v
def track(es):
 es.sort(key=lambda e:(e[0],e[1]));last=0;b=bytearray()
 for t,p,msg in es:b+=vlq(t-last)+msg;last=t
 return b'MTrk'+struct.pack('>I',len(b))+b
for ji in [False,True]:
 tracks=[track([(0,0,meta(3,'Le Lovophon corrected direct gear - 8 minute film')),(0,1,meta(81,(500000).to_bytes(3,'big'))),(0,2,meta(88,bytes([4,2,24,8]))),(END,99,meta(47,b''))])]
 for v in voices:
  ch=v['channel']-1;note=v['midi_note'];bend=round(8192+v['correction_cents']/200*8192) if ji else 8192
  es=[(0,0,meta(3,f"String {v['string']:02d} {v['note']} ratio {v['ratio']}")),(0,1,meta(32,bytes([ch]))),(0,2,bytes([192|ch,24]))]
  for j,(cc,val) in enumerate([(101,0),(100,0),(6,2),(38,0),(101,127),(100,127)]):es.append((0,3+j,bytes([176|ch,cc,val])))
  es.append((0,10,bytes([224|ch,bend&127,bend>>7])))
  for e in v['events']:
   tick=round(e['video_audio_seconds']*TPS);es.extend([(tick,30,bytes([144|ch,note,84])),(min(END,tick+int(1.8*TPS)),20,bytes([128|ch,note,0]))])
  es.extend([(END,90,bytes([176|ch,123,0])),(END,99,meta(47,b''))]);tracks.append(track(es))
 name='LeLovophon_8min_'+('Just_Intonation' if ji else 'Bitwig_Scala')+'.mid';(O/name).write_bytes(b'MThd'+struct.pack('>IHHH',6,1,13,PPQ)+b''.join(tracks))
shutil.copyfile(R/'outputs/Lovophone_Pentatonic_Bitwig.scl',O/'LeLovophon_Pentatonic.scl')
# Deterministic harmonic plucked-string audition; no claimed acoustic measurement.
audio=np.zeros((N,2),dtype=np.float32)
for v,row in zip(voices,ROWS):
 f=v['frequency_hz'];length=int(10*SR);t=np.arange(length,dtype=np.float64)/SR;sig=np.zeros(length);pos=(row['pick_x']-row['bridge_x'])/(320-row['bridge_x']);tau=2.9*(130.8127826502993/f)**.30
 for h in range(1,min(65,int(18000/f))):
  amp=math.sin(math.pi*h*pos)/(h**1.65);sig+=amp*np.sin(2*math.pi*f*h*t)*np.exp(-t/(tau/(1+.17*(h-1))))
 sig*=np.minimum(t/.0015,1);sig[-2400:]*=np.linspace(1,0,2400);sig/=np.max(np.abs(sig));sig=(sig*.24).astype(np.float32)
 pan=-.6+1.2*(v['string']-1)/11;gain=[math.cos((pan+1)*math.pi/4),math.sin((pan+1)*math.pi/4)]
 for e in v['events']:
  start=round(e['video_audio_seconds']*SR);count=min(length,N-start)
  for ch in range(2):
   audio[start:start+count,ch]+=sig[:count]*gain[ch]
   # Circular tails permit repeated playback without chopping the last strings.
   if count<length:audio[:length-count,ch]+=sig[count:]*gain[ch]
 print('VOICE',v['note'],v['pluck_count'],flush=True)
peak=float(np.max(np.abs(audio)));audio*=10**(-1/20)/peak
wav=O/'LeLovophon_8min_Nylon_Preview.wav'
with wave.open(str(wav),'wb') as w:
 w.setnchannels(2);w.setsampwidth(3);w.setframerate(SR)
 for start in range(0,N,SR*10):
  pcm=np.rint(audio[start:start+SR*10].reshape(-1)*8388607).astype(np.int32);packed=np.empty((len(pcm),3),dtype=np.uint8)
  for k in range(3):packed[:,k]=(pcm>>(8*k))&255
  w.writeframes(packed.tobytes())
subprocess.run([(shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'),'-v','error','-y','-i',str(wav),'-c:a','libmp3lame','-b:a','320k',str(O/'LeLovophon_8min_Nylon_Preview.mp3')],check=True)
for v in voices:v.pop('events')
report=dict(duration_seconds=480,sample_rate=SR,total_plucks=len(events),tempo_bpm=120,midi_tracks=13,string_tracks=12,voices=voices,video_clock_scale=SCALE,clock_note='Matches endpoint-inclusive corrected 360 film: frame index/12 = mechanism seconds *5759/5760. No duplicate end-of-cycle note at final zero frame; next loop begins with the shared zero pluck.',audio='Synthesized harmonic nylon-like pluck; not a recording or prediction of the unbuilt soundbox. Stereo pan low to high, fixed velocity, no reverb. Circular decay tails from preceding cycle, peak normalized to -1 dBFS.',physical_test_passed=False)
(O/'Sound_Details.json').write_text(json.dumps(report,indent=2));print('COMPLETE',len(events),flush=True)
(O/'Readme.md').write_text('''# Le Lovophon — corrected direct-gear film soundtrack

The WAV is an exactly eight-minute, 48 kHz, 24-bit stereo synthesized nylon-like string audition, tuned to the established C-based just-intonation pentatonic ratios. The MP3 is a convenient listening copy. This is not a recording or an acoustic prediction of the unbuilt instrument. There is no reverb; decays wrap around the loop rather than being cut off.

Plucks occur at both centre crossings of each exact crank-rocker mechanism, including its unequal outward/return timing. These supersede the old Lab Frame/Unified MIDI for this corrected direct-gear video. The audio and both MIDI variants share one event list.

In Bitwig, use 120 BPM, place the audio/video/MIDI at the same zero, and import the twelve string tracks into your group. The duration is 240 bars in 4/4. Octave names can differ: MIDI 48 is our C3, 130.8127826503 Hz.

For Bitwig with the supplied Scala tuning, use LeLovophon_8min_Bitwig_Scala.mid and apply LeLovophon_Pentatonic.scl to every instrument, with conventional C-based mapping and C3 at 130.8127826503 Hz. This MIDI has neutral pitch bend. Alternatively use LeLovophon_8min_Just_Intonation.mid with ordinary equal-tempered instruments that honor each track's pitch-bend channel and +/-2-semitone range. Do not combine pitch-bend tuning with Scala tuning. The WAV already has the correct tuning.

The current film samples both zero and 480 seconds in 5760 images. To match those images, internal pluck times are scaled by 5759/5760 (less than 0.02%). There is no additional duplicate pluck on its closing zero frame: that belongs to the next loop. No opening silence, no count-in. The CSV includes both mechanism and film/audio times. MIDI event rounding is at most 0.261 milliseconds. Gate lengths are 1.8 seconds; your chosen synth envelope controls the audible decay.

The prototype assumes picks release on both passes. Actual pick-release deflection, string tension and measured sound remain bench-test questions. Files stay local.
''')
