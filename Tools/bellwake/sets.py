"""Stage dressing and interactive mechanisms for the five Bellwake sets."""

from atelier import *
from finish_art import cottage, district, bake_ground

ROOMS = ["Bellmarket", "RootChoir", "Reedwater", "CinderLens", "StillBelfry"]
CHARS = ["WZ_VIL_N01", "WZ_FOR_N01", "WZ_SWA_N01", "WZ_LAV_N01", "WZ_HAU_N03"]
CREATURE = ["WZ_VIL_N02", "WZ_FOR_N02", "WZ_SWA_N02", "WZ_LAV_N02", "WZ_HAU_N02"]
STATIONS = [
    [],
    [(-7, 2), (1, 8), (8, 0)],
    [(-7, 1), (0, 4), (7, 1)],
    [(-5, -1), (-5, 7), (6, 7)],
    [(-7, 2), (0, 8), (7, 2)],
]


def ground(k, x, y):
    # Piecewise-linear terraces on the same two-metre grid as the walkable mesh.
    rise = [1.0, 2.0, 0.4, 1.0, 1.5][k]
    return rise * min(1, max(0, (y - 8) / 6))


def floor(k):
    pts = []
    faces = []
    width = 21
    for j in range(21):
        for i in range(width):
            x = -20 + 2 * i
            y = -20 + 2 * j
            pts.append((x, y, ground(k, x, y)))
    for j in range(20):
        for i in range(20):
            a = j * width + i
            faces.append((a, a + 1, a + 1 + width, a + width))
    o = geometry("Court and sloping apse", pts, faces, ROOMS[k] + "Ground", "Terrain")
    layer = o.data.uv_layers.active
    for li, loop in enumerate(o.data.loops):
        p = o.data.vertices[loop.vertex_index].co
        layer.data[li].uv = ((p.x + 20) / 40, (p.y + 20) / 40)


def ridge(k):
    if k == 0:
        from market_art import market_ridge
        market_ridge(ground)
        return
    stone = ["Mountain", "MossRock", "Shale", "Basalt", "Slate"][k]
    rings = []
    n = 64
    for i in range(n):
        a = i * math.tau / n
        c, s = math.cos(a), math.sin(a)
        q = max(abs(c), abs(s))
        x, y = 20 * c / q, 20 * s / q
        cap = 6 + 2 * math.sin(3 * a + 0.7) + rng.uniform(0, 2) + (3 if k in (1, 4) else 0)
        rings.append(
            [
                (x, y, ground(k, x, y) - 0.2),
                (x * 1.09, y * 1.09, cap * 0.55),
                (x * 1.24, y * 1.24, cap),
                (x * 1.5, y * 1.5, cap * 0.7),
                (x * 2.3, y * 2.3, cap + 4 + 5 * math.sin(5 * a)),
            ]
        )
    pts = [p for row in rings for p in row]
    faces = []
    for i in range(n):
        for j in range(4):
            a = i * 5 + j
            b = ((i + 1) % n) * 5 + j
            faces.extend([(a, b + 1, b), (a, a + 1, b + 1)])
    geometry("Cut escarpment and distant ridgeline", pts, faces, stone, "Rim")
    for x, y, w, d in [(0, -20.4, 41, 0.8), (0, 20.4, 41, 0.8), (-20.4, 0, 0.8, 41), (20.4, 0, 0.8, 41)]:
        collision("Closed map limit", x, y, -2, w, d, 18)


def pine(x, y, z, h, variant):
    lean = 0.12 * h * math.sin(variant)
    shaft("Dark bark", (x, y, z - 0.18), (x + lean, y, z + h * 0.79), h * 0.067, h * 0.023, "Wood", 7)
    for j in range(3):
        a = variant + j * 2.4
        ratio = 0.34 if j == 0 else 0.22
        cx = x + lean + math.cos(a) * h * 0.13
        cy = y + math.sin(a) * h * 0.13
        shaft("Bough", (x, y, z + h * 0.36), (cx, cy, z + h * 0.65), h * 0.037, 0.07, "Wood", 6)
        lathe(
            "Faceted leafy whorl",
            cx,
            cy,
            z + h * (0.46 + 0.09 * j),
            [
                (h * ratio * 0.5, 0),
                (h * ratio, h * 0.12),
                (h * ratio * 0.75, h * 0.24),
                (h * ratio * 0.18, h * 0.36),
            ],
            "Leaves" if j != 1 else "Moss",
            7,
        )
    collision("Tree bole", x, y, z - 0.2, h * 0.10, h * 0.10, h * 0.58)


