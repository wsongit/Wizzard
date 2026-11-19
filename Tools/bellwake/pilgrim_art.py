"""Build the five road wards in Blender, with continuous walkable ground and a surveyed map for each."""

import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from atelier import RES, init, finish, geometry, shaft, lathe, block, model, marker, collision
from pilgrim import FIELDS, SIZE, CELL, ENTRY, layout, world, edge
from underworks import rooms
from works_finish import plaques, mount
from works_sets import ring
from wrenfall import oak_crown
from sets import arch

STONE = ["MossRock", "OchrePlaster", "HousePlaster", "Shale", "Masonry"]
CROWN = ["Leaves", "RoofTiles", "Wood", "RimeSnow", "Slate"]
TRIM = ["Wood", "Basalt", "Brass", "Shale", "MossRock"]
HEIGHT = [2.65, 3.45, 3.05, 2.90, 3.70]
PEOPLE = ["WZ_VIL_N01", "WZ_FOU_N01", "WZ_VIL_N03", "WZ_ICE_N01", "WZ_SWA_N01"]
THEMES = ["#456240", "#7f492f", "#5b4f62", "#495966", "#3e6261"]


def elevation(k, x, y):
    raw = (
        0.72
        + 0.5 * np.sin(x / 13 + k) * np.cos(y / 17)
        + 1.5 * np.exp(-((x - 29) ** 2 + (y - 24) ** 2) / 450)
    )
    return raw * np.clip((x * x + (y + 14) ** 2) / 145, 0, 1)


def beam(name, a, b, r, mat, group="Set", n=6):
    return shaft(name, a, b, r, r, mat, n, group)


def texture(k, r, edges, sites):
    key = r["key"]
    n = 512
    y, x = np.mgrid[:n, :n]
    wx = x / n * 120 - 60
    wy = 60 - y / n * 120
    rng = np.random.default_rng(811 + k)

    def noise(m):
        return (
            np.asarray(
                Image.fromarray(rng.integers(0, 255, (m, m), dtype=np.uint8)).resize(
                    (n, n), Image.Resampling.BICUBIC
                ),
                float,
            )
            / 255
            - 0.5
        )

    def tile(name):
        a = np.asarray(Image.open(RES / "Textures" / (name + ".png")).convert("RGB"), float)
        return a[
            np.floor(wy * 4.5).astype(int) % a.shape[0], np.floor(wx * 4.5).astype(int) % a.shape[1]
        ]

    path = Image.new("L", (n, n))
    d = ImageDraw.Draw(path)

    def pt(c):
        a, b = world(c)
        return (int((a + 60) * n / 120), int((60 - b) * n / 120))

    for a, b in sorted(edges):
        d.line([pt(a), pt(b)], fill=255, width=[12, 16, 14, 10, 15][k])
    from PIL import ImageFilter

    blend = np.clip(
        np.asarray(path.filter(ImageFilter.GaussianBlur(2.7)), float) / 255 + noise(81) * 0.19, 0, 1
    )[:, :, None]
    a = tile(["Grass", "Loam", "Setts", "RimeSnow", "Moss"][k]) * 0.78 + np.array(
        [[29, 36, 12], [35, 18, 9], [20, 16, 20], [43, 47, 48], [19, 30, 21]][k]
    )
    b = tile(["DirtPath", "Causeway", "Shale", "MossRock", "Causeway"][k]) * 0.74 + np.array(
        [[51, 47, 29], [46, 27, 16], [60, 56, 65], [57, 61, 57], [38, 46, 41]][k]
    )
    ground = a * (1 - blend) + b * blend + (noise(24) * 17 + noise(n) * 11)[:, :, None]
    for c in sites:
        px, py = world(c)
        ground *= 1 - 0.24 * np.exp(-((wx - px) ** 2 / 3 + (wy - py - 1.4) ** 2 / 2))[:, :, None]
    # Contact shadows run along actual solid wall bays. A break in the survey stays sunlit.
    shade = Image.new("L", (n, n))
    sd = ImageDraw.Draw(shade)
    for yy in range(SIZE):
        for xx in range(SIZE):
            for dx, dy in ((1, 0), (0, 1)):
                if edge((xx, yy), (xx + dx, yy + dy)) in edges:
                    continue
                gx, gy = world((xx, yy))
                gx += 4 * dx + 0.5
                gy += 4 * dy - 0.4

                def pixel(x, y):
                    return ((x + 60) * n / 120, (60 - y) * n / 120)

                sd.line(
                    [pixel(gx - 4 * dy, gy - 4 * dx), pixel(gx + 4 * dy, gy + 4 * dx)],
                    fill=102,
                    width=13,
                )
    ground *= 1 - np.asarray(shade.filter(ImageFilter.GaussianBlur(4)), float)[:, :, None] / 340
    Image.fromarray(ground.clip(0, 255).astype("uint8")).save(RES / "Textures" / (key + "Ground.png"))
    # The drawing area is fixed so both players can put a live bearing on the same printed chart.
    im = Image.new("RGB", (768, 544), "#dfce9e")
    d = ImageDraw.Draw(im)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 24)
    number = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    d.rectangle((6, 6, 761, 537), outline="#766442", width=3)
    d.rectangle((16, 32, 496, 512), fill=THEMES[k], outline="#332f25", width=2)
    xy = lambda c: (32 + c[0] * 32, 496 - c[1] * 32)
    for a, b in sorted(edges):
        d.line([xy(a), xy(b)], fill="#e7daa9", width=9)
    for j, c in enumerate(sites):
        x, y = xy(c)
        d.ellipse((x - 11, y - 11, x + 11, y + 11), fill="#263e42", outline="#f0dda1", width=2)
        d.text((x, y), str(j) if j else "S", font=number, anchor="mm", fill="white")
    d.text((510, 43), "PILGRIMS’ CUT", font=small, fill="#645338")
    d.text((510, 70), r["title"].replace("The ", ""), font=title, fill="#302c26")
    labels = ["Entrance shelter"] + [a[1] for a in FIELDS[k][6]] + ["North road wicket"]
    for j, label in enumerate(labels):
        y = 130 + j * 37
        d.text((514, y), "S" if not j else str(j), font=number, fill="#88512e")
        d.text((543, y), label, font=small, fill="#322e25")
    d.text((515, 468), "N ↑     One square = 8 m", font=small, fill="#354442")
    d.text((515, 493), "Blue rings mark work yards.", font=small, fill="#354442")
    im.save(RES / "Textures" / (key + "Survey.png"))
    plaques(k, r)


