from pathlib import Path
import csv,json,zipfile
from prototype_a_math import *
rows=[]
def add(id,qty,item,source,status,notes=''):rows.append(dict(id=id,quantity=qty,item=item,source=source,status=status,notes=notes))
D='https://www.dhm-online.com/en/toothed-pulleys-gt2/'
add('BUY01',1,'60T, 2 mm pitch, 6 mm belt, 5 mm bore aluminium pulley, DHM05010106',D+'389-gt2-pulley-o-5-mm-60-teeth-h6.html','Catalogue candidate','Hub/flange dimensions vary by batch; get drawing or measure before spacer manufacture')
add('BUY02',1,'30T, 2 mm pitch, 6 mm belt, 5 mm bore aluminium pulley, DHM05010107',D+'390-gt2-pulley-o-5-mm-30-teeth-h6.html','Catalogue candidate','Same profile as other pulleys and belts, supplier must confirm')
add('BUY03',2,'20T, 2 mm pitch, 6 mm belt, 5 mm bore aluminium pulley, DHM05010102',D+'385-gt2-pulley-o-5-mm-20-teeth-h6.html','Catalogue candidate','Two intermediate/output positions, not a 16T bored to bearing OD')
add('BUY04',2,'160 mm closed belt, 80 teeth, 2 mm pitch, 6 mm wide, DHM05030201','https://www.dhm-online.com/fr/courroie-gt2/438-courroie-neoprene-gt2-fermee-h-6-mm-80-dents-160-mm.html','HOLD profile confirmation','Current GT2 vs older S2M naming conflict. Do not buy a substituted profile merely because pitch is2 mm')
add('BUY05',10,'625-ZZ bearing, 5 x16 x5 mm','https://www.123roulement.com/roulement-palier/roulement-bille/simple-rangee/625-zz','Exact dimensional catalogue item','6 drive fixture +4 pluck fixture. Check manufacturer drawing and fits')
add('STOCK01',3,'5 mm ground steel shaft, 100 mm cut length','Stock / machine service','Specification, merchant not selected','Ratio fixture; tolerance h6/g6 to match actual bearings, collars on inner races')
add('STOCK02',2,'5 mm ground steel shaft, 96 mm cut length','Stock / machine service','Specification, merchant not selected','Pluck fixture; crank shaft must end at blind-bore depth52 globalZ')
add('BUY06',10,'5 mm bore split shaft collar, external retention','Motion supplier','Exact SKU to select','Two per shaft; envelope outside plate carriers, no preload; final thickness sets shaft spacing')
add('BUY07',1,'5-to-5 mm shaft coupling','Motion supplier','Exact SKU to select after alignment','Only to link two separately tested fixtures; not represented as coupled in CAD')
add('STOCK03',4,'Aluminium spacer tube OD8 / ID4.5 x50 mm','Cut stock / machine service','Specified cut part','Drive cheek spacing')
add('STOCK04',4,'Aluminium spacer tube OD8 / ID4.5 x30 mm','Cut stock / machine service','Specified cut part','Pluck cheek spacing')
add('BUY08',24,'M3x20 socket-head bolts, M3 nuts and washers','Metric fastener supplier','Standard specification','Ratio bearing-carrier clamps; check thread projection against pulleys')
add('BUY09',12,'M2x5 screws','Metric fastener supplier','Standard specification','Ratio bearing retainer, one face only')
add('BUY10',16,'M2x3 screws','Metric fastener supplier','Standard specification','Pluck cheek retainers on both faces; short screws avoid meeting in6 mm plate; machinist to confirm engagement')
add('BUY11',4,'M3x16 socket-head clamp bolts','Metric fastener supplier','Standard specification','Crank, rocker and two interchangeable arms; check head seating')
add('BUY12',2,'M2 locking nuts and washers','Metric fastener supplier','Standard specification','Journal pin retention; ensure nut tightens spacers without clamping POM link')
add('STOCK05',2,'Pin spacer ID3.1 / OD5 x3.0 mm','Turned stock','Custom cut / turn','Before POM link')
add('STOCK06',2,'Pin spacer ID3.1 / OD5 x1.9 mm','Turned stock','Custom cut / turn','After POM link; nominal0.1 axial running clearance')
add('BUY13',2,'M4x40 tension/anchor screws and axial capture washers/locknuts','Metric fastener supplier','Thrust stack to detail','Guide rod prevents drawbar rotation; captive screw must turn without moving axially')
add('STOCK07',2,'4 mm smooth steel guide rod, 50 mm','Cut stock','Specified','Keep parallel to M4 tension screw')
add('STOCK08',1,'Unwound nylon string, nominal0.8 mm, at least700 mm','Music string supplier','Actual linear density and tension rating needed','Tie loops and tails consume extra length; nominal43.1 N is an estimate not safe working rating')
add('BUY14',4,'Polished smooth string-guide eyelets, for4.5 mm post hole','Music/hobby supplier','Exact SKU / finished bore to confirm','No nylon on raw drilled aluminium edges; centre height must preserve speaking length')
add('STOCK09',1,'Plywood board140 x400 x12 mm','Wood cutting service','Cut stock','Pluck fixture; base holes drilled from assembled angle feet')
add('STOCK10',1,'Plywood board200 x120 x12 mm','Wood cutting service','Cut stock','Optional drive fixture bench base')
add('STOCK11',6,'20 x20 x2 angle, nominal40 mm long plus M4 mounting bolts','Cut stock / hardware shop','Drill to assembly','2 end-post feet +4 linkage cheek feet; board holes from fit-up. Not all brackets in CAD')
for id,qty,item in [('R01',2,'Drive cheek 180 x100 x6,6061-T6'),('R02',6,'Bearing carrier30 x50 x6,6061-T6'),('R03',14,'Bearing retainer27/8 x1 stainless'),('P01',2,'Pluck cheek140 x140 x6,6061-T6'),('P02',1,'Blind split-clamp crank,6061-T6'),('P03',1,'14 mm rocker with split hub,6061-T6'),('P04',1,'80 mm POM-C connecting rod'),('P05a',1,'C3 arm67.196938 mm,6061-T6'),('P05b',1,'D5 arm14.932653 mm,6061-T6'),('P06',2,'String end post40 x125 x4,6061-T6'),('P07',2,'Custom steel threaded journal pin'),('P08',2,'Guided tension drawbar32 x12 x10,brass/aluminium')]:
 add(id,qty,item,'CNC / sheet service','Quotation candidate; drawings govern','Machinist review required before production; STEP threads shown as pilots/nominal cylinders')
