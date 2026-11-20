"""Original surface paintings fitted to the stock in each workshop."""

from pathlib import Path
import numpy as np
from PIL import Image

SOURCES = Path(__file__).resolve().parent / "surface_sources"
SWATCHES = (
    "crate",
    "lid",
    "rope",
    "canvas",
    "grain",
    "bread",
    "basket",
    "jug",
    "metal",
    "tile",
    "paper",
    "book",
    "log",
    "end",
    "leaves",
    "wool",
    "apple",
    "quince",
    "stem",
    "calyx",
    "staves",
    "cask_lid",
    "bronze",
    "iron",
    "pages",
    "spine",
    "jar_mouth",
    "salt_glaze",
    "shoot",
    "sail",
    "wool_end",
    "yarn",
)


# Grade large marks for the room light. Leave the dark jar mouth and metal patina intact.
def paint(path):
    sheet = Image.new("RGB", (512, 256))
    for bank, source in enumerate(("workyard-goods", "workyard-details")):
        with Image.open(SOURCES / (source + ".png")) as image:
            for item in range(16):
                x, y = (item % 4) * 120, (item // 4) * 120
                tile = image.crop((x, y, x + 120, y + 120)).resize(
                    (60, 60), Image.Resampling.LANCZOS
                )
                paint_pixels = np.asarray(tile, dtype=float)
                mean = paint_pixels.mean(axis=(0, 1))
                pigment = mean + 0.82 * (paint_pixels - mean)
                pigment = np.uint8(np.clip(np.rint(pigment), 0, 255))
                # Edge extrusion protects the body and cap colours in the mip chain.
                patch = np.pad(pigment, ((2, 2), (2, 2), (0, 0)), mode="edge")
                sheet.paste(
                    Image.fromarray(patch), (bank * 256 + item % 4 * 64, item // 4 * 64)
                )
    sheet.save(path, optimize=True)


def uv_for(name, u, v):
    bank, cell = divmod(SWATCHES.index(name), 16)
    x = bank * 256 + cell % 4 * 64
    y = cell // 4 * 64
    return (x + 2.5 + 59 * u) / 512, 1 - (y + 2.5 + 59 * (1 - v)) / 256


if __name__ == "__main__":
    paint(SOURCES.parents[2] / "Assets/Resources/Bellwake/Textures/YardGoods.png")
