"""Tavi's painted face, hinged workshop clothes and bellmender's tools."""

import math

import bpy
import numpy as np
from mathutils import Matrix, Vector
from PIL import Image, ImageDraw
from surface_paint import tinted
from atelier import RES, geometry, mats, origins

ATLAS = "TaviAtelier"
# Each four-column swatch occupies a 64 × 32 rectangle below the face.
PIGMENTS = {
    "hair": (70, 37, 33),
    "fringe": (101, 53, 40),
    "hairLight": (126, 69, 47),
    "skin": (197, 132, 96),
    "shirt": (84, 128, 128),
    "shirtLight": (122, 157, 144),
    "apron": (117, 64, 46),
    "apronEdge": (152, 85, 52),
    "pants": (65, 70, 82),
    "boots": (74, 55, 49),
    "welt": (105, 75, 54),
    "brass": (203, 158, 79),
    "kerchief": (173, 78, 59),
    "linen": (220, 196, 149),
    "iron": (78, 89, 91),
    "seam": (114, 87, 59),
}


CLOTH = {"shirt":"blue-canvas", "shirtLight":"linen", "apron":"leather", "apronEdge":"leather",
         "pants":"wool", "boots":"leather", "welt":"leather", "brass":"bronze",
         "kerchief":"linen", "linen":"linen", "iron":"iron"}


def paint_atlas():
    path = RES / "Textures" / (ATLAS + ".png")
    rng = np.random.default_rng(9017)
    y, x = np.indices((128, 256))
    angle = (x / 255 - 0.5) * math.tau
    base = (
        np.array([191, 132, 99])
        + (np.cos(angle) * 15 - 4 * y / 128)[..., None]
        + rng.normal(0, 1.1, (128, 256, 1))
    )
    for cx in (103, 152):
        blush = np.exp(-(((x - cx) / 10) ** 2) - ((y - 76) / 7) ** 2)
        base += blush[..., None] * np.array([10, -6, -4])
    im = Image.new("RGB", (256, 256))
    im.paste(Image.fromarray(np.uint8(np.clip(base, 0, 255))), (0, 0))
    d = ImageDraw.Draw(im)
    for flip in (0, 1):

        def points(coords):
            return [(255 - u if flip else u, v) for u, v in coords]

        def poly(coords, ink):
            d.polygon(points(coords), fill=ink)

        def stroke(coords, ink, width=1):
            d.line(points(coords), fill=ink, width=width)

        stroke([(94, 54), (101, 51), (110, 52), (115, 56)], (144, 87, 69), 2)
        poly(
            [(94, 62), (99, 58), (105, 57), (111, 58), (116, 63), (111, 65), (104, 67), (99, 65)],
            (235, 216, 179),
        )
        poly([(92,63),(98,56),(105,54),(112,56),(118,62),(113,67),(104,69),(97,67)], (241,223,190))
        cx = 149 if flip else 106
        d.ellipse((cx - 5, 56, cx + 4, 68), fill=(56, 102, 91))
        d.ellipse((cx - 2, 57, cx + 2, 66), fill=(54, 41, 35))
        d.rectangle((cx - 2, 57, cx, 59), fill=(252, 233, 201))
        stroke([(93, 60), (96, 62), (100, 58), (105, 57), (111, 58), (116, 62)], (71, 42, 36), 2)
        stroke([(99, 66), (104, 67), (110, 66)], (168, 106, 85))
        poly(
            [(94, 51), (98, 47), (104, 46), (111, 48), (116, 51), (115, 53), (107, 50), (99, 49)],
            (86, 49, 40),
        )
        for a, b in ((99, 72), (103, 74), (109, 73), (95, 75), (112, 71)):
            stroke([(a, b), (a + 1, b)], (156, 96, 74))
    d.line([(147, 47), (146, 51)], fill=(211, 151, 112), width=2)
    d.line([(124, 81), (126, 82), (128, 81), (130, 82), (132, 81)], fill=(142, 85, 65), width=1)
    d.line([(117, 94), (123, 94), (127, 93), (131, 94), (137, 92)], fill=(119, 65, 55), width=2)
    d.line([(122, 97), (129, 98), (134, 96)], fill=(215, 151, 116), width=2)
    for i, (key, color) in enumerate(PIGMENTS.items()):
        cy, cx = divmod(i, 4)
        grain = rng.normal(0, 2.3, (32, 64)) + 2 * np.sin(np.arange(64)[None, :] * 0.91)
        if key in ("apron", "boots", "welt", "hair", "fringe", "hairLight"):
            grain += 4 * np.cos(np.arange(64)[None, :] * 0.29 + np.arange(32)[:, None] * 0.12)
        tile = np.clip(np.array(color) + grain[..., None], 0, 255).astype("uint8")
        swatch = tinted(CLOTH[key], color, 11, (64,32)) if key in CLOTH else Image.fromarray(tile)
        im.paste(swatch, (cx * 64, 128 + cy * 32))
    im.resize((128,128),Image.Resampling.LANCZOS).save(path, optimize=True)
    if ATLAS in mats:
        # init() may already have packed the preceding version of this atlas.
        image=next(n.image for n in mats[ATLAS].node_tree.nodes if n.type=="TEX_IMAGE")
        if image.packed_file: image.unpack(method="REMOVE")
        image.reload()
        image.pack()
    else:
        mat = bpy.data.materials.new(ATLAS)
        mat.use_nodes = True
        node = mat.node_tree.nodes.new("ShaderNodeTexImage")
        node.image = bpy.data.images.load(str(path))
        node.image.pack()
        node.interpolation = "Closest"
        mat.node_tree.links.new(
            node.outputs["Color"], mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"]
        )
        mats[ATLAS] = mat


