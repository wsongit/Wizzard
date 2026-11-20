"""Trade-specific measuring tools fixed to the six survey frames on the Mercy Run."""
from math import cos, sin, tau
from atelier import block, geometry, lathe, shaft


def rod(name, a, b, radius, paint, sides=8):
    return shaft(name, a, b, radius, radius, paint, sides)


def linen_chart(x, y, z):
    # The display stands in its original posts. Offset the cloth behind the chart face.
    for side in (-1, 1):
        xx = x + side * 1.36
        rod("Ash tenter standard", (xx,y+.07,z+1.72), (xx,y+.07,z+3.95), .069, "Wood")
        lathe("Tenter finial", xx,y+.07,z+3.88, [(.10,0),(.077,.14),(.025,.22)], "Brass", 7)
    rod("Tenter crosspiece", (x-1.64,y+.07,z+3.79), (x+1.64,y+.07,z+3.79), .071, "Wood")
    for n, (swatch, hem) in enumerate((("MillCanvas","SeaCloth"), ("SeaCloth","MillCanvas"), ("Awning","MillCanvas"))):
        left = x - 1.42 + n * .96
        # A folded edge wraps the rail. The bottom hangs at a different height on each piece.
        pts = []
        for j in range(6):
            dx = j * .158
            wave = .060 * cos(j * 1.69 + n)
            pts += [(left+dx, y+.06+wave, z+3.77), (left+dx,y-.073+wave,z+3.73),
                    (left+dx, y-.112+wave, z+3.37+.042*cos(j*1.4+n)),
                    (left+dx,y-.116+wave,z+3.30+.042*cos(j*1.4+n))]
        upper, bottom = [], []
        for j in range(5):
            i = j * 4
            upper.extend([(i+1,i+5,i+4,i), (i+2,i+6,i+5,i+1)])
            bottom.append((i+3,i+7,i+6,i+2))
        geometry("Linen on the drying rail",pts,upper,swatch)
        geometry("Dyed selvedge",pts,bottom,hem)
        for j in (0,4):
            xx=left+.08+j*.158
            rod("Boxwood clothes pin", (xx,y-.073,z+3.69), (xx,y+.062,z+3.85), .025, "Wood", 5)


def kite_chart(x, y, z):
    for side in (-1,1):
        xx=x+side*1.36
        rod("Bridle frame cheek",(xx,y+.08,z+1.71),(xx,y+.08,z+3.31),.065,"Wood")
        rod("Spreader strut",(xx,y+.075,z+3.22),(x,y+.075,z+3.78),.057,"Wood")
    a=(x,y-.05,z+4.82)
    b=(x+1.37,y+.04,z+4.04)
    c=(x,y-.02,z+3.29)
    d=(x-1.37,y+.04,z+4.04)
    centre=(x,y-.29,z+4.025)
    # The ridge stands proud of the trailing corners, like a framed lifting kite.
    for one,two,paint in [(a,b,"Awning"),(b,c,"MillCanvas"),(c,d,"Awning"),(d,a,"MillCanvas")]:
        geometry("Taut kite panel",[one,two,centre],[(0,2,1)],paint)
        rod("Willow edge cane",one,two,.028,"Wood",6)
    rod("Kite spine",a,c,.037,"Wood",7)
    rod("Kite belly spar",d,b,.031,"Wood",7)
    for side in (-1,1):
        pts=[(x+side*1.34,y+.04,z+4.04), (x+side*1.50,y-.01,z+3.86),
             (x+side*1.38,y-.04,z+3.61), (x+side*1.58,y-.015,z+3.39)]
        for j,(one,two) in enumerate(zip(pts,pts[1:])):
            rod("Kite tail cord",one,two,.015,"Wood",5)
            cx,cy,cz=two
            geometry("Swallowtail knot",[(cx-.09,cy,cz+.07),(cx-.07,cy,cz-.065),(cx,cy-.023,cz),
                    (cx+.095,cy+.005,cz+.064),(cx+.08,cy+.005,cz-.068)],
                    [(0,1,2),(2,4,3)],"Awning" if j%2==0 else "MillCanvas")