def arch(x, y, z, width, height, mat, cap, group="Set"):
    # Voussoirs use a continuous intrados, with interlocking keystone and imposts.
    radius = width / 2
    spring = height - radius
    t = 0.52
    d = 0.78
    for s in (-1, 1):
        block("Pilaster", (x + s * (radius + t / 2), y, z + spring / 2), (t, d, spring), mat, group)
        block(
            "Impost",
            (x + s * (radius + t / 2), y, z + spring - 0.12),
            (t + 0.22, d + 0.22, 0.28),
            cap,
            group,
        )
        block("Plinth", (x + s * (radius + t / 2), y, z + 0.22), (t + 0.26, d + 0.2, 0.44), cap, group)
        collision("Arch support", x + s * (radius + t / 2), y, z - 0.12, t + 0.2, d + 0.2, spring + 0.2)
    for i in range(11):
        a = math.pi * i / 11
        b = math.pi * (i + 1) / 11
        outer = radius + t + (0.20 if i == 5 else 0)
        quad = [(radius, a), (outer, a), (outer, b), (radius, b)]
        pts = [
            (x + r * math.cos(ang), y + dy, z + spring + r * math.sin(ang))
            for dy in [-d / 2, d / 2]
            for r, ang in quad
        ]
        geometry(
            "Crown stone" if i == 5 else "Arch stone",
            pts,
            [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)],
            cap if i == 5 else mat,
            group,
        )


def flags(x, y, z, h, cloth):
    shaft("Standard staff", (x, y, z), (x, y, z + h), 0.085, 0.065, "Wood")
    shaft("Cross spar", (x - 0.7, y, z + h - 0.15), (x + 0.7, y, z + h - 0.15), 0.075, 0.075, "Brass")
    pts = [
        (x - 0.55, y, z + h - 0.2),
        (x + 0.55, y, z + h - 0.2),
        (x + 0.49, y + 0.17, z + h - 1.75),
        (x, y + 0.23, z + h - 2.2),
        (x - 0.49, y + 0.17, z + h - 1.75),
    ]
    geometry("Swallowtail standard", pts, [(4, 3, 2, 1, 0)], cloth)
    lathe("Finial", x, y, z + h, [(0.06, 0), (0.14, 0.1), (0.02, 0.35)], "Brass", 6)


def prop(id, name, x, y, h, rot=0, foot=None, k=0):
    o = model(id, name, x, y, ground(k, x, y) - 0.012, h, rot)
    if foot:
        collision(name + " footing", x, y, ground(k, x, y) - 0.2, *foot)
    return o


def bell(x, y, z, scale, group):
    profile = [
        (0.48, 0),
        (0.52, 0.055),
        (0.51, 0.12),
        (0.39, 0.22),
        (0.31, 0.53),
        (0.27, 0.68),
        (0.15, 0.77),
        (0.08, 0.8),
    ]
    lathe(
        "Spun lip and shoulder",
        x,
        y,
        z,
        [(r * scale, h * scale) for r, h in profile],
        "BellMetal",
        16,
        group,
    )
    lathe(
        "Inscribed waist",
        x,
        y,
        z + 0.19 * scale,
        [(0.412 * scale, 0), (0.405 * scale, 0.04 * scale)],
        "Brass",
        16,
        group,
    )
    shaft(
        "Clapper",
        (x, y, z - 0.12 * scale),
        (x, y, z + 0.12 * scale),
        0.09 * scale,
        0.055 * scale,
        "Brass",
        8,
        group,
    )


def plinth(x, y, z, mat):
    lathe(
        "Carved octagonal footing",
        x,
        y,
        z - 0.08,
        [(0.91, 0), (0.91, 0.19), (0.69, 0.28), (0.60, 0.82), (0.76, 0.92), (0.76, 1.03)],
        mat,
        8,
    )
    collision("Solid control base", x, y, z - 0.1, 1.13, 1.13, 1.11)


