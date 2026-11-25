"""Independent numeric probe of engine/undead.py (checker's script; renders nothing).

Run:  $BPY -m tools.check_undead_probe
"""
import math
import sys

import bpy
from mathutils import Vector


def main():
    from engine import quick

    scene = quick.reset()
    quick.setup(scene)
    cam = quick.camera(scene, (0.0, -8.0, 1.5), (0.0, 0.0, 1.0))
    before = {k: len(getattr(bpy.data, k)) for k in ("objects", "meshes", "materials", "images", "actions", "collections")}
    from engine import undead as U
    from engine import characters as ch
    from engine import fx, mobs, props
    after = {k: len(getattr(bpy.data, k)) for k in before}
    print("IMPORT leaves bpy.data untouched:", before == after, before, after)

    res = []

    def say(label, ok, detail=""):
        res.append(bool(ok))
        print("%s %-70s %s" % ("ok  " if ok else "BAD ", label, detail))

    def vis(c, f):
        scene.frame_set(int(f))
        own = [o for o in c.objects() if o.type == "MESH" and not o.hide_render]
        st = c.__dict__.get(U._STATE) or {}
        red = [t for t in st.get("twins", {}).values() if not t.hide_render]
        return len(own), len(red)

    # ------------------------------------------------------------ six at once
    zs = [U.make_zombie("z%d" % i, baby=(i == 5)) for i in range(6)]
    names = [o.name for z in zs for o in z.objects()]
    say("six zombies: distinct object names", len(names) == len(set(names)), "%d objects" % len(names))
    mats = {o.data.materials[0].name for z in zs[:5] for o in z.objects() if o.type == "MESH"}
    say("five adult zombies share one material", len(mats) == 1, str(mats))
    for i, z in enumerate(zs):
        z.place(1, (i * 1.5, 0.0, 0.0), 0.0)
        z.show(1, True)
        z.walk(1, [(i * 1.5, 0.0, 0.0), (i * 1.5, -6.0, 0.0)])
    ends = []
    for i, z in enumerate(zs):
        ends.append(z.die(30 + i, camera=cam, seed=i))
    say("six deaths: each gone 24 frames later", ends == [54 + i for i in range(6)], str(ends))
    n_poof = sum(len(b.objects) for b in fx._BURSTS if b.kind == "poof")
    print("     poof objects for six deaths:", n_poof, "| scene objects:", len(bpy.data.objects))
    v0 = [vis(z, 40) for z in zs]
    v1 = [vis(z, 70) for z in zs]
    say("six deaths: all red at 40, none left at 70", all(a == 0 and b > 0 for a, b in v0) and all(a == 0 and b == 0 for a, b in v1), "%s %s" % (v0, v1))
    # bob phase differs between zombies
    scene.frame_set(20)
    bobs = {round(z.arm_r.rotation_euler[1], 4) for z in zs[:5]}
    say("zombies bob out of phase", len(bobs) >= 4, str(sorted(bobs)))

    # ------------------------------------------------------------ twice / frame 1
    a = U.make_zombie("twice")
    a.place(1, (0.0, 10.0, 0.0), 0.0)
    a.show(1, True)
    try:
        e1 = a.hurt(1, attacker=(0.0, 9.0, 0.0))
        e2 = a.hurt(1, attacker=(0.0, 9.0, 0.0))
        p = a.pos_at(60)
        say("hurt twice on frame 1: one hop, same end", e1 == e2 and abs(p.y - 11.99) < 0.03, "end %s %s, y at 60 = %.3f" % (e1, e2, p.y))
        say("hurt at frame 1: red on 1, own meshes hidden; back on 13", vis(a, 1) == (0, 6) and vis(a, 13)[1] == 0 and vis(a, 13)[0] == 6, "%s %s %s" % (vis(a, 0), vis(a, 1), vis(a, 13)))
        say("hurt at frame 1: nothing red at frame 0 (pre-roll)", vis(a, 0)[1] == 0, str(vis(a, 0)))
    except Exception as exc:
        say("hurt twice on frame 1", False, repr(exc))
    # second blow while still in the air (attack interval 24 frames > 19, but a director may hit faster)
    b = U.make_zombie("combo")
    b.place(1, (4.0, 10.0, 0.0), 0.0)
    b.hurt(20, attacker=(4.0, 9.0, 0.0))
    b.hurt(26, attacker=(4.0, 9.0, 0.0))
    zmax = max(b.pos_at(20 + k * 0.5).z for k in range(80))
    say("second blow in mid-air: no double jump above 1 block (game: vy kept when not on ground)", zmax < 1.2, "apex %.3f, rest y %.3f z %.3f" % (zmax, b.pos_at(90).y, b.pos_at(90).z))

    d = U.make_zombie("die_twice")
    d.place(1, (8.0, 10.0, 0.0), 0.0)
    d.show(1, True)
    try:
        g1 = d.die(1, camera=cam)
        g2 = d.die(1, camera=cam)
        n = len([bu for bu in fx._BURSTS if bu.kind == "poof" and bu.frame == 25])
        say("die twice on frame 1: gone 25 both times", g1 == g2 == 25, "%s %s, %d poof bursts at 25 (a doubled cloud if 2)" % (g1, g2, n))
        say("die at frame 1: there at 1 (red), gone at 25", vis(d, 1) == (0, 6) and vis(d, 25) == (0, 0), "%s %s" % (vis(d, 1), vis(d, 25)))
    except Exception as exc:
        say("die twice on frame 1", False, repr(exc))

    # attack twice on the same frame / aggro persistence over place
    c = U.make_zombie("arms")
    c.place(1, (12.0, 10.0, 0.0), 0.0)
    c.attack(10)
    c.attack(10)
    say("attack twice on one frame: one swing", c._attacks == [10])
    c.aggro(20)
    c.place(100, (12.0, 12.0, 0.0), 0.0)
    scene.frame_set(101)
    base = c.arm_r.rotation_euler[0] - c.arm_bob(101)[0]
    say("place() after aggro(): arms back OUT (docstring: 'arms out')", abs(base - U.ARMS_OUT) < 1e-3, "pitch %.1f deg" % math.degrees(base))
    scene.frame_set(50)
    m = [mm.type for mm in ch._find(c.arm_r, "rotation_euler", 0).modifiers]
    say("bob modifier survives place/attack/aggro", m == ["FNGENERATOR"], str(m))

    # ------------------------------------------------------------ cuts
    v = ch.make_villager("cutv", "farmer")
    v.place(1, (0.0, 20.0, 0.0), 0.0)
    v.show(1, True)
    hz = U.make_zombie("cutz")
    hz.place(1, (0.0, 18.8, 0.0), math.radians(180))
    hz.attack(40, target=v)
    # the film cuts at frame 46 to another shot where the same villager stands somewhere else
    v.place(46, (30.0, 30.0, 0.0), 0.5)
    pos = [tuple(round(x, 3) for x in v.pos_at(f)) for f in (45, 46, 47, 50, 58, 70)]
    say("place() 6 frames after a blow: knock-back does not go on in the new shot",
        all(abs(v.pos_at(f).x - 30.0) < 1e-6 and abs(v.pos_at(f).z) < 1e-6 for f in (46, 47, 50, 58, 70)), str(pos))
    scene.frame_set(50)
    legs = (round(v.leg_l.rotation_euler[0], 3), round(v.leg_r.rotation_euler[0], 3))
    say("... legs neutral after that place()", abs(legs[0]) < 1e-3 and abs(legs[1]) < 1e-3, str(legs))
    say("... and the red flash does NOT carry into the new shot", vis(v, 46)[1] == 0, "red parts at 46/50: %s %s" % (vis(v, 46), vis(v, 50)))

    dz = U.make_zombie("cutdie")
    dz.place(1, (4.0, 20.0, 0.0), 0.0)
    dz.show(1, True)
    gone = dz.die(40, camera=cam, attacker=(4.0, 19.0, 0.0))
    dz.place(50, (40.0, 40.0, 0.0), 0.0)        # cut in the middle of the death, the zombie is reused
    s50, s64, s80 = vis(dz, 50), vis(dz, 64), vis(dz, 80)
    scene.frame_set(55)
    tilt = math.degrees(dz.root.rotation_euler[1])
    say("place() in the middle of a death: alive, upright, normal colours from then on",
        s50 == (6, 0) and s64 == (6, 0) and s80 == (6, 0) and abs(tilt) < 0.1, "50:%s 64:%s 80:%s tilt@55 %.1f" % (s50, s64, s80, tilt))
    dz2 = U.make_zombie("cutdie2")
    dz2.place(1, (6.0, 20.0, 0.0), 0.0)
    dz2.show(1, True)
    gone = dz2.die(40, camera=cam)
    dz2.place(gone + 10, (6.0, 22.0, 0.0), 0.0)
    say("place() after the death: back", vis(dz2, gone + 10) == (6, 0) and vis(dz2, gone + 5) == (0, 0), "%s %s" % (vis(dz2, gone + 5), vis(dz2, gone + 10)))
    dz2.show(gone + 30, False)
    dz2.show(gone + 60, True)
    say("show() off/on after that", vis(dz2, gone + 40) == (0, 0) and vis(dz2, gone + 60) == (6, 0))

    # ------------------------------------------------------------ Stage
    from films import lookdev
    from engine import shots

    class _V:                                   # the bits of a Village that Stage.finish touches
        lantern_lights = []
        anchors, yaws = {}, {}

    film = shots.Film(scene, fps=24)
    st = lookdev.Stage(scene, film, _V(), {})
    s1 = st.shot("one", 2.0)
    s2 = st.shot("two", 2.0)
    s3 = st.shot("three", 2.0)
    z = U.add_zombie(st, "stz")
    z_again = U.add_zombie(st, "stz")
    vil = st.actor("stv", "farmer")
    zv = U.add_zombie_villager(st, "stzv", "farmer")
    say("add_zombie registers and is idempotent", st.cast["stz"] is z and z_again is z and st.cast["stzv"] is zv)
    f2 = s2.frame_start
    z.place(f2, (0.0, 30.0, 0.0), math.radians(180))
    vil.place(s1.frame_start, (0.0, 31.3, 0.0), 0.0)
    st.use(s1, vil)
    st.use(s2, z, vil, zv)
    st.use(s3, zv)
    z.attack(f2 + 5, target=vil, max_back=0.2)
    z.attack(f2 + 29)
    U.infect(vil, zv, f2 + 29, attacker=z, max_back=0.2)
    st.finish()
    f1, f3 = s1.frame_start, s3.frame_start
    rows = {"shot1": (vis(z, f1 + 5), vis(vil, f1 + 5), vis(zv, f1 + 5)),
            "shot2 start": (vis(z, f2), vis(vil, f2), vis(zv, f2)),
            "flash": (vis(z, f2 + 6), vis(vil, f2 + 6), vis(zv, f2 + 6)),
            "after infect": (vis(z, f2 + 30), vis(vil, f2 + 30), vis(zv, f2 + 30)),
            "shot3": (vis(z, f3 + 2), vis(vil, f3 + 2), vis(zv, f3 + 2))}
    for k, r in rows.items():
        print("     %-12s zombie %s villager %s zombie villager %s" % (k, r[0], r[1], r[2]))
    say("Stage: zombie hidden in shots 1 and 3", rows["shot1"][0] == (0, 0) and rows["shot3"][0] == (0, 0) and rows["shot2 start"][0][0] == 6)
    say("Stage: villager shown in shot 1, red during the flash, gone after the infection",
        rows["shot1"][1][0] > 0 and rows["flash"][1][0] == 0 and rows["flash"][1][1] > 0 and rows["after infect"][1] == (0, 0))
    say("Stage: zombie villager not rendered before the infection although st.use() lists it; there in shot 3",
        rows["shot2 start"][2] == (0, 0) and rows["after infect"][2][0] > 0 and rows["shot3"][2][0] > 0)
    zv_pos = zv.pos_at(f2 + 60)
    say("infect in a 1x1 cell (max_back 0.2): stays within 0.2 of the spot", abs(zv_pos.y - 31.3) <= 0.2 + 1e-6 and abs(zv_pos.x) < 1e-6, str(tuple(round(q, 3) for q in zv_pos)))
    top = max(zv.pos_at(f2 + 29 + k * 0.5).z for k in range(40))
    print("     infected in a cell: hop apex %.3f (2.125 tall mob + hop = %.3f: needs that headroom)" % (top, top + 2.125))

    # ------------------------------------------------------------ hold / throw / cure
    steve = ch.make_player("p_steve")
    apple = props.make_item("golden_apple")
    steve.hold(apple)
    steve.place(1, (0.0, 40.0, 0.0), math.radians(180))
    steve.show(1, True)
    czv = U.make_zombie_villager("c_zv", "librarian")
    czv.place(1, (0.0, 43.5, 0.0), 0.0)
    czv.show(1, True)
    cv = ch.make_villager("c_v", "librarian")
    cv.show(1, True)
    hit = U.throw_potion(steve, czv, 1, camera=cam)
    say("throw at frame 1: impact later, bottle shown from 1", int(hit) > 1 and hit.frames[0] == 1, "impact %d speed %.2f hit %s" % (int(hit), hit.speed, tuple(round(q, 2) for q in hit.hit)))
    out = U.cure(czv, cv, int(hit) + 10, int(hit) + 82, camera=cam, player=steve, weakness_from=int(hit))
    fe = out["frame_end"]
    say("cure: zombie villager before, villager after", vis(czv, fe - 1)[0] > 0 and vis(cv, fe - 1) == (0, 0) and vis(czv, fe) == (0, 0) and vis(cv, fe)[0] > 0,
        "%s %s | %s %s" % (vis(czv, fe - 1), vis(cv, fe - 1), vis(czv, fe), vis(cv, fe)))
    say("cure: the villager is NOT rendered before the cure (frame 1..end-1) though show(1, True) was keyed", vis(cv, 1) == (0, 0) and vis(cv, fe - 20) == (0, 0), "%s" % (vis(cv, 1),))
    scene.frame_set(fe + 3)
    say("apple consumed and stays consumed after a later show()", apple.scale[0] < 0.01)
    steve.show(fe + 5, True)
    scene.frame_set(fe + 6)
    say("  ... after Character.show at a later shot start", apple.scale[0] < 0.01 and not apple.hide_render, "scale %.4f hide %s" % (apple.scale[0], apple.hide_render))
    # a far throw
    try:
        far = U.throw_potion((0.0, 0.0, 1.52), (9.0, 0.0, 0.0), 200, camera=cam, count=10)
        say("throw 9 blocks: speed raised, arrives", far.speed > 0.5, "speed %.2f, %d frames of flight" % (far.speed, int(far) - 200))
    except Exception as exc:
        say("throw 9 blocks", False, repr(exc))
    # particles stop at a time cut
    n_before = sum(1 for bu in fx._BURSTS for p in bu.particles if p["first"] <= 300 < p["last"])
    lone = U.effect_swirls(czv, 250, 400, "strength", camera=cam)
    alive = sum(1 for p in lone.particles if p["first"] <= 300 < p["last"])
    ended = fx.stop_particles(300)
    alive2 = sum(1 for p in lone.particles if p["first"] <= 300 < p["last"])
    late = sum(1 for p in lone.particles if p["first"] > 300 and p["last"] > p["first"])
    say("fx.stop_particles(300) ends the swirls alive at 300", alive > 0 and alive2 == 0, "%d alive -> %d; ended %d; particles that would still APPEAR after 300: %d" % (alive, alive2, ended, late))
    scene.frame_set(330)
    still = [o.name for o in lone.objects if not o.hide_render]
    say("... and none of that burst is rendered at frame 330", not still, "%d rendered" % len(still))

    # ------------------------------------------------------------ feet in a walk with a corner + keys inside the shutter rule
    w = U.make_zombie("corner")
    w.place(1, (20.0, 0.0, 0.0), math.radians(90))
    end = w.walk(1, [(20.0, 0.0, 0.0), (24.0, 0.0, 0.0), (24.0, 4.0, 0.0)])
    info = w.last_walk
    print("     corner walk:", {k: (round(x, 3) if isinstance(x, float) else x) for k, x in info.items()}, "end", end)
    yaws = [round(math.degrees(w.yaw_at(f)), 1) for f in range(38, 56, 2)]
    print("     yaw through the corner (frames 38..54):", yaws)
    # speed on the first and last frame (no ease)
    v_first = (w.pos_at(2) - w.pos_at(1)).length * 24.0
    print("     speed on the first frame: %.2f blocks/s (no ease in)" % v_first)

    # very short walk
    w2 = U.make_zombie("short")
    w2.place(1, (30.0, 0.0, 0.0), math.radians(90))
    e = w2.walk(1, [(30.0, 0.0, 0.0), (30.4, 0.0, 0.0)])
    print("     0.4-block walk:", e, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in w2.last_walk.items()})

    # hide keys: CONSTANT and on integer frames?
    bad = []
    for c_ in (v, dz, z, vil, zv, czv, cv):
        for ob in list(c_.objects()) + list((c_.__dict__.get(U._STATE) or {}).get("twins", {}).values()):
            fc = ch._find(ob, "hide_render", 0)
            if fc is None:
                continue
            for kp in fc.keyframe_points:
                if kp.interpolation != "CONSTANT" or abs(kp.co.x - round(kp.co.x)) > 1e-6:
                    bad.append((ob.name, kp.co.x, kp.interpolation))
    say("visibility keys are CONSTANT on whole frames", not bad, str(bad[:3]))
    print("PROBE: %d of %d ok" % (sum(res), len(res)))


if __name__ == "__main__":
    main()
