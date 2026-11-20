"""Blender 4.3: blender -b --python-exit-code 1 --python Tools/bellwake/wayfarer_art.py"""
import bpy, math, sys
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parents[2]
res=root/'Assets/Resources/Bellwake'
out=res/'Wayfarer'
out.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
materials={}
groups={}
def paint(name):
    if name not in materials:
        m=bpy.data.materials.new(name); m.use_nodes=True
        tex=m.node_tree.nodes.new('ShaderNodeTexImage')
        tex.image=bpy.data.images.load(str(res/'Textures'/(name+'.png')));tex.image.pack();tex.interpolation='Closest'
        bs=m.node_tree.nodes.get('Principled BSDF')
        m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
        bs.inputs['Roughness'].default_value=.93
        materials[name]=m
    return materials[name]
def mesh(name, rows, ink, sides=16, smooth=True, phase=0):
    # Each section shares a ring of vertices with its neighbours. No intersecting cylinder pieces.
    pts=[];faces=[]
    for x,y,z,rx,ry in rows:
        for k in range(sides):
            a=math.tau*k/sides+phase
            pts.append((rx*math.cos(a)+x,ry*math.sin(a)+y,z))
    faces.append(tuple(reversed(range(sides))))
    for j in range(len(rows)-1):
        for i in range(sides):
            a=j*sides+i;b=j*sides+(i+1)%sides
            faces.append((a,b,b+sides,a+sides))
    faces.append(tuple(range(len(pts)-sides,len(pts))))
    data=bpy.data.meshes.new(name);data.from_pydata(pts,[],faces);data.update()
    o=bpy.data.objects.new(name,data);group.objects.link(o);data.materials.append(paint(ink))
    uv=data.uv_layers.new()
    for f in data.polygons:
        f.use_smooth=smooth and 0<f.index<len(faces)-1
        for j,li in enumerate(f.loop_indices):
            v=data.loops[li].vertex_index
            if f.index in (0,len(faces)-1):
                a=math.tau*(v%sides)/sides+phase
                uv.data[li].uv=(.5+.5*math.cos(a),.5+.5*math.sin(a))
                continue
            u=(v%sides)/sides
            if f.index not in (0,len(faces)-1) and (f.index-1)%sides==sides-1 and u==0:u=1
            uv.data[li].uv=(u,(v//sides)/(len(rows)-1))
    return o
def oval(n,x,y,z,w,d,h,m):
    return mesh(n,[(x,y,z+t*h,w*r,d*r) for t,r in [(-1,.12),(-.82,.58),(-.42,.91),(0,1),(.42,.91),(.82,.58),(1,.12)]],m)
def stem(n,a,b,r,s,m):
    length=(Vector(b)-Vector(a)).length
    o=mesh(n,[(0,0,0,r,r),(0,0,length,s,s)],m,12)
    o.location=a;o.rotation_euler=(Vector(b)-Vector(a)).to_track_quat('Z','Y').to_euler()
    return o
def begin(name):
    global group
    group=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(group);groups[name]=group
def pivot(o,p):
    from mathutils import Matrix
    o.data.transform(Matrix.Translation(-Vector(p)));o.location=p
begin('Bellrunner')
mesh('Pear-shaped coat',[(0,0,-.23,.11,.09),(0,0,-.15,.19,.145),(0,0,.01,.235,.16),(0,0,.125,.215,.13),(0,0,.19,.12,.09)],'Fur')
oval('Bib',0,-.13,-.015,.145,.04,.14,'Skin')
mesh('Woven collar',[(0,0,.105,.213,.146),(0,0,.135,.211,.141),(0,0,.177,.154,.12)],'SeaCloth')
oval('Bell pin',.075,-.137,.119,.031,.012,.037,'Brass')
for s,n in [(-1,'Left'),(1,'Right')]:
    o=mesh(n+'Boot',[(s*.106,-.028,-.36,.053,.077),(s*.105,-.044,-.339,.072,.093),(s*.103,-.026,-.29,.061,.075),(s*.105,0,-.24,.041,.044),(s*.101,0,-.187,.048,.05)],'RoofSlate')
    pivot(o,(s*.101,0,-.187))
begin('RunnerHead')
oval('Crown',0,.012,.13,.153,.137,.143,'Fur')
oval('Soft muzzle',0,-.094,.103,.098,.073,.07,'Skin')
for s in [-1,1]:
    oval('Ear',s*.14,.004,.16,.05,.034,.063,'Fur')
    oval('Bright eye',s*.059,-.111,.164,.024,.017,.029,'RoofSlate')
    oval('Catchlight',s*.059-.005,-.126,.174,.008,.005,.009,'Amber')
begin('LanternMoth')
# A pointed forewing and a scalloped hindwing share a single hinged shell on each side.
oval('Velvet head',0,-.077,.012,.049,.051,.045,'ElderBark')
oval('Lantern thorax',0,-.008,.011,.063,.088,.052,'Brass')
oval('Lantern abdomen',0,.086,-.008,.052,.085,.043,'MothLamp')
for side,name in [(-1,'Left'),(1,'Right')]:
    x=side
    stem('Feeler base',(x*.018,-.096,.036),(x*.049,-.143,.081),.006,.004,'Brass')
    stem('Bent feeler',(x*.049,-.143,.081),(x*.093,-.162,.092),.004,.002,'Brass')
    oval('Moth eye',x*.035,-.106,.018,.012,.016,.015,'RoofSlate')
    outline=[(.034,-.052,.016),(.12,-.093,.04),(.224,-.102,.059),(.301,-.073,.08),
             (.268,-.021,.071),(.204,.031,.062),(.156,.055,.046),(.212,.065,.052),
             (.22,.097,.063),(.181,.116,.049),(.15,.116,.045),(.125,.135,.036),
             (.089,.113,.028),(.05,.064,.021)]
    n=len(outline)
    pts=[(x*u,v,w+dz) for dz in (-.009,.009) for u,v,w in outline]
    # The lower and upper polygon share a thin band of faces. Give the thin edge its own UV area.
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces.extend((i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n))
    data=bpy.data.meshes.new(name+' scales');data.from_pydata(pts,[],faces);data.update()
    wing=bpy.data.objects.new(name+'Wing',data);group.objects.link(wing);data.materials.append(paint('MothWing'))
    uv=data.uv_layers.new()
    for face in data.polygons:
        for j,li in enumerate(face.loop_indices):
            i=data.loops[li].vertex_index%n
            u,v,w=outline[i]
            uv.data[li].uv=((u-.028)/.284,(v+.109)/.25) if face.index<2 else [(0,.02),(.4,.02),(.4,.08),(0,.08)][j]
    if side<0:
        for face in data.polygons:face.flip()
    pivot(wing,(x*.034,0,.013))
begin('GroveBank')
bank=mesh('Bellroot clearing',[(0,0,-1.3,12,10),(0,0,-.33,13,11),(0,0,-.07,5.3,4),(0,0,0,2.86,1.57)],'ChoirLoam',32)
for v in bank.data.vertices:
    px,py,pz=v.co
    if v.index//32 in (1,2):
        behind=max(0,min(1,(py-.7)/6))
        v.co.z+=behind*((.64+.28*math.cos(.61*px)) if v.index//32==2 else (2.1+.57*math.sin(.42*px)+.36*math.cos(.87*px)))
bank.data.update()
from mathutils.bvhtree import BVHTree
bank_tree=BVHTree.FromPolygons([v.co for v in bank.data.vertices],[f.vertices[:] for f in bank.data.polygons])
def soil(x,y):
    return bank_tree.ray_cast((x,y,8),(0,0,-1))[0].z
for face in bank.data.polygons:
    if face.index==0:continue
    for li in face.loop_indices:
        v=bank.data.vertices[bank.data.loops[li].vertex_index].co
        bank.data.uv_layers.active.data[li].uv=(v.x*.75,v.y*.75)
def foliage(name,x,y,z,rx,ry,h,seed):
    from random import Random
    r=Random(seed); sides=8
    o=mesh(name,[(x+.04*rx,y,z-h*.53,rx*.42,ry*.44),(x-.06*rx,y,z-h*.23,rx*.91,ry*.93),
                 (x,y+.05*ry,z+h*.12,rx,ry),(x+.08*rx,y,z+h*.37,rx*.73,ry*.71),
                 (x+.15*rx,y,z+h*.53,rx*.24,ry*.27)],'ElderLeaf',sides,False,seed*.28)
    for vert in o.data.vertices:
        v=vert.co
        v.x=x+(v.x-x)*r.uniform(.90,1.11);v.y=y+(v.y-y)*r.uniform(.89,1.10)
        v.z+=r.uniform(-.065,.065)*h
    o.data.update()
    layer=o.data.uv_layers.active
    for face in o.data.polygons:
        axis=max(range(3),key=lambda i:abs(face.normal[i]))
        u,v=[(1,2),(0,2),(0,1)][axis]
        for li in face.loop_indices:
            pos=o.data.vertices[o.data.loops[li].vertex_index].co
            layer.data[li].uv=(pos[u]*.73,pos[v]*.73)
    return o

# Birch and elder saplings form a shallow horseshoe at the back of the opening stage.
for i,(x,y,h) in enumerate([(-6,4,3.9),(-4.3,6.1,4.7),(-2.3,5.9,3.3),(-.4,7.2,4.6),
                             (2.6,6.4,3.8),(5.1,4.9,4.1),(6.5,2.9,3.0)]):
    z=soil(x,y); lean=.15*math.sin(i*2.8)
    stem('Coppice trunk',(x,y,z-.23),(x+lean,y,z+h*.69),.23,.093,'ElderBark')
    for j in range(3):
        a=i*2.2+j*2.1
        dx,dy=.6*math.cos(a),.57*math.sin(a)
        base=z+h*(.56+.10*j)
        stem('Forked sapling',(x+lean,y,z+h*.37),(x+dx,y+dy,base),.115,.047,'ElderBark')
        foliage('Leaves at dawn',x+dx,y+dy,base+.33,h*(.30-.017*j),h*.26,h*.45,35+i*3+j)
sys.path.insert(0,str(Path(__file__).resolve().parent))
from title_clearing import landscape
landscape(bank,group,paint,stem,foliage)
begin('Bellroot')
mesh('Fluted elder trunk',[(0,0,-.45,1.38,1.29),(0,0,.1,1.22,1.12),(.12,0,.85,.79,.74),
     (.17,.06,1.58,.66,.65),(.24,.12,2.22,.59,.54),(.04,.17,3.8,.4,.37)],'ElderBark',16)
for i in range(7):
    a=i*math.tau/7+.14*math.sin(i*1.8);dy,dx=math.sin(a),math.cos(a)
    z=2.68+(i%3)*.42; reach=1.26+.36*math.sin(i*2)
    base=(.15,.10,1.52+i*.145); fork=(.72*dx,.74*dy,2.13+i*.11)
    end=(reach*dx,reach*dy,z+.43)
    stem('Crooked shoulder',base,fork,.315,.235,'ElderBark')
    stem('Forked arm',fork,end,.247,.085,'ElderBark')
    stem('Spur',fork,(end[0]-.39*dy,end[1]+.39*dx,z+.47),.166,.055,'ElderBark')
    foliage('Elder crown',end[0],end[1],z+.76,1.30,.96,1.67,10+i)
    stem('Root buttress',(.51*dx,.51*dy,.60),(1.1*dx,1.1*dy,.11),.34,.21,'ElderBark')
    stem('Trailing root',(1.1*dx,1.1*dy,.13),(1.64*dx+.13*dy,1.64*dy,-.115),.21,.071,'ElderBark')
foliage('Upper crook',-.22,.23,4.77,1.50,1.21,1.69,32)
for side in [-1,1]:
    x=side*.30
    oval('Hollow eye socket',x,-.591,1.48,.163,.079,.108,'RoofSlate')
    oval('Amber iris',x,-.661,1.48,.078,.029,.078,'Brass')
    oval('Old pupil',x+.012,-.688,1.472,.032,.015,.046,'RoofSlate')
    oval('Amber glint',x-.003,-.699,1.505,.017,.008,.017,'MothLamp')
    stem('Bark brow',(side*.12,-.626,1.66),(side*.52,-.55,1.55),.113,.065,'ElderBark')
mesh('Nose knot',[(.025,-.638,1.05,.105,.09),(.03,-.65,1.11,.132,.129),
                  (.03,-.62,1.24,.09,.081),(.05,-.59,1.38,.051,.057)],'ElderBark',9)
oval('Mouth hollow',.04,-.741,.897,.16,.044,.046,'RoofSlate')
stem('Chin ledge',(-.12,-.725,.862),(.18,-.711,.85),.049,.042,'ElderBark')
begin('TollSword')
mesh('Leaf blade',[(0,0,.1,.043,.014),(0,0,.18,.065,.018),(0,0,.55,.045,.018),(0,0,.74,.005,.003)],'RiverSteel',4,False)
mesh('Crossguard',[(0,0,.065,.098,.023),(0,0,.101,.129,.026),(0,0,.125,.083,.021)],'Brass')
stem('Wrapped grip',(0,0,-.145),(0,0,.08),.023,.021,'Wood')
oval('Pommel',0,0,-.148,.04,.035,.044,'Brass')
for z in [-.112,-.086,-.060,-.034,-.008,.018]:
    mesh('Grip ferrule',[(0,0,z,.024,.024),(0,0,z+.006,.024,.024)],'SeaCloth',8)
for side in [-1,1]:
    stem('Swept quillon',(side*.052,0,.10),(side*.122,.005,.143),.018,.011,'Brass')
begin('FerryShield')
o=mesh('Kite shield',[(0,0,-.24,.012,.018),(0,0,-.07,.155,.038),(0,0,.105,.186,.044),(0,0,.18,.145,.036),(0,0,.22,.06,.026)],'Wood',12)
o.data.materials.append(paint('FerryShieldFace'))
for face in o.data.polygons:
    if face.normal.y>-.3:continue
    face.material_index=1
    for li in face.loop_indices:
        v=o.data.vertices[o.data.loops[li].vertex_index].co
        o.data.uv_layers.active.data[li].uv=(.5+v.x/.384,(v.z+.25)/.488)
oval('Boss',0,-.036,.05,.081,.042,.081,'Brass')
for s in [-1,1]:stem('Edge binding',(0,0,-.23),(s*.155,0,-.04),.009,.012,'BellMetal')
for side in [-1,1]:
    stem('Upper rim',(side*.153,0,-.045),(side*.176,0,.115),.010,.012,'BellMetal')
    stem('Crest rim',(side*.176,0,.115),(side*.057,0,.212),.012,.008,'BellMetal')
    for height in [-.02,.13]:oval('Punched copper rivet',side*.132,-.026,height,.014,.009,.014,'Brass')
begin('ReedStaff')
stem('Reedwood shaft',(0,0,-.34),(0,0,.58),.023,.032,'Wood')
mesh('Staff socket',[(0,0,.55,.031,.031),(0,0,.58,.052,.052),(0,0,.61,.041,.041)],'Brass',9)
for i in range(4):
    a=math.tau*i/4+.42
    joint=(.081*math.cos(a),.081*math.sin(a),.683)
    stem('Chime cradle',(.03*math.cos(a),.03*math.sin(a),.59),joint,.010,.012,'Brass')
    stem('Chime crook',joint,(.019*math.cos(a),.019*math.sin(a),.789),.012,.009,'Brass')
mesh('Chime crown',[(0,0,.775,.031,.031),(0,0,.793,.035,.035),(0,0,.817,.011,.011)],'RiverSteel',8)
stem('Chime suspension',(0,0,.786),(0,0,.711),.005,.004,'Brass')
oval('River droplet',0,0,.68,.031,.031,.047,'SeaGlass')
for height in [.14,.18,.22,.26]:
    mesh('Twine collar',[(0,0,height,.032,.032),(0,0,height+.012,.033,.033)],'SeaCloth',8)
begin('RillBeetle')
pivot(oval('Shell',0,0,.244,.28,.36,.187,'KilnGlaze'),(0,0,.244))
oval('Face',0,-.28,.19,.18,.16,.135,'BellMetal')
for s in [-1,1]:
    oval('Eye',s*.105,-.407,.219,.04,.03,.042,'Amber')
    for j in range(3):
        stem('Foot',(s*.17,(j-1)*.19,.19),(s*.31,(j-1)*.24,.012),.043,.026,'Wood')
begin('MireSkipper')
oval('Speckled hide',0,.04,.166,.255,.32,.143,'MossRock')
pivot(oval('Broad jaw',0,-.17,.19,.25,.21,.12,'Leaves'),(0,-.10,.19))
for s in [-1,1]:
    oval('Eye ridge',s*.13,-.18,.285,.075,.087,.088,'Leaves')
    oval('Golden iris',s*.14,-.247,.3,.043,.025,.039,'Amber')
    oval('Long haunch',s*.226,.155,.116,.103,.17,.106,'Moss')
    stem('Webbed foot',(s*.22,.16,.064),(s*.36,-.08,.016),.052,.033,'Leaves')
begin('Waystall')
for s in [-1,1]:
    for t in [-1,1]:stem('Oak post',(s*.81,t*.37,-.45),(s*.81,t*.37,1.86),.07,.061,'Wood')
mesh('Counter',[(0,0,.71,1.45,.73),(0,0,.82,1.45,.73)],'Wood',4,False,math.pi/4)
mesh('Linen canopy',[(0,0,1.77,1.62,.94),(0,0,1.94,1.53,.87),(0,0,2.23,.35,.29)],'Awning',4,False,math.pi/4)
# Closed canvas hems hang above the player and a signed board faces the queue at the counter end.
for i in range(6):
    x=-.96+i*.385
    mesh('Canopy scallop',[(x,-.612,1.655,.157,.021),(x,-.612,1.695,.236,.024),
                           (x,-.612,1.785,.236,.025)],'Awning' if i%2 else 'SeaCloth',4,False,math.pi/4)
stem('Sign bracket',(-.81,-.38,1.68),(-.81,-.61,1.58),.032,.022,'Wood')
for x in [-.925,-.695]:
    stem('Sign cord',(x,-.608,1.60),(x,-.608,1.505),.009,.009,'Brass')
# Give each side of the sign a complete square of enamel. Side edges are plain timber.
pts=[(x,y,z) for y in (-.635,-.584) for z in (1.206,1.514) for x in (-.977,-.643)]
faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
data=bpy.data.meshes.new('Provisioner shingle');data.from_pydata(pts,[],faces);data.update()
sign=bpy.data.objects.new('Ferry enamel sign',data);group.objects.link(sign)
for ink in ['FerryEnamel','Wood']:data.materials.append(paint(ink))
uv=data.uv_layers.new()
for face in data.polygons:
    face.material_index=int(face.index>1)
    for j,li in enumerate(face.loop_indices):
        v=data.vertices[data.loops[li].vertex_index].co
        uv.data[li].uv=((v.x+.977)/.334,(v.z-1.206)/.308) if face.index<2 else [(0,0),(1,0),(1,.25),(0,.25)][j]
begin('MarketPear')
mesh('Honey pear',[(0,0,0,.026,.024),(0,0,.015,.055,.05),(0,0,.053,.071,.066),
     (0,0,.086,.056,.053),(.006,0,.118,.032,.030),(.011,0,.133,.021,.019)],'HoneyPear',12)
leaf=mesh('Fruit leaf',[(.016,0,.14,.008,.005),(.033,.002,.15,.019,.008),
         (.055,.004,.154,.006,.003)],'ElderLeaf',6)
stem('Pear stem',(0,0,.119),(.015,0,.159),.009,.006,'Wood')
# Save each export in local coordinates, then arrange the editable Blender gallery.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wayfarer_export import export_piece
requested=set(sys.argv[sys.argv.index("--")+1:]) if "--" in sys.argv else set()
for key,collection in groups.items():
    if requested and key not in requested:continue
    export_piece(key,collection,out)
for i,collection in enumerate(groups.values()):
    collection["gallery_offset"]=((i%3)*5,(i//3)*5)
    for o in collection.objects:o.location.x+=(i%3)*5;o.location.y+=(i//3)*5
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Blender/Bellwake/Wayfarer.blend'),compress=True)
