"""Blender authoring for the two tides of Sillwater and Ada's map office."""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from atelier import (
    RES,
    init,
    finish,
    geometry,
    block,
    shaft,
    lathe,
    marker,
    model,
    collision,
)
from sets import arch, bell
from works_sets import line, ring
from works_finish import plaques, mount
from engine_art import panel
from underworks import rooms
from sillwater import HIGH, OFFICE, PLACES, PINS, PITCH, SITES
from wrenfall import oak_crown

TAU = math.tau
TARGETS = [((c - 2) * PITCH, (r - 2) * PITCH) for c, r in PINS]
BRIDGES = (-26, 8, 46)


def river(x):
    return 8 + 3.2 * np.sin(x / 15) + 1.3 * np.cos(x / 8)


def land(x, y):
    d = abs(y - river(x))
    shore = np.clip((d - 3) / 6, 0, 1)
    mound = 1.16 + 0.37 * np.sin(x / 12) * np.cos(y / 13)
    for px, py, h, w in (
        (-35, 32, 3.1, 15),
        (36, 0, 1.8, 12),
        (1, 45, 2.9, 15),
        (-48, -33, 1.8, 14),
    ):
        mound = mound + h * np.exp(-((x - px) ** 2 + (y - py) ** 2) / (2 * w * w))
    return (0.10 + mound * shore) * np.clip((x * x + (y + 14) ** 2) / 100, 0, 1)


def target_z(i):
    x, y = TARGETS[i]
    return float(land(x, y)) + (9.4, 10.8, 11.6)[i]


def office_height(k, x, y):
    return 0.18 * np.clip((abs(x) - 10) / 6, 0, 1)


