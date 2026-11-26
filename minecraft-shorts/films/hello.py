"""The Hello: 64.33 narrated seconds (1544 frames), 22 sentences, 24 shots, four skies. Told by a baby villager.

    "In this town, the player used to protect us. ... He crouched, once, and he stayed down. The player had blue
     eyes."      (stories/herobrine.json: the story, the picture of every beat, the risks and their fallbacks)

This file is the lead director's: the narration (the clock of the film), the skies, the shot plan and build().
The pictures are made by five sequence files, one location each, one function per shot (the contract, the set,
the places, the shared cameras, the cast and the helpers: films/hello_common.py):

    films/hello_square.py      sq01 sq09 sq10 sq11                 village square, golden hour
    films/hello_door_night.py  dn02 dn18 dn19                      the child's door at night
    films/hello_interior.py    in03 in16 in17                      inside the child's house (beat 3 ends in gold)
    films/hello_door_gold.py   dg04 dg05 dg15_a/b/c dg20 dg21 dg22 the child's door in golden light
    films/hello_meadow.py      me06 me07 me08 me12 me13 me14       exit gate, meadow road, forest wall, the signs

    $TTS tools/narrate.py hello --check                  # the voice is spoken and committed: narration/hello.*
    $BPY -m tools.hello_timeline [--json]                # the shot plan with frames and words; caption proof
    $BPY -m tools.hello_shots render --shots dg04_hello --frame 226 --zones      # stills of single shots (one
                                                         #   build per sky; 540x960, 16 samples by default)
    $BPY -m tools.hello_shots tiles --sky gold; ... sheet   # one tile per shot -> out/test/hello_shots_sheet.png
    $BPY -m render hello --still 12.0 --zones            # one frame through render.py
    $BPY -m render hello --frames dn02_fight --res 270x480 --samples 6 --threads 2     # one shot as a preview
                                                         #   (each sequence its own sample count: hello_common)
    $BPY -m render hello --frames all --max-seconds 240  # FINAL frames: this film's final quality is 540x960 at
                                                         #   16 samples (set in build(); never pass --res/--samples)

THE VOICE IS COMMITTED. Changing a word, a pause, the voice or the speed below makes narration/hello.json stale
(build stops) and, once spoken again, moves every cut after it: do not, unless the orchestrator says so. (Spoken
twice: at speed 1.0 throughout, 63.79 s; then with the last two lines at 0.9 and the tail 2.3 s, 64.33 s: every
cut up to dg21's start stayed where it was.)

GUARDED BUILD: each sequence file is imported, and each shot function called, inside a guard (see STRICT below):
a broken file or shot prints "[hello] !!! ..." and gets a stand-in; HELLO_STRICT=1 makes every error fatal.

THE SHOT LENGTHS: every shot is 1.25 to 4.25 s except dg15_b (0.88 s, "he is one house"): the middle one of the
three jump cuts of beat 15, which quicken on purpose; the cuts sit on word boundaries ("he", "closer").
THE END: the last image holds 2.0 s after the last word, then the last 6 frames are black (END_BLACK).

THE LEAD'S PASS (after the five sequences were shot and reviewed; the narration and the cuts untouched)
  Skies:  "dawn" is the DUSK preset at elevation 4 with the clouds moved (me07 / me08: a pink sunrise over the wood
          with the last stars; the 'golden' dawn read as beat 6's afternoon). "night" has its moon in the north-east
          behind house_a (azimuth 35, was 176): the west front is in moonshadow, its two door torches light the door;
          with the moon in the west the door at night read as a warm sunlit porch (luma 100-114 against 78 for the
          other night shots; now 76-85). The interior is unchanged by it (in03@160 80.0 -> 80.1).
  Shared (films/hello_common.py, its docstring has the details): CAMS "door_front" 40 mm with the starry sky over
          the roof (dn02, dn18), LIGHTS "night_door" door torches x 1 (was x 2), CAMS "beside" raised to z 1.9 (dn19:
          the zombie's fist clear of his head), PLACES "watch_mid" (8.5, 1.5) (dg15_b: 28 / 45 / 78 px), the stub
          places and cameras taken out (every other camera is its shot's own: C.cam(s, None, **CAM)), "watch_square",
          "gate_child", "window_chair" set to the values the shots use, C.held_item, me07's f/2.0 accepted.
  Decided and left: the child in dg04 / dg22 stays the soft pink block (a nose cheat tested: out of the frame or
          no nose: hello_common CAMS "two_shot"); dn02's sword in the caption band once he faces out (a prop under
          the caption, his head clear); sq01 without the background adults (the square director's reasons); the
          farmer of sq09 (walking toward us south of the well) standing north of it in sq10 (a new sentence and a
          new angle across the well: a jump in time, not a mistake a viewer can place; changing sq09's lane would
          re-open the watcher's gap measured there).
  Cuts between sequences: checked on the sequences' own preview frames, side by side (scratchpad of the lead's
          pass; the list is in its report); nothing jumps that the story does not ask for.
"""
import importlib
import os
import sys
import traceback
import types

