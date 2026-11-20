"""Small tile paintings for the elderwood shrine and Moss's work clothes."""
import numpy as np
from PIL import Image
from pathlib import Path
from scipy.ndimage import gaussian_filter
from surface_paint import costume, save_tile

root=Path(__file__).resolve().parents[2]
tex=root/'Assets/Resources/Bellwake/Textures'
def make():
    rng=np.random.default_rng(2873)
    def noise(s,n=64):
        a=gaussian_filter(rng.normal(size=(n,n)),s,mode='wrap')
        return a/max(.001,a.std())
    save_tile('ChoirOutcrop', tex)
    save_tile('ChoirLoam', tex)
    im=Image.open(tex/'ChoirLoam.png').convert('RGB')
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
    costume('MossAtelier', Image.fromarray(sheet), tex)
