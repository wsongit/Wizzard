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
 if name=='PathBlend':
  # Portable alpha shoulders reveal real ground; Unity uses a .5 cutout threshold.
  mat.node_tree.links.new(tex.outputs['Alpha'],nodes.get('Principled BSDF').inputs['Alpha'])
 nodes.get('Principled BSDF').inputs['Roughness'].default_value=1
 materials[name]=mat
for name in ['Arrival','Exit','Collision']:
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
 for ring,z in [(1.04,-.08),(1.02,height*.48),(1,height)]:
  for x,y in poly:v.append((cx+(x-cx)*ring,cy+(y-cy)*ring,z))
 n=len(poly);f=[]
 for j in range(2):
  for i in range(n):k=j*n+i;q=j*n+(i+1)%n;f.append((k,q,q+n,k+n))
 f.append(tuple(reversed(range(n))))
 mesh(name+' weathered cut face',v,f,'EarthCliff',True)
 mesh(name+' grassy top',[(x,y,height) for x,y in poly],[tuple(range(n))],'Grass',True)
 # A thin uneven moss band at the very top of the cut.
 rim=[(cx+(x-cx)*1.001,cy+(y-cy)*1.001) for x,y in poly]
 vv=[(x,y,height+.012) for x,y in rim]+[(x,y,height-.16-.09*math.sin(i*2.4)) for i,(x,y) in enumerate(rim)]
 mesh(name+' grass fringe',vv,[(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)],'Grass')

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
 # A tiny rise separates overlapping landing surfaces and prevents coplanar flicker.
 points=[(x,y,z+.02) for x,y,z in points]
 o=ribbon(name+' grassy walkable slope',points,width,'Grass',True)
 # The route sits on earth, not a suspended strip. Side faces are continuous.
 v=[tuple(a.co) for a in o.data.vertices];n=len(v);v.extend([(x,y,-.08) for x,y,z in v])
 faces=[]
 for i in range(0,n-3,3):faces.extend([(i,i+3,i+3+n,i+n),(i+2,i+2+n,i+5+n,i+5)])
 faces.extend([(2,1,0,n,n+1,n+2),(n-3,n-2,n-1,2*n-1,2*n-2,2*n-3)])
 for i in range(0,n-3,3):
  for j in range(2):faces.append((i+n+j,i+n+j+3,i+n+j+4,i+n+j+1))
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
mesh('Uneven village footprint',[(-55,-46,-.02),(60,-46,-.02),(60,30,-.02),(55,68,-.02),(-55,68,-.02),(-55,9,-.02)],[tuple(range(6))],'Grass',True)
terrace('Middle terrace',[(-25,13),(-18,9),(-13,8),(-7,8),(-2,7),(7,8),(11,14),(11,25),(-9,30),(-24,24)],3.2)
terrace('Bell terrace',[(5,23),(9,21),(16,20),(20,24),(20,34),(12,39),(3,35),(1,29)],8.0)
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
ribbon('Bell approach',[(20,30,8.012),(18,26,8.012),(16,22,8.012),(12,21.8,8.012)],2.8)

routes['Entrance court']=[(0,-21,0),(-3,-6,0),(-5,-2,0),(-10,-1,0),(-10,0,.16)]
routes['Middle terrace connection']=[(-10,8,3.2),(-9,11,3.2),(-5,11.6,3.2),(5,12,3.2),(9,19,3.2)]
routes['Bell approach']=[(20,30,8),(18,26,8),(16,22,8),(12,21.8,8)]

