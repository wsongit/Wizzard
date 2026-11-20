"""Landmark, silhouette and baked lighting details shared by both editions."""

from atelier import *
import atelier
from mathutils.bvhtree import BVHTree


def cottage(prefix, x, y, z, height, angle, floor_height):
    with bpy.data.libraries.load(str(ROOT / "Blender/MossbellVillage.blend")) as (source, target):
        target.objects = [
            name
            for name in source.objects
            if name.startswith(prefix + " ") and not name.startswith("Collision")
        ]
    objects = [o for o in target.objects if o and o.type == "MESH"]
    bounds = [o.matrix_world @ Vector(corner) for o in objects for corner in o.bound_box]
    lo = Vector(tuple(min(v[i] for v in bounds) for i in range(3)))
    hi = Vector(tuple(max(v[i] for v in bounds) for i in range(3)))
    pivot = (hi + lo) / 2
    pivot.z = lo.z + 0.18
    scale = height / (hi.z - lo.z)
    place = (
        Matrix.Translation((x, y, z))
        @ Matrix.Rotation(math.radians(angle), 4, "Z")
        @ Matrix.Scale(scale, 4)
        @ Matrix.Translation(-pivot)
    )
    for o in objects:
        if not o.users_collection:
            bpy.context.collection.objects.link(o)
        o.matrix_world = place @ o.matrix_world
        if o.name.endswith("continuous stone footing"):
            o.data=o.data.copy()
            inverse=o.matrix_world.inverted()
            verts=[(v,o.matrix_world @ v.co) for v in o.data.vertices]
            low=min(p.z for _,p in verts)
            for v,p in verts:
                if p.z < low+.001:
                    p.z=min(p.z,floor_height(p.x,p.y)-.22)
                    v.co=inverse @ p
        # Unity and glTF use the first UV set for the texture. Keep a common
        # name before batching meshes authored in different Blender scenes.
        o.data.uv_layers.active.name = "Paint"
        for slot in o.material_slots:
            key = slot.material.name.split(".")[0]
            slot.material = mats[key]
        batches["Set"].append(o)
    return scale


def clothline(k):
    for side in (-1, 1):
        x = side * 8
        y0 = -5
        y1 = 10
        for y in (y0, y1):
            shaft("Fair pole", (x, y, 0), (x, y, 4.5), 0.14, 0.085, "Wood")
        for i in range(10):
            a = i / 10
            b = (i + 1) / 10
            ya = y0 + a * 15
            yb = y0 + b * 15
            za = 4.4 - 0.9 * math.sin(a * math.pi)
            zb = 4.4 - 0.9 * math.sin(b * math.pi)
            shaft("Twisted cord", (x, ya, za), (x, yb, zb), 0.027, 0.027, "Wood", 5)
            geometry(
                "Weathered festival pennant",
                [
                    (x, ya + 0.23, za - 0.06),
                    (x, yb - 0.23, zb - 0.06),
                    (x + 0.18, (ya + yb) / 2, za - 0.85),
                ],
                [(0, 1, 2)],
                ["Pennon", "FernCloth", "SeaCloth"][i % 3],
            )


