"""Read Minecraft structure templates (.nbt) from the extracted game data. STABLE helper.

load_template(name) -> Template with .size (x, y, z) and .blocks: list of (x, y, z, block_name, props_dict)
in Minecraft coordinates (Y up). Jigsaw blocks are replaced by their final_state, structure voids and air dropped.
"""
import gzip
import os
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MC_DIR = os.path.join(ROOT, "assets", "mc")
STRUCT_DIR = os.path.join(MC_DIR, "data", "minecraft", "structure")


def _read_nbt(buf):
    pos = 0

    def take(fmt):
        nonlocal pos
        size = struct.calcsize(fmt)
        val = struct.unpack_from(fmt, buf, pos)
        pos += size
        return val[0] if len(val) == 1 else val

    def string():
        nonlocal pos
        n = take(">H")
        s = buf[pos:pos + n].decode("utf-8", "replace")
        pos += n
        return s

    def payload(tag):
        nonlocal pos
        if tag == 1:
            return take(">b")
        if tag == 2:
            return take(">h")
        if tag == 3:
            return take(">i")
        if tag == 4:
            return take(">q")
        if tag == 5:
            return take(">f")
        if tag == 6:
            return take(">d")
        if tag == 7:
            n = take(">i")
            v = buf[pos:pos + n]
            pos += n
            return list(v)
        if tag == 8:
            return string()
        if tag == 9:
            sub = take(">b")
            n = take(">i")
            return [payload(sub) for _ in range(n)]
        if tag == 10:
            out = {}
            while True:
                t = take(">b")
                if t == 0:
                    return out
                key = string()
                out[key] = payload(t)
        if tag == 11:
            n = take(">i")
            return [take(">i") for _ in range(n)]
        if tag == 12:
            n = take(">i")
            return [take(">q") for _ in range(n)]
        raise ValueError("bad NBT tag %r" % tag)

    tag = take(">b")
    string()
    return payload(tag)


def read_nbt_file(path):
    """Parse a gzip-compressed NBT file into plain dicts/lists."""
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return _read_nbt(raw)


def parse_state(text):
    """'minecraft:oak_stairs[facing=east,half=bottom]' -> ('oak_stairs', {'facing': 'east', 'half': 'bottom'})"""
    name, _, rest = text.partition("[")
    props = {}
    if rest:
        for kv in rest.rstrip("]").split(","):
            k, _, v = kv.partition("=")
            props[k.strip()] = v.strip()
    return name.replace("minecraft:", ""), props


class Template:
    def __init__(self, name, size, blocks, raw):
        self.name, self.size, self.blocks, self.raw = name, size, blocks, raw


def load_template(name):
    """name like 'village/plains/houses/plains_small_house_1' (no extension)."""
    data = read_nbt_file(os.path.join(STRUCT_DIR, name + ".nbt"))
    palette = data["palette"]
    blocks = []
    for b in data["blocks"]:
        st = palette[b["state"]]
        bname = (st.get("id") or st.get("Name")).replace("minecraft:", "")
        props = dict(st.get("properties") or st.get("Properties") or {})
        if bname == "jigsaw":
            final = b.get("nbt", {}).get("final_state", "minecraft:air")
            bname, props = parse_state(final)
        if bname in ("air", "structure_void", "cave_air"):
            continue
        x, y, z = b["pos"]
        blocks.append((x, y, z, bname, props))
    return Template(name, tuple(data["size"]), blocks, data)


def list_templates(prefix="village/plains"):
    """All template names under a prefix."""
    out = []
    base = os.path.join(STRUCT_DIR, prefix)
    for d, _, files in os.walk(base):
        for f in sorted(files):
            if f.endswith(".nbt"):
                out.append(os.path.relpath(os.path.join(d, f), STRUCT_DIR)[:-4])
    return sorted(out)


if __name__ == "__main__":
    from collections import Counter

    for n in list_templates():
        if "zombie" in n or "decays" in n:
            continue
        t = load_template(n)
        c = Counter(b[3] for b in t.blocks)
        extras = [k for k in c if k in ("bell", "lantern", "torch", "wall_torch") or k.endswith("_bed") or k.endswith("_door")]
        print(f"{n.split('plains/')[-1]:40s} size={t.size} blocks={len(t.blocks):4d} {' '.join(sorted(extras))}")
