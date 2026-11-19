"""Take six optical bearings and triangulate the three lost addresses using ordinary input."""

import json
import math


def intersection(a, b):
    (x, y), (dx, dy) = a
    (u, v), (du, dv) = b
    t = ((u - x) * dv - (v - y) * du) / (dx * dv - dy * du)
    return (round((x + t * dx) / 19) + 2, round((y + t * dy) / 19) + 2)


async def survey_parish(act, page, start, out, extended=False):
    async def use(name):
        return await act("A_" + name)

    async def take(name):
        state = await use(name)
        assert state["sight"], name
        mx, _, mz = state["markers"]["A_" + name]
        tx, _, tz = state["sight"]["target"]
        await page.evaluate("""() => {
          window.aimBearing = offset => {
            const s=bellProbe(),[x,y,z]=s.sight.target,dx=x-s.feet[0],dz=z-s.feet[2];
            const yaw=Math.atan2(-dx,-dz)+offset, diff=Math.atan2(Math.sin(yaw-s.yaw),Math.cos(yaw-s.yaw));
            const pitch=Math.atan2(y-(s.feet[1]+1.36),Math.hypot(dx,dz));
            dispatchEvent(new PointerEvent('pointermove',{movementX:Math.round(-diff/.0035),movementY:Math.round((s.pitch-pitch)/.0035)}));
          };
          aimBearing(1);
        }""")
        await page.wait_for_function("bellProbe().sight && !bellProbe().sight.linedUp")
        if extended:
            await page.keyboard.press("e")
            assert (await page.evaluate("bellProbe()"))["sight"], name
        await page.evaluate("aimBearing(0)")
        try:
            await page.wait_for_function("bellProbe().sight?.linedUp", timeout=6000)
        except Exception:
            print(
                "Sighting failed",
                name,
                await page.evaluate(
                    "({sight:bellProbe().sight,feet:bellProbe().feet})"
                ),
                flush=True,
            )
            raise
        await page.keyboard.press("e")
        await page.wait_for_function(
            "flag=>!bellProbe().sight && bellProbe().works.signals[flag]===1",
            arg="fix" + name,
        )
        return ((mx, -mz), (tx - mx, mz - tz))

    if extended:
        assert (await use("South"))["district"] == "SillwaterEbb"
    await use("Ada")
    if extended:
        await page.keyboard.press("j")
        await page.wait_for_selector("#survey:visible")
        await page.keyboard.press("j")
        await page.mouse.up()
        await page.mouse.down()
    low = [await take(n) for n in ("Willow", "Crane", "Net")]
    state = await use("North")
    assert (
        state["district"] == "SillwaterFlood" and state["works"]["camp"] == "RestNorth"
    )
    if extended:
        await page.mouse.up()
        await start()
        p = await page.evaluate("bellProbe()")
        assert (
            p["works"] == state["works"]
            and math.dist(p["feet"][::2], state["feet"][::2]) < 1
        )
    high = [await take(n) for n in ("Vestry", "Orchard", "Market")]
    assert (await use("Office"))["district"] == "SillwaterOffice"
    state = await use("Stamp")
    assert state["works"]["signals"]["parishJob"] == 0
    pins = []
    for job, (ebb, flood) in enumerate(zip(low, high)):
        cx, cy = intersection(ebb, flood)
        pins.append([cx, cy])
        assert state["threads"] == [
            "Thread" + str(job) + "0",
            "Thread" + str(job) + "1",
        ], state["threads"]
        for trace, value, negative, positive in (
            ("parishCol", cx, "West", "East"),
            ("parishRow", cy, "South", "North"),
        ):
            delta = value - state["works"]["signals"][trace]
            for _ in range(abs(delta)):
                state = await use(negative if delta < 0 else positive)
        assert state["works"]["signals"]["parishReady"] == 1, pins
        state = await use("Stamp")
        assert state["works"]["signals"]["parishJob"] == job + 1
    assert (await use("Seal"))["works"]["signals"]["parishSigned"] == 1
    state = await use("Door0")
    assert (
        state["district"] == "SillwaterEbb" and state["works"]["camp"] == "RestOffice"
    )
    state = await use("Gate")
    assert state["district"] == "Reedwater"
    (out / "sillwater.json").write_text(
        json.dumps(
            dict(
                bearings=6,
                chartPins=pins,
                activeSeconds={
                    k: v
                    for k, v in state["secondsByPlace"].items()
                    if k.startswith("Sillwater")
                },
            ),
            indent=2,
        )
        + "\n"
    )


async def packet_trip(act, page, start, out):
    async def use(name):
        return await act("A_" + name)

    for stage, leaves in ((0, 0), (6, 3), (33, 31), (34, 31)):
        save = {"number": stage, "leaves": leaves}
        if stage == 34:
            save["works"] = {"furtherBadges": [255]}
        await page.mouse.up()
        await page.evaluate(
            "s=>localStorage.setItem('wizzard.bellwake.desktop.v1',s)", json.dumps(save)
        )
        await start()
        before = await page.evaluate("bellProbe()")
        entered = await use("Packet")
        assert (
            entered["district"] == "SillwaterEbb" and entered["works"]["returnTicket"]
        )
        assert entered["works"]["camp"] == "RestGate"
        await page.mouse.up()
        await start()
        assert (await page.evaluate("bellProbe()"))["works"] == entered["works"]
        if stage == 33:
            await use("Ada")
            await use("North")
            await page.mouse.up()
            await start()
            assert (await page.evaluate("bellProbe()"))["district"] == "SillwaterFlood"
        after = await use("Gate")
        assert (
            after["district"] == before["district"]
            and after["number"] == stage
            and after["leaves"] == leaves
        )
        if stage == 34:
            await use("Ina")
            assert "my peg" in (await page.locator("#words").inner_text()).lower()
    for signed, destination in ((False, "SillwaterEbb"), (True, "Reedwater")):
        crossed = {
            "number": 5,
            "leaves": 3,
            "passage": {
                "active": True,
                "completed": 1,
                "sheet": 9,
                "position": 0,
                "logs": 7,
            },
            "works": {"furtherBadges": [255 if signed else 0]},
        }
        await page.mouse.up()
        await page.evaluate(
            "s=>localStorage.setItem('wizzard.bellwake.desktop.v1',s)",
            json.dumps(crossed),
        )
        await start()
        assert (await page.evaluate("bellProbe()"))["district"] == "RimePost"
        assert (await use("Gate"))["district"] == destination
    (out / "packet.json").write_text(
        json.dumps(
            {
                "legacyReedwater": True,
                "bothEpilogues": True,
                "reloadAtFlood": True,
                "freshMarketExcursion": True,
                "previouslySignedPassage": True,
            },
            indent=2,
        )
        + "\n"
    )
