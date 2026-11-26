"""The Crammys: 65.08 narrated seconds (1562 frames), 24 sentences, 23 shots, two skies. Told by Steve, the one player
in a musical town with nothing to perform.

    "In this town, everyone is musical except me. ... Kai said it sounded just like me coming home. I won Best
     Vocals."    (stories/crammys.json: the story, the picture of every beat, the risks and their fallbacks;
                  SHOTLISTS.md has the same as a table)

This file is the lead director's: the narration (the clock of the film), the skies, the shot plan and build(). The
pictures are made by five sequence files, one place and one light each, one function per shot (the contract, the
set, the places, the shared cameras, the cast, the continuity rules and the helpers: films/crammys_common.py; the set
itself: films/crammys_set.py):

    films/crammys_gold.py     gd01 gd02 gd03 gd04 gd05 gd06       the bandstand in golden light: the four acts, Zuri,
                                                                  Kai, Sunny, the trophy and the last lantern, the line
    films/crammys_road.py     rd07 rd09 rd17                      the village road at night: the lane (chased home;
                                                                  running back with the disc) and the exit gate
    films/crammys_meadow.py   md10 md11 md12 md13 md15 md16       the night meadow: the creeper, the skeleton, the
                                                                  middle, shot twice (ONE take), the kill, the disc
    films/crammys_jukebox.py  jb08 jb18 jb19 jb20                 the bandstand at night: the disc popped out, the
                                                                  arrows nobody asks about, to the jukebox, disc eleven
    films/crammys_finale.py   fn21 fn22 fn23 fn24                 the bandstand at night: the song, nobody moved, Kai,
                                                                  Best Vocals

    $TTS tools/narrate.py crammys --check                # the voice is spoken and committed: narration/crammys.*
    $BPY -m tools.crammys_timeline [--check|--json]      # the shot plan with frames and words; caption proof
    $BPY -m tools.crammys_shots render --shots md13_shot --frame 600 --zones     # stills of single shots (one
                                                         #   build per sky; 540x960, 16 samples by default)
    $BPY -m tools.crammys_shots tiles --sky gold; ... --sky night; ... sheet     # one tile per shot
    $BPY -m tools.crammys_geo --sky night md13_shot:600  # heads, face pixels, angle to the lens, what blocks them
    $BPY -m tools.crammys_palette --sky night 600        # tools/palette_check on one frame at final quality
    $BPY -m render crammys --still 12.0 --zones          # one frame through render.py
    $BPY -m render crammys --frames md13_shot --res 270x480 --samples 7 --threads 2    # one shot as a preview
                                                         #   (each sequence its own sample count: _common)
    $BPY -m render crammys --frames all --max-seconds 240    # FINAL frames: this film's final quality is 540x960
                                                         #   at 16 samples (set in build(); never pass --res/--samples)

THE VOICE IS COMMITTED (am_michael, speed 1.0 for every line; tail 2.2 s). Changing a word, a pause, the voice, the
speed or "say" below makes narration/crammys.json stale (build stops) and, once spoken again, moves every cut after it:
do not, unless the orchestrator says so. 163 words, no word of the story's text changed or cut (its cut priorities
were not needed). Pronunciation checked with --phonemes: the voice read "Zuri" as /zjuri/ ("zyoo-rri"); it is
respelled for the voice only ("say": "Zoo-ree" -> /zu:ri:/; the caption keeps "Zuri"); "Crammys" (/kraemiz/), "Kai"
(/kai/), "Sunny", "eleven", "jukebox", "creeper", "skeleton" are said right as written. The pauses are
shaped as a storyteller's (0.35 s default): longer after the opening line, the Sunny joke, the last gold line (the
cut to night), each meadow line (each is a picture that needs time: the creeper's step, the walk into the middle),
1.4 s after "Then it shot the creeper." (the fuse, the second arrow, the tip-over and the poof play in the silence),
after "Nobody asked." (the deadpan), 1.15 s after "Nobody moved." (the story: hold a full second after the words),
0.8 s before the last line, and 2.2 s of tail (the hold on Steve: 1.8 s of picture after "Vocals", then the 6 black
frames). Spoken length 48.4 s; with the pauses 65.08 s = 1562 frames, inside the 58-66 s asked. Delivered audio: 30 of
30 words after a silence within one frame of the clearly audible voice; 0 words estimated; -19.0 LUFS mono. Nobody
has listened to it (no audio playback here). HOW IT WAS SPOKEN: tools/narrate.py's one pass did not fit the 300 s
command limit on this shared machine (its 24 sentences took 280 s to synthesise before any word was timed), so
tools/crammys_narrate.py runs tools/narrate.narrate() itself in resumable parts with a disk cache in front of the
voice model and the recogniser (deterministic: the same result as one pass); `$TTS tools/narrate.py crammys --check`
says "current".

THE SHOT LENGTHS: every shot is 1.67 to 3.88 s (md11_skeleton 1.67 s and md10_creeper / md16_disc 1.71 s are the
shortest: "I found a skeleton." is the whole picture). md13_shot carries beats 13 AND 14 in one take (3.62 s), as
the story asks ("The same shot, held without a cut"). No cut inside a sentence; every cut is two frames before the
first word of its sentence (Sentence.cut).
THE CUT TO NIGHT: gd06_line -> rd07_chased is a hard cut from gold to moonlit blue on "I just get chased home every
night." (no dip: the story asks for a hard cut; the words "every night" cover it).
THE END: the last image holds 1.8 s after "Vocals" (the story: 1.5 s), then the last 6 frames are black (END_BLACK);
the Reel loops to frame 1.

GUARDED BUILD: each sequence file is imported, and each shot function called, inside a guard (see STRICT below):
a broken file or shot prints "[crammys] !!! ..." and gets a stand-in; CRAMMYS_STRICT=1 makes every error fatal.
"""
import importlib
import os
import sys
import traceback
import types

