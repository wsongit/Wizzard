"""Exercise the real WebXR input boundary with Meta's emulated Quest controllers."""

import asyncio, sys, subprocess, json
from pathlib import Path

here = Path(__file__).resolve().parent
harness = subprocess.check_output(
    [
        str(here / "node_modules/.bin/esbuild"),
        "--bundle",
        "--format=iife",
        "--loader=js",
    ],
    input="import {XRDevice,metaQuest3} from 'iwer'; window.testDevice=new XRDevice(metaQuest3);testDevice.installRuntime({forceInstall:true,polyfillLayers:false});",
    cwd=here,
    text=True,
)

from playwright.async_api import async_playwright


async def coast_crossing(page):
    # Tracked head and grip poses traverse the open coast. All actions use the controller trigger.
    await page.evaluate("""() => {
      window.walkSurvey = async (x,z) => {
        for(let i=0;i<350;i++) {
          const [hx,,hz]=bellProbe().vrHead,dx=x-hx,dz=z-hz,length=Math.hypot(dx,dz);
          if(length<.30) return;
          const k=Math.min(.29,length)/length,p=testDevice.position;
          p.set(p.x+dx*k,1.64,p.z+dz*k);
          testDevice.controllers.right.position.set(p.x+.23,1.30,p.z-.24);
          testDevice.controllers.left.position.set(p.x-.23,1.30,p.z-.24);
          await new Promise(r=>setTimeout(r,70));
        }
        throw Error("Headland tracked crossing stalled at "+bellProbe().vrHead);
      };
      window.sightToward = ([x,y,z]) => {
        const [hx,hy,hz]=bellProbe().vrHead,dx=x-hx,dy=y-hy,dz=z-hz;
        const yaw=Math.atan2(-dx,-dz)*.5,pitch=Math.atan2(dy,Math.hypot(dx,dz))*.5;
        testDevice.quaternion.set(Math.cos(yaw)*Math.sin(pitch), Math.sin(yaw)*Math.cos(pitch),
          -Math.sin(yaw)*Math.sin(pitch), Math.cos(yaw)*Math.cos(pitch));
      };
    }""")

    async def trigger(until):
        await page.evaluate(
            "testDevice.controllers.right.updateButtonValue('trigger',1)"
        )
        await page.wait_for_function(until, timeout=9000)
        await page.evaluate(
            "testDevice.controllers.right.updateButtonValue('trigger',0)"
        )
        await page.wait_for_timeout(180)

    await page.evaluate("walkSurvey(-4,11.8)")
    await page.evaluate("sightToward(bellProbe().markers.A_Pilot)")
    await page.wait_for_function("bellProbe().focus==='A_Pilot'")
    await trigger("bellProbe().works.signals.charter===1")
    for point in [(0, 15), (14, 15), (25, 12), (32, 8), (40, 7)]:
        await page.evaluate("([x,z])=>walkSurvey(x,z)", point)
    assert (await page.evaluate("bellProbe().vrHead"))[0] > 38
    await page.evaluate("sightToward(bellProbe().markers.A_Transit)")
    await page.wait_for_function("bellProbe().focus==='A_Transit'")
    await trigger("!!bellProbe().sight")
    await page.evaluate("sightToward(bellProbe().sight.target)")
    await page.wait_for_function("bellProbe().sight?.linedUp", timeout=9000)
    await trigger("bellProbe().works.signals.leading===1")
    print(
        "PASS tracked head beyond 38 m, shore pilot and offshore transit acquired by XR trigger",
        flush=True,
    )


