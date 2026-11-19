"""Blender models for Ossa's darkroom, adjustable silver mirrors and contact prints."""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from atelier import RES, ROOT, init, finish, geometry, block, shaft, lathe, collision, marker, origins
from works_sets import ring, line
from works_finish import plaques, mount
from engine_art import panel
from finish_art import bake_ground
from sets import arch
from plate_room import KEY, PIVOTS, NAMES, PLATES, ELBOWS, SEGMENTS, SOURCE
from underworks import rooms


def font(size):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)


def artwork():
    rng = np.random.default_rng(3301)
    root = RES / "Textures"
    for name, size, base in (
        ("PressSilver", 64, [149, 178, 177]),
        (KEY + "Ground", 512, [115, 100, 86]),
    ):
        y, x = np.indices((size, size))
        grain = rng.normal(0, 3, (size, size))
        if size == 64:
            grain += 10 * np.sin((x + y * 0.63) / 9) + 4 * np.cos((x - y) / 4)
        else:
            grain += 3 * np.cos(x * 0.06 + y * 0.13) + 4 * np.sin(y * 0.037)
            grain -= 18 * ((y % 21 < 1.2) | ((x + 21 * (y // 21 % 2)) % 42 < 1.2))
            for k in (-8, 0, 8):
                grain += np.maximum(0, 1 - np.abs((x - 256) * 40 / 512 - k) * 7) * 8
        im = Image.fromarray(np.uint8(np.clip(np.array(base) + grain[..., None], 0, 255)))
        im.save(root / (name + ".png"))
        if size == 512:
            im.save(ROOT / "Tools/bellwake/.web-assets" / (KEY + "Unlit.png"))
    # Small variegated tiles with offset seams keep long roof bays legible.
    py, px = np.indices((128, 128))
    yy = py // 16
    xx = (px + 8 * (yy % 2)) // 16
    seam = np.minimum((px + 8 * (yy % 2)) % 16, py % 16)
    mottling = 10 * np.sin(xx * 4 + yy * 6) + 3 * np.cos(py * 0.61) + rng.normal(0, 2.5, (128, 128))
    relief = np.where(seam < 1, -25, np.where(seam < 2, 12, 0))
    pigment = np.array([93, 113, 103]) + (mottling + relief)[..., None]
    Image.fromarray(np.uint8(np.clip(pigment, 0, 255))).save(root / "KilnGlaze.png")
    sheet = Image.new("RGB", (768, 544), "#dfd0a3")
    d = ImageDraw.Draw(sheet)
    mapxy = lambda p: (int(16 + (p[0] + 20) * 12), int(512 - (p[1] + 20) * 12))
    d.rectangle((16, 32, 496, 512), fill="#c2b18c", outline="#493b30", width=3)
    for a, b, c in SEGMENTS:
        d.line([mapxy(a), mapxy(b)], fill="#94846a", width=4)
    for point, label in zip(PIVOTS, NAMES):
        x, y = mapxy(point)
        d.ellipse((x - 10, y - 10, x + 10, y + 10), fill="#694b36", outline="#faf0c9", width=2)
        d.text((x + 11, y + 1), label, font=font(15), fill="#392e24")
    for point in ELBOWS:
        x, y = mapxy(point)
        d.rectangle((x - 7, y - 7, x + 7, y + 7), fill=("#366f85" if point[1] > 0 else "#ad6b26"))
    for point, col, n, *_ in PLATES:
        x, y = mapxy(point)
        d.rectangle((x - 10, y - 8, x + 10, y + 8), fill="#e7dbbe", outline="#473b2e", width=2)
        d.text((x, y - 16), n, font=font(14), anchor="ms", fill="#302b27")
    x, y = mapxy(SOURCE)
    d.ellipse((x - 7, y - 7, x + 7, y + 7), fill="#fff7d9")
    for i, (t, sz) in enumerate(
        [
            ("THE PLATE ROOM", 24),
            ("Ossa’s exposure book", 18),
            ("I    CRADLE", 19),
            ("Cold blue · north wall", 16),
            ("II   LADDER", 19),
            ("Warm gold · south wall", 16),
            ("III  HAND", 19),
            ("Cold blue · north wall", 16),
            ("Follow one shaft of light.", 16),
            ("At each silver mirror", 16),
            ("the ray turns 90°.", 16),
        ]
    ):
        d.text((513, 40 + i * 34), t, font=font(sz), fill="#4e3d32")
    sheet.save(root / (KEY + "Survey.png"))
    for i, (_, _, name, *_) in enumerate(PLATES):
        bg, mid, light = [
            ("#263f54", "#7596a1", "#d0d4bc"),
            ("#5a4232", "#aa8962", "#ead2a2"),
            ("#263d52", "#7896a5", "#ded8bd"),
        ][i]
        im = Image.new("RGB", (320, 224), bg)
        d = ImageDraw.Draw(im)
        d.rectangle((7, 7, 312, 216), outline=light, width=2)
        d.polygon(
            [
                (13, 102),
                (55, 71),
                (80, 80),
                (110, 56),
                (149, 87),
                (179, 69),
                (218, 86),
                (246, 54),
                (305, 88),
                (305, 117),
                (13, 117),
            ],
            fill=mid,
        )
        for j in range(21):
            xx = int(rng.integers(15, 270))
            yy = int(rng.integers(119, 175))
            d.line((xx, yy, xx + int(rng.integers(12, 41)), yy - 2), fill=mid, width=1)
        if i == 0:
            d.polygon(
                [(36, 131), (85, 149), (246, 148), (280, 119), (262, 151), (237, 162), (87, 162)],
                fill=light,
            )
            d.arc((98, 68, 204, 147), 0, 180, fill=light, width=7)
            d.line([(98, 108), (203, 108), (195, 98), (180, 88)], fill=light, width=4)
            d.arc((138, 79, 194, 122), 187, 346, fill=light, width=3)
            for a in range(6):
                d.line((112 + 13 * a, 114, 118 + 12 * a, 132), fill=mid, width=2)
        elif i == 1:
            d.polygon([(178, 61), (269, 61), (271, 148), (181, 148)], fill=mid)
            d.polygon([(162, 67), (223, 30), (285, 66)], fill=light)
            d.rectangle((201, 90, 226, 141), fill=bg)
            for a in (0, 24):
                d.line((80 + a, 164, 153 + a, 67), fill=light, width=5)
            for a in range(8):
                d.line((86 + a * 9, 156 - a * 12, 108 + a * 9, 156 - a * 12), fill=light, width=3)
            d.line((180, 82, 270, 82), fill=light, width=2)
        else:
            for x in range(40, 290, 26):
                d.rectangle((x, 90, x + 10, 159), fill=mid)
            d.polygon(
                [
                    (91, 163),
                    (117, 135),
                    (113, 112),
                    (94, 91),
                    (100, 84),
                    (124, 103),
                    (123, 66),
                    (130, 62),
                    (137, 101),
                    (144, 52),
                    (151, 49),
                    (151, 99),
                    (164, 58),
                    (171, 56),
                    (164, 106),
                    (179, 76),
                    (186, 77),
                    (173, 125),
                    (155, 148),
                    (139, 171),
                ],
                fill=light,
            )
            d.polygon([(85, 166), (113, 133), (151, 158), (130, 178)], fill=mid)
            d.line(
                [(105, 151), (112, 151), (114, 158), (122, 159), (123, 165), (131, 164)],
                fill=light,
                width=3,
            )
        d.text(
            (159, 188),
            ["I   PELLA’S CROSSING", "II   THE SCHOOL LANDING", "III   THE LEFT HAND"][i],
            font=font(15),
            anchor="mm",
            fill=light,
        )
        noise = rng.normal(0, 3.4, (224, 320, 1))
        im = Image.fromarray(np.uint8(np.clip(np.asarray(im) + noise, 0, 255)))
        im.save(root / ("Proof" + name + ".png"))

    # Keep the three original plates together on a print-shop contact sheet.
    paper = Image.new("RGB", (768, 544), "#d5c8a9")
    ink = ImageDraw.Draw(paper)
    ink.rectangle((15, 15, 752, 527), outline="#796e59", width=2)
    ink.text((38, 32), "THE RIVER WATCH", font=font(30), fill="#37372f")
    ink.text((40, 77), "Ossa’s contact book  /  Flood night, plates I–III", font=font(18), fill="#544837")
    for n, box in zip(("Cradle", "Ladder", "Hand"), ((39, 123), (399, 123), (39, 329))):
        x, y = box
        with Image.open(root / ("Proof" + n + ".png")) as original:
            picture = original.resize((273, 173), Image.Resampling.LANCZOS)
        ink.rectangle((x - 5, y - 5, x + 278, y + 178), fill="#f3e6cb", outline="#8c816c")
        paper.paste(picture, box)
    ink.multiline_text(
        (398, 352),
        "Ina kept her left hand on the\ngate until the boat was clear.\n\nTavi knew her by one stitch.\n\nFiled by Ossa, at first light.",
        font=font(17),
        fill="#51412d",
        spacing=5,
    )
    paper.save(RES / "Letters" / "ContactSheet.jpg", quality=89)


def make(lib):
    r = next(q for q in rooms if q["key"] == KEY)
    artwork()
    plaques(2, r)
    init(lib, 7134)
    geometry(
        "Brick exposure floor",
        [(-20, -20, 0), (20, -20, 0), (20, 20, 0), (-20, 20, 0)],
        [(0, 1, 2, 3)],
        KEY + "Ground",
        "Terrain",
        [(0, 0), (1, 0), (1, 1), (0, 1)],
    )
    for axis in (0, 1):
        for side in (-1, 1):
            x, y = (20.35 * side, 0) if axis == 0 else (0, 20.35 * side)
            w, d = (0.75, 41.5) if axis == 0 else (41.5, 0.75)
            collision("Sealed skylight foundation", x, y, -2, w, d, 18)
            block("Darkroom brick sill", (x, y, 1.25), (w, d, 3.1), "Masonry", "Rim")
            block("Window header", (x, y, 6.8), (w, d, 0.33), "Wood", "Rim")
            for k in range(-18, 20, 4):
                xx, yy = (x, k) if not axis else (k, y)
                block("Sash mullion", (xx, yy, 4.83), (0.17, 0.17, 4.00), "Wood", "Rim")
                if k % 8 == -2 or k in (-18, 14):
                    lathe(
                        "Kiln roof column",
                        xx * 0.96,
                        yy * 0.96,
                        -0.1,
                        [(0.45, 0), (0.48, 0.35), (0.28, 0.53), (0.26, 6.45), (0.45, 6.66)],
                        "Basalt",
                        8,
                        "Rim",
                    )
    # Open ridge monitors admit the sunset. The lower roof is boarded and tiled.
    for side in (-1, 1):
        for x in range(-20, 20, 4):
            eave, peak = 20 * side, 4.4 * side
            corners = [(x, eave, 6.90), (x + 4, eave, 6.90), (x + 4, peak, 9.74), (x, peak, 9.74)]
            # A solid board has separate upper and lower faces when viewed from the hillside or the shop.
            upper = corners + [(xx, yy, zz + 0.16) for xx, yy, zz in corners]
            faces = [(0, 1, 2, 3), (7, 6, 5, 4), (1, 0, 4, 5), (2, 1, 5, 6), (3, 2, 6, 7), (0, 3, 7, 4)]
            if side < 0:
                faces = [tuple(reversed(face)) for face in faces]
            geometry("Glazed roof bay", upper, faces, "KilnGlaze", "Rim")
            line("Mortised roof principal", (x, eave, 6.76), (x, 0, 10.45), 0.15, "Wood", "Rim")
            for y, z in ((6, 9.31), (12, 8.21), (18, 7.11)):
                line("Oak roof purlin", (x, y * side, z), (x + 4, y * side, z), 0.10, "Wood", "Rim")
            if x % 8 == 0:
                line("Clerestory arch brace", (x, eave, 4.35), (x, side * 13, 8.00), 0.15, "Wood", "Rim")
        line("Monitor curb", (-20, side * 4.4, 9.75), (20, side * 4.4, 9.75), 0.16, "Wood", "Rim")
    line("Ridge beam", (-20, 0, 10.55), (20, 0, 10.55), 0.22, "BellMetal", "Rim")

    # The valley, kiln chimneys and skyline visible through the sashes.
    for k in range(44):

        def ridge(i):
            a = math.tau * i / 44
            radius = 49 + 3.7 * math.sin(3 * a) + 1.6 * math.cos(9 * a)
            return (
                radius * math.cos(a),
                radius * math.sin(a),
                6.9 + 3.6 * math.sin(5 * a) + 2.1 * math.cos(9 * a),
            )

        a, b = ridge(k), ridge(k + 1)
        geometry(
            "Valley escarpment",
            [(a[0], a[1], -2), (b[0], b[1], -2), b, a],
            [(3, 2, 1, 0)],
            "Basalt" if k % 6 == 1 else "Masonry",
            "Skyline",
        )
    for i, (x, y, h) in enumerate(
        ((-26, 24, 9.8), (-21, 31, 12), (29, 16, 8.4), (33, 13, 11), (16, -31, 9.3))
    ):
        lathe(
            "Brick firing chimney",
            x,
            y,
            -1,
            [(1.70, 0), (1.75, 4.1), (1.04, 4.6), (0.70, h), (0.88, h + 0.1), (0.88, h + 0.45)],
            "Masonry",
            10,
            "Skyline",
        )
        for z in (4.1, h - 1.4):
            lathe(
                "Kiln iron band",
                x,
                y,
                z - 1,
                [(1.16 if z < 5 else 0.81, 0), (1.16 if z < 5 else 0.81, 0.13)],
                "Basalt",
                10,
                "Skyline",
            )
    # A brick arch and saw-tooth apron frame each window; the middle bay stays open.
    for side in (-1, 1):
        for wall in (0, 1):

            def at(u, h):
                return (u, 20.08 * side, h) if wall else (20.08 * side, u, h)

            for u in range(-16, 20, 8):
                for sign in (-1, 1):
                    line(
                        "Sash arch springer",
                        at(u + 3.82 * sign, 4.98),
                        at(u + 2.86 * sign, 6.24),
                        0.18,
                        "Masonry",
                        "Rim",
                    )
                    line("Sash arch crown", at(u + 2.86 * sign, 6.24), at(u, 6.75), 0.19, "Masonry", "Rim")
            line("Window base rail", at(-20, 2.83), at(20, 2.83), 0.16, "Wood", "Rim")
    h = 2.75

    def stand(x, y):
        collision("Instrument foot", x, y, -0.05, 0.98, 0.98, 1.23)
        lathe(
            "Bolted slate foot",
            x,
            y,
            -0.05,
            [(0.79, 0), (0.79, 0.17), (0.62, 0.30), (0.50, 0.67), (0.37, 0.73)],
            "Basalt",
            12,
        )
        lathe(
            "Brass instrument pillar",
            x,
            y,
            0.61,
            [(0.31, 0), (0.34, 0.12), (0.16, 0.33), (0.13, 1.57), (0.36, 1.68)],
            "Brass",
            10,
        )

    for j, (x, y) in enumerate(PIVOTS):
        n = NAMES[j]
        stand(x, y)
        group = "Mirror" + n
        origins[group] = (x, y, h)
        # Both reflective faces share a metal rim and a central physical pivot.
        angle = -math.pi / 4
        block("Silvered glass", (x, y, h), (1.72, 0.12, 1.06), "PressSilver", group, angle)
        for side in (-1, 1):
            xx = x + side * 0.87 * math.cos(angle)
            yy = y + side * 0.87 * math.sin(angle)
            shaft(
                "Mirror side binding",
                (xx, yy, h - 0.56),
                (xx, yy, h + 0.56),
                0.063,
                0.063,
                "Brass",
                8,
                group,
            )
            block(
                "Silver frame crossbeam",
                (x, y, h + side * 0.55),
                (1.80, 0.15, 0.10),
                "Brass",
                group,
                angle,
            )
        ring("Finger wheel", (x, y, 1.15), 0.53, 0.058, "BellMetal", "z", "Set")
        for k in range(4):
            a = k * math.pi / 2
            line(
                "Wheel spoke",
                (x, y, 1.15),
                (x + 0.53 * math.cos(a), y + 0.53 * math.sin(a), 1.15),
                0.032,
                "Brass",
            )
    for (x, y), (slope, colour) in ELBOWS.items():
        stand(x, y)
        angle = (1 if slope else -1) * math.pi / 4
        mat = "SeaGlass" if colour == "Blue" else "Amber"
        block("Stained filter and fixed mirror", (x, y, h), (1.38, 0.22, 1.15), mat, "Set", angle)
        for z in (h - 0.63, h + 0.63):
            block("Stained glass lead", (x, y, z), (1.59, 0.28, 0.12), "Wood", "Set", angle)
    sx, sy = SOURCE
    collision("Furnace core", sx, sy, -0.06, 1.72, 1.72, 3.41)
    lathe(
        "Obscura furnace",
        sx,
        sy,
        -0.06,
        [(1.1, 0), (1.18, 0.28), (0.87, 0.61), (0.83, 2.9), (0.96, 3.11), (0.64, 3.45)],
        "Basalt",
        12,
    )
    for dx, rad in ((0.61, 0.59), (1.01, 0.47), (1.30, 0.34)):
        shaft(
            "Collimator barrel",
            (sx + dx - 0.12, sy, h),
            (sx + dx + 0.14, sy, h),
            rad,
            rad * 0.95,
            "Brass",
            12,
        )
    for i, (a, b, col) in enumerate(SEGMENTS):
        shaft(
            "Shaft of " + col.lower() + " light",
            (*a, h),
            (*b, h),
            0.052,
            0.052,
            {"Gold": "Amber", "Blue": "SeaGlass", "White": "HousePlaster"}[col],
            7,
            "LightPath" + str(i),
        )
    for j, ((x, y), col, n, *_) in enumerate(PLATES):
        stand(x, y)
        block("Light-tight plate back", (x, y, h), (2.39, 0.19, 1.74), "Wood")
        for dx in (-1.22, 1.22):
            block("Polished mahogany rail", (x + dx, y, h), (0.09, 0.30, 1.90), "Wood")
        for dz in (-0.91, 0.91):
            block("Upper plate rail", (x, y, h + dz), (2.53, 0.30, 0.12), "Brass")
        panel("Coated negative", x, y - 0.108, h - 0.81, 2.30, 1.62, "Slate")
        panel("The developed photograph", x, y - 0.123, h - 0.81, 2.30, 1.62, "Proof" + n, "Print" + n)
        # A mechanical exposure meter gives the same cue in stereo, mono or monochrome.
        mx, mz = x + 1.60, h - 0.23
        block("Meter back", (mx, y, mz + 0.16), (0.68, 0.15, 0.59), "Wood")
        panel("Meter dial", mx, y - 0.081, mz - 0.075, 0.57, 0.48, "HousePlaster")
        for tick in range(5):
            a = math.radians(62 * tick / 4)
            line(
                "Scale graduation",
                (mx + 0.31 * math.sin(a), y - 0.101, mz + 0.31 * math.cos(a)),
                (mx + 0.35 * math.sin(a), y - 0.101, mz + 0.35 * math.cos(a)),
                0.016,
                "Basalt",
            )
        needle = "Meter" + n
        origins[needle] = (mx, y - 0.14, mz)
        line("Shutter needle", (mx, y - 0.14, mz - 0.038), (mx, y - 0.14, mz + 0.30), 0.025, "Basalt", needle)
        # A negative can be inspected from either aisle.
        obj = panel("Verso print", x, y + 0.105, h - 0.81, 2.30, 1.62, "Proof" + n, "Print" + n)
        for corner in obj.data.uv_layers.active.data:
            corner.uv.x = 1 - corner.uv.x
        obj.data.flip_normals()
        collision("Glass plate frame", x, y, h - 0.95, 2.52, 0.26, 1.90)
    for j, s in enumerate(r["stations"]):
        x, y = s["x"], s["y"]
        n = s["id"][2:]
        if n in ("Ledger", "Plan"):
            collision("Closed cabinet", x, y, -0.04, 2.17, 1.14, 1.13)
            block("Print shop cabinet", (x, y, 0.49), (2.0, 1.04, 0.97), "Wood")
            block("Desk edging", (x, y, 1.02), (2.17, 1.14, 0.13), "Brass")
            if n == "Plan":
                block("Plan frame", (x, y + 0.16, 1.91), (2.70, 0.15, 1.92), "Wood")
                panel("Engraved plan", x, y + 0.07, 1.02, 2.56, 1.81, KEY + "Survey", "Survey")
            else:
                block("Ledger leaves", (x, y, 1.14), (1.22, 0.65, 0.14), "HousePlaster")
                for q in range(4):
                    block(
                        "Bound contact proof",
                        (x - 0.50 + q * 0.30, y + 0.1, 1.22),
                        (0.05, 0.51, 0.025),
                        "Wood",
                    )
        elif n == "Gate":
            arch(x, y, -0.06, 2.85, 3.1, "Basalt", "Brass")
        marker(s["id"], x, y - (0.95 if n != "Gate" else 0.5), 1.44)
        marker(s["camp"], x, y - 2.1, 0.08)
        if n == "Gate":
            mount(s, 0, r, j, lambda k, x, y: 0)
        else:
            block("Enamel sign backing", (x, y - 0.57, 0.737), (1.40, 0.18, 0.36), "Wood")
            mount(dict(s, y=y - 0.33), 0, r, j, lambda k, x, y: 0)
    # Ossa's field camera, packed beside the desk after the flood.
    cx, cy = -8.0, -13.8
    for a in (0, math.tau / 3, 2 * math.tau / 3):
        foot = (cx + 0.91 * math.cos(a), cy + 0.91 * math.sin(a), 0.04)
        line("Ash tripod leg", foot, (cx, cy, 1.61), 0.082, "Wood")
    collision("Tripod footprint", cx, cy, -0.03, 0.91, 0.99, 2.45)
    block("Focusing rack", (cx, cy, 1.62), (0.96, 1.58, 0.12), "Brass")
    for k in range(9):
        side = 1.08 - k * 0.045
        block("Leather bellows fold", (cx, cy - 0.40 + k * 0.109, 2.13), (side, 0.067, side * 0.8), "Slate")
        block(
            "Bellows valley",
            (cx, cy - 0.34 + k * 0.109, 2.13),
            (side - 0.10, 0.064, side * 0.8 - 0.09),
            "Wood",
        )
    block("Ground-glass back", (cx, cy - 0.50, 2.13), (1.27, 0.18, 1.06), "Wood")
    panel("Camera focusing glass", cx, cy - 0.60, 1.70, 1.07, 0.86, "PressSilver")
    block("Lens board", (cx, cy + 0.57, 2.13), (0.83, 0.15, 0.75), "Wood")
    for material, near, far, radius in (
        ("Brass", 0.62, 0.87, 0.26),
        ("Basalt", 0.86, 0.99, 0.23),
        ("SeaGlass", 0.98, 1.01, 0.17),
    ):
        shaft("Portrait objective", (cx, cy + near, 2.13), (cx, cy + far, 2.13), radius, radius, material, 12)
    # Film holders, stoppered chemicals and a ribbed tray on the west bench.
    bx, by = -17.1, -9.0
    collision("Wash bench", bx, by, -0.03, 1.48, 4.48, 1.19)
    block("Wash bench cupboard", (bx, by, 0.54), (1.37, 4.40, 1.11), "Wood")
    block("Rimmed worktop", (bx, by, 1.14), (1.48, 4.48, 0.16), "Slate")
    for k in range(5):
        x, y = bx + 0.28 * (-1) ** k, by - 1.75 + 0.32 * k
        lathe(
            "Apothecary bottle",
            x,
            y,
            1.22,
            [(0.14, 0), (0.17, 0.06), (0.17, 0.29), (0.083, 0.37), (0.083, 0.46)],
            "Amber" if k % 2 else "SeaGlass",
            8,
        )
        block("Cork stopper", (x, y, 1.71), (0.13, 0.13, 0.09), "Wood")
    for k in range(6):
        block("Drying plate holder", (bx, by + 0.36 + k * 0.24, 1.55), (1.10, 0.095, 0.67), "Wood")
        block("Holder handle", (bx, by + 0.36 + k * 0.24, 1.92), (0.28, 0.11, 0.10), "Brass")
    for n, xy in zip(("MapSW", "MapSE", "MapNW"), ((-20, -20), (20, -20), (-20, 20))):
        marker(n, *xy, 0)
    marker("Spawn", 0, -14, 0.08)
    marker("Look", -0.8, 2, 1.65)
    bake_ground(KEY, lambda x, y: 0)
    finish(KEY, sky_key="CinderLens")
