"""Rebuild Mossbell in Blender. One Blender unit = one metre.
Run: blender -b -t 8 --python Tools/create_village.py
Editable named components remain in the .blend; export copies are batched by material.
"""
import bpy, math, sys, random, json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[1];out=root/'Assets/Resources/Village';out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(root/'Tools'))
from village_textures import create, linear
from village_landform import Landform
from village_buildings import build_house
from village_paths import bake as bake_paths
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for coll in list(bpy.data.collections):
 if coll.name!='Collection':bpy.data.collections.remove(coll)
textures=create(root);rng=random.Random(762)
collections={}
for name in ['Terrain','Cottages','Landmarks','Trees','Details','Collision','Review']:
 coll=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(coll);collections[name]=coll
active='Terrain';solids=[];routes={};materials={};path_layout=[]
for name,image in textures.items():
 mat=bpy.data.materials.new(name);mat.use_nodes=True;nodes=mat.node_tree.nodes
 tex=nodes.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Linear'
 mat.node_tree.links.new(tex.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
 if name=='PathBlend':
  # Portable alpha shoulders reveal real ground; Unity uses a .5 cutout threshold.
  mat.node_tree.links.new(tex.outputs['Alpha'],nodes.get('Principled BSDF').inputs['Alpha'])
 nodes.get('Principled BSDF').inputs['Roughness'].default_value=1
 materials[name]=mat
for name in ['Arrival','Exit','BoundaryEast','Collision','CollisionTerrain']:
 mat=bpy.data.materials.new(name);mat.diffuse_color=(0,0,0,0);materials[name]=mat
scales={'Grass':.25,'DirtPath':.25,'HousePlaster':.5,'OchrePlaster':.5,'RoofTiles':.65,'RoofSlate':.65,'Wood':1,'Masonry':.5,'EarthCliff':.35,'Leaves':.7,'SailCloth':.5,'Mountain':.13,'Awning':.5,'Brass':.5,'SpringWater':.4}

def finish(o,name,material,solid=False):
 o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 collections[active].objects.link(o);o.data.materials.clear();o.data.materials.append(materials[material])
 if solid:solids.append(o)
 return o

def box(name,p,s,mat,solid=False):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.scale=s
 return finish(o,name,mat,solid)

def mesh(name,v,f,mat,solid=False):
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.update();o=bpy.data.objects.new(name,m)
 collections[active].objects.link(o);o.data.materials.append(materials[mat])
 if solid:solids.append(o)
 return o

def beam(name,a,b,width=.16,mat='Wood',solid=False):
 a,b=Vector(a),Vector(b);o=box(name,(a+b)*.5,(width,width,(b-a).length),mat,solid)
 o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o

def cone(name,p,r1,r2,h,mat,verts=8,solid=False):
 bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=r1,radius2=r2,depth=h,location=p)
 return finish(bpy.context.object,name,mat,solid)

def uv_project(o):
 """Metric planar islands, slope-correct roof UVs, consistent texels/metre.
 Face orientation derives from local axes so rotated cottages retain timber grain.
 Islands intentionally overlap for tile reuse; no auto-generated stretched cube UVs.
 """
 material=o.data.materials[0].name;scale=scales.get(material,.5)
 uv=o.data.uv_layers.active or o.data.uv_layers.new(name='MetricUV')
 if o.get('path_uv'):return
 for poly in o.data.polygons:
  scale=scales.get(o.data.materials[poly.material_index].name,.5)
  n=poly.normal
  if abs(n.z)>.7:u=Vector((1,0,0))
  else:u=Vector((0,0,1)).cross(n).normalized()
  u=(u-n*u.dot(n)).normalized();v=n.cross(u).normalized()
  # Preserve scale after object transform; rotation doesn't change lengths.
  for li in poly.loop_indices:
   p=o.data.vertices[o.data.loops[li].vertex_index].co
   p=Vector((p.x*o.scale.x,p.y*o.scale.y,p.z*o.scale.z))
   uv.data[li].uv=(p.x*.25,p.y*.25) if o.data.materials[poly.material_index].name=='VillageGround' else (p.dot(u)*scale,p.dot(v)*scale)

def ribbon(name,points,width=3):
 # Roads are material coverage on the single ground surface, never stacked strips.
 path_layout.append({'name':name,'points':[list(p) for p in points],'width':width})

def ramp(name,points,width=4.5):
 ribbon(name+' worn track',points,2.9)
 routes[name]=[(x,y,landform.sample(x,y)) for x,y,z in points]

