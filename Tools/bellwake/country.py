"""Landscape continuing beyond the playable edge. All geometry is authored in Blender metres."""

import math
import random
from collections import Counter, defaultdict
from mathutils import Vector
from atelier import geometry, batches, RES, load_paint

# Distinct land uses on either side of a district. The angle locates the low pass.
REGIONS = {
    "valley": {
        "Bellmarket": 86,
        "PaperCourt": -54,
        "KettleYard": 24,
        "QuinceFold": -16,
        "LinenCourt": 47,
        "VellumWalk": 109,
        "Wickwater": 88,
        "SupperSteps": -24,
        "Highroad": 63,
    },
    "wood": {"RootChoir": 78, "RowanHollow": 114, "GlassRookery": -18},
    "marsh": {
        "Reedwater": -63,
        "RainCourt": -40,
        "DriftFen": 28,
        "SwallowLock": 4,
        "SillwaterEbb": 2,
        "SillwaterFlood": 2,
        "SillwaterOffice": 2,
    },
    "coast": {
        "Wrenfall": 90,
        "SoundingBay": 26,
        "MercySlip": 136,
        "ChainDock": 90,
        "Saltwake": 173,
    },
    "alpine": {"Cairnwatch": 27, "RimePost": 9, "KiteCrag": 86},
    "kiln": {
        "CinderLens": 14,
        "Glasscut": -20,
        "SaffronKilns": 78,
        "CastingBed": -64,
        "MouldLoft": 71,
        "GloamingPress": -72,
    },
    "quarry": {
        "SumpHall": 2,
        "TwinIntake": -37,
        "FloodLedger": 43,
        "WeighHouse": 125,
        "LanternCourt": -76,
        "OrreryLoft": 45,
        "EchoRotunda": 121,
        "StillBelfry": -91,
        "DrumHouse": 59,
        "SignalLoom": -31,
    },
}
THEMES = {
    room: (i, angle)
    for i, entries in enumerate(REGIONS.values())
    for room, angle in entries.items()
}
# Turf, exposed earth, distant rock, hedge crowns, farm plaster, tile, water and pale summit.
TILES = (
    (
        "Grass",
        "Loam",
        "Mountain",
        "Leaves",
        "HousePlaster",
        "RoofTiles",
        "Water",
        "MossRock",
    ),
    (
        "Moss",
        "ChoirLoam",
        "ChoirOutcrop",
        "Leaves",
        "Wood",
        "ElderBark",
        "Water",
        "MossRock",
    ),
    (
        "Moss",
        "Loam",
        "FenShale",
        "Leaves",
        "OchrePlaster",
        "TarredOak",
        "ParishWater",
        "MossRock",
    ),
    (
        "Moss",
        "Shale",
        "Mountain",
        "Leaves",
        "HousePlaster",
        "RoofSlate",
        "Water",
        "Shale",
    ),
    (
        "RimeSnow",
        "Shale",
        "Mountain",
        "Moss",
        "Masonry",
        "RoofSlate",
        "SeaGlass",
        "RimeSnow",
    ),
    (
        "Loam",
        "Basalt",
        "Mountain",
        "Moss",
        "OchrePlaster",
        "RoofTiles",
        "Water",
        "Shale",
    ),
    ("MossRock", "Shale", "Slate", "Moss", "Masonry", "RoofSlate", "Water", "Shale"),
)
COLORS = (
    (
        (104, 117, 63),
        (101, 85, 60),
        (121, 137, 135),
        (74, 89, 55),
        (167, 150, 116),
        (130, 82, 56),
        (107, 145, 136),
        (142, 148, 132),
    ),
    (
        (74, 99, 63),
        (82, 80, 58),
        (105, 122, 111),
        (51, 78, 49),
        (133, 124, 89),
        (101, 87, 62),
        (93, 133, 123),
        (122, 139, 123),
    ),
    (
        (97, 112, 69),
        (111, 96, 69),
        (114, 136, 129),
        (72, 94, 60),
        (158, 148, 113),
        (103, 92, 72),
        (99, 139, 133),
        (146, 153, 134),
    ),
    (
        (111, 129, 90),
        (116, 117, 97),
        (128, 149, 146),
        (79, 102, 76),
        (182, 168, 131),
        (114, 105, 93),
        (114, 153, 152),
        (158, 164, 146),
    ),
    (
        (135, 151, 144),
        (101, 112, 111),
        (130, 149, 158),
        (76, 99, 90),
        (155, 149, 127),
        (111, 117, 121),
        (127, 153, 160),
        (197, 202, 189),
    ),
    (
        (128, 112, 77),
        (111, 89, 82),
        (138, 118, 115),
        (87, 97, 65),
        (171, 133, 99),
        (142, 85, 63),
        (120, 139, 137),
        (159, 139, 127),
    ),
    (
        (99, 107, 87),
        (96, 103, 101),
        (116, 127, 133),
        (73, 91, 78),
        (145, 143, 127),
        (106, 111, 114),
        (103, 131, 138),
        (142, 149, 150),
    ),
)


