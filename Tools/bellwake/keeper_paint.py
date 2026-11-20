"""Fit individual fired-enamel paintings to the final keeper's moving pieces."""

from pathlib import Path

import numpy as np
from PIL import Image

PALETTE = (
    (45, 60, 77), (70, 100, 111), (89, 125, 122), (125, 144, 129),
    (139, 88, 56), (185, 136, 74), (223, 178, 106), (220, 205, 163),
    (62, 46, 44), (88, 63, 52), (160, 79, 52), (194, 117, 74),
    (51, 77, 91), (55, 90, 91), (127, 121, 104), (224, 153, 77),
)
CLOTH = 9
SHELLS = {"Fluted watch coat", "Repoussé brass belt", "Verdigris gorget", "Night heron cowl"}
PLUMES = {"Chased primary", "Overlapping covert", "Swept ear vane"}


def paint(path):
    source = Path(__file__).with_name("surface_sources") / "keeper-enamel.png"
    sheet = Image.new("RGB", (256, 256))
    with Image.open(source) as strokes:
        for i, base in enumerate(PALETTE):
            bank = 0 if i in (0, 1, 2, 3, 12, 13) else 2 if i in (7, 8, 15) else 1
            if i == CLOTH:
                bank, base = 3, PALETTE[0]
            sx, sy = bank % 2 * 192, bank // 2 * 192
            tile = strokes.crop((sx, sy, sx+192, sy+192)).resize((60, 60), Image.Resampling.LANCZOS)
            rgb = np.asarray(tile.convert("RGB"), dtype=float)
            # Preserve the gold of the feathers and the warm glazing in the mask.
            luminance = rgb @ [0.24, 0.61, 0.15]
            contrast = (luminance - np.median(luminance)) / max(12, np.std(luminance))
            chroma = rgb - rgb.mean(axis=(0, 1)) - (luminance - luminance.mean())[:, :, None]
            strength = (17 if bank != 2 else 7) * contrast[:, :, None]
            pixels = np.rint(np.array(base) + strength + .25*chroma).clip(0, 255).astype(np.uint8)
            tile = Image.fromarray(np.pad(pixels, ((2, 2), (2, 2), (0, 0)), mode="edge"))
            sheet.paste(tile, (i % 4 * 64, i // 4 * 64))
    sheet.save(path, optimize=True)


def fit(obj, pigment):
    """The source meshes retain their quads and end caps until Blender export."""
    name = obj.name.split(".")[0]
    mesh = obj.data
    points = np.array([v.co[:] for v in mesh.vertices])
    if name in ("Fluted watch coat", "Night heron cowl"):
        pigment = CLOTH
    layer = mesh.uv_layers.active.data

    def write(loop_index, u, v):
        layer[loop_index].uv = ((64*(pigment % 4) + 2.5 + 59*u)/256,
                                1 - (64*(pigment // 4) + 2.5 + 59*v)/256)

    def normalized(values):
        span = np.ptp(values, axis=0)
        return (values-values.min(axis=0)) / np.where(span > 1e-8, span, 1)

    if name in SHELLS:
        sectors = len(mesh.polygons[0].vertices)
        vertical = 1 - normalized(points[:, 2])
        for face in mesh.polygons:
            if len(face.vertices) == sectors:
                cap = normalized(points[list(face.vertices), :2])
                for loop_index, (u, v) in zip(face.loop_indices, cap):
                    write(loop_index, u, v)
            else:
                side = (face.index-1) % sectors
                # Give each group of four panels a whole image from hem to collar.
                for i, loop_index in enumerate(face.loop_indices):
                    u = ((side % 4) + int(i in (1, 2))) / 4
                    write(loop_index, u, vertical[mesh.loops[loop_index].vertex_index])
        return

    plane = points[:, [0, 2]].copy()
    if name in PLUMES:
        # The long engraving follows the whole diagonally hung wing plate.
        axis = plane[np.argmax(plane[:, 1])] - plane[np.argmin(plane[:, 1])]
        axis /= np.linalg.norm(axis)
        plane = np.column_stack((plane @ [axis[1], -axis[0]], plane @ axis))
    plane = normalized(plane)
    for loop in mesh.loops:
        u, v = plane[loop.vertex_index]
        write(loop.index, u, 1-v)
