"""Independent checker's film-like probe of engine/fixtures.py, written from its docstring: three shots in the real
village (edit hook), the real look (golden hour), films.lookdev.Stage, motion blur on.

  slide   film three beat 11: a platform with a still water sheet, a 2-wide lava slot at its edge; an iron golem
          slides sideways and drops in; white puff; the glow flickers
  hopper  film three beat 12: a hopper on a chest at the tower's foot; three iron ingots and a poppy land and vanish
  anvils  film five beat 19: twelve anvils on a plank shelf over a cobblestone road, released in one call, zombies
          (pillager stand-ins) under three of them die on the landing frame

    $BPY -m tools.check_fixtures_film slide:0,1,2 hopper:0 ...   -> out/test/check_fixtures_<shot>_<k>.png
    (k = index into that shot's list of interesting frames, printed by --list)
"""
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "test")


def hook(b, out):
    """The set, put in through the village's edit hook (as the fixtures docstring shows)."""
    from engine import fixtures as fx
    from engine import sets

    w = b.w
    for x, y in ((-25, 37), (-13, 47)):
        oak = b.tree_at(x, y)
        if oak is not None:
            sets.remove_tree(b, oak)
    for x0, y0, x1, y1 in ((2, 26, 16, 50), (-31, 30, -4, 47)):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                b.clear_plants(x, y)
                b.reserved.add((x, y))
    # ---- film three: the platform (top at z 3), a 2-wide slot along its south edge, lava sunk in it
    x0, x1, y0, y1 = -20, -15, 38, 42
    w.fill(x0, y0, 0, x1, y1, 2, "stone")
    w.fill(x0, y0 - 3, -1, x1, y0 - 3, 3, "stone")          # the slot's outer wall
    w.fill(x0 - 1, y0 - 3, -1, x0 - 1, y1, 3, "stone")      # a west rim (no open edge for the water)
    w.fill(x0, y0 - 2, -2, x1, y0 - 1, -2, "stone")         # under the lava
    out["water"] = fx.water_sheet(b, x0, y0, x1, y1, 3, toward="south", amount=1, name="farm_water")
    out["lava"] = fx.lava(b, [(x, y, -1) for x in range(x0, x1 + 1) for y in (y0 - 2, y0 - 1)], name="farm_lava")
    # ---- film three: hopper on a chest
    out["hopper"], out["chest"] = fx.hopper_on_chest(b, (9, 46, 0), "south", animated=False)
    # ---- film five: wall 13 high, plank shelf, twelve anvils, a cobblestone road under it
    for x in range(3, 15):
        w.fill(x, 28, 0, x, 28, 12, "stone_bricks")
        w.set(x, 29, -1, "cobblestone")
        w.set(x, 30, -1, "cobblestone")
    out["planks"] = [fx.block(b, "oak_planks", (x, 29, 12)) for x in range(3, 15)]
    out["anvils"] = fx.shelf(b, [(x, 29, 13) for x in range(3, 15)], "anvil", {"facing": "west"})


