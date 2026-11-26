"""Leg Day: 65.29 narrated seconds (1567 frames), 24 sentences, 23 shots, two skies. Told by the town's one redstoner.

    "In this town, everyone wants to get ripped. ... They call it leg day. I call it reloading."
                 (stories/redstoner.json: the story, the picture of every beat, the risks and their fallbacks;
                  SHOTLISTS.md has the same as a table)

This file is the lead director's: the narration (the clock of the film), the skies, the shot plan, the world state
of the anvil wall from shot to shot (SHELF, REARM) and build(). The pictures are made by five sequence files, one
place each, one function per shot (the contract, the set, the places, the shared cameras, the cast and the helpers:
films/legday_common.py; the set itself: films/legday_set.py):

    films/legday_square.py  sq01 sq02 sq07 sq08 sq09 sq10        the village square: the squats at the well, the
                                                                 stone row (beats 2 AND 3, one take), the bench,
                                                                 the arms, the piston column
    films/legday_pens.py    pn04 pn05 pn06 pn17                  the chicken and cow pens (milk loop, hiding)
    films/legday_climb.py   cl11 cl12 cl22 cl23                  the anvil wall from the road and the stair: the
                                                                 climb and the legs, in gold AND their exact
                                                                 repeats at dusk (one hand makes both)
    films/legday_top.py     tp13 tp14 tp18 tp24                  the wall top: the twelfth sticky piston, the
                                                                 dust, the lever, "reloading" (gold and dusk)
    films/legday_road.py    rd15 rd16 rd19 rd20 rd21             the road at the wall's foot and the meadow: the
                                                                 patrol, the charge, THE DROP, the banner and the
                                                                 bottle, Steve among the anvils

    $TTS tools/narrate.py legday --check                 # the voice is spoken and committed: narration/legday.*
    $BPY -m tools.legday_timeline [--check|--json]       # the shot plan with frames and words; caption proof
    $BPY -m tools.legday_shots render --shots rd19_drop --frame 1215 --zones     # stills of single shots (one
                                                         #   build per sky; 540x960, 16 samples by default)
    $BPY -m tools.legday_shots tiles --sky gold; ... --sky dusk; ... sheet       # one tile per shot
    $BPY -m tools.legday_geo --sky gold sq08_arms:470    # heads, face pixels, angle to the lens, what blocks them
    $BPY -m tools.legday_palette --sky gold 1215         # tools/palette_check on one frame at final quality
    $BPY -m render legday --still 12.0 --zones           # one frame through render.py
    $BPY -m render legday --frames rd19_drop --res 270x480 --samples 10 --threads 2    # one shot as a preview
                                                         #   (each sequence its own sample count: _common)
    $BPY -m render legday --frames all --max-seconds 240 # FINAL frames: this film's final quality is 540x960 at
                                                         #   16 samples (set in build(); never pass --res/--samples)

THE VOICE IS COMMITTED (am_michael, speed 1.0; the last line "I call it reloading." at 0.9, the storyteller's
slower ending, as in The Hello). Changing a word, a pause, the voice or a speed below makes narration/legday.json
stale (build stops) and, once spoken again, moves every cut after it: do not, unless the orchestrator says so.
Spoken twice by the lead: 65.83 s with the first pauses; then the pauses shaped (the two "They call it leg day."
shots made the same length, 45 frames each: the second is an exact repeat of the first; the story's turns kept
longer: before "But I'm a redstoner", after "He said that's cheating", "Nobody asked why", the drop, and before
dusk), 65.29 s = 1567 frames, inside the 58-66 s asked. No word of the script was cut (165 words: the story's trim
order, "even" and then "But", was not needed). Pronunciation checked with --phonemes: "redstoner" goes through the
narrator's built-in respelling "red-stoner"; everything else (Pillagers, crossbows, protein, anvils, reloading,
redstone, pixels) is said right as written: no "say" entry. The recogniser hears "cow" 105 ms later than the
voice model's timing (narrate.py CHECK); the model's timing is the one used (the recogniser is the less exact).

GUARDED BUILD: each sequence file is imported, and each shot function called, inside a guard (see STRICT below):
a broken file or shot prints "[legday] !!! ..." and gets a stand-in; LEGDAY_STRICT=1 makes every error fatal.

THE SHOT LENGTHS: every shot is 1.6 to 4.5 s except sq02_reps (5.50 s): beats 2 AND 3 are ONE take, as the story
asks ("The same take carries on and drifts back"): the stone bursts on "drops", nothing drops, the empty grass is
held, Steve steps to the next stone, the pull-back shows the row and the pickaxe. A cut at "It drops nothing" would
sit four frames before the burst and hide the one thing the line is about.
THE DIP: the cut from rd21 (gold, the road after the drop) to cl22 (dusk, the climb again) dips to black (DIPS):
the day passes ("before dark"), and the twelve pistons push their planks out again INSIDE the two black frames
(REARM: the trap is reloaded where nobody sees it, which is the story's point).
THE END: the last image holds 1.75 s after "reloading" (the story: "hold one second after the last word, then
cut to black"; the brief: about two), then the last 6 frames are black (END_BLACK); the Reel loops to frame 1.
"""
import importlib
import os
import sys
import traceback
import types

