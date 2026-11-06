import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as App,Part,math,json,ast
from FreeCAD import Vector as V
from pathlib import Path
ROOT=Path((_LOVOPHON_WORKSPACE + ''));OUT=ROOT/'outputs'
doc=App.openDocument(str(OUT/'Harpe_d_Amour_Twelve_Electric.FCStd'))
oldrows=json.loads(doc.Motion.LinkageGeometry);rows=json.loads(doc.Motion.LinkageGeometry);voices=json.loads((OUT/'Lovophone_Pentatonic_Note_Map.json').read_text())['voices']
code=ast.parse((OUT/'Animate_Open_Harpe.FCMacro').read_text());exec(compile(ast.Module(body=[n for n in code.body if isinstance(n,ast.FunctionDef) and n.name in ['harpe_live_beta','harpe_live_roots']],type_ignores=[]),'motion','exec'))
code=ast.parse((ROOT/'work/build_wide_swing.py').read_text());exec(compile(ast.Module(body=[n for n in code.body if isinstance(n,ast.FunctionDef) and n.name=='wire'],type_ignores=[]),'belt','exec'))
def bx(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def cy(r,h,p,axis=V(1,0,0)):return Part.makeCylinder(r,h,p,axis)
def rod(p,q,r=.4):v=q-p;return cy(r,v.Length,p,v)
def tri(pts,depth):return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,depth))
def prop(o,n,t,val,group='Pentatonic design'):
 if n not in o.PropertiesList:o.addProperty(t,n,group)
 setattr(o,n,val)
SHIFT=16
# Slide the complete mechanism, not the strings, to put every pick safely inside its new speaking length.
for parent in [doc.Structure,doc.RatioBeltDrives,doc.SharedGantry,doc.ElectricDrive]:
 for o in parent.Group:
  if o.TypeId=='Part::Feature' and o.Name!='Baseplate_310x170x6':
   sh=o.Shape.copy();sh.translate(V(SHIFT,0,0));o.Shape=sh
