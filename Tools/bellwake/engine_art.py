"""Build the four Countertide interiors and their full-scale moving mechanisms in Blender."""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from atelier import RES, init, finish, geometry, shaft, lathe, block, marker, origins, model
from works_sets import floor, height, ring, line, pigment
from works_finish import mount, plaques
from sets import arch
from finish_art import bake_ground
from tide_engine import KEYS, TOW, CARGO, FLAGS, FLAGS_NAMED, PLACES, LIFTS
from underworks import rooms

STYLES = (0, 1, 3, 6)
WOOD = "Wood"
COPPER = "BellMetal"
GOLD = "Brass"
STONE = "Masonry"
CLOTH = ("FernCloth", "Amber", "SeaCloth", "CoalCloth")
PALETTE = ("#779d65", "#e7b154", "#4fa4ae", "#635567")


def label_font(size):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


def chart(key, part):
    """Each leaf occupies one quadrant. Its physical pins and engraved lettering agree with the dispatch."""
    w, h = 384, 256
    image = Image.new("RGB", (w * 2, h * 2))
    for j in range(4):
        rng = np.random.default_rng(309 + j + part * 7)
        y, x = np.mgrid[:h, :w]
        shade = (6 * np.cos(x / 130) - 0.04 * abs(y - h / 2) + rng.normal(0, 2.5, (h, w)))[:, :, None]
        page = Image.fromarray(np.uint8(np.clip(np.array([218, 203, 164]) + shade, 0, 255)))
        d = ImageDraw.Draw(page)
        ink = "#302e2b"
        trim = "#89754f"
        red = "#883f34"
        d.rectangle((7, 7, w - 8, h - 8), outline=trim, width=2)
        d.text(
            (22, 15),
            ("HARBOUR EXCHANGE", "CHAINWATER DISPATCH", "THE PATTERN ROOM", "PILOTS’ SIGNAL OFFICE")[
                part
            ],
            font=label_font(14),
            fill=red,
        )
        if part == 1:
            d.text((21, 45), CARGO[j].title(), font=label_font(25), fill=ink)
            for i, n in enumerate(TOW[j]):
                xx = 74 + i * 117
                d.text(
                    (xx, 110), ("CEDAR", "RUSH", "WICK")[i], font=label_font(17), anchor="mm", fill=ink
                )
                d.ellipse((xx - 33, 134, xx + 33, 200), outline=trim, width=3)
                d.text((xx, 165), str(n), font=label_font(43), anchor="mm", fill=red)
            d.text((22, 219), "Berths read from the head of the slip.", font=label_font(14), fill=ink)
        elif part == 2:
            j = min(j, 2)
            n = len(LIFTS[j][0])
            dest = LIFTS[j][1]
            d.text(
                (22, 47),
                ("The handbell", "The harbour bell", "The flood bell")[j],
                font=label_font(27),
                fill=ink,
            )
            for i in range(3):
                xx = 71 + i * 120
                d.line((xx, 101, xx, 194), fill=trim, width=4)
                d.line((xx - 43, 195, xx + 43, 195), fill=trim, width=5)
                if i == dest:
                    for lev in range(n):
                        half = 40 - lev * 6
                        yy = 184 - lev * 14
                        d.rounded_rectangle((xx - half, yy, xx + half, yy + 10), 3, fill=red)
                d.text((xx, 217), PLACES[i].upper(), anchor="mm", fill=ink, font=label_font(16))
        elif part == 3:
            d.text((22, 42), FLAGS_NAMED[j], font=label_font(25), fill=ink)
            for i, abbr in enumerate(("REED", "GOLD", "TIDE", "ASH")):
                xx = 81 + i * 78
                d.text((xx, 91), abbr, anchor="mm", font=label_font(15), fill=ink)
                for l, mask in enumerate(FLAGS[j]):
                    yy = 111 + l * 24
                    d.rectangle(
                        (xx - 23, yy, xx + 23, yy + 16),
                        outline=ink,
                        width=2,
                        fill=PALETTE[i] if mask & (1 << i) else None,
                    )
                    if mask & (1 << i):
                        d.line((xx - 19, yy + 13, xx + 19, yy + 3), fill=ink, width=2)
        else:
            d.text((23, 45), "The last watch", font=label_font(28), fill=ink)
            for i, name in enumerate(("I   CHAINWATER DOCK", "II   MOULD LOFT", "III   SIGNAL LOFT")):
                d.text((29, 105 + i * 32), name, font=label_font(20), fill=red if i == j else ink)
            d.text((23, 214), "Index the drum to open a gallery.", font=label_font(15), fill=ink)
        image.paste(page, (j % 2 * w, j // 2 * h))
    image.save(RES / "Textures" / (key + "Cards.png"))


def panel(name, x, y, z, w, h, material, group="Set", j=None):
    u, v = (0, 0) if j is None else ((j % 2) / 2, (1 - j // 2) / 2)
    span = 1 if j is None else 0.5
    return geometry(
        name,
        [(x - w / 2, y, z), (x + w / 2, y, z), (x + w / 2, y, z + h), (x - w / 2, y, z + h)],
        [(0, 1, 2, 3)],
        material,
        group,
        [(u, v), (u + span, v), (u + span, v + span), (u, v + span)],
    )


def studs(x, y, z, w, h):
    for a in (-1, 1):
        for b in (-1, 1):
            shaft(
                "Forged stud",
                (x + a * w, y, z + b * h),
                (x + a * w, y - 0.07, z + b * h),
                0.07,
                0.045,
                GOLD,
                7,
            )


def slate(k, key, x, y, z, count, w=4.5, h=3):
    for side in (-1, 1):
        block(
            "Reader’s iron pillar",
            (x + side * (w * 0.47), y + 0.08, z + h * 0.38),
            (0.19, 0.24, h * 0.86 + 1),
            "Basalt",
        )
    block("Dispatch frame", (x, y, z + h / 2), (w + 0.24, 0.24, h + 0.24), WOOD)
    for j in range(count):
        panel("Engraved order leaf", x, y - 0.132, z, w, h, key + "Cards", "Order" + str(j), j)
    studs(x, y - 0.14, z + h / 2, w / 2 + 0.055, h / 2 + 0.055)


def shell(k):
    style = STYLES[k]
    mat = ("Masonry", "Shale", "Basalt", "HousePlaster")[k]
    accent = ("BellMetal", "SeaGlass", "Brass", "Wood")[k]
    h = (9.2, 7, 9.8, 8.7)[k]
    # Broad clerestories admit sky above a continuous splayed stone sill.
    for side in (-1, 1):
        for j in range(5):
            t = -16 + 8 * j
            for axis in (0, 1):
                x, y = (side * 20, t) if axis == 0 else (t, side * 20)
                block(
                    "Seawall",
                    (x, y, 1.02),
                    (0.65, 8.05, 4.0) if axis == 0 else (8.05, 0.65, 4.0),
                    mat,
                    "Rim",
                )
                block(
                    "Cornice",
                    (x, y, h - 1.3),
                    (0.78, 8.08, 1.1) if axis == 0 else (8.08, 0.78, 1.1),
                    mat,
                    "Rim",
                )
                lathe(
                    "Buttress",
                    x * 0.965,
                    y * 0.965,
                    -0.25,
                    [
                        (0.74, 0),
                        (0.77, 0.55),
                        (0.48, 0.8),
                        (0.40, h - 1.9),
                        (0.74, h - 1.6),
                        (0.74, h - 0.9),
                    ],
                    accent,
                    8,
                    "Rim",
                )
                for b in (-1, 1):
                    xx = x + (b * 3.65 if axis else 0)
                    yy = y + (0 if axis else b * 3.65)
                    line("Stone window arch", (xx, yy, h - 1.7), (x, y, h - 0.12), 0.23, mat, "Rim", 6)
        for x in (-12, -4, 4, 12):
            if k == 1:
                continue
            y = side * 18.6
            line("Roof truss heel", (x, y, h - 1.8), (x, side * 8, h + 2.8), 0.23, WOOD, "Rim")
            line("Roof tie", (x, side * 8, h + 2.8), (x, 0, h + 4), 0.17, WOOD, "Rim")
            line(
                "Knee brace", (x, side * 15.5, h - 0.46), (x, side * 13.2, h - 1.8), 0.13, accent, "Rim"
            )
    for side in (-1, 1):
        for j in range(6):
            x = side * (22 + j % 2 * 2)
            y = -18 + j * 7
            z = 1.7 + 1.5 * math.sin(j + k)
            lathe(
                "Breakwater stacks",
                x,
                y,
                z - 2,
                [(2.4, 0), (1.7, 3.6), (1.3, 6), (0.34, 7.2)],
                "Shale",
                6,
                "Horizon",
            )
    return style


def wheel(x, y, z, r, group="Set", axis="y", material=GOLD):
    ring("Cast rim", (x, y, z), r, 0.08, material, axis, group, 20)
    for j in range(6):
        a = j * math.tau / 6
        dx = r * math.cos(a)
        q = r * math.sin(a)
        end = (x + dx, y + q, z) if axis == "z" else (x + dx, y, z + q)
        line("Radiused spoke", (x, y, z), end, 0.052, material, group, 6)
    if axis == "y":
        shaft("Hub pin", (x, y + 0.14, z), (x, y - 0.14, z), 0.17, 0.12, COPPER, 10, group)


def depot(k):
    x, y = 0, 4.7
    z = height(STYLES[k], x, y)
    lathe(
        "Drum well", x, y, z - 0.25, [(3.72, 0), (3.72, 0.38), (3.48, 0.54), (3.48, 0.81)], "Basalt", 36
    )
    lathe(
        "Cast distribution table",
        x,
        y,
        z + 0.56,
        [(3.1, 0), (3.15, 0.33), (2.91, 0.48), (2.76, 0.54)],
        COPPER,
        32,
        "Drum",
    )
    for j in range(24):
        a = j * math.tau / 24
        block(
            "Index tooth",
            (x + 3.03 * math.cos(a), y + 3.03 * math.sin(a), z + 0.81),
            (0.36, 0.24, 0.35),
            GOLD,
            "Drum",
            a,
        )
    for j in range(3):
        a = j * math.tau / 3
        line(
            "Spindle brace",
            (x + 2 * math.cos(a), y + 2 * math.sin(a), z + 1.14),
            (x, y, z + 3.4),
            0.19,
            COPPER,
            "Drum",
        )
    lathe("Spindle", x, y, z + 0.9, [(0.6, 0), (0.42, 2.8), (0.64, 3.05), (0.32, 3.4)], GOLD, 12, "Drum")
    line("Index pointer", (x, y, z + 3.96), (x - 2.30, y + 0.529, z + 3.96), 0.17, "Amber", "Drum")
    geometry(
        "Broad arrow",
        [
            (x - 2.73, y + 0.63, z + 4.04),
            (x - 1.81, y + 0.82, z + 4.04),
            (x - 1.97, y + 0.09, z + 4.04),
            (x - 2.08, y + 0.47, z + 4.24),
        ],
        [(0, 1, 3), (1, 2, 3), (2, 0, 3), (0, 2, 1)],
        "Amber",
        "Drum",
    )
    origins["Drum"] = (x, y, z + 0.8)
    for j, (gx, gy) in enumerate(((-10, 7), (0, 12), (10, 7))):
        marker("Bearing" + str(j), gx, gy, z + 0.8)
        gz = height(0, gx, gy)
        lathe(
            "Port lantern",
            gx,
            gy,
            gz + 4.5,
            [(0.39, 0), (0.48, 0.44), (0.30, 0.83), (0.10, 1)],
            "SeaGlass",
            8,
            "ArchLamp" + str(j),
        )
        ring(
            "Seal of service",
            (gx + 2, gy - 0.16, gz + 2.4),
            0.40,
            0.10,
            "Amber",
            "y",
            "Finished" + str(j),
            14,
        )
        for b in (-1, 1):
            line(
                "Flanged pipe",
                (gx + b * 1.9, gy + 0.3, gz + 3.2),
                (gx + b * 1.9, gy + 2, gz + 5.1),
                0.25,
                COPPER,
            )
    for j in range(3):
        xx = -7 + j * 7
        line("Main gallery header", (xx, 18, 5), (xx, 14, 7), 0.46, COPPER)
        ring("Main union", (xx, 16, 6), 0.52, 0.085, GOLD, "y")
    slate(k, KEYS[k], 5.7, 1.4, 1.1, 3, 3.2, 2)
    # The chart follows the mechanical index on this gallery only.


def boat(x, y, z, group, i):
    sections = [
        (-1.48, 0.06, 0.3),
        (-1.12, 0.57, 0.30),
        (-0.57, 0.80, 0.26),
        (0.64, 0.79, 0.27),
        (1.16, 0.51, 0.38),
        (1.49, 0.09, 0.53),
    ]
    pts = []
    for yy, w, sheer in sections:
        pts.extend(
            [
                (x - w, y + yy, z + sheer),
                (x - w * 0.65, y + yy, z - 0.12),
                (x + w * 0.65, y + yy, z - 0.12),
                (x + w, y + yy, z + sheer),
            ]
        )
    faces = []
    for j in range(len(sections) - 1):
        for a in (0, 1, 2, 3):
            faces.append((4 * j + a, 4 * j + (a + 1) % 4, 4 * j + 4 + (a + 1) % 4, 4 * j + 4 + a))
    faces.extend([(3, 2, 1, 0), tuple(range(len(pts) - 4, len(pts)))])
    geometry("Raked chain ferry hull", pts, faces, WOOD, group)
    for j in range(6):
        yy = y - 1 + j * 0.39
        block(
            "Oak thwart",
            (x, yy, z + 0.31),
            (1.04 + 0.25 * math.cos(j), 0.16, 0.09),
            COPPER if j % 4 == 0 else WOOD,
            group,
        )
    lathe("Steering post", x, y + 0.58, z + 0.2, [(0.12, 0), (0.09, 0.82), (0.16, 0.93)], GOLD, 8, group)
    panel(
        "Commission pennant",
        x + 0.23,
        y + 0.58,
        z + 0.78,
        0.54,
        0.32,
        ("FernCloth", "SeaCloth", "Pennon")[i],
        group,
    )
    boat_fittings(x, y, z, group, i)
    for a in (-1, 1):
        ring("Chain eye", (x, y + a * 1.15, z + 0.52), 0.15, 0.045, GOLD, "y", group, 10)


def dock():
    for i, x in enumerate((-5, 0, 5)):
        block("Dressed canal curb", (x, 7.7, 0.47), (3.8, 11.5, 1.12), "Masonry")
        block("Tidal pool", (x, 7.7, 1.03), (3.15, 10.95, 0.08), "Water")
        for dx in (-1.7, 1.7):
            block("Rub rail", (x + dx, 7.7, 1.09), (0.24, 11.25, 0.21), WOOD)
            for j in range(3):
                yy = 4.3 + j * 2.9
                lathe("Berth bollard", x + dx, yy, 1, [(0.13, 0), (0.1, 0.42), (0.16, 0.49)], "Brass", 8)
                for tick in range(j + 1):
                    block(
                        "Berth tally",
                        (x + dx, yy - 0.35 + tick * 0.14, 1.23),
                        (0.22, 0.07, 0.05),
                        "Amber",
                    )
        boat(x, 4.3, 1.1, "Ferry" + str(i), i)
    marker("RailStart", 0, 4, 1)
    marker("RailEnd", 0, 10, 1)
    slate(1, KEYS[1], -8.4, 2.0, 1.10, 4, 3.8, 2.5)
    for side in (-1, 1):
        for j in range(4):
            xx = side * 14
            yy = -4 + j * 5
            lathe(
                "Stacked rope cask",
                xx,
                yy,
                height(1, xx, yy) - 0.06,
                [(0.57, 0), (0.75, 0.35), (0.75, 1.13), (0.56, 1.42)],
                WOOD,
                12,
            )
            for lev in (0.31, 1.04):
                ring("Cask hoop", (xx, yy, height(1, xx, yy) + lev), 0.74, 0.046, COPPER)
    for j in range(7):
        block("Wharf cross-head", (-12 + 4 * j, 14, 2.3), (3.85, 1.12, 0.30), WOOD)


def foundry():
    z = 1.35
    block("Sand-filled moulding pit", (0, 6.1, 0.53), (14.3, 6, 1.38), "Basalt")
    for i, x in enumerate((-5, 0, 5)):
        lathe("Rack bed", x, 5.7, z - 0.22, [(1.83, 0), (1.70, 0.22), (1.59, 0.33)], COPPER, 24)
        shaft("Collar alignment spindle", (x, 5.7, z), (x, 5.7, z + 3.25), 0.087, 0.06, GOLD, 10)
        lathe(
            "Hoist lamp",
            x,
            5.7,
            z + 3.4,
            [(0.16, 0), (0.25, 0.25), (0.15, 0.5)],
            "Amber",
            8,
            "Hook" + str(i),
        )
    for i in range(5):
        radius = 0.58 + 0.21 * i
        g = "Collar" + str(i)
        pts = []
        fs = []
        for layer, (rad, zz) in enumerate(
            (
                (radius - 0.12, 0),
                (radius, 0.045),
                (radius + 0.04, 0.14),
                (radius, 0.33),
                (radius - 0.14, 0.38),
                (radius - 0.20, 0.29),
                (radius - 0.20, 0.07),
            )
        ):
            for j in range(24):
                a = j * math.tau / 24
                pts.append((-5 + rad * math.cos(a), 5.7 + rad * math.sin(a), z + zz))
                fs.append(
                    (
                        layer * 24 + j,
                        layer * 24 + (j + 1) % 24,
                        ((layer + 1) % 7) * 24 + (j + 1) % 24,
                        ((layer + 1) % 7) * 24 + j,
                    )
                )
        geometry(
            "Turned mould jacket",
            pts,
            fs,
            ("Brass", "BellMetal", "VerdigrisSheet", "HarbourBrick", "Basalt")[i],
            g,
        )
        for rise in (0.10, 0.30):
            ring(
                "Cast mould lip",
                (-5, 5.7, z + rise),
                radius,
                0.13,
                (GOLD, COPPER, "Shale", "Brass", "Basalt")[i],
                "z",
                g,
                24,
            )
        for j in range(8):
            a = j * math.tau / 8
            block(
                "Mould seam clamp",
                (-5 + radius * math.cos(a), 5.7 + radius * math.sin(a), z + 0.20),
                (0.22, 0.17, 0.37),
                COPPER,
                g,
                a,
            )
    marker("RailStart", -5, 5.7, z)
    marker("RailEnd", 5, 5.7, z)
    for x in (-8, 8):
        block("Travelling crane upright", (x, 6, 3.6), (0.46, 0.62, 7.6), WOOD)
        for side in (-1, 1):
            line("Kingpost knee", (x, 6, 4.2), (x + side * 1.7, 6, 7.3), 0.18, COPPER)
    block("Flitch beam", (0, 6, 7.6), (17.8, 0.66, 0.45), WOOD)
    for x in (-5, 0, 5):
        wheel(x, 5.6, 7.2, 0.58, material=COPPER)
        line("Pendant chain", (x, 5.64, 6.7), (x, 5.64, 5.12), 0.055, GOLD)
    slate(2, KEYS[2], -9.2, 1.8, 1.15, 3, 4.1, 2.7)
    for j in range(4):
        x = -13 + j * 8.5
        y = 15
        lathe(
            "Brick cupola furnace",
            x,
            y,
            -0.3,
            [(1.63, 0), (1.4, 3.9), (0.94, 4.7), (0.64, 7.1), (0.79, 7.3)],
            "Basalt",
            12,
        )
        panel("Fire door", x, y - 1.43, 1.25, 0.82, 0.56, "Amber")


def loft():
    base = 0.9
    block("Loom plinth", (0, 7, 0.40), (12.6, 7.6, 1.2), "Masonry")
    for x in (-5.8, 5.8):
        for yy in (4.2, 9.7):
            block("Loom castle", (x, yy, 3.2), (0.46, 0.55, 5.0), WOOD)
            line("Castle knee", (x, yy, 4.23), (x - math.copysign(1.5, x), yy, 5.62), 0.15, COPPER)
    for yy in (4.2, 9.7):
        shaft("Warp beam", (-6, yy, 5.65), (6, yy, 5.65), 0.24, 0.24, WOOD, 12)
    for i in range(4):
        x = -4.2 + 2.8 * i
        g = "Heddle" + str(i)
        for dx in (-0.82, 0.82):
            line("Heddle upright", (x + dx, 5.5, 2.2), (x + dx, 5.5, 4.3), 0.06, GOLD, g)
        for zz in (2.2, 4.3):
            line("Heddle bar", (x - 0.85, 5.5, zz), (x + 0.85, 5.5, zz), 0.07, WOOD, g)
        for j in range(7):
            sx = x - 0.73 + j * 0.245
            line("Coloured warp", (sx, 5.5, 2.28), (sx, 5.5, 4.23), 0.034, CLOTH[i], g, 5)
            line("Spun warp", (sx, 5.6, 3.58), (sx, 9.6, 5.53), 0.028, CLOTH[i], "Set", 5)
        panel("Last completed ensign", -8 + i * 5.3, 13, 5, 2.5, 2.8, "PilotEnsigns", "Flag" + str(i), i)
    slate(3, KEYS[3], -9.25, 2.05, 1.15, 4, 4.5, 3.0)
    for i in range(5):
        z = 1.15 + (256 - (119 + i * 24)) / 256 * 3.0
        lathe(
            "Reading bead",
            -11.72,
            1.85,
            z - 0.12,
            [(0.11, 0), (0.16, 0.12), (0.10, 0.23)],
            "Amber",
            8,
            "Row" + str(i),
        )
        panel("Woven pick", 0, 3.9, 1.22 + i * 0.16, 9.6, 0.16, CLOTH[i % 4], "Cloth" + str(i))
    for x in (-14, 14):
        for j in range(5):
            y = -3 + j * 3.5
            z = height(6, x, y)
            shaft("Dyed yarn bobbin", (x, y, z + 0.12), (x, y, z + 1.3), 0.43, 0.41, CLOTH[j % 4], 12)
            for lev in (0.12, 1.31):
                lathe("Bobbin flange", x, y, z + lev, [(0.55, 0), (0.55, 0.10)], WOOD, 12)


def make(k, lib):
    key = KEYS[k]
    style = STYLES[k]
    r = next(q for q in rooms if q["key"] == key)
    workshop_paint()
    pigment(style, r)
    chart(key, k)
    plaques(style, r)
    init(lib, 805 + k)
    floor(style, key)
    shell(k)
    envelope(k)
    if k == 0:
        depot(k)
    elif k == 1:
        dock()
    elif k == 2:
        foundry()
    else:
        loft()
    for j, s in enumerate(r["stations"]):
        x, y = s["x"], s["y"]
        z = height(style, x, y)
        if s["style"] == "person":
            model(
                ("WZ_VIL_N03", "WZ_SWA_N01", "WZ_FOU_N01", "WZ_VIL_N01")[k],
                s["label"],
                x,
                y,
                z - 0.03,
                1.74,
                0,
                "Speaker",
            )
        elif s["style"] == "keepsake":
            from kitchen_art import keepsake
            keepsake(k,x,y,z)
        elif s["style"] == "lift":
            arch(x, y, z - 0.08, 2.95, 3.15, "Basalt", GOLD)
            for side in (-1, 1):
                block("Wicket jamb", (x + side * 1.56, y - 0.12, z + 1.32), (0.34, 0.57, 2.82), WOOD)
        else:
            lathe(
                "Machined pedestal",
                x,
                y,
                z - 0.09,
                [(0.63, 0), (0.63, 0.27), (0.41, 0.43), (0.36, 1.05), (0.54, 1.17)],
                "Basalt",
                10,
            )
            kind = s["style"]
            if kind == "gong":
                ring("Suspended test gong", (x, y, z + 1.65), 0.53, 0.11, GOLD, "y")
                shaft(
                    "Hammer",
                    (x + 0.47, y - 0.1, z + 1.65),
                    (x + 0.66, y - 0.12, z + 2.1),
                    0.06,
                    0.08,
                    WOOD,
                    6,
                )
                shaft(
                    "Striking boss",
                    (x, y + 0.05, z + 1.65),
                    (x, y - 0.04, z + 1.65),
                    0.41,
                    0.38,
                    COPPER,
                    12,
                )
            elif kind == "treadle":
                i = ("Reed", "Gold", "Tide", "Ash").index(s["id"][2:])
                block("Ribbed treadle", (x, y, z + 1.25), (0.75, 0.69, 0.16), CLOTH[i])
                for a in (-1, 0, 1):
                    block("Grip strip", (x, y + a * 0.18, z + 1.35), (0.60, 0.04, 0.05), GOLD)
            elif kind == "crane":
                line("Crane handle", (x, y, z + 1.2), (x, y - 0.15, z + 1.88), 0.082, COPPER)
                shaft(
                    "Handle grip",
                    (x - 0.32, y - 0.15, z + 1.88),
                    (x + 0.32, y - 0.15, z + 1.88),
                    0.09,
                    0.09,
                    WOOD,
                    8,
                )
            else:
                wheel(x, y, z + 1.52, 0.61, axis="z")
                for n in range(3):
                    a = n * math.tau / 3
                    lathe(
                        "Turning knob",
                        x + 0.58 * math.cos(a),
                        y + 0.58 * math.sin(a),
                        z + 1.49,
                        [(0.065, 0), (0.09, 0.31)],
                        WOOD,
                        8,
                    )
        mount(s, style, r, j, height)
        marker(s["id"], x, y - 0.45, z + 1.42)
        if s["style"] not in ("person", "lift"):
            sname = "Rest" + s["id"][2:]
            marker(sname, x, y - 2.25, height(style, x, y - 2.25) + 0.08)
    marker("Spawn", 0, -14, 0.08)
    marker("Look", 0, -4, 1.4)
    bake_ground(key, lambda xx, yy: height(style, xx, yy))
    finish(key, sky_key=r["theme"])


def workshop_paint():
    """Small repeatable industrial tiles, painted in palette ramps with edge highlights."""
    h = w = 96
    y, x = np.mgrid[:h, :w]
    rng = np.random.default_rng(42661)
    grit = rng.normal(0, 3.3, (h, w)) + 3 * np.sin(x * 0.4 + np.sin(y * 0.21) * 1.2)
    for name, base, pattern in (
        ("HarbourBrick", (131, 80, 55), "brick"),
        ("TarredOak", (86, 69, 53), "wood"),
        ("VerdigrisSheet", (75, 113, 104), "iron"),
    ):
        rgb = np.zeros((h, w, 3)) + base + grit[:, :, None]
        if pattern == "brick":
            row = y // 16
            xx = (x + row % 2 * 16) % 32
            yy = y % 16
            rng2 = np.random.default_rng(81)
            values = rng2.normal(0, 9, (6, 3))
            rgb += values[row, ((x + row % 2 * 16) // 32) % 3][:, :, None]
            rgb[(xx == 0) | (yy == 0)] = [61, 54, 49]
            rgb[(xx == 1) | (yy == 1)] = [91, 77, 66]
            rgb[(xx == 2) | (yy == 2)] += 14
        elif pattern == "wood":
            rgb += (
                6 * np.sin(x * 0.82 + 0.45 * np.cos(y * 0.1)) + 4 * np.sin(x * 0.28 + np.sin(y * 0.22))
            )[:, :, None]
            rgb[x % 24 == 0] -= 23
            rgb[x % 24 == 1] += 8
        else:
            rgb += (-8 * np.exp(-(x % 48) / 9) + 4 * np.sin(y / 7 + x / 13))[:, :, None]
            rgb[(x % 48 == 0) | (y % 48 == 0)] -= 27
            rgb[(x % 48 == 1) | (y % 48 == 1)] += 14
        im = Image.fromarray(np.uint8(np.clip(rgb, 0, 255)))
        d = ImageDraw.Draw(im)
        if pattern in ("iron", "wood"):
            for px in range(4, w, 24 if pattern == "wood" else 48):
                for py in range(5, h, 48):
                    d.ellipse((px - 1, py - 1, px + 2, py + 2), fill="#443f34")
                    d.point((px, py - 1), fill="#b8aa7f")
        im.save(RES / "Textures" / (name + ".png"))
    image = Image.new("RGB", (256, 192))
    for j, rows in enumerate(FLAGS):
        im = Image.new("RGB", (128, 96), "#b9a57d")
        d = ImageDraw.Draw(im)
        for a in range(4):
            for b in range(len(rows)):
                px = 8 + a * 28
                py = 9 + int(b * 76 / len(rows))
                d.rectangle(
                    (px, py, px + 26, 9 + int((b + 1) * 76 / len(rows)) - 2),
                    fill=PALETTE[a] if rows[b] & (1 << a) else "#d6caa8",
                )
        for x0 in range(0, 128, 6):
            d.line((x0, 0, x0, 95), fill="#96886d", width=1)
        d.rectangle((3, 3, 124, 92), outline="#684d32", width=2)
        image.paste(im, (128 * (j % 2), 96 * (j // 2)))
    image.save(RES / "Textures/PilotEnsigns.png")


def boat_fittings(x, y, z, g, i):
    # Separate silhouettes for the pilot launch, cargo punt and lamp tender.
    for side in (-1, 1):
        pts = [
            (x + side * w, y + a, z + h)
            for a, w, h in [
                (-1.4, 0.12, 0.33),
                (-0.90, 0.69, 0.32),
                (0.62, 0.8, 0.30),
                (1.23, 0.43, 0.45),
                (1.45, 0.1, 0.49),
            ]
        ]
        for start, end in zip(pts, pts[1:]):
            line("Painted gunwale", start, end, 0.064, ("Pennon", "SeaCloth", "Amber")[i], g, 6)
    if i == 0:
        block("Varnished pilothouse", (x, y - 0.13, z + 0.72), (0.95, 1.18, 0.86), "TarredOak", g)
        panel("Forward pilot glass", x, y - 0.73, z + 0.67, 0.67, 0.38, "WindowLight", g)
        block("Copper cabin roof", (x, y - 0.13, z + 1.2), (1.14, 1.39, 0.15), "VerdigrisSheet", g)
        shaft(
            "Ship’s funnel",
            (x + 0.31, y + 0.32, z + 1.21),
            (x + 0.31, y + 0.32, z + 1.75),
            0.13,
            0.14,
            "Basalt",
            10,
            g,
        )
    elif i == 1:
        for j, (dx, dy, h) in enumerate(((-0.33, -0.54, 0.58), (0.32, -0.43, 0.89), (0, 0.43, 0.66))):
            block("Dispatch crate", (x + dx, y + dy, z + 0.3 + h / 2), (0.51, 0.7, h), "TarredOak", g)
            for sy in (-0.22, 0.22):
                block("Rope strap", (x + dx, y + dy + sy, z + 0.34 + h), (0.52, 0.065, 0.075), GOLD, g)
    else:
        for dx, dy in ((-0.35, -0.45), (0.33, -0.45), (0, 0.22)):
            lathe(
                "Tallow drum",
                x + dx,
                y + dy,
                z + 0.30,
                [(0.23, 0), (0.28, 0.18), (0.28, 0.63), (0.22, 0.78)],
                "VerdigrisSheet",
                12,
                g,
            )
        shaft(
            "Stern lantern stand",
            (x, y + 0.83, z + 0.37),
            (x, y + 0.83, z + 1.79),
            0.065,
            0.055,
            GOLD,
            6,
            g,
        )
        lathe(
            "Storm lantern", x, y + 0.83, z + 1.72, [(0.15, 0), (0.2, 0.22), (0.13, 0.43)], "Amber", 8, g
        )
    shaft("Tiller blade", (x, y + 1.04, z + 0.26), (x, y + 1.48, z - 0.1), 0.09, 0.135, "Basalt", 6, g)


def envelope(k):
    eave = (7.4, 5.6, 7.6, 6.8)[k]
    # Three covered buildings and the open centre of a dockside arcade.
    for side in (-1, 1):
        x0 = side * 20.25
        x1 = side * (12 if k == 1 else 1.9)
        rise = (4.1, 2, 4.8, 4.25)[k]
        roof = ("VerdigrisSheet", "RoofSlate", "Basalt", "TarredOak")[k]
        cross = (x1 - x0, rise)
        for j in range(5):
            y = -20 + j * 8
            if k != 1 or j in (0, 1, 3, 4):
                geometry(
                    "Deep pitched underside",
                    [(x0, y, eave), (x1, y, eave + rise), (x1, y + 8, eave + rise), (x0, y + 8, eave)],
                    [(0, 1, 2, 3)],
                    roof,
                    "Rim",
                )
            for yy in (y + 0.08, y + 4):
                line(
                    "Paired roof rafter",
                    (x0, yy, eave - 0.12),
                    (x1, yy, eave + rise - 0.12),
                    0.24,
                    "TarredOak",
                    "Rim",
                )
                if k != 1:
                    line(
                        "Forged collar tie",
                        (x1, yy, eave + rise - 0.3),
                        (-x1, yy, eave + rise - 0.3),
                        0.13,
                        COPPER,
                        "Rim",
                    )
            for t in (0.17, 0.46, 0.76):
                xx = x0 + t * cross[0]
                zz = eave + t * rise - 0.09
                line("Purlin", (xx, y, zz), (xx, y + 8.02, zz), 0.115, "TarredOak", "Rim")
        if k != 1:
            for j in range(10):
                y = -20 + j * 4
                if j % 3 != 1:
                    geometry(
                        "High lantern glazing",
                        [
                            (0, y, eave + rise + 0.65),
                            (x1, y, eave + rise),
                            (x1, y + 4, eave + rise),
                            (0, y + 4, eave + rise + 0.65),
                        ],
                        [(0, 1, 2, 3)],
                        "SeaGlass",
                        "Rim",
                    )
        for j in range(5):
            yy = -16 + j * 8
            xx = side * 19.61
            for y in (yy - 2.5, yy + 2.5):
                block(
                    "Glazed window reveal",
                    (xx, y, eave * 0.55),
                    (0.24, 0.32, eave * 0.64),
                    "TarredOak",
                    "Rim",
                )
            for h in (3.05, eave - 0.15):
                block("Window sill and lintel", (xx, yy, h), (0.33, 5.32, 0.22), "TarredOak", "Rim")
            if k != 1:
                for a in (-1, 0, 1):
                    block(
                        "Leaded pane",
                        (xx + side * 0.10, yy + a * 1.55, eave * 0.71),
                        (0.12, 1.38, eave * 0.40),
                        "WindowLight" if (j + a) % 3 == 0 else "VerdigrisSheet",
                        "Rim",
                    )
                for vz in (0.57, 0.78):
                    block(
                        "Transom bar",
                        (xx - side * 0.07, yy, eave * vz),
                        (0.13, 5.25, 0.12),
                        "TarredOak",
                        "Rim",
                    )
            if k in (0, 2):
                block("Fired brick spandrel", (xx, yy, 1.34), (0.36, 7.35, 2.8), "HarbourBrick", "Rim")
                block(
                    "Dressed string course",
                    (xx - side * 0.08, yy, 2.79),
                    (0.42, 7.48, 0.22),
                    "Masonry",
                    "Rim",
                )
    if k == 0:
        for side in (-1, 1):
            xx = side * 13.2
            shaft("Rising pressure main", (xx, 12, 1.4), (xx, 12, 7.8), 0.76, 0.65, "VerdigrisSheet", 14)
            for z in (2.15, 3.6, 5.05, 6.50):
                ring("Main seam", (xx, 12, z), 0.75, 0.095, GOLD, "z")
            line("Bent steam elbow", (xx, 12, 7.6), (xx + side * 1.4, 12, 8.9), 0.64, "VerdigrisSheet")
    elif k == 1:
        for side in (-1, 1):
            xx = side * 14.3
            for j in range(3):
                y = 1 + j * 5.4
                z = height(1, xx, y)
                block(
                    "Harbour freight case",
                    (xx + side * 1.7, y, z + 0.51),
                    (1.35, 1.05, 1.1),
                    "TarredOak",
                )
                for a in (-0.40, 0.40):
                    block("Crate binding", (xx + side * 1.7 + a, y, z + 1.10), (0.095, 1.08, 0.08), GOLD)
            line("Derrick mast", (xx, 7, 1), (xx, 7, 7.4), 0.24, "TarredOak")
            line("Hoisting boom", (xx, 7, 5.25), (xx - side * 3.7, 7, 7.25), 0.17, "TarredOak")
            line("Topping lift", (xx, 7, 7.43), (xx - side * 3.7, 7, 7.25), 0.045, COPPER)
            line("Dock fall", (xx - side * 3.7, 7, 7.2), (xx - side * 3.7, 7, 4.47), 0.039, COPPER)
            ring("Stevedore’s hook", (xx - side * 3.7, 7, 4.27), 0.23, 0.055, GOLD, "y")
    elif k == 2:
        for j in range(4):
            x = -13 + j * 8.5
            y = 15
            for side in (-1, 1):
                block("Furnace jamb", (x + side * 0.65, y - 1.49, 2), (0.30, 0.38, 2.15), "HarbourBrick")
            for t in range(7):
                a = t * math.pi / 6
                block(
                    "Fired hearth surround",
                    (x + 0.67 * math.cos(a), y - 1.5, 2.63 + 0.62 * math.sin(a)),
                    (0.29, 0.38, 0.29),
                    "HarbourBrick",
                )
            wheel(x + 1.18, y - 1.43, 2.4, 0.35, material=GOLD)
        for x in (-13.2, 13.2):
            y = 2
            z = height(3, x, y)
            block("Coping bench", (x, y, z + 0.91), (2.85, 1.45, 0.18), "TarredOak")
            for dx in (-1, 1):
                for dy in (-0.5, 0.5):
                    block("Bench feet", (x + dx, y + dy, z + 0.44), (0.19, 0.22, 0.96), "TarredOak")
            lathe(
                "Bell pattern",
                x,
                y,
                z + 1.0,
                [(0.66, 0), (0.63, 0.13), (0.38, 0.38), (0.32, 0.77), (0.12, 0.91)],
                GOLD,
                16,
            )
    else:
        for j in range(6):
            x = -12 + j * 4.8
            y = 15.7
            line("Dyer’s rail", (x - 1.4, y, 5.95), (x + 1.4, y, 5.95), 0.10, WOOD)
            pts = []
            for a in range(8):
                xx = x - 1.25 + a * 0.36
                yy = y + 0.1 * math.sin(a * 1.6)
                pts.extend([(xx, yy, 6), (xx, yy - 0.15, 3.55 + 0.17 * math.cos(a * 0.8 + j))])
            geometry(
                "Vat-dyed hanging",
                pts,
                [(2 * a, 2 * a + 2, 2 * a + 3, 2 * a + 1) for a in range(7)],
                CLOTH[j % 4],
                "Set",
            )
        for side in (-1, 1):
            x = side * 12
            y = -0.2
            z = height(6, x, y)
            lathe(
                "Glazed dye vat",
                x,
                y,
                z - 0.03,
                [(0.86, 0), (1.1, 0.31), (1.16, 1.21), (1.22, 1.31), (1.12, 1.43)],
                "VerdigrisSheet",
                16,
            )
            lathe(
                "Dyebath",
                x,
                y,
                z + 1.42,
                [(1.05, 0), (1.05, 0.025)],
                "Pennon" if side < 0 else "SeaCloth",
                16,
            )
