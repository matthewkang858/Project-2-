"""Six Seconds: 65.46 narrated seconds (1571 frames), 23 sentences, 25 shots, two skies. Told by a piglin brute.

    "In this bastion, I'm the only one who doesn't like gold. ... So today I'm staring at an ingot. Six seconds.
     Nothing."     (stories/piglin.json: the story, the picture of every beat, the risks and their fallbacks)

This file is the lead director's: the narration (the clock of the film), the skies, the shot plan and build().
The pictures are made by five sequence files, one location (or one device) each, one function per shot (the
contract, the set, the places, the shared cameras, the cast and the helpers: films/sixseconds_common.py):

    films/sixseconds_gate.py    gt01 gt03 gt04 gt17 gt18 gt19     the guard landing, THE GATE FRAME, the corridor
    films/sixseconds_row.py     rw02 rw21 rw22 rw23               the gold wall: the ingot row, the six-second stare
    films/sixseconds_pit.py     pt05 pt06 pt07 pt08 pt09 pt10 pt20    the boots, the pit, the barter, the axe, smoke
    films/sixseconds_bridge.py  br11 br12 br13 br14 br15          the second bastion: the bridge and the pillar
    films/sixseconds_flash.py   fl16_bridge fl16_treasure fl16_home   "a full stack of worlds": three flash cuts

    $TTS tools/narrate.py sixseconds --check             # the voice is spoken and committed: narration/sixseconds.*
    $BPY -m tools.sixseconds_timeline [--check|--json]   # the shot plan with frames and words; caption proof
    $BPY -m tools.sixseconds_shots render --shots pt09_axe --frame 580 --zones    # stills of single shots (one
                                                         #   build per sky; 540x960, 16 samples by default)
    $BPY -m tools.sixseconds_shots tiles --sky wastes; ... --sky soul; ... sheet   # one tile per shot
    $BPY -m render sixseconds --still 12.0 --zones       # one frame through render.py
    $BPY -m render sixseconds --frames pt09_axe --res 270x480 --samples 7 --threads 2    # one shot as a preview
                                                         #   (each sequence its own sample count: _common)
    $BPY -m render sixseconds --frames all --max-seconds 240    # FINAL frames: this film's final quality is
                                                         #   540x960 at 16 samples (set in build(); never --res)

THE VOICE IS COMMITTED (am_michael, speed 1.0; the last three lines at 0.9, as The Hello's ending). Changing a word,
a pause, the voice or a speed below makes narration/sixseconds.json stale (build stops) and, once spoken again,
moves every cut after it: do not, unless the orchestrator says so. Spoken three times by the lead: 66.79 s with
the first pauses; then the pauses shortened (the story's holds kept: "Mostly gravel", the hold after "didn't come",
"Six seconds", "Nothing") and the ending slowed, 65.25 s; then the pause after "Six seconds." tuned so that
THE SIX-SECOND STARE is exact: rw21 + rw22 = 144 frames from the first frame of "So today I'm staring at an ingot"
to the cut into "Nothing" (the story's timing device; asserted in timeline()). 65.46 s, inside the 58-66 s asked;
no word of the script was cut. Pronunciation checked (--phonemes): nothing respelled (bastion, ingot, ender, zero
are said right).

GUARDED BUILD: each sequence file is imported, and each shot function called, inside a guard (see STRICT below):
a broken file or shot prints "[sixseconds] !!! ..." and gets a stand-in; SIXSECONDS_STRICT=1 makes errors fatal.

THE EDIT (the story's devices, designed into the plan below)
  * THE RESET: on "ended" (pt10) the picture SNAPS to black and stays black to the cut into br11, 13 frames
    (0.54 s), with the caption "ended" held on the black (RESETS). br11 comes up out of black, cut 2 frames before
    "New". The flash cuts of beat 16 are snaps too (SNAPS: 2 black frames at the start of fl16_treasure and
    fl16_home): each world that ends goes to black.
  * THE FLASH CUTS: fl16_bridge starts 8 frames BEFORE "I" (in the silence after "can't": the first world is seen
    before it is named), fl16_treasure on "full", fl16_home on "worlds": 22 / 19 / 33 frames (0.92 / 0.79 / 1.38
    s), the last one longer because it is home and it settles into "I started waiting at the gate".
  * THE SIX-SECOND STARE: rw21 (58 frames) + rw22 (86) = 144 frames exactly; "Six seconds." is spoken in the first
    second of rw22, then 2.5 s of silence; the cut into rw23 lands 2 frames before "Nothing".
  * THE END: "Nothing." is held 2.0 s, then a PLAIN cut to black for the last 8 frames (END_BLACK; no caption on
    it: not the snap that meant a reset, this world does not end); the Reel then loops to frame 1.
  * RE-USED FRAMES (films/sixseconds_common.py CAMS): the gate frame gt03 / gt18 / gt19 (the 18 -> 19 cut is the
    pixel match cut: only the brute is gone; the story's fourth use, beat 23, is replaced by the story's own
    fallback, the reverse angle: the gate frame cannot give a face turning to the gateway behind him); the boot
    framing pt05 / br11 (BOOT_FRAME); the ingot row rw02 / rw21; the pit camera pt06 / pt20.

THE SKIES (two; each costs one more build, about 2 s, per render command that has work in it)
  "wastes"  nether_wastes: the dark red haze of the home bastion, of "the older version of the world" (gt19, pt20:
            it MUST be this one, gt19 is a match cut on gt18) and of the treasure corner (fl16_treasure: an
            enclosed corner, no fog in the frame: under any biome it renders the same; a third sky would cost a
            build for nothing). Every scouting still of the set was made under it.
  "soul"    soul_sand_valley (a bastion stands in the four nether biomes: the game's tag bastion_remnant): the
            fog and the void of the second bastion's world are TEAL. "New world, different bastion, same boots"
            reads on the first frame out of black; the brute under his lantern stands out against it; the flash
            cut fl16_bridge (teal) -> fl16_treasure (enclosed gold) -> fl16_home (red) shows three worlds, which is
            the story's risk for beat 16. Lighting of the subjects is unchanged (the fog starts at 10 blocks; the
            lanterns and the lava glow are the same). Compared side by side with nether_wastes on four bridge beats:
            out/test/sixseconds_scout_sky_*_soul_sand_valley.png against sixseconds_set_<beat>.png.
"""
import importlib
import os
import sys
import traceback
import types

