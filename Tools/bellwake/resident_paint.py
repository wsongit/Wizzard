"""Paint the residents' faces and bolts of cloth onto a single original 512 px sheet."""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import math
import random
from resident_designs import COSTUMES, FACES, face_patch

# Face placement is shared with the UV builder. Each portrait appears once.
# skin, hair, jacket, edging, scarf, inner cloth
DYES = (
    ("c79170", "443830", "455d70", "91ab9e", "c67648", "ddd2ae"),
    ("996744", "332d28", "587355", "abc18a", "d7a453", "d4c6a1"),
    ("ce986e", "783d2c", "9d5339", "d9a964", "546e74", "e4cba2"),
    ("926044", "473733", "4d7180", "8cb3bb", "ae6850", "cfc7ab"),
    ("d7aa81", "685646", "695576", "b59aaa", "c79952", "d9d3b5"),
    ("a97154", "302a2e", "8e6849", "c2a780", "6c9390", "f0d7aa"),
    ("b88a6d", "9c9482", "536253", "97a681", "9b4640", "dfd3bb"),
    ("d6a17a", "614237", "a16c3b", "e1c580", "596972", "e5dbc1"),
)
PIGMENTS = (
    "skin",
    "hair",
    "coat",
    "edge",
    "scarf",
    "linen",
    "trousers",
    "shoe",
    "metal",
    "felt",
    "hairlight",
    "wood",
    "cuff",
    "satchel",
    "gold",
    "ink",
)


def rgb(word):
    return tuple(bytes.fromhex(word))


def shade(c, n):
    return tuple(max(0, min(255, round(v + n))) for v in c)


def palette(i):
    skin, hair, coat, edge, scarf, linen = map(rgb, DYES[i])
    return (
        skin,
        hair,
        coat,
        edge,
        scarf,
        linen,
        shade(coat, -24),
        rgb("513e36"),
        rgb("748181"),
        shade(scarf, -14),
        shade(hair, 23),
        rgb("8e6847"),
        shade(coat, 15),
        rgb("82543c"),
        rgb("c4a367"),
        rgb("392e30"),
    )


def eyelids(sheet, portrait, face_index, skin, hair, tilt):
    # Half-lid and shut-lid strips sit in unused cells of the costume sheet.
    # The middle of the face stays live across the swap, including the modeled nose.
    for pose in (0, 1):
        eye = portrait.copy()
        d = ImageDraw.Draw(eye)
        for side in (-1, 1):
            for relative in range(4, 23):
                x = 32 + side * relative
                upper = round(
                    28
                    - 3.4 * math.sin((relative - 4) * math.pi / 18)
                    + tilt * (relative - 5) / 17
                )
                arch = math.sin((relative - 4) * math.pi / 18)
                crease = round(
                    (29.4 + 1.3 * arch if pose else 28.4 - 2.0 * arch)
                    + tilt * (relative - 5) / 30
                )
                bottom = 33 if pose else crease + 1
                for y in range(upper - 2, bottom + 1):
                    skin_at_eye = portrait.getpixel((x, 36))
                    eye.putpixel((x, y), shade(skin_at_eye, (crease - y) * 0.9 - 2))
                if 5 <= relative <= 21:
                    d.point((x, crease), fill=shade(hair, -13))
                    if 7 <= relative <= 18:
                        d.point((x, crease - 1), fill=shade(skin, -19))
                    if not pose and 7 <= relative <= 19:
                        # Leave a sliver of iris visible below the descending lid.
                        lower = round(29.4 + 1.8 * arch)
                        iris = (84, 89, 65) if 10 <= relative <= 15 else (226, 211, 182)
                        for yy in range(crease + 1, lower + 1):
                            eye.putpixel(
                                (x, yy), (49, 43, 35) if relative in (12, 13) else iris
                            )
                    if pose and 8 <= relative <= 18:
                        d.point((x, crease + 1), fill=shade(skin, 8))
        # A mirrored eye uses its full drawing resolution. The 64px portrait is
        # still the source for the surrounding eyelids, cheeks and asymmetrical marks.
        strip = np.asarray(eye.crop((36, 23, 57, 36)))
        strip = np.pad(strip, ((1, 2), (1, 1), (0, 0)), mode="edge")
        row, column = divmod(face_index * 2 + pose, 19)
        x = column * 23 if column < 11 else 320 + (column - 11) * 23
        sheet.paste(Image.fromarray(strip), (x, 448 + row * 16))


