"""Five surviving passenger accounts from the night the relief barge Mercy ran."""

# Each witness signs one of two statements. Both outcomes open the next reach.
# Keys are appended to the existing plan so older chamber and machine saves remain valid.
REACHES = [
    (
        "MercySlip",
        "The Mercy Slip",
        219,
        4,
        "Wrenfall",
        "Bess the shipwright",
        "BESS  /  The keeper’s stairs are on the far side of six night berths. My boat carried thirty people across them. The harbour account gives the crossing to an empty hull. Help me put the hands back in it.",
        [
            (
                "Book",
                "Slip ledger",
                "desk",
                "Twenty-nine fares. Bess had counted thirty heads. The line beneath the last fare is scored through.",
            ),
            (
                "Shoe",
                "Grounding shoe",
                "anvil",
                "The iron shoe took the scrape under the school steps. You find a child's blue bead wedged in the scar.",
            ),
            (
                "Mast",
                "Sheared mast",
                "spool",
                "A loop of sail rope still binds the split. Someone short could have reached it from a passenger's shoulders.",
            ),
            (
                "Rib",
                "Numbered rib",
                "rib",
                "Two names cut into rib seven. One is Bess. The other is her apprentice Dot, who could never afford a fare.",
            ),
            (
                "Oak",
                "Crooked timber",
                "root",
                "You take the natural elbow. Bess sets the grain along the curve of the bow.",
            ),
            (
                "Rivet",
                "Copper roves",
                "anvil",
                "Dot's punch fits every head. You peen the curved rib home.",
            ),
            (
                "Seam",
                "Paying trough",
                "press",
                "You press oakum into the open seam until a stripe of tar runs clean from stem to stern.",
            ),
            (
                "Berth",
                "Floating cradle",
                "rib",
                "For the first time since the flood Bess lets the cradle ropes run slack. The hull floats level.",
            ),
            (
                "Mark",
                "Sign the boat",
                "desk",
                "You put Dot on the crew roll. Her berth belongs with the people who worked the crossing.",
            ),
        ],
        (
            "Record her fare",
            "You issue Dot the missing passage slip. She keeps the bead threaded through its corner.",
        ),
    ),
    (
        "Wickwater",
        "Wickwater Fen",
        613,
        0,
        "Reedwater",
        "Oli the lamp tender",
        "OLI  /  The fog took the far bank. My brother saw a green lamp where the chart marks only reeds. We must find who left it burning.",
        [
            (
                "Jar",
                "Wick oil jar",
                "satchel",
                "The jar smells of crushed winter apples. An orchard family paid for this oil.",
            ),
            (
                "Reed",
                "Reed cutter",
                "knife",
                "You split the reed along its pith. The white centre pulls a thread of oil up the wick.",
            ),
            (
                "Float",
                "Reed cradle",
                "float",
                "A clay lamp shouldered between two floats stays upright in the wash.",
            ),
            (
                "Feeder",
                "Feeder spring",
                "spring",
                "The spring runs towards the village in summer. In flood it ran towards the boat.",
            ),
            (
                "Glass",
                "Green shade",
                "lantern",
                "Behind the cracked glass are two pin holes, spaced like the eyes of a hare.",
            ),
            (
                "Stake",
                "Hare marker",
                "cairn",
                "The same eyes mark this piling. You tie the floating cradle to the high-water notch.",
            ),
            (
                "Trim",
                "Wick shears",
                "knife",
                "The black fray comes off. A small green flame stands upright inside the shade.",
            ),
            (
                "Tower",
                "Low fog tower",
                "beacon",
                "From these steps the small light shows a safe channel underneath the tall keeper’s lamp.",
            ),
            (
                "Mark",
                "Sign the lamp",
                "desk",
                "You hang the lamp tender’s name inside the hood. Boats can thank Oli by name.",
            ),
        ],
        (
            "Sign the spring",
            "The orchard families go down as the keepers of the spring. Oli leaves a full jar on their wall.",
        ),
    ),
    (
        "LinenCourt",
        "The Linen Courts",
        983,
        2,
        "VellumWalk",
        "Eda the washer",
        "EDA  /  No one could hear a cry above the rain. We hung different sheets for beds, food and a safe door. The council exhibit calls them festival flags.",
        [
            (
                "Chest",
                "Linen chest",
                "satchel",
                "Eda saved three hems with three different seams. She asks you to read the clothesline from a passenger’s height.",
            ),
            (
                "Blue",
                "Blue mending line",
                "line",
                "The blue hem has one fold. It hung across the infirmary windows where the beds were dry.",
            ),
            (
                "White",
                "Bread cloth",
                "rack",
                "Flour still sits in the white square’s double seam. A loaf fitted in each corner.",
            ),
            (
                "Ochre",
                "Ochre door cloth",
                "frame",
                "Three knots at the ochre edge marked an unlocked door. Ina tied them left-handed.",
            ),
            (
                "Dye",
                "Madder vat",
                "spring",
                "You lift the dry strip from the red dye. When wet it will darken to the colour of the old door cloth.",
            ),
            (
                "Loom",
                "Signal loom",
                "loom",
                "One fold, two seams, three knots. You weave the signals side by side, low enough for a child to read.",
            ),
            (
                "Raise",
                "Washing green",
                "line",
                "The three cloths rise above the parapet. A deckhand at the far berth waves a blue rag.",
            ),
            (
                "Beds",
                "Makeshift cots",
                "loom",
                "Eda puts the old stretchers back on their feet. The smallest has chalk stars under its headrail.",
            ),
            (
                "Mark",
                "Sign the shelter",
                "desk",
                "The linen court is entered as a place of shelter. Its gate will stay open in bad weather.",
            ),
        ],
        (
            "Sign the signal",
            "The cloth code goes to the ferry crews. Three knots now mean an open door on either shore.",
        ),
    ),
    (
        "KiteCrag",
        "Kite Crag",
        138,
        3,
        "Cairnwatch",
        "Ivo the line boy",
        "IVO  /  I was twelve. They sent me up here with a kite because no grown hand could feel the gusts. My kite took the towline over the break.",
        [
            (
                "Spar",
                "Split kite spar",
                "root",
                "The willow is dark where Ivo gripped it. You trim a matching spar to the length of his forearm.",
            ),
            (
                "Silk",
                "Sailmaker’s silk",
                "frame",
                "One triangle is cut from a mourning scarf. Its owner was waiting beside the broken footbridge.",
            ),
            (
                "Bridle",
                "Three-point bridle",
                "kite",
                "The low loop has stretched. You shorten it to bring the kite’s nose up into the crosswind.",
            ),
            (
                "Splice",
                "Towline splice",
                "spool",
                "The thin messenger takes a heavier line. Ivo splices the end with the knot his mother taught him.",
            ),
            (
                "Wind",
                "Notched wind stone",
                "cairn",
                "The stone whistles from the east face. The crest shelters the line boy from the worst of the gust.",
            ),
            (
                "Cast",
                "Kite saddle",
                "kite",
                "The kite rides above the broken span. Its red tail clears the parapet by the width of a hand.",
            ),
            (
                "Brake",
                "Capstan brake",
                "press",
                "You ease the tow through the brake. A barge-sized pull settles into the line.",
            ),
            (
                "Land",
                "Landing hook",
                "anvil",
                "The landing hook catches. Ivo puts his old scarf on the post so his mother would have seen it.",
            ),
            (
                "Mark",
                "Sign the pilot",
                "desk",
                "Ivo signs in his own hand. He was the pilot of the line even if he never stepped aboard.",
            ),
        ],
        (
            "Sign the crew",
            "Ivo gives each hand an inch of the old scarf. They write the crew names beneath its red edge.",
        ),
    ),
    (
        "SoundingBay",
        "Sounding Bay",
        787,
        4,
        "Saltwake",
        "Fenel the diver",
        "FENEL  /  The ship’s chart says six feet at the bar. The marks in my father’s lead line tell a different story. Read the bottom he touched on that crossing.",
        [
            (
                "Reel",
                "Sounding reel",
                "spool",
                "The reel line still smells of beeswax. A marked leather tongue means a fathom, an unmarked knot half.",
            ),
            (
                "Lead",
                "Tallow cup",
                "float",
                "You press soft tallow into the hollow under the lead. Sand and shell will stick to it when it touches bottom.",
            ),
            (
                "Shell",
                "Shell bank",
                "dais",
                "Broken pink shells cling to the cup. You mark their scalloped edges beside the shoal on the chart.",
            ),
            (
                "Stone",
                "Basalt shelf",
                "cairn",
                "The next cast comes up clean apart from black basalt grit. The old channel cuts across the shelf.",
            ),
            (
                "Hole",
                "Deep-water bell",
                "dive",
                "A low hollow note tells Fenel the sounding bell has dropped below the swell.",
            ),
            (
                "Slack",
                "Slack-water drum",
                "press",
                "You hold the drum when the line goes slack. Two leather tongues have run through your hand.",
            ),
            (
                "Cast",
                "Chart table",
                "desk",
                "Two fathoms at slack water. Fenel’s father had cut a safe course a full boat’s width from the passage on the printed chart.",
            ),
            (
                "Buoy",
                "Channel buoy",
                "dive",
                "The buoy swings free above the new channel. A strip of pink shell and the black basalt confirm its position.",
            ),
            (
                "Mark",
                "Sign the diver",
                "desk",
                "Fenel enters the sounder’s name under the depth. Next winter’s pilots will know whom to ask.",
            ),
        ],
        (
            "Sign the channel",
            "The new channel is entered as public knowledge. Both landings receive copies of the soundings.",
        ),
    ),
    (
        "SupperSteps",
        "The Supper Steps",
        990,
        1,
        "SaffronKilns",
        "Nan the baker",
        "NAN  /  By the time the boat got here the fire was out. Everybody remembers hot bread. I remember what it cost to light it.",
        [
            (
                "Tin",
                "Bread tin",
                "mould",
                "A palm pressed into the bottom steadies the old tin on the listing hearth.",
            ),
            (
                "Measure",
                "Ration measure",
                "rule",
                "Thirty portions, each the same width. Nan’s own is the one still scratched on the measure.",
            ),
            (
                "Ember",
                "Banked embers",
                "kiln",
                "A thumb of charcoal survived under the grey ash. You cup it until a point of orange shows.",
            ),
            (
                "Fan",
                "Bellows stand",
                "press",
                "Air runs under the coal. The stove begins to draw without filling the room with smoke.",
            ),
            (
                "Knead",
                "Kneading bench",
                "desk",
                "You fold the dough over Nan’s flour marks. The thirtieth loaf is as large as the first.",
            ),
            (
                "Bake",
                "Relief oven",
                "oven",
                "The recovered ember fires the oven. A crescent chip in the brick leaves its mark on each crust.",
            ),
            (
                "Rack",
                "Cooling racks",
                "rack",
                "You set thirty loaves on the racks. The last space is by the door for the person steering home.",
            ),
            (
                "Door",
                "Last supper stair",
                "arch",
                "There was no missing passenger. Bess’s crew, the light keepers and the people on shore were on one another’s lists.",
            ),
            (
                "Mark",
                "Sign the baker",
                "desk",
                "Nan puts her floury hand against the bell book. It keeps the mark of the person who fed the watch.",
            ),
        ],
        (
            "Sign the table",
            "Every seat is entered, even the one at the end for the stranger who steers home.",
        ),
    ),
]

