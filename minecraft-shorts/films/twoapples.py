"""Two Apples: narrated, 24 sentences, 24 shots, two skies. Told by a baby villager.

    "In this town, the player has an underground base. ... The player only needs one zombie. He kept the smaller
     one."     (stories/underground.json: the story, the picture of every beat, the risks and their fallbacks;
                SHOTLISTS.md section 2 has the same as a table)

This file is the lead director's: the narration (the clock of the film), the skies, the shot plan, the wall plan and
build(). The pictures are made by five sequence files, one place or chapter each, one function per shot (the contract,
the set, the places, the shared cameras, the cast, the light and the helpers: films/twoapples_common.py; the set
itself: films/twoapples_set.py on engine/underground.py):

    films/twoapples_square.py    sq01 sq02 sq03 sq20          the square at dusk: the stair mouth, the lip, the push,
                                                              the children round the well
    films/twoapples_evening.py   ev04 ev05 ev06               dad's bedroom (the red bed, the dusk window), the stairwell
    films/twoapples_turn.py      tu07 tu09 tu10 tu11 tu12     the hall from above, the lever, the blows, dad turns
    films/twoapples_cure.py      cu13 cu14 cu15 cu16 cu17 cu18 cu19    the potion, the one apple, the wall shuts,
                                                              five minutes, Mending, the follow, the wall behind him
    films/twoapples_box.py       bx08 bx21 bx22 bx23 bx24     the slot (twice), the flashback at the stair foot, the
                                                              kill, the box

    $TTS tools/narrate.py twoapples --check                   # the voice is spoken and committed: narration/twoapples.*
    $TTS tools/twoapples_narrate.py                           # (how it was spoken: tools/narrate.py's narrate(),
                                                              #   resumable under the 300 s limit; see below)
    $BPY -m tools.twoapples_timeline [--check|--json]         # the shot plan with frames and words; caption proof
    $BPY -m tools.twoapples_shots render --shots tu11_hard --frame 520 --zones      # stills of single shots (one
                                                              #   build per sky; 540x960, 16 samples by default)
    $BPY -m tools.twoapples_shots tiles --sky under; ... sheet   # one tile per shot -> out/test/twoapples_shots_sheet.png
    $BPY -m tools.twoapples_geo tu11_hard:520                 # heads, face pixels, angle to the lens, what blocks them
    $BPY -m tools.twoapples_palette 520                       # tools/palette_check on one frame at final quality
    $BPY -m render twoapples --still 12.0 --zones             # one frame through render.py
    $BPY -m render twoapples --frames tu10_hug --res 270x480 --samples 7 --threads 2    # one shot as a preview (each
                                                              #   sequence its own sample count: _common)
    $BPY -m render twoapples --frames all --max-seconds 240   # FINAL frames: this film's final quality is 540x960 at
                                                              #   16 samples (set in build(); never pass --res/--samples)

THE VOICE IS COMMITTED (am_michael, speed 1.0; the last line at 0.9, as the series' endings: the storyteller slows
down for the punchline). Pronunciation checked with `tools/narrate.py twoapples --phonemes`: every word is said right
as written (underground, downstairs, Hard, Mending, emerald, twenty, he'll): no respelling. Changing a word, a pause,
the voice or a speed below makes narration/twoapples.json stale (build stops) and, once spoken again, moves every cut
after it: do not, unless the orchestrator says so. Spoken through tools/twoapples_narrate.py (tools/narrate.py's own
narrate() with its two deterministic steps memoised on disk, so that it can be resumed under the command time limit:
one uninterrupted run takes more than 300 s on this machine; `$TTS tools/narrate.py twoapples --check` says
"current"). The voice is 49.7 s of speech (164 words, 3.3 words a second while speaking). The pauses were shaped once,
BEFORE anything was cut on them: first draft 66.7 s (over the 66 s limit), so every pause was shortened first and no
word was cut (the story's cut priorities were not needed); the long pauses stay where the story turns (comments).
Nobody has listened to it (no audio playback here): the pace was judged by measurement.

GUARDED BUILD: each sequence file is imported, and each shot function called, inside a guard (see STRICT below): a
broken file or shot prints "[twoapples] !!! ..." and gets a stand-in; TWOAPPLES_STRICT=1 makes every error fatal.

THE EDIT (the story's devices, designed into the plan below)
  * ONE SHOT PER BEAT, 24 shots, in one sentence each; the cut two frames before the sentence's first word
    (Sentence.cut). The sequences are by place and light, so a director owns a place: the square at dusk (4 shots),
    the house and the stairwell (3), the hall in front of dad's cell (5: the look down and dad's turning), the cure
    and the trade (7), the back corner, the stair foot and the box (5: everything the twist rests on, one director).
  * THE MIRROR: sq02 (the child at the lip) and bx24 (the baby zombie villager in the box) are one framing on two
    sides of the film: CAMS "lip" / "box" (films/twoapples_common.py), lens, stop, distance, eye height and the
    screen direction of the look identical.
  * THE WALL (WALL below): dad's back wall opens in tu09 (the lever), stays open through tu10-cu14 (the black
    doorway beside his robe), shuts in cu15 on "two" (the last word), and opens again from inside the box in bx24.
    build() checks it after every shot and forces the plan if a shot broke it.
  * THE SLOT TWICE: bx08 and bx21 are one camera (CAMS "slot"): with the hands and a green shape, then black.
  * NO DIP TO BLACK inside the film: the hard cut is the series' grammar; the flashback (bx22) is carried by the
    words "The night I came down" and the child seen as a villager again.
  * THE END: "He kept the smaller one." then the hold; the last 6 frames are black (END_BLACK: the story's "Cut to
    black"); the Reel then loops to frame 1.

THE LIGHT PLAN (SKIES below; the per-shot recipes are films/twoapples_common.py LIGHTS / BOOSTS / GLOWS, the set
builder's, each rendered and palette-checked, except the two the lead changed for the reveal)
  the square at dusk   "dusk"; the village's lamps x 1.3 and the mouth's torches (LIGHTS "square"; sq03 "push"); sq02
                       the mouth's two torches x 2.2 and MOUTH_GLOW 240 W below his face ("lip" + glow mouth_glow)
  dad's bedroom        "dusk" in the window and the gable pane; house_a's torches x 1.5, its own fill OFF, ROOM_COOL
                       45 W (LIGHTS "room" + glow room_cool): torch-lit, warm, the indigo in the window
  the stairwell        "dusk"; every underground torch at 1, no village light (LIGHTS "stairs")
  the hall             "under"; the baked block light at 0.45 of the game's (films/twoapples_set.py HALL_EMIT), the
                       hall's torches and lantern at 1, the hall's cool fill on (LIGHTS "hall"); tu07 DOWN_FILL 120 W;
                       cu13 COUNTER_BOUNCE 70 W + DAD_SIDE_FILL 10 W + the dad torch x 1.8; cu17 the dad torch x 1.6;
                       cu19 DAD_SIDE_FILL
  the corner, the stair foot, the box   "under", the hall's fill OFF (LIGHTS "box": it passes walls and would light the
                       box and the dark west aisle); bx08 the corner torch x 1.8 (on the hands, not the face: shade_face);
                       bx24 the slot strip 120 W and, from the wall's opening, the doorway glow 180 W (the lead's: the
                       engine's 6 W / 60 W left the reveal black, films/twoapples_common.py SLOT_STRIP_WATTS) and the
                       dad torch x 2.5
  Two skies only: no sky is seen from below the ground, and the square, the house and the stairwell are one dusk
  ("That evening"; sq20 "the square at the same dusk"). The neighbours that change sky (ev06 -> tu07, cu19 -> sq20 ->
  bx21) change place too: they are meant to read differently, and do (the stub's sheet, side by side).

THE LEAD'S SCOUTING AND WHAT IT FOUND (stills and numbers: films/twoapples_common.py SCOUTED and each shot's docstring)
  * the mirror sq02 / bx24 holds in the frame (eyes x 49 / y 44 against x 50 / y 46, 138 / 130 px, 27 / 32 degrees
    off the lens); the reveal's light was too dark and is raised (above).
  * MEASURED PROBLEMS FOR THE DIRECTORS: sq20 (the children invisible at 16 blocks, behind the well; the grown-up out
    only on the last frames: restage), bx24's pan (mush mid-pan, the baby out of the frame at its end, dad at the
    right edge), bx22 (the zombie stands from 11 frames in: stretch the walk), ev06 (fixed in the stub: the child
    started behind the lens), tu09 (the swing moved to "lever": the wall opens about "wall").
  * NOT LOOKED AT IN MOTION: nothing was previewed through render.py --frames; the stub's motion (push, bounce, runs,
    jump loop, the lever's pan, the drift, the slide, the swap behind the well, the box's pan) is the engine's and the
    set builder's numbers, checked on single frames only.
"""
import importlib
import os
import sys
import traceback
import types