def terrain(k, key):
    p = [(x, y, float(elevation(k, x, y))) for y in range(-60, 61, 3) for x in range(-60, 61, 3)]
    faces = [(a, a + 1, a + 42, a + 41) for j in range(40) for i in range(40) for a in [j * 41 + i]]
    o = geometry("Continuous roadbed", p, faces, key + "Ground", "Terrain")
    for i, l in enumerate(o.data.loops):
        x, y, _ = p[l.vertex_index]
        o.data.uv_layers.active.data[i].uv = ((x + 60) / 120, (y + 60) / 120)
    for x, y, w, d in [
        (0, 60.4, 122, 0.8),
        (0, -60.4, 122, 0.8),
        (-60.4, 0, 0.8, 122),
        (60.4, 0, 0.8, 122),
    ]:
        collision("Boundary foundation", x, y, -3, w, d, 24)


def partitions(k, edges):
    # A rectilinear union with shared corners. Only exterior faces are emitted at each crossing.
    half = [0.73, 0.53, 0.47, 0.81, 0.58][k]
    cuts = []
    for a in range(16):
        at = -60 + a * 8
        cuts.extend([at - half, at + half])
    last = len(cuts) - 1
    parts = set()
    for y in range(15):
        for x in range(16):
            if x in (0, 15) or edge((x - 1, y), (x, y)) not in edges:
                parts.update([(2 * x, 2 * y), (2 * x, 2 * y + 1), (2 * x, 2 * y + 2)])
    for y in range(16):
        for x in range(15):
            if y in (0, 15) or edge((x, y - 1), (x, y)) not in edges:
                parts.update([(2 * x, 2 * y), (2 * x + 1, 2 * y), (2 * x + 2, 2 * y)])
    # Two joined masonry courses and a separate weather cap make the depth legible at turns.
    for layer, mat in enumerate([STONE[k], CROWN[k], CROWN[k]]):
        points = []
        faces = []
        for i, j in sorted(parts):
            xy = [
                (cuts[i], cuts[j]),
                (cuts[i + 1], cuts[j]),
                (cuts[i + 1], cuts[j + 1]),
                (cuts[i], cuts[j + 1]),
            ]
            z = [elevation(k, x, y) for x, y in xy]
            base = len(points)
            for level in (layer, layer + 1):
                for a, ((x, y), h) in enumerate(zip(xy, z)):
                    crown = HEIGHT[k] + 0.14 * math.cos(x / 5 + y / 7)
                    delta = [-0.35, crown - 0.52, crown - 0.14, crown][level]
                    points.append((x, y, h + delta))
            for a, (di, dj) in enumerate([(0, -1), (1, 0), (0, 1), (-1, 0)]):
                if (i + di, j + dj) not in parts:
                    b = (a + 1) % 4
                    faces.append(tuple(base + t for t in (a, b, b + 4, a + 4)))
            if layer == 2:
                faces.append(tuple(base + t for t in (4, 5, 6, 7)))
        geometry("Ward boundary course", points, faces, mat, "Rim")
    return parts, cuts


def panel(name, x, y, z, w, h, material, group="Set"):
    return geometry(
        name,
        [(x - w / 2, y, z), (x + w / 2, y, z), (x + w / 2, y, z + h), (x - w / 2, y, z + h)],
        [(0, 1, 2, 3)],
        material,
        group,
        [(0, 0), (1, 0), (1, 1), (0, 1)],
    )