def fence(name,points):
 # Place every post on the final ground, including irregular cliff shoulders.
 posts=[]
 for a,b in zip(points,points[1:]):
  a,b=Vector(a),Vector(b);count=max(1,math.ceil((b-a).length/1.7))
  for j in range(count):
   p=a.lerp(b,j/count);p.z=landform.sample(p.x,p.y);posts.append(p)
 p=Vector(points[-1]);p.z=landform.sample(p.x,p.y);posts.append(p)
 for p in posts:
  bottom=min(landform.sample(p.x+dx,p.y+dy) for dx in (-.085,.085) for dy in (-.085,.085))-.04
  top=p.z+1.1
  box(name+' post',(p.x,p.y,(bottom+top)/2),(.17,.17,top-bottom),'Wood',True)
 for a,b in zip(posts,posts[1:]):
  for h in (.4,.85):beam(name+' rail',a+Vector((0,0,h)),b+Vector((0,0,h)),.12,'Wood',True)

# One continuous landform joins both terraces and climbing paths.
landform=Landform(globals())
# Square is deliberately small, with irregular path shoulders.
ribbon('Entrance worn path',[(0,-32,.008),(0,-22,.008),(-1,-13,.008),(-1,-5,.008),(1,3,.008)],7)
ribbon('Left cottage track',[(-22,-3,.01),(-13,-4,.01),(-3,-3,.01),(1,3,.01)],3.2)
ribbon('Right cottage track',[(1,3,.014),(8,-1,.014),(16,-6,.014),(23,-7,.014)],3)
# Low stone steps left of the well: 3.2m rise over an 8m run.
for i in range(20):
 h=(i+1)*.16;y=i*.4
 box('Left hillside stair %02d'%i,(-10,y+.2,h/2),(3.2,.4,h),'Masonry',True)
# Real cap blocks are low, rather than monumental parapets.
for side in (-1,1):
 for i in range(20):
  h=(i+1)*.16
  box('Stair edging',(-10+side*1.78,i*.4+.2,h+.12),(.32,.4,.24),'Masonry',True)
routes['Left stair']=[(-10,i*.4+.2,(i+1)*.16) for i in range(20)]
ramp('Lower right climb',[(11,-1,0),(15,5,1.2),(14,9,2.1),(11,14,3.2),(9,15,3.2)])
ramp('Upper right climb',[(9,19,3.2),(17,18,4.0),(24,22,5.7),(25,28,7.0),(20,30,8.0)])
ribbon('Middle cottage approach',[(-10,8.35,3.212),(-9,11,3.212),(-5,11.6,3.212),(5,12,3.212),(9,19,3.212)],2.8)
ribbon('Bell approach',[(20,30,8.012),(18,29,8.012),(16.5,27.5,8.012),(16.5,25.5,8.012)],2.8)

routes['Entrance court']=[(0,-21,0),(-3,-6,0),(-5,-2,0),(-10,-1,0),(-10,0,.16)]
routes['Middle terrace connection']=[(-10,8,3.2),(-9,11,3.2),(-5,11.6,3.2),(5,12,3.2),(9,19,3.2)]
routes['Bell approach']=[(20,30,8),(18,29,8),(16.5,27.5,8),(16.5,25.5,8)]

bake_paths(landform,path_layout,root,materials,textures)

active='Cottages'
def house(*args,**kwargs):return build_house(globals(),*args,**kwargs)
house('Entrance west',-8.7,-16,7,7.5,3.05,angle=-8,rise=1.7,door_side=.16,roof='RoofSlate')
house('Entrance east',9.3,-14,7.5,8,3.25,angle=10,rise=1.9,door_side=.22)
house('Lower west',-20,-1,7,6.2,3.1,angle=-4,rise=1.6,plaster='OchrePlaster',porch=True)
house('Lower east',23,-3,6.5,6.5,3,angle=8,rise=1.6,roof='RoofSlate',porch=True)
house('Middle landmark',-3,17,8,6.7,3.1,3.2,-18,1.9)
house('Back terrace cottage',-18,22,6.6,6,2.9,3.2,8,1.55,plaster='OchrePlaster')

