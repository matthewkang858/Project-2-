"""Proof stills and number checks for engine/players.py.

    $BPY -m engine.players check                 # numbers and keyframes only, no rendering
    $BPY -m engine.players lineup_front armor    # stills by name -> out/test/players_<name>.png (540x960, 16 spp)
    names: check lineup_front lineup_back armor armor_back mixed items1 .. items6 poses hurt walk closeup action square laps
           herobrine_dusk herobrine_close scale
Each still is one render (well under 300 s on two threads); run a few names per call.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

from engine import characters as ch
from engine import players as pl
from engine import quick

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS = ["diamond_sword", "iron_sword", "golden_sword", "netherite_sword", "stone_sword", "wooden_sword",
         "diamond_pickaxe", "iron_pickaxe", "golden_pickaxe", "netherite_axe",
         "iron_axe", "stone_shovel", "golden_hoe", "bow", "shield", "torch", "redstone_torch", "bucket", "milk_bucket",
         "cooked_chicken",
         "steak", "golden_apple", "splash_potion", "ender_pearl", "gold_ingot", "emerald", "music_disc_13", "goat_horn",
         "totem", "note_block",
         "tnt", "redstone_lamp", "anvil", "dirt"]


def stage(preset="golden", ground="block/grass_block_top", tint=(145, 189, 89)):
    """Fresh quick scene with a floor of a real block texture."""
    scene = quick.reset()
    quick.setup(scene)
    quick.light(scene, preset)
    mat = ch._test_material("players_test_ground", ground, tint)
    ch._test_box("players_test_ground", (-40.0, -40.0, -1.0), (40.0, 40.0, 0.0), mat)
    return scene


def render(scene, name):
    path = quick.render(scene, "players_" + name)
    print("wrote", path, flush=True)
    return path


def rows(n, per_row, dx=1.25, dy=1.6, dz=0.0):
    """Positions of n figures in rows of per_row (front row first, toward -Y)."""
    out = []
    for i in range(n):
        r, c = divmod(i, per_row)
        count = min(per_row, n - r * per_row)
        out.append(((c - (count - 1) / 2.0) * dx, r * dy, r * dz))
    return out


def frame_cam(scene, width, target, lens=40, height=2.4, side=0.18):
    """Camera in front (-Y) that fits `width` blocks across the portrait frame."""
    dist = width / (2.0 * 7.5 / lens)
    quick.camera(scene, (target[0] - side * dist, target[1] - dist, height), target, lens=lens)


def tiers(scene, n_rows, half_width, dz=2.0, depth=1.6):
    """Stone steps for the rows behind the first."""
    stone = ch._test_material("players_test_stone", "block/stone_bricks")
    for r in range(1, n_rows):
        y0 = (r - 0.5) * depth
        ch._test_box("players_test_step%d" % r, (-half_width, y0, 0.0), (half_width, y0 + depth, r * dz), stone)


def lineup(back=False):
    scene = stage()
    tiers(scene, 2, 3.4)
    skins = list(pl.SKINS) + ["herobrine"]
    for skin, pos in zip(skins, rows(10, 5, dx=1.25, dy=1.6, dz=2.0)):
        p = pl.make_player("p_" + skin, skin)
        p.place(1, pos, math.radians(180 if back else 0))
    scene.frame_set(1)
    frame_cam(scene, 6.6, (0.0, 0.8, 1.95), height=2.6)
    return render(scene, "lineup_back" if back else "lineup_front")


def armor(back=False):
    scene = stage()
    tiers(scene, 2, 2.6)
    sets = ["leather", "chainmail", "iron", "golden", "diamond", "netherite"]
    for m, pos in zip(sets, rows(6, 3, dx=1.5, dy=1.6, dz=2.0)):
        p = pl.make_player("steve_" + m, "steve")
        pl.equip(p, m)
        p.place(1, pos, math.radians((180 if back else 0) + 20))
    scene.frame_set(1)
    frame_cam(scene, 4.9, (0.0, 0.8, 1.95), height=2.6)
    return render(scene, "armor_back" if back else "armor")


def mixed():
    scene = stage()
    tiers(scene, 2, 2.9)
    looks = [("steve", dict(boots="golden")), ("alex", dict(helmet="golden")),
             ("kai", dict(chestplate="iron", leggings="leather")), ("zuri", dict(material="diamond", enchanted=True)),
             ("efe", dict(helmet="netherite", chestplate="chainmail", boots="iron")),
             ("noor", dict(leggings="golden", boots="diamond"))]
    for (skin, kw), pos in zip(looks, rows(6, 3, dx=1.75, dy=1.6, dz=2.0)):
        p = pl.make_player("m_" + skin, skin)
        pl.equip(p, **kw)
        p.place(1, pos, math.radians(-25))
    scene.frame_set(30)
    frame_cam(scene, 5.4, (0.0, 0.8, 1.9), height=2.9, side=0.05)
    return render(scene, "mixed")


def items(n):
    """Held-item sheet n (1..6): six of ITEMS in the right hand, three-quarter view, as third person shows them."""
    scene = stage()
    tiers(scene, 2, 3.2)
    chunk = ITEMS[(n - 1) * 6:n * 6]
    for i, (item, pos) in enumerate(zip(chunk, rows(len(chunk), 3, dx=2.0, dy=1.6, dz=2.0))):
        p = pl.make_player("i%d_%s" % (i, item), pl.SKINS[((n - 1) * 6 + i * 2 + 1) % 9])
        p.hold(item)
        p.place(1, pos, math.radians(38))
    scene.frame_set(1)
    frame_cam(scene, 6.2, (0.0, 0.8, 1.9), height=2.9, side=0.05)
    return render(scene, "items%d" % n)


def poses():
    scene = stage()
    tiers(scene, 2, 3.2)
    spots = rows(6, 3, dx=2.0, dy=1.6, dz=2.0)
    yaw = math.radians(38)
    f = 40
    a = pl.make_player("sneak", "sunny")
    a.place(1, spots[0], yaw)
    a.sneak(1)
    b = pl.make_player("eat", "efe")
    b.hold("cooked_chicken")
    b.place(1, spots[1], yaw)
    b.eat(20, 60)
    c = pl.make_player("drink", "makena")
    c.hold("milk_bucket")
    c.place(1, spots[2], yaw)
    c.drink(20, 60)
    d = pl.make_player("block", "steve")
    d.hold("shield", hand="left")
    d.hold("iron_sword")
    d.place(1, spots[3], math.radians(-38))
    d.block(20, 60)
    e = pl.make_player("bow", "alex")
    e.hold("bow")
    e.place(1, spots[4], yaw)
    e.draw_bow(10, 60)
    g = pl.make_player("horn", "ari")
    g.hold("goat_horn")
    g.place(1, spots[5], yaw)
    g.toot(20, 60)
    scene.frame_set(f)
    frame_cam(scene, 6.2, (0.0, 0.8, 1.9), height=2.9, side=0.05)
    return render(scene, "poses")


def hurt():
    scene = stage()
    tiers(scene, 2, 3.6, depth=2.2)
    spots = [(-2.2, 0.0, 0.0), (0.2, 0.0, 0.0), (-2.2, 2.2, 2.0), (0.2, 2.2, 2.0)]
    yaw = math.radians(-15)
    h = pl.make_player("hurt", "noor")
    h.place(1, spots[0], yaw)
    h.hurt(28)
    for i, (skin, start) in enumerate((("steve", 26), ("kai", 20), ("zuri", 9))):   # 4, 10 and 21 frames into dying
        p = pl.make_player("die%d" % i, skin)
        pl.equip(p, helmet="iron")
        p.hold("iron_sword")
        p.place(1, spots[i + 1], yaw)
        p.die(start)
    scene.frame_set(30)
    frame_cam(scene, 6.6, (0.3, 1.0, 1.9), height=3.2, side=0.05)
    return render(scene, "hurt")


def walk():
    scene = stage()
    tiers(scene, 3, 16.0, depth=2.0)
    f = 60
    for i in range(4):                                         # walking: four phases of one cycle (13.1 frames)
        p = pl.make_player("w%d" % i, pl.SKINS[i])
        x0 = -3.9 + i * 2.6
        start = f - 30 - i * 3
        a = (x0 - 4.317 * (f - start) / 24.0, 0.0, 0.0)
        p.place(start, a, math.radians(90))
        p.walk(start, [a, (x0 + 6.0, 0.0, 0.0)], ramp=(False, True))
    for i in range(4):                                         # sprinting: four phases (11.3 frames per cycle)
        p = pl.make_player("s%d" % i, pl.SKINS[4 + i])
        x0 = -3.9 + i * 2.6
        start = f - 30 - i * 3
        a = (x0 - 5.612 * (f - start) / 24.0, 2.0, 2.0)
        p.place(start, a, math.radians(90))
        p.walk(start, [a, (x0 + 8.0, 2.0, 2.0)], sprint=True, ramp=(False, True))
    for i in range(3):                                         # sprint-jumping: rising, at the top, coming down
        p = pl.make_player("j%d" % i, pl.SKINS[(i * 3 + 1) % 9])
        x0 = -3.4 + i * 3.4
        start = f - 14 - (3, 8, 12)[i]
        dist = pl.SPRINT_JUMP_SPEED * (f - start) / 24.0
        a = (x0 - dist, 4.0, 4.0)
        p.place(start, a, math.radians(90))
        p.sprint_jump(start, [a, (a[0] + 4.2767 * 4, 4.0, 4.0)])
    s = pl.make_player("sn", "zuri")                         # sneaking along the front
    s.place(1, (-3.0, -1.6, 0.0), math.radians(90))
    s.sneak(1)
    s.walk(1, [(-3.0, -1.6, 0.0), (4.0, -1.6, 0.0)])
    scene.frame_set(f)
    frame_cam(scene, 10.4, (0.0, 2.0, 2.9), height=3.6, side=0.0)
    return render(scene, "walk")


def closeup():
    """Coplanar-face check at close range: plain and enchanted diamond armor, and the skin with the most overlay."""
    scene = stage()
    a = pl.make_player("plain", "steve")
    pl.equip(a, "diamond")
    a.hold("diamond_sword")
    a.place(1, (-1.05, 0.0, 0.0), math.radians(-18))
    b = pl.make_player("ench", "steve")
    pl.equip(b, "diamond", enchanted=True)
    b.hold("diamond_sword", enchanted=True)
    b.place(1, (0.0, 0.0, 0.0), math.radians(-18))
    c = pl.make_player("kai", "kai")
    c.place(1, (1.05, 0.0, 0.0), math.radians(-18))
    c.raise_arm(1, 50, ease=0, side="l")
    scene.frame_set(40)
    quick.camera(scene, (-1.6, -7.6, 1.6), (0.0, 0.0, 0.98), lens=35)
    return render(scene, "closeup")


def action():
    """With motion blur (shutter 0.5): a sprinting armored player, an attack swing, mining, and a sleeper."""
    scene = stage()
    scene.render.use_motion_blur = True
    scene.render.motion_blur_shutter = 0.5
    try:
        scene.cycles.motion_blur_position = "START"
    except (AttributeError, TypeError):
        pass
    f = 40
    r = pl.make_player("runner", "steve")
    pl.equip(r, "iron")
    r.hold("iron_sword")
    r.hold("shield", hand="left")
    r.place(10, (-6.0, 1.2, 0.0), math.radians(90))
    r.walk(10, [(-6.0, 1.2, 0.0), (8.0, 1.2, 0.0)], sprint=True)
    a = pl.make_player("hitter", "alex")
    a.hold("diamond_axe")
    a.place(1, (-1.6, -0.6, 0.0), math.radians(30))
    a.attack(f - 3)
    m = pl.make_player("miner", "efe")
    m.hold("iron_pickaxe")
    m.place(1, (-0.2, -0.6, 0.0), math.radians(30))
    m.look_at(1, (0.6, -2.2, 0.6), ease=0)
    m.mine(20, 70)
    wool = ch._test_material("players_test_wool", "block/red_wool")
    ch._test_box("players_test_bed", (1.0, -1.6, 0.0), (2.0, 0.4, 9.0 / 16.0), wool)
    z = pl.make_player("sleeper", "noor")
    z.sleep(1, (1.5, -0.6, 9.0 / 16.0), math.radians(180))
    th = pl.make_player("thrower", "ari")
    th.hold("ender_pearl")
    th.place(1, (-2.9, -0.6, 0.0), math.radians(30))
    info = th.throw(f - 2)
    print("throw:", {k: (tuple(round(c, 2) for c in v) if hasattr(v, "__len__") else v) for k, v in info.items()})
    scene.frame_set(f)
    quick.camera(scene, (-0.9, -10.5, 3.4), (-0.4, 0.2, 0.8), lens=28)
    return render(scene, "action")


def legs(name="legs", frame_offset=0, blur=False):
    """Armored players WALKING, seen from the side and three-quarter at close range: the inner faces of leggings
    and boots (they used to tie with the leg's own inner face: hollow boots), full sets and single pieces."""
    scene = stage()
    if blur:
        scene.render.use_motion_blur = True
        scene.render.motion_blur_shutter = 0.5
        try:
            scene.cycles.motion_blur_position = "START"
        except (AttributeError, TypeError):
            pass
    stone = ch._test_material("players_test_stone", "block/stone_bricks")
    ch._test_box("players_test_step", (-4.0, 0.8, 0.0), (4.0, 2.4, 2.2), stone)
    specs = [("steve", dict(material="diamond"), 90.0, (-1.3, 0.0, 0.0)), ("steve", dict(material="netherite"), 130.0, (0.9, 0.0, 0.0)),
             ("alex", dict(leggings="iron", boots="golden"), 60.0, (-1.3, 1.6, 2.2)), ("kai", dict(boots="golden"), 110.0, (0.9, 1.6, 2.2))]
    f = 40
    for i, (skin, armor, yaw, pos) in enumerate(specs):
        p = pl.make_player("leg%d" % i, skin)
        pl.equip(p, **armor)
        yaw = math.radians(yaw)
        d = Vector((math.sin(yaw), -math.cos(yaw), 0.0))
        pos = Vector(pos)
        a = pos - d * pl.WALK_SPEED * (f - 10) / 24.0
        p.place(10, tuple(a), yaw)
        p.walk(10, [tuple(a), tuple(pos + d * 6.0)], ramp=(False, True))
    probe = bpy.data.objects["leg0_leg_r"]
    best = max(range(f - 4, f + 10), key=lambda k: abs(ch._val(probe, "rotation_euler", 0, k)))
    scene.frame_set(best + frame_offset)
    quick.camera(scene, (-0.2, -7.2, 1.9), (-0.2, 0.6, 1.6), lens=28)
    return render(scene, name)


def legs_close():
    """One walking player in full iron from the side at close range: the far leg's boot and legging from inside."""
    scene = stage()
    p = pl.make_player("inner", "steve")
    pl.equip(p, "iron")
    p.place(10, (-4.0, 0.0, 0.0), math.radians(90))
    p.walk(10, [(-4.0, 0.0, 0.0), (6.0, 0.0, 0.0)], ramp=(False, True))
    best = max(range(30, 46), key=lambda k: abs(ch._val(p.leg_r, "rotation_euler", 0, k)))
    scene.frame_set(best)
    x = p.root.matrix_world.translation.x
    quick.camera(scene, (x + 1.5, -2.9, 0.75), (x, 0.0, 0.85), lens=32)
    return render(scene, "legs_close")


def sneak_poses():
    """Posed arms while sneaking (the +0.4 rad of the crouch comes AFTER the arm pose in HumanoidModel.setupAnim)
    beside the same poses standing: shield up, bow drawn, horn."""
    scene = stage()
    tiers(scene, 2, 3.2)
    spots = rows(6, 3, dx=2.0, dy=1.6, dz=2.0)
    for i, (skin, what) in enumerate((("steve", "block"), ("alex", "bow"), ("ari", "horn"))):
        for row, sneaking in ((0, True), (1, False)):
            p = pl.make_player("%s_%d" % (what, row), skin)
            p.place(1, spots[row * 3 + i], math.radians(55 if what != "block" else -55))
            if sneaking:
                p.sneak(1)
            if what == "block":
                p.hold("shield", hand="left")
                p.hold("iron_sword")
                p.block(10, 60)
            elif what == "bow":
                p.hold("bow")
                p.draw_bow(10, 60)
            else:
                p.hold("goat_horn")
                p.toot(10, 60)
    scene.frame_set(40)
    frame_cam(scene, 6.2, (0.0, 0.8, 1.9), height=2.9, side=0.05)
    return render(scene, "sneak_poses")


def killing_blow():
    """hurt + die on one frame (the killing blow) at four moments: red for the whole 20 ticks, knocked back,
    tipping over; and a left-handed attacker in mid swing."""
    scene = stage()
    tiers(scene, 2, 3.6, depth=2.2)
    spots = [(-2.4, 0.0, 0.0), (0.0, 0.0, 0.0), (-2.4, 2.2, 2.0), (0.0, 2.2, 2.0)]
    f = 40
    for i, (skin, start) in enumerate((("steve", f - 3), ("kai", f - 9), ("zuri", f - 15), ("noor", f - 21))):
        p = pl.make_player("kb%d" % i, skin)
        pl.equip(p, chestplate="iron")
        x, y, z = spots[i]
        p.place(1, (x, y, z), math.radians(-90))                # facing west: the blow comes from there
        p.die(start, from_point=(x - 2.0, y, z + 1.0))
    a = pl.make_player("lefty", "alex")
    a.hold("iron_sword", hand="left")
    a.place(1, (3.0, 0.0, 0.0), math.radians(30))
    a.attack(f - 3, hand="left")
    scene.frame_set(f)
    frame_cam(scene, 8.4, (0.9, 1.0, 1.9), height=3.2, side=0.05)
    return render(scene, "killing_blow")


def coplanar(player, tolerance=0.5):
    """[(mesh a, mesh b, plane, px^2)] of same-facing coplanar faces of two of a player's meshes that overlap by
    more than `tolerance` square model pixels, in the pose of the current frame. Cycles has no draw order: such a
    pair renders as noise, or as whichever the BVH returns first. Planes are told apart to 0.004 px."""
    from collections import defaultdict

    bpy.context.view_layer.update()
    u = player.unit
    buckets = defaultdict(list)
    for ob in bpy.context.scene.objects:
        if ob.type != "MESH" or not ob.name.startswith(player.name + "_") or ob.hide_render:
            continue
        mw = ob.matrix_world
        rot = mw.to_3x3()
        for poly in ob.data.polygons:
            n = (rot @ poly.normal).normalized()
            pts = [mw @ ob.data.vertices[i].co for i in poly.vertices]
            key = (round(n.x, 3), round(n.y, 3), round(n.z, 3), round(n.dot(pts[0]) / u * 250.0))
            buckets[key].append((ob.name, pts))
    hits = defaultdict(float)
    for key, faces in buckets.items():
        n = Vector(key[:3])
        for i in range(len(faces)):
            for j in range(i + 1, len(faces)):
                if faces[i][0] == faces[j][0]:
                    continue
                poly, clip = list(faces[j][1]), faces[i][1]     # clip one quad by the other's edges
                centre = sum(clip, Vector()) / len(clip)
                for k in range(len(clip)):
                    e0, e1 = clip[k], clip[(k + 1) % len(clip)]
                    inward = n.cross(e1 - e0)
                    if inward.dot(centre - e0) < 0:
                        inward = -inward
                    kept = []
                    for m in range(len(poly)):
                        p0, p1 = poly[m], poly[(m + 1) % len(poly)]
                        d0, d1 = inward.dot(p0 - e0), inward.dot(p1 - e0)
                        if d0 >= 0:
                            kept.append(p0)
                        if (d0 >= 0) != (d1 >= 0):
                            kept.append(p0 + (p1 - p0) * (d0 / (d0 - d1)))
                    poly = kept
                    if len(poly) < 3:
                        break
                if len(poly) >= 3:
                    area = sum((poly[m] - poly[0]).cross(poly[m + 1] - poly[0]).length / 2.0 for m in range(1, len(poly) - 1))
                    hits[(tuple(sorted((faces[i][0], faces[j][0]))), key[:3])] += area / u / u
    return [(a, b, plane, round(area, 2)) for ((a, b), plane), area in sorted(hits.items()) if area > tolerance]


# ---------------------------------------------------------------------------------------------------- village stills
def village_stage(preset, az, el, bloom=1.0, grade="warm", motion_blur=False):
    """The real village, sky and compositor, with a films.lookdev.Stage (as films/lookdev.build_film does)."""
    from engine import look, shots, village
    from films import lookdev

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=motion_blur)
    v = village.build_village(scene, seed=1)
    sky = look.set_time(scene, preset, sun_azimuth=az, sun_elevation=el)
    look.setup_compositor(scene, bloom=bloom, grade=grade)
    film = shots.Film(scene, fps=24)
    return scene, lookdev.Stage(scene, film, v, sky)