for r in rows:r['station']+=SHIFT
first,last=oldrows[0],oldrows[-1];slope=(last['follower_y']-first['follower_y'])/(last['station']-first['station']);axis=V(1,slope,10/24);axis.normalize()
def level(x):return first['follower_y']+30+slope*(x-first['station']-SHIFT)
baseR=oldrows[0]['radius'];report=[]
for i,(r,v) in enumerate(zip(rows,voices)):
 n=r['note'];ratio=float(__import__('fractions').Fraction(v['ratio_to_C3']));L=330/ratio;R=baseR/ratio;s=r['station'];z=r['pivot_z'];uy=-91+R
 # The original cam/follower and pulley timing remains unchanged: this preserves the approved MIDI exactly.
 r.update(display_note=v['note'],pitch_ratio=ratio,pitch_ratio_exact=v['ratio_to_C3'],frequency_hz=v['frequency_hz'],midi_note=v['midi_note'],speaking_length=L,radius=R,pivot_y=uy)
 speaking_left=False;bridge=320-L;r['speaking_end']='right';r['bridge_x']=bridge
 offset=0;r['arm_axial_offset']=offset
 # Short arms need extra corner clearance: keep the rigid body away from nylon throughout its arc.
 tipsetback=1 if i>=9 else .5
 arm=bx(3,4,R-tipsetback,12+offset,-2,0).fuse(cy(6,3,V(12+offset,0,0))).cut(cy(3.05,5,V(11+offset,0,0)))
 doc.getObject(n+'_ExtendedArm').Shape=arm;doc.getObject(n+'_ExtendedPick').Shape=bx(3.3,.5,tipsetback+.4,15+offset,-.25,R-tipsetback-.3)
 assert R-math.hypot(R-tipsetback,2)>.4,(n,'rigid arm swept radius reaches string')
 doc.getObject(n+'_LongArmRotor').ContactRadius=R
 for j,off in enumerate([-5.5,0]):doc.getObject(n+'_PendulumBearing'+str(j)).Shape=cy(6,4,V(s+off,uy,z)).cut(cy(3.1,6,V(s+off-1,uy,z)))
 # Keep the shared rails and all follower forks. Replace only the arm fork's lower cheeks and stems.
 top=level(s);clamp=bx(12,7.8,22,s-6.5,top-8,z-11).cut(cy(5.15,32,V(s,top,z)-axis*16,axis))
 for off in [-5.5,0]:
  x=s+off;ring=cy(8.5,4,V(x,uy,z)).cut(cy(6.05,6,V(x-1,uy,z)));stem=bx(4,top-uy-13.5,6,x,uy+6,z-3);clamp=clamp.fuse(ring.fuse(stem))
 for zz in [z-8,z+8]:clamp=clamp.cut(cy(1.7,20,V(s-.5,top-9,zz),V(0,1,0)))
 doc.getObject(n+'_ArmHangingFork').Shape=clamp
 A=V(s+5.25,r['follower_y'],r['follower_z']);B=V(s+5.25,uy,z);ra=64/math.pi;rb=16/math.pi
 assert (A-B).Length>ra+rb+1,(n,(A-B).Length)
 doc.getObject(n+'_SwingStepUpBelt').Shape=Part.Face(wire(A,B,ra+.8,rb+.8)).cut(Part.Face(wire(A,B,ra+.1,rb+.1))).extrude(V(3,0,0))
 start,end=(-22,bridge) if speaking_left else (bridge,320);backstart,backend=(bridge,320) if speaking_left else (-22,bridge)
 st=doc.getObject(n+'_KotoSpeakingString');st.Shape=rod(V(start,-91,z),V(end,-91,z));st.SpeakingLength=L
 doc.getObject(n+'_KotoBackString').Shape=rod(V(backstart,-91,z),V(backend,-91,z))
 body=tri([V(bridge-6,-109,z-3),V(bridge,-91.6,z-3),V(bridge+6,-109,z-3)],6);window=tri([V(bridge-2.8,-106,z-4),V(bridge,-97,z-4),V(bridge+2.8,-106,z-4)],8)
 doc.getObject(n+'_KotoThirdBridge').Shape=body.cut(window);doc.getObject(n+'_NylonBridgeCrown').Shape=cy(.65,6,V(bridge,-92.05,z-3),V(0,0,1))
 for o in [st,doc.getObject(n+'_KotoThirdBridge')]:
  prop(o,'PitchName','App::PropertyString',v['note']);prop(o,'TargetFrequency','App::PropertyFrequency',v['frequency_hz']);prop(o,'PitchRatioToC3','App::PropertyString',v['ratio_to_C3']);prop(o,'SpeakingEnd','App::PropertyString',r['speaking_end']);prop(o,'BridgePositionX','App::PropertyLength',bridge)
 prop(st,'TargetTensionN','App::PropertyFloat',(2*L/1000*v['frequency_hz'])**2*(1150*math.pi*(.0008/2)**2))
 prop(st,'AcousticScope','App::PropertyString','Ideal flexible-string estimate only; 0.8 mm unwound nylon, assumed density 1150 kg/m3. Gauge, creep, compliance, inharmonicity and actual tension require physical tuning.')
 pickcenter=s+16.65+offset;edgegap=min(s+15+offset-start,end-(s+18.3+offset));assert edgegap>0,(n,start,end,pickcenter)
 for kind,p in harpe_live_roots(r,0).items():doc.getObject(n+'_'+kind).Placement=p
 for o in doc.Objects:
  if o.Name.startswith(n+'_'):
   oldlabel=o.Label
   o.Label=v['note']+' — '+(oldlabel.split(' — ',1)[-1] if ' — ' in oldlabel else o.Name[len(n)+1:].replace('_',' '))
 prop(doc.getObject(n+'_Output'),'PitchRatio','App::PropertyFloat',ratio)
 report.append(dict(string=i+1,object_prefix=n,note=v['note'],midi_note=v['midi_note'],frequency_hz=v['frequency_hz'],pitch_ratio=v['ratio_to_C3'],speaking_length_mm=L,speaking_end=r['speaking_end'],bridge_x_mm=bridge,pick_center_x_mm=pickcenter,pick_end_clearance_mm=edgegap,arm_radius_mm=R,arm_axial_offset_mm=offset,timing_ratio=r['ratio'],driver_teeth=r['driver_teeth'],driven_teeth=r['driven_teeth'],ideal_nylon_tension_n=st.TargetTensionN))
 print('Updated',v['note'],'length',round(L,3),'bridge',round(bridge,3),'speaking',r['speaking_end'],flush=True)
