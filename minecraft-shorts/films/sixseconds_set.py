"""SIX SECONDS: the sets (film-local; wraps engine/nether.py). Docstring completed at the end of the scouting pass."""
import math
import os
import sys
import types

import bpy  # noqa: F401  (makes mathutils importable)
from mathutils import Vector

from engine import nether

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINAL_RES, FINAL_SAMPLES = (540, 960), 16
SET_NAME = "sixseconds"

# ---------------------------------------------------------------------------------------------------------------
# the skies this set was scouted under (a suggestion for films/sixseconds.py SKIES; preset 'nether' = nether.Stage)
# ---------------------------------------------------------------------------------------------------------------
SUGGESTED_SKIES = {
    "home": dict(preset="nether", biome="nether_wastes"),
    "bridge": dict(preset="nether", biome="nether_wastes"),
    "treasure": dict(preset="nether", biome="nether_wastes"),
}


def _yaw(direction):
    """Yaw of a character facing a compass direction or an (dx, dy) vector (facing -Y at yaw 0)."""
    return nether._yaw(direction)


def _add(p, d):
    return (p[0] + d[0], p[1] + d[1], p[2] + (d[2] if len(d) > 2 else 0.0))


# ---------------------------------------------------------------------------------------------------------------
# the film's own anchors (added to bas.anchors / bas.yaws; every name starts with "six_")
# ---------------------------------------------------------------------------------------------------------------
def _anchors(bas):
    A, Y = bas.anchors, bas.yaws
    out = {}

    def put(name, p, yaw=None):
        p = tuple(float(v) for v in p)
        A[name] = p
        out[name] = p
        if yaw is not None:
            Y[name] = float(yaw)

    rim = A["home_rim_w"]
    put("six_pit_lure", (5.4, 7.3, -2.0))                       # beat 6: the lure ingot on the pit floor (not on
    #                                                               the kept last block's cell (4, 6))
    put("six_pearl_rest", _add(rim, (0.25, -0.45)))              # beat 7: the pearl rests here (explicit floor point:
    #                                                               barter(lob=True, toward=<runner>) keys it over the pit)
    gravel = [(-0.45, 0.2), (-0.35, -0.35), (0.15, -0.45), (0.2, 0.45), (-0.2, 0.5), (-0.55, -0.1), (0.3, -0.3)]
    for k, d in enumerate(gravel, 1):                           # beats 8 and 20: the pile round his boots (all on the
        put("six_gravel_%d" % k, _add(rim, d))                  #   floor west of the rim x 4.0)
    put("six_pearl_pile", _add(rim, (-0.5, 0.45)))            # beat 8: one lonely pearl among the gravel
    drops = {"boots": (-0.7, 0.6), "pickaxe": (-0.3, 1.1), "gravel": (-1.0, 1.0), "pearl": (0.3, 0.9)}
    for k, d in drops.items():                                  # beat 10: what the runner drops, on the blackstone
        put("six_drop_%s" % k, _add(rim, d))
    # beats 21-23: the brute at the SOUTH end of the gold row, facing the gold diagonally (north-east), his ingot on
    # the step north-north-east of him (28 degrees: in front of his chest, 17 degrees left of straight ahead, 1.8
    # away: head pitch 21 degrees). Why there: his head can then turn to the gateway within the piglin's 75 degrees
    # (beat 23: 63), a camera on the step beyond the ingot sees the ingot with his face right above it (beat 22),
    # and the ingot-row camera holds him, his ingot and both brothers (beat 21)
    put("six_brute_gold", (7.6, 10.0, 0.0), _yaw((1.0, 1.0)))
    put("six_step_ingot", (8.16, 11.71, 1.0))
    put("six_brother_1", (7.0, 13.2, 0.0), _yaw((1.0, 1.0)))   # beats 2, 21-23: the two brothers admiring (found by
    put("six_brother_2", (6.2, 11.6, 0.0), _yaw((1.0, 1.0)))   #   search: apart in the ingot-row frame, both in
    #                                                               profile, clear of the brute's line to the reverse cam)
    put("six_brute_turned", (5.2, 15.4, 0.0), _yaw("west"))    # beat 2: the brute's dark shoulder at the right edge,
    #                                                               turned away from them
    put("six_gateway_mouth", (4.5, 18.6, 1.8))
    put("six_landing_look", (0.15, 16.7, 5.55))                 # beat 1: just past the six_landing lens                  # beat 23: what he turns his head to
    foot = A["bridge_pillar_foot"]
    for k, d in enumerate(((0.45, -0.3), (-0.3, -0.45), (0.25, -0.75)), 1):     # beats 14, 15: ingots at his feet
        put("six_bridge_ingot_%d" % k, _add(foot, d))
    for s in ("home", "bridge", "treasure"):                    # beat 16: the same three spots in every flash cut
        f = A["%s_flash" % s]
        put("six_flash_puff_%s" % s, _add(f, (1.2, -0.2)))
        put("six_flash_boots_%s" % s, _add(f, (0.7, 0.1)))
        put("six_flash_extra_%s" % s, _add(f, (-0.65, 0.0)))
    return out


