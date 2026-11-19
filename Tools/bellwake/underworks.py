"""Authored room layout, witness script and finite mechanisms for the Lower Works."""

import json
from pathlib import Path
from itertools import product

RES = Path(__file__).resolve().parents[2] / "Assets/Resources/Bellwake"
machines = []
rooms = []
flags = [
    "admitted",
    "wetKey",
    "reed",
    "balanceKey",
    "yoke",
    "opticKey",
    "glass",
    "reedSet",
    "yokeSet",
    "glassSet",
    "answered",
]


def machine(key, channels, controls, initial, operator, outputs):
    states = [initial]
    indices = {initial: 0}
    rows = []
    for state in states:
        moves = []
        for op in controls:
            target = operator(state, op)
            if target not in indices:
                indices[target] = len(states)
                states.append(target)
            moves.append(indices[target])
        rows.append(dict(values=list(outputs(state)), moves=moves))
    machines.append(dict(key=key, channels=channels, controls=controls, rows=rows))


def tank(s, op):
    a, b = s
    if op == "rain":
        return 3, b
    if op == "spring":
        return a, 5
    if op == "wasteA":
        return 0, b
    if op == "wasteB":
        return a, 0
    if op == "east":
        d = min(a, 5 - b)
        return a - d, b + d
    d = min(b, 3 - a)
    return a + d, b - d


machine(
    "water",
    ["small", "deep"],
    ["rain", "spring", "wasteA", "wasteB", "east", "west"],
    (0, 0),
    tank,
    lambda s: s,
)


def echoes(s, op):
    seq = ["roof", "oar", "mill", "reed"]
    return 4 if s == 4 else s + 1 if op == seq[s] else int(op == seq[0])


machine("record", ["verse"], ["roof", "oar", "mill", "reed"], 0, echoes, lambda s: (s,))


def load(s, op):
    v = list(s)
    i = ["one", "two", "four"].index(op)
    v[i] = (v[i] + 1) % 3
    return tuple(v)


def weights(s):
    a = 1 + sum(2**i for i, n in enumerate(s) if n == 1)
    b = sum(2**i for i, n in enumerate(s) if n == 2)
    return (*s, a, b, max(-3, min(3, a - b)), int(a == b and 0 not in s))


machine(
    "crane",
    ["w1", "w2", "w4", "westPan", "eastPan", "tilt", "level"],
    ["one", "two", "four"],
    (0, 0, 0),
    load,
    weights,
)


def cast(s, op):
    if s == 5:
        return s
    if op == "recast":
        return 0
    return (
        s + 1
        if op == ["sand", "wax", "pour", "vent", "quench"][s]
        else (0 if op == "quench" else s)
    )


machine(
    "cast",
    ["heat", "molten", "finished"],
    ["sand", "wax", "pour", "vent", "quench", "recast"],
    0,
    cast,
    lambda s: (s, int(s in (3, 4)), int(s == 5)),
)


def optics(s, op):
    switch, left, right, moon, sun = s
    if op == "fork":
        switch ^= 1
    if op == "left":
        left = (left + 1) % 4
    if op == "right":
        right = (right + 1) % 4
    if op == "catch":
        moon |= int(switch == 0 and left == 2)
        sun |= int(switch == 1 and right == 3)
    return switch, left, right, moon, sun


machine(
    "prism",
    ["fork", "left", "right", "moon", "sun", "westRay", "eastRay", "moonRay", "sunRay"],
    ["fork", "left", "right", "catch"],
    (0, 0, 0, 0, 0),
    optics,
    lambda s: (
        *s,
        1 - s[0],
        s[0],
        int(s[0] == 0 and s[1] == 2),
        int(s[0] == 1 and s[2] == 3),
    ),
)


def orbit(s, op):
    a, b, c = s
    if op == "outer":
        return (a + 1) % 4, (b + 1) % 4, c
    if op == "middle":
        return a, (b + 1) % 4, (c + 1) % 4
    return a, b, (c + 1) % 4


machine(
    "orbits",
    ["oak", "wren", "tide"],
    ["outer", "middle", "inner"],
    (0, 0, 0),
    orbit,
    lambda s: s,
)


