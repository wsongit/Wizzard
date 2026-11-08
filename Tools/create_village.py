"""Original village geometry; Blender coordinates use Z up, Unity export uses Y up."""
import bpy, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]; out=root/'Assets/Resources/Village'; out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,color):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); return m
materials={n:mat(n,c) for n,c in {'HousePlaster':(.65,.57,.38),'RoofTiles':(.43,.22,.12),'Wood':(.30,.18,.07),'Stone':(.40,.42,.30),'Grass':(.32,.42,.12),'Leaves':(.27,.51,.09),'Bark':(.24,.16,.08),'Arrival':(0,0,0),'Exit':(0,0,0)}.items()}
def cube(name,pos,scale,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(materials[material]);return o

def mesh(name,verts,faces,material):
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);o.data.materials.append(materials[material]);return o

def roof(x,y,z,w,d):
 v=[(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x-w/2,y+d/2,z),(x+w/2,y+d/2,z),(x,y-d/2,z+2),(x,y+d/2,z+2)]
 mesh('Gabled tiled roof',v,[(0,2,5,4),(4,5,3,1),(0,4,1),(2,3,5),(0,1,3,2)],'RoofTiles')

def house(x,y,w,d,h=4,base=0):
 cube('Plaster cottage',(x,y,base+h/2),(w,d,h),'HousePlaster');roof(x,y,base+h,w+1,d+1)
 cube('Timber door',(x,y-d/2-.035,base+1.1),(1.3,.08,2.2),'Wood')
 for dx in (-w*.29,w*.29):
  cube('Shutter',(x+dx,y-d/2-.08,base+2.4),(1,.12,1.2),'Wood')
  cube('Window sill',(x+dx,y-d/2-.16,base+1.75),(1.3,.35,.15),'Stone')
 for dx in (-w/2+.15,w/2-.15):cube('Corner beam',(x+dx,y-d/2-.1,base+h/2),(.22,.2,h),'Wood')
 cube('Chimney',(x+w*.25,y+1,base+h+1.6),(.8,.8,2.6),'Stone')
# Walkable base, upper terrace, continuous low steps and ochre paths.
cube('Village floor',(0,0,-.5),(136,150,1),'Grass')
cube('Upper terrace',(0,44,1),(116,48,2),'Stone')
cube('Upper lawn',(0,44,2.01),(115,47,.08),'Grass')
for i in range(20):cube('Terrace step',(0,8+i*.6,(i+1)*.05),(9,.62,(i+1)*.1),'Stone')
cube('Upper stair landing',(0,20,1),(9,1.2,2),'Stone')
cube('Entrance path',(0,-37,.035),(6,52,.07),'HousePlaster');cube('Well square',(0,-7,.05),(32,24,.1),'HousePlaster')
for x,y,w,d,h,b in [(-25,-37,9,8,4,0),(25,-35,11,9,4.5,0),(-28,-11,10,9,4,0),(27,-4,10,9,4,0),(-38,13,9,8,4,0),(37,11,11,9,4,0),(-29,35,12,10,4.5,2.05),(25,42,10,9,4,2.05),(0,52,16,12,5,2.05)]:house(x,y,w,d,h,b)
# Hollow stone well ring, roof and supports.
for i in range(12):
 a=i*math.tau/12;o=cube('Well rim',(math.cos(a)*2.2,-7+math.sin(a)*2.2,.7),(1.15,.5,1.4),'Stone');o.rotation_euler.z=a+math.pi/2
for x in (-2.5,2.5):cube('Well post',(x,-7,2.4),(.3,.3,4.8),'Wood')
roof(0,-7,4.8,7,5)
# Watchtower with crossbeams and a climbable ladder.
for x in (-2,2):
 for y in (-2,2):cube('Tower post',(33+x,-22+y,4),(.45,.45,8),'Wood')
cube('Tower deck',(33,-22,7.8),(5.6,5.6,.35),'Wood');roof(33,-22,10,7,7)
for x in (31,35):cube('Tower railing',(x,-22,9),(.2,5,1.5),'Wood')
for z in range(1,16):cube('Ladder rung',(33,-24.5,z*.5),(1.3,.18,.12),'Wood')
for x in (32.35,33.65):cube('Ladder rail',(x,-24.5,4),(.14,.2,8),'Wood')
# Garden patches and fences.
for x in (-40,-32,-24):
 cube('Garden soil',(x,53,2.11),(5,9,.12),'Bark')
 for y in range(50,58,2):cube('Vegetable row',(x,y,2.4),(4,.6,.5),'Leaves')
for x in range(-48,-15,3):cube('Fence post',(x,61,3),(.18,.18,2),'Wood')
for h in (2.6,3.3):cube('Fence rail',(-32,61,h),(34,.16,.16),'Wood')
# Faceted enclosing cliffs leave a clear south entrance.
for i in range(28):
 a=i*math.tau/28
 if math.sin(a)<-.92:continue
 x,y=math.cos(a)*76,math.sin(a)*82
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(x,y,6))
 o=bpy.context.object;o.name='Enclosing mountain';o.scale=(15,16,14+(i%3)*3);o.data.materials.append(materials['Stone'])
# Gate, path lamps, and meeting benches.
for x in (-5,5):cube('Gate pier',(x,-62,3),(2,3,6),'Stone')
cube('Gate lintel',(0,-62,6.2),(12,3,1),'Wood')
for x in (-11,11):
 cube('Village bench',(x,-13,.7),(4,1.4,.3),'Wood')
 for dx in (-1.4,1.4):cube('Bench leg',(x+dx,-13,.35),(.3,1,.7),'Wood')
cube('Arrival marker',(0,-52,.15),(.02,.02,.02),'Arrival')
cube('Exit marker',(0,-62,1.5),(.02,.02,.02),'Exit')
# Consolidate into one mesh per material: seven draw groups with shared collision.
objects=list(bpy.context.scene.objects)
groups={key:[o for o in objects if o.type=='MESH' and len(o.data.materials)>0 and o.data.materials[0]==material] for key,material in materials.items()}
for key,material in materials.items():
 selected=groups[key]
 if not selected:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name=key
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.obj_export(filepath=str(out/'Mossbell.obj'),export_selected_objects=True,forward_axis='NEGATIVE_Z',up_axis='Y',export_materials=True)
# Source and overview render.
world=bpy.data.worlds.new('Village sky');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.73,.8,1);world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.context.scene.world=world
bpy.ops.object.light_add(type='SUN');bpy.context.object.rotation_euler=(.5,-.4,-.5);bpy.context.object.data.energy=2
bpy.ops.object.camera_add(location=(125,-160,130));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=180
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Blender/MossbellVillage.blend'))
scene.render.filepath=str(root/'Documentation/mossbell-village.png');bpy.ops.render.render(write_still=True)
assert (out/'Mossbell.obj').stat().st_size>10000
print('PASS: village OBJ, source scene and preview generated')
