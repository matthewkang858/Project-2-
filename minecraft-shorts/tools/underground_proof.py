"""Proof stills of engine/underground.py: the set of "Two Apples" in the real village, cast and look.

Not a film: one 1-second shot per still through films.lookdev.Stage and render.py's Session, with the multi-sky
layout the film will use (SKIES: the dusk square; "under" = the same dusk with no sun, no sky fill and no bounce
lamps for the shots under the ground, where the game's light is the baked block light and the torches).

    $BPY -m engine.underground mouth lip down          # -> out/test/underground_<name>.png (540x960, 16 spp, 2 threads)
    $BPY -m tools.underground_proof mouth lip           # the same
    UG_RES=270x480 ...                                  # cheaper framing checks (8 spp)

Every still is checked with tools/palette_check (the plain check, and the same with the set's baked materials
counted as the textures they are: stone baked dark is still stone) and its hero against the Reels safe area.
"""
import math
import os
import sys
import time

from engine import players, shots, undead
from engine import underground as U
from films.lookdev import Stage, up, yaw_to

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIES = {
    "dusk": dict(preset="dusk", az=187.0, el=5.0, bloom=1.3, grade="warm"),
    "under": dict(preset="dusk", az=187.0, el=5.0, key=0.0, ambient=0.0, bloom=1.3, grade="neutral", haze=0.0),
}
STILL_AT = 0.5
SHEET_FRAMES = 6


def _cam(s, name, focus=None, moving=False, **over):
    c = dict(U.CAMERAS[name])
    c.update(over)
    s.lens(c["lens"], c.get("fstop", 2.8))
    if moving and (c.get("pos0") or c.get("target0")):
        s.move(c.get("pos0", c["pos"]), c.get("target0", c["target"]), c["pos"], c["target"])
    else:
        s.move(c["pos"], c["target"])
    s.focus(focus if focus is not None else c.get("focus", c["target"]))
    return c


def _under(st, s, ug, scale=0.7, groups=None, near=None, radius=None, extra=(), inside=False, parts=True):
    if parts == "door":
        st.use(s, ug.door)                      # the lever hangs on ug_end_pier: out of a shot that sees through it
    elif parts:
        st.use(s, *ug.parts)                    # the door and the lever (registered: hidden where not used)
    g = {k: scale for k in U.LIGHT_GROUPS}
    g.update(groups or {})
    st.lights(s, scale=0.0, groups=g, near=near, radius=radius, extra=extra, inside="ug_hall" if inside else ())


SHOT = {"name": ""}


def _player(st, name="steve", skin="steve"):
    return players.add_player(st, name + "_" + SHOT["name"], skin)


def _actor(st, name, profession, **kw):
    return st.actor(name + "_" + SHOT["name"], profession, **kw)


# ---- the square at dusk ------------------------------------------------------------------------------------------

MOUTH_START = (5.0, 6.5, 0.0)


def shot_mouth(st, s, ug):
    """Beat 1: the mouth from a child's eye height east of it; the camera pans with Steve as he crosses in profile
    from the north and pushes in on the glowing hole as he sinks into it (still: STILL_AT["mouth"])."""
    A = st.v.anchors
    f0 = s.frame_start
    steve = _player(st, "steve")
    path = st.v.paths["ug_down"]
    steve.place(f0, MOUTH_START, math.pi)
    s.ug = dict(end=steve.walk(f0, [MOUTH_START] + path[1:10], speed=players.WALK_SPEED), steve=steve)
    st.use(s, steve)
    c = U.CAMERAS["b01_mouth"]
    s.lens(c["lens"], c["fstop"])
    s.move(c["pos0"], steve.head, c["pos"], c["target"])   # the aim rides on his head, eases onto the hole
    s.focus((5.0, 0.6, 0.9))
    st.hero(s, "steve", steve)
    st.lights(s, scale=1.3, groups={k: 1.0 for k in U.LIGHT_GROUPS}, near=A["ug_mouth_target"], radius=22.0)


def shot_lip(st, s, ug):
    """Beat 2: the baby at the lip, staring down, the glow from below as his key."""
    A = st.v.anchors
    f0 = s.frame_start
    kid = _actor(st, "kid", "none", child=True)
    kid.place(f0, A["ug_lip"], st.v.yaws["ug_lip"])
    cam = U.CAMERAS["b02_lip"]
    kid.look_at(f0, U.cheat(A["ug_lip_target"], A["ug_lip"], cam["pos"], 0.35), ease=0)
    st.use(s, kid)
    _cam(s, "b02_lip", focus=kid.head)
    st.hero(s, "child", kid)
    st.lights(s, scale=1.0, groups={k: 1.0 for k in U.LIGHT_GROUPS}, near=A["ug_lip"], radius=18.0)


def _push_setup(st, s, ug):
    A = st.v.anchors
    f0 = s.frame_start
    dad = _actor(st, "dad", "librarian")
    steve = _player(st, "steve")
    kid = _actor(st, "kid", "none", child=True)
    path = list(st.v.paths["ug_push"]) + [(A["ug_push_start"][0], -2.0, 0.0)]
    r = U.push(steve, dad, f0, path, st.v.world)
    cam = U.CAMERAS["b03_push"]
    dad.look_at(f0, (cam["pos"][0], cam["pos"][1] - 0.6, 1.4), ease=0)
    spot = U.CAMERAS["b03_push"]["kid"]
    kid.place(f0, spot, yaw_to(spot, (A["ug_push_start"][0], 2.0)))
    kid.look_at(f0, dad, ease=0)
    st.use(s, dad, steve, kid)
    return r, dad, steve, kid


