"""Proof stills for engine/music.py: the Crammys bandstand, the lane, note blocks, the jukebox, discs, the totem and
the held items in the REAL village (the edit hook, films.lookdev.Stage, engine.look), 540x960, 16 samples, 2 threads.

    $BPY -m engine.music stills wide_gold notes           # -> out/test/music_<name>.png (one build per sky and call;
    $BPY -m tools.music_proof wide_night jukebox           #    2-4 names per call stay under 300 s)
    MUSIC_RES=270x480 MUSIC_SAMPLES=8 $BPY -m tools.music_proof cams_gold      # quick framing tests

Names (sky): wide_gold (gold) wide_night (night) notes (gold: the three hero note blocks played, 3 tiles) jukebox
(night: notes rising, the disc popping out, 4 tiles) discs (night: disc 11 and cat held to the lens, and as dropped
items) totem (gold: spinning on the pedestal, 3 tiles) held (gold: gold block, pumpkin, note block, white wool held)
horn (gold: Noor raising the goat horn) doorstep (night: Kai's doorstep from the lane camera) cams_gold (beats 1-6,
6 tiles at 270x480) cams_night (beats 7, 8, 17-24, 9 tiles) clap (night: the applause, 4 tiles). Every name is
followed by tools.palette_check's report (stills; for sheets the first tile). Strips and sheets render each tile at
270x480 with motion blur on.
"""
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "test")
TILE = (270, 480)

# the skies of the proof (and the film's suggestion): see engine/music.py SKIES
from engine.music import SKIES  # noqa: E402

GOLD, NIGHT = SKIES["gold"], SKIES["night"]

# shot name -> (sky, seconds, still offset from the shot's first frame; None = a sheet of its own offsets)
SHOTS = [
    ("b1", "gold", 2.0, 10), ("b2", "gold", 2.0, 14), ("b3", "gold", 2.0, 12), ("b4", "gold", 2.0, 10),
    ("b5", "gold", 2.0, 4), ("b6", "gold", 2.0, 20), ("wide_gold", "gold", 1.5, 10), ("notes_zuri", "gold", 1.0, 6),
    ("notes_kai", "gold", 1.0, 6), ("notes_sunny", "gold", 1.0, 6), ("totem", "gold", 4.0, None),
    ("held", "gold", 1.5, 16), ("horn", "gold", 1.5, 16),
    ("lane", "night", 2.0, 18), ("lane17", "night", 2.0, 30), ("b8", "night", 3.0, 30), ("b18", "night", 1.5, 18),
    ("b19", "night", 2.0, 20), ("b20", "night", 2.0, 16), ("b21", "night", 2.0, 20), ("b22", "night", 2.0, 20),
    ("b23", "night", 2.0, 20), ("b24", "night", 2.0, 20), ("wide_night", "night", 1.5, 12),
    ("jukebox", "night", 4.0, None), ("discs_drop", "night", 1.5, 20), ("doorstep", "night", 1.0, 8),
    ("clap", "night", 1.5, None), ("discs_hero", "night", 1.0, 8), ("meadow_disc", "night", 4.0, None),
]
SKY_OF = {name: sky for name, sky, _s, _o in SHOTS}
# proof name -> the shots it is made of (several = a sheet of tiles)
PROOFS = {
    "wide_gold": ["wide_gold"], "wide_night": ["wide_night"], "notes": ["notes_zuri", "notes_kai", "notes_sunny"],
    "jukebox": ["jukebox"], "discs": ["b20", "discs_drop", "discs_hero"], "meadow_disc": ["meadow_disc"], "totem": ["totem"], "held": ["held"], "horn": ["horn"],
    "doorstep": ["doorstep"], "clap": ["clap"],
    "cams_gold": ["b1", "b2", "b3", "b4", "b5", "b6"],
    "cams_night": ["lane", "b8", "lane17", "b18", "b19", "b20", "b21", "b22", "b23", "b24"],
}
# the last frames of the moving cameras (the first frames are in cams_gold / cams_night)
ENDS = {"ends_gold": ["b1", "b5", "b6"], "ends_night": ["b21", "b24"]}
PROOFS.update(ENDS)
SHEETS = ("ends_gold", "ends_night", "notes", "discs", "totem", "jukebox", "clap", "cams_gold", "cams_night", "meadow_disc")