def make_tavi(x, y, z, height=1.84, heading=0):
    paint_atlas()
    groups = ("Speaker", "SpeakerHead", "SpeakerArm")
    part = groups[0]
    transform = (
        Matrix.Translation((x, y, z))
        @ Matrix.Rotation(math.radians(heading), 4, "Z")
        @ Matrix.Scale(height / 1.84, 4)
    )

    def mesh(name, pts, faces, pigment, uv=None):
        obj = geometry(name, pts, faces, ATLAS, part, uv)
        if uv is None:
            row, col = divmod(list(PIGMENTS).index(pigment), 4)
            layer = obj.data.uv_layers.active.data
            for i, loop in enumerate(obj.data.loops):
                v = obj.data.vertices[loop.vertex_index].co
                # Keep every corner well inside its own swatch, including the mip gutter.
                layer[i].uv = (
                    (col * 64 + 32 + 24 * math.sin(v.x * 9 + v.y * 3)) / 256,
                    1 - (128 + row * 32 + 16 + 11 * math.sin(v.z * 8 + v.y * 3)) / 256,
                )
        obj.data.transform(transform)
        return obj

    def rings(name, rows, pigment, n=12, face=False):
        pts = []
        faces = []
        uvs = []
        for j, (cz, rx, ry, cx, cy) in enumerate(rows):
            for k in range(n):
                a = (k / n - 0.5) * math.tau
                pts.append((cx + rx * math.sin(a), cy - ry * math.cos(a), cz))
            if j:
                for k in range(n):
                    a = (j - 1) * n + k
                    b = (j - 1) * n + (k + 1) % n
                    faces.append((a, b, b + n, a + n))
                    if face:
                        for lon, zz in [
                            (k / n, rows[j - 1][0]),
                            ((k + 1) / n, rows[j - 1][0]),
                            ((k + 1) / n, cz),
                            (k / n, cz),
                        ]:
                            uvs.append(
                                (
                                    0.003 + 0.994 * lon,
                                    1
                                    - (2 + 123 * (rows[-1][0] - zz) / (rows[-1][0] - rows[0][0])) / 256,
                                )
                            )
        faces.extend([tuple(reversed(range(n))), tuple(range(len(pts) - n, len(pts)))])
        if face:
            uvs.extend([(0.5, 0.97)] * (2 * n))
        return mesh(name, pts, faces, pigment, uvs if face else None)

    def oval(name, c, r, ink, n=10):
        cx, cy, cz = c
        rx, ry, rz = r
        return rings(
            name,
            [
                (cz + rz * h, rx * w, ry * w, cx, cy)
                for h, w in [(-1, 0.22), (-0.72, 0.72), (0, 1), (0.72, 0.72), (1, 0.23)]
            ],
            ink,
            n,
        )

    def tube(name, a, b, r, s, pig, n=8):
        a = Vector(a)
        b = Vector(b)
        axis = (b - a).normalized()
        u = axis.cross(Vector((1, 0, 0)) if abs(axis.x) < 0.9 else Vector((0, 0, 1))).normalized()
        v = axis.cross(u)
        pts = [
            tuple(c + rr * (u * math.cos(i * math.tau / n) + v * math.sin(i * math.tau / n)))
            for c, rr in ((a, r), (b, s))
            for i in range(n)
        ]
        fs = [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)] + [
            tuple(reversed(range(n))),
            tuple(range(n, 2 * n)),
        ]
        return mesh(name, pts, fs, pig)

    # Worn ankle boots, wide trousers and a split apron. The two feet carry different weight.
    for sign in (-1, 1):
        cx = sign * 0.126
        cy = 0.035 * sign
        rings(
            "Tavi boot sole",
            [
                (0.012, 0.102, 0.165, cx, cy - 0.043),
                (0.045, 0.108, 0.168, cx, cy - 0.045),
                (0.064, 0.102, 0.16, cx, cy - 0.04),
            ],
            "welt",
        )
        rings(
            "Tavi ankle boot",
            [
                (0.055, 0.10, 0.157, cx, cy - 0.04),
                (0.112, 0.098, 0.146, cx, cy - 0.04),
                (0.16, 0.081, 0.095, cx, cy),
                (0.29, 0.078, 0.079, cx, cy + 0.015),
            ],
            "boots",
        )
        rings(
            "Rolled boot collar",
            [
                (0.238, 0.081, 0.081, cx, cy + 0.016),
                (0.25, 0.092, 0.087, cx, cy + 0.014),
                (0.285, 0.088, 0.084, cx, cy + 0.016),
            ],
            "welt",
        )
        rings(
            "Indigo work trousers",
            [
                (0.25, 0.069, 0.069, cx, cy + 0.016),
                (0.32, 0.091, 0.09, cx, cy + 0.012),
                (0.42, 0.096, 0.099, cx, cy),
                (0.52, 0.08, 0.089, cx, cy - 0.012),
                (0.65, 0.105, 0.115, cx * 0.92, cy),
                (0.89, 0.122, 0.122, cx * 0.84, cy),
            ],
            "pants",
        )
    rings(
        "Teal work blouse",
        [
            (0.76, 0.206, 0.143, 0, 0.012),
            (0.90, 0.186, 0.134, 0, 0.008),
            (0.99, 0.172, 0.129, 0, 0),
            (1.15, 0.223, 0.151, 0, 0),
            (1.27, 0.223, 0.132, 0, 0),
            (1.34, 0.109, 0.083, 0, 0),
        ],
        "shirt",
        16,
    )
    rings("Leather work belt", [(0.927, 0.191, 0.143, 0, 0), (0.973, 0.187, 0.14, 0, 0)], "boots", 16)
    # Wrap panels follow the front of the waist and skirt with a hem gap between the knees.
    for sign in (-1, 1):
        rows = [
            (0.54, 0.235, 0.171),
            (0.65, 0.234, 0.165),
            (0.82, 0.225, 0.165),
            (0.93, 0.189, 0.151),
            (1.0, 0.17, 0.14),
            (1.185, 0.155, 0.157),
        ]
        pts = []
        fs = []
        for j, (zz, w, d) in enumerate(rows):
            for i in range(6):
                t = i / 5
                angle = (0.022 if j == 0 else 0) + t * (1.36 if j < 4 else 1.36 - 0.4 * (j - 3))
                pts.append(
                    (
                        sign * w * math.sin(angle) + sign * (0.018 if j == 0 else 0),
                        -d * math.cos(angle) - 0.014,
                        zz + 0.035 * t if j == 0 else zz,
                    )
                )
            if j:
                for i in range(5):
                    a = (j - 1) * 6 + i
                    f = (a, a + 1, a + 7, a + 6)
                    fs.append(f if sign == 1 else f[::-1])
        mesh("Oxhide apron panel", pts, fs, "apron")
    for sign in (-1, 1):
        tube(
            "Apron suspender",
            (sign * 0.093, -0.158, 1.163),
            (sign * 0.148, -0.097, 1.306),
            0.019,
            0.017,
            "welt",
            6,
        )
        oval("Hammered apron stud", (sign * 0.098, -0.167, 1.174), (0.014, 0.007, 0.014), "brass")
    mesh(
        "Apron pocket",
        [
            (-0.112, -0.173, 0.93),
            (0.115, -0.173, 0.93),
            (0.102, -0.177, 0.82),
            (0.016, -0.182, 0.785),
            (-0.102, -0.177, 0.82),
        ],
        [(4, 3, 2, 1, 0)],
        "apronEdge",
    )
    tube("Pocket piping", (-0.11, -0.18, 0.929), (0.114, -0.18, 0.929), 0.006, 0.006, "linen")
    # Tavi wears her old apprentice badge. Its flared bell outline is cut from brass.
    badge = [
        (-0.048, 1.124),
        (-0.024, 1.127),
        (-0.017, 1.12),
        (-0.014, 1.094),
        (-0.006, 1.087),
        (-0.007, 1.081),
        (-0.059, 1.081),
        (-0.061, 1.087),
        (-0.052, 1.097),
    ]
    mesh(
        "Foundry apprentice badge",
        [(u, -0.17, v) for u, v in badge],
        [tuple(reversed(range(len(badge))))],
        "brass",
    )
    oval("Badge clapper", (-0.034, -0.172, 1.08), (0.006, 0.003, 0.006), "brass", 6)
    tube("Tuning hammer handle", (0.063, -0.179, 0.925), (0.103, -0.157, 1.036), 0.010, 0.009, "welt")
    tube("Tuning hammer peen", (0.077, -0.158, 1.041), (0.128, -0.158, 1.025), 0.015, 0.011, "iron")
    rings("Neck", [(1.27, 0.082, 0.070, 0, 0), (1.49, 0.080, 0.075, 0, -0.006)], "skin", 14)
    rings(
        "Knotted neckerchief",
        [(1.265, 0.107, 0.09, 0, 0), (1.30, 0.113, 0.095, 0, 0), (1.355, 0.088, 0.079, 0, 0)],
        "kerchief",
        14,
    )
    oval("Scarf knot", (-0.071, -0.077, 1.286), (0.045, 0.03, 0.036), "kerchief")
    mesh(
        "Folded scarf end",
        [
            (-0.091, -0.086, 1.284),
            (-0.052, -0.094, 1.282),
            (-0.055, -0.144, 1.184),
            (-0.105, -0.136, 1.214),
        ],
        [(3, 2, 1, 0)],
        "kerchief",
    )
    for sign in (-1, 1):
        part = groups[2] if sign == -1 else groups[0]
        a = (sign * 0.207, 0.002, 1.244)
        b = (sign * 0.307, -0.018, 1.011)
        c = (sign * 0.31, -0.098, 0.824)
        oval("Set-in sleeve", a, (0.090, 0.092, 0.095), "shirt")
        tube("Work sleeve", a, b, 0.086, 0.066, "shirt")
        tube(
            "Rolled linen cuff",
            (sign * 0.292, -0.014, 1.04),
            (sign * 0.311, -0.026, 0.99),
            0.076,
            0.073,
            "shirtLight",
        )
        tube("Tavi forearm", b, c, 0.057, 0.040, "skin")
        oval("Tavi hand", (c[0], c[1] - 0.014, c[2] - 0.056), (0.047, 0.048, 0.081), "skin")
        oval(
            "Tavi thumb",
            (c[0] - sign * 0.031, c[1] - 0.042, c[2] - 0.038),
            (0.023, 0.022, 0.044),
            "skin",
        )
        if sign == -1:
            tube("Copper wrist ring", (c[0], c[1] + 0.008, c[2] + 0.016), c, 0.044, 0.044, "brass")
    part = groups[1]
    rings(
        "Tavi painted face",
        [
            (1.369, 0.054, 0.064, 0, -0.051),
            (1.405, 0.105, 0.094, 0, -0.028),
            (1.48, 0.143, 0.120, 0, -0.017),
            (1.56, 0.163, 0.137, 0, -0.006),
            (1.63, 0.162, 0.14, 0, 0),
            (1.71, 0.16, 0.143, 0, 0.008),
            (1.765, 0.126, 0.125, 0, 0.016),
            (1.797, 0.057, 0.066, 0, 0.021),
        ],
        "skin",
        24,
        True,
    )
    for sign in (-1, 1):
        # A projecting outer rim remains recognizable in profile at speaking distance.
        ear=[(sign*x, y, z) for x,y,z in [(.141,-.018,1.574),(.184,-.012,1.574),
             (.238,.028,1.626),(.188,.025,1.524),(.154,.005,1.499),(.174,-.028,1.553),(.166,.037,1.56)]]
        ear_faces=[(5,j,(j+1)%5) for j in range(5)]+[(6,(j+1)%5,j) for j in range(5)]
        mesh("Tavi tapered ear",ear,ear_faces if sign>0 else [tuple(reversed(f)) for f in ear_faces],"skin")
        oval("Copper drop earring", (sign * 0.174, -0.003, 1.489), (0.014, 0.012, 0.023), "brass")
    # A modeled bridge and low tip catch the sidelight without obscuring the painted eyes.
    mesh(
        "Tavi nose",
        [
            (-0.024, -0.135, 1.58),
            (0.024, -0.135, 1.58),
            (0.030, -0.143, 1.522),
            (0.016, -0.171, 1.514),
            (-0.014, -0.172, 1.514),
            (-0.031, -0.144, 1.522),
            (0, -0.149, 1.584),
        ],
        [(0, 4, 6), (6, 4, 3), (6, 3, 1), (1, 3, 2), (0, 5, 4), (5, 2, 3, 4)],
        "skin",
    )
    # The hairline is lower around the ears and nape. Break up the fringe with separate locks.
    n = 16
    pts = []
    fs = []
    for j in range(5):
        for i in range(n):
            a = (i / n - 0.5) * math.tau
            front = max(0, math.cos(a))
            hem = 1.46 + 0.211 * front**2 + 0.021 * math.sin(a * 4) * front
            zz = (hem, hem + 0.051, 1.747, 1.812, 1.843)[j]
            rx = (0.173, 0.181, 0.175, 0.128, 0.052)[j]
            ry = (0.160, 0.166, 0.162, 0.124, 0.06)[j]
            pts.append((rx * math.sin(a), 0.017 - ry * math.cos(a), zz))
            if j:
                a0 = (j - 1) * n + i
                b0 = (j - 1) * n + (i + 1) % n
                fs.append((a0, b0, b0 + n, a0 + n))
    fs.append(tuple(range(4 * n, 5 * n)))
    mesh("Tavi cropped auburn bob", pts, fs, "hair")
    for j, (a, tip) in enumerate(
        (
            (-1.47, 1.445),
            (-1.10, 1.58),
            (-0.86, 1.598),
            (-0.54, 1.644),
            (-0.22, 1.66),
            (0.12, 1.625),
            (0.47, 1.67),
            (0.83, 1.685),
            (1.22, 1.50),
        )
    ):

        def point(angle, rx, ry, zz):
            return (rx * math.sin(angle), 0.012 - ry * math.cos(angle), zz)

        p = [
            point(a - 0.24, 0.147, 0.14, 1.79),
            point(a + 0.17, 0.154, 0.146, 1.775),
            point(a + 0.09, 0.185, 0.173, 1.70),
            point(a - 0.16, 0.18, 0.17, tip),
            point(a - 0.25, 0.183, 0.171, 1.71),
        ]
        mesh(
            "Swept fringe lock", p, [(0, 4, 2), (0, 2, 1), (4, 3, 2)], "fringe" if j % 3 else "hairLight"
        )
    for j in range(2):
        tube(
            "Copper temple pin",
            (0.143, -0.102, 1.69 + j * 0.021),
            (0.163, -0.056, 1.705 + j * 0.021),
            0.005,
            0.005,
            "brass",
            6,
        )
    for group, pivot in zip(groups, [(0, 0, 0), (0, 0, 1.395), (-0.207, 0, 1.244)]):
        origins[group] = tuple(transform @ Vector(pivot))