from engine import narration, shots
from films import hello_common as HC
from films import lookdev as L

FPS = 24

# FIVE DIRECTORS EDIT FIVE FILES AT THE SAME TIME: a half-written sequence file must not stop the other four from
# building and scouting. So each sequence module is imported, and each shot function called, inside a guard: an
# error is printed loudly (module, shot, traceback) and that shot gets a plain stand-in (its location's camera,
# its torch levels, nobody in it); the rest of the film builds. HELLO_STRICT=1 in the environment turns the guard
# off (the orchestrator's merge, the final render and the contact sheets of record run strict).
STRICT = os.environ.get("HELLO_STRICT", "") not in ("", "0")
SEQUENCE_FILES = {"square": "films.hello_square", "door_night": "films.hello_door_night",
                  "interior": "films.hello_interior", "door_gold": "films.hello_door_gold",
                  "meadow": "films.hello_meadow"}
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
        print("[hello] !!! SEQUENCE %s DOES NOT IMPORT: its shots get stand-ins\n%s" % (seq, BROKEN[seq]),
              file=sys.stderr)
        return None


# the stand-in of a shot whose function is missing or raised: its location's camera and torch levels, nobody in it
STAND_IN = {"square": ("square_long", "gold"), "door_night": ("door_front", "night_door"),
            "interior": ("bed", "night_room"), "door_gold": ("two_shot", "gold"), "meadow": ("set:gate", "gold")}

# The narration: stories/herobrine.json word for word, one entry per sentence (161 words). Pauses are after the
# sentence, voice to voice; default 0.35 s. Spoken length 47.4 s; with these pauses the film is 64.33 s = 1544 frames.
NARRATION = {
    "voice": "am_michael", "speed": 1.0,
    "tail": 2.3,                                    # the last image holds two seconds after the last word, then the
    #                                                 last 6 frames are black (END_BLACK: the story's cut to black)
    "lines": [
        {"text": "In this town, the player used to protect us.", "id": "b01"},
        {"text": "He fought every zombie that knocked on our door.", "id": "b02"},
        {"text": "When he slept, the night just ended.", "id": "b03", "pause": 0.8},      # the morning is seen
        {"text": "Every morning he crouched at me, twice.", "id": "b04", "pause": 0.45},  # he is up again
        {"text": "That meant hello.", "id": "b05", "pause": 1.0},          # the child runs off; the story turns
        {"text": "One day he put on his best armor and walked into the woods.", "id": "b06", "pause": 0.8},   # dip
        {"text": "He came back at sunrise without it.", "id": "b07", "pause": 0.7},
        {"text": "He didn't crouch.", "id": "b08", "pause": 1.3},          # nothing comes back; the story turns
        {"text": "Now he just stands around and watches us.", "id": "b09", "pause": 0.4},
        {"text": "The grownups say players stand still sometimes.", "id": "b10"},
        {"text": "I watch him back.", "id": "b11", "pause": 0.8},
        {"text": "He used to take the trunk and leave the tree floating.", "id": "b12"},
        {"text": "Now he only takes the leaves.", "id": "b13", "pause": 0.4},
        {"text": "Nobody built the sand pyramid in the meadow.", "id": "b14", "pause": 0.5},
        {"text": "Every time I look, he is one house closer.", "id": "b15", "pause": 0.8},   # he is at our corner
        {"text": "He doesn't sleep anymore.", "id": "b16", "pause": 0.7},
        {"text": "The nights last all night.", "id": "b17", "pause": 0.9},
        {"text": "Last night a zombie knocked on our door until sunrise.", "id": "b18"},
        {"text": "He stood beside it and watched.", "id": "b19", "pause": 1.0},          # their two backs
        {"text": "So this morning I walked up to him and waited for my hello.", "id": "b20", "pause": 0.5},
        # the last two lines a tenth slower than the rest: the storyteller slows down for the ending (at 1.0 they
        # went by at 3.3-3.4 words per second, the film's average, as fast as "Nobody built the sand pyramid")
        {"text": "He crouched, once, and he stayed down.", "id": "b21", "pause": 1.5, "speed": 0.9},   # the second
        #                                                                                             of silence
        {"text": "The player had blue eyes.", "id": "b22", "speed": 0.9},
    ],
}

