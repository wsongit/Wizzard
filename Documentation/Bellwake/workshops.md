# The workshops of Bellwake

From the Bellmarket well, walk to the shuttered house near the northwest corner and look between the crossbars. There are shelves and pots in the shop window. Come back after sunset and the lamp lights the same objects. At Flood Ledger, walk past the deposits and look along the spines of the books. At Cinder Lens, crouch beside the kiln grate. The fire changes shape above a bed of coals that stays in place.

[Ten full-size screenshots from the playable game](workshop-gameplay.zip) · [View the contact sheet](workshop-gameplay.jpg) · [Compare the same views in the previous release](workshop-comparison.jpg)

## Where to look

| Location | What to look for |
| --- | --- |
| Bellmarket | A clay tile edge and pegged oak fascia run along the cottage eaves. Each jamb carries its grain down to the limestone threshold. Sills, shutters and crossbars cast real silhouettes in front of the shop painting. |
| Root Choir | Foresters have left logs and supplies beneath the living arches. Bark runs lengthwise on the wood and growth rings cross its cut ends. Small marks of grass pick up the light at your feet. |
| Mould Loft | Ara wears an apron over her shirt and carries a measuring rule. Her nose, brow, hair and jaw are modelled in profile. Her half-closed eye keeps a sliver of iris during a blink. |
| Gloaming Press, Flood Ledger and Sillwater Parish | Press drawers, leather bindings, pale page edges and cabinets carry different paintings. Walk beside a shelf to see the ledges and volumes pass in front of one another. |
| Cinder Lens, Casting Bed, Saffron Kilns and Supper Steps | Look through the front of the fire grate. The tips flicker over darker logs. The sixteen-frame painting is sampled at the same instant for both eyes. |
| Wrenfall Head | The berth has stores for the boat. Past the lighthouse, the headland descends to the seabed and meets the outer water. |
| Highroad | Enter a settlement and return through its gate. Near objects stream with the district, while the road has its own working yards and distant hills. |

## How the art is put together

The stock includes thirty-two paintings for lids, staves, folded cloth, fruit, bread, rope, book spines and other goods. Each piece has volume. A jar's shoulder and mouth have different pictures. Blender groups the stationary stock into a single render batch per district. Its contact shadows are painted directly into the ground beneath the placed goods. The placement data also drives the shadows when the scene is rebuilt. [Stock models](../../Tools/bellwake/workyards.py) · [Goods paintings](../../Tools/bellwake/workyard_paint.py) · [Baked contact shadows](../../Tools/bellwake/stock_contacts.py)

At normal standing height a path has two levels of detail. The large district painting gives it direction, bends and crossings. The smaller marks carry grass, grit, slate or snow at a consistent physical size. A single texture lookup supplies all four choices. A packed-earth fork shares a continuous walkable mesh with the adjoining terrain. [Ground paintings](../../Tools/bellwake/ground_brush.py) · [District surface choices](../../Assets/Resources/Bellwake/GroundPrints.json)

The cast has painted eyes, fitted clothes and character-specific hair, caps, tools and aprons. Inspect a packed scene in Blender to see the separate faces, folds and seams. A garment moves with its wearer, and an eyelid change uses the actor's existing portrait sheet. [Resident modelling](../../Tools/bellwake/residents.py) · [Character designs](../../Tools/bellwake/resident_designs.py) · [Texture source paintings](../../Tools/bellwake/surface_sources)

[See 41 residents and keepers rendered from the Blender files](workshop-cast.jpg)

The reference workbook records how the original N64 village fits pictures to things you can walk around, with measured examples for a sign, a roof, a pot, a crate, a person's eyes, tree foliage and a door. It also explains the different choices Bellwake makes for a player who can lean or crouch in VR. [Ocarina art workbook](ocarina-art-workbook.md)

## Two close looks

At Rime Post, walk to the leaning pine at the last courier bearing. Windward boughs have pale snow on the upper needles. Dark green sprays show beneath their irregular tips. The shorter pine behind it has a different outline and faces the same prevailing wind. The two share one 128 × 128 image and one material. [Winter fir painting and profiles](../../Tools/bellwake/rime_firs.py)

At the Still Belfry, walk around the winged keeper. Each engraved feather has one spine running from shoulder to tip, even where the feather has a faceted ridge down its middle. Porcelain, brass, watch cloth and enamel each use their own section of the same image. The coat painting goes from hem to collar, and the end caps have a separate flat projection. [Keeper paintings and Blender UV fitting](../../Tools/bellwake/keeper_paint.py)

## Texturing a house or prop you add in Unity

Choose **Wizzard → Create retro material library**. In the Project window, open **Assets → RetroMaterials → Workshop**. Drag **Tile fascia**, **Oak lintel**, **Rebated jamb** or **Stone threshold** onto the matching mesh slot. A crate can use **Crate side** round its body and **Crate lid** on the top. The twelve Workshop materials already point at the individual regions of the two paintings. A face with UVs spanning zero to one shows its selected picture. Existing materials you have edited keep their settings when you run the menu again. [See the twelve material swatches](workshop-materials.jpg)

## The shop window through the day

Stand in front of the baker’s west window in Bellmarket. At noon the sill catches the sun. At dusk the warm shelves begin to show through the glass, and by midnight the pots are silhouetted against the lamp. These three captures use the same player position. [View the same shop window at noon, dusk and midnight](workshop-day-and-night.jpg)

