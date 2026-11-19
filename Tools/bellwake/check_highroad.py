"""Reimport the shipping Unity field and sample each corridor at one-metre intervals."""
import bpy
from collections import Counter
import math
import json
import sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from watershed import EAST, NORTH, MEADOW, chart
from highroad import LANES

assets = root / "Assets/Resources/Bellwake"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(assets / "Rooms/Highroad.fbx"))
anchors = [o for o in bpy.context.scene.objects if o.name.startswith("FieldAnchor_")]
assert len(anchors) == 42
cells = sorted((assets / "Field").glob("FieldCell_*.fbx"))
assert len(cells) == len(anchors)
for cell in cells:
    bpy.ops.import_scene.fbx(filepath=str(cell))

def tree(objects):
    points, faces = [], []
    for obj in objects:
        offset = len(points)
        points.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
        faces.extend(tuple(offset + i for i in f.vertices) for f in obj.data.polygons)
    return BVHTree.FromPolygons(points,faces)

ground = tree([bpy.data.objects["Terrain"]])
# At a field boundary Unity palm casts hit front faces. Test the exported winding too.
rim = tree([bpy.data.objects["Rim"]])
land = bpy.data.objects["Terrain"]
uses = Counter(tuple(sorted(e)) for f in land.data.polygons for e in f.edge_keys)
boundary_samples = 0
for (ia, ib), count in uses.items():
    if count != 1:
        continue
    a, b = (land.matrix_world @ land.data.vertices[i].co for i in (ia, ib))
    mid = (a + b) * .5
    outside = Vector((b.y-a.y,a.x-b.x,0)).normalized()
    if outside.dot(mid) < 0:
        outside.negate()
    for z in (.20, .85, 1.65):
        origin = mid - outside * .3 + Vector((0,0,z))
        hit, normal, _, _ = rim.ray_cast(origin, outside, 6)
        assert hit is not None and normal.dot(outside) < -.9, ("cliff seam or backface",mid,z)
        boundary_samples += 1
obstacles = tree([bpy.data.objects[k] for k in ["Set","C_Solids","Rim"] + [f.stem for f in cells]])
doors = {o.name[4:]:o.matrix_world.translation for o in bpy.context.scene.objects if o.name.startswith("Road")}
coords = {key:(EAST[i], NORTH[j]) for j,row in enumerate(LANES) for i,key in enumerate(row.split())}
coords["LongMeadow"] = MEADOW
assert set(doors) == set(coords)
edges = [(a,b) for a in coords for b in coords if a<b and
         ((coords[a][0] == coords[b][0] and abs(coords[a][1]-coords[b][1]) in (85,170)) or
          (coords[a][1] == coords[b][1] and abs(coords[a][0]-coords[b][0]) == 180))]
assert len(edges) == 72
for key, uv in coords.items():
    xy = chart(*uv)
    assert (doors[key].xy-Vector(xy)).length < .002, key
    floor = ground.ray_cast((*xy,100),(0,0,-1),180)[0]
    assert floor and -.02 < doors[key].z-floor.z < .35, (key, floor)
probes = 0
length = 0
peak = 0
trace = []
for a,b in edges:
    ua,va = coords[a]
    ub,vb = coords[b]
    steps = math.ceil(math.hypot(ub-ua,vb-va))
    previous = None
    for step in range(steps+1):
        t = step/steps
        xy = Vector(chart(ua+(ub-ua)*t,va+(vb-va)*t))
        direction = Vector(chart(ua+(ub-ua)*(t+.001),va+(vb-va)*(t+.001)))-xy
        lateral = Vector((-direction.y,direction.x)).normalized()
        for offset in (-.55,0,.55):
            q = xy + lateral*offset
            hit,normal,_,_=ground.ray_cast((*q,100),(0,0,-1),180)
            assert hit is not None and normal.z>.92,(a,b,step,"ground",q)
            assert obstacles.ray_cast(hit+Vector((0,0,.025)),(0,0,1),2.05)[0] is None,(a,b,step,"overhead",q)
            assert obstacles.find_nearest(hit+Vector((0,0,.9)),.23)[0] is None,(a,b,step,"side",q)
            probes+=1
            if offset==0:
                if previous: length+=(hit-previous).length
                previous=hit
        if step%20==0: trace.append(xy)
# Apply the same hysteresis as the native field while crossing and revisiting every surveyed lane.
active=set()
for xy in trace + trace[::-1]:
    for mark in anchors:
        d=(mark.matrix_world.translation.xy-xy).length
        if d<=365: active.add(mark.name)
        if d>425: active.discard(mark.name)
    peak=max(peak,len(active))
assert 1 < peak < 42
result=dict(entrances=len(coords),links=len(edges),walkingMetres=round(length),
            clearanceSamples=probes,boundarySamples=boundary_samples,peakNearCells=peak,availableCells=len(cells))
print(json.dumps(result))
