"""Export Plucking Layout R5 to a glTF binary for the browser page.

Run with FreeCAD's headless interpreter from the repository root:

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd \
        -c "exec(open('sim/export_meshes_r5.py').read())"

Environment overrides: ``LOVOPHON_R5_FCSTD`` (input), ``LOVOPHON_R5_GLB``
(output), ``LOVOPHON_LINEAR`` / ``LOVOPHON_ANGULAR`` (mesh deflection in mm and
radians).

R5's 1101 solids are loose ``Part::Feature`` objects placed in world
coordinates at the saved pose (the shared centre crossing, t = 0). Each one
carries ``Motion`` (Fixed / Input / Crank / Rocker / Pendulum / Coupler) and
``Voice`` (1..12, 0 for shared parts). The exporter groups them into rigid
nodes whose vertices are written relative to the node's rotation centre, so
the page poses a node by setting its rotation about X (and, for a coupler,
its translation):

- ``input``: every ``Input`` part, about the drive axis ``drive_yz``;
- ``V##_crank``: about ``crank_yz``;
- ``V##_rocker``: ``Rocker`` and ``Pendulum`` parts, about ``pivot_yz``;
- ``V##_coupler``: the pushrod and its bushes, about the saved crank pin ``a0``;
- ``V##_string``, ``V##_bridge``: the speaking string and third bridge, world;
- ``static``: everything else, world.

Rows come from ``sim/lovophon/r5_design.json``; refresh that first after a
CAD revision (``python3 -m sim.lovophon --snapshot-r5``).
"""
import json
import math
import os
import sys
import time
from pathlib import Path

import FreeCAD as App  # noqa: E402

ROOT = Path(os.environ.get("LOVOPHON_WORKSPACE", Path.cwd()))
sys.path.insert(0, str(ROOT))
from sim.glbwriter import GlbBuilder, effectively_visible, gui_colours_and_visibility, mesh_of, world_shape  # noqa: E402
from sim.lovophon import r5  # noqa: E402

FCSTD = Path(os.environ.get("LOVOPHON_R5_FCSTD", ROOT / "outputs" / "LeLovophon_Pluck_Layout_R5" / "LeLovophon_Pluck_Layout_R5.FCStd"))
GLB = Path(os.environ.get("LOVOPHON_R5_GLB", ROOT / "sim" / "page" / "assets" / "lovophon_r5.glb"))
LINEAR_MM = float(os.environ.get("LOVOPHON_LINEAR", "0.5"))
ANGULAR_RAD = float(os.environ.get("LOVOPHON_ANGULAR", "0.6"))
DEFAULT_COLOUR = (0.78, 0.80, 0.82)


def prop(obj, name, default=None):
    return getattr(obj, name) if hasattr(obj, name) else default


def main():
    t0 = time.time()
    design = r5.load_design()
    colours, visible = gui_colours_and_visibility(FCSTD)
    doc = App.openDocument(str(FCSTD))
    builder = GlbBuilder()
    parts = [o for o in doc.Objects if o.TypeId == "Part::Feature" and effectively_visible(o, visible) and not o.Shape.isNull()]
    by_key = {}
    for o in parts:
        by_key.setdefault((prop(o, "Motion", "Fixed"), int(prop(o, "Voice", 0))), []).append(o)
    claimed = set()

    def prims(objects, origin_mm):
        out = []
        for o in objects:
            points, facets = mesh_of(world_shape(o), LINEAR_MM, ANGULAR_RAD)
            out.append(builder.primitive(points, facets, colours.get(o.Name, DEFAULT_COLOUR), origin_mm))
            claimed.add(o.Name)
        return out

    drive = design["drive_yz"]
    inputs = [o for (motion, _), objs in by_key.items() if motion == "Input" for o in objs]
    builder.node("input", prims(inputs, (0.0, drive[0], drive[1])), {"kind": "Input", "axis_yz": drive}, translation_mm=(0.0, drive[0], drive[1]))

    for row in design["voices"]:
        v = row["index"]
        note = row["note"]
        crank = (0.0, *row["crank_yz"])
        pivot = (0.0, *row["pivot_yz"])
        a0 = r5.coupler_anchor(row)
        anchor = (0.0, a0[0], a0[1])
        builder.node(f"{note}_crank", prims(by_key.get(("Crank", v), []), crank), {"voice": row["display_note"], "kind": "Crank"}, translation_mm=crank)
        rocker = by_key.get(("Rocker", v), []) + by_key.get(("Pendulum", v), [])
        builder.node(f"{note}_rocker", prims(rocker, pivot), {"voice": row["display_note"], "kind": "Rocker"}, translation_mm=pivot)
        builder.node(f"{note}_coupler", prims(by_key.get(("Coupler", v), []), anchor), {"voice": row["display_note"], "kind": "Coupler"}, translation_mm=anchor)
        string = doc.getObject(f"{note}_FluorocarbonString")
        bridge = doc.getObject(f"{note}_ThirdBridge")
        builder.node(f"{note}_string", prims([string] if string else [], (0.0, 0.0, 0.0)), {"voice": row["display_note"], "kind": "string"})
        builder.node(f"{note}_bridge", prims([bridge] if bridge else [], (0.0, 0.0, 0.0)), {"voice": row["display_note"], "kind": "bridge", "bridge_x_mm": row["bridge_x"]})

    rest = [o for o in parts if o.Name not in claimed]
    builder.node("static", prims(rest, (0.0, 0.0, 0.0)), {"design": "Plucking Layout R5", "nut_x_mm": r5.NUT_X})

    GLB.parent.mkdir(parents=True, exist_ok=True)
    size = builder.write(GLB, "LeLovophon sim/export_meshes_r5.py")
    print(json.dumps({
        "glb": str(GLB), "bytes": size, "nodes": len(builder.nodes), "triangles": builder.triangles,
        "materials": len(builder.materials), "parts": len(parts), "moving": len(parts) - len(rest),
        "linear_mm": LINEAR_MM, "angular_rad": ANGULAR_RAD, "seconds": round(time.time() - t0, 1),
    }, indent=1))


main()
