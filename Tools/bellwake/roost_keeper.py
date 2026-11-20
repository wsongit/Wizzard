"""Orla's flight coat, messenger tubes and keeper's glove for Glass Rookery."""
import math
import random
from PIL import Image
from atelier import RES, block, shaft
from moss_art import Figure


def paint():
    # One 64-pixel atlas keeps her blue coat, waxed leather and red kerchief in one material.
    base = [(51, 76, 85), (71, 105, 116), (193, 158, 83), (179, 126, 94),
            (98, 66, 48), (71, 56, 49), (126, 88, 62), (151, 143, 123),
            (214, 206, 176), (137, 64, 58), (183, 142, 80), (73, 57, 54),
            (218, 184, 147), (104, 102, 99), (56, 68, 71), (117, 137, 135)]
    rng = random.Random(9648)
    image = Image.new("RGB", (64, 64))
    for i, colour in enumerate(base):
        for v in range(16):
            for u in range(16):
                grain = rng.uniform(-.045, .045)
                if i in (0, 1, 9, 15):
                    grain += .032 * math.cos(math.pi * (u + v) / 2)
                elif i in (4, 5, 6):
                    grain += .07 * math.sin(u * .8 + math.sin(v * .61))
                elif i in (7, 13):
                    grain += .08 * math.sin(u * 1.5 + v * .26)
                shade = 1 + grain + .06 * math.cos(v * math.pi / 15)
                image.putpixel(((i % 4) * 16 + u, 48 - (i // 4) * 16 + v),
                               tuple(round(min(255, c * shade)) for c in colour))
    from surface_paint import costume
    costume("OrlaAtelier", image, RES / "Textures")


def keeper(x, y, z):
    f = Figure(x, y, z, "OrlaAtelier")
    for sign in (-1, 1):
        bx = sign * .121
        by = sign * .043
        f.rings("Split-soled roost boot", [(bx, by-.045, .007, .092, .15),
                (bx, by-.046, .065, .101, .16), (bx, by, .16, .077, .09),
                (bx, by, .36, .081, .084)], 5, 8)
        f.rings("Boot binding", [(bx, by, .29, .084, .092),
                (bx, by, .33, .086, .093)], 10, 8)
        f.tube("Wool breeches", (bx, by, .29), (sign*.104, .014, .82), .069, .116, 14)
    f.rings("Weathered flight coat", [(0,.015,.47,.25,.161),(0,.016,.55,.259,.175),
            (0,0,.84,.202,.148),(0,0,1.03,.177,.143),(-.011,.018,1.20,.221,.157),
            (-.009,.022,1.32,.239,.13),(0,.013,1.37,.119,.098)], 1)
    f.rings("Ochre woven coat hem", [(0,.015,.488,.254,.165),
            (0,.016,.516,.258,.172)], 2)
    f.rings("Tied leather waist", [(0,0,.908,.199,.16),(0,0,.951,.194,.157)], 4)
    for h in (1.01, 1.09, 1.17):
        f.oval("Horn flight-coat button", (.022,-.153,h), (.018,.012,.018), 10, 6)
    f.tube("Message sling", (-.139,-.077,1.324), (.142,-.132,.865), .027,.032,4,6)
    f.tube("Reed dispatch case", (.161,-.11,.702), (.145,-.107,.929), .056,.052,10,8)
    f.tube("Red sealing wax", (.145,-.107,.90), (.145,-.107,.942), .055,.054,9,8)
    f.tube("Near coat sleeve", (-.198,.008,1.276), (-.28,-.043,.997), .09,.071,0)
    f.tube("Resting cuff", (-.28,-.043,1.014), (-.255,-.143,.915), .074,.043,1)
    f.oval("Resting hand", (-.251,-.15,.883), (.049,.044,.078), 3, 8)

    f.joint("SpeakerArm", (.207,.01,1.26))
    f.tube("Handling sleeve", (.201,.012,1.268), (.294,-.035,1.007), .091,.069,0)
    f.tube("Gauntlet bell", (.291,-.044,1.01), (.303,-.199,1.106), .083,.052,4)
    f.oval("Falconer's palm", (.303,-.23,1.12), (.068,.078,.044), 6, 8)
    f.oval("Thumb of glove", (.259,-.213,1.144), (.025,.049,.031), 4, 6)
    for sign in (-1,1):
        f.tube("Glove stitch", (.303+sign*.036,-.094,1.072),
               (.303+sign*.034,-.18,1.119), .007,.007,2,5)
    f.joint("SpeakerHead", (0,.012,1.336))
    f.rings("Red throat kerchief", [(0,.008,1.278,.148,.111),(0,.008,1.326,.155,.122),
            (0,.014,1.377,.095,.086)], 9, 10)
    f.rings("Weathered face", [(0,-.004,1.338,.05,.067),(0,-.021,1.374,.083,.084),
            (0,-.02,1.46,.117,.103),(0,-.006,1.553,.124,.113),
            (0,.006,1.60,.108,.089)], 3)
    for sign in (-1, 1):
        f.oval("Keeper's ear", (sign*.112,.001,1.465), (.022,.031,.047), 3, 8)
        f.oval("Eye white", (sign*.052,-.114,1.488), (.029,.011,.012), 8, 8)
        f.oval("Iris", (sign*.049,-.123,1.489), (.011,.006,.012), 11, 6)
        f.tube("Wind-bent brow", (sign*.024,-.119,1.522),
               (sign*.080,-.102,1.523), .007,.011,7,6)
    f.oval("Nose", (0,-.125,1.46), (.023,.028,.041), 12, 8)
    f.tube("Quiet smile", (-.032,-.108,1.398), (.026,-.112,1.401), .006,.007,11,6)
    f.rings("Tucked silver hair", [(0,.03,1.51,.121,.112),
            (0,.025,1.589,.132,.125),(0,.047,1.628,.112,.106)], 7, 10)
    f.rings("Tied flight kerchief", [(0,.016,1.542,.13,.117),
            (0,.012,1.574,.138,.126),(0,.028,1.637,.121,.118),
            (-.017,.050,1.675,.067,.073)], 9, 12)
    f.oval("Kerchief knot", (-.1,.091,1.549), (.046,.048,.037), 9, 8)
    f.tube("Kerchief tail", (-.096,.094,1.54), (-.128,.113,1.411), .029,.014,9,6)

def dispatch_desk(x, y, z, wood, metal):
    # A fitted cabinet closes the space below the drawer and meets the sloping yard.
    block("Rookery cabinet plinth", (x,y,z+.043), (1.24,.74,.25), wood)
    block("Whistle bench carcass", (x,y,z+.48), (1.12,.62,.73), wood)
    for side in (-1,1):
        block("Framed cabinet door", (x+side*.26,y-.325,z+.417), (.49,.052,.45), "HousePlaster")
        block("Cabinet inset panel", (x+side*.26,y-.356,z+.412), (.391,.018,.35), wood)
        shaft("Latch pin", (x+side*.075,y-.372,z+.56), (x+side*.075,y-.41,z+.56), .024,.035,metal,7)
    block("Dispatch drawer", (x,y-.335,z+.722), (1.005,.065,.15), wood)
    shaft("Drawer pull", (x-.12,y-.385,z+.725), (x+.12,y-.385,z+.725), .021,.021,metal,7)
    block("Writing surface", (x,y,z+.856), (1.27,.76,.102), wood)
    # The ledge keeps rolled route slips in the wind without blocking the speaking approach.
    block("Paper ledge", (x,y+.325,z+.95), (1.24,.061,.14), wood)
    for i in range(3):
        xx=x+.28+i*.09
        shaft("Rolled route slip", (xx,y+.03,z+.95), (xx,y+.25,z+.94), .037,.038,"MillCanvas",7)
