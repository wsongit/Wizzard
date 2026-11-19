"""Survey three lost addresses across the ebb and flood, then restore their titles in the map office."""

LOW, HIGH, OFFICE = "SillwaterEbb", "SillwaterFlood", "SillwaterOffice"
PLACES = ("The Oar House", "The school at Penny Reach", "The bell lock")
PINS = ((1, 3), (4, 2), (2, 4))
PITCH = 19
SITES = (
    (("Willow", "Willow landing", -43, -27), ("Vestry", "Vestry landing", 11, 45)),
    (("Crane", "Quarry crane", 34, 27), ("Orchard", "Pear tree jetty", -40, 35)),
    (("Net", "Net menders’ quay", -44, 7), ("Market", "Floating market", 45, -21)),
)
SYMBOLS = (
    "the white oar on the boatwright’s roof",
    "the brass sun over the schoolhouse",
    "the forked key on the old lock crane",
)
LINES = (
    "The Oar House. Three families slept over the boat shed. Ada inks in a front door where the toll map showed open water.",
    "The school at Penny Reach. ‘There was a school here,’ says Ada. ‘There were fourteen names on the last roll.’ She rules the lane back in.",
    "The bell lock. Someone cut its ropes on the night of the flood, but the lock runner stayed. Ada leaves room for a witness to sign.",
)


def plot(state, op):
    job, col, row = state
    if job == 3:
        return state
    if op == "stamp" and (col, row) == PINS[job]:
        return (job + 1, 2, 2)
    return (
        job,
        max(0, min(4, col + (op == "east") - (op == "west"))),
        max(0, min(4, row + (op == "north") - (op == "south"))),
    )


