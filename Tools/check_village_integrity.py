"""Audit the whole village's ground, containment shells and building support.

Run: blender -b -t 2 --python-exit-code 1 --python Tools/check_village_integrity.py
Uses dense geometry probes, not Unity physics. Does not claim all VR exploits are
impossible: headset room-scale motion and runtime recovery require device tests.
"""
import bpy, bmesh, math, json, argparse, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--blend', type=Path, default=ROOT / 'Blender/MossbellVillage.blend')
parser.add_argument('--report', type=Path, default=ROOT / 'Documentation/village-integrity-checks.json')
parser.add_argument('--no-render', action='store_true', help=argparse.SUPPRESS)
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=str(args.blend.resolve()))
issues = []
report = {'source': str(args.blend.resolve()), 'limits': [
    'Blender geometry probes, not Unity or Quest physics tests.',
    'Ground coverage sampled every 0.5 m; this is not a proof against every possible player exploit.',
    'A closed landform, closed roofs and continuous perimeter remove internal geometry cavities; runtime exterior/under-ground recovery must also be verified in Unity.',
]}

def issue(message):
    if len(issues) < 100:
        issues.append(message)

def geometry(obj):
    return ([obj.matrix_world @ v.co for v in obj.data.vertices],
            [tuple(p.vertices) for p in obj.data.polygons])

def bvh(obj):
    vertices, _ = geometry(obj)
    # BVHTree tessellates nonplanar n-gons differently from Mesh's render
    # triangles. Probe the exact triangles that define the visible surface.
    obj.data.calc_loop_triangles()
    triangles = [tuple(tri.vertices) for tri in obj.data.loop_triangles]
    return BVHTree.FromPolygons(vertices, triangles, all_triangles=True)

def closed_shell(obj):
    vertices, faces = geometry(obj)
    data = bpy.data.meshes.new('Integrity temporary')
    data.from_pydata(vertices, [], faces)
    data.update()
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.00001)
    boundary = sum(not edge.is_manifold for edge in bm.edges)
    inconsistent = sum(edge.is_manifold and not edge.is_contiguous for edge in bm.edges)
    zero_area = sum(face.calc_area() < 1e-10 for face in bm.faces)
    volume = bm.calc_volume(signed=True)
    remaining = set(bm.faces)
    components = 0
    while remaining:
        pending = [remaining.pop()]
        components += 1
        while pending:
            face = pending.pop()
            for edge in face.edges:
                for adjacent in edge.link_faces:
                    if adjacent in remaining:
                        remaining.remove(adjacent)
                        pending.append(adjacent)
    result = {'object': obj.name, 'nonmanifold_edges': boundary,
              'inconsistent_edges': inconsistent, 'zero_area_faces': zero_area,
              'connected_components': components, 'volume_m3': round(volume, 5)}
    bm.free()
    bpy.data.meshes.remove(data)
    if boundary or inconsistent or zero_area or volume <= 0 or components != 1:
        issue('Invalid closed shell: ' + str(result))
    return result

def collision_for(obj):
    collection = bpy.data.collections.get('Collision')
    match = collection.objects.get('Collision ' + obj.name) if collection else None
    if match is None:
        issue('Missing dedicated collision: ' + obj.name)
    else:
        visible_vertices, visible_faces = geometry(obj)
        physical_vertices, physical_faces = geometry(match)
        if (visible_faces != physical_faces or len(visible_vertices) != len(physical_vertices)
                or any((a-b).length > .0001 for a, b in zip(visible_vertices, physical_vertices))):
            issue('Collision mesh differs from visible solid: ' + obj.name)
    return match

land = bpy.data.objects.get('Unified village landform')
wall = bpy.data.objects.get('Closed irregular perimeter')
if land is None or wall is None:
    raise AssertionError('Expected Unified village landform and Closed irregular perimeter')
land_collision = collision_for(land)
wall_collision = collision_for(wall)
land_tree = bvh(land)
land_collision_tree = bvh(land_collision) if land_collision else None
wall_tree = bvh(wall)
wall_collision_tree = bvh(wall_collision) if wall_collision else None
shells = [closed_shell(land), closed_shell(wall)]
for obj in (land_collision, wall_collision):
    if obj:
        shells.append(closed_shell(obj))
vertices, _ = geometry(land)
zmin = min(v.z for v in vertices)
zmax = max(v.z for v in vertices)
ceiling = zmax + 10
length = ceiling - zmin + 5

# Dense whole-domain coverage; each vertical line must cross the top and then
# the solid bottom. An intervening crossing can expose an internal cavity.
counts = {'spacing_m': 0.5, 'bounds_xy': [-55, 60, -46, 68], 'samples': 0,
          'missing_ground': 0, 'wrong_top_normal': 0,
          'internal_crossings_or_missing_bottom': 0, 'collision_mismatches': 0}