from engine import narration, shots
from films import lookdev as L
from films import twoapples_common as TC

FPS = 24

# FIVE DIRECTORS EDIT FIVE FILES AT THE SAME TIME: a half-written sequence file must not stop the other four from
# building and scouting. So each sequence module is imported, and each shot function called, inside a guard: an error
# is printed loudly (module, shot, traceback) and that shot gets a plain stand-in (its location's camera and light,
# nobody in it); the rest of the film builds. TWOAPPLES_STRICT=1 in the environment turns the guard off (the
# orchestrator's merge, the final render and the contact sheets of record run strict).
STRICT = os.environ.get("TWOAPPLES_STRICT", "") not in ("", "0")
SEQUENCE_FILES = {"square": "films.twoapples_square", "evening": "films.twoapples_evening",
                  "turn": "films.twoapples_turn", "cure": "films.twoapples_cure", "box": "films.twoapples_box"}
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
        print("[twoapples] !!! SEQUENCE %s DOES NOT IMPORT: its shots get stand-ins\n%s" % (seq, BROKEN[seq]),
              file=sys.stderr)
        return None


# The narration: stories/underground.json word for word, one entry per sentence (164 words). Pauses are after the
# sentence, voice to voice (default 0.35 s). Spoken length 49.7 s; with these pauses (12.4 s), the lead 0.3 s and
# the tail 2.3 s the film is about 64.8 s. Long pauses where the story turns or the picture needs its time (comments).
NARRATION = {
    "voice": "am_michael", "speed": 1.0,
    "tail": 2.3,                                    # the last image holds two seconds after the last word, then the
    #                                                 last 6 frames are black (END_BLACK: the story's cut to black)
    "lines": [
        {"text": "In this town, the player has an underground base.", "id": "b01", "pause": 0.5},   # his head sinks
        {"text": "My dad got taken down there.", "id": "b02", "pause": 0.5},
        {"text": "The player walked into him until he was downstairs.", "id": "b03", "pause": 0.65},   # the drop
        {"text": "That evening, I jumped on dad's bed.", "id": "b04", "pause": 0.45},
        {"text": "Nobody told me to stop.", "id": "b05", "pause": 0.8},          # the locked hold: the story turns
        {"text": "So I went down to find him.", "id": "b06", "pause": 0.5},
        {"text": "It's a trading hall, and dad has the last tiny room.", "id": "b07", "pause": 0.4},
        {"text": "The player keeps one zombie down here.", "id": "b08", "pause": 0.55},
        {"text": "He pulls a lever, and dad's wall opens.", "id": "b09", "pause": 0.45},
        {"text": "The zombie runs in and hugs him.", "id": "b10"},
        {"text": "On Hard, we always turn.", "id": "b11", "pause": 0.45},
        {"text": "Dad goes green under his hat.", "id": "b12", "pause": 0.6},     # hold on the hat
        {"text": "The player throws a potion and feeds him a golden apple.", "id": "b13"},
        {"text": "He only ever brings one.", "id": "b14", "pause": 0.4},
        {"text": "I always hope he'll bring two.", "id": "b15", "pause": 0.65},  # the wall shuts on "two"
        {"text": "Dad shakes for five minutes.", "id": "b16", "pause": 0.45},
        {"text": "Then he's dad again, and Mending costs one emerald.", "id": "b17", "pause": 0.4},
        {"text": "Dad thinks the player saved him.", "id": "b18", "pause": 0.45},
        {"text": "He never looks behind him.", "id": "b19", "pause": 0.85},       # the hold on the seam: the turn
        {"text": "Babies grow up in twenty minutes.", "id": "b20", "pause": 0.9},  # the chase needs its time
        {"text": "I'm still small.", "id": "b21", "pause": 0.7},
        {"text": "The night I came down, the zombie found me first.", "id": "b22", "pause": 0.45},
        {"text": "The player only needs one zombie.", "id": "b23", "pause": 0.7},  # the poof, the look down
        # the last line a tenth slower: the storyteller slows down for the punchline (the series' endings)
        {"text": "He kept the smaller one.", "id": "b24", "speed": 0.9},
    ],
}

