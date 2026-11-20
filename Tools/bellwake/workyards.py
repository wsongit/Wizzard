"""Stage related articles against the district's existing working furniture."""

import math
import random
from mathutils import Vector
from atelier import batches, geometry, load_paint
from bankside_plants import surface
from workyard_paint import uv_for

# The first and second anchor are different working places. Goods stay with the task
# people perform there, including when the entrance and its quest markers change state.
YARDS = {
    "Bellmarket": (
        ("Delivery cart", "freight"),
        ("Flour casks", "bake"),
        ("Faded copper counter", "folio"),
    ),
    "RootChoir": (
        ("Carved rest bench", "forester"),
        ("Hollow listening stump", "chime"),
    ),
    "Reedwater": (("Lock keeper hut", "boat"), ("Desk writing top", "folio")),
    "CinderLens": (
        ("Glass kiln", "kiln"),
        ("Smithing anvil", "iron"),
        ("Casting crucible", "kiln"),
    ),
    "StillBelfry": (("Walnut music case", "chime"), ("Old warning bell", "iron")),
    "Saltwake": (("Spare canvas", "boat"), ("Old quay", "freight")),
    "RimePost": (("The snow shelter", "wool"), ("The runner cache", "rope")),
    "Glasscut": (("Bench", "kiln"), ("Stamping desk", "folio")),
    "SumpHall": (("Cistern spring", "iron"), ("Recovered reliquary", "folio")),
    "TwinIntake": (("Canal winch", "rope"), ("Cistern shoe", "iron")),
    "FloodLedger": (("Folio shelf", "folio"), ("Oaken shelf", "book")),
    "WeighHouse": (
        ("Unclaimed salt freight", "freight"),
        ("Idle geared winder", "iron"),
    ),
    "CastingBed": (("Fettling bench", "iron"), ("Casting flask", "kiln")),
    "LanternCourt": (("Bedded spindle", "chime"), ("Stone reader", "folio")),
    "OrreryLoft": (("Astronomer’s bearing", "iron"), ("Stone reader.001", "book")),
    "EchoRotunda": (("Vault buttress", "chime"), ("Treasury cradle", "folio")),
    "Wrenfall": (
        ("Tarred barrel staves", "boat"),
        ("Harbourmaster’s document chest", "folio"),
        ("Salt-stained foundation.001", "rope"),
    ),
    "QuinceFold": (
        ("Twisted orchard bole.001", "orchard"),
        ("Workbench top.001", "forester"),
    ),
    "SaffronKilns": (("Bottle kiln chimney", "kiln"), ("Workbench top", "iron")),
    "VellumWalk": (("Archive cabinet back", "book"), ("Workbench top", "folio")),
    "Cairnwatch": (("Wind-scoured spur", "wool"), ("Smith’s stump", "rope")),
    "RainCourt": (("Aqueduct bed", "boat"), ("Workbench top", "folio")),
    "DrumHouse": (("Rising pressure main", "iron"), ("Main gallery header", "chime")),
    "ChainDock": (("Harbour freight case", "freight"), ("Stacked rope cask", "boat")),
    "MouldLoft": (("Coping bench", "kiln"), ("Rack bed", "iron")),
    "SignalLoom": (("Glazed dye vat", "wool"), ("Dyed yarn bobbin", "rope")),
    "KettleYard": (("Hearthstone", "bake"), ("Apple bole", "orchard")),
    "PaperCourt": (("Wing enclosure", "wool"), ("Walnut plinth", "book")),
    "SillwaterEbb": (
        ("Stonework foundation.001", "boat"),
        ("Stonework foundation", "wool"),
    ),
    "SillwaterFlood": (
        ("Stonework foundation.001", "boat"),
        ("Stonework foundation", "wool"),
    ),
    "SillwaterOffice": (("Oiled writing desk", "folio"), ("Index case", "book")),
    "SwallowLock": (("Tidal pump house", "iron"), ("Winch rope coil", "boat")),
    "DriftFen": (
        ("Remnant brick oven", "bake"),
        ("School bench", "book"),
        ("Fork bench", "forester"),
    ),
    "GlassRookery": (("Whistle bench carcass", "folio"), ("Trough bed", "orchard")),
    "GloamingPress": (("Print shop cabinet", "book"), ("Wash bench cupboard", "kiln")),
    "RowanHollow": (("Bellows bench", "forester"), ("Survey cabinet", "book")),
    "MercySlip": (("Oak building stock", "forester"), ("Workbench top", "boat")),
    "Wickwater": (("Twisted orchard bole", "rope"), ("Workbench top", "kiln")),
    "LinenCourt": (
        ("Road line bell.001", "wool"),
        ("Archive cabinet back.001", "folio"),
    ),
    "KiteCrag": (("Tarred rescue rope", "rope"), ("Smith’s stump", "wool")),
    "SoundingBay": (
        ("Diver's bronze bell.002", "boat"),
        ("Lead rack crossbeam", "iron"),
    ),
    "SupperSteps": (("Brick oven lip", "bake"), ("Workbench top", "orchard")),
}


