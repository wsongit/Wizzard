"""The Quiet, an original jointed night-watch automaton for the Still Belfry."""

import math
from PIL import Image, ImageDraw
import numpy as np
from atelier import RES, geometry, shaft, origins

ATLAS = "QuietEnamel"
PALETTE = (
    (45, 60, 77),
    (70, 100, 111),
    (89, 125, 122),
    (125, 144, 129),
    (139, 88, 56),
    (185, 136, 74),
    (223, 178, 106),
    (220, 205, 163),
    (62, 46, 44),
    (88, 63, 52),
    (160, 79, 52),
    (194, 117, 74),
    (51, 77, 91),
    (55, 90, 91),
    (127, 121, 104),
    (224, 153, 77),
)


def paint():
    rng = np.random.default_rng(1738)
    im = Image.new("RGB", (256, 256))
    y, x = np.indices((64, 64))
    for i, pigment in enumerate(PALETTE):
        wear = 4 * np.cos((x + y * 0.78) / 7) + 2 * np.sin(y / 3.5) + rng.normal(0, 2.2, (64, 64))
        tile = Image.fromarray(np.uint8(np.clip(np.array(pigment) + wear[..., None], 0, 255)))
        im.paste(tile, ((i % 4) * 64, (i // 4) * 64))
    # Inlays run the length of the overlapping flight feathers.
    pen = ImageDraw.Draw(im)
    for i in (0, 1, 2, 3, 12, 13):
        left, top = (i % 4) * 64, (i // 4) * 64
        c = tuple(min(255, v + 20) for v in PALETTE[i])
        pen.line([(left + 31, top + 4), (left + 31, top + 57)], fill=c, width=2)
        for v in (18, 27, 36, 45):
            pen.line(
                [(left + 13, top + v - 9), (left + 31, top + v + 4), (left + 51, top + v - 11)],
                fill=c,
                width=1,
            )
    im.save(RES / "Textures" / (ATLAS + ".png"))


def keeper(x, y):
    def part(name, points, faces, colour, group, uvs=None):
        swatch = colour if isinstance(colour, list) else [colour] * len(faces)
        atlas_uv = []
        for pigment, face in zip(swatch, faces):
            coords = (
                uvs
                if uvs is not None
                else [(0.1 + 0.80 * (i % 2), 0.12 + 0.74 * (i // 2 % 2)) for i in range(len(face))]
            )
            for u, v in coords:
                atlas_uv.append(
                    ((64 * (pigment % 4) + 4 + 56 * u) / 256, 1 - (64 * (pigment // 4) + 4 + 56 * v) / 256)
                )
        return geometry(name, [(px + x, py + y, pz) for px, py, pz in points], faces, ATLAS, group, atlas_uv)

    def shell(name, rows, pigment, group="Speaker", count=12, pleats=0):
        pts = []
        for z, rx, ry, offset in rows:
            for i in range(count):
                a = i * math.tau / count
                k = 1 + pleats * (i % 2)
                pts.append((rx * k * math.sin(a), offset - ry * k * math.cos(a), z))
        faces = [tuple(reversed(range(count)))]
        for j in range(len(rows) - 1):
            for i in range(count):
                h = j * count
                nx = (i + 1) % count
                faces.append((h + i, h + nx, h + nx + count, h + i + count))
        faces.append(tuple(range(len(pts) - count, len(pts))))
        part(name, pts, faces, pigment, group)

    def enamel(name, outline, relief, colour, group):
        cx, cy, cz = [sum(p[i] for p in outline) / len(outline) for i in range(3)]
        points = outline + [(cx, cy - relief, cz)]
        faces = [(len(outline), i, (i + 1) % len(outline)) for i in range(len(outline))]
        part(name, points, faces, colour, group)

    # Eight folded stays hold a fluted funeral mantle above two cable-wrapped feet.
    for side in (-1, 1):
        for d in (-0.14, 0.14):
            shaft(
                "Bronze split toe",
                (x + side * 0.30, y - 0.02, 0.19),
                (x + side * 0.33 + d, y - 0.42, 0.05),
                0.12,
                0.048,
                "BellMetal",
                7,
                "Speaker",
            )
        shaft(
            "Hinged ankle",
            (x + side * 0.30, y, 0.14),
            (x + side * 0.31, y + 0.04, 0.97),
            0.13,
            0.16,
            "Wood",
            8,
            "Speaker",
        )
    shell(
        "Fluted watch coat",
        [
            (0.34, 0.58, 0.35, 0.08),
            (0.56, 0.72, 0.42, 0.08),
            (1.05, 0.62, 0.39, 0.09),
            (1.75, 0.42, 0.32, 0.07),
            (2.25, 0.74, 0.45, 0.08),
            (2.59, 0.62, 0.36, 0.06),
        ],
        0,
        count=24,
        pleats=0.115,
    )
    shell(
        "Repoussé brass belt",
        [(1.44, 0.54, 0.39, 0.08), (1.55, 0.55, 0.39, 0.08), (1.61, 0.52, 0.37, 0.08)],
        5,
    )
    shell(
        "Verdigris gorget",
        [
            (2.20, 0.76, 0.47, 0.05),
            (2.34, 0.89, 0.46, 0.06),
            (2.64, 0.56, 0.36, 0.05),
            (2.72, 0.33, 0.25, 0.04),
        ],
        2,
    )
    for side in (-1, 1):
        enamel(
            "Folded scale over the heart",
            [(0, -0.48, 2.53), (side * 0.56, -0.34, 2.50), (side * 0.38, -0.40, 2.16), (0, -0.51, 2.01)],
            0.035,
            3,
            "Speaker",
        )
        for k in range(3):
            shaft(
                "Clapper chain link",
                (x + side * (0.28 + 0.025 * k), y - 0.34, 1.40 - 0.13 * k),
                (x + side * (0.30 + 0.025 * k), y - 0.35, 1.29 - 0.13 * k),
                0.025,
                0.025,
                "Brass",
                6,
                "Speaker",
            )
    # A knuckle joint and two courses of individually cut flight feathers on each wing.
    for side in (-1, 1):
        wing = "KeeperLeft" if side < 0 else "KeeperRight"
        origins[wing] = (x + side * 0.68, y, 2.43)
        shaft(
            "Wing spar",
            (x + side * 0.65, y, 2.43),
            (x + side * 1.14, y - 0.07, 1.77),
            0.22,
            0.15,
            "BellMetal",
            10,
            wing,
        )
        for level, count in ((0, 6), (1, 5)):
            for k in range(count):
                t = k / (count - 1)
                sx = side * (0.61 + 0.46 * t)
                tip = side * (0.80 + 1.10 * t)
                root = 2.36 - 0.31 * t + level * 0.075
                end = 0.69 + 0.77 * t + level * 0.67
                depth = -0.055 - level * 0.115
                mid = sx + (tip - sx) * 0.58
                outline = [
                    (sx - side * 0.125, depth, root - 0.03),
                    (sx + side * 0.11, depth + 0.02, root),
                    (mid + side * 0.15, depth, (end + root) * 0.5),
                    (tip, depth - 0.07, end),
                    (mid - side * 0.12, depth - 0.04, (end + root) * 0.5),
                ]
                enamel(
                    "Chased primary" if not level else "Overlapping covert",
                    outline,
                    0.07,
                    [0, 1, 2, 12, 13, 1][k] if not level else [1, 2, 3, 2, 1][k],
                    wing,
                )
                shaft(
                    "Feather spine",
                    (x + sx, y + depth - 0.065, root - 0.13),
                    (x + tip, y + depth - 0.08, end + 0.04),
                    0.020,
                    0.009,
                    "Brass",
                    5,
                    wing,
                )
        shaft(
            "Embossed shoulder rivet",
            (x + side * 0.73, y - 0.29, 2.38),
            (x + side * 0.73, y - 0.34, 2.38),
            0.116,
            0.108,
            "Brass",
            10,
            wing,
        )
    # A heart-shaped porcelain face under a cowl. Relief eye-rims, deep sockets and a faceted beak.
    group = "KeeperMask"
    origins[group] = (x, y, 2.75)
    shell(
        "Night heron cowl",
        [
            (2.57, 0.27, 0.24, 0.07),
            (2.81, 0.45, 0.34, 0.06),
            (3.32, 0.55, 0.40, 0.05),
            (3.55, 0.43, 0.32, 0.10),
            (3.83, 0.18, 0.19, 0.18),
            (3.97, 0.035, 0.035, 0.24),
        ],
        0,
        group,
    )
    for side in (-1, 1):
        enamel(
            "White mask lobe",
            [
                (side * 0.035, -0.44, 3.36),
                (side * 0.26, -0.42, 3.51),
                (side * 0.50, -0.28, 3.41),
                (side * 0.42, -0.33, 3.12),
                (side * 0.17, -0.39, 2.91),
                (0, -0.46, 2.81),
            ],
            0.10,
            7,
            group,
        )
        ring = [
            (side * 0.075, -0.534, 3.25),
            (side * 0.22, -0.536, 3.37),
            (side * 0.408, -0.445, 3.33),
            (side * 0.34, -0.491, 3.19),
            (side * 0.21, -0.546, 3.11),
        ]
        enamel("Copper orbital rim", ring, 0.023, 5, group)
        cx, cy, cz = side * 0.242, -0.568, 3.238
        enamel(
            "Obsidian eye",
            [(cx + (px - cx) * 0.78, py - 0.030, cz + (pz - cz) * 0.73) for px, py, pz in ring],
            0.02,
            8,
            group,
        )
        enamel(
            "Amber iris",
            [
                (cx - 0.035, cy - 0.012, cz),
                (cx, cy - 0.016, cz + 0.060),
                (cx + 0.035, cy - 0.015, cz),
                (cx, cy - 0.015, cz - 0.058),
            ],
            0.012,
            15,
            group,
        )
        enamel(
            "Swept ear vane",
            [
                (side * 0.33, -0.14, 3.44),
                (side * 0.65, 0.08, 3.75),
                (side * 0.54, 0.12, 3.38),
                (side * 0.43, 0.08, 3.28),
            ],
            0.055,
            2,
            group,
        )
    enamel(
        "Clapper beak",
        [(0, -0.49, 3.25), (0.115, -0.51, 3.15), (0, -0.62, 2.90), (-0.115, -0.51, 3.15)],
        0.20,
        6,
        group,
    )
    enamel(
        "Escapement frame",
        [(0, -0.46, 2.23), (0.205, -0.46, 2.00), (0, -0.44, 1.73), (-0.205, -0.46, 2.00)],
        0.035,
        5,
        "Speaker",
    )
    enamel(
        "Signal lantern",
        [(0, -0.52, 2.18), (0.13, -0.51, 2.00), (0, -0.49, 1.80), (-0.13, -0.51, 2)],
        0.045,
        15,
        "KeeperLamp",
    )


def music_box():
    from atelier import block, collision, lathe, marker
    from works_sets import line

    x, y = 5.2, 4.5
    lathe(
        "Octagonal music stand",
        x,
        y,
        -0.06,
        [(0.54, 0), (0.56, 0.16), (0.39, 0.30), (0.23, 0.94), (0.47, 1.09)],
        "Slate",
        8,
    )
    block("Walnut music case", (x, y, 1.22), (1.68, 0.81, 0.42), "Wood")
    collision("Music case footing", x, y, -0.05, 1.43, 0.73, 1.49)
    block("Lacquered lid", (x, y + 0.39, 1.66), (1.7, 0.09, 0.69), "Wood")
    shaft(
        "Pinned drum", (x - 0.51, y + 0.06, 1.52), (x + 0.49, y + 0.06, 1.52), 0.164, 0.164, "BellMetal", 14
    )
    for index, note in enumerate("020112201"):
        a = math.tau * index / 9
        dx = (int(note) - 1) * 0.28
        p = (x + dx, y + 0.06 + 0.15 * math.sin(a), 1.52 + 0.15 * math.cos(a))
        q = (p[0], p[1] + 0.048 * math.sin(a), p[2] + 0.048 * math.cos(a))
        shaft("Drum pin", p, q, 0.025, 0.018, "Brass", 6)
    for i in range(3):
        xx = x + (i - 1) * 0.28
        shaft(
            "Tuned steel tooth", (xx, y - 0.32, 1.44), (xx, y + 0.008, 1.64), 0.035, 0.020, "PressSilver", 7
        )
        lathe(
            "Signal pearl",
            xx,
            y - 0.28,
            1.52,
            [(0.080, 0), (0.091, 0.055), (0.04, 0.12)],
            "Amber",
            8,
            "KeeperCue" + str(i),
        )
    shaft("Winding crank", (x + 0.48, y + 0.06, 1.52), (x + 0.95, y + 0.06, 1.52), 0.046, 0.045, "Brass", 7)
    line("Crank return", (x + 0.94, y + 0.06, 1.52), (x + 0.94, y + 0.06, 1.32), 0.048, "Brass")
    shaft(
        "Turned crank handle", (x + 0.92, y + 0.06, 1.32), (x + 1.16, y + 0.06, 1.32), 0.061, 0.065, "Wood", 8
    )
    marker("A_MorningSong", x, y - 0.56, 1.45)
