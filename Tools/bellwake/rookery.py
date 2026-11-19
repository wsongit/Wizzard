"""The rookery's apprentice, the three lost pilot birds and their working signals."""

KEY = "GlassRookery"
NAMES = ("Ferry", "Flume", "Kiln", "Reed", "Crossing", "Spindle", "Alder", "Lantern", "Crown")
POINTS = ((-22, -21), (0, -24), (23, -20), (-25, 0), (-1, 1), (25, 2), (-21, 23), (1, 25), (24, 23))
# Gates on a flight mean quiet water (0), running water (1), or either (-1).
# The last bird also needs a bright roost belonging to the open shutter bank.
COURSES = (
    (
        "Pip",
        "little grebe",
        0,
        8,
        (
            (0, 1, 0),
            (1, 4, 1),
            (4, 3, 1),
            (3, 6, 0),
            (6, 7, 1),
            (7, 8, 0),
            (1, 2, 0),
            (2, 5, 1),
            (5, 4, 0),
        ),
    ),
    (
        "Slate",
        "grey heron",
        2,
        6,
        (
            (2, 5, 1),
            (5, 8, 0),
            (8, 7, 0),
            (7, 4, 1),
            (4, 1, 0),
            (1, 0, 1),
            (0, 3, 0),
            (3, 6, 1),
            (5, 4, 1),
        ),
    ),
    (
        "Ash",
        "copper tern",
        6,
        2,
        ((6, 3, 0), (3, 4, 1), (4, 7, 1), (7, 8, 0), (8, 5, 1), (5, 2, 0), (4, 1, 0), (1, 2, 1)),
    ),
)
BANKS = (0, 1, 2, 1, 0, 2, 2, 0, 1)
OPS = tuple("p" + str(i) for i in range(9)) + ("water", "light", "launch")
CHANNELS = (
    "pilotNo",
    "birdAt",
    "weirMode",
    "lightBank",
    "nestReady",
    *("bird" + str(i) for i in range(3)),
    *("canCall" + str(i) for i in range(9)),
)


def connections(stage, pos, water, light):
    bird, kind, start, goal, edges = COURSES[min(stage, 2)]
    near = {}
    for a, b, w in edges:
        if a == pos:
            near[b] = w
        if b == pos:
            near[a] = w
    return [
        int(
            stage < 3
            and i in near
            and (near[i] < 0 or near[i] == water)
            and (stage != 2 or BANKS[i] == light)
        )
        for i in range(9)
    ]


def reading(s):
    stage, pos, water, light = s
    goal = COURSES[min(2, stage)][3]
    return (
        stage,
        pos,
        water,
        light,
        int(stage < 3 and pos == goal),
        *(int(stage == i) for i in range(3)),
        *connections(*s),
    )


def shift(s, op):
    stage, pos, w, l = s
    if stage == 3:
        return s
    if op == "water":
        w = 1 - w
    elif op == "light":
        l = (l + 1) % 3
    elif op == "launch":
        if pos == COURSES[stage][3]:
            stage += 1
            if stage < 3:
                pos = COURSES[stage][2]
    else:
        target = int(op[1:])
        if connections(*s)[target]:
            pos = target
    return stage, pos, w, l


