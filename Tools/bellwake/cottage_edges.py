"""Fit the exposed edge of a roof, door, window or step to its own painted strip."""

from pathlib import Path

from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
TEXTURES = ROOT / "Assets/Resources/Bellwake/Textures"
SOURCE = Path(__file__).parent / "surface_sources/cottage-edges.png"


def paint(output=TEXTURES / "HouseEdges.png"):
    # Each usable 120 by 24 strip has a four-texel gutter on all sides.
    with Image.open(SOURCE) as source:
        sheet = Image.new("RGB", (128, 128))
        for band in range(4):
            swatch = source.crop((0, band * 32, 256, (band + 1) * 32)).resize(
                (120, 24), Image.Resampling.LANCZOS
            )
            rgb = np.asarray(swatch, dtype=float)
            # Weathered fascias sit in the same light as the existing cottage timberwork.
            middle = np.median(rgb, axis=(0, 1))
            palettes = [(107, 75, 46), (93, 64, 40), (108, 80, 51), (143, 134, 108)]
            rgb = np.clip(
                np.rint(palettes[band] + 0.80 * (rgb - middle)), 0, 255
            ).astype(np.uint8)
            sheet.paste(
                Image.fromarray(np.pad(rgb, ((4, 4), (4, 4), (0, 0)), mode="edge")),
                (0, 32 * band),
            )
        sheet.save(output, optimize=True)


def band_for(obj):
    label = obj.name.lower()
    stone = any(k in label for k in ("doorstep", "stone threshold", "hearth lintel"))
    if stone and obj.data.materials[0].name == "Masonry":
        return 3
    if obj.data.materials[0].name not in {"Wood", "TarredOak"}:
        return None
    if "eave fascia" in label:
        return 0
    if "door lintel" in label:
        return 1
    if any(k in label for k in ("door jamb", "window sill", "window jamb")):
        return 2
    return None


def fit(objects):
    from atelier import load_paint

    count = 0
    for obj in objects:
        if not obj.data.materials:
            continue
        band = band_for(obj)
        if band is None:
            continue
        mesh = obj.data
        if mesh.users > 1:
            mesh = mesh.copy()
            obj.data = mesh
        points = [obj.matrix_world @ v.co for v in mesh.vertices]
        edges = [points[e.vertices[1]] - points[e.vertices[0]] for e in mesh.edges]
        along = max(edges, key=lambda v: v.length_squared).normalized()
        major = max(range(3), key=lambda i: abs(along[i]))
        if along[major] < 0:
            along = -along
        slot = mesh.materials.find("HouseEdges")
        if slot < 0:
            slot = len(mesh.materials)
            mesh.materials.append(load_paint("HouseEdges"))
        normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()
        for face in mesh.polygons:
            normal = (normal_matrix @ face.normal).normalized()
            if normal.z < -0.66 or abs(normal.dot(along)) > 0.78:
                continue
            # The tile lip stays on the upper edge as the beam turns a corner.
            across = normal.cross(along).normalized()
            if across.z < -0.001:
                across = -across
            values = [
                (
                    points[mesh.loops[i].vertex_index].dot(along),
                    points[mesh.loops[i].vertex_index].dot(across),
                )
                for i in face.loop_indices
            ]
            xx, yy = zip(*values)
            wide, tall = max(xx) - min(xx), max(yy) - min(yy)
            if min(wide, tall) < 0.001:
                continue
            for i, (x, y) in zip(face.loop_indices, values):
                u = (x - min(xx)) / wide
                v = (y - min(yy)) / tall
                mesh.uv_layers.active.data[i].uv = (
                    (4.5 + 119 * u) / 128,
                    1 - (band * 32 + 4.5 + 23 * (1 - v)) / 128,
                )
            face.material_index = slot
            count += 1
    return count


if __name__ == "__main__":
    paint()
