"""Bundle the downloadable Windows/macOS/Linux desktop browser game into one offline HTML file."""

import base64, json, subprocess, sys, shutil, hashlib
from pathlib import Path

folder = Path(__file__).resolve().parent
root = folder.parents[2]
assets = folder.parent / ".web-assets"
story = json.loads((assets / "story.json").read_text())


out = Path(sys.argv[1])
out.parent.mkdir(parents=True, exist_ok=True)
streamed = "--streamed" in sys.argv


def asset(path):
    if streamed:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        relative = Path("assets") / (path.stem + "-" + digest + path.suffix)
        (out.parent / relative).parent.mkdir(exist_ok=True)
        shutil.copyfile(path, out.parent / relative)
        return relative.as_posix()
    return base64.b64encode(path.read_bytes()).decode("ascii")


regions = json.loads((root / "Assets/Resources/Bellwake/Passages.json").read_text())[
    "regions"
]
works = json.loads((root / "Assets/Resources/Bellwake/Underworks.json").read_text())
rooms = (
    story["rooms"]
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
    skies={
        p.stem: asset(p)
        for p in (root / "Assets/Resources/Bellwake/Skies").glob("*.jpg")
    },
    models={
        key: asset(assets / (key + ".glb"))
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
