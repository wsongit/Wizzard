"""Fixed crossed plant images at the verge, rooted on the exported terrain mesh."""
import math
import random
from mathutils.bvhtree import BVHTree
from atelier import batches, geometry

# Coordinates are in Blender metres, with the planting set back from the walking lanes.
# Index 0 is fern, 1 sorrel, 2 meadow flowers, 3 cattails.
BEDS = {
    "Bellmarket": [(4.9,-11,2),(-5.2,-13.6,1),(-7.3,-9.9,2),(4.8,-5.6,1),(7.4,-4.3,2),
                   (-8.1,1.5,0),(-5.7,8.5,1),(6,11.7,2),(-7.9,13.1,1)],
    "RootChoir": [(-4.8,-11.3,0),(5.8,-9.4,0),(-5.2,-5.8,1),(6.9,-4,0),(-8.4,1.9,0),
                  (8.5,4.2,1),(-8.8,7.6,0),(4.4,8.9,2),(10.8,11.7,0),(-4.5,12.9,1)],
    "Reedwater": [(-5.1,-11.9,1),(5.2,-9.2,2),(9.7,-3.4,3),(9.9,1.5,3),(12.8,4.9,3),
                  (-10.9,2.4,3),(-11.5,5.3,3),(-5.8,11.1,1),(4.8,13.1,2)],
    "RowanHollow": [(-7.3,-18.7,0),(8.8,-15.1,1),(-13.4,-7.9,0),(6.8,4.3,0),
                    (-11.6,11.9,0),(21,15.2,1),(-18.6,20,0),(13.8,24.9,2)],
}


def surface(objects):
    vertices, faces = [], []
    for obj in objects:
        offset = len(vertices)
        vertices.extend(obj.matrix_world @ vert.co for vert in obj.data.vertices)
        faces.extend(tuple(offset + i for i in face.vertices) for face in obj.data.polygons)
    return BVHTree.FromPolygons(vertices, faces)


def plant(key):
    if key not in BEDS or batches.get("BanksidePlants"):
        return
    terrain = surface(batches["Terrain"])
    nearby = surface(batches["Set"] + batches["C_Solids"])
    rng = random.Random(1829 + sum(key.encode()))
    verts, faces, uvs = [], [], []
    for cx, cy, kind in BEDS[key]:
        for j in range(rng.randint(3, 5)):
            angle = rng.uniform(0, math.tau)
            spread = math.sqrt(rng.random()) * 1.30 if j else 0
            x = cx + spread * math.cos(angle)
            y = cy + spread * math.sin(angle)
            hit, normal, _, _ = terrain.ray_cast((x, y, 50), (0, 0, -1), 100)
            if hit is None or normal.z < .75:
                continue
            size = rng.uniform(.45, .76) * (1.50 if kind == 3 else 1)
            if nearby.find_nearest((x, y, hit.z + .18), size * .53)[0] is not None:
                continue
            z = hit.z - size * .038
            # Opaque texels begin two pixels above the lower edge in the 64px cell.
            for turn in (0, math.pi * .5):
                dx = math.cos(angle + turn) * size * .5
                dy = math.sin(angle + turn) * size * .5
                corners = [(x-dx,y-dy,z),(x+dx,y+dy,z),(x+dx,y+dy,z+size),(x-dx,y-dy,z+size)]
                first = len(verts)
                verts.extend(corners)
                faces.append(tuple(range(first, first+4)))
                for u, v in [(0,0),(1,0),(1,1),(0,1)]:
                    uvs.append(((kind % 2 + (.5 + 63*u)/64)/2,
                                (1-kind//2 + (.5 + 63*v)/64)/2))
    if not faces:
        raise ValueError("No ground for " + key + " plants")
    plants = geometry("Rooted verge plants", verts, faces, "BanksidePlants", "BanksidePlants", uv=uvs)
    # A tuft has one light direction, including where the two planes cross.
    for face in plants.data.polygons:
        face.use_smooth = True
    plants.data.normals_split_custom_set([(0, 0, 1)] * len(plants.data.loops))
