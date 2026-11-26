"""Proof stills for engine/music.py: every beat of "The Crammys" on this module's sets, staged EXACTLY as the BEATS
section of engine/music.py says (this file is the worked example of that docstring), plus close proofs of the note
blocks, the jukebox, the discs, the totem and the held items, in the REAL village (the edit hook,
films.lookdev.Stage, engine.look), 540x960, 16 samples, 2 threads, motion blur on.

    $BPY -m engine.music stills wide_gold notes           # -> out/test/music_<name>.png (one build per sky and call;
    $BPY -m tools.music_proof wide_night jukebox           #    2-4 names per call stay under 300 s)
    MUSIC_RES=270x480 MUSIC_SAMPLES=8 $BPY -m tools.music_proof cams_gold      # quick framing tests
    $BPY -m tools.check_music_zones [gold|night] [shot ...]                  # faces vs the safe area, no render

Names (sky): wide_gold, wide_night (the frontal wide), notes (gold: the three hero note blocks played, 3 tiles),
jukebox (night: notes rising, the disc popping out, 4 tiles), discs (night: disc 11 and cat held to the lens, as
dropped items and as hero props), totem (gold: turning on the pedestal, 3 tiles), held (gold: block items held),
horn (gold: Noor raising the goat horn), doorstep (night: Kai's doorstep from the lane camera), clap (night: the
applause, 4 tiles), meadow_disc (night: beat 16's drop), cams_gold (beats 1-6, first frames), cams_night (beats 7, 8,
17-24, first frames), ends_gold / ends_night (the last frames of the moving cameras), b<N> (one beat's still,
for N in 1-6, 8, 18-24; 'lane' = beat 7, 'lane17' = beat 17), b5x / b8x / b24x (action sheets: 5 frames of the
take). Every name is followed by tools.palette_check's report (for sheets the first tile).

Overrides for framing work (no edit of engine/music.py needed): MUSIC_CAMS='{"b1": {"pos": [...], ...}}' merges
into band.cameras, MUSIC_ANCHORS='{"steve_front": [x, y]}' moves anchors (stage floor z 1.0, ground anchors keep
the ground height).
"""
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "test")
TILE = (270, 480)

# the skies of the proof (and the film's suggestion): see engine/music.py SKIES
from engine.music import SKIES  # noqa: E402

NIGHT_TORCHES = 1.3

# shot name -> (sky, seconds, still offsets from the shot's first frame; None = h[name] gives them)
SHOTS = [
    ("b1", "gold", 3.0, [12]), ("b2", "gold", 2.5, [8]), ("b3", "gold", 2.5, [8]), ("b4", "gold", 2.5, [20]),
    ("b5", "gold", 3.5, [2]), ("b6", "gold", 3.5, [3]), ("wide_gold", "gold", 1.5, [10]),
    ("notes_zuri", "gold", 1.0, [6]), ("notes_kai", "gold", 1.0, [6]), ("notes_sunny", "gold", 1.0, [6]),
    ("totem", "gold", 4.0, [6, 30, 54]), ("held", "gold", 1.5, [16]), ("horn", "gold", 1.5, [16]),
    ("lane", "night", 2.5, [24]), ("lane17", "night", 2.5, [26]), ("b8", "night", 3.5, None),
    ("b18", "night", 2.5, [30]), ("b19", "night", 2.5, [14]), ("b20", "night", 3.0, [20]),
    ("b21", "night", 2.5, [4]), ("b22", "night", 2.5, [20]), ("b23", "night", 3.0, None),
    ("b24", "night", 4.0, None), ("wide_night", "night", 1.5, [12]), ("jukebox", "night", 4.0, None),
    ("discs_drop", "night", 1.5, [20]), ("doorstep", "night", 1.0, [8]), ("clap", "night", 1.5, [1, 3, 4, 6]),
    ("discs_hero", "night", 1.0, [8]), ("meadow_disc", "night", 4.0, None),
]
SKY_OF = {name: sky for name, sky, _s, _o in SHOTS}
# proof name -> the shots it is made of (several = a sheet of tiles)
PROOFS = {
    "wide_gold": ["wide_gold"], "wide_night": ["wide_night"], "notes": ["notes_zuri", "notes_kai", "notes_sunny"],
    "jukebox": ["jukebox"], "discs": ["b20", "discs_drop", "discs_hero"], "meadow_disc": ["meadow_disc"],
    "totem": ["totem"], "held": ["held"], "horn": ["horn"], "doorstep": ["doorstep"], "clap": ["clap"],
    "cams_gold": ["b1", "b2", "b3", "b4", "b5", "b6"],
    "cams_night": ["lane", "b8", "lane17", "b18", "b19", "b20", "b21", "b22", "b23", "b24"],
}
for _n in ("b1", "b2", "b3", "b4", "b5", "b6", "b8", "b18", "b19", "b20", "b21", "b22", "b23", "b24", "lane",
           "lane17"):
    PROOFS.setdefault(_n, [_n])
# the last frames of the moving cameras (the first frames are in cams_gold / cams_night)
ENDS = {"ends_gold": ["b1", "b2", "b3", "b5", "b6"], "ends_night": ["b8", "b21", "b23", "b24"]}
PROOFS.update(ENDS)
# action sheets: every still frame the shot declares (h[shot + "_take"])
TAKES = {"b5x": "b5", "b8x": "b8", "b24x": "b24", "b6x": "b6", "b1x": "b1", "b23x": "b23", "lanex": "lane"}
for _k, _v in TAKES.items():
    PROOFS[_k] = [_v]
SHEETS = ("ends_gold", "ends_night", "notes", "discs", "totem", "jukebox", "clap", "cams_gold", "cams_night",
          "meadow_disc") + tuple(TAKES)


def _cam(s, cam, focus=None, moving=True):
    """Shot.lens / move / focus from a band.cameras entry (pos1 / target1 = the move)."""
    s.lens(cam["lens"], cam.get("fstop", 4.0))
    if moving and (cam.get("pos1") is not None or cam.get("target1") is not None):
        s.move(cam["pos"], cam["target"], cam.get("pos1", cam["pos"]), cam.get("target1", cam["target"]))
    else:
        s.move(cam["pos"], cam["target"])
    s.focus(focus if focus is not None else cam.get("focus", cam["target"]))


