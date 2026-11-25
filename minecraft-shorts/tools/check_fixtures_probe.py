"""Independent checker's numeric probe of engine/fixtures.py (no rendering): how the API behaves when a director
uses it from the docstring alone. Prints one line per check; exit code 1 if one fails.

    $BPY -m tools.check_fixtures_probe
"""
import math
import sys

import bpy

FAILED = []


def ok(label, cond, detail=""):
    """Print one check; remember it when it failed."""
    if not cond:
        FAILED.append(label)
    print("%-4s %s%s" % ("OK" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""), flush=True)


def visible(ob, f):
    """Rendered at frame f? (hide_render evaluated)"""
    bpy.context.scene.frame_set(f)
    return not ob.hide_render


def main():
    # ---- importing the module leaves the scene untouched
    bpy.ops.wm.read_factory_settings(use_empty=True)
    before = (len(bpy.data.objects), len(bpy.data.materials), len(bpy.data.images), len(bpy.data.meshes),
              len(bpy.data.lights), len(bpy.data.actions))
    from engine import fixtures as fx  # noqa: E402
    from engine import blocks, mobs, shots
    after = (len(bpy.data.objects), len(bpy.data.materials), len(bpy.data.images), len(bpy.data.meshes),
             len(bpy.data.lights), len(bpy.data.actions))
    ok("import engine.fixtures adds no datablock", before == after, "%s -> %s" % (before, after))

    scene = bpy.context.scene
    coll = blocks.new_collection(scene, "set")
    st = fx.site(coll)
    w = st.world
    w.fill(-4, -4, -1, 30, 30, -1, "cobblestone")

    # ---- hopper stream: are items visible BEFORE they are released (hanging in the air)?
    w.set(2, 2, 0, "chest", {"facing": "south"})
    h = fx.hopper(st, (2, 2, 1))
    items = [mobs.make_dropped_item(i, name="pr%d" % n, seed=n) for n, i in
             enumerate(("iron_ingot", "iron_ingot", "poppy", "iron_ingot"))]
    plans = h.stream(items, 40, every=6, height=2.2, seed=1)
    rel = [int(round(p["track"][0][0])) for p in plans]
    early = []
    for it, f0 in zip(items, rel):
        cop = it.copies[0]
        vis_before = [f for f in (1, 20, f0 - 1) if visible(cop, f)]
        if vis_before:
            early.append((it.name, f0, vis_before, tuple(round(c, 2) for c in it.pos_at(f0 - 1))))
    ok("hopper.stream without a Stage: no item is rendered before its release frame", not early, str(early))
    gone = [p["frame"] for p in plans]
    after_gone = [(it.name, g) for it, g in zip(items, gone) if visible(it.copies[0], g) or visible(it.copies[0], g + 30)]
    ok("hopper.stream: every item is gone from plan['frame'] on", not after_gone, str(after_gone))
    lands = [p["landed"] for p in plans]
    print("     releases %s, landed %s, gone %s" % (rel, lands, gone))

    # the same with a Stage-like show() at a shot start before the release (what Stage.finish does)
    it2 = mobs.make_dropped_item("iron_ingot", name="pr_stage", seed=9)
    h2 = fx.hopper(st, (6, 2, 1))
    p2 = h2.absorb(it2, 50, height=2.2)
    it2.show(1, False)
    it2.show(30, True)          # the shot starts on 30, the item is released on 50
    vis = [f for f in (30, 40, 49) if visible(it2.copies[0], f)]
    ok("absorb() in a shot that starts 20 frames before the release: not rendered before it", not vis,
       "rendered on %s at %s" % (vis, tuple(round(c, 2) for c in it2.pos_at(45))))

    # ---- frame 1: everything keyed on the first frame of a film
    c = fx.chest(st, (10, 2, 0), "south")
    done = c.open(1)
    scene.frame_set(1)
    a1 = c.lid.rotation_euler[0]
    scene.frame_set(done)
    a2 = c.lid.rotation_euler[0]
    ok("chest.open(1): shut on frame 1, fully open on the returned frame", abs(a1) < 1e-6 and abs(a2 + math.pi / 2) < 1e-4,
       "%.3f -> %.3f" % (a1, a2))
    anv = fx.block(st, "anvil", (12, 2, 6), {"facing": "north"})
    d = fx.fall(anv, frame=1, world=st)
    scene.frame_set(1)
    z1 = anv.object.location.z
    ok("fall(frame=1): it stands at its start on frame 1 and lands", abs(z1 - 6.0) < 1e-6 and d["cell"] == (12, 2, 0),
       "z %.3f, cell %s" % (z1, d["cell"]))

    # ---- calling things twice
    c2 = fx.chest(st, (14, 2, 0), "north")
    c2.open(10)
    c2.open(10)
    ok("chest.open(10) twice = once", abs(c2.angle_at(22) - math.pi / 2) < 1e-9)
    anv2 = fx.block(st, "anvil", (16, 2, 9), {"facing": "north"})
    d1 = fx.fall(anv2, frame=10, world=st)
    try:
        d2 = fx.fall(anv2, frame=30, world=st)
        ok("fall() called twice on one block re-keys it (docstring)", d2["height"] == d1["height"],
           "first: %s blocks to %s; second: %s blocks to %s" % (d1["height"], d1["cell"], d2["height"], d2["cell"]))
    except ValueError as exc:
        ok("fall() called twice on one block re-keys it (docstring)", False, str(exc)[:140])
    fl1 = fx.water(st, [(x, 8, 0) for x in range(3)], name="dup")
    fl2 = fx.water(st, [(x, 10, 0) for x in range(3)], name="dup")
    ok("two water bodies with the same name both exist with their own objects", fl1.name != fl2.name and
       not set(o.name for o in fl1.objects) & set(o.name for o in fl2.objects), "%s / %s" % (fl1.name, fl2.name))

    # ---- chest and stage
    ok("an animated Chest can be put in a Stage's cast (has show())", hasattr(c, "show"))
    ok("a Fluid can be shown / hidden per shot (has show())", hasattr(fl1, "show"))
    bd = fx.bed(st, (20, 2, 0), "north", "red", frame=40)
    ok("bed() result can be given to Stage.use (has .name)", hasattr(bd, "name"))

    # ---- release() with a World where the plank is still there (redstone planks pulled one block in)
    w.fill(20, 10, -1, 26, 10, -1, "cobblestone")
    for x in range(20, 24):
        w.set(x, 10, 7, "oak_planks")              # a plank that another module moves (not a fixtures.Block)
    row = fx.shelf(st, [(x, 10, 8) for x in range(20, 24)], "anvil", {"facing": "north"})
    try:
        fx.release(row, 30, world=st)
        ok("release() over planks still in the World", True)
    except ValueError as exc:
        ok("release() over planks still in the World: refused (no land= in release())", False, str(exc)[:160])

    # ---- landing of anvils released 1 block apart: twelve in a row
    w.fill(0, 20, -1, 13, 20, -1, "cobblestone")
    row12 = fx.shelf(st, [(x, 20, 13) for x in range(0, 12)], "anvil", {"facing": "west"})
    drops = fx.release(row12, 100, world=st, chip="game", seed=4)
    lands = sorted({d_["frame_land"] for d_ in drops})
    chipped = sum(1 for d_ in drops if d_["chipped"])
    ok("twelve anvils, one call: twelve objects, all land on one frame", len({d_["block"].object.name for d_ in drops})
       == 12 and len(lands) == 1, "land %s, chipped by the game's chance at 13 blocks: %d of 12" % (lands, chipped))
    print("     13-block drop: frame_drop %d frame_land %d head_frame %d damage %s chance %.2f" % (
        drops[0]["frame_drop"], drops[0]["frame_land"], drops[0]["head_frame"], drops[0]["damage"], drops[0]["chance"]))

    # ---- water: what sits under a water sheet still has its top face; amount 1 sheet height
    sh = fx.water_sheet(st, 0, 24, 3, 27, 0, toward="south", amount=1, name="sheet")
    ok("water_sheet amount=1 is 1/9 high", abs(sh.top((1, 25, 0)) - 1 / 9.0) < 0.01, "%.4f" % sh.top((1, 25, 0)))
    print("[check_fixtures_probe] %d failed%s" % (len(FAILED), (": " + "; ".join(FAILED)) if FAILED else ""))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