# ---------------------------------------------------------------------------------------------------------------
# the film's own camera suggestions (added to bas.cameras with the nether module's fields; names start "six_")
# ---------------------------------------------------------------------------------------------------------------
NEW_CAMERAS = {
    # beat 1: nether's 'landing' panned 9 degrees toward the brute (he was cut by the left edge) and tilted down a
    # little (the piglins at the gold sat in the caption band); a slow push in along the landing (pos1)
    "six_landing": dict(pos=(0.4, 17.4, 5.8), target=(6.0, 13.6, 3.4), lens=26.0, fstop=2.8, beats=(1,),
                        pos1=(0.62, 17.25, 5.76), set="home", focus="home_landing_edge",
                        sees=("home_landing_edge", "home_gold_1:head", "home_gold_2:head", "home_gold_3:head")),
    # beats 2 and 21 (the ingot row frame): snout height from the north-west along the gold wall; replaces nether's
    # 'ingot_row' for this film because its frame cannot hold the brute's own ingot in beat 21
    "six_ingot_row": dict(pos=(5.0, 17.0, 1.65), target=(7.6, 10.2, 1.45), lens=40.0, fstop=2.2, beats=(2, 21),
                          set="home", focus="six_step_ingot",
                          sees=("six_brother_1:head", "six_brother_2:head", "six_brute_gold:head")),
    # beat 7: behind and above the runner's right shoulder at the west rim, down into the pit
    "six_over_pit": dict(pos=(2.6, 4.9, 3.3), target=(4.9, 7.0, -0.6), lens=26.0, fstop=4.0, beats=(7,),
                         set="home", pit="open", focus="home_pit_center",
                         sees=("home_pit_2:head", "home_pit_3:head", "home_pit_4:head")),
    # beat 8: low on the floor south-west of the boots at the rim, the pit beyond them on the right
    "six_boots_rim": dict(pos=(1.75, 4.75, 1.0), target=(3.55, 6.95, 0.05), lens=40.0, fstop=2.8, beats=(8,),
                          set="home", pit="open", focus="home_rim_w", sees=("home_rim_w:shins",)),
    # beat 10: rim_side a little wider
    "six_rim_side": dict(pos=(3.4, 0.8, 1.45), target=(3.1, 7.6, 1.0), lens=35.0, fstop=3.0, beats=(9,),
                         set="home", pit="open", focus="home_rim_w", sees=("home_rim_w", "home_strike")),
    "six_rim_wide": dict(pos=(3.4, 0.8, 1.45), target=(3.3, 7.6, 0.85), lens=28.0, fstop=3.2, beats=(10,),
                         set="home", pit="open", focus="home_rim_w", sees=("home_rim_w", "home_strike")),
    # beat 22: low on the step beyond the ingot, looking back along his line of sight: the ingot in the middle,
    # his face right above it; a slow push in (pos1)
    "six_ingot_close": dict(pos=(8.84, 13.8, 1.12), target=(8.0, 11.2, 1.15), lens=35.0, fstop=2.0, beats=(22,),
                            pos1=(8.8, 13.68, 1.12), set="home", focus="six_step_ingot",
                            sees=("six_brute_gold:head",)),
    # beat 23 (the story's fallback): reverse angle from just inside the gateway, floor level
    "six_gate_reverse": dict(pos=(8.6, 16.6, 0.4), target=(7.3, 10.6, 1.2), lens=32.0, fstop=2.8, beats=(23,),
                             set="home", focus="six_brute_gold", sees=("six_brute_gold",)),
}


