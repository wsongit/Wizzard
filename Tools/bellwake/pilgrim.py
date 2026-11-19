"""The five wards of the Pilgrims' Cut. Art, trail directions and the printed maps use the same passages."""

from collections import deque
import random
from relief import REACHES, LANDINGS, configure_account, fields

SIZE, CELL = 15, 8
ENTRY = (7, 6)
FIELDS = [
    (
        "QuinceFold",
        "The Quince Fold",
        918,
        "Orchard",
        "Mara the grafter",
        "MARA  /  Our road was struck from the flood survey. A living quince once marked its first mile. Help me put one back.",
        [
            (
                "Knife",
                "Grafting bench",
                "knife",
                "Under the linen are a grafting knife and Mara’s brass waywren. Call it with Q or the left grip. It follows the next stretch of your route, then perches to wait.",
                (),
            ),
            (
                "Stock",
                "White rootstock",
                "root",
                "You pare the split stock to a green lip. The grafting bench stands in the west yard.",
                ("Knife",),
            ),
            (
                "Scion",
                "Winter quince",
                "fruit",
                "You cut a live scion above last winter’s scar. Three pale buds will travel safely in the linen.",
                ("Knife",),
            ),
            (
                "Spring",
                "The grafting spring",
                "spring",
                "You wet the wrapping and set the two green lips together. The binding holds.",
                ("Stock", "Scion"),
            ),
            (
                "Mother",
                "First mile tree",
                "tree",
                "You graft the cutting to the mile tree. Mara ties her survey ribbon beside the fresh buds.",
                ("Spring",),
            ),
        ],
        "The live mile tree carries Mara’s ribbon. The next ward is the tileworks.",
    ),
    (
        "SaffronKilns",
        "The Saffron Kilns",
        773,
        "Kiln",
        "Jori the tilemaker",
        "JORI  /  Our path was measured in roof tiles. I saved the first mould, but a wet tile in a hot kiln will split. Bring it through the old works properly.",
        [
            (
                "Mould",
                "Fluted road mould",
                "mould",
                "The brass mould has nine scallops, one for each household along the road.",
                (),
            ),
            (
                "Silt",
                "Settling cistern",
                "spring",
                "You strain red river silt through the rush bed. A palmful rolls without cracking.",
                (),
            ),
            (
                "Press",
                "Tile press",
                "press",
                "The screw sinks the nine-scallop mark into the wet slab. You slide it out on a cedar bat.",
                ("Mould", "Silt"),
            ),
            (
                "Dry",
                "Drying loft",
                "rack",
                "The warm draft under the tiled canopy draws the last damp from the clay.",
                ("Press",),
            ),
            (
                "Fire",
                "Saffron kiln",
                "kiln",
                "You fire the slab in the potter’s saggar. Ochre glaze runs into all nine scallops.",
                ("Dry",),
            ),
            (
                "Wall",
                "Tilemaker’s stair",
                "wall",
                "The fired tile fits the missing step. Jori’s mile can be read again.",
                ("Fire",),
            ),
        ],
        "The nine-scallop tile belongs to the road again. Follow the bookbinders’ lamps.",
    ),
    (
        "VellumWalk",
        "The Vellum Walk",
        413,
        "Archive",
        "Senn the bookbinder",
        "SENN  /  The index calls this place empty. Three depositions survive in separate stacks. Make a rubbing of each seal before we bind them together.",
        [
            (
                "Roll",
                "Binder’s satchel",
                "satchel",
                "You take linen sheets, a stick of graphite and the binder’s bone folder.",
                (),
            ),
            (
                "Potter",
                "Kiln deposition",
                "seal",
                "The potter paid in tiles. A scalloped impression comes up through the paper.",
                ("Roll",),
            ),
            (
                "Herd",
                "Crofter’s deposition",
                "seal",
                "The crofter kept the spring clear for winter stock. Her seal is a curled horn.",
                ("Roll",),
            ),
            (
                "Ferry",
                "Ferryman’s deposition",
                "seal",
                "The ferryman carried the midwife free. His seal carries an oar and a needle.",
                ("Roll",),
            ),
            (
                "Stitch",
                "Binder’s sewing frame",
                "frame",
                "You stitch the three rubbings between the covers. Senn leaves the spine loose for a fourth.",
                ("Potter", "Herd", "Ferry"),
            ),
            (
                "Shelf",
                "Public reading stand",
                "desk",
                "You leave a copy where anyone can read it. The copy for the hill ward slips into your bag.",
                ("Stitch",),
            ),
        ],
        "Three depositions are back in the public index. The hill ward holds the fourth.",
    ),
    (
        "Cairnwatch",
        "Cairnwatch Rise",
        292,
        "Highland",
        "Tern the pathkeeper",
        "TERN  /  My sister took our fourth deposition to the beacon in a whiteout. The cairns turned her home. Trace what she repaired, and the beacon will give it back.",
        [
            (
                "Spool",
                "The ropewalk",
                "spool",
                "You coil a length of tarred line around your shoulder.",
                (),
            ),
            (
                "Spike",
                "Surveyor’s forge",
                "anvil",
                "The pathkeeper’s iron pegs have broad heads for cold hands.",
                (),
            ),
            (
                "Saddle",
                "Wind saddle",
                "line",
                "You set the pegs and tension the handline across the wind saddle.",
                ("Spool", "Spike"),
            ),
            (
                "Glass",
                "Storm lantern",
                "lantern",
                "You lift the storm glass from its cradle. A trace of blue soot marks the sheltered side.",
                ("Saddle",),
            ),
            (
                "Beacon",
                "Cairn beacon",
                "beacon",
                "You fit the storm glass. Its blue lens lights the hollow cairn that held the missing deposition.",
                ("Glass",),
            ),
            (
                "Stone",
                "Shelter cairn",
                "cairn",
                "Inside its dry niche is a child’s route home, signed by every family that opened a door.",
                ("Beacon",),
            ),
        ],
        "The fourth deposition is safe. Carry the road book to the rain court.",
    ),
    (
        "RainCourt",
        "The Rain Court",
        506,
        "Aqueduct",
        "Issa the reeve",
        "ISSA  /  I can strike out an order. I cannot make a road public by myself. Bring the old measures from the court and open the sluices in the road’s name.",
        [
            (
                "Rod",
                "Stone standard",
                "rule",
                "Nine thumb marks on the standard match the nine scallops on the fired tile.",
                (),
            ),
            (
                "Gauge",
                "Rain gauge",
                "gauge",
                "You measure the old winter waterline against the stone standard.",
                ("Rod",),
            ),
            (
                "Weir",
                "West weir",
                "weir",
                "You lift the west paddle to the marked height. The court’s dry race takes water.",
                ("Gauge",),
            ),
            (
                "East",
                "East spillway",
                "weir",
                "You clear the eastern spillway. The wash no longer runs across the public steps.",
                ("Gauge",),
            ),
            (
                "Court",
                "Court of measures",
                "dais",
                "The two races agree at the old stone. Issa witnesses all four depositions and lifts the closure.",
                ("Weir", "East"),
            ),
            (
                "Arch",
                "Pilgrims’ mile arch",
                "arch",
                "The road book takes the ninth scallop. Nine households may use the road without asking leave.",
                ("Court",),
            ),
        ],
        "The right of way is restored. The road now leads into the Root Choir.",
    ),
]