# Facsimile dies for the registrar's press. Witnesses describe the identifying detail on the trail.
DIES = [
    (("blue bead", "split mast", "rib seven"), 2, "Dot cut her name beside Bess’s on rib seven."),
    (("hare eyes", "reed tassel", "apple leaf"), 0, "Two pinholes in the green glass made a hare’s eyes."),
    (("single hem", "three knots", "double seam"), 1, "Three left-handed knots marked a door left open."),
    (
        ("landing hook", "black brake", "red scarf"),
        2,
        "The red scarf on the landing post told the family Ivo was safe.",
    ),
    (
        ("black grit", "leather tongues", "broken shell"),
        1,
        "Two leather tongues in the line gave the depth at slack water.",
    ),
    (
        ("crescent crust", "flour hand", "palm tin"),
        0,
        "The chipped oven brick left a crescent on every loaf.",
    ),
]

# Landings on the six surveyed canals, in story order. The final point is the onward boat.
LANDINGS = {
    "MercySlip": [(2, 3), (13, 7), (4, 1), (13, 12), (1, 6), (13, 1), (7, 14), (1, 14), (0, 11), (10, 3)],
    "Wickwater": [(6, 10), (13, 13), (10, 5), (3, 12), (14, 2), (1, 6), (0, 9), (9, 14), (14, 8), (10, 2)],
    "LinenCourt": [(11, 14), (9, 1), (6, 10), (10, 9), (2, 14), (0, 1), (7, 13), (10, 5), (8, 2), (14, 11)],
    "KiteCrag": [(1, 12), (8, 2), (11, 14), (2, 10), (7, 13), (2, 1), (14, 1), (14, 9), (14, 14), (3, 8)],
    "SoundingBay": [
        (12, 4),
        (11, 12),
        (0, 6),
        (5, 1),
        (7, 14),
        (12, 10),
        (2, 10),
        (11, 2),
        (14, 10),
        (1, 13),
    ],
    "SupperSteps": [
        (0, 9),
        (11, 12),
        (9, 4),
        (10, 10),
        (8, 3),
        (5, 13),
        (1, 14),
        (13, 10),
        (12, 2),
        (4, 1),
    ],
}


