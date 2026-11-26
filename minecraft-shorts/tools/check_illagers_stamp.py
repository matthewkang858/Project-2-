"""Checker: frame fingerprints (engine.stamp) of the illagers proof film.

  1. every picture change engine.illagers makes reaches the fingerprint, also when nothing else moves: the crossbow
     model switching (shoot), the banner leaving the captain's head (take_banner), the red flash (undead.hurt
     on a pillager), the pose cut into CROSSBOW_CHARGE, and the frame after each change equals the change frame;
  2. the same film gives the same fingerprints in two separate processes: run it twice and compare the DIGEST line.

    $BPY -m tools.check_illagers_stamp            (about 60-90 s; exit code 1 if a check of part 1 fails)
"""
import hashlib
import sys
import time

MARKS = {}


def _extra(st, v):
    """A still shot in which exactly one thing changes at a time."""
    import math

    from engine import illagers as il

    s = st.shot("stamp_still", 4.0)
    f = s.frame_start
    a = il.add_pillager(st, "sp_shooter", loaded=True)
    cap = il.add_pillager(st, "sp_cap", captain=True)
    b = il.add_pillager(st, "sp_hurt")
    c = il.add_pillager(st, "sp_charge")
    a.place(f, (-0.5, 30.5, 0.0), 0.0)
    cap.place(f, (0.5, 30.5, 0.0), 0.0)
    b.place(f, (1.5, 30.5, 0.0), 0.0)
    c.place(f, (-1.5, 30.5, 0.0), 0.0)
    a.shoot(f + 20)
    cap.take_banner(f + 40)
    il.undead._flash(b, f + 60, f + 72)                 # the red twin alone (hurt() also kicks the legs)
    c.charge(f + 80)
    st.use(s, a, cap, b, c)
    s.lens(35, 4.0)
    s.move((5.0, 26.5, 1.6), (0.0, 30.5, 1.4))
    st.lights(s, 1.0)
    MARKS.update(shoot=f + 20, banner=f + 40, flash=f + 60, flash_end=f + 72, charge=f + 80)
    return []


def main():
    from engine import illagers as il
    from engine import stamp

    t0 = time.time()
    scene, film, st, v, tiles = il.proof_film(["march", "death", "loot"], extra=_extra)
    print("built in %.1f s" % (time.time() - t0))
    fp = stamp.Fingerprinter(scene, film)
    ok = []

    def fpr(f):
        return fp.frame(f)["fp"]

    for name in ("shoot", "banner", "flash", "flash_end", "charge"):
        f = MARKS[name]
        a, b, c = fpr(f - 1), fpr(f), fpr(f + 1)
        if name == "charge":                             # the arms keep moving through the charge: only "changes"
            good = a != b
        else:
            good = a != b and b == c
        ok.append(good)
        print("%s %-10s frame %4d: %s | %s | %s" % ("ok  " if good else "FAIL", name, f, a[:12], b[:12], c[:12]))
    frames = sorted({t[2] for t in tiles} | {t[2] + 1 for t in tiles} | set(MARKS.values()))
    h = hashlib.sha256()
    for f in frames:
        d = fpr(f)
        h.update(("%d:%s;" % (f, d)).encode())
        print("FP %4d %s" % (f, d[:16]))
    print("DIGEST %s over %d frames (%.1f s)" % (h.hexdigest()[:24], len(frames), time.time() - t0))
    if not all(ok):
        sys.exit(1)


if __name__ == "__main__":
    main()
