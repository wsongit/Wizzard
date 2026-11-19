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
    block(
        "Counter front panel", (x, y - 0.49, z + 0.63), (2.19, 0.05, 0.86), "SeaCloth"
    )
    for dx in (-1.22, 1.22):
        block(
            "Timber upright", (x + dx, y + 0.30, z + 1.43), (0.17, 0.20, 2.93), "Wood"
        )
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