def _cam(s, cam, focus=None, moving=False):
    s.lens(cam["lens"], cam.get("fstop", 4.0))
    if moving and cam.get("pos1") is not None:
        s.move(cam["pos"], cam["target"], cam["pos1"], cam.get("target1", cam["target"]))
    elif moving and cam.get("target1") is not None:
        s.move(cam["pos"], cam["target"], cam["pos"], cam["target1"])
    else:
        s.move(cam["pos"], cam["target"])
    s.focus(focus if focus is not None else cam.get("focus", cam["target"]))


_EMPTY = {}


def _p(st, name, skin=None, f0=None):
    """The player `name` (built on first use); f0 = the shot's first frame: whatever he held in an earlier shot is
    put away there (Player.hold keys from a frame on, in film order)."""
    from engine import players

    p = players.add_player(st, name, skin or name)
    if f0 is not None and _EMPTY.get(name) != f0:
        _EMPTY[name] = f0
        for hand in ("right", "left"):
            if p.holding_at(hand, f0) is not None:
                p.hold(None, hand=hand, frame=f0)
    return p


def _band(st, bd, s, f0, who=("zuri", "kai", "sunny", "noor", "alex"), spots=None, look=None):
    """Place the performers at their spots (spots = {who: anchor key}) facing their way."""
    out = []
    for w in who:
        p = _p(st, w, f0=f0)
        key = (spots or {}).get(w, w)
        p.place(f0, bd.A[key], bd.yaw.get(key, 0.0))
        if look is not None:
            p.look_at(f0, look, ease=0)
        out.append(p)
    return out


# ----------------------------------------------------------------------------------------------------
# golden hour (beats 1-6)
# ----------------------------------------------------------------------------------------------------
def shot_b1(st, s, bd, h):
    """Beat 1: Steve sharp in front, the three tapping behind him, Noor with the horn."""
    from engine import music

    f0 = s.frame_start
    steve = _p(st, "steve", f0=f0)
    steve.place(f0, bd.A["steve_front"], bd.yaw["steve_front"])
    cast = _band(st, bd, s, f0, who=("zuri", "kai", "sunny", "noor"))
    z, k, su, no = cast
    bd.tap("zuri", z, f0 + 2, camera=s)
    bd.tap("kai", k, f0 + 4, camera=s)
    bd.tap("sunny", su, f0 + 3, camera=s)
    music.hold(no, "goat_horn", frame=f0)
    no.toot(f0, s.frame_end)
    st.use(s, steve, *cast)
    st.hero(s, "steve", steve)
    _cam(s, bd.cameras["b1"], focus=steve.head, moving=True)
    bd.lights(st, s, scale=1.0)


def shot_b2(st, s, bd, h):
    """Beat 2: close on Zuri's note block on white wool, a rising riff (each tap one semitone up)."""
    f0 = s.frame_start
    (z,) = _band(st, bd, s, f0, who=("zuri",))
    z.look_at(f0, bd.A["note_zuri_target"], ease=0)
    h["b2_notes"] = bd.notes["zuri"].song(z, f0 + 2, count=5, every=8, camera=s)
    steve = _p(st, "steve", f0=f0)
    steve.place(f0, bd.A["steve_foot"], bd.yaw["steve_foot"])
    st.use(s, z, steve)
    st.hero(s, "zuri", z)
    _cam(s, bd.cameras["b2"], moving=True)
    bd.lights(st, s, scale=1.0)


def shot_b3(st, s, bd, h):
    """Beat 3: past Steve's soft shoulder, Kai's note block on gold."""
    f0 = s.frame_start
    steve = _p(st, "steve", f0=f0)
    steve.place(f0, bd.A["steve_kai"], bd.yaw["steve_kai"])
    steve.look_at(f0, bd.A["note_kai_target"], ease=0)
    (k,) = _band(st, bd, s, f0, who=("kai",))
    k.look_at(f0, bd.A["note_kai_target"], ease=0)
    bd.notes["kai"].song(k, f0 + 4, count=3, every=10, camera=s)
    st.use(s, k, steve)
    st.hero(s, "kai", k)
    _cam(s, bd.cameras["b3"])
    bd.lights(st, s, scale=1.0)