def material_paint(key, high, office=False):
    size = 512 if office else 768
    yy, xx = np.mgrid[:size, :size]
    span = 20 if office else 60
    x = (xx + 0.5) * 2 * span / size - span
    y = span - (yy + 0.5) * 2 * span / size

    def tile(n, rate):
        a = np.array(Image.open(RES / "Textures" / (n + ".png")).convert("RGB"))
        return a[(yy * rate // 4) % a.shape[0], (xx * rate // 4) % a.shape[1]].astype(
            float
        )

    if office:
        board = tile("Wood", 4) * 0.46 + [56, 47, 33]
        joint = (abs((x + 20) % 1.16 - 0.58) > 0.555) | (
            ((y + np.floor(x / 1.16) * 1.1) % 4.2) < 0.065
        )
        floor = board - joint[:, :, None] * 21
        base = tile("Setts", 5) * 0.68 + [33, 33, 26]
        base = np.where(((abs(x) < 11) & (y > -11) & (y < 12))[:, :, None], floor, base)
    else:
        grass = tile("Grass", 7) * (0.61 if high else 0.66) + (
            [21, 35, 25] if high else [33, 40, 14]
        )
        mud = tile("MossRock", 7) * 0.59 + [52, 41, 23]
        dist = abs(y - river(x))
        bank = np.clip((dist - 4.9) / 3.4, 0, 1)
        base = mud * (1 - bank[:, :, None]) + grass * bank[:, :, None]
        track = np.full(x.shape, 99.0)
        lanes = [
            ((-50, -27), (42, -21)),
            ((-43, 34), (42, 27)),
            ((-45, 44), (42, 45)),
            ((6, -19), (-5, -15)),
        ]
        lanes.extend(((bx, -32), (bx, 45)) for bx in BRIDGES)
        for (ax, ay), (bx, by) in lanes:
            dx, dy = bx - ax, by - ay
            t = np.clip(((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy), 0, 1)
            track = np.minimum(track, np.hypot(x - ax - t * dx, y - ay - t * dy))
        road = np.clip((2.3 - track) * 1.1, 0, 1) * np.clip((dist - 4) / 2, 0, 1)
        base = (
            base * (1 - road[:, :, None])
            + (tile("DirtPath", 6) * 0.65 + [44, 36, 20]) * road[:, :, None]
        )
        # At ebb, the shingle causeway is exposed from one bank to the other.
        if not high:
            shingle = (
                np.clip((2 - abs(x + 26)) * 1.8, 0, 1)
                * np.clip((10 - dist) * 0.8, 0, 1)
            )[:, :, None]
            base = (
                base * (1 - shingle)
                + (tile("Setts", 6) * 0.65 + [55, 52, 36]) * shingle
            )
    im = Image.fromarray(np.uint8(np.clip(base, 0, 255)))
    im.save(RES / "Textures" / (key + "Ground.png"))


def field_sheet(key, r, high):
    paper = Image.new("RGB", (768, 544), "#e1cfaa")
    d = ImageDraw.Draw(paper)
    serif = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    sans = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    heading = ImageFont.truetype(serif, 23)
    small = ImageFont.truetype(sans, 15)
    numerals = ImageFont.truetype(serif, 13)
    pt = lambda x, y: (16 + (x + 60) * 4, 512 - (y + 60) * 4)
    yy, xx = np.mgrid[:480, :480]
    x = xx / 4 - 60
    y = 60 - yy / 4
    h = land(x, y)
    delta = abs(y - river(x))
    base = np.zeros((480, 480, 3))
    base[:] = [213, 203, 158]
    base -= h[:, :, None] * [4, 2, 6]
    base[(np.mod(h, 0.44) < 0.025) & (delta > 7)] = [159, 159, 116]
    base[delta < (8.2 if high else 5.3)] = [104, 151, 153]
    paper.paste(Image.fromarray(base.astype("uint8")), (16, 32))
    for bx in BRIDGES:
        ry = float(river(bx))
        d.line((pt(bx, -34), pt(bx, ry - 8)), fill="#b1986d", width=3)
        d.line((pt(bx, ry + 8), pt(bx, 46)), fill="#b1986d", width=3)
        d.line(
            (pt(bx, ry - 8), pt(bx, ry + 8)),
            fill="#805734" if bx == 46 or (bx == 8) == high else "#a8aaa2",
            width=6,
        )
    d.rectangle((16, 32, 496, 512), outline="#666147", width=2)
    d.text((512, 35), "SILLWATER PARISH", font=small, fill="#65523d")
    d.text(
        (510, 60),
        "Flood survey" if high else "Ebb survey",
        font=heading,
        fill="#373329",
    )
    d.text((511, 101), "Ada’s field sheet   ·   N ↑", font=small, fill="#4f574e")
    names = [p[int(high)][0] for p in SITES] + [
        "South",
        "North",
        "Office",
        "Gate",
        "Ada",
    ]
    for j, name in enumerate(names, 1):
        item = next(st for st in r["stations"] if st["id"] == "A_" + name)
        sx, sy = pt(item["x"], item["y"])
        colour = ("#4c716d" if high else "#97554a") if j <= 3 else "#655744"
        d.ellipse(
            (sx - 10, sy - 10, sx + 10, sy + 10),
            fill=colour,
            outline="#fff0c8",
            width=2,
        )
        d.text((sx, sy), str(j), anchor="mm", fill="white", font=numerals)
        line = 134 + (j - 1) * 33
        d.text((514, line), str(j), font=numerals, fill=colour)
        d.text((538, line), item["label"], font=small, fill="#3c362f")
    d.text((512, 397), "1–3   Survey instruments", font=small, fill="#4f574e")
    d.text((512, 469), "One crossing stays open", font=small, fill="#4f574e")
    d.text((512, 489), "at the eastern bridge.", font=small, fill="#4f574e")
    paper.save(RES / "Textures" / (key + "Survey.png"))


def terrain(key, span, h, step):
    size = span * 2 // step + 1
    pts = [
        (x, y, float(h(x, y)))
        for y in range(-span, span + 1, step)
        for x in range(-span, span + 1, step)
    ]
    m = geometry(
        "Continuous parish terrain",
        pts,
        [
            (j * size + i, j * size + i + 1, (j + 1) * size + i + 1, (j + 1) * size + i)
            for j in range(size - 1)
            for i in range(size - 1)
        ],
        key + "Ground",
        "Terrain",
    )
    for i, l in enumerate(m.data.loops):
        x, y, _ = pts[l.vertex_index]
        m.data.uv_layers.active.data[i].uv = (
            (x + span) / (2 * span),
            (y + span) / (2 * span),
        )
    for x, y, w, d in (
        (0, span + 0.49, span * 2 + 1, 0.98),
        (0, -span - 0.49, span * 2 + 1, 0.98),
        (-span - 0.49, 0, 0.98, span * 2 + 1),
        (span + 0.49, 0, 0.98, span * 2 + 1),
    ):
        collision("Continuous boundary core", x, y, -2, w, d, 22)
        block(
            "Parish boundary",
            (x, y, 1.30),
            (w + 0.13, d + 0.13, 3.25),
            "MossRock",
            "Rim",
        )


def house(x, y, w, d, h, style=0, height=land):
    base = float(height(x, y))
    lowest = (
        min(float(height(x + a * w / 2, y + b * d / 2)) for a in (-1, 1) for b in (-1, 1))
        - 0.26
    )
    block(
        "Stonework foundation",
        (x, y, (lowest + base + 0.55) / 2),
        (w + 0.19, d + 0.2, base + 0.55 - lowest),
        "Masonry",
    )
    block(
        "Limewash walls",
        (x, y, base + h * 0.5 + 0.1),
        (w, d, h),
        "HousePlaster" if style != 1 else "OchrePlaster",
    )
    roof = "RoofTiles" if style != 2 else "RoofSlate"
    top = base + h + w * 0.32

    def window(xx, yy, zz, sidewall=False):
        side = 1 if (xx > x if sidewall else yy > y) else -1

        def piece(name, u, v, n, ww, hh, depth, mat):
            at = (
                (xx + side * n, yy + u, zz + v)
                if sidewall
                else (xx + u, yy + side * n, zz + v)
            )
            shape = (depth, ww, hh) if sidewall else (ww, depth, hh)
            block(name, at, shape, mat)

        piece("Window reveal", 0, 0, 0.05, 1.11, 1.22, 0.13, "TarredOak")
        piece("Horn glazing", 0, 0, 0.13, 0.88, 0.94, 0.055, "WindowLight")
        for offset in (-0.22, 0.22):
            piece("Glazing bar", offset, 0, 0.17, 0.042, 0.94, 0.048, "Wood")
        piece("Glazing rail", 0, 0.04, 0.17, 0.88, 0.054, 0.049, "Wood")
        piece("Drip sill", 0, -0.65, 0.13, 1.31, 0.14, 0.32, "Masonry")

    for side in (-1, 1):
        edge = x + side * (w * 0.5 + 0.42)
        surf = [
            (edge, y - d * 0.5 - 0.48, base + h - 0.02),
            (edge, y + d * 0.5 + 0.48, base + h - 0.02),
            (x, y + d * 0.5 + 0.48, top + 0.06),
            (x, y - d * 0.5 - 0.48, top + 0.06),
        ]
        under = [(xx, yy, zz - 0.18) for xx, yy, zz in surf]
        faces = [
            (3, 2, 1, 0),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (1, 2, 6, 5),
            (2, 3, 7, 6),
            (3, 0, 4, 7),
        ]
        geometry(
            "Peg-tiled roof",
            surf + under,
            faces if side < 0 else [f[::-1] for f in faces],
            roof,
        )
        ridge_y = y + side * (d * 0.5 + 0.01)
        gable = [
            (x - w * 0.5, ridge_y, base + h - 0.03),
            (x + w * 0.5, ridge_y, base + h - 0.03),
            (x, ridge_y, top),
        ]
        geometry(
            "Gable plaster",
            gable,
            [(0, 1, 2) if side < 0 else (2, 1, 0)],
            "OchrePlaster",
        )
        for dx in (-0.48, 0, 0.48):
            block(
                "Half-timber post",
                (x + dx * w, ridge_y + side * 0.06, base + h * 0.50),
                (0.18, 0.15, h),
                "TarredOak",
            )
        for dx in (-0.25, 0.25):
            line(
                "Gable stud",
                (x + dx * w, ridge_y + side * 0.08, base + h),
                (x + dx * w, ridge_y + side * 0.08, base + h + w * 0.145),
                0.085,
                "TarredOak",
            )
        line(
            "King post",
            (x, ridge_y + side * 0.08, base + h),
            (x, ridge_y + side * 0.08, top),
            0.10,
            "Wood",
        )
        for dx in (-0.5, 0.5):
            line(
                "Diagonal rake",
                (x + dx * w, ridge_y + side * 0.09, base + h),
                (x, ridge_y + side * 0.09, top),
                0.13,
                "Wood",
            )
        wall = x + side * (w * 0.5 + 0.025)
        for frac in (-0.46, 0.46):
            block(
                "Sidewall corner",
                (wall, y + frac * d, base + h * 0.5),
                (0.15, 0.20, h),
                "TarredOak",
            )
        for z0 in (0.52, h - 0.25):
            block("Sidewall plate", (wall, y, base + z0), (0.14, d, 0.16), "Wood")
            block("Facade plate", (x, ridge_y, base + z0), (w, 0.18, 0.16), "Wood")
        for end in (-1, 1):
            line(
                "Knee brace",
                (wall, y + end * d * 0.46, base + h * 0.46),
                (wall, y + end * d * 0.27, base + h - 0.31),
                0.09,
                "Wood",
            )
        window(wall, y, base + h * 0.59, True)
        for dx in (-0.28, 0.28):
            window(x + dx * w, ridge_y, base + h * 0.59)
    front = y - d * 0.5 - 0.11
    block("Door jamb", (x, front, base + 1.15), (1.31, 0.18, 2.28), "TarredOak")
    block("Plank door", (x, front - 0.093, base + 1.09), (1.04, 0.08, 2.08), "Wood")
    for dz in (0.56, 1.66):
        block(
            "Strap hinge",
            (x - 0.23, front - 0.144, base + dz),
            (0.44, 0.035, 0.08),
            "BellMetal",
        )
    shaft(
        "Latch",
        (x + 0.31, front - 0.13, base + 1.02),
        (x + 0.31, front - 0.23, base + 1.02),
        0.065,
        0.08,
        "Brass",
        8,
    )
    block(
        "Chimney",
        (x + w * 0.25, y + 0.55, base + h + 0.68),
        (0.68, 0.70, 2.7),
        "HarbourBrick",
    )
    block(
        "Chimney cap",
        (x + w * 0.25, y + 0.55, base + h + 2.08),
        (0.82, 0.84, 0.18),
        "Masonry",
    )


def mark(i):
    x, y = TARGETS[i]
    z = target_z(i)
    h = float(land(x, y))
    if i == 0:
        house(x, y, 7.2, 5.1, 3.2)
        boat(x - 1.1, y - 6.35, float(land(x - 1.1, y - 6.35)) + 0.12, 1.42)
        for a in (-1, 1):
            end = (x + a * 3.5, y - 4.7, h + 2.4)
            line(
                "Davit iron stay",
                (x + a * 3.5, y - 2.55, h + 3.20),
                end,
                0.043,
                "BellMetal",
            )
            shaft(
                "Suspended hemp fall",
                end,
                (end[0], end[1], h + 0.65),
                0.039,
                0.038,
                "Wood",
                7,
            )
            ring(
                "Boat sling",
                (end[0], end[1], h + 0.55),
                0.12,
                0.035,
                "Brass",
                "y",
                n=10,
            )
            line(
                "Boat shed davit",
                (x + a * 3.5, y - 2.5, h + 0.1),
                (x + a * 3.5, y - 4.7, h + 2.4),
                0.16,
                "Wood",
            )
        line(
            "Boatbuilder's heraldic oar",
            (x - 0.9, y, z - 1.04),
            (x + 0.83, y, z + 0.89),
            0.13,
            "HousePlaster",
        )
        blade = [(0.13, 0.12), (0.29, 0.73), (1.22, 1.45), (1.62, 1.11), (0.81, 0.13)]
        outline = [
            (x + u, y + thick, z + v) for thick in (-0.15, 0.15) for u, v in blade
        ]
        geometry(
            "Carved white ash blade",
            outline,
            [(0, 1, 2, 3, 4), (9, 8, 7, 6, 5)]
            + [(j, (j + 1) % 5, 5 + (j + 1) % 5, 5 + j) for j in range(5)],
            "HousePlaster",
        )
    elif i == 1:
        house(x, y, 8.4, 5.8, 3.9, 1)
        block(
            "School noticeboard",
            (x + 2.72, y - 3.07, h + 1.04),
            (1.18, 0.17, 0.88),
            "TarredOak",
        )
        for a in range(3):
            block(
                "Chalk writing",
                (x + 2.68, y - 3.18, h + 1.27 - a * 0.17),
                (0.76 - 0.12 * a, 0.025, 0.035),
                "HousePlaster",
            )
        lathe(
            "Gilded solar boss",
            x,
            y,
            z - 0.57,
            [
                (0.13, 0),
                (0.42, 0.13),
                (0.55, 0.40),
                (0.55, 0.72),
                (0.38, 1.03),
                (0.11, 1.14),
            ],
            "Amber",
            12,
        )
        for axis in ("x", "y"):
            ring("Armillary solar band", (x, y, z), 0.70, 0.12, "Amber", axis, n=20)
            for a in range(10):
                q = (a + 0.25) * TAU / 10
                dx, dy = (math.cos(q), 0) if axis == "y" else (0, math.cos(q))
                shaft(
                    "Gilded solar ray",
                    (x + 0.77 * dx, y + 0.77 * dy, z + 0.77 * math.sin(q)),
                    (x + 1.44 * dx, y + 1.44 * dy, z + 1.44 * math.sin(q)),
                    0.115,
                    0.034,
                    "Brass",
                    7,
                )
    else:
        for a in (-1, 1):
            block(
                "Lock gatehouse pier",
                (x + a * 2.4, y, h + 1.7),
                (1.5, 2, 4.7),
                "Masonry",
            )
        block("Lock crosshead", (x, y, h + 4.2), (7.15, 1.56, 1.05), "TarredOak")
        ring("Forked key bow", (x, y, z + 0.50), 0.63, 0.16, "Brass", "y")
        line("Key stem", (x, y, z - 1.18), (x, y, z + 0.12), 0.15, "Brass")
        for zz in (-1, -0.58):
            line("Key beard", (x, y, z + zz), (x + 0.72, y, z + zz), 0.14, "Brass")
    lathe(
        "Daymark mast",
        x,
        y,
        h,
        [(0.31, 0), (0.22, 3.6), (0.14, z - h - 1), (0.079, z - h + 0.08)],
        "TarredOak",
        10,
    )
    marker("Target" + str(i), x, y, z)


def boat(x, y, z, angle=0, larger=False):
    scale = 1.40 if larger else 1

    def point(dx, dy, dz):
        return (
            x + scale * (dx * math.cos(angle) - dy * math.sin(angle)),
            y + scale * (dx * math.sin(angle) + dy * math.cos(angle)),
            z + scale * dz,
        )

    hull = [
        (-0.08, -2.8),
        (-0.76, -1.55),
        (-0.91, 0.50),
        (-0.57, 2.20),
        (0, 2.77),
        (0.57, 2.20),
        (0.91, 0.50),
        (0.76, -1.55),
        (0.08, -2.8),
    ]
    pts = [
        point(dx * r, dy * r, h + 0.19 * abs(dy / 2.8) ** 3)
        for r, h in ((0.61, 0), (1, 0.40), (0.91, 0.51))
        for dx, dy in hull
    ]
    n = len(hull)
    geometry(
        "Clinker-built ferry",
        pts,
        [
            (k * n + j, k * n + (j + 1) % n, (k + 1) * n + (j + 1) % n, (k + 1) * n + j)
            for k in range(2)
            for j in range(n)
        ]
        + [tuple(range(n - 1, -1, -1)), tuple(range(2 * n, 3 * n))],
        "Wood",
    )
    for dy in (-1.1, 0.33, 1.26):
        line(
            "Oiled thwart",
            point(-0.64, dy, 0.58),
            point(0.64, dy, 0.58),
            0.12,
            "TarredOak",
        )
    if larger:
        shaft(
            "Ferry mast",
            point(0, 0.33, 0.55),
            point(0, 0.33, 3.54),
            0.09,
            0.045,
            "Wood",
            8,
        )
        geometry(
            "Reefed mainsail",
            [point(0, 0.33, 3.32), point(0, -1.7, 0.93), point(0, 0.3, 1.09)],
            [(0, 1, 2)],
            "HousePlaster",
        )


def watercourse(high):
    level = 1.02 if high else 0.38
    pts = []
    for x in range(-60, 61, 2):
        y = river(x)
        w = 8.2 if high else 5.3
        pts.extend([(x, y - w, level), (x, y + w, level)])
    geometry(
        "Tidal water surface",
        pts,
        [(i, i + 2, i + 3, i + 1) for i in range(0, len(pts) - 2, 2)],
        "ParishWater",
        "Waterline",
    )
    for side in (-1, 1):
        for x in range(-58, 59, 4):
            if any(abs(x - b) < 5 for b in BRIDGES):
                continue
            a = x - 2
            b = x + 2
            ya = river(a) + side * 8.6
            yb = river(b) + side * 8.6
            za = float(land(a, ya))
            zb = float(land(b, yb))
            line("Larch rail", (a, ya, za + 1.12), (b, yb, zb + 1.12), 0.11, "Wood")
            shaft(
                "Tide-pier pile",
                (a, ya, za - 0.3),
                (a, ya, za + 1.43),
                0.16,
                0.13,
                "TarredOak",
                7,
            )
    for j, bx in enumerate(BRIDGES):
        cy = float(river(bx))
        open_ = (high and j == 1) or (not high and j == 0) or j == 2
        if j == 0:
            pts = []
            for k in range(-11, 12):
                y = cy + k * 0.91
                for dx in (-1.76, -1.36, 1.36, 1.76):
                    x = bx + dx + 0.11 * math.sin(k)
                    z = max(0.59, float(land(x, y)) + 0.08)
                    pts.append((x, y, z - 0.39 if abs(dx) > 1.5 else z))
            geometry(
                "Oyster shingle causeway",
                pts,
                [
                    (4 * k + i, 4 * k + i + 1, 4 * k + i + 5, 4 * k + i + 4)
                    for k in range(22)
                    for i in range(3)
                ],
                "MossRock",
            )
        else:
            for k in range(-10, 11):
                y = cy + k * 0.95
                z = max(level + 0.22, float(land(bx, y))) + 0.035
                bottom = (
                    min(
                        float(land(bx + dx, y + dy))
                        for dx in (-1.72, 1.72)
                        for dy in (-0.47, 0.47)
                    )
                    - 0.14
                )
                block(
                    "Bridge abutment" if j == 2 else "Tide ferry pontoon",
                    (bx, y, (z - 0.10 + bottom) / 2),
                    (3.4, 0.97, z - 0.10 - bottom),
                    "Masonry" if j == 2 else "TarredOak",
                )
                block("Shod bridge decking", (bx, y, z), (3.5, 0.97, 0.24), "Wood")
                if k % 3 == 0:
                    for side in (-1, 1):
                        xx = bx + side * 1.68
                        shaft(
                            "Bridge post",
                            (xx, y, float(land(xx, y)) - 0.22),
                            (xx, y, z + 1.00),
                            0.13,
                            0.11,
                            "TarredOak",
                            7,
                        )
        if not open_:
            yy = cy - 8
            zz = float(land(bx, yy))
            for side in (-1, 1):
                block(
                    "Closed tidegate jamb",
                    (bx + side * 1.92, yy, zz + 1.57),
                    (0.40, 0.57, 3.35),
                    "Masonry",
                )
            for k in range(9):
                block(
                    "Lowered portcullis",
                    (bx + (k - 4) * 0.40, yy, zz + 1.29),
                    (0.14, 0.18, 2.75),
                    "TarredOak",
                )
            block(
                "Bottom rail of tide gate",
                (bx, yy, zz + 0.45),
                (3.6, 0.23, 0.26),
                "BellMetal",
            )
            block(
                "Upper rail of tide gate",
                (bx, yy, zz + 2.51),
                (3.6, 0.23, 0.26),
                "Wood",
            )
    for i, xx in enumerate((-54, -36, -15, 20, 32, 55)):
        yy = float(river(xx)) + (-1 if i % 2 else 1) * 2.6
        boat(
            xx,
            yy,
            level if high else float(land(xx, yy)) + 0.02,
            0.93 - 0.32 * (i % 3),
            i % 3 == 1,
        )
    for i in range(74):
        x = -58 + (i * 193 % 116)
        if min(abs(x - b) for b in BRIDGES) < 3:
            continue
        sign = (-1, 1)[i % 2]
        y = float(river(x)) + sign * (4.6 + (i * 7 % 20) * 0.105)
        z = float(land(x, y)) - 0.04
        for n in range(3):
            dx = (n - 1) * 0.19
            h = 0.75 + 0.12 * ((n + i) % 4)
            shaft(
                "Rush",
                (x + dx, y, z),
                (x + dx + 0.09, y + 0.05, z + h),
                0.04,
                0.018,
                "Reeds",
                5,
            )
            if n == 1:
                shaft(
                    "Reed head",
                    (x + dx + 0.09, y + 0.05, z + h - 0.13),
                    (x + dx + 0.10, y + 0.05, z + h + 0.14),
                    0.061,
                    0.05,
                    "Wood",
                    6,
                )


def water_tile():
    n = 64
    j, i = np.mgrid[:n, :n]
    rng = np.random.default_rng(813)
    wav = (
        np.sin(i * TAU / 32 + 1.5 * np.sin(j * TAU / 32)) * 4
        + np.sin(j * TAU / 9.14 + 1.75 * np.cos(i * TAU / 32)) * 3
    )
    base = np.array([83, 127, 130]) + wav[:, :, None] + rng.normal(0, 1.7, (n, n, 1))
    Image.fromarray(np.uint8(base)).save(RES / "Textures/ParishWater.png")


def transit(id, x, y, z, target):
    tx, ty, tz = target
    dx, dy = tx - x, ty - y
    leng = math.hypot(dx, dy)
    dx /= leng
    dy /= leng
    for a in (0, 2.09, 4.19):
        shaft(
            "Transit tripod leg",
            (x + 0.60 * math.cos(a), y + 0.6 * math.sin(a), z - 0.04),
            (x, y, z + 1.21),
            0.069,
            0.077,
            "Wood",
            7,
        )
    lathe(
        "Azimuth circle",
        x,
        y,
        z + 1.16,
        [(0.4, 0), (0.42, 0.08), (0.27, 0.16)],
        "Brass",
        16,
    )
    for i in range(8):
        a = i * TAU / 8
        line(
            "Graduation",
            (x + 0.31 * math.cos(a), y + 0.31 * math.sin(a), z + 1.27),
            (x + 0.39 * math.cos(a), y + 0.39 * math.sin(a), z + 1.27),
            0.018,
            "BellMetal",
        )
    slope = (tz - z - 1.46) / leng
    for a, b, rad, mat in (
        (-0.59, 0.45, 0.115, "Brass"),
        (0.37, 0.72, 0.155, "VerdigrisSheet"),
        (-0.69, -0.52, 0.095, "BellMetal"),
    ):
        shaft(
            "Parish sighting telescope",
            (x + a * dx, y + a * dy, z + 1.45 + a * slope),
            (x + b * dx, y + b * dy, z + 1.45 + b * slope),
            rad,
            rad,
            mat,
            10,
        )
    group = "Stamped" + id
    lathe(
        "Survey wax seal",
        x + 0.48,
        y - 0.1,
        z + 1.01,
        [(0.11, 0), (0.135, 0.06), (0.10, 0.1)],
        "Pennon",
        8,
        group,
    )


def shore(key, r, high):
    terrain(key, 60, land, 3)
    watercourse(high)
    for name, x, y in (("MapSW", -60, -60), ("MapSE", 60, -60), ("MapNW", -60, 60)):
        marker(name, x, y, 0)
    for sx, sy in ((-12, -16), (19, 40)):
        grade = float(land(sx, sy))
        for dx in (-1.65, 1.65):
            block(
                "Survey board post",
                (sx + dx, sy, grade + 1.48),
                (0.18, 0.23, 3.24),
                "Wood",
            )
        block(
            "Field chart case", (sx, sy, grade + 2.1), (3.56, 0.24, 2.56), "TarredOak"
        )
        panel(
            "Ada’s local field sheet",
            sx,
            sy - 0.145,
            grade + 0.91,
            3.35,
            2.38,
            key + "Survey",
        )

    for i in range(3):
        mark(i)
    for j, (x, y, w, d, h) in enumerate(
        (
            (-17, -33, 7, 4.2, 3.1),
            (23, -36, 6.8, 4.4, 3.6),
            (-36, -10, 5.2, 4.1, 2.7),
            (17, 49, 6.8, 4.4, 3.5),
            (-51, 47, 6.6, 4.2, 3.2),
            (49, -41, 5.4, 4.3, 3),
        )
    ):
        house(x, y, w, d, h, j % 3)
    for j in range(29):
        x = -55 + ((73 * j) % 110)
        y = -55 + ((47 * j) % 109)
        if (
            abs(y - river(x)) < 11
            or any(math.hypot(x - s["x"], y - s["y"]) < 6 for s in r["stations"])
            or any(math.hypot(x - tx, y - ty) < 7 for tx, ty in TARGETS)
        ):
            continue
        if any(
            math.hypot(x - px, y - py) < 8
            for px, py in (
                (-17, -33),
                (23, -36),
                (-36, -10),
                (17, 49),
                (-51, 47),
                (49, -41),
                (6, -16),
            )
        ):
            continue
        near_sight = False
        for i, pair in enumerate(SITES):
            _, _, ax, ay = pair[int(high)]
            bx, by = TARGETS[i]
            dx, dy = bx - ax, by - ay
            t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / (dx**2 + dy**2)))
            if math.hypot(x - ax - t * dx, y - ay - t * dy) < 4.8:
                near_sight = True
        if near_sight:
            continue
        z = float(land(x, y))
        shaft(
            "Pollard willow",
            (x, y, z - 0.18),
            (x + 0.23, y, z + 3.56),
            0.46,
            0.25,
            "Wood",
            9,
        )
        oak_crown(
            x + 0.18, y, z + 3.49, 2.62 + (j % 3) * 0.25, 2.02 + 0.17 * (j % 4), 921 + j
        )
    # A continuous band of chalk bluffs follows the horizon beyond the playable banks.
    bands = []
    for i in range(56):
        a = i * TAU / 56
        bluff_radius = 85 + 4 * math.cos(a * 7) + 3 * math.sin(a * 5)
        h = 13 + 4 * math.cos(a * 3) + 2.1 * math.sin(a * 8) + 1.5 * math.sin(a * 14)
        for radius, z in (
            (bluff_radius - 9, -3),
            (bluff_radius - 2, h * 0.58),
            (bluff_radius + 1.1, h * 0.86),
            (bluff_radius + 2.8, h),
            (bluff_radius + 12, h + 1.6),
        ):
            bands.append((radius * math.cos(a), radius * math.sin(a), z))
    for tier in range(4):
        faces = [
            (
                5 * i + tier,
                5 * i + tier + 1,
                5 * ((i + 1) % 56) + tier + 1,
                5 * ((i + 1) % 56) + tier,
            )
            for i in range(56)
        ]
        geometry(
            "Layer of coastal chalk",
            bands,
            faces,
            ("Mountain", "MossRock", "Mountain", "Grass")[tier],
            "Horizon",
        )
    for j, s in enumerate(r["stations"]):
        x, y = s["x"], s["y"]
        z = float(land(x, y))
        id = s["id"][2:]
        kind = s["style"]
        if kind == "person":
            model("WZ_SWA_N01", "Ada", x, y, z, 1.72, 8, "Speaker")
            block(
                "Ada’s map case",
                (x + 0.30, y - 0.04, z + 0.85),
                (0.27, 0.19, 0.40),
                "VerdigrisSheet",
            )
            shaft(
                "Rolled parish chart",
                (x + 0.19, y - 0.07, z + 1.05),
                (x + 0.43, y - 0.07, z + 1.05),
                0.065,
                0.065,
                "HousePlaster",
                9,
            )
        elif kind == "sight":
            i = next(i for i, p in enumerate(SITES) if p[int(high)][0] == id)
            transit(id, x, y, z, (*TARGETS[i], target_z(i)))
        elif kind == "tidebell":
            for a in (-1, 1):
                shaft(
                    "Bell-post",
                    (x + a * 0.88, y, z - 0.10),
                    (x + a * 0.88, y, z + 3.22),
                    0.16,
                    0.13,
                    "TarredOak",
                    8,
                )
            line(
                "Bell yoke",
                (x - 0.96, y, z + 3.05),
                (x + 0.96, y, z + 3.05),
                0.13,
                "Wood",
            )
            bell(x, y, z + 1.74, 1.42, "Set")
            line(
                "Pull rope",
                (x + 0.4, y, z + 2),
                (x + 0.55, y - 0.2, z + 0.83),
                0.047,
                "Brass",
            )
        elif kind == "office":
            house(x, y + 2.56, 5.75, 4.9, 2.92, 2)
        else:
            arch(x, y, z, 3.4, 3.78, "Masonry", "Wood")
        if kind not in ("person",):
            if kind not in ("exit", "office"):
                block(
                    "Sign board",
                    (x, y - 0.255, z + 0.72),
                    (1.42, 0.135, 0.37),
                    "TarredOak",
                )
            mount(s, 0, r, j, lambda k, x, y: float(land(x, y)))
        marker(s["id"], x, y - 0.52, z + 1.43)
        marker(s["camp"], x, y - 2.38, float(land(x, y - 2.38)) + 0.08)
    marker("Spawn", 0, -14, 0.08)
    marker("Look", 0, 3, 1.6)
    finish(key, sky_key=r["theme"])


