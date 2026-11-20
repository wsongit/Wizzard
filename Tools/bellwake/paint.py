"""Make tiling 64px surface paintings and copy the library's matching UV atlases."""

from pathlib import Path
import sys, shutil
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

root = Path(__file__).resolve().parents[2]
dst = root / "Assets/Resources/Bellwake/Textures"
from material_swatches import repaint
from surface_paint import SURFACES, save_tile, joinery
lib = Path(sys.argv[1])
for path in sorted((lib / "Textures").glob("*_atlas.png")):
    name = path.stem.split("_")[0]
    if not (dst / (name + "Atlas.png")).exists():
        continue
    repaint(lib / "Textures" / (name + "_atlas.png"), dst / (name + "Atlas.png"))
# Three small legacy swatches retain their published pigment pattern. They
# originally occupied positions 1, 5 and 11 in the shared random sequence.
swatches = {1: ("Skin", (155, 107, 66)), 5: ("Reeds", (90, 107, 83)), 11: ("Inlay", (126, 112, 127))}
pigment = np.random.default_rng(671)
y, x = np.mgrid[:64, :64]
for index in range(max(swatches) + 1):
    grain = pigment.normal(0, 1, (64, 64))
    if index not in swatches:
        continue
    name, colour = swatches[index]
    detail = gaussian_filter(grain, 1.5, mode="wrap")
    mottling = gaussian_filter(grain, 4, mode="wrap")
    shade = detail / detail.std() * 5 + mottling / mottling.std() * 8 + grain * 3
    if name == "Inlay":
        u = (x + (y // 16 % 2) * 16) % 32
        v = y % 16
        shade += np.where((u <= 1) | (v == 0), -29, np.where((v == 2) | (u == 3), 13, 0))
        shade += np.where(abs((x % 16) - 8) + abs((y % 16) - 8) == 7, 32, 0)
    rgb = colour + shade[..., None] * np.array([1, .92, .78])
    Image.fromarray(np.uint8(np.clip(rgb, 0, 255))).save(dst / (name + ".png"))
for name in SURFACES:
    save_tile(name, dst)
joinery(dst)

# One continuous terrain painting per room. Smooth junctions share the collision surface.
rng = np.random.default_rng(671)
# Ground lighting has its own sequence, independent of further palette edits.
rng.normal(0, 1, (3, 64, 64))

names = ["Bellmarket", "RootChoir", "Reedwater", "CinderLens", "StillBelfry"]
n = 512
gy, gx = np.mgrid[:n, :n]
wx = (gx + 0.5) * 40 / n - 20
wy = 20 - (gy + 0.5) * 40 / n


def segment(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = np.clip(((wx - a[0]) * dx + (wy - a[1]) * dy) / (dx * dx + dy * dy), 0, 1)
    return np.hypot(wx - a[0] - dx * t, wy - a[1] - dy * t)


edges = [
    [[(0, -20), (-1, -6), (1, 4), (0, 18)], [(-14, -3), (-3, -1), (6, 4), (15, 7)]],
    [
        [(0, -20), (1, -11), (-3, -4), (-7, 2), (0, 8), (5, 10), (0, 17)],
        [(0, 8), (8, 0), (3, -5), (-3, -4)],
    ],
    [[(0, -20), (0, 18)], [(-8, 8), (-7, 1), (0, 4), (7, 1), (8, 8)]],
    [[(0, -20), (-1, -9), (-5, -1), (-5, 7), (6, 7), (6, -3)], [(6, 7), (0, 15)]],
    [
        [(0, -20), (0, 18)],
        [(-8, 2), (-5, 8), (0, 10), (5, 8), (8, 2), (5, -4), (0, -6), (-5, -4), (-8, 2)],
    ],
]
for k, key in enumerate(names):
    a, b = [
        ("Grass", "DirtPath"),
        ("Moss", "Loam"),
        ("Reeds", "Causeway"),
        ("Basalt", "Setts"),
        ("Slate", "Inlay"),
    ][k]

    def tile(path):
        pixels = np.array(Image.open(dst / (path + ".png")).convert("RGB")).astype(float)
        return pixels[(gy // 1) % 64, (gx // 1) % 64]

    dist = np.minimum.reduce([segment(a1, b1) for line in edges[k] for a1, b1 in zip(line, line[1:])])
    noise = gaussian_filter(rng.normal(0, 1, (n, n)), 7, mode="wrap")
    noise /= noise.std()
    alpha = np.clip((2.1 - dist + 0.26 * noise) * 1.8 + 0.5, 0, 1)[:, :, None]
    canvas = (tile(a) * (1 - alpha) + tile(b) * alpha) * (1 + 0.055 * noise[:, :, None])
    # Moss and accumulated soot at the foot of the escarpment.
    rim = np.clip((np.maximum(abs(wx), abs(wy)) - 14) / 8, 0, 0.82)
    canvas *= 1 - 0.24 * rim[:, :, None]
    Image.fromarray(np.uint8(np.clip(canvas, 0, 255))).save(dst / (key + "Ground.png"))
    output = root / "Tools/bellwake/.web-assets"
    output.mkdir(exist_ok=True)
    shutil.copyfile(dst / (key + "Ground.png"), output / (key + "Unlit.png"))