class Stock:
    def __init__(self, x, y, heading, scale, floor):
        self.x, self.y, self.scale = x, y, scale
        self.cs, self.sn = math.cos(heading), math.sin(heading)
        self.floor = floor
        self.vertices = []
        self.faces = []
        self.uv = []

    def xy(self, x, y):
        return self.x + self.scale * (
            x * self.cs - y * self.sn
        ), self.y + self.scale * (x * self.sn + y * self.cs)

    def ground(self, x, y, r):
        # The low corners settle into turf independently. A case on a ramp never floats.
        pts = [
            self.xy(x + a * r, y + b * r)
            for a, b in ((0, 0), (-1, -1), (-1, 1), (1, 1), (1, -1))
        ]
        return min(self.floor(a, b) for a, b in pts) / self.scale - 0.009

    def point(self, p):
        x, y = self.xy(p[0], p[1])
        return (x, y, p[2] * self.scale)

    def face(self, indices, ink, uv=None):
        if uv is None:
            if len(indices) == 4:
                uv = [(0, 0), (1, 0), (1, 1), (0, 1)]
            else:
                uv = [
                    (
                        0.5 + 0.48 * math.cos(j * math.tau / len(indices)),
                        0.5 + 0.48 * math.sin(j * math.tau / len(indices)),
                    )
                    for j in range(len(indices))
                ]
        self.faces.append(tuple(indices))
        self.uv.extend(uv_for(ink, u, v) for u, v in uv)

    def box(self, x, y, z, w, d, h, ink, cap=None, angle=0):
        verts = []
        cos, sin = math.cos(angle), math.sin(angle)
        for hh in (0, h):
            for a, b in ((-w, -d), (w, -d), (w, d), (-w, d)):
                verts.append(
                    self.point(
                        (
                            x + (a * cos - b * sin) * 0.5,
                            y + (a * sin + b * cos) * 0.5,
                            z + hh,
                        )
                    )
                )
        offset = len(self.vertices)
        self.vertices.extend(verts)
        for j, indices in enumerate(
            (
                (3, 2, 1, 0),
                (4, 5, 6, 7),
                (0, 1, 5, 4),
                (1, 2, 6, 5),
                (2, 3, 7, 6),
                (3, 0, 4, 7),
            )
        ):
            self.face([offset + i for i in indices], cap if j == 1 and cap else ink)

    def shape(self, x, y, z, rows, ink, cap=None, n=8):
        base = len(self.vertices)
        for h, rx, ry, dx, dy in rows:
            for i in range(n):
                a = i * math.tau / n
                self.vertices.append(
                    self.point(
                        (x + dx + rx * math.cos(a), y + dy + ry * math.sin(a), z + h)
                    )
                )
        self.face([base + i for i in reversed(range(n))], ink)
        for j in range(len(rows) - 1):
            for i in range(n):
                a = base + j * n + i
                b = base + j * n + (i + 1) % n
                self.face(
                    (a, b, b + n, a + n),
                    ink,
                    [
                        (i / n, j / (len(rows) - 1)),
                        ((i + 1) / n, j / (len(rows) - 1)),
                        ((i + 1) / n, (j + 1) / (len(rows) - 1)),
                        (i / n, (j + 1) / (len(rows) - 1)),
                    ],
                )
        top = base + (len(rows) - 1) * n
        self.face([top + i for i in range(n)], cap or ink)

    def coil(self, x, y, z, r, ink="rope"):
        # A helical turn has a clear centre; its shadow falls on the lid directly below.
        n = 18
        first = len(self.vertices)
        for i in range(n + 1):
            a = i * math.tau / n
            rr = r * (0.97 + 0.04 * math.cos(3 * a))
            for j in range(5):
                b = j * math.tau / 5
                rad = rr + (0.031 + 0.02 * r) * math.cos(b)
                self.vertices.append(
                    self.point(
                        (
                            x + rad * math.cos(a),
                            y + rad * 0.77 * math.sin(a),
                            z + 0.036 + 0.03 * math.sin(b) + 0.016 * i / n,
                        )
                    )
                )
        for i in range(n):
            for j in range(5):
                a = first + i * 5 + j
                b = first + i * 5 + (j + 1) % 5
                self.face(
                    (a, a + 5, b + 5, b),
                    ink,
                    [
                        (i / 3 % 1, j / 5),
                        ((i % 3 + 1) / 3, j / 5),
                        ((i % 3 + 1) / 3, (j + 1) / 5),
                        (i / 3 % 1, (j + 1) / 5),
                    ],
                )
        self.face([first + j for j in reversed(range(5))], ink)
        self.face([first + 5 * n + j for j in range(5)], ink)

    def sack(self, x, y, z, w=1):
        self.shape(
            x,
            y,
            z,
            [
                (h * w, a * w, b * w, dx * w, dy * w)
                for h, a, b, dx, dy in [
                    (0, 0.17, 0.14, 0, 0),
                    (0.09, 0.24, 0.18, 0, 0),
                    (0.36, 0.22, 0.17, 0.015, 0.012),
                    (0.49, 0.065, 0.074, -0.037, 0.018),
                    (0.55, 0.089, 0.081, -0.043, 0.009),
                ]
            ],
            "grain",
        )

    def jars(self, x, y, z):
        for j, (dx, dy, h) in enumerate(((-0.11, 0, 0.42), (0.14, 0.04, 0.32))):
            self.shape(
                x + dx,
                y + dy,
                z,
                [
                    (h * a, h * b, h * b, 0, 0)
                    for a, b in (
                        (0, 0.23),
                        (0.12, 0.33),
                        (0.52, 0.37),
                        (0.72, 0.19),
                        (0.92, 0.13),
                        (1, 0.18),
                    )
                ],
                "salt_glaze" if j else "jug",
                "jar_mouth",
                8,
            )

    def leaf(self, x, y, z, h, lean):
        base = len(self.vertices)
        self.vertices.extend(
            self.point(p)
            for p in [
                (x, y, z),
                (x + lean * 0.34 - 0.048, y - 0.014, z + h * 0.61),
                (x + lean, y + 0.03, z + h),
                (x + lean * 0.34 + 0.045, y - 0.018, z + h * 0.60),
                (x + lean * 0.35, y - 0.052, z + h * 0.57),
            ]
        )
        for a in range(4):
            self.face((base + a, base + (a + 1) % 4, base + 4), "leaves")

    def goods(self, kind, variant):
        box = self.box
        shape = self.shape
        z = self.ground(-0.40, 0.10, 0.40)
        x = -0.4
        y = 0.10
        # Low bench or chest acts as an anchor. Each kit has different stacking and contents.
        if kind in ("folio", "book", "wool", "rope", "boat", "freight"):
            box(x, y, z, 0.78, 0.60, 0.62, "crate", "lid")
            top = z + 0.62
        elif kind in ("iron", "kiln", "chime"):
            box(x, y, z, 0.86, 0.65, 0.26, "end", "lid")
            top = z + 0.26
        else:
            box(x, y, z, 0.79, 0.60, 0.40, "basket", "basket")
            top = z + 0.40
        if kind in ("folio", "book"):
            for i in range(3):
                box(
                    x - 0.09 + 0.012 * i,
                    y - 0.06,
                    top + i * 0.089,
                    0.39,
                    0.28,
                    0.089,
                    "pages",
                    "book",
                    -0.13 + 0.07 * i,
                )
            box(x + 0.19, y + 0.12, top, 0.16, 0.20, 0.15, "spine", "book", 0.09)
            xx = 0.32
            zz = self.ground(xx, 0.22, 0.20)
            box(xx, 0.22, zz, 0.43, 0.34, 0.43, "crate", "lid", 0.12)
            for i in range(2):
                box(
                    xx + 0.024 * i,
                    0.22,
                    zz + 0.43 + 0.064 * i,
                    0.30,
                    0.236,
                    0.064,
                    "pages",
                    "paper",
                    0.11 - 0.06 * i,
                )
            zz = self.ground(0.12, -0.34, 0.13)
            self.jars(0.20, -0.32, zz)
        elif kind in ("freight", "boat", "rope"):
            self.coil(x - 0.10, y, top, 0.216)
            self.coil(x - 0.10, y, top + 0.058, 0.160)
            shape(
                x + 0.21,
                y + 0.03,
                top,
                [
                    (0, 0.081, 0.08, 0, 0),
                    (0.22, 0.07, 0.069, 0.015, 0),
                    (0.25, 0.081, 0.078, 0.014, 0),
                ],
                "sail",
                "wool_end",
                6,
            )
            xx = 0.38
            yy = 0.16
            zz = self.ground(xx, yy, 0.19)
            shape(
                xx,
                yy,
                zz,
                [
                    (0, 0.22, 0.20, 0, 0),
                    (0.12, 0.26, 0.235, 0, 0),
                    (0.48, 0.255, 0.23, 0, 0),
                    (0.57, 0.22, 0.20, 0, 0),
                ],
                "staves",
                "cask_lid",
            )
            for h in (0.085, 0.445):
                shape(
                    xx,
                    yy,
                    zz + h,
                    [(0, 0.262, 0.24, 0, 0), (0.042, 0.263, 0.24, 0, 0)],
                    "metal",
                )
            if kind == "freight":
                box(
                    0.17,
                    -0.36,
                    self.ground(0.17, -0.36, 0.14),
                    0.42,
                    0.29,
                    0.24,
                    "crate",
                    "lid",
                    -0.23,
                )
            else:
                box(
                    0.19,
                    -0.36,
                    self.ground(0.19, -0.36, 0.14),
                    0.43,
                    0.31,
                    0.17,
                    "canvas",
                    "wool",
                    -0.15,
                )
        elif kind == "wool":
            for i in range(3):
                box(
                    x,
                    y,
                    top + i * 0.088,
                    0.48 - i * 0.02,
                    0.36,
                    0.088,
                    "wool" if i % 2 == 0 else "canvas",
                    angle=0.06 * i,
                )
            xx = 0.31
            yy = 0.08
            zz = self.ground(xx, yy, 0.22)
            shape(
                xx,
                yy,
                zz,
                [
                    (0, 0.18, 0.16, 0, 0),
                    (0.35, 0.30, 0.25, 0, 0),
                    (0.40, 0.30, 0.25, 0, 0),
                ],
                "basket",
            )
            for dx, dy, h in (
                (-0.13, 0, 0.24),
                (0.045, 0.08, 0.32),
                (0.10, -0.08, 0.21),
            ):
                shape(
                    xx + dx,
                    yy + dy,
                    zz + 0.38,
                    [(0, 0.078, 0.075, 0, 0), (h, 0.076, 0.074, 0.018, 0.008)],
                    "yarn" if dx > 0 else "wool",
                    "wool_end",
                    7,
                )
            self.coil(0.23, -0.42, self.ground(0.23, -0.42, 0.14), 0.16)
        elif kind in ("bake", "orchard", "forester"):
            if kind == "bake":
                for dx, dy, ang in (
                    (-0.15, -0.05, 0.15),
                    (0.10, 0.059, -0.2),
                    (0.16, -0.12, -0.12),
                ):
                    shape(
                        x + dx,
                        y + dy,
                        top,
                        [
                            (0, 0.12, 0.065, 0, 0),
                            (0.072, 0.149, 0.085, 0, 0),
                            (0.122, 0.078, 0.047, 0.015, 0),
                        ],
                        "bread",
                        "bread",
                        7,
                    )
            elif kind == "orchard":
                for dx, dy, hi in (
                    (-0.18, -0.07, 0),
                    (0.02, -0.12, 0),
                    (-0.10, 0.10, 0),
                    (0.14, 0.06, 0),
                    (-0.02, 0, 0.123),
                ):
                    shape(
                        x + dx,
                        y + dy,
                        top + hi,
                        [
                            (0, 0.077, 0.069, 0, 0),
                            (0.076, 0.106, 0.096, 0, 0),
                            (0.158, 0.068, 0.065, 0.013, 0),
                        ],
                        "apple" if dx > 0 else "quince",
                        "stem" if dx > 0 else "calyx",
                        7,
                    )
            else:
                for i in range(4):
                    self.leaf(
                        x - 0.17 + 0.095 * i, y, top, 0.41 + 0.05 * i, -0.12 + 0.05 * i
                    )
            self.sack(
                0.33,
                0.15,
                self.ground(0.33, 0.15, 0.17),
                1.0 if kind == "bake" else 0.82,
            )
            self.jars(0.20, -0.35, self.ground(0.20, -0.35, 0.10))
        elif kind in ("iron", "kiln", "chime"):
            if kind == "kiln":
                for i in range(5):
                    box(
                        x - 0.04,
                        y + 0.01,
                        top + i * 0.067,
                        0.43,
                        0.29,
                        0.067,
                        "tile",
                        angle=0.02 * i,
                    )
                self.jars(0.30, 0.15, self.ground(0.30, 0.15, 0.13))
            elif kind == "iron":
                for i in range(3):
                    shape(
                        x - 0.18 + i * 0.18,
                        y,
                        top,
                        [(0, 0.085, 0.13, 0, 0), (0.135, 0.064, 0.094, 0, 0)],
                        "iron",
                        "iron",
                        4,
                    )
                box(
                    0.32,
                    0.16,
                    self.ground(0.32, 0.16, 0.18),
                    0.47,
                    0.39,
                    0.28,
                    "crate",
                    "lid",
                    -0.09,
                )
            else:
                for i in range(2):
                    h = 0.24 + 0.065 * i
                    shape(
                        x - 0.15 + i * 0.27,
                        y,
                        top,
                        [
                            (0, 0.142, 0.142, 0, 0),
                            (0.04, 0.147, 0.146, 0, 0),
                            (h * 0.62, 0.088, 0.088, 0, 0),
                            (h, 0.044, 0.043, 0, 0),
                        ],
                        "bronze",
                        "bronze",
                        8,
                    )
                self.coil(0.37, 0.14, self.ground(0.37, 0.14, 0.15), 0.22)
            box(
                0.15,
                -0.36,
                self.ground(0.15, -0.36, 0.14),
                0.47,
                0.25,
                0.17,
                "log",
                "end",
                0.13,
            )
        if variant % 3 == 2 and kind not in ("bake", "forester", "orchard"):
            self.sack(-0.68, -0.42, self.ground(-0.68, -0.42, 0.11), 0.56)


