"""Repaint the 16 fixed 32px UV islands used by Bellwake's Blender prop and NPC library."""
from pathlib import Path
import numpy as np
from PIL import Image
from surface_paint import tinted

STUDIES = {0:"oak", 1:"dock-oak", 2:"fieldstone", 3:"cliff", 4:"bronze",
           5:"linen", 7:"blue-canvas", 8:"linen", 10:"bronze", 15:"oak-leaves"}

def repaint(source, dest):
    im=Image.open(source).convert("RGB")
    if im.size!=(128,128): raise ValueError(source)
    output=Image.new("RGB",im.size)
    rng=np.random.default_rng(sum(source.stem.encode()))
    y,x=np.mgrid[:32,:32]
    for i in range(16):
        left=(i%4)*32
        top=(3-i//4)*32
        crop=im.crop((left,top,left+32,top+32))
        base=np.median(np.asarray(crop),axis=(0,1))
        coarse=rng.normal(0,1,(5,5))
        cloud=np.asarray(Image.fromarray(coarse.astype("float32")).resize((32,32),Image.Resampling.BICUBIC))
        value=cloud*5+rng.normal(0,1.6,(32,32))
        if i in (0,1):
            # Grain follows two or three grain lines around an off-centre knot.
            grain=x+.10*y+1.4*np.sin(y*.14)+4*np.exp(-((y-17)/5)**2)
            value+=np.where((grain%10)<1.2,-24,np.where((grain%10)<2.2,10,0))
            value-=17*np.exp(-((x-13)/1.8)**2-((y-17)/3.7)**2)
        elif i in (2,3):
            mortar=(y+np.round(.8*np.sin(x*.24)))%14
            seam=(x+15*((y//14)%2)+np.round(1.2*np.sin(y*.21)))%28
            value+=np.where((mortar<=1)|(seam<1),-26,np.where((mortar<3)|(seam<2),14,0))
        elif i in (5,7,8):
            value+=7*np.sin((x*.20+y*.08)+cloud*.23)
            value+=np.where(y==25,13,np.where((y==26)|(y==28),-14,0))
            value+=np.where((y==22)&((x//3)%2==0),8,0)
        elif i in (4,10,11,12):
            # Broad hammered changes in value and two small edge catches on hard surfaces.
            value+=16*np.exp(-((x+y-15)/4)**2)-10*np.exp(-((x+y-27)/8)**2)
            value+=np.where((y==3)&(x>5)&(x<18),12,0)
        elif i==15:
            value+=np.where(cloud>.15,11,-7)+np.where((cloud>.15)&(cloud<.32),8,0)
        elif i==13:
            value=value*.38 + 6*np.cos((y-7)*.12)
        else:
            value+=4*np.cos((y+x*.3)*.16)
        if i in STUDIES:
            # Keep the library's reserved UV islands and identifying colours. Paint
            # grain, chipped edges and weave inside those islands, avoiding face regions.
            pigment = np.asarray(tinted(STUDIES[i],base,18 if i in (0,1,2,3,15) else 11,(32,32)))
            value = value * (.33 if i in (5,7,8) else .14)
            base = pigment.astype(float)
        arr=base+value[:,:,None]*np.array([1,.93,.75])
        arr=np.clip(arr,0,255).astype(np.uint8)
        output.paste(Image.fromarray(arr),(left,top))
    output.save(dest)

if __name__=="__main__":
    import argparse
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('library',type=Path)
    args=cli.parse_args()
    target=Path(__file__).resolve().parents[2]/"Assets/Resources/Bellwake/Textures"
    for atlas in (args.library/"Textures").glob("*_atlas.png"):
        out=target/(atlas.stem.split('_')[0]+"Atlas.png")
        if out.exists(): repaint(atlas,out)
