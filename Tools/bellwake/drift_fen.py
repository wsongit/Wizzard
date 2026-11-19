"""Field orders and the lost property of Drift Fen."""

KEY = "DriftFen"
ITEMS = (
    (
        "flourRecovered",
        "Flour tally",
        -36,
        -26,
        "WEST BAKEHOUSE",
        "Look for the round oven beside the broken waterwheel. A tally fell where the bakers passed their chest over the sill.",
        "A bread paddle’s notch fits the tally. Brindle’s chest is still dry inside the shuttered oven. You mark it for Fen’s crew.",
    ),
    (
        "bagRecovered",
        "Pella’s clasp",
        39,
        -17,
        "EAST LAZARET",
        "Pella brought the newborns to the canvas hospital. Try the old washing frame outside its striped awning.",
        "A red clasp comes free of the washing frame. Pella tied her bag above the high-water line, in reach of anyone.",
    ),
    (
        "organRecovered",
        "The missing bass reed",
        31,
        37,
        "PENNY SCHOOL",
        "Look near the low side of the schoolhouse. The organ fell quiet before the water reached its keys.",
        "One brass tongue lies among the chalk slates. The bass reed is bent. Fen’s crew can move the organ without shaking its pipes loose.",
    ),
    (
        "watchRecovered",
        "Watchman’s key",
        -38,
        32,
        "WESTERN SIGNAL",
        "Follow the line of watch lamps to the signal tower. Someone dragged the tin out of the rain.",
        "The key is hooked through a mooring ring. A tin has been stowed under the bell bench. Ina left its key where small hands could find it.",
    ),
)


def add(rooms, room, post, step, flags):
    lock = next(r for r in rooms if r["key"] == "SwallowLock")
    flags.extend(["fenFork"] + [it[0] for it in ITEMS])
    post(lock, "FenRoad", "Drift Fen footpath", -16, -4, "arch", dict(step(to=KEY), arrival="RestGuide"))
    lock["stations"][-1]["camp"] = "RestFenRoad"
    hook = next(s for s in lock["stations"] if s["id"] == "A_Hook")
    guard = next(i for i, v in enumerate(hook["rules"]) if v["move"] == "stairlock.hook")
    for i, it in enumerate(ITEMS):
        hook["rules"].insert(
            guard + i,
            step(
                "The sling hangs empty. Search Drift Fen for the load. " + it[5],
                {"voyageNo": i, it[0]: 0},
            ),
        )
    goals = lock["goals"]
    for i, it in enumerate(ITEMS):
        j = next(j for j, g in enumerate(goals) if {"signal": "voyageNo", "value": i} in g["when"])
        goals.insert(
            j,
            step(
                "A cargo is missing. Take the western footpath to Drift Fen. " + it[5],
                {"voyageNo": i, it[0]: 0, "aboard": 0},
            ),
        )
    r = room(
        KEY,
        "Drift Fen",
        "The flood left four pieces of lost property across the old river valley. Willa keeps a sounding fork and a field sheet at the ferry.",
        "SwallowWater",
    )
    r.update(halfSpan=56, score="AlderFerry", middle=True, fog="#c3cbb1", chapter="Soundings in Drift Fen")

    def st(id, title, x, y, style, *rules):
        post(r, id, title, x, y, style, *rules)
        s = r["stations"][-1]
        s["camp"] = "Rest" + id
        return s

    st(
        "Guide",
        "Willa at the ferry",
        0,
        -13,
        "person",
        step(
            "WILLA / My fork sings back to metal under silt. Press Q or squeeze the left grip. Turn toward the answer. When the ground sings directly underneath you, look down and lift what you find. Fen will send a crew for the heavy things.",
            award="fenFork",
        ),
    )
    st(
        "Map",
        "Fen field sheet",
        6,
        -12,
        "board",
        step(
            "North beyond the alder stream: the signal tower and Penny school. South: Brindle’s oven in the west, Pella’s canvas hospital in the east. The journal carries this map."
        ),
    )
    st(
        "Home",
        "Back to Swallow Stair",
        -7,
        -19,
        "arch",
        dict(step(to="SwallowLock"), arrival="RestFenRoad"),
    )
    for i, (flag, title, x, y, site, hint, receipt) in enumerate(ITEMS):
        st(
            "Find" + str(i),
            title,
            x,
            y,
            "search",
            step("Ask Willa for her sounding fork.", {"fenFork": 0}),
            step(receipt, award=flag),
        ).update(search="Cache" + str(i), evidence=flag)
        st(
            "Story" + str(i),
            ("The oven ledger", "The washing frame", "Children’s slates", "The night signal")[i],
            x + 4,
            y - 2,
            "tablet",
            step(
                (
                    "BRINDLE / The watch sent twenty sacks. I baked them all. Anybody asking for a receipt can count the children instead.",
                    "PELLA / Three cradles. Four slings. One left hand free to hold the tiller. If a child makes a sound, mark it down as a song.",
                    "PENNY SCHOOL / Four names written up for music. A fifth, INA, has been added in a small hand halfway down the board.",
                    "NIGHT ORDERS / One long bell for the upper village. Two short bells for the fen. When both sound together, bring everybody.",
                )[i]
                + " "
                + hint
            ),
        )
    r["goals"] = [
        step("Willa at the ferry has a sounding fork for you.", {"fenFork": 0}),
        step(
            "All four loads are marked. Bring Fen’s boat to each working crane.",
            {it[0]: 1 for it in ITEMS},
        ),
    ]
    r["goals"] += [step(it[5], {it[0]: 0}) for it in ITEMS]
