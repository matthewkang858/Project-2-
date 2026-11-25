"""The Hello: 63.8 narrated seconds, 22 sentences, 24 shots, three skies. Told by a baby villager.

    "In this town, the player used to protect us. ... He crouched, once, and he stayed down. The player had blue
     eyes."      (stories/herobrine.json: the story, the picture of every beat, the risks and their fallbacks)

This file is the lead director's: the narration (the clock of the film), the skies, the shot plan and build().
The pictures are made by five sequence files, one location each, one function per shot (the contract and
everything they share: films/hello_common.py):

    films/hello_square.py      sq01 sq09 sq10 sq11                 village square, golden hour
    films/hello_door_night.py  dn02 dn18 dn19                      the child's door at night
    films/hello_interior.py    in03 in16 in17                      inside the child's house
    films/hello_door_gold.py   dg04 dg05 dg15_a/b/c dg20 dg21 dg22 the child's door in golden light
    films/hello_meadow.py      me06 me07 me08 me12 me13 me14       exit gate, meadow road, forest wall, the signs

    $TTS tools/narrate.py hello --check                  # the voice is spoken and committed: narration/hello.*
    $BPY -m render hello --still 12.0 --zones            # one frame (540x960, 16 samples); each still costs one
                                                         #   build of its sky
    $BPY -m render hello --sheet 12                      # out/test/hello_sheet.png (all three skies)
    $BPY -m tools.hello_timeline                         # the shot plan with frames and words (no scene is built)
    $BPY -m render hello --frames dn02_fight --res 270x480 --samples 8 --threads 2     # one shot as a preview
    $BPY -m render hello --frames all --max-seconds 240  # FINAL frames: this film's final quality is 540x960 at
                                                         #   16 samples (set in build(); never pass --res/--samples)

THE VOICE IS COMMITTED. Changing a word, a pause, the voice or the speed below makes narration/hello.json stale
(build stops) and, once spoken again, moves every cut after it: do not, unless the orchestrator says so.
"""
from engine import narration, shots
from films import hello_common as HC
from films import hello_door_gold, hello_door_night, hello_interior, hello_meadow, hello_square
from films import lookdev as L

FPS = 24

# The narration: stories/herobrine.json word for word, one entry per sentence (161 words). Pauses are after the
# sentence, voice to voice; default 0.35 s. Spoken length 47.1 s; with these pauses the film is 63.79 s = 1531 frames.
NARRATION = {
    "voice": "am_michael", "speed": 1.0,
    "tail": 2.0,                                    # the last image holds two seconds after the last word
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
        {"text": "He crouched, once, and he stayed down.", "id": "b21", "pause": 1.5},   # the second of silence
        {"text": "The player had blue eyes.", "id": "b22"},
    ],
}

# The skies (films.lookdev.Stage: arguments of look.set_time / look.setup_compositor). render.py builds the film
# once per sky that has work. az = where the sun (at night the moon) stands, degrees counter-clockwise from east.
SKIES = {
    # the village in golden light: square (1, 9-11), the child's door (4, 5, 15, 20-22), the end of beat 3.
    # A low sun in the south-west: house_a's door faces west, so its front, the plaza before it and the house
    # fronts north of it are in the sun (with the look-dev sun, azimuth 62, that whole side is in the house's own
    # shadow), and it comes through the south windows onto the beds when the night ends.
    "gold": dict(preset="golden", az=215.0, el=24.0, bloom=1.0, grade="warm"),
    # the meadow (6-8, 12-14): the look-dev sun in the north-east, behind the wood, and NO distance haze: with the
    # preset's haze the forest wall 35 blocks away is dark brown, without it the gaps between the trunks are black
    # (engine/sets.py, measured). All of hello_set's proof stills were made under exactly this sky.
    "meadow": dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm", haze=0.0),
    # night at the door and in the house (2, 3, 16-19): the look-dev night, the moon in the west over the plaza,
    # so the house front has a cool fill under the warm key of its two door torches.
    "night": dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool"),
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
    ("me07_return", 7, "meadow", "meadow", "b07"),             # after a dip to black (DIPS)
    ("me08_nohello", 8, "meadow", "meadow", "b08"),
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

MODULES = {"square": hello_square, "door_night": hello_door_night, "interior": hello_interior,
           "door_gold": hello_door_gold, "meadow": hello_meadow}


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
    #    frame order); particles never live across a change of place
    before = None
    for r in rows:
        if before is not None and r.sequence != before:
            C.time_jump(r.frame_start)
        getattr(MODULES[r.sequence], r.name)(st, C.shots[r.name], C, nar)
        before = r.sequence

    # 5. the dips to black (the encoder's), then hide everybody outside their shots
    for name, kw in DIPS.items():
        st.dip(C.T[name].frame_start, **kw)
    st.finish()

    # 6. this film's final quality (a measured study): 540x960 at 16 samples, upscaled to 1080x1920 at encode
    scene.render.resolution_x, scene.render.resolution_y = HC.FINAL_RES
    scene.cycles.samples = HC.FINAL_SAMPLES

    # 7. the captions: one word at a time; a word never stays on past ANY cut (the jump cuts of beat 15 included)
    caps = nar.captions(cuts=[r.frame_start for r in rows[1:]])
    return {"film": film, "captions": caps, "narration": nar, "stage": st, "context": C}
