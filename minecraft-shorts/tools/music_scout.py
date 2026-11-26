"""Scouting print for engine/music.py: a top-down character map of the village square and the lane between house_e
and house_f (seed 1), with the anchors there. No rendering.

Usage (project root):  $BPY -m tools.music_scout [x0 y0 x1 y1]
"""
import sys

from engine import quick, village

CODES = {"dirt_path": ".", "grass_block": ",", "short_grass": "'", "tall_grass": '"', "cobblestone": "C",
         "mossy_cobblestone": "C", "oak_planks": "P", "oak_log": "L", "oak_fence": "f", "lantern": "*", "torch": "t",
         "wall_torch": "t", "bell": "B", "water": "~", "oak_door": "D", "oak_stairs": "s", "cobblestone_stairs": "s",
         "dirt": "d", "poppy": "r", "dandelion": "y", "oxeye_daisy": "o", "cornflower": "c", "hay_block": "H",
         "stripped_oak_log": "L", "glass_pane": "g", "white_terracotta": "W", "oak_leaves": "%", "yellow_bed": "b",
         "white_bed": "b", "smooth_stone": "S", "stone_bricks": "S", "oak_slab": "_", "cobblestone_slab": "_"}


def main(argv):
    box = [int(a) for a in argv[:4]] if len(argv) >= 4 else [-14, -14, 14, 26]
    x0, y0, x1, y1 = box
    out = {}

    def edit(b):
        out["b"] = b

    scene = quick.reset()
    quick.setup(scene)
    v = village.build_village(scene, seed=1, edit=edit)
    b, w = out["b"], v.world
    print("legend: . path , grass ' tuft C cobble P planks L log f fence * lantern t torch D door s stairs "
          "number = height of the highest solid block above ground (2-9), # higher")
    for y in range(y1, y0 - 1, -1):
        row = []
        for x in range(x0, x1 + 1):
            g = b.surface_z(x, y)
            top = None
            for z in range(12, -3, -1):
                bid = w.block_id(x, y, z)
                if bid is not None:
                    top = (z, bid)
                    break
            if top is None:
                row.append(" ")
                continue
            z, bid = top
            h = z - g + 1
            if h >= 2 and bid not in ("tall_grass",):
                row.append(str(h) if h <= 9 else "#")
            else:
                row.append(CODES.get(bid, "?"))
        print("%4d %s" % (y, "".join(row)))
    print("     " + "".join(str(abs(x) % 10) for x in range(x0, x1 + 1)))
    for k in sorted(v.anchors):
        p = v.anchors[k]
        if x0 <= p[0] <= x1 + 1 and y0 <= p[1] <= y1 + 1:
            print("anchor %-22s (%.2f, %.2f, %.3f) yaw %s" % (k, p[0], p[1], p[2], v.yaws.get(k)))
    for name in ("house_e", "house_f", "well"):
        pl = v.buildings[name]
        print(name, "bounds", pl.bounds)
    for name, d in v.doors.items():
        print("door", name, tuple(round(c, 2) for c in d.matrix_world.translation))
    for g, obs in v.lights.items():
        for ob in obs:
            p = ob.location
            if x0 <= p[0] <= x1 + 1 and y0 <= p[1] <= y1 + 1:
                print("light %-8s (%.2f, %.2f, %.2f) %.1f W" % (g, p[0], p[1], p[2], ob.data.energy))
    unknown = sorted({w.block_id(*c) for c in w.blocks if x0 <= c[0] <= x1 and y0 <= c[1] <= y1}
                     - set(CODES))
    print("other ids:", unknown)


if __name__ == "__main__":
    main(sys.argv[1:])


def cells(x0, y0, x1, y1, z0=-1, z1=6):
    """Print every block id in a box, column by column (no rendering)."""
    scene = quick.reset()
    quick.setup(scene)
    out = {}
    v = village.build_village(scene, seed=1, edit=lambda b: out.update(b=b))
    w, b = v.world, out["b"]
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            col = []
            for z in range(z0, z1 + 1):
                st = w.get(x, y, z)
                if st is not None:
                    p = st[1] or {}
                    tag = ",".join("%s=%s" % (k, p[k]) for k in ("facing", "half", "type", "hinge") if k in p)
                    col.append("%d:%s%s" % (z, st[0], "[%s]" % tag if tag else ""))
            print("(%d,%d) g=%s %s" % (x, y, b.surface_z(x, y), "  ".join(col)))
