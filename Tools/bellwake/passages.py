"""Compile the three passage routes and paint their illustrated chart folios."""

from collections import deque
from pathlib import Path
import json, random, shutil
from PIL import Image, ImageDraw

RES = Path(__file__).resolve().parents[2] / "Assets/Resources/Bellwake"
DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
REGIONS = [
    dict(
        key="Saltwake",
        title="Saltwake Sound",
        guide="Marn",
        thing="skiff",
        intro="The drowned bell sent a second note out to sea. Marn kept the three pilots' logs. Read the soundings and bring each signal boat home.",
        rule="Steer the skiff one square. Blue arrows carry it with the current. Touch the brass buoy, then moor at the white ring.",
        sites=["The tide staff", "The salvage crane", "The last beacon"],
        testimony=[
            "The low-water mark is above Marn's shoulder. The first signal went out before the river rose.",
            "A coat button hangs from the crane hook. Ina sent the boat back empty so it could take another family.",
            "Oil for twelve winters, signed for by Tavi. She never told the pilots why the beacon still burned.",
        ],
        charts=[
            "Outer Bar",
            "Kettle Reach",
            "The Eel Cut",
            "Flood Ledger",
            "Blind Anchorage",
            "The Empty Ferry",
            "North Lantern",
            "The Widow's Buoy",
            "Home Sounding",
        ],
        ending="Marn turns the lighthouse seaward. Through the fog comes the answer of a little forest bell.",
    ),
    dict(
        key="RimePost",
        title="The Rimeway Post",
        guide="Rime",
        thing="sled",
        intro="The mountain post still holds the letters written on the night of the flood. Follow the lost courier's bearings before you descend to the lock.",
        rule="Send the sled sliding until it meets rock or the chart edge. Cross the gold mail cache, then STOP on the white landing.",
        sites=["The snow shelter", "The runner's cache", "The leaning pine"],
        testimony=[
            "The first letter is addressed to Ina at home. Everybody expected her back before breakfast.",
            "There are two sets of hoofprints outside the cache. A child took the pony back alone.",
            "The last letter is Ina's own. Please put the kettle on, she wrote. I am coming by the long way.",
        ],
        charts=[
            "First Frost",
            "Two Tracks",
            "Sparrow Shelf",
            "The Crosswind",
            "Blue Hollow",
            "The White Mile",
            "Lost Post",
            "The Break in the Pines",
            "Morning Parcel",
        ],
        ending="Rime ties the last letter in oilcloth. Down the long steps, the lock wheel starts to turn.",
    ),
    dict(
        key="Glasscut",
        title="Glasscut Gallery",
        guide="Jass",
        thing="miner",
        intro="The bell was cast from a peculiar seam of singing glass. Jass will show you the work orders the foundry tried to lose.",
        rule="Move the bronze miner one square. Push the gem cart onto the white socket. It can only be pushed from behind. The rewind lever restarts this chart.",
        sites=["The survey stand", "The lift cage", "The resonance cradle"],
        testimony=[
            "The survey pegged the seam as hollow. Something inside answered each hammer stroke.",
            "The lift book lists only one passenger that night. Tavi carried the casting order down herself.",
            "Scratched under the cradle: one night. Jass put those words in the contract before the bronze was poured.",
        ],
        charts=[
            "First Cut",
            "Ore Siding",
            "Lampblack Bend",
            "The Switchback",
            "Blind Seam",
            "The Weigh House",
            "Twelve Strokes",
            "The Counterweight",
            "Final Delivery",
        ],
        ending="The cart settles into its cradle. A thread of furnace light climbs through the stone.",
    ),
]


def advance(region, grid, goal, state, direction, travel=None):
    pos, other = state

    def step(p, d):
        dx, dy = DIRECTIONS[d]
        x, y = p % 7 + dx, p // 7 + dy
        return y * 7 + x if 0 <= x < 7 and 0 <= y < 7 and grid[y * 7 + x] != "#" else p

    n = step(pos, direction)
    if n == pos:
        return state
    if region == 2:
        if n == other:
            dest = step(other, direction)
            if dest == other:
                return state
            other = dest
        if travel is not None:
            travel.append(n)
        return n, other
    seen = set()
    while True:
        if travel is not None:
            travel.append(n)
        if n == other:
            other = -1
        here = n
        if region == 1:
            n = step(n, direction)
        elif grid[n] in "^>v<":
            n = step(n, "^>v<".index(grid[n]))
        else:
            break
        if n == here or n in seen:
            n = here
            break
        seen.add(here)
    return n, other


