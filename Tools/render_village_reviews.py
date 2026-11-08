"""Render source-scene views, including eye-level path problem areas.

These are Blender previews. Unity shader and headset validation are separate.
"""
import bpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'Blender/MossbellVillage.blend'))
scene = bpy.context.scene
ground = bpy.data.objects['Unified village landform']
ground.data.calc_loop_triangles()
bvh = BVHTree.FromPolygons([ground.matrix_world @ v.co for v in ground.data.vertices],
                           [tuple(t.vertices) for t in ground.data.loop_triangles], all_triangles=True)

def above(x, y, height):
    hit, _, _, _ = bvh.ray_cast(Vector((x, y, 40)), Vector((0, 0, -1)), 50)
    assert hit is not None
    return hit + Vector((0, 0, height))

views = [(bpy.data.objects[name], filename) for name, filename in (
    ('Entrance comparison', 'mossbell-street.png'),
    ('Spring and terrace', 'mossbell-spring.png'),
    ('Upper terrace overview', 'mossbell-terrace.png'),
    ('Layout overview', 'mossbell-village.png'))]
for name, pos, target, filename in (
    ('Courtyard road junction', above(-3, -7, 1.65), above(-1, -2, .1), 'path-courtyard.png'),
    ('Upper road cut bank', above(11, 18.75, 1.65), above(17, 18.1, .15), 'path-upper-ramp.png'),
    ('Middle road junction', above(7.7, 15.5, 1.65), above(9, 19, .1), 'path-middle-junction.png')):
    bpy.ops.object.camera_add(location=pos)
    camera = bpy.context.object
    camera.name = name
    camera.rotation_euler = (target-pos).to_track_quat('-Z', 'Y').to_euler()
    camera.data.lens = 26
    camera.data.sensor_width = 36
    views.append((camera, filename))
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.cycles.samples = 32
for camera, filename in views:
    scene.camera = camera
    scene.use_nodes = camera.name != 'Layout overview'
    scene.render.filepath = str(root/'Documentation'/filename)
    bpy.ops.render.render(write_still=True)
print('PASS: seven source-scene previews, including three eye-level path areas')