active='Landmarks'
# Mossbell's original landmark: an open timber bell pavilion with offset roofs.
# It shares the broad hilltop landmark role, not the reference windmill silhouette.
wx,wy,base=12,25.5,8.0
box('Bell pavilion stone plinth',(wx,wy,base+.33),(5.3,5.3,.74),'Masonry',True)
# Four full-width, closed treads meet the pavilion floor without a crawlspace.
for i in range(4):
 h=(i+1)*.175
 box('Bell pavilion approach step %02d'%i,(wx+3.85-i*.35,wy,base+h/2-.02),(.37,2.7,h+.04),'Masonry',True)
routes['Bell steps']=[(wx+4.2,wy,base)]+[(wx+3.85-i*.35,wy,base+(i+1)*.175) for i in range(4)]+[(wx+2.4,wy,base+.7)]
for dx in (-2.05,2.05):
 for dy in (-2.05,2.05):
  box('Bell pavilion oak upright',(wx+dx,wy+dy,base+3.5),(.34,.34,5.6),'Wood',True)
  box('Bell pavilion foot socket',(wx+dx,wy+dy,base+.78),(.55,.55,.35),'Masonry',True)
for dy in (-2.05,2.05):
 beam('Bell pavilion crosshead',(wx-2.3,wy+dy,base+6.2),(wx+2.3,wy+dy,base+6.2),.32,'Wood',True)
 for dx in (-1,1):beam('Bell pavilion diagonal',(wx+dx*2.05,wy+dy,base+4.3),(wx+dx*.8,wy+dy,base+6.15),.22)
for dx in (-2.05,2.05):beam('Bell pavilion side head',(wx+dx,wy-2.25,base+6.2),(wx+dx,wy+2.25,base+6.2),.28)
def hip_roof(label,x,y,z,w,d,rise,mat):
 v=[(x-w,y-d,z),(x+w,y-d,z),(x+w,y+d,z),(x-w,y+d,z),(x-.35,y,z+rise),(x+.35,y,z+rise)]
 mesh(label,v,[(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4),(3,2,1,0)],mat,True)
 for i in range(4):beam(label+' fascia',v[i],v[(i+1)%4],.18)
hip_roof('Bell pavilion broad hipped roof',wx,wy,base+6.4,3.0,3.05,2.1,'RoofSlate')
# Smaller off-centre roof cap gives a different silhouette from the cottages.
box('Bell pavilion lantern neck',(wx-.35,wy,base+8.55),(1.1,1.1,.8),'Wood',True)
hip_roof('Bell pavilion lantern cap',wx-.35,wy,base+8.95,.95,.95,.8,'RoofTiles')
beam('Bell weather vane stem',(wx-.35,wy,base+9.6),(wx-.35,wy,base+10.5),.07,'Brass')
mesh('Bell weather vane leaf',[(wx-.35,wy,base+10.1),(wx+.8,wy,base+10.4),(wx+.35,wy,base+10.0),(wx+.8,wy,base+9.9)],[(0,1,2),(0,2,3)],'Brass')
def bell(name,x,y,z,size):
 profile=[(.15,1.25),(.34,1.05),(.40,.48),(.53,.14),(.68,0),(.55,.02),(.43,.22),(.31,.88),(.10,1.03)]
 v=[(x+math.cos(i*math.tau/12)*r*size,y+math.sin(i*math.tau/12)*r*size,z+h*size) for r,h in profile for i in range(12)]
 f=[(j*12+i,j*12+(i+1)%12,(j+1)*12+(i+1)%12,(j+1)*12+i) for j in range(len(profile)-1) for i in range(12)]
 f.extend([tuple(range(11,-1,-1)),tuple(range(96,108))])
 mesh(name,v,f,'Brass')
 beam(name+' suspension',(x,y,z+1.2*size),(x,y,base+6.1),.09,'Wood')
 cone(name+' clapper',(x,y,z+.1*size),size*.11,size*.11,size*.4,'Wood',8)
for dx,z,size in [(-1.2,base+4.0,.6),(0,base+3.3,1.1),(1.2,base+4.0,.6)]:bell('Founders bell',wx+dx,wy-.8,z,size)
# A spring court beside the main path, with twin rectangular basins and a low canopy.
sx,sy=4.7,-1.5
for by in (-.7,.8):
 box('Spring basin base',(sx,sy+by,.15),(2.95,1.4,.3),'Masonry',True)
 for dx in (-1.35,1.35):box('Spring basin side',(sx+dx,sy+by,.55),(.25,1.4,.5),'Masonry',True)
 for dy in (-.6,.6):box('Spring basin end',(sx,sy+by+dy,.55),(2.45,.2,.5),'Masonry',True)
 box('Spring still water',(sx,sy+by,.57),(2.6,1.15,.035),'SpringWater',True)