def lamp(x, y, z, mat="Amber"):
    shaft("Lantern crook", (x, y, z), (x, y, z + 2.65), 0.10, 0.07, "Wood")
    shaft("Hanging arm", (x, y, z + 2.58), (x + 0.52, y, z + 2.58), 0.075, 0.075, "Wood")
    lathe(
        "Lantern and eaves",
        x + 0.48,
        y,
        z + 1.83,
        [(0.21, 0), (0.24, 0.1), (0.20, 0.17), (0.19, 0.49), (0.30, 0.51), (0.04, 0.72)],
        "BellMetal",
        6,
    )
    lathe("Painted light", x + 0.48, y, z + 2.0, [(0.21, 0), (0.21, 0.30)], mat, 6)


def seal(x, y, z, group, mat="Amber"):
    # An open ring around a suspended lozenge reads at a distance.
    for i in range(8):
        a = i * math.tau / 8
        b = (i + 1) * math.tau / 8
        shaft(
            "Halo link",
            (x + 0.43 * math.cos(a), y, z + 0.43 * math.sin(a)),
            (x + 0.43 * math.cos(b), y, z + 0.43 * math.sin(b)),
            0.055,
            0.055,
            "Brass",
            6,
            group,
        )
    lathe("Glass seed", x, y, z - 0.29, [(0.015, 0), (0.21, 0.28), (0.015, 0.56)], mat, 6, group)


def portal(k):
    x, y = 0, 15
    z = ground(k, x, y)
    arch(x, y, z, 4.2, 5.2, ["Masonry", "MossRock", "Shale", "Basalt", "Slate"][k], "Brass")
    marker("A_Gate", x, y - 0.9, z + 1.5)
    group = "GateLight"
    origins[group] = (x, y, z + 3.25)
    seal(x, y, z + 3.25, group, "SeaGlass")
    for s in [-1, 1]:
        flags(x + s * 3.65, y, z, 4.1, ["Pennon", "FernCloth", "SeaCloth", "CoalCloth", "NightCloth"][k])


