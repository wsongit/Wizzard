"""Tavi's opening chapter, a paper theatre reconstructed from four objects the sisters kept."""

KEY = "PaperCourt"
CAST = ("Tavi", "Ina", "Marn the ferryman")
PLACES = ("the workshop", "the lock", "the ferry")
PROPS = ("the hinge pin", "the lantern", "the bell")
ACTS = (
    (
        "Pattern",
        "Tavi’s casting pattern",
        -10,
        -6,
        (0, 0, 2),
        "The carving fits a child's palm. TAVI / I made this little bell in our workshop before there was a bell tower. Ina said she could hear the casting hiss before I poured it.",
        "A red-aproned child lifts her first bell. Another girl listens through the workshop door.",
    ),
    (
        "Log",
        "Marn’s night log",
        10,
        -5,
        (2, 2, 1),
        "In the log Marn drew his ferry loaded with families. A lantern hangs from his free hand. ‘The roof lamps were out. Mine was the only light on the crossing.’",
        "Marn holds the lantern over a crowded ferry. Three children in the painted boat stand on tiptoe to see the bank.",
    ),
    (
        "Boot",
        "Ina’s river boot",
        -11,
        7,
        (1, 1, 0),
        "Something rattles under the insole. TAVI / Ina kept the hinge pin from the lock. The big iron wheel broke loose that night. She held the gate on its hinge until Marn got through.",
        "Ina kneels in the water at the lock. The first ferry clears the open gate. Her boot is still on the stone.",
    ),
    (
        "Carbon",
        "The second receipt",
        11,
        8,
        (1, 0, 2),
        "Hold the thin paper to the light. ‘One voice lent to the bell in the workshop, until morning.’ Ina signed the bottom. The grey smudge beside it is Tavi’s thumb.",
        "Ina puts her ear against the bronze in the workshop. Tavi puts her hand over her sister’s. Only one of them can hear the answer.",
    ),
)
INVITATION = "TAVI / My sister and I made a paper theatre behind the market. I crossed her out of the play after the flood. Before I ask anything of you, I want you to see what happened. Take the blue courtyard door beside my stall."
CADENCES = ("021", "210", "101", "0120")
CREDITS = (
    "I kept the programme. ‘Ina, bellmender.’ People thought I made that bell on my own.",
    "I kept the programme. ‘Ina, lock runner.’ Now when the children put on the play, somebody has to run.",
)


def operate(state, op):
    act, who, where, what, credit = state
    if act == 4:
        if not credit and op in ("maker", "runner"):
            return act, who, where, what, 1 if op == "maker" else 2
        return state
    if op == "project" and (who, where, what) == ACTS[act][4]:
        return act + 1, who, where, what, credit
    if op == "figure":
        who = (who + 1) % 3
    elif op == "place":
        where = (where + 1) % 3
    elif op == "prop":
        what = (what + 1) % 3
    return act, who, where, what, credit


def build(room, post, step, visual, machine, flags):
    machine(
        "paperstage",
        [
            "paperAct",
            "paperActor",
            "paperPlace",
            "paperProp",
            "paperCredit",
            "paperReady",
            *["paperPlayed" + str(i) for i in range(4)],
        ],
        ["figure", "place", "prop", "project", "maker", "runner"],
        (0, 1, 0, 0, 0),
        operate,
        lambda s: (*s, int(s[0] < 4 and s[1:4] == ACTS[s[0]][4]), *(int(s[0] > i) for i in range(4))),
    )
    r = room(
        KEY,
        "Tavi’s Paper Theatre",
        "Tavi leads you into a courtyard behind the market. The toy theatre she built with her sister still has four scenes, but someone has changed the story.",
        "PaperLight",
    )
    r.update(chapter="Before the first bell", prologue=True, fog="#decba5")

    def station(id, label, x, y, style, *rules):
        post(r, id, label, x, y, style, *rules)
        r["stations"][-1]["camp"] = "Rest" + id

    station(
        "Talk",
        "Tavi at the playhouse",
        -5,
        -8,
        "person",
        step(
            "TAVI / I wrote that play when the flood was fresh. I was afraid of what the neighbours would think of Ina. Will you help me put her back in it? Read the first keepsake, choose a figure, a place and a prop, then light the stage."
        ),
    )
    for index, (id, label, x, y, choices, testimony, scene) in enumerate(ACTS):
        flag = "paper" + id
        flags.append(flag)
        station(id, label, x, y, "relic", step(testimony, award=flag))
    for index, (id, label, x, items, channel) in enumerate(
        (
            ("Figure", "Figure reel", -3.6, CAST, "paperActor"),
            ("Place", "Scenery reel", 0, PLACES, "paperPlace"),
            ("Prop", "Property reel", 3.6, PROPS, "paperProp"),
        )
    ):
        station(
            id,
            label,
            x,
            0.2,
            "reel",
            step("The four scenes are on the programme. Choose how to credit Ina.", {"paperAct": 4}),
            *[
                step(
                    "On stage: " + items[(j + 1) % 3] + ".",
                    {channel: j},
                    move="paperstage." + id.lower(),
                )
                for j in range(3)
            ],
        )
        for j in range(3):
            visual(r, id + str(j), channel, "show", match=j)
        visual(r, "Spool" + id, channel, "tilt", amount=120)
    rules = []
    goals = []
    for j, (id, label, x, y, choices, testimony, scene) in enumerate(ACTS):
        flag = "paper" + id
        rules += [
            step(
                "Scene " + str(j + 1) + " / " + scene,
                {"paperAct": j, flag: 1, "paperReady": 1},
                move="paperstage.project",
            ),
            step(
                "Read " + label + " first. Tavi wants a witness for this scene.",
                {"paperAct": j, flag: 0},
            ),
            step("The shadows tell a different story. " + testimony, {"paperAct": j}),
        ]
        goals += [
            step("Scene " + str(j + 1) + " of four. Examine " + label + ".", {"paperAct": j, flag: 0}),
            step(
                "Scene " + str(j + 1) + " of four. " + testimony + " Set the reels and light the stage.",
                {"paperAct": j},
            ),
        ]
    station(
        "Light",
        "Light the stage",
        -3.6,
        -3.7,
        "lamp",
        *rules,
        step("All four scenes have been printed. The programme desk is at the east wing."),
    )
    for j in range(4):
        visual(r, "Playbill" + str(j), "paperAct", "show", match=j)
    for i in range(3):
        visual(r, "PuppetArm" + str(i), "paperActor", "show", match=i)
    for i in range(4):
        visual(r, "LitShell" + str(i), "paperPlayed" + str(i), "show")
    for i, id in enumerate(("Maker", "Runner")):
        label = ("Ina, bellmender", "Ina, lock runner")[i]
        station(
            id,
            label,
            6.9 + 2.65 * i,
            2,
            "credit",
            step("Tavi folds the programme and puts it in her pocket.", {"paperCredit": i + 1}),
            step("The programme has already gone to print.", {"paperCredit": 2 - i}),
            step("TAVI / " + CREDITS[i], {"paperAct": 4}, move="paperstage." + id.lower()),
            step("Make the four scenes before signing the programme."),
        )
    station("Door", "Return to the market", -8, -12, "lift", step(to="@market"))
    r["goals"] = goals + [
        step("The play is complete. Choose a credit for Ina at the programme desk.", {"paperCredit": 0}),
        step("Take the courtyard gate back to the market. Tavi has a commission for you."),
    ]
    return CREDITS
