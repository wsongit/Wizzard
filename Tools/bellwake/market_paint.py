"""Paint the cut-bank, stair stone and turf for the opening village at 64 texels per tile."""
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
from surface_paint import save_tile

root = Path(__file__).resolve().parents[2]
out = root / "Assets/Resources/Bellwake/Textures"
def save(name, pixels):
    Image.fromarray(np.uint8(np.clip(pixels, 0, 255))).save(out / (name + ".png"))

def well_materials():
    rng=np.random.default_rng(1885)
    save_tile('SpringStone', out)
    cord=np.zeros((32,32,3))
    for j in range(32):
        for i in range(32):
            turn=(i+2*j)%8
            cord[j,i]=np.array((148,121,77))+(14 if turn<2 else -18 if turn>5 else 2)+rng.uniform(-6,6)
    save('FlaxCord',cord)

def make():
    well_materials()
    save_tile("MarketCutbank", out)

    save_tile("GateStone", out)
    save_tile("VillageTurf", out)

    # Paint the worn lanes into the same ground sheet as the turf and the baked shadows.
    n=512
    yy,xx=np.mgrid[:n,:n]
    wx=(xx+.5)*40/n-20
    wy=20-(yy+.5)*40/n
    lanes=[
        ([(-.7,-21),(-.9,-13),(-1.4,-6),(.55,.5),(1.6,5),(0,9),(0,21)],1.68),
        ([(-1.4,-6),(-4.4,-4.8),(-8.2,-4.6),(-12.1,-1.8)],.92),
        ([(.55,.5),(4.5,2.0),(8,4.0),(11.6,7.8)],1.02),
        ([(.2,5.5),(-2.5,6.8),(-4.8,6.0),(-10.2,7.6)],.84),
        ([(.3,-8),(4,-7.2),(8.6,-7.3),(13,-8.5)],.89)]
    distance=np.full((n,n),100.)
    for points,width in lanes:
        for a,b in zip(points,points[1:]):
            dx,dy=b[0]-a[0],b[1]-a[1]
            q=np.clip(((wx-a[0])*dx+(wy-a[1])*dy)/(dx*dx+dy*dy),0,1)
            distance=np.minimum(distance,np.hypot(wx-a[0]-q*dx,wy-a[1]-q*dy)-width)
    def haze(sigma):
        a=gaussian_filter(rng.standard_normal((n,n)),sigma,mode="wrap")
        return a / a.std()
    rng = np.random.default_rng(7122)
    patch=haze(22);brush=haze(5);grit=haze(.8)
    edge=np.clip(.5-distance*.94+brush*.20+grit*.06,0,1)
    edge=edge*edge*(3-2*edge)
    grass=np.asarray(Image.open(out/'VillageTurf.png')).astype(float)
    dirt=np.asarray(Image.open(out/'DirtPath.png').convert('RGB')).astype(float)
    meadow=grass[yy%64,xx%64]*(1+patch[:,:,None]*.049)
    dust=dirt[yy%64,xx%64]*np.array([1.04,1.04,1.02])+np.array([4,5,3])
    ground=(1-edge[:,:,None])*meadow+edge[:,:,None]*(dust+brush[:,:,None]*3.5)
    destination=root/'Tools/bellwake/.web-assets'
    destination.mkdir(parents=True,exist_ok=True)
    Image.fromarray(ground.clip(0,255).astype('uint8')).save(destination/'BellmarketUnlit.png')

if __name__ == '__main__':
    make()
