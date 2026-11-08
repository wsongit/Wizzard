"""Validate the Blender export without claiming Unity or device validation."""
from pathlib import Path
import json, math, struct
root=Path(__file__).resolve().parents[1];asset=root/'Assets/Resources/Village/Mossbell.obj'
v=[];uv=[];normals=[];faces=[];groups={};material=''
for line in asset.read_text().splitlines():
 fields=line.split()
 if not fields:continue
 if fields[0]=='v':v.append(tuple(map(float,fields[1:4])))
 elif fields[0]=='vt':uv.append(tuple(map(float,fields[1:3])))
 elif fields[0]=='vn':normals.append(tuple(map(float,fields[1:4])))
 elif fields[0]=='usemtl':material=fields[1];groups.setdefault(material,0)
 elif fields[0]=='f':
  indices=[tuple(map(int,p.split('/'))) for p in fields[1:]]
  assert all(len(i)==3 for i in indices),'Missing UV/normal indices'
  faces.append(indices);groups[material]+=len(indices)-2
assert v and faces and uv and normals
assert all(math.isfinite(x) for row in v+uv+normals for x in row)
for face in faces:
 for a,b,c in face:assert 1<=a<=len(v) and 1<=b<=len(uv) and 1<=c<=len(normals)
 texcoords=[uv[b-1] for a,b,c in face]
 area=sum(texcoords[i][0]*texcoords[(i+1)%len(face)][1]-texcoords[(i+1)%len(face)][0]*texcoords[i][1] for i in range(len(face)))
 assert abs(area)>1e-10,'Collapsed UV island'
assert all(n in groups for n in ['Collision','CollisionTerrain','BoundaryEast','Arrival','Exit','Grass','PathBlend','WindowDark','Masonry','RoofTiles','Wood'])
assert 'WindowLight' not in groups,'Daytime windows must be muted'
for key in groups:
 if key.startswith('Collision') or key in ('Arrival','Exit','BoundaryEast'):continue
 path=root/'Assets/Resources/VillageTextures'/f'{key}.png'
 assert path.exists(),key
 assert struct.unpack('>II',path.read_bytes()[16:24])==(64,64),key
for line in asset.with_suffix('.mtl').read_text().splitlines():
 if line.startswith(('map_Kd ','map_d ')):
  ref=line.split(maxsplit=1)[1];assert not Path(ref).is_absolute();assert (asset.parent/ref).exists()
assert (root/'Assets/Resources/VillageTextures/PathBlend.png').read_bytes()[25]==6,'Path PNG must preserve RGBA cutout data'
report=json.loads((root/'Documentation/village-geometry-checks.json').read_text())
assert all(not route['issues'] for route in report['routes'])
assert report['export_triangles_including_collision']==sum(groups.values())
assert (root/'Blender/MossbellVillage.blend').stat().st_size>100000
print(json.dumps({'status':'PASS export integrity (not Unity compilation)', 'vertices':len(v),'uv_coordinates':len(uv),'triangles_by_material':groups,'checked_routes':len(report['routes'])},indent=2))
