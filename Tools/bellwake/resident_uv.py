"""Fit the small painted trims around the whole piece, including the back."""

import math


def fit_trims(obj):
    if (
        obj.type != "MESH"
        or not obj.data.materials
        or obj.data.materials[0].name != "ResidentCloth"
    ):
        return
    mesh = obj.data
    layer = mesh.uv_layers.active.data
    coords = [v.co for v in mesh.vertices]
    low = [min(p[axis] for p in coords) for axis in range(3)]
    high = [max(p[axis] for p in coords) for axis in range(3)]
    width = [max(0.0001, b - a) for a, b in zip(low, high)]
    cx, cy = [(a + b) * 0.5 for a, b in zip(low, high)][:2]
    for face in mesh.polygons:
        sample = layer[face.loop_start].uv
        px, py = sample.x * 512, (1 - sample.y) * 512
        # Portraits and full-size garment fronts retain their individually unwrapped UV islands.
        if not (0 <= px < 256 and 128 <= py < 256):
            continue
        kit, ink = int(px // 32), int((py - 128) // 8)
        if ink == 0 and "knuckle" not in obj.name and "thumb" not in obj.name:
            continue
        corners = [coords[mesh.loops[i].vertex_index] for i in face.loop_indices]
        azimuth = [0.5 + math.atan2(p.y - cy, p.x - cx) / math.tau for p in corners]
        if max(azimuth) - min(azimuth) > 0.5:
            # A seam may end on the same physical edge (UV zero and one). Refit the
            # small closing face to one edge instead of stretching all the way round.
            azimuth = [a + 1 if a < 0.5 else a for a in azimuth]
            if sum(azimuth) / len(azimuth) > 1:
                azimuth = [a - 1 for a in azimuth]
        for i, p, u in zip(face.loop_indices, corners, azimuth):
            if abs(face.normal.z) > 0.75:
                u = (p.x - low[0]) / width[0]
                v = (p.y - low[1]) / width[1]
            else:
                v = (p.z - low[2]) / width[2]
            layer[i].uv = (
                (kit * 32 + 1.5 + 29 * max(0, min(1, u))) / 512,
                1 - (128 + ink * 8 + 1.5 + 5 * (1 - v)) / 512,
            )
