# Kakariko N64 reference review

Source: the user's `Kakariko_Village_N64_100_JPGs.zip` (100 JPGs).
Reviewed all 100 frames in five contact sheets. Enlarged these six examples:

- `001_village-overview.jpg`: cream timber-framed plaster, red and blue/slate roofs,
  compact elevations and contrasting brick structures.
- `005_house-exterior-and-fence.jpg`: masonry plinths, dark shutters in light frames,
  narrow rough timber fences.
- `079_kakariko-well-link-at-rim.jpg`: open polygonal stone well, thick coping and
  exposed wooden winding supports.
- `089_house-exterior-and-steps.jpg`: stone retaining walls, plaster houses on raised
  ground, stairs and shutter proportions.
- `098_windmill-exterior-wide.jpg`: tall stone tower and four lattice sails.
- `003_cucco-pen-closeup.jpg`: low rough timber enclosures beside buildings.

Other contact-sheet views show the entrance gate, ladder tower, cliffs, windmill
interior and graveyard. Interior and tomb layouts were not added: the current
village buildings are exterior models.

## Applied to Mossbell

Added an eastern windmill, contrasting roof and wall types, masonry textures and
foundations, shutter trim/slats, an open well with winch, a fenced side yard, and
irregular grass-topped earth cliffs. New textures are generated original 64×64
patterns; no screenshot pixels were used as game textures. The ZIP and extracted
reference images are not included in the repository.

Mossbell keeps its own central square, straight approach, upper terrace, house
placements and entrance/exit flow. The windmill has static decorative sails;
it is not an animated or enterable building.

## Validation limits

Blender model generation and overview rendering passed. The exported model's
indices and material names were checked against runtime material mappings.
C# syntax parsing passed. Unity compilation, actual texture rendering and Quest
play testing remain unrun. The later visual-target refinement uses shared PNG
textures in Blender and Unity; their lighting models still differ.


## Later visual target: three supplied village images

The user clarified that the target is the three ChatGPT images dated Nov 8, 2026
at 02:49:05, 02:48:54 and 02:48:48. These show stronger timber-framed cream gables,
red roof tiles, warm divided windows, prominent stone terraces, winding dirt
paths, a winch well, fenced yards, crates and chickens. Two are daylight views;
the runtime defaults to that daylight look rather than the first image's dusk.

Implemented those details with original geometry and generated 64px artwork.
No reference image pixels were copied into textures. The village retains its own
layout but lower houses were brought closer to the square, the terrace was raised
to four metres, and routes branch around the well. Ground-level previews are
renders of the actual generated model and shared texture files. Roof winding
and path overlaps were corrected while reviewing these views.
