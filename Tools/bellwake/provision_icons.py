"""Render the four inventory stamps straight from the editable Wayfarer collection."""
import math, tempfile
from pathlib import Path
import bpy
from mathutils import Vector
from PIL import Image

root=Path(__file__).resolve().parents[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
names=['TollSword','FerryShield','ReedStaff','MarketPear']
with bpy.data.libraries.load(str(root/'Blender/Bellwake/Wayfarer.blend')) as (src,dst):
    dst.collections=list(names)
collections={c.name:c for c in dst.collections}
world=bpy.data.worlds.new('Printed light');scene.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.64,.66,.62,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
cam=bpy.data.objects.new('Item portrait',bpy.data.cameras.new('Orthographic'));scene.collection.objects.link(cam)
scene.camera=cam;cam.data.type='ORTHO'
for loc,power,color in [((-3,-4,6),540,(1,.89,.69)),((3,1,4),360,(.70,.83,1))]:
    light=bpy.data.lights.new('Studio lamp','AREA');light.energy=power;light.color=color;light.size=3
    obj=bpy.data.objects.new('Lamp',light);scene.collection.objects.link(obj);obj.location=loc
    obj.rotation_euler=(-Vector(loc)).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False
scene.render.resolution_x=scene.render.resolution_y=192;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.color_mode='RGBA'
atlas=Image.new('RGBA',(256,64))
with tempfile.TemporaryDirectory() as temp:
    for i,(name,index,span,height,roll) in enumerate(zip(names,[5,6,7,11],[.96,.54,1.23,.195],[.29,0,.23,.077],[-.52,.12,-.47,.15])):
        group=collections[name]
        group.instance_offset=(5*(index%3),5*(index//3),0)
        prop=bpy.data.objects.new(name+' pose',None);scene.collection.objects.link(prop)
        prop.instance_type='COLLECTION';prop.instance_collection=group
        cam.location=(.9,-4.8,1.12+height)
        target=Vector((0,0,height))
        cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        cam.rotation_euler.rotate_axis('Z',roll);cam.data.ortho_scale=span
        scene.render.filepath=str(Path(temp)/(name+'.png'));bpy.ops.render.render(write_still=True)
        portrait=Image.open(scene.render.filepath).convert('RGBA').resize((64,64),Image.Resampling.BOX)
        atlas.paste(portrait,(i*64,0));bpy.data.objects.remove(prop,do_unlink=True)
atlas.save(root/'Assets/Resources/Bellwake/Textures/ProvisionStamps.png',optimize=True)
