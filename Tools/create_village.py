"""Original village geometry; Blender coordinates use Z up, Unity export uses Y up."""
import bpy, math, sys
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]; out=root/'Assets/Resources/Village'; out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
sys.path.insert(0,str(root/'Tools'))
from village_textures import create
textures=create(root)
def mat(name,color):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1);m.use_nodes=True
 if name in textures:
  nodes=m.node_tree.nodes;tex=nodes.new('ShaderNodeTexImage');tex.image=textures[name];tex.projection='BOX';tex.projection_blend=.15;tex.interpolation='Closest'
  coords=nodes.new('ShaderNodeTexCoord');scale=nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=.25 if name in ('Grass','EarthCliff','RoofTiles') else .2 if name in ('HousePlaster','DirtPath') else .5
  m.node_tree.links.new(coords.outputs['Object'],scale.inputs[0]);m.node_tree.links.new(scale.outputs[0],tex.inputs['Vector']);m.node_tree.links.new(tex.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
  if name=='WindowLight':
   m.node_tree.links.new(tex.outputs['Color'],nodes.get('Principled BSDF').inputs['Emission Color']);nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=.7
 else:m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*color,1)
 return m
materials={n:mat(n,c) for n,c in {'HousePlaster':(.65,.57,.38),'RoofTiles':(.43,.22,.12),'Wood':(.30,.18,.07),'Stone':(.40,.42,.30),'Grass':(.32,.42,.12),'Leaves':(.27,.51,.09),'Bark':(.24,.16,.08),'Masonry':(.39,.40,.31),'RoofSlate':(.22,.24,.32),'EarthCliff':(.46,.39,.24),'Brick':(.46,.24,.17),'DirtPath':(.45,.32,.15),'WindowLight':(1,.6,.05),'Feathers':(.8,.8,.7),'Comb':(.6,.05,.02),'SailCloth':(.7,.6,.4),'Arrival':(0,0,0),'Exit':(0,0,0)}.items()}
def cube(name,pos,scale,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(materials[material]);return o

def mesh(name,verts,faces,material):
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);o.data.materials.append(materials[material]);return o

def roof(x,y,z,w,d,material='RoofTiles'):
 v=[(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x-w/2,y+d/2,z),(x+w/2,y+d/2,z),(x,y-d/2,z+3),(x,y+d/2,z+3)]
 mesh('Gabled tiled roof',v,[(0,4,5,2),(4,1,3,5),(0,2,3,1)],material)
 mesh('Plaster gables',v,[(0,1,4),(2,5,3)],'HousePlaster')

def house(x,y,w,d,h=4,base=0):
 surface='HousePlaster'
 cube('Cottage walls',(x,y,base+h/2),(w,d,h),surface)
 cube('Stone foundation',(x,y,base+.25),(w+.2,d+.2,.5),'Masonry')
 roof(x,y,base+h,w+1,d+1,'RoofTiles')
 # Strong timber framing and warm inset windows.
 front=y-d/2-.14
 cube('Front crossbeam',(x,front,base+h-.15),(w,.22,.25),'Wood')
 cube('Front center beam',(x,front,base+h/2),(.25,.22,h),'Wood')
 cube('Gable center beam',(x,y-d/2-.56,base+h+1.5),(.25,.18,3),'Wood')
 for dx in (-w/2+.12,w/2-.12):cube('Corner beam',(x+dx,front,base+h/2),(.25,.22,h),'Wood')
 for side in (-1,1):
  beam=cube('Gable brace',(x+side*w/4,y-d/2-.56,base+h+1.5),((w*w/4+9)**.5,.2,.2),'Wood');beam.rotation_euler.y=side*math.atan2(3,w/2)
 cube('Timber door',(x,front-.03,base+1.15),(1.4,.12,2.3),'Wood')
 cube('Door handle',(x+.45,front-.13,base+1.1),(.12,.12,.15),'WindowLight')
 for dx in (-w*.28,w*.28):
  cube('Window frame',(x+dx,front,base+2.45),(1.45,.18,1.4),'Wood')
  cube('Window glass',(x+dx,front-.11,base+2.45),(1.18,.05,1.13),'WindowLight')
  cube('Window mullion',(x+dx,front-.15,base+2.45),(.09,.08,1.2),'Wood')
  cube('Window transom',(x+dx,front-.15,base+2.45),(1.2,.08,.09),'Wood')
 cube('Chimney',(x+w*.25,y+1,base+h+1.6),(.8,.8,2.6),'Stone')