def shot_push(st, s, ug):
    """Beat 3: dad pushed along to the mouth and down the first step, side-on and low; the child's head soft in
    the corner."""
    A = st.v.anchors
    r, dad, steve, kid = _push_setup(st, s, ug)
    _cam(s, "b03_push", focus=dad.head)
    st.hero(s, "dad", dad)
    st.lights(s, scale=1.0, groups={k: 1.0 for k in U.LIGHT_GROUPS}, near=A["ug_lip"], radius=20.0)
    s.ug = r


def shot_well(st, s, ug):
    """Beat 20: the square at dusk, the well, the glowing mouth beside it (the swap's camera)."""
    A = st.v.anchors
    _cam(s, "b20_well")
    st.lights(s, scale=1.3, groups={k: 1.0 for k in U.LIGHT_GROUPS}, near=A["well"], radius=24.0)


# ---- dad's house -------------------------------------------------------------------------------------------------

def shot_bed(st, s, ug):
    """Beat 4: the baby bouncing on the red bed, seen lengthwise from beside its foot, low."""
    v = st.v
    f0 = s.frame_start
    kid = _actor(st, "kid", "none", child=True)
    bed = v.beds[U.BED]
    kid.place(f0 - 2, bed["foot"], bed["yaw"] + math.pi)
    s.ug = U.bed_bounce(kid, f0 - 2, bed["foot"], jumps=6)
    kid.look_at(f0 - 2, U.CAMERAS["b04_bed"]["pos"], ease=0)
    st.use(s, kid)
    _cam(s, "b04_bed", focus=kid.head)
    st.hero(s, "child", kid)
    st.lights(s, scale=1.2, groups={U.HOUSE: 1.5}, near=v.anchors["house_a_center"], radius=14.0, inside=U.HOUSE)


def shot_bed_wide(st, s, ug):
    """Beat 5: the same room, wider, locked off, the door on the lens side: he stands on the bed facing the door."""
    v = st.v
    f0 = s.frame_start
    kid = _actor(st, "kid", "none", child=True)
    bed = v.beds[U.BED]
    kid.place(f0, bed["foot"], bed["yaw"] + math.pi)
    kid.look_at(f0, U.CAMERAS["b05_bed_wide"]["pos"], ease=0)
    st.use(s, kid)
    _cam(s, "b05_bed_wide", focus=kid.head)
    st.hero(s, "child", kid)
    st.lights(s, scale=1.2, groups={U.HOUSE: 1.5}, near=v.anchors["house_a_center"], radius=14.0, inside=U.HOUSE)


# ---- under the ground ---------------------------------------------------------------------------------------------

def shot_stairwell(st, s, ug):
    """Beat 6: the stairwell from high behind; the baby running down, tiny, head cheated toward a torch."""
    v = st.v
    f0 = s.frame_start
    kid = _actor(st, "kid", "none", child=True)
    path = v.paths["ug_down"]
    kid.place(f0, path[1], math.pi)
    kid.walk(f0, path[1:], speed=4.4, run=True)
    torch = (U.LIGHTS[2][0][0] + 0.1, U.LIGHTS[2][0][1] + 0.5, U.LIGHTS[2][0][2] + 0.6)   # the west wall's torch
    kid.track(f0, s.frame_end, torch, step=2, ease=4)       # the head follows the torch as he runs past it
    s.ug = dict(kid=kid)
    st.use(s, kid)
    _cam(s, "b06_stairwell", focus=kid.head)
    st.hero(s, "child", kid)
    st.lights(s, scale=0.0, groups={k: 1.0 for k in U.LIGHT_GROUPS})


def _shut(ug, f):
    if ug.door.is_open(f):
        ug.door.close(f)


def _cells(st, s, look=None, dad_profession="librarian", skip=(), dad_at="ug_cell_dad"):
    A = st.v.anchors
    f0 = s.frame_start
    _shut(st.ug, f0 - 6)
    out = {}
    for n in U.CELL_X:
        if n in skip:
            continue
        c = _actor(st, "cell_" + n, U.PROFESSION[n], level=2)
        spot = dad_at if n == "dad" else "ug_cell_%s" % n
        c.place(f0, A[spot], st.v.yaws[spot])
        if look is not None:
            c.look_at(f0, look(n), ease=0)
        out[n] = c
    st.use(s, *out.values())
    return out


def shot_down(st, s, ug, start=False):
    """Beat 7: the ceiling off, looking steeply down into the row of cells from above the aisle, sliding east from
    the farmer's pocket to dad's; dad looks up at us (start=True: the still is the first frame, over the farmer)."""
    c = U.CAMERAS["b07_down"]
    cells = _cells(st, s, look=lambda n: c["pos"] if n == "dad" else up(st.v.anchors["ug_aisle_%s" % n], 1.4))
    st.see_through(s, "ug_ceiling")
    st.see_through(s, "ug_caps")
    s.lens(c["lens"], c["fstop"])
    s.move(c["pos0"], c["target0"], c["pos"], c["target"])
    s.focus(cells["farmer" if start else "dad"].head)
    st.hero(s, "farmer" if start else "dad", cells["farmer" if start else "dad"])
    _under(st, s, ug, inside=True)


def shot_down_start(st, s, ug):
    shot_down(st, s, ug, start=True)


def shot_cell(st, s, ug, opened=False):
    """Beats 10-12: dad's cell from the aisle, frontal: the back wall closed (or open: the doorway black)."""
    A = st.v.anchors
    f0 = s.frame_start
    cells = _cells(st, s, look=lambda n: up(A["ug_aisle_%s" % n], 1.5))
    if opened:
        ug.door.open(f0 - 10)
        _cam(s, "b10_cell_side", focus=cells["dad"].head)
    else:
        _cam(s, "b12_cell", focus=cells["dad"].head)
    st.hero(s, "dad", cells["dad"])
    _under(st, s, ug, inside=True)


def shot_cell_open(st, s, ug):
    shot_cell(st, s, ug, opened=True)


