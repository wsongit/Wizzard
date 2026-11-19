"""Use the five mirror wheels and three plate shutters through ordinary player inputs."""

import json


async def print_plates(act, page, start, out, extended=False):
    state = await page.evaluate("bellProbe()")
    assert state["district"] == "GloamingPress"
    await act("A_Ledger")
    await act("A_Plan")
    await page.keyboard.press("j")
    await page.wait_for_function("!document.getElementById('survey').hidden")
    await page.keyboard.press("j")

    async def use(name):
        s = await act("A_" + name)
        if s["district"] == "GloamingPress":
            await page.wait_for_function("bellProbe().motionLeft===0")
            s = await page.evaluate("bellProbe()")
            sig = s["works"]["signals"]
            lit = sorted("LightPath" + k[4:] for k, v in sig.items() if k.startswith("line") and v)
            prints = sorted("Print" + n for n in ("Cradle", "Ladder", "Hand") if sig["print" + n])
            for dial in ("Fork", "North", "South", "Cross", "Crown"):
                assert s["press"]["angles"]["Mirror" + dial] == sig["dial" + dial] * 90
            for plate in ("Cradle", "Ladder", "Hand"):
                assert s["press"]["angles"]["Meter" + plate] == sig["lit" + plate] * -62
            assert s["press"]["light"] == lit and s["press"]["prints"] == prints
        return s

    if extended:
        assert (await use("Gate"))["district"] == "GloamingPress"
        assert (await use("Cradle"))["works"]["signals"]["glassProof"] == 0
        assert (await use("Hand"))["works"]["signals"]["glassProof"] == 0

    records = []
    # Trace each path on the floor. Light should take a different filter into the final two plates.
    for j, (route, shutter) in enumerate(
        (
            (("Fork", "North"), "Cradle"),
            (("Fork", "South", "Cross"), "Ladder"),
            (("Fork", "North", "Cross", "Crown"), "Hand"),
        )
    ):
        for n in route:
            state = await use(n)
            if j == 1 and n == "Fork":
                old = state
                await page.mouse.up()
                await start()
                await page.wait_for_function("bellProbe().motionLeft===0")
                state = await page.evaluate("bellProbe()")
                assert state["works"] == old["works"] and state["press"] == old["press"]
        assert state["works"]["signals"]["lit" + shutter] == 1, (shutter, state["works"]["signals"])
        if extended and j == 1:
            await use("Crown")  # Amber reaches the Hand shutter, which needs blue.
            assert (await use("Hand"))["works"]["signals"]["litHand"] == 0
            assert (await use("Ladder"))["works"]["signals"]["glassProof"] == 1
            await use("Crown")
        state = await use(shutter)
        assert state["works"]["signals"]["glassProof"] == j + 1
        records.append(
            dict(plate=shutter, beamSegments=state["press"]["light"], visiblePrints=state["press"]["prints"])
        )
    assert (await use("Gate"))["district"] == "GlassRookery"
    await page.keyboard.press("j")
    await page.wait_for_function("document.querySelector('#leaves img[alt*=prints]')?.naturalWidth === 768")
    await page.keyboard.press("j")
    assert await page.locator("#leaves img").count() == 0
    (out / "plates.json").write_text(
        json.dumps(
            dict(
                plates=records,
                reloadAfterMirror=True,
                wrongColourTested=extended,
                activeSeconds=state["secondsByPlace"]["GloamingPress"],
            ),
            indent=2,
        )
        + "\n"
    )
