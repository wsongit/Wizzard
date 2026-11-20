"""Pack the four static ticket boards into one draw without resampling their lettering."""
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
from atelier import RES, batches, mats

WIDTH, HEIGHT = 576, 512
# x and y start at the top left of each original sheet. All sides have at least 8 spare texels.
BOARDS = {"PaperTicket": (8,8,256,320), "ParishPacket": (8,344,256,160),
          "RowanWaypost": (280,8,288,128), "DriftTicket": (280,152,288,160)}


def paint():
    sheet=np.zeros((HEIGHT,WIDTH,3),dtype=np.uint8)
    empty=np.ones((HEIGHT,WIDTH),dtype=bool)
    for name,(x,y,w,h) in BOARDS.items():
        with Image.open(RES/"Textures"/(name+".png")) as board:
            if board.size!=(w,h):
                raise ValueError("Ticket dimensions changed: "+name)
            padded=np.pad(np.asarray(board.convert("RGB")), ((8,8),(8,8),(0,0)), mode="symmetric")
            sheet[y-8:y+h+8,x-8:x+w+8]=padded
        empty[y-8:y+h+8,x-8:x+w+8]=False
    # Mirroring keeps the outside texel equal to the first inside texel at four mip levels.
    # Fill the remaining space with the nearest gutter before generating the smaller mipmaps.
    row,column=distance_transform_edt(empty, return_distances=False, return_indices=True)
    Image.fromarray(sheet[row,column]).save(RES/"Textures/MarketNotices.png")


def bind():
    found=set()
    for obj in batches["Set"]:
        for i,material in enumerate(obj.data.materials):
            if material.name not in BOARDS:
                continue
            name=material.name
            x,y,w,h=BOARDS[name]
            uv=obj.data.uv_layers.active.data
            for face in obj.data.polygons:
                if face.material_index!=i:
                    continue
                for corner in face.loop_indices:
                    u,v=uv[corner].uv
                    if not (-.001<=u<=1.001 and -.001<=v<=1.001):
                        raise ValueError("A repeating UV cannot use the ticket sheet: "+name)
                    uv[corner].uv=((x+u*w)/WIDTH, (HEIGHT-y-h+v*h)/HEIGHT)
            obj.data.materials[i]=mats["MarketNotices"]
            found.add(name)
    if found!=set(BOARDS):
        raise ValueError("Missing ticket panels: "+str(set(BOARDS)-found))
