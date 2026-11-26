"""Checker: tools/palette_check on the probe film's rendered frames (tools/check_underground_probe.py).

    $BPY -m tools.check_underground_palette SKY SHOT:OFF ...      (the PNGs must exist: out/test/check_underground_*)
"""
import os
import sys


def main(argv):
    sys.modules.setdefault("films._check_underground_probe", __import__("tools.check_underground_probe",
                                                                         fromlist=["x"]))
    import render as R
    from tools import palette_check as pc
    from tools import check_underground_probe as P

    sky = argv[0]
    ses = R.Session("_check_underground_probe", sky=sky)
    ses.configure((540, 960), 16, 2, True)
    for a in argv[1:]:
        n, off = a.split(":")
        shot = next(s for s in ses.film.shots if s.name == n)
        f = shot.frame_start + int(off)
        ses.film.goto(f)
        path = os.path.join(P.ROOT, "out", "test", "check_underground_%s_%03d.png" % (n, int(off)))
        rec = pc.probe(ses.scene)
        heroes = [ob for _l, ob in P.HEROES.get(n, [])]
        rep = pc.evaluate(rec, path, heroes=heroes)
        pc.print_report("%s_%s" % (n, off), rep)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