for dx in (-1.8,1.8):
 box('Spring shelter post',(sx+dx,sy+.25,1.45),(.19,.19,2.9),'Wood',True)
 beam('Spring shelter brace',(sx+dx,sy+.25,2.1),(sx+dx*.65,sy+.25,2.9),.13)
hip_roof('Spring shelter tiled cap',sx,sy+.25,2.95,2.15,1.6,.7,'RoofTiles')
box('Spring back pump pier',(sx,sy+1.7,.9),(.7,.6,1.8),'Masonry',True)
beam('Spring brass spout',(sx,sy+1.7,1.35),(sx,sy+.9,1.35),.12,'Brass')
# Named empty for easy source-scene discovery; no flat reference backdrop is used.
active='Details'
fence('Middle west edge',[(-24,13,3.2),(-18,9.6,3.2),(-12.3,8.5,3.2)])
fence('Middle cottage edge',[(-7.8,8.5,3.2),(-2,7.5,3.2),(6.4,8.5,3.2),(9.4,11.8,3.2)])
fence('Bell west terrace edge',[(4,25,8.0),(7,22.8,8.0),(9,22,8.0)])
fence('Bell east terrace edge',[(18.6,24,8.0),(19.4,26,8.0)])
fence('West foreground fence',[(-5.1,-24,0),(-5.3,-21,0)])
fence('East cottage yard',[(16,-8,0),(16,-3,0),(22,-3,0)])
for x,y,s in [(17,-3,1),(18,-3,.8),(17,-2,1.1)]:
 box('Yard crate',(x,y,s*.45),(s,s,s*.9),'Wood',True)
 for sign in (-1,1):beam('Crate diagonal',(x-.4*s,y-.51*s,.1),(x+.4*s,y-.51*s,s*.85),.08)
for x,y,rot in [(-4,-8,0),(18,-6,.3),(20,-5,-.7)]:
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(x,y,.35));o=finish(bpy.context.object,'Brown garden bird body','Feathers');o.scale=(.23,.31,.24)
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.13,location=(x,y-.24,.62));finish(bpy.context.object,'Brown garden bird head','Feathers')
 cone('Garden bird russet tail',(x,y+.26,.45),.12,.015,.42,'Comb',4).rotation_euler.x=-.6;box('Brown garden bird beak',(x,y-.36,.61),(.09,.12,.06),'SailCloth')
 for dx in (-.09,.09):beam('Brown garden bird leg',(x+dx,y,-.01),(x+dx,y,.22),.035,'SailCloth')

# Craft yard furniture and small planted patches are original geometry.
for x,y in [(-14,-6),(20,1),(-6,3.5)]:
 box('Oak planter soil',(x,y,.2),(1.8,.7,.4),'DirtPath',True)
 for dy in (-.4,.4):box('Oak planter side',(x,y+dy,.25),(2,.12,.5),'Wood',True)
 for dx in (-.95,.95):box('Oak planter end',(x+dx,y,.25),(.12,.8,.5),'Wood',True)
 for i in range(8):
  px=x-.8+i*.22;py=y+rng.uniform(-.2,.2);h=rng.uniform(.35,.65)
  beam('Garden flower stem',(px,py,.38),(px,py,.38+h),.035,'Leaves')
  cone('Golden mossbell blossom',(px,py,.38+h),.13,.05,.12,'Petals',5)
# A handcart at the potter's yard; two wheels and an open plank bed.
cx,cy=17,-10
box('Craft cart storage base',(cx,cy,.32),(1.58,2.28,.64),'Wood',True)
box('Craft cart bed',(cx,cy,.65),(1.6,2.3,.15),'Wood',True)
for dx in (-.8,.8):
 box('Craft cart side',(cx+dx,cy,.98),(.12,2.3,.6),'Wood',True)
 wheel=cone('Craft cart solid wheel',(cx+dx*1.25,cy,.45),.48,.48,.12,'Wood',10,True);wheel.rotation_euler.y=math.pi/2
 beam('Craft cart handle',(cx+dx*.7,cy-.5,.65),(cx+dx*.7,cy-2.7,.7),.09,'Wood',True)
