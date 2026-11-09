import shutil
import sys,math,json,csv,subprocess,wave,re,shutil
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'outputs/LeLovophon_Direct_Gear_Prototype/Axle_Clearance_Revision/Sound';lib=R/'work/harp_samples/ConcertHarp-SFZ-20200702';SR=48000;N=480*SR
report=json.loads((O/'Sound_Details.json').read_text());events=list(csv.DictReader((O/'LeLovophon_8min_Pluck_Times.csv').open()));regions=[]
for block in (lib/'ConcertHarp-20200702.sfz').read_text().split('<region>')[1:]:regions.append(dict(re.findall(r'(\w+)=([^\s]+)',block)))
audio=np.zeros((N,2),np.float32);sources=[]
for voice in report['voices']:
 note=voice['midi_note'];reg=next(x for x in regions if int(x.get('lokey',0))<=note<=int(x.get('hikey',127)) and int(x.get('lovel',0))<=84<=int(x.get('hivel',127)))
 source=lib/reg['sample'];raw=subprocess.check_output([(shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'),'-v','error','-i',str(source),'-ar',str(SR),'-ac','2','-f','f32le','pipe:1']);sig=np.frombuffer(raw,np.float32).reshape(-1,2)
 # Honor the library's measured fine-tuning compensation, then apply our JI correction.
 cents=100*(note-int(reg['pitch_keycenter']))+float(reg.get('tune',0))+voice['correction_cents'];speed=2**(cents/1200)
 pos=np.arange(int(len(sig)/speed))*speed;idx=np.arange(len(sig));s=np.column_stack([np.interp(pos,idx,sig[:,ch]) for ch in range(2)]).astype(np.float32)
 s[-min(1440,len(s)):]*=np.linspace(1,0,min(1440,len(s)))[:,None]
 # Keep recorded stereo and gentle spatial separation; no per-sample peak normalization.
 pan=(voice['string']-6.5)/5.5*.25;s[:,0]*=math.sqrt(1-pan);s[:,1]*=math.sqrt(1+pan)
 for e in events:
  if int(e['string'])!=voice['string']:continue
  start=round(float(e['video_audio_seconds'])*SR);count=min(len(s),N-start);audio[start:start+count]+=s[:count]
  if count<len(s):audio[:len(s)-count]+=s[count:]
 sources.append(dict(string=voice['string'],sample=reg['sample'],sample_keycenter=int(reg['pitch_keycenter']),library_tune_cents=float(reg.get('tune',0)),ji_correction_cents=voice['correction_cents'],playback_speed=speed,duration_seconds=len(s)/SR))
 print('HARP',voice['note'],source.name,flush=True)
peak=float(np.max(np.abs(audio)));audio*=10**(-1/20)/peak
wav=O/'LeLovophon_8min_Sampled_Harp.wav'
with wave.open(str(wav),'wb') as w:
 w.setnchannels(2);w.setsampwidth(3);w.setframerate(SR)
 for start in range(0,N,SR*10):
  pcm=np.rint(audio[start:start+SR*10].reshape(-1)*8388607).astype(np.int32);packed=np.empty((len(pcm),3),np.uint8)
  for k in range(3):packed[:,k]=(pcm>>(8*k))&255
  w.writeframes(packed.tobytes())
subprocess.run([(shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'),'-v','error','-y','-i',str(wav),'-c:a','libmp3lame','-b:a','320k',str(O/'LeLovophon_8min_Sampled_Harp.mp3')],check=True)
video=O.parent/'360_Orbit'
if (video/'LeLovophon_360_8min_Blue.mp4').exists():
 subprocess.run([(shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'),'-v','error','-y','-i',str(video/'LeLovophon_360_8min_Blue.mp4'),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-t','480','-movflags','+faststart',str(video/'LeLovophon_360_8min_Concert_Harp.mp4')],check=True)
else:print('Optional older-view movie omitted; sampled audio has been generated.',flush=True)
shutil.copyfile(lib/'readme.txt',O/'Concert_Harp_Sample_Credits.txt')
(O/'Sampled_Harp_Details.json').write_text(json.dumps(dict(duration_seconds=480,source='https://freepats.zenvoid.org/OrchestralStrings/harp.html',licence='CC0 1.0',performer='K. Smith',original_library='Versilian Community Sample Library, Versilian Studios LLC',mapping='FreePats Concert Harp 2020-07-02',sources=sources,total_plucks=len(events),timing='Unchanged corrected-video CSV and MIDI',audio='Original sampled stereo, medium-soft layer, library tuning compensation plus JI offsets, no added reverb, tails wrap at loop boundary, global peak -1 dBFS',previous_synthetic_version_retained=True),indent=2));print('COMPLETE',flush=True)
