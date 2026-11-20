"""Blender source for Wrenfall Head. World units and the printed pilot chart share a coordinate system."""

import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from atelier import RES, init, geometry, block, shaft, lathe, collision, marker, model, finish, origins
from works_sets import ring
from works_finish import plaques, mount
from sets import arch
from underworks import rooms

KEY = "Wrenfall"
SPAN = 60
TRACKS = [
    [(-9, -13), (0, -15), (-9, -21), (-21, -18), (-32, -24), (-40, -27)],
    [(-4, -13), (6, -10), (14, -15), (25, -12), (32, -8), (40, -7)],
    [(-40, -26), (-47, -10), (-44, 1), (-37, 10), (-40, 21), (-28, 32)],
    [(-28, 32), (-15, 33), (-6, 39), (7, 40), (16, 32), (27, 26), (36, 23), (42, 11), (39, -5)],
    [(1, -13), (6, -1), (1, 10), (6, 19), (16, 32)],
]
WOOD = "Wood"
STONE = "Masonry"
BRASS = "Brass"


def height(x, y):
    def hill(px, py, r, h):
        return h * np.exp(-((x - px) ** 2 + (y - py) ** 2) / (2 * r * r))

    undulation = 0.6 + 0.42 * np.sin(x / 8 + y / 13) * np.cos(y / 9)
    raw = (
        undulation
        + hill(-29, 33, 15, 7)
        + hill(35, -3, 15, 4)
        + hill(-39, -26, 12, 2.5)
        + hill(25, 28, 10, 3.2)
    )
    return raw * np.clip((x * x + (y + 14) ** 2) / 170, 0, 1)


def chart_point(x, y, n):
    return (round((x + SPAN) / (2 * SPAN) * (n - 1)), round((SPAN - y) / (2 * SPAN) * (n - 1)))


TREES = [
    (-20, -28, 6),
    (-24, -30, 4.9),
    (-22, -34, 5.8),
    (-48, -18, 5.5),
    (-48, -29, 4.4),
    (-52, -33, 4),
    (-40, 8, 5.1),
    (-44, 10, 7),
    (-42, 15, 4.8),
    (-17, 17, 7),
    (-20, 21, 5.2),
    (-16, 24, 6.1),
    (14, -30, 6.5),
    (18, -28, 5),
    (22, -34, 6),
    (30, 8, 4.8),
    (27, 10, 6.1),
    (15, 45, 4.7),
    (20, 44, 5.3),
]