def _cameras(bas):
    out = {}
    for name, c in NEW_CAMERAS.items():
        d = dict(pos=tuple(c["pos"]), target=tuple(c["target"]), lens=float(c["lens"]), fstop=c["fstop"],
                 beats=tuple(c["beats"]), note=c.get("note", ""), set=c["set"], cast=tuple(c.get("cast", ())),
                 sees=tuple(c.get("sees", ())), pit=c.get("pit"), pillar=bool(c.get("pillar")),
                 focus=c.get("focus"), lights=dict(c.get("lights") or {}))
        for k in ("pos1", "target1"):
            if k in c:
                d[k] = tuple(c[k])
        bas.cameras[name] = d
        out[name] = d
    return out


# ---------------------------------------------------------------------------------------------------------------
# THE BEATS: where each one is filmed and with what (the staging of its scouting still)
# cast entries: (kind, where, look, opts) kind: brute | piglin | piglin_admire | steve | steve_crouch | steve_ingot
#               | item:<id> | poof;  where / look: an anchor name or a point; opts: dict(yaw=, aggro=, attack=)
# ---------------------------------------------------------------------------------------------------------------
G3 = [("piglin", "home_gold_%d" % k, "home_gold_target", {}) for k in (1, 2, 3)]
NE = _yaw((1.0, 1.0))

