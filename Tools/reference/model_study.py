"""Make Blender-readable, limb-local mesh studies from ZeldaRET's PAL 1.1 extraction.

Run on the extracted assets tree from the user's ROM, outside the Unity project.
Each display-list fragment gets its own OBJ. Retain the extracted sources next to
the result for matrix, branch, animation and runtime segment interpretation.
"""
import argparse
from collections import Counter
from functools import lru_cache
import json
import os
from pathlib import Path
import re
from PIL import Image

COMMAND = re.compile(r'\b(gs(?:SP(?:Vertex|1Triangle|2Triangles|1Quadrangle|ModifyVertex|Matrix)|DPLoad(?:Multi|Texture)Block(?:_4b)?))\((.*?)\)',re.S)
VTX = re.compile(r'\bVTX\(([^)]+)\)')
REFERENCE = re.compile(r'&?(\w+)(?:\[(\d+)\])?$')

@lru_cache(maxsize=384)
def vertices(path):
    if not path or not path.exists(): return []
    return [tuple(int(x.strip(),0) for x in m.split(',')[:5]) for m in VTX.findall(path.read_text())]

@lru_cache(maxsize=512)
def size(path):
    if not path: return (32,32)
    with Image.open(path) as im: return im.size

def export_fragment(source, body, output, textures, stats):
    cache, points, faces, paints = {}, [], [], {}
    material = None
    for op,args in COMMAND.findall(body):
        args = [x.strip() for x in args.split(',')]
        if op.startswith('gsDPLoad'):
            material = textures.get(args[0])
        elif op=='gsSPMatrix':
            stats['matrix_commands']+=1
        elif op=='gsSPVertex':
            m=REFERENCE.fullmatch(args[0])
            data=vertices(source.with_name(m[1]+'.inc.c')) if m else []
            start=int(m[2] or 0) if m else 0
            count,slot=int(args[1],0),int(args[2],0)
            for i in range(count):
                cache[slot+i]=data[start+i] if start+i<len(data) else None
        elif op=='gsSPModifyVertex':
            if args[1]=='G_MWO_POINT_ST' and cache.get(int(args[0],0)):
                slot=int(args[0],0)
                value=int(args[2],0)
                def signed(n):return ((n+32768)%65536)-32768
                cache[slot]=(*cache[slot][:3],signed(value>>16),signed(value&65535))
        else:
            ids=[int(x,0) for x in args]
            tris=[ids[:3]]
            if op=='gsSP2Triangles': tris.append(ids[4:7])
            if op=='gsSP1Quadrangle': tris.append([ids[0],ids[2],ids[3]])
            for tri in tris:
                verts=[cache.get(k) for k in tri]
                if None in verts:
                    stats['triangles_requiring_runtime_vertices']+=1
                    continue
                width,height=size(material)
                first=len(points)+1
                points.extend([(x,y,z,s/(32*width),1-t/(32*height)) for x,y,z,s,t in verts])
                slot=paints.setdefault(material,'paint'+str(len(paints)))
                faces.append((slot,first))
    if not faces: return
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('w') as f:
        f.write('mtllib '+output.with_suffix('.mtl').name+'\n')
        for x,y,z,u,v in points:
            f.write(f'v {x} {y} {z}\nvt {u:.5f} {v:.5f}\n')
        last=None
        for slot,first in faces:
            if slot!=last: f.write('usemtl '+slot+'\n');last=slot
            f.write('f '+' '.join(f'{i}/{i}' for i in range(first,first+3))+'\n')
    with output.with_suffix('.mtl').open('w') as f:
        for tex,slot in paints.items():
            f.write(f'newmtl {slot}\nKd 1 1 1\n')
            if tex:f.write('map_Kd '+os.path.relpath(tex,output.parent)+'\n')
    stats['fragments']+=1
    stats['static_triangles']+=len(faces)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('assets',type=Path)
    parser.add_argument('destination',type=Path)
    args=parser.parse_args()
    src=args.assets.resolve();dest=args.destination.resolve()
    if dest.is_relative_to(src): raise ValueError("Use a separate output directory")
    stats=Counter()
    for path in sorted({f.parent for f in src.rglob('*.inc.c')}):
        textures={p.name.split('.')[0]:p for p in sorted(path.glob('*.png'))}
        if path.name=='object_sa':
            # EnSa_Draw binds the two eye segments and the mouth independently.
            for slot, name in [('0x08000000','gSariaEyeOpenTex'),('0x09000000','gSariaEyeOpenTex'),
                               ('0x0A000000','gSariaMouthClosedTex')]:
                textures[slot]=textures[name]
        for f in path.glob('*.inc.c'):
            body=f.read_text()
            if not re.search(r'gsSP(?:[12]Triangle|1Quadrangle)',body):continue
            stats['draw_fragments_seen']+=1
            out=dest/f.relative_to(src).parent/(f.name[:-6]+'.obj')
            export_fragment(f,body,out,textures,stats)
    (dest/'coverage.json').write_text(json.dumps(stats,indent=2)+'\n')
    print(json.dumps(stats))
if __name__=='__main__':main()
