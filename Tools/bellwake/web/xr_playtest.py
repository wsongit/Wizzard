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


async def tracked_navigation(page):
    # Tracked head and grip poses traverse the open coast. All actions use the controller trigger.
    await page.evaluate("""() => {
      window.walkSurvey = async (x,z) => {
        for(let i=0;i<350;i++) {
          const [hx,,hz]=bellProbe().vrHead,dx=x-hx,dz=z-hz,length=Math.hypot(dx,dz);
          if(length<.30) return;
          const k=Math.min(.29,length)/length,p=testDevice.position;
          p.set(p.x+dx*k,1.64,p.z+dz*k);
          // Hold the hands over the shoulders during the belfry walk. Its sound plates
          // stand at chest height and a hand carried in front can remain planted.
          const inBelfry=bellProbe().district==="StillBelfry";
          const handY=inBelfry?2.02:1.30, handZ=p.z+(inBelfry ? .24 : -.24);
          testDevice.controllers.right.position.set(p.x+.23,handY,handZ);
          testDevice.controllers.left.position.set(p.x-.23,handY,handZ);
          await new Promise(r=>setTimeout(r,70));
        }
        throw Error("Tracked crossing to "+[x,z]+" stalled at "+bellProbe().vrHead+" palms="+bellProbe().planted);
      };
      window.sightToward = ([x,y,z]) => {
        const [hx,hy,hz]=bellProbe().vrHead,dx=x-hx,dy=y-hy,dz=z-hz;
        const yaw=Math.atan2(-dx,-dz)*.5,pitch=Math.atan2(dy,Math.hypot(dx,dz))*.5;
        testDevice.quaternion.set(Math.cos(yaw)*Math.sin(pitch), Math.sin(yaw)*Math.cos(pitch),
          -Math.sin(yaw)*Math.sin(pitch), Math.cos(yaw)*Math.cos(pitch));
      };
    }""")

async def coast_crossing(page):
    await tracked_navigation(page)
    async def trigger(until):
        await page.evaluate(
            "testDevice.controllers.right.updateButtonValue('trigger',1)"
        )
        await page.wait_for_function(until, timeout=9000)
        await page.evaluate(
            "testDevice.controllers.right.updateButtonValue('trigger',0)"
        )
        await page.wait_for_timeout(180)
        if await page.evaluate("bellProbe().dialogue"):
            await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',1)")
            await page.wait_for_function("!bellProbe().dialogue")
            await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',0)")
            await page.wait_for_timeout(150)

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


async def trigger_station(page, name, check):
    await page.evaluate("key=>sightToward(bellProbe().markers['A_'+key])",name)
    await page.wait_for_function("key=>bellProbe().focus==='A_'+key",arg=name)
    await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',1)")
    await page.wait_for_function(check)
    await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',0)")
    await page.wait_for_timeout(300)

