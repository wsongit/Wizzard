# Bellwake

Tavi made a warning bell during the flood. Her sister Ina gave it a voice for a single night. Twelve years later, the bell still keeps watch. You arrive on the first morning it fails to ring.

| Place | What to do |
| --- | --- |
| Bellmender’s Market | Find Tavi on the path, then follow the brass way arch. The wooden sign leads to the Long Meadow in Unity. |
| Saltwake Sound | Find Marn’s three witness posts. At the chart chest, steer the skiff through currents, touch the brass buoy, then reach the white mooring ring. |
| The Pilgrims’ Cut | Restore the Quince Fold, Saffron Kilns, Vellum Walk, Cairnwatch Rise and Rain Court. The road continues to the Root Choir. |
| The Root Choir | Listen to Moss. Ring the three individually pitched bells in the order described by the forest round. |
| The Rimeway Post | Recover the lost post. Slide the mail sled through the cache and stop it at the landing. |
| Reedwater Lock | Ask Fen which channel saved the village. Each wheel changes the pair of sluices marked on its station. |
| Glasscut Gallery | Read Jass’s casting records. Move the bronze miner behind the gem cart and push it onto the white socket. |
| The Cinder Lens | Trace the amber ray from the kiln. Turn the three mirrors and catch the light in the casting cup. |
| The Lower Works | Sign the night roll below Cinder Lens. Explore the three guild wings in any order, listen to the craftspeople and take their work to the great resonator. |
| Wrenfall Head | The resonator lift emerges on the Pilots’ Coast. Help Mirren bring the flood book through the reef. |
| The Still Belfry | Speak to the keeper to start the encounter. Reach and activate the called seal before the toll. After three misses, the keeper lets you try again. |
| The morning market | Choose who carries the watch. Both choices change the market and open a final conversation. |

The market, Root Choir, Reedwater, Cinder Lens and belfry each hold a witness leaf. Each of the three witness-road districts has nine dispatches and three witness posts. The compass keys on the chart chest take a trigger or E. The navigator offers a hint, the rewind lever resets the current chart, and the stamping desk certifies a delivery. Current chart positions and sealed dispatches survive a reload. A chapter, puzzle action or recovered leaf updates the checkpoint. Unity stores the journey in PlayerPrefs. The browser edition saves to local storage for its current origin. The epilogue arch takes two deliberate activations to start a fresh journey.

The witness book shows active playtime. Loading, the open journal and unfocused play are excluded. The clock starts with this update for existing checkpoints. Players already past a new district retain their place in the story.

The known-solution desktop run before the Pilgrims’ Cut reached an ending in 7 minutes 3 seconds of active play. A first-time human completion time is still unmeasured. [Playthrough details](validation.md)

## The Pilgrims’ Cut

Mara keeps the orchard shelter on the road out of Saltwake. The flood survey erased a public right of way. An old tree, the tilemakers’ mile and the evidence of the families who used the road can restore it. Each ward has a survey board. Open your witness book to see the same survey with your location marked in red. Each square measures eight metres.

At the grafting bench, take Mara’s brass waywren. Press Q or squeeze the left grip to send it along the lanes toward the next available job. It waits after four junctions. You can call it again wherever you stand. Work yards double as shelter checkpoints. After restoring a ward, ring the return line at the final work yard to reach the entrance. The other bell carries you to the open wicket. Later wards have a return path to the previous one.

[Five work yards and the orchard survey as they appear in play](pilgrims-cut.jpg)

## Beneath the village

In the Court of Three Trades, stand by the night roll and look toward the doors. West leads to the waterworks, east to the foundry and north to the lampmakers. Each wing has two chambers. Follow their service stairs to move between trades. A return to the court preserves your work at every machine.

At the intake, the narrow and wide tanks measure three and five. Use the gauges while drawing, transferring and emptying water. The archive records what people heard when the flood arrived. In the weigh house, the old western pan already carries a burden. The casting bed beyond it holds a cold mould. In the lampworks, follow both beams and read the bearings beside the orrery windows. When all three guilds have entrusted you with their work, fit the artifacts in the rotunda, play the testimony and hear Ina before taking the final lift.

**The Fourth Hand** is optional. Ask Nema in the court whose name was left off the night roll. Fen knows the rope knot, Orrel kept the pay leaf and Brannic kept a spare wage. Ossa can cast the three proofs into a nameplate. Bring it to Nema. On your final return to Bellmarket you can read it at the way arch in either ending.

## The Pilots’ Coast

Mirren waits outside the chart shelter. The large survey beside her shows where the paths meet. The western chapel records the water level the cutter needs. At Split Stone, use the sighting rail, face the bell on the distant stack and press E or a trigger to record the bearing. The northern lookout has a glass trained on a second mark. You can walk a few steps around each instrument for a clearer view. The journal records each observation.

