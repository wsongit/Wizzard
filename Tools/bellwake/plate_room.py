"""A working two-colour heliostat. Mirrors reflect a ray in the floor plane."""

from itertools import product

KEY = "GloamingPress"
SOURCE = (-16, 0)
PIVOTS = ((-8, 0), (0, 8), (0, -8), (0, 0), (8, 0))
NAMES = ("Fork", "North", "South", "Cross", "Crown")
ELBOWS = {(-8, 8): (1, "Blue"), (-8, -8): (0, "Gold")}
PLATES = (
    (
        (0, 16),
        "Blue",
        "Cradle",
        "Cradle glass",
        "A midwife’s cradle rocks on a ferry bench. The scratched initials are P.V. Pella was aboard when the horn sounded.",
    ),
    (
        (8, -16),
        "Gold",
        "Ladder",
        "Ladder glass",
        "An empty ladder leans against the school landing. The high-water scratch on the wall stands above its last rung.",
    ),
    (
        (8, 16),
        "Blue",
        "Hand",
        "Hand glass",
        "A small left hand holds the school gate open from the water side. On the cuff is the crooked stitch Tavi made for her sister.",
    ),
)
MIRRORS = set(PIVOTS) | set(ELBOWS)


def trace(bits):
    at, direction, colour = SOURCE, (1, 0), "White"
    path = []
    seen = set()
    while (at, direction) not in seen:
        seen.add((at, direction))
        dx, dy = direction
        x, y = at
        while True:
            x, y = x + dx, y + dy
            if (x, y) in MIRRORS or max(abs(x), abs(y)) == 16:
                break
        end = (x, y)
        path.append((min(at, end), max(at, end), colour))
        if end not in MIRRORS:
            return path, (end, colour)
        if end in ELBOWS:
            slope, colour = ELBOWS[end]
        else:
            slope = bits[PIVOTS.index(end)]
        direction = (dy, dx) if slope else (-dy, -dx)
        at = end
    raise ValueError("A source ray entered a closed optical circuit")


PATHS = {bits: trace(bits) for bits in product(range(2), repeat=5)}
SEGMENTS = sorted({e for path, _ in PATHS.values() for e in path})
OPS = tuple(n.lower() for n in NAMES) + tuple(p[2].lower() for p in PLATES)


def operate(state, op):
    job, *bits = state
    if job == 3:
        return state
    i = OPS.index(op)
    if i < 5:
        bits[i] ^= 1
    elif i - 5 == job and PATHS[tuple(bits)][1] == PLATES[job][:2]:
        job += 1
    return (job, *bits)


def outputs(s):
    job, *bits = s
    path, hit = PATHS[tuple(bits)]
    return (
        job,
        *bits,
        *(int(e in path) for e in SEGMENTS),
        *(int(hit == p[:2]) for p in PLATES),
        *(int(job > j) for j in range(3)),
    )


def build(room, post, step, visual, machine):
    channels = [
        "glassProof",
        *["dial" + n for n in NAMES],
        *["line" + str(i) for i in range(len(SEGMENTS))],
        *["lit" + p[2] for p in PLATES],
        *["print" + p[2] for p in PLATES],
    ]
    machine("proofs", channels, OPS, (0, 0, 0, 0, 0, 0), operate, outputs)
    r = room(
        KEY,
        "The Gloaming Press",
        "At sundown the glassworkers used two coloured filters to print the river watch’s photographic plates. Ossa has left three unprinted negatives beneath the roof lantern.",
        "CinderLens",
    )
    r.update(chapter="Three pictures of the flood", fog="#c3ae94", score="SilverBath")

    def station(id, label, xy, style, *rules):
        post(r, id, label, *xy, style, *rules)
        r["stations"][-1]["camp"] = "Rest" + id

    station(
        "Ledger",
        "Ossa’s darkroom ledger",
        (-5, -12),
        "desk",
        step(
            "OSSA / Ink ran in the flood. These three pieces of glass survived. The north elbow stains light blue and the south stains it gold. Turn the five silver mirrors a quarter turn. Follow the coloured line to the named glass, then open its shutter when the needle tips right. The cradle comes first."
        ),
    )
    station(
        "Plan",
        "Optician’s floor plan",
        (4, -11),
        "board",
        step(
            "Look down on the plan or open the witness book. A ray turns back along the angle of each mirror. Blue comes through the north filter, gold through the south. Unused lanes end at black stops."
        ),
    )
    for n, xy in zip(NAMES, PIVOTS):
        station(
            n,
            n + " mirror",
            xy,
            "mirror",
            step("The last proof is fixed in the light.", {"glassProof": 3}),
            step(
                "The mirror turns a quarter turn. Follow the beam to its next stop.",
                move="proofs." + n.lower(),
            ),
        )
        visual(r, "Mirror" + n, "dial" + n, "turn", amount=90)
    for j, (xy, col, n, label, msg) in enumerate(PLATES):
        station(
            n,
            "Expose the " + n.lower() + " plate",
            xy,
            "glass",
            step(msg, {"print" + n: 1}),
            step(msg, {"glassProof": j, "lit" + n: 1}, move="proofs." + n.lower()),
            step(
                "A faint shadow. Lead "
                + col.lower()
                + " light into the "
                + n.lower()
                + " glass before opening it.",
                {"glassProof": j},
            ),
            step("This glass follows the earlier exposures in Ossa’s ledger."),
        )
        visual(r, "Print" + n, "print" + n, "show")
        visual(r, "Meter" + n, "lit" + n, "tilt", amount=-62)
    for i in range(len(SEGMENTS)):
        visual(r, "LightPath" + str(i), "line" + str(i), "show")
    station(
        "Gate",
        "Pilot gardens",
        (15, 8),
        "lift",
        step(to="GlassRookery", when={"glassProof": 3}),
        step("The drying rack has three clips. Make all three prints before opening the gardens."),
    )
    r["goals"] = [
        step(
            "Ossa’s "
            + p[2].lower()
            + " glass needs "
            + p[1].lower()
            + " light. Trace the ray, turn the mirrors and expose the plate.",
            {"glassProof": j},
        )
        for j, p in enumerate(PLATES)
    ] + [step("All three photographs are fixed. Take them through the east gate to Orla’s pilot gardens.")]
