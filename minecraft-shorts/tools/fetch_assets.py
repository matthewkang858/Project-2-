"""Download the official Minecraft: Java Edition client from Mojang's servers and extract the files this
project reads (textures, models, blockstates, font, village structures) into assets/mc/.

The game files are Mojang's property: they are never committed to this repository (assets/mc is git-ignored).
Use them only with a copy of Minecraft you own.   Usage: python3 tools/fetch_assets.py [version]   (default 26.3)
"""
import hashlib
import json
import os
import sys
import urllib.request
import zipfile

MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "mc")
KEEP = (
    "assets/minecraft/textures/",
    "assets/minecraft/models/",
    "assets/minecraft/blockstates/",
    "assets/minecraft/font/",
    "assets/minecraft/items/",
    "data/minecraft/structure/village/",
    "data/minecraft/worldgen/template_pool/village/plains/",
)


def main(version="26.3"):
    manifest = json.load(urllib.request.urlopen(MANIFEST))
    entry = next(v for v in manifest["versions"] if v["id"] == version)
    client = json.load(urllib.request.urlopen(entry["url"]))["downloads"]["client"]
    os.makedirs(OUT, exist_ok=True)
    jar = os.path.join(OUT, "client-%s.jar" % version)
    if not os.path.exists(jar):
        print("downloading", client["url"])
        urllib.request.urlretrieve(client["url"], jar)
    sha1 = hashlib.sha1(open(jar, "rb").read()).hexdigest()
    assert sha1 == client["sha1"], "checksum mismatch"
    with zipfile.ZipFile(jar) as z:
        names = [n for n in z.namelist() if n.startswith(KEEP)]
        z.extractall(OUT, names)
    os.remove(jar)
    print("extracted %d files to %s" % (len(names), OUT))


if __name__ == "__main__":
    main(*sys.argv[1:2])