from engine import narration, shots
from films import crammys_common as CC
from films import lookdev as L

FPS = 24

# FIVE DIRECTORS EDIT FIVE FILES AT THE SAME TIME: a half-written sequence file must not stop the other four from
# building and scouting. So each sequence module is imported, and each shot function called, inside a guard: an
# error is printed loudly (module, shot, traceback) and that shot gets a plain stand-in (its location's camera,
# its torch levels, nobody in it); the rest of the film builds. CRAMMYS_STRICT=1 in the environment turns the guard
# off (the orchestrator's merge, the final render and the contact sheets of record run strict).
STRICT = os.environ.get("CRAMMYS_STRICT", "") not in ("", "0")
SEQUENCE_FILES = {"gold": "films.crammys_gold", "road": "films.crammys_road", "meadow": "films.crammys_meadow",
                  "jukebox": "films.crammys_jukebox", "finale": "films.crammys_finale"}
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
        print("[crammys] !!! SEQUENCE %s DOES NOT IMPORT: its shots get stand-ins\n%s" % (seq, BROKEN[seq]),
              file=sys.stderr)
        return None


# the stand-in of a shot whose function is missing or raised: its location's camera (films/crammys_common.py CAMS),
# nobody in it; the torch level follows the shot's own sky ("gold" or "night": the same in every build)
STAND_IN = {"gold": "gold_wide", "road": "gate", "meadow": "meadow_line", "jukebox": "jukebox", "finale": "stage_wide"}

NARRATION = {
    "voice": "am_michael", "speed": 1.0,
    "tail": 2.2,                                     # 1.8 s of picture after "Vocals", then END_BLACK
    "say": {"Zuri": "Zoo-ree"},                      # the voice read /zjuri/; the caption keeps "Zuri"
    "lines": [
        {"text": "In this town, everyone is musical except me.", "id": "b01", "pause": 0.45},           # the premise
        {"text": "Zuri keeps her note block on wool, so she plays guitar.", "id": "b02"},
        {"text": "Kai keeps his on gold, so he plays bells.", "id": "b03"},
        {"text": "Sunny keeps his on a pumpkin, and we don't talk about it.", "id": "b04", "pause": 0.55},   # the joke
        {"text": "Tonight was the Crammys, our biggest party of the year.", "id": "b05", "pause": 0.4},
        {"text": "Everyone performs, and I never have anything.", "id": "b06", "pause": 0.7},     # the last gold line: the hard cut to night
        {"text": "I just get chased home every night.", "id": "b07", "pause": 0.5},
        {"text": "But a creeper drops a music disc if a skeleton kills it.", "id": "b08", "pause": 0.55},
        {"text": "So I walked out past the last torch.", "id": "b09", "pause": 0.5},
        {"text": "I found a creeper.", "id": "b10", "pause": 0.6},     # its one slow step
        {"text": "I found a skeleton.", "id": "b11", "pause": 0.5},
        {"text": "I stood in the middle.", "id": "b12", "pause": 0.8},     # he looks left, right
        {"text": "The skeleton shot me.", "id": "b13", "pause": 0.5},
        {"text": "Then it shot me again.", "id": "b14", "pause": 0.6},
        {"text": "Then it shot the creeper.", "id": "b15", "pause": 1.4},     # the second arrow, the tip-over, the poof
        {"text": "A disc dropped.", "id": "b16", "pause": 0.7},
        {"text": "I ran to the stage with arrows still in me.", "id": "b17", "pause": 0.4},
        {"text": "Nobody asked.", "id": "b18", "pause": 0.8},     # deadpan
        {"text": "I put my disc in the jukebox.", "id": "b19"},
        {"text": "It was disc eleven, the broken one.", "id": "b20", "pause": 0.5},
        {"text": "It's just someone running away and breathing hard.", "id": "b21", "pause": 0.7},
        {"text": "Nobody moved.", "id": "b22", "pause": 1.15},   # the story: hold a full second
        {"text": "Kai said it sounded just like me coming home.", "id": "b23", "pause": 0.8},     # before the last line
        {"text": "I won Best Vocals.", "id": "b24"},
    ],
}

