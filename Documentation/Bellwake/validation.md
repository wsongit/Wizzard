# Bellwake release checks

## Quest builds and save recovery

The release and profiling commands were exercised under Windows CMD in Wine with a test editor executable. Both valid outputs were recognized. A stale APK after an early exit, a missing output, and a reported Unity failure all returned failure. Mono tests covered atomic replacement, invalid native libraries and competing copies. A signed ARM64 packaging fixture passed Android SDK signature and alignment checks before and after copying. A native build of the game still requires activation of the cloud Unity editor.

All 16 combinations of app bundle, Gradle export, architecture split and expansion-file settings were exercised in a method harness for release and profile builds, including a forced validation failure. The previous preferences were restored in all 64 cases. A second harness checked 13 fresh, saved, edited and batch-mode opening scenes.

The native title can recover a slot from its previous checkpoint. A regression check exercised all three slot keys, original single-checkpoint saves, missing and malformed current entries, and restoration of the satchel, travel clock and puzzle progress. A separate development-profiler check injected overlapping focus and pause callbacks, a 100-second interruption and an active 50 ms frame. It excluded the interruption and reported the active hitch.

## Village, forest and river art pass

[Player-height views of the exported art](bellwake-valley.jpg)

Blender reimported the 42 district FBXs. Across those exports, 1,045,338 ground probes and 234,920 boundary rays passed. The flood-fill found an approach from spawn to all 461 interaction markers. On the connecting Highroad, 37,761 clearance samples passed across 72 links, with at most 18 of 42 near-detail cells required at once.

Seven traces across Bellmarket’s stairs each found eight consecutive treads. The highest rise was about 14 cm, within the character controller’s 15 cm step allowance. Another 113 rays checked that the well grate supports the player across the slats and their gaps. At Reedwater, 2,880 rays tested the paddle and hub guards over a full rotation. Opening, closing, solving and reloading the mill puzzle produced the expected wheel motion.

The 12 portable Blender exports contain 18,402 triangles in total. Sampled hen strides kept a supporting toe within 5 mm of the turf over 402 poses. The new shop, orchard, grove and keeper art use original meshes and textures. Ocarina of Time screenshots served as visual reference.

The native runtime and editor scripts compiled against Unity 2022.3.20f1 and the project’s pinned XR packages. Seventy vertex and fragment variants passed validation against Unity’s headers and GLSL ES. An offscreen GPU check compared the close-range filter with a numerical reference at 42,029 samples, including negative and wrapping UVs and four mip levels. The largest channel difference was below 0.001 on a 0–1 scale.

The streamed and single-file browser editions matched on all 172 packaged assets. The streamed opening requested only Bellmarket’s model. The single-file edition opened the market, accepted walking and turning input, and opened the journal after the browser connection was disabled. The Windows build log records an APK from before this art pass. The cloud Unity editor has no active license. Native APK installation, headset frame times and comfort still need a licensed build and physical Quest.

## Native Unity field

The new field passed 37,761 road clearance samples on 72 connections. The C# rules and Blender room checks passed. The native Android export stopped before import because this machine needs Unity license activation. Quest frame timing and native playthrough time are pending. [Field measurements, controls and art](native-field.md)

## Native bellrunner and market

The Unity 2022.3.20f1 runtime and editor scripts compile with the Android defines and pinned XR packages. The palm reach calculation passed 5,016 lowered controller positions for eye heights from 1.20 to 2.10 metres. The highest palm centre in those poses was 3.5 cm above the tracking floor, within the 10 cm contact radius. Shoulder-height and assist-off checks also passed.

The twelve shipping Blender models contain 11,328 triangles in total. Reimport checks found closed surfaces, nondegenerate UV faces, mapped texture files and both boot and wing pivots. All 528 Bellmarket footing samples were below the walking surface. The Mossbell audit checked 864 foundation samples and 82 grounded props. Ground and clearance checks found space for both shops and encounters in all six authored districts.

The inventory checks cover prices, repeat purchases, insufficient funds, equipment, healing, and saving after each encounter. The story graph still reaches both endings from every unfinished state. The field traversal peaked at 18 of 42 scenery cells using the native streaming distances. Headset frame times and the feel of floor strokes still need a physical Quest.

