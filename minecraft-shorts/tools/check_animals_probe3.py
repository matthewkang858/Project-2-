"""Independent checker's third numeric probe of engine/animals.py: several animals after one leader, a blow in
mid-stride, hand items and Stage, stop_particles on a poof.
Run:  $BPY -m tools.check_animals_probe3"""
import math
import sys

import bpy
import numpy as np
from mathutils import Vector


def main():
    from engine import animals, characters as ch, fx, quick

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
    steve = ch.make_player("steve")

    # ---- 1. "they follow": three cows (and four hens) after Steve with their food, as the brief asks
    for kind, n, mk, food in (("cow", 3, lambda i: animals.make_cow("fc%d" % i), "wheat"),
                              ("hen", 4, lambda i: animals.make_chicken("fh%d" % i), "wheat_seeds")):
        f0 = 100 if kind == "cow" else 600
        steve.place(f0, (0, 0, 0), 0.0)
        item = animals.hand_item(steve, food, f0, f0 + 400)
        group = [mk(i) for i in range(n)]
        for i, a in enumerate(group):
            a.place(f0, (-1.8 + 1.8 * i if kind == "cow" else -1.5 + 1.0 * i, 4.0 + 0.4 * (i % 2), 0.0), 0.0)
        w_end = steve.walk(f0 + 10, [(0, 0, 0), (0, -9, 0)])
        ends = [animals.follow(a, steve, f0, w_end + 20) for a in group]
        end = max(ends)
        worst, when, pair = 9.0, None, None
        for f in range(f0, end + 1):
            for i, a in enumerate(group):
                for b in group[i + 1:]:
                    g = animals._gap(a, a.pos_at(f), a.yaw_at(f), b, b.pos_at(f), b.yaw_at(f))
                    if g < worst:
                        worst, when, pair = g, f - f0, (a.name, b.name)
        final = [tuple(round(c, 2) for c in a.pos_at(end).xy) for a in group]
        centre = min((group[i].pos_at(end) - group[j].pos_at(end)).length for i in range(n) for j in range(i + 1, n))
        expect("%d %ss follow() Steve 9 blocks: smallest gap between two bodies %.2f (frame +%s, %s); they end at %s, the two "
               "nearest %.2f apart (a %s is %.2f wide)" % (n, kind, worst, when, pair, final, centre, kind, group[0].width),
               worst > -0.1 * group[0].width,
               "they walk into one another: follow() knows only one animal")

    # ---- 2. a blow in mid-stride: does the body come back up?
    cow = animals.make_cow("mc")
    cow.place(1000, (0, 50, 0), math.radians(90))
    cow.walk(1000, [(0, 50, 0), (8, 50, 0)])
    rest = cow._rest(cow.hips, "location", 2)
    sink = [(rest - ch._val(cow.hips, "location", 2, f), f) for f in np.arange(1020.0, 1045.0, 0.25)]
    deep, f_hit = max(sink)
    f_hit = int(round(f_hit))
    deep = rest - ch._val(cow.hips, "location", 2, f_hit)
    up = cow.hurt(f_hit, attacker=(-2, 50, 0))
    ev(up + 40)
    soles = [(ob.matrix_world @ Vector((0, 0, -cow.leg_len))).z for ob in cow.legs.values()]
    expect("cow hit on frame %d of a walk, the body %.3f down in its step: 40 frames after it stands again the body is "
           "%.3f below its rest height, soles at z = %.3f" % (f_hit, deep, rest - cow.hips.location.z, min(soles)),
           abs(rest - cow.hips.location.z) < 1e-4, "it stays sunk into the ground until its next walk or place()")
    g = cow.die(up + 60, camera=cam)
    cow.place(g + 20, (0, 50, 0), 0.0)
    ev(g + 20)
    expect("... place() restores the height", abs(rest - cow.hips.location.z) < 1e-6)

    # ---- 3. stop_particles ends a poof and hearts; particles copy the camera's rotation
    hen = animals.make_chicken("sh")
    hen.place(2000, (0, 80, 0), 0.0)
    g = hen.die(2000, camera=cam)
    hearts = animals.love(hen, 2000, camera=cam, frame_end=2060)
    burst = hen.bursts[0]
    ev(g + 6)
    live = [q for q in burst.particles if not q["object"].hide_render]
    quat = cam.matrix_world.to_quaternion()
    off = max(q["object"].matrix_world.to_quaternion().rotation_difference(quat).angle for q in live)
    n_before = len(live)
    ended = fx.stop_particles(g + 8)
    ev(g + 8)
    after = [q for q in burst.particles if not q["object"].hide_render]
    hearts_after = [q for b in hearts for q in b.particles if not q["object"].hide_render]
    expect("poof: %d puffs on frame gone + 6, turned %.4f rad from the camera; fx.stop_particles(gone + 8) ended %d, %d puffs "
           "and %d hearts left" % (n_before, off, ended, len(after), len(hearts_after)),
           n_before == 20 and off < 1e-3 and not after and not hearts_after)

    # ---- 4. die() without a camera (the default) in a scene that has one / poof sizes for a calf and a chick
    calf = animals.make_cow("dk", baby=True)
    chick = animals.make_chicken("dq", baby=True)
    for a, x in ((calf, 0.0), (chick, 3.0)):
        a.place(3000, (x, 90, 0), 0.0)
        g = a.die(3000)
        b = a.bursts[-1]
        ev(g)
        pts = [q["object"].matrix_world.translation for q in b.particles if not q["object"].hide_render]
        sz = [q["size"] * 2 for q in b.particles if not q["object"].hide_render]
        expect("%s dies with camera=None: %d puffs, %.2f-%.2f wide, spread x %.2f..%.2f z %.2f..%.2f (hit box %s)" % (
            a.name, len(pts), min(sz), max(sz), min(p.x for p in pts) - x, max(p.x for p in pts) - x,
            min(p.z for p in pts), max(p.z for p in pts), a.size), len(pts) == 20)
    print("probe3:", "all %d passed" % len(res) if all(res) else "%d of %d FAILED" % (res.count(False), len(res)))
    return all(res)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
