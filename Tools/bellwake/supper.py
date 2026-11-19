"""The optional shore kitchen, a shared tune left on three objects from the night watch."""

FRAGMENTS = (
    ("ChainDock", "tinVoice", "Nell’s lunch tin", "202", "Low · High · Low"),
    ("MouldLoft", "cupVoice", "Ara’s measuring cups", "110", "Middle · Middle · High"),
    ("SignalLoom", "clothVoice", "Wen’s tea cloth", "021", "High · Low · Middle"),
)
TUNE = "".join(f[3] for f in FRAGMENTS)
NAMES = ("High", "Middle", "Low")


def note_played(progress, note):
    if progress == len(TUNE):
        return progress
    digit = str(NAMES.index(note))
    if digit == TUNE[progress]:
        return progress + 1
    first = progress // 3 * 3
    # Keep any suffix of the attempted phrase which could also begin a fresh attempt.
    attempted = TUNE[first:progress] + digit
    for size in range(min(2, len(attempted)), 0, -1):
        if attempted.endswith(TUNE[first : first + size]):
            return first + size
    return first


def add_kitchen(rooms, flags, room, post, step, visual, machine):
    hub = next(r for r in rooms if r["key"] == "DrumHouse")
    post(hub, "Kitchen", "Harbour mess stair", 12, -8, "lift", step(to="KettleYard"))
    for i, (key, flag, label, tune, words) in enumerate(FRAGMENTS):
        flags.append(flag)
        r = next(r for r in rooms if r["key"] == key)
        message = (
            "Nell used to tap the tin on her way up the mess stair. Its three dents ring " + words + ".",
            "Ara struck these cups above the foundry noise. The second part of the supper call goes "
            + words
            + ".",
            "Wen stitched the last phrase in a corner of her cloth. Pulling its three tassels rings "
            + words
            + ".",
        )[i]
        post(r, "MessNote", label, 10.2, 1.5, "keepsake", step(message, award=flag))
        r["stations"][-1].update(tune=tune, camp="RestMessNote")
    flags.append("supperServed")
    machine(
        "potcall",
        ["supperBeat", "firstPhrase", "secondPhrase", "thirdPhrase"],
        list(NAMES),
        0,
        note_played,
        lambda n: (n, int(n >= 3), int(n >= 6), int(n >= 9)),
    )
    r = room(
        "KettleYard",
        "The Harbour Mess",
        "The flood crews used to eat together here. Find their three pieces of the supper call, play them on the hanging pans and put the hot pot on the table.",
        "KettleLight",
    )
    r.update(chapter="The Supper Call", fog="#baa788")
    post(
        r,
        "Cook",
        "Iona the cook",
        -4,
        -5,
        "person",
        step(
            "IONA  /  Nell has put her boots by the door. Ara took the end seat. Wen has started on the washing-up already. There they are.",
            {"supperServed": 1},
        ),
        step(
            "IONA  /  Same three places at the table since the flood. Nell called first from the chain dock, Ara answered in the mould loft, Wen finished from the signal room. Bring me their old call."
        ),
    )
    post(
        r,
        "Score",
        "The kitchen ledger",
        -5.4,
        1.4,
        "leaf",
        step(
            "The call has three phrases. Nell’s tin starts it; Ara’s cups answer; Wen’s tea cloth brings it home. Your witness book keeps the parts you have heard. A lit bowl on the shelf means a phrase is complete."
        ),
    )
    for i, (name, x) in enumerate(zip(("Low", "Middle", "High"), (-3.2, 0, 3.2))):
        post(
            r,
            name,
            name + " pan",
            x,
            5.7,
            "pan",
            step("The kettle sings. All three voices have come home.", {"thirdPhrase": 1}),
            step(
                "The enamel rings through the kitchen. Notes placed: {supperBeat}/9.",
                move="potcall." + name,
            ),
        )
        r["stations"][-1].update(note=NAMES.index(name), swing="Pan" + name, camp="Rest" + name)
        visual(r, "Phrase" + str(i), ("firstPhrase", "secondPhrase", "thirdPhrase")[i], "show")
    post(
        r,
        "Serve",
        "Set out supper",
        5.6,
        -1.4,
        "table",
        step(
            "Three spoons lie in the empty pot. Iona has wrapped you a slice of yesterday’s apple cake.",
            {"supperServed": 1},
        ),
        step(
            "Nell knocks the mud from her boots. Ara takes the cracked blue bowl. Wen folds her tea cloth over the bread. For once, all three reach the table while the stew is still hot.",
            {**{f[1]: 1 for f in FRAGMENTS}, "thirdPhrase": 1},
            award="supperServed",
        ),
        step(
            "Iona lays out the bowls. Bring a voice from each workshop and play their supper call on the three pans."
        ),
    )
    r["stations"][-1]["camp"] = "RestServe"
    post(r, "Home", "Return to the drum house", -9, -11, "lift", step(to="DrumHouse"))
    r["goals"] = [
        step(
            "Three workmates have found one another over a hot meal. The mess stair leads back to the drum house.",
            {"supperServed": 1},
        )
    ]
    for key, flag, label, tune, words in FRAGMENTS:
        r["goals"].append(
            step(
                "Find "
                + label
                + " in "
                + {
                    "ChainDock": "Chainwater Dock",
                    "MouldLoft": "the Mould Loft",
                    "SignalLoom": "the Signal Loft",
                }[key]
                + ". Its tune belongs in the kitchen ledger.",
                {flag: 0},
            )
        )
    r["goals"].extend(
        [
            step("The call is complete. Set out the hot pot.", {"thirdPhrase": 1}),
            step(
                "Play Nell, Ara and Wen’s call in order. The journal keeps all three phrases. Notes placed: {supperBeat}/9."
            ),
        ]
    )
    for group in ("MessCrew", "ServedTable", "KitchenLamp"):
        visual(r, group, "supperServed", "show")
    return [dict(signal=flag, title=label, notes=words) for key, flag, label, tune, words in FRAGMENTS]
