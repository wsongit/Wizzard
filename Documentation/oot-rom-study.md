# Ocarina of Time ROM study for original Wizzard environments

The supplied archive was successfully inspected. It contains one **32 MiB, big-endian PAL revision 1 ROM**. Its MD5 matches the public PAL 1.1 reference checksum: `d714580dd74c2c033f5e1b6dc0aeac77`. SHA-256: `74f9266fd7fa23cc700b5b46a21fbe99cdc6ea10438bc4b48eeb625763b8611c`.

The study reads the binary file table, compressed resources, default scene headers, collision arrays and selected static-room display lists. It does not emulate gameplay or claim a visual tour of every room. The ROM and extracted research data stay outside the Unity project; the checked-in deliverables are the inspector, measurements and these notes.

## Coverage and direct measurements

The file table begins at ROM offset `0x7950`, matching the public PAL 1.1 configuration. All **1,511 files** were enumerated and their full decompressed lengths validated, including **1,457 Yaz0 streams**. The files expand to 53,287,696 bytes. This includes **378 object files**, **469 overlays**, **101 scene files** and **388 room files**.

All **101 default scene headers** and their **388 room references** were parsed. Vertex indices and array bounds were checked for **87,215 static collision polygons** across those scenes. This is structural coverage of the complete filesystem and default scene collision data, not a rendering analysis of every object or alternate scene state.

Three outdoor room-0 meshes received a deeper display-list inspection:

| Static subset | Culling groups | Decoded triangle instances | Referenced texture images | Scene collision vertices / polygons |
| --- | ---: | ---: | ---: | ---: |
| Kakariko Village (`spot01`) | 20 | 839 | 32 | 605 / 863 |
| Hyrule Field (`spot00`) | 36 | 1,639 | 49 | 1,162 / 1,579 |
| Kokiri Forest, room 0 (`spot04`) | 18 | 1,220 | 42 | 1,081 / 1,692 |

The collision figures cover each scene's static collision header, while rendering figures cover only room 0. They are not equivalent scopes or per-frame GPU counts. Alternate headers, actors, object-bank models, dynamic collision and runtime-generated display lists are excluded. Both branches of Kakariko's conditional detail list were inspected as a static union. Hyrule Field and Kokiri Forest each reference three external display lists that the inspector reports rather than inventing their content.

Detailed numerical results: [oot-rom-measurements.json](oot-rom-measurements.json).

## Findings that help the models

**Small textures vary in both dimensions and format.** Kakariko's inspected render tiles use extents including 16×16, 16×32, 16×64, 32×16, 32×32, 32×64, 64×16, 64×32 and 64×64. They include RGBA16, CI8, CI4, IA4 and I4. Rectangular tiles suit narrow trim and long architectural features; low resolution does not mean one stretched square image for every surface. Wizzard should retain distinct original wood, roof, plaster, stone, ground and foliage patterns with consistent physical repeat sizes.

**Compact geometry and material variety do much of the work.** The decoded Kakariko static room has 839 triangles and 32 texture references. Its detail is not produced by dense geometry everywhere. For Wizzard, spend geometry on roof silhouettes, door recesses, structural beams and clean stair profiles, then use restrained original low-resolution texture detail on broad faces. The number is not a whole-village triangle budget: separately loaded actors and props are absent from this count.

**Materials meet through shared geometric boundaries.** Kakariko contains **221 position-matched edges shared by differently textured triangles**, and the inspected static room contains **zero exact duplicate geometric triangles**. Vertex records are often split for texture coordinates or normals while positions meet. This is useful evidence for a joined surface with deliberate material boundaries. It does not prove that every dirt/grass transition in the game uses an identical method, nor that no partial overlap exists anywhere.

For the reported Wizzard screenshots, the practical rule is stronger: dirt intersections should form **one surface**, not several independent ribbons competing at the same depth. Dirt belongs on the walkable face. A road must not stretch up an adjacent cliff just because a projection ray happens to hit that cliff. Validate material transitions and UV orientation in addition to validating collision and ground support.

