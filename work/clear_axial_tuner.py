doc.openTransaction('Clear E arm from C tuner')
for name in ['C_TuningEnd_Foot','C_TuningEnd_Tower','C_TuningEnd_CrossBridge','C_TuningEnd_PinBlock','C_VerticalTuningPin']:
    obj=doc.getObject(name)
    shape=obj.Shape.copy()
    shape.translate(V(-4,0,0))
    obj.Shape=shape
doc.C_TuningEnd_Afterlength.Shape=axial_rod(V(118.65,40,50),V(126.65,40,45))
doc.recompute()
doc.commitTransaction()
axial_collisions=verify_axial_layout()
