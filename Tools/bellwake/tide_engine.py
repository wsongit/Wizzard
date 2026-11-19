"""The Countertide Engine. Rules for a rotary headrace, coupled hauling drums, a mould crane and a signal loom."""

KEYS = ("DrumHouse", "ChainDock", "MouldLoft", "SignalLoom")
CHAPTER = "The Countertide Engine"
TOW = ((2, 1, 0), (0, 2, 2), (1, 1, 2), (2, 0, 1))
VESSELS = ("Cedar", "Rush", "Wick")
CARGO = ("the medical launch", "the orphaned cargo", "the lamp-oil lighter", "the night ferry")
# Each bit in a row names a raised thread. Left to right, their values are 1, 2, 4 and 8.
FLAGS = ((1, 3, 7, 15), (9, 6, 6, 9), (1, 2, 4, 8, 15), (15, 9, 9, 6, 0))
FLAGS_NAMED = ("First light", "Open channel", "Outbound pilot", "All hands home")
THREADS = ("Reed", "Gold", "Tide", "Ash")
# The small collar is first. The final assembly is a five-collar tuned bell mould.
LIFTS = (((0, 0, 0), 2), ((0, 1, 0, 2), 1), ((1, 0, 2, 0, 0), 2))
PLACES = ("West", "Centre", "East")


def tow_move(state, op):
    job, positions = state
    if job == len(TOW):
        return state
    if op == "seal":
        return (job + 1, positions) if positions == TOW[job] else state
    shifts = {"cedar": (1, 1, 0), "rush": (0, 1, 1), "wick": (1, 0, 1)}[op]
    return job, tuple((p + d) % 3 for p, d in zip(positions, shifts))


def crane_move(state, op):
    job, places, hook = state
    if job == len(LIFTS):
        return state
    if op == "seal":
        if not all(p == LIFTS[job][1] for p in places):
            return state
        return job + 1, LIFTS[job + 1][0] if job + 1 < len(LIFTS) else places, -1
    pier = PLACES.index(op)
    if hook < 0:
        return (job, places, pier) if pier in places else state
    if hook == pier:
        return job, places, -1
    disk = places.index(hook)
    if pier in places and places.index(pier) < disk:
        return state
    return job, places[:disk] + (pier,) + places[disk + 1 :], -1


def weave_move(state, op):
    flag, row, mask = state
    if flag == len(FLAGS):
        return state
    if op != "beat":
        return flag, row, mask ^ (1 << THREADS.index(op))
    if mask != FLAGS[flag][row]:
        return state
    if row + 1 < len(FLAGS[flag]):
        return flag, row + 1, mask
    return flag + 1, 0, mask