def village_render(scene, st, shot, name, at=0.5):
    st.finish()
    frame = shot.frame_start + int(round(at * 24))
    scene.frame_set(frame)
    scene.render.filepath = os.path.join(ROOT, "out", "test", "players_%s.png" % name)
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    print("wrote", scene.render.filepath, "frame", frame, flush=True)
    return scene.render.filepath


def square():
    scene, st = village_stage("golden", 62.0, 27.0)
    A = st.v.anchors
    s = st.shot("square", 2.0)
    f0 = s.frame_start
    town = pl.cast_town(st, 6, seed=4)
    pl.equip(town[1], helmet="iron")
    pl.equip(town[4], chestplate="leather", boots="leather")
    c = Vector(A["square_s"])
    ang = math.radians(-32.0)                              # the lens looks west-north-west: the sun is 86 degrees off it
    a = Vector((math.cos(ang), math.sin(ang), 0.0))         # from the group toward the camera
    q = Vector((-a.y, a.x, 0.0))
    cam = c + a * 9.3 + Vector((0.0, 0.0, 1.45))
    lateral = [-1.8, -1.08, -0.36, 0.36, 1.08, 1.8]
    for i, (p, lat) in enumerate(zip(town, lateral)):
        pos = c + q * lat + a * (0.9 if i % 2 == 0 else -0.7)
        p.place(f0, (pos.x, pos.y, c.z), math.atan2(cam.x - pos.x, -(cam.y - pos.y)) + math.radians((-14, 9, -6, 12, -10, 5)[i]))
        p.look_at(f0, tuple(cam), ease=0)
        p.idle(f0, s.frame_end + 1)
    st.use(s, *town)
    s.lens(28, 4.0)
    s.move(tuple(cam), (c.x, c.y, 1.1))
    s.focus(town[2].head)
    st.hero(s, "town", town[2])
    st.lights(s, scale=1.0)
    return village_render(scene, st, s, "square", at=1.0)