# The skies (films.lookdev.Stage: arguments of look.set_time / look.setup_compositor). render.py builds the film
# once per sky that has work. az = where the sun (at night the moon) stands, degrees counter-clockwise from east.
# Two entries, each for a reason (each costs one more build, about 3 s, per render command that has work in it):
SKIES = {
    # beats 1-6, the bandstand before the party: engine/music's golden sky, the set builder's "gold" (every gold
    # camera of the set and of engine/music was placed and proved under it): the sun low in the south-west, in front
    # of the west-facing stage and 120 degrees off the cameras that look east at it; the stage front sunlit, cast
    # shadows in the picture (CONTRACT: 60-120 degrees off the lens).
    "gold": dict(preset="golden", az=240.0, el=27.0, bloom=1.0, grade="warm"),
    # beats 7-24, the night: ONE moon for the lane, the gate, the meadow and the party (the story file's "second
    # module" predates several skies per film). The set builder's: the moon due EAST, low (az 0, el 21): on the
    # game's east-west arc opposite the sun that has just set. The stage faces west, so its front lies in the well's
    # moonshadow and the LANTERNS are the key on every face (the story's "night, lantern light"); in the frontal
    # wide (fn22) the moon stands over the bandstand; in the meadow the cameras look north with the moon at their
    # right (figures side-lit against the northern sky) and md11 looks east into it: the moon at the edge of the
    # skeleton's oak (the story's "moon behind the branches"). Every night still of the set passes palette_check
    # (crammys_set docstring). COMPARED SIDE BY SIDE with gold at the one cut between them (gd06 -> rd07, the
    # story's risk "the hard cut from golden hour to night could look like a mistake": "the first night frame must be
    # clearly moonlit blue"): out/test/crammys_scout_cut_gd06_rd07.png, the last gold frame (508) against the first
    # night frame (509) at 540x960 / 16 samples: mean luma 106 -> 59, the top band of sky rgb (174, 167, 177) -> (63,
    # 75, 144), stars, house_e's moonlit roof, Kai's lantern and the door torch the only warm lights: nobody can take
    # the night for a mistake. Measured on the stub: palette_check passes on md13_shot@921 (Steve's trousers min
    # channel 14 against the limit 12: the darkest face of the film so far, keep an eye on it) and rd17_run_back@1067
    # (25). No second night entry was needed: the meadow and the stage read under the same moon.
    "night": dict(preset="night", az=0.0, el=21.0, bloom=1.3, grade="cool"),
}

# The shot plan: (shot = the function's name, beat, sequence file, sky, where it starts). A start is a sentence
# id (the cut is Sentence.cut: two frames before its first word) or (sentence id, word): a cut inside the sentence
# before that word (nar.cut_before: never inside the word before it). One shot per beat, except beats 13 + 14: one
# take ("The same shot, held without a cut": md13_shot).
SHOTS = [
    ("gd01_everyone", 1, "gold", "gold", "b01"),
    ("gd02_zuri", 2, "gold", "gold", "b02"),
    ("gd03_kai", 3, "gold", "gold", "b03"),
    ("gd04_sunny", 4, "gold", "gold", "b04"),
    ("gd05_trophy", 5, "gold", "gold", "b05"),
    ("gd06_line", 6, "gold", "gold", "b06"),
    ("rd07_chased", 7, "road", "night", "b07"),             # the hard cut to night ("every night")
    ("jb08_eject", 8, "jukebox", "night", "b08"),
    ("rd09_torch", 9, "road", "night", "b09"),
    ("md10_creeper", 10, "meadow", "night", "b10"),
    ("md11_skeleton", 11, "meadow", "night", "b11"),
    ("md12_middle", 12, "meadow", "night", "b12"),
    ("md13_shot", 13, "meadow", "night", "b13"),             # beats 13 AND 14: one take
    ("md15_kill", 15, "meadow", "night", "b15"),
    ("md16_disc", 16, "meadow", "night", "b16"),
    ("rd17_run_back", 17, "road", "night", "b17"),
    ("jb18_nobody_asked", 18, "jukebox", "night", "b18"),
    ("jb19_to_jukebox", 19, "jukebox", "night", "b19"),
    ("jb20_eleven", 20, "jukebox", "night", "b20"),
    ("fn21_running", 21, "finale", "night", "b21"),
    ("fn22_nobody_moved", 22, "finale", "night", "b22"),
    ("fn23_kai", 23, "finale", "night", "b23"),
    ("fn24_vocals", 24, "finale", "night", "b24"),
]
BEATS = {"md13_shot": (13, 14)}                # a shot that carries more than one beat (default: its own beat)
SKY_CHANGE = {}                                # no sky changes inside a shot
DIPS = {}                                      # no dips: the cut to night is a hard cut, as the story asks
END_BLACK = 6      # the last 6 frames (0.25 s) are black (an encoder dip with no way back), after the hold on Steve
#                    with the totem; the Reel then loops to frame 1


