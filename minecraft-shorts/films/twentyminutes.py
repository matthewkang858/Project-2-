"""Twenty Minutes: 64.25 narrated seconds (1542 frames), 24 sentences, 25 shots, one sky. Told by a baby villager who grows
up during the film (a baby villager grows up in twenty minutes: a Minecraft day).

    "In this village, everyone is afraid of the player. ... I'm afraid of the zombie. Apparently that counts."
                 (stories/ironfarm.json: the story, the picture of every beat, the risks and their fallbacks;
                  SHOTLISTS.md has the same as a table)

This file is the lead director's: the narration (the clock of the film), the sky, the shot plan, the second bed
(BED2_FROM) and build(). The pictures are made by five sequence files, one place each, one function per shot (the
contract, the set, the places, the shared cameras, the cast and the helpers: films/twentyminutes_common.py; the set
itself: films/twentyminutes_set.py, built on engine/towers.py):

    films/twentyminutes_square.py  sq01 sq02 sq03 sq04_tilt sq04_hat sq05   the square (the player, the push, the
                                                                            tilt to the tower, the straw hat at the
                                                                            glass) and the foot of the tower
    films/twentyminutes_cell.py    ce06 ce07 ce08 ce23                      in the pod: the bed and the zombie, the
                                                                            arms that cannot reach, the fear (the
                                                                            window camera, twice)
    films/twentyminutes_golem.py   gm09 gm10 gm11 gm12 gm24                 the platform: the golem comes, again,
                                                                            the water and the lava, its iron in the
                                                                            hopper, and the last golem
    films/twentyminutes_gap.py     gp13 gp14 gp15 gp20 gp22                 the dirt staircase and the gap: the baby
                                                                            climbs in, the grown narrator cannot get
                                                                            out, the player breaks the top step
    films/twentyminutes_grow.py    gr16 gr17 gr18 gr19 gr21                 Mom and the baby: never looked at, twenty
                                                                            minutes, the bounce, growing up, the count

    $TTS tools/narrate.py twentyminutes --check          # the voice is spoken and committed: narration/twentyminutes.*
    $TTS tools/twentyminutes_narrate.py                  # (how it was spoken: tools/narrate.py resumable, see below)
    $BPY -m tools.twentyminutes_timeline [--check|--json]    # the shot plan with frames and words; caption proof
    $BPY -m tools.twentyminutes_shots render --shots gm09_golem --frame 600 --zones    # stills of single shots
                                                         #   (540x960, 16 samples by default)
    $BPY -m tools.twentyminutes_shots tiles; ... sheet   # one tile per shot -> out/test/twentyminutes_shots_sheet.png
    $BPY -m tools.twentyminutes_geo ce23_afraid:1450     # heads, face pixels, angle to the lens, what blocks them
    $BPY -m tools.twentyminutes_palette 1450             # tools/palette_check on one frame at final quality
    $BPY -m tools.twentyminutes_probe [events looks heroes cams missing]   # the BUILT film measured, no render: every
                                                         #   event's frame, every look vs the zombie, hero boxes
    $BPY -m render twentyminutes --still 12.0 --zones    # one frame through render.py
    $BPY -m render twentyminutes --frames gm11_lava --res 270x480 --samples 7 --threads 2    # one shot as a
                                                         #   preview (each sequence its own sample count: _common)
    $BPY -m render twentyminutes --frames all --max-seconds 240    # FINAL frames: this film's final quality is
                                                         #   540x960 at 16 samples (set in build(); never --res)

THE VOICE IS COMMITTED (am_michael, speed 1.0; the last line "Apparently that counts." at 0.9, as the series' endings:
the storyteller slows down for the punchline; "lives" respelled "livs" for the voice only: the phonemiser said
/laɪvz/, the noun; the caption keeps "lives"). Changing a word, a pause, the voice or a speed below makes
narration/twentyminutes.json stale (build stops) and, once spoken again, moves every cut after it: do not, unless the
orchestrator says so. Spoken twice by the lead, through tools/twentyminutes_narrate.py: tools/narrate.py's own narrate()
with its two deterministic steps (the voice per sentence, the recogniser's second opinion per sentence) memoised on
disk, so that it can be resumed (one uninterrupted run of tools/narrate.py took more than 300 s on this machine at load
18-19, 8-15 s a sentence for the voice alone; `$TTS tools/narrate.py twentyminutes --check` says "current"). First
63.83 s: the caption check failed, "the" of "at the top" on screen for ONE frame (the voice said "at the" in 0.15 s
and engine.narration's min_frames cannot lengthen it there); so "My mom lives ..." at 0.95 (its words 2-3 frames
each), its pause 0.5 -> 0.65 (the straw hat after the cut holds 1.75 s) and the pause after "The water pushes it into
the lava." 0.75 -> 0.95 (the puff after the drop): 64.25 s = 1542 frames, inside the 58-66 s asked. No word was cut
(161). Pronunciation checked with --phonemes: "lives" respelled (above); grownups, staircase, Childhood, Apparently,
zombie, golem, poppies said right as written. The recogniser hears "fit." 115 ms later than the voice model's timing
(narrate.py CHECK; its second opinion runs EARLY inside speech as a rule): the model's timing is used. Nobody has
listened to it (no audio playback here): the pace was judged by measurement (3.46 words/s while speaking).

GUARDED BUILD: each sequence file is imported, and each shot function called, inside a guard (see STRICT below): a
broken file or shot prints "[twentyminutes] !!! ..." and gets a stand-in; TWENTYMINUTES_STRICT=1 makes errors fatal.

THE EDIT (the story's devices, designed into the plan below)
  * ONE SHOT PER BEAT, 25 shots, 1.75 to 3.67 s each (none under 1.2 s, none over 5 s), with two exceptions:
  * BEAT 4 IS TWO SHOTS, cut inside the line before "glass" (230): sq04_tilt (CAMS "tilt": a real, even tilt of 11.7
    degrees from the ground by the well's wall past the baby's shoulder up to the tower, from CAMS "plaza"'s lens,
    ending 2.5 degrees above its aim with the pod in the safe area: "My mom lives at the top of his") and sq04_hat (the
    200 mm straw hat at the glass: "glass tower now"): the story's own fallback, Mom is a few pixels from the square.
  * BEATS 23 AND 24: ce23_afraid (the window camera) is HELD through "Apparently that" ("Same shot, held"), and the cut
    falls ON "counts" (1473: "that" runs into it, so the cut is on the word's own first frame) to gm24_counts on
    CAMS "platform": the story's own fallback for the last line ("cut on that word to the low-angle platform framing
    of line 9 with the grown narrator now among the shapes behind the glass"). The platform is empty for 10 frames,
    then the golem appears out of nothing (1483), turns its head, steps and begins to slide; 2.3 s after the word the
    picture goes black (END_BLACK) before it reaches the rim.
  * THE JUMP CUT gm09 -> gm10: the identical framing (CAMS "platform", the same handheld seed), the platform EMPTY for
    15 frames while "It comes" is spoken (592-606), a new golem on the same block ON "every" (607), its step on
    "time".
  * THE LOCKED FRAMING gr17 / gr19 (CAMS "grow", the same handheld seed): Mom as the height ruler; the baby becomes
    the grown narrator in one frame ON "ended" (1178): 35 frames of the baby before it in gr19, 32 after it.
  * THE SECOND BED: P.bed2 is in every shot from gr21_count on (BED2_FROM: build() st.use's it), never before; it
    appears ON the frame gr21 gives C.bed2_at (the stub: 1304, on Steve's swing after "brought").
  * THE TOP STEP: never registered with the Stage: it stands in gp13-gp20 and gp22 breaks it.
  * NO DIP TO BLACK inside the film: one day, one light (SKIES); the twenty minutes pass in the words and the swap.
  * THE END: "counts" is held 2.0 s, then the last 6 frames are black (1537-1542, END_BLACK); the Reel loops to frame 1.
"""
import importlib
import os
import sys
import traceback
import types

