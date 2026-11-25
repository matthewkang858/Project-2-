"""Independent checker probe for engine/players.py: close-ups on the plain test stage.

    $BPY -m tools.check_players_close legs items poses ...   -> out/test/check_players_close_<name>.png
"""
import math
import sys

import bpy
from mathutils import Vector

from engine import characters as ch
from engine import players as pl
from engine import quick


def stage(preset="golden"):
    scene = quick.reset()
    quick.setup(scene)
    quick.light(scene, preset)
    mat = ch._test_material("check_players_ground", "block/grass_block_top", (145, 189, 89))
    ch._test_box("check_players_ground", (-40.0, -40.0, -1.0), (40.0, 40.0, 0.0), mat)
    return scene


def out(scene, name):
    print("wrote", quick.render(scene, "check_players_close_" + name), flush=True)


def legs(frame=1, name="legs", blur=False):
    """A walking player in full armor seen from the side and three-quarter: the inner faces of the legs."""
    scene = stage()
    if blur:
        scene.render.use_motion_blur = True
        scene.render.motion_blur_shutter = 0.5
        scene.cycles.motion_blur_position = "START"
    specs = [("steve", "diamond", 90.0, (-1.3, 0.0, 0.0)), ("steve", "netherite", 130.0, (0.9, 0.0, 0.0)),
             ("alex", dict(leggings="iron", boots="golden"), 60.0, (-1.3, 0.0, 2.2)),
             ("kai", dict(boots="diamond"), 110.0, (0.9, 0.0, 2.2))]
    stone = ch._test_material("check_players_stone", "block/stone_bricks")
    ch._test_box("check_players_step", (-4.0, 0.8, 0.0), (4.0, 2.4, 2.2), stone)
    for i, (skin, armor, yaw, pos) in enumerate(specs):
        p = pl.make_player("leg%d" % i, skin)
        if isinstance(armor, dict):
            pl.equip(p, **armor)
        else:
            pl.equip(p, armor)
        yaw = math.radians(yaw)
        d = Vector((math.sin(yaw), -math.cos(yaw), 0.0))
        pos = Vector(pos) + Vector((0, 1.6 if pos[2] else 0.0, 0))
        a = pos - d * 3.0 * pl.WALK_SPEED * (40 - 10) / 24.0 / 3.0
        p.place(10, tuple(a), yaw)
        p.walk(10, [tuple(a), tuple(pos + d * 6.0)], ramp=(False, True))
    probe = bpy.data.objects["leg0_leg_r"]
    best = max(range(36, 50), key=lambda f: abs(ch._val(probe, "rotation_euler", 0, f)))
    print("legs widest on frame", best, "angle %.2f" % ch._val(probe, "rotation_euler", 0, best), flush=True)
    scene.frame_set(best + frame - 1)
    for i in range(4):
        r = bpy.data.objects["leg%d_root" % i]
        print("  player", i, "at", tuple(round(c, 2) for c in r.matrix_world.translation), flush=True)
    quick.camera(scene, (-0.2, -7.2, 1.9), (-0.2, 0.6, 1.6), lens=28)
    out(scene, name)


def legs_seq():
    for k in (1, 2, 3):
        legs(k, "legs_f%d" % k)


def items():
    """Right-hand items in strict profile (the camera on the player's right), as third person shows them."""
    scene = stage()
    stone = ch._test_material("check_players_stone", "block/stone_bricks")
    ch._test_box("check_players_step", (-4.0, 0.8, 0.0), (4.0, 2.4, 2.2), stone)
    names = ["diamond_sword", "iron_pickaxe", "torch", "tnt", "bow", "cooked_chicken"]
    for i, item in enumerate(names):
        r, c = divmod(i, 3)
        p = pl.make_player("it%d" % i, pl.SKINS[i])
        p.hold(item)
        p.place(1, ((c - 1) * 1.7, r * 1.6, r * 2.2), math.radians(90))
    scene.frame_set(1)
    quick.camera(scene, (0.3, -7.6, 2.0), (0.0, 0.6, 1.95), lens=26)
    out(scene, "items")


def items_left():
    """Left-hand items and the shield, from the player's left and from three-quarter front."""
    scene = stage()
    stone = ch._test_material("check_players_stone", "block/stone_bricks")
    ch._test_box("check_players_step", (-4.0, 0.8, 0.0), (4.0, 2.4, 2.2), stone)
    specs = [("shield", "left", -90.0), ("shield", "left", -20.0), ("shield", "left", 160.0),
             ("diamond_sword", "left", -90.0), ("note_block", "right", 25.0), ("goat_horn", "right", 60.0)]
    for i, (item, hand, yaw) in enumerate(specs):
        r, c = divmod(i, 3)
        p = pl.make_player("il%d" % i, pl.SKINS[(i + 3) % 9])
        p.hold(item, hand=hand)
        p.place(1, ((c - 1) * 1.7, r * 1.6, r * 2.2), math.radians(yaw))
    scene.frame_set(1)
    quick.camera(scene, (0.3, -7.6, 2.0), (0.0, 0.6, 1.95), lens=26)
    out(scene, "items_left")


