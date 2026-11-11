import csv,json,math,hashlib,zipfile,shutil,html
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'outputs/LeLovophon_Monopole_R4';C=O/'Cutting_Preview';W=R/'work/monopole_r4'
cad=O/'LeLovophon_Monopole_R4.FCStd';sha=hashlib.sha256(cad.read_bytes()).hexdigest()
inv=json.loads((O/'Part_Inventory.json').read_text());motion=json.loads((O/'Checks/R4_Motion_and_Tensioner_Clearance.json').read_text());static=json.loads((O/'Checks/Static_All_Pairs.json').read_text());inherit=json.loads((O/'Checks/R3_Geometry_Inheritance.json').read_text())
assert all(x['cad_sha256']==sha for x in [motion,static,inherit]),'Reports must describe delivered CAD'
assert not static['unexpected'] and not motion['unexpected_motion_intersections'] and not motion['unexpected_tensioner_intersections']
assert all(p['valid'] and p['solids']==1 for p in inv)
mesh=json.loads((W/'mesh.json').read_text());lo=[min(v[i] for p in mesh for v in p['vertices']) for i in range(3)];hi=[max(v[i] for p in mesh for v in p['vertices']) for i in range(3)]
summary=dict(revision='Monopole R4',status='PASS recorded nominal geometry checks / UNBUILT',cad_sha256=sha,parts=len(inv),rear_support_ribs=4,front_support_posts=0,frame_rib_thickness_mm=8,largest_rear_rail_support_span_mm=203,invalid_parts=0,disconnected_part_shapes=0,static_pairs=static['pair_count'],unexpected_saved_pose_intersections=0,unexpected_new_frame_motion_intersections=0,unexpected_tensioner_intersections=0,all_moving_parts_strings_bridges_unchanged_from_R3=True,input_rpm=3,repeat_seconds_at_3rpm=480,body_length_width_height_mm=[700,220,60],saved_pose_length_width_height_mm=[hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]],physical_test_passed=False,manufacturing_release=False,scope=motion['limits'])
(O/'Verification_Summary.json').write_text(json.dumps(summary,indent=2))
# Design history evidence needed to interpret inherited local-pair clearance checks.
D=O/'Checks/Inherited_R3';D.mkdir(exist_ok=True)
for f in ['Verification_Summary.json','String_Routing.json','Drive_Calculations.json']:
 shutil.copy2(R/'outputs/LeLovophon_Protokoto_R3'/f,D/f)
for f in ['Motion_Clearance_R3.json','Final_Refinement_Inheritance.json','Dimensions_and_Tensioners.json']:
 shutil.copy2(R/'outputs/LeLovophon_Protokoto_R3/Checks'/f,D/f)
