from pathlib import Path
import subprocess,json,shutil,hashlib,time
R=Path(__file__).resolve().parents[1];O=R/'outputs/LeLovophon_Pluck_Layout_R5/Paris_Studio_16min';F=R/'work/lovophon_r5_paris_frames';ff='/opt/homebrew/bin/ffmpeg';probe='/opt/homebrew/bin/ffprobe'
missing=[n for n in range(1,5760) if not (F/('frame_%05d.png'%n)).exists()];assert not missing,missing[:12]
shutil.copyfile(F/'frame_00001.png',F/'frame_05760.png')
for n in ['Orbit_360_Start.png','Orbit_360_End.png']:shutil.copyfile(F/'frame_00001.png',O/n)
cycle=R/'work/LeLovophon_R5_Paris_Cycle_8min.mp4';movie=O/'LeLovophon_R5_Paris_16min.mp4'
subprocess.run([ff,'-v','error','-y','-framerate','12','-i',str(F/'frame_%05d.png'),'-frames:v','11520','-vf','fps=24,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p','-c:v','libx264','-threads','4','-preset','medium','-crf','15','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',str(cycle)],check=True);print('EIGHT_MINUTE_PICTURE_ENCODED',flush=True)
audio=R/'outputs/LeLovophon_Direct_Gear_Prototype/Axle_Clearance_Revision/Paris_Close_Studio/LeLovophon_8min_Harp_Salon.wav'
subprocess.run([ff,'-v','error','-y','-stream_loop','1','-i',str(cycle),'-stream_loop','1','-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-t','960','-movflags','+faststart',str(movie)],check=True);print('SIXTEEN_MINUTE_SOUND_FILM_ENCODED',flush=True)
meta=json.loads(subprocess.check_output([probe,'-v','error','-show_entries','stream=codec_name,codec_type,width,height,duration,r_frame_rate,nb_frames:format=duration,size','-of','json',str(movie)]));assert abs(float(meta['format']['duration'])-960)<.001
for st in meta['streams']:assert abs(float(st['duration'])-960)<.01
vs=next(s for s in meta['streams'] if s['codec_type']=='video');assert(vs['width'],vs['height'],vs['nb_frames'])==(1600,900,'23040')
subprocess.run([ff,'-v','error','-i',str(movie),'-f','null','-'],check=True)
pose=json.loads((O/'Orbit_360_Pose_Verification.json').read_text());assert pose['opening_closing_pose_exact'] and not pose['cropped_subject_bounds']
cad=O.parent/'LeLovophon_Pluck_Layout_R5.FCStd';cadsha=hashlib.sha256(cad.read_bytes()).hexdigest();assert cadsha=='8b5322026e943034589d3b90ea17b8ebd58bd06830b3c0050511e0693e0f7148'
verification=dict(source_cad_sha256=cadsha,render_parts=1101,physical_test_passed=False,export=meta,full_decode_passed=True,rendered_first_last_identical=(F/'frame_00001.png').read_bytes()==(F/'frame_05760.png').read_bytes(),camera_and_mechanism_pose_check=pose,rotations=2,identical_eight_minute_cycles=True,no_people=True,child_drive_goal='Comfortable child-powered starting/running effort is a mechanical design requirement, not verified by animation.')
(O/'Paris_Film_Verification.json').write_text(json.dumps(verification,indent=2))
manifest=dict(cad_sha256=cadsha,mesh_sha256=hashlib.sha256((R/'work/pluck_r5/mesh.json').read_bytes()).hexdigest(),movie_sha256=hashlib.sha256(movie.read_bytes()).hexdigest(),audio_source_sha256=hashlib.sha256(audio.read_bytes()).hexdigest(),recipe_files={n:hashlib.sha256((R/'work'/n).read_bytes()).hexdigest() for n in ['render_lovophon_r5_paris.py','render_r5_paris_animation.py','direct_gear_math.py','pluck_r5/config.py','direct_gear_studio_materials.py','lovophon_paris_close_studio.py','encode_r5_paris_16min.py']})
(O/'Film_Provenance.json').write_text(json.dumps(manifest,indent=2));print('R5_FILM_COMPLETE_AND_VERIFIED',json.dumps(meta),flush=True)
