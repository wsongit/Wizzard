"""Small tile paintings for the elderwood shrine and Moss's work clothes."""
import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path
from scipy.ndimage import gaussian_filter
from market_paint import colours

root=Path(__file__).resolve().parents[2]
tex=root/'Assets/Resources/Bellwake/Textures'
def make():
    rng=np.random.default_rng(2873)
    y,x=np.mgrid[:64,:64]
    def noise(s,n=64):
        a=gaussian_filter(rng.normal(size=(n,n)),s,mode='wrap')
        return a/max(.001,a.std())
    moss=noise(3.2);grain=noise(1.2)
    groove=np.cos(2*np.pi*(x/22+y/32+.24*noise(6)))
    t=.46+.11*noise(5)+.09*grain-.09*np.maximum(0,groove)
    stone=colours(t,[(42,45,38),(71,75,61),(104,103,80),(150,146,110)])
    coat=np.clip(.12+.24*moss+.14*grain,0,.85)[...,None]
    im=stone*(1-coat)+np.array([81,100,49])*coat
    Image.fromarray(np.uint8(np.clip(im,0,255))).save(tex/'ChoirOutcrop.png')
    t=.45+.10*moss+.096*noise(1.45)+.033*noise(.2)
    im=Image.fromarray(np.uint8(colours(t,[(36,49,30),(61,78,38),(98,111,53),(137,139,73)])))
    brush=ImageDraw.Draw(im)
    for i in range(105):
        u,v=rng.integers(-2,64,2);d=int(rng.integers(1,4))
        ink=['#708047','#4a6333','#66723c','#977a47'][i%4]
        for dx in [-64,0,64]:
            for dy in [-64,0,64]:
                brush.line([(u+dx-d,v+dy),(u+dx,v+dy-1),(u+dx+d,v+dy+1)],fill=ink)
    im.save(tex/'ChoirLoam.png')
    n=512; yy,xx=np.mgrid[:n,:n];wx=(xx+.5)*40/n-20;wy=20-(yy+.5)*40/n
    d=np.full((n,n),1e3)
    for path,w in [([(0,-21),(-1,-11),(-3,-4),(-7,2),(0,8),(5,10),(0,17)],1.18),
                   ([(0,8),(8,0),(3,-5),(-3,-4)],.98)]:
        for a,b in zip(path,path[1:]):
            dx,dy=b[0]-a[0],b[1]-a[1];q=np.clip(((wx-a[0])*dx+(wy-a[1])*dy)/(dx*dx+dy*dy),0,1)
            d=np.minimum(d,np.hypot(wx-a[0]-dx*q,wy-a[1]-dy*q)-w)
    edge=np.clip(.48-.64*d+.10*noise(3,n),0,1)[...,None]
    litter=np.asarray(im)[yy%64,xx%64].astype(float)*(1+.067*noise(16,n)[...,None])
    track=np.asarray(Image.open(tex/'DirtPath.png').convert('RGB'))[(yy+13)%64,(xx+7)%64]*np.array([.84,.88,.77])
    track+=np.array([9,10,5])+noise(6,n)[...,None]*3
    ground=litter*(1-edge)+track*edge
    dest=root/'Tools/bellwake/.web-assets';dest.mkdir(parents=True,exist_ok=True)
    Image.fromarray(np.uint8(np.clip(ground,0,255))).save(dest/'RootChoirUnlit.png')
    # Warm wool, weathered leather and a copper brooch have different grain at the same pixel density.
    colors=[(110,135,76),(67,92,66),(157,109,68),(191,132,89),(82,71,53),(83,75,57),
            (100,103,82),(169,167,132),(207,190,142),(160,77,52),(202,155,71),(60,50,42),
            (193,151,103),(47,57,56),(230,211,167),(109,64,52)]
    sheet=np.zeros((128,128,3),np.uint8);sy,sx=np.mgrid[:32,:32]
    for i,c in enumerate(colors):
        y0,x0=divmod(i,4)
        relief=noise(1.3,32)*3+rng.normal(0,1.2,(32,32))
        if i in (0,1,4,8,9):relief+=((sx+sy)%3-1)*2.3
        if i in (5,6,7):relief+=3*np.sin(.61*sx+.095*sy)
        sheet[(3-y0)*32:(4-y0)*32,x0*32:(x0+1)*32]=np.uint8(np.clip(np.array(c)+relief[...,None],0,255))
    Image.fromarray(sheet).save(tex/'MossAtelier.png')
