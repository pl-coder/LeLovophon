# Lovophone Prototype A - engineering review and quotation packet

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

## Manufacturing route

UCAL Systems is a prospective machining and assembly route. Acceptance of a one-off prototype, sourcing, engineering review, testing, price and Paris delivery remain unconfirmed. No supplier order has been placed.

## Physical acceptance

Use the PDF test sheet: free rotation without string; clean release and return with tuned nylon; torque measured at a known lever radius; exact2 input turns/9 output turns without slip; initial1000-pluck screen and inspection. Record actual settings and results. No physical pass is claimed. Without these tests I cannot honestly call the machine proven to work in reality.
