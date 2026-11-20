"""A small loop of painted fire. The hearth floor, logs and grate stay still."""

from pathlib import Path
import numpy as np
from PIL import Image

SOURCES = Path(__file__).resolve().parent / "surface_sources"
FIREBOXES = {"Live hearth", "Kiln firebox", "Ember mouth", "Firebox"}


def paint():
    with Image.open(SOURCES / "kiln-firebed.png") as painting:
        source = np.asarray(
            painting.resize((120, 120), Image.Resampling.LANCZOS), float
        )
    y, x = np.mgrid[0:120, 0:120]
    height = np.clip((88 - y) / 65, 0, 1)
    edge = np.sin(np.pi * x / 119) ** 1.8
    flames = np.clip((source[:, :, 0] - source[:, :, 2] - 17) / 125, 0, 1)
    weight = height * edge * flames
    sheet = Image.new("RGB", (256, 256))
    for i in range(16):
        phase = i * np.pi / 8
        dx = weight * (
            5.2 * np.sin(phase + 1.3 + x * 0.091 + y * 0.075)
            + 2.8 * np.sin(phase * 2 - x * 0.054 + y * 0.035)
        )
        dy = weight * (
            4.6 * np.cos(phase + x * 0.073 - y * 0.090)
            + 1.9 * np.cos(phase * 2 + x * 0.038)
        )
        xx = np.clip(x + dx, 0, 118.999)
        yy = np.clip(y + dy, 0, 118.999)
        x0 = xx.astype(int)
        y0 = yy.astype(int)
        fx = (xx - x0)[:, :, None]
        fy = (yy - y0)[:, :, None]
        sample = (1 - fy) * (
            (1 - fx) * source[y0, x0] + fx * source[y0, x0 + 1]
        ) + fy * ((1 - fx) * source[y0 + 1, x0] + fx * source[y0 + 1, x0 + 1])
        rgb = np.uint8(np.clip(np.rint(sample * 0.94 + 3), 0, 255))
        tile = np.asarray(
            Image.fromarray(rgb).resize((60, 60), Image.Resampling.LANCZOS)
        )
        sheet.paste(
            Image.fromarray(np.pad(tile, ((2, 2), (2, 2), (0, 0)), mode="edge")),
            ((i % 4) * 64, (i // 4) * 64),
        )
    sheet.save(
        SOURCES.parents[2] / "Assets/Resources/Bellwake/Textures/KilnFire.png",
        optimize=True,
    )


def fit(objects):
    from shop_paint import project

    fitted = []
    for obj in objects:
        if obj.name.split(".")[0] in FIREBOXES:
            phase = sum((i + 1) * ord(c) for i, c in enumerate(obj.name)) % 16
            project(obj, "KilnFire", phase, rows=4)
            fitted.append(obj.name)
    return fitted


if __name__ == "__main__":
    paint()
