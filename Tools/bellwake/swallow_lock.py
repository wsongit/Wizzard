"""Fen's staircase lock. Four crossings use one persistent pair of lock chambers."""

KEY = "SwallowLock"
# West tide, east tide, loading chamber and crane mark. Boat direction alternates.
RUNS = (
    (
        0,
        3,
        1,
        1,
        "Mrs Brindle’s flour chest",
        "the baker",
        "Flour kept the south landing fed for nine days. The receipt records no charge.",
    ),
    (
        2,
        3,
        2,
        2,
        "Pella’s red midwife’s bag",
        "the midwife",
        "Pella’s bill lists a birth at the lock. Fen remembers hearing that child before the bell.",
    ),
    (
        2,
        4,
        1,
        3,
        "the school’s little reed organ",
        "the schoolmistress",
        "The organ lost its lowest reed in the flood. Its empty note became the silence in Ina’s song.",
    ),
    (
        0,
        4,
        2,
        1,
        "the night-watch tin",
        "the fourth hand",
        "Inside the tin is Ina’s dry watch slip. It says: ‘If I leave to fetch them, count me present.’",
    ),
)
OPS = ("head", "chain", "tail", "west", "east", "hook", "sign")
CHANNELS = (
    "voyageNo",
    "foreMark",
    "aftMark",
    "bargeBerth",
    "aboard",
    "westTide",
    "eastTide",
    "hullMark",
    "westClear",
    "middleClear",
    "eastClear",
    "atCrane",
    "atLanding",
    "canWest",
    "canEast",
    *("load" + str(i) for i in range(4)),
)


def readings(state):
    job, a, b, pos, loaded = state
    west, east, stop, mark, *_ = RUNS[min(job, 3)]
    levels = (west, a, b, east)
    return (
        job,
        a,
        b,
        pos,
        loaded,
        west,
        east,
        levels[pos],
        int(west == a),
        int(a == b),
        int(b == east),
        int(pos == stop and levels[pos] == mark),
        int(pos == (0 if job % 2 else 3)),
        int(pos > 0 and levels[pos] == levels[pos - 1]),
        int(pos < 3 and levels[pos] == levels[pos + 1]),
        *(int(loaded and job == i) for i in range(4)),
    )


def move(state, op):
    job, a, b, pos, loaded = state
    if job == len(RUNS):
        return state
    r = readings(state)
    if op == "head":
        a = min(4, a + 1)
    elif op == "chain" and a > 0 and b < 4:
        a, b = a - 1, b + 1
    elif op == "tail":
        b = max(0, b - 1)
    elif op == "west" and r[13]:
        pos -= 1
    elif op == "east" and r[14]:
        pos += 1
    elif op == "hook" and r[11]:
        loaded = 1
    elif op == "sign" and loaded and r[12]:
        job += 1
        loaded = 0
    return job, a, b, pos, loaded


