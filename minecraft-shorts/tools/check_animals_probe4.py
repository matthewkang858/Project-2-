"""Independent checker: wander() over many seeds, a mixed herd, a minute-long pen, and the docstring's pen sizes.
Run:  $BPY -m tools.check_animals_probe4"""
import sys
import time


def main():
    from engine import animals, quick

    good = True
    worst = {}
    t0 = time.time()
    for seed in range(12):
        quick.reset()
        cows = [animals.make_cow("c%d" % i) for i in range(5)] + [animals.make_cow("k", baby=True)]
        hens = [animals.make_chicken("h%d" % i) for i in range(6)] + [animals.make_chicken("q%d" % i, baby=True) for i in range(2)]
        for kind, herd, cells in (("cows 10x10", cows, (0, 0, 9, 9)), ("hens 8x9", hens, (20, 0, 27, 8))):
            area = animals.pen_area(*cells)
            ev = animals.wander(herd, 1, 121, area, seed=seed)
            ev2 = animals.wander(herd, 121, 241, area, seed=seed + 100, place=False)
            gap, edge = animals.pen_report(herd, 1, 300, area)
            walks = sum(1 for e in list(ev.values()) + list(ev2.values()) for x in e if x[0] == "walk")
            idle = [n for n in ev if not any(x[0] == "walk" for x in ev[n] + ev2[n])]
            w = worst.setdefault(kind, [9.0, 9.0, 999, 0])
            w[0], w[1], w[2], w[3] = min(w[0], gap), min(w[1], edge), min(w[2], walks), max(w[3], len(idle))
    for kind, (gap, edge, walks, idle) in worst.items():
        width = 0.75 if kind.startswith("cows") else 0.25          # the narrowest body in the herd sets its own room
        ok = gap >= 0.24 and edge >= 0.24 and walks >= 4
        good &= ok
        print("%s %s, 12 seeds x 10 s (two calls, the second place=False): smallest body gap %.2f, from the fence %.2f, "
              "fewest walks %d, most animals that never walk %d" % ("ok  " if ok else "FAIL", kind, gap, edge, walks, idle))
    print("   (%.1f s)" % (time.time() - t0))
    # a minute in one call
    quick.reset()
    cows = [animals.make_cow("c%d" % i) for i in range(6)]
    area = animals.pen_area(0, 0, 9, 9)
    t0 = time.time()
    ev = animals.wander(cows, 1, 1441, area, seed=3)
    t1 = time.time() - t0
    gap, edge = animals.pen_report(cows, 1, 1500, area, step=2)
    walks = [sum(1 for x in e if x[0] == "walk") for e in ev.values()]
    ok = gap >= 0.74 and edge >= 0.74 and min(walks) >= 5 and t1 < 60
    good &= ok
    print("%s six cows for 60 s in one call: keyed in %.1f s, walks per cow %s, gap %.2f, edge %.2f" % (
        "ok  " if ok else "FAIL", t1, walks, gap, edge))
    # the docstring: 'a believable pen of 4 to 6 animals for 5 seconds with one call' - how many move in 5 s?
    quiet = 0
    for seed in range(12):
        quick.reset()
        cows = [animals.make_cow("c%d" % i) for i in range(5)]
        ev = animals.wander(cows, 1, 121, area, seed=seed)
        n = sum(1 for e in ev.values() if any(x[0] == "walk" for x in e))
        quiet += n <= 1
    print("     five cows, 5 s, 12 seeds: in %d of 12 pens at most one cow takes a step" % quiet)
    return good


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