rows=[
['Curved support rib',4,'5083 aluminium plate','8mm; same profile x4','R4_CurvedRib_8mm_x4.step / .dxf','Flat profile; no bearing fits or welding'],
['Crank outrigger',1,'Aluminium plate','6mm','R4_CrankOuTrigger_6mm_x1.step / .dxf','Retains R3 precision bearing console'],
['Rear backing plate',4,'Stainless steel sheet','30x48x2mm','R4_BackingPlate_2mm_x4.step / .dxf','Four4.4mm through-holes'],
['Stock angle foot',4,'Aluminium equal angle','30x30x3mm;48mm cut length','3 right +1 left STEP; two face drilling templates','Cut and drill stock angle; not a sheet-metal bend development'],
['Fixed structural rear rail',1,'Ground steel shaft','8mm diameter;629mm length','https://www.damencnc.com/en/8mm-linear-motion-shaft-precision/a165','Deburr ends; this rail does not rotate'],
['SHF8 flange shaft clamp',5,'Purchased aluminium clamp','8mm bore;32mm mounting pitch;43x24x10mm nominal','https://www.damencnc.com/en/shf8-flanged-shaft-support-8mm/a155','4 stand clamps +1 crank outrigger clamp; confirm exact purchased drawing. Pinch screws supplied with clamp'],
['Socket cap screw M5x20',18,'A2 stainless or suitable supplier-rated steel','ISO4762 nominal','Metric hardware supplier','8 rib/flange +8 roots +2 crank flange'],
['M5 hex nut',18,'Match screw material','Standard8mm AF','Metric hardware supplier','Use serviceable locking method chosen after prototype; CAD depicts plain nuts'],
['M5 plain washer',18,'Steel/stainless','Nominal10mm OD;5.3mm ID;1mm thick','Metric hardware supplier','Washer locations shown in CAD'],
['Socket cap screw M4x25',18,'A2 stainless or suitable supplier-rated steel','ISO4762 nominal','Metric hardware supplier','16 rear rim +2 crank-console bolts'],
['M4 hex nut',18,'Match screw material','Standard7mm AF','Metric hardware supplier','Accessible with bottom panel removed'],
['M4 plain washer',36,'Steel/stainless','Nominal9mm OD;4.3mm ID;1mm thick','Metric hardware supplier','Both sides of rear wall and crank console'],
['Rear-rim compression sleeve',16,'Stainless steel','6mm OD;4.3-4.4mm ID;12mm nominal length','https://www.mwcomponents.com/shop/m0541-4-ss','RAF M0541-4-SS size example; CAD bore4.4mm. Fit length to measured structural rim thickness; sleeves transfer clamp preload'],
['Crank console spacer',2,'Steel/aluminium tubular spacer','4mm length;M4 clearance;6-8mm OD','Metric hardware supplier','CAD shows8mm OD and4.4mm ID; preserve4mm bearing-console stand-off'],
]
with (C/'Rear_Frame_Bill_of_Materials.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Part','Quantity','Material','Specification','File or reference','Notes']);w.writerows(rows)
with (C/'Rear_Rim_Mounting_Locations.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Stand','Rib_start_CAD_X_mm','Rib_start_from_bass_end_mm','Hole_from_bass_end_mm','Hole_above_body_bottom_mm','Wood_bore_mm','Sleeve_length_mm','Foot_hand'])
 for i,x in enumerate([-249,-56,118,321],1):
  bx=x-30 if i==4 else x+8
  for xx in [bx+8,bx+22]:
   for yy in [-158,-134]:w.writerow([i,x,x+350,xx+350,yy+172,6.1,12,'left / projects inboard' if i==4 else 'right'])