def dress(k):
    if k == 0:
        from market_art import gate_stair, skyline_mill, spring_well, valley_orchard
        from market_yard import drying_yard
        gate_stair()
        skyline_mill()
        valley_orchard()
        drying_yard()
        for prefix, x, y, h, r in [
            ("Entrance west", -13, 4, 5.9, 25),
            ("Entrance east", 14, 12, 6.4, -27),
            ("Back terrace cottage", -12, 15, 5.6, -9),
            ("Lower east", 15, -9, 5.4, -49),
        ]:
            cottage(prefix, x, y, ground(k, x, y), h, r, lambda a,b: ground(k,a,b))
            collision("Cottage core", x, y, ground(k, x, y) - 0.2, 3.5, 3.5, h * 0.6)
        for id, name, x, y, h, r in [
            ("WZ_VIL_P02", "Striped market awning", -9, -5, 3.6, 25),
            ("WZ_VIL_P08", "Bake oven", 9, 4, 2.7, 0),
            ("WZ_VIL_P04", "Delivery cart", 8, -6, 1.65, -35),
            ("WZ_VIL_P05", "Flour casks", 10, 2, 1.1, 0),
        ]:
            prop(id, name, x, y, h, r, (1, 1, h * 0.75), k)
        spring_well(-4,7,ground(k,-4,7))
        for s in [-1, 1]:
            pine(s * 15, -2, 0, 7, 3 + s)
            lamp(s * 4, -7, 0)
            flags(s * 6, 8, 0, 4.1, "Pennon")
        arch(0, -17, 0, 5, 4.6, "Masonry", "Wood")
    if k == 1:
        for i, (x, y) in enumerate(
            [
                (-14, -12),
                (-14, -4),
                (-13, 6),
                (-16, 13),
                (15, -9),
                (14, 2),
                (13, 10),
                (8, 15),
                (-8, 14),
                (-18, 0),
                (18, 17),
            ]
        ):
            pine(x, y, ground(k, x, y), rng.uniform(7, 11), i)
        from choir_grove import braid, paint_bank
        braid()
        paint_bank()
        for id, name, x, y, h, r in [
            ("WZ_FOR_P06", "Hollow listening stump", -11, 7, 2.1, 25),
            ("WZ_FOR_P08", "Resin taps", 12, 6, 2.3, -35),
            ("WZ_FOR_P02", "Carved rest bench", -8, -6, 1.1, 20),
            ("WZ_FOR_P09", "Fern bed", 7, -7, 1.4, 20),
        ]:
            prop(id, name, x, y, h, r, (1, 1, h * 0.8), k)
        for x, y in [(-9, 4), (-8, -5), (8, 6), (7, 10), (12, -2), (-6, 13), (-15, -7), (5, -11)]:
            prop("WZ_FOR_P04", "Shelf fungi", x, y, rng.uniform(0.45, 0.90), rng.randrange(360), None, k)
        for x, y in [(-6, -8), (5, -4), (-4, 6), (5, 11)]:
            lamp(x, y, ground(k, x, y), "SeaGlass")
    if k == 2:
        for s in (-1, 1):
            for j in range(3):
                x, y = s * 14.9, -8 + j * 7
                prop("WZ_SWA_P05", "Woven reed screen", x, y, 2.4, 90, None, k)
            prop("WZ_SWA_P01", "Lock keeper hut", s * 14, 11, 4.8, -s * 30, (4, 3, 3), k)
            prop("WZ_SWA_P07", "Tangled cypress", s * 16, -11, 4.0, s * 17, (1.5, 1.5, 2.5), k)
        from lock_wheel import build as build_wheel
        build_wheel()
        for x, y in [(-10, -5), (8, -5), (9, 9), (-9, 8)]:
            prop("WZ_SWA_P06", "Boglight", x, y, 2.4, 0, None, k)
        for x in [-7, 0, 7]:
            for s in (-1, 1):
                block("Gauge channel lip", (x + s * 1.25, 8, 0.19), (0.36, 4.6, 0.52), "Shale")
            block("Slate flume", (x, 8, 0.25), (2.3, 4.4, 0.35), "Slate")
    if k == 3:
        for x in [-13, 13]:
            for y in [-9, 1, 10]:
                z = ground(k, x, y)
                block("Basalt buttress", (x, y, z + 3), (2.2, 2.4, 6.2), "Basalt")
                collision("Buttress solid", x, y, z - 0.1, 2.2, 2.4, 6.3)
                lathe(
                    "Riveted capital",
                    x,
                    y,
                    z + 5.8,
                    [(1.6, 0), (1.8, 0.35), (1.3, 0.68)],
                    "BellMetal",
                    8,
                )
            prop("WZ_LAV_P04", "Obsidian seam", x, 14, 5.5, 22, (2, 2, 3), k)
        for y in [-9, 1, 10]:
            shaft("Rafter L", (-13, y, 6), (0, y, 10), 0.29, 0.3, "Wood")
            shaft("Rafter R", (0, y, 10), (13, y, 6), 0.3, 0.29, "Wood")
            shaft("King post", (0, y, 7), (0, y, 10), 0.18, 0.18, "BellMetal")
            shaft("Tie beam", (-10, y, 7), (10, y, 7), 0.17, 0.17, "Wood")
        prop("WZ_FOU_P05", "Glass kiln", -12, -1, 4.4, 92, (2.4, 2.4, 3.6), k)
        prop("WZ_LAV_P06", "Leather bellows", 10, -9, 2.1, -25, (2, 1, 1.4), k)
        prop("WZ_LAV_P08", "Smithing anvil", 8, -6, 1.4, 25, (1, 0.8, 0.9), k)
        prop("WZ_LAV_P05", "Casting crucible", -10, 9, 2.5, -20, (1.5, 1.5, 1.7), k)
    if k == 4:
        for i in range(12):
            a = (i + 0.5) * math.tau / 12
            x, y = 15 * math.cos(a), 15 * math.sin(a) + 1
            z = ground(k, x, y)
            h = 7 + 0.7 * (i % 3)
            lathe(
                "Belfry pier",
                x,
                y,
                z - 0.18,
                [(1.2, 0), (1.15, 0.38), (0.84, 0.62), (0.70, h - 0.6), (1.05, h - 0.43), (1.14, h)],
                "Slate",
                8,
            )
            collision("Belfry pier core", x, y, z - 0.1, 1.35, 1.35, h)
            shaft("Radial bell frame", (x, y, z + h - 0.18), (0, 3, 10.8), 0.21, 0.20, "Wood")
            if i % 2 == 0:
                flags(x * 0.86, y * 0.86, z, 4.6, "NightCloth")
        bell(0, 3, 6.3, 4.5, "GreatBell")
        origins["GreatBell"] = (0, 3, 10.3)
        for x, y in [(-10, 7), (10, 7), (-11, -4), (10, -5)]:
            prop("WZ_HAU_P03", "Watch candles", x, y, 2.5, 20, None, k)
        prop("WZ_HAU_P06", "Old warning bell", -11, 10, 3.2, 18, (1.6, 1, 2.3), k)


