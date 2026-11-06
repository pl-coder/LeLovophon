import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
import runpy
ns=runpy.run_path((_LOVOPHON_WORKSPACE + '/work/koto_cam_drive.py'),run_name='definitions');globals().update(ns)
a=[40,36,40,32,36,40];b=[40,32,32,24,24,24]
def wire(A,B,ra,rb):
    d=B-A;D=d.Length;d.normalize();p=V(0,-d.z,d.y);k=(ra-rb)/D;q=math.sqrt(1-k*k);n1=d*k+p*q;n2=d*k-p*q
    return Part.Wire([Part.makeLine(A+n1*ra,B+n1*rb),Part.Arc(B+n1*rb,B+d*rb,B+n2*rb).toShape(),Part.makeLine(B+n2*rb,A+n2*ra),Part.Arc(A+n2*ra,A-d*ra,A+n1*ra).toShape()])
for i,n in enumerate(notes):
    r1=a[i]/math.pi;r2=b[i]/math.pi;s=24*i
    doc.getObject(n+'_RatioDrivePulley').Shape=cy(r1,5,V()).cut(cy(3.05,7,V(-1,0,0)))
    doc.getObject(n+'_RatioDrivenPulley').Shape=cy(r2,5,V()).cut(cy(5.05,7,V(-1,0,0)))
    for suffix in ['_RatioDrivePulley','_RatioDrivenPulley']:
        o=doc.getObject(n+suffix);o.addProperty('App::PropertyLength','ReferencePitch','Belt');o.ReferencePitch=2
        o.Label=n+' 2 mm pitch reference pulley — '+str(a[i] if suffix=='_RatioDrivePulley' else b[i])+' teeth'
    A=V(s,-83,-131);B=V(s,-59,-116)
    doc.getObject(n+'_RatioBelt').Shape=Part.Face(wire(A,B,r1+.8,r2+.8)).cut(Part.Face(wire(A,B,r1+.1,r2+.1))).extrude(V(5,0,0))
if doc.getObject('Profiles'):
    for o in list(doc.Profiles.Group):doc.removeObject(o.Name)
    doc.removeObject('Profiles')
doc.recompute();doc.save()
print('Standard two-millimetre reference pitch set; tooth forms, belt lengths and tensioners remain to be detailed.')