from engine import narration, shots
from films import lookdev as L
from films import twentyminutes_common as TC

FPS = 24

# FIVE DIRECTORS EDIT FIVE FILES AT THE SAME TIME: a half-written sequence file must not stop the other four from
# building and scouting. So each sequence module is imported, and each shot function called, inside a guard: an error
# is printed loudly (module, shot, traceback) and that shot gets a plain stand-in (its location's camera, its torch
# levels, nobody in it); the rest of the film builds. TWENTYMINUTES_STRICT=1 in the environment turns the guard off
# (the orchestrator's merge, the final render and the contact sheets of record run strict).
STRICT = os.environ.get("TWENTYMINUTES_STRICT", "") not in ("", "0")
SEQUENCE_FILES = {"square": "films.twentyminutes_square", "cell": "films.twentyminutes_cell",
                  "golem": "films.twentyminutes_golem", "gap": "films.twentyminutes_gap",
                  "grow": "films.twentyminutes_grow"}
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
        print("[twentyminutes] !!! SEQUENCE %s DOES NOT IMPORT: its shots get stand-ins\n%s" % (seq, BROKEN[seq]),
              file=sys.stderr)
        return None


# The narration: stories/ironfarm.json word for word, one entry per sentence (161 words). Pauses are after the
# sentence, voice to voice; default 0.35 s. Spoken length 46.6 s; with these pauses (15.15 s), the lead 0.3 s and the
# tail 2.3 s the film is 64.25 s = 1542 frames. The story's risk "LENGTH" asked to open the pauses after the short
# lines so that each shot runs about two seconds, a second after "ended" and a two-second tail: done (the comments).
NARRATION = {
    "voice": "am_michael", "speed": 1.0,
    "tail": 2.3,                                    # the last image holds two seconds after the last word, then the
    #                                                 last 6 frames are black (END_BLACK: the story's cut to black)
    "say": {"lives": "livs"},                       # "My mom lives at the top": the verb (the voice said /laɪvz/)
    "lines": [
        {"text": "In this village, everyone is afraid of the player.", "id": "b01", "pause": 0.4},
        {"text": "I'm not.", "id": "b02", "pause": 1.15},          # opened: the shot runs about two seconds
        {"text": "He only takes grownups.", "id": "b03", "pause": 0.8},     # opened: the push and the baby's run
        {"text": "My mom lives at the top of his glass tower now.", "id": "b04", "pause": 0.65, "speed": 0.95},
        #   (0.95: at 1.0 "at the top" came out so fast that the caption "the" was on screen for ONE frame (213);
        #    the pause opened from 0.5 so the straw hat after the cut holds 1.7 s)
        {"text": "I would wave, but our arms don't do that.", "id": "b05", "pause": 0.6},   # a beat on the stillness
        {"text": "He gave her a bed, and a zombie in a box.", "id": "b06", "pause": 0.35},
        {"text": "The zombie can't reach her.", "id": "b07", "pause": 0.45},
        {"text": "It doesn't have to.", "id": "b08", "pause": 0.95},        # opened: the fear, then the golem
        {"text": "When we get scared, an iron golem comes to save us.", "id": "b09", "pause": 0.35},
        {"text": "It comes every time.", "id": "b10", "pause": 0.65},       # opened: the jump cut's new golem steps
        {"text": "The water pushes it into the lava.", "id": "b11", "pause": 0.95},   # the slide, the drop, the puff
        {"text": "He takes the iron and leaves the poppies.", "id": "b12", "pause": 0.4},
        {"text": "He never took down his dirt staircase.", "id": "b13", "pause": 0.5},
        {"text": "At the top there's a gap, one block high.", "id": "b14", "pause": 0.4},
        {"text": "Grownups don't fit, but I do.", "id": "b15", "pause": 0.55},
        {"text": "Mom never looks at me, only at the zombie.", "id": "b16", "pause": 0.7},   # the story turns: the
        #                                                                                    clock starts
        {"text": "Childhood here lasts twenty minutes.", "id": "b17", "pause": 0.5},
        {"text": "I spent mine with her.", "id": "b18", "pause": 0.9},      # the bounce, then beside her
        {"text": "I was still inside when it ended.", "id": "b19", "pause": 1.0},     # a second held after "ended"
        {"text": "Now I don't fit.", "id": "b20", "pause": 0.85},           # opened: he stops at the plug
        {"text": "He counted us twice, then brought one more bed.", "id": "b21", "pause": 0.6},
        {"text": "I'm still not afraid of the player.", "id": "b22", "pause": 0.6},
        {"text": "I'm afraid of the zombie.", "id": "b23", "pause": 0.75},  # before the last line
        # the last line a tenth slower: the storyteller slows down for the punchline (the series' endings)
        {"text": "Apparently that counts.", "id": "b24", "speed": 0.9},
    ],
}