def paint():
    n = 768
    y, x = np.mgrid[0:n, 0:n]
    x = x * 120 / (n - 1) - 60
    y = 60 - y * 120 / (n - 1)
    rng = np.random.default_rng(587)

    def cloud(size):
        return (
            np.asarray(
                Image.fromarray(rng.integers(0, 255, (size, size), dtype=np.uint8)).resize(
                    (n, n), Image.Resampling.BICUBIC
                ),
                float,
            )
            / 255
            - 0.5
        )

    grain = cloud(156)
    patches = cloud(27)
    fine = cloud(n)
    dist = np.full((n, n), 1000.0)
    for path in TRACKS:
        for (a, b), (c, d) in zip(path, path[1:]):
            dx, dy = c - a, d - b
            t = np.clip(((x - a) * dx + (y - b) * dy) / (dx * dx + dy * dy), 0, 1)
            dist = np.minimum(dist, np.hypot(x - a - t * dx, y - b - t * dy))

    def tile(name):
        tex = np.array(Image.open(RES / "Textures" / (name + ".png")).convert("RGB"), float)
        return tex[
            (np.floor(y * 5).astype(int)) % tex.shape[0], (np.floor(x * 5).astype(int)) % tex.shape[1]
        ]

    path = np.clip((2.1 + patches * 0.85 - dist) * 1.8, 0, 1)
    ground = tile("Grass") * 0.51 + np.array([56, 71, 34]) + patches[:, :, None] * np.array([34, 26, 13])
    road = tile("DirtPath") * 0.6 + np.array([69, 64, 42])
    coast = np.clip((np.maximum(abs(x), abs(y)) - 46 + patches * 5) / 14, 0, 0.7)[:, :, None]
    rgb = ground * (1 - path[:, :, None]) + road * path[:, :, None]
    rgb = rgb * (1 - coast) + (tile("Shale") * 0.6 + 52) * coast
    shade = np.ones((n, n))
    for tx, ty, h in TREES:
        shade *= 1 - 0.31 * np.exp(
            -(((x - tx - 1.1) / (h * 0.42)) ** 2 + ((y - ty + 0.5) / (h * 0.32)) ** 2)
        )
    for tx, ty, r in [(-6, -5, 3.3), (-40, -21, 3), (-35, 40, 3.1), (30, 33, 4), (8, 47, 3), (41, 2, 2)]:
        shade *= 1 - 0.29 * np.exp(-((x - tx) ** 2 + (y - ty) ** 2) / (r * r))
    for px, py, width, depth in [
        (-10.45, -13, 0.68, 0.8),
        (-7.55, -13, 0.68, 0.8),
        (-4, -9, 0.44, 0.37),
        (0, -8, 2.15, 0.58),
        (-6, -5, 4, 2.9),
        (-40, -20, 4.0, 3.4),
    ]:
        shade *= 1 - 0.34 * np.exp(-(((x - px - 0.12) / width) ** 2 + ((y - py + 0.18) / depth) ** 2))
    petal_rng = np.random.default_rng(314)
    shades = np.array([[174, 120, 132], [197, 148, 148], [214, 167, 158], [182, 129, 139]], dtype=np.uint8)
    Image.fromarray(shades[petal_rng.integers(0, len(shades), (32, 32))]).save(
        RES / "Textures" / "SeaThrift.png"
    )
    rgb = rgb * shade[:, :, None] + (grain * 11 + fine * 10)[:, :, None]
    Image.fromarray(np.uint8(rgb.clip(0, 255))).save(RES / "Textures" / (KEY + "Ground.png"))
    n = 512
    im = Image.new("RGB", (n, n), "#c5b37a")
    draw = ImageDraw.Draw(im)
    y, x = np.mgrid[0:n, 0:n]
    elev = height(x * 120 / (n - 1) - 60, 60 - y * 120 / (n - 1))
    pix = np.array(im)
    pix[np.mod(elev, 0.85) < 0.13] = [154, 153, 98]
    im = Image.fromarray(pix)
    draw = ImageDraw.Draw(im)
    for path in TRACKS:
        draw.line([chart_point(*point, n) for point in path], fill="#846342", width=5)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 18)
    draw.rectangle((5, 5, 506, 506), outline="#504e39", width=5)
    for x, y, t in [
        (-39, -23, "Chapel"),
        (39, -4, "Split Stone"),
        (-28, 35, "Lookout"),
        (27, 29, "Halyards"),
        (8, 43, "Landing"),
        (-4, -10, "You are here"),
    ]:
        a, b = chart_point(x, y, n)
        draw.ellipse((a - 5, b - 5, a + 5, b + 5), fill="#762f21")
        draw.text(
            (a, b + 8), t, font=font, anchor="mt", fill="#332d22", stroke_width=1, stroke_fill="#d7c99e"
        )
    draw.text((250, 470), "WRENFALL   •   PILOTS’ SURVEY", font=font, anchor="mm", fill="#353c3a")
    im.save(RES / "Textures" / (KEY + "Chart.png"))


def glyph(kind, centre, size, material, group="Set"):
    x, y, z = centre
    if kind == "star":
        outline = [
            (
                math.cos(math.pi / 2 + i * math.pi / 5) * (1 if i % 2 == 0 else 0.43),
                math.sin(math.pi / 2 + i * math.pi / 5) * (1 if i % 2 == 0 else 0.43),
            )
            for i in range(10)
        ]
    elif kind == "wing":
        outline = [
            (-1, 0.7),
            (-0.15, 0.4),
            (0.28, 0.16),
            (1, 0.94),
            (0.69, 0.05),
            (0.22, -0.55),
            (-0.35, -0.9),
            (-0.21, -0.33),
            (-0.67, -0.5),
        ]
    else:
        outline = [
            (-0.82, -0.58),
            (0.82, -0.58),
            (0.55, -0.24),
            (0.46, 0.48),
            (0.24, 0.73),
            (0.08, 0.75),
            (0, 1),
            (-0.15, 0.75),
            (-0.41, 0.59),
            (-0.53, 0.3),
            (-0.57, -0.21),
        ]
    pts = [(x, y, z)] + [(x + a * size, y, z + b * size) for a, b in outline]
    geometry(
        kind + " pilot cutwork",
        pts,
        [(0, i + 1, (i + 1) % len(outline) + 1) for i in range(len(outline))],
        material,
        group,
    )


def beam(name, a, b, r, mat=WOOD, group="Set"):
    return shaft(name, a, b, r, r, mat, 8, group)


def cliff_apron(ground):
    from country import boundary
    from mathutils import Vector
    edge = boundary(ground)
    n = len(edge)
    vertices = []
    for band in range(3):
        for i, point in enumerate(edge):
            direction = Vector((point.x,point.y,0)).normalized()
            toe = 4.4 + 1.55*math.cos(i*.80)
            distance = (0,1.55,toe)[band]
            height = (point.z,point.z-.75,-4.30)[band]
            vertices.append((point.x+distance*direction.x,point.y+distance*direction.y,height))
    faces = [(j*n+i,(j+1)*n+i,(j+1)*n+(i+1)%n,j*n+(i+1)%n)
             for j in range(2) for i in range(n)]
    return geometry("Folded headland shore",vertices,faces,"MossRock","Rim")


