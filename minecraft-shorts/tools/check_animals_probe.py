"""Independent checker's probe of engine/animals.py (numbers only; the film probe is tools/check_animals_probe_film.py).

Run:  $BPY -m tools.check_animals_probe [uv] [robust]

uv      every polygon of the four rigs against my own transcription of the client's model classes and my own
        implementation of ModelPart.Cube's box unwrap (not the engine's): position -> texel, and texel coverage.
robust  what a director does by accident: import only, called twice, at frame 1, across a cut, six at once, Stage.
"""
import math
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

PI2 = math.pi / 2.0

# my transcription from javap of CowModel / BabyCowModel / AdultChickenModel / BabyChickenModel (26.x client jar):
# part: (offset xyz, rot xyz, [(texU, texV, x, y, z, w, h, d, mirror)])
MODELS = {
    "cow": ((64, 64), {
        "head": ((0, 4, -8), (0, 0, 0), [(0, 0, -4, -4, -6, 8, 8, 6, False), (1, 33, -3, 1, -7, 6, 3, 1, False),
                                         (22, 0, -5, -5, -5, 1, 3, 1, False), (22, 0, 4, -5, -5, 1, 3, 1, False)]),
        "body": ((0, 5, 2), (PI2, 0, 0), [(18, 4, -6, -10, -7, 12, 18, 10, False), (52, 0, -2, 2, -8, 4, 6, 1, False)]),
        "right_hind_leg": ((-4, 12, 7), (0, 0, 0), [(0, 16, -2, 0, -2, 4, 12, 4, False)]),
        "left_hind_leg": ((4, 12, 7), (0, 0, 0), [(0, 16, -2, 0, -2, 4, 12, 4, True)]),
        "right_front_leg": ((-4, 12, -5), (0, 0, 0), [(0, 16, -2, 0, -2, 4, 12, 4, False)]),
        "left_front_leg": ((4, 12, -5), (0, 0, 0), [(0, 16, -2, 0, -2, 4, 12, 4, True)]),
    }),
    "calf": ((64, 64), {
        "head": ((0, 13.569, -5.1667), (0, 0, 0), [(0, 18, -3, -4.569, -4.8333, 6, 6, 5, False),
                                                    (8, 29, 3, -5.569, -3.8333, 1, 2, 1, False),
                                                    (4, 29, -4, -5.569, -3.8333, 1, 2, 1, True),
                                                    (12, 29, -2, -1.569, -5.8333, 4, 3, 1, False)]),
        "body": ((3, 19, -5), (0, 0, 0), [(0, 0, -7, -7, -1, 8, 6, 12, False)]),
        "right_front_leg": ((-2.5, 18, -3.5), (0, 0, 0), [(22, 18, -1.5, 0, -1.5, 3, 6, 3, False)]),
        "left_front_leg": ((2.5, 18, -3.5), (0, 0, 0), [(34, 18, -1.5, 0, -1.5, 3, 6, 3, False)]),
        "right_hind_leg": ((-2.5, 18, 3.5), (0, 0, 0), [(22, 27, -1.5, 0, -1.5, 3, 6, 3, False)]),
        "left_hind_leg": ((2.5, 18, 3.5), (0, 0, 0), [(34, 27, -1.5, 0, -1.5, 3, 6, 3, False)]),
    }),
    "chicken": ((64, 32), {
        "head": ((0, 15, -4), (0, 0, 0), [(0, 0, -2, -6, -2, 4, 6, 3, False), (14, 0, -2, -4, -4, 4, 2, 2, False),
                                          (14, 4, -1, -2, -3, 2, 2, 2, False)]),
        "body": ((0, 16, 0), (PI2, 0, 0), [(0, 9, -3, -4, -3, 6, 8, 6, False)]),
        "right_leg": ((-2, 19, 1), (0, 0, 0), [(26, 0, -1, 0, -3, 3, 5, 3, False)]),
        "left_leg": ((1, 19, 1), (0, 0, 0), [(26, 0, -1, 0, -3, 3, 5, 3, False)]),
        "right_wing": ((-4, 13, 0), (0, 0, 0), [(24, 13, 0, 0, -3, 1, 4, 6, False)]),
        "left_wing": ((4, 13, 0), (0, 0, 0), [(24, 13, -1, 0, -3, 1, 4, 6, False)]),
    }),
    "chick": ((16, 16), {
        "body": ((0, 20.25, -1.25), (0, 0, 0), [(0, 0, -2, -2.25, -0.75, 4, 4, 4, False),
                                                (10, 8, -1, -0.25, -1.75, 2, 1, 1, False)]),
        "left_leg": ((1, 22, 0.5), (0, 0, 0), [(2, 2, -0.5, 0, 0, 1, 2, 0, False), (0, 1, -0.5, 2, -1, 1, 0, 1, False)]),
        "right_leg": ((-1, 22, 0.5), (0, 0, 0), [(0, 2, -0.5, 0, 0, 1, 2, 0, False), (0, 0, -0.5, 2, -1, 1, 0, 1, False)]),
        "right_wing": ((2, 20, 0), (0, 0, 0), [(6, 8, 0, 0, -1, 1, 0, 2, False)]),
        "left_wing": ((-2, 20, 0), (0, 0, 0), [(4, 8, -1, 0, -1, 1, 0, 2, False)]),
    }),
}