for y in (-1.1,1.1):box('Craft cart end',(cx,cy+y,.98),(1.7,.12,.6),'Wood',True)
for dx,dy in [(-.4,0),(.3,.5)]:
 cone('Potter fired crock',(cx+dx,cy+dy,1.12),.22,.28,.7,'OchrePlaster',8)
 cone('Potter crock dark opening',(cx+dx,cy+dy,1.475),.19,.19,.02,'WindowDark',8)
# Low benches leave the spring court's walking routes open.
for x,y in [(8,-5),(-17,5)]:
 box('Village resting bench',(x,y,.48),(2.0,.48,.13),'Wood',True)
 box('Bench solid stone seat base',(x,y,.22),(1.85,.43,.44),'Masonry',True)

active='Trees'
def tree(x,y,z,size,seed):
 rand=random.Random(seed)
 cone('Oak %s angular trunk'%seed,(x,y,z+size*1.5),size*.25,size*.12,size*3,'Wood',7,True)
 for i in range(3+seed%3):
  a=i*2.1+rand.random();p=Vector((x+math.cos(a)*size*.9,y+math.sin(a)*size*.9,z+size*(3+rand.uniform(-.2,.6))))
  beam('Oak branch',(x,y,z+size*1.8),p,size*.13,'Wood',True)
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=size*1.35,location=p)
  o=finish(bpy.context.object,'Oak %s green crown %s'%(seed,i),'Leaves');o.scale=(1,rand.uniform(.8,1.1),rand.uniform(.7,1.1))
  for vert in o.data.vertices:vert.co*=rand.uniform(.88,1.12)
tree_sites=[(-17,12,3.2,1.15,1),(17,33,8.0,1.05,2),(-26,-2,0,1.3,3),(28,10,0,1.0,4),(-12.8,25,3.2,1.1,5),(-23,6,0,.9,6),(30,-14,0,1.2,7)]
for values in tree_sites:tree(*values)

active='Terrain'
# One continuous rock enclosure prevents hideable seams between separate cliff blocks.
wall_path=[(-4,-34),(-18,-35),(-34,-30),(-37,-18),(-36,-5),(-38,9),(-36,23),(-37,39),(-29,51),(-14,54),(0,53),(15,55),(30,52),(42,42),(44,28),(43,14),(42,0),(42,-17),(36,-31),(19,-36),(4,-34)]
# Insert shared boundary vertices for a varied silhouette without disconnected rock slabs.
coarse_wall=list(wall_path);wall_path=[]
for a,b in zip(coarse_wall,coarse_wall[1:]):
 count=max(1,math.ceil(math.dist(a,b)/3))
 for i in range(count):wall_path.append((a[0]+(b[0]-a[0])*i/count,a[1]+(b[1]-a[1])*i/count))
wall_path.append(coarse_wall[-1])
(root/'Assets/Resources/VillageBoundary.json').write_text(json.dumps({'points':[{'x':x,'y':y} for x,y in coarse_wall]}))
v=[];f=[]
for i,(x,y) in enumerate(wall_path):
 outward=Vector((x,y-8)).normalized()*8
 height=7 if i in (0,len(wall_path)-1) else 15+2.5*math.sin(i*.61)+1.1*math.sin(i*1.9)
 v.extend([(x,y,-3),(x,y,height),(x+outward.x,y+outward.y,height+1.5),(x+outward.x,y+outward.y,-3)])
for i in range(len(wall_path)-1):
 k=i*4
 f.extend([(k,k+4,k+5,k+1),(k+1,k+5,k+6,k+2),(k+2,k+6,k+7,k+3),(k+3,k+7,k+4,k)])
f.extend([(0,1,2,3),tuple(range(len(v)-1,len(v)-5,-1))])
perimeter=mesh('Closed irregular perimeter',v,f,'EarthCliff',True)
perimeter.data.materials.append(materials['Grass'])
for i in range(len(wall_path)-1):perimeter.data.polygons[i*4+1].material_index=1
# Nonplanar wall tops must have the same explicit diagonals in render and physics.
bpy.context.view_layer.objects.active=perimeter
tri=perimeter.modifiers.new('Shared final perimeter triangles','TRIANGULATE')
bpy.ops.object.modifier_apply(modifier=tri.name)
for layer,depth in enumerate((70,95)):
 verts=[];faces=[]
 for i in range(17):
  x=-100+i*12.5;h=20+rng.random()*15+layer*5
  verts.extend([(x,depth,-3),(x,depth+10,h),(x,depth+24,-3)])
 for i in range(16):
  k=i*3;faces.extend([(k,k+3,k+4,k+1),(k+1,k+4,k+5,k+2),(k+2,k+5,k+3,k)])
 faces.extend([(0,1,2),(50,49,48)])
 mesh('Closed distant lavender ridge %s'%layer,verts,faces,'Mountain')

