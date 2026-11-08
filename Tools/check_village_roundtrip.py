"""Blender OBJ reimport check; validates portable export, not Unity physics/VR."""
import bpy
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'Blender/MossbellVillage.blend'))
for obj in list(bpy.context.scene.objects):
 if obj.type=='MESH':bpy.data.objects.remove(obj,do_unlink=True)
bpy.ops.wm.obj_import(filepath=str(root/'Assets/Resources/Village/Mossbell.obj'),forward_axis='NEGATIVE_Z',up_axis='Y')
objects=list(bpy.context.selected_objects);found=set()
for obj in objects:
 assert obj.data.uv_layers.active is not None,obj.name
 kind=obj.data.materials[0].name.split('.')[0];found.add(kind)
 if kind.startswith('Collision') or kind in ('Arrival','Exit','BoundaryEast'):obj.hide_render=True
 else:
  # Test the portable MTL references, not the source scene's packed texture nodes.
  textures=[node.image for node in obj.data.materials[0].node_tree.nodes if node.type=='TEX_IMAGE']
  assert textures and all(image.size[0]==64 and image.size[1]==64 for image in textures),kind
  if kind=='PathBlend':
   obj.visible_shadow=False
   alpha=list(textures[0].pixels)[3::4]
   assert min(alpha)<.01 and max(alpha)>.99,'Exported path lost its cutout mask'
 expected={'Arrival':(0,-21,.035),'Exit':(0,-32,.1),'BoundaryEast':(1,-21,.035)}
 if kind in expected:
  center=sum((obj.matrix_world@v.co for v in obj.data.vertices),Vector())/len(obj.data.vertices)
  assert (center-Vector(expected[kind])).length<.001,(kind,center)
assert {'Collision','CollisionTerrain','BoundaryEast','Arrival','Exit','RoofTiles','WindowDark','PathBlend'}<=found
scene=bpy.context.scene;scene.camera=bpy.data.objects['Entrance comparison'];scene.cycles.samples=16
scene.render.resolution_x=640;scene.render.resolution_y=360;scene.render.filepath=str(root/'Documentation/village-export-check.png')
bpy.ops.render.render(write_still=True)
print('PASS: OBJ reimport retained metric position, UV layers, material groups and portable 64px textures; preview rendered.')