def laps():
    """The gym town runs laps: four players sprint-jumping up the exit road, filmed with the film's motion blur."""
    scene, st = village_stage("golden", 62.0, 27.0, motion_blur=True)
    A = st.v.anchors
    s = st.shot("laps", 2.0)
    f0 = s.frame_start
    gate = Vector(A["exit_gate"])
    runners = pl.cast_town(st, 4, seed=11, items=False)
    pl.equip(runners[0], boots="golden")
    pl.equip(runners[2], "iron")
    for i, p in enumerate(runners):
        x = gate.x + (-0.9, 0.5, -0.3, 1.1)[i]
        y0 = gate.y + 18.0 - i * 3.1
        p.place(f0 - 8, (x, y0, 0.0), math.radians(0))
        p.sprint_jump(f0 - 8 - i * 3, [(x, y0, 0.0), (x, y0 - 4.2767 * 5, 0.0)])
    st.use(s, *runners)
    s.lens(35, 4.0)
    s.move((gate.x - 2.6, gate.y + 1.5, 0.9), (gate.x, gate.y + 9.0, 1.3))
    s.focus(runners[0].head)
    st.hero(s, "runner", runners[0])
    st.lights(s, scale=1.0)
    return village_render(scene, st, s, "laps", at=0.25)


def herobrine(close=False):
    scene, st = village_stage("dusk", 187.0, 5.0, bloom=1.3)
    A = st.v.anchors
    s = st.shot("hb", 2.0)
    f0 = s.frame_start
    hb = pl.add_player(st, "herobrine", "herobrine")
    kid = st.actor("kid", "none", child=True)
    gate = Vector(A["exit_gate"])
    spot = (gate.x + 0.3, gate.y + 10.0, 0.0)
    kpos = (gate.x - 0.2, spot[1] - 16.6, 0.0)
    hb.place(f0, spot, math.radians(0))
    kid.place(f0, kpos, math.radians(200))
    hb.watch(f0, s.frame_end, kid)                          # placed on f0: his head is on the child from frame one
    kid.look_at(f0, (kpos[0] - 2.0, kpos[1] - 3.0, 1.0), ease=0)
    st.use(s, hb, kid)
    if close:
        s.lens(70, 2.8)
        s.move((spot[0] - 0.9, spot[1] - 4.2, 1.55), (spot[0], spot[1], 1.5))
        s.focus(hb.head)
        st.hero(s, "herobrine", hb)
        st.lights(s, scale=1.0)
        return village_render(scene, st, s, "herobrine_close")
    cam = (kpos[0] + 0.52, kpos[1] - 3.3, 0.95)             # the child close to the lens, low on the left, turned to us
    kid.place(f0, kpos, math.radians(-12))
    kid.look_at(f0, (cam[0] + 0.5, cam[1], 0.9), ease=0)
    dist = math.dist(cam, (spot[0], spot[1], 1.6))
    print("herobrine is %.1f blocks from the lens" % dist)
    s.lens(50, 8.0)
    s.move(cam, (spot[0] - 0.25, spot[1], 1.42))
    s.focus(hb.head)
    st.hero(s, "herobrine", hb)
    st.lights(s, scale=1.0)
    return village_render(scene, st, s, "herobrine_dusk")


