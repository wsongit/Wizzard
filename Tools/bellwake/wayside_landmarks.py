"""Six silhouettes to steer by across the watershed. All dimensions are in metres."""
import math
from atelier import lathe, shaft, block, geometry
from watershed import height

def beacon(x,y,z):
    lathe("Whitecap lighthouse",x,y,z,[(4,0),(4.1,1.5),(3.3,2),(2.3,13.8),(3,14),(3,14.6)],"Masonry",10)
    lathe("Beacon panes",x,y,z+14.6,[(2.2,0),(2.2,2.2)],"Amber",8)
    for i in range(8):
        a=i*math.tau/8
        dx,dy=2.2*math.cos(a),2.2*math.sin(a)
        shaft("Lantern mullion",(x+dx,y+dy,z+14.5),(x+dx,y+dy,z+16.9),.12,.1,"BellMetal",5)
    lathe("Beacon cowl",x,y,z+16.8,[(3,0),(2.8,.4),(.35,2.3),(.10,3)],"RoofSlate",8)

def lock(x,y,z):
    for dx in (-4.4,4.4):
        lathe("Tide gate pier",x+dx,y,z,[(1.5,0),(1.2,3.2),(.8,8.8),(1,9.1)],"HarbourBrick",6)
    block("Lock beam",(x,y,z+8.8),(11,1.1,1.1),"Wood")
    for dy in (-1,1):
        shaft("Wheel bearing",(x,y+dy*1.8,z+3.9),(x,y+dy*.3,z+3.9),.5,.46,"BellMetal")
    for i in range(12):
        a=i*math.tau/12
        tip=(x+3.6*math.sin(a),y,z+3.9+3.6*math.cos(a))
        shaft("Overshot wheel spoke",(x,y,z+3.9),tip,.14,.11,"Wood",5)
        b=(i+1)*math.tau/12
        shaft("Wheel rim",tip,(x+3.6*math.sin(b),y,z+3.9+3.6*math.cos(b)),.28,.28,"Wood",5)
        shaft("Paddle",(tip[0],y-.95,tip[2]),(tip[0],y+.95,tip[2]),.3,.3,"Wood",4)

def windmill(x,y,z):
    lathe("Windmill footing",x,y,z,[(4.3,0),(4.2,1.2),(3.85,1.6)],"Masonry",10)
    lathe("Windmill drum",x,y,z+1.4,[(3.86,0),(3.32,7.3),(2.96,11.2)],"HousePlaster",10)
    for h,r in [(2.1,3.86),(7.5,3.5),(12.4,3.16)]:
        lathe("Mill timber band",x,y,z+h,[(r,0),(r,.37)],"Wood",10)
    lathe("Mill cap",x,y,z+12.55,[(3.6,0),(3.45,.6),(1.9,2.17),(.15,2.8)],"RoofTiles",10)
    hub=(x,y-3.9,z+10.7)
    shaft("Millshaft",(x,y-2.1,z+10.25),hub,.62,.53,"Wood",8)
    for i in range(4):
        a=.52+i*math.pi/2
        def point(r,w=0):
            return (hub[0]+r*math.sin(a)+w*math.cos(a),hub[1],
                    hub[2]+r*math.cos(a)-w*math.sin(a))
        shaft("Sail spar",point(0),point(8.1),.16,.1,"Wood",5)
        corners=[point(2.45,.06),point(8.0,.06),point(8,1.38),point(2.45,.88)]
        geometry("Reefed sail cloth",corners,[(0,1,2,3)],"MillCanvas",uv=[(0,0),(0,1),(1,1),(1,0)])
        for r in (2.5,4.3,6.1,7.95):
            shaft("Sail batten",point(r,-.08),point(r,.88+(r-2.45)*.09),.065,.06,"Wood",4)

def elder(x,y,z):
    lathe("Old waytree",x,y,z,[(3.2,0),(1.8,1.9),(1.15,5.4),(.65,9.3)],"Wood",7)
    for i in range(7):
        a=.45+i*math.tau/7
        sx,sy=math.cos(a),math.sin(a)
        ex,ey=x+sx*(4+i%2),y+sy*(4+i%2)
        end=z+9+i%3
        shaft("Bough",(x+sx*.6,y+sy*.6,z+4+i*.3),(ex,ey,end),.65,.27,"Wood",6)
        lathe("Elder crown",ex,ey,end-.5,[(1,0),(3.6,1.6),(3,3.8),(.55,4.9)],"Leaves",7)
    lathe("Elder upper crown",x,y,z+9,[(1.8,0),(4.6,2.2),(2.9,5.1),(.5,5.8)],"Leaves",7)

def kilns(x,y,z):
    for i,(dx,dy) in enumerate(((-3,0),(2,2),(5,-2))):
        scale=1-.17*i
        lathe("Bottle kiln",x+dx,y+dy,z,[(r*scale,h*scale) for r,h in
              [(2.7,0),(2.8,3.8),(1.25,6.7),(.98,12.7),(1.25,13),(1.24,13.45)]],"HarbourBrick",8)

def belfry(x,y,z):
    for dx in (-3.1,3.1):
        lathe("Bell tower buttress",x+dx,y,z,[(2.1,0),(1.4,3.5),(1.2,14.8),(1.6,15.3)],"Masonry",5)
    block("Headstock shelter",(x,y,z+15.4),(8.7,3.9,1.25),"Wood")
    lathe("Wild bell",x,y,z+9,[(2.25,0),(2.1,.4),(1.3,.9),(.95,3.6),(.27,4.2)],"BellMetal",10)
    shaft("Wild bell hanging bolt",(x,y,z+13),(x,y,z+15.1),.19,.22,"BellMetal",6)
    lathe("Spire",x,y,z+16,[(4.5,0),(2.8,1),(.35,6),(.06,7)],"RoofSlate",4)

def build(row,x,y):
    (beacon,lock,windmill,elder,kilns,belfry)[row](x,y,height(x,y)-.75)
