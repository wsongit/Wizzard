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
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for coll in list(bpy.data.collections):
 if coll.name!='Collection':bpy.data.collections.remove(coll)
textures=create(root);rng=random.Random(762)
collections={}
for name in ['Terrain','Cottages','Landmarks','Trees','Details','Collision','Review']:
 coll=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(coll);collections[name]=coll
active='Terrain';solids=[];routes={};materials={}
for name,image in textures.items():
 mat=bpy.data.materials.new(name);mat.use_nodes=True;nodes=mat.node_tree.nodes
 tex=nodes.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Linear'
 mat.node_tree.links.new(tex.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
 nodes.get('Principled BSDF').inputs['Roughness'].default_value=1
 materials[name]=mat
for name in ['Arrival','Exit','Collision']:
 mat=bpy.data.materials.new(name);mat.diffuse_color=(0,0,0,0);materials[name]=mat
scales={'Grass':.25,'DirtPath':.25,'HousePlaster':.5,'RoofTiles':.5,'Wood':1,'Masonry':.5,'EarthCliff':.2,'Leaves':.4,'SailCloth':.5,'Mountain':.07}

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
  n=poly.normal
  if abs(n.z)>.7:u=Vector((1,0,0))
  else:u=Vector((0,0,1)).cross(n).normalized()
  u=(u-n*u.dot(n)).normalized();v=n.cross(u).normalized()
  # Preserve scale after object transform; rotation doesn't change lengths.
  for li in poly.loop_indices:
   p=o.data.vertices[o.data.loops[li].vertex_index].co
   p=Vector((p.x*o.scale.x,p.y*o.scale.y,p.z*o.scale.z))
   uv.data[li].uv=(p.dot(u)*scale,p.dot(v)*scale)

def terrace(name,poly,height):
 # Inset top lip and broken two-stage cut face; no rectangular arena platform.
 cx=sum(p[0] for p in poly)/len(poly);cy=sum(p[1] for p in poly)/len(poly)
 v=[]
 for ring,z in [(1.04,-.08),(1.02,height*.48),(1,height-.12)]:
  for x,y in poly:v.append((cx+(x-cx)*ring,cy+(y-cy)*ring,z))
 n=len(poly);f=[]
 for j in range(2):
  for i in range(n):k=j*n+i;q=j*n+(i+1)%n;f.append((k,q,q+n,k+n))
 mesh(name+' weathered cut face',v,f,'EarthCliff',True)
 mesh(name+' grassy top',[(x,y,height) for x,y in poly],[tuple(range(n))],'Grass',True)
 # A thin uneven moss band at the very top of the cut.
 vv=[(x,y,height+.012) for x,y in poly]+[(x,y,height-.16-.09*math.sin(i*2.4)) for i,(x,y) in enumerate(poly)]
 mesh(name+' grass fringe',vv,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'Grass')

def ribbon(name,points,width=3,mat='PathBlend',solid=False):
 points=[Vector(p) for p in points];v=[];dist=0;uvs=[]
 for i,p in enumerate(points):
  t=points[min(i+1,len(points)-1)]-points[max(0,i-1)];t.z=0;t.normalize();side=Vector((t.y,-t.x,0))*width/2
  if i:dist+=(p-points[i-1]).length
  v.extend([tuple(p-side),tuple(p),tuple(p+side)]);uvs.extend([(0,dist*.25),(.5,dist*.25),(1,dist*.25)])
 o=mesh(name,v,[(i*3+j,i*3+j+1,i*3+j+4,i*3+j+3) for i in range(len(points)-1) for j in range(2)],mat,solid)
 uv=o.data.uv_layers.new(name='PathUV')
 for loop in o.data.loops:uv.data[loop.index].uv=uvs[loop.vertex_index]
 o['path_uv']=True
 if mat=='PathBlend':o.visible_shadow=False
 return o

def ramp(name,points,width=4.5):
 o=ribbon(name+' grassy walkable slope',points,width,'Grass',True)
 # The route sits on earth, not a suspended strip. Side faces are continuous.
 v=[tuple(a.co) for a in o.data.vertices];n=len(v);v.extend([(x,y,-.08) for x,y,z in v])
 faces=[]
 for i in range(0,n-3,3):faces.extend([(i,i+3,i+3+n,i+n),(i+2,i+2+n,i+5+n,i+5)])
 mesh(name+' earth shoulders',v,faces,'EarthCliff',True)
 ribbon(name+' worn track',[(x,y,z+.012) for x,y,z in points],2.9)
 routes[name]=points

def fence(name,points):
 for i in range(len(points)-1):
  a,b=Vector(points[i]),Vector(points[i+1]);length=(b-a).length;count=max(1,math.ceil(length/2))
  for j in range(count):
   p=a.lerp(b,j/count);box(name+' post',p+Vector((0,0,.55)),(.17,.17,1.1),'Wood',True)
  for h in (.4,.85):beam(name+' rail',a+Vector((0,0,h)),b+Vector((0,0,h)),.12,'Wood',True)
 p=Vector(points[-1]);box(name+' end post',p+Vector((0,0,.55)),(.17,.17,1.1),'Wood',True)

# Compact entrance court and two separate terraced landforms.
mesh('Uneven village footprint',[(-35,-36,-.02),(33,-36,-.02),(36,14,-.02),(28,42,-.02),(-28,44,-.02),(-36,9,-.02)],[tuple(range(6))],'Grass',True)
terrace('Middle terrace',[(-25,13),(-18,9),(-13,8),(-7,8),(-2,7),(7,8),(11,14),(11,25),(-9,30),(-24,24)],3.2)
terrace('Windmill terrace',[(5,23),(9,21),(16,20),(20,24),(20,34),(12,39),(3,35),(1,29)],8.0)
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
ribbon('Middle cottage approach',[(-10,8,3.212),(-9,11,3.212),(-5,11.6,3.212),(5,12,3.212),(9,19,3.212)],2.8)
ribbon('Windmill approach',[(20,30,8.012),(18,26,8.012),(16,22,8.012),(12,21.8,8.012)],2.8)

routes['Entrance court']=[(0,-21,0),(-3,-6,0),(-5,-2,0),(-10,-1,0),(-10,0,.16)]
routes['Middle terrace connection']=[(-10,8,3.2),(-9,11,3.2),(-5,11.6,3.2),(5,12,3.2),(9,19,3.2)]
routes['Windmill approach']=[(20,30,8),(18,26,8),(16,22,8),(12,21.8,8)]

active='Cottages'
def house(label,x,y,w,d,h=3.1,base=0,angle=0,rise=1.8,door_side=.18):
 before=set(bpy.context.scene.objects)
 box(label+' plaster walls',(0,0,h/2),(w,d,h),'HousePlaster',True)
 box(label+' stone footing',(0,0,.2),(w+.12,d+.12,.4),'Masonry',True)
 # Solid pitched roof with thick eaves and proper outward normals.
 a=w/2+.42;b=d/2+.4;z=h+.05
 vv=[(-a,-b,z),(a,-b,z),(-a,b,z),(a,b,z),(0,-b,z+rise),(0,b,z+rise)]
 mesh(label+' roof planes',vv,[(0,4,5,2),(4,1,3,5)],'RoofTiles',True)
 mesh(label+' front gable',[(-w/2,-d/2,h),(w/2,-d/2,h),(0,-d/2,h+rise-.15)],[(0,1,2)],'HousePlaster',True)
 mesh(label+' rear gable',[(-w/2,d/2,h),(0,d/2,h+rise-.15),(w/2,d/2,h)],[(0,1,2)],'HousePlaster',True)
 for sy in (-1,1):
  yy=sy*b
  for sx in (-1,1):beam(label+' chunky bargeboard',(sx*a,yy,z),(0,yy,z+rise),.21,'Wood',True)
 for sx in (-1,1):beam(label+' eave',(sx*a,-b,z),(sx*a,b,z),.19,'Wood',True)
 # Timber on all facades, including the visible sides of foreground houses.
 for sy in (-1,1):
  yy=sy*(d/2+.035)
  for xx in (-w/2+.08,0,w/2-.08):box(label+' upright',(xx,yy,h/2),(.18,.15,h),'Wood')
  box(label+' header',(0,yy,h-.1),(w,.17,.22),'Wood')
  beam(label+' gable kingpost',(0,yy,h),(0,yy,h+rise-.16),.16)
  for sx in (-1,1):beam(label+' gable brace',(sx*(w/2-.14),yy,h),(0,yy,h+rise-.16),.16)
 for sx in (-1,1):
  xx=sx*(w/2+.035)
  box(label+' side header',(xx,0,h-.1),(.17,d,.22),'Wood')
  for yy in (-d/2+.1,0,d/2-.1):box(label+' side timber',(xx,yy,h/2),(.16,.18,h),'Wood')
 # Doors are full-scale; dark panel set behind a proud wooden frame.
 dx=w*door_side;front=-d/2-.05
 box(label+' recessed door',(dx,front,1.06),(1.08,.04,2.12),'Wood')
 for ox in (-.62,.62):box(label+' door jamb',(dx+ox,front-.07,1.1),(.15,.16,2.2),'Wood')
 box(label+' door lintel',(dx,front-.07,2.2),(1.4,.16,.18),'Wood')
 box(label+' threshold',(dx,front-.1,.065),(1.45,.45,.13),'Masonry',True)
 cone(label+' door latch',(dx+.35,front-.12,1.05),.055,.055,.08,'SailCloth',6).rotation_euler.x=math.pi/2
 def window(cx,cy,side=False):
  if side:
   box(label+' dark side window',(cx,cy,1.9),(.07,.86,.87),'WindowDark')
   for yy in (-.51,.51):box(label+' side window frame',(cx+math.copysign(.04,cx),cy+yy,1.9),(.14,.12,1.08),'Wood')
   for zz in (-.49,.49):box(label+' side sill',(cx,cy,1.9+zz),(.17,1.12,.12),'Wood')
   box(label+' side mullion',(cx,cy,1.9),(.16,.08,.9),'Wood')
  else:
   box(label+' dark window',(cx,cy,1.9),(.86,.07,.87),'WindowDark')
   for ox in (-.51,.51):box(label+' window frame',(cx+ox,cy-.05,1.9),(.12,.16,1.08),'Wood')
   for zz in (-.49,.49):box(label+' window sill',(cx,cy-.05,1.9+zz),(1.12,.18,.12),'Wood')
   for ox in (-.17,.17):box(label+' window bars',(cx+ox,cy-.08,1.9),(.055,.1,.86),'Wood')
   box(label+' window crossbar',(cx,cy-.08,1.9),(.86,.1,.06),'Wood')
 window(-w*.27,front-.04)
 for sx in (-1,1):
  for yy in (-d*.24,d*.24):window(sx*(w/2+.08),yy,True)
 # Subtle differing chimneys and off-centre doors break repeated fronts.
 box(label+' chimney',(w*.27,d*.2,h+rise*.6),(.58,.65,1.7),'Masonry',True)
 for o in set(bpy.context.scene.objects)-before:
  uv_project(o)
  # Bake scale first, then rotate the entire cottage around its own origin.
  o.data.transform(o.matrix_world);o.matrix_world.identity()
  from mathutils import Matrix
  o.data.transform(Matrix.Translation((x,y,base)) @ Matrix.Rotation(math.radians(angle),4,'Z'))
  o['metric_uv_done']=True
house('Entrance west',-8.7,-16,7,7.5,3.05,angle=-8,rise=1.7,door_side=.16)
house('Entrance east',9.3,-14,7.5,8,3.25,angle=10,rise=1.9,door_side=.22)
house('Lower west',-20,-1,7,6.2,3.1,angle=-4,rise=1.6)
house('Lower east',23,-3,6.5,6.5,3,angle=8,rise=1.6,door_side=.1)
house('Middle landmark',-3,17,8,6.7,3.1,3.2,-18,1.9)
house('Back terrace cottage',-18,22,6.6,6,2.9,3.2,8,1.55)

active='Landmarks'
# A squat stone windmill above and right of the middle cottage.
wx,wy,base=12,25.5,8.0
cone('Windmill stone tower',(wx,wy,base+3.75),3,2.6,7.5,'Masonry',12,True)
cone('Windmill simple roof',(wx,wy,base+8.05),2.65,.15,1.6,'RoofTiles',12,True)
box('Windmill recessed door',(wx,wy-2.98,base+1.05),(1.1,.09,2.1),'Wood')
for dx in (-.64,.64):box('Windmill door frame',(wx+dx,wy-3.0,base+1.1),(.15,.16,2.2),'Wood')
box('Windmill door lintel',(wx,wy-3.0,base+2.2),(1.45,.2,.18),'Wood')
hub=Vector((wx,wy-3.25,base+7.0))
cone('Windmill axle',hub,.25,.25,.65,'Wood',10).rotation_euler.x=math.pi/2
for blade in range(4):
 angle=math.radians(29)+blade*math.pi/2;direction=Vector((math.sin(angle),0,math.cos(angle)));side=Vector((math.cos(angle),0,-math.sin(angle)))
 beam('Windmill sail spar',hub,hub+direction*6.2,.16)
 # Broad weathered plank sails, with edge frames and cross battens.
 for j in range(9):
  distance=1.7+j*.5;mid=hub+direction*distance+side*.28
  plank=box('Windmill weathered sail plank',mid,(1.5,.12,.49),'SailCloth');plank.rotation_euler.y=angle
 for sign in (-1,1):beam('Windmill sail edging',hub+direction*1.5+side*(.28+sign*.79),hub+direction*6.2+side*(.28+sign*.79),.08)
# Low open stone well, 2.6m across, with a 2.8m beam.
well=(0,-1)
for i in range(12):
 a=i*math.tau/12;b=(i+1)*math.tau/12
 v=[(math.cos(t)*r,-1+math.sin(t)*r,z) for z in (0,.82) for r in (1.05,1.38) for t in (a,b)]
 mesh('Well stone rim segment',v,[(2,3,7,6),(1,0,4,5),(4,6,7,5),(0,1,3,2),(0,2,6,4),(3,1,5,7)],'Masonry',True)
for x in (-1.58,1.58):
 box('Well oak post',(x,-1,1.4),(.27,.28,2.8),'Wood',True)
 beam('Well diagonal brace',(x,-1,2.1),(x-math.copysign(.65,x),-1,2.7),.15)
box('Well oak crossbeam',(0,-1,2.72),(3.6,.3,.3),'Wood',True)
cone('Well hanging rope',(0,-1,1.65),.026,.026,1.85,'SailCloth',6)
cone('Dark well bottom',(0,-1,-.012),1.04,1.04,.01,'WindowDark',12)

active='Details'
fence('Middle west edge',[(-24,13,3.2),(-18,9.6,3.2),(-12.3,8.5,3.2)])
fence('Middle cottage edge',[(-7.8,8.5,3.2),(-2,7.5,3.2),(6.4,8.5,3.2),(9.4,11.8,3.2)])
fence('Windmill terrace edge',[(4,25,8.0),(7,22.8,8.0),(12,21.2,8.0),(17,21.4,8.0),(21,24.6,8.0)])
fence('West foreground fence',[(-5.1,-24,0),(-5.3,-21,0)])
fence('East cottage yard',[(16,-8,0),(16,-3,0),(22,-3,0)])
for x,y,s in [(17,-3,1),(18,-3,.8),(17,-2,1.1)]:
 box('Yard crate',(x,y,s*.45),(s,s,s*.9),'Wood',True)
 for sign in (-1,1):beam('Crate diagonal',(x-.4*s,y-.51*s,.1),(x+.4*s,y-.51*s,s*.85),.08)
for x,y,rot in [(-4,-8,0),(18,-6,.3),(20,-5,-.7)]:
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(x,y,.35));o=finish(bpy.context.object,'Chicken body','Feathers');o.scale=(.23,.31,.24)
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.13,location=(x,y-.24,.62));finish(bpy.context.object,'Chicken head','Feathers')
 box('Chicken comb',(x,y-.24,.75),(.08,.13,.1),'Comb');box('Chicken beak',(x,y-.36,.61),(.09,.12,.06),'SailCloth')
 for dx in (-.09,.09):beam('Chicken leg',(x+dx,y,.05),(x+dx,y,.22),.035,'SailCloth')

