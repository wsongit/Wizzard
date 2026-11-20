"""Reedwater's working low-breast wheel with fourteen paddles and fixed bearings."""
import math
from atelier import geometry,shaft,block,origins,marker

def build():
    x,y,z=11.6,4.4,2.28
    group="MillWheel"
    def at(ax,r,angle):
        return (x+ax,y+r*math.sin(angle),z+r*math.cos(angle))
    def segment(name,low,high,inner,outer,a,b,wood,part):
        pts=[at(ax,r,t) for ax in (low,high) for r,t in [(inner,a),(outer,a),(outer,b),(inner,b)]]
        faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
        return geometry(name,pts,faces,wood,part)
    for side in [-1,1]:
        ax=1.7*side
        block('Sluice bearing footing',(x+ax,y,.32),(.39,1.59,.76),'GateStone')
        for dy in (-.62,.62):
            shaft('Splayed bearing trestle',(x+ax,y+dy,.56),(x+ax,y,z),.135,.12,'Wood',8)
        block('Capped axle saddle',(x+ax,y,z-.045),(.37,.46,.37),'Wood')
        shaft('Copper bearing',(x+ax-.21,y,z),(x+ax+.21,y,z),.142,.142,'Brass',12)
    shaft('Square mill spindle',(x-2.04,y,z),(x+2.04,y,z),.093,.093,'BellMetal',8)
    for i in range(14):
        a=i*math.tau/14;b=(i+1)*math.tau/14
        for side in [-1,1]:
            ax=side*.35
            segment('Adzed wooden felloe',ax-.057,ax+.057,1.62,1.83,a,b,'Wood',group)
            if i%2==0:
                shaft('Wheel spoke',at(ax,.14,a),at(ax,1.75,a),.085,.082,'Wood',7,group)
        segment('Broad paddle board',-.435,.435,1.63,2.17,a-.026,a+.026,'TarredOak',group)
        # Fourteen metal shoes bind the wet outer end-grain.
        segment('Paddle tip binding',-.444,.444,2.13,2.18,a-.032,a+.032,'BellMetal',group)
    shaft('Wheel nave',(x-.48,y,z),(x+.48,y,z),.216,.216,'Wood',14,group)
    for side in [-1,1]:
        ax=.39*side
        shaft('Nave band',(x+ax-.044,y,z),(x+ax+.044,y,z),.228,.228,'Brass',14,group)
    origins[group]=(x,y,z)
    marker("WheelAxle",x+1,y,z)
    # A single closed, stationary contact shell fills the sweep between the paddle tips.
    # Both hands meet the same surface while the visible paddles rotate.
    # Circumscribe the sweep so paddle tips stay inside the flats at every angle.
    clearance=2.18/math.cos(math.pi/24)+.001
    shaft('Mill wheel contact drum',(x-.447,y,z),(x+.447,y,z),clearance,clearance,'Masonry',24,'C_Solids')
    shaft('Axle cap contact',(x-.481,y,z),(x+.481,y,z),.232,.232,'Masonry',16,'C_Solids')