active='Cottages'
def house(label,x,y,w,d,h=3.1,base=0,angle=0,rise=1.8,door_side=.18,roof='RoofTiles',plaster='HousePlaster',porch=False):
 before=set(bpy.context.scene.objects)
 box(label+' plaster walls',(0,0,h/2),(w,d,h),plaster,True)
 box(label+' stone footing',(0,0,.2),(w+.12,d+.12,.4),'Masonry',True)
 # Solid pitched roof with thick eaves and proper outward normals.
 a=w/2+.42;b=d/2+.4;z=h+.05
 vv=[(-a,-b,z),(a,-b,z),(-a,b,z),(a,b,z),(0,-b,z+rise),(0,b,z+rise)]
 mesh(label+' roof planes',vv,[(0,4,5,2),(4,1,3,5)],roof,True)
 mesh(label+' front gable',[(-w/2,-d/2,h),(w/2,-d/2,h),(0,-d/2,h+rise-.15)],[(0,1,2)],plaster,True)
 mesh(label+' rear gable',[(-w/2,d/2,h),(0,d/2,h+rise-.15),(w/2,d/2,h)],[(0,1,2)],plaster,True)
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
 # Split shutters and a doorstep canopy give each workshop a working facade.
 for sx in (-1,1):
  box(label+' hinged shutter',(-w*.27+sx*.70,front-.09,1.9),(.25,.10,.90),'Wood')
 if porch:
  yy=front-1.35
  for xx in (-w*.43,w*.43):
   box(label+' porch post',(xx,yy,1.25),(.14,.14,2.5),'Wood',True)
   beam(label+' porch bracket',(xx,yy,2.05),(xx,front,2.7),.12)
  mesh(label+' porch canopy',[(-w*.47,front-.05,2.85),(w*.47,front-.05,2.85),(w*.47,yy-.25,2.5),(-w*.47,yy-.25,2.5)],[(0,3,2,1)],'Awning')
  beam(label+' porch front beam',(-w*.47,yy,2.48),(w*.47,yy,2.48),.13)
 # A small original brass bell plaque identifies Mossbell's craft houses.
 cone(label+' craft plaque',(-w*.27,front-.13,2.72),.18,.18,.055,'Brass',6).rotation_euler.x=math.pi/2
 # Subtle differing chimneys and off-centre doors break repeated fronts.
 box(label+' chimney',(w*.27,d*.2,h+rise*.6),(.58,.65,1.7),'Masonry',True)
 for o in set(bpy.context.scene.objects)-before:
  uv_project(o)
  # Bake scale first, then rotate the entire cottage around its own origin.
  o.data.transform(o.matrix_world);o.matrix_world.identity()
  from mathutils import Matrix
  o.data.transform(Matrix.Translation((x,y,base)) @ Matrix.Rotation(math.radians(angle),4,'Z'))
  o['metric_uv_done']=True
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
box('Bell pavilion stone plinth',(wx,wy,base+.35),(5.3,5.3,.7),'Masonry',True)
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
 box('Spring still water',(sx,sy+by,.57),(2.6,1.15,.035),'SpringWater')
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
fence('Bell terrace edge',[(4,25,8.0),(7,22.8,8.0),(12,21.2,8.0),(17,21.4,8.0),(21,24.6,8.0)])
fence('West foreground fence',[(-5.1,-24,0),(-5.3,-21,0)])
fence('East cottage yard',[(16,-8,0),(16,-3,0),(22,-3,0)])
for x,y,s in [(17,-3,1),(18,-3,.8),(17,-2,1.1)]:
 box('Yard crate',(x,y,s*.45),(s,s,s*.9),'Wood',True)
 for sign in (-1,1):beam('Crate diagonal',(x-.4*s,y-.51*s,.1),(x+.4*s,y-.51*s,s*.85),.08)
for x,y,rot in [(-4,-8,0),(18,-6,.3),(20,-5,-.7)]:
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(x,y,.35));o=finish(bpy.context.object,'Brown garden bird body','Feathers');o.scale=(.23,.31,.24)
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.13,location=(x,y-.24,.62));finish(bpy.context.object,'Brown garden bird head','Feathers')
 cone('Garden bird russet tail',(x,y+.26,.45),.12,.015,.42,'Comb',4).rotation_euler.x=-.6;box('Brown garden bird beak',(x,y-.36,.61),(.09,.12,.06),'SailCloth')
 for dx in (-.09,.09):beam('Brown garden bird leg',(x+dx,y,.05),(x+dx,y,.22),.035,'SailCloth')

# Craft yard furniture and small planted patches are original geometry.
for x,y in [(-14,-6),(18,1),(-6,5.5)]:
 box('Oak planter soil',(x,y,.2),(1.8,.7,.4),'DirtPath',True)
 for dy in (-.4,.4):box('Oak planter side',(x,y+dy,.25),(2,.12,.5),'Wood',True)
 for dx in (-.95,.95):box('Oak planter end',(x+dx,y,.25),(.12,.8,.5),'Wood',True)
 for i in range(8):
  px=x-.8+i*.22;py=y+rng.uniform(-.2,.2);h=rng.uniform(.35,.65)
  beam('Garden flower stem',(px,py,.38),(px,py,.38+h),.035,'Leaves')
  cone('Golden mossbell blossom',(px,py,.38+h),.13,.05,.12,'Petals',5)
# A handcart at the potter's yard; two wheels and an open plank bed.
cx,cy=17,-10
box('Craft cart bed',(cx,cy,.65),(1.6,2.3,.15),'Wood',True)
for dx in (-.8,.8):
 box('Craft cart side',(cx+dx,cy,.98),(.12,2.3,.6),'Wood',True)
 wheel=cone('Craft cart solid wheel',(cx+dx*1.25,cy,.52),.48,.48,.12,'Wood',10,True);wheel.rotation_euler.y=math.pi/2
 beam('Craft cart handle',(cx+dx*.7,cy-.5,.65),(cx+dx*.7,cy-2.7,.7),.09,'Wood',True)
for y in (-1.1,1.1):box('Craft cart end',(cx,cy+y,.98),(1.7,.12,.6),'Wood',True)
for dx,dy in [(-.4,0),(.3,.5)]:
 cone('Potter fired crock',(cx+dx,cy+dy,1.12),.22,.28,.7,'OchrePlaster',8)
 cone('Potter crock dark opening',(cx+dx,cy+dy,1.475),.19,.19,.02,'WindowDark',8)
