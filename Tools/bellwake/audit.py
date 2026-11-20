"""Reimport shipped FBXs, probe the ground and check capsule-width access to every story station.
blender -b -t 2 --python-exit-code 1 --python Tools/bellwake/audit.py -- /tmp/bell-audit
"""

import bpy, bmesh, math, json, sys
from pathlib import Path
from collections import deque
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "Assets/Resources/Bellwake"
out = Path(sys.argv[sys.argv.index("--") + 1])
out.mkdir(exist_ok=True)
works={room["key"]:room for room in json.loads((RES/"Underworks.json").read_text())["rooms"]}


def tree(objects):
    vs = []
    fs = []
    for o in objects:
        m = o.data
        offset = len(vs)
        vs.extend(o.matrix_world @ v.co for v in m.vertices)
        m.calc_loop_triangles()
        fs.extend(tuple(offset + j for j in t.vertices) for t in m.loop_triangles)
    return BVHTree.FromPolygons(vs, fs, all_triangles=True)


def check_market_stairs_and_well(objects):
    # Sample the same imported meshes used by the native character and palms.
    surface=tree([objects["Set"],objects["Terrain"],objects["C_Solids"]])
    def height(x,y,start=7):
        hit=surface.ray_cast((x,y,start),(0,0,-1),10)[0]
        assert hit is not None, ("Bellmarket missing surface",x,y)
        return hit.z

    for x in (-1.55,-1.25,-.8,0,.8,1.25,1.55):
        tops=[height(x,7.7+i*.025) for i in range(268)]
        rises=[b-a for a,b in zip(tops,tops[1:])]
        assert sum(h>.06 for h in rises)==8, ("Missing stair tread",x)
        assert min(rises)>-.022 and max(rises)<.1501, ("Stair lip",x,min(rises),max(rises))

    # Start under the bucket, above the grate. Even the gaps between slats must support a palm.
    for i in range(-6,7):
        for j in range(-6,7):
            if i*i+j*j<=36:
                h=height(-4+i*.10,7+j*.10,.63)
                assert .548<h<.58, ("Open well shaft",i,j,h)


def check_yard_detail(objects):
    for name in ("MarshHen", "ReedHen"):
        near = [objects[name+part] for part in ("","Head","Left","Right")]
        far = objects[name+"Far"]
        assert (near[0].matrix_world.translation-far.matrix_world.translation).length<.001
        for part in near+[far]:
            part.data.calc_loop_triangles()
            assert len(part.material_slots)==1 and part.material_slots[0].material.name=="YardFowl"
        assert len(far.data.loop_triangles)<sum(len(o.data.loop_triangles) for o in near)/5
        full = [o.matrix_world@v.co for o in near for v in o.data.vertices]
        small = [far.matrix_world@v.co for v in far.data.vertices]
        for axis in range(3):
            for bound in (min,max):
                assert abs(bound(v[axis] for v in full)-bound(v[axis] for v in small))<.05, (name,axis)
        assert abs(min(v.z for v in small)-min(v.z for v in full))<.005, (name,"foot height")


def check_wheel_guard(objects):
    centre=objects["MillWheel"].matrix_world.translation
    axle=(objects["WheelAxle"].matrix_world.translation-centre).normalized()
    side=axle.cross(Vector((0,0,1))).normalized()
    up=side.cross(axle).normalized()
    contact=tree([objects["C_Solids"]])
    # Test the full turning envelope against the stationary guard, including the projecting hub.
    for i in range(360):
        angle=math.radians(i)
        normal=side*math.cos(angle)+up*math.sin(angle)
        for radius,half in ((.19,.481),(.61,.447),(1.68,.447),(2.179,.447)):
            on_circle=centre+normal*radius
            for sign in (-1,1):
                hit=contact.ray_cast(on_circle+axle*(sign*.55),-sign*axle,.15)[0]
                assert hit is not None and abs((hit-on_circle).dot(axle)*sign-half)<.003, (
                    "Opening in wheel guard",i,radius,sign)


