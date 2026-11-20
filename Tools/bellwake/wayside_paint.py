"""Paint three original timber facades. Each 64 x 64 panel maps to one complete wall."""
from PIL import Image, ImageDraw
import random

def paint(destination):
    atlas = Image.new("RGB", (256, 64))
    for index, base in enumerate([(206,182,137), (182,154,109), (194,165,141)]):
        tile = Image.new("RGB",(64,64),base)
        d = ImageDraw.Draw(tile)
        rng = random.Random(751 + index)
        for _ in range(700):
            x,y=rng.randrange(64),rng.randrange(64)
            shade=rng.randint(-16,10)
            d.rectangle((x,y,x+rng.randrange(3),y+rng.randrange(3)),
                        fill=tuple(c+shade for c in base))
        for row in range(2):
            for col in range(-1,6):
                x,y=col*15+7*(row%2),52+row*6
                d.rectangle((x,y,x+14,y+5), fill=(69,62,54))
                d.rectangle((x+1,y+1,x+13,y+4),fill=rng.choice([(116,111,94),(127,118,99),(106,104,94)]))
        def timber(a,b,w):
            d.line((a,b),fill=(57,39,29),width=w)
            d.line((a,b),fill=(95,66,41),width=max(1,w-2))
        for x in (2,61): timber((x,0),(x,51),4)
        timber((0,4),(63,4),5)
        timber((0,49),(63,49),3)
        timber((3,21),(19,6),3)
        timber((60,21),(44,6),3)
        for x in ([9,42] if index==0 else [12] if index==1 else [35]):
            w=12 if index!=2 else 19
            d.rectangle((x-2,21,x+w+1,40),fill=(78,54,37))
            d.rectangle((x,23,x+w-1,37),fill=(49,48,42))
            for col in range(2):
                for row in range(2):
                    left=x+1+col*(w//2); top=24+row*7
                    d.rectangle((left,top,left+w//2-3,top+4),fill=rng.choice(
                        [(161,141,87),(182,155,91)] if index==1 else [(93,109,106),(112,121,109)]))
            d.line((x-3,40,x+w+2,40),fill=(147,116,79),width=2)
        if index == 2:
            # The fourth panel is the side and rear wall. The entrance faces the lane.
            atlas.paste(tile.copy(), (192,0))
        door = (25,39,10)[index]
        d.rectangle((door-2,18,door+13,57),fill=(62,44,31))
        d.rectangle((door,20,door+11,55),fill=(111,78,47))
        for dx in (2,5,8):
            d.line((door+dx,21,door+dx,54),fill=(80,56,37))
            d.line((door+dx+1,22,door+dx+1,53),fill=(137,94,54))
        d.line((door,39,door+10,39), fill=(69,52,39),width=2)
        d.rectangle((door+8,36,door+9,38),fill=(209,167,76))
        d.rectangle((door-2,56,door+14,58),fill=(143,131,109))
        atlas.paste(tile,(index*64,0))
    atlas.save(destination / "WayhouseFronts.png")
    from surface_paint import save_tile
    save_tile("MillCanvas", destination)

def paint_sorrel(destination):
    import math
    tile = Image.new("RGBA",(64,64))
    draw = ImageDraw.Draw(tile)
    rng = random.Random(1705)
    for angle in (-71,63,-48,42,-31,25,-12,9):
        a=math.radians(angle)
        length=rng.uniform(28,45)
        tip=(32+math.sin(a)*length,61-math.cos(a)*length)
        draw.line(((32,61),tip),fill=(94,103,43,255),width=2)
        for j in range(2,10):
            t=j/10
            x=32+t*(tip[0]-32)
            y=61+t*(tip[1]-61)
            for side in (-1,1):
                leaf=a+side*1.02
                size=(1-.68*t)*rng.uniform(9,15)
                dx,dy=math.sin(leaf)*size,-math.cos(leaf)*size
                nx,ny=-dy*.22,dx*.22
                end=(x+dx,y+dy)
                mid=(x+dx*.5,y+dy*.5)
                light=rng.choice([(118,143,63,255),(150,163,69,255),(105,128,57,255)])
                draw.polygon([(x,y),(mid[0]+nx,mid[1]+ny),end,(mid[0]-nx,mid[1]-ny)],fill=(57,81,39,255))
                draw.polygon([(x,y),(mid[0]+nx,mid[1]+ny),end],fill=light)
    tile.save(destination / "RoadSorrel.png")