# The skies (films.lookdev.Stage: arguments of look.set_time / look.setup_compositor). render.py builds the film
# once per sky that has work. az = where the sun (at night the moon) stands, degrees counter-clockwise from east.
# Four entries, each for a reason (each costs one more build, about 3 s, per render command that has work in it):
SKIES = {
    # the village in golden light: the square (1, 9-11), the child's door (4, 5, 15, 20-22), the end of beat 3.
    # A low sun in the west-south-west (films/_multisky_demo.py's): house_a's door faces west, so its front and the
    # plaza before it are in the sun (with the look-dev sun, azimuth 62, that whole side is in the house's own
    # shadow); the square's cameras look north-west to north, 80-120 degrees off it. Faces turned to the house
    # (the two-shot of 4 and 22) are lit by the film-local doorstep fill (hello_common.Hello.doorstep_fill).
    "gold": dict(preset="golden", az=215.0, el=24.0, bloom=1.0, grade="warm"),
    # the meadow (6, 12-14): the look-dev sun in the north-east, behind the wood, and NO distance haze: with the
    # preset's haze the forest wall 35 blocks away is dark brown, without it the gaps between the trunks are black
    # (engine/sets.py, measured). Every proof still of hello_set was made under exactly this sky.
    "meadow": dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm", haze=0.0),
    # "He came back at sunrise without it" (7, 8): the same meadow after the dip, the sun just up behind the wood
    # (still no haze: the wall stays black). One night has passed: the light must not be beat 6's afternoon (story
    # risk; its night insert cannot be had with fixed cuts). The DUSK preset at elevation 4 with the clouds moved:
    # a pink horizon over the wood, an indigo top with the last stars, pink clouds in new places. The first dawn
    # ('golden', elevation 9) was the same blue afternoon with every cloud in the same place, only the foreground
    # 20 % darker (both reviews of the meadow; out/test/hello_meadow_final_me07_return_470.png against
    # hello_meadow_final_me06_leave_395.png). Rendered: out/test/hello_lead_me07_return_470.png, _me08_nohello_505.png
    # (the lead's pass); palette_check passes on 460 and 505; the watcher's 8 px face stays an even smudge.
    "dawn": dict(preset="dusk", az=75.0, el=4.0, bloom=1.0, grade="warm", haze=0.0, cloud_offset=(9, -6)),
    # night at the door and in the house (2, 3, 16-19): the look-dev night preset with the moon in the NORTH-EAST,
    # behind house_a (azimuth 35, the preset's own side): the west front, its door and its window are in the moon's
    # shadow, lit by the two door torches (warm pools on the wall) and the cool sky, and the starry sky stands over
    # the roof. With the look-dev moon in the west (azimuth 176) the moon lit that front head-on and the door at
    # night read as a warm sunlit porch (mean luma 100-114 against 78 for the night interior; both reviews of the
    # door at night); now 76-85 (out/test/hello_lead_dn*_zones.png). The room inside is unchanged (in03@160 80.0 ->
    # 80.1); the window of beat 17 is darker around the child's lit face.
    "night": dict(preset="night", az=35.0, el=21.0, bloom=1.3, grade="cool"),
}

# The shot plan: (shot = the function's name, beat, sequence file, sky, where it starts). A start is a sentence
# id (the cut is Sentence.cut: two frames before its first word) or (sentence id, word): a cut inside the
# sentence before that word (nar.cut_before: never inside the word before it).
SHOTS = [
    ("sq01_guard", 1, "square", "gold", "b01"),
    ("dn02_fight", 2, "door_night", "night", "b02"),
    ("in03_bed", 3, "interior", "night", "b03"),               # ... and gold from the word "ended" (SKY_CHANGE)
    ("dg04_hello", 4, "door_gold", "gold", "b04"),
    ("dg05_nod", 5, "door_gold", "gold", "b05"),
    ("me06_leave", 6, "meadow", "meadow", "b06"),
    ("me07_return", 7, "meadow", "dawn", "b07"),             # after a dip to black (DIPS)
    ("me08_nohello", 8, "meadow", "dawn", "b08"),
    ("sq09_watches", 9, "square", "gold", "b09"),
    ("sq10_grownups", 10, "square", "gold", "b10"),
    ("sq11_stare", 11, "square", "gold", "b11"),
    ("me12_floating", 12, "meadow", "meadow", "b12"),
    ("me13_bare", 13, "meadow", "meadow", "b13"),
    ("me14_pyramid", 14, "meadow", "meadow", "b14"),
    ("dg15_a", 15, "door_gold", "gold", "b15"),                # three jump cuts in one locked frame:
    ("dg15_b", 15, "door_gold", "gold", ("b15", "he")),        #   "Every time I look," / "he is one house" /
    ("dg15_c", 15, "door_gold", "gold", ("b15", "closer")),    #   "closer."
    ("in16_empty", 16, "interior", "night", "b16"),
    ("in17_window", 17, "interior", "night", "b17"),
    ("dn18_knock", 18, "door_night", "night", "b18"),
    ("dn19_beside", 19, "door_night", "night", "b19"),
    ("dg20_walkup", 20, "door_gold", "gold", "b20"),
    ("dg21_crouch", 21, "door_gold", "gold", "b21"),
    ("dg22_eyes", 22, "door_gold", "gold", "b22"),
]
SKY_CHANGE = {"in03_bed": ("ended", "gold")}       # inside this shot the night ends ON this word: gold from there
DIPS = {"me07_return": dict(out=4, hold=1, back=4)}    # the night that passed: black on the cut and one frame more
END_BLACK = 6      # the story's "then cut to black": the last 6 frames (0.25 s) are black (an encoder dip with no
#                    way back), after a hold of 2.06 s on the white eyes; the Reel then loops to frame 1


