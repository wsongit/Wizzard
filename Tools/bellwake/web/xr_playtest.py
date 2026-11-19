"""Exercise the real WebXR input boundary with Meta's emulated Quest controllers."""

import asyncio, sys, subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
harness = subprocess.check_output(
    [str(here / "node_modules/.bin/esbuild"), "--bundle", "--format=iife", "--loader=js"],
    input="import {XRDevice,metaQuest3} from 'iwer'; window.testDevice=new XRDevice(metaQuest3);testDevice.installRuntime({forceInstall:true,polyfillLayers:false});",
    cwd=here,
    text=True,
)

from playwright.async_api import async_playwright


async def run():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
        )
        p = await b.new_page(viewport={"width": 630, "height": 380})
        errors = []
        p.on("pageerror", lambda e: (print("error", e, flush=True), errors.append(str(e))))
        p.on("console", lambda m: print(m.type, m.text[:180], flush=True) if m.type == "error" else None)
        await p.add_init_script(script=harness)
        await p.goto(sys.argv[1])
        await p.wait_for_selector("#start:enabled")
        await p.click("#vr")
        await p.wait_for_function("bellProbe().vr && bellProbe().palms.every(Boolean)", timeout=35000)
        print("entry", await p.evaluate("bellProbe()"), flush=True)
        await p.evaluate("testDevice.controllers.right.updateButtonValue('a-button',1)")
        await p.wait_for_function("bellProbe().book")
        await p.evaluate("testDevice.controllers.right.updateButtonValue('a-button',0)")
        await p.wait_for_timeout(350)
        await p.evaluate("testDevice.controllers.right.updateButtonValue('a-button',1)")
        await p.wait_for_function("!bellProbe().book")
        await p.evaluate("testDevice.controllers.right.updateButtonValue('a-button',0)")
        # Crouch, plant the right palm, then sweep it backwards against the floor.
        await p.evaluate(
            "testDevice.position.set(0,.85,0);testDevice.controllers.right.position.set(.22,.05,-.45)"
        )
        await p.wait_for_function("bellProbe().planted[1]", timeout=8000)
        before = await p.evaluate("bellProbe().vrHead")
        print("plant", before, flush=True)
        for i in range(12):
            await p.evaluate("(i)=>testDevice.controllers.right.position.set(.22,.025,-.45+.048*i)", i)
            await p.wait_for_timeout(55)
        after = await p.evaluate("bellProbe().vrHead")
        print("push", after, flush=True)
        assert after[2] < before[2] - 0.18
        await p.evaluate(
            "testDevice.controllers.right.position.set(.3,1.1,-.3);testDevice.position.set(-.8,1.65,-2.4)"
        )
        await p.wait_for_function("bellProbe().focus==='A_Talk'", timeout=10000)
        await p.evaluate("testDevice.controllers.right.updateButtonValue('trigger',1)")
        await p.wait_for_function("bellProbe().number===1")
        await p.evaluate("testDevice.controllers.right.updateButtonValue('trigger',0)")
        await p.evaluate("testDevice.controllers.right.updateAxes('thumbstick',1,0)")
        await p.wait_for_function("Math.abs(bellProbe().vrForward[0])>.5")
        await p.evaluate(
            "testDevice.controllers.right.updateAxes('thumbstick',0,0);testDevice.controllers.left.connected=false"
        )
        await p.wait_for_function("!bellProbe().palms[0]")
        await p.evaluate("testDevice.controllers.left.connected=true")
        await p.wait_for_function("bellProbe().palms[0]")
        for room in [5,1,6,2,7,0]:
            await p.evaluate("room => bellTravel(room)", room)
            await p.wait_for_function("bellProbe().vr && bellProbe().sets === 1 && bellProbe().palms.every(Boolean)")
        await p.evaluate("testDevice.activeSession.end()")
        await p.wait_for_function("!bellProbe().vr")
        assert not errors, errors
        print(
            "PASS emulated Quest 3 stereo entry, both grips, journal, planted-hand displacement and Tavi trigger",
            flush=True,
        )
        await b.close()


asyncio.run(run())