def survey(key, x, y, z, small=False):
    w = 1.9 if small else 3.4
    h = w * 544 / 768
    for side in (-1, 1):
        block("Chart post", (x + side * w * 0.40, y, z + 0.84), (0.15, 0.2, 1.85), "Wood")
    block("Rebated map frame", (x, y, z + 0.76 + h / 2), (w + 0.14, 0.20, h + 0.14), "Wood")
    panel("Survey showing every passage", x, y - 0.106, z + 0.76, w, h, key + "Survey")


def tray(x, y, z):
    for dx in (-0.56, 0.56):
        for dy in (-0.33, 0.33):
            block("Mortised trestle leg", (x + dx, y + dy, z + 0.44), (0.15, 0.18, 1.02), "Wood")
    block("Workbench top", (x, y, z + 0.94), (1.6, 1.06, 0.18), "Wood")


def spire(k, x, y, z, height, mat, group="Set"):
    lathe(
        "Stepped lantern pier",
        x,
        y,
        z - 0.15,
        [
            (0.72, 0),
            (0.72, 0.44),
            (0.50, 0.59),
            (0.38, height - 0.72),
            (0.65, height - 0.55),
            (0.63, height - 0.37),
            (0.30, height),
        ],
        mat,
        8,
        group,
    )


def craft(k, s, x, y, z):
    kind = s["style"]
    wood = "Wood"
    iron = "BellMetal"
    brass = "Brass"
    st = STONE[k]
    if kind in ("knife", "mould", "satchel", "seal", "desk", "rule", "fruit"):
        tray(x, y, z)
        h = z + 1.05
        if kind == "knife":
            beam(
                "Grafting knife grip",
                (x - 0.54, y, h + 0.09),
                (x - 0.16, y + 0.09, h + 0.09),
                0.09,
                wood,
            )
            geometry(
                "Curved pruning blade",
                [
                    (x - 0.16, y, h + 0.1),
                    (x + 0.58, y + 0.18, h + 0.10),
                    (x + 0.65, y + 0.38, h + 0.11),
                    (x + 0.24, y + 0.27, h + 0.15),
                    (x - 0.16, y + 0.17, h + 0.16),
                ],
                [(0, 1, 2, 3, 4)],
                "Slate",
            )
            for j in range(3):
                ring(
                    "Coil of binding linen",
                    (x + 0.22, y - 0.24, h + 0.08 * j),
                    0.24,
                    0.046,
                    "Awning",
                    n=12,
                )
        elif kind in ("mould", "seal", "rule"):
            for side in (-1, 1):
                block("Raised register bar", (x, y + side * 0.28, h + 0.12), (1.18, 0.11, 0.22), brass)
            cnt = 9 if kind != "seal" else [4, 6, 8][["A_Potter", "A_Herd", "A_Ferry"].index(s["id"])]
            for j in range(cnt):
                block(
                    "Calibrated scallop",
                    (x - 0.5 + j / (cnt - 1), y, h + 0.06),
                    (0.055, 0.46, 0.10),
                    iron,
                )
        elif kind == "satchel":
            block("Waxed canvas satchel", (x, y, h + 0.24), (0.84, 0.44, 0.49), "SeaCloth")
            ring("Leather carrying strap", (x, y, h + 0.56), 0.26, 0.045, wood, "y")
        elif kind == "desk":
            for j in range(4):
                block(
                    "Bound public ledger",
                    (x + 0.05 * j, y, h + 0.08 + j * 0.13),
                    (0.85, 0.63, 0.12),
                    "Pennon" if j % 2 else "Awning",
                    angle=0.06 * j,
                )
        else:
            for j in range(5):
                lathe(
                    "Winter quince",
                    x + 0.23 * math.cos(j * 1.4),
                    y + 0.23 * math.sin(j * 1.4),
                    h,
                    [(0.07, 0), (0.15, 0.12), (0.1, 0.26)],
                    "Amber",
                    7,
                )
    elif kind in ("root", "tree"):
        beam("Established rootstock", (x, y, z - 0.12), (x + 0.14, y, z + 2.8), 0.23, wood)
        for j in range(4):
            t = j * 1.73
            xx = x + 0.9 * math.cos(t)
            yy = y + 0.72 * math.sin(t)
            beam("Grafted lateral", (x, y, z + 1.6), (xx, yy, z + 2.8), 0.10, wood)
            if kind == "tree":
                oak_crown(xx, yy, z + 2.59, 0.87, 0.78, 64 + j)
        for j in range(3):
            ring("Linen union", (x + 0.07, y, z + 1.34 + j * 0.12), 0.23, 0.05, "Awning")
    elif kind in ("spring", "gauge"):
        lathe(
            "Cistern lining",
            x,
            y,
            z - 0.11,
            [(0.88, 0), (0.98, 0.12), (0.88, 0.72), (0.95, 0.79)],
            "Masonry",
            12,
        )
        lathe("Water at the weir", x, y, z + 0.69, [(0.73, 0), (0.73, 0.03)], "Water", 14)
        beam("Graduated water rod", (x + 0.45, y, z + 0.65), (x + 0.45, y, z + 2.0), 0.08, brass)
        for j in range(5):
            block("Gauge notch", (x + 0.45, y, z + 0.86 + j * 0.18), (0.29, 0.14, 0.045), "Inlay")
    elif kind in ("press", "frame", "rack", "line", "weir"):
        h = {"press": 2.3, "frame": 1.8, "rack": 2.4, "line": 2.6, "weir": 2.75}[kind]
        for side in (-1, 1):
            block("Anchored end frame", (x + side * 0.81, y, z + h / 2), (0.25, 0.34, h + 0.28), wood)
        block("Top stretcher", (x, y, z + h), (1.98, 0.34, 0.25), wood)
        if kind == "press":
            beam("Lead screw", (x, y, z + 0.73), (x, y, z + h + 0.40), 0.13, iron)
            block("Press platen", (x, y, z + 0.83), (1.38, 0.81, 0.21), "Slate")
            for j in range(6):
                ring("Thread flight", (x, y, z + 1.18 + 0.15 * j), 0.16, 0.038, brass)
        elif kind == "frame":
            for j in range(7):
                beam(
                    "Linen sewing support",
                    (x - 0.64 + j * 0.21, y, z + 0.48),
                    (x - 0.64 + j * 0.21, y, z + h),
                    0.028,
                    "Awning",
                )
            block("Book block", (x, y, z + 0.70), (1.4, 0.7, 0.37), "Pennon")
        elif kind == "rack":
            for j in range(3):
                block("Kiln bat shelf", (x, y, z + 0.45 + j * 0.61), (1.74, 0.89, 0.11), wood)
                for a in range(4):
                    block(
                        "Green tiles",
                        (x - 0.54 + 0.35 * a, y, z + 0.58 + j * 0.61),
                        (0.28, 0.53, 0.13),
                        "RoofTiles",
                    )
        elif kind == "line":
            for j in range(4):
                beam(
                    "Knotted handline",
                    (x - 0.72 + j * 0.36, y, z + 1.65 - 0.12 * math.sin(j)),
                    (x - 0.36 + j * 0.36, y, z + 1.65 - 0.12 * math.sin(j + 1)),
                    0.06,
                    "Reeds",
                )
        else:
            for j in range(5):
                block("Sluice board", (x, y, z + 0.25 + j * 0.29), (1.40, 0.22, 0.25), wood)
            ring("Sluice control", (x, y - 0.23, z + 2.1), 0.36, 0.07, brass, "y")
    elif kind in ("kiln", "beacon", "lantern"):
        h = 3.4 if kind != "lantern" else 1.28
        lathe(
            "Battered round base",
            x,
            y,
            z - 0.12,
            [(1.02, 0), (1.12, 0.24), (0.94, 0.4), (0.68, h - 0.3), (0.76, h)],
            st,
            10,
        )
        if kind == "kiln":
            lathe(
                "Firing chimney",
                x,
                y,
                z + h,
                [(0.62, 0), (0.43, 0.66), (0.42, 1.16), (0.51, 1.31)],
                "RoofTiles",
                9,
            )
            block("Kiln firebox", (x, y - 0.91, z + 0.74), (0.73, 0.11, 0.83), "Basalt")
        else:
            lathe("Storm glass", x, y, z + h, [(0.44, 0), (0.49, 0.46), (0.39, 0.88)], "SeaGlass", 8)
            for j in range(4):
                a = j * math.pi / 2
                beam(
                    "Protective iron stave",
                    (x + 0.48 * math.cos(a), y + 0.48 * math.sin(a), z + h),
                    (x + 0.48 * math.cos(a), y + 0.48 * math.sin(a), z + h + 0.87),
                    0.05,
                    iron,
                )
            lathe("Copper hood", x, y, z + h + 0.87, [(0.62, 0), (0.68, 0.1), (0.1, 0.44)], brass, 8)
    elif kind in ("wall", "cairn", "dais", "arch", "gate"):
        if kind in ("gate", "arch"):
            arch(x, y, z - 0.06, 2.1, 3.1, st, TRIM[k])
            block("Carved mile cap", (x, y, z + 3.59), (2.54, 0.83, 0.25), CROWN[k])
        else:
            for j in range(4):
                w = 1.98 - j * 0.31
                block(
                    "Dressed standing courses",
                    (x + 0.06 * math.sin(j), y, z + 0.23 + j * 0.36),
                    (w, w * 0.63, 0.44),
                    st,
                    angle=j * 0.06,
                )
            if kind == "dais":
                ring("Court seal", (x, y, z + 1.64), 0.49, 0.10, brass)
    elif kind == "spool":
        for side in (-1, 1):
            lathe("Spool flange", x, y, z + 0.55 + side * 0.36, [(0.74, 0), (0.74, 0.13)], wood, 12)
        for j in range(7):
            ring("Tarred rescue rope", (x, y, z + 0.29 + 0.095 * j), 0.50, 0.07, "Reeds")
    elif kind == "anvil":
        lathe("Smith’s stump", x, y, z - 0.05, [(0.48, 0), (0.54, 0.2), (0.45, 0.84)], wood, 8)
        block("Anvil waist", (x, y, z + 1.01), (0.66, 0.49, 0.48), iron)
        beam("Forge horn", (x - 0.44, y, z + 1.24), (x - 0.87, y, z + 1.28), 0.15, iron)
        block("Anvil face", (x, y, z + 1.30), (1.10, 0.54, 0.19), "Slate")
    elif kind in ("bell", "back"):
        spire(k, x, y, z, 1.46, st)
        beam("Bell hanger", (x, y, z + 1.45), (x, y, z + 2.30), 0.09, wood)
        lathe(
            "Road line bell",
            x,
            y,
            z + 1.67,
            [(0.42, 0), (0.46, 0.09), (0.26, 0.47), (0.10, 0.55)],
            brass,
            10,
        )


