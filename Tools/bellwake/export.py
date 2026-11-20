"""Export the editable, packed sources. No original model library download is required.
blender -b --python-exit-code 1 --python Tools/bellwake/export.py -- [room ...]
"""

import sys, json, bpy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atelier import ROOT, batches, origins, export

files = sorted((ROOT / "Blender/Bellwake").glob("*.blend"))
names = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
for file in files:
    if names and file.stem not in names:
        continue
    bpy.ops.wm.open_mainfile(filepath=str(file))
    if file.stem == "Wayfarer":
        from wayfarer_export import export_gallery
        export_gallery(ROOT / "Assets/Resources/Bellwake/Wayfarer")
        continue
    batches.clear()
    origins.clear()
    origins.update(json.loads(bpy.context.scene["bellwake_pivots"]))
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            batches[obj["batch"]].append(obj)
    export(file.stem)
