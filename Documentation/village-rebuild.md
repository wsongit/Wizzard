# Blender village rebuild

The supplied daytime entrance image is the primary composition reference. The other daytime view informs the terrain and buildings. Twilight lighting is deferred. No reference image is used as a flat backdrop; the village remains 3D. The six current-gameplay screenshots described in the pasted brief were not available as separate files in this session.

## Deliverables

- `Blender/MossbellVillage.blend`: editable metre-scale source, named cottage components, terrain, landmarks, seven varied trees, collision collection, packed original textures and four review cameras.
- `Assets/Resources/Village/Mossbell.obj` and `.mtl`: Unity-compatible UV-mapped export. Temporary export copies are batched by material; the Blender source retains separate objects.
- `Assets/Resources/VillageTextures`: original 64×64 painted-style tiles with broad pigment patches, worn stone/roof edges and woodgrain. Bilinear filtering and mipmaps preserve stable headset rendering.
- [Matched before-and-after views](village-comparison.html), [before](village-before-matched.png), [after](mossbell-street.png), [well](mossbell-well.png), [upper terrace](mossbell-terrace.png), [overview](mossbell-village.png).

The comparison images are actual Blender renders, not generated concept art or Unity captures. The old source came from commit `9ca5cbb`. The before and after share camera position `(0, -21, 1.65)`, look target `(0, 10, 3.8)`, 28 mm lens, 36 mm sensor and 1280×720 output. Lighting and material changes are part of the comparison.

## Composition and scale

Foreground cottages frame both edges of a compact court. The well is 2.76 m across, its stone rim is 0.82 m tall, and its wooden beam is 2.72 m high. The middle cottage stands on a 3.2 m terrace. The stone windmill occupies a separate 8 m terrace to the right, with a broad four-sail silhouette. A 3.2 m wide stair climbs on the left; two winding ramps climb on the right. Broken rock outcrops and separate lavender ridgelines replace the uniform perimeter wall. The extra lookout tower is removed.

Cottage door panels are 1.08×2.12 m, with full-size frames. The stair has twenty 0.16 m risers and 0.40 m treads. Unity's village step offset is 0.20 m and is restored on exit. No player or headset scale is changed. Cottages have solid exterior shells; enterable furnished interiors are not included.

UV islands use metric planar projection, including roof slopes. Masonry/plaster/roof tiles repeat at 0.5 repeats per metre, grass at 0.25, timber at 1.0. Intentional tiled UV overlap reuses the low-resolution artwork. Path U runs across painted grass shoulders; V repeats every 4 m. Daytime windows use a dark muted material with no emission. Seven trees vary canopy lobes, height, trunk and branch geometry; they use olive foliage.

## Unity integration

`MossbellVillage` loads the exported geometry through the existing fade transition. `VillageMaterials` assigns the new UV shader and PNGs. The `Collision` material group alone supplies static MeshColliders: terrain, stairs, ramp shoulders, buildings/roofs, well, fences and tree trunks. Leaves, windows and tiny ornaments do not create collision noise. Collision and marker groups are invisible. Original arm locomotion and tracking stay in place.

The village uses one medium-resolution directional shadow map within 55 m and blue-lavender fog from 35–140 m. Fog, shadow settings and step offset restore on exit. The separate desktop review camera never overrides a live XR pose. F8 loads the village and switches to the matched view; F8 again restores movement. The overlay and avatar are hidden for captures. `Wizzard > Capture village comparison` saves a real Unity render to `Documentation/UnityCaptures/village-entrance.png` once the F8 view is active.

## Validation and limits

Blender checks sample supported routes and 2 m head clearance across a 0.48 m footprint. See [geometry report](village-geometry-checks.json) for measured slopes and sample counts. The export validator checks finite mesh/UV data, non-collapsed UV islands, index integrity, material groups, all portable texture references and 64×64 PNG dimensions. UV layers share the name `SurfaceUV` so Blender material batching retains every island. The OBJ was also reimported into Blender: metric marker positions, UVs and actual MTL texture links passed, and an [export render](village-export-check.png) confirms the delivered geometry/materials. This is not a Unity import test. The overview render omits atmospheric fog so the layout is readable. C# syntax was parsed separately; that is not a Unity compile.

Unity 2022.3.20f1 is not installed in this cloud environment, and no Quest headset is connected. Unity shader compilation, actual CharacterController movement, stereo appearance, hand collision and standalone performance remain unverified. No APK or device-test result is claimed.

On the Windows project, pull with Unity closed, reopen, run `Wizzard > Validate project`, then play Meadow and use F8 for comparison. In a Quest build, enter through the village gate, walk/arm-push through the square, climb the left stair, traverse both ramps and walk back out past the arrival point to return. Check both eyes, crouching, hand contact, transitions and frame timing. Unity's actual daylight, shadow filtering and fog will differ from Blender's offline renderer until this is checked.

Remaining visual differences: the generated tile artwork is simpler and less richly weathered than the target; terrain edges and tree clusters remain more angular; the exact reference roof/rock contours are approximated. The sky is procedural. Windmill sails and chickens are static. No twilight version is included.

## Rebuild

From the repository root, with Blender 4.3.2:

```sh
blender -b -t 8 --python-exit-code 1 --python Tools/create_village.py
python Tools/check_village_export.py
blender -b -t 4 --python-exit-code 1 --python Tools/check_village_roundtrip.py
```

The generator saves source, OBJ/MTL, shared textures, geometry report and four renders. It uses CPU Cycles with 64 samples because the installed Blender build has no denoiser. Keep screenshots labeled as Blender output until captured in Unity.
