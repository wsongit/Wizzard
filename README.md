# Wizzard — The Long Meadow

An original N64-style grassy VR playground: **2,048 × 2,048 metres**, small rolling
hills, pixelated 32×32 grass, 48 scattered climbable stone/tree landmarks, and a
simple brown gorilla avatar. Arm-driven locomotion is implemented from scratch;
no Gorilla Tag code or Nintendo assets are included.

![Blender landscape preview](Documentation/meadow-preview.png)

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
  The editor is not installed; the cloud proxy denies `download.unity3d.com`
  and `packages.unity.com`. Required network additions were saved as a draft.
- Headset locomotion, stereo rendering, performance and OpenXR runtime: **unrun**.
  No headset is attached to the cloud.

After Unity is available, run **Wizzard → Validate project**, then test in Play
mode. Check both hands on flat ground and slopes, push-off jumping, rocks/trees,
snap turns, tracking loss/recovery, room-scale head collision, and repeated Play
sessions. Inspect GC allocation and frame time on the target headset. The Quest APK build, controller tracking and performance must be validated on a
physical device once Unity and the Android toolchain are installed.
