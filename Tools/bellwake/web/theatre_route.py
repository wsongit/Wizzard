"""Play four scenes through the normal market, courtyard, reel and projector interactions."""

import json

ACTS = (
    ("Pattern", (0, 0, 2), [0, 2, 1]),
    ("Log", (2, 2, 1), [2, 1, 0]),
    ("Boot", (1, 1, 0), [1, 0, 1]),
    ("Carbon", (1, 0, 2), [0, 1, 2, 0]),
)


async def perform(act, page, start, out, extended=False):
    async def use(station):
        return await act("A_" + station)

    if extended:
        assert (await use("Playhouse"))["district"] == "Bellmarket"
    state = await use("Talk")
    assert (
        state["district"] == "Bellmarket"
        and "blue courtyard door" in await page.locator("#words").inner_text()
    )
    state = await use("Playhouse")
    assert state["district"] == "PaperCourt" and state["works"]["signals"]["paperAct"] == 0
    await use("Talk")
    assert (await use("Runner"))["works"]["signals"]["paperCredit"] == 0
    if extended:
        await use("Door")
        assert (await use("Gate"))["district"] == "Bellmarket"
        await use("Playhouse")
    for i, (keepsake, solution, music) in enumerate(ACTS):
        if i == 0:
            await use("Light")
        state = await use(keepsake)
        assert state["works"]["signals"]["paper" + keepsake] == 1
        if i == 1:
            await page.mouse.up()
            await start()
            assert (await page.evaluate("bellProbe()"))["works"] == state["works"]
        for j, (station, channel) in enumerate(
            zip(("Figure", "Place", "Prop"), ("paperActor", "paperPlace", "paperProp"))
        ):
            while state["works"]["signals"][channel] != solution[j]:
                state = await use(station)
        assert [state["playhouse"][k] for k in ("figures", "places", "props")] == [[v] for v in solution]
        state = await use("Light")
        assert state["works"]["signals"]["paperAct"] == state["playhouse"]["lamps"] == i + 1
        assert state["playhouse"]["gesture"] == "PuppetArm" + str(solution[0])
        await page.wait_for_function(
            "song=>JSON.stringify(bellProbe().recentTones.slice(-song.length))===JSON.stringify(song)",
            arg=music,
        )
        if extended and i == 0:
            await page.mouse.up()
            await start()
            assert (await page.evaluate("bellProbe()"))["playhouse"]["lamps"] == 1
    saved = await page.evaluate("localStorage.getItem('wizzard.bellwake.desktop.v1')")
    if extended:
        await use("Runner")
        assert (await use("Maker"))["works"]["signals"]["paperCredit"] == 2
        assert (await use("Door"))["district"] == "Bellmarket"
        assert (await use("Talk"))["number"] == 1
        await page.mouse.up()
        await page.evaluate("s=>localStorage.setItem('wizzard.bellwake.desktop.v1',s)", saved)
        await start()
    assert (await use("Maker"))["works"]["signals"]["paperCredit"] == 1
    assert (await use("Door"))["district"] == "Bellmarket"
    state = await use("Talk")
    assert state["number"] == 1 and "voice" in await page.locator("#words").inner_text()
    if extended:
        fresh = await page.evaluate("localStorage.getItem('wizzard.bellwake.desktop.v1')")
        for ending, credit, word in ((33, 1, "bellmender"), (34, 2, "lock runner")):
            fixture = json.loads(fresh)
            fixture["number"] = ending
            await page.mouse.up()
            await page.evaluate(
                "s=>localStorage.setItem('wizzard.bellwake.desktop.v1',s)",
                json.dumps({"number": ending, "leaves": 31}),
            )
            await start()
            assert (await use("Playhouse"))["district"] == "PaperCourt"
            assert (await use("Door"))["number"] == ending
            if credit == 2:
                fixture["works"] = json.loads(saved)["works"]
            await page.mouse.up()
            await page.evaluate(
                "s=>localStorage.setItem('wizzard.bellwake.desktop.v1',s)", json.dumps(fixture)
            )
            await start()
            if credit == 2:
                await use("Runner")
                await use("Door")
            await use("Talk")
            assert word in await page.locator("#words").inner_text()
    (out / "paper-theatre.json").write_text(
        json.dumps(
            dict(
                scenes=4,
                propReels=3,
                musicalCues=4,
                activeSeconds=state["secondsByPlace"]["PaperCourt"],
                creditsTested=2 if extended else 1,
            ),
            indent=2,
        )
        + "\n"
    )
