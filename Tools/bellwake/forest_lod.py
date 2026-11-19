"""Bake woodland cells that share one paint atlas at both viewing distances."""

import bpy
import math
import numpy as np
from PIL import Image
from atelier import RES, batches, mats, origins

PAINTS = ("Wood", "RowanLeaf0", "RowanLeaf1", "RowanLeaf2")


def atlas():
    tiles = RES / "Textures"
    # The gutter repeats the outermost pixel, keeping the colours separate through minification.
    sheet = np.zeros((256, 256, 3), dtype=np.uint8)
    for i, name in enumerate(PAINTS):
        tile = np.asarray(
            Image.open(tiles / (name + ".png"))
            .convert("RGB")
            .resize((112, 112), Image.Resampling.BILINEAR)
        )
        row, column = divmod(i, 2)
        sheet[row * 128 : (row + 1) * 128, column * 128 : (column + 1) * 128] = np.pad(
            tile, ((8, 8), (8, 8), (0, 0)), mode="edge"
        )
    Image.fromarray(sheet).save(tiles / "RowanGrove.png")


def collect(parts, x, y):
    col = min(3, max(0, math.floor((x + 52) * 4 / 104)))
    row = min(2, max(0, math.floor((y + 52) * 3 / 104)))
    name = f"GroveNear{col}{row}"
    origins[name] = (-52 + (col + 0.5) * 26, -52 + (row + 0.5) * 104 / 3, 0)
    for obj, solid in parts:
        if solid:
            # Keep every contact face used by the hands, independently of the visible detail level.
            hull = obj.copy()
            hull.data = obj.data.copy()
            bpy.context.collection.objects.link(hull)
            batches["C_Solids"].append(hull)
        mesh = obj.data
        index = PAINTS.index(mesh.materials[0].name)
        atlas_y, atlas_x = divmod(index, 2)
        uv = mesh.uv_layers.active.data
        # Preserve each face's projection and share the original bark and leaf paint between cells.
        for face in mesh.polygons:
            coords = np.array([tuple(uv[i].uv) for i in face.loop_indices])
            first = np.floor(coords.min(axis=0))
            chart = coords - first
            chart /= np.maximum(1, chart.max(axis=0))
            for i, (u, v) in zip(face.loop_indices, chart):
                uv[i].uv = (
                    (128 * atlas_x + 8 + 112 * u) / 256,
                    (128 * (1 - atlas_y) + 8 + 112 * v) / 256,
                )
        mesh.materials[0] = mats["RowanGrove"]
        batches[name].append(obj)


def distant():
    # Collapse interior edges first, keeping the irregular outlines of the canopies.
    for near, parts in list(batches.items()):
        if not near.startswith("GroveNear"):
            continue
        far = near.replace("Near", "Far")
        origins[far] = origins[near]
        bpy.ops.object.select_all(action="DESELECT")
        copies = []
        for part in parts:
            copy = part.copy()
            copy.data = part.data.copy()
            bpy.context.collection.objects.link(copy)
            copy.select_set(True)
            copies.append(copy)
        obj = copies[0]
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.join()
        modifier = obj.modifiers.new("Distant branches", "DECIMATE")
        modifier.ratio = 0.21
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        obj.name = far
        batches[far].append(obj)
