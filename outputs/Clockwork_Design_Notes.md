# See-through clockwork and an antique winding key

This version adds a clockwork layout to the existing low-nylon-string harp. The string bed, ratios and pendulum geometry are retained. The new unit sits at the right end of the common input axle, toward the back of the soundbox. The old placeholder input collar is replaced by the clockwork coupling.

The educational sequence is: **WIND → STORE → TURN → PLUCK**. A removable pierced brass-style butterfly key fits a nominal 4 mm square winding arbor. Winding loads a contained mainspring barrel. The winding ratchet and click are shown separately so their anti-return role is visible. The spring barrel drives a 60-tooth wheel, a 24-tooth idler and a 20-tooth output wheel. The idler transfers rotation; the overall barrel-to-output speed ratio is 3:1. Two gear meshes leave the output turning in the same direction as the barrel.

The three main wheels use sampled involute profiles, 0.75 mm module and 20° pressure angle with nominal backlash. Sixteen sampled positions across one barrel tooth interval showed no positive-volume tooth intersections. This is a geometric mesh check, not proof of adequate backlash, tooth strength, bearing clearance or manufacturability.

Clear outer panels and a transparent cartridge inspection face make the internal layout visible in the CAD model. A small balance wheel, illustrative hairspring and lever escapement show the intended regulation architecture. The clear case encloses this clockwork module only; the rest of the instrument remains open as requested earlier. The brass appearance and scalloped open key bows are styling choices; no finish or alloy has been specified.

**This is an educational CAD concept, not a working or rated clock movement.** The escapement still needs a resolved pallet profile, locking and impulse geometry, oscillator frequency and spring selection. The spring cartridge needs a specified energy capacity, containment rating, inner/outer spring attachments and validated winding click. The harp's measured torque per pluck, starting torque, losses and acceptable speed variation are needed before selecting the spring and claiming runtime. The model deliberately contains no runtime claim. Shaft couplings, bearing retention, fastening, winding stop and a controlled run/stop function need engineering. Do not manufacture or wind the illustrated spring cartridge as drawn; use a suitably rated cartridge as the basis of the next mechanical design.

The assembled envelope including the key is approximately 394 × 202 × 179 mm. Display colours, transparent panels and visible parts are saved into the native FreeCAD file using an isolated offscreen writer. The interactive FreeCAD app was not controlled during this change. The PNG illustrations are offline renders; the outer clear skins are represented by outlines in those renders to reveal the components.

Files:
- `Harpe_d_Amour_Clockwork.FCStd` — native design with saved display settings.
- `Harpe_d_Amour_Clockwork.step` — solid geometry exchange copy; colours/transparency may differ by viewer.
- `Harpe_Clockwork_Preview.png` — overview and clockwork close-up.
- `Antique_Winding_Key.png` — winding key detail.

Background references for the power path and winding click:
- Horopedia, “Power Source”: https://horopedia.org/motor-organ-power-source/
- Clockworks, mainsprings: https://www.clockworks.com/clock-parts/clock-mainsprings.html
- AWCI, winding ratchet, arbor and barrel relationship: https://www.awci.com/wp-content/uploads/ht/1995/1995-11-web.pdf