def _cam_at(s, cam, frame):
    """Where the band camera `cam` is at `frame` of shot s (Shot.move's smooth ease)."""
    from mathutils import Vector

    u = min(1.0, max(0.0, (frame - s.frame_start) / float(max(1, s.frame_end + 1 - s.frame_start))))
    e = u * u * (3.0 - 2.0 * u)
    p0 = Vector(cam["pos"])
    p1 = Vector(cam.get("pos1", cam["pos"]))
    return p0 + (p1 - p0) * e


_EMPTY = {}


def _p(st, name, skin=None, f0=None):
    """The player `name` (built on first use); f0 = the shot's first frame: whatever he held in an earlier shot is
    put away there (KEY HOLDS PER SHOT)."""
    from engine import players

    p = players.add_player(st, name, skin or name)
    if f0 is not None and _EMPTY.get(name) != f0:
        _EMPTY[name] = f0
        for hand in ("right", "left"):
            if p.holding_at(hand, f0) is not None:
                p.hold(None, hand=hand, frame=f0)
    return p


def _put(st, bd, name, key, f0, look=None):
    """Place the player `name` on anchor `key` (facing the anchor's yaw), optionally looking at a point."""
    p = _p(st, name, f0=f0)
    p.place(f0, bd.A[key], bd.yaw.get(key, 0.0))
    if look is not None:
        p.look_at(f0, look, ease=0)
    return p


def _zone(h, s, frame, items):
    """Declare what tools/check_music_zones.py checks on `frame` of shot s: [(label, thing, kind)]."""
    h.setdefault("zones", {}).setdefault(s.name, []).append((int(frame), list(items)))


def _up(p, dz):
    return (p[0], p[1], p[2] + dz)


# ----------------------------------------------------------------------------------------------------
# golden hour (beats 1-6)
# ----------------------------------------------------------------------------------------------------
def shot_b1(st, s, bd, h):
    """Beat 1: Steve sharp in front, the three tapping behind him, Noor with the horn (no note)."""
    from engine import music

    f0, f1 = s.frame_start, s.frame_end
    cam = bd.cameras["b1"]
    steve = _put(st, bd, "steve", "steve_front", f0)
    z = _put(st, bd, "zuri", "zuri", f0)
    k = _put(st, bd, "kai", "kai", f0)
    su = _put(st, bd, "sunny", "sunny", f0)
    no = _put(st, bd, "noor", "noor", f0)
    bd.tap("zuri", z, f0 + 6, camera=s)
    bd.tap("kai", k, f0 + 16, camera=s)
    bd.tap("sunny", su, f0 + 26, camera=s)
    bd.tap("zuri", z, f0 + 40, camera=s)
    bd.tap("kai", k, f0 + 50, camera=s)
    music.hold(no, "goat_horn", frame=f0)
    no.toot(f0 + 4, f1)
    steve.look_at(f0 + 30, _up(bd.A["kai"], 1.6), ease=10)          # he turns his head back to look at them ...
    steve.look_at(f0 + 54, _up(bd.A["steve_front"], 1.5), ease=10) # ... then to the front
    steve.look_at(f0 + 54, _cam_at(s, cam, f0 + 60), ease=10)
    st.use(s, steve, z, k, su, no)
    st.hero(s, "steve", steve)
    _cam(s, cam, focus=steve.head)
    bd.lights(st, s, scale=1.0)
    nz = bd.notes
    for f in (f0 + 12, f1):
        _zone(h, s, f, [("steve", steve, "face"), ("zuri", z, "face"), ("kai", k, "face"), ("sunny", su, "face"),
                        ("noor", no, "face"), ("note_z", nz["zuri"].point, "prop"), ("note_k", nz["kai"].point, "prop"),
                        ("note_s", nz["sunny"].point, "prop"),
                        ("horn", lambda fr, no=no: no.item_point("right", fr), "prop")])
    h["b1_take"] = [8, 20, 34, 48, 70]


def shot_b2(st, s, bd, h):
    """Beat 2: close on Zuri's note block on white wool, a rising riff, tilt up to her face; Steve crosses behind."""
    f0, f1 = s.frame_start, s.frame_end
    z = _put(st, bd, "zuri", "zuri", f0)
    h["b2_notes"] = bd.notes["zuri"].song(z, f0 + 2, count=6, every=9, camera=s)
    steve = _p(st, "steve", f0=f0)
    pts = bd.v.paths["bandstand_steve_cross"]
    steve.place(f0, pts[0], 0.0)
    steve.walk(f0 + 8, pts, speed=1.6)
    steve.look_at(f0 + 8, z, ease=8)
    st.use(s, z, steve)
    st.hero(s, "zuri", z)
    cam = bd.cameras["b2"]
    _cam(s, cam)
    s.focus(z.head, at_s=s.film.seconds(f0 + 28))
    bd.lights(st, s, scale=1.0)
    _zone(h, s, f0 + 8, [("note", bd.notes["zuri"].point, "prop"), ("wool", (-8.02, 2.5, 0.5), "wide")])
    _zone(h, s, f0 + 24, [("zuri", z, "head"), ("steve", steve, "frame")])
    _zone(h, s, f1, [("zuri", z, "face"), ("steve", steve, "frame")])