ALL_FIELDS = FIELDS + fields()


def edge(a, b):
    return tuple(sorted((a, b)))


def world(cell):
    return tuple((a - 7) * CELL for a in cell)


def neighbours(cell):
    x, y = cell
    return [
        (a, b)
        for a, b in ((x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1))
        if 0 <= a < SIZE and 0 <= b < SIZE
    ]


def distances(edges, start):
    dist = {start: 0}
    q = deque([start])
    while q:
        a = q.popleft()
        for b in neighbours(a):
            if b not in dist and edge(a, b) in edges:
                dist[b] = dist[a] + 1
                q.append(b)
    return dist


def layout(index):
    key, title, seed, theme, speaker, intro, actions, ending = ALL_FIELDS[index]
    rng = random.Random(seed)
    cells = [(x, y) for y in range(SIZE) for x in range(SIZE)]
    stack = [ENTRY]
    seen = {ENTRY}
    edges = set()
    while stack:
        a = stack[-1]
        options = [b for b in neighbours(a) if b not in seen]
        if not options:
            stack.pop()
            continue
        b = rng.choice(options)
        edges.add(edge(a, b))
        seen.add(b)
        stack.append(b)
    # Cut small courtyards and relief loops into the surveyed lanes.
    edges.add(edge((7, 5), ENTRY))
    for cx, cy in [(7, 6), (3, 3), (10, 11), (4, 10), (11, 3)]:
        for x in (cx, cx + 1):
            edges.add(edge((x, cy), (x, cy + 1)))
        for y in (cy, cy + 1):
            edges.add(edge((cx, y), (cx + 1, y)))
    walls = sorted({edge(a, b) for a in cells for b in neighbours(a)} - edges)
    rng.shuffle(walls)
    for a, b in walls:
        if len(edges) >= SIZE * SIZE + (7 if index >= len(FIELDS) else 22):
            break
        if distances(edges, a)[b] > 14:
            edges.add((a, b))
    if key in LANDINGS:
        return edges, [ENTRY, *LANDINGS[key]]
    # Each work station sits on its own substantial branch; selected once for these authored seeds.
    distance = [distances(edges, ENTRY)]
    sites = [ENTRY]
    for _ in range(len(actions) + 1):
        available = [c for c in cells if c not in sites and abs(c[0] - 7) + abs(c[1] - 6) > 3]
        winner = max(
            available,
            key=lambda c: (
                min(d[c] for d in distance) * 2 + min(12, distance[-1][c]) + 0.01 * rng.random()
            ),
        )
        sites.append(winner)
        distance.append(distances(edges, winner))
    return edges, sites


