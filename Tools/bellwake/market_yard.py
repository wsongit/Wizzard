"""Two articulated marsh hens in the market's open drying yard. Local coordinates are in metres."""
import math, random
from atelier import block, geometry, shaft, origins, marker
from PIL import Image
from pathlib import Path

def plumage(out):
    shades=[(184,141,87),(104,105,95),(180,58,42),(206,157,68),(225,205,149),(82,64,50),
            (35,39,37),(244,226,166),(90,74,58),(150,120,78),(206,180,126),(120,90,62),
            (137,130,112),(79,84,86),(175,158,131),(101,75,54)]
    im=Image.new("RGB",(64,64))
    rng=random.Random(1091)
    for k, colour in enumerate(shades):
        for y in range(16):
            for x in range(16):
                # Layer small curved scallops from tail to breast.
                dx=(x+(y//5%2)*4)%8-3.5
                lip=(y-round(2*(dx/4)**2))%5
                shade=1+rng.uniform(-.055,.055)
                if k in (0,1,4,8,9,10,12,13,14):
                    shade+=.12 if lip==0 else -.13 if lip==4 else 0
                im.putpixel((16*(k%4)+x,16*(3-k//4)+y),tuple(min(255,round(v*shade)) for v in colour))
    im.save(out/"YardFowl.png")

def bird(label,x,y,scale,variant):
    def bulb(name,rows,pigment,part="",sides=10):
        pts=[]
        for cx,cy,cz,rx,ry in rows:
            for i in range(sides):
                a=math.tau*i/sides
                pts.append((x+scale*(cx+rx*math.cos(a)),y+scale*(cy+ry*math.sin(a)),scale*cz))
        faces=[tuple(reversed(range(sides)))]
        for j in range(len(rows)-1):
            for i in range(sides):
                a=j*sides+i;b=j*sides+(i+1)%sides
                faces.append((a,b,b+sides,a+sides))
        faces.append(tuple(range(len(pts)-sides,len(pts))))
        uv=[]
        for f,face in enumerate(faces):
            for v in face:
                a=math.tau*(v%sides)/sides
                if f==0 or f==len(faces)-1:u,h=.5+.48*math.cos(a),.5+.48*math.sin(a)
                else:
                    u=(v%sides)/sides;h=(v//sides)/(len(rows)-1)
                    if (f-1)%sides==sides-1 and u==0:u=1
                uv.append(((pigment%4+(1+14*u)/16)/4,(pigment//4+(1+14*h)/16)/4))
        return geometry(name,pts,faces,"YardFowl",label+part,uv)
    def egg(name,c,r,ink,part=""):
        a,b,h=c;w,d,hh=r
        return bulb(name,[(a,b,h+t*hh,w*k,d*k) for t,k in [(-1,.16),(-.62,.81),(0,1),(.63,.79),(1,.14)]],ink,part)
    # An asymmetric, low breast, fan tail and arched neck give each bird a silhouette at fence height.
    bulb("Marsh hen breast",[(0,.02,.21,.105,.15),(0,.025,.26,.197,.28),(0,0,.41,.219,.30),
         (0,-.015,.54,.181,.246),(0,-.105,.61,.115,.12)],0 if variant==0 else 12)
    for s in (-1,1):
        bulb("Folded flight feathers",[(s*.15,.15,.27,.034,.10),(s*.174,.06,.34,.063,.21),
             (s*.167,-.005,.46,.073,.22),(s*.157,-.06,.52,.046,.14)],1 if variant==0 else 8)
    for i in range(3):
        q=i-1
        bulb("Curved fan feather",[(q*.049,.20,.32,.05,.09),(q*.074,.29,.43,.056,.085),
             (q*.11,.39,.58,.063,.077),(q*.125,.42,.67-abs(q)*.035,.014,.034)],8+i)
    egg("Ruff",(0,-.145,.57),(.131,.14,.135),4 if variant==0 else 14)
    bulb("Hen head",[(0,-.17,.51,.077,.085),(0,-.18,.59,.116,.114),(0,-.205,.69,.117,.112),
         (0,-.197,.755,.075,.075),(0,-.19,.775,.031,.048)],4 if variant==0 else 10,"Head")
    for q in [-1,1]:
        egg("Hen eye",(q*.099,-.251,.689),(.023,.025,.026),6,"Head")
        egg("Hen catchlight",(q*.116,-.257,.699),(.008,.009,.009),7,"Head")
    bulb("Beak",[(0,-.252,.610,.029,.046),(0,-.287,.637,.061,.090),(0,-.252,.660,.038,.055)],3,"Head",6)
    egg("Wattle",(0,-.274,.584),(.027,.040,.055),2,"Head")
    for k in range(3):
        egg("Crown comb",(0,-.237+k*.041,.764),(.025,.043,.043+.012*k),2,"Head")
    for q,part in [(-1,"Left"),(1,"Right")]:
        bulb("Short shank",[(q*.079,-.01,-.004,.019,.019),(q*.082,.005,.076,.027,.024),
             (q*.086,.013,.224,.035,.031)],3,part,6)
        for toe in [-1,0,1]:
            bulb("Fanned toe",[(q*.082+toe*.033,-.061,-.005,.017,.064),
                 (q*.082+toe*.020,-.034,.018,.014,.049)],3,part,6)
        origins[label+part]=(x+q*.086*scale,y+.013*scale,.209*scale)
    # The far bird keeps its arched neck, comb, pointed bill and split tail in a single draw.
    def distant(name, rings, pigment, sides):
        return bulb(name, rings, pigment, "Far", sides)
    distant("Distant breast", [(0,.045,.21,.10,.16),(0,.025,.39,.22,.30),
             (0,-.09,.58,.13,.185)], 0 if variant==0 else 12, 7)
    distant("Distant mantle", [(0,-.14,.48,.10,.11),(0,-.20,.65,.12,.12),
             (0,-.21,.75,.074,.081)], 4 if variant==0 else 14, 6)
    distant("Distant red comb", [(0,-.20,.735,.026,.081),(0,-.18,.80,.018,.048)], 2, 5)
    distant("Distant bill", [(0,-.35,.62,.020,.026),(0,-.265,.65,.062,.057)], 3, 5)
    for side in (-1,1):
        distant("Distant tail", [(side*.05,.19,.32,.084,.08),
                 (side*.065,.365,.52,.063,.063),(side*.072,.406,.60,.030,.033)], 1 if variant==0 else 8, 5)
        distant("Distant shank", [(side*.084,-.014,-.002,.021,.041),
                 (side*.084,.015,.23,.026,.031)], 3, 5)
    origins[label+"Far"]=(x,y,0)
    origins[label]=(x,y,0)
    origins[label+'Head']=(x,y-.145*scale,.544*scale)
    marker(label+"Trail",x,y-1.55,0)

def drying_yard():
    # One broad opening faces the street. All of the fence posts and both bird trails stand on flat turf.
    x,y=-13.95,-8.5
    perimeter=[(x+2.45,y-1.38),(x+2.45,y-2.35),(x,y-2.35),(x-2.5,y-2.35),
               (x-2.5,y),(x-2.5,y+2.35),(x,y+2.35),(x+2.45,y+2.35),(x+2.45,y+1.10)]
    for px,py in perimeter:
        block("Split oak fence post",(px,py,.45),(.16,.17,1.14),"Wood")
    for a,b in zip(perimeter,perimeter[1:]):
        for z in (.30,.68):
            shaft("Wattle yard rail",(*a,z),(*b,z+.015),.072,.063,"Wood",5)
    bird("MarshHen",x-.92,y+.65,.99,0)
    bird("ReedHen",x+.80,y+.90,.82,1)
