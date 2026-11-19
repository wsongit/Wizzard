"""Draw a numbered thumbnail of every static display-list OBJ for the private modeling bench."""
import argparse
import csv
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


@lru_cache(maxsize=96)
def pixels(path):
    if path is None:
        return np.array([[[165, 163, 154, 255]]], dtype=np.uint8)
    with Image.open(path) as image:
        return np.asarray(image.convert("RGBA"))


def render(path, size=96):
    verts, uv, faces = [], [], []
    materials = {}
    for line in path.with_suffix(".mtl").read_text().splitlines():
        if line.startswith("newmtl "):
            active = line[7:]
        elif line.startswith("map_Kd "):
            materials[active] = (path.parent / line[7:]).resolve()
    active = None
    for line in path.read_text().splitlines():
        if line.startswith("v "):
            verts.append(tuple(map(float, line[2:].split())))
        elif line.startswith("vt "):
            uv.append(tuple(map(float, line[3:].split())))
        elif line.startswith("usemtl "):
            active = materials.get(line[7:])
        elif line.startswith("f "):
            faces.append(([int(v.split("/")[0])-1 for v in line[2:].split()], active))
    xyz = np.array(verts)
    tex = np.array(uv)
    # The original game is Y-up. One common view keeps props comparable between banks.
    view = np.array([.47, .36, .81])
    view /= np.linalg.norm(view)
    right = np.cross([0, 1, 0], view)
    right /= np.linalg.norm(right)
    up = np.cross(view, right)
    xy = xyz @ np.stack([right, -up], axis=1)
    span = max(1, np.ptp(xy, axis=0).max())
    xy = (xy - (xy.min(axis=0)+xy.max(axis=0))/2) * ((size-8)/span) + size/2
    depths = xyz @ view
    depth = np.full((size, size), -np.inf)
    line = np.linspace(0,1,size)[:,None,None]
    rgb = np.tile(np.uint8(np.array([48,48,45]) + 14*line), (1,size,1))
    for ids, material in faces:
        p, q, r = xy[ids]
        edge = xy[ids]
        x0,y0 = np.maximum(0,np.floor(edge.min(axis=0)).astype(int))
        x1,y1 = np.minimum(size-1,np.ceil(edge.max(axis=0)).astype(int))
        area = (q[0]-p[0])*(r[1]-p[1])-(r[0]-p[0])*(q[1]-p[1])
        if abs(area)<.001 or x1<x0 or y1<y0:
            continue
        y,x = np.ogrid[y0:y1+1,x0:x1+1]
        dx,dy = x+.5-p[0],y+.5-p[1]
        b = (dx*(r[1]-p[1])-dy*(r[0]-p[0]))/area
        c = (dy*(q[0]-p[0])-dx*(q[1]-p[1]))/area
        a = 1-b-c
        z = a*depths[ids[0]] + b*depths[ids[1]] + c*depths[ids[2]]
        region = np.s_[y0:y1+1,x0:x1+1]
        visible = (a>=0)&(b>=0)&(c>=0)&(z>depth[region])
        if not visible.any():
            continue
        coords = a[...,None]*tex[ids[0]]+b[...,None]*tex[ids[1]]+c[...,None]*tex[ids[2]]
        tile = pixels(material)
        h,w = tile.shape[:2]
        paint = tile[np.floor((1-coords[...,1])*h).astype(int)%h, np.floor(coords[...,0]*w).astype(int)%w]
        visible &= paint[...,3]>80
        normal = np.cross(xyz[ids[1]]-xyz[ids[0]], xyz[ids[2]]-xyz[ids[0]])
        illumination = .74+.26*abs(normal @ [.24,.85,.47])/max(1.e-9,np.linalg.norm(normal))
        rgb[region][visible] = np.clip(paint[...,:3][visible]*illumination,0,255)
        depth[region][visible] = z[visible]
    return Image.fromarray(rgb)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbench", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default(size=13)
    paths = sorted(args.workbench.rglob("*.obj"))
    with (args.destination/"index.csv").open("w", newline="") as out:
        index = csv.writer(out)
        index.writerow(["id","page","row","column","mesh"])
        for start in range(0,len(paths),64):
            page = Image.new("RGB",(8*100,8*118),(38,37,34))
            draw = ImageDraw.Draw(page)
            number = start//64+1
            name = f"models-{number:03}.jpg"
            for i,path in enumerate(paths[start:start+64]):
                row,col = divmod(i,8)
                x,y = col*100,row*118
                page.paste(render(path),(x+2,y))
                draw.text((x+4,y+97),str(start+i+1),font=font,fill="white")
                index.writerow([start+i+1,name,row+1,col+1,path.relative_to(args.workbench)])
            page.save(args.destination/name,quality=85)
    print(f"{len(paths)} meshes in {(len(paths)+63)//64} pages")


if __name__ == "__main__":
    main()
