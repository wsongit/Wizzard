"""Bake short contact shadows from stationary stock onto each district's painted ground."""

import base64
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, PngImagePlugin
from mathutils import Vector

from bankside_plants import surface

SOURCE_CHUNK = "Bellwake workyard underpaint"


def pigment(image):
    """Recover the original brushwork so moving stock never leaves an old shadow."""
    pixels = np.array(image.convert("RGB"))
    restored = pixels.copy()
    for box, encoded, digest in json.loads(image.info.get(SOURCE_CHUNK, "[]")):
        x, y, right, bottom = box
        patch = pixels[y:bottom, x:right]
        if hashlib.sha256(patch.tobytes()).hexdigest() != digest:
            raise ValueError(
                "The baked stock shadow was edited. Regenerate the district ground first."
            )
        restored[y:bottom, x:right] = np.frombuffer(
            base64.b64decode(encoded), np.uint8
        ).reshape(patch.shape)
    return restored


def ground_projection(terrain, name, size):
    mesh = terrain.data
    slots = {i for i, mat in enumerate(mesh.materials) if mat and mat.name == name}
    loops = [
        i for f in mesh.polygons if f.material_index in slots for i in f.loop_indices
    ]
    samples = loops[:: max(1, len(loops) // 192)]
    xy, uv = [], []
    for index in samples:
        pos = terrain.matrix_world @ mesh.vertices[mesh.loops[index].vertex_index].co
        tex = mesh.uv_layers.active.data[index].uv
        xy.append((pos.x, pos.y, 1))
        uv.append((tex.x * size[0], (1 - tex.y) * size[1]))
    matrix = np.linalg.lstsq(xy, uv, rcond=None)[0]
    if np.abs(np.asarray(xy) @ matrix - uv).max() > 0.02:
        raise ValueError(
            "Expected the district ground painting to project continuously"
        )
    return matrix


def shade_patch(obj, floor, projection, size):
    """Trace from this stock's floor texels, using its actual crate, cord and pot meshes."""
    corners = np.array([tuple(obj.matrix_world @ Vector(v))[:2] for v in obj.bound_box])
    low, high = corners.min(axis=0) - 0.90, corners.max(axis=0) + 0.90
    border = (
        np.array([(x, y, 1) for x in (low[0], high[0]) for y in (low[1], high[1])])
        @ projection
    )
    left, top = np.maximum([0, 0], np.floor(border.min(axis=0))).astype(int)
    right, bottom = np.minimum(size, np.ceil(border.max(axis=0))).astype(int)
    shade = np.zeros((bottom - top, right - left), np.uint8)
    obstacle = surface([obj])
    inverse = np.linalg.inv(projection[:2])
    rays = [
        (Vector((x, y, 1)).normalized(), weight, reach)
        for x, y, weight, reach in [
            (0, 0, 0.27, 1.25),
            (0.58, 0.33, 0.22, 1.12),
            (-0.42, 0.31, 0.12, 0.92),
            (0.18, -0.56, 0.13, 0.97),
            (-0.33, -0.40, 0.11, 0.81),
        ]
    ]
    for y in range(top, bottom):
        for x in range(left, right):
            wx, wy = (np.array([x + 0.5, y + 0.5]) - projection[2]) @ inverse
            point = floor.ray_cast((wx, wy, 100), (0, 0, -1), 250)[0]
            if point is None:
                continue
            point.z += 0.014
            amount = 0
            for ray, weight, reach in rays:
                hit, _, _, distance = obstacle.ray_cast(point, ray, reach)
                if hit is not None:
                    amount += weight * max(0, 1 - distance / reach) ** 0.76
            shade[y - top, x - left] = round(255 * amount)
    pixels_per_metre = np.sqrt(abs(np.linalg.det(projection[:2])))
    blur = Image.fromarray(shade).filter(
        ImageFilter.GaussianBlur(max(0.48, pixels_per_metre * 0.057))
    )
    return (int(left), int(top), int(right), int(bottom)), np.asarray(blur)


def bake(key, batches, textures):
    stocks = [o for o in batches.get("Set", []) if o.get("yard_kit")]
    name = key + "Ground"
    path = Path(textures) / (name + ".png")
    if not stocks or not path.is_file():
        return None
    terrain = next(
        o
        for o in batches["Terrain"]
        if any(m and m.name == name for m in o.data.materials)
    )
    with Image.open(path) as image:
        clean = pigment(image)
        size = image.size
    projection = ground_projection(terrain, name, size)
    floor = surface(batches["Terrain"])
    combined = np.zeros(clean.shape[:2], np.uint8)
    boxes = []
    for obj in stocks:
        box, mask = shade_patch(obj, floor, projection, size)
        left, top, right, bottom = box
        if mask.max() < 12:
            raise ValueError(f"Stock has no ground contact in {key} at {obj.name}")
        np.maximum(
            combined[top:bottom, left:right], mask, out=combined[top:bottom, left:right]
        )
        rows, cols = np.nonzero(mask)
        box = (
            left + int(cols.min()),
            top + int(rows.min()),
            left + int(cols.max()) + 1,
            top + int(rows.max()) + 1,
        )
        boxes.append(box)
    # Multiply the existing pigments. The dirt, grass and joints still show inside the contact.
    shaded = np.rint(
        clean * (1 - combined[:, :, None] / 255 * np.array([0.55, 0.53, 0.48]))
    ).astype(np.uint8)
    underpaint = []
    for left, top, right, bottom in boxes:
        # Read all patches against the unmodified baked image before restoring.
        rect = np.s_[top:bottom, left:right]
        raw = base64.b64encode(clean[rect].tobytes()).decode()
        digest = hashlib.sha256(shaded[rect].tobytes()).hexdigest()
        underpaint.append(([left, top, right, bottom], raw, digest))
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text(
        SOURCE_CHUNK, json.dumps(underpaint, separators=(",", ":")), zip=True
    )
    output = Image.fromarray(shaded)
    output.save(path, pnginfo=metadata)
    with Image.open(path) as saved:
        if not np.array_equal(pigment(saved), clean):
            raise ValueError("Workyard underpaint did not round-trip")
    material = terrain.data.materials[name]
    image = next(
        node.image for node in material.node_tree.nodes if node.type == "TEX_IMAGE"
    )
    if image.packed_file:
        image.unpack(method="REMOVE")
    image.filepath = str(path)
    image.reload()
    image.pack()
    return dict(
        stocks=len(stocks),
        changed=int(np.any(clean != shaded, axis=2).sum()),
        size=size,
    )
