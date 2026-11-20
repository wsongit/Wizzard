"""Colour-grade Bellwake's original 64-texel image studies for each surface."""
from pathlib import Path
import numpy as np
from PIL import Image

SOURCES = Path(__file__).with_name("surface_sources")
TEXTURES = Path(__file__).resolve().parents[2] / "Assets/Resources/Bellwake/Textures"

# Centre colour and luminance deviation in sRGB. Preserve local hue variations in
# the painting while allowing, for example, a sunny oak and a shaded elder crown.
SURFACES = {
    "RoofTiles": ("terracotta", (143, 71, 39), 30),
    "RoofSlate": ("slate", (83, 99, 102), 23),
    "GateStone": ("flagstones", (142, 138, 119), 21),
    "Setts": ("cobbles", (130, 105, 89), 22),
    "Causeway": ("flagstones", (153, 135, 100), 22),
    "Slate": ("flagstones", (89, 91, 112), 20),
    "Loam": ("earth", (118, 90, 60), 18),
    "Moss": ("turf", (88, 111, 58), 19),
    "RimeSnow": ("snow", (187, 203, 206), 14),
    "HousePlaster": ("limewash", (199, 180, 143), 19),
    "OchrePlaster": ("limewash", (174, 132, 86), 19),
    "Wood": ("oak", (91, 64, 39), 21),
    "TarredOak": ("dock-oak", (82, 72, 54), 18),
    "Masonry": ("fieldstone", (126, 120, 102), 28),
    "SpringStone": ("well-stone", (125, 125, 108), 30),
    "HarbourBrick": ("brick", (133, 79, 55), 24),
    "Mountain": ("cliff", (115, 111, 109), 19),
    "MarketCutbank": ("cliff", (135, 121, 83), 24),
    "ChoirOutcrop": ("cliff", (91, 99, 67), 22),
    "MossRock": ("cliff", (97, 109, 76), 22),
    "Shale": ("cliff", (95, 107, 108), 20),
    "Basalt": ("cliff", (78, 70, 76), 17),
    "Grass": ("turf", (110, 119, 57), 22),
    "VillageTurf": ("turf", (119, 130, 61), 21),
    "ChoirLoam": ("turf", (78, 93, 47), 18),
    "DirtPath": ("earth", (143, 113, 72), 19),
    "Leaves": ("oak-leaves", (83, 110, 42), 24),
    "RowanLeaf0": ("oak-leaves", (83, 109, 52), 21),
    "RowanLeaf1": ("oak-leaves", (99, 125, 59), 23),
    "RowanLeaf2": ("oak-leaves", (73, 99, 53), 21),
    "ElderLeaf": ("oak-leaves", (91, 117, 52), 23),
    "ElderBark": ("bark", (101, 81, 54), 24),
    "Water": ("water", (67, 132, 137), 16),
    "ParishWater": ("water", (83, 128, 127), 13),
    "WindowDark": ("smoked-glass", (64, 76, 76), 20),
    "WindowLight": ("horn-pane", (171, 123, 55), 22),
    "Amber": ("amber-glass", (225, 165, 68), 24),
    "SeaGlass": ("sea-glass", (100, 186, 164), 24),
    "Fur": ("fur", (111, 73, 45), 21),
    "RiverSteel": ("iron", (153, 172, 174), 19),
    "Brass": ("bronze", (153, 118, 62), 18),
    "BellMetal": ("bronze", (145, 106, 67), 19),
    "MillCanvas": ("linen", (207, 189, 148), 14),
    "Awning": ("blue-canvas", (84, 131, 122), 15),
    "SeaCloth": ("blue-canvas", (65, 127, 140), 14),
    "FernCloth": ("linen", (84, 126, 86), 13),
    "NightCloth": ("blue-canvas", (102, 83, 127), 13),
    "CoalCloth": ("linen", (158, 86, 56), 13),
    "Pennon": ("linen", (172, 80, 51), 14),
}


def tinted(study, colour, contrast, size=(64, 64)):
    with Image.open(SOURCES / (study + ".png")) as source:
        pixels = np.asarray(source.resize(size, Image.Resampling.LANCZOS), dtype=float)
    centered = pixels - np.median(pixels, axis=(0, 1))
    light = centered @ [0.299, 0.587, 0.114]
    # Dark crevices retain colour. In particular, avoid yellow-white tips on green crowns.
    chroma = centered - light[..., None]
    shading = light[..., None] * (contrast / max(1, light.std()))
    output = colour + shading * [1.02, 0.98, 0.83] + chroma * .37
    return Image.fromarray(np.uint8(np.clip(np.round(output), 0, 255)))


