"""Render the bellroot prologue art used while the native game loads."""
import bpy,math
from pathlib import Path
from mathutils import Vector, Quaternion
from PIL import Image
root=Path(__file__).resolve().parents[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
src=root/'Blender/Bellwake/Wayfarer.blend'
with bpy.data.libraries.load(str(src)) as (a,b):
    b.collections=list(a.collections)
collections={c.name:c for c in b.collections}
order=['Bellrunner','RunnerHead','LanternMoth','GroveBank','Bellroot','TollSword','FerryShield','ReedStaff','RillBeetle','MireSkipper','Waystall','MarketPear']
sc=bpy.context.scene
def place(key,loc,rot=0,scale=1):
    c=collections[key];i=order.index(key)
    c.instance_offset=(5*(i%3),5*(i//3),0)
    obj=bpy.data.objects.new(key+' sitting',None)
    sc.collection.objects.link(obj);obj.instance_type='COLLECTION';obj.instance_collection=c
    obj.location=loc;obj.rotation_euler.z=rot;obj.scale=(scale,)*3
place('GroveBank',(0,0,0),0,1.25)
place('Bellroot',(-.98,.35,0),.2,.75)
place('Bellrunner',(1.02,-.48,.37),-.40)
place('RunnerHead',(1.02,-.48,.5),-.40)
# Reuse the articulated player's hands and forearms for the character in the painting.
for part in ['LeftPalm','RightPalm','RunnerArm']:
    c=bpy.data.collections.new(part)
    with bpy.data.libraries.load(str(src.with_name(part+'.blend'))) as (a,b):
        b.objects=list(a.objects)
    for o in b.objects:
        if o.type=='MESH' and o.get('batch')=='Set':c.objects.link(o)
    collections[part]=c
def limb(key,offset,rotation,scale):
    yaw=Quaternion((0,0,1),-.40);o=bpy.data.objects.new(key+' pose',None)
    sc.collection.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=collections[key]
    o.location=Vector((1.02,-.48,.37))+yaw@offset
    o.rotation_mode='QUATERNION';o.rotation_quaternion=yaw@rotation;o.scale=scale
for side in [-1,1]:
    shoulder=Vector((side*.18,0,.12));hand=Vector((side*.24,-.095,-.18))
    limb('RunnerArm',(shoulder+hand)*.5,(shoulder-hand).to_track_quat('Z','Y'),(.8,.8,(shoulder-hand).length))
    limb('LeftPalm' if side<0 else 'RightPalm',hand,Quaternion((0,0,1),math.pi),(.8,)*3)
place('LanternMoth',(.61,-.44,.88),-.85)
cam=bpy.data.objects.new('Ledger illustration',bpy.data.cameras.new('Lens'));sc.collection.objects.link(cam);sc.camera=cam
cam.location=(2.67,-7.2,2.20);cam.rotation_euler=(Vector((-.25,0,1.23))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=42
sc.world=bpy.data.worlds.new('Dawn');sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.50,.48,.36,1);bg.inputs['Strength'].default_value=.65
env=sc.world.node_tree.nodes.new('ShaderNodeTexEnvironment')
env.image=bpy.data.images.load(str(root/'Assets/Resources/Bellwake/Skies/Bellmarket.jpg'))
sc.world.node_tree.links.new(env.outputs['Color'],bg.inputs['Color'])
for loc,power,col,size in [((-2,-4,6),580,(1,.84,.57),4),((3,-1,3),130,(.7,.86,1),2)]:
    light=bpy.data.lights.new('Daybreak','AREA');light.energy=power;light.color=col;light.shape='DISK';light.size=size
    obj=bpy.data.objects.new('Daybreak',light);sc.collection.objects.link(obj);obj.location=loc
    obj.rotation_euler=(Vector((0,0,.7))-obj.location).to_track_quat('-Z','Y').to_euler()
sc.render.engine='CYCLES';sc.cycles.samples=20;sc.cycles.use_denoising=False
sc.render.resolution_percentage=100;sc.render.resolution_x=750;sc.render.resolution_y=445
sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=91
dst=root/'Documentation/Bellwake/bellroot-waking.jpg'
sc.render.filepath=str(dst);bpy.ops.render.render(write_still=True)
im=Image.open(dst).convert('RGB').resize((256,152),Image.Resampling.BOX)
im.quantize(colors=112,method=Image.Quantize.MEDIANCUT).convert('RGB').save(root/'Assets/Resources/Bellwake/Letters/BellrootDawn.png')
