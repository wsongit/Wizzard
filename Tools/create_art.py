"""Run: blender -b --python Tools/create_art.py (from the repository root)."""
import bpy, math, random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'Assets'/'Art'; RES=ROOT/'Assets'/'Resources'
ART.mkdir(exist_ok=True); RES.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def material(name,color):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*color,1)
    m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.95
    return m
fur=material('Warm clay fur',(.38,.21,.11)); skin=material('Golden muzzle',(.64,.44,.22))
rock=material('Weathered limestone',(.35,.37,.28)); bark=material('Dark bark',(.22,.12,.05))
leaf=material('Olive canopy',(.22,.34,.07))
def ico(name,position,scale,mat,sub=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=position)
    o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(mat); return o
# Export just the animated torso. Unity supplies tracked hands and arm segments.
parts=[ico('Chest',(0,0,0),(.30,.21,.37),fur,2),
       ico('Left shoulder',(-.27,0,.17),(.16,.18,.18),fur),
       ico('Right shoulder',(.27,0,.17),(.16,.18,.18),fur),
       ico('Belly',(0,-.17,-.06),(.22,.06,.23),skin,2)]
bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join(); torso=bpy.context.object; torso.name='GorillaTorso'
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
bpy.ops.wm.obj_export(filepath=str(RES/'GorillaTorso.obj'),export_selected_objects=True,
                     forward_axis='NEGATIVE_Z',up_axis='Y',export_materials=True)
# Original pixel texture, not ripped from a Nintendo game.
rng=random.Random(641997); image=bpy.data.images.new('Meadow grass 32px',width=32,height=32)
pixels=[]
for i in range(1024):
    t=rng.random(); c=(.26,.36,.10) if t<.13 else (.53,.61,.23) if t>.84 else (.40,.51,.16)
    pixels.extend((*c,1))
image.pixels=pixels; image.filepath_raw=str(ART/'grass32.png'); image.file_format='PNG'; image.save()
mat=material('N64 meadow',(.4,.51,.16)); nodes=mat.node_tree.nodes
tex=nodes.new('ShaderNodeTexImage'); tex.image=image; tex.interpolation='Closest'; tex.extension='REPEAT'
mat.node_tree.links.new(tex.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
def height(x,z):
    edge=max(abs(x),abs(z)); t=max(0,min(1,(edge-840)/184)); t=t*t*(3-2*t)
    return 5*math.sin(x*.012)*math.cos(z*.009)+2.5*math.sin(x*.027+z*.018)+7*math.exp(-((x-115)**2+(z-95)**2)/18000)+100*t
verts=[]; faces=[]
for z in range(257):
    for x in range(257):
        px=x*8-1024; pz=z*8-1024; verts.append((px,pz,height(px,pz)))
for z in range(256):
    for x in range(256):
        i=z*257+x; faces.extend(((i,i+1,i+257),(i+1,i+258,i+257)))
mesh=bpy.data.meshes.new('2048m meadow mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
obj=bpy.data.objects.new('2048m rolling meadow',mesh); bpy.context.collection.objects.link(obj); obj.data.materials.append(mat)
uv=mesh.uv_layers.new()
for poly in mesh.polygons:
    for idx in poly.loop_indices:
        v=verts[mesh.loops[idx].vertex_index]; uv.data[idx].uv=(v[0]/8,v[1]/8)
rng=random.Random(197)
for i in range(48):
    x=rng.uniform(-750,750); y=rng.uniform(-750,750)
    if math.hypot(x,y)<25: continue
    ico('Low stone',(x,y,height(x,y)+1.4),(3,3,2),rock)
    bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=.75,radius2=.5,depth=6,location=(x+9,y,height(x+9,y)+3))
    bpy.context.object.data.materials.append(bark)
    ico('Angular canopy',(x+9,y,height(x+9,y)+7),(5,5,4),leaf)
# Place a complete example avatar for the Blender preview.
h=height(0,0); torso.location=(0,0,h+1)
ico('Head',(0,0,h+1.63),(.23,.2,.24),fur,2)
ico('Muzzle',(0,-.17,h+1.56),(.16,.09,.1),skin,1)
black=material('Eyes',(.025,.018,.008))
for sign in [-1,1]:
    ico('Eye',(sign*.09,-.18,h+1.7),(.025,.025,.025),black)
    ico('Arm',(sign*.43,0,h+.77),(.15,.15,.36),fur)
    ico('Palm',(sign*.5,-.04,h+.42),(.14,.16,.13),skin)
world=bpy.data.worlds.new('Pale blue sky'); bpy.context.scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.52,.69,.8,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.8
bpy.ops.object.light_add(type='SUN',location=(0,0,50)); sun=bpy.context.object; sun.rotation_euler=(.45,-.6,-.4); sun.data.energy=2
bpy.ops.object.camera_add(location=(13,-23,9)); camera=bpy.context.object
camera.rotation_euler=(Vector((0,40,3))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.lens=24
scene=bpy.context.scene; scene.camera=camera; scene.render.engine='CYCLES'; scene.cycles.samples=16; scene.cycles.use_denoising=False
scene.render.resolution_x=1280; scene.render.resolution_y=720; scene.render.resolution_percentage=100
scene.view_settings.view_transform='Standard'
(ROOT/'Blender').mkdir(exist_ok=True)
image.pack(); bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Blender'/'LongMeadow.blend'))
scene.render.filepath=str(ROOT/'Documentation'/'meadow-preview.png')
bpy.ops.render.render(write_still=True)
print('ART_VALIDATED: terrain vertices',len(verts),'triangles',len(faces),'grass',image.size[:])