def shot_b3(st, s, bd, h):
    """Beat 3: past Steve's soft shoulder, Kai's note block on gold, focus pulls up to Kai's face."""
    f0, f1 = s.frame_start, s.frame_end
    steve = _put(st, bd, "steve", "steve_kai", f0, look=bd.A["note_kai_target"])
    k = _put(st, bd, "kai", "kai", f0)
    bd.notes["kai"].song(k, f0 + 4, count=4, every=12, camera=s)
    st.use(s, k, steve)
    st.hero(s, "kai", k)
    cam = bd.cameras["b3"]
    _cam(s, cam)
    s.focus(k.head, at_s=s.film.seconds(f0 + 24))
    bd.lights(st, s, scale=1.0)
    gold = (-8.02, 1.5, 0.75)                                        # the gold block's front face, upper half

    def shoulder(fr, p=steve):                                       # the outer edge of his left arm
        from mathutils import Vector
        yaw = p.yaw_at(fr)
        left = Vector((math.cos(yaw), math.sin(yaw), 0.0))
        return p.pos_at(fr) + left * 0.5 + Vector((0.0, 0.0, 1.3))

    for f in (f0 + 8, f1):
        _zone(h, s, f, [("kai", k, "face"), ("gold_face", gold, "prop"), ("note", bd.notes["kai"].point, "prop"),
                        ("steve_shoulder", shoulder, "info")])


def shot_b4(st, s, bd, h):
    """Beat 4: the static wide, Sunny's one note, Zuri and Kai turn to him and back; Steve below the stage."""
    f0, f1 = s.frame_start, s.frame_end
    z = _put(st, bd, "zuri", "zuri", f0)
    k = _put(st, bd, "kai", "kai", f0)
    su = _put(st, bd, "sunny", "sunny", f0)
    bd.tap("zuri", z, f0 - 4, camera=s)
    bd.tap("sunny", su, f0 + 6, camera=s)
    sp = _up(bd.A["sunny"], 1.6)
    for p in (z, k):
        p.look_at(f0 + 12, sp, ease=6)
        p.look_at(f0 + 44, _up(bd.A["note_%s_target" % p.name], 0.0), ease=6)
    steve = _put(st, bd, "steve", "steve_foot", f0)
    fp = bd.A["steve_foot"]
    steve.look_at(f0, (fp[0] - 0.6, fp[1] + 0.3, fp[2]), ease=0)
    st.use(s, z, k, su, steve)
    _cam(s, bd.cameras["b4"])
    bd.lights(st, s, scale=1.0)
    _zone(h, s, f0 + 20, [("zuri", z, "head"), ("kai", k, "head"), ("sunny", su, "face"), ("steve", steve, "frame"),
                          ("note_s", bd.notes["sunny"].point, "prop")])


def shot_b5(st, s, bd, h):
    """Beat 5: close on the totem turning on the pedestal, the camera rises and pulls back to the whole bandstand;
    Alex places the last lantern once the north post is in the frame."""
    from engine import music

    f0, f1 = s.frame_start, s.frame_end
    cam = bd.cameras["b5"]
    t = bd.totem(f0, f1 + 1, face=cam["pos"])
    st.cast[t.name] = t
    a = _put(st, bd, "alex", "alex_post", f0)
    music.hold(a, "lantern", frame=f0)
    fp = f0 + int(round(cam["place_at"] * (f1 - f0)))
    bd.last_lantern.place(fp, player=a)
    a.hold(None, frame=fp + 1)
    h["b5_place"] = fp
    st.use(s, t, a)
    st.hero(s, "totem", t.sprite)
    _cam(s, cam)
    bd.lights(st, s, scale=1.0)
    post = bd.A["last_lantern_target"]
    _zone(h, s, f0 + 2, [("totem", t, "prop")])
    _zone(h, s, fp, [("lantern", post, "prop"), ("alex", a, "head"), ("jukebox", bd.A["jukebox_top_target"], "wide"),
                     ("postS", (-7.5, -2.5, 3.2), "wide")])
    _zone(h, s, f1, [("lantern", post, "prop"), ("alex", a, "head"), ("totem", t, "wide"),
                     ("postS", (-7.5, -2.5, 3.2), "wide")])
    h["b5_take"] = [2, int(0.35 * (f1 - f0)), fp - f0 - 1, fp - f0 + 3, f1 - f0]


def shot_b6(st, s, bd, h):
    """Beat 6: the dolly along the line beside the stage, each act held out to the lens; Steve at the end with
    nothing, looking down at his empty hand."""
    from engine import music

    f0, f1 = s.frame_start, s.frame_end
    cam = bd.cameras["b6"]
    acts = (("zuri", "note_block"), ("noor", "goat_horn"), ("alex", "music_disc_cat"), ("sunny", "pumpkin"))
    cast = []
    for i, (w, item) in enumerate(acts, 1):
        p = _put(st, bd, w, "line_%d" % i, f0)
        music.hold(p, item, frame=f0)
        y = bd.A["line_%d" % i][1]
        music.present(p, f0, f1, (cam["pos"][0], y + 1.0, cam["pos"][2]), ease=0)
        cast.append(p)
    steve = _put(st, bd, "steve", "line_5", f0)
    sp = bd.A["line_5"]
    hand = (sp[0] - 0.75, sp[1] + 0.25, sp[2] + 1.05)              # his empty right hand, held out low before him
    music.present(steve, f0 + 6, f1, hand, ease=8)
    steve.look_at(f0 + 8, hand, ease=8)                              # ... and he looks down at it
    st.use(s, steve, *cast)
    _cam(s, cam, focus=cast[0].item(frame=f0))
    # rack the focus along the line, act by act, as the dolly passes each (frames where the camera is level)
    frames = []
    for i, p in enumerate(cast + [steve]):
        yi = bd.A["line_%d" % (i + 1)][1] + 1.0
        f = min(range(f0, f1 + 1), key=lambda fr: abs(_cam_at(s, cam, fr).y - yi))
        frames.append(f)
        if i:
            s.focus(p.head if p is steve else p.item(frame=f0), at_s=s.film.seconds(max(f0 + 1, f - 8)))
    bd.lights(st, s, scale=1.0)
    for i, (p, f) in enumerate(zip(cast + [steve], frames)):
        items = [(p.name, p, "head")]
        if p is not steve:
            items.append((p.name + "_item", p.item(frame=f0), "prop"))
        _zone(h, s, f, items)
    h["b6_take"] = [f - f0 for f in frames]


