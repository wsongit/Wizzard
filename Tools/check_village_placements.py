"""Audit cottage approaches, sealed foundations, and grounded village props.

Run after rebuilding:
blender -b -t 8 --python-exit-code 1 --python Tools/check_village_placements.py
Use ``-- --blend /path/to/candidate.blend`` to inspect an unsaved candidate.
Checks saved authoring geometry, including dedicated static collision. The ray
lattice is a geometry regression check, not a Unity capsule/headset simulation.
"""
import bpy
import argparse
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--blend', type=Path, default=ROOT / 'Blender/MossbellVillage.blend')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=str(args.blend))
bpy.context.view_layer.update()
SOURCE = [o for o in bpy.context.scene.objects if o.type == 'MESH'
          and not o.name.startswith('Collision ')]
COLLISION = list(bpy.data.collections['Collision'].objects)


def vertices(obj):
    return [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]


def tree(objects):
    points, faces, owners = [], [], []
    for obj in objects:
        offset = len(points)
        points.extend(vertices(obj))
        faces.extend(tuple(offset+i for i in p.vertices) for p in obj.data.polygons)
        owners.extend([obj.name] * len(obj.data.polygons))
    return BVHTree.FromPolygons(points, faces), owners


GROUND, _ = tree([bpy.data.objects['Unified village landform']])
WORLD, OWNERS = tree(COLLISION)


def ground_height(point):
    hit, _, _, _ = GROUND.ray_cast(Vector((point.x, point.y, 45)), Vector((0, 0, -1)), 60)
    return None if hit is None else hit.z


def low_points(obj):
    points = vertices(obj)
    low = min(p.z for p in points)
    bottom = [p for p in points if abs(p.z-low) < .0001]
    # Bottom-face vertices plus centre; wheels have only a short contact edge.
    center = sum(bottom, Vector()) / len(bottom)
    return bottom + [center]


def perimeter_samples(obj, spacing=.20):
    bottom = low_points(obj)[:-1]
    center = sum(bottom, Vector()) / len(bottom)
    bottom.sort(key=lambda p: math.atan2(p.y-center.y, p.x-center.x))
    result = []
    for a, b in zip(bottom, bottom[1:]+bottom[:1]):
        count = max(1, math.ceil((a-b).length/spacing))
        result.extend(a.lerp(b, i/count) for i in range(count))
    return result


report = {
    'source_blend': str(args.blend),
    'door_corridor_width_m': .65,
    'door_corridor_headroom_m': 1.8,
    'maximum_visible_support_gap_m': .025,
    'cottage_approaches': [],
    'cottage_foundations': [],
    'grounded_props': [],
    'limitations': ['Saved Blender geometry and static collision only; Unity physics and Quest headset traversal are not executed.',
                    'Door clearance uses 10 cm longitudinal and 8 cm lateral ray spacing plus horizontal cross rays.'],
}
issues = []
cores = [o for o in SOURCE if o.get('sealed_house_core')]
assert len(cores) == 6, 'Expected all six completed cottage cores'
for core in cores:
    label = core['cottage_id']
    members = [o for o in SOURCE if o.get('cottage_id') == label]
    door = next(o for o in members if o.name.endswith('solid door panel'))
    footing = next(o for o in members if o.name.endswith('continuous stone footing'))
    core_center = sum(vertices(core), Vector()) / len(core.data.vertices)
    door_center = sum(vertices(door), Vector()) / len(door.data.vertices)
    # Shortest horizontal box edge is the door panel's thickness direction.
    door_vertices = vertices(door)
    edges = [door_vertices[e.vertices[1]]-door_vertices[e.vertices[0]] for e in door.data.edges]
    outward = min((e for e in edges if abs(e.z) < .0001), key=lambda e: e.length).normalized()
    if outward.dot(door_center-core_center) < 0:
        outward = -outward
    lateral = Vector((-outward.y, outward.x, 0))
    base = min(v.z for v in vertices(footing)) + .045
    failures = set()
    samples = 0
    max_cross_slope = 0
    for step in range(22):
        point = door_center + outward*(.42 + .10*step)
        point.z = base
        heights = []
        for side in range(9):
            probe = point + lateral*(-.325 + .65*side/8)
            # Grounded doorstep is permitted; a wall or prop is not walkable.
            hit, normal, index, _ = WORLD.ray_cast(probe+Vector((0,0,.30)), Vector((0,0,-1)), 1.0)
            samples += 1
            if hit is None or normal.z < .7:
                failures.add('unsupported or steep footprint')
                continue
            heights.append(hit.z)
            head, _, owner, _ = WORLD.ray_cast(hit+Vector((0,0,.18)), Vector((0,0,1)), 1.62)
            if head is not None:
                failures.add('headroom blocked by '+OWNERS[owner])
        if heights:
            max_cross_slope = max(max_cross_slope, max(heights)-min(heights))
            for altitude in (.35, 1.0, 1.75):
                start = point-lateral*.325
                start.z = max(heights)+altitude
                hit, _, index, _ = WORLD.ray_cast(start, lateral, .65)
                if hit is not None:
                    failures.add('corridor blocked by '+OWNERS[index])
    if max_cross_slope > .22:
        failures.add('cross-corridor ground variation exceeds one step')
    report['cottage_approaches'].append({'cottage': label, 'footprint_rays': samples,
        'length_m': 2.1, 'max_cross_width_height_difference_m': round(max_cross_slope, 4),
        'issues': sorted(failures)})
    issues.extend(label+': '+problem for problem in failures)

    # A closed full-footprint footing seals the building down into real terrain.
    gaps = []
    for p in perimeter_samples(footing):
        z = ground_height(p)
        gaps.append(100 if z is None else p.z-z)
    max_gap = max(gaps)
    report['cottage_foundations'].append({'cottage': label, 'perimeter_samples': len(gaps),
        'maximum_gap_m': round(max_gap, 4), 'closed_attic_and_wall_core': bool(core['sealed_house_core'])})
    if max_gap > .025:
        issues.append(label+': exposed gap under continuous foundation')


def is_grounded_prop(obj):
    name = obj.name
    return (name.startswith(('Yard crate', 'Oak planter ', 'Craft cart storage base',
                             'Craft cart solid wheel', 'Bench solid stone seat base',
                             'Spring basin base', 'Spring shelter post',
                             'Spring back pump pier', 'Bell pavilion stone plinth',
                             'Brown garden bird leg'))
            or 'porch post' in name
            or (' post' in name and any(c.name == 'Details' for c in obj.users_collection)))


for obj in SOURCE:
    if not is_grounded_prop(obj):
        continue
    probes = low_points(obj)
    gaps = [p.z-ground_height(p) if ground_height(p) is not None else 100 for p in probes]
    max_gap = max(gaps)
    report['grounded_props'].append({'object': obj.name, 'bottom_samples': len(probes),
                                     'maximum_gap_m': round(max_gap, 4)})
    if max_gap > .025:
        issues.append(obj.name+': floats %.3f m above support' % max_gap)

report['issues'] = sorted(issues)
report['passed'] = not issues
destination = ROOT / 'Documentation/village-placement-checks.json'
destination.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({'cottage_approaches': len(report['cottage_approaches']),
                  'foundation_perimeter_samples': sum(c['perimeter_samples'] for c in report['cottage_foundations']),
                  'grounded_props': len(report['grounded_props']), 'issues': sorted(issues)}, indent=2))
assert not issues, 'Placement audit failed; see Documentation/village-placement-checks.json'
print('PASS: six 0.65 m cottage approaches, sealed foundations, and grounded prop bases')