BEATS = [
    dict(key="b01_landing", beat=1, cam="six_landing", sky="home", set="home",
         cast=[("brute", "home_landing_edge", "six_landing_look", dict(yaw=nether.yaw_to((2.65, 16.25), (0.4, 17.4))))]
         + G3, hero="brute"),
    dict(key="b02_ingot_row", beat=2, cam="six_ingot_row", sky="home", set="home",
         cast=[("piglin_admire", "six_brother_1", None, {}), ("piglin_admire", "six_brother_2", None, {}),
               ("brute", "six_brute_turned", None, {})], hero="piglin"),
    dict(key="b03_gate", beat=3, cam="gate", sky="home", set="home",
         cast=[("brute", "home_landing", "home_landing_look", {})] + G3, hero="brute"),
    dict(key="b04_inside_gate", beat=4, cam="inside_gate", sky="home", set="home",
         cast=[("steve", "home_gateway", None, dict(yaw=_yaw("south"))), ("brute", "home_landing", "home_gateway", {})],
         hero="steve"),
    dict(key="b05_boot", beat=5, cam="boot", sky="home", set="home",
         cast=[("steve", "home_boot_mark", None, {})] +
              [("piglin", "home_gold_%d" % k, "home_boot_mark", {}) for k in (1, 2, 3)], hero="boots"),
    dict(key="b06_pit", beat=6, cam="pit", sky="home", set="home", pit="keep",
         cast=[("steve", "home_rim_w", "home_pit_center", {}), ("item:gold_ingot", "six_pit_lure", None, {})] +
              [("piglin", "home_pit_approach_%d" % k, "home_pit_center", {}) for k in (1, 2, 3)],
         lights={"home_pit": 2.0}, hero="steve"),
    dict(key="b07_over_pit", beat=7, cam="six_over_pit", sky="home", set="home", pit="open",
         cast=[("steve_ingot", "home_rim_w", "home_pit_center", {}), ("item:ender_pearl", "six_pearl_rest", None, {})] +
              [("piglin_admire", "home_pit_%d" % k, None, dict(yaw=_yaw("west"))) for k in (2, 3, 4)],
         lights={"home_pit": 2.0}, hero="piglin"),
    dict(key="b08_boots_rim", beat=8, cam="six_boots_rim", sky="home", set="home", pit="open",
         cast=[("steve", "home_rim_w", "home_pit_center", {}), ("item:ender_pearl", "six_pearl_pile", None, {})] +
              [("item:gravel", "six_gravel_%d" % k, None, {}) for k in range(1, 8)],
         lights={"home_pit": 2.0}, hero="boots"),
    dict(key="b09_rim_side", beat=9, cam="six_rim_side", sky="home", set="home", pit="open",
         cast=[("steve", "home_rim_w", "home_pit_center", {}),
               ("brute", "home_strike", "home_rim_w", dict(aggro=True))] +
              [("piglin_admire", "home_pit_%d" % k, None, dict(yaw=_yaw("west"))) for k in (2, 3, 4)],
         hero="brute"),
    dict(key="b10_rim_wide", beat=10, cam="six_rim_wide", sky="home", set="home", pit="open",
         cast=[("brute", "home_strike", "home_rim_w", {}), ("poof", "home_rim_w", None, {}),
               ("item:golden_boots", "six_drop_boots", None, {}), ("item:iron_pickaxe", "six_drop_pickaxe", None, {}),
               ("item:gravel", "six_drop_gravel", None, {}), ("item:ender_pearl", "six_drop_pearl", None, {})] +
              [("piglin_admire", "home_pit_%d" % k, None, dict(yaw=_yaw("west"))) for k in (2, 3, 4)],
         hero="brute"),
    dict(key="b11_bridge_boot", beat=11, cam="bridge_boot", sky="bridge", set="bridge",
         cast=[("steve", "bridge_boot_mark", None, {})], hero="boots"),
    dict(key="b12_bridge_shoulder", beat=12, cam="bridge_shoulder", sky="bridge", set="bridge",
         cast=[("steve", "bridge_player", "bridge_player_look", {}), ("brute", "bridge_brute", "bridge_brute_look", {})],
         hero="brute"),
    dict(key="b13_bridge_pillar", beat=13, cam="bridge_pillar", sky="bridge", set="bridge", pillar=True,
         cast=[("steve_crouch", "bridge_pillar_top", None, {}),
               ("brute", "bridge_pillar_foot", "bridge_pillar_top_target", {})], hero="brute"),
    dict(key="b14_bridge_profile", beat=14, cam="bridge_profile", sky="bridge", set="bridge", pillar=True,
         cast=[("brute", "bridge_pillar_foot", "bridge_pillar_top_target", {}),
               ("item:gold_ingot", "six_bridge_ingot_1", None, {}), ("item:gold_ingot", "six_bridge_ingot_2", None, {})],
         hero="brute"),
    dict(key="b15_bridge_top", beat=15, cam="bridge_top", sky="bridge", set="bridge", pillar=True,
         cast=[("steve_crouch", "bridge_pillar_top", None, {}),
               ("brute", "bridge_pillar_foot", (0.5 + 400, 19.6, 4.6), {})] +
              [("item:gold_ingot", "six_bridge_ingot_%d" % k, None, {}) for k in (1, 2, 3)], hero="brute"),
    dict(key="b16a_bridge_flash", beat=16, cam="bridge_flash", sky="bridge", set="bridge",
         cast=[("brute", "bridge_flash", None, {}), ("poof", "six_flash_puff_bridge", None, {}),
               ("item:golden_boots", "six_flash_boots_bridge", None, {}),
               ("item:gravel", "six_flash_extra_bridge", None, {})], hero="brute"),
    dict(key="b16b_treasure_flash", beat=16, cam="treasure_flash", sky="treasure", set="treasure",
         cast=[("brute", "treasure_flash", None, {}), ("poof", "six_flash_puff_treasure", None, {}),
               ("item:golden_boots", "six_flash_boots_treasure", None, {}),
               ("item:ender_pearl", "six_flash_extra_treasure", None, {})], hero="brute"),
    dict(key="b16c_home_flash", beat=16, cam="flash", sky="home", set="home",
         cast=[("brute", "home_flash", None, {}), ("poof", "six_flash_puff_home", None, {}),
               ("item:golden_boots", "six_flash_boots_home", None, {}),
               ("item:iron_pickaxe", "six_flash_extra_home", None, {})], hero="brute"),
    dict(key="b17_corridor", beat=17, cam="corridor", sky="home", set="home",
         cast=[("brute", "home_gateway", None, {})] + G3, hero="brute"),
    dict(key="b18_gate", beat=18, cam="gate", sky="home", set="home", flicker=True,
         cast=[("brute", "home_gateway", None, {})] + G3, hero="brute"),
    dict(key="b19_gate", beat=19, cam="gate", sky="home", set="home",
         cast=[("steve", (5.6, 15.0, 0.0), None, dict(yaw=nether.yaw_to((4.5, 19.0), (6.4, 9.0))))] + G3,
         hero="steve"),
    dict(key="b20_pit", beat=20, cam="pit", sky="home", set="home", pit="open",
         cast=[("steve", "home_rim_w", "home_pit_center", {})] +
              [("piglin_admire", "home_pit_%d" % k, None, dict(yaw=_yaw("west") if k in (2, 4) else _yaw("south")))
               for k in (1, 2, 3, 4)] +
              [("item:gravel", "six_gravel_%d" % k, None, {}) for k in (1, 3, 5)] +
              [("item:ender_pearl", "six_pearl_rest", None, {})],
         lights={"home_pit": 2.0}, hero="piglin"),
    dict(key="b21_ingot_row", beat=21, cam="six_ingot_row", sky="home", set="home",
         cast=[("piglin_admire", "six_brother_1", None, {}), ("piglin_admire", "six_brother_2", None, {}),
               ("brute", "six_brute_gold", "six_step_ingot", {}), ("item:gold_ingot", "six_step_ingot", None, {})],
         hero="brute"),
    dict(key="b22_ingot_close", beat=22, cam="six_ingot_close", sky="home", set="home",
         cast=[("brute", "six_brute_gold", "six_step_ingot", {}), ("item:gold_ingot", "six_step_ingot", None, {})],
         hero="brute"),
    dict(key="b23_gate_reverse", beat=23, cam="six_gate_reverse", sky="home", set="home",
         cast=[("brute", "six_brute_gold", "six_gateway_mouth", {}), ("item:gold_ingot", "six_step_ingot", None, {}),
               ("piglin_admire", "six_brother_1", None, {}), ("piglin_admire", "six_brother_2", None, {})],
         hero="brute"),
    dict(key="b23_gate", beat=23, cam="gate", sky="home", set="home",
         cast=[("brute", "six_brute_gold", "six_gateway_mouth", {}), ("item:gold_ingot", "six_step_ingot", None, {}),
               ("piglin_admire", "six_brother_1", None, {}), ("piglin_admire", "six_brother_2", None, {})],
         hero="brute"),
]
BEAT_KEYS = [b["key"] for b in BEATS]


