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


## Release checks

The 46 playable models contain 966 image references to 215 distinct paintings. Eight of the larger shared sheets occupy 901,735 bytes in the published game. Those same PNGs occupied 24,433,459 bytes across the original model references before packaging. In the largest changed district, Bellmarket, the model images add 3.5 MiB of estimated RGBA8 storage with full mip chains over the previous release. Actual headset memory use depends on the driver and the other resources the game has open.

The FBX geometry tests sampled 1,045,338 ground positions and cast 234,920 boundary rays. The landscape check cast another 117,396 probes across 44 Blender scenes. The 768 textured triangles on the keeper's enamel and the 768 on the Rime Post fir mantles all have two-dimensional texture coordinates. The packed source images in all 51 editable Blender files matched the project paintings.

The desktop game opened the market and journal in both editions. The single-page edition did so with a single document request and subsequent network requests blocked. The signed WebXR APK updated in place on an Android emulator, retained its application identity and served all 182 packaged files with the expected contents. Headset comfort and frame time require a physical Quest. [Release measurements](workshop-test-results.json)