def save_tile(name, destination=TEXTURES):
    if name == "SpringStone":
        wall = np.asarray(tinted(*SURFACES[name], size=(128,76)))
        top = np.asarray(tinted("well-coping", (150, 145, 123), 22, (128,36)))
        sheet = np.concatenate((np.pad(wall, ((4,4),(0,0),(0,0)), mode="edge"),
                                np.pad(top, ((4,4),(0,0),(0,0)), mode="edge")))
        Image.fromarray(sheet).save(destination / "SpringStone.png", optimize=True)
        return
    size = (32, 64) if name == "MillCanvas" else (64, 64)
    tile = tinted(*SURFACES[name], size=size)
    if name == "RowanLeaf1":
        tile = tile.transpose(Image.Transpose.ROTATE_90)
    elif name == "RowanLeaf2":
        tile = tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    tile.save(destination / (name + ".png"), optimize=True)


# Each island fills a 64px cell including its mirrored gutter. Later mip levels
# see a neighbourhood of one material before neighbouring colours enter the sample.
PANEL_SIZE = 56
GUTTER = 4
PITCH = 64
COLUMNS = 4
PANEL_NAMES = ("door", "window", "crate", "cask", "door-boards", "shutter")


def joinery(destination=TEXTURES):
    sheet = Image.new("RGB", (COLUMNS * PITCH, 2 * PITCH))
    for i, name in enumerate(PANEL_NAMES):
        source_name = {"door-boards": "dock-oak", "shutter": "window"}.get(name, name)
        with Image.open(SOURCES / (source_name + ".png")) as source:
            art = source.convert("RGB")
            if name == "shutter":
                art = art.crop((4, 12, 14, 51))
            elif name == "door-boards":
                # These doors already have modelled hinges, handles and lintels.
                art = tinted("dock-oak", (113, 79, 45), 21)
            art = art.resize((PANEL_SIZE, PANEL_SIZE), Image.Resampling.LANCZOS)
            pad = np.pad(np.asarray(art), ((GUTTER, GUTTER), (GUTTER, GUTTER), (0, 0)), mode="symmetric")
        sheet.paste(Image.fromarray(pad), (i % COLUMNS * PITCH, i // COLUMNS * PITCH))
    # The long strip shares the cask lid's material, including on small buckets.
    staves = np.asarray(tinted("oak-staves", (125, 89, 52), 25, (120,56)))
    sheet.paste(Image.fromarray(np.pad(staves, ((4,4),(4,4),(0,0)), mode="edge")), (128,64))
    sheet.save(destination / "Joinery.png", optimize=True)


# The left half retains every original skin, hair, eye and tool island. The right
# half is a continuous garment unwrap; one chest motif spans multiple polygons.
GARB = {"OrlaAtelier": "flight-coat", "MossAtelier": "lichen-coat",
        "FenAtelier": "storm-coat", "OssaAtelier": "kiln-apron"}


def costume(atlas, colours, destination):
    side = colours.width
    sheet = Image.new("RGB", (2 * side, side))
    clothes = {"OrlaAtelier": {0:"blue-canvas",1:"wool",4:"leather",5:"leather",6:"leather",9:"linen",14:"wool"},
               "MossAtelier": {0:"linen",1:"wool",2:"leather",4:"linen",5:"leather",9:"linen",13:"wool"},
               "FenAtelier": {0:"blue-canvas",1:"linen",4:"leather",5:"leather",8:"linen",13:"wool"},
               "OssaAtelier": {0:"leather",1:"leather",2:"wool",4:"leather",5:"wool",8:"linen"}}
    cell = side // 4
    for index, study in clothes[atlas].items():
        x, y = index % 4 * cell, (3-index//4) * cell
        colour = np.median(np.asarray(colours.crop((x,y,x+cell,y+cell))), axis=(0,1))
        colours.paste(tinted(study, colour, 9, (cell,cell)), (x,y))
    sheet.paste(colours, (0,0))
    with Image.open(SOURCES / (GARB[atlas] + ".png")) as art:
        # Keep the pigment resolution of the source. The outside four texels guard the seam.
        sized = art.resize((side-8, side-8), Image.Resampling.LANCZOS)
        pixels = np.asarray(sized, dtype=float)
        target = np.median(np.asarray(colours.crop((cell, 3*cell, 2*cell, 4*cell))), axis=(0,1))
        pixels += .90 * (target - np.median(pixels, axis=(0,1)))
        sized = Image.fromarray(np.uint8(np.clip(pixels, 0, 255)))
        gutter = np.pad(np.asarray(sized), ((4,4), (4,4), (0,0)), mode="edge")
    sheet.paste(Image.fromarray(gutter), (side,0))
    sheet.save(destination / (atlas + ".png"), optimize=True)


if __name__ == "__main__":
    for material in SURFACES:
        save_tile(material)
    joinery()
