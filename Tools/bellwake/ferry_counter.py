"""The Sillwater packet counter and its enamel destination board."""

from PIL import Image, ImageDraw, ImageFont
from atelier import RES, block, lathe, marker, shaft
from engine_art import panel


def destination_board():
    im = Image.new("RGB", (256, 160), "#293e40")
    d = ImageDraw.Draw(im)
    letters = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

    def font(n):
        return ImageFont.truetype(letters, n)

    d.rounded_rectangle((3, 3, 252, 156), 8, outline="#d6bb77", width=4)
    d.polygon(
        [(51, 112), (75, 127), (168, 127), (193, 110), (159, 114), (94, 114)],
        fill="#c8884e",
    )
    d.line((121, 111, 121, 71), fill="#f0dfad", width=5)
    d.polygon([(125, 74), (126, 106), (172, 106)], fill="#e1c598")
    d.line(
        [(22, 134), (65, 131), (102, 137), (147, 131), (183, 134), (236, 130)],
        fill="#849f96",
        width=3,
    )
    d.text((128, 22), "SILLWATER", font=font(28), anchor="mt", fill="#f4dfaa")
    d.text(
        (128, 56),
        "R E T U R N    T I C K E T S",
        font=font(12),
        anchor="mt",
        fill="#e4cca1",
    )
    im.save(RES / "Textures/ParishPacket.png")


def counter(x, y, z):
    oak = "TarredOak"
    block("Purfled packet desk", (x, y, z + 0.61), (2.62, 0.96, 1.28), oak)
    block("Desk writing top", (x, y, z + 1.28), (2.74, 1.05, 0.11), "Wood")
    block("Counter front panel", (x, y - 0.49, z + 0.63), (2.19, 0.05, 0.86), "SeaCloth")
    for dx in (-1.22, 1.22):
        block("Timber upright", (x + dx, y + 0.30, z + 1.43), (0.17, 0.20, 2.93), "Wood")
    block("Enamel backing", (x, y + 0.31, z + 2.47), (2.50, 0.22, 1.59), oak)
    panel("Packet service board", x, y + 0.181, z + 1.74, 2.34, 1.46, "ParishPacket")
    block("Rain drip", (x, y + 0.29, z + 3.31), (2.70, 0.66, 0.12), "VerdigrisSheet")
    block(
        "Ticket block",
        (x - 0.49, y - 0.17, z + 1.40),
        (0.58, 0.33, 0.12),
        "HousePlaster",
    )
    for i in range(4):
        block(
            "Fare counterfoil",
            (x - 0.68 + i * 0.12, y - 0.17, z + 1.464),
            (0.033, 0.27, 0.016),
            "Pennon",
        )
    lathe(
        "Clerk’s handbell",
        x + 0.41,
        y - 0.12,
        z + 1.34,
        [
            (0.16, 0),
            (0.14, 0.05),
            (0.10, 0.15),
            (0.043, 0.18),
            (0.04, 0.29),
            (0.06, 0.33),
        ],
        "Brass",
        12,
    )
    for dx in (-1.14, 1.14):
        shaft(
            "Brass desk rail",
            (x + dx, y - 0.55, z + 1.13),
            (x + dx, y - 0.61, z + 1.25),
            0.05,
            0.05,
            "Brass",
            7,
        )
    shaft(
        "Handrail",
        (x - 1.15, y - 0.62, z + 1.25),
        (x + 1.15, y - 0.62, z + 1.25),
        0.05,
        0.05,
        "Brass",
        9,
    )
    marker("A_Packet", x, y - 0.72, z + 1.41)


def fen_ticket_paint():
    im = Image.new("RGB", (288, 160), "#4c3835")
    d = ImageDraw.Draw(im)
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    d.rounded_rectangle((4, 4, 283, 155), 8, outline="#e2c98d", width=3)
    d.rounded_rectangle((10, 10, 277, 149), 5, outline="#9f8462", width=2)
    d.text((144, 20), "DRIFT FEN", anchor="mt", font=ImageFont.truetype(path, 28), fill="#f8e7bd")
    for j in range(3):
        xx = 76 + j * 68
        d.line((xx, 110, xx, 68), fill="#bea783", width=3)
        d.rounded_rectangle((xx - 4, 56, xx + 4, 80), 4, fill="#e0c480")
    d.arc((53, 79, 236, 135), 5, 175, fill="#91ad9c", width=4)
    d.text(
        (144, 133),
        "FERRY   •   RETURN FARE",
        anchor="mm",
        font=ImageFont.truetype(path, 14),
        fill="#f2d79c",
    )
    im.save(RES / "Textures/DriftTicket.png")


