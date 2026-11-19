"""Make tiling 64px surface paintings and copy the library's matching UV atlases."""

from pathlib import Path
import sys, shutil
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

root = Path(__file__).resolve().parents[2]
dst = root / "Assets/Resources/Bellwake/Textures"
from material_swatches import repaint
lib = Path(sys.argv[1])
for name in ["Village", "Forest", "Swamp", "Lava", "Foundry", "Haunted", "Ruins", "Sky"]:
    repaint(lib / "Textures" / (name + "_atlas.png"), dst / (name + "Atlas.png"))
for name in [
    "Mountain",
    "Grass",
    "DirtPath",
    "Masonry",
    "Wood",
    "Leaves",
    "Brass",
    "RoofSlate",
    "RoofTiles",
    "HousePlaster",
    "WindowDark",
    "Awning",
    "OchrePlaster",
    "WindowLight",
]:
    shutil.copyfile(root / "Assets/Resources/VillageTextures" / (name + ".png"), dst / (name + ".png"))
colors = {
    "Fur": (103, 68, 43),
    "Skin": (155, 107, 66),
    "Moss": (82, 111, 52),
    "Loam": (116, 88, 58),
    "MossRock": (98, 108, 70),
    "Reeds": (90, 107, 83),
    "Causeway": (153, 133, 97),
    "Shale": (92, 112, 116),
    "Basalt": (72, 64, 73),
    "Setts": (126, 98, 87),
    "Slate": (79, 83, 112),
    "Inlay": (126, 112, 127),
    "Pennon": (169, 69, 45),
    "FernCloth": (73, 133, 91),
    "SeaCloth": (57, 132, 141),
    "CoalCloth": (165, 84, 52),
    "NightCloth": (106, 80, 136),
    "BellMetal": (143, 100, 57),
    "Amber": (249, 188, 68),
    "SeaGlass": (111, 211, 191),
    "Water": (66, 138, 143),
}
y, x = np.mgrid[:64, :64]
rng = np.random.default_rng(671)
for name, c in colors.items():
    a = rng.normal(0, 1, (64, 64))
    detail = gaussian_filter(a, 1.5, mode="wrap")
    mott = gaussian_filter(a, 4, mode="wrap")
    t = detail / detail.std() * 5 + mott / mott.std() * 8 + a * 3
    if name in ("Shale", "Basalt", "Slate", "Setts", "Inlay", "Causeway", "MossRock"):
        row = y // 16
        u = (x + (row % 2) * 16) % 32
        v = y % 16
        t += np.where((u <= 1) | (v == 0), -29, np.where((v == 2) | (u == 3), 13, 0))
        if name == "Inlay":
            t += np.where(abs((x % 16) - 8) + abs((y % 16) - 8) == 7, 32, 0)
    elif name in ("FernCloth", "SeaCloth", "CoalCloth", "NightCloth", "Pennon"):
        t = t * 0.45 + ((x + y) % 2) * 5 + np.where(abs((x % 16) - 8) + abs((y % 16) - 8) < 5, 27, 0)
    elif name in ("SeaGlass", "Amber", "Water"):
        t = (
            t * 0.3
            + 8 * np.sin(y * np.pi / 8 + np.sin(x * np.pi / 16))
            + np.where((y + np.rint(2 * np.sin(x * np.pi / 16))) % 16 == 0, 24, 0)
        )
    elif name == "BellMetal":
        t = t * 0.7 + np.where(y % 16 < 2, 16, 0)
    arr = np.array(c)[None, None, :] + t[:, :, None] * np.array([1, 0.92, 0.78])
    Image.fromarray(np.clip(arr, 0, 255).astype("uint8")).save(dst / (name + ".png"))
# One continuous terrain painting per room. Smooth junctions share the collision surface.
from scipy.ndimage import map_coordinates

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
