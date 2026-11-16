import sys,json,csv,math,hashlib,zipfile,shutil
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from config import ROWS,ROOT as R
O=R/'outputs/LeLovophon_Pluck_Layout_R5';D=O/'Drive_Effort';W=R/'work/pluck_r5'
n=json.loads((D/'CAD_Force_Budget.json').read_text());old=json.loads((R/'outputs/LeLovophon_Monopole_R4/Drive_Effort/CAD_Force_Budget.json').read_text());e=json.loads((D/'Conditional_Force_Envelope.json').read_text());ex=json.loads((D/'Exudyn_Ideal_Dynamics_Verification.json').read_text());co=json.loads((D/'Exudyn_Simultaneous_Load_Transfer_Verification.json').read_text());assert ex['agreement_passed'] and co['force_transfer_agreement_passed']
v=n['per_voice'];previous=old['per_voice'];coef=n['all_12_simultaneous_hand_force_N_per_mm_common_string_deflection'];oldcoef=old['all_12_simultaneous_hand_force_N_per_mm_common_string_deflection'];improvement=1-coef/oldcoef
rows=[]
for r,x,y in zip(ROWS,v,previous):
 L=x['bridge_to_pick_mm']+x['pick_to_nut_mm'];fraction=x['bridge_to_pick_mm']/L
 rows.append(dict(voice=r['index'],note=r['note'],ratio=r['ratio'],speaking_length_mm=L,bridge_x_mm=r['bridge_x'],pick_x_mm=r['pick_x'],station_x_mm=r['station_x'],bridge_to_pick_mm=x['bridge_to_pick_mm'],pick_to_nut_mm=x['pick_to_nut_mm'],fraction_from_third_bridge=fraction,fraction_from_nearest_end=min(fraction,1-fraction),previous_bridge_to_pick_mm=y['bridge_to_pick_mm'],string_stiffness_N_per_mm=x['string_stiffness_N_per_mm']))
(O/'Plucking_Layout.json').write_text(json.dumps(dict(cad_sha256=n['cad_sha256'],design_choice='Practical tone/compliance compromise; six quarter-length positions then gradual movement toward the middle. Not an acoustically validated universal optimum.',nominal_string_tension_N=37.979683569383965,voices=rows),indent=2))
for path,rr in [(O/'Plucking_Positions.csv',rows),(D/'Per_Voice_Force_Transfer.csv',v)]:
 with path.open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rr[0]));writer.writeheader();writer.writerows(rr)
plt.rcParams.update({'font.size':10,'font.family':'sans-serif'})
fig,ax=plt.subplots(figsize=(11,6.7),layout='constrained');fig.patch.set_facecolor('#faf9f4');ax.set_facecolor('#faf9f4')
for i,(r,o) in enumerate(zip(rows,previous)):
 y=11-i;bx=r['bridge_x_mm'];px=r['pick_x_mm'];ox=bx+o['bridge_to_pick_mm'];L=r['speaking_length_mm']
 ax.plot([-324,321],[y,y],color='#d9d7ce',lw=1.1,zorder=1);ax.plot([bx,321],[y,y],color='#a88950',lw=2,zorder=2)
 ax.plot([bx+.25*L,bx+.75*L],[y,y],color='#b5d8ce',lw=8,alpha=.55,zorder=1,solid_capstyle='butt')
 ax.scatter([bx,321],[y,y],marker='|',s=90,color='#634f2c',zorder=3);ax.scatter([ox],[y],marker='x',s=35,color='#c86748',zorder=4);ax.scatter([px],[y],s=43,color='#11645b',zorder=5)
 ax.text(340,y,f'{min(r["fraction_from_third_bridge"],1-r["fraction_from_third_bridge"])*100:.0f}%',va='center',color='#11645b',fontsize=10)