def fields():
    return [
        (
            key,
            title,
            seed,
            theme,
            speaker,
            intro,
            [
                (name, label, style, line, (jobs[i - 1][0],) if i else ())
                for i, (name, label, style, line) in enumerate(jobs)
            ],
            "Both banks have heard this account. Take the passage onward.",
        )
        for key, title, seed, _, theme, speaker, intro, jobs, _ in REACHES
    ]


# The signed statement stays in the book. A reply arrives the morning after the bell.
REPLIES = [
    [
        [
            "Dot has taken the early watch. She signs with the shipwright’s punch.",
            "Dot ferried the sisters home. Ina found the blue bead where she had left it.",
        ],
        [
            "Dot's first fare slip hangs above the public till. Children ride free on watch nights.",
            "Dot punched two return tickets, one for each sister, and slipped the bead into Ina’s hand.",
        ],
    ],
    [
        [
            "Oli hangs a little green light outside every watch hut.",
            "Oli leaves a lamp between the sisters’ doors. Ina brings it in when Tavi gets home.",
        ],
        [
            "The orchard families bring their oil a jar at a time. The fen lights last the winter.",
            "Ina took an empty jar to the orchard. She came back with oil, three apples and muddy knees.",
        ],
    ],
    [
        [
            "Eda has made the first bed by the watch door. The hem is folded once.",
            "Eda found the two sisters asleep on the chalk-star cot, their muddy boots under the rail.",
        ],
        [
            "Every watch boat flies the three-knotted cloth. There is a dry place on either bank.",
            "Tavi tied three knots in a clean cloth and hung it from the kitchen window.",
        ],
    ],
    [
        [
            "Ivo teaches the new pilots to fly a line in a crosswind. He keeps the little kite for himself.",
            "Ivo let Ina hold the line. When the kite rose, she laughed and wound it out another arm’s length.",
        ],
        [
            "Six strips of red scarf hang in the new watchroom. Each carries a different hand.",
            "The landing crew passed the scarf to Ina. She stitched the strips together on the return boat.",
        ],
    ],
    [
        [
            "Fenel writes his name on the pilot board and leaves the lead line beneath it.",
            "The sisters took the channel at slack water. At the second leather tongue, Fenel waved them through.",
        ],
        [
            "Both shores copied the soundings. The night pilots now argue over who gets the first clean chart.",
            "Ina has added one small mark to the public chart, a dry stone where two people can sit.",
        ],
    ],
    [
        [
            "Nan takes the oven watch. A crescent on the first crust tells the crew she is there.",
            "Nan kept two crescent loaves warm until Tavi and Ina came down the steps.",
        ],
        [
            "There is always a chair by the watchroom door. On the first night an unknown ferryman took it.",
            "Ina sat in the last chair. Nan moved her own plate over and made room for Tavi.",
        ],
    ],
]


