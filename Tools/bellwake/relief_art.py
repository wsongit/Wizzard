"""Blender-built exhibits and quayside silhouettes for the Mercy Run."""

import math
from atelier import block, shaft, geometry, lathe
from works_sets import ring


def spar(name, a, b, thick, paint, group="Set"):
    return shaft(name, a, b, thick, thick * 0.87, paint, 7, group)


def exhibit(kind, x, y, z, scale=1):
    def pt(a, b, h):
        return (x + a * scale, y + b * scale, z + h * scale)

    def beam(name, a, b, t, paint):
        return spar(name, pt(*a), pt(*b), t * scale, paint)

    def plank(name, centre, size, paint):
        return block(name, pt(*centre), tuple(n * scale for n in size), paint)

    if kind == "rib":
        # A framed section of clinker-built hull displayed in its shores.
        for b in (-0.48, 0, 0.48):
            profile = [
                (-0.88, b, 1.62),
                (-0.63, b, 1.00),
                (-0.27, b, 0.72),
                (0, b, 0.65),
                (0.27, b, 0.72),
                (0.63, b, 1),
                (0.88, b, 1.62),
            ]
            for a, c in zip(profile, profile[1:]):
                beam("Steam-bent oak frame", a, c, 0.09, "Wood")
        for side in (-1, 1):
            beam("Sheer strake", (side * 0.84, -0.6, 1.52), (side * 0.84, 0.62, 1.52), 0.105, "RoofTiles")
            beam("Slipway shore", (side * 0.7, 0, 0.03), (side * 0.5, 0, 0.92), 0.11, "Wood")
        plank("Beech keel", (0, 0, 0.63), (0.18, 1.38, 0.19), "BellMetal")
    elif kind == "float":
        for side in (-1, 1):
            for i in range(3):
                beam(
                    "Tied willow float",
                    (side * (0.45 + i * 0.08), -0.68, 0.23),
                    (side * (0.45 + i * 0.08), 0.68, 0.27),
                    0.094,
                    "Reeds",
                )
            for b in (-0.51, 0.51):
                beam("Float lashings", (-0.7, b, 0.33), (0.7, b, 0.33), 0.055, "Wood")
        lathe(
            "Glazed lamp well",
            x,
            y,
            z + 0.32 * scale,
            [(0.36 * scale, 0), (0.29 * scale, 0.43 * scale), (0.22 * scale, 0.48 * scale)],
            "MossRock",
            10,
        )
        lathe(
            "Reed flame",
            x,
            y,
            z + 0.74 * scale,
            [(0.13 * scale, 0), (0.16 * scale, 0.2 * scale), (0.025 * scale, 0.43 * scale)],
            "Amber",
            7,
        )
    elif kind == "loom":
        for side in (-1, 1):
            beam("Laundry trestle", (side * 0.83, -0.43, 0.04), (side * 0.83, 0.18, 2.21), 0.087, "Wood")
            beam("Laundry brace", (side * 0.83, 0.55, 0.02), (side * 0.83, 0.13, 1.94), 0.074, "Wood")
        beam("Hanging rail", (-1, 0.13, 2.04), (1, 0.13, 2.04), 0.08, "Wood")
        for i, paint in enumerate(("SeaCloth", "Awning", "Pennon")):
            a = -0.72 + 0.52 * i
            verts = [
                pt(a, 0.12, 2.04),
                pt(a + 0.41, 0.12, 2.04),
                pt(a + 0.42, 0.17, 1.23 - 0.11 * i),
                pt(a + 0.21, 0.04, 1.17 - 0.11 * i),
                pt(a, 0.16, 1.25 - 0.11 * i),
            ]
            geometry("Hemmed signal cloth", verts, [(0, 1, 3), (1, 2, 3), (0, 3, 4)], paint)
    elif kind == "kite":
        tail = (0, -0.1, 0.97)
        head = (0, 0.03, 3.26)
        left = (-0.96, 0, 2.42)
        right = (0.96, 0, 2.42)
        for i, (a, b) in enumerate(((head, left), (left, tail), (tail, right), (right, head))):
            geometry(
                "Hand-stitched kite panel",
                [pt(*a), pt(*b), pt(0, -0.17, 2.36)],
                [(0, 1, 2)],
                ("Awning", "Pennon", "Pennon", "SeaCloth")[i],
            )
        beam("Hazel spine", tail, head, 0.044, "Wood")
        beam("Cross spar", left, right, 0.047, "Reeds")
        beam("Tether post", (0, 0.19, 0.02), (0, 0.19, 2.36), 0.063, "Wood")
        for j in range(4):
            a = 0.10 * math.sin(j)
            h = 0.93 - 0.17 * j
            geometry(
                "Knotted red tail",
                [
                    pt(a - 0.16, 0, h + 0.08),
                    pt(a + 0.17, 0, h - 0.08),
                    pt(a + 0.17, 0, h + 0.08),
                    pt(a - 0.16, 0, h - 0.08),
                ],
                [(0, 1, 2), (0, 3, 1)],
                "Pennon",
            )
    elif kind == "dive":
        lathe(
            "Diver's bronze bell",
            x,
            y,
            z + 0.31 * scale,
            [
                (0.72 * scale, 0),
                (0.77 * scale, 0.13 * scale),
                (0.56 * scale, 0.94 * scale),
                (0.27 * scale, 1.26 * scale),
                (0.09 * scale, 1.29 * scale),
            ],
            "Brass",
            12,
        )
        for i in range(6):
            a = math.tau * i / 6
            beam(
                "Bell stiffener",
                (0.72 * math.cos(a), 0.72 * math.sin(a), 0.41),
                (0.34 * math.cos(a), 0.34 * math.sin(a), 1.46),
                0.035,
                "BellMetal",
            )
        ring("Rope eye", pt(0, 0, 1.73), 0.17 * scale, 0.045 * scale, "BellMetal", "y")
    else:
        lathe(
            "Retained oven course",
            x,
            y,
            z - 0.04 * scale,
            [
                (0.85 * scale, 0),
                (0.94 * scale, 0.23 * scale),
                (0.88 * scale, 0.88 * scale),
                (0.68 * scale, 1.37 * scale),
                (0.24 * scale, 1.57 * scale),
            ],
            "RoofTiles",
            10,
        )
        plank("Brick oven lip", (0, -0.79, 0.54), (1.07, 0.42, 0.18), "Masonry")
        plank("Ember mouth", (0, -0.79, 0.84), (0.67, 0.16, 0.47), "Basalt")
        for j in range(5):
            a = math.pi * (j + 0.5) / 5
            plank(
                "Burnished arch brick",
                (0.46 * math.cos(a), -0.76, 0.78 + 0.37 * math.sin(a)),
                (0.19, 0.21, 0.18),
                "OchrePlaster",
            )
        lathe(
            "Off-centre clay flue",
            x + 0.31 * scale,
            y + 0.17 * scale,
            z + 1.3 * scale,
            [(0.19 * scale, 0), (0.15 * scale, 0.69 * scale), (0.23 * scale, 0.76 * scale)],
            "RoofTiles",
            8,
        )