def draw_chart():
    size = 512
    yy, xx = np.mgrid[:size, :size]
    x = xx * 96 / (size - 1) - 48
    y = 48 - yy * 96 / (size - 1)
    h = land(x, y)
    texture = np.random.default_rng(511).normal(0, 2.8, (size, size))
    parchment = np.empty((size, size, 3))
    parchment[:] = [221, 203, 159]
    parchment += (h[:, :, None] - 1) * [-5, -3, -2] + texture[:, :, None]
    delta = abs(y - river(x))
    parchment[delta < 6.6] = [135, 171, 164]
    parchment[delta < 3.8] = [105, 145, 146]
    contours = (np.mod(h, 0.46) < 0.016) & (delta > 7)
    parchment[contours] = [164, 161, 120]
    im = Image.fromarray(np.uint8(np.clip(parchment, 0, 255)))
    d = ImageDraw.Draw(im)
    pt = lambda x, y: ((x + 48) / 96 * (size - 1), (48 - y) / 96 * (size - 1))
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 13)
    for i in range(5):
        u = (i - 2) * 19
        d.line((pt(-48, u), pt(48, u)), fill="#897953", width=2)
        d.line((pt(u, -48), pt(u, 48)), fill="#897953", width=2)
        d.text(pt(u, 46.4), str(i), font=f, fill="#6b5048", anchor="mt")
        d.text(pt(-47, u), str(i), font=f, fill="#6b5048", anchor="lm")
    for j, pair in enumerate(SITES):
        for side, (_, _, px, py) in enumerate(pair):
            qx, qy = pt(px, py)
            color = "#913e3b" if not side else "#3a6977"
            d.ellipse(
                (qx - 5, qy - 5, qx + 5, qy + 5), fill=color, outline="#f2e4b9", width=2
            )
    d.rectangle((1, 1, 510, 510), outline="#655140", width=4)
    im.save(RES / "Textures/ParishChart.png")
    im = Image.new("RGB", (512, 384), "#d7be93")
    d = ImageDraw.Draw(im)
    for j, title in enumerate(PLACES):
        x = j % 2 * 256
        y = j // 2 * 192
        d.rectangle((x + 4, y + 4, x + 252, y + 188), outline="#85594d", width=3)
        d.text(
            (x + 128, y + 30),
            "SURVEY FOLIO  " + str(j + 1),
            fill="#4e615c",
            font=f,
            anchor="mm",
        )
        d.text((x + 128, y + 72), title, fill="#694d41", font=f, anchor="mm")
        for side, (_, label, _, _) in enumerate(SITES[j]):
            d.line(
                (x + 30, y + 112 + 27 * side, x + 58, y + 112 + 27 * side),
                fill=("#913e3b", "#3a6977")[side],
                width=4,
            )
            d.text(
                (x + 66, y + 112 + 27 * side),
                label,
                fill="#534f42",
                font=f,
                anchor="lm",
            )
    im.save(RES / "Textures/ParishFolios.png")


