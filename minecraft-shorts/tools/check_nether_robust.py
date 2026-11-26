"""Reviewer's robustness probe of engine/nether.py (no rendering).

    $BPY -m tools.check_nether_robust
"""
import math
import sys


def counts(bpy):
    return {k: len(getattr(bpy.data, k)) for k in ("objects", "meshes", "materials", "images", "lights", "worlds",
                                                   "node_groups", "collections", "cameras")}


def main():
    import bpy

    bpy.ops.wm.read_factory_settings(use_empty=True)
    before = counts(bpy)
    scene = bpy.context.scene
    s_before = (scene.world, scene.render.use_compositing, scene.get("look_preset"))
    import engine.nether as nether  # noqa: F401
    after = counts(bpy)
    print("[robust] import leaves bpy.data unchanged:", before == after, before if before != after else "")
    print("[robust] import leaves scene untouched:", s_before == (scene.world, scene.render.use_compositing,
                                                                  scene.get("look_preset")))

    from engine import look, shots
    look.setup_render(scene, res=(270, 480), samples=4, threads=2, motion_blur=True)
    # two instances in one scene
    a = nether.build_bastion(scene)
    try:
        b = nether.build_bastion(scene, layout={"home": (0, 200, 0), "bridge": (400, 200, 0),
                                                "treasure": (-400, 200, 0)}, name="bastion_b")
        print("[robust] second instance built:", b.face_count, "faces")
        names_a = {o.name for o in a.collection.objects}
        names_b = {o.name for o in b.collection.objects}
        print("[robust] objects a %d, b %d, shared names %d" % (len(names_a), len(names_b), len(names_a & names_b)))
        print("[robust] pit block names a:", sorted(x.name for x in a.pit_blocks.values())[:2],
              "b:", sorted(x.name for x in b.pit_blocks.values())[:2])
        print("[robust] light names a:", sorted(o.name for o in a.lantern_lights)[:3],
              "b:", sorted(o.name for o in b.lantern_lights)[:3])
        print("[robust] lava names a:", sorted(o for o in a.lava)[:3], "b:", sorted(o for o in b.lava)[:3])
        print("[robust] b's lava objects:", [getattr(v, 'name', None) for v in list(b.lava.values())[:3]])
        print("[robust] cutaways a:", {k: [o.name for o in v] for k, v in a.cutaways.items()})
        print("[robust] cutaways b:", {k: [o.name for o in v] for k, v in b.cutaways.items()})
        # pit_open on b must not change a
        film = shots.Film(scene, fps=24)
        s = film.shot("x", 0.0, 1.0)
        b.pit_open(s)
        print("[robust] after b.pit_open: a's pit there at frame 5:",
              sum(x.there_at(5) for x in a.pit_blocks.values()), "/ 8;  b's:",
              sum(x.there_at(5) for x in b.pit_blocks.values()), "/ 8")
        scene.frame_set(5)
        print("[robust] rendered at frame 5: a pit objects", sum(not x.object.hide_render for x in a.pit_blocks.values()),
              "b pit objects", sum(not x.object.hide_render for x in b.pit_blocks.values()))
        print("[robust] validate a:", a.validate()[:3], " b:", b.validate()[:3])
        print("[robust] b anchors home_landing:", b.anchors["home_landing"], "(a:", a.anchors["home_landing"], ")")
    except Exception as e:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("[robust] second instance FAILED:", type(e).__name__, e)
    # set_nether twice, other biome; world / lamps / compositor left behind
    sky1 = nether.set_nether(scene, biome="nether_wastes")
    n_l1 = len([o for o in scene.objects if o.type == "LIGHT" and o.name.startswith("look_")])
    sky2 = nether.set_nether(scene, biome="crimson_forest")
    n_l2 = len([o for o in scene.objects if o.type == "LIGHT" and o.name.startswith("look_")])
    print("[robust] set_nether twice: look lamps %d then %d; worlds %d; world now %s" % (
        n_l1, n_l2, len(bpy.data.worlds), scene.world.name))
    sky3 = nether.set_nether(scene, biome="warped_forest", haze=0.0, bloom=0.0, vignette=0.0)
    print("[robust] haze 0 / bloom 0 / vignette 0 ok; compositor group:", bpy.data.node_groups.get(look.COMP_GROUP))
    try:
        nether.set_nether(scene, biome="basalt_deltas")
        print("[robust] basalt_deltas accepted (not a bastion biome)")
    except Exception as e:  # noqa: BLE001
        print("[robust] basalt_deltas:", e)
    try:
        nether.set_nether(scene, biome="the_end")
    except KeyError as e:
        print("[robust] unknown biome -> KeyError:", str(e)[:80])
    # a SKIES entry with a set_time-only key (az) is refused?
    try:
        nether.build_sky(scene, dict(preset="nether", biome="nether_wastes", az=60))
        print("[robust] az accepted silently")
    except TypeError as e:
        print("[robust] unknown key refused:", str(e)[:90])
    # Stage.lights with no near: every set's lanterns on
    from films import lookdev  # noqa: F401
    film = shots.Film(scene, fps=24)
    st = nether.Stage(scene, film, a, sky1)
    s = st.shot("one", 1.0)
    st.lights(s, 1.0)
    on = sum(1 for o in a.lantern_lights + b.lantern_lights if not o.hide_render)
    print("[robust] Stage.lights without lights_for: %d lantern lights on (a has %d; b's are not Stage's)"
          % (on, len(a.lantern_lights)))
    # what the lava lights cost: lights of every set always on
    lava_lights = [o for o in scene.objects if o.type == "LIGHT" and (o.get("mc_light") == "lava")]
    print("[robust] lava lights in scene: %d, total W %.0f" % (len(lava_lights), sum(o.data.energy for o in lava_lights)))
    # cutaway API on the Bastion
    try:
        st.see_through(s, "home_corridor_roof")
        st.remove(s, "home_south_parapet")
        print("[robust] see_through / remove ok")
    except Exception as e:  # noqa: BLE001
        print("[robust] cutaway FAILED", e)
    # pit_open on a shot starting at frame 1
    st2film = shots.Film(scene, fps=24)
    s1 = st2film.shot("first", 0.0, 0.5)
    a.pit_open(s1)
    scene.frame_set(1)
    print("[robust] pit_open on frame 1: rendered pit objects at frame 1:",
          sum(not x.object.hide_render for x in a.pit_blocks.values()))
    # ground() and anchors z
    print("[robust] ground at home_landing:", a.ground(*a.anchors["home_landing"][:2]), "anchor z",
          a.anchors["home_landing"][2])
    print("[robust] ground at bridge_pillar_top (pillar not in World):", a.ground(*a.anchors["bridge_pillar_top"][:2]),
          "anchor z", a.anchors["bridge_pillar_top"][2])
    print("[robust] ground at home_pit_center:", a.ground(4.5, 5.5), " whole:",
          a.whole.world.surface(4, 5, 40, -40))
    return 0


if __name__ == "__main__":
    sys.exit(main())