## Earlier browser highroad

The exported map passed 17,496 ground and overhead-clearance samples on 72 links. The headset emulator spoke with Tavi, checked that a tracked step held the player in place, dismissed the conversation and walked to Paper Court. A desktop check reloaded during a visit and halfway along the road, then reached the quest destination with one active world and collision tree. [Highroad controls and reference notes](highroad.md)

## Full playthrough before the highroad update

The first ending took **1:00:28 of active play** across 41 main-story districts in the desktop browser. The runner sprinted, used known puzzle solutions, collected five witness leaves and signed all six passenger accounts. It carried its earned save across a restart and into the expanded edition at the Countertide Engine. The in-game clock excludes loading, time away and the open journal. Both endings passed from the earned choice at the tower. First-time human and physical Quest completion times remain unmeasured. [Time by district](known-route.json)

## The Mercy Run

The six berths took 0:28:44 of active play. The runner checked the evidence at each yard, reloaded mid-journey, rejected a blank seal, signed one account at each landing and used the restored bells to board the next passage. Both morning journals showed the appropriate replies in the offline edition. An emulated Quest 3 turned the press with the controller trigger, credited Dot’s fare slip and opened the passenger roll.

The six Blender exports passed 337,014 ground probes, 57,240 boundary rays and 50,400 interior passage checks. All 102 stations had reachable approaches. Across 141 transfers covering all 42 districts, only the current world, collision tree and music player remained after each arrival. GPU resource counts matched on repeat visits. The lifecycle run used Chromium’s software renderer. Physical Quest frame pacing still needs a headset measurement. [Release checks](mercy-run.json)

## Rowan Hollow

The keyboard playthrough took six acoustic bearings and restored all three instruments. It rejected off-axis bearings, an incorrect drum phrase and an unbalanced clay bird. Reloading at the spring kept its water flowing. The northern wicket opened into the Root Choir after the third repair. The Quest emulator recorded a bearing from a tracked head turn, opened the linen survey and struck the beech drums with alternating hands. The native puzzle check completed all six orders of restoration.

Blender reimported the FBX and checked 42,025 ground samples and 8,260 boundary rays. Each of the 18 stations had at least 64 reachable approaches. A three-lap travel check made 15 transfers with one world, one collision tree and one music player active after every transfer. The previous worlds were collectible and the renderer returned to the same GPU resource counts on each revisit. [In-game views](rowan-hollow.jpg) · [Measurements](rowan-hollow.json)

Twelve woodland cells now switch between two meshes made in Blender. At eight fixed headings the renderer submitted 21,490 triangles on average, down from 37,247. Average draw calls rose from 21 to 24.5. Both versions used exactly the same packed collision data. In a separate 90-frame turning test, the software renderer recorded 33.3 ms median and 83.4 ms at the 95th percentile with the new meshes, compared with 33.4 ms and 100 ms before. These measurements came from Chromium with SwiftShader. Quest hardware timing remains open.

The market’s school path was tested from a first morning and both endings. Reloading at Linn’s hut retained the visit. The north wicket returned each player to the same story state with their witness leaves intact. A fresh player could still meet Tavi and enter the paper theatre afterward. The Quest emulator used the market sign and received the field book by controller.

After the last repair, Linn’s signed linen can be read in the journal outside the forest. The Quest controller emulator turned to the illustration in the Root Choir and checked that closing the book released its display.

A separate campaign pass made **123 transfers across all 36 districts**. Each transfer finished with one active world, one collision tree and one score. All three laps returned to the same renderer resource counts, and the test recovered from a failed model request by loading the last checkpoint.

Unity now imports each room’s four collision meshes onto the model and enables collision baking when building the Quest player. The source-model check found 144 matching surfaces across the 36 districts. The importer, player and build tools compiled against the Unity 2022.3.20f1 assemblies. Native build and load timings still require an activated editor and a headset.

## The Still Belfry

