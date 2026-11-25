"""Independent checker's probe 4 of engine/piglins.py: the inherited Character API and odd calls. Numbers only.

Run:  $BPY -m tools.check_piglins_probe4
"""
import math
import sys
import traceback

import bpy
from mathutils import Vector


def main():
    from engine import quick

    scene = quick.reset()
    from engine import characters as ch
    from engine import piglins

    def attempt(label, fn):
        try:
            r = fn()
            print("   ok   %-46s -> %s" % (label, r if not isinstance(r, bpy.types.Object) else r.name))
            return r
        except Exception as err:                                # noqa
            print("   FAIL %-46s -> %s: %s" % (label, type(err).__name__, str(err)[:140]))
            return None

    p = piglins.make_piglin("p")
    b = piglins.make_piglin("b", "piglin_brute")
    k = piglins.make_piglin("k", baby=True)
    steve = ch.make_player("steve")
    steve.place(1, (0, -3, 0), math.pi)
    for q in (p, b, k):
        print(q)
        q.place(1, (0, 0, 0), 0.0)
        attempt("nod", lambda: q.nod(5))
        attempt("shake", lambda: q.shake(20))
        attempt("flinch", lambda: q.flinch(40))
        attempt("raise_arm", lambda: q.raise_arm(60))
        attempt("track", lambda: q.track(70, 100, steve))
        attempt("face", lambda: q.face(100, (3, 3, 0)))
        attempt("turn", lambda: q.turn(110, 1.0))
        attempt("idle", lambda: q.idle(120, 200, seed=1))
        attempt("walk 3 frames (0.2 block)", lambda: q.walk(200, [(0.2, 0, 0)], from_current=True))
        attempt("walk to where it stands", lambda: q.walk(210, [q.pos_at(210)], from_current=True))
        attempt("swing_arm r", lambda: q.swing_arm(220))
        attempt("swing_arm l", lambda: q.swing_arm(230, side="l"))
        attempt("hold(None)", lambda: q.hold(None, frame=240))
        attempt("hold('gold_ingot', off)", lambda: q.hold("gold_ingot", frame=250, hand="off"))
        attempt("hold('emerald', main)", lambda: q.hold("emerald", frame=260))
        attempt("item_point main", lambda: tuple(round(c, 2) for c in q.item_point(262, "main")))
        attempt("admire", lambda: q.admire(270, ticks=20))
        attempt("look_at during admire", lambda: q.look_at(280, steve))
        attempt("dance", lambda: q.dance(300, 340))
        attempt("aggro", lambda: q.aggro(350))
        attempt("attack", lambda: q.attack(360))
        attempt("aim_crossbow", lambda: q.aim_crossbow(380))
        attempt("hurt (no source)", lambda: q.hurt(400))
        attempt("hurt (source, wall 0.3 behind)", lambda: q.hurt(430, source=steve, max_back=0.3))
        attempt("lie_down", lambda: q.lie_down(470, (0, 0, 0.5625), 0.0))
        attempt("place after lie_down", lambda: q.place(480, (0, 0, 0)))
        attempt("die (no poof)", lambda: q.die(490, source=steve, poof_particles=False))
        attempt("show after death", lambda: q.show(530, True))
        scene.frame_set(531)
        print("        after die + show(True): visible meshes", sum(1 for o in q.objects() if o.type == "MESH" and not o.hide_render))
        attempt("walk while gone", lambda: q.walk(540, [(2, 0, 0)], from_current=True))
        attempt("place brings it back", lambda: q.place(600, (0, 0, 0)))
        scene.frame_set(600)
        on = [o.name for o in q.objects() if o.type == "MESH" and not o.hide_render]
        print("        at 600: %d meshes visible, items %s, roll %.2f" % (len(on), [n for n in on if "gold" in n or "emerald" in n or "cross" in n],
                                                                    q.root.rotation_euler.y))
    attempt("baby brute", lambda: piglins.make_piglin("x", "brute", baby=True))
    attempt("unknown kind", lambda: piglins.make_piglin("x", "zombified"))
    attempt("baby with armor", lambda: piglins.make_piglin("x", baby=True, armor=("helmet",)))
    attempt("brute with armor", lambda: piglins.make_piglin("xb", "brute", armor=("helmet",)).armor)
    attempt("unknown armor piece", lambda: piglins.make_piglin("xa", armor=("hat",)))
    attempt("unknown weapon id", lambda: piglins.make_piglin("xw", weapon="no_such_item"))
    attempt("weapon golden_spear", lambda: piglins.make_piglin("xs", weapon="golden_spear").weapon)
    attempt("weapon gold_block (a block)", lambda: piglins.make_piglin("xg", weapon="gold_block").weapon)
    # two idle piglins: do their ears move in step?
    a1, a2 = piglins.make_piglin("ear_a"), piglins.make_piglin("ear_b")
    for q in (a1, a2):
        q.place(1, (0, 0, 0))
        q.flop_ears(1, 200)
    print("   ears of two piglins at frame 100: %.3f vs %.3f" % (ch._val(a1.ear_r, "rotation_euler", 1, 100), ch._val(a2.ear_r, "rotation_euler", 1, 100)))
    # a piglin that stands with no idle: its ears
    a3 = piglins.make_piglin("ear_c")
    a3.place(1, (0, 0, 0))
    print("   no idle / flop_ears: ear keys", len(ch.read_keys(a3.ear_r, "rotation_euler", 1)), "(the ears hold still, as documented)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
