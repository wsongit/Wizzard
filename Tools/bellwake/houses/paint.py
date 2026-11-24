"""Paint the shared room palette and the signwriter's gilded timber boards."""

from pathlib import Path
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / "Assets/Resources/Bellwake/Houses"
TILES = [
    "Wood",
    "TarredOak",
    "HousePlaster",
    "Masonry",
    "RoofSlate",
    "RyeCrust",
    "FernCloth",
    "SeaCloth",
    "CoalCloth",
    "Brass",
    "MillCanvas",
    "OchrePlaster",
    "FerryEnamel",
    "WindowLight",
    "Slate",
    "Amber",
    "SpringStone",
    "Leaves",
    "DirtPath",
    "BellMetal",
    "book",
    "carpet",
    "door",
    "window",
    "quilt",
    "page",
    "fire",
    "jar",
    "bottle",
    "grain",
    "glass",
    "chalk",
]


def paint():
    atlas = Image.new("RGB", (512, 256))
    for i, name in enumerate(TILES):
        path = DEST.parent / "Textures" / (name + ".png")
        if path.exists():
            tile = (
                Image.open(path).convert("RGB").resize((60, 60), Image.Resampling.BOX)
            )
        else:
            rng = np.random.default_rng(i)
            base = {
                "book": (112, 45, 39),
                "carpet": (118, 62, 42),
                "door": (101, 65, 37),
                "window": (91, 141, 151),
                "quilt": (72, 109, 93),
                "page": (215, 186, 125),
                "fire": (106, 42, 23),
                "jar": (169, 92, 56),
                "bottle": (59, 105, 86),
                "grain": (182, 146, 71),
                "glass": (106, 153, 145),
                "chalk": (63, 81, 70),
            }[name]
            a = np.clip(np.array(base) + rng.normal(0, 5, (60, 60, 1)), 0, 255).astype(
                "uint8"
            )
            tile = Image.fromarray(a)
            pen = ImageDraw.Draw(tile)
            if name in ("window", "glass"):
                for x in (1, 20, 39, 58):
                    pen.line((x, 0, x, 60), fill=(66, 66, 48), width=3)
                for y in (2, 29, 57):
                    pen.line((0, y, 60, y), fill=(82, 67, 45), width=3)
                pen.line((23, 24, 32, 9), fill=(202, 205, 169), width=3)
            elif name == "door":
                for x in range(1, 60, 12):
                    pen.line((x, 0, x, 59), fill=(55, 40, 29), width=2)
                for y in (6, 48):
                    pen.rectangle((0, y, 25, y + 4), fill=(55, 55, 44))
                pen.ellipse((45, 29, 50, 34), fill=(211, 162, 72))
            elif name in ("carpet", "quilt"):
                for x in range(-7, 65, 12):
                    for y in range(-6, 65, 12):
                        pen.polygon(
                            [
                                (x, y + 6),
                                (x + 5, y + 1),
                                (x + 10, y + 6),
                                (x + 5, y + 10),
                            ],
                            outline=(212, 172, 93),
                        )
                pen.rectangle((2, 2, 57, 57), outline=(224, 192, 126), width=2)
            elif name == "page":
                for y in range(10, 52, 5):
                    for x in (6, 33):
                        pen.line(
                            (x, y, x + int(rng.integers(11, 20)), y),
                            fill=(109, 85, 57),
                            width=1,
                        )
                pen.line((29, 0, 29, 60), fill=(123, 87, 53), width=2)
            elif name == "fire":
                for x in range(-3, 60, 7):
                    pen.polygon(
                        [(x, 58), (x + 4, int(rng.integers(9, 40))), (x + 10, 58)],
                        fill=(239, 151, 51),
                    )
            elif name == "chalk":
                for x in range(9, 49, 6):
                    pen.line((x, 14, x - 2, 27), fill=(204, 199, 158))
                pen.line((6, 25, 49, 16), fill=(204, 199, 158))
            else:
                for y in (8, 13, 46, 50):
                    pen.line(
                        (0, y, 60, y),
                        fill=tuple(min(255, int(v * 1.35)) for v in base),
                        width=2,
                    )
        atlas.paste(
            Image.fromarray(
                np.pad(np.asarray(tile), ((2, 2), (2, 2), (0, 0)), mode="edge")
            ),
            ((i % 8) * 64, (i // 8) * 64),
        )
    atlas.save(DEST / "RoomPaint.png")
    names = json.loads((DEST / "Addresses.json").read_text())["signs"]
    height = 128 * 2 ** math.ceil(math.log2(math.ceil(len(names) / 4)))
    out = Image.new("RGB", (1024, height), (61, 42, 28))
    font = "/usr/share/fonts/opentype/urw-base35/Z003-MediumItalic.otf"
    for i, title in enumerate(names):
        tile = Image.new("RGB", (256, 128))
        d = ImageDraw.Draw(tile)
        rng = np.random.default_rng(523 + i)
        hue = [(47, 69, 57), (57, 64, 79), (99, 54, 44), (74, 63, 45)][i % 4]
        for y in range(128):
            s = 3 * math.sin(y * 0.23) + rng.normal(0, 2)
            d.line((0, y, 255, y), fill=tuple(int(v + s) for v in hue))
        d.rounded_rectangle((5, 7, 250, 120), 12, outline=(173, 121, 62), width=3)
        d.rounded_rectangle((10, 12, 245, 115), 9, outline=(191, 158, 99), width=1)
        for x in (20, 236):
            for y in (24, 103):
                d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(193, 152, 83))
        lines = [title]
        if len(title) > 14:
            words = title.split()
            split = min(
                range(1, len(words)),
                key=lambda n: abs(len(" ".join(words[:n])) - len(" ".join(words[n:]))),
            )
            lines = [" ".join(words[:split]), " ".join(words[split:])]
        for sz in range(48, 19, -1):
            f = ImageFont.truetype(font, sz)
            if max(f.getlength(t) for t in lines) < 213:
                break
        for n, t in enumerate(lines):
            y = 62 + (n - (len(lines) - 1) / 2) * 37
            d.text(
                (129, y + 2), t, font=f, anchor="mm", fill=(47, 30, 23), stroke_width=1
            )
            d.text((128, y), t, font=f, anchor="mm", fill=(242, 214, 148))
        out.paste(tile, (i % 4 * 256, i // 4 * 128))
    out.resize((512, height // 2), Image.Resampling.LANCZOS).save(
        DEST / "HouseSigns.png", optimize=True
    )


if __name__ == "__main__":
    paint()