def hymn(s, op):
    notes = ["river", "forge", "sky", "river", "sky"]
    return 5 if s == 5 else s + 1 if op == notes[s] else int(op == notes[0])


machine("heart", ["phrase"], ["river", "forge", "sky"], 0, hymn, lambda s: (s,))


def step(text="", when=None, award="", move="", to=""):
    return dict(
        line=text,
        when=[dict(signal=k, value=v) for k, v in (when or {}).items()],
        award=award,
        move=move,
        to=to,
    )


def room(key, title, intro, theme):
    rooms.append(
        dict(key=key, title=title, intro=intro, theme=theme, stations=[], visuals=[])
    )
    return rooms[-1]


def post(r, id, label, x, y, style, *steps):
    r["stations"].append(
        dict(id="A_" + id, label=label, x=x, y=y, style=style, rules=list(steps))
    )


def door(r, id, title, x, y, to, when=None, blocked="The lift is still locked."):
    rules = [step(when=when, to=to)]
    if when:
        rules.append(step(blocked))
    post(r, id, title, x, y, "lift", *rules)


def info(r, id, title, x, y, text):
    post(r, id, title, x, y, "leaf", step(text))


def act(r, id, title, x, y, tool, op, text):
    post(r, id, title, x, y, tool, step(text, move=op))


def v(r, node, signal, kind, amount=1, match=1):
    r["visuals"].append(
        dict(node=node, signal=signal, kind=kind, amount=amount, match=match)
    )


r = room(
    "SumpHall",
    "Court of Three Trades",
    "Below the kiln, three lift bells wait in a dry cistern. Read the roll beside the survey lantern.",
    "LowerWorks",
)
post(
    r,
    "Roll",
    "The night roll",
    -3,
    -9,
    "leaf",
    step(
        "Night crew: the river measurer, the bronze dresser, the keeper of stars. Bring their reed, yoke and nightglass to the great resonator.",
        award="admitted",
    ),
)
for id, title, x, y, to in [
    ("Intake", "Waterworks", -12, -1, "TwinIntake"),
    ("Crane", "Freight works", 12, -1, "WeighHouse"),
    ("Court", "Lamp works", 0, 13, "LanternCourt"),
]:
    door(
        r,
        id,
        title,
        x,
        y,
        to,
        {"admitted": 1},
        "The lift needs a name on the night roll.",
    )
door(
    r,
    "Heart",
    "The resonator",
    8,
    9,
    "EchoRotunda",
    {"reed": 1, "yoke": 1, "glass": 1},
    "Three sockets on the lintel: a river reed, a bronze yoke, and a disc of nightglass.",
)
info(
    r,
    "Plan",
    "Cistern survey",
    -8,
    8,
    "West measures the water. East balances bronze. North keeps the night lamps. Their buried service stairs join behind the works.",
)
for j, s in enumerate(["reed", "yoke", "glass"]):
    v(r, "Beacon" + str(j), s, "show")

r = room(
    "TwinIntake",
    "The Divided Intake",
    "A rain tank holds three measures. A spring tank holds five. The blue chalk mark in the deep tank stands at four.",
    "Waterworks",
)
for id, title, x, y, op in [
    ("Rain", "Fill the rain tank", -9, -4, "rain"),
    ("Spring", "Fill the spring tank", 9, -4, "spring"),
    ("DrainA", "Drain the rain tank", -9, 4, "wasteA"),
    ("DrainB", "Drain the spring tank", 9, 4, "wasteB"),
    ("East", "Pour west to east", -2, -4, "east"),
    ("West", "Pour east to west", 2, -4, "west"),
]:
    act(
        r,
        id,
        title,
        x,
        y,
        "valve",
        "water." + op,
        "West gauge {small}/3. East gauge {deep}/5.",
    )