def landmarks(k, r, sites):
    rand = random.Random(380 + k)
    for j, c in enumerate(sites[1:-1]):
        x, y = world(c)
        x -= 2.48
        y += 2.17
        z = elevation(k, x, y) - 0.1
        if k == 0:
            h = 4.7 + rand.random()
            shaft("Twisted orchard bole", (x, y, z), (x - 0.13, y, z + h * 0.67), 0.41, 0.21, "Wood", 8)
            for n in range(4):
                a = n * 1.61 + j
                xx = x + 1.11 * math.cos(a)
                yy = y + 0.85 * math.sin(a)
                beam(
                    "Spreading scaffold limb", (x, y, z + h * 0.45), (xx, yy, z + h * 0.78), 0.15, "Wood"
                )
                oak_crown(xx, yy, z + h * 0.70, 1.37, 1.25, j * 9 + n)
            for n in range(5):
                a = n * 1.37
                lathe(
                    "Windfall quince",
                    x + 1.0 * math.cos(a),
                    y + 0.83 * math.sin(a),
                    z + h * 0.68,
                    [(0.05, 0), (0.15, 0.13), (0.1, 0.25)],
                    "RoofTiles",
                    7,
                )
        elif k == 1:
            for n in range(2):
                xx = x + n * 0.83
                h = 4.5 + (j + n) % 3
                lathe(
                    "Bottle kiln chimney",
                    xx,
                    y,
                    z,
                    [
                        (0.59, 0),
                        (0.69, 0.28),
                        (0.57, h * 0.45),
                        (0.33, h * 0.63),
                        (0.32, h),
                        (0.44, h + 0.18),
                    ],
                    "RoofTiles" if n else "Masonry",
                    9,
                )
                for t in (0.56, 0.80):
                    lathe("Firing band", xx, y, z + h * t, [(0.43, 0), (0.43, 0.14)], "Basalt", 9)
        elif k == 2:
            block("Archive cabinet back", (x, y, z + 2.39), (2.17, 0.47, 4.81), "Wood")
            for n in range(6):
                block("Archive shelf", (x, y - 0.24, z + 0.43 + n * 0.64), (2.28, 0.68, 0.12), "Wood")
                for b in range(7):
                    bh = 0.33 + rand.random() * 0.23
                    block(
                        "Clothbound deposition",
                        (x - 0.89 + 0.28 * b, y - 0.33, z + 0.49 + n * 0.64 + bh / 2),
                        (0.2, 0.36, bh),
                        rand.choice(["CoalCloth", "SeaCloth", "Pennon", "Awning"]),
                    )
            block("Pediment", (x, y, z + 4.91), (2.53, 0.76, 0.23), "Brass")
        elif k == 3:
            for n in range(5):
                rad = 1.23 - 0.18 * n
                lathe(
                    "Cairn cap course",
                    x + 0.11 * math.sin(n),
                    y,
                    z + n * 0.54,
                    [(rad, 0), (rad * 0.97, 0.30), (rad * 0.77, 0.57)],
                    "MossRock" if n % 2 else "Shale",
                    7,
                )
            beam("Wind pennant staff", (x, y, z + 2.54), (x, y, z + 5.87), 0.105, "Wood")
            panel("Survey pennant", x + 0.40, y, z + 4.89, 0.88, 0.57, ["Pennon", "SeaCloth"][j % 2])
        else:
            x += 0.25
            spire(k, x, y, z, 4.8, "Masonry")
            for n in range(2):
                block(
                    "Channel parapet", (x, y + (n - 0.5) * 0.86, z + 5.05), (2.55, 0.21, 0.74), "Slate"
                )
            block("Aqueduct bed", (x, y, z + 4.76), (2.55, 1.10, 0.36), "MossRock")
    # Detail follows the wall tops, keeping the full walking width on the ground.
    for j in range(23):
        ix, iy = rand.randrange(1, 15), rand.randrange(1, 15)
        x = -60 + ix * 8
        y = -60 + iy * 8
        z = elevation(k, x, y)
        if k == 0:
            shaft(
                "Pleached hedge trunk", (x, y, z - 0.13), (x + 0.13, y, z + 3.5), 0.23, 0.15, "Wood", 7
            )
            oak_crown(x, y, z + 2.9, 1.18, 0.99, 99 + j)
        elif k == 1:
            lathe(
                "Terracotta vent",
                x,
                y,
                z + 2.65,
                [(0.32, 0), (0.35, 0.24), (0.25, 1.22), (0.42, 1.36)],
                "RoofTiles",
                7,
            )
        elif k == 2:
            spire(k, x, y, z, 4.0, "Wood")
            lathe(
                "Scribe’s lantern", x, y, z + 3.67, [(0.28, 0), (0.36, 0.54), (0.13, 0.73)], "Amber", 8
            )
        elif k == 3:
            lathe(
                "Wind-scoured spur",
                x,
                y,
                z - 0.03,
                [(0.65, 0), (0.68, 0.55), (0.48, 2.76), (0.24, 3.51), (0.06, 3.78)],
                "Shale",
                7,
            )
        else:
            lathe(
                "Rain court finial",
                x,
                y,
                z + 2.9,
                [(0.36, 0), (0.44, 0.38), (0.25, 0.62), (0.45, 1.05), (0.21, 1.32)],
                "Masonry",
                8,
            )
    # A distant silhouette varies by ward. It is painted scenery outside the closed boundary.
    for j in range(22):
        a = math.tau * j / 22
        rad = 85 + rand.random() * 12
        x = rad * math.cos(a)
        y = rad * math.sin(a)
        if k == 3 or k == 0:
            h = rand.uniform(9, 23)
            lathe(
                "Far folded ridgeline",
                x,
                y,
                -5,
                [(17, 0), (13, h * 0.34), (6, h * 0.72), (1, h)],
                "Mountain" if k == 3 else "MossRock",
                7,
                "Horizon",
            )
        else:
            h = rand.uniform(7, 17)
            lathe(
                "Far ward tower",
                x,
                y,
                -2,
                [(2.9, 0), (2.8, h * 0.74), (3, h * 0.78), (2.5, h * 0.86), (0.6, h)],
                STONE[k],
                8,
                "Horizon",
            )


