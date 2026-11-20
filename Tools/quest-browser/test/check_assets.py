"""Check the installed APK's loopback origin against the files in the signed package."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen
import zipfile

ORIGIN = "http://127.0.0.1:38761/"


def check(apk, url):
    with zipfile.ZipFile(apk) as archive:
        entries = [info for info in archive.infolist() if info.filename.startswith("assets/")]
        assert entries and archive.testzip() is None

        def read_back(info):
            name = info.filename.removeprefix("assets/")
            raw = archive.read(info)
            assert info.compress_type == zipfile.ZIP_STORED, name
            if name != "index.html":
                assert "-" + sha256(raw).hexdigest()[:12] + "." in name, name
            request = Request(url + name, headers={"Host": "127.0.0.1:38761"})
            with urlopen(request, timeout=20) as response:
                assert response.status == 200 and response.read() == raw, name
                if name.endswith(".png"):
                    assert response.headers.get_content_type() == "image/png", name

        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(read_back, entries))
        song = next(info for info in entries if info.filename.endswith(".ogg"))
        sample = archive.read(song)
        path = url + song.filename.removeprefix("assets/")
        for byte_range, expected in (("32-95", sample[32:96]), ("-15", sample[-15:])):
            request = Request(path, headers={"Range": "bytes=" + byte_range, "Host": "127.0.0.1:38761"})
            with urlopen(request, timeout=10) as response:
                assert response.status == 206 and response.read() == expected, byte_range
        with urlopen(Request(path, headers={"Host": "127.0.0.1:38761"}, method="HEAD"), timeout=10) as response:
            assert response.read() == b"" and int(response.headers["Content-Length"]) == len(sample)
        print(f"Verified {len(entries)} packaged files over loopback, including media ranges and HEAD")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("--url", default=ORIGIN, help="APK loopback host, optionally forwarded through adb")
    args = parser.parse_args()
    check(args.apk, args.url.rstrip("/") + "/")