def terrace():
    grid = range(-60, 61, 2)
    pts = [(x, y, float(height(x, y))) for y in grid for x in grid]
    faces = []
    for j in range(60):
        for i in range(60):
            t = j * 61 + i
            faces.extend([(t, t + 1, t + 62), (t, t + 62, t + 61)])
    ground = geometry("Unbroken salt-grass headland", pts, faces, KEY + "Ground", "Terrain")
    uv = ground.data.uv_layers.active.data
    for i, l in enumerate(ground.data.loops):
        x, y, _ = pts[l.vertex_index]
        uv[i].uv = ((x + 60) / 120, (y + 60) / 120)
    cliff_apron(ground)
    for axis in (0, 1):
        for side in (-1, 1):
            at = lambda u, r: (u, side * r) if axis == 0 else (side * r, u)
            collision(
                "Headland perimeter",
                *at(0, 60.4),
                -6,
                122 if axis == 0 else 0.8,
                0.8 if axis == 0 else 122,
                30,
            )
    # Scenic water beyond the playable lip, excluded from the physics hierarchy.
    block("Open tidal water", (0, 0, -4.1), (360, 360, 0.5), "Water", "Horizon")
    r = random.Random(662)
    for _ in range(140):
        x, y = r.uniform(-145, 145), r.uniform(-145, 145)
        if max(abs(x), abs(y)) < 66:
            continue
        w = r.uniform(1, 8)
        d = r.uniform(0.08, 0.4)
        geometry(
            "Foam streak",
            [(x - w, y, -3.81), (x, y - d, -3.81), (x + w, y + 0.2, -3.81), (x, y + d, -3.81)],
            [(0, 1, 2, 3)],
            "SeaGlass",
            "Horizon",
        )


def stone(name, x, y, z, r, h, mat, group="Set", seed=1):
    rand = random.Random(seed)
    n = 8
    pts = []
    faces = []
    vs = [rand.uniform(0.78, 1.2) for _ in range(n)]
    for k, (rr, hh) in enumerate([(1.1, -0.18), (0.99, 0.43), (0.71, 0.87), (0.45, 1)]):
        for i in range(n):
            a = i * math.tau / n
            pts.append(
                (
                    x + r * (rr * vs[i] * math.cos(a) + k * 0.06),
                    y + r * rr * vs[i] * math.sin(a),
                    z + h * (hh + rand.uniform(-0.03, 0.03)),
                )
            )
        if k:
            for i in range(n):
                faces.append(((k - 1) * n + i, (k - 1) * n + (i + 1) % n, k * n + (i + 1) % n, k * n + i))
    faces.append(tuple(range(3 * n, 4 * n)))
    return geometry(name, pts, faces, mat, group)


def hut(x, y, z, width, depth, eave, material="HousePlaster"):
    block("Salt-stained foundation", (x, y, z + 0.18), (width + 0.45, depth + 0.45, 0.75), "Masonry")
    block("Limewashed weather wall", (x, y, z + eave * 0.5), (width, depth, eave), material)
    half = width / 2 + 0.48
    d = depth / 2 + 0.46
    rise = width * 0.37
    geometry(
        "Closed steep shingle roof",
        [
            (x + a, y + b, z + h)
            for b in (-d, d)
            for a, h in [(-half, eave - 0.12), (half, eave - 0.12), (0, eave + rise)]
        ],
        [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (2, 5, 3, 0), (1, 4, 5, 2)],
        "RoofSlate",
    )
    for side in (-1, 1):
        front = y + side * (d + 0.022)
        geometry(
            "Lime infill in the gable",
            [
                (x - half + 0.14, front, z + eave),
                (x + half - 0.14, front, z + eave),
                (x, front, z + eave + rise - 0.12),
            ],
            [(0, 1, 2), (2, 1, 0)],
            material,
        )
        beam("King post", (x, front, z + eave - 0.1), (x, front, z + eave + rise - 0.06), 0.115)
        beam("Bressummer", (x - half, front, z + eave), (x + half, front, z + eave), 0.13)
        for direction in (-1, 1):
            beam(
                "Carved bargeboard",
                (x + direction * half, front, z + eave - 0.1),
                (x, front, z + eave + rise + 0.02),
                0.14,
            )
            beam(
                "Half-timber brace",
                (x, front, z + eave + 0.19),
                (x + direction * half * 0.46, front, z + eave + rise * 0.52),
                0.085,
            )
    beam("Roof ridge", (x, y - d - 0.24, z + eave + rise), (x, y + d + 0.24, z + eave + rise), 0.16)
    block("Stone threshold", (x, y - depth / 2 - 0.37, z + 0.13), (1.6, 0.72, 0.32), STONE)
    for side in (-1, 1):
        for fy in (-0.22, 0.22):
            sx = x + side * (width * 0.5 + 0.04)
            sy = y + fy * depth
            block("Side window surround", (sx, sy, z + 1.55), (0.16, 0.97, 1.08), WOOD)
            block("Side window glass", (sx + side * 0.10, sy, z + 1.55), (0.06, 0.69, 0.81), "WindowDark")
    for side in (-1, 1):
        block(
            "Tarred corner post",
            (x + side * (width / 2 - 0.12), y - depth / 2 - 0.07, z + eave * 0.5),
            (0.22, 0.2, eave),
            "Wood",
        )
    block("Plank entry", (x, y - depth / 2 - 0.08, z + 1.01), (1.06, 0.19, 2.02), "Wood")
    for side in (-1, 1):
        xw = x + side * width * 0.32
        block("Window frame", (xw, y - depth / 2 - 0.08, z + 1.54), (0.94, 0.18, 1.08), "Wood")
        block("Pilot glass", (xw, y - depth / 2 - 0.18, z + 1.55), (0.68, 0.05, 0.83), "WindowLight")
        block("Lead mullion", (xw, y - depth / 2 - 0.22, z + 1.55), (0.085, 0.06, 0.86), "Wood")


