"""Play the instrumented offline bundle through ordinary keyboard and look events.
Serve a --test build on loopback. The read-only probe exposes positions and counters.
Usage: python playtest.py URL AUDIT_DIRECTORY RESULT_DIRECTORY
"""

import asyncio, json, math, sys, os, heapq, time
from pathlib import Path
from playwright.async_api import async_playwright
from works_route import complete_works, complete_coast

url, navdir, outdir = sys.argv[1:4]
out = Path(outdir)
out.mkdir(parents=True, exist_ok=True)
rooms = ["Bellmarket", "RootChoir", "Reedwater", "CinderLens", "StillBelfry"]
metrics = []
errors = []


def route(grid, start, goal):
    cells = set(map(tuple, grid["reach"]))
    targets = set(map(tuple, grid["goals"][goal]))
    node = min(cells, key=lambda c: (c[0] - start[0]) ** 2 + (c[1] - start[1]) ** 2)
    queue = [(0, node)]
    prev = {node: None}
    cost = {node: 0}
    last = None
    while queue:
        d, v = heapq.heappop(queue)
        if v in targets:
            last = v
            break
        if d > cost[v]:
            continue
        for dx, dz in [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (-1, 1),
            (1, -1),
            (-1, -1),
        ]:
            w = (v[0] + dx, v[1] + dz)
            if (
                w not in cells
                or (v[0] + dx, v[1]) not in cells
                or (v[0], v[1] + dz) not in cells
            ):
                continue
            val = d + math.hypot(dx, dz)
            if val < cost.get(w, 1e10):
                cost[w] = val
                prev[w] = v
                heapq.heappush(queue, (val, w))
    assert last
    path = []
    while last != None:
        path.append(last)
        last = prev[last]
    path.reverse()
    # Remove intermediate collinear grid points. Keep every audited corner.
    simple = []
    for v in path:
        if len(simple) > 1:
            a, b = simple[-2:]
            u = (b[0] - a[0], b[1] - a[1])
            w = (v[0] - b[0], v[1] - b[1])
            if u[0] * w[1] == u[1] * w[0] and u[0] * w[0] + u[1] * w[1] > 0:
                simple.pop()
        simple.append(v)
    return [
        [grid["offset"] + i * grid["step"], -(grid["offset"] + j * grid["step"])]
        for i, j in simple
    ]


drive = """async ({points,id})=>{
 const frame=()=>new Promise(r=>requestAnimationFrame(r)), key=(type,code)=>dispatchEvent(new KeyboardEvent(type,{code}));
 const aim=(x,z,vertical=null)=>{const p=bellProbe(),dx=x-p.feet[0],dz=z-p.feet[2],yaw=Math.atan2(-dx,-dz);
 let diff=Math.atan2(Math.sin(yaw-p.yaw),Math.cos(yaw-p.yaw));const pitch=vertical===null?0:Math.atan2(vertical-(p.feet[1]+1.36),Math.hypot(dx,dz));
 dispatchEvent(new PointerEvent('pointermove',{movementX:Math.round(-diff/.0035),movementY:Math.round((p.pitch-pitch)/.0035)}));};
 let frames=0;key('keydown','ShiftLeft');key('keydown','KeyW');
 try{
 for(const [x,z] of points){while(true){const p=bellProbe();
 if(Math.hypot(p.feet[0]-x,p.feet[2]-z)<.29)break;
 if(++frames>1100)throw Error('Route stalled '+id+' '+JSON.stringify({p:p.feet,x,z,yaw:p.yaw}));
 aim(x,z);await frame();}}
 }finally{key('keyup','KeyW');key('keyup','ShiftLeft');}
 let p=bellProbe(),m=p.markers[id];aim(m[0],m[2],m[1]);
 for(let i=0;i<60;i++){await frame();p=bellProbe();if(p.focus===id){key('keydown','KeyE');key('keyup','KeyE');return;}}
 throw Error('Focus mismatch '+id+' '+JSON.stringify(p));
}"""