def shot_wide_gold(st, s, bd, h):
    """The whole bandstand at golden hour (the beat 22 framing), everybody on it."""
    _stage_wide(st, s, bd, h, scale=1.0)


def _stage_wide(st, s, bd, h, scale):
    f0 = s.frame_start
    z = _put(st, bd, "zuri", "zuri", f0)
    k = _put(st, bd, "kai", "kai", f0)
    su = _put(st, bd, "sunny", "sunny", f0)
    no = _put(st, bd, "noor", "ring_noor", f0)
    a = _put(st, bd, "alex", "ring_alex", f0)
    bd.tap("zuri", z, f0 + 2, camera=s)
    bd.tap("kai", k, f0 + 3, camera=s)
    bd.tap("sunny", su, f0 + 4, camera=s)
    steve = _put(st, bd, "steve", "steve_jukebox", f0)
    t = bd.totem(f0, s.frame_end + 1, face=bd.cameras["b22"]["pos"])
    st.cast[t.name] = t
    st.use(s, steve, t, z, k, su, no, a)
    _cam(s, bd.cameras["b22"])
    bd.lights(st, s, scale=scale)


def _note_close(st, s, bd, h, who, cam):
    f0 = s.frame_start
    p = _put(st, bd, who, who, f0)
    n = bd.tap(who, p, f0 + 1, camera=s)
    h["notes_" + who] = n
    st.use(s, p)
    st.hero(s, who, p)
    _cam(s, bd.cameras[cam])
    bd.lights(st, s, scale=1.0)


def shot_notes_zuri(st, s, bd, h):
    """Proof: Zuri's note block (white wool: guitar) played once."""
    _note_close(st, s, bd, h, "zuri", "note_zuri")


def shot_notes_kai(st, s, bd, h):
    """Proof: Kai's note block (gold: bells) played once."""
    _note_close(st, s, bd, h, "kai", "note_kai")


def shot_notes_sunny(st, s, bd, h):
    """Proof: Sunny's note block (pumpkin: didgeridoo) played once."""
    _note_close(st, s, bd, h, "sunny", "note_sunny")


def shot_totem(st, s, bd, h):
    """Proof: the totem turning on the pedestal (3 tiles, a second apart)."""
    f0 = s.frame_start
    cam = bd.cameras["b5"]
    t = bd.totem(f0, s.frame_end + 1, face=cam["pos"])
    st.cast[t.name] = t
    st.use(s, t)
    _cam(s, cam, moving=False)
    bd.lights(st, s, scale=1.0)


def shot_held(st, s, bd, h):
    """Proof: block items held as the game draws them (gold block, pumpkin, note block), no gesture."""
    from engine import music

    f0 = s.frame_start
    cam = bd.cameras["held"]
    cast = []
    for (w, item), y in zip((("kai", "gold_block"), ("sunny", "pumpkin"), ("zuri", "note_block")), (1.9, 1.05, 0.2)):
        p = _p(st, w, f0=f0)
        spot = (-10.2, y, bd.A["line_1"][2])
        p.place(f0, spot, -math.pi / 2.0 - 0.25)
        music.hold(p, item, frame=f0)
        p.look_at(f0, cam["pos"], ease=0)
        cast.append(p)
    st.use(s, *cast)
    _cam(s, cam, focus=cast[1].item(frame=f0))
    bd.lights(st, s, scale=1.0)


def shot_horn(st, s, bd, h):
    """Proof: Noor raises the goat horn to her face (players toot)."""
    from engine import music

    f0 = s.frame_start
    no = _put(st, bd, "noor", "noor", f0)
    music.hold(no, "goat_horn", frame=f0)
    no.toot(f0 + 4, s.frame_end)
    st.use(s, no)
    st.hero(s, "noor", no)
    _cam(s, bd.cameras["horn"], focus=no.head)
    bd.lights(st, s, scale=1.0)


# ----------------------------------------------------------------------------------------------------
# night (beats 7, 8, 17-24)
# ----------------------------------------------------------------------------------------------------
def _lane_zones(h, s, bd, kai, steve, frames):
    lan = bd.A["lane_lantern_target"]
    for f in frames:
        nt = bd.A["lane_note_target"]
        items = [("lantern_top", (lan[0], lan[1], lan[2] + 0.3), "frame"),
                 ("lantern_foot", (lan[0], lan[1], lan[2] - 0.3), "frame"),
                 ("note_block", (nt[0] + 0.52, nt[1], nt[2]), "frame"), ("steve", steve, "frame")]
        if kai is not None:
            items.insert(0, ("kai", kai, "head"))
        _zone(h, s, f, items)


def shot_lane(st, s, bd, h):
    """Beat 7: from Kai's doorstep, Steve sprinting across the lane to his door (zombie left out of the proof)."""
    f0 = s.frame_start
    kai = _put(st, bd, "kai", "lane_kai", f0)
    steve = _p(st, "steve", f0=f0)
    pts = bd.v.paths["lane_home"]
    steve.place(f0, pts[0], math.pi)
    end = steve.walk(f0, pts, sprint=True)
    kai.look_at(f0 + 6, steve, ease=6)
    for f in range(f0 + 12, min(end, s.frame_end), 6):
        kai.look_at(f, steve, ease=5)
    bd.v.door_open("house_e", end - 8)
    bd.v.door_open("house_e", end + 4, open=False)
    st.use(s, kai, steve)
    _cam(s, bd.cameras["lane"])
    bd.lights(st, s, scale=NIGHT_TORCHES)
    kick = float(os.environ.get("MUSIC_KICK", "0") or 0)
    if kick > 0:
        bd.kicker(st, s, bd.A["lane_kicker_target"], watts=kick)
    _lane_zones(h, s, bd, kai, steve, [f0 + 38, f0 + 44])
    h["lane_take"] = [6, 14, 22, 30, 42]


