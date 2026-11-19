# Bellwake release checks

## Tavi’s Paper Theatre

The browser route followed Tavi’s invitation, left and re-entered the courtyard, reconstructed four scenes from physical keepsakes, restored a mid-play checkpoint and played the four projector melodies. It printed both possible credits and checked the corresponding line from Tavi after both endings. Legacy morning-market checkpoints could enter and leave without losing their endings. An emulated Quest 3 used tracked controllers to talk to Tavi, enter the blue door, inspect the casting pattern and turn the figure reel.

Blender reimported the theatre FBX and checked 5,929 ground positions, 3,140 boundary rays and all twelve stations. The courtyard contains 11,694 visible-model triangles including the alternate scene pieces. Three laps of all 28 districts on the chapter candidate made 93 room transfers. Every transfer released the previous world, terrain collision and sky. Repeated visits reported identical GPU resource counts. [Paper theatre in play](paper-theatre.jpg)

## The Countertide Engine and the Harbour Mess

Ordinary walking and interactions completed 11 dispatches across three galleries. Four cargo deliveries took 16 station inputs, three crane assemblies took 91, and four signal flags took 50. The test restored each mechanism mid-job. The C# rules check covered 1,946 machine positions, 8,074 transitions and all six orders for the galleries.

The optional kitchen test learned all three audible fragments, read the journal after checkpoint reloads, recovered from a wrong note and served the returning crew. Each ending acknowledged their supper. The emulated Quest 3 operated the crane and the three-note kitchen phrase with tracked controller triggers. The release browser also restored the kitchen and its readable witness leaves with external requests blocked and the JavaScript decompression fallback active.

The five FBXs passed 5,929 ground samples and 3,140 boundary rays apiece. Every station had at least 52 walkable approach positions. The sets contain 12,758–21,928 triangles each. A separate differential test matched 15,360 body, palm and ray queries against the reference collision implementation.

The shipped browser models and collision buffers total 24.7 MiB compressed, down from 61.0 MiB unpacked. Three laps across 27 districts made 90 transfers and kept a single set, collision world and music source alive on every visit. The previous set, collision world and sky were all collected, and repeated visits had identical GPU resource counts. The median transfer was 530 ms, the 95th percentile was 1,182 ms, and the longest presentation gap during a transfer was 733 ms on the shared software renderer. A failed model request recovered at the last checkpoint.

The Root Choir bells, kitchen pans and keeper’s three seals now have palm strike surfaces placed in Blender. A separate emulated Quest run played 15 notes across the three locations with alternating hands. It held each hand at the contact surface to check for accidental repeats and finished the keeper encounter at full health. Physical controller vibration remains unmeasured.

On an emulated 8 Mbit/s connection with 40 ms latency and cache disabled, a cold transfer to the Drum House fell from 2.95 to 1.74 seconds, the Mould Loft from 3.10 to 1.40 seconds and the Harbour Mess from 2.28 to 1.20 seconds. These measurements run from the start of the transfer until the room unlocks. [Geometry, controls, loading and transfer measurements](countertide.json)

## Fresh-save completion time

The 26-area Countertide route candidate reached its first ending in **29 minutes 14 seconds of active play** and 29 minutes 46 seconds elapsed. The fresh-save runner used ordinary keyboard movement, a known route and chart hints. It finished the five wards, 27 dispatches, all 11 gallery jobs, five witness leaves, the optional night roll and a keeper retry. It restored the checkpoint to reach the other ending. It logged zero application errors. The optional kitchen was tested separately. For comparison, the previous 22-area route measured 25 minutes 55 seconds of active play. These were concurrent cloud software-rendering runs. A first-time human playthrough and physical Quest timing remain unmeasured. [Times for all 26 required areas](known-route.json)

## The Pilgrims’ Cut

Each of the five 120-metre-square wards has 225 surveyed cells. The tested order through the work yards covers 5.904 km along the lane centrelines. An ordinary-input playthrough gathered all 29 pieces of road work, reloaded each ward at a shelter, used the return bells and reached the Root Choir. A separate test opened the market book, read all five household letters for each ending, and restored an older final checkpoint that predated the road.

Blender reimported the shipped FBXs. In each ward the audit sampled the ground 56,169 times and cast 9,540 rays around the boundary. It checked another 8,400 crossings against the survey’s open and closed passages, including at ankle and head height. Every named station had at least 22 walkable approach positions in the connected ground flood fill. The new areas range from 25,824 to 39,306 visible-model triangles including the movable fixtures.

