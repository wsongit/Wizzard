# Wizzard — The Long Meadow

An original N64-style grassy VR playground: **2,048 × 2,048 metres**, small rolling
hills, mottled 64×64 grass, 48 scattered climbable stone/tree landmarks, and a
simple brown gorilla avatar. Arm-driven locomotion is implemented from scratch;
no Gorilla Tag code or Nintendo assets are included.

The Blender preview below shows the earlier terrain layout and palette. The updated
Unity materials use darker, softly filtered forest textures; their in-game appearance
has not yet been rendered or validated here.

![Earlier Blender landscape preview](Documentation/meadow-preview.png)

## Open the Unity project (standalone Meta Quest)

1. Install **Unity 2022.3.20f1** using Unity Hub, including **Android Build Support,
   Android SDK & NDK Tools, and OpenJDK**. Add this directory as a project.
2. Let Package Manager resolve the pinned OpenXR 1.9.1, XR Management 4.4.0,
   and Input System 1.7.0 dependencies. Accept an editor restart if prompted.
3. The editor setup script configures Quest Android and PC OpenXR with controller profiles.
   You can run **Wizzard → Configure Quest and PC OpenXR** again. Run OpenXR Project
   Validation and resolve any runtime/platform-specific requirements.
4. Open `Assets/Scenes/Meadow.unity` and press **Play**. The scene creates the
   terrain and player when entering Play mode; it is intentionally empty in edit mode.
5. In **File → Build Settings**, switch to **Android**. The setup uses ARM64,
   IL2CPP, OpenGL ES 3, linear color, single-pass stereo, Meta Quest Support,
   and Touch controller interaction profiles. Run OpenXR Project Validation for Android.
6. Run **Wizzard → Build Quest APK** to create `Builds/LongMeadow-Quest.apk`.
   Enable developer mode on your Quest and connect it by USB. Authorize USB
   debugging, then install with `adb install -r Builds/LongMeadow-Quest.apk`.
   Launch **The Long Meadow** from the headset's Unknown Sources library.
   This creates a development/sideload build; store submission is not configured.
7. Optional: for PC Play mode through Quest Link, switch to the PC build target,
   enable Meta's PC OpenXR runtime, connect Link, and press Play.

Plant either palm against terrain, a stone, or a tree, then push/pull your arm to
move. Push down and release for a jump. Crouch physically to reach the ground.
Right stick snaps rotation 45°. Tracking uses floor space; match your runtime's
floor calibration. There is no grip-button requirement. This is a prototype;
headset comfort, collision edge cases, and real-world controller behavior still
need play testing.

Without a headset: **WASD** moves, **Space** jumps, **middle click** captures mouse
look, **Escape** releases it. Mouse buttons lower the corresponding debug palms;
this mode is for inspecting the map, not a faithful VR hand simulator.

## Blender artwork

Blender **4.3.2** is installed in the cloud at `/usr/bin/blender`.
`Blender/LongMeadow.blend` contains the complete landscape and example avatar.
`Assets/Resources/GorillaTorso.obj` is the exported avatar body used by Unity;
the game creates tracked palms and arm segments. The first-person head is the
camera. Blender source stays outside Assets to avoid Unity's automatic Blender
conversion and its external FBX tooling requirements.

Regenerate all artwork and the Blender preview from the repository root:

```sh
blender -b --threads 8 --python Tools/create_art.py
blender -b Blender/LongMeadow.blend --python Tools/validate_art.py
```

## Validation status

- Blender asset generation and CPU preview render: **passed**.
- Blender terrain extent, triangle count, mesh indices, hills, texture size,
  and exported avatar: checked by `Tools/validate_art.py`.
- Unity editor compilation, package resolution, play mode and builds: **unrun**.
  The required Unity editor and Android toolchain are not installed in this cloud workspace.
- Headset locomotion, stereo rendering, performance and OpenXR runtime: **unrun**.
  No headset is attached to the cloud.

After Unity is available, run **Wizzard → Validate project**, then test in Play
mode. Check both hands on flat ground and slopes, push-off jumping, rocks/trees,
snap turns, tracking loss/recovery, room-scale head collision, and repeated Play
sessions. Inspect GC allocation and frame time on the target headset. The Quest APK build, controller tracking and performance must be validated on a
physical device once Unity and the Android toolchain are installed.

## Forest-style textures and future props

All current Unity world and avatar surfaces use distinct original 64×64 textures
with muted colors, broad mottling, bilinear filtering and mipmaps. This approximates
the soft, low-resolution forest surfaces in the supplied reference. Texture
projection supports models without UVs, including the exported gorilla torso.