# ---------------------------------------------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------------------------------------------
def build_set(scene, layout=None):
    """The three bastion sets of "Six Seconds" (engine.nether.build_bastion) with this film's anchors and camera
    suggestions added; bas.sets['sixseconds'] is the film's dict (anchors, cameras, beats, parts, cutaways)."""
    bas = nether.build_bastion(scene, layout=layout)
    anchors = _anchors(bas)
    cams = _cameras(bas)
    bas.sets[SET_NAME] = dict(anchors=anchors, cameras=cams, beats={b["key"]: b for b in BEATS},
                              parts=parts(bas), cutaways=sorted(bas.cutaways))
    return bas


def parts(bas):
    """What changes on camera: name -> what it is and how a film drives it."""
    return {
        "pit_blocks": "bas.pit_blocks (8 engine.breaking Breakables, cells x 4..5, y 6..7, z -1 / -2): "
                      "bas.pit_open(shot[, keep=[bas.pit_last.cell]])",
        "pit_last": "bas.pit_last (cell %s): breaking.mine(runner, bas.pit_last, f, camera=s)" % (bas.pit_last.cell,),
        "pit_fill": "bas.pit_fill: keyed by pit_open",
        "pillar": "bas.pillar (3 netherrack Breakables at %s): bas.pillar_in(shot) / bas.pillar_from(frame)"
                  % ([b.cell for b in bas.pillar],),
        "lava_flicker": "bas.lava_flicker(f0, f1): the corridor's lava light (beat 18)",
        "chests": "bas.chests: %s (fixtures Chest: open / close)" % sorted(bas.chests),
    }


def camera(bas, name):
    """bas.cameras[name] (the nether module's and this file's)."""
    return bas.cameras[name]


def beat(key):
    """The BEATS entry `key` ('b07_over_pit')."""
    for b in BEATS:
        if b["key"] == key:
            return b
    raise KeyError("no beat %r (beats: %s)" % (key, ", ".join(BEAT_KEYS)))


