"""The Hello, square sequence: a block map of the village square and the exit road (no render).

    $BPY -m tools.hello_square_probe [x0 x1 y0 y1] [--z 0,1,2,3]

Prints, for every column in the box, a one-letter code of the block at each height asked (default z 0..3) so the
square director can see the well, the bell, the lamp posts, the house fronts and the road before placing anybody.
Legend: . air  # wall/solid  w well  l log  p plank  g glass  f fence  t torch/lantern  s stairs/slab  d door
        c cobble  _ path (z 0 only)  x other.  Writes nothing.
"""
import math
import sys


def code(bid):
    """One letter for a block id."""
    if not bid:
        return "."
    b = bid
    if "glass" in b:
        return "g"
    if "door" in b:
        return "d"
    if "torch" in b or "lantern" in b:
        return "t"
    if "fence" in b:
        return "f"
    if "stairs" in b or "slab" in b:
        return "s"
    if "log" in b or "wood" in b:
        return "l"
    if "plank" in b:
        return "p"
    if "cobble" in b or "stone" in b:
        return "c"
    if "path" in b:
        return "_"
    if "bell" in b:
        return "B"
    if "water" in b:
        return "~"
    if "grass" in b or "flower" in b or "poppy" in b or "dandelion" in b or "fern" in b:
        return ","
    return "x"


def main(argv):
    """See the module docstring."""
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)
    from engine import quick
    from films import hello_common as HC
    zs = [0, 1, 2, 3]
    nums = []
    i = 0
    while i < len(argv):
        if argv[i] == "--z":
            zs = [int(v) for v in argv[i + 1].split(",")]
            i += 2
            continue
        nums.append(int(argv[i]))
        i += 1
    x0, x1, y0, y1 = nums if len(nums) == 4 else (-12, 12, -12, 26)
    scene = quick.reset()
    v = HC.build_set(scene)
    w = v.world
    for z in zs:
        print("\nz = %d   (x %d..%d left to right, y %d at the bottom, north up)" % (z, x0, x1, y0))
        print("      " + "".join(str(abs(x) % 10) for x in range(x0, x1 + 1)))
        for y in range(y1, y0 - 1, -1):
            row = "".join(code(w.block_id(x, y, z)) for x in range(x0, x1 + 1))
            print("%5d %s" % (y, row))
    print("\nground at a few points:", {p: round(v.ground(*p), 3) for p in [(0.5, 9.6), (0.5, 6.4), (-1.2, -6.3), (5.3, 2.1), (4.0, 3.0)]})
    for k in sorted(v.anchors):
        if any(t in k for t in ("square", "bell", "well", "exit", "house_b_door", "house_c_door", "house_e", "house_f")):
            p = v.anchors[k]
            print("  %-22s (%.2f, %.2f, %.2f)" % (k, p[0], p[1], p[2]))
    lamps = sorted((round(o.location.x, 2), round(o.location.y, 2), round(o.location.z, 2), o.get("group", ""))
                   for o in v.lantern_lights if o.get("mc_light") != "fill"
                   and x0 <= o.location.x <= x1 and y0 <= o.location.y <= y1)
    print("lights in the box:", lamps)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
