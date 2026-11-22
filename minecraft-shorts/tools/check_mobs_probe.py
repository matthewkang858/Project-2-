"""Independent checker probe for engine/mobs.py (numbers only; the renders are in tools/check_mobs_film.py).

Run:  $BPY -m tools.check_mobs_probe
"""
import math
import sys

import bpy
import numpy as np
from mathutils import Vector


def counts():
    return {k: len(getattr(bpy.data, k)) for k in ("objects", "meshes", "materials", "images", "actions", "collections")}


def ev(scene, f):
    w = int(math.floor(f))
    scene.frame_set(w, subframe=float(f) - w)
    bpy.context.view_layer.update()


def lowest(ob):
    """World-space lowest point and its y / x centre of a mesh object."""
    pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
    z = min(p.z for p in pts)
    sole = [p for p in pts if p.z < z + 1e-4]
    c = sum(sole, Vector()) / len(sole)
    return z, c


def main():
    from engine import quick

    scene = quick.reset()
    before = counts()
    from engine import mobs
    after = counts()
    print("IMPORT side effects:", {k: (before[k], after[k]) for k in before if before[k] != after[k]} or "none")
    from engine import characters as ch

    TICK = 1.2
    problems = []

    def bad(msg):
        problems.append(msg)
        print("  !!", msg)

    # ------------------------------------------------------------------ signs of the gait against the game
    g = mobs.make_iron_golem("s")
    g.place(1, (0, 0, 0), 0.0)                       # faces -Y; its right is -X
    g.walk(1, [(0, 0, 0), (0, -13, 0)], gait="vanilla", ramp=0)
    # after 0.5 animation units (0.125 block): wave(0.5) > 0 -> right leg forward (-Y), right arm back, roll to the right
    f = 1 + 0.125 / (mobs.WALK_SPEED / 24.0)
    ev(scene, f)
    zr, cr = lowest(g.leg_r)
    zl, cl = lowest(g.leg_l)
    root = g.root.matrix_world.translation
    head = g.head.matrix_world.translation
    print("vanilla, pos 0.5: right sole y - root y = %.3f, left = %.3f (negative = forward); head x - root x = %.3f"
          % (cr.y - root.y, cl.y - root.y, head.x - root.x))
    print("  leg_r x %.3f leg_l x %.3f (right must be -X)" % (cr.x, cl.x))
    if not (cr.y - root.y < 0 < cl.y - root.y):
        bad("right leg must be forward at walk position 0.5")
    ar = g.arm_r.rotation_euler.x
    al = g.arm_l.rotation_euler.x
    s = mobs.WALK_SPEED / 5.0
    w = mobs.triangle_wave(0.5, 13.0)
    print("  arms: r %.4f (game %.4f)  l %.4f (game %.4f)" % (ar, (-0.2 + 1.5 * w) * s, al, (-0.2 - 1.5 * w) * s))
    # arm world direction: the right arm must be BEHIND (+Y) when the right leg is forward
    zr2, car = lowest(g.arm_r)
    zl2, cal = lowest(g.arm_l)
    print("  right fist y - root y = %.3f, left fist = %.3f" % (car.y - root.y, cal.y - root.y))
    if not (car.y - root.y > cal.y - root.y):
        bad("right arm must be back when the right leg is forward")
    if not (car.x < 0 < cal.x):
        bad("arm_r must be on the golem's right (-X at yaw 0)")
    # roll: game = 6.5 deg * tri(pos + 6) about +Z(back) with + = lean LEFT. tri(6.5) = -1 -> lean RIGHT (-X)
    if not head.x - root.x < -0.05:
        bad("at walk position 0.5 the game leans the golem to ITS RIGHT (toward the forward right leg)")
    print("  roll now %.2f deg; ground contact: lowest sole z = %.4f / %.4f" % (math.degrees(g.root.rotation_euler.y), zr, zl))

    # how far do the soles dip under / lift off the ground during the planted walk (roll about the root = feet centre)
    g2 = mobs.make_iron_golem("p")
    g2.place(1, (5, 0, -0.0625), 0.0)
    e2 = g2.walk(1, [(5, 0, -0.0625), (5, -6, -0.0625)])
    lo, hi = 9, -9
    slide = []
    track = {}
    for fr in np.arange(1, e2 + 0.001, 0.25):
        ev(scene, fr)
        zs = []
        for name, leg in (("r", g2.leg_r), ("l", g2.leg_l)):
            z, c = lowest(leg)
            zs.append(z + 0.0625)
            track.setdefault(name, []).append((fr, c.y, z + 0.0625))
        lo, hi = min(lo, min(zs)), max(hi, min(zs))
    print("planted walk 6 blocks in %d frames: lowest sole point ranges %.4f .. %.4f above the path (negative = sunk)"
          % (e2 - 1, lo, hi))
    # stance foot: the lower one; measure its y drift while it is the lower one
    worst = 0.0
    for name in ("r", "l"):
        other = "l" if name == "r" else "r"
        run = []
        for (fr, y, z), (_f, _y, z2) in zip(track[name], track[other]):
            if z < z2 - 1e-4:
                run.append(y)
            else:
                if len(run) > 8:
                    worst = max(worst, max(run) - min(run))
                run = []
    print("  world drift of the LOWER (stance) sole while it is the lower one: %.4f block" % worst)
    info = g2.last_walk
    print("  last_walk", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in info.items()})

    # ------------------------------------------------------------------ a cut in the middle of a walk
    g3 = mobs.make_iron_golem("c")
    g3.place(1, (10, 0, 0), 0.0)
    e3 = g3.walk(1, [(10, 0, 0), (10, -8, 0)])
    g3.offer_flower(30, ease=8)
    cut = 61
    ev(scene, cut - 1 + 0.5)
    pre = (g3.root.location.copy(), g3.root.rotation_euler.y, g3.leg_r.rotation_euler.x, g3.arm_r.rotation_euler.x,
           bool(g3.flower.hide_render))
    g3.place(cut, (20, 5, 0), math.radians(90))
    ev(scene, cut - 1 + 0.5)
    post = (g3.root.location.copy(), g3.root.rotation_euler.y, g3.leg_r.rotation_euler.x, g3.arm_r.rotation_euler.x,
            bool(g3.flower.hide_render))
    d = max((pre[0] - post[0]).length, abs(pre[1] - post[1]), abs(pre[2] - post[2]), abs(pre[3] - post[3]))
    print("cut at %d: change seen at the END of frame %d's exposure: %.6f; flower hidden %s -> %s" % (cut, cut - 1, d, pre[4], post[4]))
    if d > 1e-3 or pre[4] != post[4]:
        bad("place() changes the frame before the cut")
    ev(scene, cut)
    print("  at the cut: loc %s yaw %.1f roll %.4f legs %.4f/%.4f arms %.4f/%.4f flower hidden %s"
          % (tuple(round(c, 3) for c in g3.root.location), math.degrees(g3.root.rotation_euler.z), g3.root.rotation_euler.y,
             g3.leg_r.rotation_euler.x, g3.leg_l.rotation_euler.x, g3.arm_r.rotation_euler.x, g3.arm_l.rotation_euler.x,
             g3.flower.hide_render))
    if (g3.root.location - Vector((20, 5, 0))).length > 1e-5 or abs(g3.arm_r.rotation_euler.x) > 1e-6 or not g3.flower.hide_render:
        bad("place() must reset the pose and hide the flower")
    ev(scene, cut + 40)
    if (g3.root.location - Vector((20, 5, 0))).length > 1e-5 or abs(g3.arm_r.rotation_euler.x) > 1e-6 \
            or abs(g3.root.rotation_euler.y) > 1e-6 or abs(g3.leg_l.rotation_euler.x) > 1e-6:
        bad("the old walk / offer leaks past a place(): loc %s arm %.3f roll %.3f"
            % (tuple(g3.root.location), g3.arm_r.rotation_euler.x, g3.root.rotation_euler.y))

    # ------------------------------------------------------------------ calls made twice / at frame 1
    g4 = mobs.make_iron_golem("t")
    g4.place(1, (0, 10, 0), 0.0)
    g4.place(1, (1, 10, 0), 0.5)
    g4.offer_flower(1, ease=0)
    g4.offer_flower(1, ease=0)
    g4.look_at(1, (1, 5, 0.6), ease=0)
    g4.look_at(1, (1, 5, 0.6), ease=0)
    ev(scene, 1)
    print("twice at frame 1: loc %s yaw %.2f arm_r %.4f flower hidden %s head pitch %.3f"
          % (tuple(round(c, 3) for c in g4.root.location), g4.root.rotation_euler.z, g4.arm_r.rotation_euler.x,
             g4.flower.hide_render, g4.head.rotation_euler.x))
    if abs(g4.arm_r.rotation_euler.x - (-0.8 + 0.025 * mobs.triangle_wave(400 % 70, 70))) > 1e-5 or g4.flower.hide_render:
        bad("offer_flower twice at frame 1")
    ev(scene, 0)
    print("  frame 0: flower hidden %s, arm_r %.3f" % (g4.flower.hide_render, g4.arm_r.rotation_euler.x))
    # walk while offering, then stop offering
    e4 = g4.walk(20, [(1, 4, 0)], from_current=True)
    ev(scene, 20 + (e4 - 20) / 2.0)
    print("  walking while offering (frame %.0f): arm_r %.4f arm_l %.4f, flower hidden %s"
          % (20 + (e4 - 20) / 2.0, g4.arm_r.rotation_euler.x, g4.arm_l.rotation_euler.x, g4.flower.hide_render))
    if abs(g4.arm_r.rotation_euler.x + 0.8) > 0.03 or abs(g4.arm_l.rotation_euler.x) > 1e-6:
        bad("the offer pose must survive a walk")
    g4.offer_flower(e4 + 10, on=False, ease=8)
    ev(scene, e4 + 30)
    if abs(g4.arm_r.rotation_euler.x) > 1e-6 or not g4.flower.hide_render:
        bad("offer_flower(on=False) must lower the arm and hide the flower")
    # the offer must not run on after its 400 ticks?  (the game ends it; here it holds: report)
    g5 = mobs.make_iron_golem("u")
    g5.place(1, (0, 20, 0), 0.0)
    g5.offer_flower(10, ease=8, ticks=40)
    for fr in (10 + 40 * TICK - 1, 10 + 40 * TICK + 5, 10 + 40 * TICK + 60):
        ev(scene, fr)
        print("  ticks=40: frame %.0f arm_r %.4f flower hidden %s" % (fr, g5.arm_r.rotation_euler.x, g5.flower.hide_render))

    # offer in the MIDDLE of a walk (arms are swinging)
    g6 = mobs.make_iron_golem("m")
    g6.place(1, (0, 30, 0), 0.0)
    e6 = g6.walk(1, [(0, 30, 0), (0, 22, 0)])
    g6.offer_flower(60, ease=8)
    vals = []
    for fr in np.arange(58, e6 + 4, 0.5):
        ev(scene, fr)
        vals.append((fr, g6.arm_r.rotation_euler.x, g6.arm_l.rotation_euler.x))
    jump_r = max(abs(b[1] - a[1]) for a, b in zip(vals, vals[1:]))
    jump_l = max(abs(b[2] - a[2]) for a, b in zip(vals, vals[1:]))
    print("offer during a walk: largest half-frame step arm_r %.4f arm_l %.4f rad; at the end arm_r %.4f arm_l %.4f"
          % (jump_r, jump_l, vals[-1][1], vals[-1][2]))
    if jump_r > 0.12 or jump_l > 0.12:
        bad("arm pops when the offer starts during a walk")
    if abs(vals[-1][1] + 0.8) > 0.03 or abs(vals[-1][2]) > 1e-6:
        bad("offer during a walk does not end in the offer pose")

    # two walks one after the other, and a walk that starts where a place() put it on the SAME frame as a look_at
    g7 = mobs.make_iron_golem("w")
    g7.place(1, (0, 40, 0), 0.0)
    a = g7.walk(1, [(0, 40, 0), (0, 37, 0)])
    b = g7.walk(a, [(3, 37, 0)], from_current=True)
    c = g7.walk(b + 12, [(3, 40, 0)], from_current=True, gait="vanilla")
    print("three walks: end frames", a, b, c)
    prev = None
    worst_step = 0.0
    worst_yaw = 0.0
    for fr in np.arange(1, c + 1, 0.5):
        ev(scene, fr)
        cur = (g7.root.location.copy(), g7.root.rotation_euler.z, g7.leg_r.rotation_euler.x)
        if prev is not None:
            worst_step = max(worst_step, (cur[0] - prev[0]).length)
            worst_yaw = max(worst_yaw, abs(cur[1] - prev[1]))
        prev = cur
    print("  largest half-frame move %.4f block (cruise is %.4f), largest half-frame yaw step %.2f deg"
          % (worst_step, mobs.WALK_SPEED / 48.0, math.degrees(worst_yaw)))
    if worst_step > 0.05:
        bad("position pops between consecutive walks")

    # ------------------------------------------------------------------ head limits against a low target (a baby)
    g8 = mobs.make_iron_golem("h")
    kid = ch.make_villager("kid", "none", child=True)
    g8.place(1, (0, 50, 0), 0.0)
    kid.place(1, (-0.62, 50 - 2.15, 0), math.pi)
    g8.look_at(1, kid, ease=0)
    ev(scene, 1)
    print("look at the baby 2.15 in front: head yaw %.1f pitch %.1f deg (limits 75 / 40)"
          % (math.degrees(g8.head.rotation_euler.z), math.degrees(g8.head.rotation_euler.x)))

    # ------------------------------------------------------------------ dropped items
    a = mobs.make_dropped_item("poppy")
    b = mobs.make_dropped_item("poppy")
    print("two poppies:", a.name, b.name, "| shared mesh:", a.sprite.data is b.sprite.data, "| sprite objects distinct:", a.sprite is not b.sprite)
    a.drop(1, (0, 60, -0.0625))
    a.animate(1, 73)
    for fr in (0, 1, 2):
        ev(scene, fr)
        print("  drop at frame 1: frame %d hidden %s root z %.3f" % (fr, a.sprite.hide_render, a.root.location.z))
    # motion blur at the drop: where is the root during frame 0's exposure and frame 1's
    for fr in (0.5, 0.75, 1.0, 1.5):
        ev(scene, fr)
        print("    f %.2f root %s spinner z %.4f rot %.4f" % (fr, tuple(round(c, 3) for c in a.root.location),
                                                              a.spinner.location.z, a.spinner.rotation_euler.z))
    # drop twice (a correction by the director)
    b.drop(10, (2, 60, 0), seed=1)
    b.drop(10, (3, 60, 0), seed=1)
    b.animate(10, 90)
    ev(scene, 9)
    h9 = b.sprite.hide_render
    ev(scene, 10)
    print("  drop twice at frame 10: hidden at 9 %s, at 10 %s, root %s" % (h9, b.sprite.hide_render, tuple(round(c, 3) for c in b.root.location)))
    if not h9 or b.sprite.hide_render or abs(b.root.location.x - 3) > 1e-4:
        bad("drop() twice")
    # animate twice with overlapping ranges, then past the end
    b.animate(10, 90)
    b.animate(60, 150)
    worst = 0.0
    for fr in np.arange(10, 150, 0.5):
        ev(scene, fr)
        age = (fr - 10) / TICK
        worst = max(worst, abs(b.spinner.rotation_euler.z - (age / 20.0 + b.phase)),
                    abs(b.spinner.location.z - (b.hover + 0.1 + 0.1 * math.sin(age / 10.0 + b.phase))))
    print("  animate() twice, overlapping: worst error %.5f" % worst)
    if worst > 1e-3:
        bad("animate() called twice breaks the bob / spin")
    ev(scene, 150)
    r150 = b.spinner.rotation_euler.z
    ev(scene, 200)
    print("  after animate()'s last frame the item is frozen: spin moved %.4f rad in 50 frames" % (b.spinner.rotation_euler.z - r150))
    # where is the item before animate()'s first frame when animate starts later than the drop?
    c = mobs.make_dropped_item("iron_ingot")
    rest = c.drop(20, (5, 60, 0), rest=True)
    c.animate(rest, 120)                                      # a director who animates "once it has landed"
    zs = []
    for fr in np.arange(19.5, rest + 2, 0.25):
        ev(scene, fr)
        zs.append((fr, c.spinner.location.z, c.spinner.rotation_euler.z))
    jz = max(abs(q[1] - p[1]) for p, q in zip(zs, zs[1:]))
    jr = max(abs(q[2] - p[2]) for p, q in zip(zs, zs[1:]))
    print("  drop(20) + animate(rest=%d, ..): largest quarter-frame jump of the bob %.4f block, of the spin %.4f rad" % (rest, jz, jr))
    if jz > 0.02 or jr > 0.1:
        bad("animate() starting after the drop pops the item (bob %.3f, spin %.3f)" % (jz, jr))
    # place + animate at frame 1, nothing keyed before
    d = mobs.make_dropped_item("poppy", name="placed")
    d.place(1, (7, 60, -0.0625))
    d.animate(1, 49)
    ev(scene, 1)
    zlow = min((d.sprite.matrix_world @ v.co).z for v in d.sprite.data.vertices) + 0.0625
    print("  placed poppy at frame 1: hidden %s, lowest texel %.4f above the path (bob %.3f)" % (d.sprite.hide_render, zlow, d.bob_at(1)))

    # ------------------------------------------------------------------ a second golem with the same name
    x = mobs.make_iron_golem("golem")
    y = mobs.make_iron_golem("golem")
    x.place(1, (0, 70, 0))
    y.place(1, (3, 70, 0))
    y.offer_flower(1, ease=0)
    ev(scene, 1)
    print("two golems called 'golem':", x.root.name, y.root.name, "| flower hidden", x.flower.hide_render, y.flower.hide_render,
          "| distance %.2f" % (x.root.matrix_world.translation - y.root.matrix_world.translation).length)
    if x.flower.hide_render is False or y.flower.hide_render is True:
        bad("second golem of the same name shares state with the first")
    # crack on one must not change the other
    mats_before = x.head.data.materials[0].name
    y.crack("high")
    print("  crack on the second: materials", mats_before, "->", x.head.data.materials[0].name, "/", y.head.data.materials[0].name)
    if x.head.data.materials[0].name != mats_before:
        bad("crack() leaks to another golem")

    # ------------------------------------------------------------------ inherited gestures still work on the golem rig
    z = mobs.make_iron_golem("gest")
    z.place(1, (0, 80, 0))
    for name, call in (("nod", lambda: z.nod(10)), ("shake", lambda: z.shake(30)), ("flinch", lambda: z.flinch(60)),
                       ("shiver", lambda: z.shiver(80, 110)), ("raise_arm", lambda: z.raise_arm(120)),
                       ("idle", lambda: z.idle(140, 260, seed=2)), ("turn", lambda: z.turn(270, 1.0)),
                       ("face", lambda: z.face(290, (5, 80, 0))), ("track", lambda: z.track(300, 340, kid)),
                       ("attack", lambda: z.attack(350)), ("hold", lambda: z.hold(mobs.mc.item_object("iron_ingot"))),
                       ("lie_down", lambda: z.lie_down(400, (0, 85, 0.5625), 0.0))):
        try:
            call()
            print("  %-9s ok" % name)
        except Exception as exc:                                  # noqa: BLE001
            bad("%s() raises %r" % (name, exc))

    print()
    print("PROBLEMS: %d" % len(problems))
    for p in problems:
        print(" -", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