from engine import narration, shots
from films import legday_common as LC
from films import lookdev as L

FPS = 24

# FIVE DIRECTORS EDIT FIVE FILES AT THE SAME TIME: a half-written sequence file must not stop the other four from
# building and scouting. So each sequence module is imported, and each shot function called, inside a guard: an
# error is printed loudly (module, shot, traceback) and that shot gets a plain stand-in (its location's camera,
# its torch levels, nobody in it); the rest of the film builds. LEGDAY_STRICT=1 in the environment turns the guard
# off (the orchestrator's merge, the final render and the contact sheets of record run strict).
STRICT = os.environ.get("LEGDAY_STRICT", "") not in ("", "0")
SEQUENCE_FILES = {"square": "films.legday_square", "pens": "films.legday_pens", "climb": "films.legday_climb",
                  "top": "films.legday_top", "road": "films.legday_road"}
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
        print("[legday] !!! SEQUENCE %s DOES NOT IMPORT: its shots get stand-ins\n%s" % (seq, BROKEN[seq]),
              file=sys.stderr)
        return None


# the stand-in of a shot whose function is missing or raised: its location's camera, nobody in it (the torch
# level follows the shot's own sky: "gold" or "dusk", the same in every build)
STAND_IN = {"square": "square_wide", "pens": "pens_wide", "climb": "climb", "top": "top_row", "road": "road_shelf"}

# The narration: stories/redstoner.json word for word, one entry per sentence (165 words). Pauses are after the
# sentence, voice to voice; default 0.35 s. Spoken length 51.5 s; with these pauses the film is 65.29 s = 1567 frames.
NARRATION = {
    "voice": "am_michael", "speed": 1.0,
    "tail": 2.0,                                    # the last image holds 1.75 s after the last word, then the last
    #                                                 6 frames are black (END_BLACK: the story's cut to black)
    "lines": [
        {"text": "In this town, everyone wants to get ripped.", "id": "b01"},
        {"text": "Steve mines stone with his fists.", "id": "b02"},
        {"text": "It drops nothing, and he counts that as one rep.", "id": "b03", "pause": 0.45},
        {"text": "There's a chicken farm, and a cow farm for protein shakes.", "id": "b04"},
        {"text": "Milk doesn't even fill you up.", "id": "b05", "pause": 0.45},     # the bucket's loop needs it
        {"text": "I haven't told them.", "id": "b06", "pause": 0.6},                # he walks off; the turn:
        {"text": "But I'm a redstoner.", "id": "b07", "pause": 0.45},
        {"text": "My arms are three pixels wide, and theirs are four.", "id": "b08", "pause": 0.45},
        {"text": "Steve asked how much my piston lifts, and I said twelve blocks.", "id": "b09"},
        {"text": "He said that's cheating.", "id": "b10", "pause": 0.6},            # to the wall
        {"text": "Every day they carry twelve anvils up the wall.", "id": "b11"},
        {"text": "They call it leg day.", "id": "b12", "pause": 0.7},               # = b23: the same 45 frames
        {"text": "Under each anvil, I put a sticky piston.", "id": "b13"},
        {"text": "Nobody asked why.", "id": "b14", "pause": 0.8},                   # the story turns: the patrol
        {"text": "Then the pillagers came.", "id": "b15", "pause": 0.45},
        {"text": "Everyone ran out to punch them.", "id": "b16"},
        {"text": "Pillagers have crossbows, so everyone hid behind the cows.", "id": "b17", "pause": 0.5},
        {"text": "I flipped one lever.", "id": "b18", "pause": 0.45},
        {"text": "Twelve pistons pulled back, and twelve anvils fell on the road.", "id": "b19", "pause": 0.8},
        {"text": "That left a banner and a bottle.", "id": "b20", "pause": 0.5},
        {"text": "Steve still says redstone is cheating.", "id": "b21", "pause": 0.7},   # the day passes (dip)
        {"text": "But they carried all twelve back up before dark.", "id": "b22"},
        {"text": "They call it leg day.", "id": "b23", "pause": 0.7},               # = b12; before the last line
        # the last line a tenth slower: the storyteller slows down for the ending (at 1.0 it went by in 1.11 s,
        # 3.6 words a second, faster than the film's 3.2)
        {"text": "I call it reloading.", "id": "b24", "speed": 0.9},
    ],
}

