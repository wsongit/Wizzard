"""Reimport the shipping FBX and check each road over its full length at runner width."""
import bpy
import json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path

root=Path(__file__).resolve().parents[2]
assets=root/"Assets/Resources/Bellwake"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(assets/"Rooms/Highroad.fbx"))

def tree(keys):
    points,faces=[],[]
    for key in keys:
        obj=bpy.data.objects[key]
        offset=len(points)
        points.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        faces.extend(tuple(offset+i for i in f.vertices) for f in obj.data.polygons)
    return BVHTree.FromPolygons(points,faces)

ground=tree(["Terrain"])
obstacles=tree(["Set","C_Solids","Rim"])
doors={o.name[4:]:o.matrix_world.translation for o in bpy.context.scene.objects if o.name.startswith("Road")}
keys={"Bellmarket","RootChoir","Reedwater","CinderLens","StillBelfry","LongMeadow"}
for file,field in [("Underworks","rooms"),("Passages","regions")]:
    keys.update(r["key"] for r in json.loads((assets/(file+".json")).read_text())[field])
assert set(doors)==keys
edges=[]
for a,source in doors.items():
    for b,target in doors.items():
        if b<=a: continue
        delta=target.xy-source.xy
        if a=="LongMeadow" or b=="LongMeadow":
            if abs(delta.length-10)>.001: continue
        elif abs(delta.length-20)>.001: continue
        edges.append((a,b))
        for j in range(81):
            centre=source.lerp(target,j/80)
            for offset in (-.38,0,.38):
                x=centre.x-offset*delta.y/delta.length
                y=centre.y+offset*delta.x/delta.length
                contact,normal,_,_=ground.ray_cast((x,y,12),(0,0,-1),24)
                assert contact is not None and normal.z>.92,(a,b,j,"ground",x,y)
                wall=obstacles.ray_cast(contact+Vector((0,0,.06)),(0,0,1),2.0)[0]
                assert wall is None,(a,b,j,"obstruction",wall)
assert len(edges)==72
print("Verified 43 entrances and 72 connecting lanes at 17,496 runner-clearance samples.")
