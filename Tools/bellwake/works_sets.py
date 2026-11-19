"""Editable architecture and machinery for the Lower Works. All coordinates are in metres."""

import sys, math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atelier import *
from sets import arch, lamp
from finish_art import bake_ground
from underworks import rooms
from works_finish import plaques, mount, scene_details
from PIL import Image
import numpy as np

TAU = 2 * math.pi


def smooth(t):
    t = max(0, min(1, t))
    return t * t * (3 - 2 * t)


def height(k, x, y):
    # The back galleries climb on broad ramps, with an unbroken terrain sheet under every fixture.
    rise = [1.5, 1.2, 2.6, 1.8, 1.15, 1.6, 2.5, 1.35][k]
    return rise * smooth((y - 1) / 12) + 0.6 * smooth((abs(x) - 11) / 7)


def pigment(k, r):
    n = 512
    Y, X = np.mgrid[:n, :n]
    x = X / n * 40 - 20
    y = 20 - Y / n * 40
    noise = np.random.default_rng(3022 + k)

    def broad(n0):
        return (
            np.asarray(
                Image.fromarray(
                    noise.integers(0, 255, (n0, n0), dtype=np.uint8)
                ).resize((n, n), Image.Resampling.BICUBIC),
                float,
            )
            / 255
            - 0.5
        )

    base = np.array(
        [
            (102, 102, 92),
            (92, 122, 116),
            (107, 101, 91),
            (124, 107, 83),
            (96, 81, 74),
            (123, 117, 118),
            (94, 106, 122),
            (116, 100, 108),
        ][k]
    )
    joints = (np.minimum((y + 30) % 1.45, 1.45 - (y + 30) % 1.45) < 0.035) | (
        ((x + np.floor((y + 30) / 1.45) * 0.9) % 2.2) < 0.065
    )
    shade = broad(18) * 21 + broad(96) * 17 + broad(512) * 20 - 17 * joints
    rgb = base + shade[:, :, None]
    radius = np.hypot(x, y)
    if k in (0, 6, 7):
        pattern = np.minimum.reduce(
            [abs(radius - t) for t in [3.1, 3.32, 7.2, 7.35, 12.0]]
        )
        rgb += np.maximum(0, 1 - pattern / 0.11)[:, :, None] * np.array([50, 39, 9])
    elif k in (1, 2):
        channel = np.minimum(
            abs(x + 6 + 0.32 * np.sin(y * 0.7)), abs(x - 6 + 0.32 * np.sin(y * 0.7))
        )
        rgb += np.clip(1 - channel / 0.54, 0, 1)[:, :, None] * np.array([-26, 6, 8])
    elif k in (3, 4):
        rail = np.minimum(abs(x - 3.8), abs(x + 3.8))
        rgb += np.clip(1 - rail / 0.12, 0, 1)[:, :, None] * np.array([40, 33, 28])
    else:
        ray = np.minimum(abs(x - y * 0.56), abs(x + y * 0.56))
        rgb += np.clip(1 - ray / 0.12, 0, 1)[:, :, None] * np.array([34, 36, 19])
    im = Image.fromarray(np.uint8(np.clip(rgb, 0, 255)))
    key = r["key"]
    im.save(RES / "Textures" / (key + "Ground.png"))
    im.save(ROOT / "Tools/bellwake/.web-assets" / (key + "Unlit.png"))


def ring(name, c, r, t, mat, axis="z", group="Set", n=16):
    # A continuous hollow ring. Four-sided cross section keeps the highlight faceted.
    pts = []
    faces = []
    for i in range(n):
        a = TAU * i / n
        for j in range(4):
            b = TAU * j / 4
            v = [
                (r + t * math.cos(b)) * math.cos(a),
                (r + t * math.cos(b)) * math.sin(a),
                t * math.sin(b),
            ]
            if axis == "y":
                v = [v[0], v[2], v[1]]
            elif axis == "x":
                v = [v[2], v[0], v[1]]
            pts.append(tuple(c[q] + v[q] for q in range(3)))
        for j in range(4):
            faces.append(
                (
                    4 * i + j,
                    4 * ((i + 1) % n) + j,
                    4 * ((i + 1) % n) + (j + 1) % 4,
                    4 * i + (j + 1) % 4,
                )
            )
    return geometry(name, pts, faces, mat, group)


def line(name, a, b, t, mat, group="Set", n=8):
    return shaft(name, a, b, t, t, mat, n, group)


