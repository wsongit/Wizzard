"""Build the pilot's quay, courier's post and glass mine from editable Blender geometry."""

import math, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atelier import (
    init,
    model,
    geometry,
    block,
    shaft,
    lathe,
    collision,
    marker,
    origins,
    finish,
)
from sets import arch, seal, lamp, flags
from passages import REGIONS
from passage_landmarks import relief, paint_land, scenery, bake_ground


def base(k):
    stone = ["Shale", "Slate", "Basalt"][k]
    height = relief
    points = [
        (x, y, height(x, y)) for y in range(-20, 21, 2) for x in range(-20, 21, 2)
    ]
    faces = [
        (j * 21 + i, j * 21 + i + 1, j * 21 + i + 22, j * 21 + i + 21)
        for j in range(20)
        for i in range(20)
    ]
    ground = geometry(
        "Course of the old road", points, faces, REGIONS[k]["key"] + "Ground", "Terrain"
    )
    for i, loop in enumerate(ground.data.loops):
        v = ground.data.vertices[loop.vertex_index].co
        ground.data.uv_layers.active.data[i].uv = ((v.x + 20) / 40, (v.y + 20) / 40)
    sides = [(-20, -20), (20, -20), (20, 20), (-20, 20)]
    rows = []
    for i, (x, y) in enumerate(sides):
        nx, ny = sides[(i + 1) % 4]
        for j in range(14):
            t = j / 14
            px = x + (nx - x) * t
            py = y + (ny - y) * t
            rise = (
                3.8 + 2 * math.cos(len(rows) * 0.59) + 1.3 * math.sin(len(rows) * 1.04)
            )
            if k == 0 and px < -19:
                rise = 0.4
            if k == 2:
                rise += 4.4
            rows.append(
                [
                    (px, py, height(px, py) - 0.12),
                    (px * 1.10, py * 1.10, rise * 0.7),
                    (px * 1.26, py * 1.26, rise + 3),
                    (px * 1.7, py * 1.7, rise + 1),
                ]
            )
    rim = geometry(
        "Folded horizon",
        sum(rows, []),
        [
            (
                i * 4 + n,
                ((i + 1) % len(rows)) * 4 + n,
                ((i + 1) % len(rows)) * 4 + n + 1,
                i * 4 + n + 1,
            )
            for i in range(len(rows))
            for n in range(3)
        ],
        stone,
        "Rim",
    )
    for x, y, w, d in [
        (0, -20.4, 41, 0.8),
        (0, 20.4, 41, 0.8),
        (-20.4, 0, 0.8, 41),
        (20.4, 0, 0.8, 41),
    ]:
        collision("Boundary", x, y, -2, w, d, 18)
    for side in (-1, 1):
        flags(side * 3.9, 14, 0, 3.9, ["SeaCloth", "NightCloth", "CoalCloth"][k])
    arch(0, 14, 0, 3.8, 4.7, stone, "Brass")
    seal(0, 14, 3.1, "GateLight", "SeaGlass")
    marker("A_Gate", 0, 13.1, 1.4)
    marker("Spawn", 0, -14, 0.08)
    marker("Look", 0, -4, 1.4)