from engine import narration, nether, shots
from films import sixseconds_common as SC

FPS = 24

# FIVE DIRECTORS EDIT FIVE FILES AT THE SAME TIME: a half-written sequence file must not stop the other four from
# building and scouting. So each sequence module is imported, and each shot function called, inside a guard: an
# error is printed loudly (module, shot, traceback) and that shot gets a plain stand-in (its location's camera, its
# lantern levels, nobody in it); the rest of the film builds. SIXSECONDS_STRICT=1 in the environment turns the guard
# off (the orchestrator's merge, the final render and the contact sheets of record run strict).
STRICT = os.environ.get("SIXSECONDS_STRICT", "") not in ("", "0")
SEQUENCE_FILES = {"gate": "films.sixseconds_gate", "row": "films.sixseconds_row", "pit": "films.sixseconds_pit",
                  "bridge": "films.sixseconds_bridge", "flash": "films.sixseconds_flash"}
BROKEN = {}        # sequence or shot name -> the error text (filled by build(); empty when everything built)


def _import(seq):
    """The module of one sequence (None, and the error in BROKEN, when it does not import and STRICT is off)."""
    try:
        return importlib.import_module(SEQUENCE_FILES[seq])
    except Exception:                                         # SyntaxError, ImportError, anything at import time
        if STRICT:
            raise
        BROKEN[seq] = traceback.format_exc()
        # render.py lists a film's sources from sys.modules: keep the broken file in that list under a stand-in
        # module, so that the edit which repairs it is seen as a change of the film
        stand = types.ModuleType(SEQUENCE_FILES[seq] + "_broken")
        stand.__file__ = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      SEQUENCE_FILES[seq].split(".")[-1] + ".py")
        sys.modules[stand.__name__] = stand
        print("[sixseconds] !!! SEQUENCE %s DOES NOT IMPORT: its shots get stand-ins\n%s" % (seq, BROKEN[seq]),
              file=sys.stderr)
        return None


# the stand-in of a shot whose function is missing or raised: its location's camera and lantern levels, nobody in it
STAND_IN = {"gate": ("gate", "home"), "row": ("ingot_row", "home"), "pit": ("pit", "pit"),
            "bridge": ("bridge_shoulder", "bridge"), "flash": None}
