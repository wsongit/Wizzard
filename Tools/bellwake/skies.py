"""Paint the 2:1 district panoramas and fit each outdoor skyline to its surroundings."""

import json, sys
import numpy as np
from scipy.ndimage import map_coordinates, gaussian_filter
from PIL import Image
from pathlib import Path

res = Path(__file__).resolve().parents[2] / "Assets/Resources/Bellwake/Skies"
res.mkdir(exist_ok=True)
profiles=json.loads((res.parent/"OutdoorSkies.json").read_text())
biomes={name:group for group,names in profiles.items() for name in names}
for k, (name, top, low) in enumerate(
    [
        ("Bellmarket", (57, 94, 185), (183, 198, 213)),
        ("RootChoir", (69, 112, 120), (179, 198, 154)),
        ("Reedwater", (61, 107, 168), (184, 204, 203)),
        ("CinderLens", (102, 73, 98), (214, 154, 110)),
        ("StillBelfry", (34, 41, 76), (154, 145, 180)),
        ("Morning", (86, 136, 192), (231, 198, 175)),
        ("LowerWorks",(40,53,74),(139,145,138)),
        ("Waterworks",(54,87,98),(168,184,169)),
        ("Bronzeworks",(94,59,73),(190,157,132)),
        ("Lampworks",(48,55,96),(150,158,181)),
        ("Saltwake", (57,117,153), (211,205,157)),
        ("RimePost", (66,94,148), (199,218,218)),
        ("Glasscut", (53,58,97), (175,158,171)),
        ("QuinceFold", (73,135,167), (220,212,174)),
        ("SaffronKilns", (105,103,138), (220,171,127)),
        ("VellumWalk", (65,84,127), (184,172,181)),
        ("Cairnwatch", (66,101,143), (200,216,215)),
        ("RainCourt", (64,115,130), (185,205,184)),
        ("Wrenfall", (66, 137, 172), (197, 216, 191)),
        ("Countertide",(52,72,89),(180,156,120)),
        ("Chainwater",(60,93,112),(162,198,190)),
        ("SignalCloth",(73,91,133),(220,183,151)),
        ("KettleLight",(96,132,149),(230,191,151)),
        ("PaperLight",(90,146,165),(249,205,147)),
        ("SaltMud",(92,139,158),(241,204,149)),
        ("SillRain",(74,102,149),(179,197,198)),
        ("ParishInk",(102,126,154),(227,202,169)),
        ("SwallowWater",(83,128,160),(231,202,157)),
    ]
):
    if sys.argv[1:] and name not in sys.argv[1:]: continue
    # Preserve the original atmosphere seeds for existing witness-road districts.
    k = {"Saltwake": 6, "RimePost": 7, "Glasscut": 8, "Wrenfall": 13}.get(name, k)
    rng = np.random.default_rng(522 + k)
    w, h = 768, 384
    v, u = np.mgrid[:h, :w]
    lat = (0.5 - v / h) * np.pi
    lng = u / w * 2 * np.pi
    y = np.sin(lat)
    xx = np.cos(lat) * np.cos(lng)
    zz = np.cos(lat) * np.sin(lng)
    mix = np.clip(y / 0.85, 0, 1) ** 0.62
    rgb = np.array(low) * (1 - mix[:, :, None]) + np.array(top) * mix[:, :, None]
    px = xx / np.maximum(0.17, y + 0.18)
    pz = zz / np.maximum(0.17, y + 0.18)
    noise = np.zeros_like(y)
    for freq, amp in [(2.3, 1), (6, 0.55), (13, 0.20), (29, 0.075)]:
        grid = rng.normal(size=(64, 64))
        noise += amp * map_coordinates(grid, [px * freq + 32, pz * freq + 32], order=3, mode="wrap")
    alpha = np.clip((noise - 0.05) * 0.58, 0, 0.78) * np.clip((y - 0.02) * 6, 0, 1)
    silver = np.clip((noise - 0.4) * 0.2, 0, 0.27)
    valley = name in biomes
    cloud_base = np.array([223,224,233]) if valley else np.array(low)*.98
    cloud = cloud_base + silver[:, :, None] * 42
    rgb = rgb * (1 - alpha[:, :, None]) + cloud * alpha[:, :, None]
    target = np.array([-0.57, 0.49, 0.66])
    target /= np.linalg.norm(target)
    dot = xx * target[0] + y * target[1] + zz * target[2]
    halo = np.clip((dot - 0.957) / 0.043, 0, 1) ** 4 * 0.39
    disc = np.clip((dot - 0.9976) * 2100, 0, 1)
    mask = np.maximum(halo, disc) * (1 - alpha * 0.7) if not valley else np.zeros_like(y)
    rgb = (
        rgb * (1 - mask[:, :, None])
        + np.array([254, 232, 177] if k != 4 else [230, 222, 206]) * mask[:, :, None]
    )
    if valley:
        # An unbroken panorama, painted once; no distant meshes or dynamic lights.
        if biomes[name]=="shores":
            layers=[(44,.027,.075,[141,161,176]),(61,-.014,.033,[119,150,155])]
        elif biomes[name]=="woods":
            layers=[(70,.18,.085,[101,130,117]),(115,.107,.083,[71,103,83])]
        elif biomes[name]=="marshes":
            layers=[(68,.064,.064,[131,153,153]),(93,.011,.041,[112,136,127])]
        else:
            layers=[(46,.13,.14,[142,155,186]),(67,.05,.085,[126,142,155])]
        for layer,(count,base,relief,tone) in enumerate(layers):
            azimuth=np.arange(count)/count*2*np.pi
            jag=rng.uniform(-.45,.45,count)
            outline=base+relief*(.53*np.sin(3*azimuth+.6*layer)+.35*np.sin(7*azimuth+.9)+jag)
            if biomes[name]=="shores":
                # Low islands leave large stretches of open horizon.
                outline*=np.maximum(0,np.sin(azimuth*2+1.9))**1.8
            hline=np.interp(u[0]/w,np.arange(count+1)/count,np.r_[outline,outline[0]])
            slope=(hline-np.roll(hline,1))*w/count
            alpha=np.clip((hline[None,:]-lat)*h/np.pi+.55,0,1)
            silhouette=np.asarray(tone)[None,None,:]+np.clip(slope,-.13,.13)[None,:,None]*60
            rgb=rgb*(1-alpha[:,:,None])+silhouette*alpha[:,:,None]
    if k == 4:
        for i in range(390):
            x = rng.integers(0, w)
            z = rng.integers(2, h // 2 - 9)
            rgb[z, x] = [198, 201, 197]
    Image.fromarray(np.uint8(np.clip(rgb, 0, 255))).save(res / (name + ".jpg"), quality=91)


# Sparse, constant world-space stars. The pole and the panorama seam remain continuous.
if not sys.argv[1:] or "HillStars" in sys.argv[1:]:
    rng=np.random.default_rng(4215)
    stars=np.zeros((384,768,3),dtype=np.uint8)
    for i in range(710):
        angle=np.arcsin(rng.uniform(.14,.998))
        px=int(rng.integers(0,768))
        py=int((.5-angle/np.pi)*384)
        value=rng.integers(69,170)
        colour=np.array([.94,.98,1])*value
        # A wider mark at high latitudes holds a consistent apparent diameter.
        reach=min(5,int(.62/np.cos(angle)))
        for j in range(-reach,reach+1):
            stars[py,(px+j)%768]=colour*(1-.42*abs(j)/(reach+1))
    Image.fromarray(stars).save(res/"HillStars.png")