def shot_b4(st, s, bd, h):
    """Beat 4: the static wide, Sunny's one note, Zuri and Kai turn to him; Steve below the stage."""
    f0 = s.frame_start
    z, k, su = _band(st, bd, s, f0, who=("zuri", "kai", "sunny"))
    bd.tap("sunny", su, f0 + 2, camera=s)
    sp = bd.A["sunny"]
    for p in (z, k):
        p.look_at(f0 + 3, (sp[0], sp[1], sp[2] + 1.6), ease=5)
    steve = _p(st, "steve", f0=f0)
    steve.place(f0, bd.A["steve_foot"], bd.yaw["steve_foot"])
    fp = bd.A["steve_foot"]
    steve.look_at(f0, (fp[0] - 0.6, fp[1] + 0.4, fp[2]), ease=0)
    st.use(s, z, k, su, steve)
    _cam(s, bd.cameras["b4"])
    bd.lights(st, s, scale=1.0)


def shot_b5(st, s, bd, h):
    """Beat 5: close on the totem turning above the pedestal (the camera then rises and pulls back)."""
    from engine import music

    f0 = s.frame_start
    cam = bd.cameras["b5"]
    t = bd.totem(f0, s.frame_end + 1, face=cam["pos"])
    st.cast[t.name] = t
    st.use(s, t)
    a = _p(st, "alex", f0=f0)
    a.place(f0, bd.A["alex_post"], bd.yaw["alex_post"])
    a.look_at(f0, bd.set["last_lantern"], ease=0)
    music.hold(a, "lantern", frame=f0)
    bd.last_lantern.place(f0 + 30, player=a)
    a.hold(None, frame=f0 + 31)
    st.use(s, a)
    st.hero(s, "totem", t.sprite)
    _cam(s, cam, moving=True)
    bd.lights(st, s, scale=1.0)


def shot_b6(st, s, bd, h):
    """Beat 6: the line beside the stage, each act held out to the lens; Steve at the end with nothing."""
    from engine import music

    f0 = s.frame_start
    cam = bd.cameras["b6"]
    acts = (("zuri", "note_block"), ("noor", "goat_horn"), ("alex", "music_disc_cat"), ("sunny", "pumpkin"))
    cast = []
    for i, (w, item) in enumerate(acts, 1):
        p = _p(st, w, f0=f0)
        p.place(f0, bd.A["line_%d" % i], bd.yaw["line_%d" % i])
        music.hold(p, item, frame=f0)
        y = bd.A["line_%d" % i][1]
        music.present(p, f0, s.frame_end, (cam["pos"][0], y + 1.0, cam["pos"][2]))   # where the dolly passes
        cast.append(p)
    steve = _p(st, "steve", f0=f0)
    steve.place(f0, bd.A["line_5"], bd.yaw["line_5"])
    sp = bd.A["line_5"]
    steve.look_at(f0, (sp[0] - 0.5, sp[1] + 0.1, sp[2] + 0.9), ease=0)
    st.use(s, steve, *cast)
    _cam(s, cam, focus=cast[0].item(), moving=True)
    bd.lights(st, s, scale=1.0)


def shot_wide_gold(st, s, bd, h):
    """The whole bandstand at golden hour (the beat 22 framing), everybody on it."""
    _stage_wide(st, s, bd, h, scale=1.0)


def _stage_wide(st, s, bd, h, scale):
    f0 = s.frame_start
    cast = _band(st, bd, s, f0, who=("zuri", "kai", "sunny", "noor", "alex"))
    z, k, su, no, a = cast
    bd.tap("zuri", z, f0 + 2, camera=s)
    bd.tap("kai", k, f0 + 3, camera=s)
    bd.tap("sunny", su, f0 + 4, camera=s)
    steve = _p(st, "steve", f0=f0)
    steve.place(f0, bd.A["steve_center"], bd.yaw["steve_center"])
    t = bd.totem(f0, s.frame_end + 1, face=bd.cameras["b22"]["pos"])
    st.cast[t.name] = t
    st.use(s, steve, t, *cast)
    _cam(s, bd.cameras["b22"])
    bd.lights(st, s, scale=scale)


def _note_close(st, s, bd, h, who, cam):
    f0 = s.frame_start
    (p,) = _band(st, bd, s, f0, who=(who,))
    p.look_at(f0, bd.A["note_%s_target" % who], ease=0)
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
    _cam(s, cam)
    bd.lights(st, s, scale=1.0)
    h["totem"] = [6, 30, 54]


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
    _cam(s, cam, focus=cast[1].item())
    bd.lights(st, s, scale=1.0)


def shot_horn(st, s, bd, h):
    """Proof: Noor raises the goat horn to her face (players toot)."""
    from engine import music

    f0 = s.frame_start
    (no,) = _band(st, bd, s, f0, who=("noor",))
    music.hold(no, "goat_horn", frame=f0)
    no.toot(f0 + 4, s.frame_end)
    st.use(s, no)
    st.hero(s, "noor", no)
    _cam(s, bd.cameras["horn"], focus=no.head)
    bd.lights(st, s, scale=1.0)


