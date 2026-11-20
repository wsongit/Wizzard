"""Paint the cut-bank, stair stone and turf for the opening village at 64 texels per tile."""
from pathlib import Path
import math
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image

root = Path(__file__).resolve().parents[2]
out = root / "Assets/Resources/Bellwake/Textures"
rng = np.random.default_rng(7027)
y, x = np.mgrid[:64, :64]

def wash(sigma):
    values = gaussian_filter(rng.normal(size=(64, 64)), sigma, mode="wrap")
    return (values - values.mean()) / values.std()

def colours(t, stops):
    return np.stack([np.interp(t, np.linspace(0, 1, len(stops)), [c[i] for c in stops])
                     for i in range(3)], axis=-1)

def save(name, pixels):
    Image.fromarray(np.uint8(np.clip(pixels, 0, 255))).save(out / (name + ".png"))

def well_materials():
    rng=np.random.default_rng(1885)
    arr=np.empty((64,64,3),dtype=float)
    for row in range(4):
        widths=rng.multinomial(32,[.25]*4)+8
        phase=int(rng.integers(0,64))
        for width in widths:
            tint=rng.uniform(-10,12)
            for j in range(width):
                for h in range(16):
                    xx=(phase+j)%64;yy=row*16+h
                    shade=(tint+rng.uniform(-7,7) + 13*math.exp(-((h-1)/1.6)**2)
                           - 12*math.exp(-((h-14)/1.7)**2))
                    if j==0 or h==15:shade-=26
                    arr[yy,xx]=np.array((126,123,99))+shade
            phase+=width
    field=gaussian_filter(rng.normal(size=(64,64)),2.8,mode='wrap')
    moss=np.clip((field-.012)*4,0,.49)[:,:,None]
    save('SpringStone',arr*(1-moss)+np.array([96,115,67])*moss)
    cord=np.zeros((32,32,3))
    for j in range(32):
        for i in range(32):
            turn=(i+2*j)%8
            cord[j,i]=np.array((148,121,77))+(14 if turn<2 else -18 if turn>5 else 2)+rng.uniform(-6,6)
    save('FlaxCord',cord)

def make():
    global rng
    well_materials()
    rng = np.random.default_rng(7027)
    # Fracture each tile into long, uneven stone faces. The light lip sits above its own crevice.
    sx = x + 1.45 * wash((5, 3))
    sy = y + 1.7 * wash(4)
    sites = rng.uniform(0, 64, (40, 2))
    dist = np.array([(((sx-a+32)%64-32)*1.65)**2 + (((sy-b+32)%64-32)*.68)**2 for a,b in sites])
    nearest = np.argmin(dist, axis=0)
    edges = np.sqrt(np.partition(dist, 1, axis=0)[:2])
    gap = edges[1]-edges[0]
    color = .49 + rng.uniform(-.17,.17,len(sites))[nearest] + .085*wash(2) + .032*wash(.5)
    color -= .23 * np.maximum(0,1-gap/1.4)
    color += .11 * np.maximum(0,1-abs(gap-1.8)/1.1)
    rock = colours(color, [(64,52,41),(113,93,65),(157,137,96),(195,178,132)])
    lichen = np.clip((wash(4)-.6)*.35,0,.54)[:,:,None]
    save("MarketCutbank", rock*(1-lichen) + np.array([105,114,63])*lichen)

    # Scattered warm scuffs and dark inclusions remain visible from the bottom landing.
    stone = .56 + .09*wash(4) + .07*wash(1.2) + .027*wash(.25)
    row = y//16
    edge = (x+np.array([5,19,1,12])[row])%32
    stone -= .27*((edge==0)|(y%16==0))
    stone += .12*((edge==1)|(y%16==1))
    stone -= .075*(y%16>13)
    save("GateStone",colours(stone,[(67,65,63),(103,99,91),(151,144,124),(200,192,163)]))

    # Short hooked blades and large warm/cool clumps keep the tiled grass readable in motion.
    t=.49+.105*wash(4)+.06*wash(1.4)+.035*wash(.35)
    for i in range(150):
        a,b=rng.integers(0,64,2);h=int(rng.integers(2,5));lean=rng.choice([-1,0,1])
        pigment=rng.choice([-.12,.14,.19])
        for j in range(h):
            t[(b+j)%64,(a+round(lean*j/h))%64]+=pigment*(1-.45*j/h)
    save("VillageTurf",colours(t,[(43,65,36),(89,105,50),(139,149,72),(181,181,103)]))

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
    patch=haze(22);brush=haze(5);grit=haze(.8)
    edge=np.clip(.5-distance*.94+brush*.20+grit*.06,0,1)
    edge=edge*edge*(3-2*edge)
    grass=np.asarray(Image.open(out/'VillageTurf.png')).astype(float)
    dirt=np.asarray(Image.open(out/'DirtPath.png').convert('RGB')).astype(float)
    meadow=grass[yy%64,xx%64]*(1+patch[:,:,None]*.049)
    dust=dirt[yy%64,xx%64]*np.array([1.14,1.14,1.13])+np.array([9,11,7])
    ground=(1-edge[:,:,None])*meadow+edge[:,:,None]*(dust+brush[:,:,None]*3.5)
    destination=root/'Tools/bellwake/.web-assets'
    destination.mkdir(parents=True,exist_ok=True)
    Image.fromarray(ground.clip(0,255).astype('uint8')).save(destination/'BellmarketUnlit.png')

if __name__ == '__main__':
    make()