The keeper’s mask turns toward each side seal. Two raised wings indicate the seal behind the keeper. The desktop input test read all three gestures, operated the music box and played back three verses on the physical seals. A wrong note returned to the start of its own verse. Reloading kept the earlier verse, and both endings remembered the completed song. Blender reimported the final model and checked 5,929 terrain samples, 3,140 perimeter rays and all nine stations. The finished room has 11,452 visible triangles. The emulator rang all three required seals with alternating palms, opened the crank with a trigger and played the first verse by hand. The packed collision reference matched on 3,072 body, palm and ray queries and 2,766 visibility checks. Fifteen additional transfers repeatedly loaded and released the final room. [In-game views](the-quiet.jpg) · [Measurements](the-quiet.json)

The player now slows on landing after a palm push. Separate left- and right-hand trials pushed the emulated player 0.376 m, carried momentum on release and slowed horizontal speed to below 0.025 m/s on the floor. Disconnecting the planted hand produced zero launch speed and reconnecting it in clear space produced no contact.

## The Gloaming Press

A keyboard playthrough entered from the Cinder Lens, tried the locked gate and an incorrect exposure, turned five mirror wheels, developed all three pictures and carried the contact sheet into the Glass Rookery. It checked the rendered mirror angles, the exposure needles and the visible beam after each interaction. Reloading between exposures preserved the light path. Every one of the 3,219 native machine positions can reach its goal. The C# check traversed 17,631 transitions, including blocked shutters and the route onward.

Blender reimported the final FBX. It contains 14,280 visible triangles. All 5,929 terrain samples and 3,140 perimeter rays passed, and every station had at least 84 reachable approaches. The packed collision data matched the reference on 3,072 body, palm and ray queries and 4,557 line-of-sight checks. The emulator tested both the mirror and the shutter with a tracked Quest controller.

Three campaign laps made 120 transfers across all 35 districts. A separate 15-transfer pass used the final workshop geometry and the original 33-second *Silver Bath* score. Every transfer kept one active world, one collision tree and one music player. Previously loaded worlds were collectible, and revisits returned to the same GPU resource counts. A 90-frame SwiftShader turn in the shop recorded 32 draw calls, 33.4 ms median and 116.7 ms at the 95th percentile while another browser playthrough was running. An isolated 768 × 432 window pass on the final build measured 16.7 ms median in both the workshop and belfry, with 95th percentiles of 50.1 and 50.0 ms at 0.512 render scale. Physical Quest frame times remain open. [Final isolated samples](the-quiet.json) · [Measurements](gloaming-press.json) · [Four in-game views](gloaming-press.jpg)

## Tavi and Ina’s letter

Tavi’s face, fringe, clothes and tools share one 256 × 256 texture. Her head and arm keep separate pivots for looking at the player and gesturing. The Blender reimport sampled 5,929 ground positions and cast 3,140 perimeter rays in each of her two locations. Both passed.

Ina’s portrait is rendered in Blender from those same character meshes. A desktop test restored each ending and read the illustrated letter. A Quest controller emulator opened the page twice, turned to a different page and closed the book. The image texture was released each time. [Tavi in the market and her sister’s sketch](tavi-and-ina.jpg)

Wall visibility for selecting objects and sweeping the tracked head now exits on the first obstruction. The full differential suite compared 126,663 visibility tests with the reference collision system, including hits at the exact target distance. Another 104,448 ray, body and palm queries matched across all 34 districts. The native loader starts the panorama, score and room model requests together after releasing the previous district. A bird’s voice is queued only for a district containing its perch.

## Tracked movement and streaming

The Quest controller emulator planted a single palm and pushed 0.376 m with the other controller disconnected. Both hands independently carried momentum after release. Disconnecting the planted controller during the same stroke produced zero launch velocity. Reconnecting in clear space produced no contact. A separate check put the head below the market floor and pressed the trigger. The head guard blocked conversation. The capsule stopped a horizontal attempt to cross Tavi’s solid footing, and talking worked again from the clear side.

Three complete laps made 117 transfers through all 34 districts. One set, one collision tree and one background music player remained active at every destination. The previous scene, panorama, collision data and any replaced music player were collectible at every stop. Returning to the same district produced identical GPU resource counts. Drift Fen, Swallow Stair and the Glass Rookery each played their own score. [Streaming and audio checks](glass-rookery.json)