def post_column(x, y, z, h, mat):
    lathe(
        "Octagonal footing and pier",
        x,
        y,
        z,
        [
            (0.90, 0),
            (0.9, 0.29),
            (0.72, 0.48),
            (0.54, 0.63),
            (0.47, h - 0.78),
            (0.69, h - 0.46),
            (0.9, h - 0.31),
            (0.9, h),
        ],
        mat,
        8,
    )


def floor(k, key):
    pts = [(x, y, height(k, x, y)) for y in range(-20, 21) for x in range(-20, 21)]
    fs = [
        (j * 41 + i, j * 41 + i + 1, j * 41 + i + 42, j * 41 + i + 41)
        for j in range(40)
        for i in range(40)
    ]
    o = geometry("Ramp-laid flagstones", pts, fs, key + "Ground", "Terrain")
    for i, l in enumerate(o.data.loops):
        p = o.data.vertices[l.vertex_index].co
        o.data.uv_layers.active.data[i].uv = ((p.x + 20) / 40, (p.y + 20) / 40)
    for x, y, w, d in [
        (0, -20.4, 41, 0.8),
        (0, 20.4, 41, 0.8),
        (-20.4, 0, 0.8, 41),
        (20.4, 0, 0.8, 41),
    ]:
        collision("Closed foundation", x, y, -2, w, d, 18)


def architecture(k):
    stone = [
        "Masonry",
        "Shale",
        "MossRock",
        "Masonry",
        "Basalt",
        "Slate",
        "Masonry",
        "Basalt",
    ][k]
    trim = [
        "Brass",
        "Shale",
        "Wood",
        "BellMetal",
        "BellMetal",
        "Brass",
        "Brass",
        "Brass",
    ][k]
    heights = [7.8, 5.6, 6.8, 7.5, 7.1, 6.5, 8.2, 8.5]
    eave = heights[k]
    # Ribbed walls, open clerestories and a walkable central nave. Silhouette and ceiling differ by trade.
    for side in (-1, 1):
        for i in range(5):
            a = -16 + i * 8
            x = side * 20
            block(
                "Cyclopean west and east walls",
                (x, a, eave * 0.43 - 1),
                (0.8, 8, eave * 0.86 + 2),
                stone,
                "Rim",
            )
            block(
                "Western wall cap",
                (x, a, eave * 0.86 + 0.15),
                (1.22, 8, 0.35),
                trim,
                "Rim",
            )
            block(
                "Rear gallery courses",
                (a, side * 20, eave * 0.40 - 1),
                (8, 0.8, eave * 0.80 + 2),
                stone,
                "Rim",
            )
            block(
                "Rear running cornice",
                (a, side * 20, eave * 0.80 + 0.12),
                (8, 1.25, 0.33),
                trim,
                "Rim",
            )
            post_column(side * 17.7, a, height(k, side * 17.7, a) - 0.14, eave, stone)
            for q in (-1, 1):
                block(
                    "Vertical window mullion",
                    (side * 19.76, a + q * 1.55, eave * 0.86 + 1),
                    (0.42, 0.26, 2.1),
                    "Wood",
                    "Rim",
                )
            block(
                "Lintel over clerestory",
                (side * 19.76, a, eave * 0.86 + 2.0),
                (0.68, 8, 0.30),
                trim,
                "Rim",
            )
    if k in (0, 6, 7):
        radius = [13, 0, 0, 0, 0, 0, 11.5, 12][k]
        for i in range(12):
            a = TAU * i / 12
            b = TAU * (i + 1) / 12
            pts = []
            for q in [a, b]:
                for rad, h in [
                    (25, eave + 1),
                    (radius, eave + 4),
                    (radius * 0.54, eave + 5.4),
                ]:
                    pts.append((rad * math.cos(q), rad * math.sin(q), h))
            geometry("Oculus coffer", pts, [(0, 3, 4, 1), (1, 4, 5, 2)], stone, "Rim")
            line("Radial roof rib", pts[0], pts[2], 0.16, trim, "Rim")
        ring(
            "Open oculus collar",
            (0, 0, eave + 5.4),
            radius * 0.54,
            0.33,
            trim,
            "z",
            "Rim",
            24,
        )
    else:
        for y in [-16, -8, 0, 8, 16]:
            for sx in [-1, 1]:
                line(
                    "Hammerbeam rib",
                    (sx * 18, y, eave),
                    (sx * 11, y, eave + 2.35),
                    0.19,
                    trim,
                    "Rim",
                )
                line(
                    "Principal rafter",
                    (sx * 11, y, eave + 2.35),
                    (0, y, eave + 4.9),
                    0.18,
                    trim,
                    "Rim",
                )
                geometry(
                    "Sloping aisle roof",
                    [
                        (sx * 20, y - 4, eave + 0.2),
                        (sx * 20, y + 4, eave + 0.2),
                        (sx * 12, y + 4, eave + 2.4),
                        (sx * 12, y - 4, eave + 2.4),
                    ],
                    [(0, 1, 2, 3)],
                    stone,
                    "Rim",
                )
            if k in (2, 4):
                line(
                    "Suspended tie beam",
                    (-18, y, eave + 0.1),
                    (18, y, eave + 0.1),
                    0.18,
                    "Wood",
                    "Rim",
                )
    for x, y in [(-15, -14), (14, 13), (-15, 13), (14, -14)]:
        lamp(x, y, height(k, x, y), "SeaGlass" if k in (1, 2, 5, 6) else "Amber")


