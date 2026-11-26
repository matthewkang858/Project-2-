import bpy, math
from engine import nether, look
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
bas = nether.build_bastion(scene)
w = bas.world
for n, c in sorted(bas.cameras.items()):
    p = c["pos"]
    cell = tuple(int(math.floor(v)) for v in p)
    bid = w.block_id(*cell)
    print("%-16s pos %-28s cell %-16s block %s" % (n, tuple(round(v, 2) for v in p), cell, bid))
# blocks on the line of sight from each camera to its target (first solid hit)
def first_hit(a, b):
    n = int(math.dist(a, b) / 0.05)
    for i in range(1, n):
        t = i / n
        q = [a[k] + (b[k] - a[k]) * t for k in range(3)]
        c = tuple(int(math.floor(v)) for v in q)
        if w.is_solid(*c):
            return round(math.dist(a, q), 2), c, w.block_id(*c)
    return None
for n, c in sorted(bas.cameras.items()):
    print("%-16s line to target: %s" % (n, first_hit(c["pos"], c["target"])))
# key anchors seen from cameras: brute head height
A = bas.anchors
for cam, anc in (("gate", "home_landing"), ("inside_gate", "home_landing"), ("bridge_pillar", "bridge_pillar_foot"),
                 ("bridge_profile", "bridge_pillar_foot"), ("landing", "home_gold_1"), ("rim_side", "home_rim_w"),
                 ("bridge_shoulder", "bridge_brute"), ("treasure_flash", "treasure_flash"), ("flash", "home_flash"),
                 ("bridge_flash", "bridge_flash")):
    a = bas.cameras[cam]["pos"]
    p = A[anc]
    for dz in (0.2, 1.0, 1.8):
        print("%-15s -> %-18s z+%.1f: %s" % (cam, anc, dz, first_hit(a, (p[0], p[1], p[2] + dz))))
