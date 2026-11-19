"""Three instrument makers left six listening horns in Rowan Hollow after the flood."""

KEY = "RowanHollow"
SITES = {
    "Rain": (-33, 28),
    "Root": (35, 28),
    "Wren": (10, -34),
}
EARS = {
    "Rain": ((-37, -8), (0, 22)),
    "Root": ((-6, 32), (35, -10)),
    "Wren": ((-21, -28), (24, 4)),
}
NAMES = {"Rain": "the spring harp", "Root": "the hollow beech", "Wren": "the kite loft"}
TAGS = {"Rain": "Spring", "Root": "Beech", "Wren": "Loft"}
ROOT_TUNE = "2102"
WEIGHTS = (2, 4, 3)


def rain(state, op):
    a, b, fixed = state
    if fixed:
        return state
    if op == "ridge":
        a = (a + 1) % 3
    if op == "sill":
        b = (b + 1) % 3
    return a, b, int(op == "spill" and (a, b) == (2, 1))


def drum(state, op):
    if state == len(ROOT_TUNE):
        return state
    trial = ROOT_TUNE[:state] + op
    return max(n for n in range(len(ROOT_TUNE) + 1) if trial.endswith(ROOT_TUNE[:n]))


def weigh(state, op):
    bird, arm = state
    if bird == 3:
        return state
    if op == "slide":
        return bird, 1 + arm % 4
    return (bird + 1, arm) if arm == WEIGHTS[bird] else state


