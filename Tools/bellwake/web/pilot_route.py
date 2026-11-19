"""Exercise all three pilot routes with player-input calls and verify the visible flight."""

import json
from collections import deque
from pathlib import Path


async def lead_pilots(act, page, start, out, extended=False):
    plan = json.loads(
        (Path(__file__).resolve().parents[3] / "Assets/Resources/Bellwake/Underworks.json").read_text()
    )
    idx, m = next((i, m) for i, m in enumerate(plan["machines"]) if m["key"] == "pilots")

    async def use(n):
        return await act("A_" + n)

    state = await page.evaluate("bellProbe()")
    assert state["district"] == "GlassRookery"
    if extended:
        assert (await use("P1"))["works"]["signals"]["birdAt"] == 0
        assert (await use("Gate"))["district"] == "GlassRookery"
    await use("Keeper")
    launched = []
    flights = []
    restored = False
    for job in range(3):
        state = await use("Chart")
        await page.keyboard.press("j")
        await page.wait_for_function("!document.getElementById('survey').hidden")
        await page.keyboard.press("j")
        node = state["works"]["machines"][idx]
        q = deque([(node, [])])
        seen = {node}
        while q:
            n, steps = q.popleft()
            if m["rows"][n]["values"][0] == job + 1:
                break
            for i, dest in enumerate(m["rows"][n]["moves"]):
                if dest not in seen:
                    seen.add(dest)
                    q.append((dest, steps + [(m["controls"][i], dest)]))
        else:
            raise AssertionError("No pilot route")
        for op, to in steps:
            state = await use(op.title())
            assert state["works"]["machines"][idx] == to, (op, state["works"]["signals"])
            if op.startswith("p"):
                assert state["pilotCall"] == "Pilot" + str(job)
                bird = state["pilots"][job]
                assert bird["visible"] and sum(p["visible"] for p in state["pilots"]) == 1
                if not flights or flights[-1] != job:
                    await page.wait_for_function(
                        "j=>{const p=bellProbe().pilots[j];return p.visible && Math.abs(p.wing)>.045 && p.position[1]>p.target[1]+.15}",
                        arg=job,
                    )
                    flights.append(job)
                if job == 1 and not restored:
                    await page.mouse.up()
                    await start()
                    assert (await page.evaluate("bellProbe()"))["works"] == state["works"]
                    restored = True
                await page.wait_for_function(
                    "j=>{const p=bellProbe().pilots[j];return Math.hypot(...p.position.map((v,i)=>v-p.target[i]))<.045 && Math.abs(p.wing)<.045}",
                    arg=job,
                )
            if op == "launch":
                launched.append(len(steps))
    assert not any(p["visible"] for p in state["pilots"])
    await use("Glasshouse")
    assert "All papers delivered" in await page.locator("#words").inner_text()
    entered = await use("Gate")
    assert entered["district"] == "SumpHall" and not entered["pilotCall"]
    session = await page.context.new_cdp_session(page)
    await session.send("HeapProfiler.collectGarbage")
    assert await page.evaluate("bellProbe().retiredAlive===0")
    await session.detach()
    (out / "pilots.json").write_text(
        json.dumps(
            dict(
                pilots=3,
                operations=launched,
                wingAndLandingChecked=flights,
                reload=restored,
                activeSeconds=state["secondsByPlace"]["GlassRookery"],
            ),
            indent=2,
        )
        + "\n"
    )


async def pilot_letters(act, page, start):
    plan = json.loads(
        (Path(__file__).resolve().parents[3] / "Assets/Resources/Bellwake/Underworks.json").read_text()
    )
    idx, m = next((i, m) for i, m in enumerate(plan["machines"]) if m["key"] == "pilots")
    machines = [0] * len(plan["machines"])
    machines[idx] = next(i for i, r in enumerate(m["rows"]) if r["values"][0] == 3)
    for end in (1, 2):
        await page.mouse.up()
        save = {"number": 32 + end, "leaves": 31, "works": {"machines": machines}}
        await page.evaluate("s=>localStorage.setItem('wizzard.bellwake.desktop.v1',s)", json.dumps(save))
        await start()
        await page.keyboard.press("j")
        assert plan["pilotMail"] in await page.locator("#leaves").inner_text()
        await page.wait_for_function("document.querySelector('#leaves img')?.naturalWidth === 768")

        await page.keyboard.press("j")
        assert await page.locator("#leaves img").count() == 0
        await act("A_Talk")
        assert plan["pilotEndings"][end - 1] in await page.locator("#words").inner_text()
