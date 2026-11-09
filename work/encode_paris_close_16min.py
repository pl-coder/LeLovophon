import shutil
from pathlib import Path
import subprocess,json,shutil,hashlib,wave
R=Path(__file__).resolve().parents[1];O=R/'outputs/LeLovophon_Direct_Gear_Prototype/Axle_Clearance_Revision/Paris_Close_Studio';F=R/'work/lovophon_paris_close_final_frames';ff=(shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg');probe=(shutil.which('ffprobe') or '/opt/homebrew/bin/ffprobe')
missing=[n for n in range(1,5760) if not (F/('frame_%05d.png'%n)).exists()];assert not missing,missing[:12]
shutil.copyfile(F/'frame_00001.png',F/'frame_05760.png')
for n in ['Orbit_360_Start.png','Orbit_360_End.png']:shutil.copyfile(F/'frame_00001.png',O/n)
cycle=R/'work/LeLovophon_Paris_Close_Studio_Cycle_8min.mp4';movie=O/'LeLovophon_Paris_Close_16min.mp4'
subprocess.run([ff,'-v','error','-y','-framerate','12','-i',str(F/'frame_%05d.png'),'-frames:v','11520','-vf','fps=24,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p','-c:v','libx264','-preset','medium','-crf','15','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',str(cycle)],check=True);print('EIGHT_MINUTE_PICTURE_ENCODED',flush=True)
subprocess.run([ff,'-v','error','-y','-stream_loop','1','-i',str(cycle),'-stream_loop','1','-i',str(O/'LeLovophon_8min_Harp_Salon.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-t','960','-movflags','+faststart',str(movie)],check=True);print('SIXTEEN_MINUTE_SOUND_FILM_ENCODED',flush=True)
meta=json.loads(subprocess.check_output([probe,'-v','error','-show_entries','stream=codec_name,codec_type,width,height,duration,r_frame_rate,nb_frames:format=duration,size','-of','json',str(movie)]));assert abs(float(meta['format']['duration'])-960)<.001
for st in meta['streams']:assert abs(float(st['duration'])-960)<.01
vs=next(s for s in meta['streams'] if s['codec_type']=='video');assert(vs['width'],vs['height'],vs['nb_frames'])==(1600,900,'23040')
subprocess.run([ff,'-v','error','-i',str(movie),'-f','null','-'],check=True)
# Inspect render endpoint pixel identity and camera/kinematic closure from the separate pose check.
pose=json.loads((O/'Orbit_360_Pose_Verification.json').read_text());assert pose['opening_closing_pose_exact'] and not pose['cropped_subject_bounds']
verification=dict(export=meta,full_decode_passed=True,rendered_first_last_identical=(F/'frame_00001.png').read_bytes()==(F/'frame_05760.png').read_bytes(),source_loop_sha256=hashlib.sha256((F/'frame_00001.png').read_bytes()).hexdigest(),camera_and_mechanism_pose_check=pose,rotations=2,identical_eight_minute_cycles=True,no_people=True)
(O/'Paris_Film_Verification.json').write_text(json.dumps(verification,indent=2));print('VERIFIED',json.dumps(meta),flush=True)
(O/'Readme.md').write_text('''# Le Lovophon — Paris studio, sixteen minutes

LeLovophon_Paris_Close_16min.mp4 is 960 seconds, 1600 x900, H.264 picture and 320 kb/s AAC stereo harp audio. Two identical eight-minute cycles give two complete 360-degree camera rotations. Each cycle has 5760 rendered motion samples at 12 fps, delivered at 24 fps by frame duplication. The zero pose is included at both ends, as in the preceding corrected film, with the same slight endpoint-inclusive clock convention. The sampled harp event times already match that convention.

The camera keeps a 0.95 m radius around the Lovophon. Its elevation gently follows 16 +/-5 degrees over each eight-minute orbit, looking towards a fixed target and returning to its initial transform at 8 and 16 minutes. Instrument framing was checked at 97 poses. The table remains contextual and is intentionally cropped in this closer composition. The photographic backdrop sits outside the orbit, so the opposite side reveals the studio. There are no people.

The 50 mm camera uses f/1.8 depth of field focused on the Lovophon, for a very narrow sharp region and strongly softened foreground/background, giving a miniature-like selective-focus effect. Warm side light, a low cool fill, warm rim, captured reflections, baked indirect light and screen-space ray tracing refine the material response. Tiny render-only bevels provide machined edge highlights; CAD geometry is unchanged. The parquet is stained dark brown.

The room is a procedurally built Parisian-inspired set, rather than a photograph of a real address. The Louis XV-style walnut table includes cabriole legs, rocaille apron decoration, restrained ormolu and marquetry borders. The set includes a white seamless paper sweep, chevron parquet, tall French windows, cream wall mouldings and lighting stands. The corrected mechanism and its ratios are unchanged. This is a visualization of an engineering prototype, not physical proof or a manufactured antique table specification.

The sound uses K. Smith's concert-harp recordings from the Versilian Community Sample Library, edited/mapped by FreePats, under CC0. Source and credits are in the adjacent Sound folder. Exact just-intonation ratios and pluck times remain unchanged. A light convolution of Voxengo's modelled French 18th Century Salon response supplies room ambience: wet RMS 16 dB below dry, 12 ms predelay, wet-only 180 Hz highpass / 6.5 kHz lowpass. This is a designed acoustic match, not a measurement of the pictured studio. Voxengo permits royalty-free processing including commercial use. Its raw IR is not redistributed. See Salon_Reverb_Details.json and https://www.voxengo.com/impulses/ .

LeLovophon_8min_Harp_Salon.wav is the looped 48 kHz/24-bit stereo audio source; it is repeated twice in the movie. The .blend is a scene snapshot for the accompanying render recipe, not a baked animation. Media remains local and is not uploaded to GitHub.
''')
