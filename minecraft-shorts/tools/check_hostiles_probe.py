"""Reviewer's numeric probe of engine.hostiles: calls twice, frame 1, cuts, several instances, edge cases.

    $BPY -m tools.check_hostiles_probe
"""
import math

import bpy
from mathutils import Vector

from engine import characters as ch
from engine import hostiles, players, shots, undead
from films import lookdev as L


def shown(ob, f):
    bpy.context.scene.frame_set(int(f), subframe=float(f) - int(f))
    return not ob.hide_render


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.frame_start, scene.frame_end = 1, 300
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    scene.collection.objects.link(cam)
    scene.camera = cam

    # ---- frame 1: fuse, draw, hit all on frame 1
    cr = hostiles.make_creeper("c1")
    cr.place(1, (0, 0, 0), 0.0)
    boom = cr.fuse(1)
    print("fuse(1) explodes on", boom, "white frames", [f for f in range(1, 40) if cr.white_at(f) > 0][:8])
    whites = [f for f in range(0, 40) if any(shown(o, f) for obs in cr._shells.values() for o in obs)]
    print("  shells rendered on", whites[:12], "...")
    steve = players.make_player("st1", "steve")
    steve.place(1, (3, 0, 0), 0.0)
    a1 = hostiles.hit(steve, 1, "chest", hurt=False)
    print("hit on frame 1: shown at 0/1/2:", shown(a1, 0), shown(a1, 1), shown(a1, 2))
    sk = hostiles.make_skeleton("s1")
    sk.place(1, (0, 8, 0), math.pi)
    d = sk.draw(1, target=steve)
    print("draw(1): release", d["frame"], "bow at 1/17/23/25:", [sk.bow_at(f) for f in (1, 17, 23, 25)])
    print("  bow objects shown at 1:", [k for k, o in sk.bows.items() if shown(o, 1)])

    # ---- called twice
    a2 = hostiles.hit(steve, 10, "chest", hurt=False)
    m1, m2 = a1.matrix_basis.copy(), a2.matrix_basis.copy()
    print("hit twice on the same spot: identical placement (coplanar twin) =", (m1 - m2).to_3x3().is_zero if hasattr(
        (m1 - m2).to_3x3(), "is_zero") else max(abs(x) for row in (m1 - m2) for x in row) < 1e-9, a1.name, a2.name)
    fA = hostiles.fire(sk, (2.0, 2.0, 0.0), 60)
    fB = hostiles.fire(sk, (2.0, 2.0, 0.0), 60)
    print("fire twice same frame: names", fA.arrow.name, fB.arrow.name)
    sk.draw(100, target=steve)
    sk.draw(110, target=steve)
    print("two overlapping draws (100, 110): bow at 105/112/124/126/134/135:",
          [sk.bow_at(f) for f in (105, 112, 124, 126, 134, 135)])
    again = hostiles.make_creeper("c1")
    print("make_creeper twice with one name: second root", again.root.name, "first root", cr.root.name)

    # ---- several instances: two creepers fusing at once, independent shells
    c2 = hostiles.make_creeper("c2")
    c2.place(1, (6, 0, 0), 0.0)
    c2.fuse(20)
    f = 25
    on1 = [o.name for obs in cr._shells.values() for o in obs if shown(o, f)]
    on2 = [o.name for obs in c2._shells.values() for o in obs if shown(o, f)]
    print("frame %d: c1 white %.2f shells %d ; c2 white %.2f shells %d" % (f, cr.white_at(f), len(on1), c2.white_at(f), len(on2)))

    # ---- a cut in the middle of a fuse: place() again
    c3 = hostiles.make_creeper("c3")
    c3.place(1, (10, 0, 0), 0.0)
    c3.fuse(10)
    c3.place(25, (10, 5, 0), 0.0)
    print("cut at 25 in mid-fuse: swelling 24 %.2f, 25 %.2f, 30 %.2f, 60 %.2f" % tuple(c3.swelling_at(f) for f in (24, 25, 30, 60)))
    c3.fuse(40)
    c3.place(50, (10, 8, 0), 0.0, keep_pose=True)
    print("keep_pose=True cut at 50 of a fuse from 40: swelling 49 %.2f 50 %.2f 55 %.2f" % tuple(c3.swelling_at(f) for f in (49, 50, 55)))

    # ---- skeleton dies while drawing; bows after death
    s2 = hostiles.make_skeleton("s2")
    s2.place(1, (14, 8, 0), math.pi)
    s2.draw(30, target=steve)
    gone = s2.die(40)
    print("skeleton dies at 40 while drawing: gone", gone, "bows shown at 45/%d:" % (gone + 1),
          [k for k, o in s2.bows.items() if shown(o, 45)], [k for k, o in s2.bows.items() if shown(o, gone + 1)])
    print("   bow model while dying (frame 45):", s2.bow_at(45))

    # ---- an arrow at a walking target
    walker = players.make_player("st2", "steve")
    walker.place(1, (20, 0, 0), math.pi / 2)
    walker.walk(1, [(20, 0, 0), (30, 0, 0)])
    s3 = hostiles.make_skeleton("s3")
    s3.place(1, (25, 10, 0), math.pi)
    try:
        fl = s3.shoot(10, walker, part="chest", knockback=0.0)
        print("shot at a walking player: loosed", fl.frames[0], "impact", int(fl), "hit point",
              tuple(round(c, 2) for c in fl.hit), "player at impact", tuple(round(c, 2) for c in walker.pos_at(int(fl))))
    except ValueError as e:
        print("shot at a walking player (4.3 blocks/s across the line of fire, 10 blocks away): ValueError:", e)
    cw = hostiles.make_creeper("cw")
    cw.place(1, (20, -6, 0), math.pi / 2)
    cw.walk(1, [(20, -6, 0), (30, -6, 0)], speed=hostiles.CREEPER_STROLL)
    try:
        fl = s3.shoot(40, cw)
        print("shot at a strolling creeper: impact", int(fl))
    except ValueError as e:
        print("shot at a strolling creeper (1.76 blocks/s, 16 blocks away): ValueError:", e)

    # ---- explosion victims: player, villager, zombie at 2 / 4 / 7 blocks
    c4 = hostiles.make_creeper("c4")
    c4.place(1, (40, 0, 0), 0.0)
    pl = players.make_player("st3", "steve")
    pl.place(1, (42, 0, 0), 0.0)
    vi = ch.make_villager("v1", "farmer")
    vi.place(1, (40, 4, 0), 0.0)
    zo = undead.make_zombie("z1")
    zo.place(1, (47, 0, 0), 0.0)
    end = c4.fuse(5)
    centre = c4.explode(end, victims=[pl, vi, zo], blocks=40, camera=cam)
    print("explode on", end, "pushed", c4.last_explosion["pushed"])
    for c in (pl, vi, zo):
        print("   %s at %d: %s -> %d: %s" % (c.name, end, tuple(round(x, 2) for x in c.pos_at(end)), end + 14,
                                          tuple(round(x, 2) for x in c.pos_at(end + 14))))
    c4_meshes = [o for o in c4.objects() if o.type == "MESH"]
    print("   creeper rendered on explode frame -1/0:", any(shown(o, end - 1) for o in c4_meshes), any(shown(o, end) for o in c4_meshes))

    # ---- Stage across a cut: fusing creeper in shot a, absent in b, back (placed) in c
    film = shots.Film(scene, fps=24)
    sa, sb, sc = film.shot("a", 20.0, 21.0), film.shot("b", 21.0, 22.0), film.shot("c", 22.0, 23.0)
    st = L.Stage(scene, film, None, None)
    st.in_shot.update({"a": set(), "b": set(), "c": set()})
    c5 = hostiles.add_creeper(st, "c5")
    sk5 = hostiles.add_skeleton(st, "s5")
    p5 = players.add_player(st, "p5", "steve")
    c5.place(sa.frame_start, (60, 0, 0), 0.0)
    sk5.place(sa.frame_start, (60, 8, 0), math.pi)
    p5.place(sa.frame_start, (62, 0, 0), 0.0)
    c5.fuse(sa.frame_start + 2)
    sk5.draw(sa.frame_start + 10, release=sc.frame_start + 5, target=p5)
    ar = hostiles.hit(p5, sa.frame_start + 5, "back", hurt=False)
    c5.place(sc.frame_start, (60, 2, 0), 0.0)
    sk5.place(sc.frame_start, (60, 9, 0), math.pi)
    st.use(sa, c5, sk5, p5)
    st.use(sb, p5)
    st.use(sc, c5, sk5)
    st.finish()
    for f in (sa.frame_end, sb.frame_start, sb.frame_end, sc.frame_start, sc.frame_start + 4):
        vis = sorted(o.name for o in scene.objects if o.type == "MESH" and o.name.startswith(("c5", "s5", "p5_arrow"))
                     and shown(o, f))
        print("  stage frame %d (%s): %s" % (f, film.shot_at(f).name, sorted({n.split("_")[0] + ("_" + n.split("_")[1] if
              n.startswith(("s5_bow", "p5_arrow")) else "") for n in vis})))
    print("  c5 swelling at shot c start %.2f; skeleton bow at shot c start %s, aiming %.2f" % (
        c5.swelling_at(sc.frame_start), sk5.bow_at(sc.frame_start), sk5.aiming_at(sc.frame_start)))