def branches():
    for side in (-1, 1):
        for j in range(3):
            x = side * (6 + j * 1.1)
            y = 13 + j * 1.7
            shaft(
                "Old growth tracheid",
                (x, y, 1.1),
                (x - side * 1.7, y + 0.6, 6.2 + j),
                1.0,
                0.62,
                "Wood",
                9,
            )
            shaft(
                "Reaching canopy limb",
                (x - side * 1.7, y + 0.6, 6.2 + j),
                (side * (1.2 + j * 0.7), y - 1, 8.3 + j * 0.6),
                0.66,
                0.20,
                "Wood",
                8,
            )
            for v in [-1, 1]:
                shaft(
                    "Buttress root",
                    (x, y, 2.2),
                    (x + v * (2 + j * 0.28), y - 1.7, 0.65),
                    0.68,
                    0.12,
                    "MossRock",
                    7,
                )
        for j in range(6):
            x = side * (10 + rng.uniform(0, 5))
            y = -10 + j * 4
            for n in range(7):
                a = n * math.tau / 7
                h = rng.uniform(0.45, 0.98)
                start = (x, y, 0.05 + max(0, y - 8) * 0.18)
                tip = (x + math.cos(a) * 1.45, y + math.sin(a) * 1.45, start[2] + h)
                mid = Vector(start).lerp(Vector(tip), 0.56)
                mid.z += 0.17
                cross = Vector((-math.sin(a) * 0.19, math.cos(a) * 0.19, 0))
                geometry(
                    "Bracken leaf",
                    [
                        start,
                        tuple(mid - cross),
                        tip,
                        tuple(mid + cross),
                        tuple(mid + Vector((0, 0, 0.095))),
                    ],
                    [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)],
                    "FernCloth",
                )


def district(k):
    if k == 0:
        clothline(k)
    if k == 1:
        from choir_grove import high_canopy
        branches()
        high_canopy()
    if k == 2:
        # Raised stone-lined pools outside the pedestrian causeway.
        for x in [-12.1, 11.6]:
            for y in [-3.1, 4.4]:
                block("Retaining bed", (x, y, 0.05), (3.5, 6.6, 0.15), "Shale")
                block("Pool water", (x, y, 0.14), (3.1, 6.2, 0.10), "Water")
                for sign in (-1, 1):
                    block("Coping long", (x + sign * 1.71, y, 0.24), (0.30, 6.72, 0.52), "Shale")
                    block("Coping short", (x, y + sign * 3.19, 0.24), (3.20, 0.32, 0.52), "Shale")
                for n in range(6):
                    xx = x + rng.uniform(-1.25, 1.25)
                    yy = y + rng.uniform(-2.5, 2.5)
                    shaft(
                        "Bulrush stalk",
                        (xx, yy, 0.16),
                        (xx + 0.14, yy, 0.92),
                        0.026,
                        0.018,
                        "FernCloth",
                        5,
                    )
                    shaft(
                        "Velvet seed head",
                        (xx + 0.14, yy, 0.83),
                        (xx + 0.16, yy, 1.05),
                        0.067,
                        0.04,
                        "Wood",
                        6,
                    )
    if k == 3:
        for s in (-1, 1):
            x = s * 15
            y = -3
            for yy in [-4, 5, 13]:
                shaft("Masonry furnace stack", (x, yy, -0.1), (x, yy, 8.4), 1.04, 0.73, "Basalt", 8)
                for z in (2.3, 4.5, 7.9):
                    lathe("Rolled flue collar", x, yy, z, [(0.87, 0), (0.89, 0.18)], "BellMetal", 8)
            for z in (2.5, 4.2):
                shaft("Copper supply line", (x, -8, z), (x, 13, z), 0.19, 0.19, "BellMetal", 8)
            for yy in (-7, 2):
                block("Furnace hood", (x, yy, 2.5), (2.8, 3.2, 5), "Basalt")
                block("Live hearth", (x - s * 1.415, yy, 1.4), (0.08, 2.15, 1.5), "Amber")
                for j in range(5):
                    block(
                        "Grate rib",
                        (x - s * 1.49, yy - 0.84 + j * 0.42, 1.4),
                        (0.11, 0.12, 1.64),
                        "BellMetal",
                    )
        for x, y in [(-4, -9), (5, 1), (-4, 10)]:
            shaft("Lamp chain", (x, y, 7), (x, y, 4.35), 0.035, 0.035, "BellMetal", 6)
            lathe(
                "Smith lamp glass",
                x,
                y,
                4.0,
                [(0.16, 0), (0.32, 0.11), (0.25, 0.41), (0.12, 0.52)],
                "Amber",
                8,
            )
            lathe("Lamp hood", x, y, 4.40, [(0.4, 0), (0.18, 0.20)], "BellMetal", 8)
    if k == 4:
        for i in range(9):
            a = (10 + i * 20) * math.pi / 180
            x = 15 * math.cos(a)
            y = 2 + 15 * math.sin(a)
            n = Vector((math.cos(a), math.sin(a), 0))
            t = Vector((-n.y, n.x, 0))
            base = Vector((x, y, 2))
            mid = base + Vector((0, 0, 3.4))
            pts = [
                base - t * 0.85,
                base + t * 0.85,
                mid + t * 0.85,
                mid + Vector((0, 0, 1.2)),
                mid - t * 0.85,
            ]
            geometry(
                "Enamel lancet",
                [tuple(p) for p in pts],
                [(0, 1, 2, 3, 4)],
                ["SeaCloth", "NightCloth", "FernCloth"][i % 3],
            )
            for j in range(5):
                shaft("Leaded border", pts[j], pts[(j + 1) % 5], 0.088, 0.088, "Brass", 6)
            shaft("Mullion", base, pts[3], 0.062, 0.062, "Brass", 6)