def shot_cell_shut(st, s, ug):
    """The camera of cell_open with the wall shut (the pair proves the black doorway)."""
    A = st.v.anchors
    cells = _cells(st, s, look=lambda n: up(A["ug_aisle_%s" % n], 1.5))
    _cam(s, "b10_cell_side", focus=cells["dad"].head)
    st.hero(s, "dad", cells["dad"])
    _under(st, s, ug, inside=True)


def doorway(out_dir):
    """Mean brightness where the two stills of the b10 camera differ (the doorway), shut and open."""
    import numpy as np
    from PIL import Image

    a = np.asarray(Image.open(os.path.join(out_dir, "underground_cell_shut.png")).convert("L")).astype(float)
    b = np.asarray(Image.open(os.path.join(out_dir, "underground_cell_open.png")).convert("L")).astype(float)
    m = (a - b) > 25
    if m.sum() < 50:
        print("[ug doorway] too few changed pixels (%d)" % m.sum())
        return None
    print("[ug doorway] %d px change when the wall opens: shut mean %.0f / 255, open mean %.0f / 255 (x %.2f); the "
          "lit wall beside it %.0f" % (m.sum(), a[m].mean(), b[m].mean(), b[m].mean() / max(1.0, a[m].mean()),
                                       np.median(a[~m])))
    return a[m].mean(), b[m].mean()


def shot_lever(st, s, ug):
    """Beat 9 as the docstring stages it: Steve at ug_lever_stand flips the lever (his arm from the left edge),
    the camera holds on it, then pans right onto the back wall past dad's shoulder while the focus pulls there;
    a hidden repeater (4) opens the wall 12 frames after the click, when the pan has arrived."""
    A = st.v.anchors
    f0 = s.frame_start
    cells = _cells(st, s, look=lambda n: up(A["ug_aisle_%s" % n], 1.5))
    steve = _player(st, "steve")
    steve.place(f0, A["ug_lever_stand"], st.v.yaws["ug_lever_stand"])
    st.use(s, steve)
    r = ug.open_wall(f0 + 10, player=steve, repeater=4, sync="hand")
    c = U.CAMERAS["b09_lever"]
    s.lens(c["lens"], c["fstop"])
    U.hold_then_move(s, r["flip"] + 2, c["pos"], c["target0"], c["pos"], c["target"], frame_end=r["open"] - 1)
    s.focus(A["ug_lever_target"])
    s.focus(A["ug_door_target"], at_s=st.film.seconds(r["flip"] + 3), rack_s=0.4)
    s.ug = r
    st.hero(s, "dad", cells["dad"])                         # the still is the end of the pan: dad, the doorway
    _under(st, s, ug, inside=True)


def shot_aisle(st, s, ug):
    """Beat 16 / the falloff proof: wide down the aisle from the back corner, the cells on the left, the aisle
    falling off into the dark beyond the stair foot."""
    A = st.v.anchors
    f0 = s.frame_start
    _cells(st, s, look=lambda n: up(A["ug_aisle_%s" % n], 1.5), skip=("dad",))
    zv = _zv_dad(st, s)
    zv.look_at(f0, up(A["ug_aisle_dad"], 1.5), ease=0)
    undead.shake(zv, f0, s.frame_end, 3.0)
    undead.effect_swirls(zv, f0 - 30, s.frame_end, effect="strength", camera=s)
    steve = _player(st, "steve")
    steve.place(f0, A["ug_jump_spot"], st.v.yaws["ug_jump_spot"])
    s.ug = dict(takeoffs=U.jump_loop(steve, f0 - 6, s.frame_end))
    st.use(s, steve, zv)
    st.see_through(s, "ug_end_pier")
    _cam(s, "b16_aisle", focus=steve.head)
    st.hero(s, "steve", steve)
    st.hero(s, "zombie dad", zv)
    _under(st, s, ug, inside=True, parts="door")


def shot_endwall(st, s, ug):
    """Beat 19: dad's cell from the side through the see-through end wall, the piston wall behind him."""
    A = st.v.anchors
    cam = U.CAMERAS["b19_endwall"]
    cells = _cells(st, s, look=lambda n: up(A["ug_aisle_%s" % n], 1.5) if n != "dad" else cam["look"],
                   dad_at="ug_cell_dad_mid")
    st.see_through(s, "ug_end_wall")
    st.see_through(s, "ug_end_pier")
    _cam(s, "b19_endwall", focus=cells["dad"].head, moving=True)
    st.hero(s, "dad", cells["dad"])
    _under(st, s, ug, inside=True, parts="door")


def shot_endwall_alt(st, s, ug):
    """Beat 19, the other way: from the aisle west of the cell, low; his face up the aisle, the wall at his back."""
    A = st.v.anchors
    cam = U.CAMERAS["b19_alt"]
    cells = _cells(st, s, look=lambda n: up(A["ug_aisle_%s" % n], 1.5) if n != "dad" else cam["pos"])
    _cam(s, "b19_alt", focus=cells["dad"].head)
    st.hero(s, "dad", cells["dad"])
    _under(st, s, ug, inside=True)


def shot_slot(st, s, ug, hands=False, boots=False):
    """Beats 8 / 21: the back corner from the floor, the slot of iron bars in the box. "slot" (beat 21): black
    inside, the still taken before Steve walks into the view (a defocused trouser leg in front of the lens veils
    the slot purple); "slot_hands": the baby zombie villager's hands between the bars, focus on the slot;
    "slot_boots" (beat 8 as staged): Steve's boots pass in focus, the slot and the hands soft behind them."""
    A = st.v.anchors
    f0 = s.frame_start
    steve = _player(st, "steve")
    path = U.STEVE_PAST
    steve.place(f0, path[0], yaw_to(path[0], path[1]))
    s.ug = dict(end=steve.walk(f0, path, speed=players.WALK_SPEED), steve=steve)
    st.use(s, steve)
    if hands:
        zv = undead.add_zombie_villager(st, "kid_zv_" + SHOT["name"], "none", baby=True)
        U.hands_in_slot(zv, f0)
        U.shade_face(st.v, zv)
        st.use(s, zv)
    c = U.CAMERAS["b08_slot"]
    _cam(s, "b08_slot", focus=c["boot"] if boots else U.SLOT_FACE)
    st.hero(s, "slot", *st.v.cutaways["ug_slot"])
    _under(st, s, ug)