def scale():
    from films import poppy_common

    scene, st = village_stage("golden", 62.0, 27.0)
    A = st.v.anchors
    s = st.shot("scale", 1.0)
    f0 = s.frame_start
    c = Vector(A["square_s"])
    steve = pl.add_player(st, "steve", "steve")
    alex = pl.add_player(st, "alex", "alex")
    vil = st.actor("farmer", "farmer")
    kid = st.actor("kid", "none", child=True)
    golem = poppy_common.add_golem(st)
    for ch_, dx in ((kid, -2.3), (vil, -1.3), (steve, -0.2), (alex, 0.8), (golem, 2.3)):
        ch_.place(f0, (c.x + dx, c.y + 0.6, c.z), 0.0)
    st.use(s, steve, alex, vil, kid, golem)
    s.lens(30, 5.6)
    s.move((c.x + 1.1, c.y - 11.2, 1.5), (c.x + 0.15, c.y + 0.6, 1.3))
    s.focus(steve.head)
    st.lights(s, scale=1.0)
    return village_render(scene, st, s, "scale", at=0.2)


# ---------------------------------------------------------------------------------------------------- numbers
def check():
    scene = stage()
    u = pl.MODEL_SCALE / 16.0
    p = pl.make_player("probe", "steve")
    assert abs(p.height - 1.875) < 1e-6 and abs(p.eye_height - 1.611) < 2e-3, (p.height, p.eye_height)
    print("height %.4f  eyes %.4f  unit %.5f" % (p.height, p.eye_height, u))
    print("jump arc", [round(y, 4) for y in pl.JUMP_ARC], "peak %.4f ticks %d" % (pl.JUMP_HEIGHT, pl.JUMP_TICKS))
    assert pl.JUMP_TICKS == 12 and abs(pl.JUMP_HEIGHT - 1.2522) < 1e-3
    print("sprint-jump speed %.3f blocks/s, %.3f blocks per hop" % (pl.SPRINT_JUMP_SPEED, pl.SPRINT_JUMP_SPEED * 0.6))
    assert 6.9 < pl.SPRINT_JUMP_SPEED < 7.3
    # walk: 20 blocks at the game's speed, with its ramps
    p.place(1, (0.0, 0.0, 0.0), math.radians(90))
    end = p.walk(1, [(0.0, 0.0, 0.0), (20.0, 0.0, 0.0)])
    secs = (end - 1) / 24.0
    print("walk 20 blocks: %d frames = %.2f s (20 / 4.317 = %.2f s + ramps)" % (end - 1, secs, 20 / 4.317))
    assert 4.6 < secs < 5.2
    scene.frame_set(40)
    a = Vector(p.root.location)
    scene.frame_set(64)
    b = Vector(p.root.location)
    print("cruise speed %.3f blocks/s" % ((b - a).length,))
    assert abs((b - a).length - 4.317) < 0.05
    legs = [abs(v) for _f, v, _i in ch.read_keys(p.leg_r, "rotation_euler", 0)]
    print("walk leg swing peak %.3f rad (1.4 * 0.863 = 1.208)" % max(legs))
    assert 1.15 < max(legs) < 1.21
    assert ch.read_keys(p.leg_r, "rotation_euler", 0)[-1][2] == "CONSTANT"
    assert abs(ch.read_keys(p.leg_r, "rotation_euler", 0)[-1][1]) < 1e-6
    # foot slide of the planted foot at cruise: the foot's world x while its leg swings back through vertical
    q = pl.make_player("probe2", "alex")
    q.place(1, (0.0, 3.0, 0.0), math.radians(90))
    end = q.walk(1, [(0.0, 3.0, 0.0), (30.0, 3.0, 0.0)], sprint=True)
    scene.frame_set(60)
    a = Vector(q.root.location)
    scene.frame_set(84)
    b = Vector(q.root.location)
    print("sprint speed %.3f blocks/s, leg peak %.3f" % ((b - a).length, max(abs(v) for _f, v, _i in ch.read_keys(q.leg_r, "rotation_euler", 0))))
    assert abs((b - a).length - 5.612) < 0.06
    # sprint-jump
    j = pl.make_player("probe3", "kai")
    j.place(1, (0.0, 6.0, 0.0), math.radians(90))
    end = j.sprint_jump(1, [(0.0, 6.0, 0.0), (17.1, 6.0, 0.0)])
    zs = [v for _f, v, _i in ch.read_keys(j.root, "location", 2)]
    print("sprint_jump 17.1 blocks: %d frames, %d hops, peak %.4f" % (end - 1, round((end - 1) / 14.4), max(zs)))
    assert abs(max(zs) - 1.2522) < 1e-3 and abs(zs[-1]) < 1e-9
    # crouch
    k = pl.make_player("probe4", "ari")
    k.place(1, (0.0, 9.0, 0.0), 0.0)
    eye0 = k.eye_point(1).z
    k.sneak(10)
    scene.frame_set(10)
    bpy.context.view_layer.update()
    eye1 = k.eye_point(10).z
    head_drop = (4.2 * u + 0.125)
    print("crouch: eyes %.3f -> %.3f (drop %.3f = 4.2 px + 2 px offset), torso tilt %.2f, leg back %.3f"
          % (eye0, eye1, eye0 - eye1, k.torso.rotation_euler.x, k.leg_l.location.y))
    assert abs((eye0 - eye1) - head_drop) < 1e-5 and abs(k.torso.rotation_euler.x - 0.5) < 1e-6
    assert abs(k.arm_r.rotation_euler.x - 0.4) < 1e-6
    k.place(20, (0.0, 9.0, 0.0), 0.0)
    scene.frame_set(20)
    assert abs(k.torso.rotation_euler.x) < 1e-6 and not k.crouching_at(20)
    # held items: the generic transform must equal the one characters.Character.hold uses
    m_new = pl.hand_matrix(pl._display(pl._model_chain("item/emerald"), "thirdperson_righthand"))
    m_old = ch._held_matrix("hand", pl.MODEL_SCALE)
    assert max(abs(m_new[i][j] - m_old[i][j]) for i in range(4) for j in range(4)) < 1e-6
    h = pl.make_player("probe5", "efe")
    h.place(1, (0.0, 12.0, 0.0), 0.0)
    sword = h.hold("diamond_sword")
    assert abs(h.arm_r.rotation_euler.x - ch.ITEM_ARM_PITCH) < 1e-6
    scene.frame_set(1)
    bpy.context.view_layer.update()
    tip = sword.matrix_world @ Vector((0.4, 0.0, 0.4))
    grip = sword.matrix_world @ Vector((-0.35, 0.0, -0.35))
    print("sword: grip %s tip %s (player at y 12, facing -Y)" % (tuple(round(c, 2) for c in grip), tuple(round(c, 2) for c in tip)))
    assert tip.y < grip.y - 0.3 and tip.z > grip.z, "a sword points forward and up out of the fist"
    h.hold("shield", hand="left", frame=30)
    h.hold(None, frame=40)
    assert h.holding_at("right", 39) == "diamond_sword" and h.holding_at("right", 40) is None
    assert h.holding_at("left", 29) is None and h.holding_at("left", 30) == "shield"
    scene.frame_set(41)
    assert sword.hide_render and not h.item("left").hide_render
    scene.frame_set(20)
    assert not sword.hide_render and h.item("left").hide_render
    h.show(25, False)
    h.show(35, True)
    for f, want_sword, want_shield in ((24, True, False), (26, False, False), (36, True, True), (41, False, True)):
        scene.frame_set(f)
        assert (not sword.hide_render) == want_sword and (not h.item("left").hide_render) == want_shield, f
    # armor boxes
    made = pl.equip(h, "iron")
    dims = {o.name.split("_", 1)[1]: tuple(round(d / u, 2) for d in o.dimensions) for o in made}
    print("armor boxes (pixels):", dims)
    assert dims["helmet_head"][:2] == (10.12, 10.12) and dims["chestplate_torso"][:2] == (10.0, 6.0)   # z: opaque texels only
    # the game's whole leg boxes (4 + 2 x 0.9 and 4 + 2 x 0.4 wide); the left leg's are 0.03 larger all round
    assert dims["boots_leg_r"][0] == 5.8 and dims["leggings_leg_r"][0] == 4.8, dims
    assert dims["boots_leg_l"][0] == 5.86 and dims["leggings_leg_l"][0] == 4.86, dims
    pl.equip(h, boots="golden", frame=50)
    assert h.armor_at("boots", 49) == "iron" and h.armor_at("boots", 50) == "golden" and h.armor_at("helmet", 60) == "iron"
    # hurt, knock-back, death
    d = pl.make_player("probe6", "noor")
    d.place(1, (0.0, 15.0, 0.0), 0.0)
    end = d.hurt(10, from_point=(0.0, 13.0, 1.0))
    ys = [v for _f, v, _i in ch.read_keys(d.root, "location", 1)]
    zs = [v for _f, v, _i in ch.read_keys(d.root, "location", 2)]
    print("knock-back: %.2f blocks back, hop %.3f, over %d frames" % (ys[-1] - 15.0, max(zs), end - 10))
    assert 1.6 < ys[-1] - 15.0 < 2.2 and 0.9 < max(zs) < 1.0
    scene.frame_set(15)
    assert abs(d.torso.color[3]) < 1e-6
    scene.frame_set(22)
    assert abs(d.torso.color[3] - 1.0) < 1e-6
    d.place(40, (0.0, 15.0, 0.0), 0.0)
    info = d.die(40)
    scene.frame_set(40 + 17)
    print("death: roll %.1f degrees after 17 frames, gone on frame %d" % (math.degrees(d.root.rotation_euler.y), info["frame"]))
    assert abs(math.degrees(d.root.rotation_euler.y) - 90.0) < 0.5 and info["frame"] == 64
    scene.frame_set(64)
    assert d.torso.hide_render
    # Herobrine: nothing moves but the head
    hb = pl.make_player("probe7", "herobrine")
    hb.place(1, (0.0, 18.0, 0.0), 0.0)
    hb.idle(1, 100)
    walker = ch.make_villager("probe8", "none", child=True)
    walker.place(1, (-6.0, 14.0, 0.0), math.radians(90))
    walker.walk(1, [(-6.0, 14.0, 0.0), (6.0, 14.0, 0.0)])
    hb.watch(1, 100, walker)
    assert not ch.read_keys(hb.arm_r, "rotation_euler", 0) and not ch.read_keys(hb.body, "rotation_euler", 1)
    yaws = [v for _f, v, _i in ch.read_keys(hb.head, "rotation_euler", 2)]
    print("herobrine: head yaw %.0f .. %.0f degrees over the walk, %d keys; arms keyed: no"
          % (math.degrees(min(yaws)), math.degrees(max(yaws)), len(yaws)))
    assert max(yaws) - min(yaws) > 1.0 and hb.arm_r.rotation_euler.y == 0.0
    # every default skin builds, wide and slim
    for skin in pl.SKINS:
        for slim in (False, True):
            x = pl.make_player("b_%s_%d" % (skin, slim), skin, slim=slim)
            assert round(x.arm_r.dimensions.x / u, 2) == (3.54 if slim else 4.54), x.arm_r.dimensions.x / u
    check_api(scene)
    print("check ok")
    return 0


