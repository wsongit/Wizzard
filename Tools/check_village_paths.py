"""Validate paths painted into one terrain surface, not layered ribbon meshes.

Run with Blender --python-exit-code 1. Reads the saved .blend and the actual PNG
mask. Checks exported-source UV placement, top-surface overlap, dirt on slopes,
walking-width coverage and junctions. This does not run Unity's shader or physics.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--blend', type=Path, default=ROOT / 'Blender/MossbellVillage.blend')
parser.add_argument('--report', type=Path, default=ROOT / 'Documentation/village-path-checks.json')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=str(args.blend.resolve()))
issues = []

def issue(message):
    if len(issues) < 100:
        issues.append(message)

layout = json.loads((ROOT / 'Documentation/village-path-layout.json').read_text())
bounds = layout['bounds']
xmin, xmax, ymin, ymax = bounds
paths = layout['paths']
land = bpy.data.objects['Unified village landform']
land.data.calc_loop_triangles()
vertices = [land.matrix_world @ v.co for v in land.data.vertices]
triangles = [tuple(t.vertices) for t in land.data.loop_triangles]
land_bvh = BVHTree.FromPolygons(vertices, triangles, all_triangles=True)
triangle_materials = [land.data.materials[t.material_index].name.split('.')[0]
                      for t in land.data.loop_triangles]
if 'VillageGround' not in triangle_materials:
    issue('VillageGround material missing from saved landform')

legacy = []
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH' or any(c.name == 'Collision' for c in obj.users_collection):
        continue
    if obj.get('path_uv') or any(m and m.name.split('.')[0] == 'PathBlend' for m in obj.data.materials):
        legacy.append(obj.name)
if legacy:
    issue('Detached legacy path surfaces remain: ' + ', '.join(legacy))

# The mask must use the ground's planar metric UVs consistently through the OBJ.
max_uv_error = 0
uv = land.data.uv_layers.active
if uv is None:
    issue('Landform has no UV map')
else:
    for p in land.data.polygons:
        if land.data.materials[p.material_index].name.split('.')[0] != 'VillageGround':
            continue
        for li in p.loop_indices:
            v = vertices[land.data.loops[li].vertex_index]
            expected = Vector((v.x * .25, v.y * .25))
            max_uv_error = max(max_uv_error, (uv.data[li].uv - expected).length)
    if max_uv_error > .0001:
        issue('Ground UVs do not match the shared world-space path mask: ' + str(max_uv_error))

mask_path = ROOT / 'Assets/Resources/VillageMasks/GroundPaths.png'
mask_image = bpy.data.images.load(str(mask_path), check_existing=False)
mask_image.colorspace_settings.name = 'Non-Color'
w, h = mask_image.size
pixels = list(mask_image.pixels)
channels = mask_image.channels
if (w, h) != (1024, 1024):
    issue('Unexpected mask dimensions: ' + str((w, h)))

def mask_at(x, y):
    # Blender's pixel array starts at the bottom-left, matching UV coordinates.
    u = (x-xmin)/(xmax-xmin)
    v = (y-ymin)/(ymax-ymin)
    px = max(0, min(w-1, u*w-.5))
    py = max(0, min(h-1, v*h-.5))
    ix, iy = int(px), int(py)
    jx, jy = min(ix+1, w-1), min(iy+1, h-1)
    fx, fy = px-ix, py-iy
    def value(i, j):
        return pixels[(j*w+i)*channels]
    return ((value(ix, iy)*(1-fx)+value(jx, iy)*fx)*(1-fy)
            +(value(ix, jy)*(1-fx)+value(jx, jy)*fx)*fy)

def ground_at(x, y):
    hit, normal, index, _ = land_bvh.ray_cast(Vector((x, y, 50)), Vector((0, 0, -1)), 60)
    return hit, normal, index

# One projected top triangle must own each road location. This exact convex
# clipping check catches duplicate/crossed surfaces independently of ray spacing.
def cross(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])

def clip(poly, tri):
    if cross(*tri) < 0:
        tri = list(reversed(tri))
    for a, b in zip(tri, tri[1:]+tri[:1]):
        out = []
        for p, q in zip(poly, poly[1:]+poly[:1]):
            cp, cq = cross(a, b, p), cross(a, b, q)
            ip, iq = cp >= -1e-10, cq >= -1e-10
            if ip:
                out.append(p)
            if ip != iq:
                t = cp/(cp-cq)
                out.append((p[0]+(q[0]-p[0])*t, p[1]+(q[1]-p[1])*t))
        poly = out
        if len(poly) < 3:
            return []
    return poly

def area(poly):
    return abs(sum(p[0]*q[1]-q[0]*p[1] for p, q in zip(poly, poly[1:]+poly[:1])))/2

route_points = [p for path in paths for p in path['points']]
margin = max(path['width'] for path in paths)/2 + 1
pxmin = min(p[0] for p in route_points)-margin
pxmax = max(p[0] for p in route_points)+margin
pymin = min(p[1] for p in route_points)-margin
pymax = max(p[1] for p in route_points)+margin
projected = []
for ids in triangles:
    a, b, c = (vertices[i] for i in ids)
    if (b-a).cross(c-a).z <= 1e-8:
        continue  # Closed underside and vertical skirts cannot be road surfaces.
    poly = [(p.x, p.y) for p in (a, b, c)]
    if (max(p[0] for p in poly) < pxmin or min(p[0] for p in poly) > pxmax
            or max(p[1] for p in poly) < pymin or min(p[1] for p in poly) > pymax):
        continue
    projected.append(poly)
bins = {}
pairs = set()
for i, poly in enumerate(projected):
    for y in range(math.floor(min(p[1] for p in poly)/4), math.floor(max(p[1] for p in poly)/4)+1):
        for x in range(math.floor(min(p[0] for p in poly)/4), math.floor(max(p[0] for p in poly)/4)+1):
            key = (x, y)
            for j in bins.get(key, []):
                pairs.add((j, i))
            bins.setdefault(key, []).append(i)
overlap_pairs = 0
summed_overlap = 0
for i, j in pairs:
    intersection = clip(projected[i], projected[j])
    overlap = area(intersection) if intersection else 0
    if overlap > .000001:
        overlap_pairs += 1
        summed_overlap += overlap
if overlap_pairs:
    issue('Overlapping ground triangles in path region: ' + str(overlap_pairs))

# Sample the actual image over the terrain, including mask pixels near cliffs.
# Only VillageGround renders the mask; an EarthCliff face never becomes dirt.
painted_samples = 0
steep_painted_samples = 0
max_painted_slope = 0
for j in range(h):
    for i in range(w):
        if pixels[(j*w+i)*channels] < .5:
            continue
        x = xmin+(i+.5)*(xmax-xmin)/w
        y = ymin+(j+.5)*(ymax-ymin)/h
        hit, normal, index = ground_at(x, y)
        if hit is None:
            issue('Mask is painted beyond the actual landform')
            continue
        if triangle_materials[index] != 'VillageGround':
            continue
        painted_samples += 1
        slope = math.degrees(math.acos(max(-1, min(1, normal.z))))
        max_painted_slope = max(max_painted_slope, slope)
        if normal.z < .819:
            steep_painted_samples += 1
if steep_painted_samples:
    issue('Dirt renders on steep ground faces: ' + str(steep_painted_samples))
if painted_samples < 100:
    issue('Expected a painted path network, mask is empty or misplaced')

route_reports = []
for path in paths:
    failures = []
    checked = 0
    min_coverage = 1
    for a, b in zip(path['points'], path['points'][1:]):
        a, b = Vector(a), Vector(b)
        direction = b-a
        direction.z = 0
        distance = direction.length
        if distance <= .0001:
            continue
        side = Vector((-direction.y/distance, direction.x/distance, 0))
        count = max(1, math.ceil(distance/.25))
        for i in range(count+1):
            p = a.lerp(b, i/count)
            for offset in (-.325, 0, .325):
                q = p+side*offset
                hit, normal, index = ground_at(q.x, q.y)
                coverage = mask_at(q.x, q.y)
                min_coverage = min(min_coverage, coverage)
                checked += 1
                if hit is None or triangle_materials[index] != 'VillageGround' or coverage < .5:
                    if len(failures) < 8:
                        failures.append({'xy': [round(q.x, 3), round(q.y, 3)],
                                         'mask': round(coverage, 3),
                                         'material': triangle_materials[index] if index is not None else None,
                                         'normal_z': round(normal.z, 3) if normal is not None else None})
    if failures:
        issue('Broken 0.65m dirt corridor: '+path['name']+' '+str(failures))
    route_reports.append({'name': path['name'], 'samples': checked,
                          'minimum_mask_coverage': round(min_coverage, 4), 'failures': failures})

# These junctions caused the reported visual overlaps. Each must now be painted
# into the one ground surface, with no second path plane or hole.
# Check the actual mask's connected regions as well as individual polylines.
# Tiny edge pixels are reported; a separate large patch indicates a broken link.
active_pixels = {j*w+i for j in range(h) for i in range(w)
                 if pixels[(j*w+i)*channels] >= .5}
component_sizes = []
while active_pixels:
    pending = [active_pixels.pop()]
    size = 0
    while pending:
        k = pending.pop()
        size += 1
        y, x = divmod(k, w)
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            nx, ny = x+dx, y+dy
            if 0 <= nx < w and 0 <= ny < h:
                n = ny*w+nx
                if n in active_pixels:
                    active_pixels.remove(n)
                    pending.append(n)
    component_sizes.append(size)
component_sizes.sort(reverse=True)
if len([n for n in component_sizes if n > 64]) > 1:
    issue('Painted road network has disconnected regions: '+str(component_sizes[:12]))

junctions = []
for label, x, y in [('Entrance and cottage tracks', 1, 3),
                     ('Middle approach to upper climb', 9, 19),
                     ('Upper climb to bell approach', 20, 30)]:
    hit, normal, index = ground_at(x, y)
    coverage = mask_at(x, y)
    valid = hit is not None and triangle_materials[index] == 'VillageGround' and coverage >= .5
    junctions.append({'name': label, 'xy': [x, y], 'mask_coverage': round(coverage, 4), 'passed': valid})
    if not valid:
        issue('Unpainted or missing path junction: '+label)

report = {'source': str(args.blend.resolve()),
          'status': 'PASS' if not issues else 'FAIL',
          'representation': 'One opaque landform; dirt and grass mixed by a shared PNG mask',
          'legacy_path_surfaces': legacy, 'mask_dimensions': [w, h],
          'max_world_uv_error': round(max_uv_error, 8),
          'projected_ground_triangles_checked': len(projected),
          'overlapping_top_triangle_pairs': overlap_pairs,
          'summed_projected_overlap_m2': round(summed_overlap, 8),
          'painted_mask_samples': painted_samples,
          'max_painted_slope_degrees': round(max_painted_slope, 4),
          'steep_painted_samples': steep_painted_samples,
          'mask_component_sizes_pixels': component_sizes,
          'routes': route_reports, 'junctions': junctions, 'issues': issues,
          'limits': ['Saved Blender geometry and actual PNG sampling; Unity shader/runtime not executed.',
                     'Corridor samples cover 0.65m width every 0.25m along each authored path.']}
args.report.write_text(json.dumps(report, indent=2)+'\n')
assert not issues, '\n'.join(issues)
print('PASS: single terrain surface, no projected overlaps, correct mask UVs, slope-limited dirt and continuous path junctions')
print(json.dumps({'painted_samples': painted_samples, 'route_samples': sum(p['samples'] for p in route_reports),
                  'overlap_pairs': overlap_pairs, 'maximum_dirt_slope': round(max_painted_slope, 4)}))
