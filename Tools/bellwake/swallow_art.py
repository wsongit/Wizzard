"""Build Fen's double lock, the Swallow and four individually modelled loads in Blender."""

import math
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from atelier import RES, init, block, geometry, lathe, shaft, marker, collision, model, finish
from works_sets import line, ring
from works_finish import mount, plaques
from engine_art import panel
from sets import arch, pine
from sillwater_art import terrain
from swallow_lock import KEY, RUNS
from underworks import rooms

WATER = 1.00
CHANNEL = 5
OAK = "TarredOak"
GOLD = "Brass"
TEAL = "VerdigrisSheet"
TAU = math.tau


def bank(x, y):
    # The dredged bed rises into a broad towpath around all four sides of the lock.
    d = max(abs(y - CHANNEL), abs(x) - 13.55)
    inner = min(2.06, .08 + .43 * d)
    outer = np.clip((d - 4.7) / 4.8, 0, 1)
    shore = inner - .84 * outer * outer * (3 - 2 * outer)
    start = np.clip((abs(y + 14) + 0.25 * abs(x)) / 6, 0, 1)
    return float(shore * start)


def paint(r):
    n = 512
    yy, xx = np.mgrid[:n, :n]
    x = xx * 40 / n - 20
    y = 20 - yy * 40 / n

    def tex(name, scale):
        a = np.asarray(Image.open(RES / "Textures" / (name + ".png")).convert("RGB"), float)
        return a[(yy * scale // 4) % a.shape[0], (xx * scale // 4) % a.shape[1]]

    grass = tex("Grass", 6) * 0.68 + [29, 30, 14]
    stones = tex("Setts", 5) * 0.71 + [43, 36, 28]
    road = np.clip((7.8 - np.abs(y + 2.4)) * 0.75, 0, 1)
    road = np.maximum(road, np.clip((2.6 - np.abs(y - 12)) * 0.75, 0, 1))
    road = np.maximum(road, np.clip((2.0 - np.abs(np.abs(x) - 17)) * 0.75, 0, 1))
    ground = Image.fromarray(
        np.uint8(np.clip(grass * (1 - road[:, :, None]) + stones * road[:, :, None], 0, 255))
    )
    ground.save(RES / "Textures" / (KEY + "Ground.png"))
    normal = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

    def font(n, b=False):
        return ImageFont.truetype(bold if b else normal, n)

    im = Image.new("RGB", (768, 512), "#e6d5ad")
    d = ImageDraw.Draw(im)
    for i, (w, e, stop, mark, cargo, owner, _) in enumerate(RUNS):
        x0, y0 = (i % 2) * 384, (i // 2) * 256
        d.rounded_rectangle(
            (x0 + 3, y0 + 3, x0 + 380, y0 + 252), 8, fill="#e5d3a8", outline="#836b48", width=4
        )
        d.text((x0 + 17, y0 + 15), "THE SWALLOW   /   NIGHT BOOK", font=font(14), fill="#3f655f")
        d.text(
            (x0 + 17, y0 + 43),
            f"Passage {i + 1} · " + ("Westbound" if i % 2 else "Eastbound"),
            font=font(23, True),
            fill="#433228",
        )
        d.text((x0 + 17, y0 + 82), cargo[0].upper() + cargo[1:], font=font(19), fill="#553b30")
        d.line((x0 + 17, y0 + 119, x0 + 366, y0 + 119), fill="#a99976", width=2)
        d.text(
            (x0 + 17, y0 + 134),
            f"West tide   {w}       East tide   {e}",
            font=font(20, True),
            fill="#325a58",
        )
        d.text(
            (x0 + 17, y0 + 176),
            ("Fore crane" if stop == 1 else "Aft crane") + f"  ·  load at mark {mark}",
            font=font(19),
            fill="#4c4431",
        )
        d.text((x0 + 17, y0 + 219), "Signed for " + owner, font=font(15), fill="#7c573d")
    im.save(RES / "Textures/SwallowOrders.png")
    im = Image.new("RGB", (96, 192), "#e6d8b5")
    d = ImageDraw.Draw(im)
    for i in range(5):
        sy = 160 - 32 * i
        d.line((5, sy, 39, sy), width=4, fill="#75483a")
        d.text((62, sy), str(i), font=font(23, True), anchor="mm", fill="#374e4e")
    im.save(RES / "Textures/SwallowGauge.png")
    im = Image.new("RGB", (448, 272), "#e9dcb9")
    d = ImageDraw.Draw(im)
    d.rectangle((7, 7, 441, 265), outline="#7e704d", width=3)
    d.text((22, 16), "WORKING THE STAIR", font=font(23, True), fill="#334f4b")
    for j, label in enumerate(("WEST", "FORE", "AFT", "EAST")):
        gx = 24 + j * 102
        top = (124, 124, 95, 95)[j]
        d.rectangle((gx, top, gx + 93, 151), fill="#4f8680")
        d.line((gx, 78, gx, 152, gx + 94, 152), fill="#655744", width=4)
        d.text((gx + 46, 63), label, font=font(15, True), anchor="mm", fill="#574936")
    d.text((23, 163), "Match both waterlines to open a gate.", font=font(20, True), fill="#334f4b")
    d.text((23, 199), "Head fills FORE. Chain moves FORE to AFT.", font=font(17), fill="#453b2f")
    d.text((23, 227), "Tail drains AFT. Tow a single reach per turn.", font=font(17), fill="#453b2f")
    im.save(RES / "Textures/SwallowPlan.png")
    plaques(1, r)


def vessel():
    x = -12
    y = CHANNEL
    z = WATER - 0.14

    def at(dx, dy, dz):
        return (x + dx, y + dy, z + dz)

    stations = [
        (-2.35, 0.07, 0.64),
        (-1.88, 0.66, 0.49),
        (-1.02, 0.87, 0.46),
        (0.68, 0.89, 0.47),
        (1.62, 0.72, 0.51),
        (2.28, 0.22, 0.67),
        (2.46, 0.045, 0.84),
    ]
    rows = []
    for dx, w, h in stations:
        for side, lift in ((-1, h), (-0.77, 0.12), (-0.38, 0), (0.38, 0), (0.77, 0.12), (1, h)):
            rows.append(at(dx, w * side, lift))
    faces = [
        (6 * j + i, 6 * j + i + 6, 6 * j + i + 7, 6 * j + i + 1) for j in range(6) for i in range(5)
    ]
    geometry(
        "Clinker hull", rows, faces + [tuple(range(6)), tuple(range(41, 35, -1))], "Wood", "Swallow"
    )
    for j in range(6):
        ax, aw, ah = stations[j]
        bx, bw, bh = stations[j + 1]
        geometry(
            "Oiled deck",
            [at(ax, -aw, ah), at(bx, -bw, bh), at(bx, bw, bh), at(ax, aw, ah)],
            [(0, 1, 2, 3)],
            OAK,
            "Swallow",
        )
        for sign in (-1, 1):
            line(
                "Ochre sheer stripe",
                at(ax, sign * aw, ah),
                at(bx, sign * bw, bh),
                0.055,
                "OchrePlaster",
                "Swallow",
            )
    block("Pilot cabin", at(-1.30, 0, 0.78), (0.95, 1.0, 0.65), "SeaCloth", "Swallow")
    block("Cabin window", at(-1.30, -0.51, 0.85), (0.64, 0.04, 0.32), "WindowLight", "Swallow")
    block("Cabin roof", at(-1.30, 0, 1.15), (1.21, 1.23, 0.12), "RoofSlate", "Swallow")
    lathe(
        "Steamer funnel",
        x - 1.43,
        y + 0.15,
        z + 1.20,
        [(0.13, 0), (0.13, 0.51), (0.17, 0.55)],
        "BellMetal",
        9,
        "Swallow",
    )
    for sign in (-1, 1):
        line(
            "Tow bitt", at(1.65, sign * 0.42, 0.50), at(1.65, sign * 0.42, 0.84), 0.075, GOLD, "Swallow"
        )
    marker("RailStart", x, y, z)
    marker("RailEnd", 12, y, z)
    # Distinct freight sits inside the same lashing points aboard the hull.
    base = z + 0.55
    xx = x + 0.40
    block("Baker’s flour chest", (xx, y, base + 0.34), (1.40, 0.92, 0.68), "Wood", "Cargo0")
    for dx in (-0.46, 0.46):
        block("Tin chest hoop", (xx + dx, y, base + 0.35), (0.10, 0.97, 0.73), "BellMetal", "Cargo0")
    group = "Cargo1"
    for h, w, d in ((0.1, 0.89, 0.70), (0.25, 1.07, 0.74), (0.40, 0.86, 0.63), (0.48, 0.70, 0.52)):
        block("Midwife's red bag", (xx, y, base + h), (w, d, 0.18), "Pennon", group)
    ring("Sewn bag handle", (xx, y, base + 0.57), 0.18, 0.047, OAK, "y", group)
    group = "Cargo2"
    block("Reed organ case", (xx, y, base + 0.40), (1.22, 0.84, 0.81), "Wood", group)
    for i in range(8):
        h = 0.33 + 0.075 * i
        lathe(
            "Organ pipe",
            xx - 0.49 + 0.14 * i,
            y + 0.19,
            base + 0.68,
            [(0.056, 0), (0.072, 0.1), (0.072, h)],
            "BellMetal",
            8,
            group,
        )
        block(
            "Ivory key",
            (xx - 0.48 + 0.14 * i, y - 0.37, base + 0.81),
            (0.115, 0.31, 0.06),
            "HousePlaster",
            group,
        )
    group = "Cargo3"
    block("Night-watch tin", (xx, y, base + 0.24), (0.94, 0.72, 0.45), TEAL, group)
    block("Tin lid", (xx, y, base + 0.49), (1.01, 0.79, 0.09), "BellMetal", group)
    block("Tied red docket", (xx, y - 0.21, base + 0.55), (0.50, 0.28, 0.04), "Pennon", group)


def paddle(x, y, z, style):
    block("Sluice pedestal", (x, y, z + 0.55), (1.46, 0.62, 1.12), "HarbourBrick")
    block("Capstone", (x, y, z + 1.12), (1.60, 0.72, 0.14), "Masonry")
    rad = 0.46 if style != "Chain" else 0.55
    c = (x, y, z + 1.57)
    ring("Handwheel tyre", c, rad, 0.073, TEAL, "y")
    for j in range(5):
        a = j * TAU / 5
        line("Cast spoke", c, (x + math.cos(a) * rad, y, z + 1.57 + math.sin(a) * rad), 0.049, GOLD)
    shaft("Wheel pin", (x, y - 0.15, z + 1.57), (x, y + 0.29, z + 1.57), 0.12, 0.09, OAK, 8)
    if style == "Chain":
        for i in range(7):
            ring(
                "Pump chain link",
                (x + 0.53, y + 0.25, z + 0.28 + i * 0.23),
                0.135,
                0.03,
                "BellMetal",
                "x" if i % 2 else "y",
                n=10,
            )
    elif style in ("West", "East"):
        shaft(
            "Tow drum",
            (x - 0.52, y + 0.56, z + 0.77),
            (x + 0.52, y + 0.56, z + 0.77),
            0.26,
            0.26,
            "Wood",
            10,
        )
        for i in range(7):
            ring(
                "Winch rope coil",
                (x - 0.36 + i * 0.12, y + 0.56, z + 0.77),
                0.263,
                0.033,
                "OchrePlaster",
                "x",
            )


def dock():
    for j, x in enumerate((-12, -4, 4, 12)):
        block(
            "Reach water",
            (x, CHANNEL, WATER - 0.14),
            (7.99, 4.66, 0.28),
            "ParishWater",
            "Reach" + str(j),
        )
        block("Revetment foundation", (x, CHANNEL, 0.14), (8.0, 4.75, 0.28), "Masonry")
        for sy in (-1, 1):
            yy = CHANNEL + sy * 2.53
            block("Chamber wall", (x, yy, 1.07), (8.01, 0.34, 2.20), "HarbourBrick")
            block("Chamfered quoin", (x, yy, 2.19), (8.03, 0.54, 0.13), "Masonry")
            for off in (-3.5, 0, 3.5):
                xx = x + off
                lathe("Cast rail post", xx, yy, 2.20, [(0.095, 0), (0.077, 0.55), (0.11, 0.60)], OAK, 8)
            line("Dock rail", (x - 4, yy, 2.72), (x + 4, yy, 2.72), 0.061, GOLD)
        panel("Five tide marks", x + 2.05, CHANNEL + 2.32, WATER - 0.31, 0.82, 1.86, "SwallowGauge")
    for side in (-1, 1):
        block("Towpath end cap", (side * 16.20, CHANNEL, 1.12), (0.46, 5.51, 2.34), "Masonry")
    # The closed tank is machinery. A solid core meets the parapets around its entire footprint.
    collision("Lock machinery foundation", 0, CHANNEL, -0.18, 32.35, 5.18, 2.49)
    for j, x in enumerate((-8, 0, 8)):
        for sy in (-1, 1):
            yy = CHANNEL + sy * 2.59
            block("Hoist pier", (x, yy, 2.50), (0.47, 0.64, 5.28), "HarbourBrick")
            block("Cut stone capital", (x, yy, 5.09), (0.68, 0.83, 0.25), "Masonry")
        block("Hoist crosshead", (x, CHANNEL, 5.18), (0.60, 6.06, 0.32), OAK)
        for dy in (-1.37, 1.37):
            ring("Chainwheel", (x, CHANNEL + dy, 5.08), 0.24, 0.065, GOLD, "x")
        group = "GateLeaf" + str(j)
        block("Mitred lock gate", (x, CHANNEL, 1.13), (0.25, 4.8, 2.18), "Wood", group)
        for off in (-0.78, 0.78):
            block(
                "Iron gate strap",
                (x - 0.14, CHANNEL, 1.13 + off),
                (0.09, 4.87, 0.19),
                "BellMetal",
                group,
            )
        for sign in (-1, 1):
            line(
                "Herringbone brace",
                (x - 0.16, CHANNEL, 1.96),
                (x - 0.16, CHANNEL + sign * 2.20, 0.36),
                0.11,
                OAK,
                group,
            )


def crane(x):
    y = 9.12
    z = bank(x, y)
    lathe("Cargo crane footing", x, y, z - 0.13, [(0.60, 0), (0.68, 0.29), (0.44, 0.67)], "Masonry", 10)
    shaft("Stepped crane mast", (x, y, z + 0.48), (x, y, 5.43), 0.28, 0.18, OAK, 8)
    line("Hoisting boom", (x, y, 5.02), (x, CHANNEL, 4.72), 0.19, "Wood")
    line("Galvanised stay", (x, y, 5.48), (x, CHANNEL, 4.74), 0.051, "BellMetal")
    ring("Cargo sheave", (x, CHANNEL, 4.64), 0.20, 0.066, GOLD, "x")
    line("Sling fall", (x, CHANNEL, 4.50), (x, CHANNEL, 3.53), 0.032, "Wood")
    ring("Lifting eye", (x, CHANNEL, 3.46), 0.11, 0.035, GOLD, "y")


def canopy(x, y, z):
    for a, b in ((-1.65, 0), (1.65, 0), (-1.65, 2.5), (1.65, 2.5)):
        block("Pilot shelter post", (x + a, y + b, z + 1.62), (0.19, 0.22, 3.44), OAK)
    for side in (-1, 1):
        pts = [
            (x + side * 2.02, y - 0.40, z + 3.29),
            (x + side * 2.02, y + 2.9, z + 3.29),
            (x, y + 2.9, z + 4.33),
            (x, y - 0.40, z + 4.33),
        ]
        geometry("Pilot shelter slate", pts, [(0, 1, 2, 3)], "RoofSlate")
    for yy in (y - 0.40, y + 2.9):
        geometry(
            "Pilot gable",
            [(x - 2.02, yy, z + 3.28), (x + 2.02, yy, z + 3.28), (x, yy, z + 4.32)],
            [(0, 1, 2)],
            "OchrePlaster",
        )
    block("Bench", (x, y + 1.98, z + 0.51), (3.17, 0.68, 0.24), "Wood")


def pump_house(x, y):
    z = bank(x, y)
    block("Tidal pump house", (x, y, z + 1.74), (5.45, 3.46, 3.78), "HarbourBrick")
    collision("Closed pumping house", x, y, z - 0.24, 5.45, 3.46, 3.8)
    front = y - 1.75
    for side in (-1, 1):
        row = [
            (x - 3.06, y + side * 2.07, z + 3.56),
            (x + 3.06, y + side * 2.07, z + 3.56),
            (x + 3.06, y, z + 5.00),
            (x - 3.06, y, z + 5.00),
        ]
        geometry("Slate roof", row, [(0, 1, 2, 3)], "RoofSlate")
        g = x + side * 2.72
        geometry(
            "Pump house gable",
            [(g, y - 1.73, z + 3.55), (g, y + 1.73, z + 3.55), (g, y, z + 4.98)],
            [(0, 1, 2)],
            "OchrePlaster",
        )
    for wx in (-1.72, 1.72):
        block("Lit boiler-room window", (x + wx, front, z + 2.10), (1.08, 0.09, 1.12), "WindowLight")
        for dx in (-0.56, 0, 0.56):
            block("Window iron", (x + wx + dx, front - 0.065, z + 2.10), (0.081, 0.08, 1.21), OAK)
        block("Window ledge", (x + wx, front - 0.14, z + 1.52), (1.32, 0.28, 0.12), "Masonry")
    block("Panelled door", (x, front, z + 1.16), (1.29, 0.13, 2.45), "Wood")
    for level in (0.59, 1.85):
        block("Door strap", (x - 0.32, front - 0.09, z + level), (0.63, 0.09, 0.07), "BellMetal")
    lathe(
        "Square brick chimney",
        x + 1.55,
        y + 0.33,
        z + 4.18,
        [(0.53, 0), (0.45, 1.86), (0.57, 1.90), (0.57, 2.08)],
        "HarbourBrick",
        4,
    )
    c = (x + 2.76, y, z + 1.40)
    ring("Pumping flywheel", c, 1.12, 0.12, TEAL, "x")
    for i in range(8):
        a = i * TAU / 8
        line(
            "Pump wheel spoke", c, (c[0], y + 1.11 * math.cos(a), c[2] + 1.11 * math.sin(a)), 0.072, GOLD
        )
    shaft("Pump bearing", (x + 2.53, y, c[2]), (x + 3.13, y, c[2]), 0.17, 0.17, OAK, 10)


def make(lib):
    r = next(r for r in rooms if r["key"] == KEY)
    paint(r)
    init(lib, 8712)
    terrain(KEY, 20, bank, 1)
    dock()
    vessel()
    pump_house(-14.3, 14.25)
    for i, (x, y, h) in enumerate(
        (
            (-16.9, -11, 6.7),
            (-12, -15.5, 5.4),
            (7, -16.9, 6.3),
            (17.4, 15.9, 7.1),
            (4.5, 17.6, 6.6),
            (-5, 17.8, 5.8),
        )
    ):
        pine(x, y, bank(x, y), h, 0.57 + i * 1.71)
    for x in (-4, 4):
        crane(x)
    for j, s in enumerate(r["stations"]):
        x, y = s["x"], s["y"]
        z = bank(x, y)
        id = s["id"][2:]
        if id == "Fen":
            canopy(x, y + 0.18, z)
            model("WZ_SWA_N01", "Fen in the lock coat", x, y, z, 1.75, 12, "Speaker")
        elif id in ("Gate","FenRoad"):
            arch(x, y, z, 2.75, 3.3, "HarbourBrick", OAK)
        elif id == "Sheet":
            for dx in (-1.40, 1.40):
                block("Oak standard", (x + dx, y, z + 1.12), (0.18, 0.25, 2.64), OAK)
            block("Sailing board back", (x, y, z + 1.65), (3.07, 0.31, 2.13), OAK)
            xx = x + 3.05
            for dx in (-1.26, 1.26):
                block("Notice standard", (xx + dx, y, z + 1.10), (0.16, 0.23, 2.64), OAK)
            block("Pilot diagram back", (xx, y, z + 1.71), (2.91, 0.26, 1.86), OAK)
            panel("Pilot diagram", xx, y - 0.15, z + 0.86, 2.78, 1.70, "SwallowPlan")
            for i in range(4):
                panel(
                    "Sailing chit",
                    x,
                    y - 0.18,
                    z + 0.67,
                    2.92,
                    1.95,
                    "SwallowOrders",
                    "Order" + str(i),
                    i,
                )
        elif s["style"] == "wheel":
            paddle(x, y, z, id)
        else:
            block("Docket desk", (x, y, z + 0.52), (1.62, 0.66, 1.09), OAK)
            block("Worn writing top", (x, y, z + 1.09), (1.77, 0.77, 0.11), "Wood")
            if id == "Hook":
                shaft("Sling lever", (x, y, z + 1.11), (x + 0.29, y, z + 1.79), 0.072, 0.062, GOLD, 9)
                ring("Sling lever eye", (x + 0.29, y, z + 1.84), 0.13, 0.056, TEAL, "y")
            else:
                block("Open slip book", (x, y, z + 1.19), (1.05, 0.55, 0.10), "HousePlaster")
                lathe(
                    "Registry stamp",
                    x + 0.4,
                    y,
                    z + 1.24,
                    [(0.14, 0), (0.15, 0.06), (0.06, 0.13), (0.098, 0.33)],
                    GOLD,
                    9,
                )
                if id == "Name":
                    panel(
                        "Ina's recovered watch slip",
                        x,
                        y - 0.36,
                        z + 1.25,
                        0.77,
                        0.48,
                        "PaperBills",
                        "Slip",
                    )
        if id not in ("Fen", "Gate", "FenRoad"):
            block("Sign backing", (x, y - 0.26, z + 0.72), (1.46, 0.14, 0.36), OAK)
            mount(s, 0, r, j, lambda _, xx, yy: bank(xx, yy))
        marker(s["id"], x, y - 0.52, z + 1.38)
        marker(s["camp"], x, y - 2.06, bank(x, y - 2.06) + 0.10)
    for j in range(32):
        a = j * TAU / 32
        rr = 34 + 2.5 * math.sin(5 * a)
        x = rr * math.cos(a)
        y = rr * math.sin(a)
        h = 7 + 2.4 * math.sin(3 * a) + 1.5 * math.cos(7 * a)
        lathe(
            "Flood valley ridgeline",
            x,
            y,
            -3,
            [(6, 0), (5.3, h * 0.69), (3.0, h * 0.94), (0.9, h + 1.2)],
            "MossRock",
            8,
            "Horizon",
        )
    marker("Spawn", 0, -14, 0.08)
    marker("Look", 0, 4, 2)
    finish(KEY, sky_key=r["theme"])
