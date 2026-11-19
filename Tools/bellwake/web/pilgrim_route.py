"""Walk the five wards through the regular player controls, including a journal and shelter checkpoint."""

import json
from route_checkpoint import write_json
from pathlib import Path

TRAILS = {
    "QuinceFold": ["Knife", "Stock", "Scion", "Spring", "Mother"],
    "SaffronKilns": ["Mould", "Silt", "Press", "Dry", "Fire", "Wall"],
    "VellumWalk": ["Roll", "Potter", "Herd", "Ferry", "Stitch", "Shelf"],
    "Cairnwatch": ["Spool", "Spike", "Saddle", "Glass", "Beacon", "Stone"],
    "RainCourt": ["Rod", "Gauge", "Weir", "East", "Court", "Arch"],
}


async def walk_wards(act, page, start, out, only=None, enter=None):
    path = out / "pilgrims-cut.json"
    report = json.loads(path.read_text()) if enter and path.exists() else {}
    state = None
    for name, stations in TRAILS.items():
        if only and only != name:
            continue
        if enter and not await enter(name):
            continue
        p = await page.evaluate("bellProbe()")
        assert p["district"] == name, p["district"]
        await act("A_Talk")
        await page.keyboard.press("j")
        assert await page.locator("#survey").is_visible()
        await page.screenshot(path=str(out / (name + "-survey.jpg")))
        await page.keyboard.press("j")
        for j, station in enumerate(stations):
            state = await act("A_" + station)
            assert state["works"]["signals"][name + station] == 1, (name, station)
            if j == 0:
                camp = state["works"]["camp"]
                await page.mouse.up()
                await start()
                resume = await page.evaluate("bellProbe()")
                assert (
                    resume["works"]["camp"] == camp and resume["works"]["signals"][name + station] == 1
                )
                if name == "QuinceFold":
                    await page.keyboard.press("q")
                    await page.wait_for_function("bellProbe().guide?.cells.length>1")
                    guide = await page.evaluate("bellProbe().guide")
                    assert all(
                        abs(a % 15 - b % 15) + abs(a // 15 - b // 15) == 1
                        for a, b in zip(guide["cells"], guide["cells"][1:])
                    )
                    await page.wait_for_function(
                        "p=> Math.hypot(...bellProbe().guide.pos.map((x,i)=>x-p[i]))>.45",
                        arg=guide["pos"],
                    )
                target = resume["markers"]["A_" + station]
                assert sum((resume["feet"][i] - target[i]) ** 2 for i in (0, 2)) < 9
        await act("A_Bell")
        await act("A_Fast")
        state = await act("A_Gate")
        report[name] = {
            "jobs": stations,
            "camp": camp,
            "next": state["district"],
            "activeSeconds": state["secondsByPlace"][name],
        }
        write_json(path, report)
    if not only and state is not None:
        assert state["district"] == "RowanHollow"

async def mercy_run(act, page, start, out, enter=None):
    plan = json.loads((Path(__file__).resolve().parents[3] / "Assets/Resources/Bellwake/Underworks.json").read_text())
    rolls = out / "mercy-run.json"
    report = json.loads(rolls.read_text()) if enter and rolls.exists() else {}
    accounts = plan["reliefAccounts"]
    for i, account in enumerate(accounts):
        name = account["key"]
        if enter and not await enter(name):
            continue
        room = next(room for room in plan["rooms"] if room["key"] == name)
        assert await page.evaluate("bellProbe().district") == name
        await act("A_Talk")
        await page.keyboard.press("j")
        assert await page.locator("#survey").is_visible()
        await page.screenshot(path=str(out / (name + "-survey.jpg")))
        await page.keyboard.press("j")
        stations = [s for s in room["stations"] if s.get("trail") and s["id"] not in ("A_Mark", "A_Gate")]
        for j, station in enumerate(stations):
            result = await act(station["id"])
            assert result["works"]["signals"][name+station["id"][2:]] == 1
            if j == 3:
                await page.mouse.up()
                await start()
                assert (await page.evaluate("bellProbe().works")) == result["works"]
        failed = await act("A_Mark")
        assert failed["works"]["signals"][name+"Mark"] == 0
        choice = "A_Other" if i % 2 else "A_Mark"
        station = next(s for s in room["stations"] if s["id"] == choice)
        needed = next(c["value"] for r in station["rules"] for c in r["when"] if c["signal"] == name+"Die")
        for n in range(1,needed+1):
            state = await act("A_Die")
            assert state["works"]["signals"][name+"Die"] == n
        state = await act(choice)
        assert state["works"]["signals"][name+"Mark"] and state["works"]["signals"][name+"SecondAccount"] == i%2
        await page.keyboard.press("j")
        assert account["second" if i%2 else "first"] in await page.locator("#leaves").inner_text()
        await page.keyboard.press("j")
        await act("A_Bell")
        await act("A_Fast")
        state = await act("A_Gate")
        assert state["district"] == (accounts[i+1]["key"] if i+1<len(accounts) else "StillBelfry")
        report[name] = dict(account=choice, checkpoint=True, activeSeconds=state["secondsByPlace"][name])
        write_json(rolls, report)