def paint(path):
    sheet = Image.new("RGB", (512, 512))
    for face_index, (name, visage) in enumerate(FACES.items()):
        kind = COSTUMES[name].kit
        colors = palette(kind)
        skin, hair = colors[:2]
        face = Image.new("RGB", (64, 64))
        pixels = face.load()
        rng = random.Random(1103 + kind)
        for y in range(64):
            for x in range(64):
                side = (abs(x - 31) / 32) ** 1.7
                blush = math.exp(-(((abs(x - 32) - 16) / 7) ** 2) - ((y - 39) / 6) ** 2)
                base = shade(
                    skin, 7 - 16 * side + (28 - y) * 0.09 + rng.uniform(-1.7, 1.7)
                )
                pixels[x, y] = (
                    min(255, int(base[0] + 6 * blush)),
                    max(0, int(base[1] - 6 * blush)),
                    max(0, int(base[2] - 5 * blush)),
                )
        d = ImageDraw.Draw(face)
        tilt = visage.brow
        for s in (-1, 1):

            def line(points, col, width=1):
                d.line([(32 + s * x, y) for x, y in points], fill=col, width=width)

            def poly(points, col):
                d.polygon([(32 + s * x, y) for x, y in points], fill=col)

            # Inner eye sits lower than its far corner on the alert expression. Use a dark upper lid.
            high = visage.lid
            poly(
                [
                    (5, 29),
                    (8, 25 + high),
                    (13, 24 + tilt),
                    (21, 27 + tilt),
                    (17, 31 + high),
                    (10, 32),
                ],
                shade(skin, -39),
            )
            poly(
                [
                    (6, 29),
                    (10, 26 + high),
                    (15, 25 + tilt),
                    (20, 27 + tilt),
                    (16, 30 + high),
                    (10, 31),
                ],
                (235, 222, 193),
            )
            poly(
                [(10, 26), (15, 26), (15, 30), (12, 31), (10, 29)],
                (72, 72 + kind * 2, 54 + kind * 3),
            )
            line([(12, 26), (12, 30)], (49, 40, 36), 2)
            line([(11, 26), (12, 26)], (234, 224, 188))
            line(
                [(5, 29), (9, 25 + high), (15, 24 + tilt), (21, 26 + tilt)],
                shade(hair, -12),
                2,
            )
            poly(
                [
                    (5, 22),
                    (8, 19),
                    (15, 17 + tilt),
                    (22, 20 + tilt),
                    (15, 20 + tilt),
                    (8, 22),
                ],
                shade(hair, -6),
            )
            line([(17, 33 + high), (21, 32 + high)], shade(skin, -16))
            if visage.mark in ("age", "jawbeard", "smile"):
                line([(19, 35), (23, 34)], shade(skin, -18))
                line([(18, 37), (21, 37)], shade(skin, -13))
            if visage.mark == "freckles":
                for x, y in ((13, 36), (17, 35), (21, 37), (15, 38)):
                    d.point((32 + s * x, y), fill=shade(skin, -27))
        d.line([(29, 40), (31, 41), (34, 40)], fill=shade(skin, -34))
        mouth = [(24, 48), (29, 47), (33, 48), (38, 47), (40, 46 - kind % 2)]
        d.line(mouth, fill=shade(skin, -56), width=1)
        d.line([(29, 50), (32, 51), (36, 50)], fill=shade(skin, 14))
        if visage.mark == "scar":
            d.line([(41, 17), (40, 22), (43, 29), (45, 35)], fill=shade(skin, 16))
        if visage.mark == "mole":
            d.ellipse((44, 39, 45, 40), fill=shade(hair, -4))
        if visage.mark == "soot":
            for xx, yy in ((15, 36), (17, 36), (16, 37), (19, 35), (14, 37), (20, 36)):
                d.point((xx, yy), fill=shade(skin, -23))
        if visage.mark == "stubble":
            for yy in range(46, 61, 2):
                for xx in range(14 + (yy % 3), 49, 3):
                    if abs(xx - 32) > 9 or yy > 51:
                        d.point((xx + rng.randint(0, 1), yy), fill=shade(skin, -16))
        if visage.mark == "age":
            d.line([(13, 37), (17, 40), (19, 41)], fill=shade(skin, -17))
            d.line([(23, 45), (20, 49), (20, 51)], fill=shade(skin, -20))
            d.line([(43, 46), (45, 49)], fill=shade(skin, -19))
            d.line([(23, 14), (31, 13), (41, 14)], fill=shade(skin, -10))
        sheet.paste(face, face_patch(name))
        eyelids(sheet, face, face_index, skin, hair, tilt)
    for kind in range(8):
        colors = palette(kind)
        with Image.open(
            Path(__file__).parent / "surface_sources" / "resident-trims.png"
        ) as trim:
            for ink, base in enumerate(colors):
                x, y = ink % 4 * 64, ink // 4 * 64
                patch = trim.crop((x, y, x + 64, y + 64)).resize(
                    (30, 6), Image.Resampling.LANCZOS
                )
                pigments = np.asarray(patch, dtype=float)
                variation = pigments - np.median(pigments, axis=(0, 1))
                contrast = (
                    0.17,
                    0.60,
                    0.70,
                    0.62,
                    0.67,
                    0.66,
                    0.54,
                    0.72,
                    0.56,
                    0.55,
                    0.57,
                    0.57,
                    0.72,
                    0.61,
                    0.46,
                    0.46,
                )[ink]
                pixels = np.uint8(np.clip(np.rint(base + variation * contrast), 0, 255))
                sheet.paste(
                    Image.fromarray(
                        np.pad(pixels, ((1, 1), (1, 1), (0, 0)), mode="edge")
                    ),
                    (kind * 32, 128 + ink * 8),
                )
        # Crop each full garment painting independently so the hem survives mipping.
        with Image.open(
            Path(__file__).parent / "surface_sources" / "resident-tailoring.png"
        ) as atlas:
            x, y = kind % 4 * 96, kind // 4 * 144
            cloth = atlas.crop((x, y, x + 96, y + 144)).resize(
                (58, 90), Image.Resampling.LANCZOS
            )
        samples = np.asarray(cloth, dtype=float)
        middle = np.median(samples, axis=(0, 1))
        pigment = np.asarray(colors[2]) + (samples - middle) * 0.85
        pigment = np.uint8(np.clip(np.rint(pigment), 0, 255))
        sheet.paste(
            Image.fromarray(np.pad(pigment, ((3, 3), (3, 3), (0, 0)), mode="edge")),
            ((kind % 4) * 64, 256 + (kind // 4) * 96),
        )
    sheet.save(path, optimize=True)


if __name__ == "__main__":
    from pathlib import Path

    paint(
        Path(__file__).resolve().parents[2]
        / "Assets/Resources/Bellwake/Textures/ResidentCloth.png"
    )