def configure_account(index, room, post, step, visual, machine, flags):
    key, _, _, _, _, _, _, jobs, alternate = REACHES[index]
    dies, correct, clue = DIES[index]
    mark, die, second = key + "Mark", key + "Die", key + "SecondAccount"
    evidence = key + jobs[-2][0]
    flags.append(second)
    machine(die, [die], ["turn"], 0, lambda n, op: (n + 1) % 4, lambda n: (n,))
    sealed = step("The ink is dry. Your choice is on the passenger roll.", {mark: 1})
    mismatch = step("That impression disagrees with the witness. " + clue, {evidence: 1})
    unfinished = step("Finish the local witness work before signing the passenger roll.")

    def sign(line, award=""):
        return step(line, {evidence: 1, die: correct + 1}, award=award, move=key + ".Mark")

    desk = next(s for s in room["stations"] if s["id"] == "A_Mark")
    desk["rules"] = [sealed, sign(jobs[-1][3]), mismatch, unfinished]
    x, y = desk["x"], desk["y"]
    post(
        room,
        "Other",
        alternate[0],
        x - 2.1,
        y,
        "desk",
        sealed,
        sign(alternate[1], second),
        mismatch,
        unfinished,
    )
    labels = ("blank",) + dies
    post(
        room,
        "Die",
        "Witness seal press",
        x + 2.04,
        y,
        "die",
        sealed,
        *[
            step("The press now shows " + labels[(n + 1) % 4] + ".", {die: n}, move=die + ".turn")
            for n in range(4)
        ],
    )
    for n in range(4):
        visual(room, "DieFace" + str(n), die, "show", match=n)
    goal = next(g for g in room["goals"] if g["lead"] == "A_Mark")
    goal["line"] = (
        "Set the seal press to match the evidence, then choose which account to sign. "
        + jobs[-1][1]
        + " or "
        + alternate[0].lower()
        + "."
    )
