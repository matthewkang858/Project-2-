"""Proof stills for engine/towers.py: the iron farm tower of "Twenty Minutes" in the REAL village (the edit hook,
films.lookdev.Stage, engine.look's golden hour or dusk), 540x960, 16 samples, 2 threads, motion blur on.

    $BPY -m engine.towers stills b01 b04 pod_out           # -> out/test/towers_<name>.png (one build per call:
    $BPY -m tools.towers_proof b01 b04                     #    at most 4-5 names per call stay under 300 s)
    $BPY -m tools.towers_proof --where b01 b04 ...         # no render: where every hero's head lands (x %, y %)
    $BPY -m engine.towers stills square_dusk pod_out_dusk  # the same shots under the dusk sky (another build)
    TOWERS_RES=270x480 TOWERS_SAMPLES=8 $BPY -m tools.towers_proof b01     # quick framing tests
The bNN shots stage each beat of stories/ironfarm.json exactly as the BEATS section of engine/towers.py says
(anchors, cameras, calls); each is followed by tools.palette_check's report and a copy with the Reels zones drawn
(out/test/towers_<name>_zones.png). Every shot exists in every build (keying is cheap); a call renders only the
frames of the names it is given. Strips (several frames side by side, 270x480 each, motion blur on): slide, hopper,
stairs, bounce, push, b24.
"""
import math
import os
import sys
import time
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "test")
GOLD = dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm")
DUSK = dict(preset="dusk", az=187.0, el=5.0, bloom=1.3, grade="warm")
STRIP_RES = (270, 480)

# shot name -> (seconds, frames to render as offsets into the shot (one = a still, several = a strip; None: chosen
# by _strip_offsets))
SHOTS = [
    ("b01", 3.0, [40]), ("b02", 2.0, [30]), ("b03", 6.0, [60]), ("b04", 3.0, [70]), ("b04_long", 1.5, [12]),
    ("b05", 2.0, [30]), ("b06", 3.0, [2, 36]),
    ("square_wide", 1.0, [12]), ("push", 6.0, None), ("pod_out", 1.0, [12]),
    ("pod_in", 1.0, [12]), ("b08", 2.0, [30]), ("b09", 2.0, [30]), ("two_shot", 1.0, [12]),
    ("back", 1.0, [12]), ("gap", 1.0, [12]),
    ("bounce", 4.0, None), ("lineup", 1.0, [12]), ("slide", 6.0, None), ("hopper", 5.0, None),
    ("b12", 3.0, [20]), ("b14", 2.0, [36]), ("b16", 1.5, [20]), ("grow", 2.0, None), ("b20", 2.0, [40]),
    ("high", 2.0, [30]), ("b22", 4.0, [14]), ("stairs", 3.0, None), ("b24", 4.0, None),
]
DUSK_SHOTS = {"square_dusk": "square_wide", "pod_out_dusk": "pod_out", "pod_in_dusk": "pod_in",
              "cell_side_dusk": "b08"}
ALIASES = {"square": "b04", "foot": "b05", "cell_side": "b08", "platform": "b09"}


def seed_of(name):
    """A fixed per-name seed (Python's str hash differs from process to process: the frames must not)."""
    return zlib.crc32(name.encode("utf-8")) % 97


# ----------------------------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------------------------
def _cam(s, cam, focus=None, moved=False):
    s.lens(cam["lens"], cam.get("fstop", 4.0))
    if moved and "target1" in cam:
        s.move(cam["pos"], cam["target"], cam.get("pos1", cam["pos"]), cam["target1"])
    else:
        s.move(cam["pos"], cam["target"])
    s.focus(focus if focus is not None else cam.get("focus", cam["target"]))


def _lights(st, s, fm, pod=True):
    if pod:
        st.lights(s, scale=1.0, groups={fm.set["lights"][0]: 1.0, fm.set["lights"][1]: 1.0})
    else:
        st.lights(s, scale=1.0)


def _golem(st):
    from engine import mobs

    g = st.cast.get("golem")
    if g is None:
        g = st.cast["golem"] = mobs.make_iron_golem("golem")
    return g


def _zombie(st, fm, f0, aggro=False, look=None):
    from engine import undead

    z = st.cast.get("zombie") or undead.add_zombie(st, "zombie")
    fm.zombie_in_cell(z, f0, aggro=aggro, look=look)
    return z


def _heads(h, name, frame, **chars):
    h.setdefault("where", {}).setdefault(name, []).append((frame, {k: getattr(c, "head", c) for k, c in chars.items()}))


