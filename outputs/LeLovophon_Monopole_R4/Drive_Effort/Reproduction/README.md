# Reproduce the ideal force calculations

Use an isolated Python environment with the supplied requirements. Run `model.py`, then `exudyn_check.py 480 .005`, then `exudyn_coincidence.py .2`. Results appear in `Results/`. Units are SI internally; CAD geometry and exported notes identify millimetre inputs explicitly. No GUI or live FreeCAD instance is required. The Exudyn and virtual-work models verify the same ideal physics; agreement does not validate omitted friction or pick contact. Refer to the parent note for limitations and interpretation.