# Low benches leave the spring court's walking routes open.
for x,y in [(8,-5),(-17,5)]:
 box('Village resting bench',(x,y,.48),(2.0,.48,.13),'Wood',True)
 for dx in (-.75,.75):box('Bench stone foot',(x+dx,y,.22),(.23,.4,.44),'Masonry',True)

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
# Broken rock formations with stepped/tilted rims; separate distant ridgelines.
for side in (-1,1):
 for j in range(7):
  x=side*((38 if side==1 else 32)+rng.uniform(-3,3));y=-18+j*9
  h=rng.uniform(12,21);w=rng.uniform(6,10);d=rng.uniform(7,11)
  poly=[(x-w*.5,y-d*.5),(x+w*.5,y-d*.4),(x+w*.6,y+d*.5),(x-w*.4,y+d*.6)]
  top=[(px+side*rng.uniform(1,4),py+rng.uniform(-1,1),h+rng.uniform(-2,2)) for px,py in poly]
  mesh('Irregular side rock',[(px,py,-.15) for px,py in poly]+top,[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]+[(3,2,1,0)],'EarthCliff',True)
  mesh('Uneven grassy rock rim',top,[(0,1,2,3)],'Grass',True)
for j in range(9):
 x=-36+j*9;y=45+rng.uniform(-2,5);h=rng.uniform(11,17)
 v=[(x-6,y,-1),(x+6,y+2,-1),(x+5,y+3,h),(x-4,y+1,h+rng.uniform(-4,4)),(x-3,y+11,h+3),(x+5,y+12,h+2),(x-3,y+11,-1),(x+5,y+12,-1)]
 mesh('Closed rear cliff',v,[(0,1,2,3),(3,2,5,4),(0,3,4,6),(1,7,5,2),(6,4,5,7),(0,6,7,1)],'EarthCliff',True)
# Continuous, closed backing connects the decorative rocks without flattening their silhouettes.
# The only perimeter opening is the 8m entrance corridor at the south.
wall_path=[(-4,-34),(-18,-35),(-34,-30),(-37,-18),(-36,-5),(-38,9),(-36,23),(-37,39),(-29,51),(-14,54),(0,53),(15,55),(30,52),(42,42),(44,28),(43,14),(42,0),(42,-17),(36,-31),(19,-36),(4,-34)]
wall_rng=random.Random(944);v=[];f=[]
for i,(x,y) in enumerate(wall_path):
 outward=Vector((x,y-8)).normalized()*8
 height=7 if i in (0,len(wall_path)-1) else wall_rng.uniform(12,19)
 v.extend([(x,y,-2),(x,y,height),(x+outward.x,y+outward.y,height+wall_rng.uniform(-1,2)),(x+outward.x,y+outward.y,-2)])
for i in range(len(wall_path)-1):
 k=i*4
 f.extend([(k,k+4,k+5,k+1),(k+1,k+5,k+6,k+2),(k+2,k+6,k+7,k+3),(k+3,k+7,k+4,k)])
f.extend([(0,1,2,3),tuple(range(len(v)-1,len(v)-5,-1))])
perimeter=mesh('Closed irregular perimeter',v,f,'EarthCliff',True)
perimeter.data.materials.append(materials['Grass'])
for i in range(len(wall_path)-1):perimeter.data.polygons[i*4+1].material_index=1
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
 obj.data.materials.clear();obj.data.materials.append(materials['Collision'])
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
mtl=out/'Mossbell.mtl';mtl.write_text('\n'.join(line.split()[0]+' ../VillageTextures/'+line.split()[-1] if line.startswith(('map_Kd ','map_d ')) else line for line in mtl.read_text().splitlines())+'\n')
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
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False
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
report={'tree_ground_checks':tree_checks,'units':'metres','doors_m':{'height':2.12,'width':1.08},'stairs_m':{'rise':.16,'tread':.4,'width':3.2,'steps':20},'routes':checks,'export_triangles_including_collision':export_triangles,'visual_objects':len(source),'collision_objects':len(collision_copies),'uv':'metric face islands; path strips use width-normalized U and 4m V repeat','review_camera':{'position_blender':[0,-21,1.65],'target_blender':[0,10,3.8],'lens_mm':28,'sensor_width_mm':36,'vertical_fov_degrees':round(math.degrees(2*math.atan(36*9/16/(2*28))),4)},'limitations':['Blender geometry checks only; Unity import/physics and Quest headset traversal not executed.']}
(root/'Documentation/village-geometry-checks.json').write_text(json.dumps(report,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Blender/MossbellVillage.blend'))
for cam,filename in zip(cameras if '--no-render' not in sys.argv else [],['mossbell-street.png','mossbell-spring.png','mossbell-terrace.png','mossbell-village.png']):
 scene.camera=cam;scene.use_nodes=cam.name!='Layout overview'
 scene.render.filepath=str(root/'Documentation'/filename);bpy.ops.render.render(write_still=True)
print('PASS: editable Blender source, UV OBJ, dedicated collision and route checks; '+('renders skipped (--no-render)' if '--no-render' in sys.argv else 'four comparison views rendered'))