# The skies (films.lookdev.Stage: arguments of look.set_time / look.setup_compositor). render.py builds the film once
# per sky that has work. az = where the sun stands, degrees counter-clockwise from east. TWO entries, each for a
# reason (each costs one more build, 20-50 s on this machine, per render command that has work in it):
SKIES = {
    # the square, dad's house and the stairwell (sq01-03, ev04-06, sq20): the set's dusk (films/twoapples_set.py:
    # every scouting still of these places was made under exactly this sky). The sun just under the western houses
    # (azimuth 187, elevation 5): the sky over the well orange-pink at the horizon, indigo with the first stars above;
    # b01 / b20 look west into it; the square is lit by its lamps and the glow of the mouth; the bedroom's window and
    # gable pane show the indigo. ONE dusk for the whole story ("That evening": the story changed "night" to
    # "evening" so that the film has one dusk sky, and sq20 is "the square at the same dusk").
    "dusk": dict(preset="dusk", az=187.0, el=5.0, bloom=1.3, grade="warm"),
    # everything under the ground (tu07-cu19, bx08, bx21-24): the same dusk with NO sun, no sky fill, no bounce lamps
    # and no haze (engine/underground.py SKY): below the ground the only light is the baked block light of the game
    # and the torches. Under "dusk" the sky's fill and ground-bounce lamps would light the hall from nowhere. It does
    # not read as a different time: no sky is ever seen from the hall (its neighbours ev06 and sq20 are other places).
    "under": dict(preset="dusk", az=187.0, el=5.0, key=0.0, ambient=0.0, bloom=1.3, grade="neutral", haze=0.0),
}