def boat(x, y, z, group):
    # Longitudinal stations carry the rising keel, painted sheer strake and weather deck.
    sections = [
        (-4.8, 0.08, 1.53),
        (-3.5, 0.91, 1.16),
        (-1.6, 1.34, 0.98),
        (1, 1.42, 0.97),
        (3.3, 1.08, 1.09),
        (4.45, 0.78, 1.22),
    ]
    pts = []
    for u, w, h in sections:
        pts.extend(
            [
                (x + u, y + w * a, z + b)
                for a, b in [(-1, h), (-0.84, 0.48), (0, 0.03), (0.84, 0.48), (1, h)]
            ]
        )
    faces = []
    for i in range(len(sections) - 1):
        for j in range(4):
            a = i * 5 + j
            faces.append((a, a + 5, a + 6, a + 1))
    faces.extend([tuple(range(4, -1, -1)), tuple(range(25, 30))])
    geometry("Riveted lapstrake hull", pts, faces, WOOD, group)
    for i in range(len(sections) - 1):
        u, w, h = sections[i]
        v, b, k = sections[i + 1]
        geometry(
            "Weathered deck",
            [(x + u, y - w, z + h), (x + v, y - b, z + k), (x + v, y + b, z + k), (x + u, y + w, z + h)],
            [(0, 1, 2, 3)],
            "Causeway",
            group,
        )
        for s in (-1, 1):
            beam(
                "Painted sheer strake",
                (x + u, y + s * w, z + h),
                (x + v, y + s * b, z + k),
                0.08,
                "SeaGlass",
                group,
            )
    mast = (x - 0.7, y, z + 7.2)
    beam("Cutter mainmast", (x - 0.7, y, z + 0.62), mast, 0.12, WOOD, group)
    for u in (-4.5, 4.25):
        beam("Tarred standing rigging", mast, (x + u, y, z + 1.27), 0.037, "CoalCloth", group)
    for coords, mat in [
        ([(-0.54, 6.8), (2.0, 5.1), (3.05, 2.22), (-0.54, 2.05)], "Awning"),
        ([(-0.93, 6.24), (-1.09, 2.0), (-4.03, 1.79)], "SeaCloth"),
    ]:
        vs = [(x + u, y - 0.04, z + h) for u, h in coords]
        geometry(
            "Linen working sail", vs, [tuple(range(len(vs))), tuple(reversed(range(len(vs))))], mat, group
        )
    block("Aft hatch coaming", (x + 2.66, y, z + 1.19), (1.14, 0.95, 0.36), "RoofSlate", group)
    for u in (-2.1, 1.5):
        block("Thwart", (x + u, y, z + 1.13), (0.24, 1.95, 0.11), WOOD, group)


