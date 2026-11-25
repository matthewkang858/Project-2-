"""Independent checker's probe 2 of engine/piglins.py: feet (measured without the module's own stance table),
hit timing, held-item geometry, poof stop. Numbers only.

Run:  $BPY -m tools.check_piglins_probe2
"""
import math
import sys

import bpy
from mathutils import Vector


def main():
    from engine import quick

    scene = quick.reset()
    from engine import characters as ch
    from engine import fx, mobs, piglins

    def soles(p):
        return [(p.leg_l.matrix_world @ Vector((0, 0, -p.leg_len))), (p.leg_r.matrix_world @ Vector((0, 0, -p.leg_len)))]

    def slip(p, fa, fb, label, dt=0.125):
        """Per step of dt frames the slower sole is taken as the planted one: its travel is the slip."""
        worst, total, sink, lift = 0.0, 0.0, 0.0, 0.0
        prev = None
        t = float(fa)
        ground = p.pos_at(fa).z
        run_slip, run_len, worst_run = 0.0, 0, 0.0
        while t <= fb + 1e-6:
            scene.frame_set(int(math.floor(t)), subframe=t - math.floor(t))
            bpy.context.view_layer.update()
            s = soles(p)
            sink = min(sink, s[0].z - ground, s[1].z - ground)
            if prev is not None:
                d = [math.hypot(s[i].x - prev[i].x, s[i].y - prev[i].y) for i in (0, 1)]
                k = 0 if d[0] <= d[1] else 1
                worst = max(worst, d[k])
                total += d[k]
                lift = max(lift, s[k].z - ground)
            prev = [v.copy() for v in s]
            t += dt
        body = (p.pos_at(fb) - p.pos_at(fa)).length
        print("   %-42s slower sole: %.4f blocks in all over %.1f blocks walked (%.1f %%), worst %.4f per 1/8 frame; "
              "standing sole up to %.3f off the floor; a sole up to %.3f BELOW the floor"
              % (label, total, body, 100.0 * total / max(body, 1e-6), worst, lift, -sink))

    g = piglins.make_piglin("g")
    cases = [("adult walk 5", dict(points=[(0, 0, 0), (0, -5, 0)])),
             ("adult run 7", dict(points=[(0, 0, 0), (0, -7, 0)], run=True)),
             ("adult walk, two corners", dict(points=[(0, 0, 0), (0, -3, 0), (3, -3, 0), (3, 0, 0)])),
             ("adult run, one corner", dict(points=[(0, 0, 0), (0, -4, 0), (4, -4, 0)], run=True)),
             ("slow heavy (1.2, swing .5)", dict(points=[(0, 0, 0), (0, -5, 0)], speed=1.2, swing=0.5)),
             ("short walk 1.0 block", dict(points=[(0, 0, 0), (0, -1.0, 0)])),
             ("short walk 0.4 block", dict(points=[(0, 0, 0), (0, -0.4, 0)])),
             ("diagonal 3.3", dict(points=[(0, 0, 0), (2.2, -2.5, 0)])),
             ("VANILLA gait walk 5 (for scale)", dict(points=[(0, 0, 0), (0, -5, 0)], gait="vanilla")),
             ("VANILLA gait run 7 (for scale)", dict(points=[(0, 0, 0), (0, -7, 0)], gait="vanilla", run=True))]
    f = 1000
    for label, kw in cases:
        g.place(f, (0, 0, 0), 0.0)
        end = g.walk(f, **kw)
        slip(g, f, end, label + " [%d fr]" % (end - f))
        f += 400
    h = piglins.make_piglin("h", baby=True)
    for label, kw in (("baby walk 5", dict(points=[(0, 0, 0), (0, -5, 0)])), ("baby run 5", dict(points=[(0, 0, 0), (0, -5, 0)], run=True)),
                      ("baby speed 4.5", dict(points=[(0, 0, 0), (0, -5, 0)], speed=4.5))):
        h.place(f, (0, 0, 0), 0.0)
        end = h.walk(f, **kw)
        slip(h, f, end, label + " [%d fr]" % (end - f))
        f += 400
    b = piglins.make_piglin("b", "brute")
    b.place(f, (0, 0, 0), 0.0)
    b.aggro(f)
    end = b.walk(f, [(0, 0, 0), (0, -7, 0)], run=True, ramp=(0, 3))
    slip(b, f, end, "brute chase, axe high [%d fr]" % (end - f))
    scene.frame_set(f + 10)
    print("   brute while chasing: weapon arm %.2f (held high -1.8), other arm %.2f, hips z %.3f" %
          (b.arm_r.rotation_euler.x, b.arm_l.rotation_euler.x, b.hips.location.z))

    # ---- die shortly after a hit (still in the air)
    print("HIT THEN DIE")
    for gap in (6, 10, 12, 15, 24, 34):
        v = piglins.make_piglin("v%d" % gap)
        v.place(1, (0, 0, 0), 0.0)
        back = v.hurt(10, source=(0, -1.4, 0))
        gone = v.die(10 + gap, source=(0, -1.4, 0), poof_particles=False)
        zs = [round(v.pos_at(t).z, 2) for t in (10 + gap, 10 + gap + 6, 10 + gap + 14, gone - 1)]
        print("   hurt(10) stands still %d; die(%d): height at death start / +6 / +14 / last frame = %s ; ends y=%.2f"
              % (back, 10 + gap, zs, v.pos_at(gone - 1).y))
    v = piglins.make_piglin("vh")
    v.place(1, (0, 0, 0), 0.0)
    v.hurt(10, source=(0, -1.4, 0))
    v.hurt(18, source=(0, -1.4, 0))
    print("   hurt(10), hurt(18): height at 18 / 24 / 40 / 80 =", [round(v.pos_at(t).z, 2) for t in (18, 24, 40, 80)])

    # ---- held items: where is the sword / axe / crossbow / ingot, in blocks
    print("HELD ITEMS (piglin at origin facing -Y; x: its left is +X)")
    for kind, weapon in (("piglin", "golden_sword"), ("brute", "golden_axe"), ("piglin", "crossbow")):
        p = piglins.make_piglin("w_" + weapon, kind, weapon=weapon)
        p.place(1, (0, 0, 0), 0.0)
        scene.frame_set(1)
        bpy.context.view_layer.update()
        ob = p.weapon
        m = ob.matrix_world
        cen = m.translation
        # the sprite lies in its local XZ plane: local +X = texture right, local +Z = texture up
        tip = (m.to_3x3() @ Vector((1, 0, 1))).normalized()
        print("   %-13s centre (%.3f, %.3f, %.3f) scale %.2f; texture diagonal (handle -> tip) points (%.2f, %.2f, %.2f); normal (%.2f, %.2f, %.2f); hand at (%.3f, %.3f, %.3f)"
              % (weapon, cen.x, cen.y, cen.z, m.to_scale().x, tip.x, tip.y, tip.z, *(m.to_3x3() @ Vector((0, 1, 0))).normalized(),
                 *(p.arm_r.matrix_world @ Vector((-1 / 16, 0, -10 / 16)))))
    bb = piglins.make_piglin("w_baby", baby=True, weapon="golden_sword")
    bb.place(1, (0, 0, 0), 0.0)
    scene.frame_set(1)
    bpy.context.view_layer.update()
    print("   baby with a sword: centre", tuple(round(c, 3) for c in bb.weapon.matrix_world.translation), "scale %.2f" % bb.weapon.matrix_world.to_scale().x)

    # ---- poof: sizes, where, facing, stop()
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    scene.collection.objects.link(cam)
    cam.location = (0, -8, 1.5)
    cam.rotation_euler = (math.radians(90), 0, 0)
    scene.camera = cam
    burst = piglins.poof((0, 0, 0), 100, camera=cam, seed=3)
    sizes = sorted({round(2 * p["size"], 2) for p in burst.particles})
    print("POOF: %d objects, %d particles; widths %s" % (len(burst.objects), len({p["carrier"].name for p in burst.particles}), sizes))
    for fr in (100, 101, 102, 106, 112, 124, 148, 172, 196):
        scene.frame_set(fr)
        bpy.context.view_layer.update()
        on = [o for o in burst.objects if not o.hide_render]
        zs = [o.matrix_world.translation.z for o in on]
        stages = sorted({o.name.rsplit("_", 1)[-1] for o in on})
        facing = max((abs((o.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized().dot(Vector((0, -1, 0))) - 1.0) for o in on), default=0.0)
        print("   frame %d: %2d puffs visible, heights %.2f..%.2f, sprite stages %s, worst facing error %.4f" %
              (fr, len(on), min(zs, default=0), max(zs, default=0), stages, facing))
    n = burst.stop(110)
    scene.frame_set(110)
    print("   burst.stop(110) ended %d; visible at 110: %d; at 109: " % (n, sum(1 for o in burst.objects if not o.hide_render)), end="")
    scene.frame_set(109)
    print(sum(1 for o in burst.objects if not o.hide_render))
    print("   fx.stop_particles knows the poof:", burst in fx._BURSTS)

    # ---- look_at limits and the hole picture: how far down can it look
    p = piglins.make_piglin("looker")
    p.place(1, (0, 0, 0), 0.0)
    p.look_at(1, (0, -0.6, -2.0), ease=0)
    scene.frame_set(1)
    print("LOOK down a hole at its feet: head pitch %.1f deg (limit 40)" % math.degrees(p.head.rotation_euler.x))
    p.look_at(1, (5, 5, 1.7), ease=0)
    scene.frame_set(1)
    print("LOOK behind: head yaw %.1f deg (limit 75)" % math.degrees(p.head.rotation_euler.z))
    return 0


if __name__ == "__main__":
    sys.exit(main())
