"""Original, reproducible 64px pigment tiles for Mossbell's material families.
All pixels are authored here; reference images are not inputs to the generator.
PNG values are sRGB. Unity and Blender share these exact portable texture files.
"""
import bpy, math, random
PALETTES={
 'HousePlaster':((.49,.43,.32),(.86,.79,.63)),
 'OchrePlaster':((.48,.32,.19),(.80,.62,.38)),
 'RoofTiles':((.24,.085,.045),(.67,.31,.18)),
 'RoofSlate':((.16,.22,.23),(.42,.48,.45)),
 'Wood':((.11,.075,.035),(.45,.32,.16)),
 'Masonry':((.23,.25,.23),(.61,.59,.49)),
 'EarthCliff':((.18,.21,.13),(.63,.58,.40)),
 'Leaves':((.075,.19,.035),(.46,.59,.19)),
 'Grass':((.15,.23,.045),(.61,.61,.27)),
 'DirtPath':((.28,.22,.12),(.65,.54,.34)),
 'WindowDark':((.065,.085,.08),(.21,.26,.23)),
 'WindowLight':((.53,.32,.08),(.74,.52,.17)),
 'Feathers':((.22,.18,.12),(.52,.43,.27)),
 'Comb':((.36,.11,.04),(.61,.27,.09)),
 'SailCloth':((.41,.43,.30),(.78,.75,.53)),
 'Awning':((.16,.30,.27),(.44,.57,.45)),
 'Brass':((.25,.19,.08),(.67,.50,.22)),
 'SpringWater':((.10,.23,.20),(.32,.46,.34)),
 'Petals':((.42,.23,.06),(.87,.66,.22)),
 'Mountain':((.28,.30,.34),(.50,.49,.48))}