def make(k, lib):
    key = FIELDS[k][0]
    r = next(r for r in rooms if r["key"] == key)
    edges, sites = layout(k)
    texture(k, r, edges, sites)
    init(lib, 183 + k)
    terrain(k, key)
    partitions(k, edges)
    landmarks(k, r, sites)
    facades(k, edges)
    waywren()
    for j, s in enumerate(r["stations"]):
        x, y = s["x"], s["y"]
        z = elevation(k, x, y)
        if s["style"] == "person":
            model(PEOPLE[k], FIELDS[k][4], x, y, z - 0.025, 1.72, 0, "Speaker")
        elif s["style"] == "map":
            survey(key, x, y, z)
        else:
            craft(k, s, x, y, z)
            if s["style"] not in ("gate", "arch"):
                block("Nameboard foot", (x, y - 0.29, z + 0.44), (0.14, 0.17, 0.98), "Wood")
            mount(s, k, r, j, lambda ki, xx, yy: elevation(ki, xx, yy))
        marker(s["id"], x, y - 0.45, z + 1.47)
        if s.get("camp"):
            xx, yy = (0, -10) if s["id"] == "A_Talk" else (x, y - 2.25)
            marker(s["camp"], xx, yy, elevation(k, xx, yy) + 0.11)
        if s["id"][2:] in [a[0] for a in FIELDS[k][6]]:
            tag = "Proof" + s["id"][2:]
            pole = x + 1.02
            beam("Witness peg", (pole, y, z - 0.03), (pole, y, z + 2.1), 0.07, "Wood")
            panel("Certified mile ribbon", pole + 0.25, y - 0.02, z + 1.7, 0.50, 0.32, "SeaCloth", tag)
        if s["id"] == "A_Gate":
            lathe(
                "Restored road lamp",
                x,
                y,
                z + 3.69,
                [(0.23, 0), (0.28, 0.27), (0.09, 0.45)],
                "Amber",
                8,
                "RoadLamp",
            )
    for name, x, y in [("MapSW", -60, -60), ("MapSE", 60, -60), ("MapNW", -60, 60)]:
        marker(name, x, y, 0)
    marker("Spawn", 0, -14, 0.08)
    marker("Look", 0, -4, 1.4)
    finish(key)


