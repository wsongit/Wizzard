"""Reference shared workshop, costume and hillside paintings once per game download."""

import json
import struct

SHARED_PAINTS = (
    "CabinetBindings",
    "CountryBeyond",
    "HardwareTrims",
    "HouseEdges",
    "KilnFire",
    "ResidentCloth",
    "ShopWindows",
    "YardGoods",
)


def externalize(model, paintings):
    magic, version, size, json_size, tag = struct.unpack_from("<4sIII4s", model)
    if (magic, version, size, tag) != (b"glTF", 2, len(model), b"JSON"):
        raise ValueError("Invalid binary glTF header")
    scene = json.loads(model[20 : 20 + json_size])
    shared = [
        image for image in scene.get("images", []) if image.get("name") in paintings
    ]
    if not shared:
        return model
    start = 28 + json_size
    original = scene["bufferViews"]
    retired = set()
    for image in shared:
        name = image["name"]
        index = image.pop("bufferView")
        view = original[index]
        offset = start + view.get("byteOffset", 0)
        if model[offset : offset + view["byteLength"]] != paintings[name]:
            raise ValueError(f"Packed Blender painting differs from {name}.png")
        image["uri"] = f"paint/{name}.png"
        image.pop("mimeType", None)
        retired.add(index)

    binary = bytearray()
    compact = []
    remap = {}
    for index, view in enumerate(original):
        if index in retired:
            continue
        if view["buffer"] != 0:
            raise ValueError("Expected a single Blender binary buffer")
        old = start + view.get("byteOffset", 0)
        binary.extend(bytes(-len(binary) % 4))
        remap[index] = len(compact)
        compact.append(dict(view, byteOffset=len(binary)))
        binary.extend(model[old : old + view["byteLength"]])

    def fix_views(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "bufferView":
                    value[key] = remap[child]
                else:
                    fix_views(child)
        elif isinstance(value, list):
            for child in value:
                fix_views(child)

    scene["bufferViews"] = compact
    fix_views(scene)
    scene["buffers"][0]["byteLength"] = len(binary)
    binary.extend(bytes(-len(binary) % 4))
    metadata = json.dumps(scene, ensure_ascii=False, separators=(",", ":")).encode()
    metadata += b" " * (-len(metadata) % 4)
    total = 28 + len(metadata) + len(binary)
    return (
        struct.pack("<4sIII4s", magic, version, total, len(metadata), tag)
        + metadata
        + struct.pack("<I4s", len(binary), b"BIN\0")
        + binary
    )