# Walkable base, upper terrace, continuous low steps and ochre paths.
cube('Village floor',(0,0,-.5),(136,150,1),'Grass')
cube('Upper terrace',(0,44,2),(116,48,4),'Masonry')
cube('Upper lawn',(0,44,4.01),(115,47,.08),'Grass')
for i in range(40):cube('Terrace step',(0,i*.5,(i+1)*.05),(7,.52,(i+1)*.1),'Masonry')
cube('Upper stair landing',(0,20,2),(7,1.2,4),'Masonry')
for side in (-1,1):
 x=side*4
 v=[(x-.25,0,0),(x+.25,0,0),(x+.25,20,0),(x-.25,20,0),(x-.25,0,.6),(x+.25,0,.6),(x+.25,20,4.6),(x-.25,20,4.6)]
 mesh('Stair parapet',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)],'Masonry')
def path(points,width=4,z=.004):
 points=[Vector(p) for p in points];verts=[]
 for i,p in enumerate(points):
  tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized()
  side=Vector((-tangent.y,tangent.x))*width/2
  verts.extend([(p.x+side.x,p.y+side.y,z),(p.x-side.x,p.y-side.y,z)])
 mesh('Worn dirt path',verts,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(points)-1)],'DirtPath')
path([(0,-64),(0,-43),(-3,-25),(0,-8),(-3,0)])
path([(-18,-30),(-3,-25),(15,-28)],3,.005)
path([(-18,-7),(0,-8),(19,2)],3,.005)
path([(0,20),(-5,30),(-29,35)],3,4.07)
path([(-5,30),(20,29),(44,36)],3,4.08)
for i in range(12):
 a=i*math.tau/12;b=(i+1)*math.tau/12
 mesh('Well clearing',[(0,-7,.085),(math.cos(a)*10,-7+math.sin(a)*10,.085),(math.cos(b)*10,-7+math.sin(b)*10,.085)],[(0,1,2)],'DirtPath')
for x,y,w,d,h,b in [(-14,-35,9,8,4,0),(15,-32,11,9,4.5,0),(-18,-7,10,9,4,0),(19,4,10,9,4,0),(-38,13,9,8,4,0),(37,11,11,9,4,0),(-29,35,12,10,4.5,4.05),(25,42,10,9,4,4.05),(0,52,16,12,5,4.05)]:house(x,y,w,d,h,b)
# Hollow stone well ring, roof and supports.
for i in range(8):
 a=i*math.tau/8;o=cube('Well rim',(math.cos(a)*2.2,-7+math.sin(a)*2.2,.7),(1.8,.55,1.4),'Masonry');o.rotation_euler.z=a+math.pi/2
for x in (-2.5,2.5):cube('Well post',(x,-7,2.4),(.3,.3,4.8),'Wood')
cube('Well winch beam',(0,-7,4.6),(5.5,.3,.3),'Wood')
cube('Well winch',(0,-7,2.8),(4.6,.22,.22),'Wood')
bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.035,depth=2.1,location=(0,-7,1.6));bpy.context.object.name='Well rope';bpy.context.object.data.materials.append(materials['SailCloth'])
# Watchtower with crossbeams and a climbable ladder.
for x in (-2,2):
 for y in (-2,2):cube('Tower post',(33+x,-22+y,4),(.45,.45,8),'Wood')