# ----------------------------------------------------------------------------------------------------
# the beats (as BEATS in engine/towers.py stages them)
# ----------------------------------------------------------------------------------------------------
def shot_b01(st, s, fm, h):
    """Beat 1: C['square'], the baby on square_baby, Steve along tower_steve_square at the lens."""
    from engine import players

    f0 = s.frame_start
    baby = st.actor("baby", "none", child=True)
    baby.place(f0, fm.A["square_baby"], fm.yaw["square_baby"])
    steve = players.add_player(st, "steve", "steve")
    path = fm.v.paths[fm.name + "_steve_square"]
    steve.place(f0, path[0], fm.yaw["square_baby"] + math.pi)
    steve.walk(f0, path)
    p, yw = baby.pos_at(f0), fm.yaw["square_baby"]
    ahead = (p.x + 2.0 * math.sin(yw), p.y - 2.0 * math.cos(yw))
    baby.look_at(f0, (ahead[0], ahead[1], p.z + 1.2), ease=0)            # in profile from behind, the nose out
    baby.look_at(f0 + 30, (ahead[0], ahead[1], p.z + 3.4), ease=24)      # the big head tilts up as he comes
    st.use(s, baby, steve)
    _cam(s, fm.cameras["square"], focus=baby.head)
    _lights(st, s, fm)
    _heads(h, s.name, f0 + 40, baby=baby, steve=steve)


def shot_b02(st, s, fm, h):
    """Beat 2: C['baby_face'], Steve along tower_steve_past strides between the lens and the baby."""
    from engine import players

    f0 = s.frame_start
    baby = st.actor("baby", "none", child=True)
    baby.place(f0, fm.A["square_baby"], fm.yaw["square_baby"])
    steve = players.add_player(st, "steve", "steve")
    path = fm.v.paths[fm.name + "_steve_past"]
    steve.place(f0, path[0], math.atan2(path[1][0] - path[0][0], -(path[1][1] - path[0][1])))
    steve.walk(f0 + 6, path)
    for f in range(f0, s.frame_end + 1, 4):
        baby.look_at(f, steve, ease=3)
    st.use(s, baby, steve)
    st.hero(s, "baby", baby)
    _cam(s, fm.cameras["baby_face"], focus=baby.head)
    _lights(st, s, fm)
    _heads(h, s.name, f0 + 30, baby=baby)


def shot_b03(st, s, fm, h):
    """Beat 3: C['push_square'] (panning with them): towers.push along tower_push_square, the baby runs after."""
    from engine import players, towers

    f0 = s.frame_start
    steve = players.add_player(st, "steve", "steve")
    mom = st.actor("mom", "farmer")
    route = fm.v.paths[fm.name + "_push_square"]
    r = towers.push(steve, mom, f0 + 2, route)
    for f in range(f0 + 2, s.frame_end + 1, 12):
        p = mom.pos_at(f)
        mom.look_at(f, (p.x - 2.0, p.y + 2.2, p.z + 1.6), ease=4)          # hat brim and nose to the lens
    baby = st.actor("baby", "none", child=True)
    baby.place(f0, fm.A["push_baby"], fm.yaw["push_baby"])
    fb = f0 + 24                                    # three running steps, stopping 1.2 behind Steve (0.7 clear)
    here, his = baby.pos_at(fb), steve.pos_at(fb + 10)
    baby.walk(fb, [tuple(here), (max(his.x + 1.2, here.x - 1.6), here.y, here.z)], run=True)
    baby.look_at(fb, mom, ease=4)
    st.use(s, steve, mom, baby)
    _cam(s, fm.cameras["push_square"], focus=mom.head, moved=True)
    _lights(st, s, fm)
    h["push_square"] = r
    _heads(h, s.name, f0 + 36, mom=mom, steve=steve, baby=baby)
    _heads(h, s.name, s.frame_end - 2, mom=mom, steve=steve)


