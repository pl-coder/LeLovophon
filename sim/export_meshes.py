"""Export the Lab Frame Ratio Review to a glTF binary for the browser page.

Run with FreeCAD's headless interpreter from the repository root:

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd \
        -c "exec(open('sim/export_meshes.py').read())"

Environment overrides: ``LOVOPHON_FCSTD`` (input document), ``LOVOPHON_GLB``
(output), ``LOVOPHON_LINEAR`` / ``LOVOPHON_ANGULAR`` (mesh deflection in mm
and radians).

Nodes in the GLB:

- ``<note>_<kind>`` for each voice and kind in Driver, Output, LongArmRotor,
  Rocker: the children of that App::Part, in the Part's local frame. The page
  sets each node's translation and X-axis rotation from ``sim.lovophon.poses``.
- ``<note>_bridge``: the voice's third bridge and crown, in world coordinates,
  so the page can slide it along X when the bridge slider moves.
- ``static``: every other visible solid, in world coordinates.

Hidden objects (the saved presentation hides the motor and the obsolete tray
parts) are left out. Belts stay as static reference geometry, as in Paul's own
animation. Colours come from each object's saved ShapeAppearance.

Geometry is indexed with per-vertex normals averaged over adjacent faces, one
material per distinct colour (``sim/glbwriter.py``, shared with the R5
exporter).
"""
import json
import os
import sys
import time
from pathlib import Path

import FreeCAD as App  # noqa: E402

ROOT = Path(os.environ.get("LOVOPHON_WORKSPACE", Path.cwd()))
sys.path.insert(0, str(ROOT))
from sim.glbwriter import GlbBuilder, effectively_visible, gui_colours_and_visibility, mesh_of, world_shape  # noqa: E402

FCSTD = Path(os.environ.get("LOVOPHON_FCSTD", ROOT / "outputs" / "Lovophone_Lab_Frame_Ratio_Review.FCStd"))
GLB = Path(os.environ.get("LOVOPHON_GLB", ROOT / "sim" / "page" / "assets" / "lovophon.glb"))
LINEAR_MM = float(os.environ.get("LOVOPHON_LINEAR", "0.5"))
ANGULAR_RAD = float(os.environ.get("LOVOPHON_ANGULAR", "0.6"))
KINDS = ("Driver", "Output", "LongArmRotor", "Rocker")
DEFAULT_COLOUR = (0.78, 0.80, 0.82)


def main():
    t0 = time.time()
    colours, visible = gui_colours_and_visibility(FCSTD)
    doc = App.openDocument(str(FCSTD))
    rows = json.loads(doc.Motion.LinkageGeometry)
    builder = GlbBuilder()
    claimed = set()

    def prims_for(objects, local):
        out = []
        for o in objects:
            if o.TypeId != "Part::Feature" or not effectively_visible(o, visible):
                continue
            shape = o.Shape if local else world_shape(o)
            if shape.isNull():
                continue
            points, facets = mesh_of(shape, LINEAR_MM, ANGULAR_RAD)
            out.append(builder.primitive(points, facets, colours.get(o.Name, DEFAULT_COLOUR)))
            claimed.add(o.Name)
        return out

    for row in rows:
        n = row["note"]
        for kind in KINDS:
            part = doc.getObject(f"{n}_{kind}")
            builder.node(f"{n}_{kind}", prims_for(part.Group, local=True), {"voice": row["display_note"], "kind": kind})
        bridge = [doc.getObject(f"{n}_KotoThirdBridge"), doc.getObject(f"{n}_NylonBridgeCrown")]
        builder.node(f"{n}_bridge", prims_for([b for b in bridge if b], local=False), {"voice": row["display_note"], "kind": "bridge", "bridge_x_mm": row["bridge_x"]})
        string = [doc.getObject(f"{n}_KotoSpeakingString")]
        builder.node(f"{n}_string", prims_for([s for s in string if s], local=False), {"voice": row["display_note"], "kind": "string"})

    rest = [o for o in doc.Objects if o.TypeId == "Part::Feature" and o.Name not in claimed]
    builder.node("static", prims_for(rest, local=False))

    shaft = doc.getObject("CommonInputShaft_D6")
    extras = {}
    if shaft is not None:
        bb = world_shape(shaft).BoundBox
        extras["input_shaft_mm"] = {"x_min": bb.XMin, "x_max": bb.XMax, "y": (bb.YMin + bb.YMax) / 2, "z": (bb.ZMin + bb.ZMax) / 2, "radius": (bb.YMax - bb.YMin) / 2}
    tuner = doc.getObject("KotoTunerBlock")
    if tuner is not None:
        extras["tuner_block_x_mm"] = world_shape(tuner).BoundBox.Center.x
    builder.nodes[-1]["extras"] = extras

    GLB.parent.mkdir(parents=True, exist_ok=True)
    size = builder.write(GLB, "LeLovophon sim/export_meshes.py")
    hidden = [o.Name for o in doc.Objects if o.TypeId == "Part::Feature" and not effectively_visible(o, visible)]
    print(json.dumps({
        "glb": str(GLB), "bytes": size, "nodes": len(builder.nodes), "triangles": builder.triangles,
        "materials": len(builder.materials), "linear_mm": LINEAR_MM, "angular_rad": ANGULAR_RAD,
        "coloured_objects": len(colours), "hidden_solids_skipped": len(hidden), "seconds": round(time.time() - t0, 1),
    }, indent=1))


main()