# ----------------------------------------------------------------------------------------------------
# night (beats 7, 8, 17-24)
# ----------------------------------------------------------------------------------------------------
NIGHT_TORCHES = 1.3


def shot_lane(st, s, bd, h):
    """Beat 7: from Kai's doorstep, Steve sprinting across the lane to his door (zombie left out of the proof)."""
    f0 = s.frame_start
    kai = _p(st, "kai", f0=f0)
    kai.place(f0, bd.A["lane_kai"], bd.yaw["lane_kai"])
    steve = _p(st, "steve", f0=f0)
    pts = bd.v.paths["lane_home"]
    steve.place(f0, pts[0], math.pi)
    steve.walk(f0, pts, sprint=True)
    kai.look_at(f0 + 8, steve, ease=8)
    st.use(s, kai, steve)
    _cam(s, bd.cameras["lane"], focus=bd.A["lane_note_target"])
    bd.lights(st, s, scale=NIGHT_TORCHES, lane=1.0)


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
    _cam(s, bd.cameras["lane"], focus=bd.A["lane_note_target"])
    bd.lights(st, s, scale=NIGHT_TORCHES, lane=1.0)


def shot_doorstep(st, s, bd, h):
    """Proof: the doorstep dressing (lantern, gold block, note block) with Kai, from the lane camera."""
    f0 = s.frame_start
    kai = _p(st, "kai", f0=f0)
    kai.place(f0, bd.A["lane_kai"], bd.yaw["lane_kai"])
    st.use(s, kai)
    _cam(s, bd.cameras["lane"], focus=bd.A["lane_note_target"])
    bd.lights(st, s, scale=NIGHT_TORCHES, lane=1.0)


def shot_b8(st, s, bd, h):
    """Beat 8: over Steve's shoulder, Alex pops the disc out of the playing jukebox; it turns above it."""
    f0 = s.frame_start
    cast = _band(st, bd, s, f0, who=("zuri", "kai", "alex"),
                 spots={"zuri": "flank_n2", "kai": "flank_n3", "alex": "alex_eject"})
    a = cast[2]
    a.look_at(f0, bd.A["jukebox_top_target"], ease=0)
    steve = _p(st, "steve", f0=f0)
    steve.place(f0, bd.A["steve_watch"], bd.yaw["steve_watch"])
    steve.look_at(f0, bd.A["jukebox_top_target"], ease=0)
    bd.jukebox.play(f0 - 30, f0 + 10, disc="music_disc_cat", camera=s)
    item = bd.jukebox.eject(f0 + 12, player=a, disc="music_disc_cat", camera=s, until=s.frame_end + 1)
    st.cast[item.name] = item
    steve.look_at(f0 + 14, item.root, ease=6)
    st.use(s, steve, item, *cast)
    h["b8"] = item
    _cam(s, bd.cameras["b8"])
    bd.lights(st, s, scale=NIGHT_TORCHES)


def shot_jukebox(st, s, bd, h):
    """Proof: the jukebox playing (notes every 24 frames) and Alex ejecting the disc: 4 tiles."""
    f0 = s.frame_start
    (a,) = _band(st, bd, s, f0, who=("alex",), spots={"alex": "alex_eject"})
    a.look_at(f0, bd.A["jukebox_top_target"], ease=0)
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
    """Proof: disc 11 and cat as dropped items (11 on the stage floor, cat on the jukebox), close."""
    from engine import mobs

    f0 = s.frame_start
    cam = bd.cameras["discs_drop"]
    d11 = mobs.make_dropped_item("music_disc_11", name="proof_disc_11")
    d11.place(f0, bd.pedestal_top)                       # on the gold pedestal (the totem's place)
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

    f0 = s.frame_start
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
    """Beat 18: medium three-shot from the front of the stage: Sunny, Steve (arrived from the wing), Noor."""
    f0 = s.frame_start
    su, no = _band(st, bd, s, f0, who=("sunny", "noor"), spots={"sunny": "three_sunny", "noor": "three_noor"})
    steve = _p(st, "steve", f0=f0)
    steve.place(f0, bd.A["three_steve"], bd.yaw["three_steve"])
    su.look_at(f0, bd.A["jukebox_top_target"], ease=0)
    no.look_at(f0, bd.A["jukebox_top_target"], ease=0)
    steve.look_at(f0, bd.A["jukebox_top_target"], ease=0)
    sp = bd.A["three_steve"]
    su.look_at(f0 + 8, (sp[0], sp[1], sp[2] + 1.2), ease=6)          # to the arrows ...
    su.look_at(f0 + 26, bd.A["jukebox_top_target"], ease=6)          # ... and back to the jukebox
    st.use(s, su, no, steve)
    st.hero(s, "steve", steve)
    _cam(s, bd.cameras["b18"], focus=steve.head)
    bd.lights(st, s, scale=NIGHT_TORCHES)