# The shot plan: (shot = the function's name, beat, sequence file, sky, where it starts). A start is a sentence id (the
# cut is Sentence.cut: two frames before its first word) or (sentence id, word): a cut inside the sentence before that
# word (nar.cut_before: never inside the word before it). One shot per beat.
SHOTS = [
    ("sq01_base", 1, "square", "dusk", "b01"),
    ("sq02_lip", 2, "square", "dusk", "b02"),          # CAMS "lip": the framing bx24 repeats
    ("sq03_push", 3, "square", "dusk", "b03"),
    ("ev04_bed", 4, "evening", "dusk", "b04"),
    ("ev05_stop", 5, "evening", "dusk", "b05"),
    ("ev06_stairs", 6, "evening", "dusk", "b06"),
    ("tu07_hall", 7, "turn", "under", "b07"),
    ("bx08_slot", 8, "box", "under", "b08"),           # CAMS "slot" (locked), the hands
    ("tu09_lever", 9, "turn", "under", "b09"),          # the wall opens (WALL)
    ("tu10_hug", 10, "turn", "under", "b10"),
    ("tu11_hard", 11, "turn", "under", "b11"),
    ("tu12_green", 12, "turn", "under", "b12"),         # dad turns: the zombie villager from the last blow
    ("cu13_potion", 13, "cure", "under", "b13"),
    ("cu14_apple", 14, "cure", "under", "b14"),
    ("cu15_two", 15, "cure", "under", "b15"),           # the wall shuts on "two" (WALL)
    ("cu16_shakes", 16, "cure", "under", "b16"),
    ("cu17_emerald", 17, "cure", "under", "b17"),       # the cure's swap inside the shot
    ("cu18_saved", 18, "cure", "under", "b18"),
    ("cu19_behind", 19, "cure", "under", "b19"),
    ("sq20_grow", 20, "square", "dusk", "b20"),
    ("bx21_small", 21, "box", "under", "b21"),          # CAMS "slot" again, the push, black
    ("bx22_found", 22, "box", "under", "b22"),
    ("bx23_kill", 23, "box", "under", "b23"),
    ("bx24_kept", 24, "box", "under", "b24"),           # CAMS "box": the mirror of sq02; the wall opens (WALL)
]
# THE WALL PLAN: the only shots that move dad's back wall (the piston door), and to what. Shut before tu09.
WALL = {"tu09_lever": "open", "cu15_two": "shut", "bx24_kept": "open"}
DIPS = {}                                      # no dip to black inside the film (see THE EDIT)
END_BLACK = 6      # the story's "Cut to black": the last 6 frames (0.25 s) are black (an encoder dip with no way back),
#                    after a hold of about 2 s on dad's back; the Reel then loops to frame 1
MIN_SHOT, MAX_SHOT = 1.2, 5.0                  # seconds: a shot outside needs its reason here
LENGTH_REASONS = {}


