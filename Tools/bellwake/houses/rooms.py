"""Blender source for the fitted rooms; export the same textured triangles to both players."""

import bpy, sys, json, math
from pathlib import Path
from mathutils import Vector

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here))
from paint import TILES, DEST, ROOT

bpy.ops.wm.read_factory_settings(use_empty=True)
mat = bpy.data.materials.new("Painted household goods")
mat.use_nodes = True
tile = mat.node_tree.nodes.new("ShaderNodeTexImage")
tile.image = bpy.data.images.load(str(DEST / "RoomPaint.png"))
tile.image.pack()
mat.node_tree.links.new(
    tile.outputs["Color"],
    mat.node_tree.nodes.get("Principled BSDF").inputs["Base Color"],
)


def shape(name, p, size, paint, sides=0, angle=0, tilt=0):
    if sides:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=sides, radius=0.5, depth=1, location=p
        )
    else:
        bpy.ops.mesh.primitive_cube_add(size=1, location=p)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.rotation_euler[2] = angle
    o.rotation_euler[0] = tilt
    idx = TILES.index(paint)
    uv = o.data.uv_layers.active
    for face in o.data.polygons:
        # Every face receives the full painted cell; map its longest horizontal edge to the writing baseline.
        norm = face.normal
        axis = max(range(3), key=lambda k: abs(norm[k]))
        u, v = ((1, 2), (0, 2), (0, 1))[axis]
        pts = [
            o.data.vertices[o.data.loops[j].vertex_index].co for j in face.loop_indices
        ]
        a, b = min(p[u] for p in pts), max(p[u] for p in pts)
        c, d = min(p[v] for p in pts), max(p[v] for p in pts)
        for j, q in zip(face.loop_indices, pts):
            xx = (q[u] - a) / max(0.00001, b - a)
            yy = (q[v] - c) / max(0.00001, d - c)
            if (axis == 0 and norm.x < 0) or (axis == 1 and norm.y > 0):
                xx = 1 - xx
            uv.data[j].uv = (
                (64 * (idx % 8) + 2.5 + xx * 59) / 512,
                1 - (64 * (idx // 8) + 61.5 - yy * 59) / 256,
            )
    o.data.materials.append(mat)
    room.objects.link(o)
    bpy.context.scene.collection.objects.unlink(o)
    return o


def box(name, x, y, z, w, d, h, paint):
    return shape(name, (x, y, z), (w, d, h), paint)


def pot(x, y, z, s=1, paint="jar"):
    for i, (wide, h, dz) in enumerate(
        [(0.38, 0.10, 0.05), (0.48, 0.30, 0.25), (0.32, 0.14, 0.47), (0.37, 0.07, 0.57)]
    ):
        shape(
            "Turned vessel", (x, y, z + dz * s), (wide * s, wide * s, h * s), paint, 9
        )


def table(x, y, w=1.7, d=0.85, h=0.87):
    box("Scrubbed tabletop", x, y, h, w, d, 0.14, "Wood")
    for a in (-1, 1):
        for b in (-1, 1):
            box(
                "Pinned oak leg",
                x + a * (w / 2 - 0.12),
                y + b * (d / 2 - 0.12),
                h / 2,
                0.14,
                0.14,
                h,
                "TarredOak",
            )


def bed(x, y, cloth):
    box("Bedstead", x, y, 0.32, 1.48, 2.25, 0.47, "Wood")
    box("Folded quilt", x, y - 0.23, 0.61, 1.43, 1.61, 0.16, cloth)
    box("Ticking pillow", x, y + 0.73, 0.64, 1.18, 0.46, 0.21, "MillCanvas")
    box("Carved headboard", x, y + 1.07, 0.64, 1.61, 0.14, 1.07, "TarredOak")


def shelf(x, y):
    for xx in (x - 1.1, x + 1.1):
        box("Cupboard side", xx, y, 1.14, 0.13, 0.67, 2.25, "TarredOak")
    for z in (0.36, 1.08, 1.84):
        box("Shelf", x, y, z, 2.34, 0.69, 0.12, "Wood")


def books(x, y, z):
    for i in range(7):
        box(
            "Clothbound volume",
            x + i * 0.14,
            y,
            z + 0.16 + (i % 3) * 0.015,
            0.12,
            0.28,
            0.34 + (i % 3) * 0.03,
            ["book", "FernCloth", "SeaCloth"][i % 3],
        )


def interior(style):
    for i in range(4):
        for j in range(4):
            box(
                "Floor bay",
                -3 + i * 2,
                -2.55 + j * 1.7,
                -0.12,
                2,
                1.7,
                0.24,
                "Wood" if style.startswith("home") or style == "inn" else "SpringStone",
            )
    for y in (-3.47, 3.47):
        for i in range(4):
            box(
                "Plaster bay",
                -3 + i * 2,
                y,
                1.67,
                2,
                0.18,
                3.34,
                "OchrePlaster" if style in ("baker", "inn") else "HousePlaster",
            )
            box(
                "Oak stud",
                -3.9 + i * 2,
                y - (0.11 if y > 0 else -0.11),
                1.67,
                0.12,
                0.14,
                3.34,
                "TarredOak",
            )
        box("Base course", 0, y * 0.975, 0.22, 8.1, 0.22, 0.44, "Masonry")
    for x in (-4.07, 4.07):
        for j in range(4):
            box("Side bay", x, -2.55 + j * 1.7, 1.67, 0.18, 1.7, 3.34, "HousePlaster")
        box("Wall rail", x * 0.978, 0, 1.13, 0.17, 6.8, 0.13, "TarredOak")
        for y in (-1.4, 1.45):
            box(
                "Leaded light",
                x * 0.971,
                y,
                2.05,
                0.08,
                1.27,
                1.24,
                "glass" if style == "glass" else "window",
            )
            box("Window sill", x * 0.956, y, 1.42, 0.30, 1.44, 0.13, "Wood")
    box("Ceiling", 0, 0, 3.46, 8.2, 6.99, 0.2, "Wood")
    for y in (-2.8, -0.15, 2.45):
        box("Summer beam", 0, y, 3.22, 8.17, 0.23, 0.29, "TarredOak")
    box("Street door", 0, -3.30, 1.18, 1.34, 0.12, 2.36, "door")
    box("Door head", 0, -3.24, 2.38, 1.58, 0.23, 0.19, "TarredOak")
    box("Woven runner", 0, -0.4, 0.012, 1.65, 3.43, 0.024, "carpet")
    table(0, 2.6, 1.63, 0.78, 0.93)
    box("Open household record", 0, 2.52, 1.043, 0.56, 0.38, 0.066, "page")
    shape("Brass ink well", (0.52, 2.55, 1.06), (0.14, 0.14, 0.16), "Brass", 8)
    if style.startswith("home") or style == "inn":
        side = -1 if style != "home2" else 1
        bed(
            side * 2.75,
            1.18,
            {
                "home": "quilt",
                "home2": "SeaCloth",
                "home3": "carpet",
                "inn": "FernCloth",
            }[style],
        )
        if style == "inn":
            bed(-side * 2.75, 1.18, "SeaCloth")
        else:
            table(-side * 2.64, 0.28)
            pot(-side * 2.64, 0.28, 0.94)
            box("Stool", -side * 2.68, -0.72, 0.28, 0.56, 0.56, 0.52, "Wood")
    elif style == "baker":
        box("Brick oven", -2.72, 1.75, 0.85, 2.14, 1.61, 1.7, "Masonry")
        box("Fire mouth", -2.72, 0.92, 0.84, 1.00, 0.08, 0.7, "fire")
        box("Hood", -2.72, 1.76, 1.94, 1.65, 1.38, 0.54, "Masonry")
        box("Flue", -2.72, 1.87, 2.72, 0.75, 0.76, 1.1, "Masonry")
        table(2.53, 0.28)
        for i in range(3):
            shape(
                "Scored loaf",
                (2.04 + i * 0.48, 0.28, 1.07),
                (0.42, 0.56, 0.27),
                "RyeCrust",
                8,
            )
    elif style == "forge":
        box("Forge hearth", -2.85, 1.65, 0.59, 1.93, 1.48, 1.18, "Masonry")
        box("Coals", -2.85, 1.68, 1.19, 1.61, 1.2, 0.09, "fire")
        box("Brick flue", -2.85, 2.45, 2.22, 0.93, 0.61, 2.22, "Masonry")
        shape("Anvil stump", (2.45, 0.4, 0.37), (0.81, 0.81, 0.74), "Wood", 9)
        box("Anvil waist", 2.45, 0.4, 0.84, 0.48, 0.33, 0.22, "SpringStone")
        box("Anvil face", 2.45, 0.4, 1.02, 1.13, 0.41, 0.18, "SpringStone")
        table(2.62, 2.18)
        shape("Bell mould", (2.62, 2.18, 1.16), (0.72, 0.72, 0.44), "Brass", 10)
    elif style == "mill":
        for x in (-2.8, 2.7):
            shape("Millstone", (x, 1.6, 0.56), (1.73, 1.73, 0.91), "SpringStone", 12)
            shape("Drive spindle", (x, 1.6, 1.95), (0.26, 0.26, 2.84), "Wood", 8)
        for i in range(4):
            pot(-3.26 + i * 0.58, -1.55, 0, 0.95, "grain")
    elif style == "watch":
        shelf(-2.59, 2.85)
        for j in range(2):
            for i in range(3):
                x = -3.11 + i * 0.51
                z = 0.58 + j * 0.77
                shape("Lamp base", (x, 2.77, z), (0.3, 0.28, 0.19), "BellMetal", 8)
                shape("Reservoir", (x, 2.77, z + 0.18), (0.24, 0.24, 0.24), "Amber", 8)
        table(2.63, 0.31)
        shape("Reflector stand", (2.63, 0.31, 1.27), (0.21, 0.21, 0.68), "Brass", 8)
        shape(
            "Signal mirror",
            (2.63, 0.31, 1.65),
            (0.87, 0.87, 0.13),
            "Brass",
            12,
            tilt=1.2,
        )
    elif style == "pilot":
        table(-2.59, 0.35)
        shape("Compass bowl", (-2.59, 0.35, 1.02), (0.63, 0.63, 0.16), "Brass", 12)
        for i in range(3):
            shape(
                "Line drum",
                (2.53, 1.9 - i * 0.84, 0.45),
                (0.72, 0.72, 0.88),
                "grain",
                10,
            )
        shape("Lantern foot", (2.46, -1.55, 0.68), (0.55, 0.55, 1.34), "TarredOak", 8)
        shape("Lantern", (2.46, -1.55, 1.68), (0.49, 0.49, 0.66), "Amber", 8)
    elif style == "theatre":
        box("Small stage", -2.63, 1.49, 0.4, 2.35, 2.25, 0.8, "Wood")
        for x in (-3.63, -1.65):
            box("Curtain hanging", x, 1.05, 1.93, 0.44, 0.19, 2.21, "book")
        box("Pelmet", -2.63, 1.05, 2.97, 2.42, 0.32, 0.36, "book")
        box("Painted river backdrop", -2.63, 2.48, 1.73, 2.27, 0.12, 1.9, "SeaCloth")
        for x in (-3.02, -2.3):
            shape("Puppet head", (x, 1.6, 1.69), (0.24, 0.22, 0.24), "RyeCrust", 8)
            box("Puppet coat", x, 1.6, 1.39, 0.32, 0.18, 0.41, "FernCloth")
        for y in (-1.4, 0.25, 1.9):
            table(2.35, y, 1.61, 0.44, 0.45)
    elif style in ("school", "chapel"):
        for x in (-2.54, 2.54):
            for y in (-0.66, 1.22):
                table(x, y, 1.62, 0.46, 0.46)
                if style == "school":
                    table(x, y + 0.55, 1.62, 0.57, 0.85)
                    box("Writing slate", x, y + 0.55, 0.943, 0.62, 0.35, 0.038, "chalk")
        if style == "school":
            box("Lesson board", -2.72, 3.33, 2, 2.3, 0.14, 1.34, "chalk")
        else:
            shelf(-2.52, 2.95)
            for i in range(5):
                shape(
                    "Beeswax votive",
                    (-3.22 + i * 0.31, 2.91, 0.62),
                    (0.17, 0.17, 0.38),
                    "Amber",
                    8,
                )
    elif style == "pump":
        for x in (-2.65, 2.65):
            box("Pump bed", x, 1.18, 0.31, 1.25, 1.49, 0.62, "Masonry")
            shape("Pump barrel", (x, 1.18, 1.27), (0.83, 0.83, 1.31), "BellMetal", 10)
            shape("Piston rod", (x, 1.18, 2.12), (0.21, 0.21, 0.74), "Brass", 8)
            box("Pump lever", x, 1.18, 2.53, 0.2, 2.18, 0.19, "TarredOak")
    elif style == "potter":
        shelf(-2.72, 2.88)
        for j in range(2):
            for i in range(3):
                pot(-3.36 + i * 0.57, 2.81, 0.39 + 0.77 * j, 0.72)
        shape("Wheel spindle", (2.40, 0.53, 0.39), (0.29, 0.29, 0.78), "Wood", 8)
        shape("Throwing wheel", (2.40, 0.53, 0.82), (1.18, 1.18, 0.16), "Wood", 12)
        pot(2.40, 0.53, 0.90, 0.78)
    elif style == "weaver":
        for x in (-3.38, -1.84):
            box("Loom upright", x, 1.1, 1.28, 0.19, 0.32, 2.56, "TarredOak")
        for z in (0.43, 2.36):
            box("Loom crossbar", -2.61, 1.1, z, 1.75, 0.36, 0.19, "Wood")
        box("Woven panel", -2.61, 1.1, 1.19, 1.35, 0.09, 1.31, "quilt")
        for i in range(12):
            box(
                "Warp thread",
                -3.22 + i * 0.111,
                1.1,
                2.07,
                0.023,
                0.025,
                0.54,
                "MillCanvas",
            )
        table(2.55, 0.18)
        for i in range(3):
            box(
                "Folded bolt",
                2.55,
                0.18,
                1.00 + 0.11 * i,
                1.21,
                0.65,
                0.12,
                ["SeaCloth", "FernCloth", "carpet"][i],
            )
    elif style == "glass":
        for x in (-2.75, 2.75):
            table(x, 0.55, 1.40, 2.7)
            for j in range(3):
                pot(x, -0.23 + j * 0.72, 0.94, 0.78)
                shape(
                    "Winter leaves",
                    (x, -0.23 + j * 0.72, 1.60),
                    (0.54, 0.46, 0.56),
                    "Leaves",
                    7,
                )
    else:
        shelf(-2.55, 2.85)
        books(-3.38, 2.78, 0.43)
        books(-3.38, 2.78, 1.15)
        books(-3.38, 2.78, 1.91)
        table(2.63, 0.31)
        box("Clerk slate", 2.63, 0.31, 0.957, 0.95, 0.54, 0.04, "chalk")
    if style not in ("inn", "mill"):
        pot(-3.35, -2.42, 0, 1.22)
        pot(-2.73, -2.48, 0, 0.74, "bottle")


def export():
    pos = []
    uvs = []
    colors = []
    indices = []
    verts = {}
    for o in room.objects:
        o.data.calc_loop_triangles()
        for tri in o.data.loop_triangles:
            normal = o.matrix_world.to_3x3().inverted().transposed() @ tri.normal
            normal.normalize()
            light = 0.81 + 0.12 * normal.z + 0.07 * normal.x
            for j in tri.loops:
                p = o.matrix_world @ o.data.vertices[o.data.loops[j].vertex_index].co
                u, v = o.data.uv_layers.active.data[j].uv
                vertex = tuple(round(a, 5) for a in (p.x, p.z, -p.y, u, v, light))
                if vertex not in verts:
                    verts[vertex] = len(verts)
                    pos.extend(vertex[:3])
                    uvs.extend(vertex[3:5])
                    colors.append(vertex[5])
                indices.append(verts[vertex])
    (DEST / (room.name + ".json")).write_text(
        json.dumps(
            dict(pos=pos, uv=uvs, light=colors, indices=indices), separators=(",", ":")
        )
        + "\n"
    )


for i, style in enumerate(
    (
        "home",
        "home2",
        "home3",
        "inn",
        "baker",
        "mill",
        "pilot",
        "watch",
        "glass",
        "office",
        "forge",
        "theatre",
        "school",
        "chapel",
        "pump",
        "potter",
        "weaver",
    )
):
    room = bpy.data.collections.new(style)
    bpy.context.scene.collection.children.link(room)
    interior(style)
    bpy.context.view_layer.update()
    export()
    # Separate rooms on the editable floor plan after exporting room-local coordinates.
    for o in room.objects:
        o.location.x += 11 * (i % 5)
        o.location.y += 9 * (i // 5)
p = ROOT / "Blender/HouseInteriors.blend"
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(p), compress=True)