def waywren():
    """Carved brass field guide with separate wings hinged along its back."""
    gold = "Brass"
    dark = "Wood"
    blue = "SeaGlass"

    def shell(name, sections, mat):
        n = 8
        pts = []
        fs = []
        for y, z, w, h in sections:
            for i in range(n):
                a = i * math.tau / n
                pts.append((w * math.cos(a), y, z + h * math.sin(a)))
        for j in range(len(sections) - 1):
            for i in range(n):
                a = j * n + i
                b = j * n + (i + 1) % n
                fs.append((a, b, b + n, a + n))
        fs.extend([tuple(range(n)), tuple(reversed(range(len(pts) - n, len(pts))))])
        geometry(name, pts, fs, mat, "GuideBird")

    shell(
        "Hammered wren breast",
        [
            (-0.30, 0.07, 0.045, 0.06),
            (-0.14, 0.035, 0.14, 0.13),
            (0.02, 0.025, 0.16, 0.16),
            (0.17, 0.055, 0.12, 0.13),
            (0.21, 0.1, 0.08, 0.08),
        ],
        gold,
    )
    shell(
        "Walnut head casing",
        [(0.08, 0.13, 0.075, 0.09), (0.16, 0.18, 0.115, 0.106), (0.24, 0.19, 0.085, 0.075)],
        dark,
    )
    shaft("Tapered beak", (0.008, 0.235, 0.18), (0, 0.39, 0.175), 0.06, 0.009, gold, 6, "GuideBird")
    for side, group in [(-1, "GuideLeft"), (1, "GuideRight")]:
        shaft(
            "Glass eye",
            (side * 0.092, 0.18, 0.21),
            (side * 0.117, 0.18, 0.21),
            0.030,
            0.027,
            blue,
            8,
            "GuideBird",
        )
        for j in range(4):
            a = (side * 0.082, 0.105 - j * 0.055, 0.08)
            b = (side * (0.34 + 0.078 * j), 0.14 - j * 0.11, 0.065)
            d = (side * (0.285 + 0.07 * j), -0.035 - j * 0.108, 0.04)
            c = (side * 0.105, -0.125 - j * 0.023, 0.015)
            geometry(
                "Stamped primary feather",
                [a, b, d, c, (side * 0.26, -j * 0.065, 0.12)],
                [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (3, 2, 1, 0)],
                gold if j % 2 == 0 else "BellMetal",
                group,
            )
        shaft(
            "Tail quill",
            (side * 0.045, -0.17, 0.07),
            (side * 0.13, -0.43, 0.22),
            0.052,
            0.022,
            blue,
            5,
            "GuideBird",
        )
    ring("Winding key", (0, -0.1, -0.13), 0.067, 0.014, gold, "y", "GuideBird", 10)