active='Trees'
def tree(x,y,z,size,seed):
 rand=random.Random(seed)
 cone('Oak %s angular trunk'%seed,(x,y,z+size*1.5),size*.25,size*.12,size*3,'Wood',7,True)
 for i in range(4):
  a=i*2.1+rand.random();p=Vector((x+math.cos(a)*size*.9,y+math.sin(a)*size*.9,z+size*(3+rand.uniform(-.2,.6))))
  beam('Oak branch',(x,y,z+size*1.8),p,size*.13,'Wood',True)
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=size*1.35,location=p)
  o=finish(bpy.context.object,'Oak %s olive crown %s'%(seed,i),'Leaves');o.scale=(1,rand.uniform(.8,1.1),rand.uniform(.7,1.1))
  for vert in o.data.vertices:vert.co*=rand.uniform(.88,1.12)
for values in [(-17,12,3.2,1.15,1),(23,34,8.0,1.05,2),(-26,-2,0,1.3,3),(28,10,0,1.0,4),(-22,30,3.2,1.1,5),(-29,18,0,.9,6),(30,-14,0,1.2,7)]:tree(*values)

active='Terrain'
# Broken rock formations with stepped/tilted rims; separate distant ridgelines.
for side in (-1,1):
 for j in range(7):
  x=side*((38 if side==1 else 32)+rng.uniform(-3,3));y=-18+j*9
  h=rng.uniform(12,21);w=rng.uniform(6,10);d=rng.uniform(7,11)
  poly=[(x-w*.5,y-d*.5),(x+w*.5,y-d*.4),(x+w*.6,y+d*.5),(x-w*.4,y+d*.6)]
  top=[(px+side*rng.uniform(1,4),py+rng.uniform(-1,1),h+rng.uniform(-2,2)) for px,py in poly]
  mesh('Irregular side rock',[(px,py,-.15) for px,py in poly]+top,[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)],'EarthCliff',True)
  mesh('Uneven grassy rock rim',top,[(0,1,2,3)],'Grass',True)
