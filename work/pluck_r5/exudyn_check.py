import os,sys,json,math,time
from pathlib import Path
import numpy as np
import exudyn as exu
from exudyn.itemInterface import ObjectGround,PointGround,Rigid2D,RigidBody2D,MarkerBodyPosition,MarkerNodeCoordinate,CoordinateConstraint,RevoluteJoint2D,Force,SensorObject,SensorNode
from force_model import R,W,O,ROWS,DRIVE,groups,pose,geometry,linkage,loads,OMEGA,GRAV,transfer_at_zero
# Independent constrained 37-rigid-body planar dynamics; CAD groups reduced only by rigid aggregation.
SC=exu.SystemContainer();mbs=SC.AddSystem();ground=mbs.AddObject(ObjectGround());ng=mbs.AddNode(PointGround());mg=mbs.AddMarker(MarkerNodeCoordinate(nodeNumber=ng,coordinate=0))
bodies={};nodes={};coms={};eps=1e-6
for g in groups:
 c0,p0=pose(g,0);cm,pm=pose(g,-eps);cp,pp=pose(g,eps);vel=np.r_[(cp-cm)/(2*eps)*OMEGA,(pp-pm)/(2*eps)*OMEGA]
 n=mbs.AddNode(Rigid2D(name=g['key'],referenceCoordinates=[*c0,0],initialVelocities=vel.tolist()));ob=mbs.AddObject(RigidBody2D(name=g['key'],nodeNumber=n,mass=g['mass'],inertia=g['I']))
 bodies[g['key']]=ob;nodes[g['key']]=n;coms[g['key']]=c0
 mc=mbs.AddMarker(MarkerBodyPosition(bodyNumber=ob));mbs.AddLoad(Force(markerNumber=mc,loadVector=[-g['mass']*GRAV,0,0]))
def marker(k,p):
 p=np.array(p);pos=p if k is None else p-coms[k]
 return mbs.AddMarker(MarkerBodyPosition(bodyNumber=ground if k is None else bodies[k],localPosition=[*pos,0]))
def pin(a,b,p):return mbs.AddObject(RevoluteJoint2D(markerNumbers=[marker(a,p),marker(b,p)]))
pin(None,'Input',np.array(DRIVE)/1000)
mi=mbs.AddMarker(MarkerNodeCoordinate(nodeNumber=nodes['Input'],coordinate=2))
def uf(mbs,t,item,offset):return OMEGA*t
def uft(mbs,t,item,offset):return OMEGA
drive=mbs.AddObject(CoordinateConstraint(name='Input drive torque',markerNumbers=[mg,mi],offsetUserFunction=uf,offsetUserFunction_t=uft))
joints={}
for r in ROWS:
 i=r['index'];ck=f'{i:02d}_Crank';rk=f'{i:02d}_Rocker';co=f'{i:02d}_Coupler';Q=np.array(r['crank_yz'])/1000;P=np.array(r['pivot_yz'])/1000;a0,b0,_=linkage(r,r['phase_rad'])
 pin(None,ck,Q);pin(None,rk,P);ja=pin(ck,co,np.array(a0)/1000);jb=pin(rk,co,np.array(b0)/1000)
 mc=mbs.AddMarker(MarkerNodeCoordinate(nodeNumber=nodes[ck],coordinate=2));mbs.AddObject(CoordinateConstraint(markerNumbers=[mc,mi],factor1=-float(__import__('fractions').Fraction(r['ratio']))))
 joints[i]=(ja,jb)
sdrive=mbs.AddSensor(SensorObject(objectNumber=drive,writeToFile=False,storeInternal=True,outputVariableType=exu.OutputVariableType.Force))
# For this first verification no pick/contact or friction is invented. It checks exact masses, gravity, inertia and gearing.
sinput=mbs.AddSensor(SensorNode(nodeNumber=nodes['Input'],writeToFile=False,storeInternal=True,outputVariableType=exu.OutputVariableType.Coordinates))
mbs.Assemble();settings=exu.SimulationSettings();duration=float(sys.argv[1]) if len(sys.argv)>1 else 480.;step=float(sys.argv[2]) if len(sys.argv)>2 else .01
settings.timeIntegration.endTime=duration;settings.timeIntegration.numberOfSteps=int(round(duration/step));settings.timeIntegration.adaptiveStep=False;settings.timeIntegration.automaticStepSize=False
settings.timeIntegration.verboseMode=0;settings.timeIntegration.newton.relativeTolerance=1e-10;settings.timeIntegration.newton.absoluteTolerance=1e-11;settings.timeIntegration.generalizedAlpha.spectralRadius=.8
settings.solution.file.write=False;settings.solution.sensors.writePeriod=step;settings.linearSolver.solverType=exu.LinearSolverType.EigenSparse
print('SOLVE',duration,step,'bodies',len(groups),'version',exu.config.Version(),flush=True);start=time.monotonic();mbs.SolveDynamic(settings)
data=mbs.GetSensorStoredData(sdrive);coords=mbs.GetSensorStoredData(sinput);gv,it,J=loads(data[:,0]*OMEGA);expected=gv+it
# ConstraintForce is a Lagrange multiplier; its applied drive torque has opposite sign.
errpos=np.max(np.abs(data[:,1]-expected));errneg=np.max(np.abs(-data[:,1]-expected));sgn=1 if errpos<errneg else -1;actual=sgn*data[:,1];error=np.abs(actual-expected)
# Ignore only the initial acceleration consistency sample, report it separately.
report=dict(engine='Exudyn',version=exu.config.Version(),simulation_seconds=duration,step_seconds=step,wall_seconds=time.monotonic()-start,rigid_bodies=len(groups),physical_inputs='Exact CAD moving mass/centre/inertia; rigid ideal gears and 4-bar pin joints, gravity, prescribed3rpm; no friction or string force.',multiplier_to_drive_torque_sign=sgn,max_abs_torque_Nm=float(max(abs(actual))),max_absolute_analytical_difference_Nm=float(max(error[1:])),initial_difference_Nm=float(error[0]),input_angle_max_error_rad=float(np.max(np.abs(coords[:,3]-coords[:,0]*OMEGA))),agreement_passed=bool(np.max(error[1:])<1e-5),physical_test_passed=False)
(O/'Exudyn_Ideal_Dynamics_Verification.json').write_text(json.dumps(report,indent=2));np.savez(W/'exudyn.npz',time=data[:,0],torque=actual,analytical=expected);print(json.dumps(report,indent=2),flush=True)
