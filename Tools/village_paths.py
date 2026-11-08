"""Bake a united road mask onto the existing solid landform, never extra faces.

Grass and dirt remain their original 64 px repeating tiles. The larger grayscale
image only places those materials; it does not replace them with a high-res photo.
"""
import bpy
import json
import math
import numpy as np
from mathutils import Vector

BOUNDS = (-55, 60, -46, 68)
SIZE = 1024
MATERIAL = 'VillageGround'


def surface_material(grass, dirt, mask):
    """Blender equivalent of the opaque Unity VillageGround shader."""
    material = bpy.data.materials.new(MATERIAL)
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    shader = nodes.get('Principled BSDF')
    shader.inputs['Roughness'].default_value = 1
    uv = nodes.new('ShaderNodeTexCoord')
    grass_node = nodes.new('ShaderNodeTexImage')
    grass_node.image = grass
    dirt_node = nodes.new('ShaderNodeTexImage')
    dirt_node.image = dirt
    for node in (grass_node, dirt_node):
        node.interpolation = 'Linear'
        links.new(uv.outputs['UV'], node.inputs['Vector'])
    scale = nodes.new('ShaderNodeVectorMath')
    scale.operation = 'MULTIPLY'
    scale.inputs[1].default_value = (4 / 115, 4 / 114, 1)
    links.new(uv.outputs['UV'], scale.inputs[0])
    offset = nodes.new('ShaderNodeVectorMath')
    offset.operation = 'ADD'
    offset.inputs[1].default_value = (55 / 115, 46 / 114, 0)
    links.new(scale.outputs[0], offset.inputs[0])
    mask_node = nodes.new('ShaderNodeTexImage')
    mask_node.image = mask
    mask_node.interpolation = 'Linear'
    mask_node.extension = 'EXTEND'
    links.new(offset.outputs[0], mask_node.inputs['Vector'])
    mix = nodes.new('ShaderNodeMixRGB')
    links.new(mask_node.outputs['Color'], mix.inputs[0])
    links.new(grass_node.outputs['Color'], mix.inputs[1])
    links.new(dirt_node.outputs['Color'], mix.inputs[2])
    links.new(mix.outputs[0], shader.inputs['Base Color'])
    return material


def bake(landform, paths, root, materials, textures):
    xmin, xmax, ymin, ymax = BOUNDS
    x, y = np.meshgrid(
        xmin + (np.arange(SIZE, dtype=np.float32) + .5) * (xmax-xmin) / SIZE,
        ymin + (np.arange(SIZE, dtype=np.float32) + .5) * (ymax-ymin) / SIZE)
    # Small, spatially stable edge variation is shared by every road and junction.
    edge = (.10*np.sin(x*1.7+y*.37) + .07*np.sin(y*2.3-x*.83)
            + .045*np.sin(x*4.2+y*2.2))
    candidates = []
    any_road = np.zeros_like(x)
    for path in paths:
        nearest = np.full_like(x, np.inf)
        target = np.zeros_like(x)
        for a, b in zip(path['points'], path['points'][1:]):
            dx, dy = b[0]-a[0], b[1]-a[1]
            length2 = dx*dx + dy*dy
            if length2 < 1e-8:
                raise ValueError('Duplicate road control point: '+path['name'])
            t = np.clip(((x-a[0])*dx+(y-a[1])*dy)/length2, 0, 1)
            d2 = (x-a[0]-t*dx)**2+(y-a[1]-t*dy)**2
            closer = d2 < nearest
            target[closer] = (a[2]+t*(b[2]-a[2]))[closer]
            nearest = np.minimum(nearest, d2)
        coverage = np.clip((path['width']/2+edge-np.sqrt(nearest))/.35+.5, 0, 1)
        coverage = coverage*coverage*(3-2*coverage)
        candidates.append((coverage, target))
        any_road = np.maximum(any_road, coverage)

    # Only road-candidate pixels need ray casts. Sample the FINAL triangulated
    # surface, so a path cannot climb a cliff or spill onto a different terrace.
    height = np.zeros_like(x)
    normal_z = np.zeros_like(x)
    rows, cols = np.nonzero(any_road > 0)
    for j, i in zip(rows, cols):
        hit, normal, _, _ = landform.bvh.ray_cast(
            Vector((float(x[j, i]), float(y[j, i]), 40)), Vector((0, 0, -1)), 50)
        if hit is None:
            raise ValueError('Road has no ground beneath it')
        height[j, i], normal_z[j, i] = hit.z, normal.z
    mask = np.zeros_like(x)
    for coverage, target in candidates:
        fit = np.clip((.45-np.abs(height-target))/.15, 0, 1)
        fit *= normal_z >= .82
        mask = np.maximum(mask, coverage*fit)

    directory = root/'Assets/Resources/VillageMasks'
    directory.mkdir(parents=True, exist_ok=True)
    image = bpy.data.images.new('GroundPaths', width=SIZE, height=SIZE, alpha=False)
    image.colorspace_settings.name = 'Non-Color'
    pixels = np.ones((SIZE, SIZE, 4), dtype=np.float32)
    pixels[:, :, :3] = mask[:, :, None]
    image.pixels.foreach_set(pixels.ravel())
    image.filepath_raw = str(directory/'GroundPaths.png')
    image.file_format = 'PNG'
    image.save()
    image.pack()
    material = surface_material(textures['Grass'], textures['DirtPath'], image)
    materials[MATERIAL] = material
    landform.object.data.materials[0] = material
    landform.object['integrated_path_mask'] = 'VillageMasks/GroundPaths'
    layout = {'bounds': list(BOUNDS), 'mask_size': [SIZE, SIZE],
              'uv_metres_per_tile': 4, 'maximum_slope_degrees': math.degrees(math.acos(.82)),
              'maximum_height_difference_m': .45,
              'image_origin': 'Blender pixels bottom-left; PNG rows top-down',
              'paths': paths, 'road_candidate_pixels': len(rows),
              'painted_pixels': int(np.count_nonzero(mask > .01))}
    (root/'Documentation/village-path-layout.json').write_text(json.dumps(layout, indent=2)+'\n')
    return image
