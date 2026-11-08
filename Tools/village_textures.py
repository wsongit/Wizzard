"""Original 64px material tiles, shared by the Unity model and Blender previews."""
import bpy, math, random
PALETTES={
 'HousePlaster':((.43,.36,.23),(.85,.77,.56)),
 'RoofTiles':((.20,.075,.035),(.64,.30,.13)),
 'Wood':((.12,.065,.025),(.42,.27,.10)),
 'Masonry':((.19,.21,.17),(.54,.52,.40)),
 'EarthCliff':((.23,.25,.19),(.52,.48,.33)),
 'Leaves':((.12,.32,.035),(.42,.67,.15)),
 'Grass':((.13,.19,.045),(.44,.46,.14)),
 'DirtPath':((.27,.18,.085),(.57,.44,.23)),
 'WindowLight':((.70,.30,.015),(1,.75,.12)),
 'Feathers':((.55,.53,.42),(.9,.87,.73)),
 'Comb':((.42,.035,.015),(.75,.1,.025)),
 'SailCloth':((.40,.34,.21),(.79,.71,.50))}
def create(root):
 out=root/'Assets/Resources/VillageTextures';out.mkdir(parents=True,exist_ok=True)
 result={}
 for kind,(lo,hi) in PALETTES.items():
  rng=random.Random(87+sum(map(ord,kind)))
  grid=[[rng.random() for x in range(8)] for y in range(8)]
  def noise(x,y):
   ix=int(x)//8;iy=int(y)//8;u=(x%8)/8;v=(y%8)/8
   u=u*u*(3-2*u);v=v*v*(3-2*v)
   return (grid[iy%8][ix%8]*(1-u)+grid[iy%8][(ix+1)%8]*u)*(1-v)+(grid[(iy+1)%8][ix%8]*(1-u)+grid[(iy+1)%8][(ix+1)%8]*u)*v
  pixels=[]
  for y in range(64):
   for x in range(64):
    n=noise(x,y);t=.15+.7*n+rng.uniform(-.15,.15)
    if kind in ('RoofTiles','Masonry'):
     row=y//8;shift=(row%2)*8;col=((x+shift)%64)//16
     t=.22+.55*grid[row%8][col]+rng.uniform(-.12,.12)
     if y%8==0 or (x+shift)%16==0:t=.01
     elif y%8==1:t=min(1,t+.2)
     if kind=='Masonry' and y%8>5 and n>.55:t*=.7
    if kind=='Wood':t=.15+.5*noise(x*2,y*.25)+.12*math.sin(x*.8+noise(x,y)*2)+rng.uniform(-.07,.07)
    if kind=='SailCloth':t=.4+.4*n-(.18 if x%16<2 else 0)
    if kind=='WindowLight':t=.65+.3*n
    t=max(0,min(1,t));pixels.extend([lo[c]+(hi[c]-lo[c])*t for c in range(3)]+[1])
  image=bpy.data.images.new(kind+'64',width=64,height=64);image.pixels=pixels;image.filepath_raw=str(out/(kind+'.png'));image.file_format='PNG';image.save();image.pack();result[kind]=image
 return result
