"""The Hello: print what the set offers (anchors, beds, doors, cutaways, house_a block by block). No render."""
import sys

import bpy

from engine import quick, sets, village


def main(argv):
    """Build the village with hello_set and print its data; `layers` also prints house_a layer by layer."""
    scene = quick.reset()
    v = village.build_village(scene, seed=1, bed_colors={"house_a_bed_2": "red"}, edit=lambda b: sets.hello_set(b))
    print("ANCHORS")
    for k in sorted(v.anchors):
        p = v.anchors[k]
        print("  %-26s (%.2f, %.2f, %.2f)  yaw %s" % (k, p[0], p[1], p[2], ("%.2f" % v.yaws[k]) if k in v.yaws else "-"))
    print("PATHS")
    for k in sorted(v.paths):
        pts = v.paths[k]
        print("  %-22s %d nodes: %s ... %s" % (k, len(pts), tuple(round(c, 2) for c in pts[0]), tuple(round(c, 2) for c in pts[-1])))
    print("BEDS", {k: {kk: (tuple(round(c, 2) for c in vv) if isinstance(vv, (tuple, list)) else vv) for kk, vv in b.items()} for k, b in v.beds.items() if "house_a" in k})
    print("DOORS", {k: tuple(round(c, 2) for c in d.matrix_world.translation) for k, d in v.doors.items()})
    print("CUTAWAYS", {k: len(obs) for k, obs in v.cutaways.items()})
    print("BUILDINGS", {k: b for k, b in v.buildings.items()} if isinstance(v.buildings, dict) else v.buildings)
    print("LIGHT GROUPS", {g: [(tuple(round(c, 2) for c in o.location), o.get("mc_light"), round(o.get("base_energy", 0), 1)) for o in obs]
                           for g, obs in v.lights.items() if g in ("house_a", "well", "bell_w", "bell_e", "house_b", "house_c")})
    print("SETS", list(v.sets))
    hello = v.sets["hello"]
    print("HELLO CAMERAS", hello["cameras"])
    print("HELLO layout", hello.get("layout"))
    if "layers" in argv:
        w = v.world
        x0, x1, y0, y1 = 6, 23, -17, -3
        for z in range(0, 8):
            print("z =", z)
            for y in range(y1, y0 - 1, -1):
                row = []
                for x in range(x0, x1 + 1):
                    g = w.get(x, y, z)
                    if g is None:
                        row.append(" . ")
                        continue
                    bid, props = g
                    short = {"oak_planks": "PL", "cobblestone": "CB", "mossy_cobblestone": "CB", "oak_log": "LG", "stripped_oak_log": "SL",
                             "oak_stairs": "ST", "oak_door": "DR", "glass_pane": "GP", "torch": "TO", "wall_torch": "WT",
                             "white_bed": "BD", "red_bed": "RB", "oak_fence": "FN", "oak_slab": "SB", "grass_block": "GR",
                             "dirt_path": "PA", "dirt": "DI", "oak_pressure_plate": "PP", "oak_trapdoor": "TD",
                             "short_grass": "sg", "tall_grass": "tg", "oak_leaves": "LV", "white_terracotta": "WT2",
                             "cobblestone_stairs": "CS", "cobblestone_slab": "Cs", "oak_wall_sign": "SG"}.get(bid, bid[:3])
                    f = (props or {}).get("facing", "")
                    row.append("%-3s" % (short + (f[:1] if f else "")))
                print("  y %4d  " % y + " ".join(row))
            print("          " + " ".join("%-3d" % x for x in range(x0, x1 + 1)))


if __name__ == "__main__":
    main(sys.argv[1:])