def shot_b19(st, s, bd, h):
    """Beat 19: from behind and above Steve walking to the jukebox, the four in a half circle beyond it."""
    from engine import music

    f0 = s.frame_start
    four = _band(st, bd, s, f0, who=("zuri", "kai", "sunny", "noor"),
                 spots={"zuri": "half_1", "kai": "half_2", "sunny": "half_3", "noor": "half_4"})
    steve = _p(st, "steve", f0=f0)
    music.hold(steve, "music_disc_11", frame=f0)
    steve.place(f0, bd.A["steve_wing"], bd.yaw["steve_wing"])
    steve.walk(f0, [bd.A["steve_wing"], bd.A["steve_jukebox"]], speed=1.6)
    for p in four:
        p.look_at(f0, steve, ease=0)
    a = _p(st, "alex", f0=f0)
    a.place(f0, bd.A["alex"], bd.yaw["alex"])
    st.use(s, steve, a, *four)
    _cam(s, bd.cameras["b19"])
    bd.lights(st, s, scale=NIGHT_TORCHES)


def shot_b20(st, s, bd, h):
    """Beat 20: from across the jukebox, disc 11 held straight at the lens, Alex's cat beside it."""
    from engine import music

    f0 = s.frame_start
    cam = bd.cameras["b20"]
    steve = _p(st, "steve", f0=f0)
    steve.place(f0, bd.A["steve_jukebox"], bd.yaw["steve_jukebox"])
    music.hold(steve, "music_disc_11", frame=f0)
    steve.look_at(f0, cam["pos"], ease=0)
    music.present(steve, f0, s.frame_end, cam["pos"])
    a = _p(st, "alex", f0=f0)
    a.place(f0, bd.A["alex_beside"], bd.yaw["alex_beside"])
    music.hold(a, "music_disc_cat", frame=f0)
    music.present(a, f0, s.frame_end, cam["pos"])
    st.use(s, steve, a)
    st.hero(s, "disc 11", steve.item())
    _cam(s, cam, focus=steve.item())
    bd.lights(st, s, scale=NIGHT_TORCHES)


def shot_b21(st, s, bd, h):
    """Beat 21: the jukebox sharp in front, notes rising, Steve stiff beside it."""
    f0 = s.frame_start
    steve = _p(st, "steve", f0=f0)
    steve.place(f0, bd.A["steve_jukebox"], bd.yaw["steve_jukebox"])
    steve.look_at(f0, bd.A["jukebox_top_target"], ease=0)
    bd.jukebox.play(f0 - 10, s.frame_end + 1, disc="music_disc_11", camera=s)
    st.use(s, steve)
    _cam(s, bd.cameras["b21"], moving=True)
    bd.lights(st, s, scale=NIGHT_TORCHES)


def _all_flank(st, bd, s, f0):
    spots = {"zuri": "flank_n1", "kai": "flank_n2", "sunny": "flank_s2", "noor": "flank_s3", "alex": "flank_n3"}
    cast = _band(st, bd, s, f0, who=("zuri", "kai", "sunny", "noor", "alex"), spots=spots,
                 look=bd.A["jukebox_top_target"])
    steve = _p(st, "steve", f0=f0)
    steve.place(f0, bd.A["flank_s1"], bd.yaw["flank_s1"])
    steve.look_at(f0, bd.A["jukebox_top_target"], ease=0)
    return cast, steve


def shot_b22(st, s, bd, h):
    """Beat 22: the locked-off frontal wide, six players still, all facing the jukebox."""
    f0 = s.frame_start
    cast, steve = _all_flank(st, bd, s, f0)
    bd.jukebox.play(f0 - 10, s.frame_end + 1, disc="music_disc_11", camera=s)
    st.use(s, steve, *cast)
    _cam(s, bd.cameras["b22"])
    bd.lights(st, s, scale=NIGHT_TORCHES)