post(
    r,
    "Float",
    "Test the lock float",
    0,
    6,
    "lever",
    step(
        "The float touches the fourth notch. Counterweights lift the archive gate.",
        {"deep": 4},
        "wetKey",
    ),
    step("The float reads {deep}. The blue notch is four."),
)
info(
    r,
    "Plate",
    "Pipe diagram",
    -13,
    9,
    "The brass crossfeeds stop when the receiving tank fills or the source runs dry. Spill water at either drain. Only the east gauge sets the lock.",
)
door(r, "Archive", "Flood archive", 0, 14, "FloodLedger", {"wetKey": 1})
door(r, "Home", "Cistern lift", -12, -10, "SumpHall")
v(r, "WestWater", "small", "lift", 0.41)
v(r, "EastWater", "deep", "lift", 0.32)
v(r, "LockLamp", "wetKey", "show")

r = room(
    "FloodLedger",
    "Archive of High Water",
    "An archivist filed the night of the flood by sound. Read the two surviving accounts, then play the four reliefs in the order the witnesses heard them.",
    "Waterworks",
)
info(
    r,
    "Page1",
    "A ferryman’s deposition",
    -11,
    7,
    "I was on the roof before the oar touched the gutter. The mill wheel was silent until the ferryman pulled us off.",
)
info(
    r,
    "Page2",
    "The miller’s deposition",
    11,
    7,
    "First came the roof tiles giving way. The wheel began to turn after the oar struck. Only then did we hear Ina whistle through a reed.",
)
for id, title, x, y, op in [
    ("Roof", "A falling roof", -9, -3, "roof"),
    ("Oar", "An oar on slate", -3, 2, "oar"),
    ("Mill", "A mill wheel", 3, 2, "mill"),
    ("Reed", "A reed whistle", 9, -3, "reed"),
]:
    act(
        r,
        id,
        title,
        x,
        y,
        "chime",
        "record." + op,
        "The archive echoes {verse} of four sounds.",
    )
post(
    r,
    "Take",
    "The river reed",
    0,
    10,
    "relic",
    step(
        "An ordinary cut reed. The river measurer carried it to call boats in fog. It still holds her breath.",
        {"verse": 4},
        "reed",
    ),
    step("The four reliefs have not answered together."),
)
door(r, "Home", "Intake lift", -12, -10, "TwinIntake")
door(r, "Short", "Cargo stair", 12, -10, "WeighHouse", {"reed": 1})
v(r, "ReedLight", "verse", "show", match=4)

r = room(
    "WeighHouse",
    "The Counterweight House",
    "The west pan carries a fixed one-pound bell. Balance both pans using all three loose weights, then set the brake at the north gantry.",
    "Bronzeworks",
)
for id, n, x, y, op in [
    ("One", 1, -8, -4, "one"),
    ("Two", 2, 0, -5, "two"),
    ("Four", 4, 8, -4, "four"),
]:
    act(
        r,
        id,
        str(n) + " lb crane",
        x,
        y,
        "winch",
        "crane." + op,
        "The crane cycles store, west, east. West: {westPan} lb. East: {eastPan} lb.",
    )
post(
    r,
    "Brake",
    "Set the brake",
    0,
    8,
    "lever",
    step(
        "The pointer rests at the notch. The casting lift engages.",
        {"level": 1},
        "balanceKey",
    ),
    step(
        "West {westPan}, east {eastPan}. Hang every loose weight and bring the beam level."
    ),
)
info(
    r,
    "Ticket",
    "Freight ticket",
    -12,
    7,
    "The western shipping bell weighs one pound before any loose freight lands. The removable ingots weigh one, two and four. Every ingot must leave its rack.",
)
door(r, "Kiln", "Casting bed", 0, 14, "CastingBed", {"balanceKey": 1})
door(r, "Home", "Cistern lift", -12, -10, "SumpHall")
v(r, "BalanceBeam", "tilt", "roll", 3)
for n in [1, 2, 4]:
    for slot in range(3):
        v(r, "Load" + str(n) + "At" + str(slot), "w" + str(n), "show", match=slot)

for j in [1, 2]:
    amt = (-1 if j == 1 else 1) * 0.22
    v(r, "Pan" + str(j), "tilt", "lift", amt)
    for n in [1, 2, 4]:
        v(r, "Load" + str(n) + "At" + str(j), "tilt", "lift", amt)