def compile_board(region, rng, depth):
    for attempt in range(18000):
        grid = [
            "#" if rng.random() < (0.25 if region != 1 else 0.21) else "."
            for _ in range(49)
        ]
        free = [i for i, c in enumerate(grid) if c == "."]
        start, cargo, goal = rng.sample(free, 3)
        if region == 0:
            for i in free:
                if i not in [start, cargo, goal] and rng.random() < 0.32:
                    grid[i] = rng.choice("^>v<")
        states = [(start, cargo)]
        ids = {states[0]: 0}
        rows = []
        parents = {}
        solved = []
        for i, (p, c) in enumerate(states):
            win = c == goal if region == 2 else p == goal and c == -1
            row = []
            paths = []
            for d in range(4):
                travel = []
                t = (p, c) if win else advance(region, grid, goal, (p, c), d, travel)
                paths.append("".join(chr(65 + n) for n in travel))
                if t not in ids:
                    ids[t] = len(states)
                    states.append(t)
                j = ids[t]
                row.append(j)
                if j != i:
                    parents.setdefault(j, []).append((i, d))
            rows.append(
                dict(
                    p=p,
                    c=c,
                    move=row,
                    paths=paths if region != 2 else None,
                    hint=-1,
                    win=win,
                )
            )
            if win:
                solved.append(i)
        q = deque(solved)
        dist = {i: 0 for i in solved}
        while q:
            j = q.popleft()
            for i, d in parents.get(j, []):
                if i in dist:
                    continue
                dist[i] = dist[j] + 1
                rows[i]["hint"] = d
                q.append(i)
        length = dist.get(0, 0)
        if depth <= length <= depth + 6:
            return dict(grid="".join(grid), goal=goal, par=length, states=rows)
    raise ValueError((region, depth))


def paint(region, boards):
    palette = [
        ("#286465", "#478d85", "#344d4c", "#b6cfab"),
        ("#769ea7", "#a4c9c7", "#5b6c81", "#e5eee1"),
        ("#6e6468", "#968c81", "#413c50", "#d7b58a"),
    ][region]
    atlas = Image.new("RGB", (672, 672))
    rng = random.Random(921 + region)
    for idx, b in enumerate(boards):
        im = Image.new("RGB", (224, 224))
        d = ImageDraw.Draw(im)
        for i, c in enumerate(b["grid"]):
            x = i % 7 * 32
            y = i // 7 * 32
            d.rectangle(
                (x, y, x + 31, y + 31),
                fill=palette[(i + i // 7) % 2],
                outline=palette[2],
            )
            for _ in range(8):
                a = x + rng.randrange(2, 27)
                e = y + rng.randrange(2, 29)
                d.line((a, e, a + rng.randrange(2, 5), e), fill=palette[1])
            if c == "#":
                d.polygon(
                    [
                        (x + 2, y + 25),
                        (x + 9, y + 8),
                        (x + 17, y + 3),
                        (x + 26, y + 12),
                        (x + 30, y + 26),
                    ],
                    fill=palette[2],
                    outline=palette[3],
                )
                d.line(
                    [(x + 9, y + 8), (x + 17, y + 12), (x + 17, y + 3)],
                    fill=palette[3],
                    width=2,
                )
            elif c in "^>v<":
                dx, dy = DIRECTIONS["^>v<".index(c)]
                cx, cy = x + 16, y + 16
                d.line(
                    (cx - dx * 9, cy - dy * 9, cx + dx * 9, cy + dy * 9),
                    fill="#e0edc4",
                    width=3,
                )
                d.line(
                    [
                        (cx - dy * 6, cy + dx * 6),
                        (cx + dx * 9, cy + dy * 9),
                        (cx + dy * 6, cy - dx * 6),
                    ],
                    fill="#e0edc4",
                    width=3,
                )
            if i == b["goal"]:
                for inset, col in [(3, "#30272c"), (5, "#fff3cb"), (9, "#fff3cb")]:
                    d.ellipse(
                        (x + inset, y + inset, x + 31 - inset, y + 31 - inset),
                        outline=col,
                        width=2,
                    )
        atlas.paste(im, ((idx % 3) * 224, (idx // 3) * 224))
    atlas.save(RES / "Textures" / (REGIONS[region]["key"] + "Chart.png"), optimize=True)


if __name__ == "__main__":
    import sys

    from material_swatches import repaint
    rng = random.Random(123091)
    for r, reg in enumerate(REGIONS):
        repaint(
            Path(sys.argv[1])
            / "Textures"
            / (["Coast", "Ice", "Crystal"][r] + "_atlas.png"),
            RES / "Textures" / (["Coast", "Ice", "Crystal"][r] + "Atlas.png"),
        )
        boards = [
            compile_board(r, rng, depth)
            for depth in (
                [4, 6, 8, 9, 10, 12, 14, 16, 19]
                if r != 1
                else [3, 4, 5, 6, 7, 8, 9, 10, 11]
            )
        ]
        paint(r, boards)
        directory = RES / "Charts"
        directory.mkdir(exist_ok=True)
        (directory / (reg["key"] + ".json")).write_text(
            json.dumps(dict(boards=boards), separators=(",", ":"))
        )
        print(reg["key"], [(b["par"], len(b["states"])) for b in boards], flush=True)
    (RES / "Passages.json").write_text(
        json.dumps(dict(regions=REGIONS), separators=(",", ":"))
    )