Three laps of all 22 areas made 66 transfers in Chromium. Each arrived with one active set, collision world and score. Forced collection released the previous set, collision world and sky every time. The repeated visits had matching GPU resource counts. The browser also recovered its checkpoint after a deliberately failed district download. In this concurrent SwiftShader run the median transfer took 773 ms and the 95th percentile was 1,330 ms, including three presentation frames. The worst interval during a transfer was 817 ms.

A separate test warmed each ward for 90 frames and turned through the scene for another 90. At 768 × 432 with adaptive rendering scale 0.512, SwiftShader median frame intervals ranged from 66.6 to 100 ms and the 95th percentiles from 116.6 to 200 ms. These cloud runs do not establish a comfortable headset frame rate.

The browser now queries the baked collision buffer directly. Across the five wards the previous loader added 11.1–19.0 MB to the Node JavaScript heap at load. The packed loader retained 0.95–1.56 MB of binary data per ward and added less than 9 KB to that heap at load, before the small contact pool warmed up. A differential check compared 67,584 capsule, sphere and ray queries in the 22 areas, including the contact normals and hit positions. The emulated Quest 3 tested the survey with A, tool acquisition with a trigger, a moving waywren with the left grip and hand-powered movement. Physical Quest frame timing and a first-time human completion remain unmeasured. [District, geometry, memory and transfer measurements](pilgrims-cut.json)

## Fresh-save completion time before the Pilgrims’ Cut

A clean browser profile began with Tavi’s first conversation, completed all 27 dispatches and all seventeen areas, earned the five witness leaves and restored Ina’s name to the roll. It reached the first ending after **7 minutes 3 seconds of active play** and 7 minutes 10 seconds on the wall clock. The run used the Wrenfall release at `5d44dec`, normal movement and interaction, chart hints and advance knowledge of the solutions. It included intentional checkpoint reloads and one keeper retry. The test then restored the decision and reached the other ending with zero application errors.

To time the current route, use the desktop playtest command below with `--timed` and a fresh browser profile. The results directory includes the active time for each area.

## Wrenfall Head

A player-input run went from Cinder Lens through all three guilds and across the 120-by-120-metre headland to the Still Belfry. It tried each optical instrument off target, sighted each offshore mark, saved and restored the first flag, and followed the Linnet to the berth. The cutter moved 27.66 metres between its measured start and end points. Seven crew models appear on arrival. An emulated Quest 3 crossed the former room boundary, reached the eastern rail beyond 38 metres and recorded the distant bell using head tracking and the controller trigger.

A checkpoint carrying Elin’s flood book reached both endings. The roster and Ina each gave their own response, and the book appeared in the journal after reloading the final decision. A pre-coast checkpoint reached both endings with its original journal. The emulated headset used the controller trigger to turn a journal page.

A separate clean checkout exported the packed Wrenfall Blender scene and reproduced all 17 mesh groups, 31 embedded textures, 34 scene nodes and the exact collision binary. Blender reimported the final FBX. Its 35,533 visible triangles passed 56,169 ground probes, 9,540 boundary rays and the connected approach check at all eleven stations. The final art pass kept the collision file and every reachable grid cell identical to the movement-tested version. Unity 2022.3.20f1 compiled the release and development scripts. The native rule check passed 256 mechanism states, 967 transitions and all six orders of the Lower Works.

The streamed edition loaded the coastal model, collision data, sky and music when restoring Wrenfall. The standalone HTML restored the same journal from its embedded assets. Across three laps of all seventeen areas, each of the 51 arrivals retained one world, one collision hierarchy and one score. Collection cleared every retired world, collision hierarchy and panorama. Revisited areas returned to their original geometry, texture and program counts.

On the cloud SwiftShader renderer the median door-to-ready time was 320 ms, the 95th percentile was 500 ms, and the longest frame during travel took 250 ms. The three coastal arrivals took 278, 320, 502 ms, including three presentation frames. Part of the soak overlapped other browser tests. Physical Quest timing and first-time human campaign duration remain unmeasured. [Per-transfer data, geometry and playthrough](wrenfall.json)

## Lower Works release

A keyboard-and-mouse run entered all eight chambers, restored a partially filled intake from a checkpoint, recovered three guild artifacts and rode the lift to the Still Belfry. It also completed the fourth hand’s petition. Separate epilogue runs read the earned nameplate in both endings. The native rules check visited 252 machinery positions, checked 955 transitions and completed all six possible guild orders. The Unity 2022.3.20f1 compiler accepted the release and development player and editor assemblies.

