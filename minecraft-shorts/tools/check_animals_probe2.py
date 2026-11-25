"""Independent checker's second numeric probe of engine/animals.py: blows in mid-air, the planted pair measured
without the module's own stance list, head aim, head speed, follow with a turning leader.

Run:  $BPY -m tools.check_animals_probe2
"""
import math
import sys

import bpy
import numpy as np
from mathutils import Vector


def main():
    from engine import animals, characters as ch, quick

    scene = quick.reset()
    res = []

    def expect(label, cond, detail=""):
        res.append(bool(cond))
        print("%s %s%s" % ("ok  " if cond else "FAIL", label, (": " + str(detail)) if detail != "" else ""))

    def ev(f):
        whole = int(math.floor(f))
        scene.frame_set(whole, subframe=float(f) - whole)
        bpy.context.view_layer.update()

    cam = quick.camera(scene, (6, -6, 2), (0, 0, 0.5))

    # ---- 1. a hen hit again 12 frames after the first blow (the game's earliest second hit: 10 ticks), still in the air
    hen = animals.make_chicken("hen")
    hen.place(1, (0, 0, 0), 0.0)
    up1 = hen.hurt(10, attacker=(0, -2, 0))
    z12 = hen.pos_at(22).z
    up2 = hen.hurt(22, attacker=(0, -2, 0))
    zs = [round(hen.pos_at(f).z, 3) for f in (22, 26, 30, up2, up2 + 30, up2 + 100)]
    expect("hen hit at 10 (stands at %d) and again at 22 while %.2f above the ground: heights at 22, 26, 30, %d, +30, +100 = %s"
           % (up1, z12, up2, zs), abs(zs[-1]) < 1e-6, "it never comes down: it stands in the air at z = %.2f for the rest of the film" % zs[-1])
    # the same with the killing blow
    hen2 = animals.make_chicken("hen2")
    hen2.place(1, (5, 0, 0), 0.0)
    hen2.hurt(10, attacker=(5, -2, 0))
    g = hen2.die(22, camera=cam, attacker=(5, -2, 0))
    zc = [round(hen2.pos_at(f).z, 3) for f in (22, 30, g - 1)]
    burst = hen2.bursts[-1]
    ev(g)
    pz = [q["object"].matrix_world.translation.z for q in burst.particles if q["first"] <= g < q["last"]]
    expect("hen killed at 22 while in the air: body height at 22, 30, %d = %s; the poof starts at heights %.2f-%.2f" % (
        g - 1, zc, min(pz), max(pz)), abs(zc[-1]) < 1e-6, "the corpse tips over and lies in the air")
    # a cow hit while it hops / a blow on the frame it 'stands again' is fine?
    cow = animals.make_cow("cow")
    cow.place(1, (10, 0, 0), 0.0)
    up = cow.hurt(10, attacker=(10, -2, 0))
    up_b = cow.hurt(up, attacker=(10, -2, 0))
    expect("cow hit again on the frame hurt() returned (%d): back on the ground afterwards (z %.3f at %d)" % (
        up, cow.pos_at(up_b + 30).z, up_b + 30), abs(cow.pos_at(up_b + 30).z) < 1e-6)

    # ---- 2. the planted pair, measured on the evaluated rig without last_walk["stance"]
    def planted_report(a, f_a, f_b, step=0.02):
        """While the root moves: the smaller of the two pairs' largest sole displacement per sample (0 = one pair
        always stands still) and the largest height of that standing pair's soles."""
        worst, lift, prev, prev_root, where = 0.0, 0.0, None, None, None
        for f in np.arange(float(f_a), float(f_b) + 1e-6, step):
            ev(float(f))
            cur = {leg: (ob.matrix_world @ Vector((0.0, 0.0, -a.leg_len))).copy() for leg, ob in a.legs.items()}
            root = a.root.matrix_world.translation.copy()
            yaw = a.root.rotation_euler.z
            if prev is not None and ((root - prev_root).length > 1e-5 or abs(yaw - prev_yaw) > 1e-5):
                per_pair = []
                for pair in a.gait_groups:
                    per_pair.append((max((cur[l].xy - prev[l].xy).length for l in pair), max(cur[l].z for l in pair)))
                d, z = min(per_pair)
                if d > worst:
                    worst, where = d, round(float(f), 2)
                lift = max(lift, z)
            prev, prev_root, prev_yaw = cur, root, yaw
        return worst, lift, where

    for name, mk in (("cow", lambda: animals.make_cow("pc")), ("calf", lambda: animals.make_cow("pk", baby=True)),
                     ("hen", lambda: animals.make_chicken("ph")), ("chick", lambda: animals.make_chicken("pq", baby=True))):
        a = mk()
        a.place(1000, (0, 100, 0), 0.4)
        # a dog-leg with a rounded corner, then a turn on the spot, then a short walk back: what a director writes
        e1 = a.walk(1000, [(0, 100, 0), (3, 97, 0), (7, 98, 0)])
        e2 = a.face(e1 + 6, (0, 100, 0))
        e3 = a.walk(e2 + 4, [a.pos_at(e2 + 4), (4, 99.5, 0)])
        w, lift, where = planted_report(a, 1000, e3)
        # a sample that straddles a change of the standing pair shows up to half of what a swinging sole covers in it
        bound = 0.5 * 2.0 * (a.walk_speed / 24.0) * 0.02 * 1.6
        expect("%-5s dog-leg + turn + walk back (frames 1000-%d): the standing pair moves at most %.4f block per 1/50 frame "
               "(at %s; a pair change alone explains %.4f), its soles at most %.3f above the ground" % (
                   name, e3, w, where, bound, lift), w < bound and lift < 0.07)
        for o in a.objects():
            o.hide_render = True
    # follow() behind a leader who turns
    cow = animals.make_cow("fc")
    steve = ch.make_player("steve")
    steve.place(2000, (0, 200, 0), 0.0)
    cow.place(2000, (0, 205, 0), math.pi)                                 # facing AWAY from him
    w_end = steve.walk(2010, [(0, 200, 0), (5, 196, 0), (9, 201, 0)])
    end = animals.follow(cow, steve, 2000, w_end + 12)
    w, lift, where = planted_report(cow, 2000, end)
    gaps = [(steve.pos_at(f) - cow.pos_at(f)).length for f in range(2000, end + 1)]
    turn = max(abs(ch._wrap(cow.yaw_at(f + 1) - cow.yaw_at(f))) for f in range(2000, end))
    expect("follow() a leader who turns, starting with her back to him: standing pair moves %.4f at most (at %s), gap %.2f-%.2f, "
           "ends %.2f behind, turns %.1f deg/frame at most" % (w, where, min(gaps), max(gaps), gaps[-1], math.degrees(turn)),
           w < 0.5 * 2.0 * (animals.COW_TEMPT / 24.0) * 0.02 * 1.6 and 2.2 < gaps[-1] < 2.8)

    # ---- 3. the head really points at what it looks at
    cow = animals.make_cow("lc")
    hen = animals.make_chicken("lh")
    calf = animals.make_cow("lk", baby=True)
    for a, x in ((cow, 0.0), (hen, 4.0), (calf, 8.0)):
        a.place(3000, (x, 300, 0), 0.6)
        target = Vector((x + 2.5, 297.5, 1.9))
        a.look_at(3000, target, ease=0)
        ev(3000)
        m = a.head.matrix_world
        fwd = (m.to_3x3() @ Vector((0.0, -1.0, 0.0))).normalized()
        want = (target - m.translation).normalized()
        off = math.degrees(fwd.angle(want))
        expect("%s look_at: the head's front points %.1f degrees off the target (head yaw %.0f, pitch %.0f)" % (
            a.name, off, math.degrees(a.head.rotation_euler.z), math.degrees(a.head.rotation_euler.x)), off < 3.0)
    # an item held by Steve as the target of track(), and the 40 degree limit on a hen looking up at his hand
    steve.place(3100, (4.0, 298.4, 0), 0.0)
    wheat = animals.hand_item(steve, "wheat_seeds", 3100, 3200)
    hen.place(3100, (4.0, 300, 0), 0.0)
    hen.track(3100, 3150, wheat)
    ev(3120)
    m = hen.head.matrix_world
    fwd = (m.to_3x3() @ Vector((0.0, -1.0, 0.0))).normalized()
    want = (wheat.matrix_world.translation - m.translation).normalized()
    expect("hen tracks the seeds in Steve's hand: %.1f degrees off (pitch %.0f, limit 40)" % (
        math.degrees(fwd.angle(want)), -math.degrees(hen.head.rotation_euler.x)),
        math.degrees(fwd.angle(want)) < 3.0 or abs(abs(math.degrees(hen.head.rotation_euler.x)) - 40.0) < 0.1)

    # ---- 4. head speed in a wandering pen: never faster than the game's 10 degrees per tick? (walk -> idle joints)
    herd = [animals.make_cow("h%d" % i) for i in range(5)]
    area = animals.pen_area(0, 400, 9, 409)
    animals.wander(herd, 4000, 4240, area, seed=2, watch=steve)
    worst, who = 0.0, None
    for a in herd:
        for f in np.arange(4000.0, 4300.0, 0.5):
            dy = abs(ch._val(a.head, "rotation_euler", 2, f + 0.5) - ch._val(a.head, "rotation_euler", 2, f))
            if dy > worst:
                worst, who = dy, (a.name, float(f))
    expect("wander(): heads turn at most %.1f degrees per tick (game: 10) %s" % (math.degrees(worst) * 2 * 1.2, who),
           math.degrees(worst) * 2 * 1.2 <= 10.5)
    # body yaw speed in the pen: the stepping turn
    worst = max(abs(ch._wrap(a.yaw_at(f + 1) - a.yaw_at(f))) for a in herd for f in range(4000, 4300))
    print("     wander(): bodies turn at most %.1f degrees per frame" % math.degrees(worst))
    # how much of the time is anything happening?
    moving = sum(1 for a in herd for f in range(4000, 4240) if (a.pos_at(f + 1) - a.pos_at(f)).length > 1e-4)
    print("     wander(): %d cows walk %.0f %% of the 10 s" % (len(herd), 100.0 * moving / (len(herd) * 240)))
    print("probe2:", "all %d passed" % len(res) if all(res) else "%d of %d FAILED" % (res.count(False), len(res)))
    return all(res)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
