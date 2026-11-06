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
material per distinct colour. Written by hand because ``Import.export`` skips
shapes without triangulation data.
"""
import json
import math
import os
import struct
import time
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import FreeCAD as App  # noqa: E402
import MeshPart  # noqa: E402

ROOT = Path(os.environ.get("LOVOPHON_WORKSPACE", Path.cwd()))
FCSTD = Path(os.environ.get("LOVOPHON_FCSTD", ROOT / "outputs" / "Lovophone_Lab_Frame_Ratio_Review.FCStd"))
GLB = Path(os.environ.get("LOVOPHON_GLB", ROOT / "sim" / "page" / "assets" / "lovophon.glb"))
LINEAR_MM = float(os.environ.get("LOVOPHON_LINEAR", "0.5"))
ANGULAR_RAD = float(os.environ.get("LOVOPHON_ANGULAR", "0.6"))
KINDS = ("Driver", "Output", "LongArmRotor", "Rocker")
DEFAULT_COLOUR = (0.78, 0.80, 0.82)
MM_TO_M = 0.001


def gui_colours_and_visibility(path):
    """Diffuse colour and visibility per object from GuiDocument.xml.

    FreeCAD 1.x stores ShapeAppearance as a binary MaterialList file inside the
    archive: uint32 count, then per material four packed RGBA uint32 colours
    (ambient, diffuse, specular, emissive) in little-endian order, so the
    diffuse bytes are ``[alpha, b, g, r]`` at offsets 8..11.
    """
    colours, visible = {}, {}
    with zipfile.ZipFile(path) as archive:
        gui = ET.fromstring(archive.read("GuiDocument.xml"))
        for vp in gui.findall("./ViewProviderData/ViewProvider"):
            name = vp.attrib["name"]
            vis = vp.find("./Properties/Property[@name='Visibility']/Bool")
            visible[name] = vis is None or vis.attrib["value"] == "true"
            ml = vp.find("./Properties/Property[@name='ShapeAppearance']/MaterialList")
            if ml is not None and "file" in ml.attrib:
                try:
                    blob = archive.read(ml.attrib["file"])
                except KeyError:
                    continue
                if len(blob) >= 12 and struct.unpack("<I", blob[:4])[0] >= 1:
                    colours[name] = (blob[11] / 255, blob[10] / 255, blob[9] / 255)
    return colours, visible


def effectively_visible(obj, visible):
    """An object shows only if it and every container above it are visible."""
    seen = set()
    stack = [obj]
    while stack:
        o = stack.pop()
        if o.Name in seen:
            continue
        seen.add(o.Name)
        if not visible.get(o.Name, True):
            return False
        for parent in o.InList:
            if parent.TypeId in ("App::Part", "App::DocumentObjectGroup"):
                stack.append(parent)
    return True


def world_shape(obj):
    s = obj.Shape.copy()
    s.transformShape((obj.getGlobalPlacement() * obj.Placement.inverse()).toMatrix())
    return s


def mesh_of(shape):
    m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=LINEAR_MM, AngularDeflection=ANGULAR_RAD, Relative=False)
    points, facets = m.Topology
    return points, facets


class GlbBuilder:
    def __init__(self):
        self.bin = bytearray()
        self.buffer_views = []
        self.accessors = []
        self.meshes = []
        self.nodes = []
        self.materials = []
        self.material_index = {}
        self.triangles = 0

    def material(self, colour):
        key = tuple(round(c, 3) for c in colour)
        if key not in self.material_index:
            self.material_index[key] = len(self.materials)
            self.materials.append(
                {
                    "pbrMetallicRoughness": {"baseColorFactor": [*key, 1.0], "metallicFactor": 0.15, "roughnessFactor": 0.65},
                    "doubleSided": True,
                }
            )
        return self.material_index[key]

    def _view(self, data, target):
        while len(self.bin) % 4:
            self.bin += b"\0"
        offset = len(self.bin)
        self.bin += data
        self.buffer_views.append({"buffer": 0, "byteOffset": offset, "byteLength": len(data), "target": target})
        return len(self.buffer_views) - 1

    def primitive(self, points, facets, colour):
        """Indexed primitive with area-weighted vertex normals."""
        n = len(points)
        if n == 0 or not facets:
            return None
        normals = [[0.0, 0.0, 0.0] for _ in range(n)]
        for a, b, c in facets:
            pa, pb, pc = points[a], points[b], points[c]
            ux, uy, uz = pb.x - pa.x, pb.y - pa.y, pb.z - pa.z
            vx, vy, vz = pc.x - pa.x, pc.y - pa.y, pc.z - pa.z
            nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            for i in (a, b, c):
                normals[i][0] += nx
                normals[i][1] += ny
                normals[i][2] += nz
        pos = bytearray()
        nrm = bytearray()
        lo = [math.inf] * 3
        hi = [-math.inf] * 3
        for p, nv in zip(points, normals):
            xyz = (p.x * MM_TO_M, p.y * MM_TO_M, p.z * MM_TO_M)
            pos += struct.pack("<3f", *xyz)
            length = math.sqrt(nv[0] ** 2 + nv[1] ** 2 + nv[2] ** 2) or 1.0
            nrm += struct.pack("<3f", nv[0] / length, nv[1] / length, nv[2] / length)
            for i in range(3):
                lo[i] = min(lo[i], xyz[i])
                hi[i] = max(hi[i], xyz[i])
        idx = struct.pack(f"<{3 * len(facets)}I", *[i for f in facets for i in f])
        self.triangles += len(facets)
        pv = self._view(bytes(pos), 34962)
        nv_ = self._view(bytes(nrm), 34962)
        iv = self._view(idx, 34963)
        self.accessors.append({"bufferView": pv, "componentType": 5126, "count": n, "type": "VEC3", "min": lo, "max": hi})
        self.accessors.append({"bufferView": nv_, "componentType": 5126, "count": n, "type": "VEC3"})
        self.accessors.append({"bufferView": iv, "componentType": 5125, "count": 3 * len(facets), "type": "SCALAR"})
        base = len(self.accessors) - 3
        return {"attributes": {"POSITION": base, "NORMAL": base + 1}, "indices": base + 2, "material": self.material(colour)}

    def node(self, name, primitives, extras=None):
        primitives = [p for p in primitives if p]
        if not primitives:
            return
        self.meshes.append({"name": name, "primitives": primitives})
        node = {"name": name, "mesh": len(self.meshes) - 1}
        if extras:
            node["extras"] = extras
        self.nodes.append(node)

    def write(self, path):
        gltf = {
            "asset": {"version": "2.0", "generator": "LeLovophon sim/export_meshes.py"},
            "scene": 0,
            "scenes": [{"nodes": list(range(len(self.nodes)))}],
            "nodes": self.nodes,
            "meshes": self.meshes,
            "materials": self.materials,
            "accessors": self.accessors,
            "bufferViews": self.buffer_views,
            "buffers": [{"byteLength": len(self.bin)}],
        }
        js = json.dumps(gltf, separators=(",", ":")).encode()
        while len(js) % 4:
            js += b" "
        while len(self.bin) % 4:
            self.bin += b"\0"
        total = 12 + 8 + len(js) + 8 + len(self.bin)
        with open(path, "wb") as f:
            f.write(b"glTF" + struct.pack("<II", 2, total))
            f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
            f.write(struct.pack("<II", len(self.bin), 0x004E4942) + bytes(self.bin))
        return total


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
            points, facets = mesh_of(shape)
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

    rest = [o for o in doc.Objects if o.TypeId == "Part::Feature" and o.Name not in claimed]
    builder.node("static", prims_for(rest, local=False))

    GLB.parent.mkdir(parents=True, exist_ok=True)
    size = builder.write(GLB)
    hidden = [o.Name for o in doc.Objects if o.TypeId == "Part::Feature" and not effectively_visible(o, visible)]
    print(json.dumps({
        "glb": str(GLB), "bytes": size, "nodes": len(builder.nodes), "triangles": builder.triangles,
        "materials": len(builder.materials), "linear_mm": LINEAR_MM, "angular_rad": ANGULAR_RAD,
        "coloured_objects": len(colours), "hidden_solids_skipped": len(hidden), "seconds": round(time.time() - t0, 1),
    }, indent=1))


main()