def board(x, y, depth):
    return (x * 0.080, depth, 1.91 + (y + 48) * 0.055)


def clip_line(ax, ay, bx, by):
    dx = bx - ax
    dy = by - ay
    ends = []
    for limit in (-48, 48):
        if dx:
            t = (limit - ax) / dx
            v = ay + t * dy
            if -48 <= v <= 48:
                ends.append((limit, v))
        if dy:
            t = (limit - ay) / dy
            u = ax + t * dx
            if -48 <= u <= 48:
                ends.append((u, limit))
    return ends[0], ends[-1]


def office(r):
    terrain(OFFICE, 20, lambda x, y: office_height(0, x, y), 2)
    for side in (-1, 1):
        block(
            "Office sidewall",
            (side * 11.25, 1, 2.84),
            (0.49, 24.2, 5.98),
            "OchrePlaster",
        )
        for yy in (-10, -4, 2, 8, 12):
            block(
                "Oak wall stud",
                (side * 10.94, yy, 3.05),
                (0.33, 0.35, 6.1),
                "TarredOak",
            )
            line(
                "Queen-post truss",
                (side * 11.12, yy, 5.95),
                (0, yy, 8.62),
                0.24,
                "Wood",
            )
        geometry(
            "Office slate roof",
            [
                (side * 11.88, -11.45, 6.18),
                (side * 11.88, 13.88, 6.18),
                (0, 13.88, 8.95),
                (0, -11.45, 8.95),
            ],
            [(0, 1, 2, 3)],
            "RoofSlate",
        )
    block("Office rear wall", (0, 13.13, 3.02), (22.9, 0.52, 6.55), "OchrePlaster")
    for yy in (-10.98, 13.13):
        geometry(
            "Limewashed office gable",
            [(-11.5, yy, 6.09), (11.5, yy, 6.09), (0, yy, 8.91)],
            [(0, 1, 2)],
            "HousePlaster",
        )
        block("Gable tie beam", (0, yy - 0.08, 6.15), (22.98, 0.24, 0.31), "TarredOak")
        for k in range(-3, 4):
            xx = k * 2.7
            length = 2.47 * (1 - abs(xx) / 11.5)
            block(
                "Gable stud",
                (xx, yy - 0.1, 6.26 + length / 2),
                (0.15, 0.19, length),
                "Wood",
            )
    for xx in (-10.18, -3.72, 3.72, 10.18):
        width = 2.18 if abs(xx) > 8 else 3.56
        block(
            "Office front infill",
            (xx, -10.94, 2.89),
            (width, 0.28, 6.26),
            "OchrePlaster",
        )
    block("Portico lintel", (0, -10.94, 4.95), (22.66, 0.30, 2.41), "OchrePlaster")

    for row in (1.6, 3.05, 4.53):
        for k in range(7):
            xx = -8.0 + k * 2.65
            block("Ledger shelf", (xx, 12.65, row), (2.6, 0.60, 0.14), "Wood")
            for j in range(7):
                block(
                    "Cloth spine",
                    (xx - 0.92 + j * 0.29, 12.6, row + 0.41),
                    (0.22, 0.46, 0.63 + 0.09 * ((j + k) % 3)),
                    ("SeaCloth", "Pennon", "FernCloth", "TarredOak")[(j + k) % 4],
                )
    block("Survey board", (0, 6.51, 4.45), (8.14, 0.38, 5.8), "TarredOak")
    panel("Survey of Sillwater", 0, 6.29, 1.91, 7.68, 5.28, "ParishChart")
    for xx in (-4.06, 4.06):
        block("Chart standard", (xx, 6.52, 3.75), (0.26, 0.45, 7.68), "Wood")
        lathe(
            "Brass finial",
            xx,
            6.52,
            7.55,
            [(0.07, 0), (0.19, 0.10), (0.13, 0.24), (0.045, 0.36)],
            "Brass",
            9,
        )
    for k, pair in enumerate(SITES):
        tx, ty = TARGETS[k]
        for side, (_, _, x, y) in enumerate(pair):
            a, b = clip_line(x, y, tx, ty)
            depth = 6.21 - side * 0.038
            line(
                "Sight bearing",
                board(*a, depth),
                board(*b, depth),
                0.042,
                "Pennon" if not side else "SeaCloth",
                "Thread" + str(k) + str(side),
            )
        panel(
            "Title search docket",
            -6.2,
            6.22,
            2.32,
            3.26,
            2.45,
            "ParishFolios",
            "Folio" + str(k),
            k,
        )
        lathe(
            "New parish seal",
            -6.98 + k * 0.72,
            5.97,
            1.68,
            [(0.12, 0), (0.21, 0.08), (0.19, 0.18)],
            "Amber",
            9,
            "Plaque" + str(k),
        )
    block("Index case", (-6.20, 6.48, 2.56), (3.63, 0.44, 4.57), "Wood")
    start = board(-38, -38, 6.04)
    marker("RailStart", *start)
    marker("RailEnd", *board(38, -38, 6.04))
    ring("Carriage sight", start, 0.23, 0.055, "Brass", "y", "MapPin", 18)
    for dx, dz in ((0.24, 0), (-0.24, 0), (0, 0.24), (0, -0.24)):
        line(
            "Cursor index vane",
            (start[0] + dx * 0.9, start[1], start[2] + dz * 0.9),
            (start[0] + dx * 1.55, start[1], start[2] + dz * 1.55),
            0.028,
            "Brass",
            "MapPin",
        )
    for i, s in enumerate(r["stations"]):
        x, y = s["x"], s["y"]
        id = s["id"][2:]
        z = office_height(0, x, y)
        kind = s["style"]
        if kind == "person":
            model("WZ_VIL_N03", "The registrar", x, y, z, 1.72, 16, "Speaker")
        elif kind == "office":
            arch(x, y, z, 2.8, 3.13, "Masonry", "Wood")
        else:
            block(
                "Oiled writing desk", (x, y, z + 0.48), (1.71, 0.88, 0.99), "TarredOak"
            )
            block("Wear-polished rim", (x, y, z + 1), (1.83, 0.95, 0.12), "Wood")
            if kind == "handle":
                ring(
                    "Hand carriage wheel",
                    (x, y, z + 1.42),
                    0.34,
                    0.057,
                    "Brass",
                    "y",
                    n=14,
                )
                for j in range(3):
                    a = TAU * j / 3
                    line(
                        "Spoke",
                        (x, y, z + 1.42),
                        (x + 0.33 * math.cos(a), y, z + 1.42 + 0.33 * math.sin(a)),
                        0.038,
                        "BellMetal",
                    )
            elif kind == "press":
                shaft(
                    "Press screw",
                    (x, y, z + 1.03),
                    (x, y, z + 1.85),
                    0.13,
                    0.11,
                    "BellMetal",
                    9,
                )
                line(
                    "Wooden press handle",
                    (x - 0.45, y, z + 1.85),
                    (x + 0.45, y, z + 1.85),
                    0.07,
                    "Wood",
                )
            else:
                block(
                    "Green map cover", (x, y, z + 1.13), (1.37, 0.77, 0.13), "FernCloth"
                )
                lathe(
                    "Parish seal",
                    x,
                    y,
                    z + 1.20,
                    [(0.19, 0), (0.21, 0.09), (0.08, 0.16), (0.14, 0.43)],
                    "Brass",
                    9,
                )
        marker(s["id"], x, y - 0.52, z + 1.42)
        marker(s["camp"], x, y - 2.23, office_height(0, x, y - 2.23) + 0.08)
        if kind != "person":
            sign = dict(s)
            if kind != "office":
                sign["y"] -= 0.14
            mount(sign, 0, r, i, office_height)
    marker("Spawn", 0, -14, 0.08)
    marker("Look", 0, 4, 2)
    finish(OFFICE, sky_key=r["theme"])


def make(key, lib):
    r = next(r for r in rooms if r["key"] == key)
    water_tile()
    draw_chart()
    material_paint(key, key == HIGH, key == OFFICE)
    plaques(1 if key != HIGH else 5, r)
    if key != OFFICE:
        field_sheet(key, r, key == HIGH)
    init(lib, 3410 + (key == HIGH))
    if key == OFFICE:
        office(r)
    else:
        shore(key, r, key == HIGH)