def shot_b23(st, s, bd, h):
    """Beat 23: from beside the jukebox along the row of faces; Kai's head turns to Steve."""
    f0 = s.frame_start
    cast, steve = _all_flank(st, bd, s, f0)
    kai = cast[1]
    kai.look_at(f0 + 4, steve, ease=8)
    bd.jukebox.play(f0 - 10, s.frame_end + 1, disc="music_disc_11", camera=s)
    st.use(s, steve, *cast)
    st.hero(s, "kai", kai)
    _cam(s, bd.cameras["b23"], focus=kai.head)
    bd.lights(st, s, scale=NIGHT_TORCHES)


def shot_b24(st, s, bd, h):
    """Beat 24: Steve centre stage, the totem held out to the lens, the empty pedestal below, the others clapping."""
    from engine import music

    f0 = s.frame_start
    cam = bd.cameras["b24"]
    steve = _p(st, "steve", f0=f0)
    steve.place(f0, bd.A["steve_center"], bd.yaw["steve_center"])
    music.hold(steve, "totem_of_undying", frame=f0)
    steve.look_at(f0, cam["pos"], ease=0)
    music.present(steve, f0, s.frame_end, cam["pos"])
    spots = {"zuri": "flank_n1", "kai": "flank_n2", "alex": "flank_n3", "sunny": "flank_s2", "noor": "flank_s3"}
    cast = _band(st, bd, s, f0, who=("zuri", "kai", "alex", "sunny", "noor"), spots=spots)
    for i, p in enumerate(cast):
        p.look_at(f0, steve, ease=0)
        music.clap(p, f0 + 2 + 2 * i, count=6)
    bd.jukebox.play(f0 - 10, s.frame_end + 1, disc="music_disc_11", camera=s)
    st.use(s, steve, *cast)
    st.hero(s, "totem", steve.item())
    _cam(s, cam, focus=steve.item(), moving=True)
    bd.lights(st, s, scale=NIGHT_TORCHES)


def shot_wide_night(st, s, bd, h):
    """The whole bandstand at night under its lanterns (the beat 22 framing)."""
    _stage_wide(st, s, bd, h, scale=NIGHT_TORCHES)


def shot_clap(st, s, bd, h):
    """Proof: the applause (clap: fast crouches), 4 consecutive-ish tiles."""
    f0 = s.frame_start
    from engine import music

    cast = _band(st, bd, s, f0, who=("zuri", "kai", "alex"),
                 spots={"zuri": "flank_n1", "kai": "flank_n2", "alex": "flank_n3"})
    for i, p in enumerate(cast):
        p.look_at(f0, bd.cameras["clap"]["pos"], ease=0)
        music.clap(p, f0 + 2 + i, count=6)
    st.use(s, *cast)
    _cam(s, bd.cameras["clap"])
    bd.lights(st, s, scale=NIGHT_TORCHES)
    h["clap"] = [1, 3, 4, 6]


BUILDERS = {name: globals()["shot_" + name] for name, _sky, _secs, _off in SHOTS}


def build(scene, sky="gold", res=(540, 960), samples=16, threads=2, only=None):
    """The village with the bandstand and the lane, every shot of SHOTS filmed under `sky` (only those, if `only`
    lists names). Returns dict(film, stage, village, band, frames, h)."""
    from engine import look, music, shots, village
    from films.lookdev import Stage

    _EMPTY.clear()
    look.setup_render(scene, res=res, samples=samples, threads=threads)
    v = village.build_village(scene, seed=1, edit=music.crammys_set)
    bd = music.band(v)
    sk = Stage.build_sky(scene, SKIES[sky])
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, sk)
    h = dict(sky=sky)
    frames = {}
    for name, ssky, secs, off in SHOTS:
        if ssky != sky or (only is not None and name not in only):
            continue
        s = st.shot(name, secs)
        BUILDERS[name](st, s, bd, h)
        offs = [off] if off is not None else h[name]
        frames[name] = [s.frame_start + o for o in offs]
    for ob in h.get("hero_obs", []):                     # the hero props are seen in their own shot only
        hs = [x for x in film.shots if x.name == "discs_hero"][0]
        for f, hide in ((film.frame_start, True), (hs.frame_start, False), (hs.frame_end + 1, True)):
            st.key(ob, "hide_render", f, hide)
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
        w, h = r.lower().split("x")
        return int(w), int(h)
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
