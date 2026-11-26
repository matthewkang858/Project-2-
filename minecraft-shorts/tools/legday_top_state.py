"""Leg Day, sequence TOP: the part of tools/legday_state's check 10 ("no body inside a solid block in its shots")
that concerns the top sequence, sampled every 2 frames of tp13 / tp14 / tp18 / tp24 (tools/legday_state runs the
whole film every 3 frames and needs more than the 290 s a command may take on a loaded machine), and where each
body stands (its feet's height: on the walkway z 18). One build of one sky.

    $BPY -m tools.legday_top_state --sky gold        # tp13, tp14, tp18
    $BPY -m tools.legday_top_state --sky dusk        # tp24

The top director's own tool. Prefix with `nice -n 12 timeout 290`.
"""
import argparse
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

SHOTS = {"gold": ("tp13_sticky", "tp14_why", "tp18_lever"), "dusk": ("tp24_reloading",)}


def main(argv):
    ap = argparse.ArgumentParser(prog="tools.legday_top_state")
    ap.add_argument("--sky", default="gold")
    args = ap.parse_args(argv)
    import render
    from films import legday_set as LS
    ses = render.Session("legday", sky=args.sky)
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    W = C.v.world
    bad = 0
    for name in SHOTS[args.sky]:
        s = C.shots[name]
        inside, zs = {}, {}
        for f in range(s.frame_start, s.frame_end + 1, 2):
            scene.frame_set(f)
            for who in sorted(st.in_shot.get(name, ())):
                c = st.cast[who]
                root = getattr(c, "root", None)
                if root is None or not hasattr(c, "eye_point") or root.hide_render:
                    continue
                p = root.matrix_world.translation
                zs.setdefault(who, set()).add(round(p.z, 3))
                for h in (0.15, 0.9, 1.5):
                    q = (p.x, p.y, p.z + h)
                    if LS._solid_at(W, *q):
                        cell = tuple(int(math.floor(v)) for v in q)
                        inside.setdefault((who, W.block_id(*cell)), []).append(f)
                        break
        for (who, bid), fs in sorted(inside.items()):
            bad += 1
            print("[legday_top_state] FAIL %s: %s inside %s on frames %d-%d" % (name, who, bid, fs[0], fs[-1]))
        for who, z in sorted(zs.items()):
            print("[legday_top_state] %s: %s feet z %s" % (name, who, ", ".join("%.3f" % v for v in sorted(z))))
        print("[legday_top_state] %s %s: no body inside a solid block (every 2 frames, %d-%d)" % (
            "ok  " if not inside else "FAIL", name, s.frame_start, s.frame_end))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