(C/'README.md').write_text('''# Le Lovophon — R4 rear-frame quotation package

Prepared 11 November 2026. Millimetres throughout. Design/quotation preview; not a released production kit. The free-moving mechanism, musical ratios, arm proportions, strings and 700mm body come from R3. This package changes the support frame only.

The frame uses four identical curved ribs on the rear side, one straight fixed rail and a small crank outrigger. There are no front posts, overhead gantry, welded joints or bent curved tubes in the new frame. The 8mm ribs are deliberately thicker through the sheet than thin decorative panels: they must resist sideways movement as well as support weight.

## Ask the cutting shop for

- 4 × curved ribs, 8mm aluminium5083, using the rib STEP/DXF.
- 1 × crank outrigger, 6mm aluminium, using its STEP/DXF.
- 4 × rear backing plates, 2mm stainless, using their STEP/DXF.
- Optionally4 finished stock-angle feet:3right and1left, using their individual STEP files. Otherwise buy30×30×3mm aluminium equal angle, saw four48mm pieces and drill using the two face templates.

Request deburring and a soft edge break, particularly around hands and strings. Suggested appearance: satin bead-blasted/clear-anodised aluminium and plain stainless fasteners. Confirm alloy, finish, hole tolerances, minimum hole/ligament size and material availability with the chosen shop. Clearance-hole locations should be agreed to about ±0.15mm; no laser-cut hole is used as a bearing fit. Do not apply a kerf offset yourself; let the supplier compensate its process.

DXFs contain cut contours only, in millimetres, AutoCAD2000 format. Round holes are true circles. Curved outer edges are polylines with0.015mm chord tolerance; the accompanying STEP is the solid reference. Profiles were checked for closed valid loops and agreement with solid area; seeProfile_Verification.json. The angle drilling templates show two faces of existing angle stock; they are NOT unfolded bend patterns. The two complete angle STEP files settle face orientation and handedness.

## Purchased parts and precision parts

The BOM covers the new rear frame, not the whole instrument. FiveSHF8 fixed-shaft clamps accept the rear8mm solid rail. Four hold it on the ribs; one carries the outrigger. Their holes are on the shaft centreline,32mm apart. SHF8 is a catalogue family, not a guarantee that every seller has identical geometry. Check the selected manufacturer's actual footprint, projecting screw heads and tool access before releasing plate cutting. CAD clamp bodies are nominal catalogue envelopes; internal threads are omitted.

The rotating drive remains the separate5mm shaft in R3's bearings. The rear8mm rail is structural and fixed; itsSHF8 clamps are not rotating bearings. Existing precision bearing carriers, gear fits, bushes and the crank bearing console still require their original precision processes. This package does not make those parts suitable for laser cutting.

Use the16metal sleeves to carry M4 clamping preload across the12mm structural rear rim, with backing plates on the inside. Fit sleeve length to the actual measured wood thickness. The frame loads the rim rather than the thin soundboard. Rear_Rim_Mounting_Locations.csv gives the hole coordinates from the bass end and body bottom; it is a mounting reference, not a complete wood-shop cutting sheet. R4 CAD includes open-bottom nut-access pockets at nearby braces/endblocks. The future wooden-body cutting package remains a later design requirement.

## European supplier routes checked

- [JohnSteel JSBiz](https://www.john-steel.com/biz/en/): acceptsSTEP/DXF, offers cutting/bending and machining; states manufacture in France and no minimum invoice amount.
- [Fractory](https://fractory.com/fr/decoupe-laser/): aluminium laser cutting and delivery throughout France. Its[FAQ](https://fractory.com/frequently-asked-questions/) states no minimum order quantity and accepts individual3Dpart files.
- [DamenCNC Netherlands SHF8](https://www.damencnc.com/en/shf8-flanged-shaft-support-8mm/a155) and[8mm ground shaft](https://www.damencnc.com/en/8mm-linear-motion-shaft-precision/a165).
- [Olimex Bulgaria SHF8](https://www.olimex.com/Products/Robot-CNC-Parts/ShaftSupport/SUPPORT-SHF8/) is an alternative clamp source; confirm its detailed drawing before substitution.
- [RAF/MWComponents M0541-4-SS](https://www.mwcomponents.com/shop/m0541-4-ss) documents the6OD×4.3ID×12mm stainless spacer size; this is a size reference, not a confirmed European stock reservation.

These are plausible quoting/procurement routes, not supplier approvals, quotations or orders. Exact stock, delivery cost, fit and finish must be confirmed against the selected parts. No supplier has received the files.

## Assembly

See../Assembly_Guide.md. CAD clearances and idealised elastic estimates do not establish loaded stiffness, fatigue life, clamp holding torque or reliable pick release. The next build step is a full-size frame/one-voice trial, checking alignment and smooth travel before committing to all twelve voices.
'''.replace('aluminium5083','aluminium 5083').replace('seeProfile','see Profile'))
(O/'Assembly_Guide.md').write_text('''# R4 frame assembly and service

The drawing uses X along the bank, Y vertically upwards, and Z across the strings. The bass end of the body is CADX=-350mm; the bottom of the wooden body is Y=-172mm. All mounting positions in the CSV also have simple bass-end/bottom datums. Rib start positions are101,294,468and671mm from the bass end. Three feet project right along the rear rim; the last one projects left/inboard to clear the tuners.

1. Have the four identical ribs, crank outrigger and backing plates cut and deburred. Prepare the four48mm stock angles to their supplied3Dhole patterns; check the inside root radius against the rib before assembly.
2. With the removable bottom off, prepare the structural rear-rim holes and open-bottom nut/tool pockets shown in R4 CAD. Insert the sixteen metal compression sleeves, fitted to the actual rim thickness. Mount the four angles with M4through-bolts, outside/inside washers and internal backing plates. Keep the thin soundboard out of this bolt-preload stack.
3. Attach each8mm rib to its angle with twoM5bolts, head-side washers and nuts. Leave the joints adjustable initially. Fit fourSHF8clamps to the rib pads with twoM5bolts each.
4. Slide the629mm long,8mm solid fixed rail through the four clamps and the retained mechanism carriers. Do not force a bowed rail through tight clamps. Set it straight in an assembly jig, align the existing5mm input shaft and bearings, then tighten progressively. Follow the selected component suppliers' fastener/clamp instructions; final torques and locking method must be established on the prototype. No final bolt-preload/wood-strength approval is implied by the CAD.
5. Fit the fifthSHF8clamp in reverse orientation to the6mm crank outrigger. Bolt the outrigger to the existing R3crank bearing console using its two4mm spacers, washers on both sides and M4×25bolts. The end flange bolts are reversed relative to the stand bolts to maintain clearance. Keep the original crank bearing, retainer and freely rotating grip stack.
6. Turn the hand crank slowly with the picks initially clear and the strings untensioned. Check every bearing, gear, link and rod for free movement throughout the cycle; verify the clamps are fixed while the5mm input shaft rotates freely. Establish alignment and loaded frame stiffness before setting pick depth or string tension. Set gear phase using the original R3records if anything has been dismantled.
7. Bring the string load up in stages and test one voice first. Check frame movement, clamp slip, nut retention, rail straightness and actual pick release under operating load. The current nominal checks do not cover these physical effects. Record the accepted settings before extending to all twelve voices.

For routine cleaning, remove the bottom for rear nut access. Use hex keys for screw heads/clamp adjustments and7/8mm spanners to hold M4/M5nuts during assembly. Do not withdraw the structural rail or dismantle a bearing stack under string load. R3is preserved separately; this file is the new R4candidate.

The instrument's tuning, proportional arms,3rpm input reference and8minute repeat are unchanged. Turning the crank by hand gives the same rational sequence of24input turns; the elapsed8minutes depends on holding3rpm. The frame is not a speed regulator.
''')
(O/'README.md').write_text('''# Le Lovophon — curved rear stand R4

R2's rear-only support layout, rebuilt as four identical curved8mm aluminium ribs. The front and string bed are open. The ribs sweep behind the moving parts and carry a fixed8mm steel rail; a cut6mm outrigger supports the retained hand crank. The feet use stock angle, through-bolts, metal compression sleeves and internal backing plates. The new frame needs no welding.

R3's700×220×60mm body, twelve strings, bridge positions, proportional arms, pitch/rotation ratios, thin links and crank mechanism remain. Every moving solid was compared to R3and retained without geometric change. At3rpm the repeat remains480seconds; hand-cranking preserves the turn relationships, while elapsed time follows hand speed.

- LeLovophon_Monopole_R4.FCStd — complete revised CAD.
- R4_Studio_Overview.png and R4_Studio_Rear.png — material/lighting previews of this geometry.
- R4_Inspection_*.png — neutral inspection views.
- Assembly_Guide.md — frame assembly and service notes.
- Cutting_Preview/ — individualSTEP/DXFparts, angle templates, new-frame BOM, mounting positions, supplier routes and profile checks.
- Verification_Summary.json and Checks/ — nominal checks, exact R3inheritance and preliminary stiffness/mass estimates.

Status: UNBUILT; NOT a released fabrication drawing set. Final saved-pose intersections, new-frame motion checks and tensioner travel checks pass. Conservative continuous envelopes are used where disjoint, with1degree pose samples for overlapping envelopes. Physical alignment, tolerances, stiffness, clamp grip, friction, wear and pick release still require a prototype test. The idealised load estimate is not an allowable load or safety rating. Purchased clamp geometry is nominal until a specific drawing is accepted.

Wood-shop cutting drawings remain a later requirement. These files provide the frame/box interfaces without issuing a complete acoustic box manufacturing package. The prior R3CADand video have been preserved.
''')
# Normal typography in assembly/procurement notes; leave file names and URLs untouched.
import re
for pp in [O/'README.md',O/'Assembly_Guide.md',C/'README.md']:
 text=pp.read_text();protected=[]
 def keep(m):
  protected.append(m.group());return f'§{len(protected)-1}§'
 text=re.sub(r'https?://[^\s)]+|[A-Za-z0-9_]+\.(?:FCStd|png|json|csv|md|step|dxf)|R4_Inspection_\*\.png',keep,text)
 for pattern,repl in [(r'\b(R[234])(?=[a-z])',r'\1 '),(r'(SHF8)(?=[a-z])',r'\1 '),(r'(M[45])(?=[a-z])',r'\1 '),(r'(?<=[a-z])(?=\d)', ' '),(r'(?<=[a-z])(?=SHF8|R[234])',' '),(r'(?<=\d)(?=mm|rpm|seconds|input|minute|degree|right|left|metal|aluminium|rear|stand|crank)',' '),(r'(?<=\d)and(?=\d)',' and '),(r'(\b3D)(?=[a-z])',r'\1 ')]:text=re.sub(pattern,repl,text)
 text=re.sub(r'§(\d+)§',lambda m:protected[int(m.group(1))],text)
 for aa,bb in [('CADX','CAD X'),('101,294,468and 671','101, 294, 468 and 671'),('twoM5','two M5'),('M4×25bolts','M4 × 25 bolts'),('7/8 mm spanners','7 mm and 8 mm spanners'),(',8 mm',', 8 mm'),(',3 rpm',', 3 rpm'),('feet:3 right','feet: 3 right'),('centreline,32 mm','centreline, 32 mm'),('acceptsSTEP','accepts STEP'),('Its[FAQ]','Its [FAQ]'),('and[8 mm','and [8 mm'),('See../Assembly_Guide.md','See [Assembly_Guide.md](../Assembly_Guide.md)'),('6OD×4.3ID×12 mm','6 mm OD × 4.3 mm ID × 12 mm')]:text=text.replace(aa,bb)
 pp.write_text(text)