active='Details'
box('Arrival marker',(0,-21,.035),(.02,.02,.02),'Arrival')
box('Exit marker',(0,-32,.1),(.02,.02,.02),'Exit')
box('Boundary east basis marker',(1,-21,.035),(.02,.02,.02),'BoundaryEast')
for o in list(bpy.context.scene.objects):
 if o.type=='MESH':
  if not o.get('metric_uv_done'):uv_project(o)
  # Blender joins UV layers by name. One shared name prevents zero-filled UVs
  # when batching primitives, custom meshes and path strips into one material.
  if o.data.uv_layers.active:o.data.uv_layers.active.name='SurfaceUV'
# Check tree roots against terrain alone so a trunk cannot validate its own floating base.
bpy.context.view_layer.update()
terrain_vertices=[];terrain_faces=[]
for o in collections['Terrain'].objects:
 if o.type!='MESH':continue
 offset=len(terrain_vertices);terrain_vertices.extend(o.matrix_world@v.co for v in o.data.vertices)
 terrain_faces.extend(tuple(offset+i for i in p.vertices) for p in o.data.polygons)
terrain_bvh=BVHTree.FromPolygons(terrain_vertices,terrain_faces)
tree_checks=[]
for x,y,z,size,seed in tree_sites:
 hit,normal,_,_=terrain_bvh.ray_cast(Vector((x,y,z+30)),Vector((0,0,-1)),35)
 assert hit is not None and abs(hit.z-z)<.1 and normal.z>.5,('Tree root not on ground',seed,hit,z)
 tree_checks.append({'variant':seed,'root':[x,y,z],'ground_height_m':round(hit.z,3)})
# Build dedicated static collision with no leaves, windows, ropes or tiny ornaments.
active='Collision'
collision_copies=[]
for src in solids:
 obj=bpy.data.objects.new('Collision '+src.name,src.data.copy());obj.matrix_world=src.matrix_world.copy();collections['Collision'].objects.link(obj)
 obj.data.materials.clear();obj.data.materials.append(materials['CollisionTerrain' if src.name=='Unified village landform' else 'Collision'])
 for polygon in obj.data.polygons:polygon.material_index=0
 collision_copies.append(obj)
# Validate geometry support and clearance in Blender, not a substitute for headset testing.
bpy.context.view_layer.update()
verts=[];faces=[];owners=[]
for o in collision_copies:
 start=len(verts);verts.extend([o.matrix_world@v.co for v in o.data.vertices]);faces.extend([tuple(start+i for i in p.vertices) for p in o.data.polygons]);owners.extend([o.name]*len(o.data.polygons))
bvh=BVHTree.FromPolygons(verts,faces)
checks=[]
for label,pts in routes.items():
 if label not in ('Left stair','Bell steps'):
  dense=[]
  for a,b in zip(pts,pts[1:]):
   a,b=Vector(a),Vector(b);count=max(1,math.ceil((b-a).length/.2))
   for j in range(count):
    p=a.lerp(b,j/count);dense.append((p.x,p.y,landform.sample(p.x,p.y)))
  p=pts[-1];pts=dense+[(p[0],p[1],landform.sample(p[0],p[1]))]
 max_slope=0;fail=[];samples=0
 for a,b in zip(pts,pts[1:]):
  a,b=Vector(a),Vector(b);delta=b-a;run=Vector((delta.x,delta.y)).length;max_slope=max(max_slope,math.degrees(math.atan2(abs(delta.z),max(.001,run))))
  for j in range(max(2,math.ceil(run/.2))+1):
   p=a.lerp(b,j/max(2,math.ceil(run/.2)));samples+=1
   for dx,dy in [(0,0),(.24,0),(-.24,0),(0,.24),(0,-.24)]:
    origin=p+Vector((dx,dy,.45));hit,normal,index,dist=bvh.ray_cast(origin,Vector((0,0,-1)),1.0)
    if hit is None:fail.append('unsupported footprint at '+str(tuple(round(v,2) for v in p)))
    top,_,owner,_=bvh.ray_cast(p+Vector((dx,dy,.25)),Vector((0,0,1)),1.8)
    if top is not None:fail.append(owners[owner]+' footprint headroom at '+str(tuple(round(v,2) for v in p)))
   hit,normal,index,dist=bvh.ray_cast(p+Vector((0,0,.25)),Vector((0,0,1)),1.8)
   if hit is not None:fail.append(owners[index]+' headroom at '+str(tuple(round(v,2) for v in p)))
 if max_slope>40:fail.append('Walking slope exceeds 40 degrees: '+str(round(max_slope,2)))
 checks.append({'route':label,'samples':samples,'max_centerline_slope_degrees':round(max_slope,2),'issues':sorted(set(fail))})