# ---------------------------------------------------------------------------------------------------------------
# checks (no rendering)
# ---------------------------------------------------------------------------------------------------------------
LOOK_SUFFIXES = ("_target", "_center", "_cam", "_item", "_look", "_mouth", "_ingot", "_lure", "_rest")


def standing_anchors(bas):
    """Anchors where a character (or an item) stands: everything not named as a look target."""
    return {n: p for n, p in bas.anchors.items() if not n.endswith(LOOK_SUFFIXES[:5]) and "_look" not in n}


def check(bas, verbose=True):
    """Problems (empty = all good): anchors not on solid ground, cameras inside or touching blocks, what each
    camera must see out of frame or hidden (nether's check_cameras)."""
    out = []
    w = bas.world
    for name, p in sorted(bas.anchors.items()):
        if name.endswith(("_target", "_center", "_cam", "_look", "_mouth")) or "_look" in name:
            continue
        x, y, z = p
        cx, cy = int(math.floor(x)), int(math.floor(y))
        below = int(math.floor(z - 0.01))
        pit = any((cx, cy) == (c[0], c[1]) for c in bas.pit_blocks)
        pillar = any((cx, cy) == (b.cell[0], b.cell[1]) for b in bas.pillar)
        support = w.block_id(cx, cy, below)
        if pit and z > -1.5:
            support = support or "pit block (Breakable: there only while the pit is whole)"
        if pillar and z > 0.5:
            support = support or "netherrack pillar (Breakable)"
        if not support:
            out.append("anchor %s at %s: nothing under it (cell %s)" % (name, p, (cx, cy, below)))
        elif support in ("lantern", "iron_chain", "chain"):
            out.append("anchor %s at %s stands on a %s" % (name, p, support))
        g = bas.ground(x, y)
        if not (pit or pillar) and (g is None or abs(g - z) > 0.02):
            out.append("anchor %s at z %.2f, the ground there is %s" % (name, z, g))
        for cz in (int(math.floor(z + 0.2)), int(math.floor(z + 1.2))):
            bid = w.block_id(cx, cy, cz)
            if bid and w.is_solid(cx, cy, cz) and not bid.endswith(("_stairs", "_slab")):
                out.append("anchor %s inside %s" % (name, bid))
    for name, c in sorted(bas.cameras.items()):
        px, py, pz = c["pos"]
        for dx in (-0.12, 0.12):
            for dy in (-0.12, 0.12):
                for dz in (-0.12, 0.12):
                    cell = (int(math.floor(px + dx)), int(math.floor(py + dy)), int(math.floor(pz + dz)))
                    if w.is_full_cube(*cell) or w.is_solid(*cell):
                        out.append("camera %s within 0.12 of %s at %s" % (name, w.block_id(*cell), cell))
                        break
                else:
                    continue
                break
            else:
                continue
            break
    out += bas.check_cameras()
    if verbose:
        for o in out:
            print("[sixseconds_set] PROBLEM", o)
    return out


def report(bas, key):
    """Where the cast of a beat lands in its camera's frame (projected, u v 0..1 from the top left)."""
    b = beat(key)
    c = bas.cameras[b["cam"]]
    rows = []
    for kind, where, _look, _o in b["cast"]:
        p = bas.anchors[where] if isinstance(where, str) else where
        h = {"brute": 2.0, "piglin": 2.0, "piglin_admire": 2.0, "steve": 1.875, "steve_ingot": 1.875,
             "steve_crouch": 1.5}.get(kind, 0.25)
        feet = nether.project(c["pos"], c["target"], c["lens"], p)
        head = nether.project(c["pos"], c["target"], c["lens"], (p[0], p[1], p[2] + h))
        rows.append((kind, where if isinstance(where, str) else tuple(round(v, 2) for v in where),
                     None if feet is None else tuple(round(v, 2) for v in feet),
                     None if head is None else tuple(round(v, 2) for v in head)))
    return rows


# ---------------------------------------------------------------------------------------------------------------
# scouting film (in memory: films.sixseconds_set_scout), one 1-second shot per beat still
# ---------------------------------------------------------------------------------------------------------------
SCOUT_FILM = "sixseconds_set_scout"
SCOUT_FRAME = 12                 # the still is this frame of its shot
_SCOUT = []                      # the beat keys the scout film is built with


