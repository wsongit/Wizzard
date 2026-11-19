"""Guild signs, vault silhouettes, permanent machinery and scene-specific storytelling."""

import math
from PIL import Image, ImageDraw, ImageFont
from atelier import *
from sets import arch, flags
from mathutils import Matrix
from pathlib import Path

TAU = math.tau


def plaques(k, r):
    ink = [
        "#213b37",
        "#194743",
        "#383a34",
        "#49371e",
        "#492822",
        "#273948",
        "#302e46",
        "#432e39",
    ][k]
    im = Image.new("RGB", (512, 512), ink)
    d = ImageDraw.Draw(im)
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    for j, s in enumerate(r["stations"]):
        x = (j % 2) * 256
        y = j // 2 * 64
        d.rounded_rectangle(
            (x + 4, y + 4, x + 251, y + 59), 7, fill=ink, outline="#b69a61", width=3
        )
        for sx in (x + 13, x + 243):
            d.ellipse((sx - 2, y + 30, sx + 2, y + 34), fill="#e9d799")
        size = 22
        while True:
            font = ImageFont.truetype(path, size)
            label = s["label"]
            if d.textlength(label, font=font) < 219 or size < 11:
                break
            size -= 1
        d.text((x + 128, y + 31), label, fill="#fff0c3", font=font, anchor="mm")
    im.save(RES / "Textures" / (r["key"] + "Signs.png"))