def paint():
    from PIL import Image
    import numpy as np

    sheet = Image.new("RGB", (512, 256))
    for region, names in enumerate(TILES):
        for band, name in enumerate(names):
            tile = (
                Image.open(RES / "Textures" / (name + ".png"))
                .convert("L")
                .resize((32, 32), Image.Resampling.BOX)
            )
            mono = np.asarray(tile, float)
            mono = (mono - mono.mean()) / max(1, mono.std())
            contrast = (11, 13, 6, 12, 6, 8, 4, 5)[band]
            rgb = np.clip(
                np.array(COLORS[region][band]) + mono[:, :, None] * contrast, 0, 255
            ).astype("uint8")
            sheet.paste(Image.fromarray(rgb), (band * 32, region * 32))
    from pathlib import Path

    study = Path(__file__).parent / "surface_sources/valley-slopes.png"
    with Image.open(study) as painting:
        for region in range(8):
            strip = painting.crop((0, region * 48, 384, (region + 1) * 48))
            strip = strip.resize((250, 28), Image.Resampling.LANCZOS)
            pixels = np.asarray(strip, dtype=float)
            centre = np.median(pixels, axis=(0, 1))
            base = COLORS[region][2] if region < 7 else COLORS[3][6]
            graded = np.uint8(
                np.clip(np.rint(np.asarray(base) + (pixels - centre) * 0.63), 0, 255)
            )
            border = np.pad(graded, ((2, 2), (3, 3), (0, 0)), mode="edge")
            sheet.paste(Image.fromarray(border), (256, region * 32))
    sheet.save(RES / "Textures/CountryBeyond.png", optimize=True)


def boundary(obj):
    # Follow each exposed edge of the actual mesh. A rim has both an inner loop and an
    # outer loop, and a terrain grid has just the outer one. Pick by projected area.
    links = Counter()
    for f in obj.data.polygons:
        for edge in f.edge_keys:
            links[edge] += 1
    adj = defaultdict(set)
    for (a, b), count in links.items():
        if count == 1:
            adj[a].add(b)
            adj[b].add(a)
    if not adj:
        raise ValueError("No land edge on " + obj.name)
    assert all(len(edges) == 2 for edges in adj.values()), obj.name
    loops = []
    while adj:
        start = next(iter(adj))
        first = start
        prev = None
        loop = []
        while True:
            loop.append(obj.matrix_world @ obj.data.vertices[first].co)
            neighbors = adj[first]
            nxt = next((v for v in sorted(neighbors) if v != prev), None)
            del adj[first]
            if nxt == start or nxt is None:
                break
            prev, first = first, nxt
        area = sum(
            v.x * loop[(i + 1) % len(loop)].y - v.y * loop[(i + 1) % len(loop)].x
            for i, v in enumerate(loop)
        )
        if area < 0:
            loop.reverse()
        loops.append((abs(area), loop))
    return max(loops, key=lambda pair: pair[0])[1]


class CountryMesh:
    def __init__(self, theme):
        self.theme = theme
        self.verts = []
        self.faces = []
        self.uv = []

    def face(self, indices, swatch):
        # Every swatch has a two-pixel gutter. Shared vertex positions keep the folds watertight.
        pattern = (
            ((0.08, 0.12), (0.93, 0.12), (0.93, 0.89), (0.08, 0.89))
            if len(indices) == 4
            else ((0.06, 0.11), (0.95, 0.23), (0.51, 0.93))
        )
        self.faces.append(tuple(indices))
        self.uv.extend(
            ((swatch + u) / 16, 1 - (self.theme + v) / 8) for u, v in pattern
        )

    def polygon(self, points, swatch):
        offset = len(self.verts)
        self.verts.extend(points)
        self.face(range(offset, offset + len(points)), swatch)


