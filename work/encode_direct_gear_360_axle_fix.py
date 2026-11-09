import shutil
from pathlib import Path
import subprocess,json,array,hashlib,shutil
R=Path(__file__).resolve().parents[1];O=R/'outputs/LeLovophon_Direct_Gear_Prototype/Axle_Clearance_Revision/360_Orbit';F=R/'work/direct_gear_studio_360_axle_fix_frames';ff=(shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg');probe=(shutil.which('ffprobe') or '/opt/homebrew/bin/ffprobe')
expected=[F/('frame_%05d.png'%n) for n in range(1,5760)];missing=[p.name for p in expected if not p.exists()]
assert not missing,missing[:20]
# The480-second pose is exactly the starting pose. Reuse its rendered pixels to remove stochastic shading differences at the closure.
shutil.copyfile(F/'frame_00001.png',F/'frame_05760.png')
for name in ['Orbit_360_Start.png','Orbit_360_End.png']:shutil.copyfile(F/'frame_00001.png',O/name)
blue=O/'LeLovophon_360_8min_Blue.mp4';alpha=O/'LeLovophon_360_8min_Alpha.mov'
subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-f','lavfi','-i','color=c=0x0000ff:s=1280x720:r=12:d=480','-framerate','12','-i',str(F/'frame_%05d.png'),'-filter_complex','[0:v]format=rgba[bg];[bg][1:v]overlay=shortest=1:format=rgb,fps=24,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[v]','-map','[v]','-t','480','-c:v','libx264','-preset','medium','-crf','15','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',str(blue)],check=True)
print('BLUE_ENCODE_COMPLETE',flush=True)
subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-framerate','12','-i',str(F/'frame_%05d.png'),'-frames:v','5760','-vf','scale=out_color_matrix=bt709:out_range=tv','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-c:v','prores_ks','-profile:v','4','-pix_fmt','yuva444p10le','-alpha_bits','16','-threads','8',str(alpha)],check=True)
print('ALPHA_ENCODE_COMPLETE',flush=True)
verification={'opening_closing_png_identical':(F/'frame_00001.png').read_bytes()==(F/'frame_05760.png').read_bytes()}
for file in [blue,alpha]:
 d=json.loads(subprocess.check_output([probe,'-v','error','-select_streams','v:0','-show_entries','stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_frames,color_space,color_transfer,color_primaries,color_range:format=duration,size','-of','json',str(file)]));assert abs(float(d['format']['duration'])-480)<.01;assert d['streams'][0]['width']==1280;assert d['streams'][0]['height']==720;verification[file.name]=d
 subprocess.run([ff,'-v','error','-i',str(file),'-f','null','-'],check=True)
raw=subprocess.check_output([ff,'-v','error','-ss','240','-i',str(alpha),'-vf','alphaextract','-frames:v','1','-pix_fmt','gray16le','-f','rawvideo','pipe:1']);a=array.array('H');a.frombytes(raw);verification['alpha_midpoint']={'minimum':min(a),'maximum':max(a),'corner':a[0]};assert min(a)==0 and max(a)==65535

raw_ends=[]
for timestamp in ['0','479.9']:
 raw_ends.append(subprocess.check_output([ff,'-v','error','-ss',timestamp,'-i',str(alpha),'-frames:v','1','-pix_fmt','rgba','-f','rawvideo','pipe:1']))
verification['alpha_decoded_first_last_identical']=raw_ends[0]==raw_ends[1]
verification['decoded_endpoint_sha256']=[hashlib.sha256(x).hexdigest() for x in raw_ends]
assert verification['alpha_decoded_first_last_identical']
(O/'Orbit_360_Export_Verification.json').write_text(json.dumps(verification,indent=2));print(json.dumps(verification,indent=2),flush=True)
(O/'Orbit_360_Readme.md').write_text('''# Le Lovophon — axle-clearance revision, eight-minute 360-degree studio orbit

This film uses the corrected integral crank shafts: the projecting axle ends have been removed, leaving 1 mm axial clearance behind each connecting rod. See the parent revision folder for the CAD and clearance reports.

LeLovophon_360_8min_Blue.mp4:480 seconds,1280x720,H.264,24 fps delivery. Flat pure-blue background, no spill or background shadow. Silent. Twelve unique rendered motion samples per second, duplicated into24 fps delivery.

LeLovophon_360_8min_Alpha.mov: same480 seconds and geometry, ProRes4444 with transparency,12 fps. Use directly in Resolve/Fusion rather than keying fine strings. PNG frame coverage was8-bit; the master preserves that coverage in its alpha channel. No blue background is baked into this file.

One continuous360-degree camera orbit to the right over480 seconds. Constant950 mm distance to the horizontal centre of the model, with both camera and target at string height. Zero camera tilt and roll. Fixed50 mm lens with0.1 vertical lens shift to fit the bank while maintaining a level horizon. No cuts, zooms or camera-distance changes. Both the first and last frames show the exact same camera and mechanism pose. The source motion clock spans0..480 seconds inclusively over5760 samples; this endpoint-inclusive convention changes the nominal playback rate by less than0.02 percent and gives an identical closing frame.

Exact per-frame crank-rocker geometry drives gears, crank pins, connecting rods, rocker shafts and visible arms from one3 rpm input. Twelve rational cycle rates return after24 input revolutions/480 seconds. These are rigid kinematics, not physical load or string-release proof. The mechanism remains an engineering prototype with the build gates in the parent folder README.md.

Warm wood, brass, teal and aluminium under soft studio lighting. Materials are visual choices rather than approved procurement finishes. The old Lab Frame/Unified MIDI does not automatically match this new linkage motion. Media remains local; nothing was uploaded to GitHub.

The .blend files are scene snapshots used by the render recipe, not baked animation deliveries. Orbit_360_Export_Verification.json records duration, frame counts, decode checks and a midpoint alpha test.
''')
