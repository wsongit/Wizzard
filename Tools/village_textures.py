"""Original brush-style 64px tiles; broad pigment washes, worn blocks and woodgrain.
RGB palettes and generated image buffers use sRGB; PNGs preserve those values.
No reference pixels are sampled. The saved PNGs are shared with Unity.
"""
import bpy, math, random
PALETTES={
 'HousePlaster':((.49,.43,.32),(.79,.73,.57)),
 'RoofTiles':((.25,.13,.09),(.53,.30,.19)),
 'Wood':((.15,.11,.07),(.37,.27,.15)),
 'Masonry':((.29,.29,.25),(.54,.52,.43)),
 'EarthCliff':((.27,.29,.23),(.51,.48,.36)),
 'Leaves':((.13,.20,.055),(.35,.40,.13)),
 'Grass':((.20,.24,.07),(.53,.52,.24)),
 'DirtPath':((.36,.29,.18),(.56,.47,.30)),
 'WindowDark':((.09,.10,.085),(.24,.25,.20)),
 'WindowLight':((.53,.32,.08),(.74,.52,.17)),
 'Feathers':((.56,.55,.46),(.82,.80,.69)),
 'Comb':((.37,.06,.03),(.60,.14,.06)),
 'SailCloth':((.38,.33,.24),(.70,.64,.47)),
 'Mountain':((.34,.35,.43),(.49,.47,.55))}
def mix(a,b,t):return tuple(x+(y-x)*t for x,y in zip(a,b))
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def create(root):
 out=root/'Assets/Resources/VillageTextures';out.mkdir(parents=True,exist_ok=True)
 result={};art={}
 for kind,(lo,hi) in PALETTES.items():
  rng=random.Random(310+sum(map(ord,kind)))
  dabs=[(rng.uniform(0,64),rng.uniform(0,64),rng.uniform(3,12),rng.uniform(2,8),rng.uniform(-.25,.25)) for _ in range(45)]
  tiles=[[rng.uniform(.3,.8) for _ in range(8)] for _ in range(8)];rgb=[]
  strokes=[(rng.uniform(0,64),rng.uniform(0,64),rng.uniform(.8,2),rng.uniform(1,3),rng.uniform(-.2,.2)) for _ in range(100)] if kind in ('Grass','DirtPath') else []
  for y in range(64):
   for x in range(64):
    wash=.53
    for cx,cy,rx,ry,amount in dabs:
     dx=min(abs(x-cx),64-abs(x-cx))/rx;dy=min(abs(y-cy),64-abs(y-cy))/ry
     wash+=amount*max(0,1-dx*dx-dy*dy)**2
    t=wash
    for cx,cy,rx,ry,amount in strokes:
     dx=min(abs(x-cx),64-abs(x-cx))/rx;dy=min(abs(y-cy),64-abs(y-cy))/ry
     t+=amount*max(0,1-dx*dx-dy*dy)
    if kind in ('RoofTiles','Masonry'):
     height=8 if kind=='RoofTiles' else 16;row=y//height;xx=(x+(row%2)*8)%64;col=int(xx//16)
     edge=min((xx+.7*math.sin(y*.8))%16,16-(xx+.7*math.sin(y*.8))%16);yy=y%height
     t=.5*wash+.5*tiles[row][col]
     if yy<1.3 or edge<1.2:t-=.18
     elif yy<2.5:t+=.12
     if kind=='RoofTiles':t-=.13*(yy/height)
    elif kind in ('Wood','SailCloth'):
     t=wash+math.sin(x*.7+.7*math.sin(y*.12)+math.sin(x*.25))*(.14 if kind=='Wood' else .07)
     if x%16<1:t-=.15
    elif kind=='EarthCliff':
     yy=(y+3*math.sin(x*.15))%64;row=int(yy//16);xx=(x+8*(row%2)+2*math.sin(y*.21))%64;col=int(xx//16)
     edge=min(xx%16,16-xx%16,yy%16,16-yy%16)
     t=.1+.6*tiles[row][col]+.3*wash
     if edge<1:t-=.1
     elif edge<2:t+=.05
    elif kind=='Leaves':t=wash+.18*math.sin(x*.45+math.sin(y*.3))*math.sin(y*.55)
    rgb.append(mix(lo,hi,max(0,min(1,t))))
  art[kind]=rgb
 art['PathBlend']=[]
 for y in range(64):
  for x in range(64):
   edge=min(x,63-x)/63;t=max(0,min(1,(edge-.035-.025*math.sin(y*.31))/.14));t=t*t*(3-2*t)
   art['PathBlend'].append(mix(art['Grass'][y*64+x],art['DirtPath'][y*64+x],t))
 for kind,rgb in art.items():
  image=bpy.data.images.new(kind+'64',width=64,height=64)
  image.pixels=[c for pixel in rgb for c in (*pixel,1)]
  image.filepath_raw=str(out/(kind+'.png'));image.file_format='PNG';image.save();image.pack();result[kind]=image
 return result
