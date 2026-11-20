"""Unwrap the visible panels of closed wooden doors, crates and barrel heads."""
from mathutils import Vector
from surface_paint import COLUMNS, GUTTER, PANEL_NAMES, PANEL_SIZE, PITCH

PANELS = {
    "Front door": "door", "Timber door": "door", "Glasshouse oak door": "door",
    "Plank door": "door-boards", "Panelled door": "door-boards",
    "Shuttered casement": "window", "Dispatch crate": "crate",
    "Stacked rope cask": "cask", "Tarred barrel staves": "cask",
}
UP = Vector((0, 0, 1))


def bind(objects, material):
    count = 0
    for obj in objects:
        if obj.type != "MESH" or obj.get("batch", "").startswith("C_"):
            continue
        name = obj.name.split(".")[0]
        panel = PANELS.get(name)
        if name.endswith(" solid door panel"):
            panel = "door-boards"
        elif name.endswith(" hinged shutter"):
            panel = "shutter"
        if panel is None or material in obj.data.materials[:]:
            continue
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        mesh = obj.data
        # Use transformed corners. Some market houses predate the other sets and
        # carry their scale and rotation on the object rather than on the vertices.
        positions = [obj.matrix_world @ v.co for v in mesh.vertices]
        candidates = []
        for face in mesh.polygons:
            a, b, c = (positions[i] for i in face.vertices[:3])
            normal = (b - a).cross(c - a)
            area = normal.length
            if area == 0:
                continue
            normal.normalize()
            top = panel == "cask"
            if (top and normal.z > .9) or (not top and abs(normal.z) < .25):
                candidates.append((face, normal, area))
        if not candidates:
            continue
        maximum = max(area for _, _, area in candidates)
        index = PANEL_NAMES.index(panel)
        slot = len(mesh.materials)
        mesh.materials.append(material)
        uv = mesh.uv_layers.active.data
        for face, normal, area in candidates:
            if panel not in ("crate", "cask") and area < .85 * maximum:
                continue
            right = Vector((1, 0, 0)) if panel == "cask" else UP.cross(normal).normalized()
            up = normal.cross(right).normalized()
            corners = [(positions[i].dot(right), positions[i].dot(up)) for i in face.vertices]
            lo = [min(p[j] for p in corners) for j in (0, 1)]
            hi = [max(p[j] for p in corners) for j in (0, 1)]
            for loop, (x, y) in zip(face.loop_indices, corners):
                u = (x - lo[0]) / (hi[0] - lo[0])
                v = (y - lo[1]) / (hi[1] - lo[1])
                # Inset the sample to the centre of the end texels.
                uv[loop].uv = ((index % COLUMNS * PITCH + GUTTER + .5 + u * (PANEL_SIZE - 1)) / (COLUMNS * PITCH),
                               1 - (index // COLUMNS * PITCH + GUTTER + .5 + (1 - v) * (PANEL_SIZE - 1)) / (2 * PITCH))
            face.material_index = slot
            count += 1
    return count


def bind_staves(objects, material):
    import math
    for obj in objects:
        if obj.type != "MESH" or obj.name.split(".")[0] not in ("Stacked rope cask", "Tarred barrel staves", "Bound oak pail"):
            continue
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        mesh = obj.data
        points = [obj.matrix_world @ v.co for v in mesh.vertices]
        bottom = min(p.z for p in points)
        height = max(p.z for p in points) - bottom
        cx = sum(p.x for p in points) / len(points)
        cy = sum(p.y for p in points) / len(points)
        angles = [math.atan2(p.y - cy, p.x - cx) for p in points]
        # Start the wrap on an actual stave joint, including rotated barrels.
        fractions = [((a - angles[0]) / math.tau) % 1 for a in angles]
        fractions = [0.0 if u > .99999 else u for u in fractions]
        slot = mesh.materials.find(material.name)
        if slot < 0:
            slot = len(mesh.materials)
            mesh.materials.append(material)
        uv = mesh.uv_layers.active.data
        for poly in mesh.polygons:
            a,b,c = (points[i] for i in poly.vertices[:3])
            if abs((b-a).cross(c-a).normalized().z) >= .80:
                continue
            us = [fractions[i] for i in poly.vertices]
            seam = max(us) - min(us) > .5
            for loop, index, u in zip(poly.loop_indices, poly.vertices, us):
                if seam and u < .5:
                    u += 1
                v = (points[index].z - bottom) / height
                uv[loop].uv = ((132.5 + 119 * u) / 256, (4.5 + 55 * v) / 128)
            poly.material_index = slot


def well_face_uv(band, sector, sectors, height, next_height):
    # Four circumferential repeats give the ring distinct blocks; its upper
    # bevel, coping and inner lip occupy a second painted strip on the same sheet.
    u0, u1 = 4 * sector / sectors, 4 * (sector + 1) / sectors
    if 2 <= band <= 5:
        # Measured travel across the bevel and the top, from the outside inward.
        profile = (.00, .10, .28, .88, 1.0)
        v0, v1 = ((39.5 - 35 * p) / 128 for p in profile[band-2:band])
    else:
        v0, v1 = ((48.5 + 75 * max(0, min(1, (h + .03) / .71))) / 128 for h in (height, next_height))
    return [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]