def build(scene):
    """Village + set + three shots. Returns dict(film, stage, frames {shot: [frames]}, info)."""
    from engine import animals, fixtures as fx, look, mobs, shots, undead, village
    from films.lookdev import Stage, yaw_to

    look.setup_render(scene, res=(540, 960), samples=16, threads=2)
    out = {}
    v = village.build_village(scene, seed=1, edit=lambda b: hook(b, out))
    sk = look.set_time(scene, "golden", sun_azimuth=62.0, sun_elevation=27.0)
    look.setup_compositor(scene, bloom=1.0, grade="warm")
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, sk)
    frames, info = {}, {}

    # ---- slide (3 s)
    s = st.shot("slide", 3.0)
    f0 = s.frame_start
    g = st.cast["golem"] = mobs.make_iron_golem("golem")
    pos = (-17.5, 41.0, 3.0)
    g.place(f0, pos, yaw_to(pos, (-30.0, 41.0)))
    st.use(s, g)
    r = fx.slide(g, f0 + 6, "south", 41.0 - 38.0 + 0.7, drop=3.1)
    animals.poof(g, r["gone"], camera=s)
    out["lava"].flicker(r["edge"], r["edge"] + 40, at=r["gone"])
    s.lens(30, 5.6)
    s.move((-8.0, 36.2, 3.6), (-17.5, 39.0, 3.0))
    s.focus((-17.5, 39.5, 3.5))
    st.lights(s, scale=0.0)
    frames["slide"] = [f0 + 6, (f0 + 6 + r["edge"]) // 2, r["edge"], r["edge"] + 4, r["gone"], r["gone"] + 2]
    info["slide"] = {k: r[k] for k in ("frame", "edge", "frame_end", "gone")}

    # ---- hopper (3 s)
    s = st.shot("hopper", 3.0)
    f0 = s.frame_start
    items = []
    for i, iid in enumerate(("iron_ingot", "iron_ingot", "iron_ingot", "poppy")):
        it = mobs.make_dropped_item(iid, name="chk_hop_%d" % i, seed=i)
        st.cast[it.name] = it
        st.use(s, it)
        items.append(it)
    plans = out["hopper"].stream(items, f0 + 10, every=6, height=2.2)
    s.lens(40, 4.0)
    s.move((12.0, 42.2, 2.2), (9.5, 46.5, 1.5))
    s.focus((9.5, 46.5, 1.7))
    st.lights(s, scale=0.0)
    frames["hopper"] = [f0 + 2, plans[0]["landed"] or plans[0]["frame"] - 1, plans[2]["frame"] - 1]
    info["hopper"] = [(int(round(p["track"][0][0])), p["landed"], p["frame"]) for p in plans]

    # ---- anvils (4 s)
    s = st.shot("anvils", 4.0)
    f0 = s.frame_start
    rel = f0 + 8
    feet = {"z1": (5.5, 29.5, 0.0), "z2": (8.5, 29.6, 0.0), "z3": (11.5, 29.4, 0.0)}
    zs = []
    for name, p in feet.items():
        z = undead.add_zombie(st, name)
        z.place(f0, p, yaw_to(p, (20.0, 29.5)))
        zs.append(z)
    st.use(s, *zs)
    for p in out["planks"]:
        p.remove(rel)
    drops = fx.release(out["anvils"], rel, world=v, chip=9, seed=2)
    hits = fx.strikes(drops, feet)
    for name, hit in hits.items():
        st.cast[name].die(hit["frame_land"], camera=s)
    s.lens(20, 5.6)
    s.move((17.0, 31.6, 0.7), (8.0, 29.5, 4.5))
    s.focus((11.5, 29.5, 1.5))
    st.lights(s, scale=0.0)
    d = drops[0]
    frames["anvils"] = [rel + 1, (rel + d["frame_land"]) // 2, d["frame_land"] - 1, d["frame_land"], d["frame_land"] + 14]
    info["anvils"] = dict(release=rel, drop=d["frame_drop"], land=d["frame_land"], head=d["head_frame"],
                          height=d["height"], damage=d["damage"], chipped=sum(x["chipped"] for x in drops),
                          hits={k: (h["frame_land"], h["head_frame"], h["damage"]) for k, h in hits.items()})
    st.finish()
    return dict(film=film, stage=st, frames=frames, info=info, set=out, village=v)


def main(argv):
    import bpy

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    t0 = time.time()
    built = build(scene)
    print("[check_fixtures_film] built in %.1f s" % (time.time() - t0), flush=True)
    for k, v in built["info"].items():
        print("  %s: %s" % (k, v))
    for k, v in built["frames"].items():
        print("  frames %s: %s" % (k, v))
    film = built["film"]
    for arg in argv:
        if arg.startswith("-"):
            continue
        shot, _sep, idx = arg.partition(":")
        for i in [int(x) for x in idx.split(",")] if idx else range(len(built["frames"][shot])):
            f = built["frames"][shot][i]
            film.goto(f)
            path = os.path.join(OUT, "check_fixtures_%s_%d" % (shot, i))
            scene.render.filepath = path
            t = time.time()
            bpy.ops.render.render(write_still=True)
            print("[check_fixtures_film] %s frame %d -> %s.png  %.1f s" % (shot, f, path, time.time() - t), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
