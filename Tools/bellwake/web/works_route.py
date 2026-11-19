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
