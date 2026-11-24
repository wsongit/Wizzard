"""Exercise exterior signs, lore, and return trips against a --streamed --test package."""

import asyncio
import math
import os
import sys
from playwright.async_api import async_playwright


async def run(url):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path=os.getenv("CHROME", "/usr/bin/chromium"),
            args=[
                "--no-sandbox",
                "--use-angle=swiftshader",
                "--enable-unsafe-swiftshader",
            ],
        )
        page = await browser.new_page(viewport={"width": 480, "height": 300})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        await page.goto(url)
        await page.click("#start", timeout=90000)
        await page.wait_for_function(
            "window.bellDoors && bellProbe().started && !bellProbe().busy"
        )
        keys = await page.evaluate(
            "BELLWAKE.story.rooms.concat(BELLWAKE.regions.map(r=>r.key),BELLWAKE.works.rooms.map(r=>r.key))"
        )
        rooms = await page.evaluate(
            "BELLWAKE.houses.districts.filter(r=>r.doors.length).map(r=>r.key)"
        )
        count = 0
        for index, key in enumerate([*keys, "HighroadBrowser"]):
            if key not in rooms:
                continue
            if key == "HighroadBrowser":
                await page.evaluate("bellTestHighroad()")
            else:
                await page.evaluate("i=>bellTravel(i)", index)
            doors = await page.evaluate("bellDoors()")
            for n, door in enumerate(doors):
                x, y, z = door["point"]
                nx, _, nz = door["normal"]
                found = False
                for distance, offset in [
                    (1.8, 0),
                    (1.15, 0),
                    (2.5, 0),
                    (1.6, 0.9),
                    (1.6, -0.9),
                    (0.65, 0),
                ]:
                    px, pz = (
                        x + nx * distance + nz * offset,
                        z + nz * distance - nx * offset,
                    )
                    feet = await page.evaluate("a=>bellGround(...a)", [px, y - 0.9, pz])
                    if not feet:
                        continue
                    yaw = math.atan2(px - x, pz - z)
                    pitch = math.atan2(y - feet[1] - 1.62, math.hypot(px - x, pz - z))
                    await page.evaluate("a=>bellStand(...a)", [feet, yaw, pitch])
                    await page.evaluate(
                        "()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))"
                    )
                    if await page.evaluate(
                        "n=>bellProbe().houseTarget===n", door["name"]
                    ):
                        found = True
                        break
                addr = f"{key} #{n + 1} {door['name'] or 'house'}"
                if not found:
                    print("UNREACHABLE", addr, flush=True)
                    errors.append(addr)
                    continue
                await page.keyboard.press("e")
                if door["openSpace"]:
                    await page.wait_for_function(
                        "!document.querySelector('#speech').hidden"
                    )
                    await page.keyboard.press("e")
                else:
                    await page.wait_for_function(
                        "bellProbe().insideHouse", timeout=8000
                    )
                    await page.evaluate("bellStand([0,.08,-.75],0,-.26)")
                    await page.keyboard.press("e")
                    await page.wait_for_function(
                        "bellProbe().houseReading", timeout=5000
                    )
                    await page.keyboard.press("e")
                    await page.evaluate("bellStand([0,.08,1.9],Math.PI,-.22)")
                    await page.keyboard.press("e")
                    await page.wait_for_function(
                        "!bellProbe().insideHouse", timeout=5000
                    )
                    returned = await page.evaluate("bellProbe().feet")
                    if math.hypot(returned[0] - feet[0], returned[2] - feet[2]) > 0.45:
                        errors.append("Return " + addr)
                count += 1
            print(key, len(doors), flush=True)
        print("Completed", count, "visits. Errors:", errors, flush=True)
        await browser.close()
        if errors:
            raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(run(sys.argv[1]))
