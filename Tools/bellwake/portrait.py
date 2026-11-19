"""Render the market character in Blender and draw Ina's folded charcoal letter.

blender -b Blender/Bellwake/Bellmarket.blend -t 2 --python-exit-code 1 --python Tools/bellwake/portrait.py
"""

import math
import tempfile
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from PIL import Image, ImageDraw, ImageFilter, ImageFont

root = Path(__file__).resolve().parents[2]
scene = bpy.context.scene
subjects = {o for o in scene.objects if o.get("batch") in ("Speaker", "SpeakerHead", "SpeakerArm")}
assert subjects, "Open the authored Bellmarket scene before rendering Ina’s portrait."
for obj in scene.objects:
    obj.hide_render = obj not in subjects

focus = Vector((-2.01, -8, 1.36))
bpy.ops.object.camera_add(location=focus + Vector((0.92, -3.25, 0.32)))
camera = bpy.context.object
camera.rotation_euler = (focus - camera.location).to_track_quat("-Z", "Y").to_euler()
camera.data.type = "ORTHO"
camera.data.ortho_scale = 1.26
scene.camera = camera
for location, energy, size in [((-3.3, -9.6, 3.65), 130, 2.5), ((-0.7, -7.2, 2.08), 32, 1.5)]:
    bpy.ops.object.light_add(type="AREA", location=location)
    lamp = bpy.context.object
    lamp.data.energy = energy
    lamp.data.shape = "DISK"
    lamp.data.size = size
    lamp.rotation_euler = (focus - lamp.location).to_track_quat("-Z", "Y").to_euler()
scene.render.engine = "CYCLES"
scene.cycles.samples = 12
scene.cycles.use_denoising = False
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"
scene.render.resolution_x, scene.render.resolution_y = 422, 468
scene.render.resolution_percentage = 100
with tempfile.TemporaryDirectory() as tmp:
    scene.render.filepath = str(Path(tmp) / "sitting.png")
    bpy.ops.render.render(write_still=True)
    sitting = Image.open(scene.render.filepath).convert("RGBA")

rng = np.random.default_rng(282)
h, w = 544, 768
y, x = np.indices((h, w))
rough = rng.normal(0, 2.6, (h, w))
marbling = (
    np.asarray(
        Image.fromarray(np.uint8(rng.random((24, 32)) * 255)).resize((w, h), Image.Resampling.BICUBIC)
    )
    / 36
)
paper = np.array([228, 212, 171]) + (rough + marbling - 3.7)[..., None]
# Two roll creases and old thumb marks remain visible through the graphite.
for crease in (245, 516):
    dist = x - crease - 2.4 * np.sin(y / 89)
    paper += (5 * np.exp(-(((dist + 2) / 2) ** 2)) - 7 * np.exp(-((dist / 2) ** 2)))[..., None]
grey = sitting.convert("L")
alpha = np.asarray(sitting.getchannel("A")) / 255
lum = np.asarray(grey, dtype=float) / 255
blur = np.asarray(grey.filter(ImageFilter.GaussianBlur(3.6)), dtype=float) / 255
inside = np.asarray(sitting.getchannel("A").filter(ImageFilter.MinFilter(3))) / 255
ey, ex = np.indices(lum.shape)
shadow = np.clip((0.91 - lum) * 1.7, 0, 1)
edge = np.clip((blur - lum) * 4.1, 0, 1) + (alpha - inside) * 0.7
hatch = np.maximum(0, np.cos((ex + ey * 0.64 + 1.4 * np.sin(ey / 27)) * math.tau / 5))
cross = np.maximum(0, np.cos((ey - ex * 0.39) * math.tau / 7)) * (shadow > 0.55)
density = np.clip(shadow * (0.46 + 0.28 * hatch + 0.18 * cross) + edge * 0.68, 0, 1)
density *= alpha * np.clip((467 - ey) / 52, 0, 1) * rng.uniform(0.69, 1.06, lum.shape)
area = paper[34:502, 12:434]
area[:] = area * (1 - density[..., None]) + np.array([47, 45, 40]) * density[..., None]
page = Image.fromarray(np.uint8(np.clip(paper, 0, 255)))
d = ImageDraw.Draw(page)
serif = "/usr/share/fonts/truetype/liberation2/LiberationSerif-Italic.ttf"
face = lambda px: ImageFont.truetype(serif, px)
ink = (76, 66, 55)
d.text((447, 109), "Tavi,", font=face(43), fill=ink)
for i, line in enumerate(
    ("You were asleep", "at the bench.", "I took the watch.", "", "See you when", "the water falls.")
):
    d.text((447 + int(2 * math.sin(i)), 182 + 34 * i), line, font=face(29), fill=ink)
d.text((600, 417), "— Ina", font=face(37), fill=ink)
out = root / "Assets/Resources/Bellwake/Letters/Tavi.jpg"
out.parent.mkdir(exist_ok=True)
page.save(out, quality=86, optimize=True)