def timeline(nar):
    """The shot plan with its frames, from the spoken narration: [twoapples_common.ShotInfo] in film order."""
    cuts = []
    for name, _beat, _seq, _sky, start in SHOTS:
        if isinstance(start, str):
            sent, cut = nar.sentence(start), nar.sentence(start).cut
        else:
            sent = nar.sentence(start[0])
            cut = nar.cut_before(nar.word(start[1], sentence=sent))
        cuts.append((sent, cut))
    assert cuts[0][1] == 1, "the first shot starts the film"
    ends = [c - 1 for _s, c in cuts[1:]] + [nar.frames]
    rows = []
    for (name, beat, seq, sky, _start), (sent, a), b in zip(SHOTS, cuts, ends):
        assert b >= a, "shot %s is empty" % name
        mine = [w for w in nar.words if a <= w.frame <= b]
        words = [(w.caption, w.frame) for w in mine]
        # no word across a cut: a word ends inside its shot, or (running speech) in the very frame the next word
        # starts in, which is then the first frame of the next shot and shows that next word
        last = mine[-1]
        assert last.frame_end <= b or (last.frame_end == b + 1 and nar.words[last.index + 1].frame == b + 1), \
            "a word straddles the end of %s" % name
        row = TC.ShotInfo(name=name, beat=beat, sequence=seq, sky=sky, sentence=sent, frame_start=a, frame_end=b,
                          frames=b - a + 1, seconds=(b - a + 1) / float(nar.fps), words=words, wall=WALL.get(name))
        row.dip = name in DIPS
        rows.append(row)
    for prev, nxt in zip(rows, rows[1:]):
        prev.next, nxt.prev = nxt.name, prev.name
    return rows


def caption_cuts(nar, rows):
    """The frames on which a caption clears: every cut of the plan AND every sentence's own cut (the narrator's
    default, engine.narration captions(cuts=None)); here they are the same frames (one shot per sentence)."""
    return sorted({r.frame_start for r in rows[1:]} | {s.cut for s in nar.sentences[1:]})


def wall_states(rows):
    """{shot name: (state on its first frame, state on its last frame)} by THE WALL PLAN ("open" / "shut")."""
    out, state = {}, "shut"
    for r in rows:
        after = WALL.get(r.name, state)
        out[r.name] = (state, after)
        state = after
    return out


