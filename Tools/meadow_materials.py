"""Use the packaged meadow paintings in their editable Blender source scenes."""
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
PAINT = ROOT / "Assets/Resources/Bellwake/Textures"
VILLAGE = ROOT / "Assets/Resources/VillageTextures"

def image_for(material, path, scale=None):
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    shader = nodes.get("Principled BSDF")
    picture = next((node for node in nodes if node.type == "TEX_IMAGE"), None)
    if picture is None:
        picture = nodes.new("ShaderNodeTexImage")
    image = bpy.data.images.load(str(path), check_existing=True)
    if not image.packed_file:
        image.pack()
    picture.image = image
    picture.interpolation = "Linear"
    if scale is not None:
        # Some library models are authored without UVs. Project in model space
        # so each leaf and bark patch stays attached when the tree moves.
        texcoord = nodes.new("ShaderNodeTexCoord")
        repeat = nodes.new("ShaderNodeVectorMath")
        repeat.operation = "SCALE"
        repeat.inputs["Scale"].default_value = scale
        links.new(texcoord.outputs["Object"], repeat.inputs[0])
        links.new(repeat.outputs[0], picture.inputs["Vector"])
        picture.projection = "BOX"
        picture.projection_blend = .14
    links.new(picture.outputs["Color"], shader.inputs["Base Color"])
    shader.inputs["Roughness"].default_value = .95
    return image

def dress_trees():
    image_for(bpy.data.materials["Bark"], PAINT / "ElderBark.png", .65)
    for i, leaf in enumerate(("Leaves", "RowanLeaf1", "RowanLeaf2", "ElderLeaf")):
        image_for(bpy.data.materials["Leaves" + str(i)], PAINT / (leaf + ".png"), .45)

def dress_meadow():
    for name, texture, scale in (
        ("Dark bark", "ElderBark", .65), ("Olive canopy", "Leaves", .45),
        ("Weathered limestone", "MossRock", .5), ("Warm clay fur", "Fur", .5),
        ("Golden muzzle", "Skin", .5),
    ):
        image_for(bpy.data.materials[name], PAINT / (texture + ".png"), scale)
    return image_for(bpy.data.materials["N64 meadow"], VILLAGE / "Grass.png")