def add_chapter(room, post, step, visual, machine, relief=False, flags=None):
    indices = range(len(FIELDS), len(ALL_FIELDS)) if relief else range(len(FIELDS))
    for i in indices:
        key, title, seed, theme, speaker, intro, actions, ending = ALL_FIELDS[i]
        edges, sites = layout(i)
        r = room(key, title, intro, theme if relief else key)
        r.update(chapter="The Mercy Run" if relief else "The Pilgrims’ Cut", early=True, halfSpan=60)
        if relief:
            r["homeRoom"] = 3
        landscape = REACHES[i-len(FIELDS)][3] if relief else i
        import math

        def h(x, y):
            raw = (
                0.72
                + 0.5 * math.sin(x / 13 + landscape) * math.cos(y / 17)
                + 1.5 * math.exp(-((x - 29) ** 2 + (y - 24) ** 2) / 450)
            )
            return round(raw * min(1, (x * x + (y + 14) ** 2) / 145), 3)

        r["ground"] = [h(*world((x, y))) for y in range(SIZE) for x in range(SIZE)]
        controls = [a[0] for a in actions]
        channels = [key + c for c in controls]
        finish = channels[-1]
        prerequisites = [sum(1 << controls.index(c) for c in a[4]) for a in actions]

        def advance(mask, op):
            j = controls.index(op)
            need = prerequisites[j]
            return mask | (1 << j) if mask & need == need else mask

        machine(
            key,
            channels,
            controls,
            0,
            advance,
            lambda m: tuple((m >> j) & 1 for j in range(len(actions))),
        )
        x, y = world(ENTRY)
        post(r, "Talk", speaker, x - 1.5, y, "person", step(ending, {finish: 1}), step(intro))
        post(
            r,
            "Map",
            "Ward survey",
            x + 1.5,
            y + 1,
            "map",
            step(
                "Red marks the shelter where you stand. Follow the engraved lanes to the named work yards. Blue rings show the paired road bells. After restoring the ward, ring either bell to hear its partner along the footpath."
            ),
        )
        goals = [dict(step(ending, {finish: 1}), lead="A_Gate")]
        for j, (name, label, style, line, deps) in enumerate(actions):
            x, y = world(sites[j + 1])
            req = {key + d: 1 for d in deps}
            missing = (
                "First visit " + ", ".join(actions[controls.index(d)][1] for d in deps) + "."
                if deps
                else ""
            )
            rules = [
                step(
                    "This work is witnessed. The tool marks are recorded in your road book.",
                    {key + name: 1},
                ),
                step(line, req, move=key + "." + name),
            ]
            if deps:
                rules.append(step(missing))
            post(r, name, label, x, y + 1.35, style, *rules)
            r["stations"][-1]["camp"] = "Rest" + name
            goals.append(
                dict(
                    step(
                        "Find the " + label.lower() + ". Its position is marked on your survey.",
                        {**req, key + name: 0},
                    ),
                    lead="A_" + name,
                )
            )
            visual(r, "Proof" + name, key + name, "show")
        r["goals"] = goals
        x, y = world(sites[-1])
        if relief:
            destination = ALL_FIELDS[i + 1][0] if i + 1 < len(ALL_FIELDS) else "@final"
        else:
            destination = FIELDS[i + 1][0] if i + 1 < len(FIELDS) else "RowanHollow"
        post(
            r,
            "Gate",
            "Passage onward" if relief else "North road wicket",
            x,
            y + 1,
            "gate",
            step(when={finish: 1}, to=destination),
            step("The closure plate is still in place. Finish the work entered in your road book."),
        )
        visual(r, "RoadLamp", finish, "show")
        for st, dest in zip(
            [p for p in r["stations"] if p["id"] in {"A_" + c for c in controls} or p["id"] == "A_Gate"],
            sites[1:],
        ):
            dist = distances(edges, dest)

            def direction(x, y):
                if (x, y) == dest:
                    return "."
                for glyph, (dx, dy) in zip("NESW", [(0, 1), (1, 0), (0, -1), (-1, 0)]):
                    nb = (x + dx, y + dy)
                    if edge((x, y), nb) in edges and dist.get(nb, 999) < dist[x, y]:
                        return glyph
                raise ValueError((x, y))

            st["trail"] = "".join(direction(x, y) for y in range(SIZE) for x in range(SIZE))
        # The two bells answer one another across the restored ward.
        bx, by = world(sites[-2])
        post(
            r,
            "Bell",
            "Return line",
            bx + 2.1,
            by - 1.5,
            "bell",
            step("A low note comes back from the entrance shelter. Follow the lane toward its bell.", {finish: 1}),
            step("This line opens when the ward is restored."),
        )
        x, y = world(ENTRY)
        post(
            r,
            "Fast",
            "Mile line",
            x + 2.4,
            y - 2,
            "bell",
            step("The bell at the far mile answers. Follow the lane toward its sound.", {finish: 1}),
            step("The far bell has no answer yet."),
        )
        if i:
            previous = "DrumHouse" if relief and i == len(FIELDS) else ALL_FIELDS[i - 1][0]
            post(r, "Back", "Previous berth" if relief else "Previous ward", x - 2.5, y - 2, "back", step(to=previous))
        if relief:
            configure_account(i-len(FIELDS), r, post, step, visual, machine, flags)
        for st in r["stations"]:
            if st["id"] in ("A_Talk", "A_Gate"):
                st["camp"] = "Rest" + st["id"][2:]


