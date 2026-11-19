"""Build an alder floodplain, four salvage sites, Willa's fork and the survey on her ferry board."""

import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from atelier import RES, init, finish, marker, block, shaft, lathe, geometry, collision, model
from works_sets import ring, line
from engine_art import panel
from sets import arch
from sillwater_art import terrain, house
from wrenfall import oak_crown
from underworks import rooms
from drift_fen import KEY, ITEMS

SPAN = 56
WOOD = "TarredOak"
STONE = "Masonry"
BRASS = "Brass"
LANES = [
    ((0, -14), (-36, -26)),
    ((0, -14), (39, -17)),
    ((-36, -26), (-22, 4)),
    ((-22, 4), (-38, 32)),
    ((39, -17), (20, 9)),
    ((20, 9), (31, 37)),
    ((-38, 32), (31, 37)),
    ((-22, 4), (20, 9)),
]


def stream(x):
    return 6.5 + 3.4 * np.sin(x / 15)


def grade(x, y):
    delta = abs(y - stream(x))
    shelf = np.clip((delta - 2.2) / 8, 0, 1)
    hill = (
        1.1
        + 0.44 * np.cos(x / 14) * np.sin(y / 13)
        + 2.2 * np.exp(-((x + 34) ** 2 + (y - 35) ** 2) / 290)
        + 1.4 * np.exp(-((x - 32) ** 2 + (y - 39) ** 2) / 230)
    )
    h = 0.12 + hill * shelf * shelf * (3 - 2 * shelf)
    # Gravel fords stay level with both riverbanks.
    for bx in (-22, 20):
        h = h + 0.54 * np.clip(1 - abs(x - bx) / 3.7, 0, 1) * (1 - shelf)
    return h * np.clip((x * x + (y + 14) ** 2) / 64, 0, 1)


def tiles(n, x, y):
    t = np.asarray(Image.open(RES / "Textures" / (n + ".png")).convert("RGB"), float)
    return t[np.floor(y * 6).astype(int) % len(t), np.floor(x * 6).astype(int) % t.shape[1]]