if __name__ == "__main__" and len(__import__("sys").argv) == 1:
    main()


def deaths():
    """Stuck arrows when the character dies (players.die, undead.die on a villager) and after a later place()."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    scene.collection.objects.link(cam)
    p = players.make_player("pd", "steve")
    p.place(1, (0, 0, 0), 0.0)
    ar = hostiles.hit(p, 5, "back", hurt=False)
    info = p.die(20, camera=cam)
    gone = info["frame"]
    torso = [o for o in p.parts.values() if o.type == "MESH"]
    print("player dies at 20, gone %d: arrow shown at %d/%d/%d: %s; body shown at %d: %s" % (
        gone, gone - 1, gone, gone + 5, [shown(ar, f) for f in (gone - 1, gone, gone + 5)], gone + 5,
        any(shown(o, gone + 5) for o in torso)))
    p.place(gone + 20, (3, 0, 0), 0.0)
    print("   placed again at %d: arrow shown %s (body %s)" % (gone + 20, shown(ar, gone + 21),
                                                             any(shown(o, gone + 21) for o in torso)))
    v = ch.make_villager("vd", "farmer")
    v.place(1, (6, 0, 0), 0.0)
    av = hostiles.hit(v, 5, "chest", hurt=False)
    g = undead.die(v, 20, camera=cam)
    print("villager undead.die at 20 -> gone %s: arrow shown at 30 / gone+2: %s %s" % (
        g, shown(av, 30), shown(av, (g if isinstance(g, int) else g["frame"]) + 2)))


if __name__ == "__main__" and len(__import__("sys").argv) > 1 and __import__("sys").argv[1] == "deaths":
    deaths()
