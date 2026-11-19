"""The three keeper signals and Ina’s optional music-box coda via playable stations."""

import json


async def morning_song(act, page, start, out):
    assert (await act("A_MorningSong"))["keeper"]["verse"] == 0
    await act("A_Talk")
    for seal, test in (
        ("0", "s.yaw < -.96 && s.left < -1 && s.right < .10"),
        ("2", "s.yaw > .96 && s.right > 1 && s.left > -.10"),
        ("1", "Math.abs(s.yaw)<.08 && s.left < -.45 && s.right > .45"),
    ):
        await page.wait_for_function("()=>{const s=bellProbe().keeper;return s.lamp && " + test + "}")
        await act("A_Key" + seal)
    await page.wait_for_function("bellProbe().keeper.nod>.19")
    await act("A_MorningSong")
    tunes = ["020", "112", "201"]
    for bar, phrase in enumerate(tunes):
        await page.wait_for_function("ns=>bellProbe().recentTones.slice(-3).join('')===ns", arg=phrase)
        for beat, pitch in enumerate(phrase):
            state = await act("A_Key" + pitch)
            assert state["keeper"]["verse"] == 2 + bar * 3 + beat
        if bar == 0:
            assert (await act("A_Key0"))["keeper"]["verse"] == 4
            await page.mouse.up()
            await start()
            assert (await page.evaluate("bellProbe()"))["keeper"]["verse"] == 4
            await act("A_MorningSong")
    won = await page.evaluate("localStorage.getItem('wizzard.bellwake.desktop.v1')")
    for end in (1, 2):
        if end == 2:
            await page.mouse.up()
            await page.evaluate("s=>localStorage.setItem('wizzard.bellwake.desktop.v1',s)", won)
            await start()
        assert (await act("A_End" + str(end - 1)))["ending"] == end
        await act("A_Talk")
        phrase = await page.evaluate("i=>window.BELLWAKE.works.dawnEnding[i]", end - 1)
        assert phrase in await page.locator("#words").inner_text()
        await page.keyboard.press("j")
        assert "One knock from the landing" in await page.locator("#leaves").inner_text()
        await page.keyboard.press("j")
    (out / "morning-song.json").write_text(
        json.dumps(
            {
                "calls": ["Leaf", "Tide", "Ember"],
                "playedBars": tunes,
                "wrongNotePreservedFirstBar": True,
                "checkpointRestored": True,
                "endingReplies": 2,
            },
            indent=2,
        )
        + "\n"
    )
