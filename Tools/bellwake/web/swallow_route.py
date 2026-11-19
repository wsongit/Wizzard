"""Operate the physical paddles, crane and winches through all four flood-night crossings."""

import json
from collections import deque
from pathlib import Path


async def run_lock(act, page, start, out, extended=False):
    plan = json.loads(
        (Path(__file__).resolve().parents[3] / "Assets/Resources/Bellwake/Underworks.json").read_text()
    )
    idx = next(i for i, m in enumerate(plan["machines"]) if m["key"] == "stairlock")
    m = plan["machines"][idx]

    async def use(n):
        return await act("A_" + n)

    if extended:
        assert (await use("Gate"))["district"] == "SwallowLock"
        # An old solved-lock save can still enter by the normal arch.
    state = await page.evaluate("bellProbe()")
    assert state["district"] == "SwallowLock", state["district"]
    assert (await use("Gate"))["district"] == "SwallowLock"
    if extended:
        await page.wait_for_function("bellProbe().motionLeft===0")
        before = await page.evaluate("bellProbe().fixturePasses")
        await page.evaluate("async()=>{for(let i=0;i<40;i++)await new Promise(requestAnimationFrame)}")
        assert await page.evaluate("bellProbe().fixturePasses") == before
    await use("Fen")
    state = await use("Hook")
    assert not state["works"]["signals"]["aboard"]
    state = await use("Sign")
    assert (await use("FenRoad"))["district"] == "DriftFen"
    await page.keyboard.press("q")
    assert await page.evaluate("!bellProbe().uncovered && !bellProbe().works.signals.fenFork")
    await use("Guide")
    await page.keyboard.press("q")
    assert await page.evaluate(
        "!bellProbe().uncovered && document.getElementById('speech').textContent.includes('reply')"
    )
    await page.keyboard.press("j")
    await page.wait_for_function("!document.getElementById('survey').hidden")
    await page.keyboard.press("j")
    finds = ("organRecovered", "watchRecovered", "flourRecovered", "bagRecovered")
    for n, flag in zip((2, 3, 0, 1), finds):
        await use("Story" + str(n))
        state = await use("Find" + str(n))
        assert state["works"]["signals"][flag] and not state["uncovered"]
        if n == 3:
            await page.mouse.up()
            await start()
            assert (await page.evaluate("bellProbe()"))["works"] == state["works"]
    await page.keyboard.press("q")
    assert await page.evaluate("document.getElementById('speech').textContent.includes('Only the wind')")
    state = await use("Home")
    assert state["district"] == "SwallowLock" and all(state["works"]["signals"][f] for f in finds)
    receipts = []

    async def ship_position(state):
        signals = state["works"]["signals"]
        position = [-12 + 8 * signals["bargeBerth"], 0.31 * signals["hullMark"]]
        # The hull has its Blender origin at world zero; its tracked transform starts at zero.
        await page.wait_for_function(
            "([x,y])=>{const m=bellProbe().machinery.Swallow.position;return Math.abs(m[0]-(x+12))<.05 && Math.abs(m[1]-y)<.035}",
            arg=position,
        )

    for job in range(4):
        await use("Sheet")
        node = state["works"]["machines"][idx]
        pending = deque([(node, [])])
        seen = {node}
        while pending:
            key, steps = pending.popleft()
            if m["rows"][key]["values"][0] == job + 1:
                break
            for j, to in enumerate(m["rows"][key]["moves"]):
                if to not in seen:
                    seen.add(to)
                    pending.append((to, steps + [(m["controls"][j], to)]))
        else:
            raise AssertionError("stranded barge")
        for op, to in steps:
            state = await use(op.title())
            assert state["works"]["machines"][idx] == to
            if op == "hook":
                assert state["machinery"]["Cargo" + str(job)]["visible"]
                await ship_position(state)
                if job == 1:
                    await page.mouse.up()
                    await start()
                    assert (await page.evaluate("bellProbe()"))["works"] == state["works"]
            if op == "sign":
                receipts.append(len(steps))
    await ship_position(state)
    save = await page.evaluate("localStorage.getItem('wizzard.bellwake.desktop.v1')")
    if extended:
        assert (await use("Mark"))["works"]["signals"]["unnamedRunner"] == 1
        assert not (await use("Name"))["works"]["signals"]["namedRunner"]
        assert (await use("Gate"))["district"] == "Glasscut"
        await page.mouse.up()
        await page.evaluate("s=>localStorage.setItem('wizzard.bellwake.desktop.v1',s)", save)
        await start()
    assert (await use("Name"))["works"]["signals"]["namedRunner"]
    assert (await use("Gate"))["district"] == "Glasscut"
    (out / "swallow-lock.json").write_text(
        json.dumps(
            {
                "crossings": 4,
                "salvaged": list(finds),
                "fenActiveSeconds": state["secondsByPlace"]["DriftFen"],
                "operationsPerCrossing": receipts,
                "knownRouteActiveSeconds": state["secondsByPlace"]["SwallowLock"],
                "choicesTested": 2 if extended else 1,
            },
            indent=2,
        )
        + "\n"
    )


async def fen_fare(act, page, start, out):
    for number, leaves in ((0, 0), (33, 31), (34, 31)):
        await page.mouse.up()
        await page.evaluate(
            "s=>localStorage.setItem('wizzard.bellwake.desktop.v1',s)",
            json.dumps(dict(number=number, leaves=leaves)),
        )
        await start()
        before = await page.evaluate("bellProbe()")
        field = await act("A_FenPass")
        assert (
            field["district"] == "DriftFen"
            and field["works"]["returnTicket"]
            and field["works"]["camp"] == "RestGuide"
        )
        await act("A_Guide")
        if number == 0:
            await act("A_Find0")
        await page.mouse.up()
        await start()
        state = await page.evaluate("bellProbe()")
        assert state["district"] == "DriftFen" and state["works"]["signals"]["fenFork"] == 1
        quay = await act("A_Home")
        assert quay["district"] == "SwallowLock" and quay["works"]["returnTicket"]
        returned = await act("A_Gate")
        assert (
            returned["district"] == before["district"]
            and returned["number"] == number
            and returned["ending"] == before["ending"]
            and returned["leaves"] == leaves
        )
        if number == 0:
            await act("A_FenPass")
            assert await page.evaluate("bellProbe().works.signals.flourRecovered===1")
            await act("A_Home")
            await act("A_Gate")
    (out / "fen-return.json").write_text(
        json.dumps(
            {
                "freshMarket": True,
                "bothEpilogues": True,
                "reloadInField": True,
                "earlyFindPreserved": True,
            },
            indent=2,
        )
        + "\n"
    )