def mount(s, k, r, j, height):
    if s["style"] == "person":
        return
    x, y = s["x"], s["y"]
    z = height(k, x, y)
    if s["style"] == "lift":
        w, h, front, base = 2.7, 0.59, y - 0.39, z + 2.77
    else:
        w, h, front, base = 1.36, 0.31, y - 0.34, z + 0.58
    x0 = (j % 2) * 0.5 + 0.008
    x1 = x0 + 0.484
    v1 = 1 - (j // 2) / 8 - 0.006
    v0 = v1 - 0.114
    geometry(
        "Enamel guild lettering",
        [
            (x - w / 2, front, base),
            (x + w / 2, front, base),
            (x + w / 2, front, base + h),
            (x - w / 2, front, base + h),
        ],
        [(0, 1, 2, 3)],
        r["key"] + "Signs",
        "Set",
        [(x0, v0), (x1, v0), (x1, v1), (x0, v1)],
    )


def scene_details(k, height, ring, line, column):
    def point(x, y):
        return height(k, x, y)

    def prop(asset, name, x, y, h, angle=0, group="Set"):
        model("WZ_" + asset, name, x, y, point(x, y) - 0.045, h, angle, group)

    def archway(x, y, w, h):
        arch(x, y, point(x, y) - 0.08, w, h, "Masonry" if k != 4 else "Basalt", "Brass")

    def bunting(x, y, material, h=4.5):
        flags(x, y, point(x, y), h, material)

    def gable(x, y, w, d, h):
        z = point(x, y)
        block("Old workshop", (x, y, z + h / 2 - 0.1), (w, d, h), "HousePlaster")
        for sx in (-1, 1):
            block(
                "Half timber",
                (x + sx * (w / 2 - 0.13), y - d / 2 - 0.04, z + h / 2),
                (0.19, 0.16, h),
                "Wood",
            )
            geometry(
                "Weathered slate roof",
                [
                    (x, y - d / 2 - 0.45, z + h + 1.65),
                    (x + sx * (w / 2 + 0.45), y - d / 2 - 0.45, z + h),
                    (x + sx * (w / 2 + 0.45), y + d / 2 + 0.45, z + h),
                    (x, y + d / 2 + 0.45, z + h + 1.65),
                ],
                [(0, 1, 2, 3)],
                "RoofSlate",
            )
        geometry(
            "Front gable",
            [
                (x - w / 2, y - d / 2, z + h),
                (x + w / 2, y - d / 2, z + h),
                (x, y - d / 2, z + h + 1.65),
            ],
            [(0, 1, 2)],
            "OchrePlaster",
        )
        block("Timber door", (x, y - d / 2 - 0.12, z + 1.1), (1.2, 0.24, 2.2), "Wood")
        for sx in (-1, 1):
            block(
                "Latticed window",
                (x + sx * w * 0.32, y - d / 2 - 0.09, z + 1.8),
                (0.72, 0.16, 0.79),
                "WindowLight",
            )

    if k == 0:
        for side in [-1, 1]:
            archway(side * 10, 16, 4.8, 5)
            bunting(side * 7.4, 12, "SeaCloth" if side < 0 else "Pennon")
            for j in range(3):
                block(
                    "Stepped gallery bench",
                    (
                        side * (13 + j * 0.8),
                        5.4,
                        point(side * 13, 5.4) + 0.19 + j * 0.19,
                    ),
                    (0.86, 4.1, 0.45 + j * 0.38),
                    "Masonry",
                )
        ring("Charter well rim", (0, 1, 0.55), 2.1, 0.27, "Masonry", n=16)
        lathe("Cistern spring", 0, 1, 0.15, [(1.98, 0), (1.98, 0.11)], "Water", 16)
        lathe(
            "Well curb",
            0,
            1,
            -0.07,
            [(2.32, 0), (2.3, 0.41), (2.11, 0.50)],
            "Masonry",
            16,
            "C_Solids",
        )
        # Visible well has a continuous curb and a shallow, sealed volume beneath it.
        for j in range(16):
            a = j * TAU / 16
            b = (j + 1) * TAU / 16
            pp = [
                (rad * math.cos(t), 1 + rad * math.sin(t), h)
                for rad, h in [(2.23, 0), (2.23, 0.50), (1.95, 0.50), (1.95, 0.12)]
                for t in (a, b)
            ]
            geometry(
                "Dressed well block",
                pp,
                [(0, 1, 3, 2), (2, 3, 5, 4), (4, 5, 7, 6)],
                "Masonry",
            )
        prop("RUI_N01", "Nema counting the guild roll", -5, -8.1, 1.65, 12)
        prop("RUI_P06", "Recovered reliquary", -14, 13, 2.4)
    if k == 1:
        # Behind the gauges a paddle wheel rises above the incoming culvert.
        cx, cy, cz = 0, 10, point(0, 10) + 3.55
        for yy in (cy - 0.4, cy + 0.4):
            ring("Paddlewheel felloe", (cx, yy, cz), 2.96, 0.18, "Wood", "y", n=20)
        for j in range(12):
            a = j * TAU / 12
            xx = cx + 2.84 * math.cos(a)
            zz = cz + 2.84 * math.sin(a)
            line(
                "Waterwheel spoke", (cx, cy - 0.4, cz), (xx, cy - 0.4, zz), 0.11, "Wood"
            )
            block("Paddle blade", (xx, cy, zz), (0.48, 1.5, 0.33), "Wood")
        for xx in [-3.45, 3.45]:
            column(xx, cy, point(xx, cy), 3.58, "Shale")
        line(
            "Waterwheel axle",
            (cx, cy - 1.02, cz),
            (cx, cy + 1.24, cz),
            0.28,
            "BellMetal",
        )
        for x, rad in [(-6, 2), (6, 2.55)]:
            for j in range(8):
                a = j * math.pi / 8
                b = (j + 1) * math.pi / 8
                pts = [
                    (x + rad * math.cos(t), rad * math.sin(t), h)
                    for h in (0.32, 2.25)
                    for t in (a, b)
                ]
                geometry("Riveted copper tank shell", pts, [(0, 1, 3, 2)], "BellMetal")
            for h in (0.59, 0.92, 1.25, 1.58, 1.91):
                block(
                    "Gauge graduation",
                    (x + rad * 0.64, -rad * 0.79, h),
                    (0.25, 0.09, 0.045),
                    "Inlay",
                )
            for yy in (-9, 11):
                line(
                    "Overflow standpipe",
                    (x, yy, point(x, yy)),
                    (x, yy, 3.2),
                    0.25,
                    "BellMetal",
                )
                line("Arched return", (x, yy, 3.2), (x, yy + 2, 4.1), 0.24, "BellMetal")
        prop("SWA_N01", "Fen listening for cavitation", -12, -5, 1.59, 18)
        prop("SWA_P02", "Canal winch", 14, 10, 2.7, -25)
    if k == 2:
        # Two freestanding banks of folios divide the entrance nave into three readable routes.
        for x in [-6, 6]:
            for yy in [-7.4, 6.9]:
                z = point(x, yy)
                for side in [-1, 1]:
                    block(
                        "Case upright",
                        (x + side * 1.7, yy, z + 1.58),
                        (0.15, 0.82, 3.18),
                        "Wood",
                    )
                for h in [0.25, 1.10, 1.98, 2.86]:
                    block("Folio shelf", (x, yy, z + h), (3.6, 0.81, 0.13), "Wood")
                    if h < 2.5:
                        for j in range(8):
                            block(
                                "Tied manuscript",
                                (x - 1.42 + j * 0.41, yy, z + h + 0.35),
                                (0.28, 0.58, 0.43 + 0.12 * (j % 3)),
                                ["CoalCloth", "OchrePlaster", "SeaCloth", "Pennon"][
                                    j % 4
                                ],
                            )
        archway(0, 15, 6.1, 6)
        for j in range(7):
            x = -2.5 + 0.82 * j
            zt = point(0, 15) + 3.65 - math.fabs(x) * 0.44
            block(
                "Leadlight lancet",
                (x, 15.5, point(0, 15) + zt / 2),
                (0.66, 0.15, zt),
                ["SeaGlass", "Inlay", "WindowLight"][j % 3],
            )
        prop("HAU_N01", "Orrel guarding the depositions", -14, 11, 1.7, -9)
    if k == 3:
        for xx in [-7.5, 7.5]:
            for yy in (-1, 5.1):
                z = point(xx, yy)
                line(
                    "Crane shear legs",
                    (xx, yy, z),
                    (xx * 0.85, 2, z + 6.2),
                    0.24,
                    "Wood",
                )
            ring("Hoist sheave", (xx * 0.84, 1.5, 5.45), 0.55, 0.13, "Brass", "y")
        for j in range(5):
            x = -5.6 + j * 2.8
            line("Truss diagonal", (x, 2, 5.5), (x + 1.4, 2, 6.66), 0.11, "Wood")
            line("Truss return", (x + 1.4, 2, 6.66), (x + 2.8, 2, 5.5), 0.11, "Wood")
        line("Gantry ridge", (-6.9, 2, 6.66), (7, 2, 6.66), 0.15, "Wood")
        prop("FOU_P06", "Gross weight scale", -13, 11, 2.5, 20)
        prop("FOU_P02", "Idle geared winder", 12, 6, 3.65, -28)
        prop("COA_P06", "Unclaimed salt freight", 12, -5, 1.85, 22)
        prop("FOU_N01", "Brannic at the west gantry", -10, -6.6, 1.75, 18)
        lathe(
            "Fixed shipping bell",
            -5.15,
            1.58,
            1.05,
            [(0.28, 0), (0.3, 0.08), (0.16, 0.37), (0.06, 0.44)],
            "Brass",
            9,
            "Pan1",
        )
    if k == 4:
        for sx in [-1, 1]:
            gable(sx * 13.9, 14, 5.5, 5, 3.71)
            line(
                "Crucible overhead track",
                (sx * 5, 0, 6),
                (sx * 5, 12, 6),
                0.21,
                "BellMetal",
            )
            for y in [0, 12]:
                column(sx * 5, y, point(sx * 5, y), 6 - point(sx * 5, y), "Basalt")
        line("Trolley rail", (-5.3, 0.2, 6), (5.3, 0.2, 6), 0.22, "BellMetal")
        for x in [-1.55, 1.55]:
            line("Ladle chain", (x, 0.2, 6), (x * 0.73, 0.2, 3.3), 0.062, "BellMetal")
        lathe(
            "Hanging crucible",
            0,
            0.2,
            2.06,
            [(0.64, 0), (1.0, 0.22), (1.32, 1.20), (1.4, 1.38), (1.12, 1.46)],
            "BellMetal",
            10,
        )
        prop("FOU_P03", "Fettling bench", -13, -2, 1.6, 90)
        prop("LAV_N01", "Ossa by the cooling bed", 10, -7.1, 1.70, -18)
    if k == 5:
        for sx in [-1, 1]:
            x = sx * 12
            archway(x, 13.6, 4.0, 4.6)
            bunting(sx * 14, 3, "NightCloth" if sx < 0 else "Pennon", 5.2)
            for i in range(4):
                y = -9 + 4.6 * i
                z = point(sx * 15, y)
                lathe(
                    "Crystal spire",
                    sx * 15,
                    y,
                    z - 0.13,
                    [
                        (0.48, 0),
                        (0.65, 0.38),
                        (0.44, 2.3 + i * 0.38),
                        (0, 2.85 + i * 0.38),
                    ],
                    "SeaGlass" if sx < 0 else "Amber",
                    5,
                )
        for x in [-8, 8]:
            yy = 3.45
            ring("Mirror armillary", (x, yy, 2.2), 1.01, 0.065, "Brass", "x")
        prop("SKY_P05", "Signal station", -13, -5, 2.6)
    if k == 6:
        for j in range(7):
            a = math.pi * (j + 1) / 8
            x = 15.7 * math.cos(a)
            y = 15.7 * math.sin(a)
            archway(x, y, 2.85, 6 + 0.65 * math.sin(a))
            z = point(x, y)
            for i in range(4):
                xx = x - 1.05 + i * 0.70
                block(
                    "Cobalt observatory glass",
                    (xx, y + 0.32, z + 3.6),
                    (0.60, 0.12, 3.4),
                    "NightCloth",
                )
                lathe(
                    "Star inlay",
                    xx,
                    y + 0.18,
                    z + 2.5 + ((i + j) % 4) * 0.49,
                    [(0.02, 0), (0.15, 0.13), (0.02, 0.29)],
                    "WindowLight",
                    5,
                )
        for j, tag in enumerate(["OakRing", "WrenRing", "TideRing"]):
            pivot = Vector(origins[tag])
            tilt = Matrix.Rotation([0.48, -0.67, 0.88][j], 4, "X")
            for o in batches[tag]:
                o.data.transform(
                    Matrix.Translation(pivot) @ tilt @ Matrix.Translation(-pivot)
                )
        prop("SKY_P06", "Weather cabinet", -13, -1, 2.4, 18)
        prop("RUI_N02", "Surveyor’s familiar", 6, -8, 0.87, 32)
    if k == 7:
        for sx in [-1, 1]:
            for yy in [-6, 4, 14]:
                x = sx * 14
                z = point(x, yy)
                line(
                    "Vault buttress",
                    (x, yy, z - 0.2),
                    (sx * 12.7, yy, 5.8),
                    0.59,
                    "Masonry",
                )
                line(
                    "Vault spring",
                    (sx * 12.7, yy, 5.8),
                    (sx * 6.2, yy, 10.3),
                    0.40,
                    "Masonry",
                )
                bunting(sx * 11.3, yy + 1, "NightCloth" if yy < 0 else "SeaCloth", 4.0)
        lathe(
            "Resonator clapper",
            0,
            0,
            4.15,
            [(0.06, 0), (0.4, 0.24), (0.43, 0.5), (0.15, 0.7), (0.14, 1.05)],
            "Brass",
            10,
        )
        ring("Bell mouth lip", (0, 0, 4.92), 2.64, 0.12, "Brass")