def poses():
    """Crouch from the side, crouch-walk, eating from the front and the side, blocking from the side, bow from the side."""
    scene = stage()
    stone = ch._test_material("check_players_stone", "block/stone_bricks")
    ch._test_box("check_players_step", (-4.0, 0.8, 0.0), (4.0, 2.4, 2.2), stone)
    a = pl.make_player("po_sneak", "steve")
    pl.equip(a, "iron")
    a.place(1, (-1.7, 0.0, 0.0), math.radians(90))
    a.sneak(1)
    b = pl.make_player("po_eat", "alex")
    b.hold("cooked_chicken")
    b.place(1, (0.0, 0.0, 0.0), math.radians(20))
    b.eat(5, 60)
    c = pl.make_player("po_eat2", "kai")
    c.hold("golden_apple")
    c.place(1, (1.7, 0.0, 0.0), math.radians(90))
    c.eat(5, 60)
    d = pl.make_player("po_block", "efe")
    d.hold("shield", hand="left")
    d.place(1, (-1.7, 1.6, 2.2), math.radians(-90))
    d.block(5, 60)
    e = pl.make_player("po_bow", "noor")
    e.hold("bow")
    e.place(1, (0.0, 1.6, 2.2), math.radians(90))
    e.draw_bow(5, 60)
    g = pl.make_player("po_horn", "sunny")
    g.hold("goat_horn")
    g.place(1, (1.7, 1.6, 2.2), math.radians(60))
    g.toot(5, 60)
    scene.frame_set(34)
    quick.camera(scene, (0.3, -7.6, 2.0), (0.0, 0.6, 1.95), lens=26)
    out(scene, "poses")


def head_swing():
    """Herobrine with watch() from the first frame of a shot: frames 1, 4 and 12 side by side (three of him)."""
    scene = stage("night")
    for i, f in enumerate((1, 4, 12)):
        hb = pl.make_player("hbs%d" % i, "herobrine")
        hb.place(1 - f + 1 if False else 1, ((i - 1) * 1.5, 0.0, 0.0), 0.0)
        # shift each copy's timeline so that one render shows frames 1, 4 and 12 of the same call
        start = 13 - f
        hb.place(start, ((i - 1) * 1.5, 0.0, 0.0), 0.0)
        hb.watch(start, start + 60, ((i - 1) * 1.5 + 4.0, -3.0, 1.0))
    scene.frame_set(12)
    quick.camera(scene, (0.0, -6.0, 1.6), (0.0, 0.0, 1.45), lens=45)
    out(scene, "head_swing")


WHAT = {"legs": legs, "legs_blur": lambda: legs(1, "legs_blur", True), "legs_seq": legs_seq, "items": items,
        "items_left": items_left, "poses": poses, "head_swing": head_swing}

def inner():
    """Static: armored players with the legs apart, seen from the side the inner faces of the far leg face."""
    scene = stage()
    specs = [("steve", "diamond", 90.0, -1.7), ("steve", "iron", 60.0, 0.0), ("noor", dict(boots="golden"), 90.0, 1.7)]
    for i, (skin, armor, yaw, x) in enumerate(specs):
        p = pl.make_player("in%d" % i, skin)
        if isinstance(armor, dict):
            pl.equip(p, **armor)
        else:
            pl.equip(p, armor)
        p.place(1, (x, 0.0, 0.0), math.radians(yaw))
        p.leg_r.rotation_euler[0] = 0.95
        p.leg_l.rotation_euler[0] = -0.95
    scene.frame_set(1)
    for i in range(3):
        bpy.data.objects["in%d_leg_r" % i].rotation_euler[0] = 0.95
        bpy.data.objects["in%d_leg_l" % i].rotation_euler[0] = -0.95
    quick.camera(scene, (0.0, -4.6, 0.9), (0.0, 0.0, 0.55), lens=36)
    out(scene, "inner")


WHAT["inner"] = inner

def crouch():
    """Sneaking: plain Steve from his right, Kai three-quarter, armored Steve from his left."""
    scene = stage()
    a = pl.make_player("cr0", "steve")
    a.place(1, (-1.0, 0.0, 0.0), math.radians(90))
    a.sneak(1)
    b = pl.make_player("cr1", "kai")
    b.hold("torch")
    b.place(1, (0.0, 0.0, 0.0), math.radians(35))
    b.sneak(1)
    c = pl.make_player("cr2", "steve")
    pl.equip(c, "iron")
    c.hold("shield", hand="left")
    c.place(1, (1.0, 0.0, 0.0), math.radians(-90))
    c.sneak(1)
    c.block(1, 40, ease=0)
    scene.frame_set(10)
    quick.camera(scene, (0.0, -6.0, 1.3), (0.0, 0.0, 0.9), lens=30)
    out(scene, "crouch")


WHAT["crouch"] = crouch

if __name__ == "__main__":
    for n in sys.argv[1:]:
        WHAT[n]()