def shot_slot_hands(st, s, ug):
    shot_slot(st, s, ug, hands=True)


def shot_slot_boots(st, s, ug):
    shot_slot(st, s, ug, hands=True, boots=True)


def shot_box(st, s, ug, opened=False):
    """Beat 24: inside the box through its see-through side wall, the baby zombie villager lit by the strip of
    torchlight from the slot (opened=True: the wall in front of him has pulled aside, dad's cell light falls in)."""
    A = st.v.anchors
    f0 = s.frame_start
    if opened:
        r = ug.open_wall(f0 + 2, relight=(st, s))
        U.bounce(st, s, U.DOORWAY_GLOW, energy=U.DOORWAY_WATTS, color=U.POINT_COLOR, start=r["open"],
                 kind="torch")
        s.ug = r
    else:
        _shut(ug, f0 - 6)
    U.bounce(st, s, U.SLOT_STRIP, energy=U.SLOT_STRIP_WATTS, color=U.POINT_COLOR, kind="torch",
             name="ug_strip_" + s.name)
    zv = undead.add_zombie_villager(st, "kid_zv_" + SHOT["name"], "none", baby=True)
    zv.place(f0, A["ug_box"], st.v.yaws["ug_box"])
    cam = U.CAMERAS["b24_box"]
    zv.look_at(f0, U.cheat(A["ug_door_target"], up(A["ug_box"], 0.8), cam["pos"], 0.7), ease=0)   # 3/4 to us
    dad = _actor(st, "cell_dad", "librarian", level=2)
    dad.place(f0, A["ug_cell_dad"], st.v.yaws["ug_cell_dad"])
    st.use(s, zv, dad)
    for c in ("ug_box_side", "ug_end_wall", "ug_slot"):
        st.see_through(s, c)
    _cam(s, "b24_box", focus=zv.head)
    if opened:
        run = r["open_end"] + 6                              # he runs: one step into the doorway, the pan with it
        zv.look_at(run - 3, up(A["ug_cell_dad"], 1.5), ease=3)
        zv.walk(run, [A["ug_box"], (14.6, -14.9, U.F)])
        U.hold_then_move(s, run, cam["pos"], cam["target"], cam["pos1"], cam["target1"], frame_end=run + 16)
        s.focus(zv.head)
        s.focus(dad.head, at_s=st.film.seconds(run + 4), rack_s=0.5)
        s.ug.update(run=run)
    st.hero(s, "baby", zv)
    # the open wall lets dad's torch in (the game: the box re-lit to ~level 9 within a tick): its light steps up
    _under(st, s, ug, extra=[((14.5, -10.6, U.F + 1.9), 2.5)] if opened else ())


def shot_box_open(st, s, ug):
    shot_box(st, s, ug, opened=True)


def shot_foot(st, s, ug):
    """Beat 22: the foot of the stairs, the baby three-quarter front, the dark aisle behind him."""
    A = st.v.anchors
    f0 = s.frame_start
    kid = _actor(st, "kid", "none", child=True)
    kid.place(f0, A["ug_stair_foot"], st.v.yaws["ug_stair_foot"])
    kid.look_at(f0, U.CAMERAS["b22_foot"]["pos"], ease=0)
    z = undead.add_zombie(st, "zombie_" + SHOT["name"])
    zpos = (A["ug_stair_foot"][0] - 2.6, A["ug_aisle_west_end"][1], U.F)
    z.place(f0, zpos, yaw_to(zpos, A["ug_stair_foot"]))
    z.aggro(f0)
    st.use(s, kid, z)
    _cam(s, "b22_foot", focus=kid.head)
    st.hero(s, "child", kid)
    _under(st, s, ug)


def shot_falloff(st, s, ug):
    """The light proof: the aisle from the back corner with every point light off: what is left is the game's
    block light baked into the faces (measured against the lightmap by measure())."""
    _cam(s, "b16_aisle")
    st.lights(s, scale=0.0)


def _zv_dad(st, s):
    A = st.v.anchors
    zv = undead.add_zombie_villager(st, "dad_zv_" + SHOT["name"], "librarian", level=2)
    zv.place(s.frame_start, A["ug_cell_dad"], st.v.yaws["ug_cell_dad"])
    return zv


def _steve_at_counter(st, s, item=None):
    A = st.v.anchors
    steve = _player(st, "steve")
    if item:
        steve.hold(item)
    steve.place(s.frame_start, A["ug_aisle_dad"], st.v.yaws["ug_aisle_dad"])
    return steve


def shot_hit(st, s, ug):
    """Beats 10-12 in one proof shot from the b11 portrait camera: two blows (hurt_in_cell, 14 frames apart) and
    the infection (infect_in_cell): the red flash, the capped jolt (0.05 up for one tick), the swap; the attacker
    is not rendered (the blows come from ug_door_target, behind him)."""
    A = st.v.anchors
    f0 = s.frame_start
    cells = _cells(st, s, look=lambda n: up(A["ug_aisle_%s" % n], 1.5))
    dad = cells["dad"]
    zv = undead.add_zombie_villager(st, "dad_zv_" + SHOT["name"], "librarian", level=2)
    st.use(s, zv)
    s.ug = dict(blows=[f0 + 6, f0 + 20], infect=f0 + 34)
    for f in s.ug["blows"]:
        U.hurt_in_cell(dad, f, attacker=A["ug_door_target"])
    U.infect_in_cell(dad, zv, s.ug["infect"], attacker=A["ug_door_target"])
    zv.aggro(s.ug["infect"], ease=0)
    _cam(s, "b11_portrait", focus=dad.head)
    st.hero(s, "dad", dad)
    _under(st, s, ug, inside=True)