def sounding_chart(x, y, z):
    for side in (-1,1):
        xx=x+side*1.36
        rod("Sounding station standard",(xx,y+.075,z+1.68),(xx,y+.075,z+3.78),.077,"Wood")
        rod("Oak knee brace",(xx,y+.075,z+3.25),(xx-side*.50,y+.075,z+3.65),.069,"Wood")
    block("Lead rack crossbeam",(x,y+.075,z+3.70),(3.30,.18,.19),"Wood")
    for j in range(3):
        xx=x+(j-1)*1.04
        rod("Fathom line",(xx,y-.06,z+3.76),(xx,y-.06,z+3.30),.027,"FlaxCord",6)
        lathe("Colored fathom whipping",xx,y-.06,z+3.52,[(.048,0),(.048,.11)],("Awning","SeaCloth","MillCanvas")[j],6)
        lathe("Tallow-cupped plummet",xx,y-.06,z+3.22,[(.094,0),(.103,.067),(.061,.20),(.040,.24)],"BellMetal",7)
    # One block on either side of the axle, so the rope drum can be read from above and below.
    for side in (-1,1):
        xx=x+side*.43
        block("Drum bearing block",(xx,y+.08,z+3.97),(.18,.25,.54),"Wood")
    a=(x-.56,y+.08,z+4.10);b=(x+.56,y+.08,z+4.10)
    rod("Spindle",a,b,.068,"Brass",8)
    for sign in (-1,1):
        xx=x+sign*.31
        rod("Spool flange",(xx-.043,y+.08,z+4.1),(xx+.043,y+.08,z+4.1),.30,"Wood",12)
    rod("Wound lead line",(x-.27,y+.08,z+4.1),(x+.27,y+.08,z+4.1),.213,"FlaxCord",12)
    # A four-turn cord crosses the barrel, with shared faces along its entire length.
    pts=[];faces=[]
    for j in range(41):
        ang=tau*j/10
        xx=x-.25+.50*j/40
        for k in range(4):
            a=tau*k/4;rad=.215+.015*cos(a)
            pts.append((xx+.014*sin(a),y+.08+rad*cos(ang),z+4.1+rad*sin(ang)))
        if j:
            for k in range(4):
                i=4*j+k;n=4*j+(k+1)%4;faces.append((i-4,n-4,n,i))
    geometry("Spiral of wound line",pts,faces,"Reeds")


def shipwright_chart(x, y, z):
    # A planked half-scale hull on two stocks. All strakes follow the same rising sheer.
    for side in (-1, 1):
        xx = x + side * 1.36
        rod("Slip upright", (xx,y+.08,z+1.7), (xx,y+.08,z+3.5), .072, "Wood")
    block("Oak building stock", (x,y+.07,z+3.43), (3.15,.24,.17), "TarredOak")
    for xx in (x-.80, x+.80):
        for side in (-1, 1):
            rod("Cradle horn", (xx,y+.07,z+3.48), (xx,y+.07+side*.32,z+3.89), .065, "Wood", 6)
    stations = [(-1.63,.045,.29), (-1.27,.26,.11), (-.73,.42,.015),
                (.08,.47,0), (.84,.38,.045), (1.30,.23,.17), (1.58,.042,.37)]
    profile = [(0,0),(.49,.105),(.80,.245),(1,.415),(.92,.419),(.72,.235),(.43,.135),(0,.067)]
    for side in (-1, 1):
        points = [(x+length,y+.07+side*width*f,z+3.62+rise+h)
                  for length,width,rise in stations for f,h in profile]
        faces_by_paint = {"Wood":[], "TarredOak":[], "Awning":[]}
        for j in range(len(stations)-1):
            for k,paint in enumerate(("TarredOak","Wood","Awning","Wood","Wood","TarredOak","Wood")):
                i = j*len(profile)+k
                face = (i,i+8,i+9,i+1)
                faces_by_paint[paint].append(face if side==-1 else face[::-1])
        for paint,faces in faces_by_paint.items():
            geometry("Lapped hull " + paint,points,faces,paint)
        for length,width,rise in stations[1:-1]:
            # Rove heads stand proud of the red rubbing strake.
            xx = x+length
            rod("Copper rove", (xx,y+.07+side*width*.90,z+3.963+rise),
                (xx,y+.07+side*(width*.90+.027),z+3.963+rise), .034, "Brass", 6)
    for index in (0,-1):
        length,width,rise = stations[index]
        rod("Carved endpost", (x+length,y+.07,z+3.61+rise),
            (x+length,y+.07,z+4.11+rise), width+.012, "TarredOak", 7)
    for length,width,rise in (stations[2], stations[4]):
        block("Passenger thwart",(x+length,y+.07,z+3.936+rise),(.18,width*1.8,.065),"Wood")
    rod("Apprentice's painter", (x+1.59,y+.07,z+4.28),(x+1.37,y+.06,z+3.45),.028,"FlaxCord",6)