FLASH_STAND_IN = {"fl16_bridge": ("flash_bridge", "bridge"), "fl16_treasure": ("flash_treasure", "treasure"),
                  "fl16_home": ("flash_home", "home")}

# The narration: stories/piglin.json word for word, one entry per sentence (164 words). Pauses are after the
# sentence, voice to voice (default 0.35 s). Spoken: 49.2 s; with these pauses the film is 65.46 s = 1571 frames.
NARRATION = {
    "voice": "am_michael", "speed": 1.0,
    "tail": 2.35,                                   # "Nothing." held 2.0 s, then the last 8 frames black (END_BLACK)
    "lines": [
        {"text": "In this bastion, I'm the only one who doesn't like gold.", "id": "b01", "pause": 0.45},
        {"text": "My brothers will stare at one ingot for six seconds.", "id": "b02", "pause": 0.4},
        {"text": "Somebody has to guard the place.", "id": "b03", "pause": 0.65},      # the gate frame is learned
        {"text": "One day, a player ran in.", "id": "b04", "pause": 0.35},
        {"text": "He wore golden boots, so my brothers thought he was family.", "id": "b05", "pause": 0.6},
        {"text": "He dug a hole, and they fell in.", "id": "b06", "pause": 0.65},      # the third piglin lands
        {"text": "He threw gold, and they threw back ender pearls.", "id": "b07", "pause": 0.35},
        {"text": "Mostly gravel.", "id": "b08", "pause": 0.9},                         # a full beat on the pile
        {"text": "I hit him with my axe.", "id": "b09", "pause": 0.25},                # cut on the knock-back
        # "ended": the snap to black + 0.2 s = 13 black frames with the caption held, then "New world" out of black
        {"text": "He turned into smoke, and the whole world ended.", "id": "b10", "pause": 0.2},
        {"text": "New world, different bastion, same boots.", "id": "b11", "pause": 0.45},
        {"text": "Every world has a bastion, and every bastion has me.", "id": "b12", "pause": 0.4},
        {"text": "He hid on a pillar and threw gold at me.", "id": "b13", "pause": 0.35},
        {"text": "I looked at it for zero seconds.", "id": "b14", "pause": 0.45},
        {"text": "I can wait, and he can't.", "id": "b15", "pause": 0.8},              # the first flash before "I"
        {"text": "I ended a full stack of worlds.", "id": "b16", "pause": 0.9},        # the home flash settles
        {"text": "I started waiting at the gate.", "id": "b17", "pause": 0.45},
        {"text": "One day, he didn't come.", "id": "b18", "pause": 1.1},               # hold a full second: the turn
        {"text": "He found an older version of the world, from before they added me.", "id": "b19", "pause": 0.5},
        {"text": "In that bastion, everyone likes gold.", "id": "b20", "pause": 0.6},
        # the ending a tenth slower (The Hello's last lines too); the pause after "Six seconds." makes rw21 + rw22
        # exactly 144 frames (tuned on the spoken voice: 2.47 s gave 140, 2.645 gives 144)
        {"text": "So today I'm staring at an ingot.", "id": "b21", "pause": 0.4, "speed": 0.9},
        {"text": "Six seconds.", "id": "b22", "pause": 2.645, "speed": 0.9},
        {"text": "Nothing.", "id": "b23", "speed": 0.9},
    ],
}

# The skies (engine.nether.Stage: preset "nether" + the biome whose fog the game shows; keys nether.SKY_KEYS).
# render.py builds the film once per sky that has work. Two entries, each for a reason (module docstring):
SKIES = {
    "wastes": dict(preset="nether", biome="nether_wastes"),       # home, the older world, the treasure corner
    "soul": dict(preset="nether", biome="soul_sand_valley"),      # the second bastion's world: the bridge
}