r = room(
    "CastingBed",
    "Hall of Lost Wax",
    "The molds are cold. Ina’s casting receipt is pinned to the annealing pillar. Its pencil lines survived the fire.",
    "Bronzeworks",
)
info(
    r,
    "Book",
    "The caster’s receipt",
    -11,
    7,
    "Pack the river sand. Press in the wax master. Pour the bell bronze. Open the vent to free the last pocket of air. Quench only after the fourth mark.",
)
for id, title, x, y, op in [
    ("Sand", "Pack the flasks", -9, -5, "sand"),
    ("Wax", "Seat the wax master", -7, 2, "wax"),
    ("Pour", "Tip the crucible", 0, 6, "pour"),
    ("Vent", "Open the vent", 7, 2, "vent"),
    ("Cool", "Quench the yoke", 9, -5, "quench"),
]:
    act(
        r,
        id,
        title,
        x,
        y,
        "lever",
        "cast." + op,
        "Process mark {heat}/5. A premature quench resets the bed.",
    )
post(
    r,
    "Take",
    "The bronze yoke",
    0,
    11,
    "relic",
    step(
        "Inside the yoke someone engraved a time limit: until morning. The foundry never agreed to a second night.",
        {"finished": 1},
        "yoke",
    ),
    step("The master still lies in the sand."),
)
door(r, "Home", "Counterweight lift", -12, -10, "WeighHouse")
door(r, "Short", "Lampmakers’ stair", 12, -10, "LanternCourt", {"yoke": 1})
v(r, "LiquidBronze", "molten", "show")
v(r, "BrightYoke", "finished", "show")

r = room(
    "LanternCourt",
    "Court of Borrowed Light",
    "A shutter sends one shaft of light down either aisle. Both receiving cups must hold a reflection to wake the observatory.",
    "Lampworks",
)
for id, name, x, y, op in [
    ("Fork", "Swing the shutter", 0, -5, "fork"),
    ("Left", "Turn the moon mirror", -8, 2, "left"),
    ("Right", "Turn the sun mirror", 8, 2, "right"),
]:
    act(
        r,
        id,
        name,
        x,
        y,
        "wheel",
        "prism." + op,
        "The west mirror reads {left}; east reads {right}. Follow the glass line to the two receiving cups.",
    )
act(
    r,
    "Catch",
    "Capture the reflection",
    0,
    8,
    "lever",
    "prism.catch",
    "Moon stored {moon}/1. Sun stored {sun}/1.",
)
post(
    r,
    "Iris",
    "Release the iris",
    0,
    11,
    "lever",
    step(
        "Both cups flare. The roof iris slides open.", {"moon": 1, "sun": 1}, "opticKey"
    ),
    step("The moon and sun cups must each store a reflection."),
)
info(
    r,
    "Etching",
    "A lampmaker’s etching",
    -12,
    9,
    "The moon silver was cut on its second face. The sun brass took its third. Aim the shutter down each aisle and capture its light before you switch.",
)
door(r, "Loft", "Orrery lift", 8, 12, "OrreryLoft", {"opticKey": 1})
door(r, "Home", "Cistern lift", -12, -10, "SumpHall")
for tag, signal in [
    ("WestRay", "westRay"),
    ("EastRay", "eastRay"),
    ("MoonRay", "moonRay"),
    ("SunRay", "sunRay"),
    ("MoonCup", "moon"),
    ("SunCup", "sun"),
]:
    v(r, tag, signal, "show")
for tag, signal in [
    ("Shutter", "fork"),
    ("MoonMirror", "left"),
    ("SunMirror", "right"),
]:
    v(r, tag, signal, "turn", 90)

r = room(
    "OrreryLoft",
    "The Unwound Orrery",
    "The last sky of the flood has slipped out of the calendar. Sight the three fixed bearings around the gallery, then wind the brass rings.",
    "Lampworks",
)
for id, name, x, y, op in [
    ("Oak", "Wind the oak ring", -7, -3, "outer"),
    ("Wren", "Wind the wren ring", 0, -5, "middle"),
    ("Tide", "Wind the tide ring", 7, -3, "inner"),
]:
    act(
        r,
        id,
        name,
        x,
        y,
        "wheel",
        "orbits." + op,
        "Oak {oak}, wren {wren}, tide {tide}. Each dial counts zero through three.",
    )
