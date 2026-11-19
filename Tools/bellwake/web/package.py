"""Bundle the downloadable Windows/macOS/Linux desktop browser game into one offline HTML file."""

import base64, gzip, json, subprocess, sys, hashlib
from pathlib import Path

folder = Path(__file__).resolve().parent
root = folder.parents[2]
assets = folder.parent / ".web-assets"
story = json.loads((assets / "story.json").read_text())


out = Path(sys.argv[1])
out.parent.mkdir(parents=True, exist_ok=True)
streamed = "--streamed" in sys.argv


def asset(path):
    payload = path.read_bytes()
    packed = path.suffix in (".glb", ".bvh")
    if packed:
        payload = gzip.compress(payload, compresslevel=6, mtime=0)
    if streamed:
        digest = hashlib.sha256(payload).hexdigest()[:12]
        suffix = path.suffix + (".gz" if packed else "")
        relative = Path("assets") / (path.stem + "-" + digest + suffix)
        (out.parent / relative).parent.mkdir(exist_ok=True)
        (out.parent / relative).write_bytes(payload)
        return relative.as_posix()
    return base64.b64encode(payload).decode("ascii")


def render_model(key):
    name = key + ".glb"
    stripped = assets / "render" / name
    return asset(stripped if stripped.is_file() else assets / name)


regions = json.loads((root / "Assets/Resources/Bellwake/Passages.json").read_text())[
    "regions"
]
works = json.loads((root / "Assets/Resources/Bellwake/Underworks.json").read_text())
rooms = (
    ["Highroad"] + story["rooms"]
    + [region["key"] for region in regions]
    + [r["key"] for r in works["rooms"]]
)
subprocess.run(
    [
        "node",
        str(folder / "bake_collision.mjs"),
        *[str(assets / (key + ".glb")) for key in rooms],
    ],
    check=True,
)

data = dict(
    collision={key: asset(assets / (key + ".bvh")) for key in rooms},
    story=story,
    streamed=streamed,
    regions=regions,
    works=works,
    charts={
        r["key"]: asset(
            root / "Assets/Resources/Bellwake/Charts" / (r["key"] + ".json")
        )
        for r in regions
    },
    letters={p.stem: asset(p) for p in sorted((root / "Assets/Resources/Bellwake/Letters").glob("*.jpg"))},
    skies={
        p.stem: asset(p)
        for p in (root / "Assets/Resources/Bellwake/Skies").glob("*.jpg")
    },
    models={
        key: render_model(key)
        for key in rooms + ["LeftPalm", "RightPalm", "RunnerArm"]
    },
    sounds={
        p.stem: asset(p)
        for p in (root / "Assets/Resources/Bellwake/Audio").glob("*.ogg")
    },
)
test = "--test" in sys.argv
js = subprocess.check_output(
    [
        str(folder / "node_modules/.bin/esbuild"),
        str(folder / "game.js"),
        "--bundle",
        "--minify",
        "--format=iife",
        "--legal-comments=inline",
        "--define:__TEST__=" + str(test).lower(),
    ],
    text=True,
)
html = (
    (folder / "game.html")
    .read_text()
    .replace(
        "/* DATA */", "window.BELLWAKE=" + json.dumps(data, separators=(",", ":")) + ";"
    )
    .replace("/* GAME */", js.replace("</script", "<\\/script"))
)
html = "\n".join(line.rstrip() for line in html.split("\n"))
out.write_text(
    html
    + "\n<!-- Three.js license\n"
    + (folder / "node_modules/three/LICENSE").read_text()
    + "\n-->"
)