def facades(k, edges):
    """Cut relief into the closed bays; through-lanes retain the survey's full width."""
    rng = random.Random(131 + k)
    half = [0.73, 0.53, 0.47, 0.81, 0.58][k]
    bays = []
    for y in range(SIZE):
        for x in range(SIZE):
            for dx, dy in [(1, 0), (0, 1)]:
                c = (x + dx, y + dy)
                if c[0] >= SIZE or c[1] >= SIZE or edge((x, y), c) in edges:
                    continue
                a, b = world((x, y))
                bays.append((a + dx * 4, b + dy * 4, dx, dy))
    rng.shuffle(bays)
    for j, (x, y, dx, dy) in enumerate(bays[:56]):
        side = -1 if j % 2 else 1
        nx, ny = dx * side, dy * side
        tx, ty = -ny, nx

        def xyz(u, v, h):
            a = x + tx * u + nx * (half + v)
            b = y + ty * u + ny * (half + v)
            return (a, b, float(elevation(k, a, b)) + h)

        rot = math.atan2(ty, tx)

        def slab(name, u, v, h, w, d, t, mat):
            block(name, xyz(u, v, h), (w, d, t), mat, "Set", rot)

        if k == 0:
            for u in (-2.2, 0, 2.2):
                slab("Espalier stake", u, 0.05, 1.38, 0.13, 0.16, 2.85, "Wood")
            for z in (0.58, 1.14, 1.72, 2.29):
                beam(
                    "Willow training rail",
                    xyz(-2.3, 0.14, z),
                    xyz(2.3, 0.14, z + 0.06),
                    0.065,
                    "Wood",
                    n=5,
                )
            beam("Trained quince", xyz(-0.9, 0.25, -0.1), xyz(-0.59, 0.25, 1.81), 0.11, "Wood")
            for u in (-1, 1):
                beam(
                    "Fan-trained bough", xyz(-0.67, 0.25, 0.94), xyz(1.2 * u, 0.25, 2.04), 0.075, "Wood"
                )
                for b in range(2):
                    px, py, pz = xyz(u * (1.1 + b * 0.56), 0.18, 2.03 + b * 0.31)
                    lathe(
                        "Clipped orchard spur",
                        px,
                        py,
                        pz - 0.14,
                        [(0.17, 0), (0.39, 0.24), (0.23, 0.50)],
                        "Leaves",
                        6,
                    )
        elif k == 1:
            slab("Recessed oven mouth", 0, 0.035, 1.10, 2.34, 0.11, 1.68, "Basalt")
            for u in (-1, 1):
                slab("Sooted jamb", u * 1.24, 0.12, 1.13, 0.22, 0.4, 2.14, "Masonry")
                slab("Firebrick springer", u * 1.21, 0.16, 2.16, 0.38, 0.48, 0.20, "RoofTiles")
            slab("Firebrick lintel", 0, 0.17, 2.35, 2.88, 0.45, 0.27, "RoofTiles")
            for n in range(5):
                slab("Iron fire grate", (n - 2) * 0.34, 0.14, 0.85, 0.065, 0.11, 1.18, "BellMetal")
            slab("Ash sill", 0, 0.28, 0.21, 2.80, 0.58, 0.32, "Shale")
        elif k == 2:
            slab("Inset archive press", 0, 0.045, 1.53, 3.89, 0.10, 2.72, "CoalCloth")
            for u in (-1.89, 0, 1.89):
                slab("Cabinet stile", u, 0.16, 1.58, 0.16, 0.31, 2.98, "Wood")
            for m in range(3):
                slab("Pigeonhole shelf", 0, 0.19, 0.5 + m * 0.85, 3.92, 0.43, 0.11, "Wood")
                for n in range(6):
                    h = 0.39 + rng.random() * 0.31
                    slab(
                        "Rolled binding",
                        (n - 2.5) * 0.56,
                        0.15,
                        0.59 + m * 0.85 + h / 2,
                        0.25 + rng.random() * 0.19,
                        0.28,
                        h,
                        rng.choice(["Pennon", "SeaCloth", "Awning", "CoalCloth"]),
                    )
            slab("Carved cornice", 0, 0.18, 2.99, 4.07, 0.52, 0.18, "Wood")
        elif k == 3:
            for n in range(4):
                px, py, pz = xyz((n - 1.5) * 1.33, 0.06, -0.05)
                h = 1.1 + rng.random() * 1.9
                lathe(
                    "Basal crag",
                    px,
                    py,
                    pz,
                    [(0.72, 0), (0.65, h * 0.47), (0.40, h * 0.85), (0.12, h)],
                    "MossRock" if n % 2 else "Shale",
                    6,
                )
                lathe(
                    "Windward snowcap",
                    px,
                    py,
                    pz + h * 0.83,
                    [(0.39, 0), (0.14, h * 0.15), (0.04, h * 0.19)],
                    "RimeSnow",
                    6,
                )
        else:
            for u in (-2.27, 2.27):
                slab("Arcade impost", u, 0.13, 1.18, 0.48, 0.46, 2.54, "Masonry")
            for n in range(9):
                a = math.pi * n / 9
                b = math.pi * (n + 1) / 9
                pts = [
                    xyz(rad * math.cos(t), v, 1.38 + rad * 0.84 * math.sin(t))
                    for v in (0.02, 0.37)
                    for rad, t in [(2.05, a), (2.05, b), (2.45, b), (2.45, a)]
                ]
                geometry(
                    "Arcade voussoir",
                    pts,
                    [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)],
                    "Slate" if n == 4 else "Masonry",
                )
            slab("Spillway curb", 0, 0.19, 0.30, 4.50, 0.45, 0.44, "MossRock")


