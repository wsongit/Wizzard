# Bellwake release checks

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