# A readable vector overview, using the exact DXF profiles rather than redrawing geometry.
vr=json.loads((C/'Profile_Verification.json').read_text());vr['source_cad_sha256']=sha;(C/'Profile_Verification.json').write_text(json.dumps(vr,indent=2))
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1100" viewBox="0 0 1400 1100">','<rect width="1400" height="1100" fill="#f5f4ef"/>','<style>text{font-family:Arial,sans-serif;fill:#203036}.title{font-size:34px;font-weight:700}.sub{font-size:19px}.note{font-size:16px}</style>','<text x="60" y="65" class="title">Le Lovophon / R4 rear frame</text>','<text x="60" y="100" class="sub">Flat cut profiles • millimetres • quotation preview</text>']
places=[(80,170,3.0,'4 × curved rib / 8mm aluminium'),(510,180,3.0,'1 × crank outrigger / 6mm aluminium'),(1000,200,3.0,'4 × backing plate / 2mm stainless'),(640,600,3.0,'Angle: rib face drilling'),(1000,600,3.0,'Angle: body face drilling')]
for p,(px,py,sc,label) in zip(vr['profiles'],places):
 w,h=p['bounds_mm'];svg.append(f'<text x="{px}" y="{py-25}" class="sub">{html.escape(label)}</text>');svg.append(f'<g transform="translate({px},{py+h*sc}) scale({sc},-{sc})" fill="#c4d0d1" stroke="#203036" stroke-width=".45">')
 loops=p['loops'];outer=[]
 for l in loops:
  if l['type']=='polyline':outer+=['M '+' L '.join(f'{x},{y}' for x,y in l['points'])+' Z']
 svg.append('<path d="'+' '.join(outer)+'" fill-rule="evenodd"/>')
 for l in loops:
  if l['type']=='circle':svg.append(f'<circle cx="{l["x"]}" cy="{l["y"]}" r="{l["r"]}" fill="#f5f4ef"/>')
 svg.append('</g>');svg.append(f'<text x="{px}" y="{py+h*sc+30}" class="note">Envelope {w:.1f} × {h:.1f}mm</text>')
svg+=['<text x="60" y="1010" class="sub">4 rear ribs • stock angle feet • 5 SHF8 clamps • fixed Ø8 × 629 rail • bolted assembly</text>','<text x="60" y="1045" class="note">Use individual STEP/DXF files for quoting. Angle face drawings are drilling templates, not bend developments.</text>','<text x="60" y="1075" class="note">Unbuilt prototype. Confirm purchased clamp footprint and physical stiffness before production.</text>','</svg>'];(C/'Frame_Parts_Overview.svg').write_text('\n'.join(svg))
# Remove only backups/progress files created during this new revision; R3 remains untouched.
for p in O.glob('*.FCBak'):p.unlink()
for p in (O/'Checks').glob('*Progress*.json'):p.unlink()
zipfile_path=O/'R4_Cutting_and_Assembly_Preview.zip'
with zipfile.ZipFile(zipfile_path,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(C.iterdir()):
  if p.is_file():z.write(p,'Cutting_Preview/'+p.name)
 for n in ['Assembly_Guide.md','Verification_Summary.json','README.md']:z.write(O/n,n)
print(json.dumps(summary,indent=2));print('PACKAGED',zipfile_path,zipfile_path.stat().st_size)