for j in range(9):
 x=-36+j*9;y=45+rng.uniform(-2,5);h=rng.uniform(11,17)
 v=[(x-6,y,-1),(x+6,y+2,-1),(x+5,y+3,h),(x-4,y+1,h+rng.uniform(-4,4)),(x-3,y+11,h+3),(x+5,y+12,h+2)]
 mesh('Broken rear cliff',v,[(0,1,2,3),(3,2,5,4)],'EarthCliff',True)
for layer,depth in enumerate((70,95)):
 verts=[]
 for i in range(17):
  x=-100+i*12.5;h=20+rng.random()*15+layer*5
  verts.extend([(x,depth,8),(x,depth+10,h)])
 mesh('Distant lavender ridge %s'%layer,verts,[(i*2,i*2+2,i*2+3,i*2+1) for i in range(16)],'Mountain')

active='Details'
box('Arrival marker',(0,-21,.035),(.02,.02,.02),'Arrival')
box('Exit marker',(0,-32,.1),(.02,.02,.02),'Exit')
for o in list(bpy.context.scene.objects):
 if o.type=='MESH':
  if not o.get('metric_uv_done'):uv_project(o)
  # Blender joins UV layers by name. One shared name prevents zero-filled UVs
  # when batching primitives, custom meshes and path strips into one material.
  if o.data.uv_layers.active:o.data.uv_layers.active.name='SurfaceUV'