def shot_portrait(st, s, ug):
    """Beat 11: tight three-quarter portrait of dad (big nose, brow, book hat)."""
    A = st.v.anchors
    cells = _cells(st, s, look=lambda n: up(A["ug_aisle_%s" % n], 1.5))
    _cam(s, "b11_portrait", focus=cells["dad"].head)
    st.hero(s, "dad", cells["dad"])
    _under(st, s, ug, inside=True)


def shot_counter(st, s, ug):
    """Beat 13: side-on along the counter; the splash potion in the air between Steve and zombie dad."""
    f0 = s.frame_start
    _shut(ug, f0 - 6)
    zv = _zv_dad(st, s)
    steve = _player(st, "steve")
    spot = st.v.anchors["ug_counter_steve"]
    steve.place(f0, spot, yaw_to(spot, st.v.anchors["ug_cell_dad"]))
    undead.throw_potion(steve, zv, f0 + 6, camera=s)
    st.use(s, zv, steve)
    st.see_through(s, "ug_end_pier")
    st.see_through(s, "ug_end_wall")
    _cam(s, "b13_counter", focus=zv.head)
    st.hero(s, "zombie dad", zv)
    st.hero(s, "steve", steve)
    _under(st, s, ug, inside=True, extra=[((14.5, -10.6, U.F + 1.9), 1.8)], parts="door")
    U.bounce(st, s, U.COUNTER_BOUNCE)          # Steve's side toward the lens is away from every torch


def shot_apple(st, s, ug):
    """Beat 14: close on the single golden apple in Steve's hand, the green face soft behind it."""
    f0 = s.frame_start
    _shut(ug, f0 - 6)
    zv = _zv_dad(st, s)
    steve = _steve_at_counter(st, s, item="golden_apple")
    steve.raise_arm(f0, angle=55, ease=0)
    st.use(s, zv, steve)
    apple = tuple(steve.item_point("right", f0 + 12))
    _cam(s, "b14_apple", focus=apple, target=apple)
    st.hero(s, "apple", steve.item("right"))
    _under(st, s, ug, inside=True)


def shot_drift(st, s, ug):
    """Beat 15: drifting past zombie dad toward the black doorway (the wall open)."""
    f0 = s.frame_start
    zv = _zv_dad(st, s)
    if not ug.door.is_open(f0 - 8):
        ug.door.open(f0 - 8)
    undead.effect_swirls(zv, f0, s.frame_end, effect="strength", camera=s)
    st.use(s, zv)
    c = U.CAMERAS["b15_drift"]
    s.lens(c["lens"], c["fstop"])
    s.move(c["pos0"], c["target"], c["pos"], c["target"])
    s.focus((14.6, -15.0, U.F + 1.0))      # the subject is the black doorway (empty space): no hero to check
    _under(st, s, ug, inside=True)


def shot_ots(st, s, ug):
    """Beat 17: over Steve's shoulder at the counter, the emerald held up, dad (cured) facing him."""
    A = st.v.anchors
    f0 = s.frame_start
    cells = _cells(st, s, look=lambda n: up(A["ug_aisle_%s" % n], 1.5))
    steve = _steve_at_counter(st, s, item="emerald")
    steve.raise_arm(f0, angle=55, ease=0)
    cells["dad"].look_at(f0, steve, ease=0)
    st.use(s, steve)
    _cam(s, "b17_ots", focus=cells["dad"].head)
    st.hero(s, "dad", cells["dad"])
    _under(st, s, ug, inside=True)


def shot_follow(st, s, ug):
    """Beat 18: portrait of dad from far up the aisle (long lens, through the counter's windows): his head follows
    Steve, who walks away from him up the aisle (toward the lens, soft) with the book, to its 70-degree stop."""
    A = st.v.anchors
    f0 = s.frame_start
    cells = _cells(st, s, look=lambda n: up(A["ug_aisle_%s" % n], 1.5), skip=("dad",))
    dad = _actor(st, "cell_dad", "librarian", level=2)
    dad.place(f0 - 30, A["ug_cell_dad_mid"], st.v.yaws["ug_cell_dad_mid"])
    steve = _player(st, "steve")
    steve.hold("enchanted_book")
    a, b = A["ug_follow_start"], A["ug_follow_end"]
    steve.place(f0 - 30, a, yaw_to(a, b))
    steve.walk(f0 - 30, [a, b], speed=players.WALK_SPEED)
    dad.look_at(f0 - 30, steve, ease=0)
    dad.track(f0 - 30, s.frame_end, steve, step=2, ease=4)
    st.use(s, dad, steve)
    _cam(s, "b18_portrait", focus=dad.head)
    st.hero(s, "dad", dad)
    _under(st, s, ug, inside=True)


def shot_kill(st, s, ug):
    """Beat 23: Steve's last blow at the stair foot; the zombie tips over."""
    A = st.v.anchors
    f0 = s.frame_start
    steve = _player(st, "steve")
    steve.hold("iron_sword")
    foot = A["ug_stair_foot"]
    spot = (foot[0], foot[1] - 0.75, foot[2])
    z = undead.add_zombie(st, "zombie_" + SHOT["name"])
    zpos = (foot[0] - 1.35, -11.45, U.F)
    steve.place(f0, spot, yaw_to(spot, zpos))
    z.place(f0, zpos, yaw_to(zpos, spot))
    z.aggro(f0)
    steve.attack(f0 + 2)
    undead.die(z, f0 + 2, camera=s, attacker=steve)
    st.use(s, steve, z)
    _cam(s, "b23_kill", focus=steve.head)
    st.hero(s, "steve", steve)
    _under(st, s, ug)


