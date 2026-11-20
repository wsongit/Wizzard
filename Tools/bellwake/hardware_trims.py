"""Pack the original repeat paints used together on small moving mechanisms."""

from math import ceil, floor
from pathlib import Path

GROUPS = {
    "Bellmarket": ("RoadBook", "NightRoll"),
    "PaperCourt": ("SpoolFigure", "SpoolPlace", "SpoolProp"),
    "RowanHollow": ("RidgeTrough", "SillTrough", "LoftBeam"),
}
# Positions are in 64-texel repeats and use Blender's bottom-left UV origin.
PATCHES = {
    "Wood": (0, 0, 4, 4), "Brass": (4, 0, 2, 2), "BellMetal": (6, 0, 2, 2),
    "HousePlaster": (4, 2, 2, 2), "SeaCloth": (6, 2, 2, 2),
}
SIZE = (8, 4)


def paint(directory):
    from PIL import Image

    sheet = Image.new("RGB", tuple(size * 64 for size in SIZE))
    for name, (left, bottom, width, height) in PATCHES.items():
        with Image.open(directory / (name + ".png")) as tile:
            assert tile.size == (64, 64)
            for x in range(left, left + width):
                for y in range(bottom, bottom + height):
                    sheet.paste(tile, (x * 64, (SIZE[1] - 1 - y) * 64))
    sheet.save(directory / "HardwareTrims.png", optimize=True)


def offset(values, space):
    # Keep the UV phase continuous across faces. Reserve two texels at each edge for filtering.
    minimum = ceil(2 / 64 - min(values))
    maximum = floor(space - 2 / 64 - max(values))
    if minimum > maximum:
        raise ValueError(
            f"UV interval {min(values)}..{max(values)} exceeds a {space}-repeat patch"
        )
    return (minimum + maximum) // 2


def fit(key, batches):
    from atelier import load_paint

    for group in GROUPS.get(key, ()):
        for obj in batches[group]:
            mesh = obj.data
            if len(mesh.materials) != 1 or mesh.materials[0].name not in PATCHES:
                continue
            if mesh.users > 1:
                mesh = mesh.copy()
                obj.data = mesh
            left, bottom, width, height = PATCHES[mesh.materials[0].name]
            layer = mesh.uv_layers.active.data
            for face in mesh.polygons:
                vertices = [layer[i] for i in face.loop_indices]
                dx = left + offset([v.uv.x for v in vertices], width)
                dy = bottom + offset([v.uv.y for v in vertices], height)
                for v in vertices:
                    v.uv = ((v.uv.x + dx) / SIZE[0], (v.uv.y + dy) / SIZE[1])
            mesh.materials[0] = load_paint("HardwareTrims")


if __name__ == "__main__":
    paint(Path(__file__).resolve().parents[2] / "Assets/Resources/Bellwake/Textures")
