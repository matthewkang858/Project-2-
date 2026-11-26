"""Checker's probe 3 for "Twenty Minutes": the shared helpers keyed on scratch instances, read back. Prints only."""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    import bpy
    from mathutils import Vector

    import render
    from engine import characters as ch
    ses = render.Session("twentyminutes")
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    shots = {s.name: s for s in ses.film.shots}

    def bearing(a, b):
        return math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1])))

    def wrap(d):
        return (d + 180.0) % 360.0 - 180.0

    # 1. C.cheat / C.to_lens on a scratch villager facing away from a camera
    c = C.actor("baby", "gp9")
    f = 900
    c.place(f, (0.0, 0.0, 0.0), 0.0)                       # faces -Y (south)
    cam = (0.0, 5.0, 0.6)                                   # north of it: behind its back
    target = (0.5, -5.0, 0.6)                               # ahead of it, nearly away from the lens
    eye = c.eye_point(f)
    for name, fn in (("cheat 65", lambda: C.cheat(c, f, target, cam)),
                     ("to_lens 21", lambda: C.to_lens(c, f, target, cam))):
        p = fn()
        off_t = wrap(bearing(eye, target) - bearing(eye, cam))
        off_p = wrap(bearing(eye, p) - bearing(eye, cam))
        c.look_at(f, p, ease=0)
        head = math.degrees(ch._val(c.head, "rotation_euler", 2, f))
        looks = math.degrees(c.yaw_at(f)) + head
        print("%-10s target %6.1f deg off the lens -> point %6.1f off; keyed head %6.1f, looks %6.1f off the lens"
              % (name, off_t, off_p, head, wrap(bearing(eye, eye + Vector((math.sin(math.radians(looks)),
                                                                             -math.cos(math.radians(looks)), 0))) -
                                                     bearing(eye, cam))))

    # 2. C.on_zombie from a spot facing away (the head clamp is silent)
    m = C.actor("mom", "gp9")
    C.put(m, 1300, "row_4")
    C.on_zombie(m, 1300)
    ze = C.zombie_eye
    e = m.eye_point(1300)
    looks = math.degrees(m.yaw_at(1300) + ch._val(m.head, "rotation_euler", 2, 1300))
    print("on_zombie from row_4 (anchor yaw %.1f): looks %.1f, zombie at %.1f -> %.1f deg off, no warning" % (
        math.degrees(C.yaw("row_4") or 0.0), looks, bearing(e, ze), abs(wrap(looks - bearing(e, ze)))))

    # 3. C.fill with two shots given latest first, and per-shot calls in order
    s9, s10, s24 = shots["gm09_golem"], shots["gm10_again"], shots["gm24_counts"]
    lamp = C.fill("gm_check_a", (0, 0, 5), 10.0, [s10, s9])
    lamp_b = C.fill("gm_check_b", (0, 0, 6), 10.0, [s9])
    C.fill("gm_check_b", (0, 0, 6), 10.0, [s10])
    C.fill("gm_check_b", (0, 0, 6), 10.0, [s24])
    for f in (503, 504, 591, 592, 600, 639, 640, 1472, 1473, 1542):
        scene.frame_set(f)
        print("fill f %4d: [s10, s9] in one call hidden=%s | one call per shot hidden=%s" % (
            f, lamp.hide_render, lamp_b.hide_render))
    try:
        C.fill("ce_x", (0, 0, 5), 5.0, [s9])
        C.fill("ce_x", (0, 0, 5), 6.0, [s10])
        print("fill: a second call with other watts was accepted (should raise)")
    except ValueError as ex:
        print("fill: a second call with other watts raises:", str(ex)[:60])
    try:
        C.fill("zz_bad", (0, 0, 5), 5.0, [s9])
        print("fill: a name without a prefix was accepted")
    except KeyError:
        print("fill: a name without a sequence prefix raises KeyError")

    # 4. C.rack: the focus empty's keys
    s = shots["gp15_fit"]
    C.rack(s, (0.0, 0.0, 0.0), 920, frames=12)
    foc = s._focus
    from engine import shots as SH
    for fc in SH.fcurves_of(foc):
        ks = [(round(k.co.x, 1), round(k.co.y, 2)) for k in fc.keyframe_points]
        print("rack focus keys %s[%d]: %s" % (fc.data_path, fc.array_index, ks[:6]))
    print("Film.frame(%.4f s) = %d (rack asked ON 920)" % ((920 - 1) / 24.0, ses.film.frame((920 - 1) / 24.0)))

    # 5. C.actor guards
    for role, tag in (("baby", "xx"), ("pig", "gp"), ("narrator", "sq")):
        try:
            C.actor(role, tag)
            print("actor(%r, %r) accepted" % (role, tag))
        except KeyError as ex:
            print("actor(%r, %r) -> KeyError %s" % (role, tag, ex))
    a, b = C.actor("baby", "sq"), C.actor("baby", "gp")
    print("twins distinct: baby_sq root %s vs baby_gp root %s; same object: %s" % (
        a.root.name, b.root.name, a.root is b.root))
    for n in sorted(st.cast):
        cc = st.cast[n]
        obs = cc.objects() if callable(getattr(cc, "objects", None)) else []
        held = getattr(cc, "held", None)
        print("  cast %-16s %-14s objects %3d  held %s" % (n, type(cc).__name__, len(obs), held.name if held else "-"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
