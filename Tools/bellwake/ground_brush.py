"""Pack four seamless painted surface details into one linear texture sample."""

from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).parent / "surface_sources" / "underfoot.png"
OUTPUT = ROOT / "Assets/Resources/Bellwake/Textures/GroundBrush.png"


def periodic_ink(tile):
    # Separate the slow ramp between the four edges from the brushwork itself.
    # The opposite edges then meet without a mirrored tuft or a dark grid line.
    height, width = tile.shape
    jump = np.zeros_like(tile)
    jump[0] = tile[-1] - tile[0]
    jump[-1] = -jump[0]
    jump[:, 0] += tile[:, -1] - tile[:, 0]
    jump[:, -1] -= tile[:, -1] - tile[:, 0]
    fx = np.cos(2 * np.pi * np.arange(width) / width)
    fy = np.cos(2 * np.pi * np.arange(height) / height)
    laplace = 2 * (fy[:, None] + fx[None, :] - 2)
    laplace[0, 0] = 1
    ramp = np.fft.fft2(jump) / laplace
    ramp[0, 0] = 0
    pigment = tile - np.fft.ifft2(ramp).real
    pigment -= pigment.mean()
    return np.uint8(np.rint(np.clip(127.5 + pigment * (49 / pigment.std()), 4, 251)))


def paint(output=OUTPUT):
    with Image.open(SOURCE) as master:
        tiles = []
        w, h = master.width // 2, master.height // 2
        for row in range(2):
            for col in range(2):
                swatch = master.crop((col * w, row * h, (col + 1) * w, (row + 1) * h))
                tile = swatch.convert("L").resize((64, 64), Image.Resampling.LANCZOS)
                tiles.append(periodic_ink(np.asarray(tile, dtype=float)))
    Image.fromarray(np.stack(tiles, axis=-1), "RGBA").save(output, optimize=True)


if __name__ == "__main__":
    paint()
