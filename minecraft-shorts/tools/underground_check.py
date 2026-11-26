"""Numeric self-test of engine/underground.py (no rendering): `$BPY -m engine.underground` (about 20 s).

Checks the light model against the game's own formula, the flood fill, the set built into the village (edit
problems, validate, cells left for the piston door, cutaways, the light levels where the beats are staged), and the
mechanics (push, bed bounce, jump loop, hands at the slot, the swap behind the well). Exit code 1 if one fails.
"""
import math
import sys

import numpy as np

BAD = []


def ok(label, cond, detail=""):
    print("[ug check] %-4s %s%s" % ("ok" if cond else "FAIL", label, (" (" + detail + ")") if detail else ""), flush=True)
    if not cond:
        BAD.append(label)


def light_model():
    from engine import underground as U

    # lightmap.fsh by hand at block 15 / sky 0, default Brightness: c = 0.0392 + 1 * 1.0 * 1.4 (white end of the mix)
    c = U.lightmap_rgb(15, 0)
    ok("block 15: full white (clamped)", all(abs(x - 1.0) < 1e-6 for x in c), "%s" % (tuple(round(x, 3) for x in c),))
    dark = U.lightmap_rgb(0, 0)
    a = 10 / 255.0
    ng = 1 - (1 - a) ** 4
    want = (a + ng) / 2
    ok("block 0 sky 0 = the overworld's ambient #0a0a0a through notGamma at Brightness 0.5 (%.3f)" % want,
       all(abs(x - want) < 1e-6 for x in dark), "%.4f" % dark[0])
    m7 = U.lightmap_rgb(7, 0)
    ok("block 7 is warm (the game: G < R, B < G)", m7[1] < m7[0] and m7[2] < m7[1], "%s" % (tuple(round(x, 3) for x in m7),))
    lv = [max(U.lightmap_rgb(b, 0)) for b in range(16)]
    ok("brightness rises with the block level (clamped to 1 at 14-15)", all(b > a_ for a_, b in zip(lv[:15], lv[1:15]))
       and lv[15] >= lv[14],
       " ".join("%.2f" % x for x in lv))
    moody = U.lightmap_rgb(7, 0, gamma=0.0)
    ok("Brightness 'Moody' (gamma 0) is darker", max(moody) < max(m7), "%.3f < %.3f" % (max(moody), max(m7)))
    ok("dusk sky factor from timeline/day.json at tick 12480 = 0.508", abs(U.DUSK_SKY_FACTOR - 0.5082) < 1e-3,
       "%.4f" % U.DUSK_SKY_FACTOR)
    D, E = U.face_light(0, 15)
    ok("open sky, no torch: no dimming, no emission", D == 1.0 and max(E) == 0.0)
    D, E = U.face_light(12, 0)
    gr = E[1] / E[0]
    ok("film tint keeps lit stone off magenta: E G/R >= 0.93 at levels 6..14",
       all(U.face_light(b, 0)[1][1] / U.face_light(b, 0)[1][0] >= 0.93 for b in range(6, 15)), "level 12: %.3f" % gr)
    # flood fill: a torch 14 in a corridor
    op = np.zeros((20, 3, 3), dtype=bool)
    op[:, 0, :] = op[:, 2, :] = True
    op[:, :, 0] = op[:, :, 2] = True
    op[10, 1, 1] = True                                       # a wall across the corridor at x 10
    src = np.zeros_like(op, dtype=np.int16)
    src[2, 1, 1] = 14
    lvl = U.flood(op, src)
    ok("flood fill: minus one per block (BlockLightEngine)", [int(lvl[x, 1, 1]) for x in range(2, 9)] ==
       [14, 13, 12, 11, 10, 9, 8], "%s" % [int(lvl[x, 1, 1]) for x in range(0, 12)])
    ok("flood fill: stopped by an opaque block", int(lvl[11, 1, 1]) == 0 and int(lvl[10, 1, 1]) == 0)


