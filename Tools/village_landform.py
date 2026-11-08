"""Continuous, closed village ground. One top surface, no overlapping ramp shells."""
import math,bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
MIDDLE=[(-25,13),(-18,9),(-13,8),(-7,8),(-2,7),(7,8),(11,14),(11,25),(-9,30),(-24,24)]
UPPER=[(5,23),(9,21),(16,20),(20,24),(20,34),(12,39),(3,35),(1,29)]
LOW_ROUTE=[(11,-1,0),(15,5,1.2),(14,9,2.1),(11,14,3.2),(9,15,3.2)]
HIGH_ROUTE=[(9,19,3.2),(17,18,4),(24,22,5.7),(25,28,7),(20,30,8)]
def polygon_distance(x,y,poly):
 inside=False;d=1e9
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ax,ay=a;bx,by=b
  if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:inside=not inside
  dx=bx-ax;dy=by-ay;t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy)))
  d=min(d,math.hypot(x-ax-t*dx,y-ay-t*dy))
 return 0 if inside else d

def height(x,y):
 h=max(-.02,3.2*max(0,1-polygon_distance(x,y,MIDDLE)/2.3),8*max(0,1-polygon_distance(x,y,UPPER)/2.6))
 for route in (LOW_ROUTE,HIGH_ROUTE):
  nearest=(float('inf'),0)
  for a,b in zip(route,route[1:]):
   dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)))
   d=math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)
   if d<nearest[0]:nearest=(d,a[2]+t*(b[2]-a[2]))
  d,z=nearest;shoulder=max(0,min(1,(5.25-d)/3))
  h=max(h,z*shoulder)
 # Broad foundations keep whole cottage footprints supported, not just their centres.
 for cx,cy,w,d,z,angle in [(-3,17,8,6.7,3.2,-18),(-18,22,6.6,6,3.2,8)]:
  co=math.cos(math.radians(angle));si=math.sin(math.radians(angle));dx=x-cx;dy=y-cy
  u=abs(co*dx+si*dy)-w/2-.45;v=abs(-si*dx+co*dy)-d/2-.45
  dist=math.hypot(max(0,u),max(0,v));h=max(h,z*max(0,1-dist/2))
 return h

class Landform:
 def __init__(self,api):
  xs=[-55,-50,-45,-40,-35]+[i*.5 for i in range(-64,67)]+[36,40,45,50,55,60]
  ys=[-46,-42,-38,-36]+[i*.5 for i in range(-68,85)]+[46,50,55,60,64,68]
  nx=len(xs);ny=len(ys);v=[(x,y,height(x,y)) for y in ys for x in xs];f=[]
  for j in range(ny-1):
   for i in range(nx-1):
    a=j*nx+i;b=a+1;c=a+nx;d=c+1
    f.extend([(a,b,d),(a,d,c)])
  # Shared side-ring indices and closed bottom: no underside or boundary holes.
  rim=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+list(range(ny*nx-2,(ny-1)*nx-1,-1))+[j*nx for j in range(ny-2,0,-1)]
  bottom=len(v);v.extend((v[i][0],v[i][1],-3) for i in rim)
  for k,i in enumerate(rim):q=(k+1)%len(rim);f.append((i,bottom+k,bottom+q,rim[q]))
  f.append(tuple(bottom+k for k in range(len(rim)-1,-1,-1)))
  o=api['mesh']('Unified village landform',v,f,'Grass',True);o.data.materials.append(api['materials']['EarthCliff'])
  for p in o.data.polygons:
   if p.normal.z<.82:p.material_index=1
  bpy.context.view_layer.objects.active=o;o.select_set(True)
  dec=o.modifiers.new('Preserve flat plateaus','DECIMATE');dec.decimate_type='DISSOLVE';dec.angle_limit=.003;dec.delimit={'MATERIAL'}
  bpy.ops.object.modifier_apply(modifier=dec.name)
  # Explicit final triangles make authoring and runtime use the same interpolation.
  tri=o.modifiers.new('Final terrain triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=tri.name)
  self.bvh=BVHTree.FromPolygons([p.co for p in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
  self.object=o
 def sample(self,x,y):
  hit,_,_,_=self.bvh.ray_cast(Vector((x,y,40)),Vector((0,0,-1)),50)
  if hit is None:raise ValueError(('Outside landform',x,y))
  return hit.z
