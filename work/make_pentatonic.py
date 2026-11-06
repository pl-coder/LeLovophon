import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
from pathlib import Path
from fractions import Fraction
import csv,json,math,struct
R=Path((_LOVOPHON_WORKSPACE + '')); O=R/'outputs'
old=json.loads((O/'Lovophone_160min_MIDI_Details.json').read_text())['voices']
notes=[48,50,52,55,57,60,62,64,67,69,72,74]
labels=['C3','D3','E3','G3','A3','C4','D4','E4','G4','A4','C5','D5']
ratios=list(map(Fraction,['1','9/8','5/4','3/2','5/3','2','9/4','5/2','3','10/3','4','9/2']))
rows=list(csv.DictReader((O/'Lovophone_160min_Pluck_Times.csv').open()))
def vlq(n):
 a=[n&127];n>>=7
 while n:a.insert(0,(n&127)|128);n>>=7
 return bytes(a)
def meta(k,s):
 if isinstance(s,str):s=s.encode('ascii')
 return bytes([255,k])+vlq(len(s))+s
def track(es):
 es.sort(key=lambda e:(e[0],e[1]));last=0;b=bytearray()
 for t,p,m in es:b+=vlq(t-last)+m;last=t
 return b'MTrk'+struct.pack('>I',len(b))+b
mapping=[]
for i,(note,ratio,label,v) in enumerate(zip(notes,ratios,labels,old)):
 cents=1200*math.log2(float(ratio))-100*(note-48)
 mapping.append(dict(string=i+1,note=label,midi_note=note,ratio_to_C3=str(ratio),frequency_hz=130.8127826502993*float(ratio),correction_cents=cents,channel=v['channel'],timing_source=v['note']))
for duration in [480,9600]:
 for ji in [False,True]:
  end=duration*1920
  ts=[track([(0,0,meta(3,'Lovophone pentatonic audition')),(0,1,meta(81,(500000).to_bytes(3,'big'))),(0,2,meta(88,bytes([4,2,24,8]))),(0,3,meta(1,'Existing mechanical trigger timings retained. New pitches only; CAD unchanged.')),(end,99,meta(47,b''))])]
  count=0
  for v in mapping:
   ch=v['channel']-1;n=v['midi_note'];bend=round(8192+v['correction_cents']/200*8192) if ji else 8192
   es=[(0,0,meta(3,f"String {v['string']:02d} - {v['note']}")),(0,1,meta(32,bytes([ch]))),(0,2,bytes([192|ch,24]))]
   for j,(cc,val) in enumerate([(101,0),(100,0),(6,2),(38,0),(101,127),(100,127)]):es.append((0,3+j,bytes([176|ch,cc,val])))
   es.append((0,10,bytes([224|ch,bend&127,bend>>7])))
   for e in rows:
    t=float(e['seconds'])
    if int(e['midi_channel_1_based'])!=v['channel'] or t>=duration:continue
    es.extend([(round(t*1920),30,bytes([144|ch,n,84])),(min(end,round((t+2)*1920)),20,bytes([128|ch,n,0]))]);count+=1
   es.extend([(end,90,bytes([176|ch,123,0])),(end,99,meta(47,b''))]);ts.append(track(es))
  name=f"Lovophone_Pentatonic_{duration//60}min_{'Just_Intonation' if ji else 'Bitwig'}.mid"
  (O/name).write_bytes(b'MThd'+struct.pack('>IHHH',6,1,13,960)+b''.join(ts))
  print(name,count)
# Conventional chromatic key layout. Only C D E G A occur in the accompanying MIDI.
scale=['100.000000','9/8','300.000000','5/4','500.000000','600.000000','3/2','800.000000','5/3','1000.000000','1100.000000','2/1']
s='! Lovophone_Pentatonic_Bitwig.scl\n! C D E G A tuned in just intonation; unused keys remain equal tempered.\nLovophone major pentatonic on conventional C D E G A keys\n12\n!\n'+'\n'.join(scale)+'\n'
(O/'Lovophone_Pentatonic_Bitwig.scl').write_text(s,encoding='ascii')
(O/'Lovophone_Pentatonic_Note_Map.json').write_text(json.dumps({'purpose':'Pitch audition; existing CAD timings retained; CAD bridges and drivetrain unchanged','reference':'MIDI 48 = C3 = 130.8127826502993 Hz; octave labels may differ in your DAW','voices':mapping},indent=2))
(O/'Lovophone_Pentatonic_Setup.md').write_text('''# Lovophone pentatonic audition

Use Lovophone_Pentatonic_8min_Bitwig.mid for a first listen, or Lovophone_Pentatonic_160min_Bitwig.mid for the whole existing timing cycle. Set tempo to 120 BPM; do not quantize.

On every string track: Micro-pitch, then a Bitwig instrument. Drag Lovophone_Pentatonic_Bitwig.scl onto Micro-pitch. Root C, Amount 100%, reference 440 Hz. Replace the previous tuning rather than stacking another Micro-pitch. The supplied MIDI uses only C D E G A. The file has 12 entries to meet Bitwig's import requirements; the seven unused pitch classes remain equal tempered.

Alternatively, use the Just_Intonation MIDI copies with a pitch-bend-aware instrument and no Scala/Micro-pitch tuning. These contain independent channel pitch bends with a +/-2 semitone range. Do not combine the two tuning methods.

String order, low to high: C3 D3 E3 G3 A3 C4 D4 E4 G4 A4 C5 D5 (MIDI 48 50 52 55 57 60 62 64 67 69 72 74). These are scientific octave names; your DAW may display different octave numbers. The range is chosen for audition, not yet checked against physical bridge placement or string gauges.

Pure pitch ratios within each octave: C 1, D 9/8, E 5/4, G 3/2, A 5/3. Notes retain the original 2-second MIDI duration, velocity and each mechanism's actual trigger schedule so the pitch change can be compared directly. Adjust your instrument's decay for a plucked sound.

The 160-minute file retains the OLD drivetrain timing cycle; it is not a new pitch-to-speed-matched mechanical design. No CAD bridge, arm or drive geometry has been changed. Approve the sound before redesigning those parts. The eight-minute file is an excerpt, not a complete repeat.
''')
