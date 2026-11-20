"""Blender wardrobe and carved silhouettes for the people of Bellwake."""

import math
from mathutils import Matrix, Vector
from atelier import geometry, load_paint

from resident_designs import COSTUMES, CREW, FACES, face_patch
from resident_paint import PIGMENTS


class Carver:
    def __init__(self, name, dress, transform, body, head, arm):
        self.name = name
        self.dress = dress
        self.transform = transform
        self.body, self.head, self.arm = body, head, arm
        self.group = body

    def mesh(self, name, verts, faces, ink, face_uv=None, tailored=False):
        kit = self.dress.kit
        swatch = PIGMENTS.index(ink)
        uv = []
        if tailored:
            xmin, xmax = min(p[0] for p in verts), max(p[0] for p in verts)
            zmin, zmax = min(p[2] for p in verts), max(p[2] for p in verts)
        for i, face in enumerate(faces):
            coords = [verts[j] for j in face]
            norm = (Vector(coords[1]) - Vector(coords[0])).cross(
                Vector(coords[2]) - Vector(coords[0])
            )
            axis = max(range(3), key=lambda k: abs(norm[k]))
            a, b = ((1, 2), (0, 2), (0, 1))[axis]
            for j, p in zip(face, coords):
                if face_uv and i in face_uv:
                    u, v = face_uv[i][j]
                    uv.append(
                        (
                            (face_patch(self.name)[0] + 2 + 60 * u) / 512,
                            1 - (face_patch(self.name)[1] + 2 + 60 * v) / 512,
                        )
                    )
                elif (
                    tailored and norm.y < -0.00001 and abs(norm.y) > abs(norm.x) * 0.36
                ):
                    u = (p[0] - xmin) / (xmax - xmin)
                    v = (zmax - p[2]) / (zmax - zmin)
                    uv.append(
                        (
                            (64 * (kit % 4) + 3 + 58 * u) / 512,
                            1 - (256 + 96 * (kit // 4) + 3 + 90 * v) / 512,
                        )
                    )
                else:
                    u = 0.5 + 0.42 * math.sin(p[a] * 19 + p[b] * 0.73)
                    v = 0.5 + 0.30 * math.sin(p[b] * 17 - p[a] * 1.4)
                    uv.append(
                        (
                            (kit * 32 + 2 + 28 * u) / 512,
                            1 - (128 + 8 * swatch + 1 + 6 * v) / 512,
                        )
                    )
        return geometry(
            self.name + " · " + name,
            [self.transform @ Vector(v) for v in verts],
            faces,
            "ResidentCloth",
            self.group,
            uv,
        )

    def shell(self, name, rings, ink, portrait=False):
        points = sum(rings, [])
        n = len(rings[0])
        faces = [tuple(reversed(range(n)))]
        painted = {}
        for r in range(len(rings) - 1):
            for i in range(n):
                a = r * n + i
                b = r * n + (i + 1) % n
                face = (a, b, b + n, a + n)
                if portrait and i in (0, 1, 2, 3):
                    painted[len(faces)] = {
                        v: (
                            max(0, min(1, 0.5 + points[v][0] / 0.37)),
                            max(0, min(1, (1.805 - points[v][2]) / 0.355)),
                        )
                        for v in face
                    }
                faces.append(face)
        faces.append(tuple(range(len(points) - n, len(points))))
        return self.mesh(
            name,
            points,
            faces,
            ink,
            painted,
            name in ("cut coat", "overlapping shoulder cape") and ink != "linen",
        )

    def profile(self, name, rows, ink, portrait=False):
        # Five front stations reserve real planes for the cheek returns and bridge.
        section = (
            (-1, -0.34),
            (-0.71, -0.86),
            (0, -1),
            (0.71, -0.86),
            (1, -0.34),
            (0.90, 0.61),
            (0.44, 1),
            (-0.48, 1),
            (-0.93, 0.58),
        )
        rings = [
            [(x + rx * a, y + ry * b, z) for a, b in section]
            for z, rx, ry, x, y in rows
        ]
        return self.shell(name, rings, ink, portrait)

    def fold(self, name, outline, ink, ridge=0.012):
        # Closed folded panel. Its ridge throws one clean light plane across the fold.
        n = len(outline)
        x, y, z = (sum(v[i] for v in outline) / n for i in range(3))
        p = outline + [(x, y - ridge, z), (x, y + 0.009, z)]
        faces = [(n, i, (i + 1) % n) for i in range(n)] + [
            (n + 1, (i + 1) % n, i) for i in range(n)
        ]
        # Meshes can face either side of a sleeve. Orient the closed surface consistently.
        volume = sum(
            Vector(p[a]).dot(Vector(p[b]).cross(Vector(p[c]))) for a, b, c in faces
        )
        if volume < 0:
            faces = [tuple(reversed(f)) for f in faces]
        return self.mesh(name, p, faces, ink, tailored=name == "work apron")

    def rod(self, name, stages, ink, sides=5):
        axis = (Vector(stages[-1][0]) - Vector(stages[0][0])).normalized()
        right = Vector((1, 0, 0)) if abs(axis.x) < 0.82 else Vector((0, 1, 0))
        u = axis.cross(right).normalized()
        v = axis.cross(u)
        rings = []
        for center, w, d in stages:
            rings.append(
                [
                    tuple(
                        Vector(center)
                        + u * w * math.cos(k * math.tau / sides)
                        + v * d * math.sin(k * math.tau / sides)
                    )
                    for k in range(sides)
                ]
            )
        return self.shell(name, rings, ink)


def make(name, foot, height, heading, groups):
    dress = COSTUMES[name]
    transform = (
        Matrix.Translation(foot)
        @ Matrix.Rotation(heading, 4, "Z")
        @ Matrix.Scale(height / 1.88, 4)
    )
    c = Carver(name, dress, transform, *groups)
    build, lean = dress.build, dress.lean
    hip = 0.18 * build
    shoulder = 0.237 * build
    garment = dress.garment
    long = garment in ("skirt", "longcoat", "oilskin")
    left = (shoulder, 0.014, 1.321)
    neck = (lean, 0, 1.434)
    for side in (-1, 1):
        x = side * 0.116 * build
        y = side * (0.045 if dress.tool in ("hook", "rule", "hammer") else 0.026)
        c.profile(
            "turned shoe",
            [
                (0.006, 0.086, 0.148, x, y - 0.042),
                (0.047, 0.097, 0.173, x, y - 0.060),
                (0.077, 0.099, 0.163, x, y - 0.047),
                (0.135, 0.077, 0.093, x, y + 0.003),
                (0.255, 0.069, 0.065, x, y + 0.01),
            ],
            "shoe",
        )
        c.profile(
            "pressed leg",
            [
                (0.151, 0.065, 0.066, x, y),
                (0.275, 0.074, 0.075, x, y + 0.004),
                (0.458, 0.089, 0.086, x - 0.012 * side, y - 0.027),
                (0.505, 0.085, 0.08, x - 0.011 * side, y - 0.018),
                (0.69, 0.121, 0.107, x - 0.004 * side, y + 0.02),
                (0.884, 0.105, 0.11, x - 0.018 * side, 0.024),
            ],
            "trousers",
        )
        if garment in ("vest", "mantle", "oilskin"):
            c.profile(
                "boot top",
                [
                    (0.135, 0.075, 0.084, x, y),
                    (0.319, 0.093, 0.098, x, y + 0.002),
                    (0.343, 0.096, 0.1, x, y + 0.002),
                ],
                "shoe",
            )
    hem = 0.49 if long else (0.641 if garment == "smock" else 0.74)
    skirt = 1.35 if long else 1.16
    c.profile(
        "cut coat",
        [
            (hem, hip * skirt, 0.158, lean * 0.3, 0.014),
            (hem + 0.046, hip * skirt * 1.014, 0.162, lean * 0.3, 0.014),
            (0.90, hip * 1.06, 0.141, 0, 0.018),
            (1.03, hip * 0.95, 0.14, lean * 0.45, 0.017),
            (1.225, shoulder * 0.96, 0.166, lean * 0.8, 0.009),
            (1.326, shoulder, 0.146, lean, 0.017),
            (1.384, 0.116, 0.09, lean, -0.002),
        ],
        "linen" if garment == "apron" else "coat",
    )
    c.profile(
        "waist binding",
        [(0.928, hip * 1.08, 0.153, 0, 0.015), (0.974, hip * 1.06, 0.15, 0, 0.015)],
        "satchel",
    )
    if garment in ("apron", "skirt"):
        width = hip * (1.06 if garment == "apron" else 1.32)
        c.fold(
            "work apron",
            [
                (lean - 0.11, -0.174, 1.295),
                (lean + 0.11, -0.174, 1.295),
                (width * 0.76, -0.177, 0.967),
                (width, -0.181, 0.573),
                (width * 0.25, -0.198, 0.544),
                (-width, -0.178, 0.603),
                (-width * 0.80, -0.178, 0.972),
            ],
            "coat",
            0.026,
        )
        c.fold(
            "apron pocket",
            [
                (-0.108, -0.215, 0.898),
                (0.079, -0.217, 0.889),
                (0.07, -0.22, 0.788),
                (-0.09, -0.216, 0.804),
            ],
            "cuff",
            0.014,
        )
    elif garment in ("mantle", "oilskin"):
        c.profile(
            "overlapping shoulder cape",
            [
                (1.132, shoulder * 1.20, 0.181, lean, 0.019),
                (1.238, shoulder * 1.23, 0.188, lean, 0.014),
                (1.347, shoulder * 0.93, 0.142, lean, 0.016),
                (1.40, 0.11, 0.092, lean, 0.012),
            ],
            "cuff",
        )
    elif garment == "vest":
        for side in (-1, 1):
            c.fold(
                "waistcoat point",
                [
                    (lean + side * 0.02, -0.16, 1.183),
                    (lean + side * 0.12, -0.115, 1.34),
                    (lean + side * 0.192, -0.124, 1.251),
                    (side * 0.152, -0.144, 1.012),
                    (side * 0.055, -0.157, 0.943),
                ],
                "cuff",
            )
    elif garment in ("doublet", "longcoat"):
        c.fold(
            "bias lapel",
            [
                (lean - 0.102, -0.11, 1.345),
                (lean + 0.114, -0.132, 1.332),
                (0.035, -0.175, 1.125),
                (-0.035, -0.167, 1.097),
            ],
            "edge",
            0.018,
        )
        for i in range(3):
            z = 1.116 - 0.068 * i
            c.fold(
                "pewter fastening",
                [
                    (0.045, -0.161, z + 0.016),
                    (0.058, -0.162, z),
                    (0.042, -0.162, z - 0.014),
                    (0.029, -0.163, z),
                ],
                "gold",
                0.005,
            )
    c.profile(
        "neck",
        [(1.31, 0.067, 0.069, lean, 0), (1.50, 0.072, 0.067, lean, -0.012)],
        "skin",
    )
    c.profile(
        "turned collar",
        [
            (1.324, 0.117, 0.106, lean, 0),
            (1.365, 0.132, 0.108, lean, -0.006),
            (1.41, 0.092, 0.081, lean, -0.002),
        ],
        "scarf",
    )
    c.fold(
        "kerchief point",
        [
            (lean - 0.091, -0.095, 1.382),
            (lean + 0.065, -0.107, 1.367),
            (lean + 0.119, -0.145, 1.217),
            (lean + 0.016, -0.164, 1.264),
        ],
        "scarf",
        0.014,
    )
    for side in (-1, 1):
        c.group = c.arm if side == 1 else c.body
        sx = side * shoulder + lean
        elbow = (sx + side * 0.064, 0.011 if side == -1 else -0.015, 1.053)
        hand = (
            (sx + side * 0.032, -0.193, 1.116)
            if side == 1
            else (sx - side * 0.004, -0.081, 0.853)
        )
        c.rod(
            "set-in sleeve",
            [
                ((sx, 0.014, 1.317), 0.077, 0.087),
                ((sx + side * 0.039, 0.023, 1.257), 0.098, 0.102),
                (elbow, 0.074, 0.067),
            ],
            "coat" if garment != "vest" else "linen",
            6,
        )
        c.rod(
            "elbow and turned cuff",
            [
                (elbow, 0.075, 0.069),
                (
                    (hand[0], hand[1] + 0.034, hand[2] + (0.04 if side < 0 else -0.01)),
                    0.062,
                    0.066,
                ),
                (hand, 0.053, 0.052),
            ],
            "cuff",
            6,
        )
        hx, hy, hz = hand
        c.profile(
            "work-worn knuckles",
            [
                (hz - 0.096, 0.034, 0.038, hx - side * 0.008, hy - 0.016),
                (hz - 0.073, 0.055, 0.049, hx, hy - 0.013),
                (hz - 0.018, 0.06, 0.044, hx, hy - 0.01),
                (hz + 0.018, 0.043, 0.044, hx, hy),
            ],
            "skin",
        )
        c.rod(
            "folded thumb",
            [
                ((hx - side * 0.036, hy - 0.016, hz - 0.018), 0.028, 0.027),
                ((hx - side * 0.064, hy - 0.045, hz - 0.039), 0.024, 0.021),
                ((hx - side * 0.056, hy - 0.052, hz - 0.056), 0.011, 0.015),
            ],
            "skin",
            5,
        )
        if side == 1:
            accessory(c, dress.tool, hx, hy - 0.036, hz - 0.058)
    c.group = c.head
    head_transform = c.transform
    c.transform = head_transform @ Matrix.Translation((lean, -0.01, 0))
    face = FACES[name]
    jaw = face.jaw + (build - 1) * 0.048
    cheeks = face.cheek
    c.profile(
        "brow cheek and chin",
        [
            (1.444, 0.050, 0.064, 0, -0.025),
            (1.479, jaw, 0.105, 0, -0.025),
            (1.565, cheeks, 0.133, 0, -0.012),
            (1.657, 0.172, 0.144, 0, -0.004),
            (1.739, 0.163, 0.142, -0.003, 0.002),
            (1.806, 0.124, 0.115, -0.007, 0.017),
        ],
        "skin",
        True,
    )
    c.fold(
        "bridge and turned nose",
        [
            (-0.020, -0.130, 1.664),
            (0.017, -0.131, 1.662),
            (0.032, -0.137, 1.575),
            (0.014, -face.nose, 1.56),
            (-0.025, -0.151, 1.566),
        ],
        "skin",
        face.nose - 0.15,
    )
    for side in (-1, 1):
        c.fold(
            "pointed ear rim",
            [
                (side * 0.141, -0.02, 1.642),
                (side * 0.18, -0.018, 1.643),
                (side * 0.216, 0.030, 1.679),
                (side * 0.180, 0.021, 1.578),
                (side * 0.145, -0.001, 1.565),
            ],
            "skin",
            0.021,
        )
    headwear(c, dress.head)
    facial_hair(c, face.mark)
    c.transform = head_transform
    return tuple(transform @ Vector(neck)), tuple(
        transform @ Vector((left[0] + lean, left[1], left[2]))
    )


def headwear(c, style):
    # The hairline arches over the brow and falls to four unequal points at the nape.
    n = 10

    def crown_ring(rx, ry, base, rise, offset=0):
        ring = []
        for i in range(n):
            a = i * math.tau / n
            front = max(0, math.cos(a))
            ring.append(
                (
                    offset + rx * math.sin(a),
                    0.020 - ry * math.cos(a),
                    base + rise * front,
                )
            )
        return ring

    c.shell(
        "temple and nape",
        [
            crown_ring(0.177, 0.192, 1.516, 0.191),
            crown_ring(0.189, 0.196, 1.636, 0.113),
            crown_ring(0.170, 0.166, 1.795, 0.016, -0.014),
            crown_ring(0.089, 0.096, 1.838, 0, -0.029),
        ],
        "hair",
    )
    if style in ("braid", "crop", "knot", "cap", "peak"):
        for a, tip, width in (
            (-0.91, 1.635, 0.077),
            (-0.39, 1.67, 0.087),
            (0.18, 1.706, 0.073),
            (0.79, 1.682, 0.071),
        ):
            x = 0.179 * math.sin(a)
            y = 0.014 - 0.192 * math.cos(a)
            c.fold(
                "swept fringe",
                [
                    (x - width * 0.66, y + 0.009, 1.775),
                    (x + width * 0.64, y + 0.012, 1.751),
                    (x + width * 0.56, y - 0.018, 1.717),
                    (x - width * 0.43, y - 0.038, tip),
                ],
                "hairlight" if a == -0.91 else "hair",
                0.016,
            )
    if style == "crop":
        for side in (-1, 1):
            c.fold(
                "wind-cut side lock",
                [
                    (side * 0.106, 0.004, 1.778),
                    (side * 0.164, -0.016, 1.743),
                    (side * 0.208, -0.048, 1.597),
                    (side * 0.147, -0.04, 1.627),
                ],
                "hairlight",
                0.025,
            )
    if style in ("peak", "cap", "brim"):
        brim = 0.216 if style == "brim" else 0.175
        visor = 0.204 if style == "peak" else brim * 0.84
        c.profile(
            "tilted felt brim",
            [
                (1.720, brim, visor, 0.004, -0.034),
                (1.741, brim * 1.01, visor * 1.02, 0.004, -0.034),
                (1.753, 0.154, 0.135, -0.008, 0.01),
            ],
            "felt",
        )
        c.profile(
            "broken crown",
            [
                (1.738, 0.171, 0.145, -0.004, 0.014),
                (1.802, 0.166, 0.133, -0.019, 0.022),
                (1.865, 0.09, 0.082, -0.061, 0.037),
                (1.851, 0.022, 0.035, -0.105, 0.047),
            ],
            "coat",
        )
        c.profile(
            "hat ribbon",
            [(1.745, 0.175, 0.15, -0.005, 0.013), (1.766, 0.174, 0.146, -0.008, 0.017)],
            "edge",
        )
        if style == "peak":
            c.fold(
                "skew-cut feather",
                [
                    (-0.125, -0.043, 1.753),
                    (-0.161, -0.055, 1.835),
                    (-0.238, -0.032, 1.914),
                    (-0.221, -0.03, 1.838),
                    (-0.182, -0.043, 1.794),
                ],
                "scarf",
                0.009,
            )
    if style in ("hood", "scarf"):
        c.shell(
            "folded headcloth",
            [
                crown_ring(0.197, 0.209, 1.474, 0.234),
                crown_ring(0.203, 0.219, 1.640, 0.121),
                crown_ring(0.181, 0.181, 1.799, 0.030, -0.016),
                crown_ring(0.104, 0.113, 1.868, 0, -0.058),
            ],
            "coat" if style == "hood" else "scarf",
        )
        c.fold(
            "trailing scarf tip",
            [
                (0.094, 0.093, 1.739),
                (0.164, 0.082, 1.718),
                (0.241, 0.123, 1.502),
                (0.168, 0.105, 1.55),
            ],
            "edge",
            0.019,
        )
        if style == "hood":
            for side in (-1, 1):
                c.fold(
                    "cloak cheek return",
                    [
                        (side * 0.144, -0.072, 1.73),
                        (side * 0.191, -0.043, 1.67),
                        (side * 0.206, 0.025, 1.403),
                        (side * 0.141, -0.031, 1.505),
                    ],
                    "cuff",
                    0.021,
                )
    if style in ("braid", "knot"):
        c.profile(
            "bound chignon",
            [
                (1.696, 0.066, 0.063, -0.02, 0.107),
                (1.761, 0.101, 0.081, -0.045, 0.14),
                (1.842, 0.074, 0.070, -0.075, 0.126),
                (1.882, 0.026, 0.034, -0.092, 0.10),
            ],
            "hairlight",
        )
        if style == "braid":
            for j in range(3):
                x = -0.135 - 0.014 * j
                y = 0.055 - 0.028 * j
                z = 1.637 - 0.066 * j
                c.fold(
                    "overlaid braid hank",
                    [
                        (x + 0.035, y, z + 0.066),
                        (x - 0.044, y - 0.014, z + 0.034),
                        (x - 0.042, y - 0.012, z - 0.012),
                        (x + 0.001, y - 0.031, z - 0.069),
                        (x + 0.038, y, z - 0.001),
                    ],
                    "hair" if j % 2 else "hairlight",
                    0.026,
                )
        else:
            c.fold(
                "linen knot tie",
                [
                    (-0.111, 0.089, 1.833),
                    (-0.04, 0.069, 1.817),
                    (0.033, 0.107, 1.87),
                    (-0.009, 0.092, 1.893),
                ],
                "scarf",
                0.012,
            )


def accessory(c, kind, x, y, z):
    def stick(name, a, b, ra, rb, ink):
        c.rod(
            name,
            [
                ((x + a[0], y + a[1], z + a[2]), ra, ra),
                ((x + b[0], y + b[1], z + b[2]), rb, rb),
            ],
            ink,
        )

    def plate(name, outline, ink, ridge=0.014):
        c.fold(name, [(x + a, y + b, z + d) for a, b, d in outline], ink, ridge)

    if kind in ("log", "tile", "linen"):
        color = {"log": "satchel", "tile": "scarf", "linen": "linen"}[kind]
        plate(
            "folio cover"
            if kind == "log"
            else ("kiln sample" if kind == "tile" else "folded napkin"),
            [
                (-0.046, 0.012, -0.064),
                (0.126, 0.017, -0.04),
                (0.145, -0.004, 0.174),
                (-0.029, -0.008, 0.149),
            ],
            color,
            0.021,
        )
        plate(
            "binding",
            [
                (0.001, -0.019, -0.051),
                (0.017, -0.02, -0.048),
                (0.036, -0.029, 0.153),
                (0.018, -0.029, 0.151),
            ],
            "edge",
            0.004,
        )
    elif kind in ("plumb", "lantern", "seal", "key"):
        stick(
            "palm strap", (0, 0, -0.006), (0.018, -0.009, 0.088), 0.01, 0.009, "satchel"
        )
        stick(
            "plaited lanyard",
            (0.018, -0.009, 0.088),
            (0.09, -0.017, -0.077),
            0.007,
            0.006,
            "satchel",
        )
        if kind == "key":
            stick(
                "key bow",
                (0.089, -0.017, -0.075),
                (0.089, -0.017, -0.17),
                0.014,
                0.012,
                "metal",
            )
            plate(
                "key tooth",
                [
                    (0.085, -0.02, -0.14),
                    (0.118, -0.02, -0.136),
                    (0.12, -0.02, -0.16),
                    (0.086, -0.02, -0.167),
                ],
                "gold",
                0.008,
            )
        else:
            w = 0.061 if kind == "lantern" else 0.039
            c.profile(
                "hand lantern" if kind == "lantern" else "sounding weight",
                [
                    (z - 0.235, w * 0.3, w * 0.34, x + 0.09, y - 0.017),
                    (z - 0.20, w, w * 0.82, x + 0.09, y - 0.017),
                    (z - 0.104, w * 0.94, w * 0.78, x + 0.09, y - 0.017),
                    (z - 0.073, w * 0.28, w * 0.26, x + 0.09, y - 0.017),
                ],
                "gold" if kind == "lantern" else "metal",
            )
    elif kind in ("ladle", "hook", "hammer"):
        stick("worn haft", (0, 0, -0.109), (0.015, -0.006, 0.181), 0.013, 0.016, "wood")
        if kind == "hook":
            stick(
                "boat hook",
                (0.015, -0.006, 0.18),
                (0.062, -0.006, 0.22),
                0.015,
                0.011,
                "metal",
            )
            stick(
                "turned hook",
                (0.062, -0.006, 0.22),
                (0.096, -0.006, 0.175),
                0.012,
                0.005,
                "metal",
            )
        elif kind == "ladle":
            c.profile(
                "ladle bowl",
                [
                    (z + 0.163, 0.036, 0.022, x + 0.017, y - 0.01),
                    (z + 0.207, 0.056, 0.034, x + 0.027, y - 0.01),
                    (z + 0.231, 0.049, 0.021, x + 0.03, y - 0.008),
                ],
                "wood",
            )
        else:
            plate(
                "forge hammer",
                [
                    (-0.071, 0, 0.153),
                    (0.077, 0, 0.162),
                    (0.084, 0, 0.209),
                    (-0.053, 0, 0.207),
                ],
                "metal",
                0.025,
            )
    elif kind == "rule":
        stick(
            "dividers leg",
            (-0.011, 0, -0.086),
            (0.054, -0.01, 0.158),
            0.007,
            0.012,
            "gold",
        )
        stick(
            "dividers leg",
            (0.054, -0.01, 0.158),
            (0.109, -0.008, -0.062),
            0.012,
            0.005,
            "metal",
        )
    elif kind == "sprig":
        stick(
            "willow graft", (0, 0, -0.091), (0.021, -0.012, 0.20), 0.011, 0.006, "wood"
        )
        for i, s in enumerate((-1, 1, -1)):
            h = 0.067 + i * 0.047
            plate(
                "graft leaf",
                [
                    (0.013, -0.012, h),
                    (0.021 + s * 0.026, -0.018, h + 0.047),
                    (0.018 + s * 0.074, -0.016, h + 0.061),
                    (0.02 + s * 0.048, -0.013, h + 0.018),
                ],
                "edge",
                0.008,
            )
    elif kind == "winder":
        for side in (-1, 1):
            stick(
                "shuttle tip",
                (side * 0.077, 0, -0.065),
                (side * 0.081, 0, 0.113),
                0.011,
                0.009,
                "wood",
            )
        plate(
            "flax wound shuttle",
            [
                (-0.079, -0.004, -0.025),
                (0.078, -0.004, -0.037),
                (0.079, -0.004, 0.063),
                (-0.077, -0.004, 0.083),
            ],
            "linen",
        )


def principal_details(groups):
    """Re-cut specific soft facial pieces while retaining each principal's painted costume."""
    import bpy

    for obj in list(groups.get("SpeakerHead", [])):
        if not obj.data.materials:
            continue
        ink = obj.data.materials[0].name
        if ink not in (
            "TaviAtelier",
            "MossAtelier",
            "FenAtelier",
            "OssaAtelier",
            "OrlaAtelier",
        ):
            continue
        label = obj.name.split(".")[0]
        # Each description uses the object's own oriented bounds. Face paintings and
        # the performers' moving pivots stay attached to their original head group.
        if label in ("Nose bridge", "Windworn nose", "Nose"):
            shape = "nose"
        elif label in ("Lobed ear", "Ear", "Keeper's ear"):
            shape = "ear"
        elif label in (
            "Silver temple",
            "Dark temple",
            "Dark curl",
            "Whiskers",
            "High bun",
        ):
            shape = "lock"
        elif label in (
            "Eye",
            "Eye white",
            "Iris",
            "Dark iris",
            "Eye light",
            "Catchlight",
        ):
            shape = "eye"
        else:
            continue
        coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
        lo = [min(v[i] for v in coords) for i in range(3)]
        hi = [max(v[i] for v in coords) for i in range(3)]
        center = [(a + b) * 0.5 for a, b in zip(lo, hi)]
        radius = [(b - a) * 0.5 for a, b in zip(lo, hi)]
        head = groups["SpeakerHead"]
        center_x = (
            sum(
                v[0]
                for v in [
                    obj.matrix_world @ Vector(corner)
                    for corner in next(
                        o
                        for o in head
                        if o.name.startswith(
                            ("Moss’s face", "Weathered face", "Cheekbones and jaw")
                        )
                    ).bound_box
                ]
            )
            / 8
        )
        side = -1 if center[0] < center_x else 1
        if shape == "nose":
            outline = [
                (-0.46, 0.25, 1.04),
                (0.43, 0.18, 1),
                (0.96, -0.16, -0.47),
                (0.48, -0.72, -0.84),
                (-0.68, -0.62, -0.93),
                (-1, -0.01, -0.51),
            ]
            ridge = (0.02, -1.40, -0.48)
        elif shape == "ear":
            outline = [
                (-0.89, -0.20, 0.32),
                (-0.23, -0.12, 0.55),
                (1.85, 0.67, 1.35),
                (0.78, 0.44, -0.28),
                (-0.30, 0.02, -0.98),
                (-1, -0.07, -0.42),
            ]
            ridge = (0.04, -0.90, 0.015)
        elif shape == "lock":
            outline = [
                (-0.9, 0.32, 0.37),
                (-0.54, 0.31, 0.98),
                (0.46, 0.18, 0.91),
                (1.02, 0.33, 0.28),
                (1.18, -0.05, -0.28),
                (0.47, -0.29, -0.14),
                (0.13, -0.44, -1.46),
                (-0.77, -0.22, -0.53),
            ]
            ridge = (0.19, -1.12, 0.27)
        else:
            outline = [
                (-0.98, 0.12, -0.15),
                (-0.60, 0.12, 0.68),
                (0.18, 0.07, 0.94),
                (1, 0.18, 0.18),
                (0.55, 0.16, -0.68),
                (-0.19, 0.08, -0.94),
            ]
            ridge = (0.02, -0.90, 0.04)
        pts = outline + [ridge, (0, 0.86, 0.06)]
        pts = [
            (
                center[0] + side * u * radius[0],
                center[1] + v * radius[1],
                center[2] + w * radius[2],
            )
            for u, v, w in pts
        ]
        n = len(outline)
        faces = [(n, i, (i + 1) % n) for i in range(n)] + [
            (n + 1, (i + 1) % n, i) for i in range(n)
        ]
        pos = [Vector(p) - Vector(center) for p in pts]
        if sum(pos[a].dot(pos[b].cross(pos[c])) for a, b, c in faces) < 0:
            faces = [tuple(reversed(face)) for face in faces]
        olduv = [tuple(l.uv) for l in obj.data.uv_layers.active.data]
        umin, vmin = map(min, zip(*olduv))
        umax, vmax = map(max, zip(*olduv))
        uv = [
            (
                umin
                + (umax - umin)
                * min(
                    0.93, max(0.07, 0.5 + 0.40 * (pts[i][0] - center[0]) / radius[0])
                ),
                vmin
                + (vmax - vmin)
                * min(
                    0.93, max(0.07, 0.5 + 0.40 * (pts[i][2] - center[2]) / radius[2])
                ),
            )
            for f in faces
            for i in f
        ]
        label = obj.name
        groups["SpeakerHead"].remove(obj)
        bpy.data.objects.remove(obj, do_unlink=True)
        geometry(label, pts, faces, ink, "SpeakerHead", uv)
    # Tavi's ears and nose already have an angular silhouette. Lower three asymmetric
    # fringe tips and angle the outer ends to give the cropped bob breaks in profile.
    for obj in groups.get("SpeakerHead", []):
        if obj.name.split(".")[0] != "Swept fringe lock":
            continue
        index = int(obj.name.split(".")[-1]) if "." in obj.name else 0
        if index not in (0, 3, 6, 8):
            continue
        verts = obj.data.vertices
        bottom = min(v.co.z for v in verts)
        for v in verts:
            if v.co.z < bottom + 0.013:
                v.co.z -= 0.038 if index in (0, 8) else 0.022
                v.co.x += -0.024 if index < 4 else 0.018
        obj.data.update()


def returning_maker(name, foot, height, angle, names, groups, pivots):
    from river_makers import maker

    # Build this performer in isolation. The three named exports can also belong to a
    # different speaker in the same district. Restore those batches and their local pivots.
    limbs = ("Speaker", "SpeakerHead", "SpeakerArm")
    saved = {k: groups.pop(k, []) for k in limbs}
    old = {k: pivots.pop(k) for k in limbs if k in pivots}
    load_paint("OssaAtelier" if name == "Ossa" else "FenAtelier")
    maker(0, 0, 0, name == "Ossa")
    principal_details(groups)
    portions = [groups.pop(k) for k in limbs]
    joints = [pivots.pop(k) for k in limbs[1:]]
    groups.update(saved)
    pivots.update(old)
    top = max(v.co.z for objs in portions for o in objs for v in o.data.vertices)
    transform = (
        Matrix.Translation(foot)
        @ Matrix.Rotation(angle, 4, "Z")
        @ Matrix.Scale(height / top, 4)
    )
    for dest, objects in zip(names, portions):
        for o in objects:
            o.data.transform(transform)
        groups[dest].extend(objects)
    return tuple(tuple(transform @ Vector(p)) for p in joints)


def dress_residents(groups, pivots):
    import bpy

    principal_details(groups)
    sawyer(groups)
    commons = list(groups.get("Speaker", []))
    actors = []
    if len(commons) == 1 and commons[0].data.materials[0].name.endswith("Atlas"):
        actors.append(("Speaker", commons[0], True))
    for grp in ("Ina", "CrewAshore", "MessCrew", "Set"):
        for obj in list(groups.get(grp, [])):
            if not obj.data.materials or not obj.data.materials[0].name.endswith(
                "Atlas"
            ):
                continue
            if grp == "Set" and not obj.name.startswith(
                (
                    "Ossa by the cooling",
                    "Nema counting",
                    "Fen listening",
                    "Orrel guarding",
                    "Brannic at",
                )
            ):
                continue
            actors.append((grp, obj, False))
    for group, obj, animated in actors:
        first = obj.name.split()[0].replace("’s", "")
        if group == "CrewAshore":
            first = CREW[int(obj.name.rsplit(".", 1)[1]) if "." in obj.name else 0]
        if first == "The":
            first = "Registrar"
        original = [(group, obj)]
        if animated:
            original += [
                (g, p) for g in ("SpeakerHead", "SpeakerArm") for p in groups[g]
            ]
        zmax = max(
            (p.matrix_world @ Vector(c)).z for _, p in original for c in p.bound_box
        )
        foot = obj.location.copy()
        h = zmax - foot.z
        angle = obj.rotation_euler.z
        for g, p in original:
            groups[g].remove(p)
            bpy.data.objects.remove(p, do_unlink=True)
        names = (
            ("Speaker", "SpeakerHead", "SpeakerArm")
            if animated
            else (group, group, group)
        )
        if first in ("Fen", "Ossa"):
            head, arm = returning_maker(first, foot, h, angle, names, groups, pivots)
        else:
            load_paint("ResidentCloth")
            head, arm = make(first, foot, h, angle, names)
        if animated:
            pivots["SpeakerHead"], pivots["SpeakerArm"] = head, arm
    return len(actors)


def facial_hair(c, mark):
    if mark not in ("forkbeard", "jawbeard", "whiskers"):
        return
    if mark != "whiskers":
        c.profile(
            "trimmed beard",
            [
                (1.403, 0.043, 0.052, 0, -0.048),
                (1.444, 0.091, 0.094, 0, -0.039),
                (1.500, 0.129, 0.125, 0, -0.035),
                (1.547, 0.143, 0.124, 0, -0.018),
            ],
            "hair",
        )
        for side in (-1, 1):
            c.fold(
                "shaped beard tip",
                [
                    (side * 0.008, -0.171, 1.516),
                    (side * 0.105, -0.141, 1.529),
                    (side * 0.113, -0.109, 1.461),
                    (side * 0.06, -0.124, 1.382 if mark == "forkbeard" else 1.422),
                ],
                "hairlight",
                0.014,
            )
    for side in (-1, 1):
        c.fold(
            "swept moustache",
            [
                (side * 0.003, -0.163, 1.556),
                (side * 0.044, -0.165, 1.565),
                (side * 0.083, -0.148, 1.553),
                (side * 0.116, -0.155, 1.569),
                (side * 0.089, -0.166, 1.532),
                (side * 0.04, -0.169, 1.539),
            ],
            "hairlight",
            0.012,
        )


def sawyer(groups):
    import bpy

    head = next((o for o in groups.get("Set", []) if o.name == "Linn’s cheeks"), None)
    if head is None:
        return
    load_paint("ResidentCloth")
    ox, oy = face_patch("Linn")
    xs = [v.co.x for v in head.data.vertices]
    ys = [v.co.y for v in head.data.vertices]
    zs = [v.co.z for v in head.data.vertices]
    x = (min(xs) + max(xs)) * 0.5
    y = (min(ys) + max(ys)) * 0.5
    z = min(zs)
    head.data.materials[0] = load_paint("ResidentCloth")
    kit = COSTUMES["Linn"].kit
    for face in head.data.polygons:
        for li in face.loop_indices:
            v = head.data.vertices[head.data.loops[li].vertex_index].co
            if face.normal.y < -0.24:
                u = max(0.02, min(0.98, 0.5 + (v.x - x) / 0.43))
                t = max(0.02, min(0.98, (max(zs) - v.z) / 0.407))
                uv = ((ox + 2 + 60 * u) / 512, 1 - (oy + 2 + 60 * t) / 512)
            else:
                uv = ((kit * 32 + 14) / 512, 1 - 132 / 512)
            head.data.uv_layers.active.data[li].uv = uv
    # The new face painting sits directly under Linn's wire spectacles.
    for obj in list(groups["Set"]):
        if obj.name.split(".")[0] in ("Linn’s eye", "Linn’s brow"):
            groups["Set"].remove(obj)
            bpy.data.objects.remove(obj, do_unlink=True)
    carver = Carver(
        "Linn", COSTUMES["Linn"], Matrix.Translation((x, y, z)), *("Set",) * 3
    )
    carver.fold(
        "knotted scarf tail",
        [
            (-0.145, 0.084, 0.41),
            (-0.231, 0.079, 0.385),
            (-0.265, 0.094, 0.19),
            (-0.176, 0.105, 0.28),
        ],
        "scarf",
        0.021,
    )
    carver.fold(
        "second scarf tail",
        [
            (-0.16, 0.092, 0.39),
            (-0.222, 0.071, 0.362),
            (-0.327, 0.025, 0.297),
            (-0.256, 0.069, 0.389),
        ],
        "edge",
        0.016,
    )
