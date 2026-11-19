"""Paint five 2:1 equirectangular N64-style skies. Cloud noise is sampled once, offline."""

import sys
import numpy as np
from scipy.ndimage import map_coordinates, gaussian_filter
from PIL import Image
from pathlib import Path

res = Path(__file__).resolve().parents[2] / "Assets/Resources/Bellwake/Skies"
res.mkdir(exist_ok=True)
for k, (name, top, low) in enumerate(
    [
        ("Bellmarket", (87, 135, 182), (228, 202, 156)),
        ("RootChoir", (69, 112, 120), (179, 198, 154)),
        ("Reedwater", (69, 121, 153), (188, 211, 197)),
        ("CinderLens", (102, 73, 98), (214, 154, 110)),
        ("StillBelfry", (34, 41, 76), (154, 145, 180)),
        ("Morning", (106, 158, 196), (255, 208, 162)),
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
    cloud = np.array(low) * 0.98 + silver[:, :, None] * 42
    rgb = rgb * (1 - alpha[:, :, None]) + cloud * alpha[:, :, None]
    target = np.array([-0.57, 0.49, 0.66])
    target /= np.linalg.norm(target)
    dot = xx * target[0] + y * target[1] + zz * target[2]
    halo = np.clip((dot - 0.957) / 0.043, 0, 1) ** 4 * 0.39
    disc = np.clip((dot - 0.9976) * 2100, 0, 1)
    mask = np.maximum(halo, disc) * (1 - alpha * 0.7)
    rgb = (
        rgb * (1 - mask[:, :, None])
        + np.array([254, 232, 177] if k != 4 else [230, 222, 206]) * mask[:, :, None]
    )
    if k == 4:
        for i in range(390):
            x = rng.integers(0, w)
            z = rng.integers(2, h // 2 - 9)
            rgb[z, x] = [198, 201, 197]
    Image.fromarray(np.uint8(np.clip(rgb, 0, 255))).save(res / (name + ".jpg"), quality=91)