max_collision_delta = 0
for j in range(228):
    y = -46 + (j + 0.5) * 0.5
    for i in range(230):
        x = -55 + (i + 0.5) * 0.5
        counts['samples'] += 1
        hit, normal, _, _ = land_tree.ray_cast(Vector((x, y, ceiling)), Vector((0, 0, -1)), length)
        if hit is None:
            counts['missing_ground'] += 1
            issue('Ground missing at ' + str((x, y)))
            continue
        if normal.z <= 0:
            counts['wrong_top_normal'] += 1
            issue('Ground top faces down at ' + str((x, y)))
        bottom, bottom_normal, _, _ = land_tree.ray_cast(hit - Vector((0, 0, .002)), Vector((0, 0, -1)), length)
        if bottom is None or abs(bottom.z - zmin) > .01 or bottom_normal.z >= -.5:
            counts['internal_crossings_or_missing_bottom'] += 1
            issue('Possible internal ground cavity at ' + str((x, y)))
        if land_collision_tree:
            physical, _, _, _ = land_collision_tree.ray_cast(Vector((x, y, ceiling)), Vector((0, 0, -1)), length)
            delta = abs(physical.z - hit.z) if physical is not None else length
            max_collision_delta = max(max_collision_delta, delta)
            if delta > .002:
                counts['collision_mismatches'] += 1
                issue('Ground collision mismatch at ' + str((x, y)))
counts['max_visual_collision_delta_m'] = round(max_collision_delta, 6)
report['ground'] = counts

# Both sides of each vertical/sloping wall triangle, several barycentric heights.
# This includes the end caps at the intentional entrance instead of assuming a
# single radial origin can see every wall section.
wall.data.calc_loop_triangles()
wall_vertices, _ = geometry(wall)
wall_rays = 0
wall_failures = 0
for tri in wall.data.loop_triangles:
    a, b, c = (wall_vertices[i] for i in tri.vertices)
    n = (b - a).cross(c - a).normalized()
    if abs(n.z) > .8:
        continue
    for wa, wb, wc in [(1/3, 1/3, 1/3), (.6, .2, .2), (.2, .6, .2), (.2, .2, .6)]:
        p = a * wa + b * wb + c * wc
        for side in (-1, 1):
            origin = p + n * (.12 * side)
            direction = -n * side
            hit, _, _, _ = wall_tree.ray_cast(origin, direction, .25)
            wall_rays += 1
            if hit is None or (hit - p).length > .01:
                wall_failures += 1
                issue('Perimeter surface gap near ' + str(tuple(round(v, 3) for v in p)))
            if wall_collision_tree:
                physical, _, _, _ = wall_collision_tree.ray_cast(origin, direction, .25)
                if physical is None or (physical - p).length > .01:
                    wall_failures += 1
                    issue('Perimeter collision gap near ' + str(tuple(round(v, 3) for v in p)))

# Bottom edges must be buried in the landform. A watertight wall floating above
# a watertight floor would otherwise pass both independent shell checks.
wall_bottom = min(p.z for p in wall_vertices)
wall_floor_samples = 0
wall_floor_failures = 0
for edge in wall.data.edges:
    a, b = (wall_vertices[i] for i in edge.vertices)
    if max(abs(a.z - wall_bottom), abs(b.z - wall_bottom)) > .01:
        continue
    n = max(1, math.ceil((b-a).length / .5))
    for i in range(n + 1):
        p = a.lerp(b, i/n)
        top, _, _, _ = land_tree.ray_cast(Vector((p.x, p.y, ceiling)), Vector((0, 0, -1)), length)
        wall_floor_samples += 1
        if top is None or top.z < p.z + .05:
            wall_floor_failures += 1
            issue('Wall-floor separation at ' + str(tuple(round(v, 3) for v in p)))
report['perimeter'] = {'two_sided_triangle_rays': wall_rays, 'surface_failures': wall_failures,
                       'floor_join_samples': wall_floor_samples, 'floor_join_failures': wall_floor_failures,
                       'intentional_opening': 'South village entrance, x=-4..4 at y=-34'}

