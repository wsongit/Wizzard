"""Rowan Hollow. One continuous floor, seven crown shapes and three working forest instruments."""

import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from atelier import (
    RES,
    init,
    finish,
    marker,
    block,
    shaft,
    lathe,
    geometry,
    collision,
    origins,
    palm_target,
)
from works_sets import line, ring
from sillwater_art import terrain, house
from engine_art import panel
from sets import arch
import forest_lod
from atelier import batches
from choir_wood import KEY, EARS, SITES, ROOT_TUNE
from underworks import rooms

SPAN = 52
HUT = (0, -12)
GATE = (0, 43)
LANES = [(HUT, xy) for pair in EARS.values() for xy in pair]
for name, pair in EARS.items():
    LANES += [(p, SITES[name]) for p in pair]
LANES.extend([(SITES["Rain"], GATE), (SITES["Root"], GATE), ((0, 22), GATE)])


def grade(x, y):
    h = (
        0.6
        + 2.35 * np.exp(-((x - 34) ** 2 + (y - 29) ** 2) / 481)
        + 1.95 * np.exp(-((x + 29) ** 2 + (y - 34) ** 2) / 253)
        + 0.64 * np.sin(x * 0.081) * np.cos(y * 0.072)
    )
    return h * np.clip((x * x + (y + 14) ** 2) / 105, 0, 1)


