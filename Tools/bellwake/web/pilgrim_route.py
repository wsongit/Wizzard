"""Walk the five wards through the regular player controls, including a journal and shelter checkpoint."""

import json
from route_checkpoint import write_json

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
