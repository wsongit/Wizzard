"""Blender mesh atelier for Bellwake. Coordinates are metres, with +Y into each set."""

import bpy, math, random, json
from pathlib import Path
from mathutils import Vector, Matrix
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "Assets/Resources/Bellwake"
LIB = None
mats, models, batches, origins = {}, {}, defaultdict(list), {}
rigparts = {}
rng = random.Random()


def init(library, seed):
    global LIB
    LIB = library
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mats.clear()
    models.clear()
    batches.clear()
    origins.clear()
    rigparts.clear()
    rng.seed(seed)
    for path in sorted((RES / "Textures").glob("*.png")):
        material = bpy.data.materials.new(path.stem)
        material.use_nodes = True
        node = material.node_tree.nodes.new("ShaderNodeTexImage")
        node.image = bpy.data.images.load(str(path))
        node.image.pack()
        node.interpolation = "Closest"
        shader = material.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Roughness"].default_value = 0.95
        material.node_tree.links.new(node.outputs["Color"], shader.inputs["Base Color"])
        mats[path.stem] = material


def geometry(name, points, faces, material, group="Set", uv=None):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(points, [], faces)
    mesh.materials.append(mats[material])
    mesh.update()
    layer = mesh.uv_layers.new(name="Paint")
    for poly in mesh.polygons:
        norm = poly.normal
        axis = max(range(3), key=lambda i: abs(norm[i]))
        u, v = [(1, 2), (0, 2), (0, 1)][axis]
        for li in poly.loop_indices:
            p = mesh.vertices[mesh.loops[li].vertex_index].co
            layer.data[li].uv = uv[li] if uv else (p[u] / 2.6, p[v] / 2.6)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    batches[group].append(obj)
    return obj


def block(name, center, size, mat, group="Set", angle=0):
    x, y, z = center
    w, d, h = (v / 2 for v in size)
    points = []
    for c in [-h, h]:
        for a, b in [(-w, -d), (w, -d), (w, d), (-w, d)]:
            points.append(
                (
                    x + a * math.cos(angle) - b * math.sin(angle),
                    y + a * math.sin(angle) + b * math.cos(angle),
                    z + c,
                )
            )
    return geometry(
        name,
        points,
        [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)],
        mat,
        group,
    )


def shaft(name, a, b, r1, r2, mat, n=8, group="Set"):
    a, b = Vector(a), Vector(b)
    axis = (b - a).normalized()
    s = axis.cross(Vector((0, 0, 1)) if abs(axis.z) < 0.9 else Vector((0, 1, 0))).normalized()
    t = axis.cross(s)
    pts = [
        tuple(p + r * (s * math.cos(i * math.tau / n) + t * math.sin(i * math.tau / n)))
        for p, r in [(a, r1), (b, r2)]
        for i in range(n)
    ]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))] + [
        (i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)
    ]
    return geometry(name, pts, faces, mat, group)


def lathe(name, x, y, base, profile, mat, n=12, group="Set"):
    pts = [
        (x + r * math.cos(i * math.tau / n), y + r * math.sin(i * math.tau / n), base + z)
        for r, z in profile
        for i in range(n)
    ]
    faces = [tuple(reversed(range(n)))]
    for j in range(len(profile) - 1):
        for i in range(n):
            k = j * n
            a = (i + 1) % n
            faces.append((k + i, k + a, k + a + n, k + i + n))
    faces.append(tuple(range(len(pts) - n, len(pts))))
    return geometry(name, pts, faces, mat, group)


def marker(name, x, y, z):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.empty_display_size = 0.24
    obj.location = (x, y, z)
    return obj


def collision(name, x, y, z, w, d, h):
    return block(name, (x, y, z + h / 2), (w, d, h), "Masonry", "C_Solids")


def model(id, name, x, y, z, height, heading=0, group="Set"):
    if id not in models:
        path = next((LIB / "Exports").glob("*/" + id + ".glb"))
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(path))
        imported = set(bpy.data.objects) - before
        deps = bpy.context.evaluated_depsgraph_get()
        verts = []
        faces = []
        uvs = []
        regions = []
        bones = {}
        for o in sorted(imported, key=lambda a: a.name):
            if o.type != "MESH" or any(
                c.name.startswith("glTF_not_exported") for c in o.users_collection
            ):
                continue
            eo = o.evaluated_get(deps)
            m = eo.to_mesh()
            m.calc_loop_triangles()
            offset = len(verts)
            verts.extend(tuple(eo.matrix_world @ v.co) for v in m.vertices)
            tags = {}
            if group == "Speaker":
                arm = next((mod.object for mod in o.modifiers if mod.type == "ARMATURE"), None)
                if arm:
                    for tag, bone in [("Head", "Head"), ("Arm", "UpperArm.L")]:
                        bones[tag] = arm.matrix_world @ arm.pose.bones[bone].head
                for v in m.vertices:
                    if v.groups:
                        g = max(v.groups, key=lambda g: g.weight)
                        joint = o.vertex_groups[g.group].name
                        tags[v.index] = (
                            "Head"
                            if joint == "Head"
                            else "Arm"
                            if joint in ("UpperArm.L", "Forearm.L")
                            else ""
                        )

            for f in m.loop_triangles:
                faces.append(tuple(offset + i for i in f.vertices))
                regions.append(tags.get(f.vertices[0], ""))
                uvs.extend(tuple(m.uv_layers.active.data[i].uv) for i in f.loops)
            eo.to_mesh_clear()
        for o in imported:
            bpy.data.objects.remove(o, do_unlink=True)
        low = [min(p[i] for p in verts) for i in range(3)]
        high = [max(p[i] for p in verts) for i in range(3)]
        mid = [(low[i] + high[i]) / 2 for i in range(2)] + [low[2]]
        theme = path.parent.name + "Atlas"
        points = [tuple(p[i] - mid[i] for i in range(3)) for p in verts]

        def part(tag):
            take = [i for i, r in enumerate(regions) if r == tag]
            used = sorted({v for i in take for v in faces[i]})
            indices = {v: i for i, v in enumerate(used)}
            template = geometry(
                name + tag,
                [points[v] for v in used],
                [tuple(indices[v] for v in faces[i]) for i in take],
                theme,
                "_temporary",
                [uvs[i * 3 + j] for i in take for j in range(3)],
            )
            mesh = template.data
            bpy.data.objects.remove(template, do_unlink=True)
            batches.pop("_temporary")
            return mesh

        models[id] = (part(""), high[2] - low[2])
        if group == "Speaker":
            assert {"Head", "Arm"}.issubset(bones) and {"Head", "Arm"}.issubset(regions), id
            rigparts[id] = [(tag, part(tag), bones[tag] - Vector(mid)) for tag in ["Head", "Arm"]]
    mesh, h = models[id]
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = (x, y, z)
    obj.scale = (height / h,) * 3
    obj.rotation_euler.z = math.radians(heading)
    batches[group].append(obj)
    for tag, part, pivot in rigparts.get(id, []):
        limb = bpy.data.objects.new(name + " " + tag, part)
        bpy.context.collection.objects.link(limb)
        limb.location = obj.location
        limb.scale = obj.scale
        limb.rotation_euler = obj.rotation_euler
        namegroup = group + tag
        origins[namegroup] = tuple(
            Vector((x, y, z)) + Matrix.Rotation(obj.rotation_euler.z, 3, "Z") @ (pivot * (height / h))
        )
        batches[namegroup].append(limb)
    return obj


