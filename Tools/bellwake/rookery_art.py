"""Blender models for the pilots, the lantern terraces and Orla's route book."""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from atelier import (
    RES,
    init,
    finish,
    block,
    shaft,
    lathe,
    geometry,
    marker,
    origins,
    model,
    batches,
    mats,
)
from works_sets import line, ring
from sets import arch, pine
from engine_art import panel
from sillwater_art import terrain, house
from drift_fen_art import tiles
from underworks import rooms
from rookery import KEY, COURSES, POINTS, NAMES, BANKS

SPAN = 36
BRASS = "Brass"
OAK = "TarredOak"
TAU = math.tau


PLUMAGE = (
    "SeaCloth",
    "RoofSlate",
    "OchrePlaster",
    "HousePlaster",
    "BellMetal",
    "Brass",
    "TarredOak",
    "Pennon",
    "VerdigrisSheet",
    "Wood",
)


def feather_atlas():
    atlas = Image.new("RGB", (256, 256))
    for i, name in enumerate(PLUMAGE):
        src = Image.open(RES / "Textures" / (name + ".png")).convert("RGB")
        tile = src.resize((64, 64), Image.Resampling.LANCZOS)
        colors = (
            (84, 119, 131),
            (137, 154, 163),
            (178, 112, 65),
            (225, 216, 190),
            (111, 104, 78),
            (219, 164, 66),
            (42, 43, 41),
            (143, 66, 49),
            (144, 166, 148),
            (133, 98, 62),
        )
        yy, xx = np.mgrid[:64, :64]
        grain = np.asarray(tile.convert("L"), dtype=float)
        grain = (grain - grain.mean()) * 0.40 + 3.1 * np.cos(xx * 0.38 + yy * 0.19)
        color = np.uint8(np.clip(np.array(colors[i]) + grain[:, :, None], 0, 255))
        atlas.paste(Image.fromarray(color), (i % 4 * 64, i // 4 * 64))
    atlas.save(RES / "Textures/PilotPlumage.png")


def paint_pilots():
    # Pack all feather, eye and beak patches onto one sheet per articulated mesh.
    for group, parts in batches.items():
        if not (group.startswith("Pilot") or group.endswith("Whistle")):
            continue
        for obj in parts:
            mesh = obj.data
            i = PLUMAGE.index(mesh.materials[0].name)
            mesh.materials[0] = mats["PilotPlumage"]
            uv = mesh.uv_layers.active.data
            for poly in mesh.polygons:
                coords = [tuple(uv[j].uv) for j in poly.loop_indices]
                u = sum(pt[0] for pt in coords) / len(coords)
                v = sum(pt[1] for pt in coords) / len(coords)
                for j, (a, b) in zip(poly.loop_indices, coords):
                    uu = max(0.04, min(0.96, 0.5 + (a - u) * 0.94))
                    vv = max(0.04, min(0.96, 0.5 + (b - v) * 0.94))
                    uv[j].uv = ((i % 4 + uu) / 4, (3 - i // 4 + vv) / 4)


def land(x, y):
    h = (
        0.62
        + 0.18 * np.cos(x / 11) * np.sin(y / 9)
        + 2.4 * np.exp(-((x - 24) ** 2 + (y - 23) ** 2) / 145)
        + 1.95 * np.exp(-((x + 20) ** 2 + (y - 22) ** 2) / 182)
    )
    return h * np.clip((x * x + (y + 14) ** 2) / 72, 0, 1)


def brush(key):
    n = 672
    yy, xx = np.mgrid[:n, :n]
    x = (xx + 0.5) * 72 / n - 36
    y = 36 - (yy + 0.5) * 72 / n
    road = np.zeros_like(x)
    edges = {tuple(sorted((a, b))) for c in COURSES for a, b, w in c[-1]}
    for a, b in edges | {(0, 2), (6, 8)}:
        ax, ay = POINTS[a]
        bx, by = POINTS[b]
        dx = bx - ax
        dy = by - ay
        t = np.clip(((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy), 0, 1)
        road = np.maximum(road, np.clip((2.6 - np.hypot(x - ax - dx * t, y - ay - dy * t)) * 0.85, 0, 1))
    court = np.clip((11.6 - abs(x)) * 0.7, 0, 1) * np.clip((10 - abs(y + 12)) * 0.7, 0, 1)
    road = np.maximum(road, court)[:, :, None]
    base = (tiles("Grass", x, y) * 0.72 + [27, 31, 18]) * (1 - road) + (
        tiles("Setts", x, y) * 0.74 + [40, 38, 32]
    ) * road
    Image.fromarray(np.uint8(np.clip(base, 0, 255))).save(RES / "Textures" / (key + "Ground.png"))
    serif = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    sans = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font = lambda size: ImageFont.truetype(serif, size)
    body = lambda size: ImageFont.truetype(sans, size)

    def map_sheet(i, overview=False):
        im = Image.new("RGB", (768, 544), "#e9d6ac")
        d = ImageDraw.Draw(im)
        d.rectangle((16, 32, 496, 512), fill="#c3c8a0", outline="#716d50", width=3)

        def pos(j):
            a, b = POINTS[j]
            return 16 + (a + 36) * 480 / 72, 512 - (b + 36) * 480 / 72

        birds = COURSES[i]
        edges = birds[-1]
        for a, b, w in edges:
            x0, y0 = pos(a)
            x1, y1 = pos(b)
            colour = "#2e727a" if w else "#936240"
            d.line((x0, y0, x1, y1), fill=colour, width=5)
            if not w:
                for k in range(1, 15, 2):
                    d.line(
                        (
                            x0 + (x1 - x0) * k / 16,
                            y0 + (y1 - y0) * k / 16,
                            x0 + (x1 - x0) * (k + 1) / 16,
                            y0 + (y1 - y0) * (k + 1) / 16,
                        ),
                        fill="#dec89a",
                        width=3,
                    )
        for j, n in enumerate(NAMES):
            xx, yy = pos(j)
            d.ellipse((xx - 10, yy - 10, xx + 10, yy + 10), fill="#314d4d", outline="#efe5bb", width=2)
            d.text((xx, yy), str(j + 1), anchor="mm", font=font(12), fill="white")
            d.text((xx, yy + 13), n, anchor="mt", font=font(13), fill="#3d4235")
        d.text((512, 32), "GLASS ROOKERY", font=font(23), fill="#4c5140")
        d.text((512, 79), birds[0] + "’s flight", font=font(23), fill="#484038")
        d.text((513, 121), birds[1].upper(), font=body(16), fill="#655b42")
        words = (
            "From " + NAMES[birds[2]],
            "Home at " + NAMES[birds[3]],
            "Blue line · running water",
            "Ochre dash · quiet water",
            "Ask the weir wheel",
            "to change the current.",
        )
        for j, t in enumerate(words):
            d.text((512, 159 + j * 30), t, font=body(17), fill="#414c43")
        d.text((512, 368), "A  Ferry · Crossing · Lantern", font=body(15), fill="#785236")
        d.text((512, 394), "B  Flume · Reed · Crown", font=body(15), fill="#785236")
        d.text((512, 420), "C  Kiln · Spindle · Alder", font=body(15), fill="#785236")
        d.text((512, 477), "N ↑   Lodge on south side", font=body(16), fill="#405952")
        return im

    for i in range(3):
        map_sheet(i).save(RES / "Textures" / (key + "Page" + str(i) + ".png"))
    closed = Image.new("RGB", (768, 544), "#e8d8ac")
    d = ImageDraw.Draw(closed)
    d.rectangle((20, 20, 747, 523), outline="#987b50", width=7)
    d.text((384, 72), "THE THREE ARE HOME", font=font(42), anchor="mt", fill="#395b56")
    for j, (bird, kind, *_) in enumerate(COURSES):
        d.text((76, 185 + 73 * j), bird, font=font(31), fill="#554933")
        d.text(
            (262, 195 + 73 * j),
            ("The bread tally", "Five small thumbprints", "Ina’s sketch for Tavi")[j],
            font=body(25),
            fill="#4c5147",
        )
    d.text(
        (384, 449),
        "Entered by Orla · keeper of the pilot gardens",
        font=body(24),
        anchor="mt",
        fill="#51655b",
    )
    closed.save(RES / "Textures" / (key + "Page3.png"))
    im = map_sheet(0)
    d = ImageDraw.Draw(im)
    d.rectangle((16, 32, 496, 512), fill="#c3c8a0", outline="#716d50", width=3)
    for a, b in edges:
        ax, ay = POINTS[a]
        bx, by = POINTS[b]
        d.line(
            (
                16 + (ax + 36) * 480 / 72,
                512 - (ay + 36) * 480 / 72,
                16 + (bx + 36) * 480 / 72,
                512 - (by + 36) * 480 / 72,
            ),
            fill="#a38c69",
            width=4,
        )
    for x0, y0, nm in [(*pt, NAMES[i]) for i, pt in enumerate(POINTS)] + [
        (-12, 2, "Weir"),
        (12, 3, "Glass"),
        (3, 12, "Desk"),
        (-5, -11, "Orla"),
    ]:
        px = 16 + (x0 + 36) * 480 / 72
        py = 512 - (y0 + 36) * 480 / 72
        d.ellipse((px - 5, py - 5, px + 5, py + 5), fill="#56483b")
        d.text((px, py + 7), nm, anchor="mt", font=body(13), fill="#37372f")
    d.rectangle((509, 76, 766, 461), fill="#e9d6ac")
    for i, t in enumerate(
        (
            "Pilot gardens",
            "Read the flight chart",
            "at Orla’s lodge, or on",
            "any brass perch.",
            "Quiet / running water",
            "use the west wheel.",
            "Ash needs the correct",
            "bank of lit lanterns.",
            "Use the eastern drum.",
        )
    ):
        d.text((512, 83 + i * 35), t, font=font(21) if i == 0 else body(18), fill="#445541")
    im.save(RES / "Textures" / (key + "Survey.png"))
    labels = Image.new("RGB", (384, 384), "#3d514e")
    d = ImageDraw.Draw(labels)
    for i, nm in enumerate(NAMES):
        px = i % 3 * 128
        py = i // 3 * 128
        d.rounded_rectangle((px + 3, py + 3, px + 124, py + 124), 10, outline="#d3bd7d", width=3)
        d.text((px + 64, py + 31), "PERCH  " + str(i + 1), font=body(16), anchor="mm", fill="#ddc795")
        d.text((px + 64, py + 65), nm, font=font(18), anchor="mm", fill="#fff1bd")
        d.text(
            (px + 64, py + 100), "BANK  " + "ABC"[BANKS[i]], font=body(14), anchor="mm", fill="#d2c59e"
        )
    labels.save(RES / "Textures/RookPerches.png")


def aviary_paint():
    n = 96
    yy, xx = np.mgrid[:n, :n]
    u = xx / (n - 1)
    v = yy / (n - 1)
    rng = np.random.default_rng(4083)
    glass = np.zeros((n, n, 3)) + np.array((106, 150, 155))
    glass += (1 - v)[:, :, None] * [42, 33, 20]
    ridge = 0.68 + 0.085 * np.sin(u * 7.5 + 0.6) + 0.04 * np.cos(u * 13)
    glass[v > ridge] = [89, 113, 101]
    glass[v > ridge + 0.09] = [76, 100, 91]
    silver = np.clip(1 - np.abs(u + 0.58 * v - 0.51) / 0.05, 0, 1) + 0.5 * np.clip(
        1 - np.abs(u + 0.58 * v - 1.1) / 0.11, 0, 1
    )
    glass += silver[:, :, None] * [31, 30, 23] + rng.normal(0, 2.0, (n, n, 1))
    im = Image.fromarray(np.uint8(np.clip(glass, 0, 255)))
    d = ImageDraw.Draw(im)
    for x in (0, 48, 95):
        d.line((x, 0, x, 95), fill="#425d59", width=2)
    for y in (0, 47, 95):
        d.line((0, y, 95, y), fill="#526764", width=2)
    im.save(RES / "Textures/RookeryGlass.png")


def aviary(x, y):
    z = float(land(x, y))
    n = 8

    def pt(r, a, h):
        return (x + r * math.cos(a), y + r * math.sin(a), z + h)

    lathe(
        "Glasshouse high-water plinth",
        x,
        y,
        z - 0.82,
        [(4.6, 0), (4.6, 1.56), (4.79, 1.62), (4.79, 1.85), (4.46, 1.91)],
        "Masonry",
        n,
    )
    lathe("Solid enclosed winter house", x, y, z + 0.96, [(4.34, 0), (4.33, 4.45)], "SeaCloth", n)
    for j in range(n):
        a = j * TAU / n
        b = (j + 1) * TAU / n
        points = [pt(4.43, a, 1.08), pt(4.43, b, 1.08), pt(4.43, b, 5.36), pt(4.43, a, 5.36)]
        geometry(
            "Hand-leaded panes",
            points,
            [(0, 1, 2, 3)],
            "RookeryGlass",
            "Set",
            [(0, 0), (1, 0), (1, 1), (0, 1)],
        )
        shaft("Octagonal mullion", points[0], points[3], 0.14, 0.12, OAK, 8)
        for h in (1.14, 3.20, 5.30):
            line("Ring rail", pt(4.46, a, h), pt(4.46, b, h), 0.11, "Wood")
        roof = [pt(4.84, a, 5.42), pt(4.84, b, 5.42), pt(2.02, b, 7.44), pt(2.02, a, 7.44)]
        geometry("Folded copper roof", roof, [(0, 1, 2, 3)], "VerdigrisSheet")
        line("Seamed hip", roof[0], roof[3], 0.073, BRASS)
        line("Brass gutter", roof[0], roof[1], 0.086, BRASS)
    lathe(
        "Ventilated clerestory",
        x,
        y,
        z + 7.40,
        [(2.05, 0), (1.71, 0.20), (1.71, 1.00), (1.89, 1.08)],
        "RookeryGlass",
        8,
    )
    lathe(
        "Lantern cap",
        x,
        y,
        z + 8.45,
        [(2.01, 0), (1.82, 0.19), (0.28, 1.14), (0.16, 1.37)],
        "VerdigrisSheet",
        8,
    )
    shaft("Weather vane post", pt(0, 0, 9.6), pt(0, 0, 11.06), 0.08, 0.054, BRASS, 8)
    pts = [
        (x - 1.1, y, z + 10.59),
        (x - 0.3, y, z + 10.70),
        (x - 0.80, y, z + 11.14),
        (x + 0.29, y, z + 10.84),
        (x + 0.61, y, z + 11.02),
        (x + 0.93, y, z + 10.96),
        (x + 0.60, y, z + 10.80),
        (x + 0.19, y, z + 10.52),
        (x - 0.49, y, z + 10.51),
    ]
    geometry(
        "Swift weather vane", pts, [(0, 1, 8), (1, 2, 3), (1, 3, 7, 8), (3, 4, 5, 6), (3, 6, 7)], BRASS
    )
    y0 = y - 4.34
    block("Glasshouse oak door", (x, y0, z + 1.90), (1.53, 0.30, 2.47), OAK)
    block("Enamel door panel", (x, y0 - 0.17, z + 2.24), (1.19, 0.08, 1.16), "RookeryGlass")
    for j in range(3):
        block(
            "Stone door step",
            (x, y0 - 0.20 - j * 0.32, z + 0.61 - j * 0.17),
            (2.12 - j * 0.10, 0.64, 0.41),
            "Masonry",
        )


def reed_whistle(x, y, z, group):
    shaft("Kingfisher whistle", (x, y, z), (x, y + 0.25, z + 0.54), 0.085, 0.14, "Wood", 9, group)
    for h in (0.14, 0.39):
        shaft(
            "Tinned ferrule",
            (x, y + 0.45 * h, z + h),
            (x, y + 0.45 * (h + 0.04), z + h + 0.04),
            0.11,
            0.112,
            BRASS,
            9,
            group,
        )
    for h in (0.18, 0.27, 0.36):
        ell("Whistle finger hole", (x, y + 0.46 * h - 0.09, z + h), (0.037, 0.023, 0.032), OAK, group)
    ring("Lanyard ring", (x, y, z), 0.072, 0.023, BRASS, "y", group, n=8)


def ell(name, c, r, mat, group):
    x, y, z = c
    rx, ry, rz = r
    verts = [(x, y, z - rz)]
    faces = []
    n = 9
    for k in range(1, 5):
        ang = -math.pi / 2 + k * math.pi / 5
        for i in range(n):
            a = i * TAU / n + (k % 2) * 0.18
            verts.append(
                (
                    x + rx * math.cos(a) * math.cos(ang),
                    y + ry * math.sin(a) * math.cos(ang),
                    z + rz * math.sin(ang),
                )
            )
    top = len(verts)
    verts.append((x, y, z + rz))
    for i in range(n):
        j = (i + 1) % n
        faces.extend(((0, 1 + j, 1 + i), (1 + 3 * n + i, 1 + 3 * n + j, top)))
        for k in range(3):
            one = 1 + k * n + i
            two = 1 + k * n + j
            faces.append((one, two, two + n, one + n))
    geometry(name, verts, faces, mat, group)


def feather(name, base, tip, width, material, group):
    a = np.array(base)
    b = np.array(tip)
    axis = b - a
    side = np.array((-axis[1], axis[0], 0))
    side = side / max(0.001, np.linalg.norm(side)) * width
    points = [
        a,
        a + axis * 0.34 + side,
        b,
        a + axis * 0.34 - side,
        a + axis * 0.47 + [0, 0, width * 0.32],
        a + axis * 0.46 - [0, 0, width * 0.18],
    ]
    geometry(
        name,
        points,
        [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (1, 0, 5), (2, 1, 5), (3, 2, 5), (0, 3, 5)],
        material,
        group,
    )


def avian(i, x, y, z):
    # Model Y is forward. Each bird has its own proportions, bill, crest and feather sweep.
    g = "Pilot" + str(i)
    origins[g] = (x, y, z)
    h = (0.42, 1.15, 0.58)[i]
    coat = ("SeaCloth", "RoofSlate", "OchrePlaster")[i]
    breast = ("HousePlaster", "SeaCloth", "HousePlaster")[i]

    def pt(a, b, c):
        return (x + a, y + b, z + c)

    w = (0.39, 0.37, 0.32)[i]
    long = (0.61, 0.65, 0.72)[i]
    body = h + 0.33
    ell("Breast and mantle", pt(0, 0, body), (w, long, 0.31), coat, g)
    ell("Pale bib", pt(0, 0.27, body - 0.026), (w * 0.88, 0.39, 0.27), breast, g)
    for side in (-1, 1):
        leg = (0.15 * side, 0.07)
        shaft("Leg", pt(*leg, 0.033), pt(0.17 * side, -0.045, h + 0.10), 0.035, 0.046, "BellMetal", 7, g)
        for j in (-1, 0, 1):
            line(
                "Webbed toe",
                pt(*leg, 0.04),
                pt(0.15 * side + j * 0.09, 0.29 - abs(j) * 0.055, 0.034),
                0.034,
                "OchrePlaster",
                g,
            )
    hz = body + (0.36, 0.97, 0.39)[i]
    fy = (0.39, 0.58, 0.54)[i]
    if i == 1:
        shaft(
            "Curved lower neck",
            pt(0, 0.14, body + 0.04),
            pt(0, 0.01, body + 0.62),
            0.18,
            0.12,
            breast,
            8,
            g,
        )
        shaft("Folded upper neck", pt(0, 0.01, body + 0.62), pt(0, fy, hz), 0.12, 0.14, breast, 8, g)
    else:
        ell("Neck collar", pt(0, 0.31, body + 0.16), (0.23, 0.25, 0.24), breast, g)
    ell("Crown", pt(0, fy, hz), (0.24, 0.29, 0.225), coat, g)
    shaft(
        "Tapered bill",
        pt(0, fy + 0.20, hz - 0.03),
        pt(0, fy + (0.49, 0.95, 0.68)[i], hz - 0.06),
        0.097,
        0.018,
        BRASS,
        7,
        g,
    )
    for side in (-1, 1):
        ell(
            "Ivory eye ring",
            pt(side * 0.197, fy + 0.075, hz + 0.042),
            (0.048, 0.091, 0.075),
            "HousePlaster",
            g,
        )
        ell("Dark eye", pt(side * 0.235, fy + 0.095, hz + 0.046), (0.024, 0.045, 0.044), OAK, g)
        wing = g + ("Left" if side < 0 else "Right")
        pivot = pt(side * w * 0.73, 0, body + 0.09)
        origins[wing] = pivot
        pts = [
            pt(side * w * 0.63, 0.35, body + 0.16),
            pt(side * (w + 0.13), 0.06, body + 0.16),
            pt(side * (w + 0.21), -0.49, body + 0.05),
            pt(side * (w + 0.12), -0.86, body - 0.13),
            pt(side * w * 0.65, -0.35, body - 0.04),
        ]
        geometry("Tapered pilot wing", pts, [(0, 1, 2), (0, 2, 4), (2, 3, 4)], coat, wing)
        for j in range(4):
            dx = side * (w * 0.82 + 0.054 * j)
            a = pt(dx, 0.22 - 0.126 * j, body + 0.12 - 0.015 * j)
            b = pt(dx + side * 0.13, -0.44 - 0.135 * j, body - 0.055 * j)
            feather(
                "Flight feather",
                a,
                b,
                0.135 if i != 2 else 0.105,
                "VerdigrisSheet" if j == 0 else coat,
                wing,
            )
    for j in (-1, 0, 1):
        feather(
            "Tail feather",
            pt(j * 0.07, -0.42, body + 0.09),
            pt(j * 0.21, -(0.87, 1.12, 1.35)[i] + (0.34 if i == 2 else 0.08) * (j == 0), body + 0.025),
            0.14,
            coat,
            g,
        )
    if i == 0:
        for side in (-1, 1):
            ell(
                "Russet cheek",
                pt(side * 0.174, fy - 0.056, hz - 0.052),
                (0.097, 0.17, 0.117),
                "Pennon",
                g,
            )
    for dy in (-0.058, 0.081):
        ring("Message lashing", pt(0.184, dy, h * 0.63), 0.066, 0.016, "Pennon", "y", g, n=9)
    shaft(
        "Rolled flood message",
        pt(0.184, -0.111, h * 0.63),
        pt(0.184, 0.142, h * 0.63),
        0.054,
        0.051,
        "OchrePlaster",
        8,
        g,
    )
    if i != 2:
        for j in (-1, 1):
            line(
                "Trailing plume",
                pt(0.085 * j, fy - 0.10, hz + 0.16),
                pt(j * 0.17, fy - 0.55, hz + 0.26),
                0.045,
                "Pennon" if i == 0 else "HousePlaster",
                g,
            )
    else:
        ell("Black tern cap", pt(0, fy + 0.01, hz + 0.119), (0.224, 0.25, 0.126), OAK, g)


def perch(i, x, y):
    z = float(land(x, y))
    lathe(
        "Carved guidepost",
        x,
        y,
        z - 0.18,
        [(0.80, 0), (0.78, 0.46), (0.38, 0.67), (0.33, 1.40), (0.49, 1.48)],
        "Masonry",
        8,
    )
    lathe("Pilot platform", x, y, z + 1.29, [(0.52, 0), (0.74, 0.12), (0.72, 0.22)], "Wood", 10)
    marker("Roost" + str(i), x, y, z + 1.51)
    lx = x + 1.31
    lathe("Shutter cap", lx, y, z, [(0.24, 0), (0.16, 0.63), (0.29, 0.76)], OAK, 6)
    lathe(
        "Glass searchlight",
        lx,
        y,
        z + 0.73,
        [(0.23, 0), (0.26, 0.18), (0.17, 0.48), (0.05, 0.56)],
        "Amber",
        8,
        "LanternBank" + str(BANKS[i]),
    )
    # A three-column UV atlas, one enamel number per stone.
    j = i % 3
    k = i // 3
    u = j / 3
    v = (2 - k) / 3
    geometry(
        "Enamel guide number",
        [
            (x - 0.50, y - 0.44, z + 0.58),
            (x + 0.50, y - 0.44, z + 0.58),
            (x + 0.50, y - 0.44, z + 1.57),
            (x - 0.50, y - 0.44, z + 1.57),
        ],
        [(0, 1, 2, 3)],
        "RookPerches",
        "Set",
        [(u, v), (u + 1 / 3, v), (u + 1 / 3, v + 1 / 3), (u, v + 1 / 3)],
    )


def make(lib):
    r = next(r for r in rooms if r["key"] == KEY)
    brush(KEY)
    feather_atlas()
    aviary_paint()
    init(lib, 64571)
    terrain(KEY, SPAN, land, 2)
    reed_whistle(0, 0, 0, "HandWhistle")
    aviary(3, 30)
    house(-9, -18, 6.5, 5.7, 3.45, 2, height=land)
    for j, (x, y) in enumerate(POINTS):
        perch(j, x, y)
    for i, course in enumerate(COURSES):
        x, y = POINTS[course[2]]
        avian(i, x, y, float(land(x, y)) + 1.51)
    for j, (x, y) in enumerate(
        ((-31, -29), (-16, -28), (16, -29), (29, -13), (-30, 12), (13, 29), (-10, 30), (31, 25))
    ):
        pine(x, y, float(land(x, y)), 5.7 + j % 3, j * 0.78)
    # The water trough meets the weir at the west end of the valley.
    for x, y in ((-13, 6), (-10, 6), (-7, 6)):
        z = float(land(x, y))
        block("Trough bed", (x, y, z + 0.18), (3.04, 1.8, 0.38), "Masonry")
        block("Headwater surface", (x, y, z + 0.40), (3.0, 1.50, 0.08), "ParishWater")
        for side in (-1, 1):
            block("Trough coping", (x, y + side * 0.86, z + 0.48), (3.07, 0.22, 0.54), "Masonry")
    block("Sluice board", (-12.2, 6, 1.48), (0.20, 1.84, 1.18), "Wood", "WeirLeaf")
    for j, s in enumerate(r["stations"]):
        x, y = s["x"], s["y"]
        z = float(land(x, y))
        id = s["id"][2:]
        if id == "Keeper":
            model("WZ_SKY_N01", "Orla the pilot keeper", x, y, z, 1.75, 15, "Speaker")
            block("Orla's carved bench", (x - 1.21, y, z + 0.69), (1.15, 0.72, 1.42), OAK)
            reed_whistle(x - 1.21, y, z + 1.41, "BenchWhistle")
        elif id == "Gate":
            arch(x, y, z, 3.2, 3.77, "HarbourBrick", "Wood")
        elif id == "Chart":
            for off in (-2.5, 2.5):
                block("Chart frame upright", (x + off, y, z + 1.65), (0.21, 0.27, 3.6), OAK)
            block("Flight chart backing", (x, y, z + 2.12), (5.31, 0.33, 3.73), OAK)
            for i in range(4):
                panel(
                    "Pilot chart",
                    x,
                    y - 0.19,
                    z + 0.43,
                    5.02,
                    3.55,
                    KEY + "Page" + str(i),
                    "Page" + str(i),
                )
            block("Survey slat", (x + 4.51, y, z + 1.78), (2.93, 0.22, 2.20), OAK)
            panel("Rookery map", x + 4.51, y - 0.13, z + 0.78, 2.78, 1.97, KEY + "Survey")
        elif id in ("Water", "Light"):
            block("Operating pedestal", (x, y, z + 0.61), (1.35, 0.70, 1.27), "HarbourBrick")
            c = (x, y, z + 1.63)
            ring("Control wheel", c, 0.51, 0.075, "VerdigrisSheet", "y")
            for j in range(6):
                a = j * TAU / 6
                line(
                    "Wheel spoke",
                    c,
                    (x + 0.50 * math.cos(a), y, z + 1.63 + 0.50 * math.sin(a)),
                    0.044,
                    BRASS,
                )
            if id == "Light":
                for k in range(3):
                    lathe(
                        "Lens housing",
                        x - 0.43 + 0.43 * k,
                        y + 0.37,
                        z + 0.97,
                        [(0.19, 0), (0.21, 0.15), (0.14, 0.31)],
                        ("SeaGlass", "Amber", "Pennon")[k],
                        8,
                    )
        elif id == "Glasshouse":
            block("Visitor ledger stand", (x, y, z + 0.65), (1.24, 0.77, 1.32), OAK)
            block("Open visitor book", (x, y, z + 1.38), (1.36, 0.83, 0.15), "HousePlaster")
            for off in (-0.36, 0.36):
                line(
                    "Book ruling",
                    (x + off - 0.18, y - 0.25, z + 1.46),
                    (x + off + 0.15, y - 0.25, z + 1.46),
                    0.014,
                    "Wood",
                )
        elif id == "Launch":
            block("Courier table", (x, y, z + 0.58), (2.41, 0.88, 1.20), OAK)
            for dx in (-0.64, 0, 0.64):
                shaft(
                    "Reed message tube",
                    (x + dx, y - 0.21, z + 1.37),
                    (x + dx + 0.08, y + 0.27, z + 1.51),
                    0.11,
                    0.10,
                    "OchrePlaster",
                    8,
                )
        marker(s["id"], x, y - 0.73, z + 1.36)
        marker(s["camp"], x, y - 2.32, float(land(x, y - 2.32)) + 0.10)
    for name, x, y in (("MapSW", -36, -36), ("MapSE", 36, -36), ("MapNW", -36, 36)):
        marker(name, x, y, float(land(x, y)))
    for k in range(32):
        a = TAU * k / 32
        rr = 61 + 3 * math.sin(4 * a)
        lathe(
            "Cinder valley crest",
            rr * math.cos(a),
            rr * math.sin(a),
            -3,
            [(8.5, 0), (7.9, 6), (5.5, 10 + 2 * math.cos(5 * a)), (1.13, 13 + 3 * math.sin(3 * a))],
            "FenShale",
            7,
            "Horizon",
        )
    marker("Spawn", 0, -14, 0.08)
    marker("Look", 0, 9, 2)
    paint_pilots()
    finish(KEY, sky_key=r["theme"])