# Build dedicated static collision with no leaves, windows, ropes or tiny ornaments.
active='Collision'
collision_copies=[]
for src in solids:
 obj=bpy.data.objects.new('Collision '+src.name,src.data.copy());obj.matrix_world=src.matrix_world.copy();collections['Collision'].objects.link(obj)
 obj.data.materials.clear();obj.data.materials.append(materials['Collision']);collision_copies.append(obj)
# Validate geometry support and clearance in Blender, not a substitute for headset testing.
bpy.context.view_layer.update()
verts=[];faces=[];owners=[]
for o in collision_copies:
 start=len(verts);verts.extend([o.matrix_world@v.co for v in o.data.vertices]);faces.extend([tuple(start+i for i in p.vertices) for p in o.data.polygons]);owners.extend([o.name]*len(o.data.polygons))
bvh=BVHTree.FromPolygons(verts,faces)
checks=[]
for label,pts in routes.items():
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
 checks.append({'route':label,'samples':samples,'max_centerline_slope_degrees':round(max_slope,2),'issues':sorted(set(fail))})
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
mtl=out/'Mossbell.mtl';mtl.write_text('\n'.join(line.split()[0]+' ../VillageTextures/'+line.split()[-1] if line.startswith('map_Kd ') else line for line in mtl.read_text().splitlines())+'\n')
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
scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=False
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=0
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
cameras=[]
for name,pos,target in [('Entrance comparison',(0,-21,1.65),(0,10,3.8)),('Well and terrace',(-4,-8,1.65),(5,20,7)),('Upper terrace overview',(18,30,8.45),(-2,-2,1.7)),('Layout overview',(57,-65,55),(0,6,3))]:
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
report={'units':'metres','doors_m':{'height':2.12,'width':1.08},'stairs_m':{'rise':.16,'tread':.4,'width':3.2,'steps':20},'routes':checks,'export_triangles_including_collision':export_triangles,'visual_objects':len(source),'collision_objects':len(collision_copies),'uv':'metric face islands; path strips use width-normalized U and 4m V repeat','review_camera':{'position_blender':[0,-21,1.65],'target_blender':[0,10,3.8],'lens_mm':28,'sensor_width_mm':36,'vertical_fov_degrees':round(math.degrees(2*math.atan(36*9/16/(2*28))),4)},'limitations':['Blender geometry checks only; Unity import/physics and Quest headset traversal not executed.']}
(root/'Documentation/village-geometry-checks.json').write_text(json.dumps(report,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Blender/MossbellVillage.blend'))
for cam,filename in zip(cameras if '--no-render' not in sys.argv else [],['mossbell-street.png','mossbell-well.png','mossbell-terrace.png','mossbell-village.png']):
 scene.camera=cam;scene.use_nodes=cam.name!='Layout overview'
 scene.render.filepath=str(root/'Documentation'/filename);bpy.ops.render.render(write_still=True)
print('PASS: editable Blender source, UV OBJ, dedicated collision and route checks; '+('renders skipped (--no-render)' if '--no-render' in sys.argv else 'four comparison views rendered'))