def island_furniture(r):
    # Entry shelter with a field chart printed against the player's actual north.
    x, y = -6, -4
    hut(x, y, height(x, y) - 0.25, 6.2, 4.3, 2.9)
    z = height(0, -8)
    for x in (-1.7, 1.7):
        block("Survey board leg", (x, -8, z + 1.4), (0.26, 0.29, 2.9), WOOD)
    block("Chart cedar backing", (0, -8, z + 2.14), (3.68, 0.31, 2.92), WOOD)
    geometry(
        "Painted pilot chart",
        [
            (-1.72, -8.17, z + 0.78),
            (1.72, -8.17, z + 0.78),
            (1.72, -8.17, z + 3.50),
            (-1.72, -8.17, z + 3.50),
        ],
        [(0, 1, 2, 3)],
        KEY + "Chart",
        "Set",
        [(0, 0), (1, 0), (1, 1), (0, 1)],
    )
    # Low chapel, pierced bellcote, tidal staff and gull-shaped maximum tide recorded in brass.
    x, y = -40, -19
    z = height(x, y) - 0.35
    hut(x, y, z, 6.2, 5.8, 3.55, "OchrePlaster")
    block("Joined bellcote plinth", (x, y, z + 4.48), (3.34, 1.06, 2.05), STONE)
    beam("Oak bell bearing", (x - 1.2, y, z + 6.99), (x + 1.2, y, z + 6.99), 0.14, WOOD)
    arch(x, y, z + 5.45, 2.1, 2.35, "Masonry", "MossRock")
    lathe(
        "Tide chapel bell", x, y, z + 6.2, [(0.48, 0), (0.5, 0.1), (0.32, 0.54), (0.18, 0.72)], "BellMetal"
    )
    for j, (symbol, mat) in enumerate([("star", "Slate"), ("bell", "BellMetal"), ("wing", "Brass")]):
        x = -40
        y = -24
        z = height(x, y)
        if j == 0:
            block("Notched tide staff", (x, y, z + 1.46), (0.21, 0.26, 3.15), WOOD)
        block("Flood notch", (x, y - 0.17, z + 0.77 + j * 0.83), (0.83, 0.10, 0.085), mat)
        glyph(symbol, (x + 0.65, y - 0.23, z + 0.8 + j * 0.83), 0.36, mat)
    x, y = 40, -4
    z = height(x, y)
    lathe(
        "Survey bearing foot",
        x,
        y,
        z - 0.08,
        [(0.68, 0), (0.76, 0.18), (0.34, 0.38), (0.29, 1.23)],
        "Masonry",
    )
    beam("Sighting rail", (x, y - 0.4, z + 1.25), (x + 0.23, y + 2.9, z + 1.25), 0.10, BRASS)
    # Align the apertures with the bell on the distant natural stack.
    target = (45.6, 75, 12.1)
    eye = (40, -6.4, z + 1.54)
    for t in (0.055, 0.17):
        a, b, c = [eye[i] + t * (target[i] - eye[i]) for i in range(3)]
        beam("Transit sight post", (a, b, height(a, b) - 0.12), (a, b, c - 0.31), 0.14, WOOD)
        ring("Machined alignment hoop", (a, b, c), 0.33 if t < 0.1 else 0.55, 0.073, BRASS, "y")
    for j, (a, b, rr, hh) in enumerate(
        [
            (44, 75, 4.8, 14),
            (51, 81, 3.7, 9),
            (38, 90, 2.5, 6),
            (-55, 80, 5, 12),
            (-43, 92, 2.8, 6),
            (82, 28, 4.6, 12),
            (96, -18, 7, 17),
            (-81, -15, 6, 15),
        ]
    ):
        stone("Offshore chalk stack", a, b, -4, rr, hh, "Shale", "Horizon", j + 26)
    beam("Offshore bell spar", (45.6, 75, 8), (45.6, 75, 15.2), 0.35, WOOD, "Horizon")
    glyph("bell", target, 2.12, BRASS, "Horizon")
    # Wind-braced northern optical station, with copper dew hood and star plate.
    x, y = -28, 35
    z = height(x, y)
    lathe(
        "Scope bearing pedestal",
        x,
        y,
        z - 0.15,
        [(0.78, 0), (0.82, 0.27), (0.44, 0.53), (0.26, 1.24), (0.46, 1.39)],
        STONE,
    )
    direction = (0.24, 1, -0.13)
    for a, b, ra, rb, mat in [
        (-0.63, 0.2, 0.16, 0.24, "BellMetal"),
        (0.18, 1.29, 0.3, 0.43, BRASS),
        (1.29, 1.5, 0.46, 0.46, "BellMetal"),
    ]:
        pts = [(x + d * direction[0], y + d, z + 1.63 + d * direction[2]) for d in (a, b)]
        shaft("Drawtube and dew shield", *pts, ra, rb, mat, 12)
    x, y = -35, 40
    z = height(x, y) - 0.2
    lathe(
        "Watchtower battered base",
        x,
        y,
        z,
        [(3.0, 0), (3, 0.68), (2.53, 1.1), (2.03, 6.7), (2.45, 6.96), (2.51, 7.2)],
        "Masonry",
        10,
    )
    for j in range(8):
        a = j * math.tau / 8
        beam(
            "Lantern room mullion",
            (x + 1.75 * math.cos(a), y + 1.75 * math.sin(a), z + 7.2),
            (x + 1.75 * math.cos(a), y + 1.75 * math.sin(a), z + 9.35),
            0.14,
            WOOD,
        )
    lathe("Watchtower lantern", x, y, z + 7.28, [(0.63, 0), (0.86, 0.89), (0.65, 1.77)], "Amber", 10)
    lathe(
        "Turned lantern cap",
        x,
        y,
        z + 9.4,
        [(2.45, 0), (2.54, 0.13), (0.39, 1.53), (0.08, 2.5)],
        "RoofSlate",
        10,
    )
    # Code mast with real hoists. Increasing stacks of flags display acknowledged signals.
    x, y = 27, 33
    z = height(x, y)
    lathe("Mast foundation", x, y, z - 0.3, [(1.45, 0), (1.58, 0.38), (0.75, 1.0)], STONE)
    beam("Flagstaff", (x, y, z + 0.3), (x, y, z + 14), 0.26, WOOD)
    beam("Halyard crossarm", (x - 4.8, y, z + 11), (x + 4.8, y, z + 11), 0.18, WOOD)
    for j, (a, symbol, cloth) in enumerate(
        [(23, "wing", "SeaCloth"), (27, "bell", "Pennon"), (31, "star", "NightCloth")]
    ):
        b = 29
        zz = height(a, b)
        for dx in (-0.15, 0.15):
            beam("Halyard fall", (a + dx, b, zz + 0.75), (a + dx, y, z + 10.95), 0.035, "CoalCloth")
        lathe(
            "Belaying bollard",
            a,
            b,
            zz - 0.12,
            [(0.39, 0), (0.45, 0.16), (0.22, 0.3), (0.22, 0.93), (0.36, 1.0)],
            WOOD,
            8,
        )
        glyph(symbol, (a, b - 0.24, zz + 1.42), 0.39, BRASS)
        for stage in range(j + 1, 4):
            tag = "Hoist" + str(stage)
            cx = a
            cy = y - 0.22
            cz = z + 9.45
            pts = [
                (cx - 0.85, cy, cz + 0.76),
                (cx + 1, cy + 0.04, cz + 0.57),
                (cx + 0.58, cy, cz),
                (cx + 1, cy + 0.10, cz - 0.66),
                (cx - 0.85, cy, cz - 0.74),
            ]
            geometry(
                "Swallow-cut pilot signal",
                pts,
                [(0, 4, 2, 1), (2, 4, 3), (1, 2, 4, 0), (3, 4, 2)],
                cloth,
                tag,
            )
            glyph(symbol, (cx - 0.04, cy - 0.065, cz), 0.46, "Inlay", tag)
    x, y = 35, 27
    z = height(x, y)
    lathe(
        "Coastal hauling capstan",
        x,
        y,
        z - 0.11,
        [(0.86, 0), (0.85, 0.19), (0.46, 0.40), (0.43, 1.06), (0.76, 1.20), (0.73, 1.32)],
        WOOD,
        12,
    )
    for i in range(4):
        a = i * math.pi / 2
        beam(
            "Capstan sweep",
            (x, y, z + 1.2),
            (x + 1.2 * math.cos(a), y + 1.2 * math.sin(a), z + 1.2),
            0.085,
            BRASS,
        )
    x, y = 8, 43
    z = height(x, y)
    for j in range(9):
        b = 45 + j * 1.65
        block("Rescue wharf deck", (8, b, height(8, min(b, 59)) + 0.06), (5, 1.65, 0.25), WOOD, "Set")
        if j % 2 == 0:
            for dx in (-2.25, 2.25):
                beam(
                    "Wharf fender pile",
                    (8 + dx, b, -4),
                    (8 + dx, b, height(8, min(b, 59)) + 0.36),
                    0.25,
                    WOOD,
                    "Horizon",
                )
    last_top = height(8, 58.2) + 0.185
    for j in range(1, 14):
        b = 59.025 + (j - 0.5) * 0.44
        top = last_top + (-3.06 - last_top) * j / 13
        block("Low-water landing stair", (8, b, top - 0.18), (3.48, 0.44, 0.36), WOOD, "Horizon")
    block("Floating landing stage", (8, 65.0, -3.24), (10, 1.8, 0.36), WOOD, "Horizon")
    for dx in (-3.7, 3.7):
        beam("Tidal landing pile", (8 + dx, 65, -4.4), (8 + dx, 65, -1.66), 0.21, WOOD, "Horizon")
    # The keel sits 0.55 m below the waterline throughout the approach.
    boat(-18, 74, -4.40, "Linnet")
    beam("Pilot star spar", (-18.7, 74, 2.60), (-18.7, 74, 4.12), 0.075, WOOD, "Linnet")
    glyph("star", (-18.7, 73.72, 3.95), 0.96, "Amber", "Linnet")
    origins["Linnet"] = (-18, 74, -4.40)
    marker("LinnetTurn", 8, 80, -4.40)
    marker("LinnetBerth", 9, 68, -4.40)
    marker("BellBearing", 45.6, 74.98, 12.1)
    marker("StarBearing", -18.7, 73.71, 3.95)
    for j, (a, b, symbol) in enumerate([(-41.6, -23, "wing"), (41.8, -3, "bell"), (-26.4, 35, "star")]):
        zz = height(a, b)
        beam("Survey pin", (a, b, zz - 0.1), (a, b, zz + 2), 0.09, BRASS)
        glyph(symbol, (a, b - 0.13, zz + 2.26), 0.40, "SeaGlass", "Reading" + str(j))
    model("WZ_COA_N01", "Mirren the shore pilot", -4, -9, height(-4, -9) - 0.02, 1.74, 10, "Speaker")
    for j, (a, b) in enumerate([(8, 43), (10.5, 46), (5.5, 47), (13, 49), (15, 51), (4, 52), (12, 54)]):
        model(
            ["WZ_COA_N02", "WZ_COA_N03", "WZ_VIL_N01"][j % 3],
            "Rescued cutter crew",
            a,
            b,
            height(a, b) - 0.035,
            1.56 + j % 3 * 0.11,
            (25 * j) % 110,
            "CrewAshore",
        )
    for s in r["stations"]:
        x, y = s["x"], s["y"]
        z = height(x, y)
        marker(s["id"], x, y - 0.36, z + 1.46)
        if s["id"] == "A_Back":
            arch(x, y, z - 0.1, 2.3, 3.1, "MossRock", BRASS)
        if s["id"] == "A_Book":
            lathe(
                "Harbourmaster’s document chest",
                x + 1.0,
                y,
                z - 0.08,
                [(0.48, 0), (0.46, 1), (0.54, 1.09)],
                STONE,
                8,
            )
    for j, s in enumerate(r["stations"]):
        if s["id"] == "A_Map":
            continue
        mount(s, 0, r, j, lambda k, x, y: height(x, y))