# The skies (films.lookdev.Stage: arguments of look.set_time / look.setup_compositor). render.py builds the film
# once per sky that has work. az = where the sun stands, degrees counter-clockwise from east (90 = north).
# Two entries, each for a reason (each costs one more build, about 3 s, per render command that has work in it):
SKIES = {
    # beats 1-21, every place: the set's own golden sky (films/legday_set.py SKIES: every scouting still of the set
    # was made under it). THE SUN IS DUE EAST: the anvil wall's road face looks INTO it (lit, its shadow falls west,
    # off the road: the story's "build it so its road face looks at the sun"); the patrol walking south and the
    # runners going north are side-lit on their east halves, and every camera looking north or south along the
    # road has the sun 90 degrees off its axis (CONTRACT: 60-120 degrees for cast shadows). The illagers builder's
    # measurement (beat 15 backlit under the look-dev az 62) is answered by it: under az 0 the patrol's faces, seen
    # from the road looking north, are lit from the east. The square and the pens were staged for it: the players
    # there face EAST or south (the road, the lens). The morning sun of a training town; at dusk the sun has gone
    # round to the west (the day passes over the film).
    "gold": dict(preset="golden", az=0.0, el=27.0, bloom=1.0, grade="warm"),
    # beats 22-24 ("before dark"): the set's dusk, the sun gone down in the WEST behind the wall as seen from the
    # road (az 185, el 5): the road face in shadow, lit by its lanterns (LIGHTS "dusk": 1.4, the look-dev dusk level,
    # never more: lit stone beside a lantern is on the palette limit), an indigo sky with the first stars and pink
    # clouds over the wall top. COMPARED SIDE BY SIDE with gold on the shared frame (cl11 / cl22: the set builder's
    # out/test/legday_set_b11_climb.png against legday_set_b22_climb.png, and the lead's scout stills
    # out/test/legday_scout_climb_gold.png / _dusk.png): blue afternoon against indigo with stars, nobody can take
    # one for the other. KNOWN AND ACCEPTED: tools/palette_check's rule "stone not magenta" (G >= 0.92 R) fails on
    # the wall top at dusk (tp24: G/R 0.90, rgb(123,111,105), with the lanterns OFF 0.87): it is the warm dusk sky
    # on the stone, B under G, not magenta; the rule cannot tell warm from magenta (engine/fixtures' notes, the set
    # builder's report). Do not "fix" it by boosting lanterns.
    "dusk": dict(preset="dusk", az=185.0, el=5.0, bloom=1.3, grade="warm"),
}

