"""Build the offline Meta Quest Browser APK from the released Play/index.html and its assets."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
PLAY = HERE.parents[1] / "Play"
ASSET_NAME = re.compile(r"assets/[A-Za-z0-9_-]+-([0-9a-f]{12})\.(?:ogg|jpg|png|json|glb\.gz|bvh\.gz)")


def assets_in(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from assets_in(item)
    elif isinstance(value, list):
        for item in value:
            yield from assets_in(item)
    elif isinstance(value, str) and value.startswith("assets/"):
        yield value


def build(args):
    index = (PLAY / "index.html").read_bytes()
    marker = "window.BELLWAKE="
    html = index.decode("utf-8")
    manifest, _ = json.JSONDecoder().raw_decode(html, html.index(marker) + len(marker))
    if not manifest.get("streamed"):
        raise ValueError("The APK requires the streamed production index")
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    platform = args.android_jar.resolve()
    tools = args.build_tools.resolve()

    def tool(name):
        if os.name == "nt":
            name += ".bat" if name in ("d8", "apksigner") else ".exe"
        return tools / name

    with tempfile.TemporaryDirectory(prefix="bellwake-apk-", dir=output.parent) as temporary:
        stage = Path(temporary)
        classes = stage / "classes"
        classes.mkdir()
        dex = stage / "dex"
        dex.mkdir()
        sources = sorted((HERE / "src").glob("*.java"))
        boot = os.pathsep.join(map(str, (platform, tools / "core-lambda-stubs.jar")))
        subprocess.run(["javac", "-source", "8", "-target", "8", "-bootclasspath", boot,
                        "-d", classes, *sources], check=True)
        subprocess.run([tool("d8"), "--min-api", "26", "--lib", platform, "--output", dex,
                        *sorted(classes.rglob("*.class"))], check=True)
        resources = stage / "res.zip"
        base = stage / "base.apk"
        subprocess.run([tool("aapt2"), "compile", "--dir", HERE / "res", "-o", resources], check=True)
        subprocess.run([tool("aapt2"), "link", "-I", platform, "--manifest", HERE/"AndroidManifest.xml",
                        "-o", base, resources], check=True)
        names = sorted(set(assets_in(manifest)))
        if not names:
            raise ValueError("The release index contains no assets")
        with zipfile.ZipFile(base, "a") as package:
            package.write(dex / "classes.dex", "classes.dex", compress_type=zipfile.ZIP_DEFLATED)
            package.writestr("assets/index.html", index, compress_type=zipfile.ZIP_STORED)
            for name in names:
                match = ASSET_NAME.fullmatch(name)
                if not match:
                    raise ValueError("Unrecognized release asset " + name)
                data = (PLAY / name).read_bytes()
                if not hashlib.sha256(data).hexdigest().startswith(match.group(1)):
                    raise ValueError("Asset differs from the release index: " + name)
                # AssetManager.openFd serves byte ranges directly from these stored entries.
                package.writestr("assets/" + name, data, compress_type=zipfile.ZIP_STORED)
        aligned, signed = stage / "aligned.apk", stage / "signed.apk"
        subprocess.run([tool("zipalign"), "-f", "4", base, aligned], check=True)
        subprocess.run([tool("apksigner"), "sign", "--v4-signing-enabled", "false", "--ks",
                        args.keystore.resolve(), "--ks-pass", "file:" + str(args.password_file.resolve()),
                        "--out", signed, aligned], check=True)
        subprocess.run([tool("apksigner"), "verify", "--verbose", signed], check=True)
        subprocess.run([tool("zipalign"), "-c", "4", signed], check=True)
        signed.replace(output)
        print(f"Built {output} with {len(names)} fingerprinted game assets")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-tools", type=Path, required=True, help="Android SDK Build Tools directory")
    parser.add_argument("--android-jar", type=Path, required=True, help="Android SDK platform android.jar")
    parser.add_argument("--keystore", type=Path, required=True)
    parser.add_argument("--password-file", type=Path, required=True, help="Signing store password file")
    parser.add_argument("--output", type=Path, default=PLAY / "Wizzard-Bellwake-WebXR.apk")
    build(parser.parse_args())