Walking up to that window exposed a movement fault. Each frame of gravity pushed a resting player a little downhill. The WebXR and desktop controls now resolve an idle downward step vertically on walkable ground. A tracked player walked to the shop and stood there for two minutes. The previous build moved the player 36 centimetres during the test. In the updated build the player held position throughout. An active palm stroke still pushes the body against the surface normal. [Incline regression check](../../Tools/bellwake/web/standing_check.mjs)

Two floor joins also needed a separate repair. In Glasscut and Sillwater Ebb, the bottom of the player could slip between two sloped triangles at their shared edge. The browser player now checks the closest point on each walkable triangle against the rounded foot. The floor survey settled desktop and VR players at 5,285 reachable positions across 42 districts. It exercised 10,545 clear starts and skipped 25 starts already touching another object. The player kept floor support in every exercised case.

## Rowan Hollow from the path

The same tree beside the cottage has painted leaf clusters in daylight and at dusk. Walking away switches the grove to a simpler mesh that shares the bark and leaf paintings. I walked past the two switching distances in all twelve groves. Each group switched once on the way out and once on the way back, and the live texture count held at 34. [See the tree from three points on the walk](workshop-woodland.jpg)

## Release checks

The 46 playable models contain 966 image references to 215 distinct paintings. Eight of the larger shared sheets occupy 901,735 bytes in the published game. Those same PNGs occupied 24,433,459 bytes across the original model references before packaging. In the largest changed district, Bellmarket, the model images add 3.5 MiB of estimated RGBA8 storage with full mip chains over the previous release. Actual headset memory use depends on the driver and the other resources the game has open.

The FBX geometry tests sampled 1,045,338 ground positions and cast 234,920 boundary rays. The landscape check cast another 117,396 probes across 44 Blender scenes. The 768 textured triangles on the keeper's enamel and the 768 on the Rime Post fir mantles all have two-dimensional texture coordinates. The packed source images in all 51 editable Blender files matched the project paintings.

The desktop game opened the market and journal in both editions. The single-page edition did so with a single document request and subsequent network requests blocked. The signed WebXR APK updated in place on an Android emulator, retained its application identity and served all 182 packaged files with the expected contents. Headset comfort and frame time require a physical Quest. [Release measurements](workshop-test-results.json)

Seven matched camera views compared the previous edition with the workshop art. The added stock, trim, foliage and character detail cost two to four extra draw calls per view and three to six additional live textures. The market road went from 38 to 42 draw calls and from 22,913 to 25,149 visible triangles. The timings in the measurements file come from a cloud software renderer. A separate comparison recorded its GPU-process CPU use. Among the six views that held the same render scale in all four runs, the new art used between 2% and 30% more CPU per frame on that renderer. [Per-view costs](workshop-test-results.json)

I entered and exited VR twelve times in each retail browser edition using the title screen and the witness book. After warmup the number of live WebGL textures, buffers and programs stayed constant between sessions. In the streamed edition both hands and the arm model downloaded once. The single-page edition needed just its initial document request for all twelve visits.

All 1,766 render primitives in the 46 shipped models have a base-colour painting and a complete corresponding texture-coordinate channel. Regenerating the 42 districts and the highroad from their Blender sources reproduced the shipped geometry audit results. Wrenfall’s heather boulders now use its own station list during regeneration, so adding another chapter at the end of the story preserves their placement.

In Unity, four high-contrast paintings now blend neighbouring mip levels as the player steps back. The largest measured change was on the snowy firs. In a controlled sampler test, the mean of the 90th-percentile brightness-weighted colour changes across five mip boundaries fell from 18.7 to 1.2 levels on a 0–255 scale. The eaves, character clothing and workshop goods also showed visible jumps with a single mip. Nearby texels keep the three-point filter. The ground detail brush also blends between distance levels. [Unity texture import](../../Assets/Editor/BellwakeImport.cs) · [Sampler measurements](workshop-test-results.json)

The Unity Android build now imports each district’s ground painting at its original dimensions using 4 × 4 ASTC blocks. A 512 × 512 painting with all its distance levels occupies 349,552 bytes in this format. The same pixels occupy 1,048,575 bytes in RGB24. Across the 42 paintings the compressed image data totals 16.3 MiB. The game streams one district at a time. I compared the compressed blocks and the original pixels in 168 matched views, including close ground, paths seen at a shallow angle and night scenes. In every view, 99% of visible ground pixels differed by less than five brightness-weighted colour levels on a 0–255 scale. [Camera and image measurements](workshop-test-results.json)

In the native ground shader, switching abruptly between distance levels made the gravel and grass change tone as the player moved. I tested six boundaries across all 42 ground paintings in daylight and at night. Allowing the sampler to blend neighbouring levels reduced the median 95th-percentile daylight change from 10.6 to 0.9 colour levels. All 504 comparisons showed a smaller change. The extra filtering has a cost. In the Android software renderer, a 256 × 160 patch of distant ground took a median of 2.64 ms to draw with the new format and filtering, compared with 1.79 ms for the previous uncompressed, single-mip sampling. The Android emulator also ran the Unity ground fragment shader at six viewing scales against the original and compressed paintings. [Android shader comparisons](workshop-test-results.json)

An Android texture-streaming check loaded all 42 district paintings in eight different orders. On each visit it drew the Unity ground shader, released that district’s texture and kept the shared detail brush. Every return produced the same pixels. The guest test process used 7,336 KiB at the end of the first lap and 7,300 KiB at the end of the eighth.