def _enforce_wall(C, r, want):
    """After shot r's function: the wall must be in the plan's state on the shot's first and last frame. A shot that
    broke the plan (or failed: its stand-in moves nothing) gets the plan forced, loudly (fatal with STRICT)."""
    w0, w1 = want
    got0, got1 = C.wall_is_open(r.frame_start), C.wall_is_open(r.frame_end)
    if (got0, got1) == (w0 == "open", w1 == "open"):
        return
    msg = "[twoapples] !!! %s breaks THE WALL PLAN: open on its first / last frame %s / %s, the plan says %s / %s" % (
        r.name, got0, got1, w0, w1)
    if STRICT:
        raise AssertionError(msg)
    print(msg + ": forced", file=sys.stderr)
    BROKEN.setdefault(r.name, msg)
    f = max(r.frame_start, r.frame_end - 4)
    if w1 == "open" and not got1:
        C.ug.door.open(f)
    elif w1 == "shut" and got1:
        C.ug.door.close(f)


def build(scene, sky=None):
    """Build the film with `sky` active (None: the first of SKIES):
    {"film", "captions", "narration", "stage", "context"}."""
    # 1. the voice: stops here (NarrationError) if narration/twoapples.json was not spoken from NARRATION
    nar = narration.load(__name__, NARRATION, fps=FPS)
    print(nar.summary())
    rows = timeline(nar)

    # 2. the set, the stage (it builds the active sky), the lever in the cast, the shared context
    v, ug = TC.build_set(scene)
    film = shots.Film(scene, fps=FPS)
    st = L.Stage(scene, film, v, skies=SKIES, sky=sky)
    ug.register(st)                       # the lever: hidden in every shot that does not st.use it (C.lights does)
    C = TC.TwoApples(st, ug, nar, {r.name: r for r in rows})

    # 3. every shot of the plan, in order, tagged with its sky
    for r in rows:
        s = st.shot(r.name, nar.seconds(r.frames), sky=r.sky)
        assert (s.frame_start, s.frame_end) == (r.frame_start, r.frame_end), (r, s.frame_start, s.frame_end)
        C.shots[r.name] = s
    assert film.shots[-1].frame_end == nar.frames

    # 4. the pictures: each shot's function from its sequence file, IN TIMELINE ORDER (characters, the wall and the
    #    lever are keyed in frame order); particles never live across a change of place. A sequence that does not
    #    import, or a shot function that raises, gets the stand-in (see STRICT above) and is named in BROKEN. After
    #    every shot the wall is checked against THE WALL PLAN.
    BROKEN.clear()
    modules = {seq: _import(seq) for seq in SEQUENCE_FILES}
    walls = wall_states(rows)
    before = None
    for r in rows:
        if before is not None and r.sequence != before:
            C.time_jump(r.frame_start)
        s = C.shots[r.name]
        fn = getattr(modules[r.sequence], r.name, None) if modules[r.sequence] is not None else None
        try:
            if fn is None:
                raise AttributeError("films/twoapples_%s.py has no function %s" % (r.sequence, r.name))
            fn(st, s, C, nar)
        except Exception:
            if STRICT:
                raise
            BROKEN[r.name] = traceback.format_exc()
            print("[twoapples] !!! SHOT %s (%s) FAILED: it gets a stand-in\n%s" % (r.name, r.sequence,
                                                                                BROKEN[r.name]), file=sys.stderr)
            cam, light = TC.STAND_IN[r.sequence]
            C.cam(s, cam, handheld=0.004, see=())
            C.lights(s, light)
        _enforce_wall(C, r, walls[r.name])
        before = r.sequence
    if BROKEN:
        print("[twoapples] !!! %d part(s) built as stand-ins or forced: %s" % (len(BROKEN), ", ".join(BROKEN)),
              file=sys.stderr)

    # 5. the dips to black (the encoder's), the end in black, then hide everybody outside their shots
    for name, kw in DIPS.items():
        st.dip(C.T[name].frame_start, **kw)
    st.dip(nar.frames - END_BLACK + 1, out=0, hold=END_BLACK, back=0)
    st.finish()

    # 6. this film's final quality (a measured study): 540x960 at 16 samples, upscaled to 1080x1920 at encode
    scene.render.resolution_x, scene.render.resolution_y = TC.FINAL_RES
    scene.cycles.samples = TC.FINAL_SAMPLES

    # 7. the captions: one word at a time; a word never stays on past a cut
    caps = nar.captions(cuts=caption_cuts(nar, rows))
    return {"film": film, "captions": caps, "narration": nar, "stage": st, "context": C}