def shot_lane17(st, s, bd, h):
    """Beat 17: the same camera, Kai gone, Steve sprinting back toward the square holding the disc."""
    from engine import music

    f0 = s.frame_start
    steve = _p(st, "steve", f0=f0)
    pts = bd.v.paths["lane_to_square"]
    steve.place(f0, pts[0], 0.0)
    music.hold(steve, "music_disc_11", frame=f0)
    steve.walk(f0, pts, sprint=True)
    st.use(s, steve)
    _cam(s, bd.cameras["lane"])
    bd.lights(st, s, scale=NIGHT_TORCHES)
    _lane_zones(h, s, bd, None, steve, [f0 + 26])


def shot_doorstep(st, s, bd, h):
    """Proof: the doorstep dressing (lantern, gold block, note block) with Kai, from the lane camera."""
    f0 = s.frame_start
    kai = _put(st, bd, "kai", "lane_kai", f0)
    st.use(s, kai)
    _cam(s, bd.cameras["lane"])
    bd.lights(st, s, scale=NIGHT_TORCHES)


def shot_b8(st, s, bd, h):
    """Beat 8: over Steve's shoulder, Alex pops the disc out of the playing jukebox; it turns above it; Steve's
    head follows it, then turns away to the dark end of the square; focus from the disc to his profile."""
    f0, f1 = s.frame_start, s.frame_end
    cam = bd.cameras["b8"]
    z = _put(st, bd, "zuri", "zuri_watch", f0, look=bd.A["jukebox_top_target"])
    k = _put(st, bd, "kai", "kai_watch", f0, look=bd.A["jukebox_top_target"])
    a = _put(st, bd, "alex", "alex_eject", f0, look=bd.A["jukebox_top_target"])
    steve = _put(st, bd, "steve", "steve_watch", f0, look=bd.A["jukebox_top_target"])
    fe = f0 + 14
    bd.jukebox.play(f0 - 30, fe, disc="music_disc_cat", camera=s)
    item = bd.jukebox.eject(fe, player=a, disc="music_disc_cat", camera=s, until=f1 + 1)
    st.cast[item.name] = item
    steve.look_at(fe + 2, item.root, ease=6)
    fa = fe + 34
    steve.face(fa, bd.A["steve_away_target"], ease=20)              # he turns away (body and head)
    steve.look_at(fa, bd.A["steve_away_target"], ease=16)
    st.use(s, steve, item, z, k, a)
    _cam(s, cam, focus=item.sprite)
    s.focus(steve.head, at_s=s.film.seconds(fa + 4))
    bd.lights(st, s, scale=NIGHT_TORCHES)
    bd.kicker(st, s, bd.A["steve_turn_kicker_target"], watts=30.0)     # the lamp post he turns toward, cheated
                                                                    # closer: a key on his turned face
    h["b8"] = [fe + 10 - f0]
    _zone(h, s, fe + 10, [("disc", item, "prop"), ("jukebox_top", (-6.5, 0.5, 2.02), "prop"), ("alex", a, "head"),
                          ("steve", steve, "frame"), ("zuri", z, "frame"), ("kai", k, "frame")])
    _zone(h, s, f1, [("steve", steve, "head"), ("disc", item, "frame")])
    h["b8_take"] = [6, fe + 4 - f0, fe + 12 - f0, fa + 2 - f0, f1 - f0]


def shot_jukebox(st, s, bd, h):
    """Proof: the jukebox playing (notes every 24 frames) and Alex ejecting the disc: 4 tiles (the establishing
    camera that shows the jukebox's slot)."""
    f0 = s.frame_start
    a = _put(st, bd, "alex", "alex_eject", f0, look=bd.A["jukebox_top_target"])
    notes = bd.jukebox.play(f0, f0 + 60, disc="music_disc_cat", camera=s)
    fe = f0 + 56
    item = bd.jukebox.eject(fe, player=a, disc="music_disc_cat", camera=s, until=s.frame_end + 1)
    st.cast[item.name] = item
    st.use(s, a, item)
    _cam(s, bd.cameras["jukebox"])
    bd.lights(st, s, scale=NIGHT_TORCHES)
    k = int(notes[1] - f0)
    land = item.land_frame - f0
    h["jukebox"] = [k + 3, int(fe - f0) + 4, int(fe - f0) + 9, land + 8]
    h["jukebox_item"] = item


def shot_discs_drop(st, s, bd, h):
    """Proof: disc 11 and cat as dropped items (11 on the gold pedestal, cat on the jukebox), close."""
    from engine import mobs

    f0 = s.frame_start
    cam = bd.cameras["discs_drop"]
    d11 = mobs.make_dropped_item("music_disc_11", name="proof_disc_11")
    d11.place(f0, bd.pedestal_top)
    d11.face(f0 + 20, cam["pos"])
    d11.animate(f0, s.frame_end + 1)
    cat = mobs.make_dropped_item("music_disc_cat", name="proof_disc_cat")
    cat.place(f0, (bd.A["jukebox_target"][0], bd.A["jukebox_target"][1], 2.0))
    cat.face(f0 + 20, cam["pos"])
    cat.animate(f0, s.frame_end + 1)
    for d in (d11, cat):
        st.cast[d.name] = d
    st.use(s, d11, cat)
    _cam(s, cam)
    bd.lights(st, s, scale=NIGHT_TORCHES)


def shot_discs_hero(st, s, bd, h):
    """Proof: disc 11 and cat as close-up hero props (music.hero_item), upright, faces to the lens, in front of the
    jukebox in the lantern light."""
    from engine import music

    cam = bd.cameras["discs_hero"]
    for k, (disc, dy) in enumerate((("music_disc_11", -0.2), ("music_disc_cat", 0.25))):
        ob = music.hero_item(disc, collection=bd.collection)
        ob.name = "proof_hero_%s" % disc
        ob.location = (-7.75, 0.5 + dy * 1.3, 2.32 + 0.06 * k)
        ob.rotation_euler = (0.0, 0.0, math.atan2(cam["pos"][0] - ob.location[0], -(cam["pos"][1] - ob.location[1])))
        ob.scale = (0.36, 0.36, 0.36)
        h.setdefault("hero_obs", []).append(ob)
    _cam(s, cam)
    bd.lights(st, s, scale=NIGHT_TORCHES)


