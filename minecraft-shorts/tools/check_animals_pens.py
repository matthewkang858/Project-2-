"""wander() under stress, numbers only (the module's author's own test; no rendering): many seeds, each pair of
bodies against the clearance that pair was promised, the edge, how often every animal walks, a minute-long pen, a
second call with place=False while walks are still running, and avoid=.

Run:  $BPY -m tools.check_animals_pens [seeds]        (default 60 seeds; about 1 s per 4 seeds)
"""
import math
import sys
import time


def measure(animals, herd, f0, f1, area, avoid=()):
    """(worst margin between a pair of bodies and the clearance promised to that pair, worst margin of a body from
    the edge against its own width, worst margin from anything in `avoid`), over the frames; negative = broken."""
    pair, edge, other = 9.0, 9.0, 9.0
    for f in range(f0, f1 + 1):
        poses = [(a, a.pos_at(f), a.yaw_at(f)) for a in herd]
        for i, (a, pa, ya) in enumerate(poses):
            for x, y, r in a.body_points(pa, ya):
                edge = min(edge, min(x - r - area[0], area[2] - x - r, y - r - area[1], area[3] - y - r) - a.width)
            for b, pb, yb in poses[i + 1:]:
                pair = min(pair, animals._gap(a, pa, ya, b, pb, yb) - max(a.width, b.width))
            for o in avoid:
                g = animals._apart(a.body_points(pa, ya), animals._circles(o, f))[0]
                if g is not None:
                    other = min(other, g - a.width)
    return pair, edge, other


def main(argv):
    from engine import animals, characters as ch, quick

    seeds = int(argv[0]) if argv else 60
    good = True
    t0 = time.time()
    stats = {}
    for seed in range(seeds):
        quick.reset()
        cows = [animals.make_cow("c%d" % i) for i in range(5)] + [animals.make_cow("k", baby=True)]
        hens = [animals.make_chicken("h%d" % i) for i in range(6)] + [animals.make_chicken("q%d" % i, baby=True) for i in range(2)]
        for kind, herd, cells in (("5 cows + calf, 10x10 cells", cows, (0, 0, 9, 9)),
                                  ("6 hens + 2 chicks, 8x9 cells", hens, (20, 0, 27, 8))):
            area = animals.pen_area(*cells)
            ev = animals.wander(herd, 1, 121, area, seed=seed)
            ev2 = animals.wander(herd, 121, 241, area, seed=seed + 1000, place=False)   # walks of the first call still run
            pair, edge, _o = measure(animals, herd, 1, 320, area)
            walks = {n: sum(1 for x in ev[n] + ev2[n] if x[0] == "walk") for n in ev}
            first = sum(1 for n in ev if any(x[0] == "walk" for x in ev[n]))
            st = stats.setdefault(kind, dict(pair=9.0, edge=9.0, walks=[], never=0, bad=0, first=[]))
            st["pair"], st["edge"] = min(st["pair"], pair), min(st["edge"], edge)
            st["walks"].append(sum(walks.values()))
            st["first"].append(first)
            st["never"] += sum(1 for w in walks.values() if w == 0)
            st["bad"] += pair < -1e-6 or edge < -1e-6
    for kind, st in stats.items():
        ok = st["bad"] == 0
        good &= ok
        print("%s %s, %d seeds x 10 s (two calls, the second place=False): pens that break a promise %d; worst margin "
              "between two bodies %+.3f and from the edge %+.3f over what was promised; walks per pen %d-%d (mean %.1f); "
              "animals that walk in the first 5 s %d-%d of %d; animals that never walk in 10 s: %d of %d" % (
                  "ok  " if ok else "FAIL", kind, seeds, st["bad"], st["pair"], st["edge"], min(st["walks"]),
                  max(st["walks"]), sum(st["walks"]) / len(st["walks"]), min(st["first"]), max(st["first"]),
                  6 if "cows" in kind else 8, st["never"], seeds * (6 if "cows" in kind else 8)))
    print("   (%.1f s)" % (time.time() - t0))

    # ---- a minute in one call: nobody stands for the whole of it
    least, worst_pair, worst_edge, t1 = 99, 9.0, 9.0, time.time()
    spread = []
    for seed in range(max(4, seeds // 10)):
        quick.reset()
        cows = [animals.make_cow("c%d" % i) for i in range(6)]
        area = animals.pen_area(0, 0, 9, 9)
        ev = animals.wander(cows, 1, 1441, area, seed=seed)
        pair, edge, _o = measure(animals, cows, 1, 1500, area)
        walks = [sum(1 for x in e if x[0] == "walk") for e in ev.values()]
        spread.append(walks)
        least, worst_pair, worst_edge = min(least, min(walks)), min(worst_pair, pair), min(worst_edge, edge)
    ok = least >= 5 and worst_pair >= -1e-6 and worst_edge >= -1e-6
    good &= ok
    print("%s six cows for 60 s in one call, %d seeds (%.1f s): fewest walks of any cow %d; walks per cow %s ...; "
          "margins %+.3f / %+.3f" % ("ok  " if ok else "FAIL", len(spread), time.time() - t1, least, spread[:3],
                                     worst_pair, worst_edge))

    # ---- avoid=: the player stands in the pen, one cow follows him; the others keep their width from both
    worst, worst_pair, moved = 9.0, 9.0, 0
    for seed in range(max(4, seeds // 10)):
        quick.reset()
        steve = ch.make_player("steve")
        area = animals.pen_area(0, 0, 9, 9)
        steve.place(1, (4.4, 2.0, 0.0), math.pi)
        s_end = steve.walk(20, [(4.4, 2.0, 0.0), (4.4, 6.0, 0.0)])
        daisy = animals.make_cow("daisy")
        daisy.place(1, (2.5, 1.9, 0.0), math.pi)
        animals.follow(daisy, steve, 1, s_end + 10)
        cows = [animals.make_cow("c%d" % i) for i in range(4)]
        ev = animals.wander(cows, 1, 241, area, seed=seed, avoid=[steve, daisy])
        pair, _e, other = measure(animals, cows, 1, 300, area, avoid=[steve, daisy])
        worst, worst_pair = min(worst, other), min(worst_pair, pair)
        moved += sum(1 for e in ev.values() for x in e if x[0] == "walk")
    ok = worst >= -1e-6 and worst_pair >= -1e-6 and moved > 0
    good &= ok
    print("%s avoid=[steve, the cow that follows him]: four wandering cows keep %+.3f over their width from both and "
          "%+.3f from each other (%d walks)" % ("ok  " if ok else "FAIL", worst, worst_pair, moved))

    # ---- an area too narrow to turn in: the old rule, nobody leaves it
    quick.reset()
    cows = [animals.make_cow("c%d" % i) for i in range(2)]
    lane = (0.0, 0.0, 3.0, 12.0)
    ev = animals.wander(cows, 1, 481, lane, seed=1)
    pair, edge, _o = measure(animals, cows, 1, 540, lane)
    ok = pair >= -1e-6 and edge >= -1e-6
    good &= ok
    print("%s two cows in a lane 3 blocks wide for 20 s: margins %+.3f / %+.3f, walks %s" % (
        "ok  " if ok else "FAIL", pair, edge, [sum(1 for x in e if x[0] == "walk") for e in ev.values()]))
    print("pens:", "all passed" if good else "FAILED")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
