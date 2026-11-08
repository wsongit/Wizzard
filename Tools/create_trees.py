"""Generate eight original, flat-shaded tree models and a comparison render."""
import bpy, math, random
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
out=root/'Assets/Resources/Trees'; out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,color):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); return m
bark=mat('Bark',(.29,.21,.13))
leaves=[mat('Leaves'+str(i),c) for i,c in enumerate([(.30,.82,.035),(.32,.86,.04),(.29,.80,.03),(.34,.88,.045)])]
profiles=[('Round',5.5,2.2,5),('Tall',7.5,1.8,5),('Wide',5.0,3.0,6),('Leaning',6.0,2.2,5),('Forked',6.5,2.3,6),('Young',4.3,1.5,4),('Old',6.2,2.9,7),('Asymmetric',6.0,2.1,6)]
def branch(name,a,b,r1,r2):
    d=Vector(b)-Vector(a)
    bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=r1,radius2=r2,depth=d.length,location=(Vector(a)+Vector(b))/2)
    obj=bpy.context.object; obj.name=name; obj.rotation_euler=d.to_track_quat('Z','Y').to_euler(); obj.data.materials.append(bark); return obj
all_trees=[]
for index,(name,height,width,count) in enumerate(profiles):
    rng=random.Random(412+index); pieces=[]
    lean=.65 if index==3 else (.35 if index==7 else .05)
    fork=(lean,0,height*.45)
    pieces.append(branch('Trunk', (0,0,0),fork,.23 if index!=6 else .34,.13))
    pieces.append(branch('TrunkTip',fork,(lean*1.4,0,height*.85),.13,.055))
    for j in range(count):
        angle=j*math.tau/count+rng.uniform(-.3,.3)
        spread=width*rng.uniform(.45,.8)
        x=lean+math.cos(angle)*spread; y=math.sin(angle)*spread
        z=height*rng.uniform(.69,.9)
        if index==7 and j<3: x+=.8
        start=(fork[0],0,height*(.34+j*.025))
        pieces.append(branch('Branch',start,(x,y,z),.10,.035))
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(x,y,z))
        crown=bpy.context.object; crown.name='Crown'
        for v in crown.data.vertices: v.co*=rng.uniform(.82,1.14)
        crown.scale=(width*rng.uniform(.56,.76),width*rng.uniform(.55,.75),height*rng.uniform(.20,.28))
        for material in leaves: crown.data.materials.append(material)
        for face in crown.data.polygons: face.material_index=rng.randrange(len(leaves)); face.use_smooth=False
        pieces.append(crown)
    # Bake transforms and merge by surface type: two meshes per tree, with flat normals.
    merged=[]
    groups={g:[o for o in pieces if o.name.startswith('Crown')==(g=='Crown')] for g in ('Trunk','Crown')}
    for group in ('Trunk','Crown'):
        bpy.ops.object.select_all(action='DESELECT')
        selected=groups[group]
        for o in selected: o.select_set(True)
        bpy.context.view_layer.objects.active=selected[0]; bpy.ops.object.join()
        obj=bpy.context.object; obj.name=group
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        merged.append(obj)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in merged: obj.select_set(True)
    bpy.ops.wm.obj_export(filepath=str(out/f'Tree{index+1:02d}.obj'),export_selected_objects=True,forward_axis='NEGATIVE_Z',up_axis='Y',export_materials=True)
    offset=Vector(((index%4)*10,(index//4)*12,0))
    for obj in merged: obj.location+=offset
    all_trees.extend(merged)
# Save a reusable source scene and render a gallery.
world=bpy.data.worlds.new('Gallery'); world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.77,.71,1); world.node_tree.nodes['Background'].inputs[1].default_value=.8; bpy.context.scene.world=world
bpy.ops.mesh.primitive_plane_add(size=200,location=(15,6,-.04)); bpy.context.object.data.materials.append(mat('Ground',(.72,.69,.62)))
bpy.ops.object.light_add(type='AREA',location=(5,-12,30)); bpy.context.object.data.energy=6000; bpy.context.object.data.shape='DISK'; bpy.context.object.data.size=20
bpy.ops.object.camera_add(location=(36,-43,32)); camera=bpy.context.object; camera.rotation_euler=(Vector((15,6,3))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=48
scene=bpy.context.scene; scene.camera=camera; scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.cycles.use_denoising=False
scene.render.resolution_x=1400; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.filepath=str(root/'Documentation/tree-variants.png')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Blender/TreeVariants.blend'))
bpy.ops.render.render(write_still=True)
for i in range(1,9):
    text=(out/f'Tree{i:02d}.obj').read_text()
    count=profiles[i-1][3]
    assert text.count('\nf ')==count*80+(count+2)*9
    assert '\no Trunk' in text and '\no Crown' in text
print('PASS: eight exported tree models with trunk and crown meshes')
