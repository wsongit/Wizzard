"""Continue the opening clearing all the way around a room-scale player."""

import math
import bpy
from mathutils.bvhtree import BVHTree


def landscape(bank, group, paint, stem, foliage):
    n = 32
    # The original grove's second ring is its widest one. Start exactly on that lip.
    near = [tuple(bank.data.vertices[n + i].co) for i in range(n)]
    rings = [near]
    for j, (rx, ry, lift) in enumerate(
        (
            (18, 17, 0.7),
            (24, 22, 2.4),
            (34, 32, 1.7),
            (49, 45, 5.7),
            (64, 61, 11.5),
            (89, 83, 7),
        )
    ):
        row = []
        for i in range(n):
            a = math.tau * i / n
            swell = (
                0.65
                + 0.34 * math.cos(3 * a + j * 0.19)
                + 0.15 * math.sin(7 * a - 0.32 * j)
            )
            z = lift * swell + 0.35 * math.sin(a * 5 + 0.74 * j)
            row.append((rx * math.cos(a), ry * math.sin(a), z))
        rings.append(row)
    verts = [p for r in rings for p in r]
    faces = [
        (j * n + i, (j + 1) * n + i, (j + 1) * n + (i + 1) % n, j * n + (i + 1) % n)
        for j in range(len(rings) - 1)
        for i in range(n)
    ]
    m = bpy.data.meshes.new("Ground behind the clearing")
    m.from_pydata(verts, [], faces)
    m.materials.append(paint("ChoirLoam"))
    m.update()
    land = bpy.data.objects.new("Ground behind the clearing", m)
    group.objects.link(land)
    layer = m.uv_layers.new()
    for f in m.polygons:
        for li in f.loop_indices:
            p = m.vertices[m.loops[li].vertex_index].co
            layer.data[li].uv = (p.x * 0.75, p.y * 0.75)
    soil = BVHTree.FromPolygons(verts, faces)
    for thicket, (x, y) in enumerate(
        ((-13, 8), (-15, -7), (-5, -15), (10, -12), (15, 4), (6, 16))
    ):
        for j, (dx, dy, h) in enumerate(
            ((-0.98, 0.31, 4.7), (0.26, -0.90, 3.6), (1.39, 0.71, 5.4))
        ):
            px, py = x + dx, y + dy
            z = soil.ray_cast((px, py, 20), (0, 0, -1))[0].z
            lean = 0.36 * math.cos(thicket + j)
            stem(
                "Outer hazel stool",
                (px, py, z - 0.23),
                (px + lean, py, z + h * 0.73),
                0.23,
                0.085,
                "ElderBark",
            )
            for k in range(2):
                angle = thicket * 2.29 + j * 1.1 + k * 2.67
                ex, ey = px + 0.72 * math.cos(angle), py + 0.72 * math.sin(angle)
                stem(
                    "Hazel fork",
                    (px + lean * 0.4, py, z + h * 0.39),
                    (ex, ey, z + h * 0.72),
                    0.107,
                    0.041,
                    "ElderBark",
                )
                foliage(
                    "Hazel coppice",
                    ex,
                    ey,
                    z + h * 0.75,
                    h * 0.29,
                    h * 0.28,
                    h * 0.54,
                    127 + thicket * 9 + j * 2 + k,
                )