def _pos(bas, where):
    return Vector(bas.anchors[where]) if isinstance(where, str) else Vector(where)


def _stage(st, s, bas, b, pool):
    """Stage beat `b` in shot s: cast on their anchors, camera, pit / pillar, lights. Returns the visible things."""
    from engine import breaking, piglins

    A, Y = bas.anchors, bas.yaws
    f0, f1 = s.frame_start, s.frame_end
    used, vis = {}, []

    def take(k):
        ob = pool[k][used.get(k, 0)]
        used[k] = used.get(k, 0) + 1
        return ob

    hero = []
    for kind, where, look, opts in b["cast"]:
        p = _pos(bas, where)
        if kind == "poof":
            piglins.poof(p, f0 - 8, camera=s, size=(0.6, 1.8), seed=3)
            continue
        if kind.startswith("item:"):
            item_id = kind[5:]
            ob = take(item_id)
            ob.place(f0, p)
            ob.animate(f0, f1 + 1)
            vis.append(ob)
            continue
        k = "steve" if kind.startswith("steve") else "piglin" if kind.startswith("piglin") else kind
        ob = take(k)
        yaw = opts.get("yaw", Y.get(where, 0.0) if isinstance(where, str) else 0.0)
        ob.place(f0, p, yaw)
        if kind == "steve_ingot":
            ob.hold("gold_ingot")
        elif k == "steve":
            ob.hold("iron_pickaxe")
        if look is not None:
            ob.look_at(f0, _pos(bas, look), ease=0)
        if kind == "steve_crouch":
            ob.sneak(f0)
        if kind == "piglin_admire":
            ob.admire(f0, "gold_ingot")
        if opts.get("aggro"):
            ob.aggro(f0)
        if k != "steve":
            ob.flop_ears(f0, f1 + 1)
        vis.append(ob)
        if (b.get("hero") == "brute" and k == "brute") or (b.get("hero") == "piglin" and k == "piglin") \
                or (b.get("hero") in ("steve", "boots") and k == "steve"):
            hero.append(ob)
    c = bas.cameras[b["cam"]]
    pit = b.get("pit")
    if pit:
        bas.pit_open(s, keep=[bas.pit_last.cell] if pit == "keep" else ())
        if pit == "keep":
            breaking.crack(bas.pit_last, f0, 6)
            st.cast[bas.pit_last.name] = bas.pit_last
            vis.append(bas.pit_last)
    if b.get("pillar"):
        bas.pillar_in(s)
    if b.get("flicker"):
        bas.lava_flicker(f0, f1)
    s.lens(b.get("lens", c["lens"]), b.get("fstop", c["fstop"] or 4.0))
    pos, target = b.get("pos", c["pos"]), b.get("target", c["target"])
    pos1 = b.get("pos1", c.get("pos1"))
    if pos1:
        s.move(pos, target, pos1, b.get("target1", c.get("target1", target)), ease="linear")
    else:
        s.move(pos, target)
    fo = b.get("focus", c.get("focus"))
    s.focus(_pos(bas, fo) if fo is not None else Vector(target))
    st.use(s, *vis)
    if hero:
        st.hero(s, b["hero"], *hero[:1])
    lights = dict(b.get("lights") or c.get("lights") or {})
    st.lights(s, b.get("scale", 1.0), groups=lights or None, **bas.lights_for(b["set"]))
    return vis