def face_texels(cube, q, eps=0.03):
    """My own ModelPart.Cube unwrap: [(face name, u, v)] for a point q (cube space) lying on a face of the cube."""
    tu, tv, x, y, z, w, h, d, mirror = cube
    x0, y0, z0, x1, y1, z1 = x, y, z, x + w, y + h, z + d
    U0, U1, U2, U22, U3, U4 = tu, tu + d, tu + d + w, tu + d + w + w, tu + d + w + d, tu + d + w + d + w
    V0, V1, V2 = tv, tv + d, tv + d + h
    qx, qy, qz = q
    if not (x0 - eps <= qx <= x1 + eps and y0 - eps <= qy <= y1 + eps and z0 - eps <= qz <= z1 + eps):
        return []
    gx = (x0 + x1 - qx) if mirror else qx          # the vertex roles x0 <-> x1 are swapped by .mirror()
    out = []
    if abs(qy - y0) < eps and w > 0 and d > 0:
        out.append(("top", U1 + (gx - x0), V1 - (qz - z0)))
    if abs(qy - y1) < eps and w > 0 and d > 0:
        out.append(("bottom", U2 + (gx - x0), V1 - (qz - z0)))
    if abs(gx - x0) < eps and d > 0 and h > 0:
        out.append(("west", U1 - (qz - z0), V1 + (qy - y0)))
    if abs(gx - x1) < eps and d > 0 and h > 0:
        out.append(("east", U2 + (qz - z0), V1 + (qy - y0)))
    if abs(qz - z0) < eps and w > 0 and h > 0:
        out.append(("north", U1 + (gx - x0), V1 + (qy - y0)))
    if abs(qz - z1) < eps and w > 0 and h > 0:
        out.append(("south", U4 - (gx - x0), V1 + (qy - y0)))
    return out


def face_rects(cube):
    """The six texture rectangles (u0, v0, u1, v1) of a cube, zero-area ones left out."""
    tu, tv, x, y, z, w, h, d, _m = cube
    rects = [(tu + d, tv, tu + d + w, tv + d), (tu + d + w, tv, tu + d + w + w, tv + d),
             (tu, tv + d, tu + d, tv + d + h), (tu + d, tv + d, tu + d + w, tv + d + h),
             (tu + d + w, tv + d, tu + d + w + d, tv + d + h), (tu + d + w + d, tv + d, tu + d + w + d + w, tv + d + h)]
    return [r for r in rects if r[2] > r[0] and r[3] > r[1]]


