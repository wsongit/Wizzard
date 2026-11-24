"""Read actual door faces and reference markers from the editable Blender scenes."""

import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here))
from addresses import *

root = here.parents[2]
dest = root / "Assets/Resources/Bellwake/Houses"
districts = []
signs = []


def coords(v):
    return [round(t, 4) for t in (v[0], v[2], -v[1])]


def bounds(o):
    corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return [Vector([fn(v[i] for v in corners) for i in range(3)]) for fn in [min, max]]


def matches(prefix):
    return sorted(
        [o for o in bpy.context.scene.objects if o.name.split(".")[0] == prefix],
        key=lambda o: o.name,
    )


def door(p, n, record, paint=False, open_space=False):
    style, name, object_name, lore = record
    n = Vector((*n[:2], 0)).normalized()
    p = Vector(p) + n * 0.045
    if name and name not in signs:
        signs.append(name)
    ds.append(
        dict(
            point=coords(p),
            normal=coords(n),
            layout=style,
            name=name,
            sign=signs.index(name) if name else -1,
            objectName=object_name,
            lore=lore,
            paintDoor=paint,
            openSpace=open_space,
        )
    )


def panel(label, records, n=(0, -1)):
    os = matches(label)
    assert len(os) == len(records), (key, label, len(os), len(records))
    for o, r in zip(os, records):
        a, b = bounds(o)
        p = (a + b) / 2
        p.x += n[0] * (b.x - a.x) / 2
        p.y += n[1] * (b.y - a.y) / 2
        door(p, n, r)


def face(label, records, n=(0, -1), baseOffset=1.15):
    os = matches(label)
    assert len(os) == len(records), (key, label, len(os), len(records))
    for i, (o, r) in enumerate(zip(os, records)):
        vec = n[i] if isinstance(n, list) else n
        a, b = bounds(o)
        p = (a + b) / 2
        p.x += vec[0] * (b.x - a.x) / 2
        p.y += vec[1] * (b.y - a.y) / 2
        p.z = a.z + baseOffset
        door(p, vec, r, True)


def public_marker(o, rec):
    p = o.matrix_world.translation.copy() + Vector((1.7, 0, 1.15))
    door(p, (0, -1), rec, False, True)


def anchors():
    if key == "MossbellVillage":
        return []
    os = [o for o in bpy.context.scene.objects if o.type == "EMPTY"]
    a = next(o for o in os if o.name == "Spawn")
    pos = lambda o: o.matrix_world.translation
    b = max(os, key=lambda o: (pos(o) - pos(a)).xy.length)
    c = max(os, key=lambda o: abs((pos(b) - pos(a)).cross(pos(o) - pos(a)).z))
    assert abs((pos(b) - pos(a)).cross(pos(c) - pos(a)).z) > 1
    return [dict(name=o.name, p=coords(pos(o))) for o in (a, b, c)]