def finish(key, sky_key=None):
    folder = ROOT / "Blender/Bellwake"
    folder.mkdir(exist_ok=True)
    scene = bpy.context.scene
    for group, objs in batches.items():
        for o in objs:
            o["batch"] = group
    scene["bellwake_pivots"] = json.dumps(origins)
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    cam = bpy.data.objects.new("Review camera", bpy.data.cameras.new("Review lens"))
    bpy.context.collection.objects.link(cam)
    skyfile = RES / "Skies" / ((sky_key or key) + ".jpg")
    if skyfile.exists():
        cam.location = (7, -16, 4.3)
        aim = Vector((-1, 3, 2.2))
        cam.data.lens = 25
    elif key == "TrailSign":
        cam.location = (2.4, -5, 2.3)
        aim = Vector((0.4, 0, 1.2))
    elif key == "RunnerArm":
        cam.location = (1, -1.4, 0.45)
        aim = Vector((0, 0, 0))
    else:
        cam.location = (0.31, -0.39, 0.29)
        aim = Vector((0, 0, 0))
    cam.rotation_euler = (aim - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
    sun = bpy.data.objects.new("Warm daylight", bpy.data.lights.new("Daylight", "SUN"))
    bpy.context.collection.objects.link(sun)
    sun.rotation_euler = (0.65, -0.48, -0.45)
    sun.data.energy = 2.1
    sun.data.angle = 0.16
    scene.world = bpy.data.worlds.new("Painted horizon")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.55, 0.63, 0.65, 1)
    bg.inputs[1].default_value = 0.75
    if skyfile.exists():
        node = scene.world.node_tree.nodes.new("ShaderNodeTexEnvironment")
        node.image = bpy.data.images.load(str(skyfile))
        node.image.pack()
        scene.world.node_tree.links.new(node.outputs[0], bg.inputs[0])
    for group, objs in batches.items():
        hidden = (
            group in ("C_Solids", "HushWave", "Roster", "Ina", "NightRoll", "GateLight")
            or group.startswith(("Choice", "Call", "Flow", "Stray"))
            or group in ("Ray1", "Ray2", "Ray3")
        )
        for o in objs:
            o.hide_render = hidden
            if hidden:
                o.hide_set(True)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_perspective = "CAMERA"
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(folder / (key + ".blend")), compress=True)
    export(key)


def export(key):
    for obj in list(bpy.context.scene.objects):
        if obj.type in ("LIGHT", "CAMERA"):
            bpy.data.objects.remove(obj, do_unlink=True)
        else:
            obj.hide_render = False
            obj.hide_set(False)
    bpy.ops.object.select_all(action="DESELECT")
    for group, objs in batches.items():
        if not objs:
            continue
        bpy.ops.object.select_all(action="DESELECT")
        for o in objs:
            o.select_set(True)
        # Mesh users may be linked between instances. Work on a private copy during export.
        active = objs[0]
        active.data = active.data.copy()
        bpy.context.view_layer.objects.active = active
        if len(objs) > 1:
            bpy.ops.object.join()
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        active.name = group
        pivot = origins.get(group, (0, 0, 0))
        active.data.transform(Matrix.Translation(-Vector(pivot)))
        active.location = pivot
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.fbx(
        filepath=str(RES / "Rooms" / (key + ".fbx")),
        object_types={"EMPTY", "MESH"},
        add_leaf_bones=False,
        bake_anim=False,
        apply_unit_scale=True,
        axis_forward="-Z",
        axis_up="Y",
        path_mode="STRIP",
    )
    review = ROOT / "Tools/bellwake/.web-assets"
    review.mkdir(exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(review / (key + ".glb")),
        export_format="GLB",
        export_animations=False,
        export_cameras=False,
        export_lights=False,
    )
