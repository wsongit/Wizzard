# Village wall repairs

The missing sections came from open meshes and gaps between separate cliff pieces. This repair adds geometry rather than disabling back-face culling.

- A closed irregular backing connects the village perimeter. Its inner walls, outer walls, top, underside and ends are complete; the southern entrance stays open.
- Rear cliff pieces and distant mountain ridges now have sides, backs and bottom caps. Side rocks have bottom caps.
- Terrace wall tops meet their lawns. The moss fringe faces outward and sits slightly clear of the wall to avoid flickering.
- Ramp shoulders have end caps and undersides. Ground extends under the perimeter instead of ending short of the walls.
- The meadow's exterior entrance mountain now has a closed cross-section, including inner walls, a buried base and both end caps. Its existing entrance remains accessible. The same mesh is used for rendering and collision.

The updated `.blend` and OBJ include the repaired village geometry and collision. See [inside view](village-walls-inside.png), [outside view](village-walls-outside.png), and [wall validation report](village-wall-checks.json). These are actual Blender inspection renders. Earlier comparison images document the preceding art rebuild.

Blender checks passed for 30 closed shells: no boundary/nonmanifold edges, consistent face winding, and positive enclosed volume. Another 338 visibility rays checked the connected perimeter from inside and outside, excluding the entrance. All six existing route support/headroom checks and exported UV/index/texture checks passed. C# syntax was checked. The exterior runtime mesh was reviewed, but Unity compilation, physics and headset rendering remain untested because Unity and a headset are unavailable in this environment.

Reproduce the village checks:

```sh
blender -b -t 8 --python-exit-code 1 --python Tools/create_village.py -- --no-render
blender -b -t 8 --python-exit-code 1 --python Tools/check_village_walls.py
python Tools/check_village_export.py
```
