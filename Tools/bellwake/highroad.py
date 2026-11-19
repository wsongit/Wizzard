"""The Bellwake watershed. Each district has a persistent address on this shared terrain."""
from pathlib import Path
import math, json
from PIL import Image, ImageDraw, ImageFont
from atelier import init, geometry, shaft, lathe, block, marker, finish, mats, rng, RES, batches
from mathutils import Matrix
from watershed import EAST, NORTH, MEADOW, HALF_WIDTH, HALF_DEPTH, chart, height as elevation, lattice
from wayside_landmarks import build as build_landmark
from wayside_paint import paint as paint_fronts, paint_sorrel

# West to east, from the sea through the market and up to the belfry.
LANES = [
    "SoundingBay Saltwake ChainDock Wrenfall GlassRookery KiteCrag RimePost",
    "SwallowLock DriftFen Reedwater SillwaterEbb SillwaterOffice SillwaterFlood Wickwater",
    "MercySlip KettleYard SupperSteps Bellmarket PaperCourt GloamingPress VellumWalk",
    "QuinceFold RootChoir RowanHollow LinenCourt RainCourt DrumHouse SignalLoom",
    "Cairnwatch SaffronKilns CastingBed CinderLens MouldLoft Glasscut LanternCourt",
    "TwinIntake SumpHall FloodLedger WeighHouse OrreryLoft EchoRotunda StillBelfry",
]

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
    paint_fronts(RES / "Textures")
    paint_sorrel(RES / "Textures")
    init(library, 1221)
    points, faces, paints = [],[],[]
    east = lattice(HALF_WIDTH, EAST)
    north = lattice(HALF_DEPTH, (*NORTH, MEADOW[1]))
    for j, v in enumerate(north):
        for i, u in enumerate(east):
            x,y = chart(u,v)
            points.append((x,y,elevation(x,y)))
            if not i or not j:
                continue
            a = len(points)-1
            faces.append((a-len(east)-1,a-len(east),a,a-1))
            mid_u, mid_v = (east[i-1]+u)*.5, (north[j-1]+v)*.5
            across = min(abs(mid_v-k) for k in NORTH)
            along = min(abs(mid_u-k) for k in EAST)
            lane = ((across <= 2.4 and EAST[0]-2.4 <= mid_u <= EAST[-1]+2.4)
                    or (along <= 2.4 and NORTH[0]-2.4 <= mid_v <= NORTH[-1]+2.4)
                    or (abs(mid_u) <= 2.4 and MEADOW[1] <= mid_v <= NORTH[0]))
            paints.append(1 if lane else 2 if elevation(x,y)>42 else 0)
    land=geometry("Watershed turf and cart tracks",points,faces,"Grass","Terrain")
    for material in ("DirtPath","Moss"):
        land.data.materials.append(mats[material])
    for poly, paint in zip(land.data.polygons,paints):
        poly.material_index=paint
    # Broad bends in the grain keep parallel tile boundaries from marching up each hill.
    uv_layer = land.data.uv_layers.active.data
    for loop in land.data.loops:
        x, y, _ = points[loop.vertex_index]
        uv_layer[loop.index].uv = ((x*.93+y*.26+2.7*math.sin(y/24))/2.6,
                                   (y*.94-x*.27+3.1*math.sin(x/26))/2.6)
    # Vertical boundary and skyline share their foot with the outermost terrain vertices.
    edge=([chart(u,north[0]) for u in east[:-1]] + [chart(east[-1],v) for v in north[:-1]]
          + [chart(u,north[-1]) for u in reversed(east[1:])] + [chart(east[0],v) for v in reversed(north[1:])])
    verts = [(x,y,elevation(x,y)) for x,y in edge]
    verts.extend((x*1.0002,y*1.0002,elevation(x,y)+3.2) for x,y in edge)
    verts.extend((x*1.06,y*1.06,elevation(x,y)+48+17*math.sin(x*.014+y*.018)+9*math.cos(x*.036-y*.029))
                 for x,y in edge)
    n = len(edge)
    cliff_faces = [(base+i,base+i+n,base+(i+1)%n+n,base+(i+1)%n)
                   for base in (0,n) for i in range(n)]
    geometry("Encircling ridgeline",verts,cliff_faces,"Mountain","Rim")
    for row,line in enumerate(LANES):
        for col,key in enumerate(line.split()):
            x,y=chart(EAST[col], NORTH[row])
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
            reserved=[(lx,ly,3.0),(x,y,3.6)]
            if col==(1,4,3,2,4,6)[row]:
                hx,hy=chart(EAST[col]-28, NORTH[row]+24)
                build_landmark(row,hx,hy)
                reserved.append((hx,hy,10))
            # A painted window, sill, braces and stone base occupy one quad of the wall.
            if row in (0,2,4):
                hx,hy=x+22+col%3*2,y-17
                reserved.append((hx,hy,6.0))
                hz=elevation(hx,hy)
                w,d=4.6,3.1
                front=hy-d
                u0,u1=((col+row)%3*64+.5)/256,((col+row)%3*64+63.5)/256
                foot=min(elevation(hx+dx,hy+dy) for dx in (-w,w) for dy in (-d,d))-.32
                corners=[(hx-w,front,foot),(hx+w,front,foot),(hx+w,front,hz+3.5),(hx-w,front,hz+3.5)]
                back=[(a,hy+d,c) for a,_,c in corners]
                front_uv=[(u0,.01),(u1,.01),(u1,.99),(u0,.99)]
                plain_uv=[(192.5/256,.01),(255.5/256,.01),(255.5/256,.99),(192.5/256,.99)]
                geometry("Toll cottage walls",corners+back,[(0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(4,5,1,0),(3,2,6,7)],
                               "WayhouseFronts",uv=front_uv+plain_uv*5)
                ridge=[(hx-w-.5,hy,hz+5.7),(hx+w+.5,hy,hz+5.7)]
                eaves=[(hx+a*(w+.5),hy+b*(d+.5),hz+3.42) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]
                geometry("Tile eaves and closed gables",eaves+ridge,[(3,2,1,0),(0,1,5,4),(3,4,5,2),(0,4,3),(1,2,5)],"RoofTiles")
            # Leave a generous approach aisle around every trail intersection.
            tx,ty=x+6+rng.uniform(0,3),y+6
            reserved.append((tx,ty,2.8))
            base=elevation(tx,ty)-.12
            shaft("Hazel trunk",(tx,ty,base),(tx+.3,ty,base+3),.29,.16,"Wood",7)
            for j in range(3):
                lathe("Hazel crown",tx+j*.55-.5,ty+.36*(j%2),base+2+j*.19,[(.56,0),(1.42,.72),(1.10,1.49),(.18,2.08)],"Leaves",6)
            for k in range(6):
                u=EAST[col]+rng.choice((-1,1))*rng.uniform(22,76)
                v=NORTH[row]+rng.choice((-1,1))*rng.uniform(27,71)
                bx,by=chart(u,v)
                if any(math.hypot(bx-ox,by-oy)<radius+4.2 for ox,oy,radius in reserved):
                    continue
                reserved.append((bx,by,.65))
                z=elevation(bx,by)-.32
                lean=rng.uniform(-.9,.9)
                tall=rng.uniform(3.1,5.5)
                shaft("Field alder",(bx,by,z),(bx+lean,by,z+tall),.44,.20,"Wood",6)
                for side in (-1,1):
                    spread=rng.uniform(.9,1.7)
                    ex,ey=bx+side*spread,by+rng.uniform(-.7,.7)
                    shaft("Alder fork",(bx+lean*.64,by,z+tall*.64),(ex,ey,z+tall+.58),.20,.09,"Wood",5)
                    radius=rng.uniform(1.65,2.65)
                    lathe("Leaf cluster",ex,ey,z+tall-.35,[(.46,0),(radius,.9),(radius*.86,2.1),(.3,2.8)],"Leaves",6)
            for k in range(24):
                u = EAST[col]+rng.choice((-1,1))*rng.uniform(5.5,74)
                v = NORTH[row]+rng.choice((-1,1))*rng.uniform(7,72)
                sx,sy=chart(u,v)
                if any(math.hypot(sx-ox,sy-oy)<radius+.7 for ox,oy,radius in reserved):
                    continue
                z=elevation(sx,sy)-.12
                size=rng.uniform(.65,1.34)
                angle=rng.uniform(0,math.pi)
                for j in range(3):
                    dx=size*.55*math.cos(angle+j*math.pi/3)
                    dy=size*.55*math.sin(angle+j*math.pi/3)
                    geometry("Sorrel fronds",[(sx-dx,sy-dy,z),(sx+dx,sy+dy,z),
                             (sx+dx,sy+dy,z+size),(sx-dx,sy-dy,z+size)],[(0,1,2,3)],
                             "RoadSorrel",f"FieldLeaves_{row}_{col}",uv=[(0,0),(1,0),(1,1),(0,1)])
            # Preserve cell bounds for the native distance and frustum checks.
            marker(f"FieldAnchor_{row}_{col}", x, y, h)
            batches[f"FieldCell_{row}_{col}"].extend(batches["Set"])
            batches["Set"].clear()
    batches.pop("Set",None)
    bx,by=chart(HALF_WIDTH-5,HALF_DEPTH-5)
    block("Boundary footing",(bx,by,elevation(bx,by)),(1,1,.4),"Masonry","C_Solids")
    x,y=chart(*MEADOW)
    marker("RoadLongMeadow",x,y,elevation(x,y)+.14)
    for dx in (-2,2):
        z=elevation(x+dx,y)-.12
        shaft("Meadow trail cairn",(x+dx,y,z),(x+dx,y,z+1.35),.5,.29,"MossRock",7)
    marker("Spawn",x,y,elevation(x,y)+.14)
    marker("Look",x,y+4,elevation(x,y)+1)
    finish("Highroad","Bellmarket")
