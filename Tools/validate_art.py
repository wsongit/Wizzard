"""Validate the generated Blender artifact; run with the .blend loaded."""
import bpy, math
from pathlib import Path
root=Path(__file__).resolve().parents[1]
terrain=bpy.data.objects['2048m rolling meadow']
mesh=terrain.data
assert len(mesh.vertices)==66049
assert len(mesh.polygons)==131072
for axis in (0,1):
    values=[v.co[axis] for v in mesh.vertices]
    assert min(values)==-1024 and max(values)==1024
assert all(len(p.vertices)==3 for p in mesh.polygons)
assert all(math.isfinite(c) for v in mesh.vertices for c in v.co)
inner=[v.co.z for v in mesh.vertices if abs(v.co.x)<600 and abs(v.co.y)<600]
assert max(inner)-min(inner)>10, 'Interior hills missing'
assert max(inner)<20, 'Interior hills unexpectedly tall'
paint=next(n.image for n in terrain.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE')
assert tuple(paint.size)==(64,64)
assert paint.packed_file.data==(root/'Assets/Resources/VillageTextures/Grass.png').read_bytes()
assert 'GorillaTorso' in bpy.data.objects
obj=root/'Assets/Resources/GorillaTorso.obj'
assert obj.stat().st_size>1000
faces=[l for l in obj.read_text().splitlines() if l.startswith('f ')]
assert len(faces)>100
assert (root/'Documentation/meadow-preview.png').stat().st_size>10000
print('PASS: 2048m terrain, 131072 triangles, rolling hills, packed 64px grass painting, avatar OBJ, rendered preview')
