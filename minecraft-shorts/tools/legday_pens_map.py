"""Leg Day, pens sequence: a top-down map of the ground round the pens (the pens director's scouting tool).

    $BPY -m tools.legday_pens_map [x0 y0 x1 y1]       # default x -30..0, y 10..34
Each cell: a letter for the highest block there, UPPER CASE when it stands 2 or more above the ground:
  . grass   f fence   p path   w wall/stone   L log   l leaves   h house (planks/cobble/glass ...)   t tuft/plant
North is up. Nothing is written.
"""
import sys


def main(argv):
    x0, y0, x1, y1 = (int(v) for v in argv[:4]) if len(argv) >= 4 else (-30, 10, 0, 34)
    import render
    ses = render.Session("legday", sky="gold")
    v = ses.result["context"].v
    w = v.world
    print("     " + "".join("%-3d" % x if x % 3 == 0 else "" for x in range(x0, x1 + 1)))
    for y in range(y1, y0 - 1, -1):
        row = []
        for x in range(x0, x1 + 1):
            z, b = None, ""
            for zz in range(40, -8, -1):
                bid = w.block_id(x, y, zz)
                if bid and bid not in ("air", "minecraft:air"):
                    z, b = zz, bid
                    break
            if z is None:
                row.append(" ")
                continue
            if "fence" in b:
                ch = "f"
            elif "path" in b:
                ch = "p"
            elif "log" in b:
                ch = "L"
            elif "leaves" in b:
                ch = "l"
            elif "grass_block" in b or b == "dirt":
                ch = "."
            elif any(k in b for k in ("stone_brick", "stone", "cobble")):
                ch = "w"
            elif any(k in b for k in ("grass", "fern", "flower", "poppy", "dandelion", "tulip", "bush")):
                ch = "t"
            else:
                ch = "h"
            row.append(ch.upper() if z >= 2 else ch)
        print("%4d " % y + "".join(row))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