def oak_crown(x, y, z, w, h, seed):
    rand = random.Random(seed)
    pts = [(x, y, z - h * 0.22)]
    faces = []
    n = 7
    for j, (ratio, lift) in enumerate([(0.70, -0.1), (1, 0.25), (0.83, 0.66), (0.36, 0.92)]):
        for k in range(n):
            a = math.tau * (k + (j % 2) * 0.18) / n
            r = w * ratio * rand.uniform(0.85, 1.15)
            pts.append(
                (
                    x + r * math.cos(a) - j * w * 0.08,
                    y + r * 0.85 * math.sin(a),
                    z + h * (lift + rand.uniform(-0.07, 0.07)),
                )
            )
        for k in range(n):
            lo = 1 + j * n
            a = lo + k
            b = lo + (k + 1) % n
            if j == 0:
                faces.append((0, b, a))
            else:
                faces.extend([(a - n, b - n, b), (a - n, b, a)])
    tip = len(pts)
    pts.append((x - 0.25 * w, y, z + h))
    for k in range(n):
        faces.append((tip, 1 + 3 * n + k, 1 + 3 * n + (k + 1) % n))
    return geometry("Wind-pruned faceted oak crown", pts, faces, "Leaves")


def shoreline_details():
    # Shelter fittings tell the player what kind of work takes place here.
    x, y = -6, -4
    z = height(x, y)
    block("Chimney breast", (x - 2.4, y + 1, z + 2.43), (0.94, 1.06, 5.1), "Masonry")
    block("Drip course", (x - 2.4, y + 1, z + 5.01), (1.10, 1.2, 0.24), "Slate")
    for j in (-1, 1):
        lathe(
            "Chimney pot",
            x - 2.4 + j * 0.24,
            y + 1,
            z + 5.1,
            [(0.19, 0), (0.18, 0.44), (0.21, 0.54)],
            "RoofTiles",
            8,
        )
    # A seine drying between three stanchions. The weighted scallop of the mesh follows the top line.
    for x in (-16, -13, -10):
        z = height(x, -2)
        beam("Net drying post", (x, -2, z - 0.16), (x, -2, z + 2.5), 0.105)

    def stake(u, v):
        x = -16 + u * 6
        wave = abs(math.sin(2 * math.pi * u))
        return x, -2 + 0.13 * wave, height(x, -2) + 2.32 - 0.42 * wave - v * (1.35 - 0.25 * wave)

    for i in range(19):
        beam("Twine vertical", stake(i / 18, 0), stake(i / 18, 1), 0.024, "Reeds")
    for j in range(7):
        for i in range(12):
            beam("Netting", stake(i / 12, j / 6), stake((i + 1) / 12, j / 6), 0.026, "Reeds")
    for x, y in [(-12, -4), (-15.5, -4), (-37, -17), (33, 31)]:
        z = height(x, y)
        lathe(
            "Tarred barrel staves",
            x,
            y,
            z - 0.08,
            [(0.43, 0), (0.54, 0.24), (0.56, 0.75), (0.46, 1.03)],
            WOOD,
            10,
        )
        for h in (0.20, 0.79):
            lathe("Hoop iron", x, y, z + h, [(0.548, 0), (0.55, 0.07)], "BellMetal", 10)
    # Low cattle fences step with the ground at turns; openings follow the paths.
    for seq in [
        [(-22, -23), (-17, -25), (-12, -27), (-8, -26)],
        [(18, 17), (22, 18), (26, 19), (30, 19)],
        [(-49, 17), (-48, 21), (-46, 25)],
        [(0, 45), (-4, 44), (-8, 43)],
    ]:
        last = None
        for x, y in seq:
            p = (x, y, height(x, y) - 0.1)
            shaft("Fence post", p, (x - 0.04, y + 0.06, p[2] + 1.4), 0.17, 0.13, WOOD, 6)
            if last:
                for zz in (0.55, 1.03):
                    beam(
                        "Split chestnut rail",
                        (last[0], last[1], last[2] + zz),
                        (x, y, p[2] + zz),
                        0.10,
                        WOOD,
                    )
            last = p
    # Patches of salt thrift use opaque low-poly blossoms. No transparency sorting in stereo.
    petals = []
    faces = []
    leaves = []
    blades = []
    rand = random.Random(183)
    for cx, cy in [
        (-7, -13),
        (4, -8),
        (-35, -28),
        (-47, -22),
        (-12, 20),
        (39, -11),
        (34, 7),
        (-31, 30),
        (-39, 29),
        (20, 26),
        (11, 37),
        (-5, 42),
        (45, 18),
    ]:
        for _ in range(15):
            x = cx + rand.uniform(-2, 2)
            y = cy + rand.uniform(-1.5, 1.5)
            z = height(x, y) - 0.035
            h = rand.uniform(0.18, 0.51)
            i = len(petals)
            r = h * 0.22
            # A compact pink flower head on a visible stem, with lanceolate leaves at the base.
            for ring_level, (width, lift) in enumerate([(0.59, -0.035), (1.0, 0.008), (0.60, 0.060)]):
                for k in range(5):
                    a = math.tau * (k + ring_level * 0.1) / 5
                    petals.append((x + r * width * math.cos(a), y + r * width * math.sin(a), z + h + lift))
                if ring_level:
                    for k in range(5):
                        b = i + (ring_level - 1) * 5
                        other = (k + 1) % 5
                        faces.append((b + k, b + other, b + other + 5, b + k + 5))
            faces.append(tuple(i + 10 + k for k in range(5)))
            for dx, dy in [(0.018, 0), (0, 0.018)]:
                idx = len(leaves)
                leaves.extend(
                    [
                        (x - dx, y - dy, z),
                        (x + dx, y + dy, z),
                        (x + dx * 0.65, y + dy * 0.65, z + h),
                        (x - dx * 0.65, y - dy * 0.65, z + h),
                    ]
                )
                blades.extend([(idx, idx + 1, idx + 2, idx + 3), (idx + 3, idx + 2, idx + 1, idx)])
            a = rand.random() * math.tau
            for j in range(3):
                dx = math.cos(a + j * 2.1)
                dy = math.sin(a + j * 2.1)
                i = len(leaves)
                leaves.extend(
                    [
                        (x - 0.09 * dy, y + 0.09 * dx, z),
                        (x + 0.09 * dy, y - 0.09 * dx, z),
                        (x + dx * 0.23, y + dy * 0.23, z + h * 0.94),
                    ]
                )
                blades.extend([(i, i + 1, i + 2), (i + 2, i + 1, i)])
    geometry("Five-lobed sea thrift", petals, faces, "SeaThrift", "Flora")
    geometry("Thrift rosettes", leaves, blades, "Leaves", "Flora")