def beyond(key):
    if key not in THEMES or not batches.get("Terrain") or batches.get("Surroundings"):
        return
    load_paint("CountryBeyond")
    idx, pass_degrees = THEMES[key]
    seed = sum(
        (i + 1) * ord(v)
        for i, v in enumerate("Sillwater" if key.startswith("Sillwater") else key)
    )
    rand = random.Random(seed)
    phase = rand.uniform(-math.pi, math.pi)
    pass_angle = math.radians(pass_degrees)
    terrain = batches["Terrain"][0]
    rim_names = (
        "North pass and turf banks",
        "Cut escarpment and distant ridgeline",
        "Folded horizon",
        "Encircling ridgeline",
        "Folded headland shore",
    )
    rim = next(
        (o for o in batches.get("Rim", []) if o.name.split(".")[0] in rim_names), None
    )
    coast = key == "Wrenfall"
    edge = boundary(rim or terrain)
    dist = sum(math.hypot(p.x, p.y) for p in edge) / len(edge)
    large = dist > 300
    unit = 4.6 if large else min(1.75, max(0.94, dist / 50))
    profile = (0, 5.5, 17, 31, 45, 60, 80)
    ward = None
    if terrain.name == "Continuous roadbed":
        from pilgrim import ALL_FIELDS, FIELDS
        from relief import REACHES
        from pilgrim_art import elevation

        ix = next(i for i, row in enumerate(ALL_FIELDS) if row[0] == key)
        terrain_type = ix if ix < len(FIELDS) else REACHES[ix - len(FIELDS)][3]
        ward = lambda x, y: float(elevation(terrain_type, x, y))
    angles = [math.atan2(p.y, p.x) for p in edge]

    def land(i, j):
        p = edge[i]
        a = angles[i]
        co, si = math.cos(a), math.sin(a)
        # A low saddle and two unequal masses put the route in a real valley.
        saddle = (0.5 + 0.5 * math.cos(a - pass_angle)) ** 5
        long = (
            0.5
            + 0.28 * math.sin(3 * a + phase)
            + 0.16 * math.sin(5 * a - 0.6 * phase)
            + 0.08 * math.cos(9 * a + phase)
        )
        teeth = (
            abs(math.sin(7 * a + 0.9 * phase)) * 0.55
            + abs(math.cos(11 * a + 0.4)) * 0.45
        )
        relief = (0.56 + long) * (0.58 + 0.42 * (1 - saddle))
        rugged = (0.96, 1.18, 0.65, 0.77, 1.53, 1.22, 1.14)[idx]
        if coast:
            if j == 0:
                return p.copy()
            radius = profile[j] * (1 + 0.09 * math.cos(3 * a))
            x, y = p.x + co * radius * unit, p.y + si * radius * unit
            # Outcrops flank a clear bay. The central arc stays below the water.
            island = (1 - saddle) * max(0, math.sin(3 * a + 0.65) + 0.37)
            z = (-4.85, -5.7, -6.0, -5.8, -5.0, -5.4, -6.1)[j] + (
                0,
                0,
                0,
                1.7,
                4.4,
                9.5,
                2.5,
            )[j] * island
            return Vector((x, y, z))
        if not j:
            return p.copy()
        d = profile[j] * unit * (1 + (0.014 * j) * math.sin(3 * a + phase + j * 0.12))
        # Angular walls give way to rounded slopes with a genuine reverse face and valley floor.
        x = p.x + d * co
        y = p.y + d * si
        if ward and j in (1, 2):
            return Vector((x, y, ward(x, y)))
        zbase = p.z * (1, 0.92, 0.55, 0.26, 0.16, 0.13, 0.09)[j]
        z = (0, -0.40, 1.9, 0.9, 5.4, 15.6, 7.6)[j] * relief * rugged
        z += (0, 0.15, 1.4, 0.6, 1.6, 3.5, 2.1)[j] * teeth
        if key.startswith("Sillwater") and key != "SillwaterOffice" and abs(p.x) > 56:
            from sillwater_art import river

            channel = max(0, 1 - abs(y - float(river(x))) / 15)
            z = (1 - channel) * z - channel * 0.6
        return Vector((x, y, zbase + z * unit))

    mesh = CountryMesh(idx)
    n = len(edge)
    for j in range(len(profile)):
        mesh.verts.extend(land(i, j) for i in range(n))
    for j in range(len(profile) - 1):
        for i in range(n):
            k = (i + 1) % n
            swatch = (0, 0, 0, 1, 2, 7 if idx == 4 else 2)[j]
            if j in (1, 2, 3) and math.cos(angles[i] * 6 + phase) > 0.52:
                swatch = 1
            if coast and j < 4:
                swatch = 6
            # The inner loop is CCW, so advancing outward before turning along it faces up.
            mesh.face([j * n + i, (j + 1) * n + i, (j + 1) * n + k, j * n + k], swatch)
    paint_hillside(mesh, edge, coast)
    if coast:
        water = next(
            o for objs in batches.values() for o in objs if o.name == "Open tidal water"
        )
        cap = max(water.data.polygons, key=lambda face: face.normal.z)
        shore = [water.matrix_world @ water.data.vertices[i].co for i in cap.vertices]
        points = [tuple(v) for v in shore] + [
            (v.x * 2.2, v.y * 2.2, v.z - 0.24) for v in shore
        ]
        nshore = len(shore)
        faces = [
            (i, nshore + i, nshore + (i + 1) % nshore, (i + 1) % nshore)
            for i in range(nshore)
        ]
        geometry("Outer harbour water", points, faces, "Water", "Surroundings")
    else:
        distant_groups(
            mesh, edge, angles, lambda i: land(i, 2), idx, pass_angle, unit, rand
        )
    geometry(
        "Valley floor, shoulders and far crest",
        mesh.verts,
        mesh.faces,
        "CountryBeyond",
        "Surroundings",
        mesh.uv,
    )


