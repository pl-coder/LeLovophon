import os,sys,json,math,time
from pathlib import Path
import numpy as np
import exudyn as exu
from exudyn.itemInterface import ObjectGround,PointGround,Rigid2D,RigidBody2D,MarkerBodyPosition,MarkerNodeCoordinate,CoordinateConstraint,RevoluteJoint2D,Force,SensorObject,SensorNode
from model import R,W,O,ROWS,DRIVE,groups,pose,geometry,linkage,loads,OMEGA,GRAV,transfer_at_zero
# Independent constrained 37-rigid-body planar dynamics; CAD groups reduced only by rigid aggregation.
SC=exu.SystemContainer();mbs=SC.AddSystem();ground=mbs.AddObject(ObjectGround());ng=mbs.AddNode(PointGround());mg=mbs.AddMarker(MarkerNodeCoordinate(nodeNumber=ng,coordinate=0))
bodies={};nodes={};coms={};eps=1e-6
for g in groups:
 c0,p0=pose(g,0);cm,pm=pose(g,-eps);cp,pp=pose(g,eps);vel=np.r_[(cp-cm)/(2*eps)*OMEGA,(pp-pm)/(2*eps)*OMEGA]
 n=mbs.AddNode(Rigid2D(name=g['key'],referenceCoordinates=[*c0,0],initialVelocities=[0,0,0]));ob=mbs.AddObject(RigidBody2D(name=g['key'],nodeNumber=n,mass=g['mass'],inertia=g['I']))
 bodies[g['key']]=ob;nodes[g['key']]=n;coms[g['key']]=c0
 mc=mbs.AddMarker(MarkerBodyPosition(bodyNumber=ob));mbs.AddLoad(Force(markerNumber=mc,loadVector=[0,0,0]))
def marker(k,p):
 p=np.array(p);pos=p if k is None else p-coms[k]
 return mbs.AddMarker(MarkerBodyPosition(bodyNumber=ground if k is None else bodies[k],localPosition=[*pos,0]))
def pin(a,b,p):return mbs.AddObject(RevoluteJoint2D(markerNumbers=[marker(a,p),marker(b,p)]))
pin(None,'Input',np.array(DRIVE)/1000)
mi=mbs.AddMarker(MarkerNodeCoordinate(nodeNumber=nodes['Input'],coordinate=2))
def uf(mbs,t,item,offset):return 0.0
def uft(mbs,t,item,offset):return 0.0
drive=mbs.AddObject(CoordinateConstraint(name='Input drive torque',markerNumbers=[mg,mi],offsetUserFunction=uf,offsetUserFunction_t=uft))
joints={}
for r in ROWS:
 i=r['index'];ck=f'{i:02d}_Crank';rk=f'{i:02d}_Rocker';co=f'{i:02d}_Coupler';Q=np.array(r['crank_yz'])/1000;P=np.array(r['pivot_yz'])/1000;a0,b0,_=linkage(r,r['phase_rad'])
 pin(None,ck,Q);pin(None,rk,P);ja=pin(ck,co,np.array(a0)/1000);jb=pin(rk,co,np.array(b0)/1000)
 mc=mbs.AddMarker(MarkerNodeCoordinate(nodeNumber=nodes[ck],coordinate=2));mbs.AddObject(CoordinateConstraint(markerNumbers=[mc,mi],factor1=-float(__import__('fractions').Fraction(r['ratio']))))
 joints[i]=(ja,jb)
sdrive=mbs.AddSensor(SensorObject(objectNumber=drive,writeToFile=False,storeInternal=True,outputVariableType=exu.OutputVariableType.Force))

case=float(sys.argv[1]) if len(sys.argv)>1 else .2
trans=transfer_at_zero()
for r,v in zip(ROWS,trans):
 p=np.array(r['pivot_yz'])/1000;p[0]-=(r['arm_radius_mm']-.15)/1000
 mk=marker(f"{r['index']:02d}_Rocker",p)
 mbs.AddLoad(Force(markerNumber=mk,loadVector=[0,v['string_stiffness_N_per_mm']*case,0]))
mbs.Assemble();ss=exu.SimulationSettings();ss.solution.file.write=False;ss.staticSolver.numberOfLoadSteps=1;ss.staticSolver.newton.absoluteTolerance=1e-12;ss.staticSolver.newton.relativeTolerance=1e-11
mbs.SolveStatic(ss)
torque=-float(mbs.GetObjectOutput(drive,exu.OutputVariableType.Force));expected=sum(v['handle_force_per_1mm_string_deflection_N'] for v in trans)*case*.032
report=dict(engine='Exudyn',version=exu.config.Version(),case='Fully constrained all-12 zero-crossing static force transfer. Assumed common sideways string deflection; not a flexible pick/contact simulation.',assumed_string_deflection_mm=case,exudyn_input_torque_Nm=torque,independent_virtual_work_input_torque_Nm=expected,difference_Nm=torque-expected,handle_force_N=torque/.032,force_transfer_agreement_passed=abs(torque-expected)<1e-7,friction_included=False,physical_test_passed=False)
(O/'Exudyn_Simultaneous_Load_Transfer_Verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