if any(c['issues'] for c in checks):bpy.ops.wm.save_as_mainfile(filepath='/tmp/mossbell-audit.blend')
assert all(not c['issues'] for c in checks),checks
for o in collision_copies:o.hide_render=True;o.hide_set(True)
# OBJ copies carry metric UVs and are batched; editable source objects remain separate.
export=bpy.data.collections.new('Export temporary');bpy.context.scene.collection.children.link(export)
source=[o for o in bpy.context.scene.objects if o.type=='MESH' and o not in collision_copies]
for src in source+collision_copies:
 obj=bpy.data.objects.new(src.name,src.data.copy());export.objects.link(obj);obj.matrix_world=src.matrix_world.copy()
for material in materials:
 batch=[o for o in export.objects if o.data.materials[0].name==material]
 if not batch:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in batch:o.select_set(True)
 bpy.context.view_layer.objects.active=batch[0];bpy.ops.object.join();o=bpy.context.object;o.name=material
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bpy.ops.object.select_all(action='DESELECT')
for o in export.objects:o.select_set(True)
bpy.ops.wm.obj_export(filepath=str(out/'Mossbell.obj'),export_selected_objects=True,forward_axis='NEGATIVE_Z',up_axis='Y',export_materials=True)
mtl=out/'Mossbell.mtl';lines=[];ground_material=False
for line in mtl.read_text().splitlines():
 if line.startswith('newmtl '):
  ground_material=line.split()[1]=='VillageGround';lines.append(line)
  if ground_material:
   lines.extend(['map_Kd ../VillageTextures/Grass.png',
                 '# Wizzard_ground_dirt ../VillageTextures/DirtPath.png',
                 '# Wizzard_ground_mask ../VillageMasks/GroundPaths.png'])
 elif ground_material and line.startswith(('map_Kd ','map_d ')):continue
 elif line.startswith(('map_Kd ','map_d ')):lines.append(line.split()[0]+' ../VillageTextures/'+line.split()[-1])
 else:lines.append(line)
