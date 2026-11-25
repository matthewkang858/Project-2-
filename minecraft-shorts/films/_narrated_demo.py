"""Narrated demo: 10.5 seconds, four sentences, four shots, the narrator's voice. THE TEMPLATE for a narrated film.

    "In this village, everyone has a job. / The player trades with all of them. /
     But nobody trades with a nitwit. / So today, I'm leaving."

The voice is the clock. The text below is spoken once by a separate command; from then on every caption, every
cut and the film's length come from the measured voice, never from a guess:

    $TTS tools/narrate.py _narrated_demo --phonemes      # how the voice will say it (check Minecraft words first)
    $TTS tools/narrate.py _narrated_demo                 # -> narration/_narrated_demo.wav + .json (commit both);
                                                         #    prints the length against one minute
    $BPY -m render _narrated_demo --sheet 8              # look at it: out/test/_narrated_demo_sheet.png
    $BPY -m render _narrated_demo --frames all --res 360x640 --samples 8 --threads 2 --max-seconds 240
                                                         # preview frames; repeat until none are left
    $BPY -m render _narrated_demo --res 360x640 --samples 8 --encode
                                                         # -> out/preview/_narrated_demo_360x640_8spp.mp4, with the
                                                         #    narration muxed in (render.py finds narration/<film>.wav)
    $BPY -m tools.narration_sync _narrated_demo out/preview/_narrated_demo_360x640_8spp.mp4
                                                         # proof: every caption against the voice in the encoded file
  (a final film: the same without --res / --samples -> out/frames/<film>/ and out/<film>.mp4. A one-minute film is
   encoded in 10 s parts: `--encode` may end with exit code 4, "run the same command again"; it continues.)

Writing the text (engine/narration.py, WRITING FOR THE VOICE): one minute holds 140 to 165 words with this voice;
numbers, times and abbreviations are written as words; one entry of "lines" is one sentence.

Edit a sentence, a pause or the voice and `narration.load` stops the build until tools/narrate.py has spoken the
new text: a film can never be rendered against audio it does not match. The shots are the look-dev shots of
films/lookdev.py (cheap, already checked); this file only adds the time.
"""
from engine import look, narration, shots, village
from films import lookdev as L

FPS = 24

# The narration: one entry = one sentence, spoken on its own. A plain literal (tools/narrate.py reads it with ast).
NARRATION = {
    # "voice": "am_michael", "speed": 1.0,      # defaults: engine.narration.DEFAULT_VOICE, 1.0
    "tail": 1.2,                                # the last picture holds this long after the last word
    "lines": [
        "In this village, everyone has a job.",                 # default pause after a sentence: 0.35 s
        "The player trades with all of them.",
        ("But nobody trades with a nitwit.", 0.8),              # (sentence, pause): a beat on his face before the last line
        {"text": "So today, I'm leaving.", "id": "leave"},      # an id to find the sentence by
    ],
}

SKY = dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm")       # the look-dev golden hour


def shot_job(st, s):
    """The farmer on her way past the big house (films.lookdev.shot_villager, made for one second and held here
    for three). Two changes for the longer hold: she strolls at 0.78 blocks a second, and the camera rides at
    1.25 instead of 0.80, level with her face. As it was, the low camera followed her behind the tall grass
    after a second and a half and the tufts covered the lower third of the frame."""
    f0 = s.frame_start
    farmer = st.actor("ada", "farmer")
    a, b = (3.05, 22.95, 0.0), (6.6, 22.95, 0.0)
    farmer.place(f0 - 26, a, L.yaw_to(a, b))
    farmer.walk(f0 - 26, [a, b], speed=0.78)
    st.use(s, farmer)
    s.lens(42, 2.8)
    s.follow(farmer.root, (2.3, 3.0, 1.25), (2.0, 3.15, 1.25), look_offset=(-0.08, 0.0, 1.22))
    s.focus(farmer.head)
    s.handheld(0.012, seed=11)
    st.hero(s, "farmer", farmer)
    st.lights(s, scale=1.0, near=st.v.anchors["exit_gate"], radius=10.0)


def shot_leave(st, s):
    """The nitwit walks out the exit road (films.lookdev.shot_meadow, with a twin of the nitwit: he is in the
    shot before, and a character that is in two consecutive shots must not be keyed before the cut)."""
    f0 = s.frame_start
    nit = st.actor("nitwit_out", "nitwit")
    road = [(0.5, 25.5, -0.06), (0.6, 31.0, -0.06), (0.4, 38.0, -0.06), (0.5, 46.0, 0.0)]
    nit.place(f0 - 40, road[0], L.yaw_to(road[0], road[1]))
    nit.walk(f0 - 40, road)
    here, end = nit.pos_at(f0 + 12), nit.pos_at(s.frame_end)
    nit.look_at(f0, (here.x - 4.0, here.y + 0.6, 1.9), ease=0)             # his profile against the sky ...
    nit.look_at(f0 + 12, (end.x - 6.0, end.y + 0.9, 4.0), ease=10)         # ... held to the last frame
    st.use(s, nit)
    s.lens(28, 3.2)
    s.follow(nit.root, (-2.62, -3.12, 0.78), (-2.95, -3.80, 0.74), look_offset=(0.50, 0.30, 1.76))
    s.focus(nit.head)
    s.handheld(0.012, seed=23)
    st.hero(s, "nitwit", nit)
    st.lights(s, scale=1.0, near=st.v.anchors["exit_gate"], radius=14.0)


def build(scene):
    """Build the demo: {"film": Film, "captions": [(word, t0, t1), ...], "narration": Narration, "stage": Stage}."""
    # 1. the voice: stops here (NarrationError) if narration/_narrated_demo.json was not spoken from NARRATION
    nar = narration.load(__name__, NARRATION, fps=FPS)
    print(nar.summary())

    v = village.build_village(scene, seed=1)
    sky = look.set_time(scene, SKY["preset"], sun_azimuth=SKY["az"], sun_elevation=SKY["el"])
    look.setup_compositor(scene, bloom=SKY["bloom"], grade=SKY["grade"])
    film = shots.Film(scene, fps=FPS)
    st = L.Stage(scene, film, v, sky)

    # 2. the cuts: every shot starts with a sentence. Sentence.cut is the first frame of such a shot: two frames
    #    before the sentence's first word, never inside the word before. shot_frames turns cuts into shot lengths;
    #    the last shot runs to nar.frames (last word + tail).
    builders = (("villager", shot_job), ("trade", L.shot_trade), ("nitwit", L.shot_nitwit), ("leave", shot_leave))
    lengths = nar.shot_frames([nar.sentence(1), nar.sentence("But nobody"), nar.sentence("leave")])
    for (name, fn), n in zip(builders, lengths):
        fn(st, st.shot(name, nar.seconds(n)))

    # 3. the acting, on words: nar.at(word) is the frame on which that word's caption appears
    st.cast["ada"].nod(nar.at("all"))                    # the farmer agrees: "... with ALL of them"
    st.cast["nitwit"].shake(nar.at("nobody") + 2)        # the nitwit's no: "But NOBODY trades ..."
    st.finish()

    # 4. the captions: one word at a time, each on the frame in which it starts being spoken
    return {"film": film, "captions": nar.captions(), "narration": nar, "stage": st}