def actors(k):
    x, y = (-2, -8) if k != 4 else (0, 4)
    h = [1.84, 1.66, 1.82, 1.94, 3.8][k]
    name = ["Tavi", "Moss", "Fen", "Ossa", "The Quiet"][k]
    if k == 0:
        from tavi_art import make_tavi
        make_tavi(x, y, 0, h)
    elif k == 1:
        from moss_art import keeper as moss
        moss(x,y,0)
    elif k in (2,3):
        from river_makers import maker
        maker(x,y,0,k==3)
    elif k == 4:
        from quiet_art import keeper, music_box
        keeper(x,y)
        music_box()
    else:
        model(CHARS[k], name, x, y, 0, h, 0, "Speaker")
    origins["Speaker"] = (x, y, 0)
    marker("A_Talk", x, y - 0.6, min(h * 0.79, 1.9))
    collision("Speaker footing", x, y, -0.1, 0.74, 0.7, min(h, 1.65))
    x, y = (9, -3) if k != 4 else (9, 5)
    model(CREATURE[k], "Local familiar", x, y, 0, [0.8, 1.1, 0.7, 1.05, 0.8][k], -25, "Familiar")
    origins["Familiar"] = (x, y, 0)
    x, y = [(-8, 9), (-8, 10), (-6, 12), (3, 11), (-9, 8)][k]
    plinth(x, y, ground(k, x, y), "Masonry")
    model("WZ_RUI_P06", "Witness ledger", x, y, ground(k, x, y) + 0.96, 0.80, 0)
    marker("A_Letter", x, y - 0.65, ground(k, x, y) + 1.35)