def shot_meadow_disc(st, s, bd, h):
    """Proof (beat 16): the disc a skeleton-killed creeper drops (music.creeper_disc), on the moonlit meadow, from
    ground level: dropped ON the killing blow, landing, turning and bobbing."""
    from engine import music

    f0 = s.frame_start
    feet = (0.7, 36.4, bd.v.ground(0.7, 36.4))
    d = music.creeper_disc(feet, f0 + 4, disc="music_disc_11", seed=5, world=bd.v, until=s.frame_end + 1,
                           name="proof_creeper_disc", face=bd.cameras["meadow_disc"]["pos"])
    st.cast[d.name] = d
    st.use(s, d)
    cam = dict(bd.cameras["meadow_disc"])
    rest = tuple(d.rest_pos)
    cam.update(target=(rest[0], rest[1], rest[2] + 0.2), focus=(rest[0], rest[1], rest[2] + 0.25))
    _cam(s, cam)                                         # aimed where it comes to rest (DroppedItem.rest_pos)
    bd.lights(st, s, scale=NIGHT_TORCHES)
    h["meadow_disc"] = [5, 10, d.land_frame - f0 + 2, d.land_frame - f0 + 30]


def shot_b18(st, s, bd, h):
    """Beat 18: medium three-shot from the front: Steve walks on from the wing (path wing_to_three) and stops
    between Sunny and Noor; Sunny looks at the arrows for one beat and back to the jukebox."""
    from engine import music

    f0, f1 = s.frame_start, s.frame_end
    jt = bd.A["jukebox_top_target"]
    su = _put(st, bd, "sunny", "three_sunny", f0, look=jt)
    no = _put(st, bd, "noor", "three_noor", f0, look=jt)
    steve = _p(st, "steve", f0=f0)
    music.hold(steve, "music_disc_11", frame=f0)
    pts = bd.v.paths["bandstand_wing_to_three"][2:]                 # the part of the walk-on the camera sees
    steve.place(f0, pts[0], math.pi)
    end = steve.walk(f0, pts, speed=1.6)
    steve.look_at(end, jt, ease=8)
    sp = bd.A["three_steve"]
    su.look_at(end + 4, (sp[0], sp[1], sp[2] + 1.2), ease=6)        # to the arrows (chest height) ...
    su.look_at(end + 20, jt, ease=6)                                # ... and back to the jukebox
    st.use(s, su, no, steve)
    st.hero(s, "steve", steve)
    _cam(s, bd.cameras["b18"], focus=steve.head)
    bd.lights(st, s, scale=NIGHT_TORCHES)
    h["b18_end"] = end
    _zone(h, s, min(f1, end + 8), [("sunny", su, "head"), ("steve", steve, "head"), ("noor", no, "head")])


def shot_b19(st, s, bd, h):
    """Beat 19: from behind and above Steve walking from three_steve to the jukebox, the disc raised; Alex steps
    aside to ring_alex; Kai, Zuri, Sunny, Noor in the half circle beyond the jukebox (ring_*) watching him come."""
    from engine import music

    f0, f1 = s.frame_start, s.frame_end
    names = ("kai", "zuri", "sunny", "noor")
    four = [_put(st, bd, n, "ring_" + n, f0) for n in names]
    steve = _put(st, bd, "steve", "three_steve", f0)
    music.hold(steve, "music_disc_11", frame=f0)
    music.present(steve, f0, f1, _up(bd.A["jukebox_top_target"], 0.9), ease=0)      # the disc in his raised hand
    steve.walk(f0 + 4, [bd.A["three_steve"], bd.A["steve_jukebox"]], speed=1.3)
    for p in four:
        p.look_at(f0, steve, ease=0)
        for f in range(f0 + 8, f1, 8):
            p.look_at(f, steve, ease=6)
    a = _put(st, bd, "alex", "alex", f0, look=steve)
    a.walk(f0 + 10, [bd.A["alex"], bd.A["ring_alex"]], speed=1.2)
    st.use(s, steve, a, *four)
    _cam(s, bd.cameras["b19"])
    bd.lights(st, s, scale=NIGHT_TORCHES)
    for f in (f0 + 2, f0 + 30, f1):
        _zone(h, s, f, [(n, p, "face") for n, p in zip(names, four)] + [("alex", a, "frame"), ("steve", steve, "frame")])


def shot_b20(st, s, bd, h):
    """Beat 20: from across the jukebox, disc 11 held straight at the lens, Alex's cat beside it; then the insert
    and the first note."""
    from engine import music

    f0, f1 = s.frame_start, s.frame_end
    cam = bd.cameras["b20"]
    steve = _put(st, bd, "steve", "steve_jukebox", f0)
    music.hold(steve, "music_disc_11", frame=f0)
    steve.look_at(f0, bd.A["jukebox_top_target"], ease=0)
    fi = f0 + 44
    music.present(steve, f0, fi - 8, cam["pos"], ease=0)
    a = _put(st, bd, "alex", "alex_beside", f0)
    music.hold(a, "music_disc_cat", frame=f0)
    a.look_at(f0, steve, ease=0)
    music.present(a, f0, f1, cam["pos"], ease=0)
    bd.jukebox.insert(fi, player=steve, disc="music_disc_11", camera=s, until=f1 + 400)
    st.use(s, steve, a)
    st.hero(s, "disc 11", steve.item(frame=f0))
    _cam(s, cam, focus=steve.item(frame=f0))
    bd.lights(st, s, scale=NIGHT_TORCHES)
    _zone(h, s, f0 + 20, [("disc11", steve.item(frame=f0), "prop"), ("cat", a.item(frame=f0), "prop"),
                          ("steve", steve, "frame")])
    h["b20_disc"] = steve.item(frame=f0)