def the_set():
    from engine import quick
    from engine import underground as U

    scene = quick.reset()
    quick.setup(scene)
    v, ug = U.build_village(scene, seed=1)
    ok("built without edit problems", not v.edit_problems, "%s" % v.edit_problems)
    ok("Village.validate() is clean", not v.validate(), "%s" % v.validate()[:3])
    w = v.world
    ok("the piston door's cells are empty in the World", all(w.get(*c) is None for c in U.door_cells()))
    ok("door, lever built (engine.redstone kit)", ug.door is not None and ug.lever is not None and len(ug.door.blocks) == 2)
    for name in U.CUTAWAYS:
        ok("cutaway %s registered with objects" % name, bool(v.cutaways.get(name)))
    e = ug.env
    lv = {n: e.levels(p) for n, p in (("dad", (14, -14, U.F + 1)), ("box", (U.BOX[0], U.BOX[1], U.F)),
                                      ("west", (-7, -11, U.F + 1)), ("stairs", (4, -11, U.F + 1)),
                                      ("rim", (4, 1, 0)), ("corner", (17, -16, U.F)))}
    print("[ug check]      levels (block, sky): %s" % lv)
    ok("dad's cell is torch-lit (block >= 10)", lv["dad"][0] >= 10)
    ok("the aisle falls off to the west (block <= 2 at x -7)", lv["west"][0] <= 2)
    ok("the box inside is baked sealed (open doorway stays dark: <= dad - 3)", lv["box"][0] <= lv["dad"][0] - 3)
    ok("the rim of the mouth gets block light from below", lv["rim"][0] >= 8 and lv["rim"][1] == 15)
    bright = e.brightness_at((14.5, -13.5, U.F + 1.5)), e.brightness_at((-7.5, -11.5, U.F + 1.5))
    ok("brightness dad's cell %.2f vs the dark end %.2f (x3 or more)" % bright, bright[0] >= 3 * bright[1])
    mats = sum(1 for ob in v.objects for m in ob.data.materials if m is not None and "|ug" in m.name)
    ok("baked faces carry their emission (%d meshes)" % mats, mats > 50)
    for n in ("ug_lip", "ug_stair_foot", "ug_cell_dad", "ug_box", "ug_corner", "ug_lever_stand"):
        ok("anchor %s" % n, n in v.anchors)
    hole = set(ug.res["hole"])
    crossing = []
    for name, pts in v.paths.items():
        if name.startswith("ug_"):
            continue
        for a, b in zip(pts[:-1], pts[1:]):
            for i in range(41):
                x = a[0] + (b[0] - a[0]) * i / 40.0
                y = a[1] + (b[1] - a[1]) * i / 40.0
                if (int(math.floor(x)), int(math.floor(y))) in hole:
                    crossing.append(name)
                    break
    ok("no village path crosses the stair's opening", not crossing, "%s" % sorted(set(crossing)))
    for name in U.CAMERAS:
        ok("camera %s has pos, target, lens" % name, all(k in U.CAMERAS[name] for k in ("pos", "target", "lens")))
    # sight lines: nothing in the World (cutaway cells are not in it) between a camera and the faces it is for
    A = v.anchors
    face = {n: (A["ug_cell_%s" % n][0], A["ug_cell_%s" % n][1] + 0.27, U.F + 1.65) for n in U.CELL_X}
    face["dad_mid"] = (A["ug_cell_dad_mid"][0], A["ug_cell_dad_mid"][1] + 0.27, U.F + 1.65)
    cases = [("b16_aisle", n) for n in U.CELL_X] + [("b12_cell", "dad"), ("b11_portrait", "dad"),
                                                    ("b10_cell_side", "dad"), ("b18_portrait", "dad_mid"),
                                                    ("b17_ots", "dad"), ("b07_down", "dad")]
    for cam, who in cases:
        blk = sight(w, U.CAMERAS[cam]["pos"], face[who])
        ok("sight %s -> %s's face is clear" % (cam, who), blk is None, "blocked at %s" % (blk,))
    blk = sight(w, U.CAMERAS["b07_down"]["pos0"], face["farmer"])
    ok("sight b07_down (start) -> the farmer's face is clear", blk is None, "blocked at %s" % (blk,))
    # beat 9: from the b09 camera the lever's handle, dad's head and the back wall's north face beside his robe
    c9 = U.CAMERAS["b09_lever"]["pos"]
    for what, p in (("the lever handle", (U.LEVER[0] + 0.5, U.LEVER[1] + 0.1, U.F + 1.5)),
                    ("dad's head", face["dad"]), ("the door's north face beside his robe",
                                                  (U.DOOR[0][0] + 0.85, U.DOOR[0][1] + 1.02, U.F + 0.9)),
                    ("the top of the doorway", (U.DOOR[0][0] + 0.5, U.DOOR[0][1] + 1.02, U.F + 1.9))):
        blk = sight(w, c9, p)
        ok("sight b09_lever -> %s is clear" % what, blk is None, "blocked at %s" % (blk,))
    # beat 19: dad's profile from b19's start (his look 20 degrees west of north, the camera's bearing)
    c19 = U.CAMERAS["b19_endwall"]
    hd = (A["ug_cell_dad_mid"][0], A["ug_cell_dad_mid"][1], U.F + 1.6)
    look = math.atan2(c19["look"][0] - hd[0], c19["look"][1] - hd[1])
    cam = math.atan2(c19["pos0"][0] - hd[0], c19["pos0"][1] - hd[1])
    ang = abs((math.degrees(look - cam) + 180.0) % 360.0 - 180.0)
    ok("b19: dad's look %.0f degrees west of north, %.0f degrees off the lens (profile: 70-110)"
       % (-math.degrees(look), ang), 70.0 <= ang <= 110.0 and -math.degrees(look) <= 21.0)
    # the bars connected as the game connects them (IronBarsBlock.attachsTo): the window above is air
    bars = {c: w.get(*c) for c in ((8, U.CELL_Y, U.F), (8, U.CELL_Y, U.F + 1), (14, U.FRONT_Y, U.F + 2), U.SLOT)}
    want = {(8, U.CELL_Y, U.F): ("true", "true"), (8, U.CELL_Y, U.F + 1): ("false", "true"),
            (14, U.FRONT_Y, U.F + 2): ("false", "true")}
    for cell, (n, s_) in want.items():
        st_ = bars[cell]
        ok("bars at %s: north %s, south %s" % (cell, n, s_), st_ is not None and st_[1].get("north") == n
           and st_[1].get("south") == s_, "%s" % (st_,))
    # the caps: 2-high cells; the doorway meshed dark and lit
    ok("every job cell has its cap at F + 2 (cutaway ug_caps)", len(ug.res["cut"]["ug_caps"]) == len(U.CELL_X))
    ok("doorway dark copy shown, lit copy hidden by default", ug.doorway["dark"] and ug.doorway["lit"]
       and all(not o.hide_render for o in ug.doorway["dark"]) and all(o.hide_render for o in ug.doorway["lit"]))
    ok("the lit doorway is baked brighter (open: door cells %s)" % sorted(set(ug.res["open_keep"].values())),
       min(b for b, _s in ug.res["open_keep"].values()) >= 7)
    out = e.levels((U.SLOT[0] + 1, U.SLOT[1], U.F))
    print("[ug check]      the game's box (bars pass light, -1 per step): about %d; baked sealed: %d"
          % (out[0] - 2, e.levels((U.BOX[0], U.BOX[1], U.F))[0]))
    return v, ug