The optional Quest Browser timing report was exercised in an emulated 90 Hz session. The exported JSON included play intervals for Bellmarket, Drift Fen and the Glass Rookery, as well as both in-headset area loads. The emulator uses a cloud software renderer. Target frame time on a physical Quest is still unverified.

An isolated 768 × 432 desktop software-rendering pass warmed each of five districts for 90 frames and turned through a further 90. The 95th-percentile intervals were 66.6 ms in Bellmarket, 49.9 ms in the Paper Theatre, 50.1 ms at Swallow Stair, 50.1 ms in Drift Fen and 50.0 ms in the Glass Rookery. The adaptive render scale was 0.512 at each sample. These cloud intervals exceed the 13.9 ms budget for a 72 Hz headset. [Frame samples and renderer counts](field-frames.json)

## The Glass Rookery

The desktop runner started at the Cinder Lens gate, guided each bird into flight and checked its wing motion, landing and answer call. The three routes took 11, 12 and 14 operations. Reloading during the heron’s flight restored its destination. The player read the glasshouse ledger, took the gate to the Lower Works and released the valley, collision data, sky and last bird voice. Both ending conversations and the journal acknowledged Ina’s final delivery. An emulated Quest controller sounded the whistle and opened the illustrated chart.

Blender reimported the finished FBX and tested 19,881 ground positions and 5,700 perimeter rays. Every station had at least 62 walkable approaches. The scene contains 17,313 visible triangles and 46 material slots. The C# campaign check covered 3,120 machine positions and 16,839 transitions. [Rookery checks](glass-rookery.json) · [Four in-game views](glass-rookery.jpg)

## Drift Fen

The player-input test walked the floodplain, recovered all four objects in a different order from the sailing manifest, reloaded halfway and returned to both cranes. Distant soundings gave directional hints and kept objects concealed. The Quest controller emulator revealed and collected Pella’s clasp with the left grip and right trigger. Disconnecting and reconnecting the left controller hid and restored the handheld fork. Blender checked 48,841 terrain positions, 8,900 perimeter rays and all eleven stations. The final floodplain has 19,912 triangles and 37 visible material slots.

A return-fare test visited Drift Fen from Tavi’s first morning and from both endings, then checked that the original story state and witness leaves survived the ride home. A find made on the first visit stayed recovered on the second. A separate test performed forty idle animation frames after the lock settled and measured zero additional machinery updates. [Fen geometry and travel checks](drift-fen.json)

## Swallow Stair

The desktop input route delivered all four cargoes, reloaded Pella’s bag in transit, tested both filings of the watch slip and carried each result into Glasscut. The four crossings took 11, 8, 9 and 11 mechanical operations with the solutions known. The Quest controller emulator raised the fore pound, closed the west gate and transferred water to the aft pound. Blender reimported the lock and checked 5,929 ground positions, 3,140 perimeter rays and clear approaches to all 12 stations. The finished lock has 17,690 visible triangles. Across 15 between-area transfers, the travel check found one live set, one collision tree and one music player, and collected the previous scene each time. Physical Quest timing remains unmeasured.

## Long Meadow ground streaming

The native meadow reuses its vertex, UV, normal and triangle buffers as the player crosses the two-kilometre map. Adjacent tiles compute their edge lighting from the same surrounding heights. A managed test using Unity’s 2022.3 assemblies compared 69,696 vertices against the previous ground surface. The largest change in height was under one micrometre. Positions, UVs and normals matched at all 3,696 shared edge samples. Refilling the terrain buffers 640 times allocated zero managed bytes during the measured loop. Unity still allocates the mesh and its collider when a tile enters the world.

An additional travel test simulated 24 long-distance teleports over 1,536 streaming frames. Ground stayed available during each arrival, the maximum retirement count was two chunks per frame and the peak was 19 loaded tiles. A separate sweep covered 3,327 positions and peaked at 21 of 64. These checks exercise terrain generation and tile ownership. Frame timing on a physical Quest remains unmeasured.

## Three houses of Sillwater

