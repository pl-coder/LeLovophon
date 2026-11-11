import math,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'outputs/LeLovophon_Monopole_R4'
# Castigliano unit-load check on a constant22x8mm curved cantilever strip;
# includes bending and St Venant torsion, but assumes perfectly fixed foot and rigid upper rail.
P=[(-143,-153),(-65,-195),(43,-189),(65,-130)]
def at(t):return [sum(math.comb(3,i)*(1-t)**(3-i)*t**i*P[i][j] for i in range(4)) for j in [0,1]]
E=69000;nu=.33;G=E/(2*(1+nu));w=22;t=8;Iweak=w*t**3/12;Istrong=t*w**3/12;J=w*t**3*(1/3-.21*t/w*(1-t**4/(12*w**4)))
flex=[0.,0.,0.];total=0.;maxbending_per_N=0.;maxtorsion_per_N=0
for i in range(10000):
 a=at(i/10000);b=at((i+1)/10000);m=[(a[j]+b[j])/2 for j in [0,1]];dy=b[0]-a[0];dz=b[1]-a[1];ds=math.hypot(dy,dz);uy,uz=dy/ds,dz/ds;ry,rz=65-m[0],-125-m[1];total+=ds
 # FX: moment vector (0,rz,-ry); component along centreline= torsion.
 mt=rz*uy-ry*uz;mn=-rz*uz-ry*uy
 flex[0]+=(mn**2/(E*Iweak)+mt**2/(G*J))*ds
 # FY / FZ: bending about X; plus axial strain contribution.
 flex[1]+=(rz**2/(E*Istrong)+uy**2/(E*w*t))*ds
 flex[2]+=(ry**2/(E*Istrong)+uz**2/(E*w*t))*ds
 maxbending_per_N=max(maxbending_per_N,abs(mn)*(t/2)/Iweak);maxtorsion_per_N=max(maxtorsion_per_N,abs(mt))
inv=json.loads((O/'Part_Inventory.json').read_text());rho={'Aluminium':.0027,'Steel':.00785,'Bearing steel':.0078,'Brass':.0085,'Acetal':.00141,'PVDF':.00178,'Birch plywood':.00065,'Beech':.0007,'Spruce':.00045,'Rubber':.0012,'PET':.00138,'PTFE':.0022,'Iglidur G':.00146,'Spring steel':.00785}
mass=lambda ps:sum(p['volume_mm3']*rho[p['material']] for p in ps)/1000
span=321-118;railI=math.pi*8**4/64
res=dict(scope='Preliminary elastic idealisation, not FEA, allowable loads or physical stiffness verification. Perfectly fixed roots, rigid clamps/rail and a constant22x8mm strip; ignores fastener compliance, wood movement, fillets, local notch stress, load sharing and joint slip. Illustrative10N force is assumed, not a measured operating or accidental load.',nominal_total_mass_kg=mass(inv),new_rear_frame_mass_kg=mass([p for p in inv if p['name'].startswith('R4_')]),curved_strip_centreline_length_mm=total,aluminium_E_MPa=E,weak_I_mm4=Iweak,strong_I_mm4=Istrong,torsion_J_mm4=J,single_rib_tip_compliance_mm_per_N=dict(along_bank_X=flex[0],vertical_Y=flex[1],front_back_Z=flex[2]),four_identical_ribs_assuming_equal_force_sharing_10N_total_deflection_mm=dict(along_bank_X=flex[0]*2.5,vertical_Y=flex[1]*2.5,front_back_Z=flex[2]*2.5),largest_rear_rail_support_span_mm=span,solid8mm_steel_rail_10N_midspan_deflection_mm=10*span**3/(48*200000*railI),physical_test_passed=False,manufacturing_release=False)
(O/'Checks/Preliminary_Stiffness_and_Mass.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