At the eastern mast, pull the halyards in the order the pilots recorded. The flags above you show how many signals the cutter has acknowledged. Haul the harbour capstan, watch the Linnet round the reef, then meet her skipper at the landing to continue to the belfry. Her signed flood book stays in your journal. At the morning market, the harbour crew has a different part in each ending.

[Four views from the headland](wrenfall.jpg)

## Controls

| Action | Quest controllers | Unity desktop | Browser desktop |
| --- | --- | --- | --- |
| Move and jump | Plant a palm on a surface, push and release | WASD and Space | WASD and Space, Shift to run |
| Look or turn | Head tracking and right-stick snap turn | Middle click to capture the mouse, Escape to release | Drag or use the arrow keys, double click to capture the mouse |
| Speak, ring or turn | Face a nearby station and press a trigger | E | E |
| Open or close the witness book | A or X | J | J |
| Call Mara’s waywren in the five wards | Left grip | Q | Q |
| Read a collected leaf | With the book open, a trigger turns the page | E with the book open | Collected leaves appear in the book |

Crouching makes the ground easier to reach with the palms. The journal pauses the final encounter’s countdown.

## Direct browser play

Double-click `Play/Bellwake.html` in the downloaded project or extract the standalone play ZIP and open its HTML file. Geometry, textures, music and the JavaScript player are embedded. The browser edition contains all twenty-two campaign areas. The large meadow and Mossbell Village are accessible through the Unity edition.

For Quest Browser, serve the entire `Play` directory over HTTPS and open `index.html` for on-demand chapter downloads and choose **Enter VR**. With a USB-connected developer-mode Quest, a local alternative uses Python and Android platform tools on the PC. From the repository root, run these in separate terminals.

```shell
py -m http.server 8090 --bind 127.0.0.1 --directory Play
```

```shell
adb reverse tcp:8090 tcp:8090
```

Open `http://localhost:8090/index.html` in Quest Browser while USB forwarding is active. A compatible browser offers **Enter VR** on the opening screen.

## Editable art and sound

The packed Blender sources in `Blender/Bellwake` contain the twenty-two campaign sets, the meadow trail sign, the runner’s arms, the two individually modeled hands, the meadow outcrop and the mountain gate. The campaign reuses characters and props from the supplied Wizzard Themed Library, with articulated head and arm pivots on speakers. The cottages use the existing Mossbell Blender artwork. The court geometry, interactive mechanisms, bell tower, escarpments, banners, floor paintings, skies and score were authored for this campaign.

Ground and path share one continuous mesh. Lighting includes baked ground contact shadows. Buildings, clothing, brass and foliage use their own paintings and UV atlases. The Unity player loads one campaign room at a time and adds mesh colliders to the terrain, visible static set, rim and solid cores.

After editing the source, regenerate the FBX and GLB for that room from the project root. Blender 4.3.2 was used for the release.

```sh
blender -b --python-exit-code 1 --python Tools/bellwake/export.py -- RootChoir
```

The procedural authoring scripts are in `Tools/bellwake`. Rebuilding from those scripts uses the original Wizzard Themed Library folder. Editing and exporting the packed Blender scenes works independently of that download. The PNG paintings are under `Assets/Resources/Bellwake/Textures`. The nineteen original music loops and four bell cues are under `Assets/Resources/Bellwake/Audio`.

## Rebuild the portable edition

Run the packed-scene exporter without a room argument to prepare all GLBs. Compile `Tools/bellwake/StoryGraph.cs` together with `Assets/Scripts/BellwakeJourney.cs` with `Assets/Scripts/BellwakePassage.cs` and `Assets/Scripts/BellwakeWorks.cs` using Mono’s C# compiler and `System.Web.Extensions`. The resulting executable accepts the destination of the JSON story table. It checks that both endings are reachable from every unfinished state before writing the file.

```sh
blender -b --python-exit-code 1 --python Tools/bellwake/export.py
mcs -r:System.Web.Extensions -out:/tmp/BellwakeStory.exe Tools/bellwake/StoryGraph.cs Assets/Scripts/BellwakeJourney.cs Assets/Scripts/BellwakePassage.cs Assets/Scripts/BellwakeWorks.cs
mono /tmp/BellwakeStory.exe Tools/bellwake/.web-assets/story.json
npm ci --prefix Tools/bellwake/web
python Tools/bellwake/web/package.py Play/Bellwake.html
```

The browser uses Three.js under the MIT license, included in the HTML. Meta’s IWER is a development-only dependency for the emulated headset checks.