# Relief pockets let the longest bridge clear the common anchor block and the D3 bridge clear the tray lip.
# Only stationary material is removed; string endpoints, bridges, picks and all moving geometry stay unchanged.
for name in ['KotoAnchorBlock','LowGearboxTray']:
 sh=doc.getObject(name).Shape.copy()
 for r in rows:
  relief=bx(12.8,18.8,6.8,r['bridge_x']-6.4,-109.4,r['pivot_z']-3.4)
  if sh.BoundBox.intersect(relief.BoundBox):sh=sh.cut(relief)
 doc.getObject(name).Shape=sh
# Keep the motor mount's fixing holes on the original soundbox rather than cantilevering its whole foot.
br=bx(3,34,22,319.4,-109,-142).cut(cy(2.1,5,V(318.4,-83,-131))).fuse(bx(20.6,3,26,319.4,-109,-144))
mounts=[]
for x in [325,334]:
 h=cy(1.7,8,V(x,-114,-136),V(0,1,0));br=br.cut(h);mounts.append(h)
for tag in ['RightFoot0','RightFoot1']:br=br.cut(doc.getObject('Gantry'+tag).Shape)
doc.ElectricMotorBracket.Shape=br
# Drill the new gantry and motor foot locations through the lid; original holes are retained.
for tag in ['Left','Right']:
 for j in range(2):
  b=doc.getObject('Gantry'+tag+'Foot'+str(j)).Shape.BoundBox;x=(b.XMin+b.XMax)/2;z=(b.ZMin+b.ZMax)/2
  for dx in [-7,7]:mounts.append(cy(1.7,9,V(x+dx,-114,z),V(0,1,0)))
lid=doc.Baseplate_310x170x6.Shape.copy()
for h in mounts:lid=lid.cut(h)
doc.Baseplate_310x170x6.Shape=lid
for name in ['ElectricClearTop','ElectricClearRear','ElectricClearFront']:
 sh=doc.getObject(name).Shape.copy()
 for j in range(2):sh=sh.cut(doc.getObject('GantryRightFoot'+str(j)).Shape)
 doc.getObject(name).Shape=sh
doc.Label='Le Lovophone — twelve-string pentatonic'
doc.Motion.LinkageGeometry=json.dumps(rows)
prop(doc.Motion,'PitchTuning','App::PropertyString','C3 D3 E3 G3 A3 C4 D4 E4 G4 A4 C5 D5; just pentatonic 1, 9/8, 5/4, 3/2, 5/3, repeated by octaves')
prop(doc.Motion,'TimingRelationship','App::PropertyString','Original twelve independent cam timing ratios retained to reproduce the approved pentatonic MIDI; timing ratios are distinct from pitch ratios.')
doc.Motion.Status='Pentatonic pitches and proportional speaking/arm lengths; original approved MIDI timing. Mechanism translated 16 mm toward tuning end to keep all picks on the speaking sections. Concept geometry; physical string and drive tests pending.'
doc.FlatKotoStrings.Label='Twelve unwound nylon strings — C D E G A across octaves'
doc.RatioBeltDrives.Label='Original rhythmic ratio drives — new arm transmission belt paths'
doc.SharedGantry.DesignIntent='Shared hollow rails and unchanged follower supports; revised hanging arm forks for proportional pentatonic arm radii. Original rhythm retained.'
doc.recompute();invalid=[o.Name for o in doc.Objects if o.TypeId=='Part::Feature' and (o.Shape.isNull() or not o.Shape.isValid())];assert not invalid,invalid
checkpoint=ROOT/'work/Lovophone_Pentatonic_Base.FCStd';doc.saveAs(str(checkpoint))
(OUT/'Lovophone_Pentatonic_Geometry.json').write_text(json.dumps({'voices':report,'rows':rows,'speaking_span_mm':342,'longest_speaking_length_mm':330,'string_height_above_board_mm':18,'mechanism_translation_x_mm':SHIFT,'rhythm_matches_approved_midi':True,'timing_ratios_distinct_from_pitch_ratios':True,'shared_gantry_rails_geometry_unchanged':True,'follower_and_cam_geometry_unchanged':True,'invalid_shapes':invalid,'scope':'Provisional geometry, not production drawings. Target tension is an ideal flexible-string estimate; actual nylon gauge, elastic stretch, bridge friction and pluck dynamics need physical tests.'},indent=2))
print('Saved background checkpoint',checkpoint,flush=True)
