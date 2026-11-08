"""Blender OBJ reimport check; validates portable export, not Unity physics/VR."""
import bpy,sys
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'Tools'))
from village_paths import surface_material
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
  for slot,material in enumerate(obj.data.materials):
   material_kind=material.name.split('.')[0];found.add(material_kind)
   if material_kind=='VillageGround':
    # Standard MTL has a grass fallback. Rebuild the shipped three-texture
    # shader from EXTERNAL PNG files, not the source scene's packed images.
    grass=bpy.data.images.load(str(root/'Assets/Resources/VillageTextures/Grass.png'),check_existing=False)
    dirt=bpy.data.images.load(str(root/'Assets/Resources/VillageTextures/DirtPath.png'),check_existing=False)
    mask=bpy.data.images.load(str(root/'Assets/Resources/VillageMasks/GroundPaths.png'),check_existing=False)
    mask.colorspace_settings.name='Non-Color'
    assert list(grass.size)==[64,64] and list(dirt.size)==[64,64] and list(mask.size)==[1024,1024]
    obj.data.materials[slot]=surface_material(grass,dirt,mask)
   else:
    textures=[node.image for node in material.node_tree.nodes if node.type=='TEX_IMAGE']
    assert textures and all(image.size[0]==64 and image.size[1]==64 for image in textures),material_kind
 expected={'Arrival':(0,-21,.035),'Exit':(0,-32,.1),'BoundaryEast':(1,-21,.035)}
 if kind in expected:
  center=sum((obj.matrix_world@v.co for v in obj.data.vertices),Vector())/len(obj.data.vertices)
  assert (center-Vector(expected[kind])).length<.001,(kind,center)
assert {'Collision','CollisionTerrain','BoundaryEast','Arrival','Exit','RoofTiles','WindowDark','VillageGround'}<=found
assert 'PathBlend' not in found
scene=bpy.context.scene;scene.camera=bpy.data.objects['Entrance comparison'];scene.cycles.samples=16
scene.render.resolution_x=640;scene.render.resolution_y=360;scene.render.filepath=str(root/'Documentation/village-export-check.png')
bpy.ops.render.render(write_still=True)
print('PASS: OBJ reimport retained metric position, UV layers, material groups, portable 64px tiles and external ground mask; preview rendered.')