BUILDERS = {
    "mouth": ("dusk", shot_mouth), "lip": ("dusk", shot_lip), "push": ("dusk", shot_push), "well": ("dusk", shot_well),
    "bed": ("dusk", shot_bed), "bed_wide": ("dusk", shot_bed_wide), "stairwell": ("dusk", shot_stairwell),
    "down": ("under", shot_down), "down_start": ("under", shot_down_start), "cell": ("under", shot_cell), "cell_open": ("under", shot_cell_open), "cell_shut": ("under", shot_cell_shut),
    "lever": ("under", shot_lever), "aisle": ("under", shot_aisle), "endwall": ("under", shot_endwall), "endwall_alt": ("under", shot_endwall_alt),
    "slot": ("under", shot_slot), "slot_hands": ("under", shot_slot_hands),
    "slot_boots": ("under", shot_slot_boots), "box": ("under", shot_box),
    "box_open": ("under", shot_box_open),
    "foot": ("under", shot_foot), "falloff": ("under", shot_falloff), "portrait": ("under", shot_portrait),
    "counter": ("under", shot_counter), "apple": ("under", shot_apple), "drift": ("under", shot_drift),
    "ots": ("under", shot_ots), "follow": ("under", shot_follow), "kill": ("under", shot_kill),
    "hit": ("under", shot_hit),
}
ORDER = list(BUILDERS)
SHEETS = {"push_sheet": "push", "bed_sheet": "bed", "lever_sheet": "lever", "box_sheet": "box_open",
          "hit_sheet": "hit"}
MEASURE = ("aisle", "falloff")
WANTED = None                                           # names this process builds (None: every shot)


def build(scene, sky=None):
    """The proof film: one 1-second shot per still (only the WANTED ones), under SKIES."""
    v, ug = U.build_village(scene, seed=1)
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, skies=SKIES, sky=sky)
    st.ug = ug
    ug.register(st)
    # a lead-in frame: Stage.see_through / remove key the cutaway visible again on the film's FIRST frame each time
    # they are called, which undoes the see-through of a shot that starts on that frame (films/lookdev.py)
    st.shot("_lead", 1.0 / 24.0, sky=next(iter(SKIES)))
    for n in (WANTED or ORDER):
        tag, fn = BUILDERS[n]
        secs = {"push": 6.0, "bed": 6.0, "down": 3.0, "down_start": 3.0, "mouth": 4.0, "lever": 2.5,
                "box_open": 3.0, "hit": 2.0, "stairwell": 2.5, "mouth": 3.5, "slot_boots": 2.5, "slot_hands": 2.5,
                "endwall": 2.0}.get(n, 1.0)
        s = st.shot(n, secs, sky=tag)
        SHOT["name"] = n
        fn(st, s, ug)
    st.finish()
    return {"film": film, "captions": [], "stage": st, "underground": ug}


def still_frame(film, name):
    shot = next(s for s in film.shots if s.name == name)
    if name == "push":
        r = getattr(shot, "ug", None)                       # dad at the lip, 10 frames before he drops
        return (r["drops"][0] - 10) if r and r["drops"] else shot.frame_start + 50
    if name == "bed":
        return shot.ug["takeoffs"][0] + 6                    # the top of his first jump
    if name == "down":
        return shot.frame_end
    if name == "down_start":
        return shot.frame_start
    r = getattr(shot, "ug", None) or {}
    if name == "mouth":
        return _mouth_frame(shot)
    if name == "lever":
        return r["open_end"] + 6                             # the wall open, the pan and the focus pull done
    if name == "box_open":
        return r["open_end"] + 3                             # the doorway lit, before he runs
    if name == "stairwell":                                  # the child passing the west wall's torch
        kid = r["kid"]
        return min(range(shot.frame_start, shot.frame_end + 1), key=lambda f: abs(kid.pos_at(f).y + 5.6))
    if name == "aisle":
        return r["takeoffs"][1] + 7                          # the top of a jump (12 ticks: the peak at tick 5-6)
    if name == "slot_boots":                                 # his boots cross the line to the slot: the frame
        c = _crossing(shot, r["steve"])                      # nearest it with the legs together (least smear)
        legs = r["steve"]
        return min(range(c - 3, c + 4), key=lambda f: (abs(_leg_angle(legs, f)), abs(f - c)))
    if name == "slot_hands":
        return _crossing(shot, r["steve"]) + 16              # he has passed: the hands alone
    if name == "slot":
        return shot.frame_start                              # before he walks into the view
    if name == "hit":
        return r["blows"][0] - 2                             # just before the first blow (the sheet has the flash)
    if name == "endwall":
        return shot.frame_start
    return shot.frame_start + int(round(STILL_AT * film.fps))


def _leg_angle(c, f):
    import bpy

    bpy.context.scene.frame_set(f)
    return c.leg_r.matrix_basis.to_euler().x


def _crossing(shot, steve):
    """The frame on which Steve's feet are nearest the b08 camera's line to the slot."""
    from mathutils import Vector

    c = U.CAMERAS["b08_slot"]
    a, b = Vector(c["pos"][:2]), Vector(U.SLOT_FACE[:2])
    d = (b - a).normalized()

    def off(f):
        p = steve.pos_at(f)
        q = Vector((p.x, p.y)) - a
        return abs(q.x * d.y - q.y * d.x)
    return min(range(shot.frame_start, shot.frame_end + 1), key=off)


