import os as _lovophon_os
from pathlib import Path as _LovophonPath
_LOVOPHON_WORKSPACE = _lovophon_os.environ.get('LOVOPHON_WORKSPACE', str(_LovophonPath(__file__).resolve().parents[1]))
# Use a signed distance property for heights below Y=0.
for i,n in enumerate('CDEFGA'):
    st=doc.getObject(n+'_LongSpeakingString');target=doc.C_LongSpeakingString.Shape.CenterOfMass.y-10*i
    old=st.VerticalY.Value;st.removeProperty('VerticalY');st.addProperty('App::PropertyDistance','VerticalY','Geometry');st.VerticalY=target
    for suffix in ['_LongSpeakingString','_BackStringSegment']:
        obj=doc.getObject(n+suffix);shape=obj.Shape.copy();shape.translate(V(0,target-shape.CenterOfMass.y,0));obj.Shape=shape
    for obj in doc.CommonStringEnds.Group:
        if obj.Name.startswith(n+'_Shared'):
            shape=obj.Shape.copy();shape.translate(V(0,target-old,0));obj.Shape=shape
# Sixth-voice support follows the new signed height.
h=doc.A_LongSpeakingString.VerticalY.Value
doc.A_AnchorTower.Shape=sb(6,h+105,6,118,-109,-91)
# Rebuild axes and belts without shifting the string bank a second time.
exec(open((_LOVOPHON_WORKSPACE + '/work/soundbox.py')).read().replace('V(0,0,14)','V(0,0,0)'))
soundbox_rows=relocate_arms()
doc.recompute();check_soundbox(soundbox_rows);doc.save()
