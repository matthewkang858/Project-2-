"""Leg Day: the world state of the anvil wall, frame by frame, measured on a build (numbers, nothing rendered).

    $BPY -m tools.legday_state [--sky gold]          # every check of THE WORLD STATE (films/legday_common.py); exit
                                                     # 1 when one fails. One build (about 7 s).
What it checks: the crush of rd19 (all five struck and killed, the captain's feet on the landing frame inside the
march window), the drops within the game's 1.35-block toss of the captain's feet and Steve's rd21 place out of
pick-up reach, the planks out / in / out again (armed, after rd19's retraction, after the lead's re-arm inside the
dip), the twelfth piston invisible before tp13, its plank hidden until it is set, the twelfth anvils (day and dusk)
appearing ON their frames and staying, the dust power (15 by the lever) and the lever's state across the film, the
shelf per shot (which anvils each shot shows); THE CHIPPED ANVILS (the landed day set = CHIPPED = the dusk set's
chipped_anvils; every anvil in hand whole in the morning, chipped at dusk); THE PATROL CLOCK (every patrol twin at
rd19's twin's place on the same frames; the captain's feet at the key frames printed); Steve in rd21 two blocks or
more from the drops' REAL positions over the whole shot; no character inside a solid block in its shots (every 3
frames; the landed anvils' cells count as empty before the landing); the story's hard numbers: the arms two-shot
frontal (sq08: both bodies within 20 degrees of the lens from "arms" to "four"), the leg-day legs (swing 50 degrees
or more, a stair step every 7 frames or more), cl22 = cl11 and cl23 = cl12 frame for frame. Prefix with
`nice -n 15 timeout 290`.
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
    # 7. THE CHIPPED ANVILS: the day set lands chipped as CHIPPED; the dusk set and every anvil carried at dusk too
    falls = C.memo.get("rd_falls") or []
    got = tuple(i for i, d in enumerate(falls) if d.get("chipped"))
    check(got == tuple(LC.CHIPPED), "rd19: the anvils that chip on landing %s = CHIPPED %s" % (got, tuple(LC.CHIPPED)))
    dusk_ids = tuple(i for i, a in enumerate(C.anvils_dusk) if a.block_id == "chipped_anvil")
    check(dusk_ids == tuple(LC.CHIPPED), "the dusk set's chipped_anvils %s = CHIPPED" % (dusk_ids,))
    held = []
    for r in T.values():
        for name in sorted(st.in_shot.get(r.name, ())):
            c = st.cast[name]
            if hasattr(c, "holding_at"):
                it = c.holding_at("right", r.frame_start + 1)
                if it and it.endswith("anvil"):
                    held.append((r.name, name, it, r.sky))
    wrong = [h for h in held if (h[2] == "anvil") != (h[3] == "gold")]
    check(held and not wrong, "anvils in hand: whole in the morning, chipped at dusk (%d hands%s)"
          % (len(held), ("; WRONG " + ", ".join("%s %s %s" % h[:3] for h in wrong)) if wrong else ""))
    # 8. THE PATROL CLOCK: every patrol twin at the same place on the same frame, in the shots that show it
    clock = C.patrol_clock()
    twins = sorted({n.rsplit("_", 1)[0] for n in st.cast if n.startswith("patrol_") and n.endswith("_1")})
    shots_of = {tw: [r for r in T.values() if tw + "_1" in st.in_shot.get(r.name, ())] for tw in twins}
    for tw in twins:
        for r in shots_of[tw]:
            dev = 0.0
            for f in range(r.frame_start, r.frame_end + 1, 4):
                for k in range(1, 6):
                    ref = st.cast["patrol_rd19_%d" % k].pos_at(f) if f < clock["land"] else None
                    if ref is not None:
                        dev = max(dev, (st.cast["%s_%d" % (tw, k)].pos_at(f) - ref).length)
            check(dev < 0.02, "the patrol clock: %s in %s within %.3f block of rd19's twin on the same frames"
                  % (tw, r.name, dev))
    cap = st.cast.get("patrol_rd19_1")
    if cap is not None:
        print("[legday_state] the captain's feet on the clock (march from %d): %s" % (clock["start"], ", ".join(
            "%d y %.1f" % (f, cap.pos_at(f).y) for f in (903, 944, 1103, T["tp18_lever"].at("flipped"), 1142,
                                                          C.release_frame(), clock["land"]))))
    # 9. Steve in rd21 out of the drops' reach, measured on the real positions over the whole shot
    r21, items = T["rd21_still"], C.memo.get("rd_drops") or []
    steve = st.cast.get("steve_rd2")
    if steve is not None and items:
        near = min(math.dist(tuple(steve.pos_at(f))[:2], tuple(_where(scene, it, f))[:2])
                   for f in range(r21.frame_start, r21.frame_end + 1, 2) for it in items)
        check(near >= 2.0, "rd21: steve_rd2 stays %.2f blocks or more from the banner and the bottle (2 or more)" % near)
    # 10. no body inside a solid block, in its own shots (the landed anvils' cells count as empty before the landing)
    W, land = C.v.world, clock["land"]
    strip = {(0, y, 0) for y in range(46, 58)}
    inside = {}
    for r in sorted(T.values(), key=lambda r: r.frame_start):
        for f in range(r.frame_start, r.frame_end + 1, 3):
            scene.frame_set(f)
            for name in st.in_shot.get(r.name, ()):
                c = st.cast[name]
                root = getattr(c, "root", None)
                if root is None or not hasattr(c, "eye_point") or name.startswith(("cow_", "hen_")):
                    continue
                if root.hide_render:                              # dead and gone (a pillager after its poof)
                    continue
                if crush and name in crush["struck"] and f >= land:   # crushed: the body lies under its anvil (the
                    continue                                          # game draws the dying mob through the block)
                p = root.matrix_world.translation
                for h in (0.15, 0.9, 1.5):
                    q = (p.x, p.y, p.z + h)
                    cell = tuple(int(math.floor(v)) for v in q)
                    if cell in strip and f < land:
                        continue
                    if LS._solid_at(W, *q):
                        inside.setdefault((r.name, name, W.block_id(*cell)), []).append(f)
                        break
    for (shot, name, bid), fs in sorted(inside.items()):
        check(False, "%s: %s inside %s on frames %d-%d" % (shot, name, bid, fs[0], fs[-1]))
    check(not inside, "no character inside a solid block in its shots (sampled every 3 frames)")
    # 11. the story's hard numbers: the arms two-shot frontal (sq08), the leg-day legs (cl11 / cl12 / cl22 / cl23)
    r8 = T["sq08_arms"]
    cam8 = C.shots["sq08_arms"]
    for name in ("efe_sq", "steve_sq3"):
        c = st.cast[name]
        worst = 0.0
        for f in range(r8.at("arms"), r8.at("four") + 1, 2):
            scene.frame_set(f)
            cp = scene.camera.matrix_world.translation
            pp = c.pos_at(f)
            to_cam = math.atan2(cp.x - pp.x, -(cp.y - pp.y))
            d = math.degrees(abs((c.yaw_at(f) - to_cam + math.pi) % (2 * math.pi) - math.pi))
            worst = max(worst, d)
        check(worst <= 20.0, "sq08: %s's body within %.0f degrees of facing the lens from 'arms' to 'four' (20 at "
              "most: frontal, never side-on)" % (name, worst))
    del cam8
    for shot, who in (("cl11_climb", "steve_cl"), ("cl12_legday", "steve_cl2"), ("cl22_dusk", "steve_cl3"),
                      ("cl23_legday", "steve_cl4")):
        r, c = T[shot], st.cast[who]
        swing = []
        for f in range(r.frame_start + 6, r.frame_end + 1):
            scene.frame_set(f)
            swing.append(abs(math.degrees(c.parts["leg_r"].rotation_euler[0])))
        p0, p1 = c.pos_at(r.frame_start), c.pos_at(r.frame_end)
        per_step = (r.frame_end - r.frame_start) / max(abs(p1.y - p0.y), 1e-6)
        check(max(swing) >= 50.0 and per_step >= 7.0, "%s: %s's legs swing up to %.0f degrees (50 or more), a stair "
              "step every %.1f frames (7 or more)" % (shot, who, max(swing), per_step))
    for a_, b_, n in (("cl11_climb", "cl22_dusk", 70), ("cl12_legday", "cl23_legday", 45)):
        ra, rb = T[a_], T[b_]
        dev = 0.0
        for k in range(0, n):
            for role in ("steve", "kai"):
                ta = [nm for nm in st.in_shot.get(a_, ()) if nm.startswith(role + "_cl")][0]
                tb = [nm for nm in st.in_shot.get(b_, ()) if nm.startswith(role + "_cl")][0]
                scene.frame_set(ra.frame_start + k)
                pa = st.cast[ta].root.matrix_world.translation.copy()
                scene.frame_set(rb.frame_start + k)
                pb = st.cast[tb].root.matrix_world.translation.copy()
                dev = max(dev, (pa - pb).length)
        check(dev < 1e-3, "%s repeats %s frame for frame over %d frames (largest difference %.4f block)"
              % (b_, a_, n, dev))
    print("[legday_state] %d failure(s)" % len(bad))
    return 1 if bad else 0


def _where(scene, it, f):
    """World position of a dropped item's root at frame f."""
    scene.frame_set(f)
    return it.root.matrix_world.translation.copy()


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
