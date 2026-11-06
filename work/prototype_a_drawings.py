from pathlib import Path
import math,json,csv,textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib import colors
from prototype_a_math import *
O=OUT;c=canvas.Canvas(str(O/'Prototype_A_Drawings.pdf'),pagesize=landscape(A4));W,H=landscape(A4)
BLUE=colors.HexColor('#164455');GREY=colors.HexColor('#65747A');INK=colors.HexColor('#17252B')
page=0
def text(x,y,s,size=10,col=INK):c.setFillColor(col);c.setFont('Helvetica',size);c.drawString(x,y,str(s))
def lines(x,y,items,width=55,size=10):
 for item in items:
  for l in textwrap.wrap(item,width):text(x,y,l,size);y-=size*1.45
  y-=7
 return y
def header(title,subtitle):
 global page;page+=1;c.setFillColor(BLUE);c.rect(0,H-65,W,65,fill=1,stroke=0);text(30,H-30,title,20,colors.white);text(30,H-49,subtitle,10,colors.white)
 text(30,24,'LE LOVOPHONE | Prototype A | Rev A / 2026-11-05 | mm | QUOTATION & ENGINEERING REVIEW',9,GREY);text(W-65,24,f'{page} / 8',9,GREY)
 c.setStrokeColor(INK);c.setLineWidth(.7)
def nextp():c.showPage()
def outline(x,y,w,h,s=2):c.rect(x,y,w*s,h*s)
def circle(x,y,r,s=2):c.circle(x,y,r*s)
def dim(x,y,x2,y2,label):
 c.setStrokeColor(GREY);c.line(x,y,x2,y2);c.line(x-3,y-3,x+3,y+3);c.line(x2-3,y2-3,x2+3,y2+3);text((x+x2)/2-15,(y+y2)/2+5,label,9,GREY);c.setStrokeColor(INK)
def pts(ox,oy,ps,s=2):
 for x,y,d in ps:circle(ox+x*s,oy+y*s,d/2,s)
def panel(items):lines(520,H-100,items,48,10)
header('Build the mechanism before the instrument','Two independent manual test fixtures: one-string pluck and exact 9:2 drive. No motor purchase required yet.')
lines(35,H-105,[
'Purpose: test the two things the presentation model could not establish - clean mechanical plucking, and a practical high-ratio transmission.',
'The pluck fixture uses a fully pinned 4-bar: 4 mm crank, 80 mm connecting rod, 14 mm rocker and 80 mm fixed pivot spacing. It forces both directions without a follower spring or 4x swing belt.',
'The drive fixture uses (60/20) x (30/20) = 9/2 with two nominal 160 mm, 80-tooth, 2 mm pitch, 6 mm wide belts and 5 mm shafts. Supplier profile confirmation is still required.',
'Lowest voice: C3, 330 mm speaking string, 67.196938 mm arm. Highest voice: D5, 73.333333 mm speaking string, 14.932653 mm arm. Swap arm and string height; do not treat the two as simultaneously assembled voices.',
'Computed swing: +/-16.662 degrees. Link closure checked at 10,001 phases; minimum transmission angle 68.526 degrees. These are geometric results, not evidence of successful physical plucks.',
'Procurement gate: DHM lists the belt as GT2 today but S2M in an older catalogue. Its pulley pages also warn of batch dimensional variation. Verify a matched set and hub/flange dimensions before manufacture of spacers or pulley-adjacent parts.',
'No physical prototype has been built or tested. This packet is for engineering review and quotation; it is not certification that the full Lovophone works.'
],112,11)
nextp()
header('R01 / Exact 9:2 drive fixture','2 identical cheeks: aluminium 6061-T6, 180 x 100 x 6. Bearing carriers allow +/-3 mm adjustment.')
ox,oy=55,155;s=2;outline(ox,oy,180,100,s)
xs=[30,30+C1,30+C1+C2]
for x in xs:
 c.setDash(3,2);c.rect(ox+(x-19)*s,oy+34*s,38*s,32*s);c.setDash()
 for dx in [-10,10]:
  for dy in [-20,20]:
   yy=50+dy;outline(ox+(x+dx-3)*s,oy+(yy-1.7)*s,6,3.4,s)
 circle(ox+x*s,oy+50*s,2.5,s)
 text(ox+x*s-9,oy+15*s,f'{x:.3f}',9)
for x in [10,170]:
 for y in [10,90]:circle(ox+x*s,oy+y*s,2.25,s)