def check_uv():
    from engine import animals, characters as ch, quick

    scene = quick.reset()
    good = True
    makers = {"cow": lambda: animals.make_cow("cow"), "calf": lambda: animals.make_cow("calf", baby=True),
              "chicken": lambda: animals.make_chicken("hen"), "chick": lambda: animals.make_chicken("chick", baby=True)}
    tex = {"cow": "entity/cow/cow_temperate", "calf": "entity/cow/cow_temperate_baby",
           "chicken": "entity/chicken/chicken_temperate", "chick": "entity/chicken/chicken_temperate_baby"}
    for kind, make in makers.items():
        a = make()
        a.place(1, (0, 0, 0), 0.0)
        scene.frame_set(1)
        bpy.context.view_layer.update()
        (W, H), parts = MODELS[kind]
        sheet = np.array(ch._game_texture(tex[kind]))
        assert sheet.shape[:2] == (H, W), (sheet.shape, W, H)
        lift = animals.GROUND_EPS if kind in ("chicken", "chick") else 0.0
        polys = bad = 0
        area = 0.0
        worst = 0.0
        examples = []
        for ob in a.mesh_parts():
            me = ob.data
            uvl = me.uv_layers[0].data
            for p in me.polygons:
                c = ob.matrix_world @ p.center
                pm = Vector((c.x * 16.0, 24.0 - (c.z - lift) * 16.0, c.y * 16.0))
                uvs = [uvl[i].uv for i in p.loop_indices]
                u = sum(t[0] for t in uvs) / len(uvs) * W
                v = (1.0 - sum(t[1] for t in uvs) / len(uvs)) * H
                du = (max(t[0] for t in uvs) - min(t[0] for t in uvs)) * W
                dv = (max(t[1] for t in uvs) - min(t[1] for t in uvs)) * H
                area += (du + 0.04) * (dv + 0.04)
                polys += 1
                best = 1e9
                for name, (off, rot, cubes) in parts.items():
                    m = Matrix.Translation(off) @ Matrix.Rotation(rot[2], 4, "Z") @ Matrix.Rotation(rot[1], 4, "Y") \
                        @ Matrix.Rotation(rot[0], 4, "X")
                    q = m.inverted() @ pm
                    for cube in cubes:
                        for _face, eu, ev in face_texels(cube, q):
                            best = min(best, max(abs(eu - u), abs(ev - v)))
                # the texel must also be opaque
                opaque = sheet[int(min(max(v, 0), H - 1)), int(min(max(u, 0), W - 1)), 3] >= 26
                if best > 0.06 or not opaque:
                    bad += 1
                    if len(examples) < 4:
                        examples.append((ob.name, tuple(round(k, 2) for k in pm), round(u, 2), round(v, 2), round(best, 3), opaque))
                worst = max(worst, best if best < 1e8 else 0.0)
        want = 0
        for name, (off, rot, cubes) in parts.items():
            for cube in cubes:
                for (u0, v0, u1, v1) in face_rects(cube):
                    want += int((sheet[int(v0):int(v1), int(u0):int(u1), 3] >= 26).sum())
        ok = bad == 0 and abs(area - want) < 0.5
        good &= ok
        print("%s %-7s %3d polygons, %d off their texel (worst %.3f px), opaque texels drawn %.1f of %d %s" % (
            "ok  " if ok else "FAIL", kind, polys, bad, worst, area, want, examples if examples else ""))
    return good