def build(room, post, step, visual, machine, flags):
    flags.extend(
        [
            "parishWarrant",
            *["fix" + s[0] for pair in SITES for s in pair],
            "parishSigned",
        ]
    )
    machine(
        "parishplot",
        [
            "parishJob",
            "parishCol",
            "parishRow",
            "parishReady",
            *["entered" + str(i) for i in range(3)],
        ],
        ["east", "west", "north", "south", "stamp"],
        (0, 2, 2),
        plot,
        lambda s: (
            *s,
            int(s[0] < 3 and s[1:] == PINS[s[0]]),
            *[int(s[0] > i) for i in range(3)],
        ),
    )

    def station(r, id, label, x, y, style, *rules):
        post(r, id, label, x, y, style, *rules)
        r["stations"][-1]["camp"] = "Rest" + id

    def transfer(to, at):
        return {**step(to=to), "arrival": at}

    def room_for(key, label, description, theme, fog, span):
        r = room(key, label, description, theme)
        r.update(
            middle=True, chapter="Three houses of Sillwater", fog=fog, halfSpan=span
        )
        return r

    for side, key in enumerate((LOW, HIGH)):
        other = (HIGH, LOW)[side]
        r = room_for(
            key,
            ("Sillwater at Ebb", "Sillwater at Flood")[side],
            "The toll map has lost three addresses. Ada needs two lines of sight for each one, one at ebb and one at flood.",
            ("SaltMud", "SillRain")[side],
            ("#c3c1a0", "#aebdc1")[side],
            60,
        )
        station(
            r,
            "Ada",
            "Ada the parish clerk",
            -5,
            -15,
            "person",
            step(
                "ADA / The parish is in the book. Take the signed map to Fen at Reedwater.",
                {"parishSigned": 1},
            ),
            step(
                "ADA / The old toll map turned our homes into blue ink. Your witness book carries my field sheet. Look through three stands at ebb, three at flood. Join each pair of bearings on the office chart. Pull a tide bell to cross between tides.",
                award="parishWarrant",
            ),
        )
        for j, (id, x, y) in enumerate((("South", -10, -10), ("North", 26, 40))):
            landing = "Rest" + id
            station(
                r,
                id,
                ("South tide bell", "North tide bell")[j],
                x,
                y,
                "tidebell",
                {
                    **transfer(other, landing),
                    "when": [dict(signal="parishWarrant", value=1)],
                },
                step("Ask Ada at the southern landing for the parish warrant first."),
            )
        for j, pair in enumerate(SITES):
            id, label, x, y = pair[side]
            station(
                r,
                id,
                label,
                x,
                y,
                "sight",
                step(
                    "Your bearing from "
                    + label
                    + " is ruled onto office chart "
                    + str(j + 1)
                    + ".",
                    {"parishWarrant": 1},
                    award="fix" + id,
                ),
                step(
                    "Ada carries the survey warrant. Find her by the southern landing."
                ),
            )
            r["stations"][-1].update(
                sight="Target" + str(j),
                prime="parishWarrant",
                evidence="fix" + id,
                direction="Stay beside the stand. Look along its brass barrel and centre "
                + SYMBOLS[j]
                + ". Press the trigger or E to record the line.",
            )
            visual(r, "Stamped" + id, "fix" + id, "show")
        station(
            r,
            "Office",
            "Parish map office",
            6,
            -19,
            "office",
            transfer(OFFICE, "RestDoor" + str(side)),
        )
        station(
            r,
            "Gate",
            "Reedwater towpath",
            39,
            45,
            "exit",
            step(to="@reedwater", when={"parishSigned": 1}),
            step(
                "The towpath needs Ada’s signed map. Plot three houses in the parish office and seal the map."
            ),
        )
        r["goals"] = [
            step("Speak to Ada beside the southern landing.", {"parishWarrant": 0}),
            step(
                "The parish map is signed. Take the northeast towpath to Reedwater.",
                {"parishSigned": 1},
            ),
        ]
        for j, pair in enumerate(SITES):
            id, label, x, y = pair[side]
            r["goals"].append(
                step(
                    "Find " + label + " and sight " + SYMBOLS[j] + ".", {"fix" + id: 0}
                )
            )
        r["goals"].append(
            step(
                "The three local bearings are in your book. Ring a tide bell for the opposite shore, or return to the map office."
            )
        )
    r = room_for(
        OFFICE,
        "The Parish Map Office",
        "Ada’s chart is ruled in five columns and five rows. The six field stands send paired lines to this board. Move the brass pin to their intersection.",
        "ParishInk",
        "#b6b09b",
        20,
    )
    station(
        r,
        "Clerk",
        "The registrar",
        -6,
        -7,
        "person",
        step(
            "REGISTRAR / Columns run west to east, rows south to north. The garnet thread comes from the ebb survey, the blue from flood. Put the pin where those two threads cross. You can gather bearings in any order."
        ),
    )
    for id, label, x, y in (
        ("West", "West", -3, -1.4),
        ("East", "East", 3, -1.4),
        ("North", "North", 0, 1),
        ("South", "South", 0, -3.7),
    ):
        station(
            r,
            id,
            label + " carriage",
            x,
            y,
            "handle",
            step("The three addresses are in the ledger.", {"parishJob": 3}),
            step(
                "Pin carriage: west to east {parishCol}, south to north {parishRow}. The corner origin is zero.",
                move="parishplot." + id.lower(),
            ),
        )
    station(
        r,
        "Stamp",
        "Register this address",
        6,
        1,
        "press",
        *[
            step(
                LINES[j],
                {
                    "parishJob": j,
                    "parishReady": 1,
                    **{"fix" + s[0]: 1 for s in SITES[j]},
                },
                move="parishplot.stamp",
            )
            for j in range(3)
        ],
        step(
            "All three landings are entered. Sign the map at the seal desk.",
            {"parishJob": 3},
        ),
        step(
            "The pin needs both bearings for the current house, at their exact intersection."
        ),
    )
    station(
        r,
        "Seal",
        "Seal the parish map",
        -7,
        3,
        "seal",
        step(
            "Ada presses the parish seal into green wax. A lock runner’s line appears on the towpath to Reedwater.",
            {"parishJob": 3},
            award="parishSigned",
        ),
        step(
            "Three addresses must be entered before the parish seal can go on the map."
        ),
    )
    for j, key in enumerate((LOW, HIGH)):
        station(
            r,
            "Door" + str(j),
            ("Ebb landing", "Flood landing")[j],
            -7 + j * 14,
            -11,
            "office",
            transfer(key, "RestOffice"),
        )
    # Each line is visible only in the folio it belongs to, after the corresponding field sighting.
    for j in range(3):
        visual(r, "Folio" + str(j), "parishJob", "show", match=j)
        for side, site in enumerate(SITES[j]):
            visual(r, "Thread" + str(j) + str(side), "parishJob", "show", match=j)
            r["visuals"][-1]["visibleSignal"] = "fix" + site[0]
        visual(r, "Plaque" + str(j), "entered" + str(j), "show")
    visual(r, "MapPin", "parishCol", "slide", amount=1.52)
    r["visuals"][-1].update(stack="parishRow", rise=1.045)
    r["goals"] = [
        step(
            "Go back to either shore and take the northeast towpath to Reedwater.",
            {"parishSigned": 1},
        ),
        step(
            "All three houses are in the ledger. Stamp the parish seal.",
            {"parishJob": 3},
        ),
    ]
    for j, pair in enumerate(SITES):
        for side, site in enumerate(pair):
            r["goals"].append(
                step(
                    PLACES[j]
                    + ". Record the "
                    + ("ebb", "flood")[side]
                    + " bearing at "
                    + site[1]
                    + ".",
                    {"parishJob": j, "fix" + site[0]: 0},
                )
            )
        r["goals"].append(
            step(
                PLACES[j]
                + ". Find the crossing of the red and blue threads on the wall chart. Place the pin there and stamp the ledger.",
                {"parishJob": j},
            )
        )
