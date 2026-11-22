"""Print a village structure template layer by layer as ASCII (no Blender needed).

Usage (from the project root):  python3 tools/inspect_template.py houses/plains_small_house_1 [more names...]
Rows are Minecraft z (north at the top), columns are x (west at the left); layers go from y=0 upward.
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import structures as S  # noqa: E402

GLYPH = {
    "cobblestone": "#", "mossy_cobblestone": "#", "oak_planks": "P", "oak_log": "L", "stripped_oak_log": "l",
    "stripped_oak_wood": "l", "oak_stairs": "s", "cobblestone_stairs": "S", "oak_slab": "_", "cobblestone_slab": "_",
    "smooth_stone_slab": "_", "glass_pane": "g", "white_stained_glass_pane": "g", "yellow_stained_glass_pane": "g",
    "oak_door": "D", "oak_fence": "f", "oak_fence_gate": "G", "torch": "t", "wall_torch": "t", "white_bed": "B",
    "yellow_bed": "B", "dirt": "d", "grass_block": "v", "dirt_path": "=", "farmland": "~", "water": "w",
    "wheat": "x", "bell": "!", "white_terracotta": "T", "terracotta": "T", "bookshelf": "K", "lectern": "E",
    "composter": "C", "chest": "c", "oak_trapdoor": "-", "ladder": "H", "white_wool": "W", "yellow_wool": "W",
    "hay_block": "h", "cobblestone_wall": "o", "smooth_stone": "O", "short_grass": ",", "tall_grass": ",",
    "poppy": "*", "dandelion": "*", "oxeye_daisy": "*", "oak_leaves": "%", "oak_pressure_plate": ".",
    "white_carpet": ".", "yellow_carpet": ".", "green_carpet": ".",
}


def show(name):
    if not name.startswith("village/"):
        name = "village/plains/" + name
    t = S.load_template(name)
    sx, sy, sz = t.size
    print("=" * 70)
    print(name, "size (x, y, z) =", t.size)
    grid = {}
    special = []
    for x, y, z, b, p in t.blocks:
        grid[(x, y, z)] = (b, p)
        if b in ("oak_door", "bell", "lectern", "composter", "chest", "torch", "wall_torch", "ladder") or \
                b.endswith("_bed") or b not in GLYPH:
            special.append((y, z, x, b, p))
    for y in range(sy):
        print("-- y=%d" % y)
        for z in range(sz):
            row = ""
            for x in range(sx):
                b = grid.get((x, y, z))
                row += " " if b is None else GLYPH.get(b[0], "?")
            print("   |" + row + "|  z=%d" % z)
    for y, z, x, b, p in sorted(special):
        keep = {k: v for k, v in p.items() if k in ("facing", "half", "hinge", "part", "attachment", "open", "type",
                                                      "level", "axis", "face")}
        print("   %-22s at x=%d y=%d z=%d %s" % (b, x, y, z, keep))
    raw = t.raw
    jig = [b for b in raw["blocks"] if raw["palette"][b["state"]].get("id", raw["palette"][b["state"]].get("Name"))
           == "minecraft:jigsaw"]
    for b in jig:
        st = raw["palette"][b["state"]]
        pr = st.get("properties") or st.get("Properties") or {}
        print("   jigsaw at x=%d y=%d z=%d orientation=%s name=%s pool=%s final=%s" % (
            b["pos"][0], b["pos"][1], b["pos"][2], pr.get("orientation"), b["nbt"].get("name"), b["nbt"].get("pool"),
            b["nbt"].get("final_state")))
    ents = raw.get("entities", [])
    if ents:
        print("   entities:", Counter(e["nbt"].get("id") for e in ents))


if __name__ == "__main__":
    for n in sys.argv[1:]:
        show(n)