def build(room, post, step, visual, machine, flags):
    flags.append("rookWarden")
    machine("pilots", CHANNELS, OPS, (0, 0, 0, 0), shift, reading)
    r = room(
        KEY,
        "The Glass Rookery",
        "A valley of glass-topped guideposts lies beyond the furnace. Three pilot birds have never flown their flood-night routes home.",
        "SwallowWater",
    )
    r.update(halfSpan=36, score="GlassPilots", chapter="The three missing pilots", fog="#b7c1b0")

    def st(id, label, x, y, style, *rules):
        post(r, id, label, x, y, style, *rules)
        r["stations"][-1]["camp"] = "Rest" + id
        return r["stations"][-1]

    st(
        "Keeper",
        "Orla, the roost keeper",
        -5,
        -11,
        "person",
        step(
            "ORLA / Ina sent us three messages in little reed tubes. The pilots still wait where the water stopped them. Take my whistle. Face a numbered perch and whistle with Q or left grip. A trigger or E also calls. Each bird has a different paper route. Look at the framed chart or open your journal. The water wheel changes the river’s voice; Ash also listens for the lit glass.",
            award="rookWarden",
        ),
    )
    st(
        "Chart",
        "Flight book",
        3,
        -12,
        "board",
        *[
            step(
                name
                + " the "
                + kind
                + " starts at "
                + NAMES[a]
                + ". Bring the bird to "
                + NAMES[b]
                + " and go to Orla’s sending desk. "
                + (
                    "Follow the solid blue and broken ochre routes on Pip’s chart."
                    if i == 0
                    else "Look at Slate’s routes on the centre chart."
                    if i == 1
                    else "Match the destination’s shutter letter before every call."
                ),
                {"pilotNo": i},
            )
            for i, (name, kind, a, b, _) in enumerate(COURSES)
        ],
        step("The route book now holds three signatures in Orla’s careful hand."),
    )
    st(
        "Water",
        "Turn the weir wheel",
        -12,
        2,
        "wheel",
        step(
            "The weir is open. The running streams answer the blue paths.",
            {"weirMode": 0},
            move="pilots.water",
        ),
        step("The weir shuts. The quiet streams answer the ochre paths.", move="pilots.water"),
    )
    st(
        "Light",
        "Turn the glass shutters",
        12,
        3,
        "wheel",
        *[
            step(
                "The shutter lantern lights bank " + "ABC"[(i + 1) % 3] + ".",
                {"lightBank": i},
                move="pilots.light",
            )
            for i in range(3)
        ],
    )
    for j, (name, (x, y)) in enumerate(zip(NAMES, POINTS)):
        rules = [
            step("Orla keeps the whistle at the south lodge.", {"rookWarden": 0}),
            step("The three birds have flown home.", {"pilotNo": 3}),
            step("The pilot is resting on this perch already.", {"birdAt": j}),
        ]
        for i, (bird, kind, a, b, edges) in enumerate(COURSES):
            rules.append(
                step(
                    bird + " follows the guide line to " + name + ".",
                    {"pilotNo": i, "canCall" + str(j): 1},
                    move="pilots.p" + str(j),
                )
            )
            if i == 2:
                for l in set(range(3)) - {BANKS[j]}:
                    rules.append(
                        step(
                            "Ash cannot see this glass. Set the lantern to bank "
                            + "ABC"[BANKS[j]]
                            + ".",
                            {"pilotNo": i, "lightBank": l},
                        )
                    )
            for a, b, w in edges:
                if j not in (a, b):
                    continue
                origin = b if a == j else a
                rules.append(
                    step(
                        "The flight is possible from "
                        + NAMES[origin]
                        + ", but it needs "
                        + ("running" if w else "quiet")
                        + " water.",
                        {"birdAt": origin, "pilotNo": i},
                    )
                )
        rules.append(
            step(
                "The bird cannot see this perch from its current roost. Follow a line on its flight chart."
            )
        )
        st("P" + str(j), name + " perch", x, y, "perch", *rules)
    narration = (
        "Pip flies low with a tube of bread tallies. Orla reads the message. ‘There are mouths at the school. Don’t close the east gate.’",
        "Slate’s paper is covered in wet thumbprints. ‘Four aboard. If anyone asks, the child makes five.’ Orla keeps her own thumb beside them.",
        "Ash carries no order. On the reed paper Ina drew her sister’s face, in case she forgot it. Orla rolls it up for Tavi.",
    )
    st(
        "Launch",
        "Open the home flight",
        3,
        12,
        "desk",
        step("All three pilots have found the old sky road.", {"pilotNo": 3}),
        *[step(narration[i], {"pilotNo": i, "nestReady": 1}, move="pilots.launch") for i in range(3)],
        step("Lead the pilot to the destination in the flight book before opening the home flight."),
    )
    st(
        "Gate",
        "The guild stair",
        16,
        16,
        "arch",
        step(to="SumpHall", when={"pilotNo": 3}),
        step("Orla is still waiting for the pilots. Read their flight book at the lodge."),
    )
    st(
        "Glasshouse",
        "Orla’s visitor ledger",
        8,
        25,
        "ledger",
        step(
            "Three marks in the guestbook: a webbed foot, a splayed claw, a little forked tail in ink. Orla has added, ‘All papers delivered.’",
            {"pilotNo": 3},
        ),
        step(
            "The last page smells of lamp oil. ‘Ash knows each bank by its own glass. If she cannot see her colour, she stays where the letter is safe.’",
            {"pilotNo": 2},
        ),
        step(
            "In the flood Orla hung one lamp in each window of this glasshouse. The pilots carried messages between families after the footbridges went."
        ),
    )
    r["goals"] = [
        step("Speak to Orla at the south lodge.", {"rookWarden": 0}),
        step("Take the paper birds’ messages down the guild stair.", {"pilotNo": 3}),
        step("Open the home flight at the sending desk.", {"nestReady": 1}),
    ]
    for i, (bird, kind, a, b, edges) in enumerate(COURSES):
        for j, title in enumerate(NAMES):
            r["goals"].append(
                step(
                    f"{bird}, the {kind}, waits at {title}. Lead the pilot to {NAMES[b]}. Call from a connecting perch. The flight book and water wheel are marked on your map.",
                    {"pilotNo": i, "birdAt": j},
                )
            )
    for i in range(3):
        visual(r, "Pilot" + str(i), "birdAt", "perch")
        r["visuals"][-1].update(visibleSignal="bird" + str(i), amount=1.8 + i * 0.25)
        visual(r, "Page" + str(i), "pilotNo", "show", match=i)
    visual(r, "Page3", "pilotNo", "show", match=3)
    for i in range(3):
        visual(r, "LanternBank" + str(i), "lightBank", "show", match=i)
    visual(r, "WeirLeaf", "weirMode", "lift", amount=1.18)