cube('Tower deck',(33,-22,7.8),(5.6,5.6,.35),'Wood');roof(33,-22,10,7,7)
for x in (31,35):cube('Tower railing',(x,-22,9),(.2,5,1.5),'Wood')
for z in range(1,16):cube('Ladder rung',(33,-24.5,z*.5),(1.3,.18,.12),'Wood')
for x in (32.35,33.65):cube('Ladder rail',(x,-24.5,4),(.14,.2,8),'Wood')
# Garden patches and fences.
for x in (-40,-32,-24):
 cube('Garden soil',(x,53,4.11),(5,9,.12),'Bark')
 for y in range(50,58,2):cube('Vegetable row',(x,y,4.4),(4,.6,.5),'Leaves')
for x in range(-48,-15,3):cube('Fence post',(x,61,5),(.18,.18,2),'Wood')
for h in (4.6,5.3):cube('Fence rail',(-32,61,h),(34,.16,.16),'Wood')
# Tall earthy cut faces and a grassy ridge, with an opening to the south.
for i in range(32):
 a=i*math.tau/32;b=(i+1)*math.tau/32
 if math.sin((a+b)/2)<-.94:continue
 def edge(angle,radius,height):
  radius+=3*math.sin(angle*3)+2*math.sin(angle*7)
  return (math.cos(angle)*radius,math.sin(angle)*(radius+7),height)
 h1=17+3*math.sin(a*3);h2=17+3*math.sin(b*3)
 mesh('Earth cliff', [edge(a,67,-1),edge(b,67,-1),edge(a,67,h1),edge(b,67,h2)],[(0,2,3,1)],'EarthCliff')
 mesh('Grassy ridge',[edge(a,67,h1),edge(b,67,h2),edge(a,85,h1+6),edge(b,85,h2+6)],[(0,2,3,1)],'Grass')
# Stone windmill on Mossbell's eastern upper terrace, with four timber sails.
bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=4,radius2=2.9,depth=11,location=(44,36,9.55))
bpy.context.object.name='Windmill masonry';bpy.context.object.data.materials.append(materials['Masonry'])
bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=3.8,radius2=0,depth=3,location=(44,36,16.55))
bpy.context.object.name='Windmill cap';bpy.context.object.data.materials.append(materials['RoofSlate'])
cube('Windmill door',(44,31.95,5.2),(1.4,.12,2.3),'Wood')
for blade in range(4):
 angle=math.pi/4+blade*math.pi/2
 for offset in (-.65,.65):
  obj=cube('Sail spar',(44,31,14.5),(.12,.22,8),'Wood')
  obj.location=Vector((44,31,14.5))+Vector((math.sin(angle)*4+math.cos(angle)*offset,0,math.cos(angle)*4-math.sin(angle)*offset))
  obj.rotation_euler.y=angle
 for rung in range(3,9):
  obj=cube('Sail lattice',(44+math.sin(angle)*rung,31,14.5+math.cos(angle)*rung),(1.5,.15,.95),'SailCloth');obj.rotation_euler.y=angle
# Small fenced yard set away from the entrance and main route.
for x in range(-47,-30,2):cube('Yard post',(x,-22,1),(.18,.18,2),'Wood')
for y in range(-36,-21,2):cube('Yard post',(-47,y,1),(.18,.18,2),'Wood')
for h in (.65,1.35):
 cube('Yard rail',(-39,-22,h),(16,.16,.18),'Wood')
 cube('Yard rail',(-47,-29,h),(.16,14,.18),'Wood')
# Gate, path lamps, and meeting benches.
for x in (-5,5):cube('Gate pier',(x,-62,3),(2,3,6),'Stone')
cube('Gate lintel',(0,-62,6.2),(12,3,1),'Wood')
for x in (-11,11):
 cube('Village bench',(x,-13,.7),(4,1.4,.3),'Wood')
 for dx in (-1.4,1.4):cube('Bench leg',(x+dx,-13,.35),(.3,1,.7),'Wood')