def _scout_build(scene, sky=None):
    """The scouting film: one 1-second shot per beat in _SCOUT (all of BEATS by default), each under its sky."""
    from engine import piglins, players, shots

    scene.render.resolution_x, scene.render.resolution_y = FINAL_RES
    scene.cycles.samples = FINAL_SAMPLES
    bas = build_set(scene)
    film = shots.Film(scene, fps=24)
    keys = _SCOUT or BEAT_KEYS
    skies = {k: v for k, v in SUGGESTED_SKIES.items() if any(beat(b)["sky"] == k for b in keys)}
    st = nether.Stage(scene, film, bas, skies=skies, sky=sky)
    need = {}
    for key in keys:
        b = beat(key)
        n = {}
        for kind, _w, _l, _o in b["cast"]:
            k = kind[5:] if kind.startswith("item:") else "steve" if kind.startswith("steve") else \
                "piglin" if kind.startswith("piglin") else kind
            n[k] = n.get(k, 0) + 1
        for k, v in n.items():
            need[k] = max(need.get(k, 0), v)
    pool = {"brute": [piglins.add_piglin(st, "six_brute", "brute")],
            "piglin": [piglins.add_piglin(st, "six_pig_%d" % i, weapon=("crossbow" if i == 3 else "default"))
                       for i in range(1, max(need.get("piglin", 0), 1) + 1)],
            "steve": [players.add_player(st, "six_runner", "steve")]}
    players.equip(pool["steve"][0], boots="golden")
    for k, v in need.items():
        if k not in pool and k != "poof":
            pool[k] = [piglins.add_item(st, k, name="six_%s_%d" % (k, i)) for i in range(1, v + 1)]
    for key in keys:
        b = beat(key)
        s = st.shot(key, 1.0, sky=b["sky"])
        _stage(st, s, bas, b, pool)
    st.finish()
    return {"film": film, "captions": [], "stage": st, "bastion": bas}


def register_scout(keys=None):
    """Make the scouting film importable as films.sixseconds_set_scout (in memory) with these beats."""
    global _SCOUT
    _SCOUT = list(keys or BEAT_KEYS)
    mod = types.ModuleType("films." + SCOUT_FILM)
    mod.__file__ = os.path.abspath(__file__)
    mod.SKIES = {k: v for k, v in SUGGESTED_SKIES.items() if any(beat(b)["sky"] == k for b in _SCOUT)}
    mod.build = _scout_build
    sys.modules["films." + SCOUT_FILM] = mod
    return mod


def render_scouts(keys, res=FINAL_RES, samples=FINAL_SAMPLES, threads=2, tag="", check_colours=True):
    """Render the scouting still of each beat key through render.Session (one build per sky): out/test/
    sixseconds_set_<key>[tag].png and its _zones.png. Returns the paths."""
    import time

    import render as R
    from PIL import Image

    from engine import post

    register_scout(keys)
    paths = []
    by_sky = {}
    for k in keys:
        by_sky.setdefault(beat(k)["sky"], []).append(k)
    for sky, ks in by_sky.items():
        ses = R.Session(SCOUT_FILM, sky=sky)
        ses.configure(tuple(res), samples, threads, None)
        for k in ks:
            s = next(x for x in ses.film.shots if x.name == k)
            path = os.path.join(ROOT, "out", "test", "sixseconds_set_%s%s.png" % (k, tag))
            t = time.time()
            ses.render_frame(s.frame_start + SCOUT_FRAME, path)
            with Image.open(path) as im:
                post.draw_zones(im).save(path[:-4] + "_zones.png")
            print("[sixseconds_set] %s (sky %s) -> %s  %.1fs" % (k, sky, path, time.time() - t), flush=True)
            if check_colours:
                try:
                    nether.check_still(ses.scene, path, heroes=ses.result["stage"].heroes.get(k, ()))
                except Exception as e:          # a measurement must never stop the scouting
                    print("[sixseconds_set] check_still failed: %r" % (e,))
            paths.append(path)
    return paths


def _selftest():
    import bpy

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    bas = build_set(scene)
    probs = check(bas)
    print("[sixseconds_set] %d anchors, %d cameras, %d beats: %d problem(s)" % (
        len(bas.anchors), len(bas.cameras), len(BEATS), len(probs)))
    return len(probs)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    code = 0
    if not args or "check" in args:
        code += _selftest()
    if "report" in args:
        import bpy
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bas = build_set(bpy.context.scene)
        for k in [a for a in args if a in BEAT_KEYS] or BEAT_KEYS:
            print(k, beat(k)["cam"])
            for row in report(bas, k):
                print("   ", row)
    want = [a for a in args if a in BEAT_KEYS] if "report" not in args else []
    if "all" in args:
        want = list(BEAT_KEYS)
    lo = "--lo" in sys.argv
    if want:
        render_scouts(want, res=(270, 480) if lo else FINAL_RES, samples=8 if lo else FINAL_SAMPLES,
                      tag="_lo" if lo else "", check_colours=not lo)
    sys.exit(1 if code else 0)
