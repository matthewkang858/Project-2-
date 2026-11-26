"""Checker's probe film for engine/underground.py, staged from its docstring ONLY (not from tools/underground_proof).

    $BPY -m tools.check_underground_probe SHOT:OFF[,OFF...] ...     render frames (offsets from the shot start) to
                                                                  out/test/check_underground_<shot>_<off>.png
    $BPY -m tools.check_underground_probe --zones                  print the hero heads' frame positions (no render)

One film, the two SKIES of the docstring, nine shots in story order (b01, b07, b08, b09, b12, b16, b24, b20, b22),
so cuts between the set's shots are real cuts.
"""
import math
import os
import sys
import time

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

from engine import players, shots, undead
from engine import underground as U
from films.lookdev import Stage, up

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIES = {"dusk": dict(preset="dusk", az=187.0, el=5.0, bloom=1.3, grade="warm"),
         "under": dict(preset="dusk", az=187.0, el=5.0, key=0.0, ambient=0.0, bloom=1.3, grade="neutral",
                       haze=0.0)}
F = U.F
HEROES = {}          # shot -> [(label, object)]
INFO = {}


def _cam(s, name, focus=None, move_to=None):
    c = U.CAMERAS[name]
    s.lens(c["lens"], c["fstop"])
    if "pos0" in c:
        s.move(c["pos0"], c.get("target0", c["target"]), c["pos"], c["target"])
    elif move_to is not None:
        s.move(c["pos"], c["target"], move_to[0], move_to[1])
    else:
        s.move(c["pos"], c["target"])
    s.focus(focus if focus is not None else c["target"])
    return c


def _under(st, s, ug, groups=None, inside=True, parts="all"):
    if parts == "all":
        st.use(s, *ug.parts)
    elif parts == "door":
        st.use(s, ug.door)
    g = {k: 0.7 for k in U.LIGHT_GROUPS}
    g.update(groups or {})
    st.lights(s, scale=0.0, groups=g, inside="ug_hall" if inside else ())


def hero(st, s, label, obj):
    HEROES.setdefault(s.name, []).append((label, obj))
    st.hero(s, label, obj)


