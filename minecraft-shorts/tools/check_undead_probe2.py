"""Checker: second numeric probe of engine/undead.py (round trips, villager death, timing rules). No rendering."""
import math

import bpy


def main():
    from engine import quick
    scene = quick.reset()
    quick.setup(scene)
    cam = quick.camera(scene, (0.0, -8.0, 1.5), (0.0, 0.0, 1.0))
    from engine import characters as ch
    from engine import fx, mobs
    from engine import undead as U

    def vis(c, f):
        scene.frame_set(int(f))
        own = [o for o in c.objects() if o.type == "MESH" and not o.hide_render]
        st = c.__dict__.get(U._STATE) or {}
        red = [t for t in st.get("twins", {}).values() if not t.hide_render]
        return len(own), len(red)

    def say(label, ok, detail=""):
        print("%s %-74s %s" % ("ok  " if ok else "BAD ", label, detail))

    # ---- the trading hall loop: infect, cure, infect again, cure again with the SAME two characters
    v = fx.make_job_villager("trader", ("librarian", "none"))
    v.place(1, (0.0, 0.0, 0.0), 0.0)
    v.show(1, True)
    zv = U.make_zombie_villager("trader_z", "librarian")
    zv.show(1, True)
    z = U.make_zombie("z")
    z.place(1, (0.0, -1.25, 0.0), math.radians(180))
    z.show(1, True)
    z.attack(100)
    U.infect(v, zv, 100, attacker=z, max_back=0.0)
    U.cure(zv, v, 200, 260, camera=cam)
    row1 = [(f, vis(v, f)[0] > 0, vis(zv, f)[0] > 0) for f in (50, 150, 250, 300)]
    z.attack(400)
    U.infect(v, zv, 400, attacker=z, max_back=0.0)
    U.cure(zv, v, 500, 560, camera=cam)
    row2 = [(f, vis(v, f)[0] > 0, vis(zv, f)[0] > 0) for f in (50, 150, 250, 300, 450, 600)]
    want = [(50, True, False), (150, False, True), (250, False, True), (300, True, False), (450, False, True), (600, True, False)]
    say("one round (villager, zombie villager) at 50/150/250/300", row1 == want[:4], str(row1))
    say("SECOND round with the same two characters keeps the first round", row2 == want, str(row2))

    # ---- a villager killed without conversion (Easy / Normal)
    k = ch.make_villager("victim", "farmer")
    k.place(1, (5.0, 0.0, 0.0), 0.0)
    k.show(1, True)
    gone = U.die(k, 40, camera=cam, attacker=(5.0, -1.0, 0.0))
    scene.frame_set(40 + 17)
    say("villager death: tips to 90 degrees, red, gone at +24", abs(math.degrees(k.root.rotation_euler[1]) - 90.0) < 0.5 and vis(k, 50) == (0, 5) and vis(k, gone) == (0, 0),
        "%.1f deg %s %s" % (math.degrees(k.root.rotation_euler[1]), vis(k, 50), vis(k, gone)))
    k.place(gone + 20, (5.0, 3.0, 0.0), 0.0)
    scene.frame_set(gone + 21)
    say("villager: place() after the death brings him back upright", vis(k, gone + 21) == (5, 0) and abs(k.root.rotation_euler[1]) < 1e-6, "%s tilt %.2f" % (vis(k, gone + 21), k.root.rotation_euler[1]))

    # ---- the game's own rhythm: a blow every 24 frames, the victim not walking back
    w = ch.make_villager("punchbag", "none")
    w.place(1, (10.0, 0.0, 0.0), 0.0)
    for i in range(3):
        U.hurt(w, 20 + 24 * i, attacker=(10.0, -1.2, 0.0))
    ys = [round(w.pos_at(f).y, 2) for f in (19, 43, 67, 100)]
    zs = max(w.pos_at(20 + q * 0.5).z for q in range(160))
    say("three blows 24 frames apart: 1.99 blocks each, apex stays 0.965", abs(ys[-1] - 5.97) < 0.05 and zs < 1.0, "y %s apex %.3f" % (ys, zs))
    w2 = ch.make_villager("punchbag2", "none")
    w2.place(1, (14.0, 0.0, 0.0), 0.0)
    U.hurt(w2, 20, attacker=(14.0, -1.2, 0.0))
    U.hurt(w2, 32, attacker=(14.0, -1.2, 0.0))
    zs = max(w2.pos_at(20 + q * 0.5).z for q in range(100))
    say("second blow exactly 12 frames (10 ticks) later: no double height", zs < 1.0, "apex %.3f" % zs)

    # ---- attack end frame and when the arms really move
    a = U.make_zombie("timing")
    a.place(1, (20.0, 0.0, 0.0), 0.0)
    end = a.attack(50)
    vals = []
    for f in (50, 51, 52, 53, 55, 57, 58, 59, 60):
        scene.frame_set(f)
        vals.append((f, round(math.degrees(a.arm_r.rotation_euler[0] - a.arm_bob(f)[0]), 1)))
    print("     attack(50) returns %d; arm pitch by frame: %s" % (end, vals))

    # ---- sizes of what is drawn against the game's numbers
    for name, c, want_h in (("zombie", U.make_zombie("m1"), 2.0), ("husk", U.make_zombie("m2", variant="husk"), 2.125),
                            ("baby zombie", U.make_zombie("m3", baby=True), 0.9375), ("zombie villager", U.make_zombie_villager("m4", "farmer"), 2.125),
                            ("baby zombie villager", U.make_zombie_villager("m5", baby=True), 1.0)):
        c.place(1, (30.0, 0.0, 0.0), 0.0)
        scene.frame_set(1)
        bpy.context.view_layer.update()
        pts = [ob.matrix_world @ vv.co for ob in c.objects() if ob.type == "MESH" for vv in ob.data.vertices]
        lo, hi = min(p.z for p in pts), max(p.z for p in pts)
        wx = max(p.x for p in pts) - min(p.x for p in pts)
        print("     %-22s drawn z %.4f .. %.4f (model top %.4f), width %.3f, eye %.3f" % (name, lo, hi, want_h, wx, c.eye_height))
        c.show(1, False)

    # ---- walk: sole positions through a corner (does the stance foot skate while turning?)
    c = U.make_zombie("corner")
    c.place(1, (40.0, 0.0, 0.0), math.radians(90))
    end = c.walk(1, [(40.0, 0.0, 0.0), (44.0, 0.0, 0.0), (44.0, 4.0, 0.0)])
    worst, prev = 0.0, None
    f = 30.0
    while f < 56.0:
        scene.frame_set(int(f), subframe=f - int(f))
        bpy.context.view_layer.update()
        soles = [leg.matrix_world @ __import__("mathutils").Vector((0.0, 0.0, -c.leg_len)) for leg in (c.leg_l, c.leg_r)]
        if prev is not None:
            worst = max(worst, min((soles[i] - prev[i]).length for i in (0, 1)))
        prev = soles
        f += 0.25
    print("     corner: the slower sole moves up to %.3f block per quarter frame while turning (0 = planted)" % worst)


if __name__ == "__main__":
    main()