def chart(k, key):
    # Slanted, brass-bound original chart cabinet. Coordinates of the three registration pins also drive both players.
    def point(u, v, z=0):
        return ((u - 0.5) * 3.36, -3.3 + v * 1.55, 0.80 + v * 0.92 + z)

    for x in [-1.4, 1.4]:
        block("Cabinet foot", (x, -2.54, 0.36), (0.24, 1.45, 0.72), "Wood")
    pts = [
        point(u, v, z) for z in [-0.14, 0] for u, v in [(0, 0), (1, 0), (1, 1), (0, 1)]
    ]
    geometry(
        "Back of the chart chest",
        pts,
        [(0, 3, 2, 1), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)],
        "Wood",
    )
    corners = [point(u, v) for u, v in [(0, 0), (1, 0), (1, 1), (0, 1)]]
    geometry(
        "Inlaid route folio",
        corners,
        [(0, 1, 2, 3)],
        key + "Chart",
        "Chart",
        [(0, 0), (1, 0), (1, 1), (0, 1)],
    )
    for i, a in enumerate(corners):
        shaft("Brass binding", a, corners[(i + 1) % 4], 0.042, 0.042, "Brass", 6)
    collision("Cabinet backstop", 0, -2.5, 0, 3.25, 1.28, 0.7)
    for name, u, v in [
        ("NW", 0.5 / 7, 6.5 / 7),
        ("NE", 6.5 / 7, 6.5 / 7),
        ("SW", 0.5 / 7, 0.5 / 7),
    ]:
        marker(name, *point(u, v, 0.045))
    if k == 0:
        model("WZ_COA_P02", "Carved pilot boat", 0, 0, 0, 0.10, 0, "Pawn")
    elif k == 1:
        model("WZ_ICE_P03", "Mail sled miniature", 0, 0, 0, 0.09, 0, "Pawn")
    else:
        lathe(
            "Surveyor playing piece",
            0,
            0,
            0,
            [
                (0.09, 0),
                (0.10, 0.035),
                (0.047, 0.055),
                (0.05, 0.13),
                (0.073, 0.15),
                (0.025, 0.20),
            ],
            "Brass",
            8,
            "Pawn",
        )
    if k == 2:
        model("WZ_CRY_P02", "Mine wagon miniature", 0, 0, 0, 0.155, 0, "Cargo")
    else:
        lathe(
            "Cache signal",
            0,
            0,
            0,
            [(0.079, 0), (0.09, 0.04), (0.045, 0.08), (0.035, 0.16), (0.008, 0.20)],
            "Amber",
            8,
            "Cargo",
        )
    # The compass shelf is physically joined to the chest, with four keys in compass order.
    block("Compass console", (0, -3.78, 0.56), (2.30, 1.18, 0.20), "Wood")
    for x in (-0.85, 0.85):
        shaft(
            "Console knee", (x, -2.94, 0.20), (x, -4.19, 0.48), 0.10, 0.10, "Brass", 6
        )
    for i, (x, y) in enumerate([(0, -3.44), (0.69, -3.78), (0, -4.12), (-0.69, -3.78)]):
        lathe(
            "Direction key",
            x,
            y,
            0.66,
            [(0.23, 0), (0.21, 0.09), (0.16, 0.12)],
            "Slate",
            8,
        )
        # Raised compass arrows are readable even before a controller highlights the station.
        a = -i * math.pi / 2
        arrow = [
            (-0.033, -0.11),
            (0.033, -0.11),
            (0.033, 0.015),
            (0.095, 0.015),
            (0, 0.115),
            (-0.095, 0.015),
            (-0.033, 0.015),
        ]
        geometry(
            "Ivory bearing",
            [
                (
                    x + u * math.cos(a) - v * math.sin(a),
                    y + u * math.sin(a) + v * math.cos(a),
                    0.784,
                )
                for u, v in arrow
            ],
            [tuple(range(7))],
            "Amber",
        )
        marker("A_Key" + str(i), x, y, 0.84)
    for x, id, mat in [(-2.25, "Hint", "SeaGlass"), (2.25, "Reset", "BellMetal")]:
        lathe(
            "Chart tool",
            x,
            -3,
            0.02,
            [(0.23, 0), (0.18, 0.1), (0.115, 0.72), (0.235, 0.76), (0.21, 0.86)],
            mat,
            8,
        )
        marker("A_" + id, x, -3.18, 0.97)
    block("Stamping desk", (3.8, -0.5, 0.49), (1.36, 0.94, 0.98), "Wood")
    lathe(
        "Postmaster seal",
        3.8,
        -0.5,
        1,
        [(0.19, 0), (0.175, 0.09), (0.075, 0.13), (0.075, 0.35), (0.15, 0.38)],
        "Brass",
        8,
    )
    marker("A_Stamp", 3.8, -1.1, 1.2)


