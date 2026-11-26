"""Put the official Minecraft: Java Edition 26.3 client jar where engine/nether.py reads the game's bastion structure
templates (data/minecraft/structure/bastion/**.nbt), for as long as tools/fetch_assets.py does not extract them into
assets/mc. Same source and checksum as tools/fetch_assets.py (Mojang's version manifest); nothing is copied into the
project: the jar goes to $MC_CLIENT_JAR, or by default to ~/.cache/minecraft-shorts/client-26.3.jar
(engine.nether.JAR_CANDIDATES lists both).

    $BPY -m tools.nether_fetch_jar            # download (about 41 MB) unless a good jar is already there
    $BPY -m tools.nether_fetch_jar --check    # only say which jar engine.nether would use and verify its SHA-1
    $BPY -m tools.nether_fetch_jar --dest P   # download to P (then export MC_CLIENT_JAR=P for every process)

The durable fix is one line in tools/fetch_assets.py KEEP ('data/minecraft/structure/bastion/'); once that has run,
engine.nether reads assets/mc/data/minecraft/structure/bastion/ and needs no jar.
"""
import hashlib
import json
import os
import sys
import urllib.request

MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
VERSION = "26.3"
DEFAULT_DEST = os.path.join(os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"), "minecraft-shorts",
                            "client-%s.jar" % VERSION)


def client_entry(version=VERSION):
    """Mojang's download entry for the client jar: {'url', 'sha1', 'size'}."""
    manifest = json.load(urllib.request.urlopen(MANIFEST, timeout=60))
    entry = next(v for v in manifest["versions"] if v["id"] == version)
    return json.load(urllib.request.urlopen(entry["url"], timeout=60))["downloads"]["client"]


def sha1_of(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    dest = os.environ.get("MC_CLIENT_JAR") or DEFAULT_DEST
    if "--dest" in argv:
        dest = argv[argv.index("--dest") + 1]
    client = client_entry()
    if "--check" in argv:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from engine import nether          # needs bpy: run with $BPY
        kind, where = nether.template_source(quiet=True)
        if kind == "dir":
            print("engine.nether reads the templates from %s (no jar needed)" % where)
            return 0
        good = sha1_of(where) == client["sha1"]
        print("engine.nether reads the templates from the jar %s: SHA-1 %s (Mojang's %s %s)"
              % (where, "matches" if good else "DIFFERS", VERSION, client["sha1"]))
        return 0 if good else 1
    if os.path.isfile(dest) and sha1_of(dest) == client["sha1"]:
        print("%s is already the %s client jar (SHA-1 %s)" % (dest, VERSION, client["sha1"]))
        return 0
    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
    tmp = dest + ".part"
    print("downloading", client["url"], "->", dest)
    urllib.request.urlretrieve(client["url"], tmp)
    if sha1_of(tmp) != client["sha1"]:
        os.remove(tmp)
        print("checksum mismatch: nothing written")
        return 1
    os.replace(tmp, dest)
    print("ok: %s (%d bytes, SHA-1 %s)" % (dest, os.path.getsize(dest), client["sha1"]))
    if dest != DEFAULT_DEST and os.path.abspath(dest) != os.path.abspath(os.environ.get("MC_CLIENT_JAR", "")):
        print("export MC_CLIENT_JAR=%s  (for every process that builds the bastion)" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
