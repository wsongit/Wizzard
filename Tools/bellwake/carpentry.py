"""Lay the grain along cut timbers and the tile courses across sloping roofs."""
import re
import numpy as np
from mathutils import Vector

DISTRICTS = {
    "Bellmarket", "Reedwater", "PaperCourt", "ChainDock", "GlassRookery",
    "SillwaterEbb", "SillwaterFlood", "SillwaterOffice",
}
TIMBER = re.compile(r"\b(beam|timber|stud|rafter|jamb|lintel|brace|post|rail|plank|purlin|strut|spoke|joist|lath|sill|spar|mullion|crossbar|upright|stile)s?\b", re.I)
WOOD = {"Wood", "TarredOak"}
TILES = {"RoofTiles", "RoofSlate"}
UP = Vector((0, 0, 1))

def longest_axis(points):
    pts = np.array(points)
    deviations = pts - pts.mean(axis=0)
    lengths, axes = np.linalg.eigh(deviations.T @ deviations)
    if lengths[-1] < 2.2 * max(lengths[-2], 1.e-10):
        return None
    direction = Vector(axes[:, -1])
    major = max(range(3), key=lambda i: abs(direction[i]))
    if direction[major] < 0:
        direction.negate()
    return direction

def align(district, objects):
    if district not in DISTRICTS:
        return 0
    changed = 0
    for obj in objects:
        if obj.type != "MESH":
            continue
        names = {m.name for m in obj.data.materials if m}
        timber = bool(names & WOOD and TIMBER.search(obj.name))
        if not timber and not names & TILES:
            continue
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        mesh = obj.data
        points = [obj.matrix_world @ v.co for v in mesh.vertices]
        grain = longest_axis(points) if timber else None
        normals = obj.matrix_world.to_3x3().inverted_safe().transposed()
        uv = mesh.uv_layers.active.data
        for poly in mesh.polygons:
            material = mesh.materials[poly.material_index].name
            normal = (normals @ poly.normal).normalized()
            if material in TILES and .20 < abs(normal.z) < .98:
                along = (UP - normal * normal.z).normalized()
                repeat = 1.8
            elif material in WOOD and grain and abs(normal.dot(grain)) < .65:
                along = (grain - normal * grain.dot(normal)).normalized()
                repeat = 1.55
            else:
                continue
            across = along.cross(normal).normalized()
            for loop in poly.loop_indices:
                point = points[mesh.loops[loop].vertex_index]
                uv[loop].uv = (point.dot(across) / repeat, point.dot(along) / repeat)
            changed += 1
    return changed