def timeline(nar):
    """The shot plan with its frames, from the spoken narration: [crammys_common.ShotInfo] in film order."""
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
        row = CC.ShotInfo(name=name, beat=beat, beats=BEATS.get(name, (beat,)), sequence=seq, sky=sky,
                          sentence=sent, frame_start=a, frame_end=b, frames=b - a + 1,
                          seconds=(b - a + 1) / float(nar.fps), words=words)
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
    default, engine.narration captions(cuts=None)). Inside md13_shot (two sentences, one take) the last word of
    "The skeleton shot me." then clears on the second sentence's cut, two frames before "Then", as at every other
    sentence start of the film (narration.prove checks exactly that)."""
    return sorted({r.frame_start for r in rows[1:]} | {s.cut for s in nar.sentences[1:]})


def build(scene, sky=None):
    """Build the film with `sky` active (None: the first of SKIES):
    {"film", "captions", "narration", "stage", "context"}."""
    # 1. the voice: stops here (NarrationError) if narration/crammys.json was not spoken from NARRATION
    nar = narration.load(__name__, NARRATION, fps=FPS)
    print(nar.summary())
    rows = timeline(nar)

    # 2. the set, the stage (it builds the active sky), the shared context (the band, the parts, the anchors)
    v = CC.build_set(scene)
    film = shots.Film(scene, fps=FPS)
    st = L.Stage(scene, film, v, skies=SKIES, sky=sky)
    C = CC.Crammys(st, nar, {r.name: r for r in rows})

    # 3. every shot of the plan, in order, tagged with its sky
    for r in rows:
        s = st.shot(r.name, nar.seconds(r.frames), sky=r.sky)
        assert (s.frame_start, s.frame_end) == (r.frame_start, r.frame_end), (r, s.frame_start, s.frame_end)
        if r.change is not None:
            st.sky_change(r.change, r.sky_after)
        C.shots[r.name] = s
    assert film.shots[-1].frame_end == nar.frames

    # 4. the pictures: each shot's function from its sequence file, IN TIMELINE ORDER (characters and the set's
    #    moving parts are keyed in frame order); particles never live across a change of place. A sequence that
    #    does not import, or a shot function that raises, gets the stand-in (see STRICT above) and is named in BROKEN.
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
                raise AttributeError("films/crammys_%s.py has no function %s" % (r.sequence, r.name))
            fn(st, s, C, nar)
        except Exception:
            if STRICT:
                raise
            BROKEN[r.name] = traceback.format_exc()
            print("[crammys] !!! SHOT %s (%s) FAILED: it gets a stand-in\n%s" % (r.name, r.sequence, BROKEN[r.name]),
                  file=sys.stderr)
            C.cam(s, STAND_IN[r.sequence], handheld=0.004)
            C.lights(s, r.sky)
        C.close_holds()            # the shot's C.hold ends, keyed after everything it did with those hands
        before = r.sequence
    if BROKEN:
        print("[crammys] !!! %d part(s) built as stand-ins: %s" % (len(BROKEN), ", ".join(BROKEN)), file=sys.stderr)
    # THE LAST LANTERN is placed once, by Alex in gd05 (the gold sequence's); if gd05 did not place it (a stand-in),
    # it appears at 0.9 of gd05, so that the north post never has it before beat 5 (LastLantern stands from frame 1
    # unless placed)
    if C.bd.last_lantern.placed is None:
        g = C.T["gd05_trophy"]
        C.bd.last_lantern.place(g.frame_start + int(round(0.9 * (g.frame_end - g.frame_start))))

    # 5. the end in black, then hide everybody outside their shots
    for name, kw in DIPS.items():
        st.dip(C.T[name].frame_start, **kw)
    st.dip(nar.frames - END_BLACK + 1, out=0, hold=END_BLACK, back=0)
    st.finish()

    # 6. this film's final quality (a measured study): 540x960 at 16 samples, upscaled to 1080x1920 at encode
    scene.render.resolution_x, scene.render.resolution_y = CC.FINAL_RES
    scene.cycles.samples = CC.FINAL_SAMPLES

    # 7. the captions: one word at a time; a word never stays on past ANY cut (nor past a sentence's start)
    caps = nar.captions(cuts=caption_cuts(nar, rows))
    return {"film": film, "captions": caps, "narration": nar, "stage": st, "context": C}