def field(key, r):
    n = 768
    yy, xx = np.mgrid[:n, :n]
    x = (xx + 0.5) * 112 / n - 56
    y = 56 - (yy + 0.5) * 112 / n
    water = abs(y - stream(x))
    path = np.full(x.shape, 1e3)
    for (ax, ay), (bx, by) in LANES:
        dx, dy = bx - ax, by - ay
        t = np.clip(((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy), 0, 1)
        path = np.minimum(path, np.hypot(x - ax - t * dx, y - ay - t * dy))
    g = tiles("Grass", x, y) * 0.70 + [26, 36, 12]
    mud = tiles("DirtPath", x, y) * 0.69 + [43, 39, 26]
    road = np.maximum(np.clip((2.1 - path) * 1.18, 0, 1), np.clip((6.5 - water) / 3, 0, 0.88))[
        :, :, None
    ]
    im = Image.fromarray(np.uint8(np.clip(g * (1 - road) + mud * road, 0, 255)))
    im.save(RES / "Textures" / (key + "Ground.png"))
    paper = Image.new("RGB", (768, 544), "#e8d8ae")
    d = ImageDraw.Draw(paper)
    h = grade(x, y)
    ink = np.zeros((*h.shape, 3)) + [195, 199, 147]
    ink -= h[:, :, None] * [5, 4, 7]
    ink[(h % 0.38 < 0.03) & (water > 5)] = [156, 160, 116]
    ink[path < 1.7] = [185, 158, 113]
    ink[water < 3.1] = [108, 150, 150]
    for bx in (-22, 20):
        ink[(water < 4) & (abs(x - bx) < 2)] = [174, 157, 126]
    paper.paste(Image.fromarray(ink.astype("uint8")).resize((480, 480)), (16, 32))
    font = lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", n)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)

    def xy(a, b):
        return 16 + (a + 56) * 480 / 112, 512 - (b + 56) * 480 / 112

    for i, (a, b, label) in enumerate(
        [(it[2], it[3], it[4].title()) for it in ITEMS] + [(0, -14, "Willa’s ferry")], 1
    ):
        px, py = xy(a, b)
        d.ellipse((px - 10, py - 10, px + 10, py + 10), fill="#725b40", outline="#f4e8c3", width=2)
        d.text((px, py), str(i), font=font(13), fill="#fff2ce", anchor="mm")
        d.text((515, 145 + i * 31), f"{i}   {label}", font=small, fill="#403b2e")
    d.text((510, 37), "DRIFT FEN", font=font(27), fill="#405c51")
    d.text((512, 83), "Willa’s soundings", font=font(21), fill="#544533")
    for i, t in enumerate(
        (
            "N ↑    Alder stream",
            "Gravel fords cross it",
            "at two marked narrows.",
            "Ring the fork. Follow",
            "the strongest reply.",
        )
    ):
        d.text((515, 342 + 26 * i), t, font=small, fill="#554c37")
    paper.save(RES / "Textures" / (key + "Survey.png"))
    art = Image.new("RGB", (384, 256), "#284743")
    badges = (
        ("#815337", "#f0ce81", "THE BREAD OVEN"),
        ("#7d4949", "#f4d6aa", "PELLA’S WARD"),
        ("#36585a", "#f3dd9e", "PENNY SCHOOL"),
        ("#415369", "#f1d695", "WESTERN SIGNAL"),
    )
    for i, (bg, ink, word) in enumerate(badges):
        tile = Image.new("RGB", (192, 128), bg)
        d = ImageDraw.Draw(tile)
        d.rounded_rectangle((3, 3, 188, 124), 8, outline=ink, width=3)
        d.rounded_rectangle((8, 8, 183, 119), 6, outline=ink, width=1)
        if i == 0:
            for dx in (-24, 0, 24):
                d.line((96, 77, 96 + dx, 25), fill=ink, width=3)
                for j in range(4):
                    cx = 96 + dx * (j + 1) / 5
                    cy = 69 - j * 10
                    d.polygon(((cx, cy), (cx - 10, cy - 13), (cx - 2, cy - 10)), fill=ink)
                    d.polygon(((cx, cy), (cx + 10, cy - 13), (cx + 3, cy - 10)), fill=ink)
        elif i == 1:
            d.arc((58, 18, 133, 72), 0, 180, fill=ink, width=6)
            d.line((59, 46, 133, 46, 127, 35, 118, 28), fill=ink, width=3)
            d.arc((58, 49, 133, 86), 24, 156, fill=ink, width=3)
            d.ellipse((107, 29, 118, 39), fill=ink)
        elif i == 2:
            for j in range(5):
                d.line((51, 37 + 7 * j, 141, 37 + 7 * j), fill=ink, width=1)
            for cx, cy in ((74, 64), (96, 56), (118, 49)):
                d.ellipse((cx - 5, cy - 3, cx + 4, cy + 4), fill=ink)
                d.line((cx + 4, cy, cx + 4, cy - 22), fill=ink, width=3)
        else:
            d.polygon(((76, 75), (84, 42), (107, 42), (115, 75)), outline=ink, width=3)
            d.polygon(((76, 40), (96, 22), (116, 40)), fill=ink)
            d.rectangle((89, 44, 103, 57), fill=ink)
            for dx in (-1, 1):
                for j in range(3):
                    d.line((96 + 29 * dx, 45 + j * 5, 96 + 47 * dx, 37 + j * 13), fill=ink, width=2)
        d.text((96, 98), word, font=font(15), anchor="mm", fill=ink)
        art.paste(tile, (i % 2 * 192, i // 2 * 128))
    art.save(RES / "Textures/DriftFenTrades.png")
    rng = np.random.default_rng(9014)
    for name, base in (("FenShale", (107, 111, 80)), ("FenFells", (105, 119, 133))):
        grain = np.zeros((64, 64))
        for dim, weight in ((4, 10), (8, 5), (24, 3), (64, 2)):
            samples = Image.fromarray(np.uint8(rng.random((dim, dim)) * 255))
            grain += weight * (
                np.asarray(samples.resize((64, 64), Image.Resampling.BICUBIC), float) / 127.5 - 1
            )
        color = np.array(base)[None, None, :] + grain[:, :, None] * [1, 1.08, 0.85]
        Image.fromarray(np.uint8(np.clip(color, 0, 255))).save(RES / "Textures" / (name + ".png"))


def escarpment():
    # Two uninterrupted folds make a low river valley with recognisable silhouettes from each ford.
    for far in (False, True):
        rows = []
        faces = []
        n = 76
        for i in range(n):
            a = math.tau * i / n
            crest = 11.5 + 3.7 * math.cos(3 * a) + 1.8 * math.sin(8 * a) + 1.5 * math.sin(17 * a)
            if far:
                crest = (
                    26.0 + 7.4 * math.sin(2 * a + 0.55) + 4.2 * math.sin(5 * a) + 2.1 * math.cos(13 * a)
                )
            rr = (105 if far else 77) + 4.1 * math.cos(6 * a + 0.5)
            for rad, lift, skew in (
                (rr - 6, -4, 0),
                (rr - 2, crest * 0.62, -0.008),
                (rr, crest, 0.007),
                (rr + 9, crest * 0.73, 0.012),
            ):
                rows.append((rad * math.cos(a + skew), rad * math.sin(a + skew), lift))
            for j in range(3):
                a1 = i * 4 + j
                b = ((i + 1) % n) * 4 + j
                faces.extend(((a1, b + 1, b), (a1, a1 + 1, b + 1)))
        geometry(
            "Outer fells" if far else "River cut",
            rows,
            faces,
            "FenFells" if far else "FenShale",
            "Horizon",
        )
    rng = random.Random(1029)
    for i in range(58):
        x = rng.uniform(-54, 54)
        if min(abs(x - 20), abs(x + 22)) < 3.8:
            continue
        y = float(stream(x)) + rng.choice((-1, 1)) * rng.uniform(3.25, 6.3)
        z = float(grade(x, y))
        verts = []
        faces = []
        for j in range(9):
            dx, dy = rng.uniform(-0.48, 0.48), rng.uniform(-0.40, 0.40)
            h = rng.uniform(0.42, 0.91)
            v = len(verts)
            verts.extend(
                (
                    (x + dx - 0.061, y + dy, z - 0.12),
                    (x + dx + 0.061, y + dy, z - 0.12),
                    (x + dx * 1.41 + 0.06, y + dy * 1.28, z + h),
                )
            )
            faces.append((v, v + 1, v + 2))
        geometry("Bankside sedge", verts, faces, "Moss", "Banks")
        if i % 4 == 0:
            xx = x + 0.19
            lathe("Bulrush stalk", xx, y, z - 0.06, [(0.035, 0), (0.026, 1.12)], "Moss", 5, "Banks")
            lathe(
                "Bulrush head",
                xx,
                y,
                z + 0.90,
                [(0.03, 0), (0.085, 0.07), (0.070, 0.28), (0.024, 0.34)],
                "Wood",
                6,
                "Banks",
            )


def alder(x, y, h, seed):
    z = float(grade(x, y))
    rng = random.Random(seed)
    dest = (x + rng.uniform(-0.38, 0.38), y + rng.uniform(-0.38, 0.38), z + h * 0.65)
    shaft("Alder bole", (x, y, z - 0.16), dest, h * 0.064, h * 0.028, WOOD, 7)
    for i in range(3):
        a = math.tau * i / 3 + rng.uniform(-0.45, 0.45)
        dx, dy = math.cos(a) * h * 0.22, math.sin(a) * h * 0.22
        tip = (x + dx, y + dy, z + h * (0.64 + 0.09 * i))
        line("Forked bough", (x, y, z + h * 0.39), tip, h * 0.042, "Wood")
        oak_crown(tip[0], tip[1], tip[2], h * 0.28, h * 0.35, seed + i * 11)
    collision("Alder root core", x, y, z - 0.2, h * 0.095, h * 0.095, h * 0.53)


def river_mesh():
    # Break the water surface at the gravel crests so the two fords stay exposed.
    pts = []
    faces = []
    for x in range(-56, 57):
        yc = float(stream(x))
        for side in (-1, 1):
            pts.append((x, yc + side * (3.35 + 0.25 * math.cos(x / 7)), 0.40))
        if x > -56:
            i = len(pts) - 4
            faces.append((i, i + 2, i + 3, i + 1))
    geometry("Alder stream", pts, faces, "ParishWater")
    for x in (-22, 20):
        for i in (-1, 1):
            y = float(stream(x)) + i * 5.7
            z = float(grade(x + 2.4, y))
            lathe("Flood gauge", x + 2.4, y, z, [(0.13, 0), (0.10, 1.50), (0.15, 1.60)], WOOD, 8)
            for mark in range(3):
                block(
                    "Gauge enamel band",
                    (x + 2.4, y, z + 0.38 + mark * 0.30),
                    (0.23, 0.23, 0.055),
                    "HousePlaster",
                )


def bakehouse(x, y):
    z = float(grade(x, y))
    house(x, y, 6.9, 5.2, 3.40, 1, height=grade)
    xx = x + 4.3
    lathe(
        "Remnant brick oven",
        xx,
        y,
        z - 0.24,
        [(1.65, 0), (1.65, 1.43), (1.45, 1.83), (0.88, 2.17), (0.35, 2.26)],
        "HarbourBrick",
        12,
    )
    block("Soot-black oven mouth", (xx, y - 1.6, z + 0.65), (1.33, 0.12, 1.04), WOOD)
    c = (x - 3.68, y, z + 1.69)
    ring("Mill wheel felloe", c, 1.56, 0.15, WOOD, "x")
    for i in range(10):
        a = i * math.tau / 10
        p = (c[0], y + 1.55 * math.cos(a), c[2] + 1.55 * math.sin(a))
        line("Mill spoke", c, p, 0.088, "Wood")
        block("Mill bucket", p, (1.08, 0.27, 0.32), "Wood")


def hospital(x, y):
    z = float(grade(x, y))
    for dx in (-3.85, 3.85):
        for dy in (-2.5, 2.5):
            lathe("Awning pole", x + dx, y + dy, z - 0.32, [(0.085, 0), (0.085, 2.94)], WOOD, 7)
    for j in range(8):
        ax = x - 4 + j
        for side in (-1, 1):
            verts = [
                (ax, y, z + 3.95),
                (ax + 1, y, z + 3.95),
                (ax + 1, y + side * 2.85, z + 2.55),
                (ax, y + side * 2.85, z + 2.55),
            ]
            geometry(
                "Hand-sewn canvas strip",
                verts,
                [(0, 1, 2, 3)],
                "Pennon" if j % 3 == 0 else "HousePlaster",
            )
    for dx in (-2.2, 1.85):
        block("Stretcher canvas", (x + dx, y + 0.33, z + 0.70), (1.27, 2.27, 0.17), "SeaCloth")
        for sx in (-0.55, 0.55):
            for sy in (-0.92, 0.92):
                block("Stretcher foot", (x + dx + sx, y + 0.33 + sy, z + 0.32), (0.13, 0.14, 0.72), WOOD)
        block("Rolled wool blanket", (x + dx, y + 1.13, z + 0.89), (1.12, 0.52, 0.28), "HousePlaster")
    for side in (-1, 1):
        shaft(
            "Wash line post",
            (x + side * 2.3, y - 3.39, z - 0.25),
            (x + side * 2.3, y - 3.39, z + 1.93),
            0.095,
            0.075,
            WOOD,
            8,
        )
    line(
        "Washing line",
        (x - 2.3, y - 3.39, z + 1.78),
        (x + 2.3, y - 3.39, z + 1.78),
        0.027,
        "OchrePlaster",
    )
    for i in range(3):
        block(
            "Linen",
            (x - 1.33 + i * 1.1, y - 3.39, z + 1.32),
            (0.76, 0.06, 0.9),
            "HousePlaster" if i != 1 else "SeaCloth",
        )


def school(x, y):
    z = float(grade(x, y))
    house(x, y, 8.2, 5.7, 3.71, 0, height=grade)
    for dx in (-1.65, 1.65):
        shaft(
            "Yard bell upright",
            (x + dx, y + 1.5, z + 5.6),
            (x + dx, y + 1.5, z + 7.29),
            0.13,
            0.13,
            WOOD,
            8,
        )
    line(
        "School bell headstock", (x - 1.82, y + 1.5, z + 7.25), (x + 1.82, y + 1.5, z + 7.25), 0.16, WOOD
    )
    lathe(
        "School bell",
        x,
        y + 1.5,
        z + 6.18,
        [(0.61, 0), (0.56, 0.18), (0.35, 0.38), (0.27, 0.74), (0.09, 1.01)],
        BRASS,
        12,
    )
    for i in range(3):
        block("School bench", (x - 3 + i * 2.85, y - 4.10, z + 0.52), (1.89, 0.57, 0.19), "Wood")
        for dx in (-0.67, 0.67):
            block("Bench trestle", (x - 3 + i * 2.85 + dx, y - 4.10, z + 0.21), (0.24, 0.48, 0.47), WOOD)


def watch(x, y):
    z = float(grade(x, y))
    lathe(
        "Watchtower plinth",
        x,
        y,
        z - 0.8,
        [(2.19, 0), (2.28, 1.06), (1.88, 1.38), (1.67, 4.05)],
        "Masonry",
        8,
    )
    collision("Closed tower core", x, y, z - 0.32, 2.65, 2.65, 3.49)
    for side in (-1, 1):
        for sy in (-1, 1):
            line(
                "Beacon upright",
                (x + side * 1.21, y + sy * 1.21, z + 3.13),
                (x + side * 0.99, y + sy * 0.99, z + 8.4),
                0.20,
                WOOD,
            )
        line(
            "Signal brace",
            (x - 1.17, y + side * 1.17, z + 3.79),
            (x + 1.04, y + side * 1.04, z + 6.62),
            0.13,
            "Wood",
        )
    block("Lantern floor", (x, y, z + 7.07), (3.16, 3.16, 0.30), WOOD)
    lathe("Signal glass", x, y, z + 7.28, [(0.77, 0), (0.83, 0.32), (0.77, 1.68)], "WindowLight", 8)
    lathe(
        "Copper hood",
        x,
        y,
        z + 8.93,
        [(2.12, 0), (1.88, 0.26), (0.24, 1.53), (0.06, 1.91)],
        "VerdigrisSheet",
        8,
    )


def fork(x, y, z, group):
    shaft("Fork handle", (x, y, z), (x, y, z + 0.34), 0.073, 0.064, WOOD, 8, group)
    for dx in (-0.14, 0.14):
        line("Tempered tine", (x, y, z + 0.34), (x + dx, y, z + 0.47), 0.040, "BellMetal", group)
        line("Tempered tine", (x + dx, y, z + 0.47), (x + dx, y, z + 0.84), 0.039, "BellMetal", group)


def find(i, x, y, z):
    g = "Cache" + str(i)
    z += 0.34
    if i == 0:
        block("Baker tally", (x, y, z), (0.20, 0.22, 0.70), "Wood", g)
        for j in range(5):
            block(
                "Notched brass tally", (x, y - 0.13, z - 0.19 + j * 0.09), (0.18, 0.045, 0.032), BRASS, g
            )
    elif i == 1:
        ring("Bag clasp", (x, y, z + 0.13), 0.25, 0.067, BRASS, "y", g)
        block("Red leather tab", (x, y, z - 0.10), (0.29, 0.12, 0.31), "Pennon", g)
    elif i == 2:
        block("Solitary bass reed", (x, y, z), (0.23, 0.15, 0.74), "BellMetal", g)
        block("Brass tongue", (x, y - 0.09, z + 0.11), (0.077, 0.05, 0.52), BRASS, g)
    else:
        ring("Night key bow", (x, y, z + 0.25), 0.14, 0.052, BRASS, "y", g)
        line("Night key shaft", (x, y, z + 0.15), (x, y, z - 0.26), 0.055, BRASS, g)
        block("Double key bit", (x + 0.08, y, z - 0.21), (0.21, 0.09, 0.11), BRASS, g)


def make(lib):
    r = next(r for r in rooms if r["key"] == KEY)
    field(KEY, r)
    init(lib, 1542)
    terrain(KEY, SPAN, grade, 2)
    river_mesh()
    fork(0, 0, 0, "HandFork")
    bakehouse(-38, -20)
    hospital(39, -10)
    school(32, 44)
    watch(-39, 39)
    for i, (bx, by, bz, w) in enumerate(
        (
            (-38, -22.84, float(grade(-38, -20)) + 2.58, 1.53),
            (43.1, -12.70, float(grade(43, -12)) + 1.48, 1.16),
            (32, 40.99, float(grade(32, 44)) + 2.78, 2.28),
            (-39, 36.71, float(grade(-39, 39)) + 1.57, 1.58),
        )
    ):
        h = w * 2 / 3
        block("Trades board", (bx, by, bz + h / 2), (w + 0.12, 0.18, h + 0.12), WOOD)
        panel("Painted trade emblem", bx, by - 0.105, bz, w, h, "DriftFenTrades", j=i)
        if i == 1:
            block("Ward signpost", (bx, by + 0.14, bz * 0.5), (0.18, 0.22, bz + 0.6), WOOD)

    for i, (x, y) in enumerate(
        (
            (-46, -36),
            (-27, -33),
            (-43, -8),
            (-14, -18),
            (18, -24),
            (47, -24),
            (33, 0),
            (-35, 7),
            (-14, 14),
            (8, 17),
            (30, 22),
            (42, 30),
            (-26, 36),
            (-43, 23),
            (-10, 43),
            (8, 36),
            (49, 44),
            (-49, 49),
            (49, -40),
        )
    ):
        alder(x, y, float((i * 7) % 5) + 4.8, 130 + i)
    escarpment()
    for name, x, y in (("MapSW", -SPAN, -SPAN), ("MapSE", SPAN, -SPAN), ("MapNW", -SPAN, SPAN)):
        marker(name, x, y, float(grade(x, y)))
    for s in r["stations"]:
        x, y = s["x"], s["y"]
        z = float(grade(x, y))
        id = s["id"][2:]
        if id == "Guide":
            model("WZ_SWA_N03", "Willa in her ferry coat", x, y, z, 1.73, 12, "Speaker")
            block("Fork bench", (x + 1.13, y, z + 0.74), (1.30, 0.77, 1.52), WOOD)
            fork(x + 1.10, y, z + 1.50, "BenchFork")
        elif id == "Home":
            arch(x, y, z, 2.80, 3.62, STONE, WOOD)
        elif id == "Map":
            for dx in (-1.58, 1.58):
                block("Field board upright", (x + dx, y, z + 1.44), (0.18, 0.29, 3.34), WOOD)
            block("Field board", (x, y, z + 2.17), (3.66, 0.30, 2.71), WOOD)
            panel("Drift Fen on linen", x, y - 0.17, z + 0.89, 3.53, 2.50, KEY + "Survey")
        elif id.startswith("Find"):
            find(int(id[-1]), x, y, z)
        else:
            block("Salvage ledger pedestal", (x, y, z + 0.71), (0.86, 0.67, 1.45), STONE)
            block("Opened field record", (x, y, z + 1.48), (1.06, 0.75, 0.12), "HousePlaster")
        marker(s["id"], x, y - 0.43, z + (0.55 if id.startswith("Find") else 1.37))
        marker(s["camp"], x, y - 2.15, float(grade(x, y - 2.15)) + 0.10)
    marker("Spawn", 0, -14, 0.08)
    marker("Look", 0, 2, 2)
    finish(KEY, sky_key=r["theme"])