Run **Wizzard → Create retro material library** (also called by project setup).
This creates editable materials in `Assets/RetroMaterials`: Grass, Bark, Stone,
Leaves, Fur, Skin, HousePlaster, RoofTiles and Wood. Drag the appropriate material
onto each renderer/material slot of a house or prop. Adjust **Texture repeats per
unit** for the model's scale. Existing customized library materials are preserved.
New props keep their own assigned materials; there is no global grass replacement.
For custom artwork, duplicate a library material and assign your own 32×32 or
64×64 texture, using Repeat, Bilinear, mipmaps enabled and anisotropic level 0.

Runtime world materials are generated by `RetroMaterials.cs`; edit its palettes
for the generated world. The editable library is for manually placed props.
Blender artwork regeneration still produces the earlier preview palette. Unity
shader compilation, visual review and Quest performance remain untested here.

## Eight low-poly tree variants

The meadow now distributes eight original branching tree models: Round, Tall,
Wide, Leaning, Forked, Young, Old, and Asymmetric. Each gets a deterministic yaw
and 85–115% scale variation. All use the existing low-resolution bark/leaf
materials, flat crown normals and climbable mesh colliders. Geometry is shared
by instances. The trees are approximately 4–9 metres tall before instance scaling.

Models: `Assets/Resources/Trees/Tree01.obj` through `Tree08.obj`. You can also drag
these models into a scene manually; the runtime tree factory applies the retro
materials and colliders to the generated meadow instances.
Source: `Blender/TreeVariants.blend`. Regenerate with:
`blender -b --threads 8 --python Tools/create_trees.py`.

![Eight tree variants, Blender shape preview](Documentation/tree-variants.png)

This Blender preview shows the shapes with simple face colors. Unity applies
its forest textures. Export geometry and the Blender render were checked;
Unity imports, shader compilation, collisions and Quest performance still need
validation in the editor/on device.

## Mossbell Village

An original mountain village is now reached through a gate near meadow coordinates
**X 240, Z 104**. In desktop Play mode, press **V** to move near that entrance,
then walk forward through the gate. In VR, travel to the small rocky mountain in
the meadow and pass between its gate pillars.

The camera fades to black, displays **Entering / Mossbell Village**, instantiates
the village while the screen is covered, places the player safely inside, and
fades back in. Walking back out behind the village arrival point reverses the transition.
The meadow and village are mutually enabled areas in the same scene, not an
additive scene download. The village is retained after first entry so return
visits reuse its geometry. Movement velocity and planted-hand contacts reset on
teleport; head tracking continues during the fade. A short arrival distance and
cooldown avoid immediately entering the return gate.

Mossbell has its own take on a terraced N64-era village: six varied plaster-and-timber workshops, red and slate roofs, an open three-bell pavilion on the upper hill, and a covered twin spring beside the court. Seven green tree shapes, planters, a potter's handcart, fences and small brown birds complete the setting. The artwork and landmark designs are original; no Nintendo assets or reference-image pixels are included.

Source: `Blender/MossbellVillage.blend`. Export: `Assets/Resources/Village/Mossbell.obj` and `.mtl`. The source keeps editable named objects and packed textures; export copies are batched by material. Buildings are exterior shells and props are static. Original 64×64 tiles provide separate grass, dirt, natural rock, stonework, plaster, timber, roof, foliage, cloth, brass and water materials. Bilinear filtering and mipmaps preserve the texture at headset distances.

![Rebuilt village entrance — actual Blender render](Documentation/mossbell-street.png)

[Current refresh and validation limits](Documentation/village-refresh.md) · [Earlier rebuild history](Documentation/village-rebuild.md) · [Geometry report](Documentation/village-geometry-checks.json)

The existing scene loads the new model through the village fade transition. Dedicated collision follows the terrain, ramps, stairs, building shells, fences and tree trunks. Materials use the authored UVs, soft directional shadows and blue-lavender fog. Meadow atmosphere and movement settings restore on exit.

For a repeatable desktop comparison, play Meadow and press **F8**. It loads the village and switches to the 1.65 m entrance camera with the overlay and avatar hidden. Press F8 again to resume movement. Choose **Wizzard > Capture village comparison** to save an actual Unity capture. This review camera is disabled while XR is active.

Regenerate with:

```sh
blender -b -t 8 --python-exit-code 1 --python Tools/create_village.py
python Tools/check_village_export.py
```

Blender renders, route support/headroom checks and export integrity checks passed. Unity 2022.3.20f1 and a Quest headset are unavailable here, so shader compilation, actual physics/traversal, stereo rendering and standalone performance remain unverified. Run **Wizzard > Validate project** after import and follow the headset checks in the handoff. This rebuild makes no package manifest change.

Village and exterior mountain wall gaps have been repaired. See [wall repair details and inside/outside previews](Documentation/village-wall-repair.md).
