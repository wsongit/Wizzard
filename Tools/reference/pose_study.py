"""Read one PAL skeleton and an authored animation frame into a Blender reference collection."""
import math
import re
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


def field(text, label):
    match = re.search(r"^\s*([\w&.+-]+),\s*// " + label + "$", text, re.M)
    if not match:
        raise ValueError("Missing reference field " + label)
    return match[1]


def triples(text):
    values = re.findall(r"^\s*(-?(?:0x[\da-f]+|\d+)),\s*// [xyz]$", text, re.M | re.I)
    if len(values) % 3:
        raise ValueError("Incomplete reference vector")
    numbers = [int(v, 0) for v in values]
    return list(zip(numbers[::3], numbers[1::3], numbers[2::3]))


def pose(bank, geometry, skeleton, animation, frame=0):
    def read(symbol):
        return (bank / (symbol + ".inc.c")).read_text()

    names = re.findall(r"&(\w+),", read(field(read(skeleton), "segment")))
    clip = read(animation)
    if not 0 <= frame < int(field(clip, "frameCount")):
        raise ValueError("Animation frame outside clip")
    fixed = int(field(clip, "staticIndexMax"))
    samples = [int(v, 0) for v in re.findall(r"^\s*(-?(?:0x[0-9A-Fa-f]+|\d+)),",
                                            read(field(clip, "frameData")), re.M)]
    indices = triples(read(field(clip, "jointIndices")))
    if len(indices) != len(names) + 1:
        raise ValueError("Animation and skeleton have different limb counts")
    joints = [tuple(samples[index + (frame if index >= fixed else 0)] for index in xyz)
              for xyz in indices]
    objects, missing, visited = [], [], set()

    def visit(index, parent):
        if index == 255:
            return
        if index in visited:
            raise ValueError("Repeated limb " + names[index])
        visited.add(index)
        limb = read(names[index])
        translation = joints[0] if index == 0 else triples(limb)[0]
        local = parent @ Matrix.Translation(Vector(translation))
        for axis, angle in zip("ZYX", reversed(joints[index + 1])):
            local = local @ Matrix.Rotation(angle * math.pi / 32768, 4, axis)
        # Standard limbs use one list. LOD limbs store near and far lists.
        materialized = re.search(r"^\s*(\w+),\s*// (?:dList|0)$", limb, re.M)
        if materialized and materialized[1] != "NULL":
            model = geometry / (materialized[1] + ".obj")
            if model.is_file():
                before = set(bpy.context.scene.objects)
                bpy.ops.wm.obj_import(filepath=str(model), forward_axis="Y", up_axis="Z")
                for obj in set(bpy.context.scene.objects) - before:
                    obj.matrix_world = local @ obj.matrix_world
                    objects.append(obj)
            else:
                missing.append(materialized[1])
        for key, transform in (("child", local), ("sibling", parent)):
            match = re.search(r"/\* (\d+) \*/[^\n]+// " + key + "$", limb, re.M)
            if not match:
                raise ValueError("Missing " + key + " for " + names[index])
            visit(int(match[1]), transform)

    visit(0, Matrix.Rotation(math.pi / 2, 4, "X"))
    if len(visited) != len(names):
        raise ValueError("Disconnected reference skeleton")
    bpy.context.view_layer.update()
    return objects, missing