ax.set_yticks(range(12),[r['note'] for r in reversed(rows)]);ax.set_xlabel('Position along the soundbox (mm)');ax.set_xlim(-345,385);ax.set_ylim(-.8,12);ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0);ax.grid(axis='x',alpha=.12)
ax.scatter([],[],s=43,color='#11645b',label='R5 pick');ax.scatter([],[],marker='x',s=35,color='#c86748',label='R4 pick');ax.plot([],[],color='#b5d8ce',lw=7,alpha=.7,label='Middle half of speaking string');ax.legend(loc='upper left',ncol=3,frameon=False,bbox_to_anchor=(0,1.04))
fig.suptitle('R5 — picks clear of both string ends',weight='bold',fontsize=16,x=.08,ha='left');ax.text(340,11.8,'From\nnearer end',fontsize=9,color='#11645b',va='bottom');fig.savefig(O/'Plucking_Layout.png',dpi=180);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(12,5.1),layout='constrained');fig.patch.set_facecolor('#faf9f4')
for ax in axs:ax.set_facecolor('#faf9f4');ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
x=np.arange(12);axs[0].bar(x-.18,[z['string_stiffness_N_per_mm'] for z in previous],width=.36,color='#c86748',label='R4');axs[0].bar(x+.18,[z['string_stiffness_N_per_mm'] for z in v],width=.36,color='#11645b',label='R5');axs[0].set_xticks(x,[r['note'] for r in rows],rotation=50);axs[0].set_ylabel('Sideways string stiffness (N/mm)');axs[0].set_title('C4: 6.18 mm → 75 mm from bridge',loc='left',weight='bold',fontsize=11);axs[0].legend(frameon=False)
x=np.linspace(0,.5,101)
axs[1].plot(x,x*oldcoef,lw=2,color='#c86748',label='R4');axs[1].plot(x,x*coef,lw=2.5,color='#11645b',label='R5');axs[1].scatter([.2],[.2*coef],color='#11645b');axs[1].annotate(f'0.2 mm → {coef*.2:.2f} N',xy=(.2,.2*coef),xytext=(.24,2.8),color='#11645b');axs[1].set_xlabel('Assumed sideways deflection of every string (mm)');axs[1].set_ylabel('Pluck-only hand force at 32 mm crank (N)');axs[1].set_title(f'{improvement*100:.0f}% lower shared-crossing sensitivity',loc='left',weight='bold',fontsize=11);axs[1].legend(frameon=False)
fig.suptitle('Conditional calculations — actual hand-crank force is unmeasured',weight='bold',fontsize=15);fig.text(.5,-.045,'Nominal tension 38 N per string. Excludes pick release, friction, impact and manufacturing tolerances.\nEqual-deflection scenarios describe the shared centre crossing, not the full-cycle operating peak.',ha='center',fontsize=9);fig.savefig(D/'Crank_Force_Comparison.png',dpi=180,bbox_inches='tight');plt.close(fig)
# Blank records are deliberate: no physical measurements have taken place.
with (D/'Pick_Test_Record.csv').open('w',newline='') as f:
 fields=['voice','note','tension_N','bridge_to_pick_mm','pick_to_nut_mm','forward_peak_tangential_force_N','reverse_peak_tangential_force_N','forward_release_string_deflection_mm','reverse_release_string_deflection_mm','test_conditions']
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for r in rows:w.writerow(dict(voice=r['voice'],note=r['note'],tension_N=37.979683569383965,bridge_to_pick_mm=r['bridge_to_pick_mm'],pick_to_nut_mm=r['pick_to_nut_mm']))
k=e['independent_per_voice_global_max_sum_hand_N_per_1N_each_tip']
(D/'README.md').write_text(f'''# R5 hand-crank force — calculated transfer, physical release/drag still unknown

**The actual required peak hand force is not yet known.** This report does not call an assumed pick deflection, force cap or friction torque a measurement. The previous 32 mm throw is retained.

## Geometry improvement

Twelve equal-gauge nominal 1.05 mm PVDF strings remain at nominal 37.98 N each. Speaking lengths and third bridges, tuning, proportional arm lengths, gear ratios, phase settings and 480-second ideal repeat are unchanged. Whole stations have moved along X. The six bass stations pluck one quarter of their own speaking length from the third bridge. The other six progress toward the middle. All positions are 25–47% of speaking length from the nearer end, avoiding near-end stiffness. This is a practical tone/compliance choice; sound is not physically evaluated.

C4 changes from 6.18 to75 mm from the third bridge. Its small-deflection lateral stiffness falls from {previous[5]['string_stiffness_N_per_mm']:.3f} to {v[5]['string_stiffness_N_per_mm']:.3f} N/mm. Its inverse-ratio speaking length remains300 mm.

## What the current numbers mean

For sideways deflection d and nominal fixed tension T, `F = T d (1/a + 1/b)`. Exact gear/four-bar leverage reflects each tip force to the common input shaft. At the all-12 shared centre crossing, equal sideways string deflection gives:

| Assumed displacement of each string | R4 pluck-only hand force | R5 pluck-only hand force |
|---|---:|---:|
| 0.1 mm | {oldcoef*.1:.2f} N | {coef*.1:.2f} N |
| 0.2 mm | {oldcoef*.2:.2f} N | {coef*.2:.2f} N |
| 0.5 mm | {oldcoef*.5:.2f} N | {coef*.5:.2f} N |

This is a {improvement*100:.1f}% reduction in that sensitivity. These rows are **conditional centre-crossing scenarios, not a predicted operating-force range or the full-cycle peak**. They omit PET bending/release, contact dynamics, friction and tolerance/alignment effects. Arm travel and nominal pick overlap are not the same as string displacement.

The ideal mechanism with no string forces or friction has {n['ideal_no_pick_no_friction_peak_absolute_hand_force_N']:.3f} N absolute peak hand force at constant3 rpm. Moving CAD mass is {n['moving_mass_kg']:.3f} kg across37 rigid groups. Exudyn1.13.6 independently reproduces the full480-second ideal dynamics within {ex['max_absolute_analytical_difference_Nm']:.3g} N·m. Its independent static0.2 mm shared-crossing load case agrees within {abs(co['difference_Nm']):.3g} N·m. Neither agreement establishes omitted real-world loads.

## A force budget we can actually test

For a measured maximum tangential resistance at each pick and a maximum total reflected drivetrain loss torque **under those working loads**, the conservative constant-speed model envelope is:

`F_hand ≲ Σ(J_i,max × F_pick_i,max) /0.032 + τ_loss,max/0.032 +0.363 N`

J is tip travel in metres per input radian. Each voice's maximum leverage is independently refined over a complete local crank revolution and rounded upward. Summing those separate maxima deliberately overestimates simultaneous load: it even allows pick force where the arm is not touching the string. The phase-preserving full-cycle sample gives a smaller bound. This is a numerical rigid-body envelope, not a formally certified bound or a claim about startup, jams or impact.

If every pick has the same measured force cap f, this becomes approximately:

`F_hand ≲ {k:.2f} × f +31.25 × τ_loss,max +0.363 N`

Here f is in newtons and τ is in N·m. For example, **if** each tip stays below0.10 N and total reflected drag stays below0.020 N·m, the conditional envelope is {k*.1+31.25*.02+.363:.2f} N. These are proposed test conditions, not measured or assumed-to-be-achievable properties of this machine. With0.15 N per tip and the same drag, it is {k*.15+31.25*.02+.363:.2f} N. Every extra0.01 N·m of drag costs0.3125 N at the current handle. A64 mm crank would halve hand force but would not reduce shaft/link/gear loads.

The PET tongue thickness is0.3 mm and its unsupported length approximately4.85 mm. Unknown sheet stiffness, clamping, tip finish, overlap, friction, creep and direction of travel control release. Nominal dimensions alone do not identify its force curve. Drivetrain drag also depends on alignment, bearing preload, lubrication and load; a dry unloaded reading alone does not prove loaded drag.

## Minimum physical test needed to settle the number

1. Use the specified line, tension and actual replaceable PET tongue/holder. A one-string fixture needs adjustable end anchors at the distances in `Pick_Test_Record.csv`; the unused string behind its third bridge must also be tensioned as in the instrument. Anchor test loads securely and keep eyes clear of tensioned line.
2. Record a **force-versus-travel trace through contact and complete release in both directions**, using a calibrated low-force load cell or gauge with suitable range and resolution;0.01 N or finer is useful near the0.1 N test condition. Move the real arm/tip along its actual arc and at its operating crossing speed, about24 mm/s at the shared centre crossing. A slow static pull alone will not capture impacts or stick-slip. Include repeat trials and intended pick adjustment extremes. Fill the blank CSV measurements; do not infer force from apparent string travel.
3. Use those measured curves with the preserved twelve phases in the dynamics model to estimate the combined torque waveform, and measure the assembled drivetrain's loaded losses, starting drag and alignment sensitivity. Simple dry spin-down is supplementary, not sufficient.
4. **The decisive check is the complete instrument.** Measure tangential force at the32 mm crank radius (or input torque with a calibrated torque sensor), capture starts, both plucking directions and every coincidence through at least one full480-second cycle at3 rpm. Keep the tangential lever arm known; a handheld gauge at an arbitrary pull angle will under-read. Repeat the highest-load events and intended adjustment extremes. Report peak force, sustained force and measurement uncertainty. Convert force to torque with τ=0.032F. Five newtons corresponds to0.160 N·m; ten newtons to0.320 N·m. Those are conversions, not performance claims.

The whole-machine trace checks both plucking and mechanical loss together. No physical test has been performed in this assessment. A peak-force target should be agreed before selecting a reduction stage or a final hand-crank throw.

## Free software and reproducibility

[Exudyn](https://github.com/jgerstmayr/EXUDYN) / [documentation](https://exudyn.readthedocs.io/en/latest/) was used here. [Project Chrono](https://github.com/projectchrono/chrono) and [MBDyn](https://www.mbdyn.org/) are other free multibody tools; no paid licence is needed. Their usefulness still depends on measured contact and loss inputs. [SKF](https://evolution.skf.com/en/using-a-friction-model-as-an-engineering-tool-3/) explains why friction depends on conditions. [UNSW string acoustics](https://phys.unsw.edu.au/jw/strings.html) and this [ASA research summary](https://acoustics.org/pressroom/httpdocs/167th/1pMU5_Ramsey.html) explain the connection between plucking position and harmonics; no universal best tone is claimed.

CAD SHA256 `{n['cad_sha256']}`. All numerical inputs, per-voice transfer, independent solver checks and standalone reproduction files accompany this note. This remains an unbuilt design, with operating force unresolved and no manufacturing release.
''')
P=D/'Reproduction';P.mkdir(exist_ok=True)
# Adapt the previously verified portable model to the revised inputs.
base=R/'outputs/LeLovophon_Monopole_R4/Drive_Effort/Reproduction'
for name in ['model.py','exudyn_check.py','exudyn_coincidence.py','requirements.txt','README.md']:shutil.copy2(base/name,P/name)
(P/'kinematics.json').write_text(json.dumps(dict(voices=ROWS,drive_yz=[65,-25]),indent=2));shutil.copy2(W/'mass_properties.json',P/'mass_properties.json')
s=(W/'force_envelope.py').read_text().replace('from force_model import','from model import');(P/'force_envelope.py').write_text(s)
print('REPORT_DONE',improvement,flush=True)
