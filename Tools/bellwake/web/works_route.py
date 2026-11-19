"""Normal-input route through all three trades; reuse it in the full campaign playthrough."""

import json


async def complete_works(act, page, start, out):
    homes = []

    async def use(keys):
        result = None
        for name in keys.split():
            result = await act("A_" + name)
        return result

    def district(state, key):
        assert state["district"] == key, (key, state["district"])
        homes.append(key)

    state = await page.evaluate("bellProbe()")
    district(state, "SumpHall")
    district(await use("Heart"), "SumpHall")
    district(await use("Nema Roll Intake"), "TwinIntake")
    await use("Fen Float Spring West DrainA West Spring West")
    state = await page.evaluate("bellProbe()")
    assert state["works"]["signals"]["deep"] == 4
    await page.mouse.up()
    await start()
    assert (await page.evaluate("bellProbe()"))["works"] == state["works"]
    district(await use("Float Archive"), "FloodLedger")
    await use("Orrel Page1 Page2 Mill Roof Oar Mill Reed Take")
    district(await use("Short"), "WeighHouse")
    await use("Brannic Brake One Two Four Four Brake")
    district(await use("Kiln"), "CastingBed")
    await use("Book Cool Sand Wax Pour Vent Cool Ossa Take")
    district(await use("Short"), "LanternCourt")
    await use("Etching Left Left Catch Fork Right Right Right Catch Iris")
    district(await use("Loft"), "OrreryLoft")
    await use("Vane Nest Bay Oak Oak Wren Wren Wren Tide Tide Tide Take")
    state = await use("Short")
    district(state, "SumpHall")
    assert all(state["works"]["signals"][x] for x in ["reed", "yoke", "glass"])
    state = await use("Nema")
    assert state["works"]["signals"]["named"] == 1
    district(await use("Heart"), "EchoRotunda")
    await use("Score River Forge Sky River Forge Sky River Sky Listen")
    state = await use("Final")
    district(state, "Wrenfall")
    state = await complete_coast(act, page, start, out)
    from engine_route import complete_engine
    state = await complete_engine(act,page,start,out)
    district(state, "StillBelfry")
    assert state["works"] is None
    (out / "underworks.json").write_text(
        json.dumps(
            {
                "visits": homes,
                "nightRollRestored": True,
                "wetGaugeSurvivedReload": True,
                "witnesses": ["reed", "yoke", "glass"],
                "activeSeconds": state["secondsByPlace"],
            },
            indent=2,
        )
    )


async def complete_coast(act, page, start, out):
    async def use(keys):
        for name in keys.split():
            state = await act("A_" + name)
        return state

    await use("Depth Pilot Map Depth")
    for name in ["Transit", "Lookout"]:
        state = await use(name)
        assert state["sight"] and not state["sight"]["linedUp"], (name, state["sight"])
        await page.keyboard.press("e")
        assert (await page.evaluate("bellProbe()"))["sight"], (
            "off-target sighting was accepted"
        )
        await page.evaluate("""() => {
          const s=bellProbe(),[x,y,z]=s.sight.target;
          const dx=x-s.feet[0],dz=z-s.feet[2],yaw=Math.atan2(-dx,-dz);
          const diff=Math.atan2(Math.sin(yaw-s.yaw),Math.cos(yaw-s.yaw));
          const pitch=Math.atan2(y-(s.feet[1]+1.36),Math.hypot(dx,dz));
          dispatchEvent(new PointerEvent('pointermove',{movementX:Math.round(-diff/.0035),movementY:Math.round((s.pitch-pitch)/.0035)}));
        }""")
        await page.wait_for_function("bellProbe().sight?.linedUp", timeout=4500)
        await page.keyboard.press("e")
        await page.wait_for_function("!bellProbe().sight")
    await use("Bell")
    state = await use("Wing")
    assert state["works"]["signals"]["signalBar"] == 1
    await page.mouse.up()
    await start()
    assert (await page.evaluate("bellProbe()"))["works"] == state["works"]
    before = await use("Bell Star")
    state = await use("Launch")
    await page.wait_for_function("bellProbe().crew", timeout=25000)
    arrived = await page.evaluate("bellProbe()")
    distance = (
        sum((a - b) ** 2 for a, b in zip(before["vessel"], arrived["vessel"])) ** 0.5
    )
    assert distance > 25, (before["vessel"], arrived["vessel"])
    assert state["works"]["signals"]["landed"] == 1
    coast = state["works"]
    state = await use("Book")
    assert state["district"] == "DrumHouse"
    (out / "coast.json").write_text(
        json.dumps(
            dict(
                final=state["district"],
                route=coast,
                voyageDisplacementMetres=round(distance, 2),
                opticalBearings=2,
                activeSeconds=state["secondsByPlace"]["Wrenfall"],
            ),
            indent=2,
        )
    )
    return state
