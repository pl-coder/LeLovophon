import shutil
from pathlib import Path
import subprocess,json,wave,math
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'outputs/LeLovophon_Direct_Gear_Prototype/Axle_Clearance_Revision/Paris_Close_Studio';O.mkdir(exist_ok=True);SR=48000
source=R/'outputs/LeLovophon_Direct_Gear_Prototype/Axle_Clearance_Revision/Sound/LeLovophon_8min_Sampled_Harp.wav'
def decode(path,filters=None):
 cmd=[(shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'),'-v','error','-i',str(path)]
 if filters:cmd+=['-af',filters]
 return np.frombuffer(subprocess.check_output(cmd+['-ar',str(SR),'-ac','2','-f','f32le','pipe:1']),np.float32).reshape(-1,2)
dry=decode(source);ir=decode(R/'work/studio_ir/French 18th Century Salon.wav','highpass=f=180,lowpass=f=6500');on=int(np.argmax(np.max(np.abs(ir),axis=1)));ir=ir[on:].copy();ir[:96]*=np.linspace(0,1,96)[:,None];ir[-7200:]*=np.linspace(1,0,7200)[:,None];ir=np.pad(ir,((576,0),(0,0)))
# FFT overlap-add; circular tail preserves the already looped harp recording.
N=len(dry);L=len(ir);block=131072;size=1<<(block+L-2).bit_length();wet=np.zeros_like(dry)
for ch in range(2):
 H=np.fft.rfft(ir[:,ch],size);out=np.zeros(N+L-1,np.float32)
 for start in range(0,N,block):
  count=min(block,N-start);y=np.fft.irfft(np.fft.rfft(dry[start:start+count,ch],size)*H,size)[:count+L-1];out[start:start+len(y)]+=y.astype(np.float32)
 wet[:,ch]=out[:N];wet[:L-1,ch]+=out[N:]
rms_dry=float(np.sqrt(np.mean(dry.astype(float)**2)));rms_wet=float(np.sqrt(np.mean(wet.astype(float)**2)));gain=rms_dry/rms_wet*10**(-16/20);audio=dry+gain*wet;audio*=10**(-1/20)/np.max(np.abs(audio));file=O/'LeLovophon_8min_Harp_Salon.wav'
with wave.open(str(file),'wb') as w:
 w.setnchannels(2);w.setsampwidth(3);w.setframerate(SR)
 for start in range(0,N,480000):
  pcm=np.rint(audio[start:start+480000].reshape(-1)*8388607).astype(np.int32);b=np.empty((len(pcm),3),np.uint8)
  for k in range(3):b[:,k]=(pcm>>(k*8))&255
  w.writeframes(b.tobytes())
subprocess.run([(shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'),'-v','error','-y','-i',str(file),'-c:a','libmp3lame','-b:a','320k',str(O/'LeLovophon_8min_Harp_Salon.mp3')],check=True)
(O/'Salon_Reverb_Details.json').write_text(json.dumps(dict(source='https://www.voxengo.com/impulses/',response='French 18th Century Salon',creator='Aleksey Vaneev / Voxengo',type='Modelled room impulse response, not measured Paris studio acoustics',licence='Royalty-free processing including commercial usage; raw IR not redistributed',processing='Stereo convolution, dry timing untouched, IR aligned to main arrival, first 2 ms faded, 12 ms predelay, wet-only highpass 180 Hz and lowpass 6.5 kHz, final 150 ms IR fade',wet_relative_dry_rms_db=-16,wet_gain=gain,duration_seconds=N/SR,tail='Circular convolution tail, no extra time or cutoff',peak_dbfs=-1),indent=2));print('CONVOLUTION_COMPLETE',flush=True)