def build(scene, sky=None):
    v, ug = U.build_village(scene, seed=1)
    A, C = v.anchors, U.CAMERAS
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, skies=SKIES, sky=sky)
    ug.register(st)

    # ---- beat 1: Steve walks down into the mouth (dusk)
    s = st.shot("b01", 3.5, sky="dusk")
    f = s.frame_start
    steve = players.add_player(st, "steve", "steve")
    path = [(5.0, 7.0, 0.0)] + v.paths["ug_down"][:10]
    steve.place(f, path[0], math.pi)
    INFO["b01_walk_end"] = steve.walk(f, path, speed=players.WALK_SPEED)
    st.use(s, steve)
    c = _cam(s, "b01_mouth", move_to=(tuple(Vector(C["b01_mouth"]["pos"]).lerp(Vector(A["ug_mouth_target"]), 0.15)),
                                     A["ug_mouth_target"]))
    hero(st, s, "steve", steve.head)
    st.lights(s, scale=1.3, groups={g: 1.0 for g in U.LIGHT_GROUPS}, near=A["ug_mouth_target"], radius=22)

    # ---- beat 7: the ceiling off, looking down into the cells (under)
    s = st.shot("b07", 3.0, sky="under")
    f = s.frame_start
    cells = {}
    for n in U.CELL_X:
        c_ = st.actor("cell_" + n, U.PROFESSION[n])
        c_.place(f, A["ug_cell_%s" % n], v.yaws["ug_cell_%s" % n])
        cells[n] = c_
    st.see_through(s, "ug_ceiling")
    c = _cam(s, "b07_down", focus=cells["dad"].head)
    for n, c_ in cells.items():
        if n == "dad":
            c_.look_at(f, C["b07_down"]["pos"], ease=0)
        else:
            c_.look_at(f, up(A["ug_aisle_%s" % n], 1.4), ease=0)
    st.use(s, *cells.values())
    for n in cells:
        hero(st, s, n, cells[n].head)
    _under(st, s, ug)

    # ---- beat 8: the back corner from the floor, Steve's legs, the hands in the slot (under)
    s = st.shot("b08", 3.0, sky="under")
    f = s.frame_start
    steve8 = players.add_player(st, "steve8", "steve")
    a, b = (16.6, -12.4, F), (16.6, -16.4, F)
    steve8.place(f + 10, a, math.pi)
    steve8.walk(f + 10, [a, b], speed=players.WALK_SPEED)
    zv = undead.add_zombie_villager(st, "kid_zv", "none", baby=True)
    INFO["hands"] = U.hands_in_slot(zv, f)
    c = _cam(s, "b08_slot", focus=(16.6, -14.97, F + 0.15))
    st.use(s, steve8, zv)
    hero(st, s, "zv head", zv.head)
    _under(st, s, ug, groups={"ug_corner": 0.35}, inside=False)

    # ---- beat 9: the lever, the wall opens, rack focus (under)
    s = st.shot("b09", 3.0, sky="under")
    f = s.frame_start
    steve9 = players.add_player(st, "steve9", "steve")
    steve9.place(f, A["ug_lever_stand"], v.yaws["ug_lever_stand"])
    dad = st.actor("cell_dad", "librarian")
    dad.place(f, A["ug_cell_dad"], v.yaws["ug_cell_dad"])
    INFO["b09"] = r9 = ug.open_wall(f + 12, player=steve9)
    c = _cam(s, "b09_lever", focus=A["ug_lever_target"])
    s.focus(A["ug_door_target"], at_s=(r9["open"] + 2) / 24.0)
    st.use(s, steve9, dad)
    hero(st, s, "dad", dad.head)
    _under(st, s, ug)

    # ---- beat 12: frontal, the swap to a zombie villager (under)
    s = st.shot("b12", 2.0, sky="under")
    f = s.frame_start
    dad.place(f, A["ug_cell_dad"], v.yaws["ug_cell_dad"])
    zv_dad = undead.add_zombie_villager(st, "zv_dad", "librarian")
    zv_dad.place(f, A["ug_cell_dad"], v.yaws["ug_cell_dad"])
    INFO["b12_end"] = undead.infect(dad, zv_dad, f + 10, attacker=A["ug_door_target"], max_back=0.05)
    c = _cam(s, "b12_cell", focus=dad.head)
    st.use(s, dad, zv_dad)
    hero(st, s, "dad", zv_dad.head)
    _under(st, s, ug)

    # ---- beat 16: wide down the aisle, zombie dad shakes, Steve jumps (under)
    s = st.shot("b16", 3.0, sky="under")
    f = s.frame_start
    INFO["b15_close"] = ug.close_wall(f - 4)            # beat 15 closes the wall (here: in b12's last frames)
    for n in ("farmer", "fletcher", "cleric"):
        cells[n].place(f, A["ug_cell_%s" % n], v.yaws["ug_cell_%s" % n])
    zv_dad.place(f, A["ug_cell_dad"], v.yaws["ug_cell_dad"])
    undead.shake(zv_dad, f, s.frame_end, 3.0)
    undead.effect_swirls(zv_dad, f, s.frame_end, effect="strength", camera=s)
    steve16 = players.add_player(st, "steve16", "steve")
    steve16.place(f, A["ug_jump_spot"], v.yaws["ug_jump_spot"])
    INFO["jumps"] = U.jump_loop(steve16, f + 4, s.frame_end)
    st.see_through(s, "ug_end_pier")
    c = _cam(s, "b16_aisle", focus=steve16.head)
    st.use(s, cells["farmer"], cells["fletcher"], cells["cleric"], zv_dad, steve16)
    for n in ("farmer", "fletcher", "cleric"):
        hero(st, s, n, cells[n].head)
    hero(st, s, "zv_dad", zv_dad.head)
    hero(st, s, "steve", steve16.head)
    _under(st, s, ug, parts="door")

    # ---- beat 24: inside the box, the wall opens, warm light, he runs, pan to dad's back (under)
    s = st.shot("b24", 3.0, sky="under")
    f = s.frame_start
    kidz = undead.add_zombie_villager(st, "kid_zv24", "none", baby=True)
    kidz.place(f, A["ug_box"], v.yaws["ug_box"])
    cam = C["b24_box"]
    kidz.look_at(f, U.cheat(A["ug_door_target"], up(A["ug_box"], 0.8), cam["pos"], 0.7), ease=0)
    dad = st.actor("dad24", "librarian")                 # (cell_dad is a zombie villager since b12)
    dad.place(f, A["ug_cell_dad"], v.yaws["ug_cell_dad"])
    for cut in ("ug_box_side", "ug_end_wall", "ug_slot"):
        st.see_through(s, cut)
    st.lights(s, scale=0.0, groups=dict({g: 0.7 for g in U.LIGHT_GROUPS}, ug_corner=2.0))
    st.use(s, *ug.parts)
    INFO["b24"] = r24 = ug.open_wall(f + 24)
    U.bounce(st, s, U.DOORWAY_GLOW, energy=U.DOORWAY_WATTS, color=U.POINT_COLOR, start=r24["open"], kind="torch")
    f2 = r24["open_end"] + 10
    INFO["b24_walk"] = kidz.walk(f2, [A["ug_box"], (14.6, -14.9, F)])
    s.lens(cam["lens"], cam["fstop"])
    # hold, then pan left (north) onto dad's back with his first step
    tgt0 = cam["target"]
    tgt1 = (14.45, -13.6, F + 1.2)
    s.move(cam["pos"], tgt0, cam["pos"], tgt1, ease="ease_in")
    s.focus(kidz.head)
    st.use(s, kidz, dad)
    hero(st, s, "baby", kidz.head)
    INFO["b24_shot"] = (s.frame_start, s.frame_end)

    # ---- beat 20: two children round the well, one swapped for an adult behind it (dusk)
    s = st.shot("b20", 5.0, sky="dusk")
    f = s.frame_start
    k1 = st.actor("kid1", "none", child=True)
    k2 = st.actor("kid2", "none", child=True)
    grown = st.actor("grown", "none")
    rw = v.paths["ug_round_well"]
    k1.place(f, rw[0], 0.0)
    e1 = k1.walk(f, rw, speed=4.4, run=True)
    k2.place(f + 4, rw[0], 0.0)
    k2.walk(f + 4, rw, speed=4.4, run=True)
    INFO["b20"] = U.swap_hidden(k1, grown, C["b20_well"]["pos"], f, e1, v.world, then=[(3.6, 1.8, 0)], speed=1.6)
    c = _cam(s, "b20_well")
    st.use(s, k1, k2, grown)
    hero(st, s, "kid2", k2.head)
    st.lights(s, scale=1.3, groups={g: 1.0 for g in U.LIGHT_GROUPS}, near=A["ug_mouth_target"], radius=24)

    # ---- beat 22: the stair foot, the child, the zombie from the dark (under)
    s = st.shot("b22", 2.0, sky="under")
    f = s.frame_start
    kid = st.actor("kid", "none", child=True)
    kid.place(f, A["ug_stair_foot"], v.yaws["ug_stair_foot"])
    kid.look_at(f, C["b22_foot"]["pos"], ease=0)
    z = undead.add_zombie(st, "zombie")
    zp = (A["ug_aisle_west_end"][0] + 6, A["ug_aisle_west_end"][1], F)
    z.place(f, zp, -math.pi / 2)
    z.aggro(f)
    z.walk(f, [zp, (zp[0] + 3.0, zp[1], F)])
    c = _cam(s, "b22_foot", focus=kid.head)
    st.use(s, kid, z)
    hero(st, s, "kid", kid.head)
    hero(st, s, "zombie", z.head)
    _under(st, s, ug, inside=False)

    st.finish()
    return {"film": film, "captions": [], "stage": st, "underground": ug, "village": v}


