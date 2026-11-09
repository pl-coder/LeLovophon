"""Export a local film at higher speed with pitch-preserved audio; no media is tracked."""
import argparse,json,math,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
base=ROOT/'outputs/LeLovophon_Direct_Gear_Prototype/Axle_Clearance_Revision/Paris_Close_Studio'
parser.add_argument('source',nargs='?',type=Path,default=base/'LeLovophon_Paris_Close_16min.mp4')
parser.add_argument('--output',type=Path,default=base/'LeLovophon_Paris_Close_30sec_Synced.mp4')
parser.add_argument('--seconds',type=float,default=30)
args=parser.parse_args();assert args.seconds>0
ff=shutil.which('ffmpeg');probe=shutil.which('ffprobe');assert ff and probe,'Install FFmpeg and FFprobe on PATH.'
info=json.loads(subprocess.check_output([probe,'-v','error','-show_entries','format=duration','-of','json',str(args.source)]));speed=float(info['format']['duration'])/args.seconds
assert speed>=1,'This recipe accelerates a longer film.'
remaining=speed;stages=[]
while remaining>2:stages.append('atempo=2');remaining/=2
stages.append(f'atempo={remaining:.12g}')
args.output.parent.mkdir(parents=True,exist_ok=True);(ROOT/'work').mkdir(exist_ok=True)
def run(cmd):subprocess.run([ff,'-v','error','-y']+cmd,check=True)
with tempfile.TemporaryDirectory(prefix='lovophon-short-',dir=ROOT/'work') as tmp:
 tmp=Path(tmp);audio=tmp/'audio.wav';picture=tmp/'picture.mp4'
 run(['-i',str(args.source),'-vn','-af',','.join(stages+['apad',f'afade=t=out:st={max(0,args.seconds-1)}:d=1']),'-t',str(args.seconds),'-c:a','pcm_s24le',str(audio)])
 run(['-i',str(args.source),'-an','-vf',f'setpts=(PTS-STARTPTS)/{speed:.12g},fps=24','-t',str(args.seconds),'-c:v','libx264','-preset','medium','-crf','16','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',str(picture)])
 run(['-i',str(picture),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-t',str(args.seconds),'-movflags','+faststart',str(args.output)])
info=json.loads(subprocess.check_output([probe,'-v','error','-show_entries','stream=codec_type,duration,nb_frames:format=duration','-of','json',str(args.output)]));assert abs(float(info['format']['duration'])-args.seconds)<.05
for stream in info['streams']:assert abs(float(stream['duration'])-args.seconds)<.05
subprocess.run([ff,'-v','error','-i',str(args.output),'-f','null','-'],check=True)
args.output.with_suffix('.verification.json').write_text(json.dumps(dict(speed=speed,pitch_preserved=True,full_decode_passed=True,export=info),indent=2))
print(args.output)