def landings(index, sites, k):
    from pilgrim_art import elevation
    from pilgrim import world

    paint = ["SeaCloth", "FernCloth", "Awning", "Pennon", "SeaCloth", "OchrePlaster"][index]
    kind = ["rib", "float", "loom", "kite", "dive", "oven"][index]
    # The monuments rise from the quay on piled masonry, beyond the playable bank.
    block("Quay footings", (-13, 66, -3.1), (16, 11, 7.7), "Masonry", "Horizon")
    block("Slipway capstone", (-13, 66, 0.88), (15.6, 10.8, 0.44), "MossRock", "Horizon")
    exhibit(kind, -13, 66, 1.1, 5.7)
    for j, site in enumerate(sites[1:-1]):
        x, y = world(site)
        x += 2.36
        y += 2.33
        z = float(elevation(k, x, y))
        spar("Mooring upright", (x, y, z - 0.16), (x, y, z + 2.35), 0.11, "Wood")
        spar("Ensign yard", (x - 0.48, y, z + 2.19), (x + 0.48, y, z + 2.19), 0.057, "Brass")
        geometry(
            "Passenger ensign",
            [
                (x - 0.39, y, z + 2.17),
                (x + 0.39, y, z + 2.17),
                (x + 0.29, y - 0.08, z + 1.48),
                (x, y - 0.14, z + 1.62),
                (x - 0.29, y - 0.08, z + 1.48),
            ],
            [(0, 1, 3), (1, 2, 3), (0, 3, 4)],
            paint,
        )


def seal_press(x, y, z, index):
    from pilgrim_art import tray
    from relief import REACHES

    tray(x, y, z)
    for side in (-1, 1):
        block("Handpress cheek", (x + 0.48 * side, y, z + 1.34), (0.12, 0.42, 0.65), "BellMetal")
    block("Screw crosshead", (x, y, z + 1.68), (1.12, 0.40, 0.14), "Brass")
    spar("Press screw", (x, y, z + 1.35), (x, y, z + 1.92), 0.077, "BellMetal")
    spar("Hand wheel bar", (x - 0.38, y, z + 1.86), (x + 0.38, y, z + 1.86), 0.051, "Wood")
    for n in range(4):
        # UVs select a different engraving on the district's low-resolution evidence strip.
        a, b = n / 4, (n + 1) / 4
        name = "DieFace" + str(n)
        geometry(
            "Enamel evidence plate",
            [
                (x - 0.37, y - 0.36, z + 1.13),
                (x + 0.37, y - 0.36, z + 1.13),
                (x + 0.37, y - 0.36, z + 1.55),
                (x - 0.37, y - 0.36, z + 1.55),
            ],
            [(0, 1, 2, 3)],
            REACHES[index][0] + "Dies",
            name,
            [(a, 0), (b, 0), (b, 1), (a, 1)],
        )


def print_dies(index):
    from PIL import Image, ImageDraw, ImageFont
    from atelier import RES
    from relief import DIES, REACHES

    im = Image.new("RGB", (512, 64), "#34382f")
    pen = ImageDraw.Draw(im)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 13)
    for i, label in enumerate(("blank",) + DIES[index][0]):
        x = 128 * i
        pen.rounded_rectangle((x + 3, 3, x + 124, 60), 5, fill="#e0c591", outline="#886a40", width=3)
        for j in range(i):
            px = x + 64 + (j - (i - 1) / 2) * 11
            pen.polygon([(px, 10), (px + 4, 16), (px, 22), (px - 4, 16)], fill="#7f4936")
        pen.text((x + 64, 37), label, font=font, anchor="mm", fill="#34342c")
    im.save(RES / "Textures" / (REACHES[index][0] + "Dies.png"))
