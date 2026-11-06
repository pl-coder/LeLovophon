import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import FreeCAD as A,FreeCADGui as G,Part,json,math,csv,ast
from pathlib import Path
from fractions import Fraction as F
from PySide import QtWidgets
R=Path((_LOVOPHON_WORKSPACE + ''));O=R/'outputs'
q=QtWidgets.QApplication.instance() or QtWidgets.QApplication([]);G.showMainWindow();G.getMainWindow().hide()
d=A.openDocument(str(O/'Lovophone_Lab_Frame.FCStd'));rows=json.loads(d.Motion.LinkageGeometry)
def prop(o,n,t,v):
 if n not in o.PropertiesList:o.addProperty(t,n,'Build review')
 setattr(o,n,v)
def wire(B,C,r,s):
 v=C-B;D=v.Length;v.normalize();p=A.Vector(0,-v.z,v.y);k=(r-s)/D;h=math.sqrt(1-k*k);n=v*k+p*h;m=v*k-p*h
 return Part.Wire([Part.makeLine(B+n*r,C+n*s),Part.Arc(C+n*s,C+v*s,C+m*s).toShape(),Part.makeLine(C+m*s,B+m*r),Part.Arc(B+m*r,B-v*r,B+n*r).toShape()])
pairs=[(32,32),(36,32),(40,32),(48,32),(40,24),(48,24),(54,24),(60,24),(60,20),(60,18),(64,16),(72,16)]
audit=[];changed=[]
for r,(nt,dt) in zip(rows,pairs):
 n=r['note'];f=F(r['pitch_ratio_exact']);assert F(nt,dt)==f
 old=F(r['driver_teeth'],r['driven_teeth']);r['ratio']=float(f);r['ratio_exact']=str(f);r['driver_teeth']=nt;r['driven_teeth']=dt;r['input_period_seconds']=20
 assert abs(r['speaking_length']*float(f)-330)<1e-8
 assert abs(r['radius']*float(f)-rows[0]['radius'])<1e-8
 for suffix,t,bore in [('RatioDrivePulley',nt,3.05),('RatioDrivenPulley',dt,5.05)]:
  o=d.getObject(n+'_'+suffix);rad=t/math.pi
  o.Shape=Part.makeCylinder(rad,5,A.Vector(),A.Vector(1,0,0)).cut(Part.makeCylinder(bore,7,A.Vector(-1,0,0),A.Vector(1,0,0)))
  prop(o,'ReferenceTeeth','App::PropertyInteger',t);prop(o,'ReferencePitch','App::PropertyLength',2)
  prop(o,'ProcurementStatus','App::PropertyString','REFERENCE ENVELOPE ONLY: choose exact catalogue profile, hub, bore, flanges and width before manufacture')
  o.Label=r['display_note']+' — '+str(t)+' tooth pitch envelope (NOT manufacturing teeth)';changed.append(o)
 o=d.getObject(n+'_Output');o.SpeedRatio=float(f)
 prop(o,'PitchAndRotationRatio','App::PropertyString',str(f))
 B=A.Vector(r['station'],-83,-131);C=A.Vector(r['station'],-59,-116);ra=nt/math.pi;rb=dt/math.pi
 o=d.getObject(n+'_RatioBelt');o.Shape=Part.Face(wire(B,C,ra+.8,rb+.8)).cut(Part.Face(wire(B,C,ra+.1,rb+.1))).extrude(A.Vector(5,0,0));changed.append(o)
 D=(C-B).Length;alpha=math.asin((ra-rb)/D);wrap=math.pi-2*alpha;length=2*math.sqrt(D*D-(ra-rb)**2)+math.pi*(ra+rb)+2*(ra-rb)*alpha
 audit.append(dict(note=r['display_note'],prefix=n,old_rotation_ratio=str(old),pitch_and_rotation_ratio=str(f),speaking_length_mm=r['speaking_length'],arm_radius_mm=r['radius'],driver_teeth=nt,driven_teeth=dt,cam_period_seconds=20/float(f),belt_reference_length_mm=length,small_pulley_wrap_deg=math.degrees(wrap),reference_teeth_in_wrap=dt*wrap/(2*math.pi),driven_pitch_radius_minus_bore_mm=rb-5.05,procurement_status='NOT RELEASED: catalogue pulley and belt selection pending'))
d.Motion.LinkageGeometry=json.dumps(rows);d.Motion.Time=0
prop(d.Motion,'InputPeriodSeconds','App::PropertyFloat',20.0);prop(d.Motion,'FullRepeatSeconds','App::PropertyFloat',480.0)
d.Motion.TimingRelationship='Pitch and average cam rotation use identical exact pentatonic ratios; 20 s input revolution; 480 s / 8 min common phase repeat.'
d.Motion.Status='RATIO-CORRECTED LAB FRAME ENGINEERING REVIEW. Reference pulley/belt envelopes updated. Not production-ready: supplier tooth profiles, hubs, centre distances, tensioning and frame joints need detailing. Old MIDI/video invalid.'
d.Motion.ConstructionIntent='Twelve-string open lab frame, independent eccentric cam/follower pendula. Prefer catalogue motion parts and cut stock; custom flat plates and clamp/hub parts only where needed.'
d.Label='Le Lovophone — Lab Frame, matched pentatonic ratios — BUILD REVIEW'
d.RatioBeltDrives.Label='Matched pentatonic timing — reference envelopes, not fabrication profiles'
d.recompute()
def world(o):
 s=o.Shape.copy();s.transformShape((o.getGlobalPlacement()*o.Placement.inverse()).toMatrix());return s