def machinery(k):
    for i, (x, y) in enumerate(STATIONS[k]):
        z = ground(k, x, y)
        group = "Rotor" + str(i)
        origins[group] = (x, y, z + 1.3)
        plinth(x, y, z, ["Masonry", "MossRock", "Shale", "Basalt", "Slate"][k])
        marker("A_Key" + str(i), x, y - 0.68, z + 1.44)
        if k == 4:
            groupLight = "Call" + str(i)
            origins[groupLight] = (x, y, z + 2.72)
            seal(x, y, z + 2.72, groupLight, "Amber")
        if k in (1, 4):
            palm_target("Key" + str(i), x, y - (0.46 if k == 1 else 0.10),
                        z + (1.60 if k == 1 else 1.72), 0.26)
            # Three silhouettes communicate each note even without color.
            iconX, iconY, iconZ = x, y - 0.43, z + (2.75 if k == 1 else 1.73)
            strokes = [
                [
                    (0, -0.32),
                    (-0.10, -0.11),
                    (-0.34, 0.04),
                    (-0.13, 0.04),
                    (-0.31, 0.30),
                    (0.04, 0.12),
                    (0.23, 0.19),
                    (0.36, 0.12),
                    (0.16, 0.06),
                    (0.09, -0.13),
                ],
                [
                    (0, 0.31),
                    (0.07, 0.06),
                    (0.27, 0.17),
                    (0.16, -0.04),
                    (0.36, -0.23),
                    (0.12, -0.13),
                    (0, -0.32),
                    (-0.08, -0.10),
                    (-0.31, -0.23),
                    (-0.17, 0.02),
                    (-0.25, 0.21),
                    (-0.04, 0.06),
                ],
                [
                    (0, 0.36),
                    (0.19, 0.07),
                    (0.23, -0.12),
                    (0.12, -0.26),
                    (-0.09, -0.27),
                    (-0.23, -0.13),
                    (-0.20, 0.06),
                ],
            ][i]
            geometry(
                "Cut brass note emblem",
                [(iconX + a, iconY, iconZ + b) for a, b in strokes],
                [tuple(range(len(strokes)))],
                "Brass",
            )
        if k == 1:
            for s in (-1, 1):
                shaft(
                    "Tuning fork tine",
                    (x + 0.57 * s, y, z + 0.91),
                    (x + 0.57 * s, y, z + 2.5),
                    0.095,
                    0.075,
                    "Wood",
                )
            shaft("Bell crown spar", (x - 0.66, y, z + 2.5), (x + 0.66, y, z + 2.5), 0.09, 0.09, "Brass")
            bell(x, y, z + 1.35, 1.34 - 0.15 * i, group)
        elif k == 2:
            shaft("Valve stem", (x, y, z + 0.98), (x, y, z + 1.7), 0.12, 0.14, "BellMetal")
            for j in range(8):
                a = j * math.tau / 8
                b = (j + 1) * math.tau / 8
                p = (x + 0.64 * math.cos(a), y + 0.64 * math.sin(a), z + 1.65)
                q = (x + 0.64 * math.cos(b), y + 0.64 * math.sin(b), z + 1.65)
                shaft("Valve rim", p, q, 0.08, 0.08, "Brass", 6, group)
                if j % 2 == 0:
                    shaft("Spoke", (x, y, z + 1.65), p, 0.055, 0.055, "BellMetal", 6, group)
            block("Moving water", (x, 8, 0.45), (2.12, 4.21, 0.06), "Water", "Flow" + str(i))
        elif k == 3:
            block(
                "Amber mirror frame", (x, y, z + 1.78), (1.43, 0.18, 1.30), "Brass", group, math.pi / 4
            )
            for side in [-1, 1]:
                d = 0.11 * side
                block(
                    "Polished reflector",
                    (x - d * 0.707, y + d * 0.707, z + 1.78),
                    (1.23, 0.035, 1.10),
                    "SeaGlass",
                    group,
                    math.pi / 4,
                )
        else:
            seal(x, y, z + 1.7, group, ["FernCloth", "Amber", "SeaGlass"][i])
    if k == 3:
        for i, (a, b) in enumerate(
            [((-12, -1), (-5, -1)), ((-5, -1), (-5, 7)), ((-5, 7), (6, 7)), ((6, 7), (6, -2))]
        ):
            shaft("Light conduit", (*a, 1.65), (*b, 1.65), 0.07, 0.07, "Amber", 6, "Ray" + str(i))
        lathe(
            "Lens receiver",
            6,
            -2,
            0,
            [(0.8, 0), (0.63, 0.25), (0.45, 1.1), (0.23, 1.55), (0.38, 1.72), (0.08, 2.04)],
            "Brass",
            8,
        )
        marker("A_Lens", 6, -2.7, 1.45)
        for i, (a, b) in enumerate([((-5, -1), (-5, -5.4)), ((-5, 7), (-9, 7)), ((6, 7), (6, 11))]):
            shaft("Stray light", (*a, 1.65), (*b, 1.65), 0.06, 0.06, "Amber", 6, "Stray" + str(i))
            lathe(
                "Dark beam stop",
                *b,
                ground(k, *b),
                [(0.50, 0), (0.44, 0.25), (0.30, 1.1), (0.48, 1.45), (0.24, 1.72)],
                "Basalt",
                8,
            )
    if k == 4:
        for j in range(24):
            a = j * math.tau / 24
            b = (j + 0.78) * math.tau / 24
            pts = [
                (math.cos(q) * r, 4 + math.sin(q) * r, 0.17)
                for r, q in [(0.94, a), (1, a), (1, b), (0.94, b)]
            ]
            geometry("Wave in the bronze", pts, [(0, 1, 2, 3)], "Amber", "HushWave")
        origins["HushWave"] = (0, 4, 0.17)
        for i, x in enumerate([-4.7, 4.7]):
            y = 12
            z = ground(k, x, y)
            plinth(x, y, z, "Slate")
            seal(x, y, z + 1.68, "Choice" + str(i), ["Amber", "SeaGlass"][i])
            marker("A_End" + str(i), x, y - 0.85, z + 1.45)
    if k == 0:
        x, y = -5, -12
        model("WZ_FOR_P10", "Meadow trail sign", x, y, 0, 1.8, -10)
        marker("A_Meadow", x, y - 0.7, 1.3)
        model("WZ_SKY_N01", "Ina on the first morning", 3, -6, 0, 1.64, -16, "Ina")
        marker("A_Ina", 3, -6.6, 1.26)
        model("WZ_VIL_P09", "The village watch roster", 3, -6, 0, 1.85, -8, "Roster")
        marker("A_Roster", 3, -6.65, 1.45)