def distance(x, y, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = np.clip(((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy), 0, 1)
    return np.hypot(x - a[0] - dx * t, y - a[1] - dy * t)


def ground_art():
    root = RES / "Textures"
    rng = np.random.default_rng(1238)
    v, u = np.mgrid[:768, :768]
    x = (u + 0.5) * 104 / 768 - 52
    y = 52 - (v + 0.5) * 104 / 768
    path = np.minimum.reduce([distance(x, y, a, b) for a, b in LANES])
    grass = np.asarray(Image.open(root / "Grass.png").convert("RGB"), float)
    dirt = np.asarray(Image.open(root / "DirtPath.png").convert("RGB"), float)

    def tile(im, scale):
        return im[
            np.floor(-y * scale).astype(int) % im.shape[0],
            np.floor(x * scale).astype(int) % im.shape[1],
        ]

    moss = tile(grass, 5.3) * [0.79, 0.94, 0.78] + [6, 6, 3]
    tread = tile(dirt, 5.9) * [0.86, 0.89, 0.77] + [8, 6, 4]
    edge = 0.22 * np.sin(1.1 * x + 0.29 * y) + 0.27 * np.cos(y * 0.74 - x * 0.2)
    mix = np.clip((2.22 - path + edge) / 0.85, 0, 1)[..., None]
    light = (
        0.96
        + 0.07 * np.sin(0.24 * x + 0.16 * y) * np.cos(0.19 * y)
        + 0.035 * np.sin(0.55 * y - 0.31 * x)
    )
    img = (moss * (1 - mix) + tread * mix) * light[..., None]
    # Shade the tree bases into the floor paint; no piles of intersecting ground decals.
    for cx, cy, h, k in TREES:
        d2 = (x - cx + 0.62) ** 2 + (y - cy - 0.54) ** 2
        img *= (1 - 0.26 * np.exp(-d2 / (h * 0.84)))[..., None]
    Image.fromarray(np.uint8(np.clip(img, 0, 255))).save(root / (KEY + "Ground.png"))
    for i, c in enumerate(((80, 108, 51), (98, 128, 61), (69, 99, 53))):
        yy, xx = np.mgrid[:64, :64]
        shade = np.zeros_like(xx, dtype=float)
        for _ in range(84):
            dx = (xx - rng.uniform(0, 64) + 32) % 64 - 32
            dy = (yy - rng.uniform(0, 64) + 32) % 64 - 32
            shade += rng.uniform(-20, 24) * np.exp(
                -(dx**2 + dy**2) / rng.uniform(6, 27)
            )
        paint = np.array(c) + (shade + rng.normal(0, 2, (64, 64)))[..., None]
        Image.fromarray(np.uint8(np.clip(paint, 0, 255))).save(
            root / ("RowanLeaf" + str(i) + ".png")
        )
    font = lambda size: ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size
    )

    def pos(p):
        return (int(16 + 480 * (p[0] + 52) / 104), int(512 - 480 * (p[1] + 52) / 104))

    im = Image.new("RGB", (768, 544), "#e0d8ae")
    d = ImageDraw.Draw(im)
    d.rectangle((16, 32, 496, 512), fill="#c1c897", outline="#586a50", width=2)
    for cx, cy, h, k in TREES:
        px, py = pos((cx, cy))
        d.ellipse((px - 7, py - 6, px + 7, py + 6), fill="#a4b387")
    for a, b in LANES:
        d.line([pos(a), pos(b)], fill="#e4dcb8", width=6)
    colours = ["#47738a", "#855b42", "#935347"]
    for j, (fam, pair) in enumerate(EARS.items()):
        for i, (cx, cy) in enumerate(pair):
            px, py = pos((cx, cy))
            d.ellipse(
                (px - 8, py - 8, px + 8, py + 8),
                fill=colours[j],
                outline="#fbefc8",
                width=2,
            )
            d.text(
                (px + 9, py - 8), "DBW"[j] + str(i + 1), fill="#41372e", font=font(13)
            )
    for name, xy in list(SITES.items()) + [("Hut", HUT), ("Wicket", GATE)]:
        px, py = pos(xy)
        d.rectangle((px - 4, py - 4, px + 4, py + 4), fill="#54452f")
        if name in ("Hut", "Wicket"):
            d.text((px + 6, py - 18), name, font=font(15), fill="#514333")
    for j, (label, size) in enumerate(
        [
            ("ROWAN HOLLOW", 23),
            ("The sawyer’s linen", 17),
            ("WEST    /    EAST", 15),
            ("D1 · D2    Rain cups", 16),
            ("B1 · B2    Root horns", 16),
            ("W1 · W2   Wren horns", 16),
            ("Squares mark instruments.", 15),
            ("Activate each horn.", 15),
            ("Turn to face its call.", 15),
            ("Mark where the lines meet.", 15),
        ]
    ):
        d.text(
            (510, 42 + 34 * j),
            label,
            font=font(size),
            fill=colours[j - 3] if j in (3, 4, 5) else "#463c30",
        )
    im.save(root / (KEY + "Survey.png"))


def placements():
    rng = random.Random(6604)
    trees = []
    for _ in range(1300):
        if len(trees) >= 85:
            break
        x, y = rng.uniform(-49, 49), rng.uniform(-49, 49)
        if min(distance(x, y, a, b) for a, b in LANES) < 3.7:
            continue
        if any(
            math.hypot(x - a, y - b) < 6.0
            for a, b in [
                *SITES.values(),
                HUT,
                GATE,
                *[p for ps in EARS.values() for p in ps],
                (4, -9),
                (-3, -8),
            ]
        ):
            continue
        if any(math.hypot(x - a, y - b) < 5.3 for a, b, h, k in trees):
            continue
        trees.append((x, y, rng.uniform(5.4, 9.6), len(trees) % 7))
    return trees


TREES = placements()


def crown(x, y, z, w, h, rng, mat):
    pts = [(x, y, z - 0.16 * h)]
    faces = []
    n = 6
    rot = rng.random()
    for j, (r, lift) in enumerate(((0.82, 0.05), (1, 0.36), (0.55, 0.78))):
        for i in range(n):
            a = math.tau * (i / n + rot + j * 0.07)
            rr = r * w * rng.uniform(0.86, 1.13)
            pts.append(
                (
                    x + rr * math.cos(a),
                    y + 0.89 * rr * math.sin(a),
                    z + (lift + rng.uniform(-0.055, 0.055)) * h,
                )
            )
        for i in range(n):
            a = 1 + j * n + i
            b = 1 + j * n + (i + 1) % n
            faces.append((0, b, a) if j == 0 else (a - n, b - n, b, a))
    tip = len(pts)
    pts.append((x + 0.09 * w, y, z + h))
    faces.extend((1 + 2 * n + i, 1 + 2 * n + (i + 1) % n, tip) for i in range(n))
    geometry("Faceted rowan crown", pts, faces, mat, "Canopies")


def rowan(x, y, h, k, seed):
    rng = random.Random(seed)
    z = float(grade(x, y))
    bend = (k - 3) * 0.095
    trunk = 0.20 + h * 0.028
    lathe(
        "Furrowed woodland foot",
        x,
        y,
        z - 0.25,
        [(trunk * 1.65, 0), (trunk * 1.35, 0.43), (trunk, 0.94)],
        "Wood",
        7,
    )
    shaft(
        "Leaning bole",
        (x, y, z + 0.52),
        (x + bend, y + 0.08, z + h * 0.61),
        trunk,
        trunk * 0.57,
        "Wood",
        7,
    )
    for j in range(2 + k % 3):
        a = k * 0.71 + j * 2.14
        reach = h * (0.17 + 0.013 * (k % 4))
        xx = x + reach * math.cos(a)
        yy = y + reach * math.sin(a)
        lift = h * (0.54 + 0.07 * (j % 2))
        shaft(
            "Split fruiting branch",
            (x + bend * 0.7, y, z + h * 0.37),
            (xx, yy, z + lift + 0.30),
            trunk * 0.51,
            0.12,
            "Wood",
            6,
        )
        crown(
            xx,
            yy,
            z + lift,
            h * (0.20 + 0.019 * (k % 3)),
            h * 0.36,
            rng,
            "RowanLeaf" + str((k + j) % 3),
        )
    crown(
        x + bend,
        y + 0.08,
        z + h * 0.62,
        h * (0.21 + 0.014 * (k % 3)),
        h * (0.31 + 0.03 * (k % 4)),
        rng,
        "RowanLeaf" + str(k % 3),
    )


def horn(x, y, kind, side):
    z = float(grade(x, y))
    sgn = 1 if side else -1
    lathe(
        "Listening chair",
        x,
        y,
        z - 0.12,
        [(0.65, 0), (0.68, 0.20), (0.42, 0.35), (0.28, 1.22), (0.39, 1.30)],
        "MossRock",
        10,
    )
    axis = (sgn * 0.86, 0.24, 0.22)

    def pt(t):
        return (x + t * axis[0], y + t * axis[1], z + 1.46 + t * axis[2])

    mat = {"Rain": "BellMetal", "Root": "Wood", "Wren": "Brass"}[kind]
    # Recessed bell: inner rings and outer wall share the turned mouth, leaving a real sound well.
    from mathutils import Vector

    a = Vector(axis).normalized()
    u = a.cross(Vector((0, 0, 1))).normalized()
    v = a.cross(u)
    rings = [
        (-0.52, 0.095),
        (-0.04, 0.14),
        (0.30, 0.22),
        (0.62, 0.43),
        (0.87, 0.68),
        (0.9, 0.59),
        (0.60, 0.35),
        (0.20, 0.13),
    ]
    vertices = [
        tuple(
            Vector(pt(t))
            + r * (u * math.cos(i * math.tau / 12) + v * math.sin(i * math.tau / 12))
        )
        for t, r in rings
        for i in range(12)
    ]
    faces = [
        (
            j * 12 + i,
            j * 12 + (i + 1) % 12,
            (j + 1) * 12 + (i + 1) % 12,
            (j + 1) * 12 + i,
        )
        for j in range(len(rings) - 1)
        for i in range(12)
    ]
    faces.append(tuple(range(len(vertices) - 12, len(vertices))))
    geometry("Flared listening trumpet", vertices, faces, mat)
    for t, rad in ((0.04, 0.17), (0.55, 0.40), (0.85, 0.69)):
        rim = [
            tuple(
                Vector(pt(t + offset))
                + radius
                * (u * math.cos(i * math.tau / 12) + v * math.sin(i * math.tau / 12))
            )
            for offset, radius in (
                (-0.024, rad - 0.04),
                (-0.024, rad),
                (0.024, rad),
                (0.024, rad - 0.04),
            )
            for i in range(12)
        ]
        quads = [
            (
                j * 12 + i,
                j * 12 + (i + 1) % 12,
                ((j + 1) % 4) * 12 + (i + 1) % 12,
                ((j + 1) % 4) * 12 + i,
            )
            for j in range(4)
            for i in range(12)
        ]
        geometry("Rolled brass lip", rim, quads, "Brass")
    shaft("Horn diaphragm", pt(0.21), pt(0.22), 0.13, 0.13, "Slate", 12)
    for i in range(3):
        off = -0.19 + i * 0.19
        line(
            "Instrument reed",
            (x + off, y - 0.35, z + 0.73),
            (x + off, y - 0.34, z + 1.14 + i * 0.07),
            0.03,
            mat,
        )
    block("Brass maker’s tablet", (x, y - 0.38, z + 0.65), (1.04, 0.1, 0.37), "Brass")


def spring(x, y):
    z = float(grade(x, y))
    for dx in (-4, 4):
        shaft(
            "Spring harp pier",
            (x + dx, y + 1.0, z - 0.3),
            (x + dx * 0.84, y + 1.0, z + 4.8),
            0.56,
            0.37,
            "MossRock",
            8,
        )
    line(
        "Harp lintel",
        (x - 3.4, y + 1, z + 4.6),
        (x + 3.4, y + 1, z + 4.85),
        0.25,
        "Wood",
    )
    for k in range(8):
        dx = -2.51 + k * 0.72
        shaft(
            "Water-struck bronze tongue",
            (x + dx, y + 1, z + 2.2 + 0.13 * k),
            (x + dx, y + 1, z + 4.52 + 0.04 * k),
            0.056,
            0.052,
            "Brass",
            6,
        )
    for id, xx, h in (
        ("RidgeTrough", x - 2, z + 2.40),
        ("SillTrough", x + 3, z + 1.67),
    ):
        lathe(
            "Sluice pintle",
            xx,
            y,
            z - 0.16,
            [(0.69, 0), (0.70, 0.23), (0.34, 0.43), (0.32, h - z + 0.13)],
            "Masonry",
            8,
        )
        origins[id] = (xx, y, h)
        heading = math.radians(120 if id == "RidgeTrough" else -120)

        def offset(along, across, lift):
            return (
                xx + along * math.cos(heading) - across * math.sin(heading),
                y + along * math.sin(heading) + across * math.cos(heading),
                h + lift,
            )

        block("Open trough bed", (xx, y, h), (5.04, 0.65, 0.13), "Wood", id, heading)
        for d in (-0.33, 0.33):
            block(
                "Trough side rail",
                offset(0, d, 0.14),
                (5.12, 0.11, 0.32),
                "Wood",
                id,
                heading,
            )
        for along in (-2.18, -1.05, 1.05, 2.18):
            block(
                "Copper trough strap",
                offset(along, 0, -0.02),
                (0.092, 0.84, 0.16),
                "BellMetal",
                id,
                heading,
            )
    # With both troughs on their carved marks their lips meet at the first fall.
    group = "SpringStream"
    for xa, xb, lift, width in ((-4.48, 0.48, 2.49, 0.39), (0.52, 5.48, 1.76, 0.38)):
        block(
            "Water in both runs",
            (x + (xa + xb) * 0.5, y, z + lift),
            (xb - xa, width, 0.045),
            "ParishWater",
            group,
        )
    for dx, high, low in ((0.50, 2.50, 1.78), (5.51, 1.76, 0.54)):
        block(
            "Falling water",
            (x + dx, y, z + (high + low) * 0.5),
            (0.082, 0.37, high - low),
            "ParishWater",
            group,
        )
    for dx, high in ((-4.62, 2.56), (5.52, 0.49)):
        lathe(
            "Carved catch bowl",
            x + dx,
            y,
            z - 0.21,
            [
                (0.80, 0),
                (0.71, 0.29),
                (0.82, high - 0.04),
                (0.70, high + 0.08),
                (0.57, high + 0.08),
                (0.49, high - 0.15),
            ],
            "MossRock",
            10,
        )
    lathe(
        "Spring crown",
        x - 4.62,
        y,
        z + 2.21,
        [(0.52, 0), (0.55, 0.15), (0.42, 0.22)],
        "ParishWater",
        10,
    )
    line(
        "Copper headrace",
        (x - 4.64, y, z + 2.62),
        (x - 4.44, y, z + 2.58),
        0.17,
        "BellMetal",
    )
    for i in range(8):
        dx = -2.51 + i * 0.72
        line(
            "Clapper linkage",
            (x + 5.5, y, z + 0.61),
            (x + dx, y + 1, z + 2.2 + 0.13 * i),
            0.024,
            "Brass",
        )
        lathe(
            "Tuned bronze cup",
            x + dx,
            y + 1,
            z + 2 + 0.13 * i,
            [(0.16, 0), (0.18, 0.08), (0.095, 0.20)],
            "BellMetal",
            8,
        )
    wheel = (x + 5.5, y, z + 0.87)
    ring("Water harp paddle wheel", wheel, 0.56, 0.065, "Wood", "y", "Set", 12)
    for tooth in range(8):
        co, sn = math.cos(tooth * math.tau / 8), math.sin(tooth * math.tau / 8)
        line(
            "Wet paddle spoke",
            wheel,
            (wheel[0] + 0.54 * co, y, wheel[2] + 0.54 * sn),
            0.057,
            "Wood",
        )
    for k in range(2):
        block(
            "Watercourse gauge",
            (x - 2 + k * 5, y - 0.58, z + 1.12),
            (0.73, 0.16, 0.52),
            "Slate",
        )
        for d in range(2 - k):
            block(
                "Carved water mark",
                (x - 2 + k * 5 + (d - 0.4) * 0.15, y - 0.68, z + 1.15),
                (0.055, 0.04, 0.32),
                "Brass",
            )
    lathe(
        "Spill valve",
        x,
        y - 3,
        float(grade(x, y - 3)) - 0.09,
        [(0.56, 0), (0.57, 0.18), (0.19, 0.39), (0.2, 1.0)],
        "Masonry",
        8,
    )
    ring(
        "Cast spill wheel",
        (x, y - 3, float(grade(x, y - 3)) + 1.03),
        0.39,
        0.06,
        "BellMetal",
        "z",
        "Set",
    )


def beech(x, y):
    z = float(grade(x, y))
    for i, (dx, h) in enumerate(((-3, 2.35), (0, 1.92), (3, 1.54))):
        xx = x + dx
        zz = float(grade(xx, y))
        lathe(
            "Hollow log",
            xx,
            y,
            zz - 0.10,
            [
                (0.70, 0),
                (0.76, 0.25),
                (0.56, h - 0.28),
                (0.52, h),
                (0.42, h + 0.07),
                (0.35, h - 0.20),
            ],
            "Wood",
            10,
        )
        block(
            "Resonator slit",
            (xx, y - 0.54, zz + h * 0.56),
            (0.15, 0.10, h * 0.63),
            "Slate",
        )
        for k in range(i + 1):
            block(
                "Pitch notch",
                (xx - 0.18 + k * 0.16, y - 0.55, zz + 1.0),
                (0.055, 0.08, 0.22),
                "Brass",
            )
        palm_target(("Long", "Middle", "Short")[i], xx, y - 0.69, zz + 1.25, 0.24)
    for side in (-1, 1):
        shaft(
            "Cathedral beech",
            (x + side * 2, y + 2, z - 0.28),
            (x + side * 0.68, y + 2, z + 7.7),
            0.8,
            0.33,
            "Wood",
            9,
        )
        crown(
            x + side * 2.1,
            y + 2,
            z + 6.3,
            3.9,
            4.0,
            random.Random(42 + side),
            "RowanLeaf1",
        )
    block(
        "Beech pilgrim ribbon",
        (x, y + 1.5, z + 5.25),
        (0.40, 0.15, 2.6),
        "Amber",
        "BeechRibbon",
    )
    for i in range(4):
        xx = x - 2.61 + i * 0.39
        zz = float(grade(x - 2, y - 4))
        block("Notched stave", (xx, y - 4, zz + 0.78), (0.32, 0.48, 1.59), "Wood")
        block(
            "Incised knock",
            (xx, y - 4.25, zz + 1.31),
            (0.14, 0.035, 0.07 * (1 + int(ROOT_TUNE[i]))),
            "Brass",
        )


def loft(x, y):
    z = float(grade(x, y))
    for xx in (-3.0, 3.0):
        for yy in (0, 3.3):
            block("Loft post", (x + xx, y + yy, z + 2.29), (0.32, 0.35, 5.0), "Wood")
    for i in range(8):
        block(
            "Lapped weatherboard",
            (x, y + 3.3, z + 0.4 + i * 0.50),
            (6.25, 0.33, 0.53),
            "Wood",
        )
    for s in (-1, 1):
        pts = [
            (x + s * 3.7, y - 0.65, z + 4.65),
            (x + s * 3.7, y + 4.2, z + 4.65),
            (x, y + 4.2, z + 6.41),
            (x, y - 0.65, z + 6.41),
        ]
        pts += [(px, py, pz - 0.17) for px, py, pz in pts]
        faces = [
            (0, 1, 2, 3),
            (7, 6, 5, 4),
            (4, 5, 1, 0),
            (5, 6, 2, 1),
            (6, 7, 3, 2),
            (7, 4, 0, 3),
        ]
        geometry(
            "Kite loft roof",
            pts,
            faces if s > 0 else [tuple(reversed(f)) for f in faces],
            "RoofSlate",
        )
        for yy in (-0.60, 3.98):
            line(
                "Gable verge",
                (x + s * 3.7, y + yy, z + 4.57),
                (x, y + yy, z + 6.35),
                0.14,
                "Wood",
            )
            line(
                "Loft knee brace",
                (x + s * 3, y + yy + 0.34, z + 3.41),
                (x + s * 1.8, y + yy + 0.34, z + 4.60),
                0.12,
                "Wood",
            )
    for yy in (-0.26, 3.50):
        line(
            "Gable tie",
            (x - 3.28, y + yy, z + 4.56),
            (x + 3.28, y + yy, z + 4.56),
            0.14,
            "Wood",
        )
        line("King post", (x, y + yy, z + 4.52), (x, y + yy, z + 6.28), 0.13, "Wood")
    line("Loft ridge", (x, y - 0.71, z + 6.40), (x, y + 4.25, z + 6.4), 0.17, "Wood")
    beam = "LoftBeam"
    origins[beam] = (x, y, z + 2.08)
    shaft(
        "Weigh beam",
        (x - 2.16, y, z + 2.08),
        (x + 2.16, y, z + 2.08),
        0.12,
        0.12,
        "Wood",
        8,
        beam,
    )
    for side in (-1, 1):
        for dx in (-0.36, 0.36):
            line(
                "Basket cord",
                (x + side * 1.69, y, z + 2.08),
                (x + side * 1.69 + dx, y, z + 1.44),
                0.037,
                "Brass",
                beam,
            )
        block(
            "Weigh pan",
            (x + side * 1.69, y, z + 1.4),
            (0.86, 0.75, 0.1),
            "BellMetal",
            beam,
        )
    lathe(
        "Scale fulcrum",
        x,
        y,
        z - 0.13,
        [(0.63, 0), (0.64, 0.20), (0.25, 0.65), (0.14, 2.23)],
        "Masonry",
        8,
    )
    for i in range(3):
        group = "Bird" + str(i)
        bx = x + 1.69
        by = y
        bz = z + 1.46
        lathe(
            "Clay lapwing",
            bx,
            by,
            bz,
            [(0.19, 0), (0.32 + i * 0.035, 0.18), (0.24, 0.41), (0.12, 0.48)],
            ("HousePlaster", "Brass", "Slate")[i],
            9,
            group,
        )
        glaze = ("HousePlaster", "Brass", "Slate")[i]
        lathe(
            "Glazed bird head",
            bx,
            by - 0.17,
            bz + 0.38,
            [(0.09, 0), (0.20, 0.09), (0.19, 0.25), (0.095, 0.32)],
            glaze,
            9,
            group,
        )
        shaft(
            "Whistle beak",
            (bx, by - 0.29, bz + 0.52),
            (bx, by - 0.57, bz + 0.47),
            0.095,
            0.01,
            "Amber",
            7,
            group,
        )
        for side in (-1, 1):
            line(
                "Painted wing",
                (bx + side * 0.25, by - 0.14, bz + 0.32),
                (bx + side * 0.16, by + 0.33, bz + 0.28),
                0.10,
                "SeaGlass",
                group,
            )
            shaft(
                "Bird eye",
                (bx + side * 0.132, by - 0.27, bz + 0.57),
                (bx + side * 0.147, by - 0.29, bz + 0.57),
                0.037,
                0.032,
                "CoalCloth",
                7,
                group,
            )
        shaft(
            "Feathered whistle tail",
            (bx, by + 0.13, bz + 0.21),
            (bx + 0.04 * i, by + 0.55, bz + 0.49),
            0.16,
            0.057,
            glaze,
            7,
            group,
        )
        if i == 2:
            shaft(
                "Mended brass tip",
                (bx + 0.08, by + 0.48, bz + 0.45),
                (bx + 0.10, by + 0.65, bz + 0.55),
                0.081,
                0.052,
                "Brass",
                7,
                group,
            )
    for xx in (-2, 2):
        block("Bellows bench", (x + xx, y - 0.66, z + 0.57), (1.17, 0.98, 1.17), "Wood")
    marker("RailStart", x - 2.6, y - 0.65, z + 1.39)
    marker("RailEnd", x - 1.35, y - 0.65, z + 1.39)
    line(
        "Notched poise track",
        (x - 2.7, y - 0.65, z + 1.35),
        (x - 1.25, y - 0.65, z + 1.35),
        0.075,
        "Brass",
    )
    for notch in range(4):
        block(
            "Poise notch",
            (x - 2.45 + 0.32 * notch, y - 0.80, z + 1.29),
            (0.05, 0.18, 0.11),
            "HousePlaster",
        )
    block(
        "Traveller weight",
        (x - 2.77, y - 0.65, z + 1.43),
        (0.22, 0.42, 0.35),
        "BellMetal",
        "Poise",
    )
    for i in range(5):
        block(
            "Bellows pleat",
            (x + 2, y - 0.66, z + 1.18 + 0.048 * i),
            (0.95 - 0.036 * i, 0.71, 0.038),
            "Slate",
        )
    block(
        "Dedication pennant",
        (x, y - 0.42, z + 4.25),
        (1.45, 0.11, 0.71),
        "Amber",
        "WrenBanner",
    )


def linn(x, y, z):
    def form(name, sections, material, sides=10):
        points = [
            (
                x + cx + rx * math.cos(i * math.tau / sides),
                y + cy + ry * math.sin(i * math.tau / sides),
                z + lift,
            )
            for cx, cy, lift, rx, ry in sections
            for i in range(sides)
        ]
        faces = [
            (
                j * sides + i,
                j * sides + (i + 1) % sides,
                (j + 1) * sides + (i + 1) % sides,
                (j + 1) * sides + i,
            )
            for j in range(len(sections) - 1)
            for i in range(sides)
        ]
        faces += [
            tuple(reversed(range(sides))),
            tuple(range(len(points) - sides, len(points))),
        ]
        geometry(name, points, faces, material)

    for side in (-1, 1):
        block(
            "Cobbled boot",
            (x + side * 0.16, y - 0.055, z + 0.13),
            (0.24, 0.44, 0.27),
            "Wood",
        )
    form(
        "Full skirt",
        [(0, 0, 0.18, 0.43, 0.31), (0, 0, 0.48, 0.40, 0.29), (0, 0, 0.98, 0.24, 0.18)],
        "FernCloth",
    )
    form(
        "Sawyer’s jacket",
        [
            (0, 0, 0.91, 0.29, 0.20),
            (0, 0, 1.19, 0.35, 0.24),
            (0, 0, 1.42, 0.33, 0.20),
            (0, 0, 1.51, 0.14, 0.12),
        ],
        "NightCloth",
    )
    block("Leather apron", (x, y - 0.206, z + 0.83), (0.46, 0.066, 0.82), "Wood")
    for dx in (-0.17, 0.17):
        line(
            "Apron strap",
            (x + dx, y - 0.18, z + 1.43),
            (x + dx * 0.8, y - 0.25, z + 1.18),
            0.026,
            "Amber",
        )
    form(
        "Linn’s cheeks",
        [
            (0, -0.016, 1.48, 0.12, 0.12),
            (0, -0.02, 1.55, 0.188, 0.16),
            (0, 0, 1.78, 0.21, 0.196),
            (0, 0.015, 1.88, 0.15, 0.14),
        ],
        "Skin",
    )
    form(
        "Wool kerchief",
        [
            (0, 0.047, 1.72, 0.22, 0.168),
            (0, 0.037, 1.84, 0.242, 0.213),
            (0, 0.05, 1.97, 0.16, 0.15),
            (-0.043, 0.08, 2.01, 0.08, 0.065),
        ],
        "FernCloth",
    )
    for side in (-1, 1):
        block(
            "Linn’s brow",
            (x + side * 0.08, y - 0.174, z + 1.737),
            (0.066, 0.04, 0.025),
            "Wood",
        )
        block(
            "Linn’s eye",
            (x + side * 0.08, y - 0.177, z + 1.696),
            (0.041, 0.037, 0.035),
            "CoalCloth",
        )
        start = (x + side * 0.28, y, z + 1.35)
        elbow = (x + side * 0.40, y - 0.12, z + 1.08)
        hand = (x + side * 0.32, y - 0.33, z + 1.15)
        shaft("Sleeve", start, elbow, 0.13, 0.104, "NightCloth", 8)
        shaft("Rolled cuff", elbow, hand, 0.096, 0.08, "FernCloth", 8)
        shaft(
            "Carver’s hand",
            hand,
            (hand[0] - 0.04 * side, hand[1] - 0.11, hand[2]),
            0.084,
            0.061,
            "Skin",
            8,
        )
    shaft(
        "Sharpened quill",
        (x + 0.31, y - 0.42, z + 1.14),
        (x + 0.40, y - 0.45, z + 1.48),
        0.021,
        0.01,
        "HousePlaster",
        6,
    )
    shaft(
        "Nose",
        (x, y - 0.159, z + 1.675),
        (x, y - 0.227, z + 1.64),
        0.050,
        0.026,
        "Skin",
        7,
    )
    for dx in (-0.26, 0.25):
        line(
            "Reading glasses arm",
            (x + dx * 0.47, y - 0.193, z + 1.702),
            (x + dx * 0.78, y + 0.005, z + 1.70),
            0.012,
            "Brass",
        )
        ring(
            "Reading glasses",
            (x + dx * 0.33, y - 0.191, z + 1.693),
            0.061,
            0.010,
            "Brass",
            "y",
            "Set",
            9,
        )


def make(lib):
    r = next(r for r in rooms if r["key"] == KEY)
    ground_art()
    from rowan_letter import make as embroider_linen

    embroider_linen()
    forest_lod.atlas()
    init(lib, 6887)
    terrain(KEY, SPAN, grade, 2)
    for i, (x, y, h, k) in enumerate(TREES):
        core, leaves = len(batches["Set"]), len(batches["Canopies"])
        rowan(x, y, h, k, 1500 + i)
        parts = [(o, True) for o in batches["Set"][core:]] + [
            (o, False) for o in batches["Canopies"][leaves:]
        ]
        del batches["Set"][core:], batches["Canopies"][leaves:]
        forest_lod.collect(parts, x, y)
    forest_lod.distant()
    # Broad ridges enclose the forest beyond the continuous collision boundary.
    rng = random.Random(484)
    p = []
    for i in range(68):
        a = i * math.tau / 68
        rad = 70 + 4 * math.sin(6 * a)
        p.append(
            (
                rad * math.cos(a),
                rad * math.sin(a),
                7.2 + 4 * math.sin(5 * a) + rng.uniform(0, 3),
            )
        )
    for i, a in enumerate(p):
        b = p[(i + 1) % len(p)]
        geometry(
            "Timbered ridge",
            [(a[0], a[1], -2), (b[0], b[1], -2), b, a],
            [(3, 2, 1, 0)],
            "MossRock",
            "Backdrop",
        )
    house(-7, -6, 7, 6, 3.9, 0, height=grade)
    linn(-4.15, -11.22, float(grade(-4.15, -11.22)))
    spring(*SITES["Rain"])
    beech(*SITES["Root"])
    loft(*SITES["Wren"])
    for fam, (x, y) in SITES.items():
        marker("Source" + fam, x, y, float(grade(x, y)) + 3.25)
    for fam, pair in EARS.items():
        for i, (x, y) in enumerate(pair):
            horn(x, y, fam, i)
    for s in r["stations"]:
        x, y = s["x"], s["y"]
        z = float(grade(x, y))
        n = s["id"][2:]
        if n == "Gate":
            arch(x, y, z - 0.05, 3.4, 4.0, "MossRock", "Wood")
        if n in ("Plan", "Linn"):
            block("Survey cabinet", (x, y, z + 0.56), (2.1, 0.95, 1.17), "Wood")
            if n == "Plan":
                block(
                    "Linen stretcher",
                    (x, y + 0.14, z + 2.02),
                    (2.84, 0.16, 2.04),
                    "Wood",
                )
                panel(
                    "Linn’s map",
                    x,
                    y + 0.04,
                    z + 1.08,
                    2.69,
                    1.90,
                    KEY + "Survey",
                    "Survey",
                )
            else:
                block(
                    "Field notebook",
                    (x, y, z + 1.21),
                    (1.1, 0.61, 0.10),
                    "HousePlaster",
                )
        marker(s["id"], x, y - (1.32 if n in ("Slide", "Breath") else 0.82), z + 1.32)
        marker(s["camp"], x, y - 2.29, float(grade(x, y - 2.29)) + 0.09)
    for n, x, y in (
        ("MapSW", -SPAN, -SPAN),
        ("MapSE", SPAN, -SPAN),
        ("MapNW", -SPAN, SPAN),
    ):
        marker(n, x, y, 0)
    marker("Spawn", 0, -14, 0.1)
    marker("Look", 0, 5, 1.45)
    finish(KEY, sky_key="RootChoir")
