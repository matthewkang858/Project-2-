"""Six Seconds, sequence FLASH: score the runner's death puff of the three flash cuts without a render.

    $BPY -m tools.sixseconds_flash_probe puffs [--seeds 0-199] [--offsets 6,8,10,12] [--top 6]
    $BPY -m tools.sixseconds_flash_probe one WORLD SEED OFFSET           # frame by frame for one choice
    $BPY -m tools.sixseconds_flash_probe check                           # the mirror against engine.piglins.poof

For every world (bridge / treasure / home), seed and start offset (the puff starts OFFSET frames before the cut, as
C.puff(s, six_flash_puff_<world>, f0 - OFFSET, seed=SEED) does) it simulates engine.piglins.poof (a mirror of its
random draws without Blender objects, checked against it by `check`) at
the SHARED anchor six_flash_puff_<world> (= the brute's flash place + FLASH_OFFSETS puff (+0.95, +0.3)) and
projects every puff's sprite (its alpha-covered part, per sprite stage) into the SHARED flash camera
(films/sixseconds_common.py CAMS["flash_<world>"]) on each PICTURE frame of the cut (after its snap). It sums, in
frame-% squared:
    vis     the puff seen inside x 8-82 % (y 14-60 %) and not hidden behind the brute (what reads as "a puff")
    spill   the puff at x > 82 % (outside the safe area for faces and hero props; information only)
    hidden  the puff where a phone hides it: x > 95 % (the side crop) or x > 84 % below y 45 % (the icon column)
    brute   the puff IN FRONT of the brute over his silhouette box (head x 33-67 / y 19-31, body x 31-69 / y 30-47,
            legs x 40-60 / y 46-60): white on his face and armband
    drops   the puff over the golden boots (x 11-29 / y 49-58) or the extra drop (x 59-76 / y 48-59)
    gold    (treasure) the puff over the gold-block pile (x 68-100 / y 23-48)
The score = vis - hidden - 3 brute - 3 drops - 1.5 gold. Nothing is written; no set is built (the floor is z 0 and
nothing collides, as in the film: C.puff passes no village).
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# the brute's flash place in each world (engine/nether.py anchors home_flash / bridge_flash / treasure_flash: the
# SHARED flash cameras aim 0.5 above them, 5 blocks away) and the shot of each world
WORLDS = {"bridge": ((400.5, 16.5, 0.0), "fl16_bridge"),
          "treasure": ((-396.0, 0.8, 0.0), "fl16_treasure"),
          "home": ((4.5, 14.5, 0.0), "fl16_home")}
REGIONS = {
    "brute": [((33, 67), (19, 31)), ((31, 69), (30, 47)), ((40, 60), (46, 60))],
    "drops": [((11, 29), (49, 58)), ((59, 76), (48, 59))],
    "gold": [((68, 100), (23, 48))],
}
BRUTE_DEPTH = 5.0           # the brute's distance from the lens (his front face about 4.85)


def _alpha_box(sprite):
    """(fill fraction, (x0, x1, y0, y1) in -1..1 quad coordinates) of a particle sprite's opaque texels."""
    from engine import mcassets
    import numpy as np
    a = np.asarray(mcassets.texture_array(sprite))
    alpha = a[..., 3] if a.shape[-1] == 4 else np.ones(a.shape[:2])
    alpha = alpha / (255.0 if alpha.max() > 1.0 else 1.0)
    ys, xs = np.nonzero(alpha > 0.1)
    h, w = alpha.shape
    if len(xs) == 0:
        return 0.0, (0, 0, 0, 0)
    box = (2.0 * xs.min() / w - 1.0, 2.0 * (xs.max() + 1) / w - 1.0, 2.0 * ys.min() / h - 1.0,
           2.0 * (ys.max() + 1) / h - 1.0)
    inside = alpha[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return float((inside > 0.1).mean()), box


def _overlap(a, b):
    """Area of the intersection of two boxes ((x0, x1), (y0, y1)) in %^2."""
    w = min(a[0][1], b[0][1]) - max(a[0][0], b[0][0])
    h = min(a[1][1], b[1][1]) - max(a[1][0], b[1][0])
    return max(0.0, w) * max(0.0, h)


def _plan():
    from engine import narration
    from films import sixseconds as F
    nar = narration.load("sixseconds", F.NARRATION, fps=F.FPS)
    return {r.name: r for r in F.timeline(nar)}


def particles(spot, frame, seed, size=(0.6, 1.8)):
    """engine.piglins.poof's puffs without making a Blender object: the same random draws in the same order (seed,
    frame and spot salt the generator), the same fx._simulate. [dict(pos, size, spawn, spans=[(stage, a, b)])]: the
    tick positions, the quad's half side, the spawn frame, the frames [a, b) each sprite stage is drawn on.
    `check` compares it with the real poof()."""
    from engine import fx, piglins
    x, y, z = (float(v) for v in spot)
    rng = fx._rng(seed, int(frame), 60, int(round(x * 16.0)), int(round(y * 16.0)))
    w, h = size
    top = len(piglins.POOF_SPRITES) - 1
    out = []
    for _i in range(piglins.POOF_COUNT):
        va = rng.normal(0.0, 1.0, 3) * 0.02
        p = (x + w * (2.0 * rng.random() - 1.0) - va[0] * 10.0,
             y + w * (2.0 * rng.random() - 1.0) - va[1] * 10.0,
             z + h * rng.random() - va[2] * 10.0)
        v = va + (rng.random(3) * 2.0 - 1.0) * 0.05
        rng.random()                                          # grey
        quad = 0.1 * (rng.random() * rng.random() * 6.0 + 1.0)
        life = int(16.0 / (rng.random() * 0.8 + 0.2)) + 2
        path = fx._simulate(p, v, life, 0.04 * piglins.POOF_GRAVITY, piglins.POOF_FRICTION, None, 0.2, rng)
        ages = {}
        for age in range(len(path)):
            ages.setdefault(age * top // life, []).append(age)
        spans = []
        for k, span in sorted(ages.items()):
            fa = int(math.ceil(frame + span[0] * piglins.TICK - 1e-6))
            fb = int(math.ceil(frame + (span[-1] + 1) * piglins.TICK - 1e-6))
            if fb > fa:
                spans.append((k, fa, fb))
        out.append(dict(pos=path, size=quad, spawn=float(frame), spans=spans))
    return out


def _at(p, f):
    """A puff's position on frame f (the carrier's keys: drawn one tick behind, linear between ticks)."""
    from mathutils import Vector
    from engine import piglins
    path = p["pos"]
    t = (f - p["spawn"]) / piglins.TICK
    i = int(math.floor(t)) - 1
    if i < 0:
        return Vector(path[0])
    i = min(i, len(path) - 2)
    a = max(0.0, min(1.0, t - 1 - i))
    return Vector(path[i]).lerp(Vector(path[i + 1]), a)


def simulate(world, seed, offset, rows, sprites):
    """[(frame, [(u0, u1, v0, v1, depth, fill)])] of one choice over the cut's picture frames (u, v in %)."""
    from mathutils import Vector
    from films import sixseconds_common as SC
    from films import sixseconds_set as SS
    brute, shot = WORLDS[world]
    row = rows[shot]
    first = row.black[1] + 1 if row.black else row.frame_start
    cam = SC.CAMS["flash_%s" % world]
    off = SS.FLASH_OFFSETS["puff"]
    spot = (brute[0] + off[0], brute[1] + off[1], brute[2])
    puffs = particles(spot, row.frame_start - offset, seed)
    C, T = Vector(cam["pos"]), Vector(cam["target"])
    fwd = (T - C).normalized()
    right = fwd.cross(Vector((0.0, 0.0, 1.0))).normalized()
    up = right.cross(fwd)
    k_u = cam["lens"] / (36.0 * 9.0 / 16.0) * 100.0
    k_v = cam["lens"] / 36.0 * 100.0
    out = []
    for f in range(first, row.frame_end + 1):
        quads = []
        for p in puffs:
            stage = [k for k, a, b in p["spans"] if a <= f < b]
            if not stage:
                continue
            d = _at(p, f) - C
            z = d.dot(fwd)
            if z <= 0.1:
                continue
            cu = 50.0 + d.dot(right) / z * k_u
            cv = 50.0 - d.dot(up) / z * k_v
            fill, (x0, x1, y0, y1) = sprites[stage[0]]
            s = p["size"]                                   # half the quad's side (the quad spans -1..1)
            hu, hv = s / z * k_u, s / z * k_v
            quads.append((cu + x0 * hu, cu + x1 * hu, cv + y0 * hv, cv + y1 * hv, z, fill))
        out.append((f, quads))
    return out


def cmd_check(argv):
    """The mirror against the real engine.piglins.poof for one spot, frame and seed."""
    import bpy
    from mathutils import Vector
    from engine import piglins
    scene = bpy.context.scene
    cd = bpy.data.cameras.new("probe_cam")
    scene.camera = bpy.data.objects.new("probe_cam", cd)
    scene.collection.objects.link(scene.camera)
    worst = 0.0
    cases = ((17, 991, (401.45, 16.8, 0.0)), (3, 1009, (-395.05, 1.1, 0.0)), (40, 1028, (5.45, 14.8, 0.0)))
    for seed, frame, spot in cases:
        real = piglins.poof(Vector(spot), frame, camera=scene.camera, size=(0.6, 1.8), seed=seed)
        mine = particles(spot, frame, seed)
        assert len(real.particles) == sum(len(p["spans"]) for p in mine), "particle count"
        flat = [(p, k, a, b) for p in mine for k, a, b in p["spans"]]
        for r, (p, k, a, b) in zip(real.particles, flat):
            assert (r["stage"], r["first"], r["last"]) == (k, a, b), (r["stage"], r["first"], r["last"], k, a, b)
            assert abs(r["size"] - p["size"]) < 1e-9
            worst = max(worst, max((Vector(q) - Vector(m)).length for q, m in zip(r["pos"], p["pos"])))
    print("mirror matches poof(): stages, frames, sizes equal; worst position difference %.2e" % worst)


def score(world, frames, gold_weight=1.5):
    tot = dict(vis=0.0, spill=0.0, hidden=0.0, brute=0.0, drops=0.0, gold=0.0, n=0)
    for f, quads in frames:
        for u0, u1, v0, v1, z, fill in quads:
            box = ((u0, u1), (v0, v1))
            area = (u1 - u0) * (v1 - v0) * fill
            full = max(1e-6, (u1 - u0) * (v1 - v0))
            behind = z > BRUTE_DEPTH - 0.1
            on_brute = sum(_overlap(box, r) for r in REGIONS["brute"]) / full * area
            tot["spill"] += _overlap(box, ((82, 140), (-20, 120))) / full * area
            cut = _overlap(box, ((95, 140), (-20, 120))) + _overlap(box, ((84, 95), (45, 120)))
            tot["hidden"] += cut / full * area
            seen = _overlap(box, ((8, 82), (14, 60))) / full * area
            tot["vis"] += max(0.0, seen - (on_brute if behind else 0.0))
            if not behind:
                tot["brute"] += on_brute
            tot["drops"] += sum(_overlap(box, r) for r in REGIONS["drops"]) / full * area
            if world == "treasure":
                tot["gold"] += sum(_overlap(box, r) for r in REGIONS["gold"]) / full * area
        tot["n"] += 1
    n = max(1, tot["n"])
    for k in ("vis", "spill", "hidden", "brute", "drops", "gold"):
        tot[k] /= n                                         # per picture frame
    tot["score"] = tot["vis"] - tot["hidden"] - 3.0 * tot["brute"] - 3.0 * tot["drops"] - gold_weight * tot["gold"]
    return tot


def _sprites():
    from engine import piglins
    return [_alpha_box(s) for s in piglins.POOF_SPRITES]


def cmd_puffs(argv):
    import argparse
    ap = argparse.ArgumentParser(prog="tools.sixseconds_flash_probe puffs")
    ap.add_argument("--seeds", default="0-199")
    ap.add_argument("--offsets", default="6,8,10,12")
    ap.add_argument("--top", type=int, default=6)
    ap.add_argument("--worlds", default="bridge,treasure,home")
    ap.add_argument("--gold", type=float, default=1.5, help="weight of the gold-pile cover in the score")
    ap.add_argument("--budget", type=float, default=240.0, help="seconds: stop the search and print what is done")
    a = ap.parse_args(argv)
    import time
    t0 = time.time()
    lo, hi = (int(v) for v in a.seeds.split("-"))
    offsets = [int(v) for v in a.offsets.split(",")]
    rows, sprites = _plan(), _sprites()
    for world in a.worlds.split(","):
        res = []
        for seed in range(lo, hi + 1):
            if time.time() - t0 > a.budget:
                print("(budget spent: seeds %d-%d only)" % (lo, seed - 1))
                break
            for off in offsets:
                res.append((score(world, simulate(world, seed, off, rows, sprites), a.gold), seed, off))
        res.sort(key=lambda r: -r[0]["score"])
        print("== %s (%d candidates)" % (world, len(res)))
        stub = [r for r in res if r[1] == {"bridge": 17, "treasure": 18, "home": 19}[world] and r[2] == 8]
        for t, seed, off in res[:a.top] + stub:
            print("  seed %3d off %2d  score %7.1f  vis %6.1f  spill %6.1f  hidden %6.1f  brute %5.1f  drops %5.1f"
                  "  gold %5.1f%s" % (seed, off, t["score"], t["vis"], t["spill"], t["hidden"], t["brute"], t["drops"],
                                      t["gold"],
                     "   (the stub)" if (t, seed, off) in stub else ""))


def cmd_one(argv):
    world, seed, off = argv[0], int(argv[1]), int(argv[2])
    rows, sprites = _plan(), _sprites()
    frames = simulate(world, seed, off, rows, sprites)
    for f, quads in frames:
        if not quads:
            print("%d: none" % f)
            continue
        u0 = min(q[0] for q in quads)
        u1 = max(q[1] for q in quads)
        v0 = min(q[2] for q in quads)
        v1 = max(q[3] for q in quads)
        print("%d: %2d puffs  x %5.1f-%5.1f  y %5.1f-%5.1f" % (f, len(quads), u0, u1, v0, v1))
    print(score(world, frames))


def main(argv):
    cmds = {"puffs": cmd_puffs, "one": cmd_one, "check": cmd_check}
    if not argv or argv[0] not in cmds:
        print(__doc__)
        return 2
    return cmds[argv[0]](argv[1:]) or 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
