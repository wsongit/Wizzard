"""Exercise the production room lifecycle without resetting the tab between trips."""

import asyncio
import json
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright


async def main():
    url, destination = sys.argv[1:3]
    errors, requests, samples = [], [], []
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            executable_path=os.getenv("CHROME", "/usr/bin/chromium"),
            args=[
                "--no-sandbox",
                "--use-angle=swiftshader",
                "--enable-unsafe-swiftshader",
            ],
        )
        page = await browser.new_page(viewport={"width": 768, "height": 432})
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.on("request", lambda req: requests.append(req.url))
        devtools = await page.context.new_cdp_session(page)
        await page.goto(url)
        await page.click("#start", timeout=60000)
        initial = [u for u in requests if ".glb" in u]
        if await page.evaluate("window.BELLWAKE.streamed"):
            assert len(initial) == 1 and "Bellmarket" in initial[0], initial
        await page.evaluate("""() => {
            window.gaps = []; let prev;
            const tick = t => {if(prev !== undefined) gaps.push(t-prev); prev=t; requestAnimationFrame(tick)};
            requestAnimationFrame(tick);
        }""")
        frame_routes = {"--press-keeper-frames": (34,4), "--keeper-frames": (4,), "--press-frames": (34,), "--wards": range(17,22), "--parish-frames": (28,29,30), "--field-frames": (0,27,31,32,33)}
        districts = next((rooms for flag, rooms in frame_routes.items() if flag in sys.argv), None)
        if districts is not None:
            for index in districts:
                await page.evaluate("i=>bellTravel(i)",index)
                sample=await page.evaluate("""async() => {
                    const frame=()=>new Promise(requestAnimationFrame);
                    for(let i=0;i<90;i++) await frame();
                    gaps.length=0;
                    dispatchEvent(new KeyboardEvent('keydown',{code:'ArrowLeft'}));
                    for(let i=0;i<90;i++) await frame();
                    dispatchEvent(new KeyboardEvent('keyup',{code:'ArrowLeft'}));
                    const s=bellProbe(), sorted=gaps.slice().sort((a,b)=>a-b);
                    return {district:s.district,samples:sorted.length,scale:s.ratio,
                        medianMs:sorted[Math.floor(sorted.length*.5)],p95Ms:sorted[Math.floor(sorted.length*.95)],
                        calls:s.calls,triangles:s.tris};
                }""")
                samples.append(sample)
                print(sample,flush=True)
            assert not errors,errors
            Path(destination).write_text(json.dumps({"renderer":"Chromium SwiftShader","samples":samples},indent=2)+"\n")
            await browser.close()
            return
        route = [27, 5, 17,18,19,20,21, 1, 6, 28, 29, 30, 28, 2, 31, 32, 31, 7, 3, 34, 33, 8, 9, 10, 11, 12, 13, 14, 15, 16, 22, 23, 22, 24, 22, 25, 22, 26, 4, 0]
        if "--keeper" in sys.argv:
            route=[26,4,0,4,0]
        if "--press" in sys.argv:
            route=[3,34,33,34,0]
        if "--pilots" in sys.argv:
            route=[3,33,8,33,0]
        if "--swallow" in sys.argv:
            route = [2,31,32,31,7,31,0]
        if "--parish" in sys.argv:
            route = [28,29,30,29,28,2,0]
        for lap in range(3):
            for room in route:
                sample = await page.evaluate(
                    """async room => {
                    const frames = async n => {while(n--) await new Promise(requestAnimationFrame)};
                    const start = performance.now(); gaps.length = 0;
                    await bellTravel(room); await frames(3);
                    const load = Math.round(performance.now()-start), spike = Math.max(...gaps);
                    gaps.length=0;
                    dispatchEvent(new KeyboardEvent("keydown",{code:"KeyW"}));
                    await frames(24);
                    dispatchEvent(new KeyboardEvent("keyup",{code:"KeyW"}));
                    const s=bellProbe();
                    const sorted=gaps.slice().sort((a,b)=>a-b);
                    return {room,district:s.district,loadMs:load,maxTravelFrameMs:Math.round(spike),
                       walkP95Ms:Math.round(sorted[Math.floor(sorted.length*.95)]),gpu:s.gpu,
                       sets:s.sets,trees:s.trees,music:s.music,musicTheme:s.musicTheme,musicGeneration:s.musicGeneration,effects:s.effects,
                       floor:s.feet[1], errors:document.getElementById('error').textContent};
                }""",
                    room,
                )
                expected_score = {"GloamingPress":"SilverBath","GlassRookery":"GlassPilots","DriftFen":"AlderFerry","SwallowLock":"SwallowWater"}.get(sample["district"])
                if expected_score:
                    assert sample["musicTheme"] == expected_score, sample
                assert sample["sets"] == sample["trees"] == sample["music"] == 1
                assert sample["effects"] <= 4 and abs(sample["floor"]) < 3, sample
                assert not sample.pop("errors"), sample
                # Force collection only after the timing sample; weak handles cannot retain the old world.
                await devtools.send("HeapProfiler.collectGarbage")
                sample["retiredAlive"] = await page.evaluate("bellProbe().retiredAlive")
                assert sample["retiredAlive"] == 0, sample
                if samples and sample["musicTheme"] == samples[-1]["musicTheme"]:
                    assert (
                        sample["musicGeneration"] == samples[-1]["musicGeneration"]
                    ), sample
                if lap:
                    assert samples[-len(route)]["gpu"] == sample["gpu"], (
                        samples[-len(route)],
                        sample,
                    )
                samples.append(sample)
                print(sample, flush=True)
        if initial:
            # Simulate a lost asset request. The retry must restore the committed checkpoint.
            await page.route("**/RootChoir-*.glb.gz", lambda route: route.abort())
            await page.evaluate("() => bellTravel(1)")
            await page.get_by_text("Reload last checkpoint").wait_for()
            await page.unroute("**/RootChoir-*.glb.gz")
            await page.get_by_text("Reload last checkpoint").click()
            await page.wait_for_selector("#start:enabled")
            assert (await page.evaluate("bellProbe()"))["room"] == 0
        assert not errors, errors
        Path(destination).write_text(
            json.dumps(
                {"renderer": "Chromium SwiftShader", "laps": 3, "samples": samples},
                indent=2,
            )
            + "\n"
        )
        await browser.close()


asyncio.run(main())