def paint_hillside(mesh, edge, coast):
    # Map a continuous painting across adjoining faces. Reverse at each quarter
    # rather than stretching a complete hillside over every narrow terrain quad.
    n = len(edge)
    distance = [0.0]
    for i, point in enumerate(edge):
        distance.append(distance[-1] + (edge[(i + 1) % n] - point).length)
    starts = (
        [0]
        + [
            min(range(n), key=lambda i: abs(distance[i] - distance[-1] * q / 4))
            for q in (1, 2, 3)
        ]
        + [n]
    )
    for quarter, (first, last) in enumerate(zip(starts, starts[1:])):
        length = distance[last] - distance[first]
        for i in range(first, last):
            u = [(distance[j] - distance[first]) / length for j in (i, i + 1)]
            if quarter % 2:
                u = [1 - x for x in u]
            for band in (3, 4, 5):
                # The crest is also the top of the painting. The reverse slope
                # samples back into the image so the paint joins across the ridge.
                lower, upper = ((1, 0.72), (0.72, 0), (0, 0.72))[band - 3]
                coords = ((u[0], lower), (u[0], upper), (u[1], upper), (u[1], lower))
                row = 7 if coast and band == 3 else mesh.theme
                uv = [
                    ((259.5 + x * 249) / 512, 1 - (row * 32 + 2.5 + y * 27) / 256)
                    for x, y in coords
                ]
                start = (band * n + i) * 4
                mesh.uv[start : start + 4] = uv


def distant_groups(mesh, edge, angles, position, theme, pass_angle, unit, rand):
    # Small connected stands or groups of roofs, viewed across the hollow. Leave the saddle open.
    n = len(edge)
    used = []
    for sector in range(7):
        a = sector * math.tau / 7 + rand.uniform(-0.18, 0.18)
        if math.cos(a - pass_angle) > 0.88:
            continue
        first = min(range(n), key=lambda i: 1 - math.cos(angles[i] - a))
        # Three nearby bases, each on an interpolated point of the supporting strip.
        for j in range(rand.randint(2, 4)):
            i = (first + j) % n
            k = (i + 1) % n
            f = rand.uniform(0.12, 0.8)
            p = position(i).lerp(position(k), f)
            if any((p - q).length < 1.3 * unit for q in used):
                continue
            used.append(p)
            tangent = Vector((-math.sin(a), math.cos(a), 0))
            outward = Vector((math.cos(a), math.sin(a), 0))
            p.z -= 0.27 * unit
            if theme in (0, 3, 5, 6) and sector % 3 == 0:
                # Gabled roofs, both eaves and the end wall visible at grazing angles.
                w = rand.uniform(1, 1.7) * unit
                d = rand.uniform(0.8, 1.12) * unit
                h = rand.uniform(1.9, 2.8) * unit
                u = tangent * w
                v = outward * d
                z = Vector((0, 0, h))
                rise = Vector((0, 0, 0.58 * h))
                corners = [p - u - v, p + u - v, p + u + v, p - u + v]
                for l in range(4):
                    mesh.polygon(
                        [
                            corners[l],
                            corners[(l + 1) % 4],
                            corners[(l + 1) % 4] + z,
                            corners[l] + z,
                        ],
                        4,
                    )
                for s in (-1, 1):
                    roof = p + s * v + z
                    mesh.polygon(
                        [roof - u, roof + u, p + u + z + rise, p - u + z + rise], 5
                    )
                    mesh.polygon(
                        [p + s * u - v + z, p + s * u + v + z, p + s * u + z + rise], 4
                    )
            else:
                w = rand.uniform(1.2, 2.3) * unit
                h = rand.uniform(2.0, 4.5) * unit
                low = p + Vector((0, 0, 0.52 * h))
                tip = p + tangent * 0.17 * w + Vector((0, 0, h))
                ring = [
                    low
                    + Vector(
                        (
                            math.cos(t * math.tau / 5 + a) * w,
                            math.sin(t * math.tau / 5 + a) * w,
                            0,
                        )
                    )
                    for t in range(5)
                ]
                for l in range(5):
                    mesh.polygon([p, ring[(l + 1) % 5], ring[l]], 3)
                    mesh.polygon([ring[l], ring[(l + 1) % 5], tip], 3)