def _mouth_frame(shot):
    """Beat 1's still: Steve at the lip of the stair (the first step under his feet)."""
    steve = shot.ug["steve"]
    return min(range(shot.frame_start, shot.frame_end + 1), key=lambda f: abs(steve.pos_at(f).y - 0.3))


def palette(ses, name, path, heroes=()):
    """tools/palette_check on a still, twice: as it is, and with the set's baked materials counted as their
    textures (the plain check does not know a stone texture baked darker is stone). Returns the failed checks."""
    import numpy as np

    from tools import palette_check as pc

    rec = pc.probe(ses.scene)
    rep = pc.evaluate(rec, path, heroes=heroes)
    pc.print_report(name, rep)
    rec2 = dict(rec)
    mats = rec["material"].copy()
    alb = rec["albedo"].copy()
    gy, gx = mats.shape
    n = 0
    for j in range(gy):
        for i in range(gx):
            m = mats[j, i]
            if "#" in m and ("|ug" in m or m.split("#")[0] in pc.STONE):
                head, tail = m.split("#", 1)
                hexs = tail[:6]
                try:
                    tint = [int(hexs[k:k + 2], 16) / 255.0 for k in (0, 2, 4)]
                except ValueError:
                    continue
                if head in pc.STONE or head in pc.PLANKS:
                    mats[j, i] = head
                    if min(tint) > 0.02 and not np.isnan(alb[j, i, 0]):
                        alb[j, i] = np.clip(alb[j, i] / np.array(tint), 0.0, 1.0)
                    n += 1
    rec2["material"], rec2["albedo"] = mats, alb
    rep2 = pc.evaluate(rec2, path, heroes=())
    for cname, ok, text in rep2["checks"]:
        if cname in ("stone not magenta", "planks saturation"):
            print("[check] %-10s %-4s %-28s %s (baked faces counted: %d cells)"
                  % (name + "+", "ok" if ok else "FAIL", cname, text, n), flush=True)
    return rep["failed"] + [c for c in rep2["failed"] if c[0] in ("stone not magenta", "planks saturation")]