**Vertex bytes must be interpreted with the lighting state.** In Kakariko, **785 of the 839 inspected triangles** load vertices with `G_LIGHTING` enabled. Their RGB-sized vertex fields hold normals, not painted colors. The remaining unlit geometry uses **seven distinct vertex colors**. The appropriate lesson is simple directional vertex lighting plus texture contrast; it would be wrong to infer hundreds of baked colors merely by counting differing vertex bytes. Keep readable shaded facets and avoid overbright materials that erase the texture.

**Rendering and collision are separate representations.** Kakariko's scene has 863 collision triangles and its inspected room union has 839 render triangles. Different totals are expected because the two structures serve different purposes and scopes. For Wizzard, collision simplification must be intentional and checked against the visible walking surface, especially at stairs, landings and building foundations.

**Third-person construction needs extra closure for VR.** Kakariko's inspected static room has **375 boundary edges after matching vertex positions**. This does not mean the finished game has 375 visible holes: some edges terminate separate surfaces or meet actors and other runtime geometry. It does show that this subset is not one watertight solid. Wizzard's headset can inspect undersides, lean near walls and reach unusual angles, so roofs, attics, prop bases and containment surfaces still need complete geometry and collision. Reusing an original open-face construction pattern without that adaptation would bring back the hiding gaps being fixed.

## Applied review rules for Wizzard

1. Union crossing roads or integrate their material into one ground mesh; reject duplicated coplanar road faces.
2. Keep road UVs consistent through junctions and clip road coverage to intended walkable surfaces.
3. Build terrace edges and foundations as continuous supported geometry; use decorative trim only after the primary shape is correct.
4. Keep roofs thick and close their undersides and attic ends; inspect the backs of every building.
5. Preserve compact silhouettes, distinct small texture patterns and visible shading rather than adding random polygons or excessive brightness.
6. Check the exported Unity model from player height, including junctions and sloping paths. Collision-only tests cannot detect a flickering or stretched material overlay.

## Reproduce the inspection

Download the public **metadata only**:

```sh
curl -fsSL https://raw.githubusercontent.com/zeldaret/oot/main/baseroms/pal-1.1/segments.csv -o /tmp/oot-pal11-segments.csv
python3 Tools/inspect_oot_rom.py \
  --rom /path/to/your/supplied-ROM.zip \
  --segments /tmp/oot-pal11-segments.csv \
  --output /tmp/oot-rom-report.json
```

A `.z64` input works too. The inspector requires the verified revision, parses a ZIP in memory, writes numerical JSON only, and does not write extracted models or textures. The current run passed full DMA/decompression checks and every default scene collision index check. Selected static rooms decode with the unresolved external calls explicitly listed in the report.

Public format references used to interpret the binary data:

- [PAL 1.1 configuration and DMA offset](https://github.com/zeldaret/oot/blob/main/baseroms/pal-1.1/config.yml)
- [PAL 1.1 segment names](https://github.com/zeldaret/oot/blob/main/baseroms/pal-1.1/segments.csv)
- [PAL 1.1 compressed-ROM checksum](https://github.com/zeldaret/oot/blob/main/baseroms/pal-1.1/checksum-compressed.md5)
- [Scene commands](https://github.com/zeldaret/oot/blob/main/include/scene.h), [room shapes](https://github.com/zeldaret/oot/blob/main/include/room.h), and [collision structures](https://github.com/zeldaret/oot/blob/main/include/bgcheck.h)
- [GBI command definitions](https://github.com/zeldaret/oot/blob/main/include/ultra64/gbi.h)
- [Kakariko scene metadata](https://github.com/zeldaret/oot/blob/main/assets/xml/scenes/overworld/spot01.xml)

The inspector derives texture dimensions from the final render tile, not `SetTextureImage`'s often-placeholder width of 1. It masks collision vertex flags with `0x1FFF`, treats Y as vertical, and matches geometry by position across UV seams. Those details matter for trustworthy measurements.
