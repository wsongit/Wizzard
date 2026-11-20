"""Moss, the Root Choir's keeper, in a moss-stained coat, field cap and Ina's red ribbon."""
import math
from mathutils import Vector
from atelier import geometry, origins

class Figure:
    def __init__(self,x,y,z,atlas):
        self.origin=(x,y,z)
        self.group='Speaker'
        self.atlas=atlas
    def joint(self,name,pivot):
        self.group=name
        origins[name]=tuple(a+b for a,b in zip(self.origin,pivot))
    def draw(self,name,points,faces,pigment):
        x,y,z=self.origin
        obj=geometry(name,[(x+a,y+b,z+c) for a,b,c in points],faces,self.atlas,self.group)
        uv=obj.data.uv_layers.active
        for f in obj.data.polygons:
            dominant=max(range(3),key=lambda j:abs(f.normal[j]))
            a,b=[(1,2),(0,2),(0,1)][dominant]
            vs=[points[obj.data.loops[li].vertex_index] for li in f.loop_indices]
            umin=min(v[a] for v in vs);umax=max(v[a] for v in vs)
            vmin=min(v[b] for v in vs);vmax=max(v[b] for v in vs)
            for li,v in zip(f.loop_indices,vs):
                u=(v[a]-umin)/max(.0001,umax-umin);h=(v[b]-vmin)/max(.0001,vmax-vmin)
                uv.data[li].uv=((pigment%4+.09+.82*u)/8,(pigment//4+.09+.82*h)/4)
        return obj
    def rings(self,name,rows,pig,n=12):
        pts=[(a+rx*math.cos(i*math.tau/n),b+ry*math.sin(i*math.tau/n),c) for a,b,c,rx,ry in rows for i in range(n)]
        faces=[tuple(reversed(range(n)))]
        for j in range(len(rows)-1):
            for i in range(n):
                v=j*n+i;w=j*n+(i+1)%n
                faces.append((v,w,w+n,v+n))
        faces.append(tuple(range(len(pts)-n,len(pts))))
        obj = self.draw(name, pts, faces, pig)
        if name in ("Weathered flight coat", "Lichen coat", "Storm coat", "Split kiln apron"):
            # Begin at the back and keep both corners of the final face on that
            # side of the seam. The motif remains centred over the front (-Y).
            side = 64 if self.atlas == "OrlaAtelier" else 128
            uv = obj.data.uv_layers.active.data
            height = rows[-1][2] - rows[0][2]
            for j in range(len(rows)-1):
                for k in range(n):
                    around = (k-round(n/4)) % n
                    face = obj.data.polygons[1+j*n+k]
                    for loop, col, row in zip(face.loop_indices,
                            (around, around+1, around+1, around), (j, j, j+1, j+1)):
                        u = (4.5 + (side-9)*col/n) / side
                        v = (4.5 + (side-9)*(rows[row][2]-rows[0][2])/height) / side
                        uv[loop].uv = (.5+.5*u, v)
        return obj
    def oval(self,name,centre,r,pig,n=10):
        a,b,c=centre;rx,ry,rz=r
        return self.rings(name,[(a,b,c+rz*k,rx*w,ry*w) for k,w in [(-1,.14),(-.69,.74),(0,1),(.68,.79),(1,.16)]],pig,n)
    def tube(self,name,a,b,r,s,pig,n=8):
        a,b=Vector(a),Vector(b);along=(b-a).normalized()
        u=along.cross(Vector((0,1,0)) if abs(along.y)<.8 else Vector((0,0,1))).normalized()
        v=along.cross(u)
        pts=[tuple(c+rad*(u*math.cos(k*math.tau/n)+v*math.sin(k*math.tau/n))) for c,rad in [(a,r),(b,s)] for k in range(n)]
        faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
        faces += [(k,(k+1)%n,(k+1)%n+n,k+n) for k in range(n)]
        return self.draw(name,pts,faces,pig)

def keeper(x,y,z):
    figure=Figure(x,y,z,'MossAtelier')
    rings,oval,tube,draw=figure.rings,figure.oval,figure.tube,figure.draw
    for side in [-1,1]:
        a=side*.129;b=side*.042
        rings('Walking boot',[(a,b-.041,.008,.096,.158),(a,b-.048,.055,.106,.166),(a,b-.042,.093,.10,.15),
                              (a,b,.180,.074,.087),(a,b+.005,.25,.079,.078)],5)
        rings('Scuffed boot cuff',[(a,b,.194,.081,.084),(a,b,.214,.09,.087),(a,b,.253,.089,.085)],2)
        rings('Wool breeches',[(a,b,.23,.072,.072),(a,b+.02,.34,.095,.10),(a*.91,b-.023,.46,.102,.103),
                              (a,b,.55,.081,.087),(a*.89,b,.68,.119,.118),(a*.83,.014,.84,.13,.119)],13)
    rings('Lichen coat',[(0,0,.65,.233,.155),(0,.02,.691,.254,.171),(.012,.02,.85,.239,.164),
          (.003,.014,.99,.207,.155),(0,.02,1.14,.239,.175),(-.01,.015,1.21,.237,.153),(-.016,0,1.26,.119,.106)],1)
    rings('Woven belt',[(.006,.02,.885,.238,.169),(.003,.015,.935,.231,.164)],4)
    oval('Leather field pouch',(.163,-.128,.836),(.078,.066,.096),2)
    oval('Pouch clasp',(.17,-.19,.87),(.019,.014,.021),10)
    rings('Weather cape',[(0,.015,1.07,.277,.19),(-.016,.013,1.16,.29,.177),
          (-.016,.001,1.25,.184,.132),(-.025,0,1.29,.128,.108)],0)
    rings('Ribbon collar',[(-.012,-.002,1.195,.16,.137),(-.014,-.006,1.22,.171,.14),(-.019,0,1.257,.15,.133)],9)
    draw('Ina’s mended ribbon',[(-.044,-.145,1.216),(.016,-.144,1.211),(.092,-.167,1.057),
        (.051,-.169,1.071),(.047,-.168,1.046),(-.017,-.154,1.141)],[(0,5,4,3,2,1)],9)
    for s in [-1,1]:
        if s>0:figure.joint('SpeakerArm',(.214,.02,1.175))
        shoulder=(s*.205,.012,1.16)
        elbow=(s*.287,-.015,1.007 if s>0 else .96)
        hand=(s*(.235 if s>0 else .30),-.179 if s>0 else -.10,1.026 if s>0 else .806)
        tube('Rainproof sleeve',shoulder,elbow,.097,.082,1,10)
        tube('Gathered sleeve',elbow,hand,.085,.059,0,10)
        oval('Moss’s hand',hand,(.060,.058,.073),3)
        oval('Curled thumb',(hand[0]-s*.047,hand[1]-.025,hand[2]+.009),(.027,.033,.042),3)
        if s>0:
            tube('Copper tuning peg',(.234,-.17,.99),(.228,-.199,1.225),.013,.017,10)
            oval('Wooden striker head',(.228,-.20,1.233),(.045,.036,.033),5)
        figure.group='Speaker'
    figure.joint('SpeakerHead',(-.021,.002,1.264))
    rings('Moss’s face',[(-.02,-.03,1.24,.077,.087),(-.014,-.036,1.275,.111,.111),
          (-.018,-.023,1.34,.149,.143),(-.02,-.015,1.42,.167,.143),(-.02,.001,1.49,.158,.145),
          (-.025,.013,1.56,.133,.120),(-.025,.015,1.595,.08,.082)],3,16)
    for s in [-1,1]:
        oval('Ear',(-.019+s*.156,-.012,1.391),(.037,.038,.047),3)
        oval('Silver temple',(-.02+s*.136,.024,1.459),(.053,.081,.075),7)
        oval('Eye',(-.022+s*.061,-.144,1.423),(.034,.012,.021),14,12)
        oval('Dark iris',(-.022+s*.061+.002,-.156,1.425),(.015,.005,.018),11)
        oval('Catchlight',(-.024+s*.061,-.160,1.433),(.0048,.003,.005),14,8)
        tube('Silver brow',(-.02+s*.029,-.152,1.459),(-.02+s*.098,-.135,1.451),.014,.009,7)
        tube('Crease below the eye',(-.02+s*.054,-.148,1.388),(-.02+s*.107,-.127,1.39),.004,.002,15,6)
    oval('Windworn nose',(-.022,-.156,1.388),(.038,.042,.046),12)
    tube('Crooked smile',(-.07,-.151,1.336),(.001,-.161,1.332),.005,.007,15,7)
    tube('Smile corner',(.001,-.161,1.332),(.033,-.151,1.345),.007,.003,15,7)
    rings('Travelling cap',[(-.014,.006,1.477,.187,.162),(-.025,.006,1.526,.197,.171),
          (-.075,.026,1.591,.164,.135),(-.126,.03,1.621,.094,.083),(-.179,.011,1.601,.044,.05)],1,14)
    rings('Turned cap band',[(-.018,0,1.479,.186,.163),(-.018,-.003,1.498,.203,.173),
          (-.025,0,1.528,.195,.165)],0,14)
    oval('Copper leaf brooch',(-.168,-.108,1.512),(.03,.015,.031),10)
    for i in range(2):
        tube('Reeds in the cap',(-.162+i*.014,-.10,1.523),(-.189-.023*i,-.091,1.659+.030*i),.014,.003,8,6)