# The shot plan: (shot = the function's name, beat, sequence file, sky, where it starts). A start is a sentence id
# (the cut is Sentence.cut: two frames before its first word), (sentence id, word): a cut inside the sentence before
# that word (nar.cut_before: never inside the word before it), or (sentence id, frames): that many frames after
# (negative: before) the sentence's own cut.
SHOTS = [
    ("gt01_landing", 1, "gate", "wastes", "b01"),
    ("rw02_ingots", 2, "row", "wastes", "b02"),
    ("gt03_guard", 3, "gate", "wastes", "b03"),           # THE GATE FRAME (1st)
    ("gt04_runin", 4, "gate", "wastes", "b04"),
    ("pt05_boots", 5, "pit", "wastes", "b05"),            # THE BOOT FRAMING (1st)
    ("pt06_dig", 6, "pit", "wastes", "b06"),              # THE PIT CAMERA (1st); the pit is dug from here ...
    ("pt07_pearl", 7, "pit", "wastes", "b07"),
    ("pt08_gravel", 8, "pit", "wastes", "b08"),
    ("pt09_axe", 9, "pit", "wastes", "b09"),
    ("pt10_smoke", 10, "pit", "wastes", "b10"),           # ... to here; RESET: black from "ended" to the cut
    ("br11_boots", 11, "bridge", "soul", "b11"),          # THE BOOT FRAMING (2nd), out of black
    ("br12_blocks", 12, "bridge", "soul", "b12"),
    ("br13_pillar", 13, "bridge", "soul", "b13"),
    ("br14_zero", 14, "bridge", "soul", "b14"),
    ("br15_wait", 15, "bridge", "soul", "b15"),
    ("fl16_bridge", 16, "flash", "soul", ("b16", -8)),     # three flash cuts: 8 frames before "I" ...
    ("fl16_treasure", 16, "flash", "wastes", ("b16", "full")),    # ... snap, on "full" ...
    ("fl16_home", 16, "flash", "wastes", ("b16", "worlds")),      # ... snap, on "worlds"
    ("gt17_waits", 17, "gate", "wastes", "b17"),
    ("gt18_nocome", 18, "gate", "wastes", "b18"),         # THE GATE FRAME (2nd): he waits in the gateway
    ("gt19_older", 19, "gate", "wastes", "b19"),          # THE GATE FRAME (3rd): the match cut, he is gone
    ("pt20_likes", 20, "pit", "wastes", "b20"),           # THE PIT CAMERA (2nd); the older world, no brute
    ("rw21_stare", 21, "row", "wastes", "b21"),           # THE INGOT ROW (2nd); the stare starts here ...
    ("rw22_six", 22, "row", "wastes", "b22"),             # ... 144 frames ...
    ("rw23_nothing", 23, "row", "wastes", "b23"),         # ... to this cut; the reverse angle (beat 23's fallback)
]
RESETS = {"pt10_smoke": "ended"}       # the picture snaps to black ON this word and stays black to the end of the
#                                        shot, the caption held on it (the encoder's dip; nothing is rendered less)
SNAPS = {"fl16_treasure": 2, "fl16_home": 2}     # black on the first N frames of these shots (between flash cuts)
END_BLACK = 8      # the plain cut to black: the last 8 frames (0.33 s), after the 2.0 s hold on "Nothing."


def _start(nar, start):
    """(Sentence, cut frame) of a SHOTS start."""
    if isinstance(start, str):
        sent = nar.sentence(start)
        return sent, sent.cut
    sid, what = start
    sent = nar.sentence(sid)
    if isinstance(what, str):
        return sent, nar.cut_before(nar.word(what, sentence=sent))
    return sent, sent.cut + int(what)


def timeline(nar):
    """The shot plan with its frames, from the spoken narration: [sixseconds_common.ShotInfo] in film order."""
    cuts = [_start(nar, start) for _n, _b, _q, _s, start in SHOTS]
    assert cuts[0][1] == 1, "the first shot starts the film"
    ends = [c - 1 for _s, c in cuts[1:]] + [nar.frames]
    rows = []
    for (name, beat, seq, sky, _start_), (sent, a), b in zip(SHOTS, cuts, ends):
        assert b >= a, "shot %s is empty" % name
        assert seq in SC.PREFIX and name.startswith(SC.PREFIX[seq]), "shot %s: prefix of %s" % (name, seq)
        assert sky in SKIES, "shot %s: no sky %s" % (name, sky)
        mine = [w for w in nar.words if a <= w.frame <= b]
        words = [(w.caption, w.frame) for w in mine]
        if mine:
            # no word across a cut: a word ends inside its shot, or (running speech, the flash cuts) in the very
            # frame the next word starts in, which is then the first frame of the next shot and shows that word
            last = mine[-1]
            assert last.frame_end <= b or (last.frame_end == b + 1 and nar.words[last.index + 1].frame == b + 1), \
                "a word straddles the end of %s" % name
        row = SC.ShotInfo(name=name, beat=beat, sequence=seq, sky=sky, sentence=sent, frame_start=a, frame_end=b,
                          frames=b - a + 1, seconds=(b - a + 1) / float(nar.fps), words=words)
        if name in RESETS:
            row.black = (nar.at(RESETS[name], sentence=sent), b)
        elif name in SNAPS:
            row.black = (a, a + SNAPS[name] - 1)
        rows.append(row)
    rows[-1].black = (nar.frames - END_BLACK + 1, nar.frames)
    for prev, nxt in zip(rows, rows[1:]):
        prev.next, nxt.prev = nxt.name, prev.name
    by = {r.name: r for r in rows}
    stare = by["rw21_stare"].frames + by["rw22_six"].frames
    assert stare == SC.STARE_FRAMES, "the six-second stare is %d frames, not %d" % (stare, SC.STARE_FRAMES)
    return rows