def instrument(k, s):
    x, y = s["x"], s["y"]
    z = height(k, x, y)
    kind = s["style"]
    id = s["id"]
    # Interaction pins sit on the front face clear of solid geometry for both hand and gaze.
    if kind == "person":
        marker(id, x, y - 0.48, z + 1.30)
        return
    if kind == "lift":
        arch(x, y, z - 0.08, 2.8, 3.52, "Slate", "Brass")
        block(
            "Bronze lift doors",
            (x, y + 0.19, z + 1.42),
            (2.74, 0.28, 2.86),
            "BellMetal",
        )
        for dx in [-0.98, -0.50, 0, 0.50, 0.98]:
            block(
                "Embossed door stile",
                (x + dx, y - 0.01, z + 1.36),
                (0.086, 0.10, 2.7),
                "Brass",
            )
        ring("Lift gong", (x, y - 0.14, z + 2.00), 0.35, 0.072, "Brass", "y")
        marker(id, x, y - 0.58, z + 1.39)
        return
    if kind == "leaf":
        lathe(
            "Stone reader",
            x,
            y,
            z - 0.07,
            [(0.5, 0), (0.49, 0.18), (0.35, 0.32), (0.25, 0.87), (0.44, 1.02)],
            "Masonry",
            8,
        )
        block("Engraved tablet", (x, y, z + 1.14), (0.86, 0.42, 0.36), "OchrePlaster")
        for j in range(3):
            block(
                "Etched witness line",
                (x - 0.04 * (j % 2), y - 0.225, z + 1.07 + j * 0.085),
                (0.55 - 0.09 * j, 0.024, 0.023),
                "Wood",
            )
    elif kind in ("wheel", "valve", "winch"):
        lathe(
            "Bedded spindle",
            x,
            y,
            z - 0.04,
            [(0.54, 0), (0.52, 0.18), (0.31, 0.32), (0.23, 1.08)],
            "BellMetal",
            8,
        )
        if kind == "winch":
            for dx in (-0.35, 0.35):
                ring("Winch cheek", (x + dx, y, z + 1), 0.33, 0.08, "Brass", "x")
            line(
                "Grooved drum", (x - 0.42, y, z + 1), (x + 0.42, y, z + 1), 0.20, "Wood"
            )
        else:
            ring("Valve rim", (x, y - 0.16, z + 1.1), 0.38, 0.061, "Brass", "y", n=12)
            for i in range(3):
                a = TAU * i / 3
                line(
                    "Wheel spoke",
                    (x, y - 0.16, z + 1.1),
                    (x + math.cos(a) * 0.34, y - 0.16, z + 1.1 + math.sin(a) * 0.34),
                    0.041,
                    "Brass",
                )
    elif kind == "chime":
        for dx in (-0.48, 0.48):
            line("Trestle", (x + dx, y, z - 0.03), (x + dx, y, z + 1.69), 0.08, "Wood")
        line("Chime bar", (x - 0.62, y, z + 1.7), (x + 0.62, y, z + 1.7), 0.085, "Wood")
        lathe(
            "Tuned cup",
            x,
            y,
            z + 0.78,
            [(0.31, 0), (0.34, 0.07), (0.20, 0.24), (0.13, 0.56), (0.04, 0.65)],
            "Brass",
            9,
        )
    elif kind == "relic":
        lathe(
            "Treasury cradle",
            x,
            y,
            z - 0.04,
            [
                (0.62, 0),
                (0.66, 0.18),
                (0.42, 0.28),
                (0.34, 0.9),
                (0.58, 1.01),
                (0.52, 1.10),
            ],
            "Slate",
            10,
        )
        ring("Gimbal", (x, y, z + 1.42), 0.34, 0.05, "Brass", "y")
    else:
        block("Lever footing", (x, y, z + 0.26), (0.78, 0.74, 0.52), "Masonry")
        line("Pull arm", (x, y, z + 0.46), (x, y - 0.22, z + 1.16), 0.075, "BellMetal")
        line(
            "Oak handhold",
            (x - 0.19, y - 0.22, z + 1.16),
            (x + 0.19, y - 0.22, z + 1.16),
            0.083,
            "Wood",
        )
    marker(id, x, y - 0.51, z + 1.22)