# Changed pulleys are rotationally symmetric reference discs: their swept volume is invariant.
allparts=[o for o in d.Objects if o.TypeId=='Part::Feature'];shapes={o.Name:world(o) for o in allparts};issues=[]
for o in changed:
 s=shapes[o.Name]
 for p in allparts:
  if p==o or p.Name.startswith(o.Name.split('_')[0]+'_'):continue
  t=shapes[p.Name]
  if s.BoundBox.intersect(t.BoundBox):
   v=s.common(t).Volume
   if v>1e-4:issues.append(dict(part=o.Name,other=p.Name,overlap_mm3=v))
invalid=[o.Name for o in allparts if o.Shape.isNull() or not o.Shape.isValid()];assert not invalid
# Exact rational minimal return and all voiced pitch/length relationships.
from functools import reduce
lcm=reduce(math.lcm,[F(r['ratio_exact']).denominator for r in rows]);assert lcm==24 and lcm*20==480
prop(d.Motion,'FabricationReleased','App::PropertyBool',False)
prop(d.Motion,'ChangedEnvelopeInterferenceCount','App::PropertyInteger',len(issues))
d.recompute();d.saveAs(str(O/'Lovophone_Lab_Frame_Ratio_Review.FCStd'))
with (O/'Lovophone_Lab_Frame_Ratio_Audit.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=audit[0]);w.writeheader();w.writerows(audit)
report=dict(input_period_seconds=20,repeat_seconds=480,denominator_lcm=lcm,matched_voices=12,invalid_shapes=invalid,changed_envelope_intersections=issues,voices=audit,production_released=False,scope='Exact pitch/average-rotation and inverse length checks. Intersections are new drive envelope candidates, not a complete physical contact simulation. Existing frame joints remain un-detailed. Catalogue profiles and belt lengths must be selected before machining.')
(O/'Lovophone_Lab_Frame_Ratio_Audit.json').write_text(json.dumps(report,indent=2))
# Full component inventory, including hidden motor reservation parts.
def classify(n):
 if 'Bearing' in n:return 'Catalogue bearing / bush — match drawing','123Roulement','Confirm dimensions, clearance and retention; not every bearing has the same size'
 if any(k in n for k in ['RatioDrivePulley','RatioDrivenPulley','SwingDrivePulley','SwingDrivenPulley','Belt']):return 'Catalogue timing drive preferred; interface redesign needed','MISUMI / HPC / specialist','Reference envelope only; no approved SKU, width, tooth form, hub or belt length'
 if any(k in n for k in ['Bolt','Nut','Washer','Screw']):return 'Catalogue fastener','Metric fastener supplier','Confirm thread, length, strength and tool access; target M3 / 2.5 mm Allen'
 if any(k in n for k in ['Rail','Post','Stay','Transom','Longeron','Shaft','Axle']) and not any(k in n for k in ['Clamp','Saddle','Motor','Bracket']):return 'Cut standard tube / rod / precision shaft','Stock supplier; cut service','Smooth bearing journals; rod tolerances and actual joint allowances to specify'
 if any(k in n for k in ['Soundbox','Baseplate']):return 'CNC-routed timber / plywood','Online wood CNC service to confirm','Material, grain, glue joints and acoustic response pending'
 if any(k in n for k in ['ExtendedArm','FollowerLever','Cheek','EndPlate','Foot','Tab']):return 'Custom flat cut / drilled component','John Steel / Xometry','DXF plus thickness; bearing bores and precision holes need machining drawing'
 if any(k in n for k in ['Clamp','Hub','Fork','Hanging','Bracket']):return 'Custom machined fitting; consolidate repeated families','Xometry / Protolabs Network','STEP plus drawing; fits, threads, captive nuts, splits and clamp travel not detailed'
 if any(k in n for k in ['String','NylonOverEdge']):return 'Catalogue unwound nylon string','Music string supplier','Nominal 0.8 mm only; physical tuning, creep and total tension to verify'
 if any(k in n for k in ['Motor','PWM','Speed','Electric','N20']):return 'Catalogue electrical component / mount reservation','Select after one-voice torque test','No production motor or control selected; 3 rpm input under load required'
 if 'Spring' in n:return 'Catalogue spring to size','Spring supplier','Return torque, preload and fatigue not sized'
 if any(k in n for k in ['Pick','Crown','Guide','Knob','Pad']):return 'Replaceable wear component / printed prototype','Sculpteo PA12 / stock','Functional material and wear test needed; printing is not default for precision fits'
 return 'Custom or catalogue equivalent — review interface','Engineering review','No verified purchased replacement yet'
inv=[]
for o in allparts:
 route,supplier,status=classify(o.Name);bb=shapes[o.Name].BoundBox
 inv.append(dict(object=o.Name,label=o.Label,quantity_in_model=1,route=route,supplier_candidate=supplier,status=status,bbox_x_mm=round(bb.XLength,3),bbox_y_mm=round(bb.YLength,3),bbox_z_mm=round(bb.ZLength,3)))
with (O/'Lovophone_Lab_Frame_Procurement_Inventory.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=inv[0]);w.writeheader();w.writerows(inv)
print(json.dumps(dict(saved=True,parts=len(inv),ratio_mismatches_original=sum(F(x['old_rotation_ratio'])!=F(x['pitch_and_rotation_ratio']) for x in audit),new_envelope_intersections=len(issues),invalid_shapes=invalid)),flush=True)
