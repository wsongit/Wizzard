"""A playable cooks’ yard, with a furnished open-front bakehouse and individually spun instruments."""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from atelier import (
    ROOT,
    RES,
    init,
    finish,
    geometry,
    block,
    shaft,
    lathe,
    marker,
    palm_target,
    collision,
    model,
    origins,
)
from works_sets import ring, line
from works_finish import plaques, mount
from sets import arch
from finish_art import bake_ground
from underworks import rooms
from wrenfall import oak_crown
from engine_art import panel, workshop_paint


def high(k, x, y):
    return 0.72 * min(1, max(0, (abs(x) - 8) / 8)) + 0.38 * min(1, max(0, (y - 12) / 6))


def painted_yard():
    n = 512
    y, x = np.mgrid[:n, :n]
    wx = x / n * 40 - 20
    wy = 20 - y / n * 40
    rng = np.random.default_rng(167)
    noise = rng.normal(0, 2.0, (n, n))

    def sample(key):
        tile = np.array(Image.open(RES / "Textures" / (key + ".png")).convert("RGB"))
        h, w = tile.shape[:2]
        return tile[(y * 7 // 4) % h, (x * 7 // 4) % w].astype(float)

    grass = sample("Grass") * 0.65 + [28, 33, 12]
    gravel = sample("Setts") * 0.72 + [36, 29, 17]
    road = np.clip((2.4 + 0.3 * np.sin(wy * 0.65) - abs(wx - 1.5 * np.sin(wy * 0.24))) * 1.6, 0, 1)
    apron = np.clip(3.5 - np.maximum(abs(wx) * 0.48, abs(wy + 1.9) * 0.7), 0, 1)
    t = np.maximum(road, apron)[:, :, None]
    rgb = grass * (1 - t) + gravel * t
    inside = (abs(wx) < 7.7) & (wy > -0.4) & (wy < 12.6)
    mortar = ((x + ((y // 12) % 2) * 13) % 26 < 1) | (y % 12 < 1)
    tile = sample("HarbourBrick") * 0.32 + [94, 64, 39] + noise[:, :, None] - mortar[:, :, None] * 20
    rgb[inside] = tile[inside]
    im = Image.fromarray(np.uint8(np.clip(rgb + noise[:, :, None], 0, 255)))
    im.save(RES / "Textures/KettleYardGround.png")
    im.save(ROOT / "Tools/bellwake/.web-assets/KettleYardUnlit.png")
    im = Image.new("RGB", (384, 256), "#d9c395")
    d = ImageDraw.Draw(im)
    d.rectangle((6, 6, 377, 249), outline="#816343", width=3)
    font = lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", n)
    d.text((21, 21), "The harbour mess", font=font(27), fill="#803c31")
    for j, (label, bits) in enumerate(
        (("Nell · lunch tin", "202"), ("Ara · cups", "110"), ("Wen · cloth", "021"))
    ):
        yy = 91 + j * 53
        d.text((22, yy - 12), label, font=font(17), fill="#324940")
        for a, ch in enumerate(bits):
            xx = 235 + a * 43
            hy = yy + (int(ch) - 1) * 9
            d.ellipse((xx - 6, hy - 4, xx + 5, hy + 4), fill="#614e39")
            d.line((xx + 4, hy, xx + 4, hy - 16), fill="#614e39", width=2)
    im.save(RES / "Textures/MessLedger.png")


def slab(name, x, y, z, w, d, h, mat):
    return block(name, (x, y, z + h / 2), (w, d, h), mat)


def bowl(name, x, y, z, r, mat, group="Set"):
    # A rolled edge around a hollow bowl with a glazed interior.
    pts = []
    rings = [
        (0.37, 0),
        (0.57, 0.12),
        (0.95, 0.57),
        (1, 0.64),
        (0.94, 0.71),
        (0.85, 0.60),
        (0.44, 0.22),
        (0.20, 0.16),
    ]
    n = 16
    for rad, zz in rings:
        pts.extend(
            [
                (
                    x + r * rad * math.cos(i * math.tau / n),
                    y + r * rad * math.sin(i * math.tau / n),
                    z + r * zz,
                )
                for i in range(n)
            ]
        )
    faces = [
        (j * n + i, j * n + (i + 1) % n, (j + 1) * n + (i + 1) % n, (j + 1) * n + i)
        for j in range(len(rings) - 1)
        for i in range(n)
    ]
    faces.append(tuple((len(rings) - 1) * n + i for i in range(n)))
    return geometry(name, pts, faces, mat, group)


def table(x, y, z, w, d, h):
    for a in (-1, 1):
        for b in (-1, 1):
            slab(
                "Chamfered trestle leg",
                x + a * (w / 2 - 0.18),
                y + b * (d / 2 - 0.18),
                z - 0.04,
                0.17,
                0.18,
                h,
                "TarredOak",
            )
    for i in range(4):
        slab(
            "Scrubbed ash plank",
            x,
            y + ((i + 0.5) / 4 - 0.5) * d,
            z + h - 0.09,
            w,
            d / 4 - 0.012,
            0.14,
            "Wood",
        )


def keepsake(k, x, y, z):
    table(x, y, z, 1.5, 0.98, 1)
    if k == 1:
        lathe(
            "Blue lunch pail",
            x,
            y,
            z + 1.04,
            [(0.23, 0), (0.4, 0.13), (0.39, 0.52), (0.42, 0.55), (0.32, 0.62)],
            "VerdigrisSheet",
            16,
        )
        ring("Bale handle", (x, y, z + 1.70), 0.29, 0.026, "Brass", "y")
    elif k == 2:
        for j in range(3):
            xx = x + (j - 1) * 0.44
            bowl("Patternmaker’s measure", xx, y, z + 1.05, 0.24 - 0.028 * j, "BellMetal")
            line(
                "Pewter handle",
                (xx + 0.13, y, z + 1.17),
                (xx + 0.21, y + 0.25, z + 1.20),
                0.033,
                "Brass",
            )
    else:
        pts = []
        for i in range(12):
            xx = x - 0.58 + i * 0.105
            fold = 0.023 * math.cos(i)
            pts.extend(
                [
                    (xx, y + 0.27, z + 1.075 + fold),
                    (xx, y - 0.49, z + 1.075 + fold),
                    (xx, y - 0.53 + fold, z + 0.60 + 0.05 * math.sin(i * 0.6)),
                ]
            )
        geometry(
            "Tea cloth",
            pts,
            [
                (3 * i + a, 3 * i + 3 + a, 3 * i + 4 + a, 3 * i + 1 + a)
                for i in range(11)
                for a in (0, 1)
            ],
            "Awning",
        )
        for i in range(3):
            xx = x + (i - 1) * 0.26
            line("Knotted tassel", (xx, y - 0.51, z + 0.64), (xx, y - 0.54, z + 0.39), 0.028, "SeaCloth")


def building():
    # The packed-earth yard continues beneath the open front. Plaster fills the timber bays.
    for side in (-1, 1):
        x = side * 7.8
        slab("Stone kitchen sill", x, 6.1, -0.12, 0.6, 13.3, 0.82, "Masonry")
        slab("Limewashed side wall", x, 6.1, 0.66, 0.39, 13.1, 2.35, "HousePlaster")
        for y in (-0.45, 3.9, 8.4, 12.65):
            slab("Kitchen wall post", x, y, -0.09, 0.53, 0.47, 4.13, "TarredOak")
        for y in (1.74, 6.18, 10.53):
            line(
                "Wind brace",
                (x - side * 0.22, y - 1.86, 0.73),
                (x - side * 0.22, y + 1.83, 2.98),
                0.13,
                "Wood",
            )
            panel("Leadlight", x - side * 0.06, y, 3.08, 0.83, 0.62, "WindowLight")
        for y in (-0.53, 12.65):
            line("Rafter", (x, y, 3.96), (0, y, 6.9), 0.23, "Wood")
        # Overhang and two weather courses cast a distinct red roof silhouette.
        pts = [
            (side * 8.54, -1.38, 3.71),
            (0, -1.38, 7.04),
            (0, 13.44, 7.04),
            (side * 8.54, 13.44, 3.71),
        ]
        geometry("Cookhouse tile slope", pts, [(0, 1, 2, 3)], "RoofTiles")
        for t in (0.22, 0.52, 0.82):
            xx = side * 8.54 * (1 - t)
            line(
                "Kitchen purlin",
                (xx, -1.40, 3.59 + 3.31 * t),
                (xx, 13.47, 3.59 + 3.31 * t),
                0.13,
                "TarredOak",
            )
        for y in (2.8, 7.8):
            line("Visible roof couple", (x, y, 3.85), (0, y, 6.80), 0.15, "TarredOak")
    slab("Rear kitchen wall", 0, 12.7, -0.10, 15.8, 0.51, 4.1, "HousePlaster")
    for y in (-0.65, 12.7):
        line("Heavy tie beam", (-7.95, y, 3.92), (7.95, y, 3.92), 0.24, "TarredOak")
        geometry(
            "Plastered gable", [(-7.85, y, 4), (7.85, y, 4), (0, y, 6.95)], [(0, 1, 2)], "OchrePlaster"
        )
        for xx in (-4, 0, 4):
            line("Gable stud", (xx, y - 0.13, 4), (xx, y - 0.13, 6.92 - abs(xx) * 0.37), 0.09, "Wood")
        for side in (-1, 1):
            line("Mortised knee", (side * 7.7, y, 2.68), (side * 6.25, y, 3.91), 0.16, "TarredOak")
    # Hearth and hood.
    x, y = -4.7, 10.8
    slab("Hearthstone", x, y, -0.08, 4.4, 2.52, 0.42, "Basalt")
    for side in (-1, 1):
        slab("Fired brick cheek", x + side * 1.53, y, 0.27, 0.61, 2.12, 2.42, "HarbourBrick")
    slab("Smoke-black fireback", x, y + 0.82, 0.31, 2.75, 0.29, 2.05, "Basalt")
    block("Hearth lintel", (x, y, 2.63), (3.83, 2.15, 0.46), "Masonry")
    pts = [
        (x + a * w, y + b * d, z)
        for w, d, z in ((1.98, 1.11, 2.80), (0.72, 0.55, 4.88))
        for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))
    ]
    geometry(
        "Corbelled smoke hood",
        pts,
        [(a, (a + 1) % 4, (a + 1) % 4 + 4, a + 4) for a in range(4)],
        "HarbourBrick",
    )
    slab("Chimney stack", x, y, 4.85, 1.49, 1.11, 3.38, "HarbourBrick")
    for dx in (-0.55, 0.1, 0.61):
        shaft(
            "Charred billet",
            (x + dx - 0.28, y - 0.5, 0.43),
            (x + dx + 0.25, y + 0.35, 0.55),
            0.15,
            0.12,
            "TarredOak",
            7,
        )
        lathe("Hearth coals", x + dx, y - 0.15, 0.48, [(0.25, 0), (0.21, 0.21), (0.08, 0.5)], "Amber", 7)
    line("Hearth crane", (x + 1.03, y - 0.77, 1.95), (x, y - 0.77, 1.95), 0.065, "BellMetal")
    line("Pot hook", (x, y - 0.77, 1.95), (x, y - 0.77, 1.28), 0.035, "BellMetal")
    lathe(
        "Iron stew kettle",
        x,
        y - 0.77,
        0.69,
        [(0.42, 0), (0.62, 0.17), (0.64, 0.48), (0.49, 0.6)],
        "Basalt",
        18,
    )
    ring("Hearth kettle bale", (x, y - 0.77, 1.35), 0.43, 0.034, "BellMetal", "y")
    for yy in (8.4, 10.6):
        table(4.9, yy, 0.08, 3.05, 1.19, 0.92)
        for i in range(4):
            bowl("Dipped blue crockery", 3.91 + i * 0.60, yy, 0.08 + 0.99, 0.24, "VerdigrisSheet")
    for j in range(9):
        x = -1.72 + j * 0.55
        shaft(
            "Bunch of drying herbs",
            (x, 11.8, 3.52),
            (x + 0.06, 11.8, 3.08 - 0.07 * (j % 3)),
            0.04,
            0.13,
            "Leaves" if j % 3 else "Pennon",
            5,
        )


def kitchen_pans():
    line("Wrought pan rail", (-4.25, 5.75, 2.8), (4.25, 5.75, 2.8), 0.105, "BellMetal")
    for x in (-4.25, 4.25):
        slab("Pan rail foot", x, 5.75, -0.04, 0.35, 0.42, 3.0, "TarredOak")
        line("End brace", (x, 5.75, 2.16), (x - math.copysign(0.65, x), 5.75, 2.78), 0.095, "Wood")
    for i, (name, x, r) in enumerate(zip(("Low", "Middle", "High"), (-3.2, 0, 3.2), (0.66, 0.53, 0.43))):
        group = "Pan" + name
        cy = 5.70
        cz = 1.51
        palm_target(name, x, cy - .10, cz, r * .51)
        pts = []
        n = 24
        for radius, depth in (
            (0.17, 0.29),
            (0.60, 0.26),
            (1, 0.10),
            (1.02, -0.016),
            (0.92, -0.09),
            (0.70, 0.035),
            (0.17, 0.07),
        ):
            for j in range(n):
                a = j * math.tau / n
                pts.append((x + radius * r * math.cos(a), cy + depth, cz + r * radius * math.sin(a)))
        fs = [
            (j * n + a, j * n + (a + 1) % n, (j + 1) * n + (a + 1) % n, (j + 1) * n + a)
            for j in range(6)
            for a in range(n)
        ]
        fs.extend([tuple(range(n - 1, -1, -1)), tuple(range(6 * n, 7 * n))])
        geometry("Spun copper pan", pts, fs, ("BellMetal", "Brass", "VerdigrisSheet")[i], group)
        shaft(
            "Pan handle",
            (x, cy + 0.07, cz + r * 0.73),
            (x, cy + 0.07, 2.63),
            0.09,
            0.06,
            "TarredOak",
            8,
            group,
        )
        ring("Hanging eye", (x, cy + 0.06, 2.70), 0.10, 0.025, "Brass", "y", group, 12)
        origins[group] = (x, cy, 2.77)
        lathe(
            "Filled witness bowl",
            x,
            6.81,
            2.93,
            [(0.16, 0), (0.35, 0.14), (0.37, 0.23)],
            "Amber",
            10,
            "Phrase" + str(i),
        )
    block("Witness shelf", (0, 6.86, 2.87), (8.15, 0.64, 0.13), "Wood")
    for x in (-3.7, 3.7):
        line("Shelf hanger", (x, 6.88, 2.86), (x, 6.88, 5.37), 0.043, "BellMetal")


def make(lib):
    r = next(q for q in rooms if q["key"] == "KettleYard")
    workshop_paint()
    painted_yard()
    plaques(0, r)
    init(lib, 1459)
    pts = [(x, y, high(0, x, y)) for y in range(-20, 21, 2) for x in range(-20, 21, 2)]
    o = geometry(
        "Continuous turf and kitchen clay",
        pts,
        [
            (j * 21 + i, j * 21 + i + 1, (j + 1) * 21 + i + 1, (j + 1) * 21 + i)
            for j in range(20)
            for i in range(20)
        ],
        "KettleYardGround",
        "Terrain",
    )
    for li, l in enumerate(o.data.loops):
        x, y, _ = pts[l.vertex_index]
        o.data.uv_layers.active.data[li].uv = ((x + 20) / 40, (y + 20) / 40)
    for x, y, w, d in ((0, 20.4, 41, 0.8), (0, -20.4, 41, 0.8), (-20.4, 0, 0.8, 41), (20.4, 0, 0.8, 41)):
        collision("Yard boundary", x, y, -2, w, d, 18)
        block("Cobble windbreak", (x, y, 0.86), (w + 0.11, d + 0.11, 2.13), "MossRock", "Rim")
    building()
    kitchen_pans()
    for i, (x, y) in enumerate(((-14, -6), (14, -7), (-14, 8), (13.8, 7), (-10.4, 14.8), (14, 14))):
        z = high(0, x, y)
        shaft("Apple bole", (x, y, z - 0.08), (x + 0.27, y, 3.25 + z), 0.40, 0.21, "Wood", 9)
        oak_crown(x + 0.18, y, z + 3.05, 2.91, 2.45, 89 + i)
        for j in range(5):
            a = j * math.tau / 5 + i
            lathe(
                "Windfall apple",
                x + 1.7 * math.cos(a),
                y + 1.7 * math.sin(a),
                z + 3.13 + 0.14 * math.cos(j),
                [(0.06, 0), (0.17, 0.13), (0.13, 0.28), (0.05, 0.31)],
                "Pennon",
                7,
            )
    for side in (-1, 1):
        for j in range(4):
            x = side * (21 + j % 2 * 2)
            y = -15 + j * 9
            ht = 8 + 3 * math.cos(j)
            lathe(
                "Coastal headland",
                x,
                y,
                -2,
                [(4.3, 0), (3.2, ht * 0.64), (1.8, ht * 0.8), (0.47, ht)],
                "MossRock",
                7,
                "Horizon",
            )
    for j, s in enumerate(r["stations"]):
        x, y = s["x"], s["y"]
        z = high(0, x, y)
        id = s["id"][2:]
        if id == "Cook":
            model("WZ_VIL_N03", "Iona the cook", x, y, z - 0.02, 1.64, 0, "Speaker")
        if id == "Score":
            table(x, y, z, 2, 1.2, 0.94)
            block("Ledger cover", (x, y, z + 1.12), (1.76, 0.17, 1.15), "TarredOak")
            panel("Harbour ledger", x, y - 0.10, z + 0.63, 1.62, 1, "MessLedger")
        if id == "Serve":
            table(x, y, z, 3.8, 1.76, 0.99)
            for i, dx in enumerate((-1.19, 0, 1.19)):
                bowl("Place setting", x + dx, y - 0.34, z + 1.07, 0.29, "VerdigrisSheet")
                line(
                    "Pewter spoon",
                    (x + dx + 0.33, y - 0.47, z + 1.08),
                    (x + dx + 0.35, y - 0.18, z + 1.10),
                    0.033,
                    "BellMetal",
                )
                for k in range(3):
                    lathe(
                        "Served supper",
                        x + dx + 0.09 * math.cos(k * 2),
                        y - 0.34 + 0.08 * math.sin(k * 2),
                        z + 1.16,
                        [(0.056, 0), (0.08, 0.05), (0.04, 0.11)],
                        "Amber",
                        7,
                        "ServedTable",
                    )
            lathe(
                "Hot tureen",
                x,
                y + 0.27,
                z + 1.08,
                [(0.31, 0), (0.48, 0.15), (0.51, 0.46), (0.38, 0.57), (0.13, 0.69)],
                "BellMetal",
                16,
                "ServedTable",
            )
        if id == "Home":
            arch(x, y, z, 2.65, 3, "Masonry", "Wood")
        if s["style"] != "person":
            if id in ("High", "Middle", "Low"):
                block("Pan legend", (x, y - 0.27, 0.66), (1.35, 0.14, 0.4), "TarredOak")
            mount(s, 0, r, j, high)
        marker(s["id"], x, y - 0.45, z + 1.4)
        if s.get("camp"):
            marker(s["camp"], x, y - 2.25, high(0, x, y - 2.25) + 0.08)
    for asset, name, x, y, angle in (
        ("WZ_SWA_N01", "Nell", 4.3, -0.02, 23),
        ("WZ_FOU_N01", "Ara", 5.78, -0.01, -16),
        ("WZ_VIL_N01", "Wen", 7.15, -0.25, -43),
    ):
        model(asset, name, x, y, high(0, x, y) - 0.03, 1.65, angle, "MessCrew")
    lathe(
        "Mess welcome lantern",
        -0.6,
        -0.75,
        3.03,
        [(0.16, 0), (0.28, 0.12), (0.27, 0.48), (0.11, 0.61)],
        "Amber",
        8,
        "KitchenLamp",
    )
    marker("Spawn", 0, -14, 0.08)
    marker("Look", 0, -4, 1.4)
    bake_ground("KettleYard", lambda x, y: high(0, x, y))
    finish("KettleYard", sky_key="KettleLight")