# The sky (films.lookdev.Stage: arguments of look.set_time / look.setup_compositor). render.py builds the film once
# per sky that has work. ONE entry, on purpose:
SKIES = {
    # every shot, every place: the set's golden hour (films/twentyminutes_set.py SKIES; every scouting still of the set
    # and every proof of engine/towers.py was made under exactly this sky). THE STORY ASKS FOR ONE SKY ("golden hour,
    # sun about 27 degrees up ... a Minecraft day is twenty minutes, so the sun is truly back in the same place when
    # the narrator grows up"): the twenty minutes of the childhood are one whole day, and the light coming back the
    # same is the joke's arithmetic. The story's fallback for a change of light (a dusk second half from the growing-up
    # shot on) is NOT taken: engine/towers.py measured the glass pod ten blocks up under the look-dev dusk sun
    # (elevation 5) failing tools/palette_check (stone G/R 0.90-0.91, villager skin saturation 0.57), and the passing
    # of the childhood is carried by the narration, the locked framing of gr17 / gr19 and the one-frame swap.
    # The sun stands in the north-north-east (az 62: degrees counter-clockwise from east), elevation 27: the pod's
    # villagers face EAST (the zombie's cell) and are lit by it through the glass; the plaza camera looks north-west
    # with the sun about 85 degrees off its axis (side light, cast shadows); the back of the tower (the dirt zigzag)
    # faces it; from CAMS "platform" it stands at the upper left behind the golem's head ("huge against the gold sky").
    # Not compared with any other sky: there is no other.
    "gold": dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm"),
}

