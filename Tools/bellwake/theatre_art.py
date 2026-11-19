"""Tavi's courtyard and a working miniature proscenium. Dimensions are in metres."""

import math
import random
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from atelier import (
    ROOT,
    RES,
    init,
    finish,
    shaft,
    block,
    lathe,
    geometry,
    marker,
    model,
    collision,
    origins,
)
from works_sets import ring, line
from works_finish import plaques, mount
from finish_art import bake_ground
from engine_art import panel
from wrenfall import oak_crown
from sets import arch, bell
from theatre import KEY, ACTS
from underworks import rooms


def height(k, x, y):
    return 0.52 * min(1, max(0, (abs(x) - 10) / 8)) + 0.3 * min(1, max(0, (y - 12) / 6))


def paintings():
    rng = random.Random(1133)
    tex = RES / "Textures"
    yy, xx = np.mgrid[:512, :512]

    def tile(name, scale):
        p = np.asarray(Image.open(tex / (name + ".png")).convert("RGB"))
        return p[(yy * scale // 4) % p.shape[0], (xx * scale // 4) % p.shape[1]].astype(float)

    x, y = xx * 40 / 512 - 20, 20 - yy * 40 / 512
    grass = tile("Grass", 5) * 0.62 + [31, 37, 10]
    path = tile("Setts", 5) * 0.55 + [59, 45, 31]
    d = np.minimum(abs(x + 0.32 * np.sin(y * 0.5)) - 2.4, abs(y + 4.6) - 2.3)
    d = np.minimum(d, np.maximum(abs(x) - 9, abs(y - 3) - 6))
    mix = np.clip(0.55 - d * 1.7, 0, 1)[:, :, None]
    ground = Image.fromarray(np.uint8(np.clip(grass * (1 - mix) + path * mix, 0, 255)))
    ground.save(tex / (KEY + "Ground.png"))
    ground.save(ROOT / ("Tools/bellwake/.web-assets/" + KEY + "Unlit.png"))
    atlas = Image.new("RGB", (640, 384), "#d9c79c")
    font = lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", n)
    for j, title in enumerate(
        ("Tavi's workshop", "The mill lock", "Marn's crossing", "The paper players")
    ):
        im = Image.new("RGB", (320, 192))
        d = ImageDraw.Draw(im)
        sky, land, ink = [
            ((239, 193, 136), (109, 140, 119), (88, 61, 62)),
            ((129, 164, 176), (95, 119, 112), (55, 74, 84)),
            ((117, 137, 174), (123, 132, 149), (66, 69, 96)),
            ((210, 180, 147), (157, 130, 107), (93, 64, 58)),
        ][j]
        for row in range(192):
            t = row / 192
            d.line((0, row, 320, row), fill=tuple(round(v * (0.85 + 0.17 * t)) for v in sky))
        d.ellipse((232, 12, 258, 38), fill="#f6d798")
        for layer in range(2):
            pts = [
                (i, 65 + layer * 20 + int(12 * math.sin(i * 0.034 + j) + rng.randrange(-4, 5)))
                for i in range(-3, 327, 8)
            ]
            d.polygon(
                pts + [(325, 160), (0, 160)], fill=tuple(min(255, v + 23 * (1 - layer)) for v in land)
            )
        if j == 0:
            for x, y, w in ((10, 127, 91), (104, 113, 63), (188, 124, 86)):
                d.rectangle((x, y - 38, x + w, y + 13), fill="#d2af83", outline=ink, width=2)
                d.polygon(
                    [(x - 6, y - 36), (x + w * 0.47, y - 68), (x + w + 5, y - 36)],
                    fill="#9d614e",
                    outline=ink,
                    width=2,
                )
                d.line((x + w * 0.49, y - 65, x + w * 0.49, y + 12), fill=ink, width=3)
                for a in (x + 12, x + w - 25):
                    d.rectangle((a, y - 28, a + 11, y - 14), fill="#5b7770", outline=ink)
        elif j == 1:
            d.rectangle((0, 94, 320, 160), fill="#738f91")
            for a in range(3):
                x = 24 + a * 102
                d.rectangle((x, 55, x + 22, 147), fill="#c0b29b", outline=ink, width=2)
                d.rectangle((x - 3, 51, x + 26, 61), fill="#cfc3a8", outline=ink)
                d.line((x + 20, 115, x + 100, 88), fill=ink, width=5)
            for x in range(7, 310, 12):
                d.line((x, 89, x + 7, 86), fill="#d8c8a9")
        elif j == 2:
            d.rectangle((0, 101, 320, 160), fill="#7d9797")
            for x, y in [(24, 109), (149, 119), (226, 104)]:
                d.polygon([(x, y), (x + 66, y), (x + 55, y + 11), (x + 13, y + 11)], fill=ink)
                d.line((x + 31, y, x + 31, y - 45), fill=ink, width=2)
                d.polygon([(x + 28, y - 42), (x + 7, y - 6), (x + 29, y - 6)], fill="#e1c292")
                d.line((x + 32, y - 39, x + 55, y - 3), fill=ink)
        for _ in range(95):
            x = rng.randrange(315)
            y = rng.randrange(125, 160)
            d.line((x, y, x + rng.randint(2, 9), y - 1), fill=land)
        d.rectangle((0, 159, 320, 192), fill="#594942")
        d.text((160, 174), title, anchor="mm", font=font(16), fill="#f6deae")
        d.rectangle((2, 2, 317, 189), outline="#ceae79", width=3)
        atlas.paste(im, (j % 2 * 320, j // 2 * 192))
    atlas.save(tex / "PaperScenes.png")
    cards = Image.new("RGB", (512, 384), "#dfcba4")
    for i, title in enumerate(
        ("The first casting", "The crossing", "The broken hinge", "Until morning")
    ):
        x = i % 2 * 256
        y = i // 2 * 192
        d = ImageDraw.Draw(cards)
        d.rectangle((x + 6, y + 6, x + 249, y + 185), outline="#93554d", width=3)
        d.text((x + 128, y + 35), "THE PAPER PLAY", font=font(16), anchor="mm", fill="#546356")
        d.text(
            (x + 128, y + 76), ("I", "II", "III", "IV")[i], font=font(30), anchor="mm", fill="#97564b"
        )
        d.text((x + 128, y + 122), title, font=font(19), anchor="mm", fill="#4d4b3f")
        d.text(
            (x + 128, y + 157),
            ("Casting pattern", "Ferry log", "River boot", "Second receipt")[i],
            font=font(14),
            anchor="mm",
            fill="#68533e",
        )
    cards.save(tex / "PaperBills.png")


def stage():
    # A deep wooden frame leaves three separate sight lines for scenery, figure and object.
    block("Footlight platform", (0, 5.3, 0.79), (12.4, 3.3, 1.65), "TarredOak")
    block("Apron with gilt lip", (0, 4.0, 1.65), (12.7, 1.16, 0.26), "Wood")
    for i in range(21):
        x = (i - 10) * 0.57
        lathe("Shell footlight", x, 3.67, 1.72, [(0.12, 0), (0.18, 0.13), (0.10, 0.21)], "Brass", 8)
    for side in (-1, 1):
        x = 5.93 * side
        block("Wing enclosure", (x, 5.46, 3.19), (0.9, 3.1, 3.4), "OchrePlaster")
        for y in (3.82, 6.87):
            lathe(
                "Turned proscenium column",
                x,
                y,
                1.59,
                [
                    (0.46, 0),
                    (0.46, 0.20),
                    (0.31, 0.29),
                    (0.33, 0.54),
                    (0.20, 3),
                    (0.33, 3.18),
                    (0.44, 3.24),
                    (0.44, 3.47),
                ],
                "Brass",
                12,
            )
        for j in range(7):
            xx = side * (4.38 + j * 0.19)
            h = 2.65 + 0.27 * math.cos(j * 0.63)
            lathe(
                "Gathered velvet wing",
                xx,
                4.04,
                5.16 - h,
                [(0.09, 0), (0.19, 0.13), (0.13, h * 0.54), (0.19, h)],
                "Pennon",
                7,
            )
        for j in range(3):
            shaft(
                "Gilt fan leaf",
                (x, 3.88, 5.25),
                (x + side * (j - 1) * 0.34, 3.88, 5.86 - abs(j - 1) * 0.15),
                0.14,
                0.035,
                "Brass",
                6,
            )
    block("Painted canopy", (0, 5.46, 5.28), (13.4, 4.24, 0.4), "TarredOak")
    for i in range(11):
        x = (i - 5) * 1.1
        geometry(
            "Scalloped valance",
            [
                (x - 0.56, 3.35, 5.25),
                (x + 0.56, 3.35, 5.25),
                (x + 0.42, 3.35, 4.94),
                (x, 3.32, 4.76),
                (x - 0.42, 3.35, 4.94),
            ],
            [(0, 1, 2, 3, 4)],
            "Pennon",
        )
        lathe("Valance tassel", x, 3.31, 4.59, [(0.03, 0), (0.07, 0.04), (0.04, 0.17)], "Brass", 7)
    for side in (-1, 1):
        geometry(
            "Sloping theatre roof",
            [(side * 7, 3.1, 5.59), (side * 7, 7.78, 5.59), (0, 7.78, 7.34), (0, 3.1, 7.34)],
            [(0, 1, 2, 3)],
            "RoofSlate",
        )
    for x in (-4.1, -2.2, 0, 2.2, 4.1):
        z = 6.73 - 0.25 * abs(x)
        ring("Painted rosette", (x, 3.39, z), 0.16, 0.045, "Brass", "y", n=12)
    for i in range(4):
        x = (i - 1.5) * 0.88
        ring("Marquee lamp bezel", (x, 3.32, 5.37), 0.15, 0.038, "Brass", "y")
        lathe(
            "Lit shell lamp",
            x,
            3.28,
            5.23,
            [(0.055, 0), (0.14, 0.06), (0.14, 0.21), (0.045, 0.28)],
            "Amber",
            8,
            "LitShell" + str(i),
        )
    for j in range(3):
        panel("Printed scenery", 0, 6.78, 1.8, 10.68, 3.28, "PaperScenes", "Place" + str(j), j)
    block("Left programme stand", (-8.0, 2.3, 1.25), (2.55, 0.31, 2.27), "TarredOak")
    for j in range(4):
        panel("Act title", -8, 2.12, 0.43, 2.35, 1.76, "PaperBills", "Playbill" + str(j), j)


def puppet(i):
    g = "Figure" + str(i)
    x = -1.7
    y = 4.88
    z = 1.82
    coat = ("Pennon", "SeaCloth", "FernCloth")[i]
    for j, (xx, h) in enumerate(((-0.22, 0.38), (0.21, 0.36))):
        shaft(
            "Cutout boot",
            (x + xx, y, z + 0.04),
            (x + xx + 0.06, y, z + h),
            0.13,
            0.11,
            "TarredOak",
            7,
            g,
        )
    lathe(
        "Painted articulated coat",
        x,
        y,
        z + 0.30,
        [(0.48, 0), (0.35, 0.41), (0.37, 0.71), (0.16, 0.83)],
        coat,
        8,
        g,
    )
    lathe(
        "Puppet face",
        x,
        y,
        z + 1.09,
        [(0.15, 0), (0.27, 0.13), (0.28, 0.39), (0.18, 0.49)],
        "Skin",
        9,
        g,
    )
    for dx in (-0.10, 0.10):
        block("Ink eye", (x + dx, y - 0.247, z + 1.39), (0.037, 0.029, 0.045), "TarredOak", g)
    if i == 0:
        lathe(
            "Tavi’s swept fringe",
            x,
            y + 0.025,
            z + 1.46,
            [(0.28, 0), (0.27, 0.14), (0.13, 0.18)],
            "Wood",
            8,
            g,
        )
        block("Leather apron", (x, y - 0.32, z + 0.78), (0.46, 0.09, 0.51), "Wood", g)
    if i == 1:
        for side in (-1, 1):
            shaft(
                "Ina’s plait",
                (x + side * 0.21, y + 0.02, z + 1.5),
                (x + side * 0.32, y - 0.01, z + 0.88),
                0.102,
                0.066,
                "Wood",
                7,
                g,
            )
            ring("Ribbon", (x + side * 0.32, y - 0.04, z + 0.92), 0.084, 0.032, "Pennon", "z", g)
    if i == 2:
        lathe(
            "Ferryman’s hat",
            x,
            y,
            z + 1.48,
            [(0.40, 0), (0.40, 0.06), (0.27, 0.07), (0.19, 0.24)],
            "Loam",
            10,
            g,
        )
        lathe(
            "Grey beard",
            x,
            y - 0.12,
            z + 1.04,
            [(0.065, 0), (0.23, 0.18), (0.2, 0.26)],
            "HousePlaster",
            6,
            g,
        )
    for side in (-1, 1):
        shoulder = (x + 0.30 * side, y, z + 0.98)
        elbow = (x + 0.53 * side, y - 0.04, z + 0.72 + 0.12 * (side == 1))
        hand = (x + 0.71 * side, y - 0.13, z + 0.68 + 0.36 * (side == 1))
        arm = "PuppetArm" + str(i) if side == 1 else g
        if side == 1:
            origins[arm] = shoulder
        shaft("Jointed sleeve", shoulder, elbow, 0.11, 0.11, "Brass" if side == 1 else coat, 8, arm)
        shaft("Painted forearm", elbow, hand, 0.088, 0.079, "Brass" if side == 1 else "Skin", 7, arm)
        ring("Paper fastener", elbow, 0.08, 0.025, "Brass", "y", arm, 10)
    for xx in (x - 0.42, x + 0.42):
        shaft("Puppet string", (xx, y, z + 1.05), (xx, y, 4.81), 0.012, 0.012, "Wood", 5, g)


def keepsake(kind, x, y, z, group="Set", scale=1):
    def pos(dx, dy, dz):
        return (x + dx * scale, y + dy * scale, z + dz * scale)

    def piece(name, a, b, r1, r2, m):
        shaft(name, pos(*a), pos(*b), r1 * scale, r2 * scale, m, 9, group)

    if kind == "pin":
        piece("Gate pin", (-0.44, 0, 0.07), (0.39, 0.05, 0.68), 0.105, 0.105, "BellMetal")
        piece("Pin head", (0.33, 0.05, 0.63), (0.46, 0.06, 0.74), 0.19, 0.19, "Brass")
        ring(
            "Split retaining eye",
            pos(-0.38, -0.01, 0.12),
            0.17 * scale,
            0.036 * scale,
            "Brass",
            "y",
            group,
        )
    elif kind == "lantern":
        lathe(
            "Lantern cage",
            x,
            y,
            z,
            [
                (r * scale, h * scale)
                for r, h in (
                    (0.30, 0),
                    (0.33, 0.10),
                    (0.23, 0.20),
                    (0.23, 0.6),
                    (0.38, 0.69),
                    (0.09, 0.94),
                )
            ],
            "Brass",
            8,
            group,
        )
        for j in range(4):
            a = (j + 0.5) * math.tau / 4
            piece(
                "Luminous mica",
                (0.235 * math.cos(a), 0.235 * math.sin(a), 0.18),
                (0.235 * math.cos(a), 0.235 * math.sin(a), 0.61),
                0.081,
                0.08,
                "Amber",
            )
        ring("Bent wire handle", pos(0, 0, 1), 0.20 * scale, 0.027 * scale, "BellMetal", "y", group)
    elif kind == "bell":
        bell(x, y, z, scale, group)
    elif kind == "boot":
        lathe(
            "River boot cuff",
            x,
            y,
            z + 0.19,
            [(0.20, 0), (0.23, 0.12), (0.22, 0.61), (0.27, 0.65), (0.27, 0.73)],
            "Wood",
            9,
            group,
        )
        block("Boot sole", pos(0, -0.22, 0.12), (0.49, 0.81, 0.18), "TarredOak", group)
        lathe(
            "Patched toe",
            x,
            y - 0.32,
            z + 0.16,
            [(0.19, 0), (0.22, 0.09), (0.13, 0.19)],
            "Wood",
            9,
            group,
        )
        for i in range(3):
            piece(
                "Boot lace",
                (-0.14, -0.19, 0.44 + 0.12 * i),
                (0.14, -0.19, 0.48 + 0.12 * i),
                0.019,
                0.019,
                "Brass",
            )
    elif kind in ("log", "carbon"):
        block(
            "Book cover",
            pos(0, 0, 0.04),
            (1.02, 0.71, 0.09),
            "Wood" if kind == "log" else "Pennon",
            group,
        )
        for j in (-1, 1):
            block("Vellum folio", pos(j * 0.23, 0, 0.13), (0.45, 0.65, 0.075), "HousePlaster", group)
            for i in range(4):
                block(
                    "Lines of writing",
                    pos(j * 0.23, -0.2 + i * 0.12, 0.172),
                    (0.34 - 0.04 * (i % 2), 0.016, 0.008),
                    "Wood",
                    group,
                )
    else:
        block("Split casting pattern", pos(0, 0, 0.15), (1, 0.7, 0.3), "Wood", group)
        lathe(
            "Wax bell original",
            x,
            y,
            z + 0.3,
            [(0.27, 0), (0.30, 0.04), (0.17, 0.26), (0.11, 0.32)],
            "Amber",
            12,
            group,
        )


def make(lib):
    r = next(r for r in rooms if r["key"] == KEY)
    paintings()
    plaques(0, r)
    init(lib, 1196)
    points = [(x, y, height(0, x, y)) for y in range(-20, 21, 2) for x in range(-20, 21, 2)]
    o = geometry(
        "Courtyard turf and setts",
        points,
        [
            (j * 21 + i, j * 21 + i + 1, (j + 1) * 21 + i + 1, (j + 1) * 21 + i)
            for j in range(20)
            for i in range(20)
        ],
        KEY + "Ground",
        "Terrain",
    )
    for i, loop in enumerate(o.data.loops):
        x, y, _ = points[loop.vertex_index]
        o.data.uv_layers.active.data[i].uv = ((x + 20) / 40, (y + 20) / 40)
    for x, y, w, d in (
        (0, 20.45, 41, 0.9),
        (0, -20.45, 41, 0.9),
        (-20.45, 0, 0.9, 41),
        (20.45, 0, 0.9, 41),
    ):
        collision("Courtyard boundary", x, y, -2, w, d, 18)
        block("Orchard wall", (x, y, 1.08), (w + 0.04, d + 0.04, 2.61), "MossRock", "Rim")
    for x, y, w, d, h in (
        (-10, 15.1, 8, 4.4, 4.0),
        (5.3, 15.5, 10.2, 4.6, 3.35),
        (16, 1.4, 4, 8.2, 3.5),
    ):
        z = height(0, x, y)
        block("Neighbour’s house", (x, y, z + h / 2 - 0.08), (w, d, h + 0.16), "OchrePlaster")
        for side in (-1, 1):
            geometry(
                "Peg-tile roof",
                [
                    (x + side * (w / 2 + 0.42), y - d / 2 - 0.45, z + h),
                    (x + side * (w / 2 + 0.42), y + d / 2 + 0.45, z + h),
                    (x, y + d / 2 + 0.45, z + h + 1.72),
                    (x, y - d / 2 - 0.45, z + h + 1.72),
                ],
                [(0, 1, 2, 3)],
                "RoofTiles",
            )
        geometry(
            "Closed gable",
            [(x - w / 2, y - d / 2, z + h), (x + w / 2, y - d / 2, z + h), (x, y - d / 2, z + h + 1.72)],
            [(0, 1, 2)],
            "OchrePlaster",
        )
        for dx in (-w * 0.47, -w * 0.23, 0, w * 0.23, w * 0.47):
            block("Front stud", (x + dx, y - d / 2 - 0.04, z + h * 0.51), (0.18, 0.16, h * 1.02), "Wood")
        for dx in (-w * 0.26, w * 0.26):
            block(
                "Shuttered casement",
                (x + dx, y - d / 2 - 0.13, z + h * 0.56),
                (1.15, 0.14, 1.14),
                "TarredOak",
            )
            block("Amber window", (x + dx, y - d / 2 - 0.23, z + h * 0.58), (0.78, 0.06, 0.76), "Amber")
    for j, (x, y) in enumerate(((-15, -8), (16, -10), (-16, 4), (-2, 16), (15, 13))):
        z = height(0, x, y)
        shaft("Pear tree trunk", (x, y, z - 0.06), (x + 0.31, y, z + 3.1), 0.4, 0.21, "Wood", 8)
        oak_crown(x + 0.3, y, z + 3.18, 2.7, 2.5, 139 + j)
    stage()
    for j, kind in enumerate(("pin", "lantern", "bell")):
        puppet(j)
        keepsake(kind, 1.81, 4.87, 2.01, "Prop" + str(j), 1.4)
    for j, s in enumerate(r["stations"]):
        id = s["id"][2:]
        x = s["x"]
        y = s["y"]
        z = height(0, x, y)
        if id == "Talk":
            from tavi_art import make_tavi
            make_tavi(x, y, z, 1.79, 13)
        elif id == "Door":
            arch(x, y, z, 2.6, 3, "Masonry", "Wood")
        else:
            block("Walnut plinth", (x, y, z + 0.45), (1.62, 0.97, 0.93), "TarredOak")
            block("Desk top", (x, y, z + 0.97), (1.72, 1.01, 0.12), "Wood")
            if id in ("Figure", "Place", "Prop"):
                g = "Spool" + id
                shaft(
                    "Reel shaft",
                    (x - 0.57, y, z + 1.27),
                    (x + 0.57, y, z + 1.27),
                    0.10,
                    0.10,
                    "Brass",
                    8,
                )
                ring("Operator’s flywheel", (x, y, z + 1.35), 0.35, 0.07, "Brass", "y", g, 16)
                for i in range(3):
                    a = i * math.tau / 3
                    shaft(
                        "Reel spoke",
                        (x, y, z + 1.35),
                        (x + 0.33 * math.cos(a), y, z + 1.35 + 0.33 * math.sin(a)),
                        0.032,
                        0.032,
                        "Wood",
                        6,
                        g,
                    )
                origins[g] = (x, y, z + 1.35)
            elif id == "Light":
                keepsake("lantern", x, y, z + 1.04, scale=0.66)
            elif id in ("Maker", "Runner"):
                keepsake("carbon", x, y, z + 1.04)
                line(
                    "Goose quill",
                    (x + 0.3, y + 0.1, z + 1.08),
                    (x + 0.55, y + 0.13, z + 1.72),
                    0.034,
                    "HousePlaster",
                )
            else:
                keepsake(
                    dict(Pattern="pattern", Log="log", Boot="boot", Carbon="carbon")[id], x, y, z + 1.04
                )
        marker(s["id"], x, y - 0.5, z + 1.42)
        marker(s["camp"], x, y - 2.2, height(0, x, y - 2.2) + 0.08)
        if id != "Talk":
            label = dict(s)
            if id != "Door":
                label["y"] -= 0.18
            mount(label, 0, r, j, height)
    marker("Spawn", 0, -14, 0.08)
    marker("Look", 0, 4, 1.55)
    bake_ground(KEY, lambda x, y: height(0, x, y))
    finish(KEY, sky_key="PaperLight")


def ticket_poster():
    im = Image.new("RGB", (256, 320), "#e3cb98")
    d = ImageDraw.Draw(im)
    font = lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", n)
    d.rectangle((7, 7, 248, 312), outline="#875847", width=4)
    d.rectangle((14, 15, 241, 305), outline="#62765d", width=2)
    d.text((128, 43), "TAVI & INA'S", font=font(21), anchor="mm", fill="#5e6252")
    d.text((128, 88), "PAPER", font=font(47), anchor="mm", fill="#935248")
    d.text((128, 133), "THEATRE", font=font(34), anchor="mm", fill="#935248")
    d.rectangle((37, 161, 219, 258), fill="#65847d", outline="#8f6241", width=4)
    for side in (-1, 1):
        x = 128 + side * 85
        d.polygon(
            [(x, 164), (x - side * 50, 164), (x - side * 19, 217), (x - side * 25, 251), (x, 251)],
            fill="#a45245",
        )
    for x, c in ((102, "#b99c63"), (151, "#c4a078")):
        d.line((x, 167, x, 191), fill="#e0c69a")
        d.ellipse((x - 9, 187, x + 9, 205), fill="#efcf9a")
        d.polygon([(x - 7, 204), (x + 7, 204), (x + 13, 234), (x - 13, 234)], fill=c)
        d.line((x - 4, 231, x - 7, 248), fill="#473e36", width=4)
        d.line((x + 5, 231, x + 8, 248), fill="#473e36", width=4)
    d.text((128, 281), "COURTYARD DOOR", font=font(17), anchor="mm", fill="#4b5f57")
    im.save(RES / "Textures/PaperTicket.png")


def ticket_door(x, y, z):
    # Front faces the lane. The closed leaves sit beneath a continuous timber lintel.
    for side in (-1, 1):
        xx = x + side * 0.67
        block("Painted playhouse door", (xx, y, z + 1.28), (1.31, 0.26, 2.56), "VerdigrisSheet")
        for h in (0.53, 1.88):
            block("Raised door panel", (xx, y - 0.15, z + h), (1.04, 0.09, 0.73), "SeaCloth")
        block("Oak jamb", (x + side * 1.43, y, z + 1.39), (0.22, 0.5, 2.78), "TarredOak")
        block("Stage door pull", (x + side * 0.19, y - 0.22, z + 1.15), (0.07, 0.08, 0.29), "Brass")
    block("Ticket door lintel", (x, y, z + 2.75), (3.36, 0.7, 0.29), "Wood")
    for side in (-1, 1):
        geometry(
            "Tiled entrance hood",
            [
                (x + side * 1.85, y - 0.65, z + 2.94),
                (x + side * 1.85, y + 0.73, z + 2.94),
                (x, y + 0.73, z + 3.83),
                (x, y - 0.65, z + 3.83),
            ],
            [(0, 1, 2, 3)],
            "RoofTiles",
        )
    geo = [(x - 1.71, y - 0.60, z + 2.94), (x + 1.71, y - 0.60, z + 2.94), (x, y - 0.60, z + 3.8)]
    geometry("Painted pediment", geo, [(0, 1, 2)], "OchrePlaster")
    ring("Ticket rosette", (x, y - 0.63, z + 3.24), 0.17, 0.034, "Brass", "y")
    block("Programme board", (x - 1.82, y - 0.05, z + 1.65), (0.93, 0.19, 1.23), "Wood")
    panel("Playbill at the entrance", x - 1.82, y - 0.16, z + 1.07, 0.86, 1.12, "PaperTicket")
    block("Ticket booth back", (x, y + 0.51, z + 1.37), (3.04, 0.89, 2.76), "OchrePlaster")
    marker("A_Playhouse", x, y - 0.52, z + 1.44)