for id, n, x, y, text in [
    ("Vane", "Oak sight", -12, 6, "The oak stood in the second quarter."),
    ("Nest", "Wren sight", 0, 12, "The wren perched at the first quarter."),
    ("Bay", "Tide sight", 12, 6, "The tide mark rests at the second quarter."),
]:
    info(r, id, n, x, y, text)
post(
    r,
    "Take",
    "Nightglass cradle",
    0,
    6,
    "relic",
    step(
        "The nightglass holds the sky from twelve years ago. A girl is looking up from the lock.",
        {"oak": 2, "wren": 1, "tide": 2},
        "glass",
    ),
    step(
        "The oak hand draws the wren with it. The wren draws the tide. Only the tide turns alone."
    ),
)
door(r, "Home", "Lantern lift", -12, -10, "LanternCourt")
door(r, "Short", "Cistern stair", 12, -10, "SumpHall", {"glass": 1})
for tag, signal in [("OakRing", "oak"), ("WrenRing", "wren"), ("TideRing", "tide")]:
    v(r, tag, signal, "turn", 90)

r = room(
    "EchoRotunda",
    "The First Resonator",
    "The old instrument has three mouths. Fit the witnesses’ gifts, then play the five-bar phrase engraved on its rim.",
    "LowerWorks",
)
for id, name, x, y, artifact, op, occupied in [
    ("River", "Reed pipe", -9, 0, "reed", "river", "reedSet"),
    ("Forge", "Yoke drum", 0, 7, "yoke", "forge", "yokeSet"),
    ("Sky", "Nightglass harp", 9, 0, "glass", "sky", "glassSet"),
]:
    post(
        r,
        id,
        name,
        x,
        y,
        "chime",
        step(
            "The voice answers bar {phrase}/5.",
            {"reedSet": 1, "yokeSet": 1, "glassSet": 1},
            move="heart." + op,
        ),
        step(
            "The witness gift locks into the sounding board.",
            {artifact: 1, occupied: 0},
            occupied,
        ),
        step("Fit the other gifts before playing."),
    )
info(
    r,
    "Score",
    "The rim engraving",
    -9,
    9,
    "Reed calls to bronze. Bronze calls to glass. The reed calls once more, and the glass replies. Five sounds, with a breath between them.",
)
post(
    r,
    "Listen",
    "Voice under the floor",
    0,
    11,
    "relic",
    step(
        "INA  /  I did promise to keep watch. I never promised to stop growing up. Tell Tavi I still want the window by the river.",
        {"phrase": 5},
        "answered",
    ),
    step("The instrument is waiting for the complete phrase."),
)
door(r, "Home", "Cistern lift", -12, -10, "SumpHall")
door(
    r,
    "Final",
    "Lift to the Still Belfry",
    12,
    -10,
    "Wrenfall",
    {"answered": 1},
    "Speak to the voice beneath the floor after playing the phrase.",
)
for j, s in enumerate(["reedSet", "yokeSet", "glassSet"]):
    v(r, "Mouth" + str(j), s, "show")