# The shot plan: (shot = the function's name, beat, sequence file, sky, where it starts). A start is a sentence id (the
# cut is Sentence.cut: two frames before its first word) or (sentence id, word): a cut inside the sentence before that
# word (nar.cut_before: never inside the word before it). One shot per beat, except beat 4 (two: the tilt, then the
# straw hat on the 200 mm lens, the story's own fallback) and beats 23 + 24 (the window shot of 23 is HELD through
# "Apparently that", and the cut on "counts" goes to the platform framing of beat 9: the story's own fallback for the
# last line).
SHOTS = [
    ("sq01_afraid", 1, "square", "gold", "b01"),
    ("sq02_imnot", 2, "square", "gold", "b02"),
    ("sq03_grownups", 3, "square", "gold", "b03"),
    ("sq04_tilt", 4, "square", "gold", "b04"),
    ("sq04_hat", 4, "square", "gold", ("b04", "glass")),     # the cut inside the line: the straw hat at the glass
    ("sq05_wave", 5, "square", "gold", "b05"),
    ("ce06_bed", 6, "cell", "gold", "b06"),
    ("ce07_reach", 7, "cell", "gold", "b07"),
    ("ce08_scared", 8, "cell", "gold", "b08"),
    ("gm09_golem", 9, "golem", "gold", "b09"),
    ("gm10_again", 10, "golem", "gold", "b10"),              # the jump cut on the identical framing
    ("gm11_lava", 11, "golem", "gold", "b11"),
    ("gm12_iron", 12, "golem", "gold", "b12"),
    ("gp13_stairs", 13, "gap", "gold", "b13"),
    ("gp14_gap", 14, "gap", "gold", "b14"),
    ("gp15_fit", 15, "gap", "gold", "b15"),
    ("gr16_mom", 16, "grow", "gold", "b16"),
    ("gr17_twenty", 17, "grow", "gold", "b17"),
    ("gr18_bounce", 18, "grow", "gold", "b18"),
    ("gr19_ended", 19, "grow", "gold", "b19"),               # CAMS "grow" again: the swap on "ended"
    ("gp20_nofit", 20, "gap", "gold", "b20"),
    ("gr21_count", 21, "grow", "gold", "b21"),               # the second bed appears here (BED2_FROM)
    ("gp22_step", 22, "gap", "gold", "b22"),
    ("ce23_afraid", 23, "cell", "gold", "b23"),              # held through "Apparently that" (beats 23 and 24)
    ("gm24_counts", 24, "golem", "gold", ("b24", "counts")),  # the cut on "counts": CAMS "platform", the hold, black
]
BEATS = {"ce23_afraid": (23, 24)}              # a shot that carries more than one beat (default: its own beat)
SKY_CHANGE = {}                                # no sky change inside a shot
DIPS = {}                                      # no dip to black inside the film
BED2_FROM = "gr21_count"                       # P.bed2 is shown in this shot and every shot after it (never before);
#                                                gr21 makes it appear on Steve's swing: C.bed2_at(frame)
END_BLACK = 6      # the story's "then cut to black": the last 6 frames (0.25 s) are black (an encoder dip with no
#                    way back), after the hold on the golem; the Reel then loops to frame 1


