"""Paint shallow shop glimpses and bind the individual ledgers already on the shelves."""

from pathlib import Path
import math

ROOT = Path(__file__).resolve().parents[2]
TEXTURES = ROOT / "Assets/Resources/Bellwake/Textures"
SOURCES = Path(__file__).resolve().parent / "surface_sources"


def paint():
    from PIL import Image
    import numpy as np

    for name, source in (
        ("ShopWindows", "shop-windows"),
        ("CabinetBindings", "cabinet-bindings"),
    ):
        sheet = Image.new("RGB", (256, 128))
        with Image.open(SOURCES / (source + ".png")) as artwork:
            for i in range(8):
                x, y = i % 4 * 128, i // 4 * 128
                tile = artwork.crop((x, y, x + 128, y + 128)).resize(
                    (60, 60), Image.Resampling.LANCZOS
                )
                rgb = np.asarray(tile, dtype=float) / 255
                if name == "ShopWindows":
                    # Reflected daylight lifts the deepest shadow behind the horn panes.
                    rgb = rgb**0.80 * (0.75, 0.73, 0.69) + (0.055, 0.071, 0.065)
                else:
                    rgb = rgb * 0.92 + 0.025
                tile = np.uint8(np.clip(np.rint(255 * rgb), 0, 255))
                pixels = np.pad(tile, ((2, 2), (2, 2), (0, 0)), mode="edge")
                sheet.paste(Image.fromarray(pixels), (i % 4 * 64, i // 4 * 64))
        sheet.save(TEXTURES / (name + ".png"), optimize=True)


def project(obj, paint_name, cell, horizontal_axis=None, front_sign=None, rows=2):
    from atelier import load_paint
    from mathutils import Vector

    mesh = obj.data
    if mesh.users > 1:
        mesh = obj.data.copy()
        obj.data = mesh
    corners = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
    # The original house meshes may already have their rotations baked in. Find
    # their broad vertical pane in world space, including diagonally oriented homes.
    normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()
    normals = [(normal_matrix @ f.normal).normalized() for f in mesh.polygons]
    if horizontal_axis is None:
        broad = max(
            (f for f in mesh.polygons if abs(normals[f.index].z) < 0.15),
            key=lambda f: f.area,
        )
        axis = normals[broad.index]
    else:
        axis = Vector((1, 0, 0) if horizontal_axis == "x" else (0, 1, 0))
    painted = [
        f
        for f in mesh.polygons
        if (
            (normals[f.index].dot(axis) * front_sign > 0.91)
            if front_sign is not None
            else abs(normals[f.index].dot(axis)) > 0.91
        )
    ]
    if not painted:
        raise ValueError("Expected a vertical painted face on " + obj.name)
    # Place the projection on the existing face, preserving physical sills, hinges and shelves.
    slot = load_paint(paint_name)
    mesh.materials.append(slot)
    for face in painted:
        n = normals[face.index]
        right = Vector((-n.y, n.x, 0)).normalized()
        points = [point.dot(right) for point in corners]
        heights = [point.z for point in corners]
        left, bottom = min(points), min(heights)
        width, height = max(points) - left, max(heights) - bottom
        for loop in face.loop_indices:
            vertex = mesh.loops[loop].vertex_index
            u = (points[vertex] - left) / width
            v = (heights[vertex] - bottom) / height
            mesh.uv_layers.active.data[loop].uv = (
                (cell % 4 * 64 + 2.5 + 59 * u) / 256,
                1 - (cell // 4 * 64 + 2.5 + 59 * (1 - v)) / (rows * 64),
            )
        face.material_index = len(mesh.materials) - 1
    return len(painted)


def fittings(room, objects):
    books = {
        "Clothbound deposition": ("y", -1),
        "Cloth spine": ("y", -1),
        "Bound flood ledger": ("x", None),
    }
    labels = {
        "Print shop cabinet": (4, "y", -1),
        "Wash bench cupboard": (5, "x", 1),
        "Cabinet inset panel": (6, "y", -1),
        "Index case": (7, "y", -1),
    }
    cottages = {
        "Entrance west": 0,
        "Entrance east": 1,
        "Back terrace cottage": 2,
        "Lower east": 3,
    }
    fitted = []
    for obj in objects:
        if not obj.data.materials:
            continue
        label = obj.name.split(".")[0]
        if label in books:
            axis, face = books[label]
            if face is None:
                face = 1 if sum(v.co.x for v in obj.data.vertices) < 0 else -1
            dye = {
                "Pennon": 0,
                "CoalCloth": 0,
                "FernCloth": 1,
                "SeaCloth": 2,
                "Awning": 1,
                "Wood": 3,
                "TarredOak": 3,
            }
            project(
                obj,
                "CabinetBindings",
                dye.get(obj.data.materials[0].name, 3),
                axis,
                face,
            )
        elif label in labels:
            cell, axis, face = labels[label]
            project(obj, "CabinetBindings", cell, axis, face)
        elif room == "Bellmarket" and "front or rear dark pane" in label:
            cell = next(
                value for prefix, value in cottages.items() if label.startswith(prefix)
            )
            project(obj, "ShopWindows", cell)
        elif room.startswith("Sillwater") and label == "Horn glazing":
            center = obj.matrix_world @ obj.data.vertices[0].co
            cell = (4, 5, 6, 2)[
                (math.floor(center.x / 8) + math.floor(center.y / 9)) % 4
            ]
            project(obj, "ShopWindows", cell)
        elif room == "Wrenfall" and label == "Pilot glass":
            project(obj, "ShopWindows", 7)
        else:
            continue
        fitted.append(obj.name)
    return fitted


if __name__ == "__main__":
    paint()