def timeline(nar):
    """The shot plan with its frames, from the spoken narration: [hello_common.ShotInfo] in film order."""
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
        # no word across a cut: a word ends inside its shot, or (running speech, beat 15) in the very frame the
        # next word starts in, which is then the first frame of the next shot and shows that next word
        last = mine[-1]
        assert last.frame_end <= b or (last.frame_end == b + 1 and nar.words[last.index + 1].frame == b + 1), \
            "a word straddles the end of %s" % name
        row = HC.ShotInfo(name=name, beat=beat, sequence=seq, sky=sky, sentence=sent, frame_start=a, frame_end=b,
                          frames=b - a + 1, seconds=(b - a + 1) / float(nar.fps), words=words)
        if name in SKY_CHANGE:
            word, sky_after = SKY_CHANGE[name]
            row.change, row.sky_after = nar.at(word, sentence=sent), sky_after
            assert a < row.change <= b
        row.dip = name in DIPS
        rows.append(row)
    for prev, nxt in zip(rows, rows[1:]):
        prev.next, nxt.prev = nxt.name, prev.name
    return rows


def build(scene, sky=None):
    """Build the film with `sky` active (None: the first of SKIES):
    {"film", "captions", "narration", "stage", "context"}."""
    # 1. the voice: stops here (NarrationError) if narration/hello.json was not spoken from NARRATION
    nar = narration.load(__name__, NARRATION, fps=FPS)
    print(nar.summary())
    rows = timeline(nar)

    # 2. the set, the stage (it builds the active sky), the shared context
    v = HC.build_set(scene)
    film = shots.Film(scene, fps=FPS)
    st = L.Stage(scene, film, v, skies=SKIES, sky=sky)
    C = HC.Hello(st, nar, {r.name: r for r in rows})

    # 3. every shot of the plan, in order, tagged with its sky
    for r in rows:
        s = st.shot(r.name, nar.seconds(r.frames), sky=r.sky)
        assert (s.frame_start, s.frame_end) == (r.frame_start, r.frame_end), (r, s.frame_start, s.frame_end)
        if r.change is not None:
            st.sky_change(r.change, r.sky_after)             # beat 3: "... the night just ENDED"
        C.shots[r.name] = s
    assert film.shots[-1].frame_end == nar.frames

    # 4. the pictures: each shot's function from its sequence file, IN TIMELINE ORDER (characters are keyed in
    #    frame order); particles never live across a change of place. A sequence that does not import, or a shot
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
                raise AttributeError("films/hello_%s.py has no function %s" % (r.sequence, r.name))
            fn(st, s, C, nar)
        except Exception:
            if STRICT:
                raise
            BROKEN[r.name] = traceback.format_exc()
            print("[hello] !!! SHOT %s (%s) FAILED: it gets a stand-in\n%s" % (r.name, r.sequence, BROKEN[r.name]),
                  file=sys.stderr)
            cam, light = STAND_IN[r.sequence]
            C.cam(s, cam, handheld=0.004)
            C.lights(s, light)
        before = r.sequence
    if BROKEN:
        print("[hello] !!! %d part(s) built as stand-ins: %s" % (len(BROKEN), ", ".join(BROKEN)), file=sys.stderr)

    # 5. the dips to black (the encoder's), the end in black, then hide everybody outside their shots
    for name, kw in DIPS.items():
        st.dip(C.T[name].frame_start, **kw)
    st.dip(nar.frames - END_BLACK + 1, out=0, hold=END_BLACK, back=0)
    st.finish()

    # 6. this film's final quality (a measured study): 540x960 at 16 samples, upscaled to 1080x1920 at encode
    scene.render.resolution_x, scene.render.resolution_y = HC.FINAL_RES
    scene.cycles.samples = HC.FINAL_SAMPLES

    # 7. the captions: one word at a time; a word never stays on past ANY cut (the jump cuts of beat 15 included)
    caps = nar.captions(cuts=[r.frame_start for r in rows[1:]])
    return {"film": film, "captions": caps, "narration": nar, "stage": st, "context": C}