def scene(k, lib):
    reg = REGIONS[k]
    key = reg["key"]
    paint_land(k, key)
    init(lib, 989 + k)
    base(k)
    scenery(k)
    chart(k, key)
    prefix = ["COA", "ICE", "CRY"][k]

    def obj(n, name, x, y, h, a=0):
        model("WZ_" + prefix + "_P%02d" % n, name, x, y, 0, h, a)

    model("WZ_" + prefix + "_N01", reg["guide"], -3.8, -8.8, 0, 1.67, -12, "Speaker")
    marker("A_Talk", -3.8, -9.42, 1.3)
    model(
        "WZ_" + prefix + "_N02", "Wayside familiar", 4.2, -8.1, 0, 0.72, 29, "Familiar"
    )
    layouts = [
        [
            (9, "The tide staff", -8.7, -6, 3.1, 0),
            (3, "The salvage crane", 10, 3, 3.8, -22),
            (5, "The last beacon", -7.7, 10, 6.7, 8),
            (2, "Ferry in the shallows", -14, -3, 1.05, 29),
            (1, "Old quay", -14, 4, 0.9, 0),
            (8, "Spare canvas", 8, -9, 3.2, 45),
            (4, "Crab pots", -8, 4, 1.35, -6),
            (6, "Salt cargo", 12, -3, 1.2, 35),
            (10, "Shell cairn", 7, 11, 1.85, 0),
        ],
        [
            (1, "The snow shelter", -9, -5, 3.25, 8),
            (10, "The runner cache", 9.2, 2, 1.35, -20),
            (9, "The leaning pine", -8, 10, 5.8, 19),
            (2, "Frost gate", 8, 10, 4.65, 18),
            (3, "Runners at rest", 9, -8, 1.17, -19),
            (5, "Pass pole", -11, 2, 2.4, 6),
            (7, "Aurora lantern", -4, 5, 2.65, 11),
            (8, "Post tools", 13, -2, 2.1, -35),
            (9, "Twinned pine", -13, 13, 4.2, -71),
        ],
        [
            (9, "The survey stand", -8, -6, 2.7, -3),
            (4, "The lift cage", 9, 3, 4.5, 23),
            (10, "The resonance cradle", -7.5, 10, 2.9, -12),
            (3, "Tunnel brace", 9, -9, 3.5, -25),
            (1, "Silver geode", -13, 3, 4.6, 0),
            (5, "Ore washer", 9.5, 10, 2.7, 16),
            (6, "Bench", -12, -11, 1.7, 15),
            (8, "Tuning chimes", -10.3, 5.8, 2.35, 3),
            (7, "Glowcap seam", 13, -3, 1.8, -7),
        ],
    ]
    for j, (n, name, x, y, h, a) in enumerate(layouts[k]):
        obj(n, name, x, y, h, a)
        if j < 3:
            # Freestanding letter posts keep the controls outside the actual prop silhouette.
            px = x + (-1 if x > 0 else 1) * 2.75
            py = y - 1.9
            block("Witness post", (px, py, 0.6), (0.25, 0.29, 1.2), "Wood")
            block("Stamped docket", (px, py - 0.04, 1.22), (0.52, 0.32, 0.10), "Brass")
            marker("A_Log" + str(j), px, py - 0.30, 1.42)
    for x, y in [(-6, -1), (5, 5)]:
        lamp(x, y, 0, ["Amber", "SeaGlass", "Amber"][k])
    bake_ground(key, relief)
    finish(key)


if __name__ == "__main__":
    lib = Path(sys.argv[sys.argv.index("--") + 1])
    wanted = sys.argv[sys.argv.index("--") + 2 :]
    for k in range(3):
        if not wanted or REGIONS[k]["key"] in wanted:
            scene(k, lib)