def lamp_chart(x, y, z):
    # The low green lamp and high amber lamp tell the same story as Oli's water marks.
    for side in (-1, 1):
        xx = x + side*1.36
        rod("Beacon gallows", (xx,y+.09,z+1.67), (xx,y+.09,z+4.69), .083,"TarredOak")
        rod("Shouldered oak knee",(xx,y+.09,z+3.89),(xx-side*.64,y+.09,z+4.51),.082,"Wood")
    block("Beacon yard",(x,y+.09,z+4.56),(3.22,.20,.22),"Wood")
    for side,base,glass in ((-1,3.30,"SeaGlass"),(1,3.58,"Amber")):
        xx = x+side*.82
        cy = y-.02
        lathe("Oil reservoir",xx,cy,z+base,[(.15,0),(.30,.07),(.295,.15),(.235,.20)],"BellMetal",8)
        lathe("Faceted pilot glass",xx,cy,z+base+.17,[(.225,0),(.265,.23),(.225,.39)],glass,8)
        for dx,dy in ((-.19,-.15),(.19,-.15),(-.19,.15),(.19,.15)):
            rod("Lantern cage stay",(xx+dx,cy+dy,z+base+.15),(xx+dx,cy+dy,z+base+.57),.023,"Brass",5)
        lathe("Vented rain cap",xx,cy,z+base+.55,[(.32,0),(.315,.065),(.13,.20),(.11,.27)],"VerdigrisSheet",8)
        lathe("Chimney collar",xx,cy,z+base+.76,[(.14,0),(.14,.06),(.068,.105)],"BellMetal",8)
        rod("Lamp drop", (xx,cy,z+base+.84), (xx,y+.09,z+4.57),.035,"FlaxCord",6)
    block("Water notch gauge",(x,y-.04,z+3.85),(.12,.105,1.02),"Wood")
    for j in range(4):
        block("High-water tally",(x+.035,y-.103,z+3.48+j*.19),(.105,.027,.029),"MillCanvas")


