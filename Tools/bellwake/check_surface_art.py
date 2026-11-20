"""Verify the image paintings, atlas margins and artwork embedded in the playable rooms."""
import argparse
from collections import defaultdict
import gzip
import json
from pathlib import Path
import struct
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image

from surface_paint import GARB, SURFACES, TEXTURES, joinery, save_tile

def check_paintings():
    with TemporaryDirectory() as directory:
        generated = Path(directory)
        for material in SURFACES:
            save_tile(material, generated)
        joinery(generated)
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

def check_rooms(directory):
    page = (directory / "index.html").read_text()
    manifest = json.JSONDecoder().raw_decode(page.split("window.BELLWAKE=",1)[1])[0]
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
            view = scene["bufferViews"][image["bufferView"]]
            start = view.get("byteOffset",0)
            assert buffers[start:start+view["byteLength"]] == canonical.read_bytes(), (room,name)
            usage[name].add(room)
    assert usage["BanksidePlants"] == {"Bellmarket","Reedwater","RootChoir","RowanHollow"}
    assert {"Bellmarket","ChainDock","Wrenfall","PaperCourt"} <= usage["Joinery"]
    assert usage["RowanGrove"] == {"RowanHollow"}
    for coat in GARB:
        assert usage[coat], coat
    return len(manifest["models"]), len(usage)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory",type=Path,nargs="?",default=TEXTURES.parents[3]/"Play")
    check_paintings()
    count, paintings = check_rooms(parser.parse_args().directory)
    print(f"Verified the tile paintings, plant and prop margins, and {paintings} images across {count} playable models.")