def build(room, post, step, visual, machine, flags):
    flags.extend(
        ["woodBook"]
        + ["heard" + family + side for family in SITES for side in ("West", "East")]
    )
    machine(
        "springharp",
        ["ridgeCut", "sillCut", "rainMended"],
        ["ridge", "sill", "spill"],
        (0, 0, 0),
        rain,
        lambda s: s,
    )
    machine(
        "beechdrum",
        ["drumBeat", "rootMended"],
        list("012"),
        0,
        drum,
        lambda n: (n, int(n == 4)),
    )
    machine(
        "kitevoice",
        ["birdLoads", "poise", "loadOffset", "wrenMended"],
        ["slide", "weigh"],
        (0, 1),
        weigh,
        lambda s: (*s, 0 if s[0] == 3 else s[1] - WEIGHTS[s[0]], int(s[0] == 3)),
    )
    r = room(
        KEY,
        "Rowan Hollow",
        "For twelve winters the forest has sounded one chord short. In the sawyer’s hut, Linn still keeps the field book for three broken instruments.",
        "RootChoir",
    )
    r.update(halfSpan=52, chapter="The listening wood", fog="#a7b999", homeRoom=1)

    def st(id, title, xy, kind, *rules):
        post(r, id, title, *xy, kind, *rules)
        s = r["stations"][-1]
        s["camp"] = "Rest" + id
        return s

    st(
        "Linn",
        "Linn’s field book",
        (-3, -12),
        "book",
        step(
            "LINN / There. You can hear the three works from the school again. Ina used to knock the door in time with the beech. We left it on the latch for her. At the north wicket, listen for rain, root, then wren.",
            {"rainMended": 1, "rootMended": 1, "wrenMended": 1},
        ),
        step(
            "LINN / We used to hear them from the school. Listen at both horns of each kind. Stay by the horn and turn your head until the call is straight ahead. Mark both bearings and visit the instrument between them. My map is in your witness book.",
            award="woodBook",
        ),
    )
    st(
        "Plan",
        "Map of the three listening walks",
        (4, -9),
        "map",
        step(
            "Two rain cups hear running water, two root horns hear struck timber and two wren horns hear the little air organ. Your book rules a line for each bearing you take. The three walks cross at the hut."
        ),
    )
    for family, pair in EARS.items():
        for side, xy in zip(("West", "East"), pair):
            key = family + side
            flag = "heard" + key
            ear = st(
                key,
                family + " horn · " + side.lower() + " walk",
                xy,
                "ear",
                step(
                    "This bearing is already on the linen. Follow it toward "
                    + NAMES[family]
                    + ".",
                    {flag: 1},
                ),
                step(
                    "You pin the "
                    + family.lower()
                    + " thread on the field map. The second horn’s line will cross it at the instrument.",
                    {"woodBook": 1},
                    award=flag,
                ),
                step("Linn keeps the survey linen at the sawyer’s hut."),
            )
            ear.update(
                sight="Source" + family,
                prime="woodBook",
                evidence=flag,
                call=family + "WoodCall",
                direction="Keep your feet at the horn. Turn toward the call and use the trigger or E again to mark its direction.",
            )

    def confirmed(family):
        return {"heard" + family + "East": 1, "heard" + family + "West": 1}

    def needs(family):
        return step(
            "The two "
            + family.lower()
            + " horns will tell you which sound belongs here. Mark both bearings first."
        )

    for id, title, xy, text in [
        (
            "Ridge",
            "High watercourse",
            (-35, 28),
            "Each click turns the upper trough. Its two cut rings face the harp.",
        ),
        (
            "Sill",
            "Low watercourse",
            (-30, 28),
            "The lower lip turns. Its single-cut end feeds the brass mouth below.",
        ),
        (
            "Spill",
            "Spring harp sluice",
            (-33, 25),
            "The sill spills over the stones. Match the upper trough to mark II and the lower to I, then lift again.",
        ),
    ]:
        rules = [step("The spring is singing again.", {"rainMended": 1})]
        if id == "Spill":
            rules.append(
                step(
                    "Water crosses both gutters. A brass tongue rises in the little harp. Linn’s mother made this call for the ferryman who could never see her window.",
                    {**confirmed("Rain"), "ridgeCut": 2, "sillCut": 1},
                    move="springharp.spill",
                )
            )
        rules.extend(
            [
                step(text, confirmed("Rain"), move="springharp." + id.lower()),
                needs("Rain"),
            ]
        )
        st(id, title, xy, "water", *rules)
    visual(r, "RidgeTrough", "ridgeCut", "turn", amount=120)
    visual(r, "SillTrough", "sillCut", "turn", amount=120)
    visual(r, "SpringStream", "rainMended", "show")
    st(
        "Bark",
        "The beech stave",
        (33, 24),
        "bark",
        step(
            "LINN / I could always tell my father’s hands. High, middle, low, high. Three hollow lengths of wood. The shortest sings highest.",
            confirmed("Root"),
        ),
        needs("Root"),
    )
    for i, (dx, n) in enumerate(((-3, "Long"), (0, "Middle"), (3, "Short"))):
        s = st(
            n,
            n + " beech drum",
            (35 + dx, 28),
            "drum",
            step("All four knocks ring under the roots.", {"rootMended": 1}),
            *(
                [
                    step(
                        "High, middle, low, high. The hollow beech carries your last knock across the valley. Linn used to hear those four notes from her father’s workshop.",
                        {**confirmed("Root"), "drumBeat": 3},
                        move="beechdrum.2",
                    )
                ]
                if i == 2
                else []
            ),
            step(
                "The beech answers your hand.",
                confirmed("Root"),
                move="beechdrum." + str(i),
            ),
            needs("Root"),
        )
        s["note"] = 2 - i
    visual(r, "BeechRibbon", "rootMended", "show")
    st(
        "Slide",
        "Move the loft counterweight",
        (8, -34),
        "scale",
        step("The kite reeds have found their balance.", {"wrenMended": 1}),
        step(
            "You slide the bronze poise to the next notch. The pointer rises when the poise outweighs the bird.",
            confirmed("Wren"),
            move="kitevoice.slide",
        ),
        needs("Wren"),
    )
    rules = [
        step(
            "The last bird sings clear. Three clay throats together make the wren that once called Ina in for supper.",
            {"wrenMended": 1},
        )
    ]
    for b, a in enumerate(WEIGHTS):
        rules.append(
            step(
                [
                    "The first bird whistles low. Linn lowers the second, with the broad clay belly.",
                    "The second whistles clear. The third bird has a narrow tail and a chipped crest.",
                    "All three reeds sing. The tiniest clay bird was Ina’s. Linn mended its tail with a penny’s worth of brass.",
                ][b],
                {**confirmed("Wren"), "birdLoads": b, "poise": a},
                move="kitevoice.weigh",
            )
        )
    st(
        "Breath",
        "Sound the balanced reed",
        (12, -34),
        "scale",
        *rules,
        step(
            "The air escapes. Slide the poise until the beam lies level, then draw the bellows.",
            confirmed("Wren"),
        ),
        needs("Wren"),
    )
    visual(r, "LoftBeam", "loadOffset", "tilt", amount=9)
    visual(r, "Poise", "poise", "slide", amount=0.32)
    for i in range(3):
        visual(r, "Bird" + str(i), "birdLoads", "show", match=i)
        r["visuals"][-1]["mount"] = "LoftBeam"
    visual(r, "WrenBanner", "wrenMended", "show")
    won = {"rainMended": 1, "rootMended": 1, "wrenMended": 1}
    st(
        "Gate",
        "Root Choir wicket",
        (0, 43),
        "gate",
        step(to="@choir", when=won),
        step(
            "Listen. Three voices should carry through the wicket. Your field book will tell you which is missing."
        ),
    )
    # Each repaired voice changes the next entry in Linn’s book.
    r["goals"] = [
        step(
            "Meet Linn at the sawyer’s hut and take the listening linen.",
            {"woodBook": 0},
        )
    ]
    for family in SITES:
        for side in ("West", "East"):
            r["goals"].append(
                step(
                    "Find the "
                    + family.lower()
                    + " horn on the "
                    + side.lower()
                    + " walk and take a bearing. The field map shows both walks.",
                    {"heard" + family + side: 0},
                )
            )
        r["goals"].append(
            step(
                "Follow the two "
                + family.lower()
                + " bearings to "
                + NAMES[family]
                + " and restore its voice.",
                {family.lower() + "Mended": 0},
            )
        )
    r["goals"].append(
        step(
            "Rain, root and wren are sounding. Go to the north wicket to enter the Root Choir."
        )
    )