def build(scene, sky=None):
    """Build the film with `sky` active (None: the first of SKIES):
    {"film", "captions", "narration", "stage", "context"}."""
    # 1. the voice: stops here (NarrationError) if narration/sixseconds.json was not spoken from NARRATION
    nar = narration.load(__name__, NARRATION, fps=FPS)
    print(nar.summary())
    rows = timeline(nar)

    # 2. the set, the stage (it builds the active sky), the shared context
    bas = SC.build_set(scene)
    film = shots.Film(scene, fps=FPS)
    st = nether.Stage(scene, film, bas, skies=SKIES, sky=sky)
    C = SC.Six(st, nar, {r.name: r for r in rows})

    # 3. every shot of the plan, in order, tagged with its sky
    for r in rows:
        s = st.shot(r.name, nar.seconds(r.frames), sky=r.sky)
        assert (s.frame_start, s.frame_end) == (r.frame_start, r.frame_end), (r, s.frame_start, s.frame_end)
        C.shots[r.name] = s
    assert film.shots[-1].frame_end == nar.frames

    # 4. the pictures: each shot's function from its sequence file, IN TIMELINE ORDER (characters are keyed in
    #    frame order); particles never live across a change of sequence. A sequence that does not import, or a shot
    #    function that raises, gets the stand-in (see STRICT above) and is named in BROKEN.
    BROKEN.clear()
    modules = {seq: _import(seq) for seq in SEQUENCE_FILES}
    before = None
    for r in rows:
        if before is not None and r.sequence != before:
            C.time_jump(r.frame_start)
        s = C.shots[r.name]
        fn = getattr(modules[r.sequence], r.name, None) if modules[r.sequence] is not None else None
        try:
            if fn is None:
                raise AttributeError("films/sixseconds_%s.py has no function %s" % (r.sequence, r.name))
            fn(st, s, C, nar)
        except Exception:
            if STRICT:
                raise
            BROKEN[r.name] = traceback.format_exc()
            print("[sixseconds] !!! SHOT %s (%s) FAILED: it gets a stand-in\n%s" % (r.name, r.sequence,
                                                                                  BROKEN[r.name]), file=sys.stderr)
            cam, light = STAND_IN[r.sequence] or FLASH_STAND_IN[r.name]
            C.cam(s, cam, handheld=0.004)
            C.lights(s, light)
        before = r.sequence
    if BROKEN:
        print("[sixseconds] !!! %d part(s) built as stand-ins: %s" % (len(BROKEN), ", ".join(BROKEN)),
              file=sys.stderr)

    # 5. the encoder's black: the reset, the snaps between the flash cuts, the end; then hide everybody outside
    #    their shots
    for r in rows:
        if r.black is not None:
            a, b = r.black
            st.dip(a, out=0, hold=b - a + 1, back=0)
    st.finish()

    # 6. this film's final quality (a measured study): 540x960 at 16 samples, upscaled to 1080x1920 at encode
    scene.render.resolution_x, scene.render.resolution_y = SC.FINAL_RES
    scene.cycles.samples = SC.FINAL_SAMPLES

    # 7. the captions: one word at a time; a word never stays on past ANY cut (the flash cuts included); "ended"
    #    stays on the black of the reset (it holds until the cut into br11)
    caps = nar.captions(cuts=[r.frame_start for r in rows[1:]])
    return {"film": film, "captions": caps, "narration": nar, "stage": st, "context": C}