def main(names, res=None, samples=16, threads=2):
    """Render the named proof stills (and sheets) to out/test/underground_<name>.png."""
    import render as R
    from PIL import Image

    global WANTED
    if res is None:
        res = tuple(int(a) for a in os.environ.get("UG_RES", "540x960").split("x"))
        if res[0] < 540:
            samples = min(samples, 8)
    names = list(names)
    if not names or names == ["all"]:
        names = ORDER + list(SHEETS)
    sys.modules["films._underground_proof"] = sys.modules[__name__]
    out_dir = os.path.join(ROOT, "out", "test")
    failed = []
    stills = [n for n in names if n in BUILDERS]
    sheets = [n for n in names if n in SHEETS]
    WANTED = sorted(set(stills) | {SHEETS[n] for n in sheets}, key=ORDER.index)
    for sky in SKIES:
        mine = [n for n in stills if BUILDERS[n][0] == sky]
        mine_sheets = [n for n in sheets if BUILDERS[SHEETS[n]][0] == sky]
        if not mine and not mine_sheets:
            continue
        ses = R.Session("_underground_proof", sky=sky)
        ses.configure(res, samples, threads, None)
        stage = ses.result["stage"]
        for n in mine + [SHEETS[x] for x in mine_sheets]:
            if n in WINDOWS:
                window(ses, n, WINDOWS[n])
        for n in mine:
            t = time.time()
            path = os.path.join(out_dir, "underground_%s%s.png" % (n, os.environ.get("UG_TAG", "")))
            frame = still_frame(ses.film, n)
            ses.render_frame(frame, path)
            print("[ug proof] %-11s frame %4d -> %s  %.1f s" % (n, frame, path, time.time() - t), flush=True)
            failed += [(n, c) for c in palette(ses, n, path, stage.heroes.get(n, ()))]
            if n in MEASURE:
                measure(ses, path, n)
        for sh in mine_sheets:
            shot = next(s for s in ses.film.shots if s.name == SHEETS[sh])
            frames = _sheet_frames(sh, shot, ses)
            tiles = []
            small = (res[0] // 2, res[1] // 2)
            ses.configure(small, max(8, samples // 2), threads, None)
            for f in frames:
                t = time.time()
                p = os.path.join(out_dir, "underground_%s_f%04d.png" % (sh, f))
                ses.render_frame(f, p)
                tiles.append(p)
                print("[ug proof] %-11s frame %4d  %.1f s" % (sh, f, time.time() - t), flush=True)
            ses.configure(res, samples, threads, None)
            _contact(tiles, frames, os.path.join(out_dir, "underground_%s.png" % sh))
    if "cell_open" in names and "cell_shut" in names:
        doorway(out_dir)
    print("[ug proof] checks:", "all passed" if not failed else "FAILED: %s" % failed)
    return 1 if failed else 0


WINDOWS = {"mouth": "steve", "slot_boots": "steve"}       # shots whose hero's frames in the picture are printed


def window(ses, name, who):
    """Print the frames of a shot on which a character's head is in the picture, and in the Reels safe area
    (x 8-82 %, y 14-60 %: tools/palette_check), through the shot's own (moving) camera."""
    import bpy
    from bpy_extras.object_utils import world_to_camera_view

    shot = next(s for s in ses.film.shots if s.name == name)
    c = shot.ug[who]
    scene = ses.scene
    seen, safe = [], []
    for f in range(shot.frame_start, shot.frame_end + 1):
        scene.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        p = c.head.evaluated_get(dg).matrix_world.translation
        q = world_to_camera_view(scene, shot.camera.evaluated_get(dg), p)
        x, y = q.x * 100.0, (1.0 - q.y) * 100.0
        if q.z > 0 and 0 <= x <= 100 and 0 <= y <= 100:
            seen.append(f - shot.frame_start)
            if 8 <= x <= 82 and 14 <= y <= 60:
                safe.append(f - shot.frame_start)
    span = lambda fs: "%d frames (%s)" % (len(fs), "%d..%d" % (fs[0], fs[-1]) if fs else "-")
    print("[ug window] %-10s %s's head in the picture %s, in the safe area %s (frames from the shot's start)"
          % (name, who, span(seen), span(safe)), flush=True)
    return seen, safe


def _sheet_frames(sheet, shot, ses):
    r = getattr(shot, "ug", None) or {}
    if sheet == "push_sheet":
        land = (r["drops"][0] if r and r["drops"] else shot.frame_start + 60)
        return [land - 10, land - 7, land - 5, land - 3, land - 1, land + 2]
    if sheet == "lever_sheet":                              # hand in, click, pan, the wall moving, open, held
        return [r["hand"] - 2, r["hand"], r["flip"] + 7, r["open"], r["open_end"] + 1, r["open_end"] + 12]
    if sheet == "box_sheet":                                # shut, opening, lit, his step, the pan, dad's back
        run = r["run"]
        return [r["open"] - 6, r["open"] + 1, r["open_end"] + 3, run + 5, run + 11, run + 18]
    if sheet == "hit_sheet":                                # before, blow 1 (top of the jolt), blow 2, the swap
        b1, b2, inf = r["blows"][0], r["blows"][1], r["infect"]
        return [b1 - 2, b1 + 1, b1 + 6, b2 + 1, inf + 1, inf + 8]
    land = r["landings"][0]                                 # bed: the jump, its landing and the bounces
    return [r["takeoffs"][0] + 3, r["takeoffs"][0] + 7, land, land + 5, land + 10, r["takeoffs"][1] + 5
            if len(r["takeoffs"]) > 1 else land + 16]


def _contact(paths, frames, out):
    from PIL import Image, ImageDraw

    ims = [Image.open(p).convert("RGB") for p in paths]
    w, h = ims[0].size
    sheet = Image.new("RGB", (w * 3, h * 2), (0, 0, 0))
    d = ImageDraw.Draw(sheet)
    for i, (im, f) in enumerate(zip(ims, frames)):
        x, y = (i % 3) * w, (i // 3) * h
        sheet.paste(im, (x, y))
        d.text((x + 6, y + 6), "f%d" % f, fill=(255, 255, 0))
    sheet.save(out)
    for p in paths:
        os.remove(p)
    print("[ug proof] sheet ->", out)



def measure(ses, path, label, grid=(54, 96)):
    """The light on the set's floor and walls in a rendered still against the game: for every probed pixel that
    shows a baked face (ray cast through the shot camera), displayed / texel (both sRGB) next to the game's lightmap
    brightness for that face (its cell's levels, x the face's cardinal shade). Prints a table by block level and
    returns {level: (rendered ratio median, game value, samples)}."""
    import bpy
    import numpy as np
    from mathutils import Vector
    from PIL import Image

    from tools import palette_check as pc

    scene = ses.scene
    ug = ses.result["underground"]
    e = ug.env
    img = np.asarray(Image.open(path).convert("RGB")).astype(np.float32) / 255.0
    h, w = img.shape[:2]
    cam = scene.camera
    dg = bpy.context.evaluated_depsgraph_get()
    ce = cam.evaluated_get(dg)
    mw = ce.matrix_world
    tr, br, bl, tl = [mw @ v for v in ce.data.view_frame(scene=scene)]
    origin = mw.translation.copy()
    gx, gy = grid
    rows = {}
    for j in range(gy):
        fy = (j + 0.5) / gy
        left, right = tl.lerp(bl, fy), tr.lerp(br, fy)
        for i in range(gx):
            fx = (i + 0.5) / gx
            d = (left.lerp(right, fx) - origin).normalized()
            o = origin.copy()
            for _ in range(8):
                hit, loc, nrm, index, ob, matrix = scene.ray_cast(dg, o, d)
                if not hit:
                    break
                orig = ob.original
                if orig.hide_render or not orig.visible_camera:
                    o = loc + d * 2e-4
                    continue
                break
            if not hit or orig.type != "MESH":
                continue
            mname, texel = pc._texel(orig, index, loc, matrix)
            if texel is None or "|ug" not in (mname or "") or texel[3] < 0.5:
                continue
            n = Vector(nrm).normalized()
            cell = tuple(int(math.floor(c)) for c in (loc + n * 0.02))
            b, s_ = e.levels(cell)
            dname = U._dir_of(n)
            tint = [int(mname.split("#", 1)[1][k:k + 2], 16) / 255.0 for k in (0, 2, 4)]
            base = np.array(texel[:3]) / np.maximum(np.array(tint), 1e-3)          # the untinted texel (sRGB)
            px = img[min(h - 1, int(fy * h)), min(w - 1, int(fx * w))]
            lum_t = float(base.max())
            if lum_t < 0.15:
                continue
            ratio = float(px.max()) / lum_t
            game = max(U.lightmap_rgb(b, s_)) * U.CARDINAL[dname]
            rows.setdefault((b, dname in ("up", "down")), []).append((ratio, game))
    print("[ug measure] %s: displayed / texel against the game's lightmap x cardinal shade, by block level" % label)
    out = {}
    for (b, horiz), vals in sorted(rows.items()):
        if len(vals) < 4:
            continue
        r = np.median([v[0] for v in vals])
        g = np.median([v[1] for v in vals])
        out[(b, horiz)] = (float(r), float(g), len(vals))
        print("[ug measure]   level %2d %-6s rendered %.2f  game %.2f  (%d samples)"
              % (b, "floor" if horiz else "walls", r, g, len(vals)))
    return out


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
