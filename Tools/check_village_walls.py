"""Check closed village wall geometry and render front/rear inspection views in Blender."""
import bpy,bmesh,math,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'Blender/MossbellVillage.blend'))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('Collision')]
checks=[]
def check(name,group):
 vertices=[];faces=[]
 for obj in group:
  offset=len(vertices);vertices.extend([obj.matrix_world@v.co for v in obj.data.vertices]);faces.extend([tuple(offset+i for i in p.vertices) for p in obj.data.polygons])
 data=bpy.data.meshes.new('Wall check');data.from_pydata(vertices,[],faces);data.update()
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
 holes=sum(not e.is_manifold for e in bm.edges);flipped=sum(e.is_manifold and not e.is_contiguous for e in bm.edges);volume=bm.calc_volume(signed=True)
 checks.append({'name':name,'open_or_nonmanifold_edges':holes,'inconsistent_edges':flipped,'volume_m3':round(volume,3)})
 bm.free();bpy.data.meshes.remove(data)
 assert holes==0 and flipped==0 and volume>0,checks[-1]
for obj in objects:
 if obj.name.startswith(('Closed rear cliff','Closed distant lavender ridge','Closed irregular perimeter')):check(obj.name,[obj])
for name in ('Middle terrace','Windmill terrace'):
 check(name,[bpy.data.objects[name+' weathered cut face'],bpy.data.objects[name+' grassy top']])
for name in ('Lower right climb','Upper right climb'):
 check(name,[bpy.data.objects[name+' grassy walkable slope'],bpy.data.objects[name+' earth shoulders']])
for obj in objects:
 if obj.name.startswith('Irregular side rock'):
  suffix=obj.name.removeprefix('Irregular side rock');check(obj.name,[obj,bpy.data.objects['Uneven grassy rock rim'+suffix]])
wall=bpy.data.objects['Closed irregular perimeter'];tree=BVHTree.FromPolygons([wall.matrix_world@v.co for v in wall.data.vertices],[tuple(p.vertices) for p in wall.data.polygons])
ray_checks=0
for angle in range(0,360,2):
 if 260<=angle<=280:continue # intentional south entrance
 direction=Vector((math.cos(math.radians(angle)),math.sin(math.radians(angle)),0));origin=Vector((0,0,1.65))
 for start,travel in [(origin,direction),(origin+direction*100,-direction)]:
  hit,normal,_,_=tree.ray_cast(start,travel,110)
  assert hit is not None and normal.dot(travel)<-.001,(angle,normal)
  ray_checks+=1
(root/'Documentation/village-wall-checks.json').write_text(json.dumps({'closed_shells':checks,'inside_and_outside_visibility_rays':ray_checks,'intentional_opening':'8m south entrance','limits':'Blender topology and normals checks; Unity/headset not available.'},indent=2)+'\n')
scene=bpy.context.scene;scene.use_nodes=False;scene.cycles.samples=24
scene.render.resolution_x=1280;scene.render.resolution_y=720
camera=scene.camera
for filename,pos,target in [('village-walls-inside.png',(0,-24,3),(0,20,11)),('village-walls-outside.png',(80,85,60),(0,16,5))]:
 camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=24
 scene.render.filepath=str(root/'Documentation'/filename);bpy.ops.render.render(write_still=True)
print('PASS:',len(checks),'closed wall shells;',ray_checks,'inside/outside visibility checks')