def fen_ticket(x, y, z):
    oak = "TarredOak"
    block("Fen ticket pedestal", (x, y, z + 0.64), (1.62, 0.75, 1.30), oak)
    block("Faded copper counter", (x, y, z + 1.33), (1.80, 0.91, 0.12), "VerdigrisSheet")
    for dx in (-0.81, 0.81):
        shaft(
            "Fen board standard",
            (x + dx, y + 0.22, z + 1.33),
            (x + dx, y + 0.22, z + 2.85),
            0.076,
            0.061,
            "Wood",
            8,
        )
    block("Pilot's destination board", (x, y + 0.22, z + 2.18), (1.85, 0.15, 1.08), oak)
    panel("Red fen fare", x, y + 0.13, z + 1.68, 1.75, 0.98, "DriftTicket")
    lathe(
        "Ticket punch stand",
        x + 0.28,
        y - 0.11,
        z + 1.40,
        [(0.14, 0), (0.11, 0.04), (0.052, 0.14), (0.06, 0.33)],
        "Brass",
        10,
    )
    shaft(
        "Punch lever",
        (x + 0.27, y - 0.11, z + 1.70),
        (x - 0.17, y - 0.19, z + 1.80),
        0.045,
        0.06,
        oak,
        8,
    )
    for j in range(3):
        block(
            "Red return chits",
            (x - 0.41 + j * 0.06, y - 0.13, z + 1.404 + j * 0.018),
            (0.35, 0.24, 0.022),
            "Pennon",
        )
    marker("A_FenPass", x, y - 0.49, z + 1.50)


def wood_sign_paint():
    im=Image.new("RGB",(288,128),"#4e5836")
    d=ImageDraw.Draw(im)
    font="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    d.rounded_rectangle((3,3,284,124),8,outline="#b3ad78",width=3)
    d.text((144,19),"ROWAN HOLLOW",font=ImageFont.truetype(font,27),anchor="mt",fill="#fff1c6")
    d.line((29,70,258,70),fill="#8f9061",width=2)
    d.text((144,88),"SCHOOL PATH  ·  RETURN WALK",font=ImageFont.truetype(font,13),anchor="mt",fill="#fff0c4")
    im.save(RES/"Textures/RowanWaypost.png")


def wood_sign(x,y,z):
    lathe("Sawyer’s forked waypost",x,y,z-.15,[(.29,0),(.34,.21),(.19,.45),(.15,2.34),(.10,2.55)],"Wood",8)
    block("Carved destination board",(x,y-.085,z+1.60),(1.93,.16,.89),"Wood")
    panel("Rowan school path",x,y-.170,z+1.19,1.80,.80,"RowanWaypost")
    for side in (-1,1):
        shaft("Rail cleat",(x,y+.02,z+1.04),(x+side*.73,y+.03,z+1.40),.065,.06,"Wood",7)
    # A little carved wren with a copper repair across the tail.
    zz=z+2.23
    lathe("Waypost wren",x,y,zz,[(.075,0),(.17,.10),(.20,.21),(.13,.31),(.08,.33)],"Brass",9)
    lathe("Wren crown",x-.13,y,zz+.20,[(.09,0),(.135,.08),(.12,.19),(.065,.22)],"Brass",9)
    shaft("Bird bill",(x-.20,y,zz+.31),(x-.41,y-.01,zz+.29),.064,.009,"Wood",6)
    shaft("Cleaved tail",(x+.10,y,zz+.16),(x+.37,y+.012,zz+.40),.108,.05,"Brass",7)
    shaft("Mended tail tip",(x+.34,y+.01,zz+.38),(x+.46,y+.014,zz+.48),.058,.035,"Amber",7)
    for side in (-1,1):
        shaft("Carved wren wing",(x-.026,y+side*.145,zz+.18),(x+.24,y+side*.11,zz+.26),.071,.03,"Wood",7)
    marker("A_WoodWalk",x,y-.40,z+1.55)