def road_leaf_paint():
    """Illuminated endpapers, sized for the lectern on the market pier."""
    w, h = 384, 248
    rng = np.random.default_rng(196)
    y, x = np.mgrid[:h, :w]
    shade = (
        9 * np.cos((x % 192 - 91) / 87)
        - 11 * np.exp(-abs(x - 191) / 12)
        + 2 * np.sin(y / 9)
        + rng.normal(0, 3.4, (h, w))
    )
    image = Image.fromarray(
        np.uint8(np.clip(np.array([220, 202, 156])[None, None, :] + shade[:, :, None], 0, 255))
    )
    d = ImageDraw.Draw(image)
    gold = "#9d713c"
    red = "#8c342f"
    ink = "#473a2b"
    green = "#4f694f"
    font = lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", n)
    for left in (8, 200):
        d.rectangle((left, 8, left + 175, h - 9), outline=gold, width=2)
        d.rectangle((left + 4, 12, left + 171, h - 13), outline=green, width=1)
        for rx, ry in ((left + 5, 13), (left + 170, 13), (left + 5, h - 14), (left + 170, h - 14)):
            d.polygon([(rx - 3, ry), (rx, ry - 4), (rx + 3, ry), (rx, ry + 4)], fill=red)
    d.text((25, 23), "The public road", font=font(19), fill=red)
    d.text((27, 48), "Nine household marks", font=font(11), fill=ink)
    for i in range(9):
        cx, cy = 40 + i % 3 * 45, 86 + i // 3 * 44
        d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), outline=gold, width=2)
        angle = i * math.pi / 7
        n = 3 + i % 4
        pts = [
            (
                cx + 9 * math.cos(angle + j * 2 * math.pi / n),
                cy + 9 * math.sin(angle + j * 2 * math.pi / n),
            )
            for j in range(n)
        ]
        d.line(pts + [pts[0]], fill=green if i % 2 else red, width=2)
        d.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=ink)
    d.text((26, 210), "Entered at Mossbell", font=font(12), fill=ink)
    d.text((214, 23), "Letters home", font=font(19), fill=red)
    for i, name in enumerate(("Mara", "Jori", "Senn", "Tern", "Issa")):
        yy = 58 + i * 33
        d.text((217, yy), name, font=font(14), fill=green if i % 2 else red)
        d.line((265, yy + 9, 351 - i * 3, yy + 9), fill=gold, width=1)
        for j in range(2):
            for k in range(5):
                px = 220 + k * 26
                py = yy + 19 + j * 3
                d.line((px, py, px + 13 + int(rng.integers(0, 10)), py), fill=ink, width=1)
    image.save(RES / "Textures/RoadLetters.png")
