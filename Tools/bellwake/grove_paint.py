"""Original 64-pixel bark, leaf clusters, moth scales and enamel for the dawn clearing."""
import math, random
from pathlib import Path
from PIL import Image, ImageDraw
root=Path(__file__).resolve().parents[2]/'Assets/Resources/Bellwake/Textures'
rng=random.Random(18117)
def save(name,im):
    im.convert('RGB').save(root/(name+'.png'),optimize=True)
# Low-frequency olive clumps and a few individual leaf tips remain readable when mipmapped.
import numpy as np
from scipy.ndimage import gaussian_filter
paint_rng=np.random.default_rng(4230)
def patch(sigma):
    a=gaussian_filter(paint_rng.normal(size=(64,64)),sigma,mode='wrap')
    return a/a.std()
from surface_paint import save_tile
save_tile('ElderLeaf',root)
save_tile('ElderBark',root)
def palette(t,stops):
    return np.uint8(np.stack([np.interp(t,np.linspace(0,1,len(stops)),[c[i] for c in stops]) for i in range(3)],axis=-1))
wing=Image.new('RGB',(64,64),'#493e48');d=ImageDraw.Draw(wing)
for y in range(64):
    for x in range(64):
        vein=(x+.26*y)/64
        value=.25+.50*math.sin(math.pi*x/64)**.65+.12*math.cos(23*vein)+rng.uniform(-.04,.04)
        wing.putpixel((x,y),tuple(round(a+(b-a)*value) for a,b in zip((66,75,75),(152,190,160))))
for end in [(63,5),(63,21),(63,41),(47,63),(24,63)]:
    d.line([(1,34),(22,30),(36,28),end],fill='#687b68',width=1)
for x,y,r in [(46,15,7),(52,32,4),(41,47,3)]:
    d.ellipse((x-r,y-r,x+r,y+r),fill='#5e6057',outline='#c6b672')
    d.ellipse((x-r//2,y-r//2,x+r//2,y+r//2),fill='#d5c282')
    d.point((x-1,y-1),fill='#f4e3ac')
save('MothWing',wing)
lamp=Image.new('RGB',(64,64));p=lamp.load()
for y in range(64):
    for x in range(64):
        v=max(0,min(1,(.8+.2*math.sin(y*.13))*(.6+.4*math.sin(math.pi*x/64)**.6)+rng.uniform(-.05,.04)))
        p[x,y]=tuple(round(a+(b-a)*v) for a,b in zip((150,82,23),(255,228,134)))
save('MothLamp',lamp)

# The bellrunner's ferry uses this blue pennant and copper crossing mark.
sign=Image.new('RGB',(64,64),'#4f7278');d=ImageDraw.Draw(sign)
for y in range(64):
    d.line((0,y,63,y),fill=rng.choice(['#567a7b','#557779','#507779','#537376']))
d.rectangle((3,3,60,60),outline='#b2a579',width=2)
d.rectangle((6,6,57,57),outline='#334f59')
d.ellipse((26,11,38,22),fill='#a98248',outline='#3f504e',width=2)
d.polygon([(28,18),(36,18),(39,24),(40,34),(45,40),(19,40),(24,34),(25,25)],fill='#d4af67',outline='#4c5146',width=2)
d.ellipse((29,38,35,44),fill='#dfb964',outline='#6e6148')
for x,y in [(12,48),(19,50),(26,48),(33,50),(40,48)]:
    d.line([(x,y),(x+4,y+1),(x+7,y)],fill='#d4c08d',width=2)
save('FerryEnamel',sign)

yy,xx=np.mgrid[:64,:64]
save_tile('RiverSteel',root)

timber=palette(np.clip(.47+.12*patch((5,1.4))+.04*patch(1),0,1),[(64,51,41),(96,71,48),(135,101,67),(157,125,79)])
shield=Image.fromarray(timber);d=ImageDraw.Draw(shield)
for x in [12,26,40,52]:
    d.line([(x,0),(x-1,24),(x+1,42),(x,63)],fill='#534639')
# Two tidal bands follow the shield's taper underneath its brass boss.
for z in [35,43]:
    d.line([(3,z-6),(13,z),(23,z+2),(31,z-1),(40,z-3),(48,z-2),(60,z+3)],fill='#364f53',width=5)
    d.line([(3,z-7),(13,z-1),(23,z+1),(31,z-2),(40,z-4),(48,z-3),(60,z+2)],fill='#92b1a0',width=2)
for x,z in [(14,13),(49,13),(21,46),(41,46)]:
    d.ellipse((x-2,z-2,x+2,z+2),fill='#927644',outline='#4e4b3b')
    d.point((x-1,z-1),fill='#ded098')
save('FerryShieldFace',shield)

blush=np.exp(-((xx-20)/18)**2-((yy-39)/20)**2)
rough=patch(2.6)*4+patch(.55)*3
fruit=np.stack([207+25*blush+rough,168-47*blush+rough*.87,69-14*blush+rough*.5],axis=-1)
pear=Image.fromarray(np.uint8(np.clip(fruit,0,255)));d=ImageDraw.Draw(pear)
for i in range(125):
    x,y=rng.randrange(64),rng.randrange(64);c=np.asarray(pear.getpixel((x,y)))//1.22
    d.point((x,y),fill=tuple(int(k) for k in c))
save('HoneyPear',pear)