# The shot plan: (shot = the function's name, beat(s), sequence file, sky, where it starts). A start is a sentence
# id (the cut is Sentence.cut: two frames before its first word) or (sentence id, word): a cut inside the sentence
# before that word (nar.cut_before: never inside the word before it). One shot per beat, except beats 2 + 3: one
# take (see the module docstring).
SHOTS = [
    ("sq01_squats", 1, "square", "gold", "b01"),
    ("sq02_reps", 2, "square", "gold", "b02"),              # beats 2 AND 3: one take, 5.5 s
    ("pn04_farms", 4, "pens", "gold", "b04"),
    ("pn05_milk", 5, "pens", "gold", "b05"),
    ("pn06_told", 6, "pens", "gold", "b06"),
    ("sq07_bench", 7, "square", "gold", "b07"),
    ("sq08_arms", 8, "square", "gold", "b08"),
    ("sq09_lifts", 9, "square", "gold", "b09"),
    ("sq10_cheating", 10, "square", "gold", "b10"),
    ("cl11_climb", 11, "climb", "gold", "b11"),
    ("cl12_legday", 12, "climb", "gold", "b12"),
    ("tp13_sticky", 13, "top", "gold", "b13"),
    ("tp14_why", 14, "top", "gold", "b14"),
    ("rd15_pillagers", 15, "road", "gold", "b15"),
    ("rd16_punch", 16, "road", "gold", "b16"),
    ("pn17_cows", 17, "pens", "gold", "b17"),
    ("tp18_lever", 18, "top", "gold", "b18"),
    ("rd19_drop", 19, "road", "gold", "b19"),
    ("rd20_banner", 20, "road", "gold", "b20"),
    ("rd21_still", 21, "road", "gold", "b21"),
    ("cl22_dusk", 22, "climb", "dusk", "b22"),               # after a dip to black (DIPS); the row re-armed in it
    ("cl23_legday", 23, "climb", "dusk", "b23"),
    ("tp24_reloading", 24, "top", "dusk", "b24"),
]
BEATS = {"sq02_reps": (2, 3)}                  # a shot that carries more than one beat (default: its own beat)
SKY_CHANGE = {}                                # no sky changes inside a shot
DIPS = {"cl22_dusk": dict(out=3, hold=1, back=3)}    # the day passes: black on the cut and one frame more (1369,
#                                                      1370), fading out from 1366, back by 1373 ("But" is on 1371:
#                                                      its caption is drawn over the dip at full strength)
END_BLACK = 6      # the story's "then cut to black": the last 6 frames (0.25 s) are black (an encoder dip with no
#                    way back), after a hold of 1.75 s on the narrator at the lever; the Reel then loops to frame 1

# THE ANVILS ON THE SHELF, shot by shot (the lead's: build() applies it to every shot, stand-ins included; a
# sequence director does not st.use anvils himself). films/legday_common.py SHELF names the states: which set
# (the day set falls in rd19 and lies on the road after it; the dusk set is the one "back up") and which planks
# (index 0 = the south plank, nearest the stair; 11 = the north one beside the lever, "the twelfth").
#   "eight"        day set on planks 3..10: before and during the morning climb (cl11: 8 up, 4 in hands; the
#                  twelfth piston is not there yet: the narrator sets it in tp13)
#   "eleven"       day set on planks 0..10 (tp13; tp14 until Steve sets the twelfth: C.appear(s, C.P.anvils[11], f))
#   "twelve"       all twelve of the day set: armed (rd15-tp18), falling (rd19), on the road (rd20, rd21)
#   "dusk_eight"   dusk set on planks 3..10 (cl22, cl23: "eight anvils already back in place")
#   "dusk_eleven"  dusk set on planks 0..10 (tp24 until Steve sets the twelfth: C.appear(s, C.P.anvils_dusk[11], f))
SHELF = {
    "sq01_squats": "eight", "sq02_reps": "eight", "pn04_farms": "eight", "pn05_milk": "eight",
    "pn06_told": "eight", "sq07_bench": "eight", "sq08_arms": "eight", "sq09_lifts": "eight",
    "sq10_cheating": "eight", "cl11_climb": "eight", "cl12_legday": "eight", "tp13_sticky": "eleven",
    "tp14_why": "eleven", "rd15_pillagers": "twelve", "rd16_punch": "twelve", "pn17_cows": "twelve",
    "tp18_lever": "twelve", "rd19_drop": "twelve", "rd20_banner": "twelve", "rd21_still": "twelve",
    "cl22_dusk": "dusk_eight", "cl23_legday": "dusk_eight", "tp24_reloading": "dusk_eleven",
}
# THE RE-ARM (the lead's, keyed by build() just before cl22_dusk's function): the twelve sticky pistons push their
# planks out again starting half a frame before cl22's first frame (the move takes 2.4 frames: [1368.5, 1370.9],
# entirely inside the dip's two black frames 1369-1370; frame 1368, at a third of the picture, still shows them in),
# the lever is on and the dust lit again from 1369. See legday_common.LegDay.rearm.
REARM = "cl22_dusk"


def timeline(nar):
    """The shot plan with its frames, from the spoken narration: [legday_common.ShotInfo] in film order."""
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
        row = LC.ShotInfo(name=name, beat=beat, beats=BEATS.get(name, (beat,)), sequence=seq, sky=sky,
                          sentence=sent, frame_start=a, frame_end=b, frames=b - a + 1,
                          seconds=(b - a + 1) / float(nar.fps), words=words, shelf=SHELF[name])
        if name in SKY_CHANGE:
            word, sky_after = SKY_CHANGE[name]
            row.change, row.sky_after = nar.at(word, sentence=sent), sky_after
            assert a < row.change <= b
        row.dip = name in DIPS
        rows.append(row)
    for prev, nxt in zip(rows, rows[1:]):
        prev.next, nxt.prev = nxt.name, prev.name
    return rows