def ward_passages(key, objects, ground, reach, off, step):
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from pilgrim import ALL_FIELDS as FIELDS, SIZE, edge, layout, world, neighbours
    edges,_ = layout(next(i for i,f in enumerate(FIELDS) if f[0] == key))
    rim = tree([objects["Rim"]])
    room = works[key]
    for name in ["GuideBird","GuideLeft","GuideRight","MapSW","MapSE","MapNW"]:
        assert name in objects, (key,name)
    for station in room["stations"]:
        if station.get("camp"):
            pt = objects[station["camp"]].matrix_world.translation
            assert (round((pt.x-off)/step),round((pt.y-off)/step)) in reach,(key,station["camp"])
        trail = station.get("trail")
        if trail:
            assert len(trail)==SIZE*SIZE and trail.count(".")==1
            destination=trail.index(".")
            for start in range(len(trail)):
                cell=start
                for _ in range(len(trail)):
                    if cell==destination: break
                    other=cell+{"N":SIZE,"S":-SIZE,"E":1,"W":-1}[trail[cell]]
                    assert edge((cell%SIZE,cell//SIZE),(other%SIZE,other//SIZE)) in edges
                    cell=other
                assert cell==destination,(key,station["id"],start)
    shots=0
    for y in range(SIZE):
        for x in range(SIZE):
            a=(x,y)
            for b in neighbours(a):
                dx,dy=b[0]-x,b[1]-y
                wx,wy=world(a)
                for offset in (-3,-1.5,0,1.5,3):
                    mx=wx+4*dx-offset*dy
                    my=wy+4*dy+offset*dx
                    z=ground.ray_cast((mx,my,10),(0,0,-1),20)[0].z
                    for height in (.3,1.6):
                        hit=rim.ray_cast((mx-dx,my-dy,z+height),(dx,dy,0),2)[0]
                        assert (hit is None)==(edge(a,b) in edges),(key,a,b,offset,height)
                        shots+=1
    return shots


def check_painted_surfaces(meshes, material_name):
    # A collapsed UV triangle makes the keeper's coat cap or a snowy bough
    # sample a line of pigment. Catch it on the same FBX that Unity imports.
    painted = 0
    for obj in meshes:
        mesh = obj.data
        slots = {i for i, mat in enumerate(mesh.materials) if mat and mat.name == material_name}
        if not slots:
            continue
        mesh.calc_loop_triangles()
        uvs = mesh.uv_layers.active.data
        for tri in mesh.loop_triangles:
            if tri.material_index not in slots or tri.area < 1e-8:
                continue
            a, b, c = [uvs[i].uv for i in tri.loops]
            assert abs((b - a).cross(c - a)) > 1e-10, (obj.name, material_name, tri.index)
            painted += 1
    assert painted, material_name


def main(key):
    if key == "Highroad":
        import runpy
        result=runpy.run_path(str(Path(__file__).with_name("check_highroad.py")))["result"]
        return dict(asset=key, **result)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(RES / "Rooms" / (key + ".fbx")))
    objects = {o.name: o for o in bpy.context.scene.objects}
    mesh = [o for o in objects.values() if o.type == "MESH"]
    if key in ("StillBelfry", "RimePost"):
        check_painted_surfaces(mesh, "QuietEnamel" if key == "StillBelfry" else "RimeFir")
    for o in mesh:
        if o.name in ("Speaker","SpeakerHead","SpeakerArm","Ina") or key in ("RunnerArm","RightPalm","LeftPalm"):
            bm=bmesh.new()
            bm.from_mesh(o.data)
            # Weld physical positions for this check only, so a painted UV seam is legal.
            bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000005)
            openings=sum(edge.is_boundary for edge in bm.edges)
            bm.free()
            assert openings==0,(key,o.name,"open character edges",openings)
        assert o.data.uv_layers.active, (key, o.name, "missing UV")
        uv = o.data.uv_layers.active.data
        ranges = {}
        for poly in o.data.polygons:
            values = ranges.setdefault(poly.material_index, [float("inf")] * 2 + [float("-inf")] * 2)
            for loop in poly.loop_indices:
                u, v = uv[loop].uv
                values[0] = min(values[0], u)
                values[1] = min(values[1], v)
                values[2] = max(values[2], u)
                values[3] = max(values[3], v)
        assert all(max(b[2] - b[0], b[3] - b[1]) > 0.0001 for b in ranges.values()), (
            key,
            o.name,
            "collapsed material UVs",
        )
        assert all((RES / "Textures" / (m.name + ".png")).is_file() for m in o.data.materials), (
            key,
            o.name,
            [m.name for m in o.data.materials],
        )
    if "Terrain" not in objects:
        assert mesh and sum(len(o.data.polygons) for o in mesh) > 25
        static_tree = tree(mesh)
        if key == "MossbellApproach":
            entrance = objects["GateAt"].matrix_world.translation
            assert (entrance - Vector((0, -36, 0))).length < 0.02
            for x in [-2.5, -1.5, 0, 1.5, 2.5]:
                for height in [0.25, 1.0, 2.2]:
                    assert static_tree.ray_cast((x, -50, height), (0, 1, 0), 20)[0] is None, (
                        "Blocked meadow portal"
                    )
        if key == "MeadowOutcrop":
            for x, y in [(0, 0), (0.65, 0), (-0.65, 0), (0, 0.55), (0, -0.55)]:
                hit, normal, _, _ = static_tree.ray_cast((x, y, 5), (0, 0, -1), 10)
                assert hit and hit.z > 1.2 and normal.z > 0, "Missing outcrop crown"
        return {"asset": key, "triangles": sum(len(o.data.loop_triangles) for o in mesh)}
    if key=="Bellmarket":
        check_market_stairs_and_well(objects)
        check_yard_detail(objects)
    if key=="Reedwater":
        check_wheel_guard(objects)
    ground = tree([objects["Terrain"]])
    solid = tree([objects["C_Solids"], objects["Set"], objects["Rim"]])
    spawn = objects["Spawn"].matrix_world.translation
    for dx, dy in [(0,0),(-.19,0),(.19,0),(0,-.19),(0,.19)]:
        origin = (spawn.x+dx, spawn.y+dy, spawn.z+.3)
        support, normal, _, _ = ground.ray_cast(origin, (0,0,-1), .55)
        assert support is not None and normal.z>.65 and -.06<=spawn.z-support.z<=.20, (key, "unsupported spawn", spawn)
    if key=="GlassRookery":
        eye = spawn + Vector((0,0,1.55))
        board = objects["A_Chart"].matrix_world.translation
        keeper = objects["A_Keeper"].matrix_world.translation
        for target in (keeper,board):
            sight = target - eye
            assert solid.ray_cast(eye,sight.normalized(),sight.length-.15)[0] is None, (key,"blocked entrance view")
        assert (board-eye).length>5 and (keeper-eye).length<10, (key,"room to see the chart and keeper")
    markers = {n: o.matrix_world.translation for n, o in objects.items() if n.startswith("A_")}
    target_names = {n[4:] for n in objects if n.startswith("Hit_")}
    expected = {"Key0","Key1","Key2"} if key in ("RootChoir","StillBelfry") else {"Low","Middle","High"} if key=="KettleYard" else {"Long","Middle","Short"} if key=="RowanHollow" else set()
    assert target_names == expected, (key, target_names)
    for name in target_names:
        centre = objects["Hit_"+name].matrix_world.translation
        edge = objects["Edge_"+name].matrix_world.translation
        assert .18 <= (centre-edge).length <= .38 and (centre-markers["A_"+name]).length<1, (key,name)
    if key in works:
        assert set(markers)=={s["id"] for s in works[key]["stations"]},key
        assert all(v["node"] in objects for v in works[key]["visuals"]),key
        assert all(s["swing"] in objects for s in works[key]["stations"] if s.get("swing")),key
        assert all(s["sight"] in objects for s in works[key]["stations"] if s.get("sight")),key
        for source in works.values():
            for station in source["stations"]:
                for rule in station["rules"]:
                    if rule.get("to")==key and rule.get("arrival"):
                        assert rule["arrival"] in objects,(source["key"],key,rule["arrival"])
        for visual in works[key]["visuals"]:
            if visual["kind"]=="slide":assert {"RailStart","RailEnd"}.issubset(objects),key
            if visual["kind"]=="pointer":assert {"Bearing0","Bearing1","Bearing2"}.issubset(objects),key
            if visual["kind"]=="voyage":
                assert all(visual["node"]+suffix in objects for suffix in ["Turn","Berth"]),key
    elif key != "Bellmarket":
        assert {"A_Key0", "A_Key1", "A_Key2"}.issubset(markers)
    span = works.get(key, {}).get("halfSpan", 20)
    step = 0.5
    off = 1 - span
    rows = int(-2 * off / step) + 1
    blocked = set()
    surfaces = {}
    for j in range(rows):
        for i in range(rows):
            x, y = off + i * step, off + j * step
            hit, normal, _, _ = ground.ray_cast((x, y, 10), (0, 0, -1), 20)
            assert hit and normal.z > 0.84, (key, x, y, "ground hole or slope")
            z = hit.z
            surfaces[i, j] = z
            if key in works or key in ("Saltwake","RimePost","Glasscut"):
                # Thin posts may fall between vertical probes. Reserve clearance for the swept body.
                for h in (.23,.50,.8,1.1,1.39,1.62):
                    near=solid.find_nearest(Vector((x,y,z+h)),.46)
                    if near[0] is not None:
                        blocked.add((i,j));break
            for dx, dy in [(0, 0), (0.28, 0), (-0.28, 0), (0, 0.28), (0, -0.28)]:
                # Test above foot height, including the head clearance on the actual mesh.
                if solid.ray_cast((x + dx, y + dy, z + 1.72), (0, 0, -1), 1.60)[0] is not None:
                    blocked.add((i, j))
                    break
    start = (round((spawn.x - off) / step), round((spawn.y - off) / step))
    assert start in surfaces and start not in blocked, (key, "blocked spawn")
    reach = {start}
    q = deque([start])
    while q:
        i, j = q.popleft()
        for di, dj in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            cell = i + di, j + dj
            if cell in surfaces and cell not in reach and cell not in blocked:
                reach.add(cell)
                q.append(cell)
    if key in works:
        for station in works[key]["stations"]:
            name=station.get("camp")
            if name:
                point=objects[name].matrix_world.translation
                assert (round((point.x-off)/step),round((point.y-off)/step)) in reach,(key,name,"unsafe checkpoint")
    perimeter = tree([objects["C_Solids"]])
    rays = 0
    for axis in [0, 1]:
        for sign in [-1, 1]:
            for i in range(8 * span - 3):
                for h in [0.15, 0.6, 1.6, 3, 8]:
                    along = .5 - span + i * .25
                    ray = Vector((sign, 0, 0)) if axis == 0 else Vector((0, sign, 0))
                    origin = (
                        Vector((sign * (span - .35), along, h))
                        if axis == 0
                        else Vector((along, sign * (span - .35), h))
                    )
                    hit, normal, _, _ = perimeter.ray_cast(origin, ray, 1.3)
                    assert hit is not None and normal.dot(ray) < -0.9, (key, origin, "boundary opening")
                    rays += 1
    goals = {}
    for name, pos in markers.items():
        choices = []
        for i, j in reach:
            p = Vector((off + i * step, off + j * step, surfaces[i, j] + 1.65))
            delta = pos - p
            d = delta.length
            if (
                d < 3.35
                and d > 1.15
                and solid.ray_cast(p, delta.normalized(), max(0.01, d - 0.40))[0] is None
            ):
                choices.append((i, j))
        assert len(choices) > 3, (key, name, "unreachable station")
        goals[name] = sorted(choices)
    interior = ward_passages(key,objects,ground,reach,off,step) if works.get(key,{}).get("early") else 0
    # Exactly one member of each near/far pair is active. Audit the larger member
    # and verify the lower-detail set covers the same part of the wood.
    visible = [o for o in mesh if o.name != "C_Solids" and not o.name.startswith("GroveFar")]
    for o in mesh:
        if not o.name.startswith("GroveFar"):
            continue
        near=objects[o.name.replace("Far","Near")]
        assert len(o.data.loop_triangles)<len(near.data.loop_triangles),o.name
        assert len(o.data.materials)<=len(near.data.materials),o.name
    tri = sum(len(o.data.loop_triangles) for o in visible)
    slots = sum(len(o.data.materials) for o in visible)
    assert tri < 50000 and slots < 64, (key, tri, slots)
    (out / (key + ".json")).write_text(
        json.dumps(dict(reach=sorted(reach), goals=goals, offset=off, step=step))
    )
    return dict(
        asset=key,
        groundProbes=rows * rows,
        boundaryRays=rays,
        interiorCrossings=interior,
        walkableCells=len(reach),
        stations=len(markers),
        minApproaches=min(map(len, goals.values())),
        triangles=tri,
        visibleMaterialSlots=slots,
    )


selection = sys.argv[sys.argv.index("--")+2:]
keys = selection or [p.stem for p in sorted((RES / "Rooms").glob("*.fbx"))]
report = [main(key) for key in keys]
(out / "summary.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