def add_engine(room, post, step, visual, machine):
    def hall(key, title, intro, theme):
        r = room(key, title, intro, theme)
        r["chapter"] = CHAPTER
        r["fog"] = ("#af9d83", "#a4c2b7", "#ad8e83", "#b5a7ad")[KEYS.index(key)]
        return r

    def station(r, id, label, x, y, kind, *rules):
        post(r, id, label, x, y, kind, *rules)
        if kind not in ("person", "lift"):
            r["stations"][-1]["camp"] = "Rest" + id

    def back(r):
        station(r, "Home", "Drum-house stair", -8, -10, "lift", step(to="DrumHouse"))

    machine(
        "distribution",
        ["drumBearing", "towOpen", "craneOpen", "loomOpen"],
        ["turn"],
        0,
        lambda n, op: (n + 1) % 3,
        lambda n: (n, *(int(i == n) for i in range(3))),
    )
    r = hall(
        KEYS[0],
        "The Drum House",
        "The spill crew once brought a town to safety here. Elin’s log names three deliveries left unfinished. Turn the drum to connect a gallery and finish the crew’s last watch.",
        "Countertide",
    )
    station(
        r,
        "Keeper",
        "Elin’s dispatch desk",
        -4,
        -6,
        "person",
        step(
            "ELIN  /  Bring the night ferry alongside, seat the five mould collars and fly the home signal. The final lift answers only when every crew is clear."
        ),
    )
    station(
        r,
        "Turn",
        "Index the headrace",
        0,
        -2,
        "index",
        step(
            "The drum rolls into its next stop. Follow the illuminated arch. The three stops run dock, foundry, loom.",
            move="distribution.turn",
        ),
    )
    for i, (id, key, label, x, y, sig) in enumerate(
        zip(
            ("Dock", "Crane", "Loom"),
            KEYS[1:],
            ("Chain dock", "Mould loft", "Signal loft"),
            (-10, 0, 10),
            (7, 12, 7),
            ("towOpen", "craneOpen", "loomOpen"),
        )
    ):
        station(
            r,
            id,
            label,
            x,
            y,
            "lift",
            step(to=key, when={sig: 1}),
            step("The waterwheel has disconnected this passage. Index the brass drum at the centre."),
        )
        visual(r, "ArchLamp" + str(i), sig, "show")
        visual(r, "Finished" + str(i), ("towJob", "craneJob", "loomFlag")[i], "show", match=(4, 3, 4)[i])
    for i in range(3):
        visual(r, "Order" + str(i), "drumBearing", "show", match=i)
    visual(r, "Drum", "drumBearing", "pointer")
    station(
        r,
        "Final",
        "Keeper’s ascent",
        6,
        -8,
        "lift",
        step(to="@final", when={"towJob": 4, "craneJob": 3, "loomFlag": 4}),
        step("The lift waits for the night ferry, the assembled bell mould and the home signal."),
    )
    station(r, "Back", "Coastal stair", -10, -11, "lift", step(to="Wrenfall"))
    r["goals"] = [
        step(
            "Dispatch tally   /   Four barge loads: {towJob}/4   •   Moulds: {craneJob}/3   •   Signal flags: {loomFlag}/4. The brass drum selects the open gallery."
        )
    ]
    r = hall(
        KEYS[1],
        "Chainwater Dock",
        "Three chain ferries share hauling drums. Match their berths to the dispatch order, then sound the manifest gong.",
        "Chainwater",
    )
    machine(
        "towlines",
        ["towJob", "berth0", "berth1", "berth2", "towReady"],
        ["cedar", "rush", "wick", "seal"],
        (0, (0, 0, 0)),
        tow_move,
        lambda s: (s[0], *s[1], int(s[0] < len(TOW) and s[1] == TOW[s[0]])),
    )
    station(
        r,
        "Talk",
        "Nell the lighterman",
        -5,
        -7,
        "person",
        step(
            "NELL  /  Each brass wheel draws two chains. After the third berth a boat rounds the loop to the first. Read cedar, rush, wick, from left to right. Watch the three lamps on the dispatch board."
        ),
    )
    for i, name in enumerate(VESSELS):
        station(
            r,
            name,
            name + " capstan",
            -5 + 5 * i,
            -1,
            "winch",
            step(
                ("Cedar and Rush", "Rush and Wick", "Wick and Cedar")[i]
                + " advance. The mooring drums now read {berth0}, {berth1}, {berth2}.",
                move="towlines." + name.lower(),
            ),
        )
        visual(r, "Ferry" + str(i), "berth" + str(i), "slide", 2.9)
    r["goals"] = []
    for j, target in enumerate(TOW):
        r["goals"].append(
            step(
                "Load "
                + str(j + 1)
                + " / "
                + CARGO[j]
                + ". Berths needed: "
                + ", ".join(map(str, target))
                + ". Current: {berth0}, {berth1}, {berth2}.",
                {"towJob": j},
            )
        )
        visual(r, "Order" + str(j), "towJob", "show", match=j)
    r["goals"].append(step("The night ferry has made fast. Report to the drum house."))
    station(
        r,
        "Seal",
        "Manifest gong",
        8,
        -5,
        "gong",
        step("Every boat is alongside. Nell has signed the log.", {"towJob": 4}),
        step(
            "Nell casts off the load and stamps the manifest. Loads entered: {towJob}/4.",
            {"towReady": 1},
            move="towlines.seal",
        ),
        step("One or more hulls are at the wrong berth. Read the order board before ringing."),
    )
    back(r)

    def crane_outputs(s):
        job, p, hook = s
        return (
            job,
            hook,
            int(job < len(LIFTS) and all(n == LIFTS[job][1] for n in p)),
            *(
                n
                for i in range(5)
                for n in (
                    p[i] if i < len(p) else 0,
                    sum(q == p[i] for q in p[i + 1 :]) if i < len(p) else 0,
                    int(i < len(p)),
                )
            ),
        )

    channels = ["craneJob", "hook", "craneReady"] + [
        tag + str(i) for i in range(5) for tag in ("tower", "tier", "castVisible")
    ]
    machine("moulds", channels, [*PLACES, "seal"], (0, LIFTS[0][0], -1), crane_move, crane_outputs)
    r = hall(
        KEYS[2],
        "The Mould Loft",
        "A travelling hook moves one bronze collar at a time. The three racks are the only safe place to put a collar down.",
        "Bronzeworks",
    )
    station(
        r,
        "Talk",
        "Ara the patternmaker",
        -5,
        -7,
        "person",
        step(
            "ARA  /  Touch a rack to hook its top collar, then touch another rack to lower it. A wider collar cannot sit on a smaller one. Touch the first rack again to release the hook."
        ),
    )
    for i, id in enumerate(PLACES):
        station(
            r,
            id,
            id + " rack",
            -5 + 5 * i,
            -1,
            "crane",
            step(
                "The hook answers the rack. A lit pennant marks the pickup. Only exposed collars can travel.",
                move="moulds." + id,
            ),
        )
        visual(r, "Hook" + str(i), "hook", "show", match=i)
    for i in range(5):
        visual(r, "Collar" + str(i), "tower" + str(i), "slide", 5)
        r["visuals"][-1].update(stack="tier" + str(i), rise=0.49, visibleSignal="castVisible" + str(i))
    r["goals"] = []
    for j, (start, dest) in enumerate(LIFTS):
        r["goals"].append(
            step(
                ("The handbell", "The harbour bell", "The flood bell")[j]
                + ": assemble all "
                + str(len(start))
                + " collars on the "
                + PLACES[dest].lower()
                + " rack, then pull the testing chain.",
                {"craneJob": j},
            )
        )
        visual(r, "Order" + str(j), "craneJob", "show", match=j)
    r["goals"].append(step("The five-piece flood-bell mould rings true. Return to Elin."))
    station(
        r,
        "Seal",
        "Testing chain",
        8,
        -5,
        "gong",
        step("Ara has signed the flood-bell casting.", {"craneJob": 3}),
        step(
            "A clear note carries through the loft. Ara enters the pattern in the flood book. Moulds passed: {craneJob}/3.",
            {"craneReady": 1},
            move="moulds.seal",
        ),
        step(
            "The witness mark is incomplete. Assemble the entire stack on the rack named on the pattern card."
        ),
    )
    back(r)

    def weave_outputs(s):
        f, row, mask = s
        return (
            f,
            row,
            int(f < len(FLAGS) and FLAGS[f][row] == mask),
            *(int(bool(mask & (1 << i))) for i in range(4)),
            *(int(f < len(FLAGS) and j < row) for j in range(5)),
            *(int(f > j) for j in range(4)),
        )

    machine(
        "weaving",
        [
            "loomFlag",
            "loomRow",
            "loomReady",
            *["warp" + str(i) for i in range(4)],
            *["woven" + str(i) for i in range(5)],
            *["sent" + str(i) for i in range(4)],
        ],
        [*THREADS, "beat"],
        (0, 0, 0),
        weave_move,
        weave_outputs,
    )
    r = hall(
        KEYS[3],
        "The Signal Loft",
        "Four coloured warps cross the pilot’s loom. Read the flag sampler from top to bottom. Set each row on the treadles before beating the shuttle.",
        "SignalCloth",
    )
    station(
        r,
        "Talk",
        "Wen the signal weaver",
        -6,
        -8,
        "person",
        step(
            "WEN  /  The four warps are reed, gold, tide and ash. A filled square means raise that colour. A hollow square means lower it. The lit knot marks the next row. The treadles keep their positions between rows."
        ),
    )
    for i, name in enumerate(THREADS):
        station(
            r,
            name,
            name + " treadle",
            -6 + i * 4,
            -1,
            "treadle",
            step(
                name + " changes shed. Reed {warp0} · Gold {warp1} · Tide {warp2} · Ash {warp3}.",
                move="weaving." + name,
            ),
        )
        visual(r, "Heddle" + str(i), "warp" + str(i), "lift", 0.7)
    r["goals"] = []
    for j, name in enumerate(FLAGS_NAMED):
        for row, mask in enumerate(FLAGS[j]):
            names = ", ".join(THREADS[i] for i in range(4) if mask & (1 << i)) or "none"
            r["goals"].append(
                step(
                    "“"
                    + name
                    + "” · row "
                    + str(row + 1)
                    + " of "
                    + str(len(FLAGS[j]))
                    + ". Raise "
                    + names
                    + ". Lower the other warps, then beat.",
                    {"loomFlag": j, "loomRow": row},
                )
            )
        visual(r, "Order" + str(j), "loomFlag", "show", match=j)
    r["goals"].append(step("All four pilot signals hang from the rafters. Return to Elin."))
    for i in range(5):
        visual(r, "Row" + str(i), "loomRow", "show", match=i)
        visual(r, "Cloth" + str(i), "woven" + str(i), "show")
    for i in range(4):
        visual(r, "Flag" + str(i), "sent" + str(i), "show")
    station(
        r,
        "Beat",
        "Beat the shuttle",
        8,
        -5,
        "gong",
        step("The home signal is flying.", {"loomFlag": 4}),
        step(
            "Wen passes the shuttle. Flags finished: {loomFlag}/4. Rows in the current flag: {loomRow}.",
            {"loomReady": 1},
            move="weaving.beat",
        ),
        step("The shuttle stops short. Match the raised warps to the lit row of the sampler."),
    )
    back(r)
