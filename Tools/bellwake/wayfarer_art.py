"""Blender 4.3: blender -b --python-exit-code 1 --python Tools/bellwake/wayfarer_art.py"""
import bpy, math
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
oval('Lantern',0,0,0,.07,.118,.061,'Brass')
oval('Beacon',0,.058,-.02,.055,.06,.046,'Amber')
for s,n in [(-1,'Left'),(1,'Right')]:
    o=mesh(n+'Wing',[(s*.095,0,0,.09,.055),(s*.15,.008,.025,.133,.093),(s*.135,.02,.038,.11,.073)],'SeaCloth',12)
    pivot(o,(s*.034,0,0))
begin('GroveBank')
bank=mesh('Bellroot clearing',[(0,0,-1.3,12,10),(0,0,-.33,13,11),(0,0,-.07,5.3,4),(0,0,0,2.86,1.57)],'Moss',32)
for face in bank.data.polygons:
    if face.index==0:continue
    for li in face.loop_indices:
        v=bank.data.vertices[bank.data.loops[li].vertex_index].co
        bank.data.uv_layers.active.data[li].uv=(v.x*.75,v.y*.75)
begin('Bellroot')
mesh('Fluted elder trunk',[(0,0,-.45,1.38,1.29),(0,0,.1,1.22,1.12),(.12,0,.85,.79,.74),(.2,.12,2,.60,.56),(.04,.17,3.8,.4,.37)],'Wood',18)
for i in range(7):
    a=i*math.tau/7;s,c=math.sin(a),math.cos(a);z=3.2+(i%3)*.41
    stem('Curved bough',(0,.07,1.5+i*.16),(1.17*c,1.17*s,z),.32,.13,'Wood')
    oval('Crown',1.24*c,1.24*s,z+.46,1.25,.99,1.02,'Leaves')
    stem('Root flare',(.48*c,.48*s,.56),(1.63*c,1.63*s,-.12),.36,.14,'Wood')
oval('Crown crest',0,.15,4.55,1.37,1.14,1.04,'Leaves')
for s in [-1,1]:
    oval('Amber eye',s*.32,-.69,1.34,.093,.065,.12,'Amber')
    stem('Bark brow',(s*.19,-.66,1.55),(s*.48,-.59,1.48),.11,.062,'Wood')
oval('Hollow knot',0,-.78,.96,.136,.029,.098,'RoofSlate')
begin('TollSword')
mesh('Leaf blade',[(0,0,.1,.043,.014),(0,0,.18,.065,.018),(0,0,.55,.045,.018),(0,0,.74,.006,.006)],'BellMetal',4,False)
mesh('Crossguard',[(0,0,.065,.098,.023),(0,0,.101,.129,.026),(0,0,.125,.083,.021)],'Brass')
stem('Wrapped grip',(0,0,-.145),(0,0,.08),.023,.021,'Wood')
oval('Pommel',0,0,-.148,.04,.035,.044,'Brass')
begin('FerryShield')
o=mesh('Kite shield',[(0,0,-.24,.012,.018),(0,0,-.07,.155,.038),(0,0,.105,.186,.044),(0,0,.18,.145,.036),(0,0,.22,.06,.026)],'Wood',12)
oval('Boss',0,-.036,.05,.081,.042,.081,'Brass')
for s in [-1,1]:stem('Edge binding',(0,0,-.23),(s*.155,0,-.04),.009,.012,'BellMetal')
begin('ReedStaff')
stem('Reedwood shaft',(0,0,-.34),(0,0,.58),.023,.032,'Wood')
mesh('Caged chime',[(0,0,.57,.041,.041),(0,0,.65,.083,.083),(0,0,.74,.063,.063),(0,0,.81,.016,.016)],'Brass')
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
begin('MarketPear')
oval('Pear belly',0,0,.065,.068,.063,.07,'Amber')
stem('Pear stem',(0,0,.119),(.015,0,.159),.009,.006,'Wood')
# Save each export in local coordinates, then arrange the editable Blender gallery.
for key,collection in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    pivot_names={'LeftWing','RightWing','LeftBoot','RightBoot','Shell','Broad jaw'}
    moving=[]; copies=[]
    for o in collection.objects:
        if o.name in pivot_names:
            moving.append(o)
            continue
        duplicate=o.copy();duplicate.data=o.data.copy()
        bpy.context.scene.collection.objects.link(duplicate)
        duplicate.select_set(True);copies.append(duplicate)
    body=copies[0];bpy.context.view_layer.objects.active=body
    if len(copies)>1:bpy.ops.object.join()
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    body.name=key+' paint'
    for part in moving:part.select_set(True)
    bpy.ops.export_scene.fbx(filepath=str(out/(key+'.fbx')),use_selection=True,bake_anim=False,
                             object_types={'MESH'},axis_forward='-Z',axis_up='Y',path_mode='STRIP')
    bpy.data.objects.remove(body,do_unlink=True)
for i,collection in enumerate(groups.values()):
    for o in collection.objects:o.location.x+=(i%3)*5;o.location.y+=(i//3)*5
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Blender/Bellwake/Wayfarer.blend'),compress=True)