The eight new Blender exports passed 47,432 ground probes and 25,120 perimeter rays. Every station had at least 44 reachable approach cells. The emulated Quest 3 used a tracked controller to sign the night roll, crossed eleven room boundaries and retained the ability to plant a hand and push off.

A single Chromium tab crossed all sixteen campaign areas three times. After each of the 48 transfers one world, one collision hierarchy and one score remained live. Previous room roots, collisions and panoramas cleared after collection. Revisited areas returned to their original resource counts. A transfer within a guild kept the current music playing. Interrupting an asset request recovered the last checkpoint.

The cloud software renderer recorded a median of 278.5 ms and a 95th percentile of 525 ms from door selection to ready, including three presentation frames. Its largest transition frame interval was 333 ms. The run used SwiftShader and overlapped other browser work. Physical Quest frame pacing and first-time human completion time remain unmeasured. [All 48 transfers and dungeon playthrough results](lower-works.json)

## Earlier campaign checks

The browser playthrough started at Tavi’s market stall and used the normal movement, look and interaction controls. It collected every witness leaf, saved and reloaded a partial forest melody, solved the lock and lens puzzles, lost the belfry encounter, retried it and reached both endings. The watch roster and Ina each appeared in the appropriate epilogue. The run recorded zero application errors. The C# story explorer also visited all 35 reachable progression states and found a path to each ending from every unfinished state.

## Geometry and placement

Blender 4.3.2 reimported all eleven shipping FBXs. The five campaign districts passed 29,645 ground probes and 15,700 outward perimeter rays. The audit found a connected approach from the spawn to every story marker with a clearance sample wider than the player capsule. Each painted material had a usable UV range. The optional meadow gate also passed 15 approach-clearance rays, and five downward probes reached the outcrop’s climbable crown. Separately exporting the eleven packed Blender source files reproduced the audited triangle counts, station access and walkable cell counts.

During development the forge ledger intersected the crucible, and the entrance to the final chamber placed the player inside a column. The ledger now stands at its own lectern and the colonnade frames the entrance. The market’s architectural meshes and prop meshes now share a consistently named UV layer on export. Ground contact shadows are baked into the painted floor.

[Per-room geometry and access results](geometry.json)

## Frame timing

The table records 70 frame intervals per viewpoint after a 95-frame warmup in Chromium using the cloud computer’s SwiftShader software renderer. The viewport was 768 × 432. The adaptive 3D render scale settled at 0.512, while the interface stayed at the full viewport resolution. Each room uses a pre-painted panoramic sky. The game batches static geometry by material and keeps one district active.

| Room | Median frame interval | 95th percentile | Draw calls at sample |
| --- | ---: | ---: | ---: |
| Bellmender’s Market | 33.3 ms | 66.6 ms | 24 |
| Root Choir | 33.3 ms | 50.0 ms | 24 |
| Reedwater Lock | 33.2 ms | 50.0 ms | 24 |
| Cinder Lens | 33.3 ms | 50.0 ms | 25 |
| Still Belfry | 33.2 ms | 50.0 ms | 24 |

The software run showed occasional slow frames. A 72 Hz Quest frame takes about 13.9 ms. Measuring that target requires a physical headset. Development Unity APKs log a 360-frame sample after each room has warmed up.

[Browser timing and playthrough results](playthrough.json)

## XR, Unity and delivery

- Meta’s IWER Quest 3 profile entered an immersive stereo WebXR session and tracked both controllers. A test crouched the player, planted one palm and swept it back. After correcting the hand-release tolerance, the stroke moved the player forward approximately 0.53 m. The same test opened and closed the journal, spoke to Tavi by trigger, snap-turned, disconnected and reconnected a controller, and exited immersive mode.
- The Unity 2022.3.20f1 Roslyn compiler compiled all game scripts and all project editor scripts against the installed editor assemblies and the Input System 1.7.0, XR Management 4.4.0 and OpenXR 1.9.1 package sources. The editor itself stopped before asset import because the cloud machine had no active Unity license. Unity Play mode, shader compilation in the editor, Android APK export and physical headset comfort await a licensed editor and device.
- The original meadow geometry check passed. Mossbell Village’s existing path regression checked 2,085 route samples and found zero overlapping top-surface triangle pairs.
- The production HTML embeds its models, score, skies and runtime. Cloud Chromium’s file policy required loading that file over loopback for the release smoke test.