def sight(world, a, b, step=0.02):
    """The first opaque full cube on the segment a -> b (None: clear)."""
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    n = max(2, int(np.linalg.norm(b - a) / step))
    for i in range(1, n):
        q = a + (b - a) * (i / n)
        c = tuple(int(math.floor(x)) for x in q)
        if world.is_solid(*c) and world.is_full_cube(*c):
            return c
    return None


def mechanics(v, ug):
    from engine import characters, players, undead
    from engine import underground as U

    dad = characters.make_villager("t_dad", "librarian")
    steve = players.make_player("t_steve")
    path = list(v.paths["ug_push"]) + [(5.0, -2.0, 0.0)]
    r = U.push(steve, dad, 10, path, v.world)
    ok("push: dad drops down the first step (z -0.5)", r["drops"] and abs(r["villager"][-1][1] + 0.5) < 1e-6,
       "drops %s, end z %.3f" % (r["drops"], r["villager"][-1][1]))
    ok("push: nudged along at 0.7..1.4 blocks/s", 0.7 <= r["speed"] <= 1.4, "%.2f" % r["speed"])
    gaps = [vv[0] - pp for vv, pp in zip(r["villager"], r["player"])]
    ok("push: the player never passes him (gap > 0)", min(gaps) > 0.0, "min gap %.3f" % min(gaps))
    ok("push: the player stops on the square", max(r["player"]) < 4.9, "%.2f" % max(r["player"]))
    dad2 = characters.make_villager("t_dad2", "librarian")
    steve2 = players.make_player("t_steve2")
    r2 = U.push(steve2, dad2, 10, path, v.world, taps=None, max_ticks=60, steps_down=9)
    gaps2 = [vv[0] - pp for vv, pp in zip(r2["villager"], r2["player"])]
    ok("held walk key: the player walks THROUGH him (the game's push is weakest at full overlap)",
       min(gaps2) < -0.6, "min gap %.2f" % min(gaps2))
    kid = characters.make_villager("t_kid", "farmer", child=True)
    bb = U.bed_bounce(kid, 10, v.beds[U.BED]["foot"], jumps=3)
    ok("bed (game, 3 calls): ONE jump of 1.252, then the bed's bounces 0.56, 0.24, 0.10, 0.04",
       len(bb["takeoffs"]) == 1 and bb["peaks"][:5] == [1.252, 0.556, 0.238, 0.104, 0.042], "%s" % bb["peaks"])
    kid6 = characters.make_villager("t_kid6", "farmer", child=True)
    b6 = U.bed_bounce(kid6, 10, v.beds[U.BED]["foot"], jumps=6)
    ok("bed (game, 6 calls): two jumps 36 frames apart (the calls in the air are spent)",
       len(b6["takeoffs"]) == 2 and b6["takeoffs"][1] - b6["takeoffs"][0] == 36, "take-offs %s" % b6["takeoffs"])
    kidr = characters.make_villager("t_kidr", "farmer", child=True)
    br = U.bed_bounce(kidr, 10, v.beds[U.BED]["foot"], jumps=4, mode="regular")
    ok("bed (regular, NOT the game): 4 jumps of 1.252 every 14.4 frames",
       br["peaks"][:4] == [1.252] * 4 and all(abs((b - a) - 14.4) <= 1.0 for a, b in
                                              zip(br["takeoffs"], br["takeoffs"][1:])), "%s" % br["takeoffs"])
    # beats 10-12: the blows in the capped cell, the head tracked through the b11 / b12 cameras
    hop(v)
    st = players.make_player("t_jumper")
    st.place(100, (8.5, -11.0, U.F), 0.0)
    jl = U.jump_loop(st, 100, 160)
    ok("jump loop: take-offs every 14-15 frames", all(14 <= b - a <= 15 for a, b in zip(jl, jl[1:])), "%s" % jl)
    z = max(st.pos_at(f).z for f in range(100, 116))
    ok("jump loop: 1.25 high", abs(z - U.F - 1.25) < 0.02, "%.3f" % (z - U.F))
    zv = undead.make_zombie_villager("t_kzv", baby=True)
    h = U.hands_in_slot(zv, 20)
    ok("hands: fingertips in the pane of the bars", h["pane"][0] <= h["tip_x"] <= h["pane"][1], "%s" % h)
    ok("hands: his back inside the box", h["body_back"] >= U.SLOT[0] - 1.0 - 1e-6)
    # the swap behind the well: a child running round the well's south side, filmed from the south-west
    child = characters.make_villager("t_child", "none", child=True)
    adult = characters.make_villager("t_adult", "none")
    route = v.paths["ug_round_well"]
    child.place(200, route[0], 0.0)
    end = child.walk(200, route, speed=4.4, run=True)
    cam = U.CAMERAS["b20_well"]["pos"]
    try:
        sw = U.swap_hidden(child, adult, cam, 200, end, v.world, then=[(3.6, 1.8, 0.0)], speed=1.6)
        ok("swap: found a hidden run behind the well (frame %d, hidden %s)" % (sw["frame"], sw["hidden"]), True)
    except ValueError as e:
        ok("swap: found a hidden run behind the well", False, str(e))