def check_api(scene):
    """Every other call of the API once, read back: hands, variants, timed armor, death and standing up again."""
    from engine import props

    p = pl.make_player("api", "sunny")
    p.place(1, (5.0, 0.0, 0.0), 0.0)
    em = props.make_item("emerald")
    assert p.hold(em, hand="left") is em and em.parent is p.arm_l
    assert abs(p.arm_l.rotation_euler.x - ch.ITEM_ARM_PITCH) < 1e-6
    p.hold("goat_horn")
    ends = (p.toot(10, 40), p.attack(50), p.jump(60), p.eat(80), p.hurt(130))
    print("toot / attack / jump / eat / hurt end on frames", ends)
    assert ends == (43, 59, 75, 118, 142)
    scene.frame_set(20)
    vis = {k: (not a.ob.hide_render) for k, a in p._hands["r"][-1].variants.items()}
    assert vis == {"": False, "tooting_goat_horn": True}, vis
    p.block(140, 160)
    p.watch(170, 220, (10.0, -5.0, 1.0), body=True)
    made = pl.equip(p, "golden", frame=30)
    pl.equip(p, helmet=None, frame=90)
    assert p.armor_at("helmet", 50) == "golden" and p.armor_at("helmet", 95) is None and p.armor_at("boots", 95) == "golden"
    helm = [o for o in made if "helmet" in o.name][0]
    for f, want in ((20, False), (50, True), (95, False)):
        scene.frame_set(f)
        assert (not helm.hide_render) == want, (f, helm.hide_render)
    p.die(230)
    p.place(300, (6.0, 1.0, 0.0), 0.5)
    scene.frame_set(300)
    assert abs(p.root.rotation_euler.y) < 1e-6 and abs(p.torso.color[3] - 1.0) < 1e-6
    p.show(300, True)
    p.sneak(310)
    end = p.walk(310, [(6.0, 1.0, 0.0), (6.0, -3.0, 0.0)])
    print("sneak-walk 4 blocks: %d frames (4 / 1.295 = 74 frames + ramps)" % (end - 310))
    assert 74 <= end - 310 <= 90
    town = pl.cast_town(None, 9, seed=2)
    print("town:", [(t.skin, t.holding_at("right", 1)) for t in town])
    assert len({t.skin for t in town}) == 9 and len({t.idle_seed for t in town}) >= 8


STILLS = {
    "check": check, "lineup_front": lambda: lineup(False), "lineup_back": lambda: lineup(True),
    "armor": lambda: armor(False), "armor_back": lambda: armor(True), "mixed": mixed,
    "items1": lambda: items(1), "items2": lambda: items(2), "items3": lambda: items(3),
    "items4": lambda: items(4), "items5": lambda: items(5), "items6": lambda: items(6),
    "poses": poses, "hurt": hurt, "walk": walk, "closeup": closeup, "action": action, "square": square, "laps": laps,
    "herobrine_dusk": lambda: herobrine(False), "herobrine_close": lambda: herobrine(True), "scale": scale,
}


def main(argv=None):
    names = list(argv if argv is not None else sys.argv[1:]) or ["check"]
    for n in names:
        if n not in STILLS:
            print("unknown still %r; choose from: %s" % (n, " ".join(STILLS)))
            return 2
    for n in names:
        STILLS[n]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
