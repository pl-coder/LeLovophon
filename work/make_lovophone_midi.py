import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
from pathlib import Path
from fractions import Fraction
import json,math,struct,csv
ROOT=Path((_LOVOPHON_WORKSPACE + ''));OUT=ROOT/'outputs';rows=json.loads((ROOT/'work/twelve_motion_map.json').read_text())['rows']
DURATION=9600;PPQ=960;TEMPO=500000;TPS=PPQ*1_000_000/TEMPO;END=round(DURATION*TPS)
channels=[0,1,2,3,4,5,6,7,8,10,11,12];notes=list(range(60,72));tracks=[];events_csv=[];summary=[]
def vlq(n):
 assert 0<=n<0x10000000
 a=[n&127];n>>=7
 while n:a.insert(0,(n&127)|128);n>>=7
 return bytes(a)
def meta(k,s):
 if isinstance(s,str):s=s.encode('utf-8')
 return bytes([255,k])+vlq(len(s))+s
def chunk(events):
 events.sort(key=lambda x:(x[0],x[1]));buf=bytearray();last=0
 for tick,order,msg in events:buf+=vlq(tick-last)+msg;last=tick
 return b'MTrk'+struct.pack('>I',len(buf))+buf
def beta(r,phi):
 th=-phi;uy,uz=r['follower_y'],r['follower_z'];cy=-59-4*math.sin(th);cz=-116+4*math.cos(th);vy,vz=cy-uy,cz-uz;d=math.hypot(vy,vz);vy/=d;vz/=d;a=(r['lever_length']**2-225+d*d)/(2*d);h=math.sqrt(max(0,r['lever_length']**2-a*a));py,pz=uy+vy*a,uz+vz*a;b1=(py-vz*h,pz+vy*h);b2=(py+vz*h,pz-vy*h);by,bz=b1 if b1[0]>b2[0] else b2;return math.atan2(-(by-uy),bz-uz)
def crossings(r):
 def f(x):b=beta(r,x)-r['beta_mid'];return math.atan2(math.sin(b),math.cos(b))
 roots=[];a=0;fa=f(a)
 for j in range(1,2049):
  b=2*math.pi*j/2048;fb=f(b)
  if fa*fb<0:
   lo,hi=a,b;fl=fa
   for _ in range(55):
    mid=(lo+hi)/2;fm=f(mid)
    if fl*fm<=0:hi=mid
    else:lo=mid;fl=fm
   rt=(lo+hi)/2
   if not roots or abs(rt-roots[-1])>1e-8:roots.append(rt)
  a,fa=b,fb
 assert len(roots)==2,(r['note'],roots)
 return roots
conductor=[(0,0,meta(3,'Le Lovophone — 160-minute just-intonation cycle')),(0,1,meta(0x51,TEMPO.to_bytes(3,'big'))),(0,2,meta(0x58,bytes([4,2,24,8]))),(0,3,meta(1,'Normal model speed: C drive 3 rpm. Two centre-crossing plucks per cam revolution. C4 reference. Per-channel pitch bend, range +/-2 semitones.')),(0,4,meta(6,'Cycle start')),(END,5,meta(6,'Full twelve-voice cycle complete')),(END,99,meta(0x2f,b''))]
ji=[chunk(conductor)];et=[chunk([(t,o,m if not (t==0 and o==0) else meta(3,'Le Lovophone — 160-minute equal-temperament compatibility copy')) for t,o,m in conductor])]
for i,r in enumerate(rows):
 ch=channels[i];note=notes[i];name=r.get('display_note',r['note']);ratio=Fraction(r['ratio']).limit_denominator(1000);cents=1200*math.log2(float(ratio))-100*i;bend=round(8192+cents/200*8192);freq=261.6255653005986*float(ratio);period=20/float(ratio);roots=crossings(r)
 initial=[(0,0,meta(3,name+' — '+str(ratio)+' of C')),(0,1,meta(0x20,bytes([ch]))),(0,2,meta(1,f'Pitch {freq:.9f} Hz; correction {cents:+.6f} cents; speaking length {r["speaking_length"]:.6f} mm.')),(0,3,bytes([0xc0|ch,24])),(0,4,bytes([0xb0|ch,7,100])),(0,5,bytes([0xb0|ch,11,127]))]
 # RPN 0: independent +/-2 semitone pitch-bend sensitivity on each string channel.
 for order,cc,val in [(6,101,0),(7,100,0),(8,6,2),(9,38,0),(10,101,127),(11,100,127)]:initial.append((0,order,bytes([0xb0|ch,cc,val])))
 e=initial+[(0,12,bytes([0xe0|ch,bend&127,(bend>>7)&127]))];compat=initial+[(0,12,bytes([0xe0|ch,0,64]))];count=0
 for k in range(math.ceil(DURATION/period)+1):
  for direction,phi in enumerate(roots):
   t=(k+phi/(2*math.pi))*period
   if not 0<=t<DURATION:continue
   on=round(t*TPS);off=min(END,round((t+2)*TPS));velocity=84
   for target in [e,compat]:target.extend([(on,30,bytes([0x90|ch,note,velocity])),(off,20,bytes([0x80|ch,note,0]))])
   events_csv.append([f'{t:.9f}',name,ch+1,note,f'{freq:.9f}',f'{cents:.6f}',direction+1]);count+=1
 e.extend([(END,90,bytes([0xb0|ch,123,0])),(END,99,meta(0x2f,b''))]);compat.extend([(END,90,bytes([0xb0|ch,123,0])),(END,99,meta(0x2f,b''))]);ji.append(chunk(e));et.append(chunk(compat));assert count==int(960*ratio),(name,count,ratio)
 summary.append({'note':name,'ratio':str(ratio),'channel':ch+1,'midi_note':note,'frequency_hz':freq,'pitch_correction_cents':cents,'pitch_bend_14bit':bend,'pluck_count':count,'cycle_seconds':period,'pluck_phases_radians':roots})
