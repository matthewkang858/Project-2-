"""Independent checker's second probe of engine/breaking.py: edge cases, no rendering.

    $BPY -m tools.check_breaking_probe2
"""
import math
import sys

import bpy

from tools.check_breaking_probe import door_yaw, fresh, ok, BAD, rendered


def main():
    from engine import breaking, characters, look, shots, undead, village
    from engine.breaking import _door
    from films.lookdev import Stage

    scene = fresh()
    v = village.build_village(scene, seed=1)
    skyobj = look.set_time(scene, "night", sun_azimuth=176.0, sun_elevation=21.0)
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, skyobj)
    s = st.shot("one", 6.0)
    s.move(*breaking.DOOR_CAM["plaza"][:2])
    door = v.doors["house_a"]
    # lights before / after the split
    grp = door and [L for L in v.lantern_lights if L.get("group") == "house_a"]
    print("house_a lights before:", [(L.name, tuple(round(c, 2) for c in L.location), round(L["base_energy"], 1),
                                      L.get("mc_light")) for L in grp])
    new = breaking.door_torches(v, "house_a")
    again = breaking.door_torches(v, "house_a")
    ok("door_torches twice returns the same two lights", [o.name for o in new] == [o.name for o in again] and len(new) == 2)
    st.lights(s, scale=1.3, extra=[((9.7, -7.5, 2.9), 4.0)])
    print("after Stage.lights(scale=1.3, extra=the lookdev door key x4):",
          [(L.name, round(L.data.energy, 1)) for L in new],
          "old merged light hidden:", [L.name for L in bpy.data.objects if L.type == "LIGHT" and L.hide_render
                                       and L.get("group") == "house_a"])
    ok("the lookdev `extra` door key boosts BOTH door torches after the split", abs(new[0].data.energy - new[1].data.energy) < 1e-6,
       "%s" % [round(L.data.energy, 1) for L in new])
    # two zombies at one door with the same rhythm
    z1 = undead.add_zombie(st, "zombie")
    z2 = undead.add_zombie(st, "zombie_b")
    a = breaking.bang_on_door(z1, door, 1, 73, attempt=48, every=16, along=-0.3, shudder=8)
    one = [door_yaw(door, h) for h in a["hits"]]
    b = breaking.bang_on_door(z2, door, 1, 73, attempt=48, every=16, along=0.3, shudder=8)
    two = [door_yaw(door, h) for h in a["hits"]]
    ok("two zombies knocking in step on one door: the shudder is not doubled", max(abs(x - y) for x, y in zip(one, two)) < 1e-6,
       "one zombie %.3f rad, two zombies %.3f rad (%.0f degrees)" % (one[0], two[0], math.degrees(two[0])))
    d12 = (z1.pos_at(5) - z2.pos_at(5)).length
    print("two zombies stand %.2f apart (each 0.6 wide)" % d12)
    # the game's irregular rhythm in a 3.2 s shot
    for seed in (1, 2, 3, 4, 5, 6):
        print("  seed", seed, "knocks in 77 frames:", breaking.knock_frames(1, 78, seed=seed))
    # door opened while cracked: the copies follow
    breaking.crack(v.doors["house_b"], 10, 7)
    v.door_open("house_b", 20, open=True, frames=6)
    scene.frame_set(26)
    t = _door(v.doors["house_b"])
    var = [o for o in t.objects if not o.hide_render][0]
    bpy.context.view_layer.update()
    yaw = var.matrix_world.to_euler()[2] - float(v.doors["house_b"]["closed_yaw"])
    ok("a cracked door that is opened: the cracked copy turns with it", abs(abs(yaw) - math.pi / 2) < 1e-3, "%.3f" % yaw)
    # odd blocks
    cell0 = (-3, 31, v.world.top(-3, 31) + 1)
    for i, (bid, props) in enumerate((("anvil", {"facing": "north"}), ("oak_fence", {}), ("glass", {}),
                                      ("oak_leaves", {"persistent": "true"}), ("grass_block", {"snowy": "false"}),
                                      ("oak_stairs", {"facing": "east", "half": "bottom", "shape": "straight"}),
                                      ("torch", {}), ("sand", {}), ("oak_door", {"half": "lower", "facing": "east", "hinge": "left", "open": "false"}))):
        try:
            blk = breaking.place_block(v.collection, bid, (cell0[0] + 2 * i, cell0[1] + 3, cell0[2]), props, world=v)
            blk.crack(100, 5)
            r = breaking.break_block(blk, 120, camera=s, drop="auto")
            n = len(r["burst"].particles) if r["burst"] else 0
            try:
                t_ = breaking.break_ticks(bid)
            except KeyError as e:
                t_ = "no hardness"
            print("  %-12s faces %3d  shape boxes %d  particles %3d  texture %s  drop %s  ticks by hand %s" % (
                bid, len(blk.object.data.polygons), len(blk.shape), n, blk.particle_texture, r["drop"], t_))
        except Exception as e:                               # noqa: BLE001
            ok("place_block / crack / break_block of %s" % bid, False, repr(e)[:160])
    # an old-rig player (engine.characters)
    steve = st.actor("old_steve", "steve")
    rock = breaking.place_block(v.collection, "stone", (cell0[0], cell0[1] + 6, cell0[2]), world=v)
    steve.place(200, (cell0[0] + 0.5, cell0[1] + 6 - 0.9, float(cell0[2])), math.pi)
    try:
        m = breaking.mine(steve, rock, 205, duration=48, camera=s)
        ok("mine() with an engine.characters player", m["frame"] == 253 and len(m["swings"]) == 11, "break %s swings %d" % (m["frame"], len(m["swings"])))
    except Exception as e:                                   # noqa: BLE001
        ok("mine() with an engine.characters player", False, repr(e)[:200])
    # mine twice the same block (a director re-keying)
    try:
        m2 = breaking.mine(steve, rock, 205, duration=48, camera=s)
        print("mine() called twice on the same block: second call break %s, particles objects now %d" % (
            m2["frame"], sum(1 for o in bpy.data.objects if o.name.startswith("fx_") or "particle" in o.name)))
    except Exception as e:                                   # noqa: BLE001
        print("mine() twice raised:", repr(e)[:200])
    st.use(s, z1, z2, steve)
    st.finish()
    print("[probe2] %d failed%s" % (len(BAD), ": " + "; ".join(BAD) if BAD else ""))
    return len(BAD)


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