def basin(k, x, y, r, group):
    z = height(k, x, y)
    lathe(
        "Cistern shoe",
        x,
        y,
        z - 0.11,
        [(r + 0.22, 0), (r + 0.22, 0.30), (r, 0.48)],
        "Masonry",
        14,
    )
    for h in (0.55, 1.68, 2.26):
        ring("Hoop", (x, y, z + h), r, 0.075, "Brass", n=14)
    for i in range(12):
        a = TAU * i / 12
        px = x + r * math.cos(a)
        py = y + r * math.sin(a)
        line(
            "Tank stanchion", (px, py, z + 0.3), (px, py, z + 2.32), 0.085, "BellMetal"
        )
    lathe(
        "Rising water surface",
        x,
        y,
        z + 0.42,
        [(r * 0.92, 0), (r * 0.92, 0.085)],
        "Water",
        16,
        group,
    )
    # Vault contains a closed solid core; narrow gaps at the gauge cannot admit a head.
    lathe(
        "Sealed cistern volume",
        x,
        y,
        z - 0.2,
        [(r, 0), (r, 2.60)],
        "Masonry",
        14,
        "C_Solids",
    )
    for i in range(5):
        block(
            "Gauge tick",
            (x + r + 0.09, y, z + 0.62 + i * 0.34),
            (0.16, 0.15, 0.053),
            "Inlay",
        )


def lantern(x, y, z, group):
    lathe(
        "Pilot flame",
        x,
        y,
        z,
        [(0.045, 0), (0.19, 0.18), (0.16, 0.44), (0.02, 0.65)],
        "Amber",
        7,
        group,
    )