def check_robust():
    import importlib

    from engine import quick

    scene = quick.reset()
    res = []

    def expect(label, cond, detail=""):
        res.append(bool(cond))
        print("%s %s%s" % ("ok  " if cond else "FAIL", label, (": " + str(detail)) if detail != "" else ""))

    def ev(f):
        whole = int(math.floor(f))
        scene.frame_set(whole, subframe=float(f) - whole)
        bpy.context.view_layer.update()

    # ---- import leaves the scene untouched
    counts0 = {k: len(getattr(bpy.data, k)) for k in ("objects", "meshes", "materials", "images", "actions", "collections")}
    animals = importlib.import_module("engine.animals")
    from engine import characters as ch, fx, mobs, shots, village  # noqa: F401
    counts1 = {k: len(getattr(bpy.data, k)) for k in counts0}
    expect("import engine.animals creates no datablocks", counts0 == counts1, (counts0, counts1))

    # ---- frame 1: place, hurt, die on the first frame of a film
    cow = animals.make_cow("c1")
    cow.place(1, (0, 0, 0), 0.0)
    try:
        e = cow.hurt(1, attacker=(0, -2, 0))
        ev(1)
        red1 = (cow.body.hide_render, cow._twins["body"].hide_render)
        ev(0)
        red0 = (cow.body.hide_render, cow._twins["body"].hide_render)
        expect("hurt on frame 1: red on frame 1 %s, normal on frame 0 %s, stands at %d" % (red1, red0, e),
               red1 == (True, False) and red0 == (False, True))
    except Exception as ex:                                              # noqa: BLE001
        expect("hurt on frame 1", False, repr(ex))
    hen = animals.make_chicken("h1")
    hen.place(1, (3, 0, 0), 0.0)
    try:
        cam = quick.camera(scene, (6, -6, 2), (0, 0, 0.5))
        g = hen.die(1, camera=cam)
        ev(1)
        s1 = (hen.body.hide_render, hen._twins["body"].hide_render)
        ev(g)
        s2 = (hen.body.hide_render, hen._twins["body"].hide_render)
        expect("die on frame 1: red on frame 1 %s, gone on %d %s" % (s1, g, s2), s1 == (True, False) and s2 == (True, True) and g == 25)
    except Exception as ex:                                              # noqa: BLE001
        expect("die on frame 1", False, repr(ex))

    # ---- called twice: hurt in the middle of a hurt, die after die, die during hurt, hurt after death
    cow2 = animals.make_cow("c2")
    cow2.place(100, (0, 10, 0), 0.0)
    e1 = cow2.hurt(110, attacker=(0, 8, 0))
    e2 = cow2.hurt(116, attacker=(0, 8, 0))                               # second blow while still in the air and red
    zs = [cow2.pos_at(f).z for f in np.arange(110, e2 + 20, 0.25)]
    ys = [cow2.pos_at(f).y for f in np.arange(110, e2 + 20, 0.25)]
    ev(121.9)
    r_a = not cow2._twins["body"].hide_render
    ev(127)
    r_b = not cow2._twins["body"].hide_render
    ev(128)
    r_c = not cow2._twins["body"].hide_render
    ev(e2 + 40)
    rest = (round(cow2.root.location.z, 4), [round(o.rotation_euler.x, 4) for o in cow2.legs.values()])
    expect("second hurt 6 frames into the first: in the air z at the 2nd blow %.2f, peak %.2f, no jump in y (max step %.3f), "
           "red through 127 (%s %s) off at 128 (%s), rests %s" % (
               cow2.pos_at(116).z, max(zs), max(abs(b - a) for a, b in zip(ys, ys[1:])), r_a, r_b, r_c, rest),
           r_a and r_b and not r_c and rest[0] == 0.0 and all(v == 0.0 for v in rest[1])
           and max(abs(b - a) for a, b in zip(zs, zs[1:])) < 0.2 and max(abs(b - a) for a, b in zip(ys, ys[1:])) < 0.2)
    # (the game: a mob in the air keeps its vertical speed on the second blow: knockback() only lifts it if onGround)
    vz = (cow2.pos_at(116.6).z - cow2.pos_at(116.0).z) / 0.6
    print("     after the 2nd blow in mid-air the vertical speed is %+.3f blocks/frame (game: unchanged, it was %+.3f)" % (
        vz, (cow2.pos_at(116.0).z - cow2.pos_at(115.4).z) / 0.6))

    cow3 = animals.make_cow("c3")
    cow3.place(200, (0, 20, 0), 0.0)
    cow3.walk(200, [(0, 20, 0), (0, 14, 0)])
    cow3.hurt(220, attacker=(0, 16, 0))
    g3 = cow3.die(226, camera=cam, attacker=(0, 16, 0))
    states = {}
    for f in (219, 220, 225, 226, 231, 232, 240, g3 - 1, g3, g3 + 5):
        ev(f)
        states[f] = (not cow3.body.hide_render, not cow3._twins["body"].hide_render)
    expect("die 6 frames after a hurt in mid-walk: red from 220 to %d without a gap, gone on %d: %s" % (g3 - 1, g3, states),
           all(states[f] == (False, True) for f in (220, 225, 226, 231, 232, 240, g3 - 1)) and states[g3] == (False, False)
           and states[219] == (True, False))
    ev(g3 - 1)
    tip = math.degrees(cow3.root.rotation_euler.y)
    legs = [round(math.degrees(o.rotation_euler.x), 1) for o in cow3.legs.values()]
    expect("... lying at %.1f degrees with straight legs %s on the last frame" % (tip, legs), abs(tip - 90) < 0.1 and not any(legs))
    try:
        g3b = cow3.die(g3 + 10, camera=cam)                               # a director's slip: killed twice
        ev(g3 + 12)
        st2 = (not cow3.body.hide_render, not cow3._twins["body"].hide_render)
        expect("die() on an animal that is already gone shows nothing %s" % (st2,), st2 == (False, False), "it reappears red")
    except Exception as ex:                                              # noqa: BLE001
        expect("die() twice", False, repr(ex))
    try:
        cow3.hurt(g3 + 60)
        ev(g3 + 62)
        st3 = (not cow3.body.hide_render, not cow3._twins["body"].hide_render)
        expect("hurt() on an animal that is gone shows nothing %s" % (st3,), st3 == (False, False), "it reappears red")
    except Exception as ex:                                              # noqa: BLE001
        expect("hurt() after death", False, repr(ex))
    cow3.place(g3 + 100, (0, 20, 0), 0.5)
    ev(g3 + 100)
    expect("place() brings it back upright and normal", not cow3.body.hide_render and cow3._twins["body"].hide_render
           and abs(cow3.root.rotation_euler.y) < 1e-9 and abs(cow3.root.rotation_euler.z - 0.5) < 1e-9)

    # ---- across a cut: walking in shot A, placed in shot B: the last frame of A (exposed f..f+0.5) is no ghost
    cow4 = animals.make_cow("c4")
    cow4.place(300, (0, 30, 0), math.radians(90))
    cow4.walk(300, [(0, 30, 0), (8, 30, 0)])
    cow4.look_at(310, (4, 25, 1.0))
    cut = 340
    cow4.place(cut, (20, 40, 0), math.radians(-90))
    a0, a1 = cow4.pos_at(cut - 1), cow4.pos_at(cut - 0.5)
    ev(cut - 0.5)
    pose_pre = [round(o.rotation_euler.x, 3) for o in cow4.legs.values()]
    ev(cut)
    pose_post = [round(o.rotation_euler.x, 4) for o in cow4.legs.values()] + [round(cow4.head.rotation_euler.z, 4),
                                                                              round(cow4.hips.location.z - cow4._rest(cow4.hips, "location", 2), 4)]
    expect("cut at %d: frame %d is exposed on the walk (x %.2f -> %.2f, legs %s), frame %d is at the new spot, neutral %s" % (
        cut, cut - 1, a0.x, a1.x, pose_pre, cut, pose_post),
        a1.x > a0.x and a1.x < 9 and any(abs(v) > 0.05 for v in pose_pre) and (cow4.pos_at(cut) - Vector((20, 40, 0))).length < 1e-6
        and not any(pose_post))
    # a hurt flash and a hand item cut by the next shot's place()
    cow4.hurt(400)
    cow4.place(405, (20, 40, 0), 0.0)
    ev(405)
    expect("place() 5 frames into a red flash ends the flash", not cow4.body.hide_render and cow4._twins["body"].hide_render)

    # ---- walk() and wander() called twice over the same frames; the same call twice
    cow5 = animals.make_cow("c5")
    cow5.place(500, (0, 50, 0), 0.0)
    cow5.walk(500, [(0, 50, 0), (0, 44, 0)])
    endb = cow5.walk(520, [cow5.pos_at(520), (5, 48, 0)])                 # re-directed in mid-walk
    xs = [cow5.pos_at(f) for f in np.arange(500, endb + 1, 0.5)]
    step = max((b - a).length for a, b in zip(xs, xs[1:]))
    yaws = [cow5.yaw_at(f) for f in np.arange(500, endb + 1, 0.5)]
    ystep = max(abs(b - a) for a, b in zip(yaws, yaws[1:]))
    expect("a second walk() in mid-walk: no jump (largest half-frame step %.3f blocks, %.1f degrees)" % (step, math.degrees(ystep)),
           step < 0.09 and ystep < math.radians(25))
    herd = [animals.make_cow("w%d" % i) for i in range(6)]
    area = animals.pen_area(40, 40, 49, 49)
    animals.wander(herd, 600, 720, area, seed=1)
    k1 = sum(len(fc.keyframe_points) for a in herd for o in a.objects() if o.animation_data and o.animation_data.action
             for fc in shots.fcurves_of(o))
    animals.wander(herd, 600, 720, area, seed=1)                          # the same call again (a re-run cell)
    k2 = sum(len(fc.keyframe_points) for a in herd for o in a.objects() if o.animation_data and o.animation_data.action
             for fc in shots.fcurves_of(o))
    gap, edge = animals.pen_report(herd, 600, 760, area)
    expect("wander() twice with the same arguments: %d -> %d keys, gap %.2f, edge %.2f" % (k1, k2, gap, edge),
           gap >= 0.74 and edge >= 0.74 and k2 < k1 * 1.3)
    ev2 = animals.wander(herd, 721, 840, area, seed=2, place=False)       # the next shot goes on
    gap, edge = animals.pen_report(herd, 600, 880, area)
    jump = max((a.pos_at(f + 0.5) - a.pos_at(f)).length for a in herd for f in np.arange(700, 760, 0.5))
    expect("wander(place=False) from frame 721 while walks of the first call still run: gap %.2f, edge %.2f, largest "
           "half-frame step %.3f" % (gap, edge, jump), gap >= 0.74 and edge >= 0.74 and jump < 0.09, ev2 and "")
    # a pen that is too small says so
    try:
        animals.wander([animals.make_cow("x%d" % i) for i in range(6)], 900, 960, animals.pen_area(60, 60, 64, 64), seed=1)
        expect("six cows in a 5 x 5 ring: refused", False, "no error")
    except ValueError as ex:
        expect("six cows in a 5 x 5 ring: refused with a message", True, str(ex)[:70])

    # ---- soles of a wandering herd, measured on the evaluated rigs (not from last_walk)
    worst, where = 0.0, None
    for a in herd[:3]:
        prev = {}
        for f in np.arange(600.0, 880.0, 0.25):
            ev(float(f))
            for leg, ob in a.legs.items():
                p = (ob.matrix_world @ Vector((0.0, 0.0, -a.leg_len))).copy()
                if leg in prev and p.z < 0.004 and prev[leg].z < 0.004:
                    d = (p.xy - prev[leg].xy).length
                    if d > worst:
                        worst, where = d, (a.name, leg, round(float(f), 2))
                prev[leg] = p
    expect("wandering cows: a sole on the ground moves at most %.4f blocks per quarter frame %s" % (worst, where), worst < 0.012)

    # ---- Stage: hidden outside its shots, twins, loot, hand items
    from films.lookdev import Stage

    scene2 = quick.reset()
    film = shots.Film(scene2, fps=24)

    class _V:                                                             # Stage needs only v.lantern_lights here
        lantern_lights = []
    st = Stage(scene2, film, _V(), {})
    sA, sB, sC = st.shot("a", 2.0), st.shot("b", 2.0), st.shot("c", 2.0)
    cow = animals.add_cow(st, "daisy")
    same = animals.add_cow(st, "daisy")
    chick = animals.add_chicken(st, "pip", baby=True)
    hen = animals.add_chicken(st, "hen")
    steve = st.actor("steve", "steve")
    cam = quick.camera(scene2, (6, -6, 2), (0, 0, 0.5))
    expect("add_cow twice returns the same animal; st.cast has it", same is cow and st.cast["daisy"] is cow)
    # shot a: cow + steve with wheat (no frame_end, as the signature allows); shot b: hen dies; shot c: cow again
    cow.place(sA.frame_start, (0, 0, 0), 0.0)
    steve.place(sA.frame_start, (0, -3, 0), math.pi)
    wheat = animals.hand_item(steve, "wheat", sA.frame_start)
    st.use(sA, cow, steve)
    st.hero(sA, "cow", cow)
    st.hero(sA, "chick", chick)
    hen.place(sB.frame_start, (5, 0, 0), 0.0)
    hen.hurt(sB.frame_start + 4)
    g = hen.die(sB.frame_start + 20, camera=cam)
    loot = animals.drop_loot(hen, sB.frame_start + 20, stage=st)          # exactly as the docstring's example line
    st.use(sB, hen)
    cow.place(sC.frame_start, (0, 0, 0), 0.0)
    cow.hurt(sC.frame_start + 2)
    st.use(sC, cow)
    st.finish()

    def vis(ob, f):
        film.goto(f)
        bpy.context.view_layer.update()
        return not ob.hide_render

    mid = {s.name: (s.frame_start + s.frame_end) // 2 for s in film.shots}
    expect("Stage: cow rendered in a, hidden in b, rendered in c",
           vis(cow.body, mid["a"]) and not vis(cow.body, mid["b"]) and vis(cow.body, sC.frame_end))
    expect("Stage: the cow's red twin is hidden in a and b, shown only during its flash in c",
           not vis(cow._twins["body"], mid["a"]) and not vis(cow._twins["body"], mid["b"])
           and vis(cow._twins["body"], sC.frame_start + 3) and not vis(cow._twins["body"], sC.frame_end))
    expect("Stage: the hen (hurt and dying in b) shows nothing in a and c: parts %s twins %s" % (
        [vis(hen.body, mid["a"]), vis(hen.body, mid["c"])], [vis(hen._twins["body"], mid["a"]), vis(hen._twins["body"], mid["c"])]),
        not vis(hen.body, mid["a"]) and not vis(hen._twins["body"], mid["a"]) and not vis(hen.body, mid["c"])
        and not vis(hen._twins["body"], mid["c"]))
    expect("Stage: st.hero(shot, 'chick', chick) gives an object (%s)" % st.heroes["a"][1][1][0].name, st.heroes["a"][1][1][0] is chick.body)
    lv = [vis(it.sprite, g - 1) for it in loot]
    expect("drop_loot(hen, f, stage=st) as in the docstring example: loot visible in its shot %s" % lv, all(lv),
           "the example registers the loot with the Stage but never st.use()s it: Stage.finish hides it for the whole film")
    wv = [vis(wheat, mid["a"]), vis(wheat, mid["b"]), vis(wheat, mid["c"])]
    expect("hand_item(steve, 'wheat', f0) without frame_end: wheat visible in a, b, c = %s while Steve is in a only" % wv,
           wv == [True, False, False], "the item floats where his hand was in every later shot")
    # particles of a death in shot b that are still alive in shot c
    burst = hen.bursts[-1]
    alive_c = sum(1 for q in burst.particles if q["first"] <= sC.frame_start + 2 < q["last"])
    print("     poof of a death %d frames before the cut: %d puffs still alive 2 frames into the next shot (fx.stop_particles needed)"
          % (sC.frame_start - g, alive_c))

    # ---- six at once + every method once on every kind (smoke)
    scene3 = quick.reset()
    cam = quick.camera(scene3, (6, -6, 2), (0, 0, 0.5))
    errs = []
    for kind, mk in (("cow", lambda n: animals.make_cow(n)), ("calf", lambda n: animals.make_cow(n, baby=True)),
                     ("hen", lambda n: animals.make_chicken(n)), ("chick", lambda n: animals.make_chicken(n, baby=True))):
        for i in range(6):
            a = mk("%s%d" % (kind, i))
            x = 3.0 * i
            try:
                a.place(1, (x, 0, 0), 0.3 * i)
                e = a.walk(1, [(x, 0, 0), (x, -3, 0), (x + 1.5, -4, 0)])
                e = a.turn(e, 1.0)
                e = a.face(e, (x + 5, 5, 0))
                a.look_at(e, (x, 10, 2))
                a.track(e, e + 20, cam)
                a.idle(e + 20, e + 120, seed=i)
                e = a.hop(e + 120, (x + 4, 6, 1.0))
                e = a.fall(e + 2, (x + 4, 7, 0.0))
                a.nod(e + 2)
                a.shake(e + 12)
                e = a.flinch(e + 30)
                a.swing_arm(e)
                a.raise_arm(e)
                e = a.hurt(e + 4, attacker=(x, 0, 0), max_back=0.5)
                e = a.walk(e, [a.pos_at(e), (x, 12, 0)], run=True, gait="vanilla")
                animals.love(a, e, camera=cam, frame_end=e + 30)
                e = a.die(e + 30, camera=cam)
                a.place(e + 10, (x, 0, 0), 0.0)
                a.show(e + 20, False)
                a.eye_point(e), a.mouth_point(e)
            except Exception as ex:                                      # noqa: BLE001
                errs.append((kind, i, repr(ex)[:160]))
                break
    expect("24 animals, every method once each", not errs, errs)
    n_obj = len(bpy.data.objects)
    print("     scene of 24 animals after one life each: %d objects, %d meshes" % (n_obj, len(bpy.data.meshes)))
    print("robust:", "all %d passed" % len(res) if all(res) else "%d of %d FAILED" % (res.count(False), len(res)))
    return all(res)


if __name__ == "__main__":
    which = set(sys.argv[1:]) or {"uv", "robust"}
    good = True
    if "uv" in which:
        good &= check_uv()
    if "robust" in which:
        good &= check_robust()
    sys.exit(0 if good else 1)