A player-input test took all six optical bearings, rejected off-target sightings, restored the north landing after a reload, triangulated three deeds from the observed directions and left for Reedwater with Ada’s seal. A Quest 3 controller emulator opened and closed the field sheet, sighted the oar and moved the chart carriage 1.52 metres. The self-contained browser edition restored the flood map and signed title with external asset requests blocked.

Blender reimported all three shipped FBXs. The checks sampled 118,267 ground positions and cast 22,220 boundary rays. Every station and tide-change checkpoint was reachable. The ebb shore contains 30,840 visible-model triangles, flood has 30,664 and the office has 6,200. The C# progression check reached its goal from all 2,133 machine positions and checked 9,120 transitions. The game and editor scripts compiled against Unity 2022.3.20f1.

The 31-place streaming test made 105 transfers. Three additional laps made 21 transfers between the finished shores, office, lock and market. The previous world, collision tree and panorama were collectible on every transfer. Returning to the same area produced the same GPU resource counts. The meadow streaming model crossed 3,327 positions and peaked at 21 of 64 chunks loaded. Unity now queues the current area’s texture requests during the fade. Physical Quest frame times and native APK execution still need a licensed device build. [Parish geometry and playtest measurements](sillwater.json)

An isolated 768 × 432 software-rendering check warmed each parish area for 90 frames, then turned through it for another 90. The 95th-percentile frame intervals were 66.7, 66.6, 50 ms at ebb, at flood and in the office respectively. These timings exceed the 13.9 ms budget for 72 Hz. The test used Chromium SwiftShader and adaptive resolution at 0.512 scale. The physical headset’s GPU has yet to be profiled.

The return ticket was tested from a fresh market, an older Reedwater checkpoint and both endings. The test reloaded at flood, used the towpath before signing, and confirmed the original story checkpoint and ending on return. A completed early survey carried its title past Rimeway. An emulated Quest controller used the market counter and took the packet back. Across the market, lock and three parish areas, 15,360 capsule, sphere and ray queries matched the reference collision implementation.

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

The 26-area Countertide route candidate reached its first ending in **29 minutes 14 seconds of active play** and 29 minutes 46 seconds elapsed. The fresh-save runner used ordinary keyboard movement, a known route and chart hints. It finished the five wards, 27 dispatches, all 11 gallery jobs, five witness leaves, the optional night roll and a keeper retry. It restored the checkpoint to reach the other ending. It logged zero application errors. The optional kitchen was tested separately. For comparison, the previous 22-area route measured 25 minutes 55 seconds of active play. These were concurrent cloud software-rendering runs. A first-time human playthrough and physical Quest timing remain unmeasured. [Times for the 26-area release](https://github.com/wsongit/Wizzard/blob/cd11d43/Documentation/Bellwake/known-route.json)

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

## Rowan Hollow and campaign checkpoint recovery

The fresh-save browser run played from Bellmarket through Rowan Hollow, the three guilds and the launch at Wrenfall. A cloud restart interrupted the run there. Separate keyboard playtests crossed the reef, completed all three Countertide workshops, reached Still Belfry and played both endings. The Wrenfall test measured 27.66 metres of vessel travel. The Countertide test checked 157 station inputs and restored each machine after a page reload. At the time of that recovery test, the pre-forest timing was 35 minutes 16 seconds.

The timed runner now saves the earned browser state and elapsed time on disk at chapter entries. In a recovery test, a fresh character finished the paper play and Saltwake, then the test process was stopped at Quince Fold. A new browser restored the first witness leaf and completed the knife and stock stations in the orchard. To repeat the run, serve the instrumented build and use the navigation grids from the Blender audit. Keep the result directory on persistent storage. Use the same build, navigation grids and result directory when resuming.

```sh
python Tools/bellwake/web/playtest.py URL AUDIT_DIRECTORY RESULT_DIRECTORY --timed --compact
python Tools/bellwake/web/playtest.py URL AUDIT_DIRECTORY RESULT_DIRECTORY --resume --compact
```

After an interruption, the runner replays the unfinished chapter. The elapsed time follows the saved route and excludes downtime and discarded attempts. The first ending produces `known-route.json`. The second ending and journal checks produce `playthrough.json`.
