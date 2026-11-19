"""Scenery and terrain paintings for the three witness districts."""

import math
from atelier import *
from sets import arch
from finish_art import bake_ground


def relief(x, y):
    return max(0, max(abs(x), abs(y)) - 15) * (
        0.15 + 0.07 * math.cos(x * 0.5 + y * 0.3)
    )


def paint_land(k, key):
    import numpy as np
    from PIL import Image

    n = 512
    y, x = np.mgrid[0:n, 0:n].astype(float)
    x = (x + 0.5) * 40 / n - 20
    y = 20 - (y + 0.5) * 40 / n
    noise = np.random.default_rng(187 + k)

    def cloud(size):
        field = Image.fromarray(
            noise.integers(0, 256, (size, size), dtype=np.uint8)
        ).resize((n, n), Image.Resampling.BICUBIC)
        return np.asarray(field).astype(float) / 255 - 0.5

    mott = cloud(26) * 21 + cloud(124) * 15 + cloud(512) * 14
    col = [(138, 135, 101), (196, 210, 208), (99, 91, 101)][k]
    base = np.zeros((n, n, 3)) + col
    path = np.full((n, n), 100.0)
    for a, b in [
        ((0, -20), (0, -5)),
        ((0, -5), (-6, -7)),
        ((0, -5), (7, 1)),
        ((7, 1), (0, 13)),
        ((0, 13), (-5, 9)),
        ((-5, 9), (-6, -7)),
    ]:
        dx, dy = b[0] - a[0], b[1] - a[1]
        t = np.clip(((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy), 0, 1)
        path = np.minimum(path, np.hypot(x - a[0] - t * dx, y - a[1] - t * dy))
    paved = np.array([(173, 148, 113), (154, 173, 177), (132, 117, 109)][k])
    blend = np.clip((1.35 + cloud(58) * 0.65 - path) * 2, 0, 1)[:, :, None]
    base = base * (1 - blend) + paved * blend
    if k == 0:
        edge = x + 10.2 + np.sin(y * 0.23) * 1.3
        tide = np.clip(-edge * 0.7, 0, 1)[:, :, None]
        base = (
            base * (1 - tide)
            + (
                np.array([67, 119, 126])
                + np.cos(y * 5 + np.sin(x * 1.6) * 1.8)[:, :, None] * 7
            )
            * tide
        )
        base += np.exp(-((edge + 0.8) ** 2) / 0.22)[:, :, None] * 36
    if k == 1:
        base += (
            np.maximum(0, np.sin(0.55 * x + 0.26 * y + cloud(15) * 3) - 0.7)[:, :, None]
            * 37
        )
    if k == 2:
        base += np.exp(-(((np.sin(x * 0.4 + y * 0.67 + cloud(18) * 3)) / 0.1) ** 2))[
            :, :, None
        ] * np.array([13, 10, 14])
    result = Image.fromarray(np.uint8(np.clip(base + mott[:, :, None], 0, 255)))
    result.save(RES / "Textures" / (key + "Ground.png"))
    result.save(ROOT / "Tools/bellwake/.web-assets" / (key + "Unlit.png"))
    if k == 1:
        a = np.array(Image.open(RES / "Textures/Shale.png").convert("RGB"), float).mean(
            2
        )
        img = np.uint8(
            np.clip(
                np.array([176, 195, 202]) + ((a - a.mean()) * 0.48)[:, :, None], 0, 255
            )
        )
        Image.fromarray(img).save(RES / "Textures/RimeSnow.png")


def roof(name, x, y, w, d, eave, rise, mat):
    for side in [-1, 1]:
        a = x + side * w * 0.5
        geometry(
            name,
            [
                (x, y - d / 2, eave + rise),
                (a, y - d / 2, eave),
                (a, y + d / 2, eave),
                (x, y + d / 2, eave + rise),
            ],
            [(0, 1, 2, 3)],
            mat,
        )
        shaft(
            "Rough-hewn eave",
            (a, y - d / 2, eave - 0.09),
            (a, y + d / 2, eave - 0.09),
            0.11,
            0.11,
            "Wood",
            6,
        )
    shaft(
        "Ridge cap",
        (x, y - d / 2 - 0.12, eave + rise),
        (x, y + d / 2 + 0.12, eave + rise),
        0.13,
        0.13,
        "Wood",
        6,
    )


def house(k, x, y, w, d, h):
    wall = ["OchrePlaster", "HousePlaster", "Masonry"][k]
    block("Weathered foundation", (x, y, 0.37), (w + 0.26, d + 0.26, 0.74), "Masonry")
    block("Plaster between timbers", (x, y, (h + 0.65) * 0.5), (w, d, h - 0.65), wall)
    for side in [-1, 1]:
        px = x + side * (w / 2 - 0.09)
        block("Corner upright", (px, y - d / 2 - 0.05, h / 2), (0.21, 0.19, h), "Wood")
        wx = x + side * w * 0.31
        block("Casement", (wx, y - d / 2 - 0.09, 1.65), (0.85, 0.12, 0.93), "Wood")
        block(
            "Window glass",
            (wx, y - d / 2 - 0.161, 1.65),
            (0.66, 0.044, 0.72),
            "WindowLight",
        )
        block("Lead mullion", (wx, y - d / 2 - 0.20, 1.65), (0.065, 0.04, 0.73), "Wood")
    block("Front door", (x, y - d / 2 - 0.085, 1.03), (1.12, 0.15, 2.06), "Wood")
    block("Latch", (x + 0.35, y - d / 2 - 0.17, 1.02), (0.14, 0.07, 0.11), "Brass")
    geometry(
        "Plastered gable",
        [
            (x - w / 2, y - d / 2, h),
            (x + w / 2, y - d / 2, h),
            (x, y - d / 2, h + 1.75),
        ],
        [(0, 1, 2)],
        wall,
    )
    block("Gable collar", (x, y - d / 2 - 0.05, h), (w + 0.1, 0.18, 0.17), "Wood")
    block("King post", (x, y - d / 2 - 0.08, h + 0.8), (0.15, 0.14, 1.62), "Wood")
    roof(
        "Weather roof",
        x,
        y,
        w + 0.8,
        d + 0.9,
        h,
        1.85,
        "RimeSnow" if k == 1 else "RoofSlate",
    )
    block("Chimney", (x + w * 0.28, y + 0.42, h + 1.1), (0.72, 0.74, 2.8), "Masonry")
    collision("Closed interior", x, y, 0, w, d, h)


def scenery(k):
    if k == 0:
        house(0, 10, 15, 5.7, 4.7, 3.45)
        # Sail loft, open-sided so that its roof frames the pilot station from the quay.
        for x in (9.5, 15.7):
            for y in (-15, -9.7):
                shaft("Loft post", (x, y, -0.14), (x, y, 3.55), 0.20, 0.14, "Wood", 7)
        roof("Tarred sailcloth", 12.6, -12.35, 7.1, 6.2, 3.6, 1.35, "SeaCloth")
        for y in [-14, -8, -2, 4, 10, 16]:
            lathe(
                "Harbour pile",
                -13.5,
                y,
                -0.22,
                [(0.20, 0), (0.175, 1.35), (0.20, 1.43)],
                "Wood",
                7,
            )
        for y in [-14, -8, -2, 4, 10]:
            for j in range(4):
                a = j / 4
                b = (j + 1) / 4
                shaft(
                    "Tarred mooring line",
                    (-13.5, y + a * 6, 1.14 - 0.3 * math.sin(math.pi * a)),
                    (-13.5, y + b * 6, 1.14 - 0.3 * math.sin(math.pi * b)),
                    0.043,
                    0.043,
                    "BellMetal",
                    5,
                )
        for n, (x, y, h) in enumerate([(-24, -3, 8), (-27, 7, 11), (-32, 19, 15)]):
            shaft(
                "Mast beyond the jetty", (x, y, 0.2), (x, y, h), 0.135, 0.068, "Wood", 7
            )
            geometry(
                "Gaff sail",
                [
                    (x + 0.16, y, 1.3),
                    (x + 0.16, y, h - 0.5),
                    (x + 3.8, y + 0.4, h - 2.6),
                    (x + 4.4, y + 0.6, 2.1),
                ],
                [(0, 1, 2, 3)],
                "Awning" if n % 2 else "Pennon",
                "Rim",
            )
    elif k == 1:
        house(1, 9.4, 16, 6.2, 4.25, 3.25)
        for i, (x, y, h) in enumerate(
            [
                (-17, -13, 7),
                (-16, -9, 5.9),
                (15, -13, 7.4),
                (17, 7, 6.6),
                (-15, 15, 8.9),
                (-11, 17, 5.2),
                (14, 13, 6.1),
            ]
        ):
            z = relief(x, y)
            shaft(
                "Spruce bole",
                (x, y, z - 0.2),
                (x + 0.1, y, z + h * 0.82),
                h * 0.045,
                h * 0.018,
                "Wood",
                8,
            )
            for n in range(3):
                r = (0.255 - n * 0.045) * h
                off = (0.20 + n * 0.20) * h
                lathe(
                    "Needle skirt",
                    x + 0.05 * n,
                    y,
                    z + off,
                    [(r * 0.35, 0), (r, 0.16 * h), (r * 0.58, 0.29 * h), (0, 0.44 * h)],
                    "Leaves",
                    9,
                )
                lathe(
                    "Snow on boughs",
                    x + 0.05 * n,
                    y,
                    z + off + 0.18 * h,
                    [(r * 0.86, 0), (r * 0.61, 0.10 * h), (0, 0.275 * h)],
                    "RimeSnow",
                    9,
                )
        for i in range(11):
            cx = -40 + i * 7.6
            cy = 38 + rng.uniform(-2, 4)
            h = rng.uniform(11, 22)
            n = 8
            pts = []
            peakx = cx + rng.uniform(-3, 3)
            peaky = cy + rng.uniform(-2, 2)
            for j in range(n):
                a = j * math.tau / n
                r = rng.uniform(9, 14)
                bx, by = cx + math.cos(a) * r, cy + math.sin(a) * r
                f = rng.uniform(0.45, 0.78)
                pts.extend(
                    [
                        (bx, by, 0),
                        ((1 - f) * bx + f * peakx, (1 - f) * by + f * peaky, h * f),
                    ]
                )
            pts.append((peakx, peaky, h))
            faces = []
            for j in range(n):
                m = 2 * j
                q = 2 * ((j + 1) % n)
                faces.extend([(m, q, q + 1, m + 1), (m + 1, q + 1, 2 * n)])
            o = geometry("Wind-scoured ridge", pts, faces, "Slate", "Rim")
            o.data.materials.append(mats["RimeSnow"])
            for f in list(o.data.polygons)[1::2]:
                f.material_index = 1
    else:
        for y in [-11, 0, 10]:
            # Rock-cut lookout colonnade with a continuous covered walkway on the east side.
            arch(14.8, y, 0.04, 4.6, 6.1, "Basalt", "Masonry")
            for x in (11.8, 17.8):
                block("Buttress plinth", (x, y, 0.46), (1.25, 1.8, 0.92), "Slate")
        for x in (11.9, 17.7):
            block("Gallery cornice", (x, 0, 6.0), (0.75, 24, 0.54), "Masonry")
        roof("Gallery vault", 14.8, 0, 7.3, 24, 6.25, 1.65, "Basalt")
        for x in [-14.6, -13.7]:
            block("Mine rail", (x, -0.3, 0.13), (0.065, 27, 0.11), "BellMetal")
        for i in range(30):
            block(
                "Oak tie", (-14.15, -13 + i * 0.89, 0.065), (1.44, 0.19, 0.13), "Wood"
            )
        for i in range(14):
            x = -18 + rng.uniform(-0.9, 0.9)
            y = -14 + i * 2.15
            h = rng.uniform(1.1, 3.4)
            shaft(
                "Prismatic column",
                (x, y, 0.1),
                (x + 0.44, y, h),
                0.40,
                0.30,
                "SeaGlass",
                5,
            )
            shaft(
                "Crystal crown",
                (x + 0.44, y, h),
                (x + 0.60, y, h + 0.65),
                0.30,
                0.015,
                "SeaGlass",
                5,
            )