def shot_b21(st, s, bd, h):
    """Beat 21: the jukebox sharp in front, notes rising, push past it to Steve stiff beside it."""
    f0, f1 = s.frame_start, s.frame_end
    steve = _put(st, bd, "steve", "steve_jukebox", f0, look=bd.A["jukebox_top_target"])
    bd.jukebox.play(f0 - 10, f1 + 1, disc="music_disc_11", camera=s)
    steve.look_at(f0 + 26, _up(bd.A["ring_kai"], 1.6), ease=20)      # slowly from the jukebox to the others
    st.use(s, steve)
    _cam(s, bd.cameras["b21"])
    bd.lights(st, s, scale=NIGHT_TORCHES)
    _zone(h, s, f0 + 4, [("jukebox_top", (-6.5, 0.5, 2.02), "prop"), ("steve", steve, "frame")])
    _zone(h, s, f1, [("steve", steve, "head")])


def _six(st, bd, s, f0, look=None):
    """Beats 22-24: Steve at steve_jukebox, Alex, Kai, Zuri, Sunny, Noor at ring_<name>."""
    jt = bd.A["jukebox_top_target"] if look is None else look
    out = {n: _put(st, bd, n, "ring_" + n, f0, look=jt) for n in ("alex", "kai", "zuri", "sunny", "noor")}
    out["steve"] = _put(st, bd, "steve", "steve_jukebox", f0, look=jt)
    return out


def shot_b22(st, s, bd, h):
    """Beat 22: the locked-off frontal wide, six players still, all facing the jukebox."""
    f0, f1 = s.frame_start, s.frame_end
    six = _six(st, bd, s, f0)
    bd.jukebox.play(f0 - 10, f1 + 1, disc="music_disc_11", camera=s)
    st.use(s, *six.values())
    _cam(s, bd.cameras["b22"])
    bd.lights(st, s, scale=NIGHT_TORCHES)
    _zone(h, s, f0 + 20, [(n, p, "head") for n, p in six.items()] + [
        ("postN", (-7.5, 3.5, 3.3), "wide"), ("postS", (-7.5, -2.5, 3.3), "wide"),
        ("jukebox_top", (-6.5, 0.5, 2.02), "prop")])


def shot_b23(st, s, bd, h):
    """Beat 23: Kai's slow step and head turn to Steve, then Zuri, Sunny, Noor, Alex in turn; Steve looks at the
    jukebox, then at them."""
    f0, f1 = s.frame_start, s.frame_end
    six = _six(st, bd, s, f0)
    kai, steve = six["kai"], six["steve"]
    kai.walk(f0 + 6, [bd.A["ring_kai"], bd.A["kai_step"]], speed=0.8)
    kai.look_at(f0 + 8, steve, ease=10)
    for i, n in enumerate(("zuri", "sunny", "noor", "alex")):
        six[n].look_at(f0 + 26 + 7 * i, steve, ease=7)
    steve.look_at(f0 + 52, _up(bd.A["ring_zuri"], 1.6), ease=10)
    bd.jukebox.play(f0 - 10, f1 + 1, disc="music_disc_11", camera=s)
    st.use(s, *six.values())
    st.hero(s, "kai", kai)
    _cam(s, bd.cameras["b23"], focus=kai.head)
    bd.lights(st, s, scale=NIGHT_TORCHES)
    _zone(h, s, f0 + 4, [(n, p, "head") for n, p in six.items()])
    _zone(h, s, f1, [(n, p, "face") for n, p in six.items() if n != "steve"] + [("steve", steve, "head")])
    h["b23"] = [4, f1 - f0]
    h["b23_take"] = [4, 20, 36, 52, f1 - f0]


def shot_b24(st, s, bd, h):
    """Beat 24: Steve centre stage, the totem held out to the lens, the empty pedestal below; the pull back
    reveals the five others clapping (fast crouches)."""
    from engine import music

    f0, f1 = s.frame_start, s.frame_end
    cam = bd.cameras["b24"]
    six = _six(st, bd, s, f0)
    steve = six["steve"]
    steve.place(f0, bd.A["steve_jukebox"], bd.yaw["steve_jukebox"])
    steve.look_at(f0, cam["pos"], ease=0)
    music.hold(steve, "totem_of_undying", frame=f0)
    music.present(steve, f0, f1, cam["pos"], ease=0)
    for i, n in enumerate(("zuri", "kai", "sunny", "noor", "alex")):
        six[n].look_at(f0, steve, ease=0)
        music.clap(six[n], f0 + 30 + 2 * i, count=int((f1 - f0 - 34) / 4))
    bd.jukebox.play(f0 - 10, f1 + 1, disc="music_disc_11", camera=s)
    st.use(s, *six.values())
    st.hero(s, "totem", steve.item(frame=f0))
    _cam(s, cam, focus=steve.item(frame=f0))
    s.focus(steve.head, at_s=s.film.seconds(f0 + 40))
    bd.lights(st, s, scale=NIGHT_TORCHES)
    ped = (-8.5, -0.5, 2.0)
    _zone(h, s, f0 + 2, [("totem", steve.item(frame=f0), "prop"), ("steve", steve, "face"), ("pedestal", ped, "wide")])
    _zone(h, s, f1, [(n, p, "head") for n, p in six.items()] + [("pedestal", ped, "wide"),
                                                                  ("totem", steve.item(frame=f0), "prop")])
    h["b24"] = [2, f1 - f0]
    h["b24_take"] = [2, 30, 60, 75, f1 - f0]


def shot_wide_night(st, s, bd, h):
    """The whole bandstand at night under its lanterns (the beat 22 framing)."""
    _stage_wide(st, s, bd, h, scale=NIGHT_TORCHES)


def shot_clap(st, s, bd, h):
    """Proof: the applause (clap: fast crouches), 4 consecutive-ish tiles."""
    from engine import music

    f0 = s.frame_start
    cast = [_put(st, bd, n, k, f0) for n, k in (("kai", "ring_kai"), ("zuri", "ring_zuri"), ("sunny", "ring_sunny"))]
    for i, p in enumerate(cast):
        p.look_at(f0, bd.cameras["clap"]["pos"], ease=0)
        music.clap(p, f0 + 2 + i, count=6)
    st.use(s, *cast)
    _cam(s, bd.cameras["clap"])
    bd.lights(st, s, scale=NIGHT_TORCHES)