def bake_ground(key, height=None):
    # Ground-only bake from the actual placed meshes. This preserves contacts
    # on mobile without shadow maps, transparent decals or overlapping floors.
    import numpy as np
    from PIL import Image, ImageFilter

    bpy.context.view_layer.update()
    vertices = []
    faces = []
    for group, objects in batches.items():
        if group in ("MillSails","MillWheel") or group.startswith(("MarshHen","ReedHen")):
            continue
        if group in ("C_Solids", "Terrain", "Rim", "Skyline", "Ina", "Roster", "HushWave") or group.startswith(
            ("Flow", "Ray", "Stray", "Call", "Choice", "LightPath", "Print")
        ):
            continue
        for o in objects:
            m = o.data
            offset = len(vertices)
            vertices.extend(o.matrix_world @ v.co for v in m.vertices)
            m.calc_loop_triangles()
            faces.extend(tuple(offset + v for v in t.vertices) for t in m.loop_triangles)
    bvh = BVHTree.FromPolygons(vertices, faces, all_triangles=True)
    from sets import ground, ROOMS

    if height is None:
        k = ROOMS.index(key)
        height = lambda x,y: ground(k,x,y)
    n = 180
    shade = np.zeros((n, n), np.float32)
    rays = [
        (Vector((-0.54, -0.36, 1)).normalized(), 18, 0.34),
        (Vector((0, 0, 1)), 3, 0.28),
        (Vector((0.50, 0.12, 1)).normalized(), 2.3, 0.15),
    ]
    for j in range(n):
        for i in range(n):
            x = (i + 0.5) * 40 / n - 20
            y = 20 - (j + 0.5) * 40 / n
            start = Vector((x, y, height(x, y) + 0.035))
            for direct, limit, w in rays:
                hit, _, _, dist = bvh.ray_cast(start, direct, limit)
                if hit is not None:
                    shade[j, i] += w * (1 - 0.28 * dist / limit)
    shade = (
        Image.fromarray(np.uint8(np.clip(shade * 255, 0, 255)))
        .resize((512, 512), Image.Resampling.BILINEAR)
        .filter(ImageFilter.GaussianBlur(1.4))
    )
    path = RES / "Textures" / (key + "Ground.png")
    base = ROOT / "Tools/bellwake/.web-assets" / (key + "Unlit.png")
    if key in ROOMS and not base.is_file():
        # The shipped courts retain the original underpainting beneath the cast shadows.
        base = ROOT / "Tools/bellwake/surface_sources/courts" / (key + ".png")
    pixels = np.array(Image.open(base), dtype=float) * (
        1 - np.array(shade)[:, :, None] / 255 * np.array([0.99, 0.91, 0.79])
    )
    Image.fromarray(np.uint8(np.clip(pixels, 0, 255))).save(path)
    paint = mats[key + "Ground"].node_tree.nodes.get("Image Texture").image
    if paint.packed_file:
        paint.unpack(method="REMOVE")
    paint.filepath = str(path)
    paint.reload()
    paint.pack()