def hop(v):
    """Beats 10-12: dad's head through the b11_portrait and b12_cell cameras while hurt_in_cell / infect_in_cell
    jolt him (the cap stops the hop at 0.05): it must stay inside the Reels safe area on every frame."""
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    from engine import characters, undead
    from engine import underground as U

    A = v.anchors
    dad = characters.make_villager("t_hdad", "librarian")
    zv = undead.make_zombie_villager("t_hzv", "librarian")
    dad.place(300, A["ug_cell_dad"], v.yaws["ug_cell_dad"])
    r1 = U.hurt_in_cell(dad, 306, attacker=A["ug_door_target"])
    r2 = U.hurt_in_cell(dad, 320, attacker=A["ug_door_target"])
    r3 = U.infect_in_cell(dad, zv, 334, attacker=A["ug_door_target"])
    ok("cell: each blow is a jolt of 0.05 (the cap at F + 2 stops the hop)",
       all(abs(r["peak"] - 0.05) < 1e-3 for r in (r1, r2, r3)), "%s" % [round(r["peak"], 3) for r in (r1, r2, r3)])
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    cd = bpy.data.cameras.new("t_hopcam")
    cam = bpy.data.objects.new("t_hopcam", cd)
    scene.collection.objects.link(cam)
    cd.sensor_fit, cd.sensor_width = "AUTO", 36.0
    for name in ("b11_portrait", "b12_cell", "b10_cell_side"):
        c = U.CAMERAS[name]
        cam.location = c["pos"]
        cam.rotation_euler = (Vector(c["target"]) - Vector(c["pos"])).to_track_quat("-Z", "Y").to_euler()
        cd.lens = c["lens"]
        ys, xs, moves = [], [], []
        for who, f0, f1 in ((dad, 300, 334), (zv, 334, 350)):
            seg = []
            for f in range(f0, f1):
                scene.frame_set(f)
                dg = bpy.context.evaluated_depsgraph_get()
                p = who.head.evaluated_get(dg).matrix_world.translation
                q = world_to_camera_view(scene, cam, p)
                xs.append(q.x * 100.0)
                ys.append((1.0 - q.y) * 100.0)
                seg.append(ys[-1])
            moves.append(max(seg) - min(seg))
        ok("%s: dad's head stays in the safe area through the blows (y %.1f..%.1f %%, x %.1f..%.1f %%; the jolts "
           "move it %.1f %% / %.1f %% of the frame height)" % (name, min(ys), max(ys), min(xs), max(xs), *moves),
           min(ys) >= 14 and max(ys) <= 60 and min(xs) >= 8 and max(xs) <= 82 and max(moves) < 4.0)
    bpy.data.objects.remove(cam)


def main():
    light_model()
    v, ug = the_set()
    mechanics(v, ug)
    print("[ug check] %s" % ("all passed" if not BAD else "%d FAILED: %s" % (len(BAD), BAD)))
    return 1 if BAD else 0


if __name__ == "__main__":
    sys.exit(main())
