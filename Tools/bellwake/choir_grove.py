"""Root Choir's living threshold, rock-and-moss banks and hanging seed lantern."""
import math
from mathutils import Vector
from atelier import geometry,shaft,lathe,mats,batches

def root_run(name,route,ink,n=9):
    centres=[Vector(p[:3]) for p in route];pts=[];faces=[]
    for j,(p,r) in enumerate(zip(centres,[p[3] for p in route])):
        across=(centres[min(len(route)-1,j+1)]-centres[max(0,j-1)]).normalized()
        side=Vector((0,1,0))
        side=(side-across*side.dot(across)).normalized()
        upright=across.cross(side)
        for i in range(n):
            a=math.tau*i/n
            q=p+(side*math.cos(a)+upright*math.sin(a))*r*(1+.08*math.sin(3*a+.6*j))
            pts.append(tuple(q))
    for j in range(len(route)-1):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n
            faces.append((a,b,b+n,a+n))
    faces.extend([tuple(reversed(range(n))),tuple(range(len(pts)-n,len(pts)))])
    return geometry(name,pts,faces,ink)

def braid():
    root_run('Old tree crossing the lane',[
        (-3.68,-5.8,-.22,.89),(-3.54,-5.71,.43,.74),(-3.66,-5.53,1.82,.56),
        (-3.20,-5.37,3.15,.51),(-2.43,-5.13,3.92,.43),(-1.22,-5.15,4.29,.34),
        (-.28,-5.34,4.22,.30),(1.03,-5.17,4.62,.30),(2.15,-4.98,4.12,.39),
        (3.05,-5.26,3.08,.48),(3.49,-5.23,1.53,.57),(3.44,-5.34,.50,.68),
        (3.69,-5.63,-.24,.84)],'ElderBark',11)
    for side in [-1,1]:
        x=side*3.53;y=-5.54
        for dx,dy in [(1.2,.5),(.7,-.83),(-.33,.79)]:
            root_run('Anchored oak flare',[(x,y,.75,.46),(x+side*dx*.51,y+dy*.47,.23,.30),
                     (x+side*dx,y+dy,-.13,.14)],'ElderBark',7)
        root_run('Outside fork',[(side*3.35,-5.4,2.55,.38),(side*4.11,-5.28,3.45,.27),
                 (side*4.36,-4.97,4.37,.17),(side*5.31,-5.25,4.96,.07)],'ElderBark')
        for j,(dx,dy,h,r) in enumerate([(4.85,-5.04,4.05,1.20),(3.81,-5.27,4.28,1.19),(2.56,-5.30,4.35,.90)]):
            lathe('Old oak crown',side*dx,dy,h,[(.51*r,0),(.93*r,.25*r),(r,.65*r),(.69*r,1.0*r),(.26*r,1.15*r)],
                  'ElderLeaf',7)
    # The hollow copper seed hangs from the upper crook, high above the player corridor.
    for x in [-.3,.25]:
        shaft('Braided suspension',(x,-5.37,4.15),(x*.38,-5.39,3.71),.036,.029,'Wood',6)
    lathe('Seed hanger',0,-5.4,3.54,[(.12,0),(.105,.062),(.081,.11),(.065,.18)],'Brass',8)
    lathe('Copper cup',0,-5.4,3.10,[(.064,0),(.225,.11),(.285,.34),(.223,.44),(.137,.48)],'Brass',9)
    lathe('Seed glass',0,-5.4,3.24,[(.17,0),(.271,.12),(.278,.19),(.225,.24)],'SeaGlass',9)
    for j in range(3):
        a=math.tau*j/3
        shaft('Seed cradle',(0,-5.4,3.12),(.274*math.cos(a),-5.4+.274*math.sin(a),3.45),.025,.020,'Brass',6)

def paint_bank():
    rim=batches['Rim'][0];rim.data.materials[0]=mats['ChoirOutcrop']
    rim.data.materials.append(mats['ChoirLoam'])
    for f in rim.data.polygons:
        # Both painted zones inherit the connected geometry of the retaining bank.
        if (f.index//2)%4 in (2,3):f.material_index=1


def high_canopy():
    # Tie the six bare limbs of the apse to full crowns over the back terrace.
    for side in [-1,1]:
        for j in range(3):
            bx,by=side*(1.2+j*.7),12+j*1.7
            z=8.3+j*.6
            for k,(dx,dy,r,h) in enumerate([(.35,-.39,1.68,1.47),(1.55,.61,1.85,1.58),(2.54,-.38,1.23,1.15)]):
                rx=bx+side*dx;ry=by+dy;bottom=z-.49+.15*k
                shaft('Last leaf-bearing fork',(bx+side*.91,by+.35,z-.38),(rx,ry,bottom+.42),.19,.068,'ElderBark',7)
                lathe('Interlocking crown',rx,ry,bottom,[(r*.44,0),(r*.91,h*.22),(r,h*.54),(r*.73,h*.83),(r*.22,h)],'ElderLeaf',8)