def shot_b04(st, s, fm, h):
    """Beat 4: the tilt from C['square_start'] to C['square'], the baby on square_baby looking up at the pod,
    Mom on mom_glass; rack focus baby -> Mom."""
    f0 = s.frame_start
    baby = st.actor("baby", "none", child=True)
    baby.place(f0, fm.A["square_baby"], fm.yaw["square_baby"])
    baby.look_at(f0, fm.A["pod_target"], ease=0)
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["mom_glass"], fm.yaw["mom_glass"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    z = _zombie(st, fm, f0, look=mom)
    st.use(s, baby, mom, z)
    a, b = fm.cameras["square_start"], fm.cameras["square"]
    s.lens(b["lens"], b["fstop"])
    s.move(a["pos"], a["target"], b["pos"], b["target"])
    s.focus(baby.head)
    s.focus(mom.head, at_s=2.0, rack_s=0.6)
    _lights(st, s, fm)
    _heads(h, s.name, f0 + 70, baby=baby, mom=mom)


def shot_b04_long(st, s, fm, h):
    """Beat 4, the cut inside the line: C['square_long'] on Mom at the front glass, the panes on the line hidden."""
    f0 = s.frame_start
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["mom_glass"], fm.yaw["mom_glass"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    z = _zombie(st, fm, f0, look=mom)
    st.use(s, mom, z)
    cam = fm.cameras["square_long"]
    _cam(s, cam, focus=mom.head)
    fm.see_through(st, s, cam, points=[mom])
    _lights(st, s, fm)
    _heads(h, s.name, f0 + 12, mom=mom)


def shot_b05(st, s, fm, h):
    """Beat 5: the baby on foot_front, C['foot'], head far up, one small hop in place."""
    from engine import towers

    f0 = s.frame_start
    baby = st.actor("baby", "none", child=True)
    baby.place(f0, fm.A["foot_front"], fm.yaw["foot_front"])
    up = baby.pos_at(f0)
    baby.look_at(f0, (up.x + 0.8, up.y - 2.0, up.z + 4.0), ease=0)
    towers.hop(baby, f0 + 34, fm.A["foot_front"])
    st.use(s, baby)
    st.hero(s, "baby", baby)
    _cam(s, fm.cameras["foot"], focus=baby.head)
    _lights(st, s, fm)
    _heads(h, s.name, f0 + 30, baby=baby)


def shot_b06(st, s, fm, h):
    """Beat 6: the pan from the red bed's foot (C['pan_bed']) to the cell; Mom on bed_beside, the zombie in its
    cell."""
    f0 = s.frame_start
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["bed_beside"], fm.yaw["bed_beside"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    z = _zombie(st, fm, f0, look=mom)
    st.use(s, mom, z)
    _cam(s, fm.cameras["pan_bed"], focus=fm.beds["mom"]["pos"], moved=True)
    s.focus(z.head, at_s=1.8, rack_s=0.8)
    _lights(st, s, fm)
    _heads(h, s.name, f0 + 2, mom=mom)
    _heads(h, s.name, f0 + 36, mom=mom)
    _heads(h, s.name, s.frame_end, zombie=z)


def _backed(st, fm, s, f0, who, seeds=None, panic=True):
    """Villagers on anchors, trembling (towers.panic) with their heads on the zombie."""
    from engine import towers

    cast = []
    for name, prof, spot in who:
        c = st.actor(name, prof)
        c.place(f0, fm.A[spot], fm.yaw[spot])
        cast.append(c)
    for c in cast:
        if panic:
            towers.panic(c, f0, s.frame_end, fm.zombie_eye, seed=(seeds or {}).get(c.name, seed_of(c.name)))
        else:
            c.look_at(f0, fm.zombie_eye, ease=0)
    return cast


def shot_b08(st, s, fm, h):
    """Beat 8: C['cell_side']; Mom, the cleric and the librarian backed against the far glass (back_3, back_1,
    back_2), trembling; the empty platform behind the glass."""
    f0 = s.frame_start
    cast = _backed(st, fm, s, f0, (("cleric", "cleric", "back_1"), ("librarian", "librarian", "back_2"),
                                   ("mom", "farmer", "back_3")))
    z = _zombie(st, fm, f0, aggro=True, look=cast[2])
    st.use(s, z, *cast)
    st.hero(s, "mom", cast[2])
    _cam(s, fm.cameras["cell_side"], focus=cast[0].head)
    _lights(st, s, fm)
    _heads(h, s.name, f0 + 30, cleric=cast[0], librarian=cast[1], mom=cast[2])


def shot_b09(st, s, fm, h):
    """Beat 9: C['platform']; a golem appears on golem_spawn (yaw 0: facing south, its face to the lens side) and
    turns its head to the pod, where the three stand on back_1..3."""
    f0 = s.frame_start
    g = _golem(st)
    fm.golem_spawn(g, f0 + 6, yaw=0.0, look=fm.A["pod_target"], look_after=10, empty_from=s)
    cast = _backed(st, fm, s, f0, (("cleric", "cleric", "back_1"), ("librarian", "librarian", "back_2"),
                                   ("mom", "farmer", "back_3")), panic=False)
    st.use(s, g, *cast)
    st.hero(s, "golem", g)
    _cam(s, fm.cameras["platform"], focus=g.head)
    _lights(st, s, fm)
    _heads(h, s.name, f0 + 30, golem=g, cleric=cast[0], librarian=cast[1], mom=cast[2])


def shot_b12(st, s, fm, h):
    """Beat 12, wide: C['hopper_wide']; the baby on 'poppies' among the strewn poppies, Steve on chest_steve with
    an ingot turns from the chest and walks out of frame, a stack of ingots and a poppy fall into the hopper."""
    from engine import mobs, players

    f0 = s.frame_start
    items = [mobs.make_dropped_item("iron_ingot", name="w_iron", seed=1, count=3),
             mobs.make_dropped_item("poppy", name="w_poppy", seed=2)]
    for it in items:
        st.cast[it.name] = it
    fm.deliver(items, f0 + 4, every=6, seed=2)
    lying = []
    for i in range(4):
        it = mobs.make_dropped_item("poppy", name="w_lying_%d" % i, seed=10 + i)
        st.cast[it.name] = it
        lying.append(it)
    cam = fm.cameras["hopper_wide"]
    fm.strew(lying, f0, s.frame_end + 1, seed=3, face=cam["pos"])
    steve = players.add_player(st, "steve", "steve")
    steve.hold("iron_ingot")
    steve.place(f0, fm.A["chest_steve"], fm.yaw["chest_steve"])
    p = steve.pos_at(f0)
    steve.walk(f0 + 30, [tuple(p), (p.x + 3.0, p.y + 2.0, p.z)])
    baby = st.actor("baby", "none", child=True)
    baby.place(f0, fm.A["poppies"], fm.yaw["poppies"])
    baby.look_at(f0, steve, ease=0)
    st.use(s, steve, baby, *(items + lying))
    _cam(s, cam, focus=baby.head)
    _lights(st, s, fm)
    _heads(h, s.name, f0 + 20, baby=baby, steve=steve)


def shot_b14(st, s, fm, h):
    """Beat 14: C['top_step_side']; the baby on step 8 hops up the last step onto top_step_baby beside the
    opening; Mom on bed_side through the glass."""
    from engine import towers

    f0 = s.frame_start
    baby = st.actor("baby", "none", child=True)
    s8 = fm.set["stairs"][8]
    baby.place(f0, s8, fm.yaw["top_step"])
    e = towers.hop(baby, f0 + 8, fm.A["top_step_baby"])
    baby.turn(e + 2, fm.yaw["top_step_baby"], ease=6)
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["bed_side"], fm.yaw["bed_side"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    z = _zombie(st, fm, f0, look=mom)
    st.use(s, baby, mom, z)
    cam = fm.cameras["top_step_side"]
    _cam(s, cam, focus=baby.head)
    fm.see_through(st, s, cam, points=[mom])                             # the straw hat through the back glass
    _lights(st, s, fm)
    _heads(h, s.name, f0 + 36, baby=baby, mom=mom)


def shot_b16(st, s, fm, h):
    """Beat 16: C['red_bed']; Mom on bed_side on the zombie, the baby pressed against her on the lens side,
    looking up at her, its body turned to the lens."""
    from engine.village import yaw_to

    f0 = s.frame_start
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["bed_side"], fm.yaw["bed_side"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    z = _zombie(st, fm, f0, aggro=True, look=mom)
    baby = st.actor("baby", "none", child=True)
    bs = fm.A["bed_side"]
    bp = (bs[0] - 0.62, bs[1] - 0.05, bs[2])
    cam = fm.cameras["red_bed"]
    baby.place(f0, bp, yaw_to(bp, (0.5 * cam["pos"][0] + 0.5 * bs[0], 0.5 * cam["pos"][1] + 0.5 * bs[1])))
    baby.look_at(f0, mom, ease=0)
    st.use(s, mom, baby, z)
    _cam(s, cam, focus=baby.head)
    fm.see_through(st, s, cam, points=[mom, baby])
    _lights(st, s, fm)
    _heads(h, s.name, f0 + 20, baby=baby, mom=mom, zombie=z)


def shot_b20(st, s, fm, h):
    """Beat 20: C['gap_side'] (outside the east glass, the panes on the line hidden): the narrator walks into the
    plug, stops on gap_adult, his head tilts down to the gap (look at gap_down)."""
    f0 = s.frame_start
    nar = st.actor("narrator", "none")
    ga = fm.A["gap_adult"]
    nar.place(f0, (ga[0], ga[1] - 1.6, ga[2]), fm.yaw["gap_adult"])
    e = nar.walk(f0 + 4, [(ga[0], ga[1] - 1.6, ga[2]), ga])
    nar.look_at(e + 4, fm.A["gap_down"], ease=8)
    st.use(s, nar)
    cam = fm.cameras["gap_side"]
    _cam(s, cam, focus=nar.head)
    gt = fm.A["gap_target"]
    fm.see_through(st, s, cam, points=[(ga[0], ga[1], ga[2] + 1.6), (ga[0], ga[1], ga[2] + 0.6), gt,
                                       (gt[0], gt[1] - 0.4, gt[2]), (gt[0], gt[1], gt[2] + 1.0)])
    _lights(st, s, fm)
    _heads(h, s.name, f0 + 40, narrator=nar)


def shot_b22(st, s, fm, h):
    """Beat 22: C['back_glass']; the narrator on watch_22 still, eyes level; Steve on one_down breaks the top step
    by hand, then walks down the steps (towers.walk_down)."""
    from engine import players, towers

    f0 = s.frame_start
    fm.top_step.restore(f0)
    nar = st.actor("narrator", "none")
    nar.place(f0, fm.A["watch_22"], fm.yaw["watch_22"])
    steve = players.add_player(st, "steve", "steve")
    steve.place(f0, fm.A["one_down"], fm.yaw["one_down"])
    steve.look_at(f0, fm.top_step.center, ease=0)
    nar.look_at(f0, (fm.A["one_down"][0], fm.A["one_down"][1], fm.L["F"] + 1.62), ease=0)    # eyes level
    m = fm.break_top_step(steve, f0 + 6, camera=s, until=s.frame_end + 1)
    st_ = fm.set["stairs"]
    towers.walk_down(steve, m["frame"] + 8, [st_[7], st_[6], st_[5]])
    st.cast[fm.top_step.name] = fm.top_step
    st.use(s, nar, steve, fm.top_step)
    _cam(s, fm.cameras["back_glass"], focus=steve.head)
    _lights(st, s, fm)
    h["b22"] = m
    _heads(h, s.name, f0 + 14, narrator=nar, steve=steve)


def shot_b24(st, s, fm, h):
    """Beats 23 / 24: C['cell_side']; cleric and librarian on back_1 / back_2, Mom on mom, the narrator on
    mom_glass, Mom's and the narrator's tremble matched (same seed); the golem appears on golem_24 behind them,
    looks at the pod, steps, begins to slide; rack focus to it."""
    f0 = s.frame_start
    k = 7
    cast = _backed(st, fm, s, f0, (("cleric", "cleric", "back_1"), ("librarian", "librarian", "back_2"),
                                   ("mom", "farmer", "mom"), ("narrator", "none", "mom_glass")),
                   seeds={"mom": k, "narrator": k})
    z = _zombie(st, fm, f0, aggro=True, look=cast[2])
    g = _golem(st)
    fs = f0 + 18
    fm.golem_spawn(g, fs, pos=fm.A["golem_24"], yaw=math.radians(60.0), look=fm.A["pod_target"], look_after=6,
                   empty_from=s)
    e = fm.golem_step(g, fs + 26)
    fm.golem_slide(g, e + 4)
    st.use(s, z, g, *cast)
    st.hero(s, "narrator", cast[3])
    _cam(s, fm.cameras["cell_side"], focus=cast[2].head)
    s.focus(g.head, at_s=(fs + 30 - f0) / 24.0, rack_s=0.6)
    _lights(st, s, fm)
    h["b24"] = dict(spawn=fs, step=e)
    _heads(h, s.name, fs + 40, golem=g, cleric=cast[0], librarian=cast[1], mom=cast[2], narrator=cast[3])


# ----------------------------------------------------------------------------------------------------
# the other proofs (the set, the mechanics)
# ----------------------------------------------------------------------------------------------------
def shot_square_wide(st, s, fm, h):
    """The establishing wide from the plaza: the well and the bell in front, the tower above the roofs."""
    f0 = s.frame_start
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["mom_glass"], fm.yaw["mom_glass"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    st.use(s, mom)
    _cam(s, fm.cameras["square_wide"])
    st.lights(s, scale=1.0)


def shot_pod_out(st, s, fm, h):
    """The pod from outside: villagers in their beds, Mom up, the zombie in its cell, panes on the line hidden."""
    f0 = s.frame_start
    cast = []
    for key, prof in (("white_1", "cleric"), ("white_2", "librarian")):
        c = st.actor(prof, prof)
        bed = fm.beds[key]
        c.lie_down(f0, bed["pos"], bed["yaw"])
        cast.append(c)
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["mom"], fm.yaw["mom"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    z = _zombie(st, fm, f0, look=mom)
    st.use(s, mom, z, *cast)
    cam = fm.cameras["pod_out"]
    _cam(s, cam, focus=mom.head)
    mp = fm.A["mom"]
    pts = [mom, (mp[0], mp[1], mp[2] + 0.5), fm.zombie_eye]
    for key in ("white_1", "white_2", "mom"):
        bd = fm.beds[key]
        pts += [(bd["head"][0], bd["head"][1], bd["head"][2] + 0.3),
                (bd["foot"][0], bd["foot"][1], bd["foot"][2] + 0.3)]
    fm.see_through(st, s, cam, points=pts)
    st.hero(s, "mom", mom)
    _lights(st, s, fm)


def shot_pod_in(st, s, fm, h):
    """Inside at villager eye height from the south-west corner: Mom on 'mom' trembling, the zombie's arms out of
    the window beyond her (the lens stands where back_1 / back_3 are: nobody else in this shot)."""
    f0 = s.frame_start
    cast = _backed(st, fm, s, f0, (("mom", "farmer", "mom"),))
    z = _zombie(st, fm, f0, look=cast[0])
    st.use(s, z, *cast)
    _cam(s, fm.cameras["pod_in"], focus=cast[0].head)
    st.hero(s, "mom", cast[0])
    _lights(st, s, fm)


def shot_two_shot(st, s, fm, h):
    """Beat 7: the zombie's arms out of the window, one empty block, Mom's face (long lens, profile)."""
    f0 = s.frame_start
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["mom"], fm.yaw["mom"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    z = _zombie(st, fm, f0, aggro=True, look=mom)
    st.use(s, mom, z)
    st.see_through(s, fm.name + "_pod_north")
    _cam(s, fm.cameras["two_shot"], focus=mom.head)
    st.hero(s, "mom", mom)
    _lights(st, s, fm)
    _heads(h, s.name, f0 + 12, mom=mom, zombie=z)


def shot_high(st, s, fm, h):
    """Beat 21: high over Steve's shoulder, the roof hidden to the camera: four in a row, the second bed appears."""
    from engine import players

    f0 = s.frame_start
    names = (("librarian", "librarian"), ("cleric", "cleric"), ("narrator", "none"), ("mom", "farmer"))
    cast = []
    steve = players.add_player(st, "steve", "steve")
    steve.place(f0, fm.A["top_step"], fm.yaw["top_step"])
    for i, (n, prof) in enumerate(names):
        c = st.actor(n, prof)
        c.place(f0, fm.A["row_%d" % (i + 1)], fm.yaw["row_%d" % (i + 1)])
        cast.append(c)
    for c in cast[:2]:
        c.look_at(f0, (c.pos_at(f0).x - 3.0, c.pos_at(f0).y - 1.0, fm.L["F"] + 1.6), ease=0)
    cast[2].look_at(f0, steve, ease=0)
    cast[3].look_at(f0, fm.zombie_eye, ease=0)
    steve.watch(f0, s.frame_end, cast[2])
    steve.sneak(f0 + 14)
    steve.attack(f0 + 18)
    fm.bed2.place_at(f0 + 20)
    st.use(s, steve, *cast)
    st.see_through(s, fm.name + "_pod_roof")
    _cam(s, fm.cameras["high"], focus=cast[2].head)
    _lights(st, s, fm)
    _heads(h, s.name, f0 + 30, **{c.name: c for c in cast})


def shot_slide(st, s, fm, h):
    """Beats 9-11: a golem appears on the platform, turns its head to the pod, slides west and drops into the slot;
    the puff, the glow's flicker."""
    f0 = s.frame_start
    g = _golem(st)
    fm.golem_spawn(g, f0 + 6, look=fm.A["pod_target"], look_after=8, empty_from=s)
    e = fm.golem_step(g, f0 + 30)
    r = fm.golem_slide(g, e + 2)
    d = fm.golem_death(g, r, camera=s, until=s.frame_end + 1)
    h["slide"] = dict(r, death=d, spawn=f0 + 6)
    st.use(s, g)
    _cam(s, fm.cameras["slide"], focus=fm.A["golem_spawn"])
    st.lights(s, scale=1.0)


def shot_hopper(st, s, fm, h):
    """Beat 12, macro: one golem's drops (towers.golem_loot: a stack of ingots, drawn as two, and a poppy) fall on
    the hopper and vanish into it one stack per 8 ticks; poppies lie on the grass."""
    from engine import mobs, towers

    f0 = s.frame_start
    loot = towers.golem_loot(1)
    items = [mobs.make_dropped_item(iid, name="hop_%s" % iid, seed=i, count=n)
             for i, (iid, n) in enumerate(sorted(loot.items())) if n > 0]
    for it in items:
        st.cast[it.name] = it
    plans = fm.deliver(items, f0 + 4, every=7, seed=2)
    lying = []
    for i in range(3):
        it = mobs.make_dropped_item("poppy", name="lying_%d" % i, seed=10 + i)
        st.cast[it.name] = it
        lying.append(it)
    cam = fm.cameras["hopper"]
    cx, cy = fm.L["chest"][0] + 0.5, fm.L["chest"][1] + 0.5
    spots = [(cx - 0.55, cy + 1.9), (cx + 0.45, cy + 2.15), (cx - 0.05, cy + 2.55)]
    fm.strew(lying, f0, s.frame_end + 1, seed=3, spots=spots, face=cam["pos"])
    st.use(s, *(items + lying))
    h["hopper"] = plans
    _cam(s, cam, focus=fm.A["hopper_target"])
    st.lights(s, scale=1.0)


def shot_stairs(st, s, fm, h):
    """Beat 22, outside view: Steve one step down breaks the top dirt step by hand (cracks, then the crumbs)."""
    from engine import players

    f0 = s.frame_start
    fm.top_step.restore(f0)
    steve = players.add_player(st, "steve", "steve")
    steve.place(f0, fm.A["one_down"], fm.yaw["one_down"])
    steve.look_at(f0, fm.top_step.center, ease=0)
    m = fm.break_top_step(steve, f0 + 10, camera=s, until=s.frame_end + 1)
    h["stairs"] = m
    st.cast[fm.top_step.name] = fm.top_step
    st.use(s, steve, fm.top_step)
    _cam(s, fm.cameras["stairs"], focus=fm.top_step.center)
    st.lights(s, scale=1.0)


def shot_lineup(st, s, fm, h):
    """The narrator: baby, the grown narrator (unemployed: plain brown robe), a nitwit (green robe) side by side."""
    f0 = s.frame_start
    spot = fm.A["lineup"]
    who = (("lineup_baby", "none", True), ("narrator_adult", "none", False), ("lineup_nitwit", "nitwit", False))
    cast = []
    for i, (n, prof, child) in enumerate(who):
        c = st.actor(n, prof, child=child) if child else st.actor(n, prof)
        p = (spot[0], spot[1] + 0.95 - i * 0.95, spot[2])
        c.place(f0, p, fm.yaw["lineup"])
        cast.append(c)
    st.use(s, *cast)
    _cam(s, fm.cameras["lineup"], focus=cast[1].head)
    st.lights(s, scale=1.0)


def shot_back(st, s, fm, h):
    """Beat 13: the back of the tower, locked tall: the dirt zigzag, the stray dirt, the baby at the foot."""
    f0 = s.frame_start
    baby = st.actor("baby", "none", child=True)
    baby.place(f0, fm.A["stairs_foot"], fm.yaw["stairs_foot"])
    baby.look_at(f0, fm.A["stairs_target"], ease=0)
    st.use(s, baby)
    _cam(s, fm.cameras["back"])
    st.lights(s, scale=1.0)


def shot_gap(st, s, fm, h):
    """Beat 15: inside at floor level, the gap in the middle, the cleric against the plug, the baby under it."""
    f0 = s.frame_start
    cl = st.actor("cleric", "cleric")
    cl.place(f0, fm.A["gap_side"], fm.yaw["gap_side"])
    baby = st.actor("baby", "none", child=True)
    baby.place(f0, (fm.A["gap_in"][0] + 0.1, fm.A["gap_in"][1] + 0.75, fm.A["gap_in"][2]), 0.0)
    st.use(s, cl, baby)
    _cam(s, fm.cameras["gap"], focus=fm.A["gap_target"])
    _lights(st, s, fm)


def shot_bounce(st, s, fm, h):
    """Beat 18: the baby bounces on Mom's red bed (two jumps, the glass roof stopping each, the small rebounds
    after), its face cheated to the lens."""
    from engine.village import yaw_to

    f0 = s.frame_start
    baby = st.actor("baby", "none", child=True)
    cam = fm.cameras["bounce"]
    bp, mp = fm.beds["mom"]["pos"], fm.A["bed_side"]
    toward = (0.65 * cam["pos"][0] + 0.35 * mp[0], 0.65 * cam["pos"][1] + 0.35 * mp[1])
    e = fm.bounce(baby, f0 + 2, "mom", jumps=2, yaw=yaw_to(bp, toward))
    h["bounce"] = (f0 + 2, e)
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["bed_side"], fm.yaw["bed_side"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    st.use(s, baby, mom)
    _cam(s, fm.cameras["bounce"], focus=baby.head)
    _lights(st, s, fm)


def shot_push(st, s, fm, h):
    """The push mechanics side-on (a stand-in place behind the tower): Steve shoves Mom along."""
    from engine import players, towers

    f0 = s.frame_start
    steve = players.add_player(st, "steve", "steve")
    mom = st.actor("mom", "farmer")
    route = fm.set["push_route"]
    r = towers.push(steve, mom, f0 + 2, route)
    mom.look_at(f0 + 2, (route[0][0] - 1.0, route[0][1] + 4.0, 1.6), ease=0)
    h["push"] = r
    st.use(s, steve, mom)
    _cam(s, fm.cameras["push"], focus=mom.head)
    st.lights(s, scale=1.0)


def shot_grow(st, s, fm, h):
    """Beats 17 / 19: the locked side view at the front glass; the baby at Mom's folded arms snaps to the grown
    narrator (unemployed, plain brown robe) in one frame. Mom's head stays on the zombie."""
    from engine import towers

    f0 = s.frame_start
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["mom_glass"], fm.yaw["mom_glass"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    baby = st.actor("baby", "none", child=True)
    baby.place(f0, fm.A["baby_glass"], fm.yaw["baby_glass"])
    baby.look_at(f0, fm.zombie_eye, ease=0)
    adult = st.actor("narrator", "none")
    f = f0 + 24
    towers.grow_up(baby, adult, f, look=fm.zombie_eye)
    h["grow"] = f
    st.use(s, mom, baby, adult)
    _cam(s, fm.cameras["grow"], focus=mom.head)
    _lights(st, s, fm)


BUILDERS = {name: globals()["shot_" + name] for name, _secs, _offs in SHOTS}


def build(scene, sky=None, res=(540, 960), samples=16, threads=2):
    """The village with the tower, one shot per entry of SHOTS. Returns dict(film, stage, village, farm, frames)."""
    from engine import look, shots, towers, village
    from films.lookdev import Stage

    sky = sky or GOLD
    look.setup_render(scene, res=res, samples=samples, threads=threads)
    v = village.build_village(scene, seed=1, edit=lambda b: towers.iron_farm(b))
    fm = towers.farm(v)
    sk = Stage.build_sky(scene, sky)
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, sk)
    h = dict(sky=sky)
    frames, by_name = {}, {}
    for name, secs, offs in SHOTS:
        s = st.shot(name, secs)
        by_name[name] = s
        BUILDERS[name](st, s, fm, h)
        if offs is None:
            offs = _strip_offsets(name, s, h)
        frames[name] = [s.frame_start + o for o in offs]
    st.finish()
    return dict(film=film, stage=st, village=v, farm=fm, frames=frames, h=h, shots=by_name)


def _strip_offsets(name, s, h):
    f0 = s.frame_start
    if name == "slide":
        r = h["slide"]
        return [r["spawn"] - f0 - 1, r["spawn"] - f0, r["frame"] + 14 - f0, r["edge"] - f0 + 2,
                r["gone"] - f0 - 2, r["gone"] - f0 + 6]
    if name == "hopper":
        plans = h["hopper"]
        first = int(round(plans[0]["track"][0][0]))
        return [first - 1 - f0, first + 4 - f0, plans[0]["frame"] - 2 - f0, plans[-1]["frame"] - 2 - f0,
                plans[-1]["frame"] + 1 - f0]
    if name == "stairs":
        m = h["stairs"]
        a, z = m["start"], m["frame"]
        return [a - 1 - f0, a + (z - a) // 3 - f0, a + 2 * (z - a) // 3 - f0, z - 1 - f0, z + 3 - f0]
    if name == "grow":
        f = h["grow"]
        return [f - 1 - f0, f - f0]
    if name == "bounce":
        a, e = h["bounce"]
        return sorted(set([a - f0 + k for k in (0, 2, 4, 7, 10)] + [min(e + 2, s.frame_end) - f0]))
    if name == "push":
        r = h["push"]
        e = r["end"]
        n = min(e, s.frame_end) - f0
        return [2] + [int(2 + (n - 2) * k / 5.0) for k in range(1, 6)]
    if name == "b24":
        b = h["b24"]
        return [b["spawn"] - 1 - f0, b["spawn"] - f0, b["spawn"] + 16 - f0, b["step"] + 20 - f0]
    return [12]


# ----------------------------------------------------------------------------------------------------
# rendering
# ----------------------------------------------------------------------------------------------------
def _render(scene, film, frame, path):
    import bpy

    film.goto(frame)
    tmp = path[:-4] + "_part"
    scene.render.filepath = tmp
    scene.render.use_file_extension = True
    bpy.ops.render.render(write_still=True)
    os.replace(tmp + ".png", path)
    return path


def _check(scene, film, frame, path, name, heroes=()):
    from tools import palette_check as pc

    film.goto(frame)
    rec = pc.probe(scene)
    rep = pc.evaluate(rec, path, heroes=heroes)
    pc.print_report(name, rep)
    return rep


def where(scene, built, name):
    """{label: (x %, y % from the top, depth)} of the heads registered for shot `name`, at its check frame."""
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    out = []
    for frame, heads in built["h"].get("where", {}).get(name, []):
        built["film"].goto(frame)
        pos = {}
        for label, ob in heads.items():
            p = ob.matrix_world.translation + ob.matrix_world.to_3x3() @ Vector((0.0, 0.0, 0.25))
            q = world_to_camera_view(scene, scene.camera, p)
            pos[label] = (round(100 * q.x), round(100 * (1 - q.y)), round(q.z, 2))
        out.append((frame, pos))
    return out


def _env_res():
    r = os.environ.get("TOWERS_RES")
    if r:
        w, h = r.lower().split("x")
        return int(w), int(h)
    return 540, 960


def render(names, dusk=False, only_where=False):
    """Render the named stills / strips to out/test/towers_<name>.png (dusk=True: the dusk sky)."""
    import bpy
    from PIL import Image, ImageDraw

    from engine import post

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    t0 = time.time()
    res = _env_res()
    samples = int(os.environ.get("TOWERS_SAMPLES", "16"))
    built = build(scene, DUSK if dusk else GOLD, res=res, samples=samples)
    film = built["film"]
    print("[towers proof] built in %.1f s" % (time.time() - t0), flush=True)
    os.makedirs(OUT, exist_ok=True)
    tag = os.environ.get("TOWERS_TAG", "")
    reports = {}
    for name in names:
        shot = DUSK_SHOTS.get(name, name) if dusk else ALIASES.get(name, name)
        for f, pos in where(scene, built, shot):
            bad = {k: v for k, v in pos.items() if not (8 <= v[0] <= 82 and 14 <= v[1] <= 60)}
            print("[towers proof] %-12s frame %d heads (x %%, y %%, depth): %s%s" % (
                name, f, pos, ("   OUTSIDE THE SAFE AREA: %s" % sorted(bad)) if bad else ""), flush=True)
        if only_where:
            continue
        frames = built["frames"][shot]
        path = os.path.join(OUT, "towers_%s%s.png" % (name, tag))
        t = time.time()
        if len(frames) == 1:
            _render(scene, film, frames[0], path)
            heroes = [ob for _l, obs in built["stage"].heroes.get(shot, []) for ob in obs]
            reports[name] = _check(scene, film, frames[0], path, name, heroes=heroes)
            if name.startswith("b"):
                post.draw_zones(Image.open(path)).save(path[:-4] + "_zones.png")
        else:
            r = scene.render
            full = (r.resolution_x, r.resolution_y)
            r.resolution_x, r.resolution_y = STRIP_RES
            tiles = []
            for fr in frames:
                p = os.path.join(OUT, "towers_%s_f%d.png" % (name, fr))
                _render(scene, film, fr, p)
                tiles.append((fr, Image.open(p).convert("RGB")))
                os.remove(p)
            r.resolution_x, r.resolution_y = full
            W, H = STRIP_RES
            sheet = Image.new("RGB", (W * len(tiles), H + 22), (20, 20, 20))
            d = ImageDraw.Draw(sheet)
            for i, (fr, im) in enumerate(tiles):
                sheet.paste(im, (i * W, 22))
                d.text((i * W + 6, 5), "frame %d" % fr, fill=(255, 255, 255))
            sheet.save(path)
        print("[towers proof] %-12s frames %s -> %s  %.1f s" % (name, frames, path, time.time() - t), flush=True)
    return built, reports


def main(argv):
    """Command line: names (see the module docstring)."""
    only_where = "--where" in argv
    names = [a for a in argv if not a.startswith("-")] or ["b04"]
    dusk = [n for n in names if n in DUSK_SHOTS]
    gold = [n for n in names if n not in DUSK_SHOTS]
    unknown = [n for n in gold if ALIASES.get(n, n) not in BUILDERS]
    if unknown:
        print("unknown proof names %s; known: %s %s %s" % (unknown, sorted(BUILDERS), sorted(DUSK_SHOTS),
                                                           sorted(ALIASES)))
        return 2
    failed = 0
    for group, is_dusk in ((gold, False), (dusk, True)):
        if group:
            _built, reports = render(group, dusk=is_dusk, only_where=only_where)
            failed += sum(len(r["failed"]) for r in reports.values())
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