# Grass fringe and rails on the raised terrace; leave the stair opening clear.
for left,right in [(-53,-5),(5,53)]:
 cube('Moss coping',((left+right)/2,20.15,4.1),(right-left,.65,.22),'Grass')
 for x in range(left,right,3):cube('Terrace fence post',(x,20.5,4.9),(.18,.18,1.8),'Wood')
 for h in (4.55,5.25):cube('Terrace fence rail',((left+right)/2,20.5,h),(right-left,.15,.15),'Wood')
for x,y in [(24,-5),(25.5,-5),(24,-3.5)]:
 cube('Crate',(x,y,.6),(1.3,1.3,1.2),'Wood')
 for dx in (-.53,.53):cube('Crate edge',(x+dx,y-.67,.6),(.12,.1,1.2),'Bark')
 brace=cube('Crate brace',(x,y-.68,.6),(1.6,.1,.12),'Bark');brace.rotation_euler.y=.7
for x,y in [(9,-16),(11,-15),(-8,-3)]:
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(x,y,.4));o=bpy.context.object;o.scale=(.27,.36,.3);o.data.materials.append(materials['Feathers'])
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.17,location=(x,y-.27,.72));bpy.context.object.data.materials.append(materials['Feathers'])
 cube('Chicken comb',(x,y-.27,.9),(.1,.2,.12),'Comb');cube('Chicken beak',(x,y-.45,.71),(.1,.16,.07),'WindowLight')
 for dx in (-.1,.1):cube('Chicken foot',(x+dx,y-.05,.1),(.06,.2,.08),'WindowLight')
# Leafy accents near the square and terrace, clear of the entrance and staircase.
for x,y,base in [(9,11,0),(-12,35,4),(-38,-10,0)]:
 bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=.4,radius2=.2,depth=5,location=(x,y,base+2.5));bpy.context.object.data.materials.append(materials['Wood'])
 for dx,dy,dz in [(-1,0,0),(1,.4,.3),(0,-.7,1.3)]:
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=2.3,location=(x+dx,y+dy,base+5+dz));bpy.context.object.data.materials.append(materials['Leaves'])
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
 if key=='DirtPath':bpy.context.object.visible_shadow=False
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.obj_export(filepath=str(out/'Mossbell.obj'),export_selected_objects=True,forward_axis='NEGATIVE_Z',up_axis='Y',export_materials=True)
# Keep exported texture references portable between Linux and Windows.
mtl=out/'Mossbell.mtl'
mtl.write_text('\n'.join(line.split()[0]+' ../VillageTextures/'+line.split()[-1] if line.startswith(('map_Kd ','map_Ke ')) else line for line in mtl.read_text().splitlines())+'\n')
# Source and overview render.
world=bpy.data.worlds.new('Village sky');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.35,.48,.85,1);world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.context.scene.world=world
bpy.ops.object.light_add(type='SUN');bpy.context.object.rotation_euler=(.5,-.4,-.5);bpy.context.object.data.energy=2
bpy.ops.object.camera_add(location=(125,-160,130));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=180
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.cycles.use_denoising=False;scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Blender/MossbellVillage.blend'))
scene.render.filepath=str(root/'Documentation/mossbell-village.png');bpy.ops.render.render(write_still=True)
cam.data.type='PERSP';cam.data.lens=23
scene.render.resolution_x=1280;scene.render.resolution_y=720
for filename,position,target in [('mossbell-street.png',(0,-39,2.1),(10,18,5.5)),('mossbell-well.png',(-6,-14,2.1),(25,28,9))]:
 cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(root/'Documentation'/filename);bpy.ops.render.render(write_still=True)
assert (out/'Mossbell.obj').stat().st_size>10000
print('PASS: village OBJ, source scene and preview generated')