v(r, "BellHeart", "phrase", "show", match=5)
# Crew members remember what the official copies omitted. Evidence can be gathered in any wing order.
flags.extend(["petition", "knot", "blank", "wage", "token", "named"])
post(
    rooms[0],
    "Nema",
    "Nema the archivist",
    -5,
    -8.1,
    "person",
    step(
        "NEMA  /  Four places at supper tonight. I have already laid out the plates.",
        {"named": 1},
    ),
    step(
        "NEMA  /  Ina, fourth hand of the night shift. There. A name, a wage, a place at the table. I can put the book away now.",
        {"token": 1},
        "named",
    ),
    step(
        "NEMA  /  Fen can tie the pilots’ knot. Orrel kept the pay leaf. Brannic knows what the fourth hand earned. Take those three proofs to Ossa at the casting bed.",
        {"petition": 1},
    ),
    step(
        "NEMA  /  The roll lists three trades. Our soup pot fed four. If you learn who the fourth hand was, bring me something I can file.",
        award="petition",
    ),
)
post(
    rooms[1],
    "Fen",
    "Fen the lockkeeper",
    -12,
    -5,
    "person",
    step(
        "FEN  /  Ina tied her mooring rope left over right. This was the knot she used that night. Take it; you can feel the turn with your eyes shut.",
        award="knot",
    ),
)
post(
    rooms[2],
    "Orrel",
    "Orrel the witness",
    -14,
    11,
    "person",
    step(
        "ORREL  /  Hold the blank pay leaf to the light. See the dents? Someone wrote Ina, then lifted the ink. The paper remembers the weight of the pen.",
        award="blank",
    ),
)
post(
    rooms[3],
    "Brannic",
    "Brannic the foreman",
    -10,
    -6.6,
    "person",
    step(
        "BRANNIC  /  Four wage counters on my scale that morning. One came back with nobody to collect it. I kept it under the pan.",
        award="wage",
    ),
)
post(
    rooms[4],
    "Ossa",
    "Ossa the crane smith",
    10,
    -7.1,
    "person",
    step("OSSA  /  Nema will know where to hang the new nameplate.", {"token": 1}),
    step(
        "OSSA  /  A knot, a name in paper, a wage in bronze. Press them together while the bed is hot. Take this nameplate back to Nema.",
        {"knot": 1, "blank": 1, "wage": 1, "finished": 1},
        "token",
    ),
    step(
        "OSSA  /  Give me the lockkeeper’s knot, the archivist’s pay leaf and the foreman’s spare wage. Once the casting is finished I can press a permanent nameplate."
    ),
)

# Wrenfall is the open coastal approach from the resonator to the final bell.
flags.extend(["charter", "sounding", "leading", "distress", "landed"])
machine(
    "lampcode",
    ["signalBar"],
    ["bell", "wing", "star"],
    0,
    lambda state, op: (
        3
        if state == 3
        else state + 1
        if op == ("wing", "bell", "star")[state]
        else int(op == "wing")
    ),
    lambda state: (state,),
)
r = room(
    "Wrenfall",
    "Wrenfall Head",
    "Find Mirren at the chart shelter. A pilot cutter is waiting outside the reef.",
    "Wrenfall",
)
r.update(halfSpan=60, chapter="The Pilots’ Coast")
post(
    r,
    "Pilot",
    "Mirren, shore pilot",
    -4,
    -9,
    "person",
    step(
        "MIRREN  /  Tell the bell keeper who brought us in. All seven hands signed this page. Everyone who did the work gets a line.",
        {"landed": 1},
    ),
    step(
        "MIRREN  /  Draw a triangle on my chart. West is the tide chapel. East is the split stone. The watcher on the north bluff can read the cutter’s last lamp.",
        {"charter": 1},
    ),
    step(
        "MIRREN  /  The Linnet is carrying the last flood book. Her skipper can see our headland, but the guide lamps went out. Take my chart. I will meet her at the landing.",
        award="charter",
    ),
)
info(
    r,
    "Map",
    "Pilots’ field chart",
    0,
    -8,
    "Three soundings make a safe entry. Read the brass rubbing in the western chapel, sight the two posts at Split Stone to the east, and climb the northern lookout. Then signal from the eastern mast.",
)
post(
    r,
    "Depth",
    "Tide chapel rubbing",
    -40,
    -24,
    "rubbing",
    step(
        "A gull’s wing marks the full-flood line, above the drowned bell. Mirren’s cutter draws three fathoms. Open her passage with the WING flag.",
        {"charter": 1},
        "sounding",
    ),
    step(
        "A tide scale beside a worn footprint. The shore pilot can tell you whose draft to look for."
    ),
)
post(
    r,
    "Transit",
    "Split Stone transit",
    40,
    -4,
    "sight",
    step(
        "Look along the brass rail. The two ringed posts meet around the bell on the offshore rock. BELL is the second flag while the cutter crosses the bar.",
        {"charter": 1},
        "leading",
    ),
    step(
        "Two rings frame a distant mark. Find Mirren in the chart shelter to learn the pilot code."
    ),
)
post(
    r,
    "Lookout",
    "North bluff glass",
    -28,
    35,
    "scope",
    step(
        "Through the blue glass, the Linnet flashes the keeper’s star. STAR answers her and brings her into shelter. Raise the flags at the eastern mast.",
        {"charter": 1},
        "distress",
    ),
    step(
        "Someone left the scope trained on a cutter. The shore pilot knows her call sign."
    ),
)
for id, label, x, op in [
    ("Wing", "Swallowtail halyard", 23, "wing"),
    ("Bell", "Bell halyard", 27, "bell"),
    ("Star", "Star halyard", 31, "star"),
]:
    post(
        r,
        id,
        label,
        x,
        29,
        "halyard",
        step(
            "The Linnet has crossed the reef. Go to the stone landing.", {"landed": 1}
        ),
        step(
            "A shutter flashes from the cutter. She has acknowledged {signalBar} of three signals.",
            {"sounding": 1, "leading": 1, "distress": 1},
            move="lampcode." + op,
        ),
        step(
            "The shore pilot requires all three observations before you give a vessel the way. Check the chart."
        ),
    )
