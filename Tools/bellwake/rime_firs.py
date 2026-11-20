"""Paint snow on the windward needles and give the two post-road firs hanging tips."""

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIRS = {"The leaning pine": 0.38, "Twinned pine": 1.96}


def paint(path):
    import numpy as np
    from PIL import Image

    sheet = Image.new("RGB", (128, 128))
    with Image.open(Path(__file__).with_name("surface_sources") / "rime-fir.png") as source:
        for cell in range(4):
            x, y = cell % 2 * 192, cell // 2 * 192
            brush = source.crop((x, y, x + 192, y + 192)).resize((60, 60), Image.Resampling.LANCZOS)
            padded = np.pad(np.asarray(brush), ((2, 2), (2, 2), (0, 0)), mode="edge")
            sheet.paste(Image.fromarray(padded), (cell % 2 * 64, cell // 2 * 64))
    sheet.save(path, optimize=True)


def sculpt(obj, phase):
    import bmesh
    from atelier import load_paint

    mesh = obj.data.copy()
    obj.data = mesh
    branches = load_paint("RimeFir")
    mesh.materials.append(branches)
    slot = len(mesh.materials) - 1
    bm = bmesh.new()
    bm.from_mesh(mesh)
    uv = bm.loops.layers.uv.active
    # This cell of the original IceAtlas was the snow mantle. Keep the spruce's
    # actual crooked trunk, sawn roots and two branch forks from the source model.
    mantle = [f for f in bm.faces if all(.5 < loop[uv].uv.x < .75 and .25 < loop[uv].uv.y < .5 for loop in f.loops)]
    if len(mantle) != 72:
        raise ValueError(f"{obj.name} has {len(mantle)} original crown triangles")
    unused = {v for face in mantle for v in face.verts}
    bmesh.ops.delete(bm, geom=mantle, context="FACES_ONLY")
    bmesh.ops.delete(bm, geom=[v for v in unused if not v.link_faces], context="VERTS")

    def face(vertices, coordinates, cell):
        f = bm.faces.new(vertices)
        f.material_index = slot
        for loop, (u, v) in zip(f.loops, coordinates):
            loop[uv].uv = ((cell % 2 * 64 + 2.5 + 59*u) / 128, 1 - (cell // 2 * 64 + 2.5 + 59*(1-v)) / 128)

    count = 16
    for tier, radius in enumerate((1.04, .85, .67)):
        z = 1.25 + .65 * tier
        rows = []
        for ring, (width, height) in enumerate(((.74, .10), (1.0, 0), (.67, .37), (.31, .77))):
            row = []
            for j in range(count):
                a = math.tau*j/count + phase + .24*tier
                tip = .5 + .5 * math.cos(j*math.pi)
                spread = width*radius*(.87 + .13*tip + .038*math.cos(3*a + tier))
                sag = ((.12 + .07*math.sin(2*a + phase))*tip) * (1.0, 1.0, .45, .13)[ring]
                row.append(bm.verts.new((spread*math.cos(a), -.05 + spread*math.sin(a), z + height - sag)))
            rows.append(row)
        underside = bm.verts.new((0, -.05, z + .17))
        crown = bm.verts.new((.04*math.cos(tier+phase), -.05+.04*math.sin(tier+phase), z+1.10))
        for j in range(count):
            k = (j+1) % count
            a = math.tau*(j+.5)/count + phase + .24*tier + obj.rotation_euler.z
            # The same northwesterly wind loads both trees. Hems expose the greener underside.
            cell = 0 if math.cos(a - 2.3) > .35 else 2 if math.cos(a - 2.3) > -.4 else 1
            left = .5*(j%2)
            right = left+.5
            face([underside, rows[0][k], rows[0][j]], [(.5, .95), (right, .04), (left, .04)], 3)
            for r, (v0,v1) in enumerate(((.9,.05), (.03,.47), (.47,.81))):
                face([rows[r][j], rows[r][k], rows[r+1][k], rows[r+1][j]],
                     [(left,v0), (right,v0), (right,v1), (left,v1)], 3 if r==0 else cell)
            face([rows[-1][j],rows[-1][k],crown],[(left,.81),(right,.81),((left+right)*.5,1)],cell)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def fit(key, objects):
    if key == "RimePost":
        for obj in objects:
            if obj.name in FIRS and all(material.name != "RimeFir" for material in obj.data.materials):
                sculpt(obj, FIRS[obj.name])


if __name__ == "__main__":
    paint(ROOT / "Assets/Resources/Bellwake/Textures/RimeFir.png")
