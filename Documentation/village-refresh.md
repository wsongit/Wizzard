# Mossbell Village art refresh

Mossbell now uses a terraced late-1990s village atmosphere with its own landmark, buildings, props and texture artwork. The reference pack informed material scale, value grouping, terrain edges and composition. No reference pixels, ripped models, Nintendo characters, logos, music or map data were used to generate these assets. This documents the design work; it is not a legal clearance opinion.

## What changed

- The hilltop windmill is replaced by an **open oak bell pavilion**: three brass bells, a wide hipped slate roof, a smaller offset red cap and a leaf-shaped weather vane.
- The central round well is replaced by **two rectangular spring basins** under a tiled shelter beside the main route. The centre of the court stays open.
- Six cottages retain varied proportions and angles. Slate and terracotta roofs, cream and ochre plaster, shutters, bell plaques, and two canvas porch canopies give the workshops different identities.
- Seven tree variants have irregular green leaf clusters with dark gaps and lighter leaf accents. Height, crown proportions, cluster count and branch arrangement vary. Every root is checked against the terrain, including the two upper terraces.
- Planters with golden flowers, a potter's handcart, benches, crates and small brown garden birds add signs of village life.
- The spring rim uses non-overlapping stone sections, and ramp landings have a 2 cm separation from terrace surfaces to prevent coplanar flicker.
- All village textures are original **64×64** images generated from the checked-in authoring code. Grass and foliage use irregular painted patches and short strokes; natural rock uses irregular elongated facets instead of masonry rows. Roof tiles, plaster, wood, cloth, brass and water use distinct patterns. The textures are softly filtered with mipmaps. Cutout path shoulders reveal the actual grass underneath, eliminating the mismatched grass-texture seams on the old path strips; mipmaps preserve their alpha coverage.

## Deliverables and viewing

Editable source: `Blender/MossbellVillage.blend`. Unity export: `Assets/Resources/Village/Mossbell.obj` and `.mtl`. Textures: `Assets/Resources/VillageTextures/`. The exported model remains batched by material, with separate collision and arrival/exit marker groups.

![Mossbell entrance, actual Blender render](mossbell-street.png)

[Before refresh](mossbell-before-refresh.png) · [Spring and terrace](mossbell-spring.png) · [Upper terrace](mossbell-terrace.png) · [Layout overview](mossbell-village.png) · [Export reimport preview](village-export-check.png)

In Unity, open `Assets/Scenes/Meadow.unity`, press Play and then **F8** for the desktop entrance view. Press F8 again to move around. In VR, enter through the village gate at meadow coordinates X 240, Z 104. The existing fade transition and gorilla locomotion load this updated model without a new scene setup.

## Validation

The generator checks ground support and head clearance along six routes, including the left stair and both right-hand climbs. Seven tree roots are ray-checked against terrain-only geometry so a floating trunk cannot validate itself. The export validator checks finite vertices, valid indices, non-collapsed UVs, required material/marker groups, 64×64 texture dimensions and portable diffuse/alpha MTL paths. The path PNG must preserve its RGBA mask, and reimport also verifies its alpha range. The wall checker verifies closed wall shells, consistent normals, and visibility from inside/outside the perimeter. OBJ reimport checks the actual exported model and texture references, then renders it.

Results are recorded in `village-geometry-checks.json` and `village-wall-checks.json`:

- **PASS:** six supported routes, 655 centreline samples with footprint/headroom checks.
- **PASS:** all seven tree roots meet terrain within 0.1 m.
- **PASS:** 30 closed wall shells and 338 inside/outside visibility rays.
- **PASS:** OBJ indices, finite mesh/UV data, UV area, material groups, 64×64 image dimensions and portable diffuse/alpha texture references.
- **PASS:** exported OBJ reimport, marker positions, UVs, actual PNG loading and path alpha range; a fresh reimport preview was rendered.
- **Measured:** 13,618 visible triangles in 20 material batches; 4,244 collision triangles; 24 marker triangles. This is an asset count, not a measured headset frame rate.

The images here are Blender renders, not Unity or headset captures. Unity 2022.3.20f1 and a Quest headset are unavailable in this environment. Unity import, shader compilation, hand collision, stereo appearance and device frame timing still need on-device/editor validation. Houses remain exterior shells; bells, water, birds and cart are static scenery.

## Rebuild

```sh
blender -b -t 8 --python-exit-code 1 --python Tools/create_village.py
python Tools/check_village_export.py
blender -b -t 4 --python-exit-code 1 --python Tools/check_village_roundtrip.py
blender -b -t 4 --python-exit-code 1 --python Tools/check_village_walls.py
```

Review the generated entrance, spring, upper-terrace and overview views before accepting future palette or geometry changes. Keep the artwork at 64×64 rather than mistaking a large screenshot's dimensions for the size of an original material texture.