def bounds(obj):
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return tuple(
        Vector([fn(c[i] for c in corners) for i in range(3)]) for fn in (min, max)
    )


def restack(key, floor):
    # Move the complete old prop, including its hoop or strap meshes, as one rigid unit.
    slots = []
    if key == "Wrenfall":
        slots = [((-15.5, -4), (-13.36, -4.21), ("Tarred barrel staves", "Hoop iron"))]
    elif key == "ChainDock":
        for side in (-1, 1):
            for y, yy in zip((-4, 1, 6, 11), (-1.68, 0.04, 8.52, 10.16)):
                slots.append(
                    (
                        (side * 14, y),
                        (side * 14, yy),
                        ("Stacked rope cask", "Cask hoop"),
                    )
                )
            for y, yy in zip((1, 6.4, 11.8), (-1.36, 0.14, 9.32)):
                slots.append(
                    (
                        (side * 16, y),
                        (side * 16, yy),
                        ("Harbour freight case", "Crate binding"),
                    )
                )
    elif key == "SignalLoom":
        for side in (-1, 1):
            for y, (xx, yy) in zip(
                (-3, 0.5, 4, 7.5, 11),
                ((14, -3), (15.23, -2.76), (14.52, -1.87), (14, 8.22), (15.24, 8.51)),
            ):
                slots.append(
                    (
                        (side * 14, y),
                        (side * xx, yy),
                        ("Dyed yarn bobbin", "Bobbin flange"),
                    )
                )
    for (x, y), (xx, yy), labels in slots:
        parts = []
        for o in batches["Set"]:
            if o.name.split(".")[0] not in labels:
                continue
            lo, hi = bounds(o)
            if (
                abs((lo.x + hi.x) * 0.5 - x) < 0.43
                and abs((lo.y + hi.y) * 0.5 - y) < 0.15
            ):
                parts.append(o)
        assert len(parts) == 3, (key, x, y, [o.name for o in parts])
        bottom = min(bounds(o)[0].z for o in parts)
        hh = min(
            floor(xx + a * 0.46, yy + b * 0.46)
            for a, b in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1))
        )
        for o in parts:
            o.location += Vector((xx - x, yy - y, hh - bottom - 0.012))