async def palm_instruments(browser):
    plan=json.loads((here.parents[2]/"Assets/Resources/Bellwake/Underworks.json").read_text())
    words=[0]*((len(plan["flags"])+29)//30)
    for flag in ("woodBook","heardRootWest","heardRootEast"):
        word,bit=divmod(plan["flags"].index(flag),30)
        words[word] |= 1 << bit
    wood_save={"number":2,"leaves":1,"works":{"active":True,"chamber":27,"camp":"RestMiddle",
                "badges":words[0],"furtherBadges":words[1:]}}
    for district, save, order in (
        ("RowanHollow",wood_save,["Short","Middle","Long","Short"]),
        ("KettleYard", {"number": 21, "works": {"active": True, "chamber": 18, "camp": "RestLow"}},
         ["Low", "High", "Low", "Middle", "Middle", "High", "High", "Low", "Middle"]),
        ("RootChoir", {"number": 2}, ["Key2", "Key1", "Key0"]),
        ("StillBelfry", {"number": 23}, ["Key0", "Key2", "Key1"]),
    ):
        if "--wood-palms" in sys.argv and district!="RowanHollow": continue
        if "--belfry-palms" in sys.argv and district!="StillBelfry": continue
        page = await browser.new_page(viewport={"width": 630, "height": 380})
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        await page.add_init_script(script=harness)
        await page.add_init_script("localStorage.setItem('wizzard.bellwake.desktop.v1',"+json.dumps(json.dumps(save))+")")
        await page.goto(sys.argv[1])
        await page.click("#vr", timeout=60000)
        await page.wait_for_function("k=>bellProbe().vr && bellProbe().district===k", arg=district)
        await tracked_navigation(page)
        await page.evaluate("""() => {
            window.tapBell = async (name, side) => {
                const s=bellProbe(), target=s.instruments['A_'+name], [x,y,z]=target.centre;
                const frame=()=>new Promise(resolve=>setTimeout(resolve,95));
                // Pull both hands behind the approach plane when walking across an instrument.
                if (s.district === "StillBelfry" && name === "Key1") {
                    // Leave the east plinth on its open side, then pass east of the keeper.
                    for (const [px,pz] of [[7,1],[3,1],[3,-6.2],[0,-6.2]]) await walkSurvey(px,pz);
                }
                await walkSurvey(x,z+1.03);
                const grip=testDevice.controllers[side];
                const pose=(depth)=>{
                    const head=bellProbe().vrHead, p=testDevice.position;
                    grip.position.set(p.x+x-head[0],p.y+y-head[1],p.z+z+depth-head[2]);
                };
                for(const d of [.65,.54,.43,.32,.21,.10,.02]){pose(d);await frame()}
                await new Promise(resolve=>setTimeout(resolve,370));
                const hand=bellProbe().handPositions[side==='left'?0:1];
                // Draw the striking hand back before walking away from the instrument.
                for(const d of [.14,.26,.39,.52,.65]) {pose(d);await frame()}
                const p=testDevice.position;
                grip.position.set(p.x+(side==="left"?-.22:.22),p.y-.24,p.z+.04);
                for(let n=0;n<5;n++) await new Promise(r=>testDevice.activeSession.requestAnimationFrame(r));
                return {hand, target:[x,y,z]};
            };
        }""")
        for j, name in enumerate(order):
            before=await page.evaluate("bellProbe().recentTones.length")
            contact=await page.evaluate("([name,side])=>tapBell(name,side)", [name, "left" if j%2 else "right"])
            state=await page.evaluate("bellProbe()")
            assert len(state["recentTones"])==before+1,(district,name,contact,state["recentTones"])
            if district=="RowanHollow":
                assert state["works"]["signals"]["drumBeat"]==j+1, state["works"]
            if district=="KettleYard":
                assert state["works"]["signals"]["supperBeat"]==j+1, state["works"]
            print(district, name, "palm stroke", j+1, flush=True)
        if district=="RootChoir":
            assert state["number"]!=2 and state["recentTones"][-3:]==[2,1,0]
        if district=="StillBelfry":
            assert state["number"]==31, state["number"]
        if district=="StillBelfry" and "--morning-palms" in sys.argv:
            await page.evaluate("async()=>{for (const p of [[0,-6.15],[3,-6.15],[3,-2],[5.2,-2.6]]) await walkSurvey(...p)}")
            await trigger_station(page,"MorningSong","bellProbe().keeper.verse===1")
            await page.wait_for_function("bellProbe().keeper.lit.includes(2)")
            await page.wait_for_function("bellProbe().recentTones.slice(-3).join('')==='020'")
            await page.evaluate("async()=>{await walkSurvey(5.2,.8);await walkSurvey(-7,.8)}")
            for i,key in enumerate(("Key0","Key2","Key0")):
                await page.evaluate("([id,hand])=>tapBell(id,hand)",[key,"left" if i==1 else "right"])
                assert await page.evaluate("bellProbe().keeper.verse")==i+2
            print("PASS keeper guidance, crank trigger, three sounding pearls and two-handed reply",flush=True)
        await page.evaluate("testDevice.activeSession.end()")
        assert not errors,errors
        await page.close()
    print("PASS two-handed physical music, close repeated notes and held-hand rejection",flush=True)


async def theatre_checkpoint(browser):
    page = await browser.new_page(viewport={"width":630,"height":380})
    errors=[]
    page.on("pageerror",lambda err:errors.append(str(err)))
    await page.add_init_script(script=harness)
    await page.goto(sys.argv[1])
    await page.click("#vr",timeout=60000)
    await page.wait_for_function("bellProbe().vr && bellProbe().palms.every(Boolean)")
    await tracked_navigation(page)
    async def visit(key, arrived):
        await page.evaluate("""async name=>{const [x,y,z]=bellProbe().markers['A_'+name];
            await walkSurvey(x,z+1.8)}""",key)
        await trigger_station(page,key,arrived)
    await visit("Talk","document.getElementById('words').textContent.includes('blue courtyard door')")
    before=await page.evaluate("bellProbe().vrHead")
    assert await page.evaluate("bellProbe().dialogue")
    await page.evaluate("testDevice.position.x+=.7")
    await page.wait_for_timeout(400)
    after=await page.evaluate("bellProbe().vrHead")
    assert abs(before[0]-after[0])<.03,(before,after)
    await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',1)")
    await page.wait_for_function("!bellProbe().dialogue")
    await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',0)")
    await page.wait_for_timeout(300)
    await visit("Playhouse","!bellProbe().busy && bellProbe().district==='Highroad'")
    await page.evaluate("""async()=>{
        for(let i=0;i<200;i++){
            const p=bellProbe();
            if(p.busy || !p.road) break;
            const [x,,z]=p.road.target,[hx,,hz]=p.vrHead;
            const dx=x-hx,dz=z-hz,k=Math.min(1,.25/Math.hypot(dx,dz));
            const pos=testDevice.position;
            pos.set(pos.x+k*dx,1.64,pos.z+k*dz);
            testDevice.controllers.left.position.set(pos.x-.2,1.3,pos.z-.2);
            testDevice.controllers.right.position.set(pos.x+.2,1.3,pos.z-.2);
            await new Promise(r=>setTimeout(r,80));
        }
    }""")
    await page.wait_for_function("!bellProbe().busy && bellProbe().district==='PaperCourt'")

    await visit("Pattern","bellProbe().works.signals.paperPattern===1")
    await visit("Figure","bellProbe().works.signals.paperActor===2")
    assert (await page.evaluate("bellProbe().playhouse.figures"))==[2]
    await page.evaluate("testDevice.activeSession.end()")
    assert not errors,errors
    await page.close()
    print("PASS market invitation, blue door, casting pattern and woodcut figure reel with tracked controllers",flush=True)


async def school_waypost(browser):
    page=await browser.new_page(viewport={"width":630,"height":380})
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    await page.add_init_script(script=harness)
    await page.goto(sys.argv[1])
    await page.click("#vr",timeout=60000)
    await page.wait_for_function("bellProbe().vr && bellProbe().district==='Bellmarket'")
    await tracked_navigation(page)
    mark=await page.evaluate("bellProbe().markers.A_WoodWalk")
    await page.evaluate("([x,z])=>walkSurvey(x,z)",[mark[0],mark[2]+1.8])
    await trigger_station(page,"WoodWalk","!bellProbe().busy && bellProbe().district==='RowanHollow'")
    assert (await page.evaluate("bellProbe().works"))["returnTicket"]
    await trigger_station(page,"Linn","bellProbe().works.signals.woodBook===1")
    await page.evaluate("testDevice.activeSession.end()")
    assert not errors,errors
    await page.close()
    print("PASS tracked market waypost and field book at Linn’s hut",flush=True)


async def school_letter(browser):
    plan=json.loads((here.parents[2]/"Assets/Resources/Bellwake/Underworks.json").read_text())
    machines=[0]*len(plan["machines"])
    for i,machine in enumerate(plan["machines"]):
        for voice in ("rainMended","rootMended","wrenMended"):
            if voice in machine["channels"]:
                signal=machine["channels"].index(voice)
                machines[i]=next(j for j,row in enumerate(machine["rows"]) if row["values"][signal]==1)
    save={"number":2,"leaves":1,"works":{"machines":machines}}
    page=await browser.new_page(viewport={"width":630,"height":380})
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    await page.add_init_script(script=harness)
    await page.add_init_script("localStorage.setItem('wizzard.bellwake.desktop.v1',"+json.dumps(json.dumps(save))+")")
    await page.goto(sys.argv[1])
    await page.click("#vr",timeout=60000)
    await page.wait_for_function("bellProbe().vr && bellProbe().district==='RootChoir'")
    await page.evaluate("testDevice.controllers.right.updateButtonValue('a-button',1)")
    await page.wait_for_function("bellProbe().book")
    await page.evaluate("testDevice.controllers.right.updateButtonValue('a-button',0)")
    await page.wait_for_timeout(200)
    await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',1)")
    await page.wait_for_function("bellProbe().vrMap && bellProbe().journalCaption.includes('school linen')")
    await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',0)")
    await page.evaluate("testDevice.controllers.right.updateButtonValue('a-button',1)")
    await page.wait_for_function("!bellProbe().book && !bellProbe().sheetAllocated")
    await page.evaluate("testDevice.activeSession.end()")
    assert not errors,errors
    await page.close()
    print("PASS Linn’s illustrated letter opened in the choir and released on book close",flush=True)


async def listening_checkpoint(browser):
    page=await browser.new_page(viewport={"width":630,"height":380})
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    await page.add_init_script(script=harness)
    plan=json.loads((here.parents[2]/"Assets/Resources/Bellwake/Underworks.json").read_text())
    word,bit=divmod(plan["flags"].index("woodBook"),30)
    words=[0]*(word+1)
    words[word] = 1 << bit
    save={"number":2,"leaves":1,"works":{"active":True,"chamber":27,"camp":"RestRainWest",
                                          "badges":words[0],"furtherBadges":words[1:]}}
    await page.add_init_script("localStorage.setItem('wizzard.bellwake.desktop.v1',"+json.dumps(json.dumps(save))+")")
    await page.goto(sys.argv[1])
    await page.click("#vr",timeout=60000)
    await page.wait_for_function("bellProbe().vr && bellProbe().district==='RowanHollow'")
    await tracked_navigation(page)
    await trigger_station(page,"RainWest","bellProbe().sight && bellProbe().forestAudio?.playing")
    await page.evaluate("sightToward(bellProbe().sight.target)")
    await page.wait_for_function("bellProbe().sight?.linedUp")
    await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',1)")
    await page.wait_for_function("!bellProbe().forestAudio && bellProbe().works.signals.heardRainWest===1")
    await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',0)")
    await page.evaluate("testDevice.controllers.right.updateButtonValue('a-button',1)")
    await page.wait_for_function("bellProbe().vrMap")
    await page.evaluate("testDevice.controllers.right.updateButtonValue('a-button',0)")
    await page.evaluate("testDevice.activeSession.end()")
    assert not errors,errors
    await page.close()
    print("PASS tracked listening horn, acoustic bearing, release and witness map",flush=True)


async def parish_checkpoint(browser):
    for room,chamber,camp in (("SillwaterEbb",20,"RestWillow"),("SillwaterOffice",22,"RestWest")):
        page=await browser.new_page(viewport={"width":630,"height":380})
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        await page.add_init_script(script=harness)
        save={"number":6,"works":{"active":True,"chamber":chamber,"camp":camp,"furtherBadges":[1]}}
        await page.add_init_script("localStorage.setItem('wizzard.bellwake.desktop.v1',"+json.dumps(json.dumps(save))+")")
        await page.goto(sys.argv[1])
        await page.click("#vr",timeout=60000)
        await page.wait_for_function("key=>bellProbe().vr && bellProbe().district===key && bellProbe().palms.every(Boolean)",arg=room)
        await tracked_navigation(page)
        if room=="SillwaterEbb":
            for visible in (True,False):
                await page.evaluate("testDevice.controllers.right.updateButtonValue('a-button',1)")
                await page.wait_for_function("v=>bellProbe().vrMap===v",arg=visible)
                await page.evaluate("testDevice.controllers.right.updateButtonValue('a-button',0)")
                await page.wait_for_timeout(300)
            await trigger_station(page,"Willow","!!bellProbe().sight")
            await page.evaluate("sightToward(bellProbe().sight.target)")
            await page.wait_for_function("bellProbe().sight?.linedUp")
            await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',1)")
            await page.wait_for_function("!bellProbe().sight && bellProbe().works.signals.fixWillow===1")
            await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',0)")
        else:
            before=await page.evaluate("bellProbe().machinery.MapPin.position")
            await trigger_station(page,"West","bellProbe().works.signals.parishCol===1")
            await page.wait_for_function("x=>Math.abs(bellProbe().machinery.MapPin.position[0]-x)<.04",arg=before[0]-1.52)
        await page.evaluate("testDevice.activeSession.end()")
        assert not errors,errors
        await page.close()
    print("PASS tracked Willow transit, visual bearing and brass chart pin displacement",flush=True)


async def packet_checkpoint(browser,fen=False):
    page=await browser.new_page(viewport={"width":630,"height":380})
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    await page.add_init_script(script=harness)
    await page.goto(sys.argv[1])
    await page.click("#vr",timeout=60000)
    await page.wait_for_function("bellProbe().vr && bellProbe().palms.every(Boolean)")
    await tracked_navigation(page)
    if fen:
        await page.evaluate("walkSurvey(9.2,13.50)")
        await trigger_station(page,"FenPass","!bellProbe().busy && bellProbe().district==='DriftFen'")
        await trigger_station(page,"Guide","bellProbe().works.signals.fenFork===1")
        for x,z in ((0,23),(-7,23),(-7,21.2)):
            await page.evaluate("([x,z])=>walkSurvey(x,z)",[x,z])
        await trigger_station(page,"Home","!bellProbe().busy && bellProbe().district==='SwallowLock'")
        for x,z in ((-16,3),(-17,2),(-17,-8.5),(-7,-8.5),(-5,-10.5),(9,-10.5),(11,-12.5),(13.5,-11.8)):
            await page.evaluate("([x,z])=>walkSurvey(x,z)",[x,z])
    else:
        await page.evaluate("walkSurvey(6,12.35)")
        await trigger_station(page,"Packet","!bellProbe().busy && bellProbe().district==='SillwaterEbb'")
    await trigger_station(page,"Gate","!bellProbe().busy && bellProbe().district==='Bellmarket'")
    assert (await page.evaluate("bellProbe().number"))==0
    assert not errors,errors
    await page.evaluate("testDevice.activeSession.end()")
    await page.close()
    print("PASS Quest return fare, "+("Willa’s fork, lock towpath" if fen else "parish landing")+" and return to Tavi’s first morning",flush=True)


async def pilot_checkpoint(browser):
    plan=json.loads((here.parents[2]/"Assets/Resources/Bellwake/Underworks.json").read_text())
    flag=plan["flags"].index("rookWarden")
    words=[0]*((len(plan["flags"])-1)//30);words[flag//30-1]=1<<(flag%30)
    save={"number":21,"works":{"active":True,"chamber":next(i for i,r in enumerate(plan["rooms"]) if r["key"]=="GlassRookery"),"camp":"RestP1","furtherBadges":words}}
    page=await browser.new_page(viewport={"width":630,"height":380});errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    await page.add_init_script(script=harness)
    await page.add_init_script("localStorage.setItem('wizzard.bellwake.desktop.v1',"+json.dumps(json.dumps(save))+")")
    await page.goto(sys.argv[1]);await page.click("#vr",timeout=60000)
    await page.wait_for_function("bellProbe().vr && bellProbe().district==='GlassRookery' && bellProbe().palms.every(Boolean)")
    await tracked_navigation(page)
    await page.evaluate("sightToward(bellProbe().markers.A_P1)")
    await page.wait_for_function("bellProbe().focus==='A_P1'")
    await page.evaluate("testDevice.controllers.left.updateButtonValue('squeeze',1)")
    await page.wait_for_function("bellProbe().works.signals.birdAt===1 && bellProbe().pilotCall==='Pilot0'")
    await page.evaluate("testDevice.controllers.left.updateButtonValue('squeeze',0)")
    await page.wait_for_function("Math.abs(bellProbe().pilots[0].wing)>.06")
    await page.wait_for_function("(()=>{const p=bellProbe().pilots[0];return Math.hypot(...p.position.map((v,i)=>v-p.target[i]))<.04})()")
    await page.evaluate("testDevice.controllers.right.updateButtonValue('a-button',1)")
    await page.wait_for_function("bellProbe().vrMap")
    await page.evaluate("testDevice.controllers.right.updateButtonValue('a-button',0)")
    assert not errors,errors
    await page.evaluate("testDevice.activeSession.end()");await page.close()
    print("PASS tracked whistle, grebe reply, wingbeats, landing and pilot chart in the headset",flush=True)


async def headset_report(browser):
    page = await browser.new_page(viewport={"width": 630, "height": 380}, accept_downloads=True)
    errors = []
    page.on("pageerror",lambda err:errors.append(str(err)))
    await page.add_init_script(script=harness)
    url = sys.argv[1]
    await page.goto(url + ("&" if "?" in url else "?") + "timings")
    await page.click("#vr", timeout=60000)
    await page.wait_for_function("bellProbe().vr && bellProbe().palms.every(Boolean)")
    for next_room in (32,33,None):
        await page.evaluate("""async()=>{for(let i=0;i<48;i++)await new Promise(r=>testDevice.activeSession.requestAnimationFrame(r))}""")
        if next_room is not None:
            await page.evaluate("r=>bellTravel(r)",next_room)
    await page.evaluate("testDevice.activeSession.end()")
    await page.wait_for_function("!bellProbe().vr")
    await page.keyboard.press("j")
    async with page.expect_download() as download:
        await page.click("#timings:visible")
    file = await download.value
    assert file.suggested_filename == "Bellwake-headset-timings.json"
    report = json.loads(Path(await file.path()).read_text())
    rows = {r["room"]:r for r in report["rooms"]}
    for place in ("Bellmarket","DriftFen","GlassRookery"):
        row=rows[place]
        assert 12 <= row["recentFrames"] <= 360 and row["recentMedianMs"]>0, row
        assert row["recentP95Ms"]>=row["recentMedianMs"] and row["maxRendererTextures"]>0, row
        if place!="Bellmarket":
            assert row["loads"]==1 and row["meanLoadMs"]>0 and row["worstTransitionFrameMs"]>0,row
    assert not errors,errors
    print(json.dumps(report, indent=2),flush=True)
    await page.close()


async def obstructed_head(browser):
    page = await browser.new_page(viewport={"width": 630, "height": 380})
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    await page.add_init_script(script=harness)
    await page.goto(sys.argv[1])
    await page.click("#vr", timeout=60000)
    await page.wait_for_function("bellProbe().vr && bellProbe().palms.every(Boolean)")
    await tracked_navigation(page)
    await page.evaluate("walkSurvey(-2,10.4)")
    await page.evaluate("sightToward(bellProbe().markers.A_Talk)")
    await page.wait_for_function("bellProbe().focus==='A_Talk' && !bellProbe().headObstructed")
    await page.evaluate("window.clearPose=[testDevice.position.x,testDevice.position.y,testDevice.position.z]")
    for subject in ("floor", "footing"):
        await page.evaluate("""what=>{
            const p=testDevice.position, h=bellProbe().vrHead;
            if(what==='floor')p.y-=h[1]+.35;
            else p.set(p.x-2-h[0],p.y+1.15-h[1],p.z+7.55-h[2]);
        }""",subject)
        await page.wait_for_timeout(350)
        measured = await page.evaluate("({guard:bellProbe().headObstructed,head:bellProbe().vrHead})")
        print(subject, measured, flush=True)
        if subject == "footing" and not measured["guard"]:
            # The capsule sweep can prevent the tracking origin reaching the obstacle at all.
            assert measured["head"][2] >= 8.52, measured
            break
        assert measured["guard"], measured
        await page.evaluate("sightToward(bellProbe().markers.A_Talk)")
        await page.wait_for_function("!bellProbe().focus")
        await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',1)")
        await page.wait_for_timeout(240)
        await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',0)")
        assert not await page.evaluate("bellProbe().works?.invited || JSON.parse(localStorage.getItem('wizzard.bellwake.desktop.v1'))?.works?.invited"), subject
        await page.evaluate("testDevice.position.set(...clearPose)")
        await page.wait_for_function("!bellProbe().headObstructed")
    await page.evaluate("testDevice.position.set(...clearPose)")
    await page.evaluate("walkSurvey(-2,10.4)")
    await trigger_station(page,"Talk","document.querySelector('#words').textContent.includes('blue courtyard door')")
    assert not errors,errors
    await page.evaluate("testDevice.activeSession.end()")
    await page.close()
    print("PASS a submerged head cannot talk through the floor, a solid footing stops the head crossing and returning to the clear side restores the market conversation.", flush=True)


async def single_palm_release(browser):
    for side, drop in (("right", False), ("left", False), ("right", True)):
        page = await browser.new_page(viewport={"width": 600, "height": 370})
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        await page.add_init_script(script=harness)
        await page.goto(sys.argv[1])
        await page.click("#vr", timeout=60000)
        await page.wait_for_function("bellProbe().vr && bellProbe().palms.every(Boolean)")
        result = await page.evaluate("""async ([side, drop])=>{
            const i=side==="left"?0:1, hand=testDevice.controllers[side], sign=i?1:-1;
            const next=()=>new Promise(r=>testDevice.activeSession.requestAnimationFrame(r));
            testDevice.controllers[i?"left":"right"].connected=false;
            testDevice.position.set(0,.85,0);
            hand.position.set(.22*sign,.05,-.45);
            for(let n=0;n<80 && !bellProbe().planted[i];n++)await next();
            if(!bellProbe().planted[i])throw Error("Palm did not plant");
            const start=bellProbe().vrHead;
            for(let n=1;n<=8;n++){
                hand.position.set(.22*sign,.025,-.45+n*.047);
                await next();
            }
            const before=bellProbe();
            if(drop)hand.connected=false;else hand.position.y+=.27;
            for(let n=0;n<10 && bellProbe().planted[i];n++)await next();
            const release=bellProbe();
            for(let n=0;n<4;n++)await next();
            const after=bellProbe();
            for(let n=0;n<170 && Math.hypot(bellProbe().releaseVelocity[0],bellProbe().releaseVelocity[2])>.025;n++)await next();
            const settled=bellProbe();
            hand.connected=true;
            hand.position.set(.22*sign,1.1,-.32);
            await next();await next();
            return {side,drop,plantedBefore:before.planted[i],stillPlanted:release.planted[i],
                push:before.vrHead[2]-start[2],releaseSpeed:release.releaseVelocity[2],
                glide:after.vrHead[2]-before.vrHead[2],settledSpeed:Math.hypot(settled.releaseVelocity[0],settled.releaseVelocity[2]),reconnected:bellProbe().palms[i],
                phantomContact:bellProbe().planted[i]};
        }""", [side, drop])
        assert result["plantedBefore"] and not result["stillPlanted"], result
        assert result["settledSpeed"] <= .025,result
        assert result["push"] < -.08 and result["reconnected"] and not result["phantomContact"], result
        if drop:
            assert abs(result["releaseSpeed"]) < .015 and abs(result["glide"]) < .04, result
        else:
            assert result["releaseSpeed"] < -.1 and result["glide"] < -.01, result
        assert not errors, errors
        print(result, flush=True)
        await page.evaluate("testDevice.activeSession.end()")
        await page.close()


async def portrait_checkpoint(browser):
    plan = json.loads((here.parents[2] / "Assets/Resources/Bellwake/Underworks.json").read_text())
    idx, machine = next((i, m) for i, m in enumerate(plan["machines"]) if m["key"] == "pilots")
    machines = [0] * len(plan["machines"])
    machines[idx] = next(i for i, r in enumerate(machine["rows"]) if r["values"][0] == 3)
    save = {"number": 33, "leaves": 31, "works": {"machines": machines}}
    page = await browser.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    await page.add_init_script(script=harness)
    await page.add_init_script("localStorage.setItem('wizzard.bellwake.desktop.v1',"+json.dumps(json.dumps(save))+")")
    await page.goto(sys.argv[1])
    await page.click("#vr", timeout=60000)
    await page.wait_for_function("bellProbe().vr && bellProbe().palms.every(Boolean)")
    async def press(control, assertion):
        await page.evaluate("(c)=>testDevice.controllers.right.updateButtonValue(c,1)",control)
        try:
            await page.wait_for_function(assertion)
        except Exception:
            print(await page.evaluate("()=>{const s=bellProbe();return [s.book,s.journalPage,s.vrMap,s.vrPortrait,s.journalCaption]}"),flush=True)
            raise
        await page.evaluate("(c)=>testDevice.controllers.right.updateButtonValue(c,0)",control)
        # Give the emulator two presented XR frames to deliver selectend before a second press.
        await page.evaluate("new Promise(done=>testDevice.activeSession.requestAnimationFrame(()=>testDevice.activeSession.requestAnimationFrame(done)))")
    for _ in range(2):
        await press("a-button","bellProbe().book")
        await press("trigger","bellProbe().vrPortrait")
        await press("trigger","bellProbe().journalPage === 2 && !bellProbe().vrMap")
        await press("a-button","!bellProbe().book && !bellProbe().sheetAllocated")
    await page.evaluate("testDevice.activeSession.end()")
    assert not errors, errors
    await page.close()
    print("PASS tracked journal opens Ina's illustrated gift twice and releases its GPU page on close.",flush=True)


async def fen_checkpoint(browser):
    plan=json.loads((here.parents[2]/"Assets/Resources/Bellwake/Underworks.json").read_text())
    flag=plan["flags"].index("fenFork")
    words=[0]*((len(plan["flags"])-1)//30)
    words[flag//30-1]=1<<(flag%30)
    save={"number":13,"works":{"active":True,"chamber":next(i for i,r in enumerate(plan["rooms"]) if r["key"]=="DriftFen"),"camp":"RestFind1","furtherBadges":words}}
    page=await browser.new_page(viewport={"width":630,"height":380})
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    await page.add_init_script(script=harness)
    await page.add_init_script("localStorage.setItem('wizzard.bellwake.desktop.v1',"+json.dumps(json.dumps(save))+")")
    await page.goto(sys.argv[1]);await page.click("#vr",timeout=60000)
    await page.wait_for_function("bellProbe().vr && bellProbe().district==='DriftFen' && bellProbe().palms.every(Boolean)")
    await tracked_navigation(page)
    await page.wait_for_function("bellProbe().handFork!==null")
    await page.evaluate("testDevice.controllers.left.connected=false")
    await page.wait_for_function("bellProbe().handFork===null")
    await page.evaluate("testDevice.controllers.left.connected=true")
    await page.wait_for_function("bellProbe().handFork!==null")
    await page.evaluate("testDevice.controllers.left.updateButtonValue('squeeze',1)")
    await page.wait_for_function("bellProbe().uncovered==='A_Find1'")
    await page.evaluate("testDevice.controllers.left.updateButtonValue('squeeze',0)")
    await trigger_station(page,"Find1","bellProbe().works.signals.bagRecovered===1 && !bellProbe().uncovered")
    assert not errors,errors
    await page.evaluate("testDevice.activeSession.end()");await page.close()
    print("PASS left grip revealed Pella’s hidden brass clasp and right trigger recovered it",flush=True)

async def swallow_checkpoint(browser):
    plan=json.loads((here.parents[2]/"Assets/Resources/Bellwake/Underworks.json").read_text())
    index=plan["flags"].index("fenWatch")
    page=await browser.new_page(viewport={"width":630,"height":380})
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    await page.add_init_script(script=harness)
    save={"number":13,"works":{"active":True,"chamber":next(i for i,r in enumerate(plan["rooms"]) if r["key"]=="SwallowLock"),"camp":"RestHead","furtherBadges":[1<<(index%30)]}}
    await page.add_init_script("localStorage.setItem('wizzard.bellwake.desktop.v1',"+json.dumps(json.dumps(save))+")")
    await page.goto(sys.argv[1])
    await page.click("#vr",timeout=60000)
    await page.wait_for_function("bellProbe().vr && bellProbe().district==='SwallowLock' && bellProbe().palms.every(Boolean)")
    await tracked_navigation(page)
    await trigger_station(page,"Head","bellProbe().works.signals.foreMark===1 && bellProbe().works.signals.westClear===0")
    await page.evaluate("walkSurvey(0,3.56)")
    await trigger_station(page,"Chain","bellProbe().works.signals.foreMark===0 && bellProbe().works.signals.aftMark===1")
    await page.evaluate("testDevice.activeSession.end()")
    assert not errors,errors
    await page.close()
    print("PASS headset trigger raised the fore pound, shut its gate, and transferred water to aft",flush=True)


async def press_checkpoint(browser):
    plan = json.loads((here.parents[2]/"Assets/Resources/Bellwake/Underworks.json").read_text())
    chamber = next(i for i,r in enumerate(plan["rooms"]) if r["key"]=="GloamingPress")
    index, machine = next((i,m) for i,m in enumerate(plan["machines"]) if m["key"]=="proofs")
    for camp, prefix, wheel, check in (
        ("Fork", [0,0,0,0,0,0], "Fork", "bellProbe().works.signals.dialFork===1"),
        ("Hand", [2,1,0,1,0,1], "Hand", "bellProbe().works.signals.glassProof===3")
    ):
        machines = [0] * len(plan["machines"])
        machines[index] = next(i for i,r in enumerate(machine["rows"]) if r["values"][:6]==prefix)
        save = {"number":21, "leaves":15, "works":{"active":True,"chamber":chamber,"camp":"Rest"+camp,"machines":machines}}
        page = await browser.new_page(viewport={"width":630,"height":380})
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        await page.add_init_script(script=harness)
        await page.add_init_script("localStorage.setItem('wizzard.bellwake.desktop.v1',"+json.dumps(json.dumps(save))+")")
        await page.goto(sys.argv[1])
        await page.click("#vr",timeout=60000)
        await page.wait_for_function("bellProbe().vr && bellProbe().district==='GloamingPress' && bellProbe().palms.every(Boolean)")
        await tracked_navigation(page)
        await trigger_station(page,wheel,check)
        await page.evaluate("testDevice.controllers.right.updateButtonValue('a-button',1)")
        await page.wait_for_function("bellProbe().vrMap")
        await page.evaluate("testDevice.controllers.right.updateButtonValue('a-button',0)")
        if camp == "Hand":
            assert await page.locator("#leaves img[alt*=prints]").get_attribute("src") is None
            await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',1)")
            await page.wait_for_function("bellProbe().vrContact")
            await page.evaluate("testDevice.controllers.right.updateButtonValue('trigger',0)")
        await page.wait_for_timeout(350)
        await page.evaluate("testDevice.controllers.right.updateButtonValue('a-button',1)")
        await page.wait_for_function("!bellProbe().book && !bellProbe().sheetAllocated")
        assert not errors, errors
        await page.evaluate("testDevice.activeSession.end()")
        await page.close()
    print("PASS tracked mirror, glass exposure, survey, contact sheet and journal texture release", flush=True)


async def kitchen_checkpoint(browser):
    page = await browser.new_page(viewport={"width": 630, "height": 380})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    await page.add_init_script(script=harness)
    save = {"number": 21, "works": {"active": True, "chamber": 18, "camp": "RestLow"}}
    await page.add_init_script("localStorage.setItem('wizzard.bellwake.desktop.v1',"+json.dumps(json.dumps(save))+")")
    await page.goto(sys.argv[1])
    await page.click("#vr", timeout=60000)
    await page.wait_for_function("bellProbe().vr && bellProbe().district==='KettleYard' && bellProbe().palms.every(Boolean)")
    await tracked_navigation(page)
    for beat, (name, x) in enumerate((("Low", -3.2), ("High", 3.2), ("Low", -3.2)), start=1):
        await page.evaluate("x=>walkSurvey(x,-3.45)", x)
        await trigger_station(page, name, "bellProbe().works.signals.supperBeat==="+str(beat))
    state = await page.evaluate("bellProbe()")
    assert state["recentTones"][-3:] == [2, 0, 2] and state["works"]["signals"]["firstPhrase"]
    assert not errors, errors
    await page.evaluate("testDevice.activeSession.end()")
    await page.close()
    print("PASS tracked pans, controller triggers and the first supper phrase", flush=True)


async def crane_checkpoint(browser):
    page=await browser.new_page(viewport={"width":630,"height":380})
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    await page.add_init_script(script=harness)
    save={"number":21,"leaves":15,"works":{"active":True,"chamber":16,"camp":"RestWest"}}
    await page.add_init_script("localStorage.setItem('wizzard.bellwake.desktop.v1',"+json.dumps(json.dumps(save))+")")
    await page.goto(sys.argv[1])
    await page.click("#vr",timeout=60000)
    await page.wait_for_function("bellProbe().vr && bellProbe().district==='MouldLoft' && bellProbe().palms.every(Boolean)")
    await tracked_navigation(page)
    await trigger_station(page, "West","bellProbe().works.signals.hook===0")
    await page.evaluate("walkSurvey(0,3.3)")
    await trigger_station(page, "Centre","bellProbe().works.signals.tower0===1")
    await page.wait_for_function("Math.abs(bellProbe().machinery.Collar0.position[0]-5)<.05")
    await page.evaluate("walkSurvey(-5,3.3)")
    await trigger_station(page, "West","bellProbe().works.signals.hook===0")
    await page.evaluate("walkSurvey(0,3.3)")
    await trigger_station(page, "Centre","bellProbe().works.signals.hook===0 && bellProbe().works.signals.tower1===0")
    assert (await page.evaluate("bellProbe().works.signals.tower0"))==1
    await page.evaluate("testDevice.activeSession.end()")
    assert not errors,errors
    await page.close()
    print("PASS Quest tracked rack selection, five-metre collar transfer and rejected oversize collar",flush=True)


async def relief_seal(browser):
    plan = json.loads((here.parents[2] / "Assets/Resources/Bellwake/Underworks.json").read_text())
    chambers = [room["key"] for room in plan["rooms"]]
    machines = [m["key"] for m in plan["machines"]]
    slip = plan["machines"][machines.index("MercySlip")]
    values = [0] * len(machines)
    values[machines.index("MercySlip")] = next(i for i, row in enumerate(slip["rows"])
        if row["values"][-2:] == [1, 0])
    save = {"number": 21, "leaves": 15, "works": {
        "active": True, "chamber": chambers.index("MercySlip"), "camp": "RestMark", "machines": values}}
    page = await browser.new_page(viewport={"width": 600, "height": 350})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    await page.add_init_script(script=harness)
    await page.add_init_script("localStorage.setItem('wizzard.bellwake.desktop.v1',"+json.dumps(json.dumps(save))+")")
    await page.goto(sys.argv[1])
    await page.click("#vr", timeout=60000)
    await page.wait_for_function("bellProbe().vr && bellProbe().palms.every(Boolean)")
    await tracked_navigation(page)
    for n in range(1, 4):
        await trigger_station(page, "Die", f"bellProbe().works.signals.MercySlipDie==={n}")
    await trigger_station(page, "Other", "bellProbe().works.signals.MercySlipSecondAccount===1")
    await page.evaluate("testDevice.controllers.right.updateButtonValue('a-button',1)")
    await page.wait_for_function("bellProbe().vrMap")
    assert "You issue Dot" in await page.locator("#leaves").inner_text()
    await page.evaluate("testDevice.activeSession.end()")
    assert not errors, errors
    await page.close()
    print("PASS Quest seal press, alternate signature and passenger roll", flush=True)


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
        if "--mercy-seal" in sys.argv:
            await relief_seal(b)
            await b.close()
            return
        if "--headset-report" in sys.argv:
            await headset_report(b)
            await b.close()
            return
        if "--head-guard" in sys.argv:
            await obstructed_head(b)
            await b.close()
            return
        if "--single-palm" in sys.argv:
            await single_palm_release(b)
            await b.close()
            return
        if "--wood-walk" in sys.argv:
            await school_waypost(b)
            await b.close()
            return
        if "--wood-letter" in sys.argv:
            await school_letter(b)
            await b.close()
            return
        if "--wood-palms" in sys.argv:
            await palm_instruments(b)
            await b.close()
            return
        if "--wood" in sys.argv:
            await listening_checkpoint(b)
            await b.close()
            return
        if "--press" in sys.argv:
            await press_checkpoint(b)
            await b.close()
            return
        if "--portrait" in sys.argv:
            await portrait_checkpoint(b)
            await b.close()
            return
        if "--pilots" in sys.argv:
            await pilot_checkpoint(b)
            await b.close()
            return
        if "--fen" in sys.argv:
            await fen_checkpoint(b)
            await b.close()
            return
        if "--swallow" in sys.argv:
            await swallow_checkpoint(b)
            await b.close()
            return
        if "--packet" in sys.argv or "--fen-pass" in sys.argv:
            await packet_checkpoint(b,"--fen-pass" in sys.argv)
            await b.close()
            return
        if "--parish" in sys.argv:
            await parish_checkpoint(b)
            await b.close()
            return
        if "--theatre" in sys.argv:
            await theatre_checkpoint(b)
            await b.close()
            return
        if "--palms" in sys.argv or "--belfry-palms" in sys.argv:
            await palm_instruments(b)
            await b.close()
            return
        if "--kitchen" in sys.argv:
            await kitchen_checkpoint(b)
            await b.close()
            return
        await crane_checkpoint(b)
        if "--engine" in sys.argv:
            await b.close()
            return
        await kitchen_checkpoint(b)
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
        await p.wait_for_function("bellProbe().dialogue && document.getElementById('words').textContent.includes('blue courtyard door')")
        await p.evaluate("testDevice.controllers.right.updateButtonValue('trigger',0)")
        await p.wait_for_timeout(120)
        await p.evaluate("testDevice.controllers.right.updateButtonValue('trigger',1)")
        await p.wait_for_function("!bellProbe().dialogue")
        await p.evaluate("testDevice.controllers.right.updateButtonValue('trigger',0)")
        await p.evaluate("testDevice.controllers.right.updateAxes('thumbstick',1,0)")
        await p.wait_for_function("Math.abs(bellProbe().vrForward[0])>.5")
        await p.evaluate(
            "testDevice.controllers.right.updateAxes('thumbstick',0,0);testDevice.controllers.left.connected=false"
        )
        await p.wait_for_function("!bellProbe().palms[0]")
        await p.evaluate("testDevice.controllers.left.connected=true")
        await p.wait_for_function("bellProbe().palms[0]")
        for room in [5, 17, 18, 19, 20, 21, 1, 6, 2, 7, 8, 9, 11, 14, 15, 16, 22, 23, 24, 25, 26, 27, 0]:
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