# Architecture can explicitly mark closed envelope meshes. Footing corners and
# edges are checked against terrain only so a foundation cannot support itself.
cottages = bpy.data.collections.get('Cottages')
support_checks = []
closed_architecture = []
closed_cores = []
if cottages:
    for obj in cottages.objects:
        if obj.type != 'MESH':
            continue
        if obj.get('integrity_closed_shell', False) or obj.get('sealed_house_core', False) or obj.get('closed_building_slab', False):
            shells.append(closed_shell(obj))
            closed_architecture.append(obj.name)
            if obj.get('sealed_house_core', False):
                closed_cores.append(obj.name)
            physical = collision_for(obj)
            if physical:
                shells.append(closed_shell(physical))
        name = obj.name.lower()
        if not ('footing' in name or 'foundation' in name or obj.get('integrity_support', False)):
            continue
        verts, _ = geometry(obj)
        low = min(v.z for v in verts)
        high = max(v.z for v in verts)
        bottom_verts = [v for v in verts if abs(v.z-low) < .001]
        if not bottom_verts:
            continue
        probes = list(bottom_verts)
        probes.append(sum(bottom_verts, Vector()) / len(bottom_verts))
        for edge in obj.data.edges:
            a, b = (verts[i] for i in edge.vertices)
            if abs(a.z-low) > .001 or abs(b.z-low) > .001:
                continue
            n = max(1, math.ceil((a-b).length / .5))
            probes.extend(a.lerp(b, i/n) for i in range(1, n))
        # Cover the interior too: corners and edges alone miss a depression
        # underneath a broad foundation. A downward foundation ray clips this
        # world-space grid to the actual rotated footprint.
        footing_tree = bvh(obj)
        min_x, max_x = min(v.x for v in verts), max(v.x for v in verts)
        min_y, max_y = min(v.y for v in verts), max(v.y for v in verts)
        interior_samples = 0
        for j in range(math.floor(min_y * 2), math.ceil(max_y * 2) + 1):
            for i in range(math.floor(min_x * 2), math.ceil(max_x * 2) + 1):
                x, y = i * .5, j * .5
                hit, _, _, _ = footing_tree.ray_cast(Vector((x, y, ceiling)), Vector((0, 0, -1)), length)
                if hit is not None:
                    probes.append(Vector((x, y, low)))
                    interior_samples += 1
        max_float = 0
        max_burial = 0
        for p in probes:
            top, _, _, _ = land_tree.ray_cast(Vector((p.x, p.y, ceiling)), Vector((0, 0, -1)), length)
            if top is None:
                issue('No terrain under ' + obj.name)
                continue
            max_float = max(max_float, p.z - top.z)
            max_burial = max(max_burial, top.z - high)
        if max_float > .08 or max_burial > .08:
            issue('Foundation placement: '+obj.name+' floating='+str(round(max_float,3))+' buried='+str(round(max_burial,3)))
        support_checks.append({'object': obj.name, 'samples': len(probes),
                               'interior_samples': interior_samples,
                               'max_float_m': round(max_float, 5), 'max_burial_above_footing_m': round(max_burial, 5)})
if len(closed_cores) < 6:
    issue('Expected at least six sealed cottage cores, got '+str(len(closed_cores)))
if len(support_checks) < 6:
    issue('Expected at least six foundation support checks, got '+str(len(support_checks)))
report['closed_architecture'] = closed_architecture
report['sealed_cottage_cores'] = closed_cores
report['building_support'] = support_checks

# Check trunk bases against terrain independently of the generator's own root
# centre assertions. The whole base ring must sit on or intersect the ground.
tree_support = []
trees = bpy.data.collections.get('Trees')
if trees:
    for obj in trees.objects:
        if obj.type != 'MESH' or 'angular trunk' not in obj.name:
            continue
        verts, _ = geometry(obj)
        low = min(v.z for v in verts)
        probes = [v for v in verts if abs(v.z-low) < .001]
        probes.append(sum(probes, Vector()) / len(probes))
        max_float = 0
        for p in probes:
            top, _, _, _ = land_tree.ray_cast(Vector((p.x, p.y, ceiling)), Vector((0, 0, -1)), length)
            if top is None:
                issue('No terrain under tree: ' + obj.name)
            else:
                max_float = max(max_float, p.z-top.z)
        if max_float > .08:
            issue('Floating tree base: ' + obj.name + ' gap=' + str(round(max_float, 3)))
        tree_support.append({'object': obj.name, 'samples': len(probes), 'max_float_m': round(max_float, 5)})
if len(tree_support) < 7:
    issue('Expected at least seven trunk support checks, got ' + str(len(tree_support)))
report['tree_support'] = tree_support
report['closed_shells'] = shells
report['issues'] = issues
report['status'] = 'PASS' if not issues else 'FAIL'
args.report.write_text(json.dumps(report, indent=2) + '\n')
assert not issues, '\n'.join(issues)
print('PASS: whole-domain ground coverage, solid landform, matching collision, wall surfaces/joins and building support')
print(json.dumps({'ground_samples': counts['samples'], 'wall_rays': wall_rays,
                  'wall_floor_samples': wall_floor_samples,
                  'foundations': len(support_checks), 'closed_architecture': len(closed_architecture)}))
