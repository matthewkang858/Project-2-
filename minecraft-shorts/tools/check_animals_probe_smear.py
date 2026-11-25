"""Independent checker: what moves how far inside one exposure ([f, f + 0.5]) anywhere in the probe film.
Run:  $BPY -m tools.check_animals_probe_smear"""
import math
import sys

import bpy
from mathutils import Vector


def main():
    from engine import animals, characters as ch, quick
    from tools.check_animals_probe_film import build

    scene = quick.reset()
    film, st, cast = build(scene)
    rows = []
    for s in film.shots:
        names = st.in_shot[s.name]
        for name in sorted(names):
            a = st.cast[name]
            if not isinstance(a, animals.Animal):
                continue
            for f in range(s.frame_start, s.frame_end + 1):
                if a.gone_at(f):
                    continue
                d = (a.pos_at(f + 0.5) - a.pos_at(f)).length
                yaw = abs(ch._wrap(a.yaw_at(f + 0.5) - a.yaw_at(f)))
                tip = abs(ch._val(a.root, "rotation_euler", 1, f + 0.5) - ch._val(a.root, "rotation_euler", 1, f))
                leg = max(abs(ch._val(o, "rotation_euler", 0, f + 0.5) - ch._val(o, "rotation_euler", 0, f)) for o in a.legs.values())
                head = max(abs(ch._val(a.head, "rotation_euler", i, f + 0.5) - ch._val(a.head, "rotation_euler", i, f)) for i in (0, 2))
                hips = abs(ch._val(a.hips, "location", 2, f + 0.5) - ch._val(a.hips, "location", 2, f))
                rows.append((s.name, f - s.frame_start, name, d, math.degrees(yaw), math.degrees(tip), math.degrees(leg),
                             math.degrees(head), hips))
    for label, idx, unit in (("root travel", 3, "blocks"), ("body yaw", 4, "deg"), ("death tip", 5, "deg"), ("leg swing", 6, "deg"),
                             ("head", 7, "deg"), ("hips height", 8, "blocks")):
        top = sorted(rows, key=lambda r: -r[idx])[:4]
        print("%-12s largest change inside one exposure: %s" % (label, ["%s+%d %s %.2f %s" % (r[0], r[1], r[2], r[idx], unit) for r in top]))
    # who is seen at a cut in mid-move: the first frame of each shot
    for s in film.shots[1:]:
        f = s.frame_start
        moved = []
        for name in sorted(st.in_shot[s.name] & st.in_shot[film.shots[film.shots.index(s) - 1].name]):
            a = st.cast[name]
            if isinstance(a, animals.Animal):
                j = (a.pos_at(f) - a.pos_at(f - 1)).length
                if j > 0.3:
                    moved.append((name, round(j, 2)))
        print("cut into %-5s: animals of the previous shot that jump at the cut: %s" % (s.name, moved))
    return 0


if __name__ == "__main__":
    sys.exit(main())