async def run():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(
            executable_path=os.environ.get("CHROME", "/usr/bin/chromium"),
            args=[
                "--no-sandbox",
                "--use-angle=swiftshader",
                "--enable-unsafe-swiftshader",
                "--ignore-gpu-blocklist",
            ],
        )
        page = await b.new_page(viewport={"width": 768, "height": 432})
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on(
            "console", lambda m: errors.append(m.text) if m.type == "error" else None
        )

        async def start():
            await page.goto(url)
            await page.wait_for_selector("#start:enabled", timeout=60000)
            await page.click("#start")
            await page.mouse.move(380, 200)
            await page.mouse.down()

        coast_only = "--coast" in sys.argv
        works_only = "--works" in sys.argv
        target_post = "--last-post" in sys.argv
        glasscut_only = "--glasscut" in sys.argv
        nameplate = "--night-roll" in sys.argv
        endings_only = "--endings" in sys.argv or nameplate
        if target_post or glasscut_only or endings_only or works_only or coast_only:
            saved = {"number": 13, "leaves": 7}
            if works_only:
                saved = {"number": 21, "leaves": 15}
            if coast_only:
                saved = {
                    "number": 21,
                    "leaves": 15,
                    "works": {"active": True, "chamber": 8},
                }
            if endings_only:
                saved = {"number": 31, "leaves": 31}
            if nameplate:
                plan = json.loads(
                    (
                        Path(__file__).resolve().parents[3]
                        / "Assets/Resources/Bellwake/Underworks.json"
                    ).read_text()
                )
                saved["works"] = {"badges": 1 << plan["flags"].index("named")}
            if target_post:
                saved["passage"] = {
                    "completed": 2,
                    "active": True,
                    "sheet": 6,
                    "position": 0,
                    "logs": 3,
                }
            await page.add_init_script(
                "if(!sessionStorage.fixture){localStorage.setItem('wizzard.bellwake.desktop.v1',"
                + json.dumps(json.dumps(saved))
                + ");sessionStorage.fixture='1'}"
            )
        await start()
        timed = "--timed" in sys.argv
        run_start = time.monotonic()

        async def act(id):
            p = await page.evaluate("bellProbe()")
            k = p["room"]
            g = json.loads((Path(navdir) / (p["district"] + ".json")).read_text())
            if p["passage"] and id.startswith("A_Key"):
                # Read the sloped chart from the pilot's position in front of the four keys.
                g["goals"][id] = [
                    c
                    for c in g["goals"][id]
                    if abs(g["offset"] + c[0] * g["step"]) <= 0.5
                    and -6.5 <= g["offset"] + c[1] * g["step"] <= -5.5
                ]
            if p["district"] == "Bellmarket" and id == "A_Talk":
                # Tavi speaks from beneath the awning. Approach her from its open frontage.
                g["goals"][id] = [
                    c
                    for c in g["goals"][id]
                    if -2.7 <= g["offset"] + c[0] * g["step"] <= -1.3
                    and -11.6 <= g["offset"] + c[1] * g["step"] <= -10
                ]
            if p.get("works"):
                # Stand in front of the station as a player reading its plaque would.
                mx, my, mz = p["markers"][id]
                front = [
                    c
                    for c in g["goals"][id]
                    if abs(g["offset"] + c[0] * g["step"] - mx) < 1.4
                    and 1.25 < -mz - (g["offset"] + c[1] * g["step"]) < 2.75
                ]
                if front:
                    g["goals"][id] = front
            path = route(
                g,
                [
                    (p["feet"][0] - g["offset"]) / g["step"],
                    (-p["feet"][2] - g["offset"]) / g["step"],
                ],
                id,
            )
            await page.evaluate(drive, {"points": path, "id": id})
            await page.wait_for_function("!bellProbe().busy", timeout=30000)
            after = await page.evaluate("bellProbe()")
            print(p["district"], id, "=>", after["number"], flush=True)
            return after

        async def profile():
            if timed:
                return
            await page.evaluate(
                "async()=>{for(let i=0;i<95;i++)await new Promise(requestAnimationFrame)}"
            )
            stats = await page.evaluate(
                """async()=>{let times=[],prev=await new Promise(requestAnimationFrame);for(let i=0;i<70;i++){const t=await new Promise(requestAnimationFrame);times.push(t-prev);prev=t}times.sort((a,b)=>a-b);let s=bellProbe();return {room:s.room,scale:s.ratio,medianMs:times[35],p95Ms:times[66],calls:s.calls,triangles:s.tris};}"""
            )
            metrics.append(stats)
            print("frames", stats, flush=True)
            await page.screenshot(path=str(out / (rooms[stats["room"]] + ".jpg")))

        async def passage(key):
            current = await page.evaluate("bellProbe()")
            assert current["district"] == key, current
            await act("A_Talk")
            await act("A_Gate")
            assert (await page.evaluate("bellProbe()"))["district"] == key
            solutions = []
            for sheet in range(9):
                if sheet % 3 == 0:
                    await act("A_Log" + str(sheet // 3))
                if sheet == 0:
                    await act("A_Hint")
                    await act(
                        "A_Key"
                        + str((await page.evaluate("bellProbe()"))["passage"]["hint"])
                    )
                    await act("A_Reset")
                moves = 0
                while True:
                    info = (await page.evaluate("bellProbe()"))["passage"]
                    if info["win"]:
                        break
                    assert (
                        info["sheet"] == sheet and 0 <= info["hint"] < 4 and moves < 75
                    ), info
                    await act("A_Key" + str(info["hint"]))
                    moves += 1
                    if sheet == 0 and moves == 2:
                        checkpoint = (await page.evaluate("bellProbe()"))["passage"]
                        await page.screenshot(path=str(out / (key + "-chart.jpg")))
                        await page.mouse.up()
                        await start()
                        assert (await page.evaluate("bellProbe()"))[
                            "passage"
                        ] == checkpoint
                solutions.append(moves)
                await act("A_Stamp")
            assert (await page.evaluate("bellProbe()"))["passage"]["logs"] == 7
            await act("A_Gate")
            assert (await page.evaluate("bellProbe()"))["passage"] is None
            (out / (key + ".json")).write_text(
                json.dumps(
                    {
                        "shortestMovesPlayed": solutions,
                        "witnessPosts": 3,
                        "midChartReload": True,
                    },
                    indent=2,
                )
            )

        if target_post:
            await act("A_Log2")
            step = (await page.evaluate("bellProbe()"))["passage"]["hint"]
            after = await act("A_Key" + str(step))
            assert after["passage"]["position"] != 0 and after["passage"]["logs"] == 7
            assert not errors, errors
            print(
                "PASS Glasscut resonance cradle to chart, first route input accepted",
                flush=True,
            )
            await b.close()
            return
        if coast_only:
            await complete_coast(act, page, start, out)
            assert not errors, errors
            await b.close()
            return
        if works_only:
            await act("A_Gate")
            await complete_works(act, page, start, out)
            await b.close()
            return
        if not endings_only:
            if glasscut_only:
                await act("A_Gate")
            else:
                await profile()
                await act("A_Talk")
                await act("A_Letter")
                await act("A_Gate")
                await passage("Saltwake")
                await profile()
                await act("A_Talk")
                await act("A_Key0")
                await act("A_Key2")
                await page.mouse.up()
                await start()  # saved partial melody survives reload
                await act("A_Key1")
                await act("A_Key0")
                await act("A_Letter")
                await act("A_Gate")
                await passage("RimePost")
                await profile()
                await act("A_Talk")
                await act("A_Key1")
                await act("A_Key0")
                await act("A_Key2")
                await act("A_Letter")
                await act("A_Gate")
            await passage("Glasscut")
            await profile()
            await act("A_Talk")
            await act("A_Key2")
            await act("A_Key0")
            await act("A_Key1")
            await act("A_Lens")
            await act("A_Letter")
            await act("A_Gate")
            await complete_works(act, page, start, out)
            await profile()
            await act("A_Letter")
            await act("A_Talk")
            for i in range(3):
                await act("A_Key1")  # three misses must allow a clean retry
            await act("A_Talk")
            await act("A_Key0")
            await act("A_Key2")
            await act("A_Key1")
        save = await page.evaluate(
            "localStorage.getItem('wizzard.bellwake.desktop.v1')"
        )
        final = await act("A_End0")
        assert final["ending"] == 1 and final["leaves"] == 31
        if timed:
            durations = final["secondsByPlace"]
            assert len(durations) == 17, durations
            (out / "known-route.json").write_text(
                json.dumps(
                    {
                        "method": "Fresh save, normal movement, keyboard interaction and chart hints. Includes all 27 dispatches, five leaves, the optional night roll, checkpoint reloads and a keeper retry.",
                        "firstEnding": final["ending"],
                        "elapsedSeconds": round(time.monotonic() - run_start, 2),
                        "activeSeconds": round(sum(durations.values()), 2),
                        "activeSecondsByPlace": {
                            place: round(seconds, 2)
                            for place, seconds in durations.items()
                        },
                    },
                    indent=2,
                )
                + "\n"
            )
        if nameplate:
            assert final["dedication"]
            await act("A_Nameplate")
        await act("A_Roster")
        await act("A_Talk")
        await page.mouse.up()
        await page.evaluate(
            "s=>localStorage.setItem('wizzard.bellwake.desktop.v1',s)", save
        )
        await start()
        final = await act("A_End1")
        assert final["ending"] == 2 and final["leaves"] == 31
        if nameplate:
            assert final["dedication"]
            await act("A_Nameplate")
        await act("A_Ina")
        await act("A_Talk")
        await page.keyboard.press("j")
        assert (await page.evaluate("bellProbe()"))["book"]
        await page.keyboard.press("j")
        assert not errors, errors
        (out / "playthrough.json").write_text(
            json.dumps(
                {
                    "viewport": [768, 432],
                    "renderer": "Chromium SwiftShader",
                    "framesPerRoom": 70,
                    "samples": metrics,
                    "endings": [1, 2],
                    "witnessLeaves": 5,
                    "errors": errors,
                },
                indent=2,
            )
        )
        await b.close()


if __name__ == "__main__":
    asyncio.run(run())