def paint_rye_crust():
    from PIL import Image, ImageDraw
    import random
    from atelier import RES

    width, height = 64, 48
    rng = random.Random(990)
    crust = Image.new("RGB", (width, height))
    for v in range(height):
        for u in range(width):
            rim = min(1, ((u-32)/32)**2 + ((v-22)/25)**2)
            toast = 36*rim + 22*max(0, (v-32)/15)
            fleck = rng.choice((-13,-6,-3,0,4,8,11))
            crust.putpixel((u,v), (round(192-toast+fleck),round(123-toast*.91+fleck),
                                   round(60-toast*.56+fleck*.7)))
    draw = ImageDraw.Draw(crust)
    for _ in range(78):
        u,v = rng.randrange(4,60),rng.randrange(4,41)
        draw.line([(u,v),(u+1,v)],fill=rng.choice(("#b9864e","#e4b478","#916235")))
    # The broken brick leaves a crescent on each loaf. Three lame cuts open onto the crumb.
    draw.arc((36,6,54,20), 295,120, fill="#7f492b",width=2)
    for u,v in ((14,29),(28,27),(42,25)):
        draw.polygon([(u-4,v+7),(u-1,v),(u+7,v-7),(u+3,v+2)],fill="#744326")
        draw.polygon([(u-2,v+4),(u,v),(u+5,v-5),(u+2,v+1)],fill="#f3d2a0")
        draw.line([(u-4,v+5),(u-2,v),(u+5,v-7)],fill="#dca168")
    crust.save(RES/"Textures"/"RyeCrust.png")


def bakery_chart(x, y, z):
    for side in (-1, 1):
        xx = x+side*1.36
        rod("Bread rack cheek",(xx,y+.07,z+1.7),(xx,y+.07,z+3.55),.077,"Wood")
    block("Floured mantle",(x,y-.025,z+3.43),(3.12,.57,.15),"Wood")
    # Each thin peel has a beveled shoulder, rounded blade and narrow ash handle.
    outline = [(-.065,0),(-.09,.20),(-.32,.38),(-.36,.74),(-.31,.86),
               (-.17,.94),(.17,.94),(.31,.86),(.36,.74),(.32,.38),(.09,.20),(.065,0)]
    for side in (-1,1):
        bx,by,bz = x+side*.23,y+.085+side*.09,z+3.85
        tilt = side*.64
        def place(u,v,depth):
            return (bx+u*cos(tilt)+v*sin(tilt),by+depth,bz+v*cos(tilt)-u*sin(tilt))
        rod("Ash peel handle",place(0,-.70,0),place(0,.16,0),.058,"Wood",8)
        points = [place(u*scale,v,depth) for scale,depth in ((1,-.05),(.94,.05)) for u,v in outline]
        n = len(outline)
        faces = [tuple(reversed(range(n))),tuple(range(n,2*n))]
        faces += [(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
        geometry("Carved baker's peel",points,faces,"Wood")
        for h in (.16,.30):
            rod("Peel rivet",place(0,h,-.048),place(0,h,-.067),.036,"Brass",6)
    for j,(dx,size) in enumerate(((-.87,.86),(-.15,1.02),(.70,1.13))):
        xx,cy,base = x+dx,y-.13,z+3.515
        points = []
        for height,radius in ((0,.78),(.08,1),(.18,.88),(.27,.49),(.30,.18)):
            for k in range(10):
                a = k*tau/10
                points.append((xx+size*.35*radius*cos(a),cy+size*.22*radius*sin(a),base+size*height))
        faces = [tuple(reversed(range(10))),tuple(range(40,50))]
        for ring in range(4):
            for k in range(10):
                a=10*ring+k
                b=10*ring+(k+1)%10
                faces.append((a,b,b+10,a+10))
        # Planar UVs keep the three painted cuts legible across the low-poly crown.
        # The underside and vertical heel sample the brown lower edge of the same tile.
        uv = []
        for face_index,face in enumerate(faces):
            for vertex in face:
                vx,vy,_ = points[vertex]
                u = .5+(vx-xx)/(.76*size)
                v = .5+(vy-cy)/(.48*size)
                if face_index == 0 or (2 <= face_index < 12 and vertex < 10):
                    v = .04
                uv.append((u,v))
        geometry("Baked ration loaf",points,faces,"RyeCrust",uv=uv)



CHARTS = {
    "MercySlip": shipwright_chart,
    "Wickwater": lamp_chart,
    "LinenCourt": linen_chart,
    "KiteCrag": kite_chart,
    "SoundingBay": sounding_chart,
    "SupperSteps": bakery_chart,
}