public_halls = {
    "KettleYard": "Kettle Yard Cookhouse",
    "PaperCourt": "The Paper Playhouse",
    "SillwaterOffice": "Ada's Chart Office",
    "GloamingPress": "The Gloaming Press",
    "WeighHouse": "The Public Weigh House",
    "FloodLedger": "The Flood Archive",
    "MouldLoft": "The Mould Loft",
    "DrumHouse": "The Drum House",
    "SignalLoom": "The Signal Loom",
    "SupperSteps": "The Common Table",
    "Glasscut": "The Glasscut Works",
    "CinderLens": "The Cinder Lens",
    "SumpHall": "The Pump Guild",
    "ChainDock": "The Chain Dock",
    "OrreryLoft": "The Orrery Loft",
    "EchoRotunda": "The Echo Rotunda",
    "LanternCourt": "The Lantern Court",
    "StillBelfry": "The Still Belfry",
    "LinenCourt": "The Linen Exchange",
    "SaffronKilns": "The Saffron Kilns",
    "TwinIntake": "The Twin Intake",
    "CastingBed": "The Casting Floor",
    "RainCourt": "The Rain Court",
    "VellumWalk": "The Vellum Exchange",
    "SoundingBay": "The Sounding Office",
    "MercySlip": "The Mercy Slip",
    "Wickwater": "The Wick House",
}
keys = set(public_halls) | set(
    "Bellmarket Highroad HighroadBrowser MossbellVillage GlassRookery DriftFen RowanHollow Reedwater Wrenfall SwallowLock Saltwake RimePost SillwaterEbb SillwaterFlood".split()
)
parish = [
    renamed(FERRY, "The Oar House"),
    renamed(SCHOOL, "Penny Reach School"),
    *[home(i) for i in range(6)],
    OFFICE,
]
for key in sorted(keys):
    ds = []
    path = next((root / "Blender").rglob(key + ".blend"))
    bpy.ops.wm.open_mainfile(filepath=str(path))
    if key in ("MossbellVillage", "Bellmarket"):
        index = {
            "Entrance west": BAKER,
            "Entrance east": home(1),
            "Back terrace cottage": home(0),
            "Lower east": BOOK,
            "Lower west": home(3),
            "Middle landmark": renamed(FERRY, "The Brass Shuttle"),
        }
        if key == "MossbellVillage":
            index.update(
                {
                    "Entrance east": POTTER,
                    "Back terrace cottage": renamed(SNOW, "The Bell & Blanket"),
                    "Lower west": renamed(SALT, "Spring Chandlery"),
                    "Middle landmark": WEAVER,
                }
            )
        for prefix, r in index.items():
            for o in matches(prefix + " solid door panel"):
                a, b = bounds(o)
                p = (a + b) / 2
                step = matches(prefix + " stone doorstep")[0]
                sa, sb = bounds(step)
                dr = (sa + sb) / 2 - p
                dr.z = 0
                dr.normalize()
                door(p + dr * 0.06, dr, r)
        if key == "Bellmarket":
            # The hilltop mill stands beyond the district wall. A delivery entrance in the
            # north bank reaches its floor from the public terrace.
            door((9.8, 19.93, 2.06), (0, -1), MILL, True)
            ds[-1]["millPassage"] = True
            door(
                (-9, -6.85, 1.12),
                (0, -1),
                renamed(BAKER, "Tavi’s Provisions"),
                False,
                True,
            )
            panel("Painted playhouse door", [THEATRE, THEATRE])
            ds[-2]["point"] = [
                (x + y) / 2 for x, y in zip(ds[-1]["point"], ds[-2]["point"])
            ]
            ds.pop()
        else:
            door(
                (14.65, 26.9, 9.05),
                (1, 0),
                renamed(WATCH, "Mossbell Pavilion"),
                False,
                True,
            )
    if key in ("Highroad", "HighroadBrowser"):
        lane = ["Mercy", "Kettle", "Supper", "Bellmarket", "Paper", "Press", "Vellum"]
        face("Roadside shelter", [renamed(SNOW, v + " Rest") for v in lane])
        if key == "Highroad":
            stamps = "Sounding Saltwake Chain Wrenfall Glass Kite Rime Mercy Kettle Supper Bellmarket Paper Gloaming Vellum Cairn Saffron Casting Cinder Mould Glasscut Lantern".split()
            face(
                "Toll cottage walls",
                [
                    (
                        "office",
                        v + " Toll House",
                        "The toll stamp",
                        f"The {v} stamp is worn smooth on one edge. "
                        + [
                            "On flood mornings the clerk turned it sideways. A sideways mark meant the return journey was already paid.",
                            "In the margin a runner has drawn a cup. The inn across the ridge accepted that mark in place of a coin.",
                            "The debts on this page are in loaves and lamp oil. The column for names has been carefully scraped clean.",
                        ][i % 3],
                    )
                    for i, v in enumerate(stamps)
                ],
            )
            face("Windmill footing", [renamed(MILL, "The Highroad Mill")])
            face("Whitecap lighthouse", [renamed(WATCH, "Whitecap Light")])
    if key in ("SillwaterEbb", "SillwaterFlood"):
        panel("Plank door", parish)
    if key == "RowanHollow":
        panel("Plank door", [home(2)])
    if key == "DriftFen":
        panel(
            "Plank door",
            [renamed(BAKER, "The Highwater Oven"), renamed(SCHOOL, "The Reed School")],
        )
        face("Watchtower plinth", [renamed(WATCH, "The Fen Watch")])
        pole = matches("Awning pole")[0]
        a, b = bounds(pole)
        door((a.x - 0.15, a.y - 0.33, a.z + 1.47), (0, -1), HOSPITAL, False, True)
    if key == "GlassRookery":
        panel("Plank door", [renamed(FERRY, "The Rookery Lodge")])
        panel("Glasshouse oak door", [GLASS])
    if key == "Reedwater":
        face("Lock keeper hut", [home(4), renamed(PUMP, "The Lock House")])
    if key == "RimePost":
        panel("Front door", [SNOW])
    if key == "Saltwake":
        panel("Front door", [SALT])
    if key == "Wrenfall":
        panel("Plank entry", [renamed(FERRY, "The Pilot's Table"), CHAPEL])
        face("Watchtower battered base", [WATCH])
    if key == "CastingBed":
        panel("Timber door", [FORGE, renamed(BOOK, "The Pattern Store")])
    if key == "SwallowLock":
        panel("Panelled door", [PUMP])
    if key == "PaperCourt":
        face(
            "Neighbour’s house",
            [home(0), home(4), home(3)],
            [(0, -1), (0, -1), (-1, 0)],
        )
    if key == "RowanHollow":
        o = matches("Kite loft roof")[0]
        a, b = bounds(o)
        door((10, a.y, ((a.z + b.z) / 2) - 2.45), (0, -1), LOFT, False, True)
    if key in public_halls:
        # These are already walk-in workspaces. A freestanding nameboard marks their public entrance.
        title = public_halls[key]
        public_marker(
            bpy.data.objects["Spawn"],
            ("office", title, "The brass dedication", HALL_INSCRIPTIONS[key]),
        )
    districts.append(dict(key=key, anchors=anchors(), doors=ds))
if "Lockside Exchange" not in signs:
    signs.append("Lockside Exchange")
dest.mkdir(exist_ok=True)
(dest / "Addresses.json").write_text(
    json.dumps(dict(districts=districts, signs=signs), indent=1, ensure_ascii=False)
    + "\n"
)
