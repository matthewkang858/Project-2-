"""Independent checker's probe of engine/piglins.py (numbers only; the renders are in check_piglins_probe_film.py).

Run:  $BPY -m tools.check_piglins_probe
"""
import math
import sys

import bpy
from mathutils import Vector


def counts():
    return {k: len(getattr(bpy.data, k)) for k in ("objects", "meshes", "materials", "images", "actions", "collections")}


def visible(ob, scene, frame):
    scene.frame_set(int(math.floor(frame)), subframe=frame - math.floor(frame))
    return not ob.hide_render


def main():
    from engine import quick

    scene = quick.reset()
    before = counts()
    from engine import piglins  # noqa
    after = counts()
    print("IMPORT leaves the scene untouched:", before == after, before, after)

    from engine import characters as ch
    from engine import mobs, shots
    from films.lookdev import Stage

    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, None, None)
    steve = st.actor("steve", "steve")
    a = piglins.add_piglin(st, "a")
    a2 = piglins.add_piglin(st, "a")
    print("add_piglin twice gives the same object:", a is a2)
    b = piglins.add_piglin(st, "b", "brute")
    c = piglins.add_piglin(st, "c", baby=True)
    d = piglins.add_piglin(st, "d", weapon="crossbow", armor=("helmet", "chestplate", "leggings", "boots"))
    e = piglins.add_piglin(st, "e", "brute")
    f = piglins.add_piglin(st, "f")
    n6 = counts()
    print("six piglins + steve:", n6)
    faces = sum(len(o.data.polygons) for p in (a, b, c, d, e, f) for o in p.objects() if o.type == "MESH")
    print("faces of six piglins (twins and items included):", faces)
    mats = {m.name for p in (a, b, e, f) for o in p.objects() if o.type == "MESH" for m in o.data.materials}
    print("materials used by 2 piglins + 2 brutes:", sorted(mats))
    anim_mats = [m.name for m in bpy.data.materials if m.animation_data is not None or (m.node_tree and m.node_tree.animation_data)]
    print("animated materials:", anim_mats)

    ingot = piglins.add_item(st, "gold_ingot")
    pearl = piglins.add_item(st, "ender_pearl")

    # ---------------- shot 1 (frames 1..72): everything at frame 1
    s1 = st.shot("one", 3.0)
    f0 = s1.frame_start
    print("shot one", s1.frame_start, s1.frame_end)
    a.place(f0, (0, 0, 0), 0.0)
    end = a.walk(f0, [(0, 0, 0), (0, -4, 0)])
    print("walk at frame 1 ends", end, a.last_walk["steps"], "steps")
    b.place(f0, (3, 0, 0), 0.0)
    b.aggro(f0)
    b.idle(f0, s1.frame_end + 1, seed=3)
    c.place(f0, (-3, 0, 0), 0.0)
    c.walk(f0, [(-3, 0, 0), (-3, -5, 0), (0, -5, 0)], run=True)
    print("baby run:", {k: c.last_walk[k] for k in ("speed", "steps", "step_frames", "slides", "swing")})
    d.place(f0, (5, 0, 0), 0.0)
    steve.place(f0, (0, -8, 0), math.pi)
    hurt_end = d.hurt(f0, source=steve)          # hurt on the very first frame
    d.hurt(f0 + 6, source=steve)                 # and again before the first flash is over
    print("hurt at frame 1 ->", hurt_end, "flash spans", d._flash)
    st.use(s1, a, b, c, d, steve)
    s1.lens(35, 2.8)
    s1.move((0, -12, 1.5), (0, 0, 1))

    # ---------------- shot 2: a dies at the very end of it; b, e not used
    s2 = st.shot("two", 2.0)
    f0 = s2.frame_start
    a.place(f0, (0, 0, 0), 0.0)
    steve.place(f0, (0, -1.3, 0), math.pi)
    gone = a.die(s2.frame_end - 30, source=steve, camera=s2)
    print("shot two", s2.frame_start, s2.frame_end, "a dies", s2.frame_end - 30, "gone", gone)
    burst = a.last_death["burst"]
    print("poof lives until frame", burst.frame_end, "(shot two ends", s2.frame_end, ")")
    st.use(s2, a, steve)
    s2.lens(35, 2.8)
    s2.move((0, -12, 1.5), (0, 0, 1))

    # ---------------- shot 3: a is back; barter twice; e walks and is hit while walking
    s3 = st.shot("three", 14.0)
    f0 = s3.frame_start
    a.place(f0, (0, 0, 0), 0.0)
    steve.place(f0, (0, -4, 0), math.pi)
    ingot.place(f0, (0.3, -0.8, 0.0))
    beats1 = piglins.barter(a, ingot, f0 + 10, pearl, toward=steve, admire_ticks=30)
    try:
        ingot.place(beats1["landed"] + 5, (0.3, -0.8, 0.0))
        beats2 = piglins.barter(a, ingot, beats1["landed"] + 20, pearl, toward=steve, admire_ticks=30)
        print("barter twice with the same items: ok", {k: v for k, v in beats2.items() if k not in ("item", "rest")})
    except Exception as err:                                   # noqa
        beats2 = None
        print("barter twice with the same items FAILS:", type(err).__name__, err)
    e.place(f0, (4, 4, 0), 0.0)
    wend = e.walk(f0, [(4, 4, 0), (4, -4, 0)])
    hit = f0 + 20
    p_before = e.pos_at(hit)
    back = e.hurt(hit, source=(4, e.pos_at(hit).y - 1.0, 0))
    print("hurt while walking: walk would end", wend, "| hit", hit, "at", tuple(round(v, 2) for v in p_before),
          "| stands still", back, "at", tuple(round(v, 2) for v in e.pos_at(back)), "| at walk end", tuple(round(v, 2) for v in e.pos_at(wend + 5)))
    # attack twice
    b.place(f0, (-4, 0, 0), 0.0)
    b.aggro(f0)
    e1 = b.attack(f0 + 10)
    e2 = b.attack(f0 + 34)
    e3 = b.attack(f0 + 40)                          # too soon (overlaps nothing, but < 24 frames)
    print("attacks end", e1, e2, e3)
    st.use(s3, a, b, e, steve, ingot, pearl)
    s3.lens(35, 2.8)
    s3.move((0, -12, 1.5), (0, 0, 1))
    st.finish()

    # ---- visibility audit, every frame of the film
    cast = dict(a=a, b=b, c=c, d=d, e=e, f=f)
    problems = []
    for frame in range(film.frame_start, film.frame_end + 1):
        scene.frame_set(frame)
        shot = film.shot_at(frame)
        for name, p in cast.items():
            want = name in st.in_shot[shot.name]
            shown = [o.name for o in p.objects() if o.type == "MESH" and not o.hide_render]
            if not want and shown:
                problems.append((frame, shot.name, name, "visible outside its shot", shown[:4]))
            if want and not p.gone_at(frame):
                for ob, twin in p._skin:
                    if (not ob.hide_render) == (not twin.hide_render):
                        problems.append((frame, shot.name, name, "skin and red twin both %s" % ("on" if not ob.hide_render else "off"), ob.name))
                        break
                for side in ("r", "l"):
                    on = [k for k, o in p._items[side].items() if not o.hide_render]
                    if len(on) > 1:
                        problems.append((frame, shot.name, name, "two items in hand " + side, on))
            if want and p.gone_at(frame) and shown:
                problems.append((frame, shot.name, name, "gone but visible", shown[:4]))
        # poof particles outside the shot of the death
        if shot.name != "two":
            on = [o.name for o in burst.objects if not o.hide_render]
            if on:
                problems.append((frame, shot.name, "poof", "particles of shot two visible", len(on)))
    print("VISIBILITY problems:", len(problems))
    seen = set()
    for pr in problems:
        key = (pr[1], pr[2], pr[3])
        if key not in seen:
            seen.add(key)
            print("   first:", pr, "| count", sum(1 for q in problems if (q[1], q[2], q[3]) == key))

    # f was never placed and never used: where is it?
    scene.frame_set(1)
    print("unused piglin f visible at frame 1:", [o.name for o in f.objects() if o.type == "MESH" and not o.hide_render][:3])

    # ---- a after its death and place(): upright, alive, skin normal
    scene.frame_set(s3.frame_start)
    print("a at start of shot three: roll %.3f, gone %s, hurt %s, visible parts %d, weapon visible %s" %
          (a.root.rotation_euler.y, a.gone_at(s3.frame_start), a.hurt_at(s3.frame_start),
           sum(1 for o, _t in a._skin if not o.hide_render), not a.weapon.hide_render))
    # last frame of shot two as the shutter sees it (f + 0.5): still at its shot-two state?
    scene.frame_set(s2.frame_end, subframe=0.5)
    print("a at the end of the last exposure of shot two: pos", tuple(round(v, 3) for v in a.root.location),
          "roll %.3f" % a.root.rotation_euler.y)

    # ---- hurt twice on d: red continuous over both, position sane
    for fr in (1, 6, 7, 12, 13, 18, 19, 20):
        scene.frame_set(fr)
        print("   d frame %2d: red %s pos %s" % (fr, not d._skin[0][1].hide_render, tuple(round(v, 2) for v in d.root.location)))

    # ---- independent foot-slip measure (no use of last_walk["stance"]): the lower sole must not move
    def soles(p):
        return [(p.leg_l.matrix_world @ Vector((0, 0, -p.leg_len))), (p.leg_r.matrix_world @ Vector((0, 0, -p.leg_len)))]

    def slip(p, fa, fb, label):
        worst, total, air, sink = 0.0, 0.0, 0.0, 0.0
        prev = None
        t = float(fa)
        ground = p.pos_at(fa).z
        while t <= fb + 1e-6:
            scene.frame_set(int(math.floor(t)), subframe=t - math.floor(t))
            bpy.context.view_layer.update()
            s = soles(p)
            low = 0 if s[0].z <= s[1].z else 1
            air = max(air, min(s[0].z, s[1].z) - ground)
            sink = min(sink, min(s[0].z, s[1].z) - ground)
            if prev is not None and prev[0] == low:
                dd = math.hypot(s[low].x - prev[1].x, s[low].y - prev[1].y)
                worst = max(worst, dd)
                total += dd
            prev = (low, s[low].copy())
            t += 0.25
        print("   %s: planted sole moves at most %.4f block per quarter frame, %.3f in total over %d frames; lowest sole up to %.3f above / %.3f below the floor"
              % (label, worst, total, fb - fa, air, -sink))

    g = piglins.make_piglin("g")
    g.place(1000, (0, 0, 0), 0.0)
    eg = g.walk(1000, [(0, 0, 0), (0, -5, 0)])
    slip(g, 1000, eg, "adult walk 5 blocks")
    g.place(1200, (0, 0, 0), 0.0)
    eg = g.walk(1200, [(0, 0, 0), (0, -7, 0)], run=True)
    slip(g, 1200, eg, "adult run 7 blocks")
    g.place(1400, (0, 0, 0), 0.0)
    eg = g.walk(1400, [(0, 0, 0), (0, -3, 0), (3, -3, 0), (3, 0, 0)])
    slip(g, 1400, eg, "adult walk with two corners")
    g.place(1600, (0, 0, 0), 0.0)
    eg = g.walk(1600, [(0, 0, 0), (0, -5, 0)], speed=1.2, swing=0.5)
    slip(g, 1600, eg, "slow heavy walk (speed 1.2, swing 0.5)")
    g.place(1800, (0, 0, 0), 0.0)
    eg = g.walk(1800, [(0, 0, 0), (0, -5, 0)], gait="vanilla")
    slip(g, 1800, eg, "VANILLA gait (for scale)")
    h = piglins.make_piglin("h", baby=True)
    h.place(1000, (0, 0, 0), 0.0)
    eh = h.walk(1000, [(0, 0, 0), (0, -5, 0)])
    slip(h, 1000, eh, "baby walk")
    h.place(1200, (0, 0, 0), 0.0)
    eh = h.walk(1200, [(0, 0, 0), (0, -5, 0)], run=True)
    slip(h, 1200, eh, "baby run")
    # walk continued mid-way
    g.place(2000, (0, 0, 0), 0.0)
    eg = g.walk(2000, [(0, 0, 0), (0, -6, 0)])
    mid = 2000 + 30
    pm = g.pos_at(mid)
    eg2 = g.walk(mid, [(3, pm.y, 0)], from_current=True)
    jump = max((g.pos_at(mid + k * 0.25) - g.pos_at(mid + (k - 1) * 0.25)).length for k in range(-8, 12))
    print("   re-walk mid-way (from_current): largest move per quarter frame around the change %.4f (cruise %.4f)" % (jump, 1.94 / 24 / 4))
    scene.frame_set(mid)
    print("   legs at the change: l %.3f r %.3f ; one frame later l %.3f r %.3f" %
          (g.leg_l.rotation_euler.x, g.leg_r.rotation_euler.x, ch._val(g.leg_l, "rotation_euler", 0, mid + 1), ch._val(g.leg_r, "rotation_euler", 0, mid + 1)))

    # ---- snap poses and the shutter: nothing may change in (f - 1, f - 0.5]
    k = piglins.make_piglin("k", "brute")
    k.place(3000, (0, 0, 0), 0.0)
    k.aggro(3010)
    for t in (3009.0, 3009.5, 3009.74, 3009.76, 3010.0):
        print("   aggro snap: arm at %.2f = %.3f" % (t, ch._val(k.arm_r, "rotation_euler", 0, t)))
    # die twice
    try:
        g1 = k.die(3020, camera=None, poof_particles=False)
        g2 = k.die(3030, camera=None, poof_particles=False)
        print("die twice:", g1, g2, "gone spans", k._gone, "flash", k._flash)
    except Exception as err:                                    # noqa
        print("die twice raises:", type(err).__name__, err)
    try:
        k2 = piglins.make_piglin("k2")
        k2.place(1, (0, 0, 0))
        k2.die(10)
        print("die() without camera: poof built with", len(k2.last_death["burst"].objects), "objects")
    except Exception as err:                                    # noqa
        print("die() without camera raises:", type(err).__name__, str(err)[:150])
    # make_piglin twice with the same name
    try:
        z1 = piglins.make_piglin("same")
        z2 = piglins.make_piglin("same")
        print("make_piglin twice with one name: roots", z1.root.name, z2.root.name, "| parts shared?", z1.head is z2.head)
    except Exception as err:                                    # noqa
        print("make_piglin twice raises:", type(err).__name__, err)
    return 0


if __name__ == "__main__":
    sys.exit(main())
