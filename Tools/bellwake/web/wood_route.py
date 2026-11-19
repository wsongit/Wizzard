"""Walk the three listening walks using player input and test each restoration."""

import json


async def restore_wood(act, page, start, out, extended=False):
    grove_views = set()

    async def use(name):
        sample = await act("A_" + name)
        if sample["district"] == "RowanHollow":
            cells = sample["grove"]
            assert len(cells) == 12 and all(near != far for near, far in cells), name
            grove_views.add(tuple(near for near, far in cells))
        return sample

    async def face(angle):
        await page.evaluate(
            """offset=>{
          const s=bellProbe(),[x,,z]=s.sight.target;
          const yaw=Math.atan2(s.feet[0]-x,s.feet[2]-z)+offset;
          const delta=Math.atan2(Math.sin(yaw-s.yaw),Math.cos(yaw-s.yaw));
          dispatchEvent(new PointerEvent("pointermove",{movementX:Math.round(-delta/.0035)}));
        }""",
            angle,
        )

    async def book():
        await page.keyboard.press("j")
        await page.wait_for_selector("#survey:visible")
        await page.keyboard.press("j")
        await page.mouse.up()
        await page.mouse.down()

    async def take(name):
        s = await use(name)
        assert s["sight"], name
        await face(1)
        await page.wait_for_function(
            "bellProbe().sight && !bellProbe().sight.linedUp && bellProbe().forestAudio?.position>1"
        )
        if extended:
            await page.keyboard.press("e")
            assert (await page.evaluate("bellProbe()"))["sight"]
            await face(-1)
            await page.wait_for_function("bellProbe().forestAudio?.position < -1")
        await face(0)
        await page.wait_for_function(
            "bellProbe().sight?.linedUp && bellProbe().forestAudio?.playing"
        )
        await page.keyboard.press("e")
        await page.wait_for_function(
            "flag=>!bellProbe().sight && !bellProbe().forestAudio && bellProbe().works.signals[flag]",
            arg="heard" + name,
        )

    assert (await page.evaluate("bellProbe()"))["district"] == "RowanHollow"
    await use("Linn")
    await book()
    if extended:
        assert (await use("Gate"))["district"] == "RowanHollow"
        assert (await use("Spill"))["works"]["signals"]["rainMended"] == 0
    await take("RainWest")
    await take("RainEast")
    await use("Ridge")
    await use("Ridge")
    await use("Sill")
    s = await use("Spill")
    assert s["works"]["signals"]["rainMended"] == 1
    await page.mouse.up()
    await start()
    assert (await page.evaluate("bellProbe()"))["works"] == s["works"]
    await take("RootWest")
    await take("RootEast")
    await use("Bark")
    if extended:
        await use("Short")
        assert (await use("Long"))["works"]["signals"]["drumBeat"] == 0
    for key in ("Short", "Middle", "Long", "Short"):
        s = await use(key)
    assert s["works"]["signals"]["rootMended"] == 1
    await take("WrenEast")
    await take("WrenWest")
    if extended:
        assert (await use("Breath"))["works"]["signals"]["birdLoads"] == 0
    for turns in (1, 2, 3):
        for _ in range(turns):
            await use("Slide")
        s = await use("Breath")
    assert s["works"]["signals"]["wrenMended"] == 1
    await book()
    end = await use("Gate")
    assert (
        end["district"] == "RootChoir"
        and end["forestAudio"] is None
        and end["grove"] == []
    )
    assert len(grove_views) >= 4, grove_views
    await page.keyboard.press("j")
    await page.wait_for_function(
        "document.querySelector('#leaves img[data-illustration=RowanLinen]')?.naturalWidth===768"
    )
    await page.keyboard.press("j")
    (out / "rowan-hollow.json").write_text(
        json.dumps(
            dict(
                bearings=6,
                voices=3,
                differentGroveViews=len(grove_views),
                savedAndResumed=True,
                testedWrongBearings=extended,
                activeSeconds=end["secondsByPlace"]["RowanHollow"],
            ),
            indent=2,
        )
        + "\n"
    )


async def wood_walk_trip(act, page, start, out):
    """A first morning and both epilogues can visit without giving up their story progress."""
    results = []
    for stage in (0, 33, 34):
        await page.mouse.up()
        if stage:
            await page.evaluate(
                "v=>localStorage.setItem('wizzard.bellwake.desktop.v1',v)",
                json.dumps({"number": stage, "leaves": 31}),
            )
        await start()
        before = await page.evaluate("bellProbe()")
        assert before["district"] == "Bellmarket" and before["number"] == stage
        forest = await act("A_WoodWalk")
        assert forest["district"] == "RowanHollow" and forest["works"]["returnTicket"]
        assert forest["works"]["camp"] == "RestLinn"
        book = await act("A_Linn")
        assert book["works"]["signals"]["woodBook"] == 1
        await page.mouse.up()
        await start()
        restored = await page.evaluate("bellProbe()")
        assert (
            restored["district"] == "RowanHollow" and restored["works"] == book["works"]
        )
        after = await act("A_Gate")
        assert (
            after["district"] == "Bellmarket"
            and after["number"] == stage
            and after["leaves"] == before["leaves"]
        )
        journal = json.loads(
            await page.evaluate("localStorage.getItem('wizzard.bellwake.desktop.v1')")
        )
        assert not journal["works"]["returnTicket"]
        if stage == 0:
            second = await act("A_WoodWalk")
            assert second["works"]["signals"]["woodBook"] == 1
            await act("A_Gate")
            assert (await act("A_Talk"))["district"] == "Bellmarket"
            assert (await act("A_Playhouse"))["district"] == "PaperCourt"
        results.append(stage)
    (out / "wood-walk.json").write_text(
        json.dumps(
            {
                "returnedStoryStates": results,
                "reloadInForest": True,
                "firstMorningTheatreStillAvailable": True,
            },
            indent=2,
        )
        + "\n"
    )
