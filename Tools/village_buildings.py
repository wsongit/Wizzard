"""Complete, closed cottage shells and facade finishing for Mossbell.

All geometry is authored here. The API is the generator's helper dictionary;
calling code remains responsible for the active collection and export batching.
The house core includes its attic, so decorative roof pieces cannot expose a
player-sized hollow between a wall box and an open roof surface.
"""
import math
from mathutils import Matrix


def build_house(api, label, x, y, w, d, h=3.1, base=0, angle=0, rise=1.8,
                door_side=.18, roof='RoofTiles', plaster='HousePlaster', porch=False):
    bpy = api['bpy']
    box, mesh, beam, cone = (api[k] for k in ('box', 'mesh', 'beam', 'cone'))
    uv_project = api['uv_project']
    before = set(bpy.context.scene.objects)

    # One outward-facing watertight pentagonal prism fills walls AND attic.
    # Its gable overlaps the roof underside by 35 mm rather than ending short.
    a, b = w / 2 + .42, d / 2 + .4
    roof_z, thickness = h + .05, .16
    inner_eave = roof_z + rise * (1 - (w / 2) / a) - thickness + .035
    inner_peak = roof_z + rise - thickness + .035
    outline = [(-w/2, -.045), (w/2, -.045), (w/2, inner_eave),
               (0, inner_peak), (-w/2, inner_eave)]
    vertices = [(px, yy, pz) for yy in (-d/2, d/2) for px, pz in outline]
    faces = [tuple(range(5)), tuple(range(9, 4, -1))]
    faces += [(i, i+5, (i+1) % 5+5, (i+1) % 5) for i in range(5)]
    core = mesh(label+' closed wall and attic core', vertices, faces, plaster, True)
    core['sealed_house_core'] = True
    core['footprint_m'] = [w, d]
    core['roof_overlap_m'] = .035
    box(label+' continuous stone footing', (0, 0, .18), (w+.12, d+.12, .45), 'Masonry', True)

    def closed_slab(name, top, depth, material, solid=True):
        bottom = [(px, py, pz-depth) for px, py, pz in top]
        f = [(0, 1, 2, 3), (7, 6, 5, 4)]
        f += [(i, i+4, (i+1) % 4+4, (i+1) % 4) for i in range(4)]
        result = mesh(name, top+bottom, f, material, solid)
        result['closed_building_slab'] = True
        return result

    closed_slab(label+' closed west roof', [(-a,-b,roof_z), (0,-b,roof_z+rise),
                 (0,b,roof_z+rise), (-a,b,roof_z)], thickness, roof)
    closed_slab(label+' closed east roof', [(0,-b,roof_z+rise), (a,-b,roof_z),
                 (a,b,roof_z), (0,b,roof_z+rise)], thickness, roof)
    box(label+' roof ridge cap', (0, 0, roof_z+rise+.035), (.23, 2*b+.12, .16), roof)
    for sy in (-1, 1):
        yy = sy*(b+.025)
        for sx in (-1, 1):
            beam(label+' bargeboard', (sx*a,yy,roof_z-.06), (0,yy,roof_z+rise-.06), .20)
    for sx in (-1, 1):
        beam(label+' eave fascia', (sx*a,-b,roof_z-.08), (sx*a,b,roof_z-.08), .20)

    # All four elevations have headers, sole plates and visible structural posts.
    for sy in (-1, 1):
        yy = sy*(d/2+.055)
        for xx in (-w/2+.08, 0, w/2-.08):
            box(label+' facade upright', (xx,yy,h/2), (.18,.16,h), 'Wood')
        for zz in (.47, h-.12):
            box(label+' facade timber course', (0,yy,zz), (w,.17,.18), 'Wood')
        beam(label+' gable kingpost', (0,yy,h-.1), (0,yy,inner_peak-.03), .16)
        for sx in (-1, 1):
            beam(label+' gable brace', (sx*(w/2-.14),yy,h-.05), (0,yy,inner_peak-.06), .16)
    for sx in (-1, 1):
        xx = sx*(w/2+.055)
        for zz in (.47, h-.12):
            box(label+' side timber course', (xx,0,zz), (.17,d,.18), 'Wood')
        for yy in (-d/2+.08, 0, d/2-.08):
            box(label+' side upright', (xx,yy,h/2), (.16,.18,h), 'Wood')
        # Small corner braces finish the side facade without blank triangular ends.
        for sy in (-1, 1):
            beam(label+' corner brace', (xx,sy*(d/2-.12),h-.6),
                 (xx,sy*(d/2-.67),h-.12), .12)

    front, dx = -d/2-.04, w*door_side
    box(label+' solid door panel', (dx,front,1.09), (1.08,.10,2.16), 'Wood')
    for ox in (-.62,.62):
        box(label+' door jamb', (dx+ox,front-.06,1.12), (.15,.23,2.24), 'Wood')
    box(label+' door lintel', (dx,front-.06,2.25), (1.4,.23,.18), 'Wood')
    box(label+' stone doorstep', (dx,front-.1,.07), (1.46,.45,.14), 'Masonry', True)
    for zz in (.55, 1.65):
        box(label+' door hinge', (dx-.43,front-.065,zz), (.24,.035,.07), 'Brass')
    latch = cone(label+' door latch', (dx+.34,front-.075,1.06), .055,.055,.06,'Brass',8)
    latch.rotation_euler.x = math.pi/2
    beam(label+' door lower brace', (dx-.43,front-.065,.35), (dx+.43,front-.065,.9), .065)

    def window(cx, cy, side=False, sign=1, shutters=True):
        """Closed painted glass panels with properly outward frames on every side."""
        z = 1.88
        if side:
            box(label+' side dark pane', (cx,cy,z), (.065,.84,.87), 'WindowDark')
            outer = cx+sign*.06
            for yy in (-.5,.5):
                box(label+' side window jamb', (outer,cy+yy,z), (.19,.12,1.08), 'Wood')
            for zz in (-.49,.49):
                box(label+' side window sill', (outer,cy,z+zz), (.20,1.12,.12), 'Wood')
            box(label+' side window mullion', (outer,cy,z), (.13,.065,.87), 'Wood')
            box(label+' side window transom', (outer,cy,z), (.13,.86,.065), 'Wood')
            if shutters:
                for yy in (-.70,.70):
                    box(label+' side shutter', (outer,cy+yy,z), (.19,.25,.90), 'Wood')
                    for zz in (-.28,.28):
                        box(label+' side shutter strap', (outer+sign*.105,cy+yy,z+zz), (.025,.25,.045), 'Brass')
        else:
            box(label+' front or rear dark pane', (cx,cy,z), (.84,.065,.87), 'WindowDark')
            outer = cy+sign*.06
            for xx in (-.5,.5):
                box(label+' window jamb', (cx+xx,outer,z), (.12,.19,1.08), 'Wood')
            for zz in (-.49,.49):
                box(label+' window sill', (cx,outer,z+zz), (1.12,.20,.12), 'Wood')
            box(label+' window mullion', (cx,outer,z), (.065,.13,.87), 'Wood')
            box(label+' window transom', (cx,outer,z), (.86,.13,.065), 'Wood')
            if shutters:
                for xx in (-.7,.7):
                    box(label+' hinged shutter', (cx+xx,outer,z), (.25,.19,.90), 'Wood')
                    for zz in (-.28,.28):
                        box(label+' shutter strap', (cx+xx,outer+sign*.105,z+zz), (.25,.025,.045), 'Brass')

    window(-w*.27, -d/2-.025, sign=-1)
    for sx in (-1, 1):
        for yy in (-d*.24, d*.24):
            window(sx*(w/2+.025), yy, side=True, sign=sx, shutters=False)
    for xx in (-w*.23, w*.23):
        window(xx, d/2+.025, sign=1)

    # Two workshops keep their existing canvas porches; the canopy has a real
    # underside and thickness so it remains visible/collidable from above/below.
    if porch:
        yy = front-1.35
        for xx in (-w*.43, w*.43):
            box(label+' porch post', (xx,yy,1.25), (.14,.14,2.5), 'Wood', True)
            beam(label+' porch bracket', (xx,yy,2.05), (xx,front,2.7), .12)
        closed_slab(label+' closed porch canopy', [(-w*.47,front-.05,2.85),
                    (-w*.47,yy-.25,2.5), (w*.47,yy-.25,2.5),
                    (w*.47,front-.05,2.85)], .055, 'Awning')
        beam(label+' porch front beam', (-w*.47,yy,2.48), (w*.47,yy,2.48), .13)
    box(label+' craft plaque mount', (-w*.27,front,2.70), (.37,.10,.38), 'Wood')
    plaque = cone(label+' brass craft plaque', (-w*.27,front-.075,2.70), .18,.18,.055,'Brass',6)
    plaque.rotation_euler.x = math.pi/2

    # A continuous capped chimney, rather than an open hole through a roof.
    chimney_top = roof_z+rise+.58
    chimney_bottom = h+.25
    box(label+' chimney shaft', (w*.27,d*.2,(chimney_top+chimney_bottom)/2),
        (.58,.65,chimney_top-chimney_bottom), 'Masonry', True)
    box(label+' chimney cap', (w*.27,d*.2,chimney_top+.075), (.78,.85,.15), 'Masonry', True)
    box(label+' closed dark chimney crown', (w*.27,d*.2,chimney_top+.155), (.43,.50,.015), 'WindowDark')

    # Primitive transforms are assigned through RNA; the final primitive has no
    # following operator to flush its matrix. Update before baking every matrix.
    bpy.context.view_layer.update()
    transform = Matrix.Translation((x,y,base)) @ Matrix.Rotation(math.radians(angle),4,'Z')
    for obj in set(bpy.context.scene.objects)-before:
        uv_project(obj)
        obj.data.transform(obj.matrix_world)
        obj.matrix_world.identity()
        obj.data.transform(transform)
        obj['metric_uv_done'] = True
        obj['cottage_id'] = label
    return core
