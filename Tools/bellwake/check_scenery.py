"""Check the landscape joins in the packed editable district and road scenes.

blender -b -t 2 --python-exit-code 1 -P Tools/bellwake/check_scenery.py -- report.json
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atelier import ROOT
from bankside_plants import surface
from country import THEMES, boundary


def points(obj):
    return [obj.matrix_world @ v.co for v in obj.data.vertices]


def join_error(start, end):
    if len(start) != len(end):
        raise ValueError(f"Rings have different lengths ({len(start)}, {len(end)})")
    return max((a - b).length for a, b in zip(start, end))


def check(key):
    bpy.ops.wm.open_mainfile(
        filepath=str(ROOT / "Blender" / "Bellwake" / (key + ".blend"))
    )
    groups = defaultdict(list)
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            groups[obj["batch"]].append(obj)
    terrain = groups["Terrain"][0]
    rim = next(
        (
            m
            for m in groups["Rim"]
            if m.name.split(".")[0]
            in {
                "North pass and turf banks",
                "Cut escarpment and distant ridgeline",
                "Folded horizon",
                "Encircling ridgeline",
                "Folded headland shore",
            }
        ),
        None,
    )
    edge = boundary(rim or terrain)
    land = next(o for o in groups["Surroundings"] if o.name.startswith("Valley floor"))
    v = points(land)
    count = len(edge)
    gap = join_error(edge, v[:count])
    bvh = surface([land])
    probes = 0
    for face in list(land.data.polygons)[: count * 6]:
        a, b, c, d = (v[i] for i in face.vertices)
        area = (b - a).cross(d - a).z + (c - b).cross(d - b).z
        assert area > 0, (key, "inverted bank", face.index)
        for t in (0.05, 0.5, 0.95):
            p = a.lerp(b, t).lerp(d.lerp(c, t), 0.5)
            assert bvh.ray_cast((p.x, p.y, 600), (0, 0, -1), 1200)[0] is not None, (
                key,
                face.index,
                t,
            )
            probes += 1
    if key == "Wrenfall":
        shore = points(rim)
        gap = max(gap, join_error(boundary(terrain), shore[: len(shore) // 3]))
        water = next(
            o for o in bpy.context.scene.objects if o.name == "Open tidal water"
        )
        cap = max(water.data.polygons, key=lambda f: f.normal.z)
        lip = [water.matrix_world @ water.data.vertices[i].co for i in cap.vertices]
        sea = next(
            o
            for o in groups["Surroundings"]
            if o.name.startswith("Outer harbour water")
        )
        gap = max(gap, join_error(lip, points(sea)[: len(lip)]))
    assert gap < 0.0003, (key, "open landscape join", gap)
    return {"rimVertices": count, "seamMetres": round(gap, 6), "verticalProbes": probes}


if __name__ == "__main__":
    results = {key: check(key) for key in sorted([*THEMES, "HighroadBrowser"])}
    if "--" in sys.argv:
        Path(sys.argv[sys.argv.index("--") + 1]).write_text(
            json.dumps(results, indent=2) + "\n"
        )
    print(
        "Checked",
        len(results),
        "landscapes and",
        sum(r["verticalProbes"] for r in results.values()),
        "ground samples.",
    )
