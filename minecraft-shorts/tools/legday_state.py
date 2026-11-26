"""Leg Day: the world state of the anvil wall, frame by frame, measured on a build (numbers, nothing rendered).

    $BPY -m tools.legday_state [--sky gold]          # every check of THE WORLD STATE (films/legday_common.py); exit
                                                     # 1 when one fails. One build (about 7 s).
What it checks: the crush of rd19 (all five struck and killed, the captain's feet on the landing frame inside the
march window), the drops within the game's 1.35-block toss of the captain's feet and Steve's rd21 place out of
pick-up reach, the planks out / in / out again (armed, after rd19's retraction, after the lead's re-arm inside the
dip), the twelfth piston invisible before tp13, its plank hidden until it is set, the twelfth anvils (day and dusk)
appearing ON their frames and staying, the dust power (15 by the lever) and the lever's state across the film, the
shelf per shot (which anvils each shot shows). Prefix with `nice -n 15 timeout 290`.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    """Build one sky and check the wall's state (see the module docstring)."""
    import argparse
    ap = argparse.ArgumentParser(prog="tools.legday_state")
    ap.add_argument("--sky", default="gold")
    args = ap.parse_args(argv)
    import render                                     # (imports bpy first: the film modules need mathutils)
    ses = render.Session("legday", sky=args.sky)
    from films import legday_common as LC
    from films import legday_set as LS
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    T = C.T
    bad = []

    def check(ok, text):
        print("[legday_state] %s %s" % ("ok  " if ok else "FAIL", text))
        if not ok:
            bad.append(text)

    def hidden(ob, f):
        scene.frame_set(f)
        return bool(ob.hide_render)

    def pos(ob, f):
        scene.frame_set(f)
        return tuple(ob.matrix_world.translation)

    # 1. rd19: the crush and the drops
    crush = C.memo.get("rd_crush")
    check(crush is not None, "rd19_drop keyed the crush (C.memo['rd_crush'])")
    if crush:
        land = crush["land"]
        check(len(crush["struck"]) == 5, "rd19: %d of 5 pillagers crushed %s" % (len(crush["struck"]), crush["struck"]))
        cap = st.cast[sorted(crush["struck"])[0]] if crush["struck"] else None
        if cap is not None:
            feet = cap.pos_at(land)
            lo, hi = LC.LAND_WINDOW
            check(lo <= feet.y <= hi, "rd19: the captain's feet on the landing frame %d at y %.2f (window %.2f .. %.2f)"
                  % (land, feet.y, lo, hi))
            check(T["rd19_drop"].frame_start < land < T["rd19_drop"].frame_end - 24,
                  "rd19: the anvils land on %d, inside the shot with the death (24 frames) before its end %d"
                  % (land, T["rd19_drop"].frame_end))
            for where in ("banner_spot", "bottle_spot"):
                d = math.dist(C.P(where)[:2], (feet.x, feet.y))
                check(d <= 1.35, "the %s is %.2f blocks from the captain's feet (the game's toss: 1.35 at most)"
                      % (where, d))
            d = math.dist(C.P("steve_among_anvils")[:2], C.P("banner_spot")[:2])
            check(d >= 2.0, "rd21: Steve stands %.2f blocks from the banner (out of pick-up reach: 2 or more)" % d)
    # 2. the planks: out (armed), in after rd19's retraction, out again after the re-arm inside the dip
    plank = C.row.blocks[0]
    ob = plank.objects[0] if isinstance(plank.objects, list) else plank.objects()[0]
    r22 = T["cl22_dusk"].frame_start
    f_back = T["rd19_drop"].at("back")
    for f, x_want, why in ((T["sq01_squats"].frame_start, 0.0, "armed at the start"),
                           (f_back - 1, 0.0, "out just before rd19's retraction"),
                           (f_back + 4, -1.0, "in after the retraction"),
                           (r22 - 1, -1.0, "still in on rd21's last frame"),
                           (r22 + 2, 0.0, "out again after the re-arm (inside the dip)")):
        x = pos(ob, f)[0]
        check(abs(x - x_want) < 0.02, "plank 1 at x %.2f on frame %d: %s" % (x, f, why))
    # 3. the twelfth piston and its plank (tp13)
    t13 = T["tp13_sticky"]
    p12 = C.row.pistons[11]
    obs = p12.objects if isinstance(p12.objects, list) else p12.objects()
    seen_before = any(not hidden(o, t13.frame_start - 5) for o in obs if o.type == "MESH")
    seen_after = any(not hidden(o, t13.frame_end) for o in obs if o.type == "MESH")
    check(not seen_before and seen_after, "the twelfth piston: invisible before tp13 (%s), there at its end (%s)"
          % (not seen_before, seen_after))
    pl12 = C.row.blocks[11]
    pobs = pl12.objects if isinstance(pl12.objects, list) else pl12.objects()
    check(hidden(pobs[0], t13.frame_start) and not hidden(pobs[0], t13.frame_end),
          "the twelfth plank: hidden at tp13's start, there at its end")
    # 4. the twelfth anvils appear ON their frames and stay
    for shot, anvil, nxt in (("tp14_why", C.anvils[11], "rd15_pillagers"),
                             ("tp24_reloading", C.anvils_dusk[11], None)):
        r = T[shot]
        o = anvil.objects()[0]
        flips = [f for f in range(r.frame_start, r.frame_end) if hidden(o, f) and not hidden(o, f + 1)]
        stays = hidden(o, r.frame_start) and not hidden(o, r.frame_end)
        if nxt:
            stays = stays and not hidden(o, T[nxt].frame_start + 1)
        check(len(flips) == 1 and stays, "%s: %s appears on frame %s and stays" % (shot, anvil.name, flips))
    # 5. the shelf per shot: the anvils each shot shows (the day set on the road after rd19)
    for r in sorted(T.values(), key=lambda r: r.frame_start):
        which, idx = LC.SHELF[r.shelf]
        f = r.frame_start + 1
        # (an anvil that chipped on landing is drawn by its chipped_anvil / damaged_anvil variant: any object counts)
        seen = lambda a: any(not hidden(o, f) for o in a.objects())
        shown = [i for i, a in enumerate(getattr(C, which)) if seen(a)]
        other = "anvils_dusk" if which == "anvils" else "anvils"
        leak = [i for i, a in enumerate(getattr(C, other)) if seen(a)]
        want = list(idx)
        check(shown == want and not leak, "%-15s shelf %-11s shows %s %s%s" % (
            r.name, r.shelf, which, _ranges(shown), ("; LEAK of %s %s" % (other, leak)) if leak else ""))
    # 6. the dust and the lever
    lever_flip = T["tp18_lever"].at("flipped")
    for f, want, why in ((T["tp14_why"].frame_start, 15, "lit by the lever in tp14"),
                         (lever_flip + 3, 0, "dark after the flip in tp18"),
                         (T["rd21_still"].frame_end, 0, "dark through rd21"),
                         (r22 + 2, 15, "lit again after the re-arm")):
        lev = C.wire.level_at((LS.DUST_X, LS.DUST_Y[-1], LS.TOP_Z + 1), f)
        check(lev == want, "dust by the lever at power %d on frame %d: %s" % (lev, f, why))
    for f, want in ((lever_flip - 2, True), (lever_flip + 3, False), (r22 + 2, True)):
        check(C.lever.state_at(f) == want, "lever %s on frame %d" % ("on" if want else "off", f))
    print("[legday_state] %d failure(s)" % len(bad))
    return 1 if bad else 0


def _ranges(ix):
    """[3, 4, 5, 7] -> '3-5,7'."""
    out, run = [], []
    for i in ix:
        if run and i == run[-1] + 1:
            run.append(i)
        else:
            if run:
                out.append("%d-%d" % (run[0], run[-1]) if len(run) > 1 else str(run[0]))
            run = [i]
    if run:
        out.append("%d-%d" % (run[0], run[-1]) if len(run) > 1 else str(run[0]))
    return ",".join(out) or "none"


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