def dressing(k, r):
    if k == 0:
        for j, (x, y) in enumerate([(-5.6, 1), (5.6, 1), (0, 7.0)]):
            z = height(k, x, y)
            post_column(x, y, z - 0.03, 2.8, "Slate")
            ring("Guild halo", (x, y, z + 3.12), 0.63, 0.10, "Brass", "y")
            lantern(x, y, z + 2.95, "Beacon" + str(j))
        for rad, z in [(3.2, 7.2), (2.5, 7.7), (1.5, 8.4)]:
            ring("Suspended cistern crown", (0, 0, z), rad, 0.14, "Brass")
        for j in range(8):
            a = TAU * j / 8
            x, y = 3.2 * math.cos(a), 3.2 * math.sin(a)
            line(
                "Chandelier chain",
                (x, y, 7.25),
                (x * 1.8, y * 1.8, 13.05),
                0.045,
                "BellMetal",
                "Rim",
            )
            lathe(
                "Lantern bell",
                x,
                y,
                6.58,
                [(0.19, 0), (0.26, 0.18), (0.15, 0.54), (0.04, 0.67)],
                "WindowLight",
                6,
            )
    elif k == 1:
        for x, g, rad in [(-6, "WestWater", 2), (6, "EastWater", 2.55)]:
            basin(k, x, 0, rad, g)
        line("Elevated crossfeed", (-6, 0, 2.72), (6, 0, 2.72), 0.20, "BellMetal")
        for x in (-6, 6):
            line("Downpipe", (x, 0, 2.72), (x, 0, 2.05), 0.19, "BellMetal")
        for x in (-4, 0, 4):
            ring("Compression flange", (x, 0, 2.72), 0.27, 0.052, "Brass", "x")
        lantern(0, 6, height(k, 0, 6) + 1.5, "LockLamp")
    elif k == 2:
        for sx in (-1, 1):
            for y in (-7, 2, 12):
                x = sx * 15.3
                z = height(k, x, y)
                block("Bookcase back", (x, y, z + 2.0), (0.34, 4.6, 4.0), "Wood")
                for h in [0.4, 1.23, 2.09, 2.96, 3.78]:
                    block(
                        "Oaken shelf",
                        (x - sx * 0.36, y, z + h),
                        (0.96, 4.72, 0.12),
                        "Wood",
                    )
                    if h < 3.4:
                        for j in range(7):
                            block(
                                "Bound flood ledger",
                                (x - sx * 0.34, y - 1.9 + j * 0.58, z + h + 0.34),
                                (
                                    0.52,
                                    0.24 + rng.random() * 0.14,
                                    0.43 + rng.random() * 0.28,
                                ),
                                rng.choice(["SeaCloth", "Pennon", "CoalCloth", "Wood"]),
                            )
        lantern(0, 10, height(k, 0, 10) + 1.28, "ReedLight")
    elif k == 3:
        z = height(k, 0, 2)
        for x in (-6.5, 6.5):
            post_column(x, 2, z - 0.08, 5.35, "Masonry")
        block("Gantry head", (0, 2, z + 5.53), (14.2, 1, 0.58), "Wood")
        line("Balance axle", (0, 1.2, z + 4.65), (0, 2.7, z + 4.65), 0.35, "Brass")
        block(
            "Indicator beam",
            (0, 1.05, z + 4.65),
            (9.8, 0.44, 0.31),
            "BellMetal",
            "BalanceBeam",
        )
        origins["BalanceBeam"] = (0, 1.05, z + 4.65)
        for idx, x in enumerate((-4.3, 4.3), 1):
            lathe(
                "Suspended pan",
                x,
                1.1,
                z + 0.70,
                [(1.27, 0), (1.52, 0.32)],
                "Brass",
                12,
                "Pan" + str(idx),
            )
            for dy in (-0.75, 0.75):
                line(
                    "Pan guide",
                    (x, 1.1 + dy, z + 0.95),
                    (x, 1.1 + dy, z + 4.35),
                    0.066,
                    "BellMetal",
                )
        for j, n in enumerate([1, 2, 4]):
            size = 0.37 + 0.10 * j
            for q, (x, y, h) in enumerate(
                [
                    (-2.2 + j * 2.2, 4.4, height(k, 0, 4.4)),
                    (-5 + j * 0.63, 1.1, z + 1.02),
                    (3.7 + j * 0.63, 1.1, z + 1.02),
                ]
            ):
                lathe(
                    "Calibrated iron weight",
                    x,
                    y,
                    h,
                    [
                        (size * 0.82, 0),
                        (size, 0.07),
                        (size, 0.30 + j * 0.12),
                        (size * 0.52, 0.40 + j * 0.12),
                    ],
                    "BellMetal",
                    8,
                    "Load" + str(n) + "At" + str(q),
                )
    elif k == 4:
        for x in (-6, 6):
            z = height(k, x, 8)
            lathe(
                "Bell furnace",
                x,
                8,
                z - 0.12,
                [
                    (1.88, 0),
                    (1.96, 0.40),
                    (1.55, 3.2),
                    (0.95, 3.8),
                    (0.72, 5.6),
                    (0.90, 5.85),
                ],
                "Basalt",
                10,
            )
            block("Firebox", (x, 6.48, z + 1.18), (1.27, 0.25, 0.85), "WindowLight")
            for a in (-0.4, 0, 0.4):
                block(
                    "Fire grate",
                    (x + a, 6.27, z + 1.18),
                    (0.075, 0.12, 0.9),
                    "BellMetal",
                )
        lathe(
            "Casting flask",
            0,
            1,
            0,
            [(1.42, 0), (1.50, 0.25), (1.26, 0.79)],
            "Slate",
            12,
        )
        lathe(
            "Bronze bath",
            0,
            1,
            0.80,
            [(1.11, 0), (1.11, 0.08)],
            "Amber",
            12,
            "LiquidBronze",
        )
        ring(
            "Cast bell yoke",
            (0, 11, height(k, 0, 11) + 1.46),
            0.29,
            0.09,
            "Amber",
            "x",
            "BrightYoke",
        )
    elif k == 5:
        for x, tag in [(0, "Shutter"), (-8, "MoonMirror"), (8, "SunMirror")]:
            y = -3.65 if x == 0 else 3.45
            z = 2.2
            origins[tag] = (x, y, z)
            post_column(x, y, height(k, x, y) - 0.1, 1.4, "Slate")
            block("Silvered facet", (x, y, z), (0.95, 0.14, 1.40), "SeaGlass", tag)
            ring("Mirror bezel", (x, y, z), 0.72, 0.065, "Brass", "y", tag)
        for name, a, b in [
            ("WestRay", (0, -3.65, 2.2), (-8, 3.45, 2.2)),
            ("EastRay", (0, -3.65, 2.2), (8, 3.45, 2.2)),
            ("MoonRay", (-8, 3.45, 2.2), (-4, 9, 2.2)),
            ("SunRay", (8, 3.45, 2.2), (4, 9, 2.2)),
        ]:
            line(
                "Refracted pencil",
                a,
                b,
                0.047,
                "SeaGlass" if "Moon" in name or "West" in name else "Amber",
                name,
                5,
            )
        for x, tag in [(-4, "MoonCup"), (4, "SunCup")]:
            post_column(x, 9, height(k, x, 9) - 0.08, 1.15, "Slate")
            lantern(x, 9, 2.24, tag)
    elif k == 6:
        z = height(k, 0, 1)
        lathe(
            "Astronomer’s bearing",
            0,
            1,
            z - 0.09,
            [(2.12, 0), (2.25, 0.28), (1.78, 0.52), (1.2, 1.19)],
            "Masonry",
            16,
        )
        for j, (tag, rad) in enumerate(
            [("OakRing", 2.25), ("WrenRing", 1.64), ("TideRing", 1.04)]
        ):
            h = z + 2.35 + j * 0.55
            origins[tag] = (0, 1, h)
            ring("Graduated ecliptic", (0, 1, h), rad, 0.10, "Brass", "z", tag, 24)
            line("Pointer", (0, 1, h), (0, 1 + rad, h), 0.09, "BellMetal", tag)
            lathe(
                "Planet finial",
                0,
                1 + rad,
                h - 0.16,
                [(0.02, 0), (0.27, 0.17), (0.23, 0.36), (0.03, 0.48)],
                ["Amber", "SeaGlass", "Inlay"][j],
                8,
                tag,
            )
        line("Orrery shaft", (0, 1, z + 1.10), (0, 1, z + 3.8), 0.18, "BellMetal")
    else:
        for j, (x, y, h) in enumerate([(-8, 2, 5.4), (0, 8.6, 6.2), (8, 2, 4.9)]):
            z = height(k, x, y)
            for n in range(5):
                px = x + (n - 2) * 0.52
                hh = h - (n % 3) * 0.68
                lathe(
                    "Organ reed",
                    px,
                    y,
                    z - 0.1,
                    [(0.22, 0), (0.26, 0.18), (0.22, hh - 0.32), (0.36, hh)],
                    "Brass" if j == 1 else "Slate",
                    9,
                )
            lantern(x, y - 0.45, z + 2.0, "Mouth" + str(j))
        for j in range(6):
            a = TAU * j / 6
            x, y = 3 * math.cos(a), 3 * math.sin(a)
            line(
                "Bronze suspension",
                (x, y, 5.7),
                (x * 1.35, y * 1.35, 12.65),
                0.055,
                "BellMetal",
                "Rim",
            )
        lathe(
            "The resonator shell",
            0,
            0,
            4.85,
            [(2.6, 0), (2.68, 0.22), (1.92, 1.05), (1.25, 2.24), (0.42, 2.54)],
            "BellMetal",
            16,
        )
        lantern(0, 0, 4.35, "BellHeart")


def make(k, lib):
    r = rooms[k]
    key = r["key"]
    pigment(k, r)
    plaques(k, r)
    init(lib, 9017 + k)
    floor(k, key)
    architecture(k)
    dressing(k, r)
    scene_details(k, height, ring, line, post_column)
    for j, s in enumerate(r["stations"]):
        instrument(k, s)
        mount(s, k, r, j, height)
    marker("Spawn", 0, -14, 0.08)
    marker("Look", 0, -4, 1.4)
    bake_ground(key, lambda x, y: height(k, x, y))
    finish(key, sky_key=r["theme"])


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1 :]
    for i, r in enumerate(rooms):
        if r.get("chapter") or (len(args) > 1 and r["key"] not in args[1:]):
            continue
        make(i, Path(args[0]))