BUILDERS = {name: globals()["shot_" + name] for name, _sky, _secs, _off in SHOTS}


def _overrides(bd):
    """MUSIC_CAMS / MUSIC_ANCHORS (framing work)."""
    cams = os.environ.get("MUSIC_CAMS")
    if cams:
        for k, d in json.loads(cams).items():
            bd.cameras.setdefault(k, {}).update({a: (tuple(b) if isinstance(b, list) else b) for a, b in d.items()})
    anc = os.environ.get("MUSIC_ANCHORS")
    if anc:
        for k, p in json.loads(anc).items():
            old = bd.A[k]
            bd.A[k] = (p[0], p[1], p[2] if len(p) > 2 else old[2])
            if len(p) > 3:
                bd.yaw[k] = p[3]


def build(scene, sky="gold", res=(540, 960), samples=16, threads=2, only=None):
    """The village with the bandstand and the lane, every shot of SHOTS filmed under `sky` (only those, if `only`
    lists names). Returns dict(film, stage, village, band, frames, h)."""
    from engine import look, music, shots, village
    from films.lookdev import Stage

    _EMPTY.clear()
    look.setup_render(scene, res=res, samples=samples, threads=threads)
    v = village.build_village(scene, seed=1, edit=music.crammys_set)
    bd = music.band(v)
    _overrides(bd)
    sk = Stage.build_sky(scene, SKIES[sky])
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, sk)
    h = dict(sky=sky)
    frames = {}
    for name, ssky, secs, offs in SHOTS:
        if ssky != sky or (only is not None and name not in only):
            continue
        s = st.shot(name, secs)
        BUILDERS[name](st, s, bd, h)
        offs = offs if offs is not None else h[name]
        frames[name] = [s.frame_start + o for o in offs]
        if name + "_take" in h:
            frames[name + "_take"] = [s.frame_start + o for o in h[name + "_take"]]
    for ob in h.get("hero_obs", []):                     # the hero props are seen in their own shot only
        hs = [x for x in film.shots if x.name == "discs_hero"][0]
        for f, hide in ((film.frame_start, True), (hs.frame_start, False), (hs.frame_end + 1, True)):
            st.key(ob, "hide_render", f, hide)
            st.key(ob, "hide_viewport", f, hide)
    st.finish()
    return dict(film=film, stage=st, village=v, band=bd, frames=frames, h=h)


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


def _env_res():
    r = os.environ.get("MUSIC_RES")
    if r:
        w, hh = r.lower().split("x")
        return int(w), int(hh)
    return 540, 960


def render(names, sky):
    """Render the named proofs of one sky to out/test/music_<name>.png. Returns (built, reports)."""
    import bpy
    from PIL import Image, ImageDraw

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    t0 = time.time()
    res = _env_res()
    samples = int(os.environ.get("MUSIC_SAMPLES", "16"))
    need = sorted({sh for n in names for sh in PROOFS[n]})
    built = build(scene, sky, res=res, samples=samples, only=need)
    film = built["film"]
    print("[music proof] %s built in %.1f s" % (sky, time.time() - t0), flush=True)
    os.makedirs(OUT, exist_ok=True)
    tag = os.environ.get("MUSIC_TAG", "")
    reports = {}
    for name in names:
        path = os.path.join(OUT, "music_%s%s.png" % (name, tag))
        t = time.time()
        if name in ENDS:
            tiles = [(sh, [x for x in film.shots if x.name == sh][0].frame_end) for sh in PROOFS[name]]
        elif name in TAKES:
            sh = TAKES[name]
            tiles = [(sh, f) for f in built["frames"][sh + "_take"]]
        elif name in ("cams_gold", "cams_night"):
            tiles = [(sh, built["frames"][sh][0]) for sh in PROOFS[name]]
        else:
            tiles = [(sh, f) for sh in PROOFS[name] for f in built["frames"][sh]]
        heroes = [ob for _l, obs in built["stage"].heroes.get(tiles[0][0], []) for ob in obs]
        if name not in SHEETS:
            sh, f = tiles[0]
            _render(scene, film, f, path)
            reports[name] = _check(scene, film, f, path, name, heroes=heroes)
        else:
            r = scene.render
            full = (r.resolution_x, r.resolution_y)
            W, H = TILE if res[0] >= TILE[0] else res
            r.resolution_x, r.resolution_y = W, H
            ims = []
            for i, (sh, f) in enumerate(tiles):
                p = os.path.join(OUT, "music_%s_t%d.png" % (name, i))
                _render(scene, film, f, p)
                if i == 0:
                    reports[name] = _check(scene, film, f, p, name + ":" + sh, heroes=heroes)
                ims.append(("%s f%d" % (sh, f), Image.open(p).convert("RGB")))
                os.remove(p)
            r.resolution_x, r.resolution_y = full
            cols = min(len(ims), 5)
            rows = (len(ims) + cols - 1) // cols
            sheet = Image.new("RGB", (W * cols, (H + 18) * rows), (20, 20, 20))
            d = ImageDraw.Draw(sheet)
            for i, (label, im) in enumerate(ims):
                x, y = (i % cols) * W, (i // cols) * (H + 18)
                sheet.paste(im, (x, y + 18))
                d.text((x + 4, y + 3), label, fill=(255, 255, 255))
            sheet.save(path)
        print("[music proof] %-11s %s -> %s  %.1f s" % (name, tiles, path, time.time() - t), flush=True)
    return built, reports


def main(argv):
    """Command line: proof names (see the module docstring)."""
    names = [a for a in argv if not a.startswith("-")] or ["wide_gold"]
    unknown = [n for n in names if n not in PROOFS]
    if unknown:
        print("unknown proof names %s; known: %s" % (unknown, sorted(PROOFS)))
        return 2
    failed = 0
    for sky in ("gold", "night"):
        group = [n for n in names if SKY_OF[PROOFS[n][0]] == sky]
        if group:
            _built, reports = render(group, sky)
            failed += sum(len(r["failed"]) for r in reports.values())
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
