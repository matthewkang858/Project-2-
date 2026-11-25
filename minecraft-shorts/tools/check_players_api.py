"""Checker probe: every item of the brief builds in both hands; API edge cases.

    $BPY -m tools.check_players_api
"""
import math
import time

import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
from engine import characters as ch      # noqa: E402
from engine import players as pl         # noqa: E402

scene = bpy.context.scene
mats = ["wooden", "stone", "iron", "golden", "diamond", "netherite", "copper"]
items = ["%s_%s" % (m, t) for t in ("sword", "pickaxe", "axe", "shovel", "hoe") for m in mats]
items += ["bow", "shield", "torch", "redstone_torch", "bucket", "milk_bucket", "cooked_chicken", "steak", "golden_apple",
          "splash_potion", "ender_pearl", "gold_ingot", "emerald", "music_disc", "music_disc_13", "goat_horn", "totem",
          "note_block", "tnt", "redstone_lamp", "anvil", "dirt", "potion", "pearl", "milk", "horn", "chicken", "apple",
          "crafting_table", "lever", "redstone", "repeater", "piston", "iron_ingot", "bread", "water_bucket", "lava_bucket",
          "flint_and_steel", "fishing_rod", "trident", "crossbow", "spyglass", "oak_planks", "cobblestone", "lantern",
          "bell", "chest", "white_bed", "oak_door", "compass", "clock", "map", "book", "diamond", "stick", "arrow"]
t = time.time()
p = pl.make_player("it", "steve")
p.place(1, (0, 0, 0), 0.0)
okc, failed = 0, []
for k, item in enumerate(items):
    for hand in ("right", "left"):
        try:
            ob = p.hold(item, hand=hand, frame=10 + k)
            n = len(ob.data.polygons)
            if n == 0:
                failed.append((item, hand, "empty mesh"))
            else:
                okc += 1
        except Exception as e:                      # noqa: BLE001
            failed.append((item, hand, "%s: %s" % (type(e).__name__, str(e)[:90])))
print("items built: %d ok in %.1f s; failed:" % (okc, time.time() - t))
for f in failed:
    print("   ", f)
print("objects hanging on one rig after %d holds: %d" % (len(items) * 2, len(p._attached)))

# every armor material, every slot
for m in pl.ARMOR_MATERIALS:
    try:
        made = pl.equip(pl.make_player("ar_" + m, "steve"), m)
        print("  armor %-12s %d boxes, faces %s" % (m, len(made), [len(o.data.polygons) for o in made]))
    except Exception as e:                          # noqa: BLE001
        print("  armor %s FAILED: %s" % (m, e))
for bad in ("wood", "emerald"):
    try:
        pl.equip(p, bad)
        print("  equip(%r) accepted" % bad)
    except Exception as e:                          # noqa: BLE001
        print("  equip(%r): %s: %s" % (bad, type(e).__name__, str(e)[:100]))
try:
    pl.make_player("x", "notch")
except Exception as e:                              # noqa: BLE001
    print("  make_player('notch'): %s: %s" % (type(e).__name__, str(e)[:100]))

# the killing blow: hurt (knock-back) and die on the same frame
d = pl.make_player("kb", "steve")
d.place(1, (0, 10, 0), 0.0)
d.hurt(20, from_point=(0, 8, 0))
info = d.die(20)
print("\nhurt(20, from) + die(20): colour alpha keys", ch.read_keys(d.torso, "color", 3))
for f in (20, 26, 31, 32, 38, 43, 44):
    scene.frame_set(f)
    print("   frame %d: red %s  roll %.0f deg  y %.2f z %.2f  visible %s" % (
        f, d.torso.color[3] < 0.5, math.degrees(d.root.rotation_euler.y), d.root.location.y, d.root.location.z, not d.torso.hide_render))
d2 = pl.make_player("kb2", "steve")
d2.place(1, (0, 14, 0), 0.0)
d2.die(20)
d2.hurt(20, from_point=(0, 12, 0))
print("die(20) + hurt(20, from): colour alpha keys", ch.read_keys(d2.torso, "color", 3))

# same name twice; add_player twice
a = pl.make_player("dup", "alex")
b = pl.make_player("dup", "alex")
print("\nmake_player twice with one name:", a.root.name, b.root.name, "| materials shared:", a.torso.data.materials[0] is b.torso.data.materials[0])


class FakeStage:
    cast = {}


st = FakeStage()
x = pl.add_player(st, "bob", "kai")
y = pl.add_player(st, "bob", "kai")
print("add_player twice:", x is y)
st.cast["steve"] = ch.make_player("steve")          # what st.actor("steve", "steve") builds
town = pl.cast_town(st, 6, seed=1)
print("cast_town with an old 'steve' in the cast:", [(type(t).__name__, t.name) for t in town])
town2 = pl.cast_town(st, 12, seed=1, names=["t%d" % i for i in range(12)])
print("12 players:", [(t.skin, t.slim) for t in town2])
print("idle seeds:", [t.idle_seed for t in town2])

# a very short walk
s = pl.make_player("short", "ari")
s.place(1, (0, 20, 0), 0.0)
e = s.walk(1, [(0, 20, 0), (0, 19.5, 0)])
print("\nwalk of 0.5 block at the default speed: %d frames; root y per frame %s" % (
    e - 1, [round(ch._val(s.root, "location", 1, f), 2) for f in range(1, e + 2)]))
e = s.walk(40, [(0, 19.5, 0), (0, 19.5, 0)])
print("walk of zero length returns", e)
# polyline API parity with Character.walk: from_current, run
r = pl.make_player("run", "efe")
r.place(1, (0, 30, 0), 0.0)
e = r.walk(1, [(4, 30, 0)], from_current=True, run=True)
print("walk(from_current, run): end %d, speed %.2f" % (e, 4.0 / ((e - 1) / 24.0)))
# sleep
z = pl.make_player("sleep", "noor")
z.sleep(1, (0.5, 40.0, 0.5625), 0.0)
scene.frame_set(1)
bpy.context.view_layer.update()
print("sleeping: head at %s, feet-root at %s, eye_point %s" % (tuple(round(c, 2) for c in z.head.matrix_world.translation),
                                                               tuple(round(c, 2) for c in z.root.matrix_world.translation),
                                                               tuple(round(c, 2) for c in z.eye_point(1))))