post(
    r,
    "Launch",
    "Harbour capstan",
    35,
    27,
    "winch",
    step(
        "The rescue line is fast. The pilot is waiting at the northern landing.",
        {"landed": 1},
    ),
    step(
        "The line pulls taut. The Linnet clears the last rock and ties up below the lantern. Seven people step ashore.",
        {"signalBar": 3},
        "landed",
    ),
    step(
        "The reef line cannot be hauled until the cutter acknowledges all three flags."
    ),
)
post(
    r,
    "Book",
    "Flood book landing",
    8,
    43,
    "landing",
    step(
        "SKIPPER ELIN  /  Seven of us. Seven signatures. Take our book to the bell and tell them a promise needs a crew.",
        {"landed": 1},
        to="@final",
    ),
    step("The berth is empty. Signal the cutter from the eastern mast."),
)
door(r, "Back", "Down to the resonator", -9, -13, "EchoRotunda")
for j in range(3):
    v(r, "Reading" + str(j), ["sounding", "leading", "distress"][j], "show")
for count in range(1, 4):
    v(r, "Hoist" + str(count), "signalBar", "show", match=count)
v(r, "Linnet", "landed", "voyage", amount=9)
v(r, "CrewAshore", "landed", "show")

for station in r["stations"]:
    if station["id"] == "A_Transit":
        station.update(
            sight="BellBearing",
            evidence="leading",
            direction="Look north along the brass rail. Center the gold bell beyond the two rings, then press E or trigger.",
        )
    if station["id"] == "A_Lookout":
        station.update(
            sight="StarBearing",
            evidence="distress",
            direction="Face the cutter beyond the northern bluff. Center the star above her sail, then press E or trigger.",
        )
for descriptor in rooms:
    for station in descriptor["stations"]:
        station["note"] = {
            "A_Roof": 0,
            "A_Oar": 1,
            "A_Mill": 2,
            "A_Reed": 3,
            "A_River": 0,
            "A_Forge": 1,
            "A_Sky": 2,
        }.get(station["id"], 2 if station["style"] == "person" else 0)
if __name__ == "__main__":
    (RES / "Underworks.json").write_text(
        json.dumps(
            dict(
                flags=flags,
                machines=machines,
                rooms=rooms,
                logTitle="The Linnet’s flood book",
                logEntry="Six salt-blurred names and Elin’s careful seventh. In the margin she wrote, “A bell can call for hands. It cannot promise on their behalf.”",
                logEndings=[
                    "Elin has signed for the night tide. Six lines stand open for volunteers.",
                    "Ina opens the pilots’ book to the last page. “Do you think Elin would teach me to steer?”",
                ],
            ),
            separators=(",", ":"),
        )
    )
