"""Trade-specific measuring tools fixed to three survey frames on the Mercy Run."""
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


CHARTS={"LinenCourt":linen_chart,"KiteCrag":kite_chart,"SoundingBay":sounding_chart}