# Five letters in the market's public road book. Each family answers the player's last choice.
ROAD_LEAVES = [
    dict(
        name="Mara · Orchard post",
        shared="A graft takes when the two cuts grow one skin. Come evening nine children cut nine lanterns from my winter quinces. You should see them waiting their turns at the bell.",
        freed="Ina came for a cutting. She held the knife backward until I showed her. We planted the graft by her door. By supper she had asked me three times when it might flower.",
    ),
    dict(
        name="Jori · Tileworks post",
        shared="I made a thumb tile for each new keeper. Once their shift is done they lay it warm-side down on the sill. My daughter can tell who worked the night by touching the clay.",
        freed="Tavi asked for a roof tile with no mark on it. She and Ina sat on my kiln step drawing sea birds into the wet clay with the same pin.",
    ),
    dict(
        name="Senn · Archive post",
        shared="In the index I wrote room for ten hands, although only nine households live along the road. A stranger ought to be able to sign. You did.",
        freed="The day the bell let her go, Ina brought the book back herself. She crossed out the word missing. She left the space after her name quite empty.",
    ),
    dict(
        name="Tern · Beacon post",
        shared="Someone left a lamp in the cairn for whoever takes the hill after dark. Tonight it was my turn. I left dry socks for the next pair of feet.",
        freed="My sister walked the high mile with Ina. Neither said much. At the last cairn they left two green stones in the dry niche, one for each return.",
    ),
    dict(
        name="Issa · Water court",
        shared="The closure is lifted in nine different hands. My seal sits at the bottom with the rest. The right of way belongs to the next person who needs it.",
        freed="Today a young bellmender asked me if she needed leave to use the road. I took the old closure plate down and gave it to her for a boat anchor.",
    ),
]
