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
