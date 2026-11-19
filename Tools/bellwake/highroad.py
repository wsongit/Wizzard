"""The Bellwake watershed. Each district has a persistent address on this shared terrain."""
from pathlib import Path
import math, json
from PIL import Image, ImageDraw, ImageFont
from atelier import init, geometry, shaft, lathe, block, marker, finish, mats, rng, RES, batches
from mathutils import Matrix

# West to east, from the sea through the market and up to the belfry.
LANES = [
    "SoundingBay Saltwake ChainDock Wrenfall GlassRookery KiteCrag RimePost",
    "SwallowLock DriftFen Reedwater SillwaterEbb SillwaterOffice SillwaterFlood Wickwater",
    "MercySlip KettleYard SupperSteps Bellmarket PaperCourt GloamingPress VellumWalk",
    "QuinceFold RootChoir RowanHollow LinenCourt RainCourt DrumHouse SignalLoom",
    "Cairnwatch SaffronKilns CastingBed CinderLens MouldLoft Glasscut LanternCourt",
    "TwinIntake SumpHall FloodLedger WeighHouse OrreryLoft EchoRotunda StillBelfry",
]

def elevation(x,y):
    return 2.5 + 1.3*math.sin(x/28)*math.cos(y/35) + .72*math.sin((x+y)/19)