## Run the checks

From the repository root, export the packed scenes and generate `story.json` as described in the [build guide](guide.md). Install the web player dependencies, Python Playwright and a Chromium executable.

```sh
blender -b -t 2 --python-exit-code 1 --python Tools/bellwake/audit.py -- /tmp/bellwake-audit
python Tools/bellwake/web/package.py /tmp/bellwake-test/game.html --test
python -m http.server 8090 --bind 127.0.0.1 --directory /tmp/bellwake-test
```

In a second terminal, run the desktop journey and the emulated controller check.

```sh
python Tools/bellwake/web/playtest.py http://localhost:8090/game.html /tmp/bellwake-audit /tmp/bellwake-results
python Tools/bellwake/web/xr_playtest.py http://localhost:8090/game.html
```

In Unity, **Wizzard → Validate Bellwake rooms** checks the actual Unity-imported meshes, UVs, interaction markers, material names, cubemaps and audio clips. The Quest build menu runs this validation before building.

## Area streaming

The streamed browser build fetched only Bellmarket's model on startup. A single Chromium tab then visited all five districts three times. Each return matched the first visit's live geometry, texture and shader-program counts. One world, one collision hierarchy and one music player remained after each arrival. Weak references to the previous room root, collision hierarchy and panorama all cleared after garbage collection on every trip. Forced collection took place after the timing sample. The test also interrupted a room download and recovered the previous checkpoint. The offline HTML keeps the compressed source payload in the document and releases decoded room resources on travel.

On the cloud CPU renderer at 768 × 432, the median door-to-ready sample (including three presentation frames) was 248 ms and the largest presentation interval during a transition was 150 ms. Resource lifetime passed. These timings leave physical Quest frame pacing unverified. Both endings and all five witness leaves passed through normal keyboard interactions using the baked collision data. A separate emulated Quest 3 session crossed four room transitions and retained both tracked palms. [Per-trip measurements](streaming.json)

The C# meadow window passed 3,327 positions over three laps including map edges and teleports. The run counted 1,617 loads and 1,613 releases with four tiles at the final corner. Peak residency was 21 of 64 chunks. This check executes the selection and eviction code independently of Unity physics.

To repeat the browser travel test, package the test page with `--test --streamed`, serve it, and run `python Tools/bellwake/web/travel_test.py http://localhost:8090/index.html travel.json`. To exercise the native assets in a licensed Unity editor, enter Play mode and choose **Run Bellwake round-trip check (Play Mode)** from the BellwakeCampaign component's context menu. It traverses each campaign area and three meadow/village round trips while preserving the checkpoint. Development builds log transition duration, worst frame and allocated memory, followed by a 360-frame sample. Native runtime and device measurements require a licensed editor and a Quest.

## Witness Road campaign expansion

Saltwake Sound, Rimeway Post and Glasscut Gallery are now on the main route. Each district contains nine deliveries, three witness accounts, a distinct ruleset and an original music loop. A keyboard-and-mouse playthrough completed all 27 dispatches in sections, including 320 directional moves on their shortest routes. Each district preserved a partially completed chart across a page reload. A checkpoint from the earlier edition entered Glasscut from Reedwater. Both epilogues remained reachable. The player stores active time per district for future playtime measurement. A first-time human completion time is still unmeasured. [Route checks](witness-road.json)

The native rule check exercised four actions at each of 10,414 puzzle positions. Every position could reach delivery using hints or a local rewind. The Blender mesh check sampled another 17,787 ground positions and 9,420 perimeter rays. Every interaction had at least 56 clear approach cells in the conservative route grid. Runtime collision uses the exported triangles. A targeted player-input regression walked from Glasscut’s resonance cradle back to the chart and moved the miner. [Geometry results](geometry.json)

Use `Tools/bellwake/PassageCheck.cs` with `Assets/Scripts/BellwakePassage.cs` and Mono’s `System.Web.Extensions` reference to run the rule check. Pass `Assets/Resources/Bellwake` to its executable. The browser playthrough accepts `--last-post`, `--glasscut` and `--endings` to reproduce those crossings independently.

The expanded eight-district travel check made 24 transitions in a single browser tab. Per-district GPU counts held steady across all three visits and the previous world, collision tree and panorama cleared on every trip. An emulated Quest 3 retained both tracked palms through six transfers. A physical Quest run is still needed for the 72 Hz frame budget.
