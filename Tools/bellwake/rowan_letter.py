"""Embroider the completed bearings and Linn's school note onto the back of her survey."""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from choir_wood import EARS, SITES

ROOT = Path(__file__).resolve().parents[2] / "Assets/Resources/Bellwake"
INK = "#433b30"


def make():
    rng = np.random.default_rng(9243)
    y, x = np.mgrid[:544, :768]
    weave = (
        rng.normal(0, 2.1, (544, 768)) + 1.7 * np.cos(x * 2.1) + 1.5 * np.cos(y * 1.55)
    )
    img = Image.fromarray(
        np.uint8(np.clip(np.array([224, 215, 180]) + weave[..., None], 0, 255))
    )
    d = ImageDraw.Draw(img)

    def face(size, italic=False):
        path = (
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif"
            + ("-Italic" if italic else "")
            + ".ttf"
        )
        return ImageFont.truetype(path, size)

    for i in range(18, 748, 10):
        for py in (16, 528):
            d.line((i, py, i + 5, py), fill="#9e8870", width=2)
    for py in range(18, 524, 10):
        for px in (17, 750):
            d.line((px, py, px, py + 5), fill="#9e8870", width=2)
    d.text((43, 34), "The school linen", font=face(40), fill=INK)
    d.text(
        (44, 92),
        "From the field book of Linn, sawyer of Rowan Hollow",
        font=face(20, True),
        fill=INK,
    )
    d.line((44, 134, 723, 134), fill="#8d7957", width=2)
    ink = ["#315d74", "#74442c", "#884c4a"]

    def chart(p):
        return np.array([60 + (p[0] + 52) * 2.46, 428 - (p[1] + 52) * 2.46])

    for i, (family, pair) in enumerate(EARS.items()):
        source = chart(SITES[family])
        for ear in pair:
            a = chart(ear)
            b = source + (source - a) * 0.18
            segments = max(3, int(np.linalg.norm(b - a) / 7))
            for t in range(segments):
                p = a + (b - a) * t / segments
                q = a + (b - a) * (t + 0.77) / segments
                d.line([tuple(p), tuple(q)], fill=ink[i], width=3)
            px, py = a
            d.ellipse((px - 4, py - 4, px + 4, py + 4), fill=ink[i])
        px, py = source
        d.ellipse((px - 7, py - 7, px + 7, py + 7), outline=ink[i], width=3)
    for i, label in enumerate(("Rain", "Root", "Wren")):
        px = 49 + i * 88
        d.line((px, 454, px + 17, 454), fill=ink[i], width=4)
        d.text((px + 20, 441), label, font=face(16), fill=INK)
    for j, line in enumerate(
        (
            "Ina —",
            "Your thumb went through the linen",
            "here. I darned the hole in red,",
            "and you said it looked like a wren.",
            "",
            "The harp has water again. Today",
            "I heard the four knocks at the beech",
            "and set a fourth cup on the table.",
            "",
            "Come in by the kitchen door.",
            "Linn",
        )
    ):
        d.text((332, 153 + j * 29), line, font=face(18, j in (0, 9, 10)), fill=INK)
    # The visible darning cross lies at the intersection of the wren threads.
    px, py = chart(SITES["Wren"])
    for dx in (-3, 0, 3):
        d.line((px + dx, py - 5, px + dx, py + 5), fill="#a34c36", width=2)
    for dy in (-3, 1, 4):
        d.line((px - 5, py + dy, px + 5, py + dy), fill="#a34c36", width=1)
    img.save(ROOT / "Letters/RowanLinen.jpg", quality=91, subsampling=0, optimize=True)


if __name__ == "__main__":
    make()
