"""Check the native-only street fronts against the shipped highroad and village collision."""

import json
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[3]
houses = root / "Assets/Resources/Bellwake/Houses"
book = json.loads((houses / "Addresses.json").read_text())
errors = []


def collision(objects):
    verts, faces = [], []
    for obj in objects:
        base = len(verts)
        verts.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
        faces.extend(tuple(base + i for i in p.vertices) for p in obj.data.polygons)
    return BVHTree.FromPolygons(verts, faces)


def world(p):
    return Vector((p[0], -p[2], p[1]))


for district in book["districts"]:
    key = district["key"]
    for door in district["doors"]:
        assert door["lore"] and door["objectName"]
        assert door["sign"] == (
            book["signs"].index(door["name"]) if door["name"] else -1
        )
        assert (houses / (door["layout"] + ".json")).exists()
    if key == "MossbellVillage":
        bpy.ops.wm.open_mainfile(filepath=str(root / "Blender/MossbellVillage.blend"))
        tree = collision(bpy.data.collections["Collision"].objects)
    elif key == "Highroad":
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(
            filepath=str(root / "Assets/Resources/Bellwake/Rooms/Highroad.fbx")
        )
        # A Blender round trip must preserve the reference empties used to bind Unity doors.
        for a in district["anchors"]:
            actual = bpy.data.objects[a["name"]].matrix_world.translation
            assert (actual - world(a["p"])).length < 0.01, (actual, a)
        tree = collision(
            o
            for o in bpy.context.scene.objects
            if o.type == "MESH"
            and (
                o.name in ("Terrain", "Set", "Rim", "C_Solids")
                or o.name.startswith("FieldCell_")
            )
        )
    else:
        continue
    for door in district["doors"]:
        p, n = world(door["point"]), world(door["normal"])
        side = Vector((-n.y, n.x, 0))
        for dist, offset in ((1.65, 0), (2.2, 0), (1, 0), (1.6, 0.8), (1.6, -0.8)):
            at = p + n * dist + side * offset
            floor, normal, _, _ = tree.ray_cast(
                at + Vector((0, 0, 0.2)), (0, 0, -1), 3.1
            )
            if floor is None or normal.z < 0.55:
                continue
            eye = floor + Vector((0, 0, 1.62))
            delta = p - eye
            if delta.length > 3.25:
                continue
            if (
                tree.ray_cast(eye, delta.normalized(), max(0, delta.length - 0.48))[0]
                is None
            ):
                break
        else:
            errors.append((key, door["name"] or door["point"]))
    print("Native street fronts", key, len(district["doors"]), flush=True)
assert not errors, errors

layouts = sorted(
    {d["layout"] for district in book["districts"] for d in district["doors"]}
)
for layout in layouts:
    room = json.loads((houses / (layout + ".json")).read_text())
    verts = list(zip(*[iter(room["pos"])] * 3))
    faces = list(zip(*[iter(room["indices"])] * 3))
    assert len(room["uv"]) == 2 * len(verts) and len(room["light"]) == len(verts)
    tree = BVHTree.FromPolygons(verts, faces, all_triangles=True)
    # Test the upward floor surface directly. Wall base courses have coplanar
    # undersides at the perimeter and their back faces do not support the player.
    floor_faces = [
        f
        for f in faces
        if all(abs(verts[i][1]) < 0.0001 for i in f)
        and (Vector(verts[f[1]]) - Vector(verts[f[0]]))
        .cross(Vector(verts[f[2]]) - Vector(verts[f[0]]))
        .y
        > 0
    ]
    floor_tree = BVHTree.FromPolygons(verts, floor_faces, all_triangles=True)
    for i in range(-39, 40):
        for j in range(-33, 34):
            hit, normal, _, _ = floor_tree.ray_cast(
                (i / 10, 0.005, j / 10), (0, -1, 0), 0.02
            )
            assert hit is not None and normal.y > 0.99, (layout, "floor", i, j)
    for height in (0.35, 1.55, 2.85):
        for i in range(-32, 33):
            for end in (-1, 1):
                assert (
                    tree.ray_cast((4.3 * end, height, i / 10), (-end, 0, 0), 0.55)[0]
                    is not None
                ), (layout, "side wall", i)
                assert (
                    tree.ray_cast((i / 10, height, 3.8 * end), (0, 0, -end), 0.58)[0]
                    is not None
                ), (layout, "end wall", i)
print("Closed floors and walls verified in", len(layouts), "furnished layouts.")
