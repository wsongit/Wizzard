# Village wall and ground integrity

The current village uses one closed ground mesh and one continuous perimeter. The former detached cliff blocks and ramp shells have been replaced, removing the narrow spaces between them. Wall bases overlap the ground; wall tops and sides use explicit triangles shared with collision. Only the intended southern entrance is open.

Cottage cores extend through the attic and overlap closed roof slabs. Foundations, tree roots and fence-post bottoms meet the final terrain. See [current renders and validation](village-refresh.md), [whole-area integrity report](village-integrity-checks.json) and [placement report](village-placement-checks.json).

The old `village-wall-checks.json` and `village-walls-inside.png` / `village-walls-outside.png` are historical records of the earlier separate-wall repair. Current checks supersede those per-piece tests. `Tools/check_village_walls.py` now forwards to the complete integrity audit.

```sh
blender -b -t 4 --python-exit-code 1 --python Tools/check_village_integrity.py
blender -b -t 4 --python-exit-code 1 --python Tools/check_village_placements.py
```

These checks inspect authored geometry. Unity import, physics and Quest traversal still need editor/device validation.
