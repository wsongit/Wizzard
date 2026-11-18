"""Bundle the downloadable Windows/macOS/Linux desktop browser game into one offline HTML file."""

import base64, json, subprocess, sys
from pathlib import Path

folder = Path(__file__).resolve().parent
root = folder.parents[2]
assets = folder.parent / ".web-assets"
story = json.loads((assets / "story.json").read_text())


def encode(path):
    return base64.b64encode(path.read_bytes()).decode("ascii")


data = dict(
    story=story,
    skies={p.stem: encode(p) for p in (root / "Assets/Resources/Bellwake/Skies").glob("*.jpg")},
    models={
        key: encode(assets / (key + ".glb"))
        for key in story["rooms"] + ["LeftPalm", "RightPalm", "RunnerArm"]
    },
    sounds={p.stem: encode(p) for p in (root / "Assets/Resources/Bellwake/Audio").glob("*.ogg")},
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
    .replace("/* DATA */", "window.BELLWAKE=" + json.dumps(data, separators=(",", ":")) + ";")
    .replace("/* GAME */", js.replace("</script", "<\\/script"))
)
out = Path(sys.argv[1])
out.parent.mkdir(parents=True, exist_ok=True)
html = "\n".join(line.rstrip() for line in html.split("\n"))
out.write_text(
    html + "\n<!-- Three.js license\n" + (folder / "node_modules/three/LICENSE").read_text() + "\n-->"
)
