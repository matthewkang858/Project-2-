"""Proof stills and number checks for engine/players.py.

    $BPY -m engine.players check                 # numbers and keyframes only, no rendering
    $BPY -m engine.players lineup_front armor    # stills by name -> out/test/players_<name>.png (540x960, 16 spp)
    names: check lineup_front lineup_back armor armor_back mixed items1 .. items6 poses hurt walk closeup action square laps
           herobrine_dusk herobrine_close scale
           legs legs_next legs_blur legs_close (walking in armor, close) sneak_poses killing_blow
           herobrine_first (the FIRST frame of a watch() shot) herobrine_night death_poof
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
        p.sprint_jump(start, [a, (a[0] + 4.2767 * 4, 4.0, 4.0)], ramp=False)
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
    specs = [("steve", dict(material="diamond"), 90.0, (-1.5, 0.0, 0.0)), ("steve", dict(material="netherite"), 130.0, (0.5, 0.0, 0.0)),
             ("alex", dict(leggings="iron", boots="golden"), 60.0, (-1.5, 1.6, 2.2)), ("kai", dict(boots="golden"), 110.0, (0.5, 1.6, 2.2))]
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
    frame_cam(scene, 6.9, (0.0, 0.8, 1.9), height=2.9, side=0.05)
    return render(scene, "sneak_poses")


def killing_blow():
    """hurt + die on one frame (the killing blow from the lens side) 3, 9, 15 and 21 frames in: red for the whole
    20 ticks, knocked back, tipping onto the left side; and a left-handed attacker in mid swing."""
    scene = stage()
    tiers(scene, 2, 3.8, depth=4.5)
    spots = [(-2.2, 0.0, 0.0), (0.0, 0.0, 0.0), (-2.2, 4.5, 2.0), (0.0, 4.5, 2.0)]
    f = 40
    for i, (skin, start) in enumerate((("steve", f - 3), ("kai", f - 9), ("zuri", f - 15), ("noor", f - 21))):
        p = pl.make_player("kb%d" % i, skin)
        pl.equip(p, chestplate="iron")
        x, y, z = spots[i]
        p.place(1, (x, y, z), 0.0)
        if i % 2:
            p.hurt(start, from_point=(x, y - 2.0, z + 1.0))     # the two calls a director would make ...
            p.die(start)
        else:
            p.die(start, from_point=(x, y - 2.0, z + 1.0))      # ... or the one
    a = pl.make_player("lefty", "alex")
    a.hold("iron_sword", hand="left")
    a.place(1, (2.3, 0.4, 0.0), math.radians(-20))
    a.attack(f - 3, hand="left")
    scene.frame_set(f)
    frame_cam(scene, 7.0, (0.1, 2.2, 1.9), height=3.6, side=0.05)
    return render(scene, "killing_blow")


def coplanar(player, tolerance=0.25, apart=0.004):
    """[(mesh a, mesh b, normal, px^2)] of same-facing faces of two of a player's meshes that lie in one plane
    (within `apart` model pixels) and overlap by more than `tolerance` square pixels, in the pose of the current
    frame. Cycles has no draw order: such a pair renders as noise, or as whichever the BVH returns first.
    The default tolerance passes the one tie the game's own geometry has: the arms rest 0.05 rad splayed, and a
    sliver (0.1 px2, 0.1 px wide) of each arm's front and back lies in the torso's front and back plane."""
    from collections import defaultdict

    bpy.context.view_layer.update()
    u = player.unit
    faces = []
    for ob in bpy.context.scene.objects:
        if ob.type != "MESH" or not ob.name.startswith(player.name + "_") or ob.hide_render:
            continue
        mw = ob.matrix_world
        rot = mw.to_3x3()
        for poly in ob.data.polygons:
            n = (rot @ poly.normal).normalized()
            pts = [mw @ ob.data.vertices[i].co for i in poly.vertices]
            faces.append((ob.name, n, n.dot(pts[0]) / u, pts))
    faces.sort(key=lambda f: (round(f[1].x, 2), round(f[1].y, 2), round(f[1].z, 2)))
    hits = defaultdict(float)
    for i, (name_a, na, da, clip) in enumerate(faces):
        for name_b, nb, db, quad in faces[i + 1:]:
            if abs(nb.x - na.x) > 0.02:                         # sorted by normal: no more candidates
                break
            if name_a == name_b or na.dot(nb) < 0.999999 or abs(da - db) > apart:
                continue
            poly = list(quad)                                   # clip one quad by the other's edges
            centre = sum(clip, Vector()) / len(clip)
            for k in range(len(clip)):
                e0, e1 = clip[k], clip[(k + 1) % len(clip)]
                inward = na.cross(e1 - e0)
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
                hits[(tuple(sorted((name_a, name_b))), (round(na.x, 2), round(na.y, 2), round(na.z, 2)))] += area / u / u
    return [(a, b, n, round(area, 2)) for ((a, b), n), area in sorted(hits.items()) if area > tolerance]


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
        p.sprint_jump(f0 - 8 - i * 3, [(x, y0, 0.0), (x, y0 - 4.2767 * 5, 0.0)], ramp=False)   # already running laps
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


def death_poof():
    """A killing blow in the village square, 4 frames after the victim vanished: the 20 white puffs of
    LivingEntity.makePoofParticles (engine.animals.poof, called by Player.die) fill his upright hit box where the
    knock-back left him; a second victim, 11 frames into his death, is red and tipping over."""
    scene, st = village_stage("golden", 62.0, 27.0)
    A = st.v.anchors
    s = st.shot("death", 2.0)
    f0 = s.frame_start
    c = Vector(A["square_s"])
    ang = math.radians(-32.0)
    a = Vector((math.cos(ang), math.sin(ang), 0.0))             # from the group toward the camera
    q = Vector((-a.y, a.x, 0.0))
    cam = c + a * 8.0 + Vector((0.0, 0.0, 1.45))

    def spot(lat, depth):
        p = c + q * lat + a * depth
        return (p.x, p.y, c.z)

    def toward(p0, p1):
        return math.atan2(p1[0] - p0[0], -(p1[1] - p0[1]))

    hitter = pl.add_player(st, "hitter", "ari")
    hitter.hold("iron_sword")
    v1 = pl.add_player(st, "victim1", "steve")
    pl.equip(v1, boots="golden")
    v2 = pl.add_player(st, "victim2", "kai")
    hitter.place(f0, spot(0.9, 1.5), toward(spot(0.9, 1.5), spot(0.0, 0.0)))
    v1.place(f0, spot(0.0, 0.0), toward(spot(0.0, 0.0), spot(0.9, 1.5)))
    v2.place(f0, spot(1.2, -1.5), toward(spot(1.2, -1.5), tuple(cam)))
    hitter.attack(f0 + 1)
    info = v1.die(f0 + 3, from_point=hitter, village=st.v)      # knocked away from the lens, 1.0 left and 1.7 deeper
    v2.die(f0 + 20, from_point=spot(1.2, 1.0))
    print("death_poof: victim1 gone on frame %d at %s, %r" % (info["frame"], tuple(round(x, 2) for x in info["feet"]), info["burst"]))
    assert info["burst"] is not None and len(info["burst"].particles) >= 20
    st.use(s, hitter, v1, v2)
    s.lens(32, 4.0)
    s.move(tuple(cam), (c.x, c.y, 1.0))
    s.focus(hitter.head)
    st.hero(s, "hitter", hitter)
    st.lights(s, scale=1.0)
    return village_render(scene, st, s, "death_poof", at=31.0 / 24.0)


def herobrine_first():
    """The FIRST frame of a shot in which Herobrine watches a child walk past, 45 degrees to his side, with the
    film's motion blur: placed and told to watch on that frame, his head is on the child already (it used to
    swing there over the first eight frames of every shot)."""
    scene, st = village_stage("dusk", 187.0, 5.0, bloom=1.3, motion_blur=True)
    A = st.v.anchors
    s = st.shot("hb", 2.0)
    f0 = s.frame_start
    hb = pl.add_player(st, "herobrine", "herobrine")
    kid = st.actor("kid", "none", child=True)
    gate = Vector(A["exit_gate"])
    spot = (gate.x + 0.3, gate.y + 10.0, 0.0)
    k0, k1 = (spot[0] + 2.6, spot[1] - 2.6, 0.0), (spot[0] - 4.5, spot[1] - 2.6, 0.0)
    hb.place(f0, spot, 0.0)
    kid.place(f0, k0, math.radians(-90))
    kid.walk(f0, [k0, k1], speed=2.0)
    hb.watch(f0, s.frame_end, kid)
    yaws = [round(math.degrees(ch._val(hb.head, "rotation_euler", 2, f)), 1) for f in (f0, f0 + 1, f0 + 2, f0 + 8, f0 + 24)]
    print("herobrine_first: head yaw on frames +0 +1 +2 +8 +24: %s (the child is %.1f degrees to his side on +0)"
          % (yaws, math.degrees(hb._aim(kid, f0)[0])))
    st.use(s, hb, kid)
    s.lens(28, 5.6)
    s.move((spot[0] + 1.4, spot[1] - 8.2, 1.35), (spot[0] + 1.4, spot[1], 1.15))
    s.focus(hb.head)
    st.hero(s, "herobrine", hb)
    st.lights(s, scale=1.0)
    return village_render(scene, st, s, "herobrine_first", at=0.0)


def herobrine_night():
    """Herobrine at NIGHT, 20 blocks from a 35 mm lens: the default glow (left) beside glow=7 (right)."""
    from engine import look, shots, village
    from films import lookdev

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=False)
    v = village.build_village(scene, seed=1)
    sky = look.set_time(scene, "night")
    look.setup_compositor(scene, bloom=1.0, grade="warm")
    st = lookdev.Stage(scene, shots.Film(scene, fps=24), v, sky)
    s = st.shot("night", 1.0)
    f0 = s.frame_start
    cam = (0.4, 24.0, 1.3)
    hb = pl.add_player(st, "herobrine", "herobrine")
    hb.place(f0, (-0.6, 44.0, 0.0), 0.0)
    hb7 = pl.add_player(st, "herobrine7", "herobrine", glow=7.0)
    hb7.place(f0, (1.6, 44.0, 0.0), 0.0)
    for h in (hb, hb7):
        h.watch(f0, s.frame_end, cam)
    st.use(s, hb, hb7)
    s.lens(35, 4.0)
    s.move(cam, (0.5, 44.0, 1.5))
    s.focus(hb.head)
    st.lights(s, scale=1.0)
    print("herobrine_night: %.1f blocks from the lens" % math.dist(cam, (-0.6, 44.0, 1.6)))
    return village_render(scene, st, s, "herobrine_night", at=0.5)


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
    end = j.sprint_jump(1, [(0.0, 6.0, 0.0), (17.1, 6.0, 0.0)], ramp=False)
    zs = [v for _f, v, _i in ch.read_keys(j.root, "location", 2)]
    print("sprint_jump 17.1 blocks in full stride: %d frames, %d hops, peak %.4f" % (end - 1, round((end - 1) / 14.4), max(zs)))
    assert end - 1 == 58
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
    assert abs(k.head.scale.x - 1.0) < 1e-6 and abs(ch._val(k.head, "scale", 0, 12) - pl.CROUCH_HEAD_TIE) < 1e-6
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
    check_review(scene)
    print("check ok")
    return 0


def check_review(scene):
    """What the independent review found, pinned down: depth ties, the first frame of a stare, the killing blow,
    chained moves, the start and end of a lap, posed arms, and the API's rough edges."""
    rot, loc = "rotation_euler", "location"
    val = ch._val
    # 1. no two meshes of a player share a plane where they overlap: standing, striding, crouching, crouching archer
    a = pl.make_player("tie_a", "steve")
    pl.equip(a, "diamond")
    a.place(1, (30.0, 0.0, 0.0), math.radians(90))
    scene.frame_set(1)
    found = {"standing in full diamond": coplanar(a)}
    a.walk(1, [(30.0, 0.0, 0.0), (40.0, 0.0, 0.0)])
    wide = max(range(20, 40), key=lambda k: abs(val(a.leg_r, rot, 0, k)))
    scene.frame_set(wide)
    found["striding (legs %.2f rad apart)" % (2 * abs(val(a.leg_r, rot, 0, wide)))] = coplanar(a)
    b = pl.make_player("tie_b", "kai")
    pl.equip(b, leggings="iron", boots="golden")
    b.hold("bow")
    b.place(1, (30.0, 3.0, 0.0), 0.0)
    b.sneak(1)
    scene.frame_set(1)
    found["crouching in leggings and boots"] = coplanar(b)
    b.draw_bow(2, 30)
    scene.frame_set(20)
    found["crouching with the bow drawn"] = coplanar(b)
    c = pl.make_player("tie_c", "herobrine")
    pl.equip(c, boots="golden")
    c.place(1, (30.0, 6.0, 0.0), 0.0)
    scene.frame_set(1)
    found["herobrine (arms dead straight) in golden boots"] = coplanar(c)
    for label, hits in found.items():
        print("coplanar overlaps, %s: %s" % (label, hits or "none"))
    assert not any(found.values()), found
    scene.frame_set(1)
    slivers = coplanar(a, tolerance=0.01)                       # everything, however small: only arm against torso
    print("smaller than 0.25 px2, standing:", slivers or "none")
    assert slivers and all(x[3] < 0.25 and "arm" in x[0] and "torso" in x[1] for x in slivers), slivers

    # 2. the stare: on the target from the first frame of the shot when placed on that frame
    hb = pl.make_player("stare", "herobrine")
    kid = ch.make_villager("stare_kid", "none", child=True)
    kid.place(50, (36.0, 14.0, 0.0), math.radians(-90))
    kid.walk(50, [(36.0, 14.0, 0.0), (24.0, 14.0, 0.0)], speed=2.0)
    hb.place(50, (30.0, 20.0, 0.0), 0.0)
    hb.watch(50, 140, kid)
    want = math.degrees(hb._aim(kid, 50)[0])
    got = [math.degrees(val(hb.head, rot, 2, f)) for f in (49.76, 50, 51, 52, 58)]
    steps = [abs(math.degrees(val(hb.head, rot, 2, f + 1) - val(hb.head, rot, 2, f))) for f in range(50, 140)]
    print("watch() after place(): head yaw on the first frame %.1f (target %.1f), then %s; largest step %.2f deg/frame"
          % (got[1], want, [round(g, 1) for g in got[2:]], max(steps)))
    assert abs(want) > 30 and abs(got[1] - want) < 0.5 and abs(got[0] - want) < 0.5 and max(steps) < 2.5
    worst = max(math.degrees(hb.look_vector(f).angle(kid.eye_point(f) - hb.eye_point(f))) for f in range(50, 141, 5))
    assert worst < 1.5, worst
    hb.watch(140, 200, (36.0, 14.0, 1.0))                       # a new target in mid shot: he turns to it
    assert abs(val(hb.head, rot, 2, 140) - val(hb.head, rot, 2, 139.9)) < 0.01
    turner = pl.make_player("stare2", "herobrine")
    turner.place(50, (30.0, 23.0, 0.0), 0.0)
    turner.watch(50, 140, (20.0, 30.0, 1.6), body=True)          # behind him: the body is turned on the first frame too
    d = Vector((20.0, 30.0, 1.6)) - turner.eye_point(50)
    off = math.degrees(turner.look_vector(50).angle(d))
    print("watch(body=True) at a target 125 degrees behind: look is %.1f degrees off it on the first frame" % off)
    assert off < 1.0

    # 3. the killing blow: red for the whole death, in either call order, and knocked back
    for order in ("hurt, die", "die, hurt", "die(from_point)"):
        k = pl.make_player("blow_" + order[:3] + str(len(order)), "noor")
        k.place(1, (30.0, 30.0, 0.0), 0.0)
        if order == "hurt, die":
            k.hurt(20, from_point=(30.0, 28.0, 0.0))
            info = k.die(20)
        elif order == "die, hurt":
            info = k.die(20)
            k.hurt(20, from_point=(30.0, 28.0, 0.0))
        else:
            info = k.die(20, from_point=(30.0, 28.0, 0.0))
        red = []
        for f in range(18, 45):
            scene.frame_set(f)
            red.append((f, k.torso.color[3] < 0.5, k.torso.hide_render))
        on = [f for f, r, _h in red if r]
        print("%s: red on frames %d..%d, gone on %d, feet %s, colour keys %s" % (
            order, on[0], on[-1], info["frame"], tuple(round(c, 2) for c in k.pos_at(info["frame"])),
            ch.read_keys(k.torso, "color", 3)))
        assert on == list(range(20, 45)) and info["frame"] == 44 and red[-1][2] and not red[-2][2]
        assert [key[:2] for key in ch.read_keys(k.torso, "color", 3)] == [(0.0, 1.0), (20.0, 0.0)]
        assert abs(k.pos_at(44).y - 31.99) < 0.02
        if order != "die, hurt":
            assert abs(info["feet"].y - 31.99) < 0.02 and info["size"] == (0.6, 1.8)
    k.place(60, (30.0, 30.0, 0.0), 0.0)                         # standing again: his own colours
    scene.frame_set(60)
    assert abs(k.torso.color[3] - 1.0) < 1e-6 and abs(k.torso.scale.x - 1.0) < 1e-9
    w = pl.make_player("blow_walk", "ari")                     # killed in mid stride: he stops, the legs hang straight
    w.place(1, (30.0, 33.0, 0.0), math.radians(90))
    w.walk(1, [(30.0, 33.0, 0.0), (40.0, 33.0, 0.0)])
    w.die(30)
    assert abs(val(w.leg_r, rot, 0, 30)) < 1e-6 and abs(val(w.leg_r, rot, 0, 29)) > 0.2
    assert abs(val(w.root, loc, 0, 31) - val(w.root, loc, 0, 30)) < 1e-6 < abs(val(w.root, loc, 0, 30) - val(w.root, loc, 0, 29))
    for order in (0, 1):                                        # ... and with a blow from behind he is knocked on, legs straight
        w = pl.make_player("blow_walk%d" % order, "ari")
        w.place(1, (30.0, 34.0 + order, 0.0), math.radians(90))
        w.walk(1, [(30.0, 34.0 + order, 0.0), (40.0, 34.0 + order, 0.0)])
        x30 = val(w.root, loc, 0, 30)
        if order:
            w.die(30)
            w.hurt(30, from_point=(20.0, 34.0 + order, 0.0))
        else:
            w.hurt(30, from_point=(20.0, 34.0 + order, 0.0))
            w.die(30)
        assert abs(val(w.root, loc, 0, 54) - x30 - 1.99) < 0.02 and abs(val(w.leg_r, rot, 0, 31)) < 1e-6, order
    try:
        from engine import animals
    except ImportError:
        animals = None
    if animals is not None:
        quick.camera(scene, (30.0, 20.0, 1.6), (30.0, 36.0, 1.0), lens=35)
        pf = pl.make_player("blow_poof", "efe")
        pf.place(1, (30.0, 36.0, 0.0), 0.0)
        info = pf.die(20, from_point=(30.0, 34.0, 0.0), camera=scene.camera)
        zs = [p["pos"][0][2] for p in info["burst"].particles]
        print("die(camera=...): %r around feet %s" % (info["burst"], tuple(round(c, 2) for c in info["feet"])))
        assert len(info["burst"].particles) >= 20 and info["burst"].frame == 44

    # 4. chained moves: no jump in the legs, no halt at the joins
    limit = 0.6662 / 1.2 * 1.4 * 1.25                           # 1.25 x the fastest the game's leg turns per frame
    m = pl.make_player("chain", "kai")
    m.place(1, (0.0, 40.0, 0.0), math.radians(90))
    e1 = m.walk(1, [(0.0, 40.0, 0.0), (6.0, 40.0, 0.0)], sprint=True, ramp=(True, False))
    e2 = m.sprint_jump(e1, [(6.0, 40.0, 0.0), (6.0 + 4.2767 * 3, 40.0, 0.0)], ramp=(True, False))
    e3 = m.walk(e2, [(18.83, 40.0, 0.0), (26.0, 40.0, 0.0)])
    legs = [val(m.leg_r, rot, 0, f) for f in range(1, e3 + 30)]
    jump = max(abs(b - a) for a, b in zip(legs, legs[1:]))
    xs = [val(m.root, loc, 0, f) for f in range(1, e3 + 2)]
    speed = [(b - a) * 24.0 for a, b in zip(xs, xs[1:])]
    print("sprint -> sprint_jump -> walk (frames %d, %d, %d): largest leg change %.2f rad/frame (limit %.2f); slowest "
          "frame between frames 6 and %d: %.2f blocks/s; arms still swing in the last walk: %.2f rad"
          % (e1, e2, e3, jump, limit, e3 - 12, min(speed[5:e3 - 12]), max(abs(val(m.arm_l, rot, 0, f)) for f in range(e2 + 4, e3))))
    assert jump < limit, jump
    assert min(speed[5:e3 - 12]) > 3.5 and abs(xs[-1] - 26.0) < 1e-6
    assert max(abs(val(m.arm_l, rot, 0, f)) for f in range(e2 + 4, e3)) > 0.5
    n2 = pl.make_player("chain2", "alex")
    n2.place(1, (0.0, 43.0, 0.0), math.radians(90))
    e1 = n2.walk(1, [(0.0, 43.0, 0.0), (6.0, 43.0, 0.0)], ramp=(True, False))
    e2 = n2.walk(e1, [(6.0, 43.0, 0.0), (14.0, 43.0, 0.0)], sprint=True)
    legs = [val(n2.leg_r, rot, 0, f) for f in range(1, e2 + 30)]
    xs = [val(n2.root, loc, 0, f) for f in range(1, e2 + 2)]
    speed = [(b - a) * 24.0 for a, b in zip(xs, xs[1:])]
    print("walk -> sprint: largest leg change %.2f rad/frame; speed over the join %s"
          % (max(abs(b - a) for a, b in zip(legs, legs[1:])), [round(s, 2) for s in speed[e1 - 4:e1 + 5]]))
    assert max(abs(b - a) for a, b in zip(legs, legs[1:])) < limit and min(speed[e1 - 4:e1 + 5]) > 4.0
    n3 = pl.make_player("chain3", "zuri")                      # stop, then go on from the frame walk() returned
    n3.place(1, (0.0, 46.0, 0.0), math.radians(90))
    e1 = n3.walk(1, [(0.0, 46.0, 0.0), (5.0, 46.0, 0.0)])
    e2 = n3.walk(e1, [(5.0, 46.0, 0.0), (10.0, 46.0, 0.0)])
    legs = [val(n3.leg_r, rot, 0, f) for f in range(1, e2 + 30)]
    assert max(abs(b - a) for a, b in zip(legs, legs[1:])) < limit

    # 5. a lap from rest to rest: the first hop is shorter, the last landing slides out
    lap = pl.make_player("lap", "sunny")
    lap.place(1, (0.0, 50.0, 0.0), math.radians(90))
    end = lap.sprint_jump(1, [(0.0, 50.0, 0.0), (20.0, 50.0, 0.0)])
    xs = [val(lap.root, loc, 0, 1 + k * pl.TICK) for k in range(int(round((end - 1) / pl.TICK)) + 1)]
    zs = [val(lap.root, loc, 2, 1 + k * pl.TICK) for k in range(len(xs))]
    hops = [round(xs[k + 12] - xs[k], 2) for k in range(0, len(xs) - 12, 12) if max(zs[k:k + 12]) > 1.0]
    tail = [round((b - a) * 20.0, 2) for a, b in zip(xs[len(hops) * 12:], xs[len(hops) * 12 + 1:])]
    print("sprint_jump 20 blocks from rest: %d frames, hops of %s blocks, then the slide %s blocks/s (%.2f blocks)"
          % (end - 1, hops, tail, xs[-1] - xs[len(hops) * 12]))
    assert hops[0] < hops[1] - 0.8 and abs(xs[-1] - 20.0) < 1e-6 and max(zs[len(hops) * 12:]) < 1e-9
    assert tail and all(b < a for a, b in zip(tail, tail[1:])) and tail[-1] < 0.3
    assert abs(max(zs) - pl.JUMP_HEIGHT) < 1e-3
    print("steady hop, blocks per tick: %s; carried over the landing %.3f" % ([round(s, 3) for s in pl.HOP_STEPS], pl.HOP_CARRY))

    # 6. posed arms: the blocking arm, and the crouch on top of every pose
    q = pl.make_player("pose", "steve")
    q.place(1, (0.0, 55.0, 0.0), 0.0)
    q.hold("shield", hand="left")
    q.hold("bow")
    q.block(10, 40)
    stand = val(q.arm_l, rot, 0, 25)
    q.draw_bow(50, 80)
    bow = val(q.arm_r, rot, 0, 70)
    q.sneak(100)
    q.block(100, 130)
    low = val(q.arm_l, rot, 0, 115)
    q.draw_bow(140, 170)
    bow_low = (val(q.arm_r, rot, 0, 160), val(q.arm_l, rot, 0, 160))
    print("block: arm xRot %.4f standing (game -0.9425), %.4f sneaking (-0.5425); bow %.4f standing, %.4f sneaking"
          % (stand, low, bow, bow_low[0]))
    assert abs(stand + 0.9424779) < 1e-5 and abs(low + 0.5424779) < 1e-5
    assert abs(bow + math.pi / 2) < 1e-5 and all(abs(v + math.pi / 2 - 0.4) < 1e-5 for v in bow_low)
    lefty = pl.make_player("lefty", "ari")
    lefty.place(1, (0.0, 58.0, 0.0), 0.0)
    lefty.attack(10, hand="left")
    lo_l = min(val(lefty.arm_l, rot, 0, 10 + k * 0.3) for k in range(30))
    lo_r = min(val(lefty.arm_r, rot, 0, 10 + k * 0.3) for k in range(30))
    righty = pl.make_player("righty", "ari")
    righty.place(1, (0.0, 61.0, 0.0), 0.0)
    righty.attack(10)
    lo = min(val(righty.arm_r, rot, 0, 10 + k * 0.3) for k in range(30))
    print("attack(hand='left'): left arm to %.2f rad, right arm stays at %.2f; right-handed: right arm to %.2f" % (lo_l, lo_r, lo))
    assert lo_l < -1.0 and abs(lo_r) < 1e-6 and abs(lo_l - lo) < 0.25
    assert abs(val(lefty.arm_l, rot, 0, 20)) < 1e-6 and abs(val(lefty.body, rot, 2, 20)) < 1e-6
    lefty.attack(60, hand="left")
    lefty.attack(65, hand="left")                               # in the second half of the first: a second swing
    assert min(val(lefty.arm_l, rot, 0, 66 + k * 0.3) for k in range(20)) < -1.0 and abs(val(lefty.arm_l, rot, 0, 80)) < 1e-6
    info = lefty.throw(30, hand="left")
    assert min(val(lefty.arm_l, rot, 0, 30 + k * 0.3) for k in range(30)) < -1.0

    # 7. the API's rough edges
    t = pl.make_player("turtle", "efe")
    t.hold("torch")
    made = pl.equip(t, "turtle_scute")
    assert [o.name for o in made] == ["turtle_helmet_head"] and t.armor_at("boots", 1) is None, made
    for bad, call in (("a turtle chestplate", lambda: pl.equip(t, chestplate="turtle_scute")),
                      ("a held chest", lambda: t.hold("chest")),
                      ("a held nonsense", lambda: t.hold("no_such_thing")), ("wooden armor", lambda: pl.equip(t, "wood"))):
        try:
            call()
        except ValueError as e:
            print("%s -> ValueError: %s" % (bad, e))
        else:
            raise AssertionError(bad + " was accepted")
    assert t.holding_at("right", 1) == "torch"                  # a refused item leaves the hand as it was

    class FakeStage:
        cast = {}

    st = FakeStage()
    st.cast["steve"] = ch.make_player("old_steve")              # what Stage.actor("steve", "steve") builds
    town = pl.cast_town(st, 9, seed=1)
    print("cast_town beside an old Steve:", [p.name for p in town])
    assert all(isinstance(p, pl.Player) for p in town) and "player_steve" in [p.name for p in town]
    assert pl.cast_town(st, 9, seed=1) == town
    from engine import props

    s1 = pl.make_player("like1", "steve")
    s2 = pl.make_player("like2", "steve")
    o1 = s1.hold("iron_sword")
    o2 = s2.hold(props.make_item("iron_sword"), like="iron_sword")
    flat = pl.make_player("like3", "steve").hold(props.make_item("iron_sword"))
    assert max(abs(o1.matrix_basis[i][j] - o2.matrix_basis[i][j]) for i in range(4) for j in range(4)) < 1e-6
    assert max(abs(o1.matrix_basis[i][j] - flat.matrix_basis[i][j]) for i in range(4) for j in range(4)) > 0.1


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
    "legs": legs, "legs_blur": lambda: legs("legs_blur", blur=True), "legs_next": lambda: legs("legs_next", frame_offset=1),
    "legs_close": legs_close, "sneak_poses": sneak_poses, "killing_blow": killing_blow, "herobrine_first": herobrine_first,
    "herobrine_night": herobrine_night, "death_poof": death_poof,
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
