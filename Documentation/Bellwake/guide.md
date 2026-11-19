# Bellwake

Tavi made a warning bell during the flood. Her sister Ina gave it a voice for a single night. Twelve years later, the bell still keeps watch. You arrive on the first morning it fails to ring.

| Place | What to do |
| --- | --- |
| Bellmender’s Market | Find Tavi on the path, then follow the brass way arch. The wooden sign leads to the Long Meadow in Unity. |
| The Root Choir | Listen to Moss. Ring the three individually pitched bells in the order described by the forest round. |
| Reedwater Lock | Ask Fen which channel saved the village. Each wheel changes the pair of sluices marked on its station. |
| The Cinder Lens | Trace the amber ray from the kiln. Turn the three mirrors and catch the light in the casting cup. |
| The Still Belfry | Speak to the keeper to start the encounter. Reach and activate the called seal before the toll. After three misses, the keeper lets you try again. |
| The morning market | Choose who carries the watch. Both choices change the market and open a final conversation. |

Each district holds a witness leaf. A chapter, puzzle action or recovered leaf updates the checkpoint. Unity stores the journey in PlayerPrefs. The browser edition saves to local storage for its current origin. The epilogue arch takes two deliberate activations to start a fresh journey.

## Controls

| Action | Quest controllers | Unity desktop | Browser desktop |
| --- | --- | --- | --- |
| Move and jump | Plant a palm on a surface, push and release | WASD and Space | WASD and Space, Shift to run |
| Look or turn | Head tracking and right-stick snap turn | Middle click to capture the mouse, Escape to release | Drag or use the arrow keys, double click to capture the mouse |
| Speak, ring or turn | Face a nearby station and press a trigger | E | E |
| Open or close the witness book | A or X | J | J |
| Read a collected leaf | In the Unity book, a trigger turns the page | E with the book open | Collected leaves appear in the book |

Crouching makes the ground easier to reach with the palms. The journal pauses the final encounter’s countdown.

## Direct browser play

Double-click `Play/Bellwake.html` in the downloaded project or extract the standalone play ZIP and open its HTML file. Geometry, textures, music and the JavaScript player are embedded. The browser edition contains the five campaign districts. The large meadow and Mossbell Village are accessible through the Unity edition.

For Quest Browser, serve the entire `Play` directory over HTTPS and open `index.html` for on-demand chapter downloads and choose **Enter VR**. With a USB-connected developer-mode Quest, a local alternative uses Python and Android platform tools on the PC. From the repository root, run these in separate terminals.

```shell
py -m http.server 8090 --bind 127.0.0.1 --directory Play
```

```shell
adb reverse tcp:8090 tcp:8090
```

Open `http://localhost:8090/index.html` in Quest Browser while USB forwarding is active. A compatible browser offers **Enter VR** on the opening screen.

## Editable art and sound

The eleven packed Blender sources in `Blender/Bellwake` contain the five sets, the meadow trail sign, the runner’s arms, the two individually modeled hands, the meadow outcrop and the mountain gate. The campaign reuses characters and props from the supplied Wizzard Themed Library, with articulated head and arm pivots on speakers. The cottages use the existing Mossbell Blender artwork. The court geometry, interactive mechanisms, bell tower, escarpments, banners, floor paintings, skies and score were authored for this campaign.

Ground and path share one continuous mesh. Lighting includes baked ground contact shadows. Buildings, clothing, brass and foliage use their own paintings and UV atlases. The Unity player loads one campaign room at a time and adds mesh colliders to the terrain, visible static set, rim and solid cores.

After editing the source, regenerate the FBX and GLB for that room from the project root. Blender 4.3.2 was used for the release.

```sh
blender -b --python-exit-code 1 --python Tools/bellwake/export.py -- RootChoir
```

The procedural authoring scripts are in `Tools/bellwake`. Rebuilding from those scripts uses the original Wizzard Themed Library folder. Editing and exporting the packed Blender scenes works independently of that download. The PNG paintings are under `Assets/Resources/Bellwake/Textures`. The six original music loops and four bell cues are under `Assets/Resources/Bellwake/Audio`.

## Rebuild the portable edition

Run the packed-scene exporter without a room argument to prepare all GLBs. Compile `Tools/bellwake/StoryGraph.cs` together with `Assets/Scripts/BellwakeJourney.cs` using Mono’s C# compiler and `System.Web.Extensions`. The resulting executable accepts the destination of the JSON story table. It checks that both endings are reachable from every unfinished state before writing the file.

```sh
blender -b --python-exit-code 1 --python Tools/bellwake/export.py
mcs -r:System.Web.Extensions -out:/tmp/BellwakeStory.exe Tools/bellwake/StoryGraph.cs Assets/Scripts/BellwakeJourney.cs
mono /tmp/BellwakeStory.exe Tools/bellwake/.web-assets/story.json
npm ci --prefix Tools/bellwake/web
python Tools/bellwake/web/package.py Play/Bellwake.html
```

The browser uses Three.js under the MIT license, included in the HTML. Meta’s IWER is a development-only dependency for the emulated headset checks.
