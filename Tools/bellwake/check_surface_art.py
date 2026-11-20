"""Verify source paintings, atlas margins and image references in both room packaging formats."""
import argparse
from collections import defaultdict
import gzip
import json
from pathlib import Path
import struct
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image

from cottage_edges import paint as paint_house_edges
from ground_brush import paint as paint_brush
from keeper_paint import paint as paint_keeper
from resident_paint import paint as paint_people
from rime_firs import paint as paint_firs
from surface_paint import GARB, SURFACES, TEXTURES, joinery, save_tile

def check_paintings():
    with TemporaryDirectory() as directory:
        generated = Path(directory)
        for material in SURFACES:
            save_tile(material, generated)
        joinery(generated)
        paint_house_edges(generated / "HouseEdges.png")
        paint_brush(generated / "GroundBrush.png")
        paint_keeper(generated / "QuietEnamel.png")
        paint_firs(generated / "RimeFir.png")
        paint_people(generated / "ResidentCloth.png")
        for file in generated.glob("*.png"):
            with Image.open(file) as expected, Image.open(TEXTURES / file.name) as published:
                assert np.array_equal(np.asarray(expected), np.asarray(published)), file.name

    with Image.open(TEXTURES / "BanksidePlants.png") as plants:
        assert plants.mode == "RGBA" and plants.size == (128,128)
        alpha = np.asarray(plants)[:,:,3]
        for y in (0,64):
            for x in (0,64):
                tile = alpha[y:y+64,x:x+64]
                assert .12 < np.mean(tile >= 115) < .55, (x,y)
                assert max(tile[0].max(),tile[-1].max(),tile[:,0].max(),tile[:,-1].max()) < 115

    # Mipmaps must see a copy of the nearest stave at a strip's edge.
    with Image.open(TEXTURES / "Joinery.png") as image:
        pixels = np.asarray(image)
        for x in (128,129,130,131):
            assert np.array_equal(pixels[68:124,x],pixels[68:124,132])
        for x in (252,253,254,255):
            assert np.array_equal(pixels[68:124,x],pixels[68:124,251])

    # Far mips should approach a neutral multiplier. Opposite edges meet at most
    # as sharply as ordinary neighboring marks anywhere inside each painted tile.
    with Image.open(TEXTURES / "GroundBrush.png") as texture:
        ink = np.asarray(texture, dtype=float)
        assert ink.shape == (64,64,4)
        assert np.max(np.abs(ink.mean(axis=(0,1)) - 127.5)) < 2
        seam = np.abs(ink[:,0] - ink[:,-1]).mean(0) + np.abs(ink[0] - ink[-1]).mean(0)
        interior = np.abs(np.diff(ink,axis=0)).mean((0,1)) + np.abs(np.diff(ink,axis=1)).mean((0,1))
        assert np.all(seam <= interior)

    with Image.open(TEXTURES / "ResidentCloth.png") as texture:
        ink = np.asarray(texture, dtype=float)
        for face in range(37):
            frames = []
            for state in range(2):
                row, col = divmod(face*2+state, 19)
                x = (col * 23 if col < 11 else 320 + (col - 11) * 23) + 1
                y = row*16+449
                frames.append(ink[y:y+13,x:x+21])
            assert np.abs(frames[0] - frames[1]).mean() > 8, face

def check_rooms(directory):
    page = (directory / "index.html").read_text()
    manifest = json.JSONDecoder().raw_decode(page.split("window.BELLWAKE=",1)[1])[0]
    assert (directory / manifest["groundBrush"]).read_bytes() == (TEXTURES / "GroundBrush.png").read_bytes()
    usage = defaultdict(set)
    for room, file in manifest["models"].items():
        model = gzip.decompress((directory / file).read_bytes())
        json_size = struct.unpack_from("<I", model, 12)[0]
        scene = json.loads(model[20:20+json_size])
        buffers = memoryview(model)[28+json_size:]
        for image in scene.get("images",[]):
            name = image["name"]
            canonical = TEXTURES / (name + ".png")
            assert canonical.is_file(), (room,name)
            if "uri" in image:
                assert image["uri"] == "paint/" + name + ".png", (room, name)
                payload = (directory / manifest["paints"][name]).read_bytes()
            else:
                view = scene["bufferViews"][image["bufferView"]]
                start = view.get("byteOffset",0)
                payload = buffers[start:start+view["byteLength"]]
            assert payload == canonical.read_bytes(), (room,name)
            usage[name].add(room)
    assert usage["BanksidePlants"] == {"Bellmarket","Reedwater","RootChoir","RowanHollow"}
    assert {"Bellmarket","ChainDock","Wrenfall","PaperCourt"} <= usage["Joinery"]
    assert usage["RowanGrove"] == {"RowanHollow"}
    district_models = set(manifest["collision"])
    assert usage["CountryBeyond"] == district_models and usage["YardGoods"] == district_models
    assert usage["KilnFire"] == {"CinderLens", "CastingBed", "SaffronKilns", "SupperSteps"}
    assert usage["RimeFir"] == {"RimePost"}
    assert usage["ShopWindows"] == {"Bellmarket", "Wrenfall", "SillwaterEbb", "SillwaterFlood"}
    assert {"GlassRookery", "GloamingPress", "SillwaterOffice", "FloodLedger"} <= usage["CabinetBindings"]
    assert {"Bellmarket", "MouldLoft", "RowanHollow", "Wrenfall"} <= usage["ResidentCloth"]
    for coat in GARB:
        assert usage[coat], coat
    return len(manifest["models"]), len(usage)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory",type=Path,nargs="?",default=TEXTURES.parents[3]/"Play")
    check_paintings()
    count, paintings = check_rooms(parser.parse_args().directory)
    print(f"Verified the tile paintings, plant and prop margins, and {paintings} images across {count} playable models.")