def night_roll():
    # The dedication mounts directly to the front of the east arch pier.
    x,y,z=2.36,14.53,ground(0,2.36,15)+1.2
    group="NightRoll"
    block("Guild dedication frame",(x,y,z+.22),(.65,.08,.49),"Brass",group)
    geometry("Night roll enamel",[(x-.30,y-.046,z+.025),(x+.30,y-.046,z+.025),(x+.30,y-.046,z+.415),(x-.30,y-.046,z+.415)],[(0,1,2,3)],"NightRegister",group,[(0,0),(1,0),(1,1),(0,1)])
    for j in range(10):
        a=j*math.tau/10;b=(j+1)*math.tau/10
        shaft("Pilot’s left-hand knot",(x+.10*math.sin(2*a),y-.07+.032*math.cos(3*a),z-.10+.13*math.cos(a)),(x+.10*math.sin(2*b),y-.07+.032*math.cos(3*b),z-.10+.13*math.cos(b)),.022,.022,"Wood",6,group)
    marker("A_Nameplate",x,y-.38,z+.23)

def public_road_book():
    # Hang the open ledger on the west gate pier opposite Ina's dedication.
    x,y,z=-2.36,14.50,ground(0,-2.36,15)+1.17
    group="RoadBook"
    block("Brass-backed charter case",(x,y,z+.17),(.92,.15,.68),"Brass",group)
    block("Oiled walnut cover",(x,y-.085,z+.17),(.86,.042,.62),"Wood",group)
    for side in (-1,1):
        for j in range(4):
            block("Bound vellum leaves",(x+side*.196,y-.12-j*.008,z+.17),(.389-j*.007,.014,.539-j*.007),"HousePlaster",group)
        a,b=x+side*.022,x+side*.375
        u0,u1=(.5,0) if side<0 else (.5,1)
        geometry("Ruled illuminated page",[(a,y-.172,z-.08),(b,y-.149,z-.08),(b,y-.149,z+.417),(a,y-.172,z+.417)],[(0,1,2,3)],"RoadLetters",group,
                 [(u0,0),(u1,0),(u1,1),(u0,1)])
    shaft("Raised sewing cord",(x,y-.158,z-.112),(x,y-.158,z+.456),.022,.022,"Wood",8,group)
    for dx,dz in [(-.405,-.095),(.405,-.095),(-.405,.427),(.405,.427)]:
        shaft("Corner boss",(x+dx,y-.094,z+dz),(x+dx,y-.123,z+dz),.028,.019,"Brass",8,group)
    for j in range(5):
        xx=x+(j-2)*.085
        block("Household tally ribbon",(xx,y-.141,z-.117-(j%2)*.02),(.048,.018,.14),"SeaCloth" if j%2 else "Amber",group)
    marker("A_RoadBook",x,y-.40,z+.18)


def make(key, lib):
    k = ROOMS.index(key)
    if k in (2,3):
        from river_makers import paint as paint_maker
        paint_maker("FenAtelier" if k==2 else "OssaAtelier")
    if k == 1:
        from choir_paint import make as paint_choir
        paint_choir()
    if k == 4:
        from quiet_art import paint
        paint()
    if k == 0:
        from market_paint import make as paint_market
        paint_market()
        from market_yard import plumage
        plumage(RES/"Textures")
        from pilgrim_art import road_leaf_paint
        from theatre_art import ticket_poster
        from ferry_counter import fen_ticket_paint, fen_ticket, wood_sign_paint, wood_sign
        wood_sign_paint()
        fen_ticket_paint()
        ticket_poster()
        road_leaf_paint()
    if k in (0,2):
        from ferry_counter import destination_board, counter
        destination_board()
    init(lib, 4971 + k)
    floor(k)
    ridge(k)
    dress(k)
    actors(k)
    machinery(k)
    portal(k)
    if k==0:
        from theatre_art import ticket_door
        ticket_door(-9,-10.9,ground(0,-9,-10.9))
        night_roll()
        public_road_book()
        wood_sign(2.9,-10.9,ground(0,2.9,-10.9))
        fen_ticket(9.2,-11.1,ground(0,9.2,-11.1))
    if k in (0,2):
        x,y=(6,-10) if k==0 else (-6,-10)
        counter(x,y,ground(k,x,y))
    marker("Spawn", 0, -14, 0.08)
    marker("Look", 0, -4, 1.4)
    district(k)
    bake_ground(key)
    finish(key)
    if k == 0:
        init(lib, 78)
        lamp(0, 0, 0, "SeaGlass")
        model("WZ_FOR_P10", "Bellmarket sign", 0.75, 0, 0, 1.7)
        finish("TrailSign")