dim(ox,oy-25,ox+360,oy-25,'180');dim(ox+xs[0]*s,oy+115*s,ox+xs[1]*s,oy+115*s,f'{C1:.3f}');dim(ox+xs[1]*s,oy+115*s,ox+xs[2]*s,oy+115*s,f'{C2:.3f}')
panel(['Shafts: (X,Y) = (30,50), (67.836782,50), (122.744491,50). Positions are nominal untensioned pitch geometry.',
'4 x 4.5 through holes: (10,10), (170,10), (10,90), (170,90).',
'At each shaft: central relief slot 32 diameter with 6 mm horizontal centre travel (38 x32 overall). Neighbouring reliefs may merge.',
'Carrier mount slots: 3.4 wide, 6 mm centre travel (9.4 overall), centres at shaft X +/-10; Y=30 and70. Use STEP for exact rounded slots.',
'Outside cheek Z=0..6 and56..62; four spacer tubes OD8/ID4.5 x50 between them. M4 threaded tie rods and washers/nuts for bench assembly.',
'Pulley belt midplanes Z=14 and38. 60/20 first stage, 30/20 second. Intermediate shaft carries 20T and30T clamped together.',
'Pulley body/hub/flange geometry in assembly CAD is a clearance reservation, not a supplier drawing. Do not machine reference discs.'])
nextp()
header('R02 / R03 Bearing carriers and retainers','6 identical carriers; 6 identical retainer disks. Axial load is retained by shoulders and screws.')
ox,oy=100,170;s=4;outline(ox,oy,30,50,s)
circle(ox+15*s,oy+25*s,8,s);c.setDash(3,2);circle(ox+15*s,oy+25*s,4,s);c.setDash()
pts(ox,oy,[(x,y,3.4) for x in [5,25] for y in [5,45]],s)
pts(ox,oy,[(4,25,1.6),(26,25,1.6)],s)
text(90,140,'R02 - view into bearing pocket',10)
circle(350,265,13.5,4);circle(350,265,4,4)
for dx in [-11,11]:circle(350+dx*4,265,1.1,4)
text(297,195,'R03 - 1 mm stainless',10)
panel(['R02: 30 x50 x6, 6061-T6. Local origin at lower-left. Bearing centre (15,25).',
'16 H7 pocket (+0/+0.018), depth5 from inner face. 8 through bore leaves a 1 mm outer shoulder. Do not substitute a laser-cut bearing seat.',
'4 x3.4 through at (5,5),(25,5),(5,45),(25,45).',
'2 x M2 tapped through, centres (4,25),(26,25). STEP shows 1.6 pilot holes; tap to drawing.',
'R03: 27 OD /8 ID x1 stainless. 2 x2.2 through at +/-11 along horizontal diameter.',
'625-ZZ bearings: 5 x16 x5. Retainer screws M2x5; check no screw end protrudes into another part. Front carrier is mirrored in assembly.',
'Fit 5 mm ground shafts, with separate shaft collars bearing only against inner races. Set axial play without preloading the bearings.',
'General machined dimensions +/-0.10 unless stated; pocket depths +/-0.03; deburr 0.2 max at bearing shoulder.'])
nextp()
header('P01 / One-string linkage cheeks','2 identical aluminium 6061-T6 plates, 140 x140 x6. 30 mm clear spacing between inner faces.')
ox,oy=60,120;s=2.3;outline(ox,oy,140,140,s)
pts(ox,oy,[(30,110,16),(110,110,16),(110,110-RLOW,10),(110,110-RHIGH,10)]+[(x,y,4.5) for x in [10,130] for y in [10,130]],s)
pts(ox,oy,[(x,110,1.6) for x in [19,41,99,121]],s)
dim(ox+30*s,oy+150*s,ox+110*s,oy+150*s,'80.000')
panel(['Crank bearing centre (30,110); rocker bearing centre (110,110). 16 H7 through at both centres. Position tolerance +/-0.03 relative to each other.',
'4 x4.5 through: (10,10),(130,10),(10,130),(130,130).',
'String-clearance ports: 10 through at (110,42.803062) for C3 and (110,95.067347) for D5. Only one configuration is strung at a time.',
'2 x M2 tapped through per bearing at X=19,41 for crank, X=99,121 for rocker; Y=110; STEP shows tap pilot. 27/8 x1 retainers on both faces hold outer race with 0.5 mm nominal axial clearance. Use M2x3 screws from each face; longer opposing screws can collide.',
'Plates Z=0..6 and36..42. Four 30 mm spacer tubes on corner M4 tie bolts.',
'Two 5 mm shafts, nominal length96, Z=-44..52. Crank blind bore receives shaft only to Z52. Do not let shaft break through into the crank-pin hole.',
'Bench board: plywood140 x400 x12, orient along strings. Bolt plate lower edges to standard20 x20 x2 angle feet using existing lower holes. Drill board to actual assembled angle holes. Brackets/bolts not all drawn in reference assembly.'])
nextp()
header('P02 / P03 Positive-drive crank and rocker','Split hubs clamp to 5 mm shafts. Small pin hole and large shaft bore are separated axially in the crank.')
ox,oy=135,280;s=7;circle(ox,oy,10,s);circle(ox,oy,2.5,s);circle(ox+4*s,oy,1.25,s)
text(50,180,'P02: 20 OD x12; front view',11)
ox2=350;circle(ox2,oy,9,s);circle(ox2,oy,2.5,s);circle(ox2+14*s,oy,5,s);circle(ox2+14*s,oy,1.25,s)
text(275,180,'P03: 14 pin-centre radius',11)
panel(['P02: 20 OD x12, 6061-T6. Rear shaft bore5 H7 blind depth6. Front M3 thread blind depth4, centre at (4,0). Preserve 2 mm web between bore floors.',
'P03: hub18 OD x12, pin boss10 OD x12, centres14 apart; 10 mm wide x6 connecting web. 5 H7 through hub; M3 blind depth4 from front at pin centre.',
'Both hubs: rear split0.8 wide from bore towards +Y, depth6. M3 clamping bolt transverse X at localY=6,Z=3. Left half3.4 clearance; right half M3 tapped (STEP pilot2.5). Use M3x16; machine seating flats if required for head and thread engagement.',
'P02/P03 sit at Z46..58. Both pin flanges sit on front Z58 so rod journals align.',
'Do not use an ordinary through-drilled crank: 5 mm shaft and3 mm pin at4 mm spacing would touch. The blind, two-sided construction is deliberate.',
'Machinist to confirm M3 thread engagement, clamp seating and no split closes fully before gripping shaft. No adhesive or friction roller substitutes for pin capture.'])
nextp()
header('P04 / P05 Coupler, arms and replaceable picks','One long arm installed; short arm is a swap part. The two configurations retain inverse musical lengths.')
ox,oy=65,330;s=4;outline(ox,oy-20,80,10,s);circle(ox,oy,5,s);circle(ox+80*s,oy,5,s);circle(ox,oy,1.52,s);circle(ox+80*s,oy,1.52,s);dim(ox,oy+35,ox+320,oy+35,'80 +/-0.05')
text(65,275,'P04: POM-C, 4 thick, plain bearing link',11)
for x,r,label in [(100,RLOW,'C3'),(280,RHIGH,'D5')]:
 scale=2.0;circle(x,170,9,scale);circle(x,170,2.5,scale);outline(x-6,170-(r-1)*scale,6,r-1,scale);circle(x,170-(r-5)*scale,1.7,scale);text(x+30,160,label,11)