def mix(a,b,t):return tuple(x+(y-x)*t for x,y in zip(a,b))
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def create(root):
 out=root/'Assets/Resources/VillageTextures';out.mkdir(parents=True,exist_ok=True)
 result={};art={}
 for kind,(lo,hi) in PALETTES.items():
  rng=random.Random(910+sum(map(ord,kind)))
  grids={n:[[rng.random() for _ in range(n)] for _ in range(n)] for n in (4,8,16,32,64)}
  def noise(x,y,n):
   xx=x*n/64;yy=y*n/64;ix=math.floor(xx);iy=math.floor(yy);u=xx-ix;v=yy-iy
   u=u*u*(3-2*u);v=v*v*(3-2*v);g=grids[n]
   return (g[iy%n][ix%n]*(1-u)+g[iy%n][(ix+1)%n]*u)*(1-v)+(g[(iy+1)%n][ix%n]*(1-u)+g[(iy+1)%n][(ix+1)%n]*u)*v
  # Uneven painted patches; the wrap makes brush dabs tile at every edge.
  dabs=[(rng.uniform(0,64),rng.uniform(0,64),rng.uniform(2,8),rng.uniform(2,7),rng.uniform(-.42,.42)) for _ in range(65)]
  blades=[(rng.randrange(64),rng.randrange(64),rng.uniform(-2,2),rng.randint(2,5),rng.choice((-.22,.20,.27))) for _ in range(125)]
  stones=[(rng.uniform(0,64),rng.uniform(0,64),rng.uniform(.35,.85)) for _ in range(26)]
  rgb=[]
  for y in range(64):
   for x in range(64):
    coarse=noise(x,y,8);fine=noise(x,y,32);grain=noise(x,y,64)
    wash=.20+.40*noise(x,y,4)+.24*coarse+.12*fine+.05*grain
    dab=0
    for cx,cy,rx,ry,amount in dabs:
     dx=min(abs(x-cx),64-abs(x-cx))/rx;dy=min(abs(y-cy),64-abs(y-cy))/ry
     dab+=amount*max(0,1-dx*dx-dy*dy)
    t=wash+dab
    if kind in ('Grass','Leaves'):
     t=.16+.5*coarse+.25*fine+.10*grain+dab
     for cx,cy,lean,length,amount in blades:
      dy=(y-cy+32)%64-32;dx=(x-cx+32)%64-32
      if 0<=dy<length and abs(dx-lean*dy/length)<(.8 if kind=='Grass' else 1.5):
       t+=amount*(1-dy/length*.45)
     # Leaf clusters have dark small gaps and broad lighter centres, no sine stripes.
     if kind=='Leaves':t+=.12*(coarse-.5)
    elif kind=='DirtPath':
     t=.17+.48*coarse+.18*fine+.13*grain+dab*.7
     if grain>.90:t-=.13
    elif kind in ('RoofTiles','RoofSlate','Masonry'):
     height=8 if kind!='Masonry' else 16;row=y//height;xx=(x+(row%2)*8)%64;col=xx//16
     edge=min(xx%16,15-xx%16);yy=y%height
     t=.24+.38*grids[8][row][col]+.2*fine+.16*grain+dab*.35
     if yy==0 or edge==0:t-=.30
     elif yy==1:t+=.20
     elif edge==1:t+=.06
     if kind!='Masonry':t-=.19*yy/height
     # Scattered chips and pigment scratches, not uniform pixel noise.
     if (edge<3 or yy<3) and grain>.72:t+=.14
    elif kind in ('EarthCliff','Mountain'):
     # Irregular long rock facets; no courses or brick grid on natural terrain.
     xx=x+3*(noise(x,y,4)-.5);yy=y+4*(noise(x+13,y,8)-.5)
     near=[]
     for cx,cy,value in stones:
      dx=abs((xx-cx+32)%64-32);dy=abs((yy-cy+32)%64-32)
      near.append((dx*dx*1.5+dy*dy*.55,value))
     near.sort();gap=math.sqrt(near[1][0])-math.sqrt(near[0][0])
     t=.12+.50*near[0][1]+.22*fine+.16*grain+dab*.35
     if gap<.38:t-=.27
     elif gap<1.0:t+=.11
     if coarse<.3:t-=.08
    elif kind=='Wood':
     warp=x+1.8*math.sin(y*math.tau/64)+1.1*math.sin(y*math.tau/32)
     t=.20+.50*noise(warp,y*.25,32)+.15*grain+dab*.25
     if x%16==0:t-=.25
     if x%16==1:t+=.12
     # A few short dark grain marks, interrupted rather than endless bands.
     if noise(warp+11,y,16)<.26:t-=.15
    elif kind in ('HousePlaster','OchrePlaster'):
     t=.40+.27*coarse+.16*fine+.08*grain+dab*.65
     if grain<.12:t-=.10
    elif kind in ('Awning','SailCloth'):
     t=wash+dab*.45+(.035 if (x+y)%2 else -.035)
     if x%32==0:t-=.19
     if x%32==1 and y%4<2:t+=.18
    elif kind=='SpringWater':
     t=.2+.36*coarse+.24*fine
     if .48<fine<.55:t+=.20
    elif kind=='Brass':t=wash+dab*.7+.14*grain
    rgb.append(mix(lo,hi,max(0,min(1,t))))
  art[kind]=rgb
 art['PathBlend']=[];path_alpha=[]
 for y in range(64):
  for x in range(64):
   edge=min(x,63-x)/63;t=max(0,min(1,(edge-.025-.026*math.sin(y*math.tau/32))/.17));t=t*t*(3-2*t)
   # Cutout shoulders reveal the actual ground below, avoiding mismatched grass UVs.
   art['PathBlend'].append(art['DirtPath'][y*64+x]);path_alpha.append(t)
 for kind,rgb in art.items():
  image=bpy.data.images.new(kind+'64',width=64,height=64,alpha=True)
  image.pixels=[c for i,pixel in enumerate(rgb) for c in (*pixel,path_alpha[i] if kind=='PathBlend' else 1)]
  image.filepath_raw=str(out/(kind+'.png'));image.file_format='PNG';image.save();image.pack();result[kind]=image
 return result