async def orchard_checkpoint(browser):
    page = await browser.new_page(viewport={"width":630,"height":380})
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    await page.add_init_script(script=harness)
    # Begin at an unclaimed bench. Earning the tool and calling it both use tracked controllers.
    save={"number":2,"leaves":1,"passage":{"completed":1},"works":{"active":True,"chamber":9,"camp":"RestKnife"}}
    await page.add_init_script("localStorage.setItem('wizzard.bellwake.desktop.v1',"+json.dumps(json.dumps(save))+")")
    await page.goto(sys.argv[1])
    await page.click("#vr",timeout=60000)
    await page.wait_for_function("bellProbe().vr && bellProbe().district==='QuinceFold' && bellProbe().palms.every(Boolean)")
    await page.evaluate("testDevice.controllers.right.updateButtonValue('a-button',1)")
    await page.wait_for_function("bellProbe().vrMap")
    await page.evaluate("testDevice.controllers.right.updateButtonValue('a-button',0)")
    await page.wait_for_timeout(500)
    await page.evaluate("testDevice.controllers.right.updateButtonValue('a-button',1)")
    await page.wait_for_function("!bellProbe().book && !bellProbe().vrMap")
    await page.evaluate("testDevice.controllers.right.updateButtonValue('a-button',0)")
    await page.evaluate("""() => {
      const s=bellProbe(), [x,y,z]=s.markers.A_Knife, [hx,hy,hz]=s.vrHead;
      const yaw=Math.atan2(hx-x,hz-z)*.5, pitch=Math.atan2(y-hy,Math.hypot(x-hx,z-hz))*.5;
      testDevice.quaternion.set(Math.cos(yaw)*Math.sin(pitch),Math.sin(yaw)*Math.cos(pitch),
                                -Math.sin(yaw)*Math.sin(pitch),Math.cos(yaw)*Math.cos(pitch));
    }""")
    await page.wait_for_function("bellProbe().focus==='A_Knife'")
    await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',1)")
    await page.wait_for_function("bellProbe().works.signals.QuinceFoldKnife===1")
    await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',0)")
    await page.evaluate("testDevice.controllers.left.updateButtonValue('squeeze',1)")
    await page.wait_for_function("bellProbe().guide?.cells.length>1")
    pos=await page.evaluate("bellProbe().guide.pos")
    await page.wait_for_function("p=>Math.hypot(...bellProbe().guide.pos.map((v,i)=>v-p[i]))>.5",arg=pos)
    await page.evaluate("testDevice.controllers.left.updateButtonValue('squeeze',0)")
    await page.evaluate("testDevice.activeSession.end()")
    assert not errors,errors
    await page.close()
    print("PASS Quest controller survey, tool acquisition and articulated waywren flight",flush=True)


async def run():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(
            executable_path="/usr/bin/chromium",
            args=[
                "--no-sandbox",
                "--use-angle=swiftshader",
                "--enable-unsafe-swiftshader",
            ],
        )
        await orchard_checkpoint(b)
        if "--orchard" in sys.argv:
            await b.close()
            return
        p = await b.new_page(viewport={"width": 630, "height": 380})
        errors = []
        p.on(
            "pageerror",
            lambda e: (print("error", e, flush=True), errors.append(str(e))),
        )
        p.on(
            "console",
            lambda m: (
                print(m.type, m.text[:180], flush=True) if m.type == "error" else None
            ),
        )
        await p.add_init_script(script=harness)
        await p.goto(sys.argv[1])
        await p.wait_for_selector("#start:enabled")
        await p.click("#vr")
        await p.wait_for_function(
            "bellProbe().vr && bellProbe().palms.every(Boolean)", timeout=35000
        )
        print("entry", await p.evaluate("bellProbe()"), flush=True)
        await p.evaluate("testDevice.controllers.right.updateButtonValue('a-button',1)")
        await p.wait_for_function("bellProbe().book")
        await p.evaluate("testDevice.controllers.right.updateButtonValue('trigger',1)")
        await p.wait_for_function(
            "bellProbe().journalPage===1 && bellProbe().journalCaption.includes('witness leaf')"
        )
        await p.evaluate("testDevice.controllers.right.updateButtonValue('trigger',0)")
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
            await p.evaluate(
                "(i)=>testDevice.controllers.right.position.set(.22,.025,-.45+.048*i)",
                i,
            )
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
        for room in [5, 17, 18, 19, 20, 21, 1, 6, 2, 7, 8, 9, 11, 14, 15, 16, 0]:
            await p.evaluate("room => bellTravel(room)", room)
            await p.wait_for_function(
                "bellProbe().vr && bellProbe().sets === 1 && bellProbe().palms.every(Boolean)"
            )
            if room == 16:
                await coast_crossing(p)
            if room == 8:
                # Approach the night roll using tracked head motion in the hall, then use the real XR trigger.
                await p.wait_for_timeout(200)
                await p.evaluate("""async()=>{for(let i=0;i<22;i++){
                  testDevice.position.x-=.135;testDevice.position.z-=.10;
                  await new Promise(r=>setTimeout(r,40));
                }}""")
                await p.wait_for_function("bellProbe().focus==='A_Roll'", timeout=10000)
                await p.evaluate(
                    "testDevice.controllers.right.updateButtonValue('trigger',1)"
                )
                await p.wait_for_function("bellProbe().works.signals.admitted===1")
                await p.evaluate(
                    "testDevice.controllers.right.updateButtonValue('trigger',0)"
                )
        await p.evaluate("testDevice.activeSession.end()")
        await p.wait_for_function("!bellProbe().vr")
        assert not errors, errors
        print(
            "PASS emulated Quest 3 stereo entry, both grips, journal, planted-hand displacement and Tavi trigger",
            flush=True,
        )
        await b.close()


asyncio.run(run())
