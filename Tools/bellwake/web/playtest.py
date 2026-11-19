"""Play the instrumented offline bundle through ordinary keyboard and look events.
Serve a --test build on loopback. The read-only probe exposes positions and counters.
Usage: python playtest.py URL AUDIT_DIRECTORY RESULT_DIRECTORY [--timed | --resume]
"""

import asyncio, json, math, sys, os, heapq, time
from pathlib import Path
from playwright.async_api import async_playwright
from pilgrim_route import walk_wards, mercy_run, TRAILS
from works_route import complete_works, complete_coast
from route_checkpoint import RouteCheckpoint
from wood_route import restore_wood, wood_walk_trip
from quiet_route import morning_song
from press_route import print_plates
from pilot_route import lead_pilots, pilot_letters
from theatre_route import perform
from swallow_route import run_lock, fen_fare
from parish_route import survey_parish, packet_trip
from engine_route import complete_engine, complete_supper

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
 if(++frames>Math.max(1100,points.length*110))throw Error('Route stalled '+id+' '+JSON.stringify({p:p.feet,x,z,yaw:p.yaw}));
 aim(x,z);await frame();}}
 }finally{key('keyup','KeyW');key('keyup','ShiftLeft');}
 let p=bellProbe(),m=p.markers[id];aim(m[0],m[2],m[1]);
 if(p.district==="DriftFen" && id.startsWith("A_Find")){
   key("keydown","KeyQ");key("keyup","KeyQ");await frame();
   if(bellProbe().uncovered!==id)throw Error("Fork failed at "+id);
 }
 for(let i=0;i<60;i++){await frame();p=bellProbe();if(p.focus===id){const interact=p.district==="GlassRookery" && /^A_P[0-8]$/.test(id) && p.works.signals.rookWarden ? "KeyQ" : "KeyE";key("keydown",interact);key("keyup",interact);return;}}
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
        viewport={"width":384,"height":216} if "--compact" in sys.argv else {"width":768,"height":432}
        page = await b.new_page(viewport=viewport)
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

        ward_only=next((arg[7:] for arg in sys.argv if arg.startswith("--ward=")),None)
        engine_only = "--engine" in sys.argv
        supper_only = "--supper" in sys.argv
        coast_only = "--coast" in sys.argv
        works_only = "--works" in sys.argv
        song_only = "--morning-song" in sys.argv
        press_only = "--press" in sys.argv
        pilots_only = "--pilots" in sys.argv
        target_post = "--last-post" in sys.argv
        glasscut_only = "--glasscut" in sys.argv
        supper_ending = "--supper-ending" in sys.argv
        road_letters = "--road-letters" in sys.argv
        floodbook = "--flood-book" in sys.argv or road_letters or supper_ending
        nameplate = "--night-roll" in sys.argv or floodbook
        endings_only = "--endings" in sys.argv or nameplate
        parish_only = "--parish" in sys.argv
        lock_only="--swallow" in sys.argv
        wood_only="--wood" in sys.argv
        timed = "--timed" in sys.argv or "--resume" in sys.argv
        if timed and set(sys.argv[4:]) - {"--timed", "--resume", "--compact"}:
            raise ValueError("Use a full fresh campaign for timed routes")
        checkpoint = RouteCheckpoint(out, "--resume" in sys.argv) if timed else None
        if checkpoint:
            if checkpoint.entry and checkpoint.entry["stage"] == "Finished":
                print("Timed route already completed; see known-route.json and playthrough.json.")
                await b.close()
                return
            await checkpoint.restore(page)

        async def enter(stage):
            assert not errors, errors
            return checkpoint is None or await checkpoint.enter(stage, page)

        if wood_only or song_only or press_only or pilots_only or lock_only or parish_only or target_post or glasscut_only or endings_only or works_only or coast_only or ward_only or engine_only or supper_only:
            saved = {"number": 13, "leaves": 7}
            if wood_only:
                saved={"number":2,"leaves":1,"works":{"active":True,"chamber":27}}
            if song_only:
                saved={"number":22,"leaves":31}
            if lock_only:
                saved={"number":13,"leaves":7}
            if parish_only:
                saved={"number":6,"leaves":3,"works":{"active":True,"chamber":20}}
            if ward_only:
                saved={"number":2,"leaves":1,"passage":{"completed":1},"works":{"active":True,"chamber":9+list(TRAILS).index(ward_only)}}
            if works_only or pilots_only or press_only:
                saved = {"number": 21, "leaves": 15}
            if engine_only or supper_only:
                saved={"number":21,"leaves":15,"works":{"active":True,"chamber":14}}
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
                flags = ["named", "landed"] if floodbook else ["named"]
                if supper_ending: flags.append("supperServed")
                saved["works"] = {
                    "badges": sum(1 << plan["flags"].index(flag) for flag in flags)
                }
            if road_letters:
                machines=[0]*len(plan["machines"])
                idx=next(i for i,m in enumerate(plan["machines"]) if m["key"]=="RainCourt")
                m=plan["machines"][idx]
                machines[idx]=next(i for i,row in enumerate(m["rows"]) if row["values"][m["channels"].index("RainCourtArch")]==1)
                saved["works"]["machines"]=machines
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
        if checkpoint:
            checkpoint.started = time.monotonic()

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
        if "--wood-walk" in sys.argv:
            await wood_walk_trip(act,page,start,out)
            assert not errors,errors
            await b.close()
            return
        if wood_only:
            await restore_wood(act,page,start,out,extended=True)
            assert not errors,errors
            await b.close()
            return
        if song_only:
            await morning_song(act,page,start,out)
            assert not errors, errors
            await b.close()
            return
        if ward_only:
            await walk_wards(act,page,start,out,ward_only)
            assert not errors,errors
            await b.close()
            return
        if supper_only:
            await complete_supper(act,page,start,out)
            assert not errors,errors
            await b.close()
            return
        if engine_only:
            await complete_engine(act,page,start,out)
            assert not errors,errors
            await b.close()
            return
        if coast_only:
            await complete_coast(act, page, start, out)
            assert not errors, errors
            await b.close()
            return
        if works_only or pilots_only or press_only:
            await act("A_Gate")
            await print_plates(act,page,start,out,True)
            if press_only:
                assert not errors, errors
                await b.close()
                return
            await lead_pilots(act,page,start,out,True)
            if pilots_only:
                assert not errors,errors
                await b.close()
                return
            await complete_works(act, page, start, out)
            await b.close()
            return
        if lock_only:
            await run_lock(act,page,start,out,True)
            assert not errors,errors
            await b.close()
            return
        if "--pilot-letters" in sys.argv:
            await pilot_letters(act,page,start)
            assert not errors,errors
            await b.close()
            return
        if "--fen-pass" in sys.argv:
            await fen_fare(act,page,start,out)
            assert not errors,errors
            await b.close()
            return
        if "--packet" in sys.argv:
            await packet_trip(act,page,start,out)
            assert not errors,errors
            await b.close()
            return
        if parish_only:
            await survey_parish(act,page,start,out,True)
            assert not errors,errors
            await b.close()
            return
        if "--theatre" in sys.argv:
            await perform(act,page,start,out,True)
            assert not errors,errors
            await b.close()
            return
        if not endings_only:
            if glasscut_only:
                await act("A_Gate")
            else:
                if await enter("Market"):
                    await profile()
                    await perform(act,page,start,out)
                    await act("A_Letter")
                    await act("A_Gate")
                if await enter("Saltwake"):
                    await passage("Saltwake")
                await walk_wards(act,page,start,out,enter=enter)
                if await enter("RowanHollow"):
                    await restore_wood(act,page,start,out)
                if await enter("RootChoir"):
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
                if await enter("RimePost"):
                    await passage("RimePost")
                if await enter("Parish"):
                    await survey_parish(act,page,start,out)
                if await enter("Reedwater"):
                    await profile()
                    await act("A_Talk")
                    await act("A_Key1")
                    await act("A_Key0")
                    await act("A_Key2")
                    await act("A_Letter")
                    await act("A_Gate")
            if await enter("SwallowLock") and await page.evaluate("bellProbe().district") == "SwallowLock":
                await run_lock(act,page,start,out)
            if await enter("Glasscut"):
                await passage("Glasscut")
            if await enter("CinderLens"):
                await profile()
                await act("A_Talk")
                await act("A_Key2")
                await act("A_Key0")
                await act("A_Key1")
                await act("A_Lens")
                await act("A_Letter")
                await act("A_Gate")
            if await enter("Press"):
                await print_plates(act,page,start,out)
            if await enter("Pilots"):
                await lead_pilots(act,page,start,out)
            await complete_works(act, page, start, out, enter=enter)
            await mercy_run(act, page, start, out, enter=enter)
            if await enter("Keeper"):
                await profile()
                await act("A_Letter")
                await act("A_Talk")
                for i in range(3):
                    await act("A_Key1")  # three misses must allow a clean retry
                await act("A_Talk")
                await act("A_Key0")
                await act("A_Key2")
                await act("A_Key1")
        if not await enter("Endings"):
            raise ValueError(f"Unknown checkpoint stage: {checkpoint.entry['stage']}")
        save = await page.evaluate(
            "localStorage.getItem('wizzard.bellwake.desktop.v1')"
        )
        final = await act("A_End0")
        assert final["ending"] == 1 and final["leaves"] == 31
        if timed:
            durations = final["secondsByPlace"]
            required = await page.evaluate("""[
                ...window.BELLWAKE.story.rooms,
                ...window.BELLWAKE.regions.map(r=>r.key),
                ...window.BELLWAKE.works.rooms.map(r=>r.key).filter(key=>key!=="KettleYard")
            ]""")
            assert set(durations) == set(required), set(required).symmetric_difference(durations)
            (out / "known-route.json").write_text(
                json.dumps(
                    {
                        "method": "Fresh save, normal movement, keyboard interaction and chart hints. Includes all 27 dispatches, five leaves, the optional night roll, checkpoint reloads and a keeper retry.",
                        "firstEnding": final["ending"],
                        "elapsedSeconds": round(checkpoint.elapsed, 2),
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
        async def road_book(ending):
            claimed=road_letters or not (endings_only or glasscut_only)
            assert final["roadBook"]==claimed
            if not claimed:return
            await act("A_RoadBook")
            for i,speaker in enumerate(("Mara","Jori","Senn","Tern","Issa","Mara")):
                if i:await page.keyboard.press("e")
                assert speaker.lower() in (await page.locator("#act").inner_text()).lower()
                if i==0:
                    assert ("graft takes" if ending==1 else "cutting") in await page.locator("#words").inner_text()
                    await page.screenshot(path=str(out/("road-book-ending-"+str(ending)+".jpg")))
        await road_book(1)
        if nameplate:
            assert final["dedication"]
            await act("A_Nameplate")
        await act("A_Roster")
        assert ("four bowls up to the tower" in await page.locator("#words").inner_text()) == (supper_ending)
        if floodbook:
            assert "night tide" in await page.locator("#words").inner_text()
        await act("A_Talk")
        await page.mouse.up()
        await page.evaluate(
            "s=>localStorage.setItem('wizzard.bellwake.desktop.v1',s)", save
        )
        await start()
        final = await act("A_End1")
        assert final["ending"] == 2 and final["leaves"] == 31
        await road_book(2)
        if nameplate:
            assert final["dedication"]
            await act("A_Nameplate")
        await act("A_Ina")
        assert ("calls for Tavi" in await page.locator("#words").inner_text()) == (supper_ending)
        if floodbook:
            assert "teach me to steer" in await page.locator("#words").inner_text()
        await act("A_Talk")
        await page.keyboard.press("j")
        assert (await page.evaluate("bellProbe()"))["book"]
        journal = await page.locator("#leaves").inner_text()
        for clue in ("child's drawing", "ribbon", "lock book", "casting receipt", "what the river sounds like"):
            assert clue in journal, journal
        if endings_only:
            assert (
                "The Linnet’s flood book" in await page.locator("#leaves").inner_text()
            ) == floodbook
        await page.keyboard.press("j")
        assert not errors, errors
        (out / "playthrough.json").write_text(
            json.dumps(
                {
                    "viewport": [viewport["width"], viewport["height"]],
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
        if checkpoint:
            await enter("Finished")
        await b.close()


if __name__ == "__main__":
    asyncio.run(run())