def add(room, post, step, visual, machine, flags):
    flags.extend(("fenWatch", "namedRunner", "unnamedRunner"))
    machine("stairlock", CHANNELS, OPS, (0, 0, 0, 0, 0), move, readings)
    r = room(
        KEY,
        "Swallow Stair",
        "Fen’s lock has two working chambers. Four cargoes are still missing from the night book.",
        "SwallowWater",
    )
    r.update(middle=True, chapter="The four passages of the Swallow", fog="#c8c6ac")

    def station(id, title, x, y, kind, *rules):
        post(r, id, title, x, y, kind, *rules)
        r["stations"][-1]["camp"] = "Rest" + id

    station(
        "Fen",
        "Fen at the pilot house",
        -6,
        -11,
        "person",
        step(
            "FEN / We wrote down what the flood washed away. Nobody wrote down what we saved. Work the little Swallow through the stair for me. The brass board gives you the two tides, the crane and its loading mark. Read it before each crossing.",
            award="fenWatch",
        ),
    )
    station(
        "Sheet",
        "Night sailing board",
        0,
        -6.5,
        "board",
        *[
            step(
                f"Crossing {i + 1}. Take {name} from the {'fore' if stop == 1 else 'aft'} crane at mark {mark}. Deliver it to the {'west' if i % 2 else 'east'} landing. West tide {w}, east tide {e}.",
                {"voyageNo": i},
            )
            for i, (w, e, stop, mark, name, _, _) in enumerate(RUNS)
        ],
        step("The four cargoes are entered. Read Ina’s slip at the night desk."),
    )

    def command(id, title, x, y, before, line):
        station(
            id,
            title,
            x,
            y,
            "wheel",
            step("Take the watch from Fen first.", {"fenWatch": 0}),
            step("The Swallow is moored for morning.", {"voyageNo": 4}),
            *before,
            step(line, move="stairlock." + id.lower()),
        )

    command(
        "Head",
        "Headwater feed",
        -10,
        -1.5,
        [step("The fore chamber is already at its upper mark.", {"foreMark": 4})],
        "The fore chamber rises to {foreMark}.",
    )
    command(
        "Chain",
        "Bucket chain",
        0,
        -1.5,
        [
            step("The fore sump is empty. Open the headwater feed.", {"foreMark": 0}),
            step("The aft chamber is full. Open the tail sluice.", {"aftMark": 4}),
        ],
        "One measure moves from fore to aft. Fore {foreMark}, aft {aftMark}.",
    )
    command(
        "Tail",
        "Tailwater sluice",
        10,
        -1.5,
        [step("The aft chamber is already at its low mark.", {"aftMark": 0})],
        "The aft chamber falls to {aftMark}.",
    )
    command(
        "West",
        "Haul west",
        -14,
        -6.5,
        [
            step("The Swallow is at the west landing.", {"bargeBerth": 0}),
            step("The westward gate is shut. Match the water marks on its two sides.", {"canWest": 0}),
        ],
        "The little towboat passes west through the open gate.",
    )
    command(
        "East",
        "Haul east",
        14,
        -6.5,
        [
            step("The Swallow is at the east landing.", {"bargeBerth": 3}),
            step("The eastward gate is shut. Match the water marks on its two sides.", {"canEast": 0}),
        ],
        "The little towboat passes east through the open gate.",
    )
    station(
        "Hook",
        "Lower the cargo sling",
        0,
        12,
        "crane",
        step("Ask Fen for the watch.", {"fenWatch": 0}),
        step("The last cargo is ashore.", {"voyageNo": 4}),
        step("A load is already secured.", {"aboard": 1}),
        step(
            "Bring the empty boat under the crane named on the board and set that chamber to the loading mark.",
            {"atCrane": 0},
        ),
        *[
            step(
                "The sling settles " + run[4] + " onto the Swallow.",
                {"voyageNo": i},
                move="stairlock.hook",
            )
            for i, run in enumerate(RUNS)
        ],
    )
    station(
        "Sign",
        "Stamp the delivery",
        10,
        -12,
        "desk",
        step("All four receipts hang at the night desk.", {"voyageNo": 4}),
        step("The cargo sling is empty.", {"aboard": 0}),
        step("The Swallow must reach the landing opposite her departure.", {"atLanding": 0}),
        *[step(run[6], {"voyageNo": i}, move="stairlock.sign") for i, run in enumerate(RUNS)],
    )
    for id, x, title, flag, other, line in (
        (
            "Name",
            -8,
            "Enter Ina’s name",
            "namedRunner",
            "unnamedRunner",
            "Fen sets Ina’s name beside the fourth crossing.",
        ),
        (
            "Mark",
            8,
            "Keep the runner’s mark",
            "unnamedRunner",
            "namedRunner",
            "Fen copies the runner’s tiny swallow. The name stays hers to give.",
        ),
    ):
        station(
            id,
            title,
            x,
            13,
            "seal",
            step("Fen has already filed the night slip.", {other: 1}),
            step(line, {"voyageNo": 4}, award=flag),
            step("Four deliveries will open the night-watch tin."),
        )
    station(
        "Gate",
        "Glasscut towpath",
        14,
        14,
        "arch",
        step(to="@glasscut", when={"namedRunner": 1}),
        step(to="@glasscut", when={"unnamedRunner": 1}),
        step("Finish the four passages and file the night-watch slip."),
    )
    r["goals"] = [
        step("Fen has the night orders outside the pilot house.", {"fenWatch": 0}),
        step("Take the northeast towpath to Glasscut.", {"namedRunner": 1}),
        step("Take the northeast towpath to Glasscut.", {"unnamedRunner": 1}),
        step(
            "Read the night slip. File Ina by name or keep the runner’s swallow mark.", {"voyageNo": 4}
        ),
    ]
    for i, (_, _, stop, mark, title, *_) in enumerate(RUNS):
        r["goals"].extend(
            (
                step(
                    f"Deliver {title} to the {'west' if i % 2 else 'east'} landing, then stamp its receipt.",
                    {"voyageNo": i, "aboard": 1},
                ),
                step(
                    f"Collect {title} in the {'fore' if stop == 1 else 'aft'} chamber at mark {mark}. Read the sailing board for the tides.",
                    {"voyageNo": i},
                ),
            )
        )
    for i, signal in enumerate(("westTide", "foreMark", "aftMark", "eastTide")):
        visual(r, "Reach" + str(i), signal, "lift", amount=0.31)
    for i, signal in enumerate(("westClear", "middleClear", "eastClear")):
        visual(r, "GateLeaf" + str(i), signal, "lift", amount=2.8)
    for node, hide in (("Swallow", ""), *[(f"Cargo{i}", f"load{i}") for i in range(4)]):
        visual(r, node, "bargeBerth", "slide", amount=8)
        r["visuals"][-1].update(stack="hullMark", rise=0.31, visibleSignal=hide)
    for i in range(4):
        visual(r, "Order" + str(i), "voyageNo", "show", match=i)
    visual(r, "Slip", "voyageNo", "show", match=4)