def timeline(nar):
    """The shot plan with its frames, from the spoken narration: [twentyminutes_common.ShotInfo] in film order."""
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
        row = TC.ShotInfo(name=name, beat=beat, beats=BEATS.get(name, (beat,)), sequence=seq, sky=sky,
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
    default, engine.narration captions(cuts=None)). Inside ce23_afraid (two sentences, one held shot) the last word of
    "I'm afraid of the zombie." then clears on the next sentence's cut, two frames before "Apparently", as at every
    other sentence start of the film (narration.prove checks exactly that)."""
    return sorted({r.frame_start for r in rows[1:]} | {s.cut for s in nar.sentences[1:]})


def build(scene, sky=None):
    """Build the film with `sky` active (None: the first of SKIES):
    {"film", "captions", "narration", "stage", "context"}."""
    # 1. the voice: stops here (NarrationError) if narration/twentyminutes.json was not spoken from NARRATION
    nar = narration.load(__name__, NARRATION, fps=FPS)
    print(nar.summary())
    rows = timeline(nar)

    # 2. the set, the stage (it builds the active sky), the shared context (the farm's parts; the second bed
    #    registered with the Stage, so it is hidden wherever no shot uses it)
    v = TC.build_set(scene)
    film = shots.Film(scene, fps=FPS)
    st = L.Stage(scene, film, v, skies=SKIES, sky=sky)
    C = TC.TwentyMinutes(st, nar, {r.name: r for r in rows})

    # 3. every shot of the plan, in order, tagged with its sky
    for r in rows:
        s = st.shot(r.name, nar.seconds(r.frames), sky=r.sky)
        assert (s.frame_start, s.frame_end) == (r.frame_start, r.frame_end), (r, s.frame_start, s.frame_end)
        if r.change is not None:
            st.sky_change(r.change, r.sky_after)
        C.shots[r.name] = s
    assert film.shots[-1].frame_end == nar.frames

    # 4. the pictures: each shot's function from its sequence file, IN TIMELINE ORDER (characters, the golem and the
    #    farm's parts are keyed in frame order); particles never live across a change of place. The second bed is in
    #    every shot from BED2_FROM on. A sequence that does not import, or a shot function that raises, gets the
    #    stand-in (see STRICT above) and is named in BROKEN.
    BROKEN.clear()
    modules = {seq: _import(seq) for seq in SEQUENCE_FILES}
    before = None
    bed2_on = False
    for r in rows:
        if before is not None and r.sequence != before:
            C.time_jump(r.frame_start)
        s = C.shots[r.name]
        if r.name == BED2_FROM:
            bed2_on = True
        if bed2_on:
            st.use(s, C.P_.bed2)
        fn = getattr(modules[r.sequence], r.name, None) if modules[r.sequence] is not None else None
        try:
            if fn is None:
                raise AttributeError("films/twentyminutes_%s.py has no function %s" % (r.sequence, r.name))
            fn(st, s, C, nar)
        except Exception:
            if STRICT:
                raise
            BROKEN[r.name] = traceback.format_exc()
            print("[twentyminutes] !!! SHOT %s (%s) FAILED: it gets a stand-in\n%s" % (r.name, r.sequence,
                                                                                    BROKEN[r.name]), file=sys.stderr)
            C.cam(s, TC.STAND_IN[r.sequence], handheld=0.004)
            C.lights(s, "square" if r.sequence == "square" else "tower")
        if r.name == BED2_FROM and C.bed2_frame is None:
            f = nar.at("bed", sentence=r.sentence.id)
            print("[twentyminutes] !!! %s did not place the second bed (C.bed2_at): it appears on \"bed\" (%d)"
                  % (r.name, f), file=sys.stderr)
            C.bed2_at(f)
        before = r.sequence
    if BROKEN:
        print("[twentyminutes] !!! %d part(s) built as stand-ins: %s" % (len(BROKEN), ", ".join(BROKEN)),
              file=sys.stderr)

    # 5. the dips to black (the encoder's), the end in black, then hide everybody outside their shots
    for name, kw in DIPS.items():
        st.dip(C.T[name].frame_start, **kw)
    st.dip(nar.frames - END_BLACK + 1, out=0, hold=END_BLACK, back=0)
    st.finish()

    # 6. this film's final quality (a measured study): 540x960 at 16 samples, upscaled to 1080x1920 at encode
    scene.render.resolution_x, scene.render.resolution_y = TC.FINAL_RES
    scene.cycles.samples = TC.FINAL_SAMPLES

    # 7. the captions: one word at a time; a word never stays on past ANY cut (nor past a sentence's start)
    caps = nar.captions(cuts=caption_cuts(nar, rows))
    return {"film": film, "captions": caps, "narration": nar, "stage": st, "context": C}
