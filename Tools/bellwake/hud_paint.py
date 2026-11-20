"""Original 16-pixel heart, ferry-token and digit stamps for the Quest display."""
from pathlib import Path
from PIL import Image, ImageDraw
import random

out=Path(__file__).resolve().parents[2]/"Assets/Resources/Bellwake/Textures"
atlas=Image.new("RGBA",(256,16))
hearts=[(1,4),(3,2),(6,2),(8,4),(10,2),(13,2),(15,4),(15,8),(9,14),(7,14),(1,8)]
def cell(index):
    stamp=Image.new("RGBA",(16,16))
    return stamp,ImageDraw.Draw(stamp)
for i in range(2):
    s,d=cell(i)
    d.polygon(hearts,fill="#272437")
    d.polygon([(2,5),(4,3),(6,3),(8,5),(11,3),(13,3),(14,5),(14,7),(8,13),(2,7)],
              fill="#9d333c" if i==0 else "#635765")
    if i==0:
        d.polygon([(3,5),(5,4),(8,6),(11,4),(13,5),(12,8),(8,11),(4,8)],fill="#eb5d4f")
        d.line([(4,5),(5,4),(6,4)],fill="#ffe3aa")
        d.point((12,5),fill="#ffb783")
    else:
        d.line([(3,5),(4,4),(6,4)],fill="#9a9191")
    atlas.paste(s,(i*16,0))
s,d=cell(2)
d.polygon([(4,1),(11,1),(14,4),(14,11),(11,14),(4,14),(1,11),(1,4)],fill="#282534")
d.polygon([(4,2),(11,2),(13,5),(13,10),(10,13),(5,13),(2,10),(2,5)],fill="#af7d36")
d.line([(3,9),(3,5),(5,3),(10,3)],fill="#ffe6a0",width=2)
d.line([(6,6),(10,6),(10,8),(8,10),(6,8),(6,6)],fill="#503e32")
atlas.paste(s,(32,0))
digits=['111101101101111','010110010010111','111001111100111','111001111001111','101101111001001',
        '111100111001111','111100111101111','111001001001001','111101111101111','111101111001111']
for i,bits in enumerate(digits):
    s,d=cell(i+3)
    for shift,color in [(1,"#2b2836"),(0,"#ffedb0")]:
        for j,on in enumerate(bits):
            if on!='1':continue
            x,y=4+2*(j%3)+shift,3+2*(j//3)+shift
            d.rectangle((x,y,x+1,y+1),fill=color)
    atlas.paste(s,((i+3)*16,0))
s,d=cell(13)
d.polygon([(2,5),(13,5),(8,12),(7,12)],fill="#172735")
d.polygon([(3,4),(12,4),(8,10),(7,10)],fill="#88d7d0")
d.line([(3,4),(12,4)],fill="#d5f4dc")
atlas.paste(s,(208,0))
atlas.save(out/"PocketGlyphs.png")
rng=random.Random(802)
panel=Image.new("RGBA",(192,56))
for y in range(56):
    for x in range(192):
        bevel=min(x,191-x,y,55-y)
        if min(x,191-x)+min(y,55-y)<4:continue
        n=rng.choice([-2,0,0,1,2])+((x//5+2*(y//4))%3)
        c=(16+n,22+n,37+n,218) if bevel>1 else ((57,72,86,218) if bevel==1 else (12,15,22,210))
        panel.putpixel((x,y),c)
d=ImageDraw.Draw(panel)
for x,dx in [(4,1),(187,-1)]:
    for y,dy in [(3,1),(52,-1)]:
        d.line([(x,y+4*dy),(x,y+dy),(x+dx,y),(x+5*dx,y)],fill="#b3a583")
panel.save(out/"Letterpress.png")
