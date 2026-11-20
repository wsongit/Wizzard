"""Bellmarket's north pass and working hill mill. Coordinates follow the authored village in metres."""
import math
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from atelier import batches, block, collision, geometry, lathe, marker, mats, origins, rng, shaft
from wayside_landmarks import windmill

def market_ridge(ground):
    # Cut a saddle behind the gate. The escarpment and turf share vertices at every change of paint.
    points, faces, inks = [], [], []
    count = 64
    for i in range(count):
        a = math.tau*i/count
        c,s = math.cos(a), math.sin(a)
        x,y = 20*c/max(abs(c),abs(s)), 20*s/max(abs(c),abs(s))
        cap = 6 + 2*math.sin(3*a+.7) + rng.uniform(0,2)
        bank = min(1,max(0,(abs(x)-2.2)/6)) if y>17 else 1
        bank = bank*bank*(3-2*bank)
        crest = 1.85 + (cap-1.85)*bank
        far = 3 + (cap+1+5*math.sin(5*a))*bank
        for scale,z in [(1,ground(0,x,y)-.2),(1.09,.55*crest),(1.20,.93*crest),
                        (1.24,crest),(1.5,.78*crest),(2.3,far)]:
            points.append((x*scale,y*scale,z))
    for i in range(count):
        x,y,_ = points[i*6];xx,yy,_ = points[((i+1)%count)*6]
        road = y>18 and yy>18 and abs((x+xx)*.5)<2.2
        for band in range(5):
            a,b = i*6+band, ((i+1)%count)*6+band
            faces.extend([(a,b+1,b),(a,a+1,b+1)])
            ink = "DirtPath" if road else ("MarketCutbank","MarketCutbank","VillageTurf","VillageTurf","Mountain")[band]
            inks.extend([ink,ink])
    rim=geometry("North pass and turf banks",points,faces,"MarketCutbank","Rim")
    names=["MarketCutbank","VillageTurf","Mountain","DirtPath"]
    for name in names[1:]:rim.data.materials.append(mats[name])
    for face, name in zip(rim.data.polygons,inks):face.material_index=names.index(name)
    for x,y,w,d in [(0,-20.4,41,.8),(0,20.4,41,.8),(-20.4,0,.8,41),(20.4,0,.8,41)]:
        collision("Closed map limit",x,y,-2,w,d,18)

def masonry_section(name, left, right, profile, paint):
    # Extrude a closed Y/Z outline across the width. This keeps each step attached to the next.
    n=len(profile)
    points=[(x,y,z) for x in (left,right) for y,z in profile]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return geometry(name,points,faces,paint)

def gate_stair():
    start,end=8,14
    profile=[(start,-.26),(end,-.26),(end,1.015)]
    for j in reversed(range(8)):
        y=start+(end-start)*j/8
        top=(j+1)/8+.015
        profile.append((y,top))
        if j:profile.append((y,j/8+.015))
    masonry_section("Eight courses of gate steps",-1.60,1.60,profile,"GateStone")
    cheek=[(start-.33,-.24),(end+.20,-.24),(end+.20,1.33),(end,1.33),(start,.33),(start-.33,.33)]
    for left in [-1.86,1.60]:
        masonry_section("Low stair coping",left,left+.26,cheek,"Masonry")