def caption_cuts(nar, rows):
    """The frames on which a caption clears: every cut of the plan AND every sentence's own cut (the narrator's
    default, engine.narration captions(cuts=None)). Inside sq02_reps (two sentences, one take) the last word of
    "Steve mines stone with his fists." then clears on the second sentence's cut (126), two frames before "It",
    as at every other sentence start of the film (narration.prove checks exactly that)."""
    return sorted({r.frame_start for r in rows[1:]} | {s.cut for s in nar.sentences[1:]})


def build(scene, sky=None):
    """Build the film with `sky` active (None: the first of SKIES):
    {"film", "captions", "narration", "stage", "context"}."""
    # 1. the voice: stops here (NarrationError) if narration/legday.json was not spoken from NARRATION
    nar = narration.load(__name__, NARRATION, fps=FPS)
    print(nar.summary())
    rows = timeline(nar)

    # 2. the set, the stage (it builds the active sky), the shared context (it builds the moving parts of the set
    #    in their armed state, registers the anvils and keys the wall's state before the film: legday_common)
    v = LC.build_set(scene)
    film = shots.Film(scene, fps=FPS)
    st = L.Stage(scene, film, v, skies=SKIES, sky=sky)
    C = LC.LegDay(st, nar, {r.name: r for r in rows})

    # 3. every shot of the plan, in order, tagged with its sky
    for r in rows:
        s = st.shot(r.name, nar.seconds(r.frames), sky=r.sky)
        assert (s.frame_start, s.frame_end) == (r.frame_start, r.frame_end), (r, s.frame_start, s.frame_end)
        if r.change is not None:
            st.sky_change(r.change, r.sky_after)
        C.shots[r.name] = s
    assert film.shots[-1].frame_end == nar.frames

    # 4. the pictures: each shot's function from its sequence file, IN TIMELINE ORDER (characters and the set's
    #    moving parts are keyed in frame order); particles never live across a change of place. Before each
    #    function: the anvils on the shelf for that shot (SHELF) and, before cl22_dusk, the re-arm (REARM). A
    #    sequence that does not import, or a shot function that raises, gets the stand-in (see STRICT above) and is
    #    named in BROKEN.
    BROKEN.clear()
    modules = {seq: _import(seq) for seq in SEQUENCE_FILES}
    before = None
    for r in rows:
        if before is not None and r.sequence != before:
            C.time_jump(r.frame_start)
        s = C.shots[r.name]
        if r.name == REARM:
            C.rearm(r.frame_start)
        C.shelf(s, r.shelf)
        fn = getattr(modules[r.sequence], r.name, None) if modules[r.sequence] is not None else None
        try:
            if fn is None:
                raise AttributeError("films/legday_%s.py has no function %s" % (r.sequence, r.name))
            fn(st, s, C, nar)
        except Exception:
            if STRICT:
                raise
            BROKEN[r.name] = traceback.format_exc()
            print("[legday] !!! SHOT %s (%s) FAILED: it gets a stand-in\n%s" % (r.name, r.sequence, BROKEN[r.name]),
                  file=sys.stderr)
            C.cam(s, STAND_IN[r.sequence], handheld=0.004)
            C.lights(s, r.sky)
        before = r.sequence
    if BROKEN:
        print("[legday] !!! %d part(s) built as stand-ins: %s" % (len(BROKEN), ", ".join(BROKEN)), file=sys.stderr)

    # 5. the dips to black (the encoder's), the end in black, then hide everybody outside their shots
    for name, kw in DIPS.items():
        st.dip(C.T[name].frame_start, **kw)
    st.dip(nar.frames - END_BLACK + 1, out=0, hold=END_BLACK, back=0)
    st.finish()

    # 6. this film's final quality (a measured study): 540x960 at 16 samples, upscaled to 1080x1920 at encode
    scene.render.resolution_x, scene.render.resolution_y = LC.FINAL_RES
    scene.cycles.samples = LC.FINAL_SAMPLES

    # 7. the captions: one word at a time; a word never stays on past ANY cut (nor past a sentence's start)
    caps = nar.captions(cuts=caption_cuts(nar, rows))
    return {"film": film, "captions": caps, "narration": nar, "stage": st, "context": C}
