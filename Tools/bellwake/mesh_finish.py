"""Seat freestanding atlas models and close openings on rigid character sections before batching."""
import re
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

# These imported units have their origin at the sole/base. Hanging scenery, boats,
# machines with separate moving parts and wall-mounted decorations keep their authored mounts.
STANDING = re.compile(r'bench|hut|cairn|standing stone|cypress|pine|crane|frost gate|shelter|\banvil\b|crucible|listening stump|tunnel brace|at the west gantry|by the cooling bed|counting the guild roll|guarding the depositions|listening for cavitation',re.I)

def seal(mesh, character=False, fringe=False):
    bm=bmesh.new()
    bm.from_mesh(mesh)
    # Imported UV splits often duplicate positions. BMesh keeps UVs per face loop.
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000005)
    edges={e for e in bm.edges if e.is_boundary}
    if fringe and edges:
        bm.verts.ensure_lookup_table()
        # Carve a longer point into the swept fringe, then thicken the painted lock.
        if len(bm.verts)==5:
            tip=min(bm.verts,key=lambda v:v.co.z)
            tip.co.z-=.028
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bmesh.ops.solidify(bm,geom=list(bm.faces),thickness=.009)
        bm.to_mesh(mesh)
        mesh.update()
        bm.free()
        return 1
    count=0
    uv=bm.loops.layers.uv.active
    while edges:
        first=edges.pop()
        component={first}
        stack=[first]
        while stack:
            for v in stack.pop().verts:
                neighbours={e for e in v.link_edges if e in edges}
                edges-=neighbours
                component.update(neighbours)
                stack.extend(neighbours)
        verts={v for e in component for v in e.verts}
        if not 3<=len(verts)<=128 or len(component)!=len(verts) or any(sum(e in component for e in v.link_edges)!=2 for v in verts):
            continue
        # A planar panel outlined by its own boundary is an intentional sheet.
        normals=[e.link_faces[0].normal for e in component]
        if all(abs(normals[0].dot(n))>.995 for n in normals):
            if not character: continue
            sheet={e.link_faces[0] for e in component}
            pending=list(sheet)
            while pending:
                neighbours={f for e in pending.pop().edges for f in e.link_faces}-sheet
                sheet.update(neighbours)
                pending.extend(neighbours)
            if all(abs(normals[0].dot(f.normal))>.98 for f in sheet):
                # Collars, fringes and badges keep their painted fronts and gain a back and hem.
                size=max((v.co-next(iter(verts)).co).length for v in verts)
                bmesh.ops.solidify(bm,geom=list(sheet),thickness=max(.0001,size*.035))
                count+=1
                continue
        source={v:next((l[uv].uv.copy() for l in v.link_loops),None) for v in verts} if uv else {}
        caps=bmesh.ops.holes_fill(bm,edges=list(component),sides=0)['faces']
        for face in caps:
            if uv:
                for l in face.loops:
                    if source.get(l.vert) is not None: l[uv].uv=source[l.vert]
        if caps:
            bmesh.ops.triangulate(bm,faces=caps)
            count+=len(caps)
    if count:
        bm.to_mesh(mesh)
        mesh.update()
    bm.free()
    return count

def finish_geometry(groups,pivots):
    import bpy
    bpy.context.view_layer.update()
    report=[]
    cached=set()
    for group in ('Speaker','SpeakerHead','SpeakerArm','Ina','Set'):
        for o in groups.get(group,[]):
            mesh=o.data
            if mesh in cached: continue
            cached.add(mesh)
            if group=='Set' and not any(m and m.name.endswith('Atlas') for m in mesh.materials): continue
            caps=seal(mesh, group!="Set",o.name.startswith("Swept fringe lock"))
            if caps: report.append((o.name,'sealed',caps))
    terrain=groups.get('Terrain',[])
    if not terrain: return report
    solids=[o for o in terrain+groups.get('Set',[]) if o.data.polygons]
    def ground(anchor,parts):
        verts=[o.matrix_world@v.co for o in parts for v in o.data.vertices]
        low=min(v.z for v in verts)
        feet=[v for v in verts if v.z<=low+.012]
        hits=[]
        for p in feet[::max(1,len(feet)//10)]:
            origin=p+Vector((0,0,.15))
            levels=[]
            for o in solids:
                if o in parts: continue
                if o not in bounds:
                    box=[o.matrix_world@Vector(v) for v in o.bound_box]
                    bounds[o]=(min(v.x for v in box),max(v.x for v in box),min(v.y for v in box),max(v.y for v in box),min(v.z for v in box),max(v.z for v in box))
                a,b,c,d,bot,top=bounds[o]
                if not a-.001<=p.x<=b+.001 or not c-.001<=p.y<=d+.001 or bot>origin.z or top<low-1.5: continue
                if o not in trees:
                    trees[o]=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons])
                hit,normal,_,_=trees[o].ray_cast(origin,(0,0,-1),1.7)
                if hit is not None and normal.z>.50: levels.append(hit.z-p.z)
            if levels: hits.append(max(levels))
        if not hits: return
        dz=max(hits)-.007
        if abs(dz)<.019: return
        # On very uneven ground, the highest boot/base contact controls placement.
        for o in parts:
            o.location.z+=dz
        for k in ('SpeakerHead','SpeakerArm'):
            if any(o in groups.get(k,[]) for o in parts) and k in pivots:
                x,y,z=pivots[k];pivots[k]=(x,y,z+dz)
        bounds.clear();trees.clear()
        bpy.context.view_layer.update()
        report.append((anchor,'base offset',round(dz,3)))
    bounds,trees={},{}
    for o in solids:
        if o in terrain or not STANDING.search(o.name) or not any(m and m.name.endswith('Atlas') for m in o.data.materials): continue
        ground(o.name,[o])
    actors=[o for k in ('Speaker','SpeakerHead','SpeakerArm') for o in groups.get(k,[])]
    if actors: ground('speaker',actors)
    return report