def gather(key, *, relocate_existing=True):
    import bpy
    from country import THEMES
    from highroad import LANES

    if key not in THEMES or not batches.get("Terrain"):
        return []
    terrain = surface(batches["Terrain"])

    def height(x, y):
        hit = terrain.ray_cast((x, y, 250), (0, 0, -1), 600)[0]
        return hit.z if hit is not None else None

    if relocate_existing:
        restack(key, height)
    bpy.context.view_layer.update()
    load_paint("YardGoods")
    groups = [(key, "Set", batches["Set"], YARDS[key])] if key != "Highroad" else []
    if key == "Highroad":
        # Each cluster belongs to the same streamed cell as its landmark on the native field.
        landmarks = (
            "Coastal beacon",
            "Lock hoist cheek",
            "Roadside shelter",
            "Ridge standing stone",
            "Vented tile kiln",
            "Belfry buttress",
        )
        for r, line in enumerate(LANES):
            for col, gate in enumerate(line.split()):
                group = "FieldCell_%d_%d" % (r, col)
                props = batches.get(group, [])
                if props:
                    groups.append(
                        (gate, group, props, [(landmarks[r], YARDS[gate][0][1])])
                    )
                else:
                    # The compact browser field shares one static batch. Select this gate's own landmark.
                    gatepos = bpy.data.objects["Road" + gate].location
                    matching = [
                        o
                        for o in batches["Set"]
                        if o.name.split(".")[0] == landmarks[r]
                    ]
                    chosen = min(
                        matching,
                        key=lambda o: (sum(bounds(o), Vector()) * 0.5 - gatepos).length,
                    )
                    groups.append(
                        (
                            gate,
                            "Set",
                            batches["Set"],
                            [(chosen.name, YARDS[gate][0][1])],
                        )
                    )
    markers = [
        o.location.copy()
        for o in bpy.context.scene.objects
        if o.type == "EMPTY"
        and (
            o.name.startswith(("A_", "Road", "Hit_", "Rest", "Arrival", "Berth"))
            or o.name == "Spawn"
        )
    ]
    spawn = bpy.data.objects["Spawn"].location
    seed = sum(
        (i + 1) * ord(c)
        for i, c in enumerate(
            "Sillwater" if key in ("SillwaterEbb", "SillwaterFlood") else key
        )
    )
    fixed = batches["Set"] + batches["C_Solids"] + batches["Rim"]
    # Store exact placement in the Blender file so geometry and support can be checked after export.
    report = []
    occupied = []
    static = surface(fixed) if fixed else None
    for place, group, objects, sites in groups:
        obstacles = [static]
        if group != "Set":
            obstacles.append(surface(objects))
        for ix, (label, kind) in enumerate(sites):
            root_label = label.rsplit(".", 1)[0]
            candidates = [o for o in objects if o.name.split(".")[0] == root_label]
            candidates.sort(
                key=lambda o: (
                    o.name != label,
                    (sum(bounds(o), Vector()) * 0.5 - spawn).length,
                )
            )
            if not candidates:
                raise ValueError(f"{place} is missing the stock anchor {label}")
            name = "Workyard · " + place + " · " + kind + " · " + str(ix)
            if any(o.name == name for o in objects):
                continue
            rng = random.Random(seed + ix + sum(place.encode()))

            def spot():
                for scale in (1.12, 0.91):
                    for gap in (0.18, 0.49, 0.86, 1.27, 1.72, 2.18, 2.64):
                        for offset in (
                            0,
                            0.68,
                            -0.68,
                            1.40,
                            -1.40,
                            2.12,
                            -2.12,
                            math.pi,
                        ):
                            a = toward + offset + rng.uniform(-0.07, 0.07)
                            nx, ny = math.cos(a), math.sin(a)
                            # A box face, followed by the stocked area's depth and a working gap.
                            face = min(
                                dx / max(abs(nx), 0.0001), dy / max(abs(ny), 0.0001)
                            )
                            dist = face + scale * 0.68 + gap
                            x, y = center.x + dist * nx, center.y + dist * ny
                            angle = a - math.pi * 0.5 + rng.uniform(-0.12, 0.12)
                            stock = Stock(x, y, angle, scale, height)
                            if any(
                                math.hypot(x - p.x, y - p.y)
                                < (3.35 if key == "Highroad" else 2.15)
                                for p in markers
                            ):
                                continue
                            if any(
                                math.hypot(x - px, y - py) < 2.0 for px, py in occupied
                            ):
                                continue
                            pts = [
                                stock.xy(xx, yy)
                                for xx in (-0.92, -0.58, -0.22, 0.14, 0.47, 0.75)
                                for yy in (-0.64, -0.29, 0.07, 0.42, 0.57)
                            ]
                            zs = [height(px, py) for px, py in pts]
                            if None in zs or max(zs) - min(zs) > 0.28:
                                continue
                            collision = False
                            for (px, py), pz in zip(pts, zs):
                                for tree in obstacles:
                                    if tree is None:
                                        continue
                                    upper = tree.ray_cast(
                                        (px, py, pz + 1.32), (0, 0, -1), 1.27
                                    )[0]
                                    if (
                                        upper is not None
                                        or tree.find_nearest((px, py, pz + 0.33), 0.19)[
                                            0
                                        ]
                                        is not None
                                    ):
                                        collision = True
                                        break
                                if collision:
                                    break
                            if not collision:
                                return stock
                return None

            for obj in candidates:
                lo, hi = bounds(obj)
                center = (lo + hi) * 0.5
                dx, dy = (hi.x - lo.x) * 0.5, (hi.y - lo.y) * 0.5
                toward = math.atan2(spawn.y - center.y, spawn.x - center.x)
                stock = spot()
                if stock:
                    break
            else:
                raise ValueError(f"{place}: no supported stock position beside {label}")
            occupied.append((stock.x, stock.y))
            stock.goods(kind, ix + seed % 3)
            model = geometry(
                name, stock.vertices, stock.faces, "YardGoods", group, stock.uv
            )
            model["yard_anchor"] = obj.name
            model["yard_kit"] = kind
            report.append(
                {
                    "place": place,
                    "anchor": obj.name,
                    "kit": kind,
                    "xy": [round(stock.x, 3), round(stock.y, 3)],
                    "faces": len(stock.faces),
                }
            )
    return report