def spring_well(x,y,z):
    # Lay out continuous mortar courses around the shaft and unwrap the coping stones from above.
    profile=[(.87,-.25),(.93,.07),(.91,.68),(.98,.72),(.98,.84),(.69,.84),(.66,.74),(.66,-.14)]
    sectors=32
    points=[(x+r*math.cos(j*math.tau/sectors),y+r*math.sin(j*math.tau/sectors),z+h)
            for r,h in profile for j in range(sectors)]
    faces=[];uv=[]
    for band,(radius,height) in enumerate(profile):
        k=(band+1)%len(profile)
        for j in range(sectors):
            jj=(j+1)%sectors
            face=(band*sectors+j,band*sectors+jj,k*sectors+jj,k*sectors+j)
            faces.append(face)
            if band in (2,4,5,7):
                uv.extend([((points[v][0]-x)*.74,(points[v][1]-y)*.74) for v in face])
            else:
                uv.extend([(j*3/sectors,height*1.40),((j+1)*3/sectors,height*1.40),
                           ((j+1)*3/sectors,profile[k][1]*1.40),(j*3/sectors,profile[k][1]*1.40)])
    geometry("Lichen-stained spring masonry",points,faces,"SpringStone",uv=uv)
    lathe("Spring water",x,y,z,[(.672,.29),(.672,.31)],"SeaGlass",24)
    # The old oak grate shows water between its slats. The closed support keeps tracked hands out of the shaft.
    for row in range(-3,4):
        offset=row*.18
        length=2*math.sqrt(.736**2-(abs(offset)+.052)**2)
        block("Oak spring grate",(x,y+offset,z+.53),(length,.104,.076),"TarredOak")
    lathe("Sealed well shaft",x,y,z,[(.685,-.16),(.685,.559)],"Masonry",24,"C_Solids")
    for side in (-1,1):
        xx=x+side*.79
        shaft("Windlass upright",(xx,y,z+.64),(xx,y,z+2.19),.091,.08,"Wood",10)
        shaft("Bearing plate",(xx-.061,y,z+2.07),(xx+.061,y,z+2.07),.127,.127,"BellMetal",10)
    shaft("Windlass axle",(x-1.00,y,z+2.07),(x+1.03,y,z+2.07),.073,.073,"TarredOak",12)
    shaft("Wooden winding drum",(x-.34,y,z+2.07),(x+.34,y,z+2.07),.117,.117,"Wood",12)
    for j in range(8):
        a=x-.21+j*.045
        shaft("Turns of flax rope",(a,y,z+2.07),(a+.026,y,z+2.07),.14,.15,"FlaxCord",10)
        shaft("Turns of flax rope",(a+.026,y,z+2.07),(a+.046,y,z+2.07),.15,.14,"FlaxCord",10)
    for side in (-1,1):
        a=x+side*.325
        shaft("Windlass cheek",(a-.025,y,z+2.07),(a+.025,y,z+2.07),.178,.178,"TarredOak",12)
    shaft("Bent crank",(x+1.0,y,z+2.07),(x+1.0,y-.18,z+1.90),.052,.046,"BellMetal",8)
    shaft("Crank grip",(x+.98,y-.18,z+1.90),(x+1.23,y-.18,z+1.90),.055,.061,"Wood",10)
    cy=y+.14;cx=x+.11
    # Bucket and handle share a suspension point directly below the last turn of the rope.
    lathe("Bound oak pail",cx,cy,z,[(.134,.69),(.154,.72),(.204,1.026),(.196,1.045),
          (.17,1.037),(.124,.731)],"Wood",14)
    for h,r in [(.75,.16),(.97,.202)]:
        lathe("Pail band",cx,cy,z,[(r-.003,h-.019),(r+.003,h-.016),(r+.004,h+.017),(r-.001,h+.020)],"BellMetal",14)
    last=None
    for j in range(9):
        a=math.pi*j/8
        point=(cx+.187*math.cos(a),cy,z+1.007+.211*math.sin(a))
        if last is not None:shaft("Iron carrying bow",last,point,.013,.013,"BellMetal",7)
        last=point
    shaft("Plaited fall", (cx,cy,z+1.21),(cx,cy,z+2.07),.015,.015,"FlaxCord",7)


def skyline_mill():
    # Seat the drum on the actual far bank at its highest point. Its footing reaches the lowest point.
    x,y,scale = 9.8,28.5,.78
    rim=batches["Rim"][0].data
    tree=BVHTree.FromPolygons([v.co for v in rim.vertices],[p.vertices[:] for p in rim.polygons])
    heights=[]
    for radius in (0,1.9,3.4):
        for i in range(48):
            a=math.tau*i/48
            hit=tree.ray_cast((x+radius*math.cos(a),y+radius*math.sin(a),50),(0,0,-1))[0]
            heights.append(hit.z)
    z=max(heights)-.20
    start=len(batches["Set"])
    windmill(0,0,0,"MillSails",(z-min(heights)+.45)/scale)
    place=Matrix.Translation((x,y,z)) @ Matrix.Scale(scale,4)
    for obj in batches["Set"][start:]+batches["MillSails"]:
        obj.matrix_world=place @ obj.matrix_world
    pivot=place @ Vector((0,-3.9,10.7))
    origins["MillSails"]=tuple(pivot)
    marker("MillAxis",pivot.x,pivot.y-1,pivot.z)

def valley_orchard():
    from atelier import lathe, shaft
    rim=batches["Rim"][0].data
    land=BVHTree.FromPolygons([v.co for v in rim.vertices],[p.vertices[:] for p in rim.polygons])
    for i,(x,y,h) in enumerate([(-8.6,30,4.3),(-6.5,35,4.1),(-4.4,39,3.0),(5.4,36,3.6),
                                 (7.5,40,4.8),(12.7,39,3.5),(-14.7,33,4.1),(15.2,33.9,4.9)]):
        z=land.ray_cast((x,y,60),(0,0,-1))[0].z
        lean=.13*math.sin(i*2.7)
        shaft("Orchard trunk",(x,y,z-.36),(x+lean,y,z+h*.72),.20,.105,"Wood",8)
        for j in range(3):
            a=i*2.1+j*2.4
            dx,dy=.58*math.cos(a),.58*math.sin(a)
            low=z+h*(.35+.09*j)
            shaft("Orchard fork",(x+lean,y,z+h*.36),(x+dx,y+dy,low+.50),.125,.06,"Wood",6)
            r=h*(.29-.025*j)
            lathe("Orchard canopy",x+dx,y+dy,low,[(r*.54,0),(r,h*.18),(r*.85,h*.32),(r*.24,h*.43)],
                  "Leaves",7)