panel(['P04: POM-C, 4 thick, 10 wide, rounded5-radius ends. Pin centres80 +/-0.05. Two3.02..3.04 through holes for3 h6 journal pins. The rod is a cheap replaceable dry bearing component.',
'P05 aluminium arms: 18 OD x8 split-clamp hub with5 H7 bore; 6 wide x3 body. Pivot-to-string radius67.196938 (C3) or14.932653 (D5). Rigid tip stops1 mm short.',
'Pick mount3.4 through at radius R-5 on arm centreline. Hub clamp detail follows P03.',
'Pick trial strips: PET0.5 thick, 6 wide x7.3 long; 3.4 mounting hole5.3 back from tip. Shim/slot to find minimum reliable string intrusion. CAD shows0.3 mm nominal; this is a test setting, not a proven release geometry.',
'Arm plane Z=-35..-32; hub toZ=-27. Pick on front faceZ=-32..-31.5. Set arm vertical when rocker is at its measured mid-angle (94.8116 degrees nominal).',
'Rigid arm must never contact the string. Test both directions; the return stroke may double-pluck or drag. If it does, develop a one-way compliant pick before scaling to twelve voices.'])
nextp()
header('P07 / P08 Retained pins and string tensioning','Turned journal pins; guided M4 drawbar. Standard threaded fasteners shown as pilot / major cylinders in STEP.')
lines(35,H-105,[
'P07 - TWO IDENTICAL TURNED PINS, STEEL: from rear to front, M3 x4 male root, 5 OD x1 flange, 3 h6 x9 journal, M2 x3 threaded tip. Add standard thread reliefs without reducing the usable journal. Install root into M3 blind crank / rocker hole; flange seats on front face. Retain with M2 nut and plain washer. Add 3.0 mm and 1.9 mm ID3.1 / OD5 spacers around the4 mm POM link; total stack8.9 leaves nominal0.1 mm axial play. Check free rotation after tightening, and use a locknut or equivalent positive locking method. Pins are custom turned parts, not plain dowels.',
'P06 - TWO END POSTS: aluminium6061-T6, 40 x125 x4. Local origin lower-left. Guide holes4.5 through at X20, Y42.803062 and95.067347. At each height add M4-screw clearance4.5 atX30 and guide-rod4 H7 atX10. Bottom mounting holes4.5 at(5,8) and(35,8). Guide holes for nylon need rounded, polished eyelets: no string on a raw aluminium edge.',
'P08 - TWO GUIDED DRAWBARS: brass or aluminium32 x12 x10. Local origin at centre in XY, rear faceZ0. Through M4 thread at(X10,Y0), guide bore4.2 at(X-10,Y0), nylon cross-hole2.0 alongY at(X0,Z5). Round string hole edgesR0.5 minimum and polish. STEP shows3.3 tap pilot. Use a4 mm smooth guide parallel to the M4 screw to prevent rotation. Start with M4x40 screw at tuning end; capture screw axially with washers/collar or thrust arrangement so turning moves the drawbar rather than the screw. The exact thrust stack must be checked in assembly before tensioning.',
'FIXTURE STRING SPAN: first guide atZ-70, second atZ272, total342. Place third bridge atZ260 for C3 (330 mm speaking from Z-70) orZ3.333333 for D5 (73.333333 speaking). Make a smooth removable bridge on a clamped wooden block with adjustable crown height matching the selected guide height. String outside the speaking span can be damped. A portable soundbox is not required for this force/release test.',
'ANCHORING: use an unwound nylon test string with smooth tie-block loops/knots at the drawbars. Do not trap nylon against a grub-screw point. Bring up tension gradually with eye protection and keep the bench clamped down. This is an adult workshop test fixture, not a classroom article.'
],121,10)
nextp()
header('Assembly, measurements and release gates','Hand crank first. A motor cannot fix a mechanism that binds or fails to release the string.')
lines(35,H-103,[
'1. Assemble the two fixtures independently. Verify carrier and shaft alignment, positive bearing retention, free rotation and fastener access. Set belt planes with actual purchased parts; confirm GT2 tooth compatibility with supplier before tightening. Use the slots to tension only enough to prevent tooth jumping.',
'2. Turn the pluck crank manually through at least two full revolutions before stringing. Verify there is no toggle, rubbing link, binding POM journal or shaft interference. Set the vertical arm at rocker mid-angle. Fit the long C3 arm and its low string configuration first.',
'3. Tune C3 with a tuner to130.8128 Hz. For the nominal0.8 mm nylon /1150 kg/m3 model, the ideal tension is about43.1 N (verify actual linear density; this is not a measured safe rating). Sweep pick intrusion from zero upwards in small steps. Record release angle, double-plucks, return drag, string damage and sound.',
'4. Measure crank torque with a spring scale at a known radius. At50 mm radius, torque[Nm] = force[N] x0.050. Record peak and running torque for string off/on and each pick thickness. Do not size a motor from stall torque. Repeat with the short D5 arm and73.333 mm speaking length; target588.6575 Hz.',
'5. Mark the ratio fixture shafts. Two input turns must produce nine output turns in the same direction. Run at3 rpm input /13.5 rpm output. Record belt tracking, backlash, tooth jumping and peak input torque; include the connected pluck module through an aligned5-to5 coupling after standalone tests. The separate fixtures are not coupled in the reference CAD.',
'6. Endurance: run1000 plucks at the final intended setting as an initial screening test, inspect nylon and picks, retighten/check fasteners and record any missed/double plucks. This is a proposed acceptance screen, not a validated service-life specification. Stop for cracks, pin migration, slipping clamps or fraying string.',
'7. Only then choose the motor and closed-loop speed control from measured torque and starting margin; preserve mechanical pitch/rotation ratios. Twelve synchronous plucks can add their reflected torque. One voice does not establish twelve-voice peak load, soundbox strength or final portable layout.',
'FABRICATION GATES: machinist confirms threads/fit tolerances and pin/clamp details; supplier confirms matched belt tooth profile and pulley dimensions; assemble complete base brackets, guide eyelets and tensioner thrust capture; perform physical release/force tests. None of these physical checks is claimed passed. Exact bought-parts candidates and source links are in the BOM/README.'
],122,10)
c.save();print('Saved8-page dimensioned drawing and test packet')