add('WEAR01',4,'Trial flexible pick strips PET0.5 mm','Sheet stock','Cut trial parts','Try multiple thicknesses and minimum intrusion; actual release not validated')
add('WOOD01',1,'Removable smooth third bridge on clampable wood block','Workshop / wood service','Fit-up part','Set correct crown height; bridge260 for C3 or3.333333 forD5 alongZ from fixture coordinates')
with (OUT/'Prototype_A_BOM.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
readme='''# Lovophone Prototype A - engineering review and quotation packet

This is a pair of physical test-fixture designs, not the full Lab Frame and not a physically proven instrument. The existing Lab Frame and Unified projects are preserved. No orders, uploads or supplier messages have been sent.

## Open these first

- Prototype_A_Drawings.pdf: eight dimensioned pages and the assembly/force/release test procedure.
- Lovophone_Prototype_A.FCStd: native CAD, independent ratio and pluck fixtures side by side. The stored short arm is a spare, not installed simultaneously.
- Prototype_A_BOM.csv: bought-part candidates, custom quantities, source URLs and unresolved selections. A listed SKU is not blanket approval of compatibility.
- Individual STEP files: custom quotation candidates. Prototype_A_Assembly_REFERENCE.step is an assembly reference, not a command to machine every object.
- Prototype_A_Calculations.json and Prototype_A_CAD_Check.json: computed geometry checks and their limits.

## What changed from the visual Lab Frame

The driven pendulum is retained. Its spring-loaded roller follower and 4x swing belt are replaced by an 80/4/80/14 mm pinned crank-rocker. It drives both directions and gives +/-16.662 degrees of swing. This tests a simpler manufacturing route before modifying the whole instrument. Full twelve-voice layout and matching MIDI have not been rebuilt around it.

The highest9:2 speed ratio is split into(60/20)*(30/20). Bearings are in separate carriers, not cut into tiny pulley hubs. With nominal160 mm belts, centre distances are37.836782 and54.907709 mm. Small pulley wrap improves to140.671 and173.353 degrees respectively (reference7.815 and9.631 teeth). These are calculations, not a belt strength approval.

The lively8-minute repeat remains the twelve-voice target:20-second input revolution, ratios1,9/8,5/4,3/2,5/3,2,9/4,5/2,3,10/3,4,9/2. This test fixture by itself does not generate an8-minute musical programme.

## What passed on the computer

10,001-phase exact linkage check: maximum closure error2.84e-14 mm; minimum transmission angle68.526 degrees. Native solid validity and144-pose moving rigid-link-to-fixed clearance sweep passed for low-C3 and high-D5 configurations. A rod/string interference was found and removed by positioning the linkage above both string heights. Flexible pick contact and release remain a physical test. The short-arm check swaps its geometry and string height in memory; its physical test remains outstanding.

## What must happen before machining / purchasing

1. Confirm an actually matched pulley/belt profile. DHM's current05030201 page saysGT2; an older catalogue calls itS2M. Those names are not automatically interchangeable. Confirm in writing or obtain a matched manufacturer's set.
2. Obtain supplier drawings or measure pulley batches: DHM warns dimensions other than bore may vary by+/-2 mm. The assembly uses hub/flange reservations. Bearing and shaft stack lengths and collars must be finalized from actual parts.
3. Machinist reviews blind crank bore/pin separation, thread runouts, clamp seating/bolt engagement, journal pin fits, bearing fits, short retainer screws and tolerances. Threads in STEP are not modeled thread forms: the PDF governs. The split hubs need real clamp grip before the slit closes.
4. Finish the standard base-angle mounting, polished string guides, bridge block and captive tension-screw thrust stack in assembly. Those interfaces are deliberately fit-up items, not a claim of a finished factory kit. The CAD does not represent every nut, washer, spacer or bracket.
5. Hand-test the plucking fixture and measure force before selecting the motor. No N20, stepper or other motor is asserted sufficient. A twelve-voice simultaneous pluck requires additional peak-load validation.

## Supplier shortlist / Paris

- DHM pulley candidates:05010106(60T),05010107(30T),05010102(20T), all5 mm bore/6 mm belt. Exact links in BOM. Its current site advertises worldwide shipping; confirm actual Paris checkout cost and availability. Price/stock are live, not a quote.
- 123Roulement625-ZZ5x16x5: https://www.123roulement.com/roulement-palier/roulement-bille/simple-rangee/625-zz
- CNC custom parts and turned pins: Xometry https://xometry.eu/fr/usinage-cnc/ or Protolabs Network https://www.hubs.com/fr/usinage-cnc/france/ . France delivery advertised; upload individual STEP and PDF only after release gates are resolved.
- Flat plates: a sheet service can cut outlines, but bearing seats and specified holes require machining. Do not accept laser kerf as a reamed fit.
- POM coupler: CNC quote alongside metal parts; a machined dry-bearing trial link, not an unspecified printed plastic substitute.

## UCAL

Identity awaiting Paul's website. If UCAL Systems(https://ucalsystems.com/capabilities/) is intended, it lists turning/milling, gear cutting and precision machining, but describes production quantities from hundreds to millions monthly. Its acceptance of a single instrument, complete bought-parts sourcing, assembly/testing, Paris delivery, price and lead time have not been confirmed. Do not promise one-stop supply or replace cheap catalogue bearings/belts with custom manufacture merely to use one vendor.

A one-vendor request should include: procure the bought parts, machine the custom candidates from reviewed drawings, finish fit-up interfaces, assemble one test fixture, return dimensional inspection and measured torque/release results, and quote delivery to Paris. That would be a commissioned engineering prototype, not just a bag of machined pieces. No such request has been sent.

## Physical acceptance

Use the PDF test sheet: free rotation without string; clean release and return with tuned nylon; torque measured at a known lever radius; exact2 input turns/9 output turns without slip; initial1000-pluck screen and inspection. Record actual settings and results. No physical pass is claimed. Without these tests I cannot honestly call the machine proven to work in reality.
'''
(OUT/'README.md').write_text(readme)
# Keep exports clean, no autosave backups in the deliverable bundle.
files=[p for p in OUT.iterdir() if p.is_file() and p.suffix not in ['.FCBak','.blend1']]
with zipfile.ZipFile(ROOT/'outputs/Lovophone_Prototype_A_Review.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,'Lovophone_Prototype_A/'+p.name)
with zipfile.ZipFile(ROOT/'outputs/Lovophone_Prototype_A_Review.zip') as z:assert z.testzip() is None
print('BOM lines',len(rows),'files in verified packet',len(files))