mtl.write_text('\n'.join(lines)+'\n')
export_triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in export.objects)
for o in list(export.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.data.collections.remove(export)
# Readable source collections, metric units, packed textures and named review cameras.
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
world=bpy.data.worlds.new('Soft blue daylight');world.use_nodes=True;scene.world=world
nodes=world.node_tree.nodes;links=world.node_tree.links;bg=nodes['Background'];bg.inputs[0].default_value=(.53,.63,.86,1);bg.inputs[1].default_value=.65
# Direction-based sky gradient and broad cloud patches, also visible in the source file.
coord=nodes.new('ShaderNodeTexCoord');sep=nodes.new('ShaderNodeSeparateXYZ');links.new(coord.outputs['Normal'],sep.inputs[0])
rampnode=nodes.new('ShaderNodeValToRGB');rampnode.color_ramp.elements[0].position=0;rampnode.color_ramp.elements[0].color=(.20,.27,.62,1);rampnode.color_ramp.elements[1].position=.7;rampnode.color_ramp.elements[1].color=(.06,.12,.65,1);skyheight=nodes.new('ShaderNodeMath');skyheight.operation='MULTIPLY';skyheight.inputs[1].default_value=-1;links.new(sep.outputs['Z'],skyheight.inputs[0]);links.new(skyheight.outputs[0],rampnode.inputs[0])
noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5;noise.inputs['Detail'].default_value=2;links.new(coord.outputs['Normal'],noise.inputs['Vector'])
cloud=nodes.new('ShaderNodeValToRGB');cloud.color_ramp.elements[0].position=.52;cloud.color_ramp.elements[1].position=.72;links.new(noise.outputs['Fac'],cloud.inputs[0])
mix=nodes.new('ShaderNodeMixRGB');links.new(cloud.outputs['Color'],mix.inputs[0]);links.new(rampnode.outputs[0],mix.inputs[1]);mix.inputs[2].default_value=(.8,.83,.9,1);links.new(mix.outputs[0],bg.inputs[0])
ambient=nodes.new('ShaderNodeBackground');ambient.inputs[0].default_value=(.65,.64,.54,1);ambient.inputs[1].default_value=.8
lightpath=nodes.new('ShaderNodeLightPath');worldmix=nodes.new('ShaderNodeMixShader');links.new(lightpath.outputs['Is Camera Ray'],worldmix.inputs[0]);links.new(ambient.outputs[0],worldmix.inputs[1]);links.new(bg.outputs[0],worldmix.inputs[2]);links.new(worldmix.outputs[0],nodes['World Output'].inputs['Surface'])
active='Review'
bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.name='Gentle afternoon sun';sun.rotation_euler=(.75,0,.4);sun.data.energy=2.5;sun.data.angle=.14
scene.render.engine='CYCLES';scene.cycles.samples=16 if '--draft' in sys.argv else 32;scene.cycles.use_denoising=False
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=0
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
cameras=[]
for name,pos,target in [('Entrance comparison',(0,-21,1.65),(0,10,3.8)),('Spring and terrace',(0,-9,2.3),(4.7,-1.5,1.7)),('Upper terrace overview',(22,25,11),(-6,-6,1.5)),('Layout overview',(57,-65,55),(0,6,3))]:
 bpy.ops.object.camera_add(location=pos);cam=bpy.context.object;cam.name=name;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=28;cam.data.sensor_width=36;cameras.append(cam)
scene.camera=cameras[0]
for window in bpy.context.window_manager.windows:
 for area in window.screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA'
   area.spaces.active.shading.type='MATERIAL'
# Local geometry fog uses compositor depth in Blender; Unity uses the same distance endpoints.
scene.use_nodes=True;scene.view_layers[0].use_pass_z=True
nodes=scene.node_tree.nodes;nodes.clear();links=scene.node_tree.links
rl=nodes.new('CompositorNodeRLayers');mapping=nodes.new('CompositorNodeMapRange');mapping.inputs['From Min'].default_value=35;mapping.inputs['From Max'].default_value=140;mapping.use_clamp=True;links.new(rl.outputs['Depth'],mapping.inputs['Value'])
# Keep the procedural sky, which is infinitely distant, out of geometry fog.
less=nodes.new('CompositorNodeMath');less.operation='LESS_THAN';less.inputs[1].default_value=500;links.new(rl.outputs['Depth'],less.inputs[0]);mult=nodes.new('CompositorNodeMath');mult.operation='MULTIPLY';links.new(mapping.outputs[0],mult.inputs[0]);links.new(less.outputs[0],mult.inputs[1])
fog=nodes.new('CompositorNodeMixRGB');links.new(mult.outputs[0],fog.inputs[0]);links.new(rl.outputs['Image'],fog.inputs[1]);fog.inputs[2].default_value=(linear(.55),linear(.56),linear(.70),1)
comp=nodes.new('CompositorNodeComposite');links.new(fog.outputs[0],comp.inputs[0])
report={'tree_ground_checks':tree_checks,'units':'metres','doors_m':{'height':2.12,'width':1.08},'stairs_m':{'rise':.16,'tread':.4,'width':3.2,'steps':20},'routes':checks,'export_triangles_including_collision':export_triangles,'visual_objects':len(source),'collision_objects':len(collision_copies),'uv':'metric face islands; single ground uses shared world-XY UVs at 4m repeat, with a united material mask','review_camera':{'position_blender':[0,-21,1.65],'target_blender':[0,10,3.8],'lens_mm':28,'sensor_width_mm':36,'vertical_fov_degrees':round(math.degrees(2*math.atan(36*9/16/(2*28))),4)},'limitations':['Blender geometry checks only; Unity import/physics and Quest headset traversal not executed.']}
(root/'Documentation/village-geometry-checks.json').write_text(json.dumps(report,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Blender/MossbellVillage.blend'))
for cam,filename in zip(cameras if '--no-render' not in sys.argv else [],['mossbell-street.png','mossbell-spring.png','mossbell-terrace.png','mossbell-village.png']):
 scene.camera=cam;scene.use_nodes=cam.name!='Layout overview'
 scene.render.filepath=str(root/'Documentation'/filename);bpy.ops.render.render(write_still=True)
print('PASS: editable Blender source, UV OBJ, dedicated collision and route checks; '+('renders skipped (--no-render)' if '--no-render' in sys.argv else 'four comparison views rendered'))