def zones(scene, film, frame, names):
    """Print where each hero head is in the frame (x, y from the top, %), and whether inside x 8-82, y 14-60."""
    scene.frame_set(frame)
    cam = scene.camera
    shot = next(s for s in film.shots if s.frame_start <= frame <= s.frame_end)
    for label, ob in HEROES.get(shot.name, []):
        dg = bpy.context.evaluated_depsgraph_get()
        ev = ob.evaluated_get(dg)
        pts = [ev.matrix_world @ Vector(c) for c in ev.bound_box]
        ctr = sum(pts, Vector()) / 8.0
        p = world_to_camera_view(scene, cam, ctr)
        x, y = p.x * 100, (1 - p.y) * 100
        ok = 8 <= x <= 82 and 14 <= y <= 60 and p.z > 0
        vis = not ob.hide_render
        print("[zones] %s f%d %-10s x %5.1f %% y %5.1f %% depth %.2f %s%s" % (shot.name, frame, label, x, y, p.z,
              "inside" if ok else "OUTSIDE", "" if vis else " (hidden)"), flush=True)


def main(argv):
    import render as R

    sys.modules["films._check_underground_probe"] = sys.modules[__name__]
    want = {}
    for a in argv:
        if a == "--zones":
            continue
        name, offs = a.split(":")
        want[name] = [int(o) for o in offs.split(",")]
    sky_of = {"b01": "dusk", "b20": "dusk"}
    for sky in SKIES:
        mine = {n: o for n, o in want.items() if sky_of.get(n, "under") == sky}
        if not mine and "--zones" not in argv:
            continue
        HEROES.clear()
        ses = R.Session("_check_underground_probe", sky=sky)
        ses.configure((540, 960), 16, 2, True)
        film = ses.film
        print("[probe] INFO", {k: v for k, v in INFO.items()}, flush=True)
        for n, offs in mine.items():
            shot = next(s for s in film.shots if s.name == n)
            for o in offs:
                fr = shot.frame_start + o
                path = os.path.join(ROOT, "out", "test", "check_underground_%s_%03d.png" % (n, o))
                t = time.time()
                zones(ses.scene, film, fr, None)
                ses.render_frame(fr, path)
                print("[probe] %s frame %d -> %s %.1f s" % (n, fr, path, time.time() - t), flush=True)
        if "--zones" in argv and not mine:
            for s in film.shots:
                if sky_of.get(s.name, "under") == sky:
                    zones(ses.scene, film, (s.frame_start + s.frame_end) // 2, None)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