def make(library):
    # Each location occupies a 128 x 48 swatch in one sign atlas.
    story_titles=["Bellmender's Market","The Root Choir","Reedwater Lock","The Cinder Lens","The Still Belfry"]
    titles=dict(zip(["Bellmarket","RootChoir","Reedwater","CinderLens","StillBelfry"],story_titles))
    for filename, field in (("Underworks","rooms"),("Passages","regions")):
        titles.update({r["key"]:r["title"] for r in json.loads((RES/(filename+".json")).read_text())[field]})
    image=Image.new("RGB",(1024,512),(73,45,33))
    draw=ImageDraw.Draw(image)
    for row,line in enumerate(LANES):
        for col,key in enumerate(line.split()):
            name=titles[key].replace("The ","",1)
            for size in range(18,7,-1):
                font=ImageFont.truetype("DejaVuSans-Bold.ttf",size)
                if font.getlength(name)<122: break
            x,y=128*col,48*row
            draw.rectangle((x+2,y+3,x+125,y+44),outline=(176,128,74),width=2)
            draw.text((x+64,y+23),name,fill=(250,226,167),font=font,anchor="mm")
    image.save(RES/"Textures/HighroadSigns.png")
    init(library, 1221)
    points, faces, paints = [],[],[]
    for j in range(73):
        for i in range(81):
            x,y=(i-40)*2,(j-36)*2
            points.append((x,y,elevation(x,y)))
            if i and j:
                a=len(points)-1
                faces.append((a-82,a-81,a,a-1))
                xx, yy=x-1,y-1
                across=min(abs(yy-v) for v in range(-50,51,20))
                along=min(abs(xx-v) for v in range(-60,61,20))
                lane=(across<2.2 and abs(xx)<65) or (along<2.2 and abs(yy)<55)
                paints.append(1 if lane else 2 if across<4 and along<4 else 0)
    land=geometry("Watershed turf and cart tracks",points,faces,"Grass","Terrain")
    for material in ("DirtPath","Moss"):
        land.data.materials.append(mats[material])
    for poly, paint in zip(land.data.polygons,paints):
        poly.material_index=paint
    # Vertical boundary and skyline share their foot with the outermost terrain vertices.
    edge=[(x,-72) for x in range(-80,80,2)]+[(80,y) for y in range(-72,72,2)]+[(x,72) for x in range(80,-80,-2)]+[(-80,y) for y in range(72,-72,-2)]
    verts=[(x,y,elevation(x,y)) for x,y in edge]+[(x*1.10,y*1.10,elevation(x,y)+10+4*math.sin(x*.12+y*.08)) for x,y in edge]
    n=len(edge)
    geometry("Encircling ridgeline",verts,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],"Mountain","Rim")
    for row,line in enumerate(LANES):
        for col,key in enumerate(line.split()):
            x,y=(col-3)*20,(row-2.5)*20
            h=elevation(x,y)
            marker("Road"+key,x,y,h+.14)
            gate_start=len(batches["Set"])
            # Milestones and roofed toll arches are open on both axes.
            for side in (-1,1):
                sx=x+side*1.85
                base=elevation(sx,y)-.16
                lathe("Stone plinth",sx,y,base,[(.39,0),(.36,.55),(.27,.65)],"Masonry",5)
                shaft("Waypost",(sx,y,base+.4),(sx,y,h+3.4),.21,.15,"Wood",6)
            block("Carved lintel",(x,y,h+3.34),(4.3,.38,.34),"Wood")
            sign_y=y-.27
            plaque=[(x-1.5,sign_y,h+2.97),(x+1.5,sign_y,h+2.97),(x+1.5,sign_y,h+3.99),(x-1.5,sign_y,h+3.99)]
            u0,u1=(col*128+1)/1024,((col+1)*128-1)/1024
            v0,v1=1-((row+1)*48-1)/512,1-(row*48+1)/512
            uv=[(u0,v0),(u1,v0),(u1,v1),(u0,v1)]
            geometry("Painted road name",plaque,[(0,1,2,3)],"HighroadSigns",uv=uv)
            geometry("Painted reverse",[(a,y+.27,c) for a,b,c in plaque],[(1,0,3,2)],"HighroadSigns",uv=uv)
            block("Sign core",(x,y,h+3.48),(3,.52,1.02),"Wood")
            block("District enamel",(x,y-.22,h+3.3),(1.0,.12,.32),("Brass","FenShale","KilnGlaze","SeaGlass","OchrePlaster","Basalt")[row])
            # Both straight-through lanes must clear the posts at each crossroads.
            turn=Matrix.Translation((x,y,0)) @ Matrix.Rotation(math.pi/4,4,"Z") @ Matrix.Translation((-x,-y,0))
            for part in batches["Set"][gate_start:]:
                part.data.transform(turn)
            # The ridges can be identified by silhouette even when lettering is distant.
            lx,ly=x-6,y-5
            base=elevation(lx,ly)-.18
            if row==0:
                lathe("Coastal beacon",lx,ly,base,[(1.7,0),(1.25,.7),(.86,4.4),(1.10,4.65),(.70,5)],"HarbourBrick",8)
                lathe("Lantern glass",lx,ly,base+4.94,[(.7,0),(.73,.69),(.22,1.03)],"Amber",6)
            elif row==1:
                for post in (-1,1):
                    shaft("Lock hoist cheek",(lx+post,ly,base),(lx+post*.65,ly,base+3.6),.19,.14,"Wood",5)
                block("Lock hoist crown",(lx,ly,base+3.6),(2.55,.47,.34),"Wood")
                lathe("Winding drum",lx,ly,base,[(.72,0),(.65,1.2),(.76,1.4)],"BellMetal",8)
            elif row==2:
                block("Roadside shelter",(lx,ly,base+1.2),(3.4,2.6,2.6),"HousePlaster")
                geometry("Hipped roof",[(lx+a,ly+b,base+c) for a,b,c in [(-2,-1.6,2.45),(2,-1.6,2.45),(2,1.6,2.45),(-2,1.6,2.45),(-1.2,0,3.85),(1.2,0,3.85)]],[(3,2,1,0),(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)],"KilnGlaze")
            elif row==3:
                for i in range(3):
                    bx,by=lx+i*.74,ly+.4*(i%2)
                    lathe("Ridge standing stone",bx,by,elevation(bx,by)-.12,[(.44,0),(.46,1.55+i*.45),(.18,2.12+i*.42)],"MossRock",5)
            elif row==4:
                lathe("Vented tile kiln",lx,ly,base,[(1.6,0),(1.55,1.65),(.59,2.7),(.49,3.65),(.64,3.72)],"HarbourBrick",8)
            else:
                lathe("Belfry buttress",lx,ly,base,[(1.25,0),(.78,2.9),(.55,5.1),(.07,6.3)],"Basalt",5)
            tx,ty=x+6+rng.uniform(0,3),y+6
            base=elevation(tx,ty)-.12
            shaft("Hazel trunk",(tx,ty,base),(tx+.3,ty,base+3),.29,.16,"Wood",7)
            for j in range(3):
                lathe("Hazel crown",tx+j*.55-.5,ty+.36*(j%2),base+2+j*.19,[(.56,0),(1.42,.72),(1.10,1.49),(.18,2.08)],"Leaves",6)
    # Perimeter marker does not obstruct the road network.
    block("Boundary footing",(78,70,elevation(78,70)),(1,1,.4),"Masonry","C_Solids")
    marker("RoadLongMeadow",0,-60,elevation(0,-60)+.14)
    for x in (-2,2):
        shaft("Meadow trail cairn",(x,-60,elevation(x,-60)-.12),(x,-60,elevation(x,-60)+1.2),.5,.29,"MossRock",7)
    marker("Spawn",0,0,elevation(0,0)+.14)
    marker("Look",0,4,elevation(0,4)+1)
    finish("Highroad","Bellmarket")
