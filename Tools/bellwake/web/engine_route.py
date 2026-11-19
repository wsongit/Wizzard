"""Walk the Countertide galleries, operate the real stations and return to the main campaign."""

import json
from collections import deque
from pathlib import Path


def route(machine, start, channel, done):
    target = machine["channels"].index(channel)
    paths = {start: []}
    pending = deque([start])
    while pending:
        node = pending.popleft()
        if machine["rows"][node]["values"][target] == done:
            return paths[node]
        for op, to in zip(machine["controls"], machine["rows"][node]["moves"]):
            if to not in paths:
                paths[to] = paths[node] + [(op, to)]
                pending.append(to)
    raise AssertionError(machine["key"] + " unreachable")


async def complete_engine(act, page, start, out):
    plan = json.loads(
        (Path(__file__).resolve().parents[3] / "Assets/Resources/Bellwake/Underworks.json").read_text()
    )

    async def use(key):
        return await act("A_" + key)

    assert (await use("Keeper"))["district"] == "DrumHouse"
    assert (await use("Final"))["district"] == "DrumHouse"
    assert (await use("Loom"))["district"] == "DrumHouse"
    report = {}
    for i, (door, district, key, progress, goal, model) in enumerate(
        (
            ("Dock", "ChainDock", "towlines", "towJob", 4, "Ferry0"),
            ("Crane", "MouldLoft", "moulds", "craneJob", 3, "Collar0"),
            ("Loom", "SignalLoom", "weaving", "loomFlag", 4, "Heddle0"),
        )
    ):
        if i:
            await use("Turn")
        state = await use(door)
        assert state["district"] == district
        await use("Talk")
        state = await use("Beat" if key == "weaving" else "Seal")
        assert state["works"]["signals"][progress] == 0
        idx = next(i for i, m in enumerate(plan["machines"]) if m["key"] == key)
        m = plan["machines"][idx]
        walk = route(m, state["works"]["machines"][idx], progress, goal)
        observed = set()
        before = state["machinery"][model]["position"]
        for j, (op, to) in enumerate(walk):
            state = await use(op[0].upper() + op[1:])
            assert state["works"]["machines"][idx] == to, (key, op, to, state["works"])
            if j == 3:
                await page.mouse.up()
                await start()
                restored = await page.evaluate("bellProbe()")
                assert restored["works"] == state["works"], district
                near = restored["markers"]["A_" + op[0].upper() + op[1:]]
                assert sum((near[a] - restored["feet"][a]) ** 2 for a in (0, 2)) < 9
            observed.add(state["works"]["signals"][progress])
        assert goal in observed and set(range(1, goal + 1)) <= observed
        await page.wait_for_timeout(550)
        after = (await page.evaluate("bellProbe()"))["machinery"][model]["position"]
        report[key] = dict(
            stationInputs=len(walk), completed=goal, checkpoint=True, modelFrom=before, modelTo=after
        )
        assert (await use("Home"))["district"] == "DrumHouse"
    state = await use("Final")
    assert state["district"] == "StillBelfry" and state["works"] is None
    (out / "countertide.json").write_text(json.dumps(report, indent=2) + "\n")
    return state


async def complete_supper(act, page, start, out):
    async def use(name):
        return await act("A_" + name)

    await use("Kitchen")
    assert not (await use("Serve"))["meal"]["served"]
    await use("Home")
    journals = []
    for i, (door, tones, label) in enumerate(
        (("Dock", [2, 0, 2], "Nell"), ("Crane", [1, 1, 0], "Ara"), ("Loom", [0, 2, 1], "Wen"))
    ):
        if i:
            await use("Turn")
        await use(door)
        await use("MessNote")
        await page.wait_for_function(
            "notes => JSON.stringify(bellProbe().recentTones.slice(-3))===JSON.stringify(notes)",
            arg=tones,
        )
        await page.mouse.up()
        await start()
        await page.keyboard.press("j")
        book = await page.locator("#leaves").inner_text()
        assert label in book
        journals.append(book)
        await page.keyboard.press("j")
        await use("Home")

    await use("Kitchen")
    await use("Cook")
    await use("Score")
    for note in ("Low", "High", "Low", "Low"):
        state = await use(note)
    assert state["works"]["signals"]["supperBeat"] == 3
    await page.mouse.up()
    await start()
    assert (await page.evaluate("bellProbe()"))["works"]["signals"]["supperBeat"] == 3
    for note in ("Middle", "Middle", "High", "High", "Low", "Middle"):
        state = await use(note)
    assert state["works"]["signals"]["thirdPhrase"] and not state["meal"]["served"]
    assert all((await use("Serve"))["meal"].values())
    await page.mouse.up()
    await start()
    assert all((await page.evaluate("bellProbe()"))["meal"].values())
    await use("Home")
    (out / "supper.json").write_text(
        json.dumps(
            dict(journals=journals, pitches=9, badNoteRecovery=True, checkpoint=True, served=True),
            indent=2,
        )
        + "\n"
    )
    print(
        "PASS three audible fragments, witness journal, wrong note recovery, checkpoint and harbour supper",
        flush=True,
    )