header=b'MThd'+struct.pack('>IHHH',6,1,13,PPQ)
(OUT/'Lovophone_160min_Just_Intonation.mid').write_bytes(header+b''.join(ji));(OUT/'Lovophone_160min_Equal_Temperament.mid').write_bytes(header+b''.join(et))
with (OUT/'Lovophone_160min_Pluck_Times.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['seconds','string','midi_channel_1_based','midi_note','just_frequency_hz','pitch_correction_cents','crossing_in_cycle']);w.writerows(sorted(events_csv,key=lambda x:float(x[0])))
ratios=[Fraction(r['ratio']).limit_denominator(1000) for r in rows][1:]+[Fraction(2,1)]
(OUT/'Lovophone_Just_Intonation.scl').write_text('! Lovophone_Just_Intonation.scl\n! Root C; choose C4 / MIDI 60 as the reference when importing.\nLe Lovophone: twelve-note 5-limit just intonation\n12\n!\n'+'\n'.join(str(f.numerator)+'/'+str(f.denominator) for f in ratios)+'\n')
report={'duration_seconds':DURATION,'duration_minutes':160,'ppq':PPQ,'tempo_bpm':120,'C_reference':'C4, MIDI 60, 261.6255653 Hz','input_speed_rpm':3,'pluck_model':'Two actual beta=beta_mid crossings per cam cycle; preserves the CAD phase offsets and unequal half-cycle intervals.','total_plucks':len(events_csv),'voice_count':12,'note_duration_seconds':2,'voices':summary,'scope':'Idealized MIDI trigger schedule; no string acoustics, contact dynamics or motor-speed fluctuation. MIDI pitch bends require per-channel support. Equal-temperament copy deliberately omits the just-intonation corrections.'}
(OUT/'Lovophone_160min_MIDI_Details.json').write_text(json.dumps(report,indent=2))
(OUT/'Lovophone_MIDI_Readme.md').write_text('''# Le Lovophone — full 160-minute MIDI cycle

Open **Lovophone_160min_Just_Intonation.mid** for the intended tuning. It contains twelve string tracks plus a tempo track, at normal model speed: 3 rpm for the common axle, with two plucks per cam revolution. The complete pattern is 160 minutes and contains 17,150 plucks. Trigger times follow the model’s actual centre crossings, including its phase offsets and unequal half-cycle intervals.

The starting register is C4. Each string uses its own MIDI channel and a fixed pitch bend, with ±2-semitone bend sensitivity set by RPN. Channel 10 is avoided. The initial program is General MIDI nylon-string guitar; choose another sound if desired. A note lasts two seconds and is truncated at the end boundary when necessary. There is no generated audio in these files.

For correct just intonation, use a multitimbral instrument that respects pitch bend independently on each channel, or route each string track to a separate instrument instance. A plugin that treats all channels as one pitch-bend domain can detune the whole ensemble. The Scala file is an alternative tuning method: use it with the equal-tempered compatibility MIDI, root C / MIDI 60, **without** also applying the pitch-bend corrections. Applying both methods would double the correction.

**Lovophone_160min_Equal_Temperament.mid** preserves the identical timing and track layout with neutral pitch bends. It is a compatibility copy for plugins that ignore channel tuning. Without a Scala or other tuning map, it plays twelve-tone equal temperament rather than our just-intonation scale.

The CSV gives every trigger time. The JSON gives frequencies, pitch corrections, event counts and phase details. The schedule is an idealized mechanical performance: it does not simulate nylon vibration, contact force, motor fluctuation, dynamics or resonance. You can transpose the register, change the instrument and adjust note lengths in your DAW.
''')
print(json.dumps({'duration_minutes':160,'voices':12,'plucks':len(events_csv),'just_midi_bytes':(OUT/'Lovophone_160min_Just_Intonation.mid').stat().st_size},indent=2))