def greenery(region):
    for i, (x, y, h) in enumerate(TREES):
        z = height(x, y) - 0.11
        lean = -0.20 * h
        root = (x, y, z)
        crown = (x + lean, y, z + h * 0.69)
        shaft("Salt-bent trunk", root, crown, h * 0.10, h * 0.047, "Wood", 7)
        for j, angle in enumerate((0.3, 2.45, 4.48)):
            a = angle + math.sin(i) * 0.65
            ex = x + lean + 0.24 * h * math.cos(a)
            ey = y + 0.21 * h * math.sin(a)
            branch = (ex, ey, z + h * (0.65 + 0.035 * j))
            beam("Wind-cut branch", (x + lean * 0.61, y, z + h * 0.43), branch, h * 0.043)
            oak_crown(
                ex,
                ey,
                branch[2] - 0.055 * h,
                h * (0.32 + 0.035 * (j % 2)),
                h * (0.39 + 0.03 * (i % 2)),
                3 * i + j + 11,
            )
    rand = random.Random(421)
    for j in range(45):
        x, y = rand.uniform(-56, 55), rand.uniform(-55, 56)
        if min(abs(x) + abs(y + 14), abs(x - 27) + abs(y - 30)) < 12:
            continue
        if any((x - s["x"]) ** 2 + (y - s["y"]) ** 2 < 35 for s in region["stations"]):
            continue
        if any((x - a) ** 2 + (y - b) ** 2 < 30 for path in TRACKS for a, b in path):
            continue
        rad = rand.uniform(0.6, 1.7)
        stone("Heather-clad granite", x, y, height(x, y) - 0.12, rad, rad * 0.93, "MossRock", seed=j + 89)


def make(lib):
    r = next(r for r in rooms if r["key"] == KEY)
    paint()
    plaques(1, r)
    init(lib, 184)
    terrace()
    island_furniture(r)
    greenery(r)
    shoreline_details()
    marker("Spawn", 0, -14, 0.08)
    marker("Look", 0, -4, 1.4)
    finish(KEY)
