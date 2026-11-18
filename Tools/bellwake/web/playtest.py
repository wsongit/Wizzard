"""Play the instrumented offline bundle through ordinary keyboard and look events.
Serve a --test build on loopback. The read-only probe exposes positions and counters.
Usage: python playtest.py URL AUDIT_DIRECTORY RESULT_DIRECTORY
"""

import asyncio, json, math, sys, os, heapq
from pathlib import Path
from playwright.async_api import async_playwright

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
        for dx, dz in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            w = (v[0] + dx, v[1] + dz)
            if w not in cells or (v[0] + dx, v[1]) not in cells or (v[0], v[1] + dz) not in cells:
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
    return [[grid["offset"] + i * grid["step"], -(grid["offset"] + j * grid["step"])] for i, j in simple]


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
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

        async def start():
            await page.goto(url)
            await page.wait_for_selector("#start:enabled", timeout=60000)
            await page.click("#start")
            await page.mouse.move(380, 200)
            await page.mouse.down()

        await start()

        async def act(id):
            p = await page.evaluate("bellProbe()")
            k = p["room"]
            g = json.loads((Path(navdir) / (rooms[k] + ".json")).read_text())
            path = route(
                g,
                [(p["feet"][0] - g["offset"]) / g["step"], (-p["feet"][2] - g["offset"]) / g["step"]],
                id,
            )
            await page.evaluate(drive, {"points": path, "id": id})
            await page.wait_for_function("!bellProbe().busy", timeout=30000)
            after = await page.evaluate("bellProbe()")
            print(rooms[k], id, "=>", after["number"], flush=True)
            return after

        async def profile():
            await page.evaluate(
                "async()=>{for(let i=0;i<95;i++)await new Promise(requestAnimationFrame)}"
            )
            stats = await page.evaluate(
                """async()=>{let times=[],prev=await new Promise(requestAnimationFrame);for(let i=0;i<70;i++){const t=await new Promise(requestAnimationFrame);times.push(t-prev);prev=t}times.sort((a,b)=>a-b);let s=bellProbe();return {room:s.room,scale:s.ratio,medianMs:times[35],p95Ms:times[66],calls:s.calls,triangles:s.tris};}"""
            )
            metrics.append(stats)
            print("frames", stats, flush=True)
            await page.screenshot(path=str(out / (rooms[stats["room"]] + ".jpg")))

        await profile()
        await act("A_Talk")
        await act("A_Letter")
        await act("A_Gate")
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
        await profile()
        await act("A_Talk")
        await act("A_Key1")
        await act("A_Key0")
        await act("A_Key2")
        await act("A_Letter")
        await act("A_Gate")
        await profile()
        await act("A_Talk")
        await act("A_Key2")
        await act("A_Key0")
        await act("A_Key1")
        await act("A_Lens")
        await act("A_Letter")
        await act("A_Gate")
        await profile()
        await act("A_Letter")
        await act("A_Talk")
        for i in range(3):
            await act("A_Key1")  # three misses must allow a clean retry
        await act("A_Talk")
        await act("A_Key0")
        await act("A_Key2")
        await act("A_Key1")
        save = await page.evaluate("localStorage.getItem('wizzard.bellwake.desktop.v1')")
        final = await act("A_End0")
        assert final["ending"] == 1 and final["leaves"] == 31
        await act("A_Roster")
        await act("A_Talk")
        await page.mouse.up()
        await page.evaluate("s=>localStorage.setItem('wizzard.bellwake.desktop.v1',s)", save)
        await start()
        final = await act("A_End1")
        assert final["ending"] == 2 and final["leaves"] == 31
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


asyncio.run(run())
