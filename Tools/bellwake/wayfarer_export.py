"""Export Wayfarer gallery pieces with their moving parts on the authored pivots."""

import bpy


def export_piece(key, collection, out):
    bpy.ops.object.select_all(action="DESELECT")
    pivot_names = {
        "LeftWing",
        "RightWing",
        "LeftBoot",
        "RightBoot",
        "Shell",
        "Broad jaw",
    }
    moving = []
    copies = []
    for o in collection.objects:
        if o.name in pivot_names:
            moving.append(o)
            continue
        duplicate = o.copy()
        duplicate.data = o.data.copy()
        bpy.context.scene.collection.objects.link(duplicate)
        duplicate.select_set(True)
        copies.append(duplicate)
    body = copies[0]
    bpy.context.view_layer.objects.active = body
    if len(copies) > 1:
        bpy.ops.object.join()
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    body.name = key + " paint"
    for part in moving:
        part.select_set(True)
    bpy.ops.export_scene.fbx(
        filepath=str(out / (key + ".fbx")),
        use_selection=True,
        bake_anim=False,
        object_types={"MESH"},
        axis_forward="-Z",
        axis_up="Y",
        path_mode="STRIP",
    )
    bpy.data.objects.remove(body, do_unlink=True)


def export_gallery(out):
    for i, collection in enumerate(bpy.context.scene.collection.children):
        if not collection.objects:
            continue
        x, y = collection.get("gallery_offset", ((i % 3) * 5, (i // 3) * 5))
        for obj in collection.objects:
            obj.location.x -= x
            obj.location.y -= y
        export_piece(collection.name, collection, out)
