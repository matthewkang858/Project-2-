"""One minute of narration through the whole chain, without a Blender scene: the proof at FILM LENGTH.

films/_narrated_demo.py proves the chain on 10 seconds of real picture. The six films are a minute long, and a
minute is where a narrator goes wrong (the first version put captions 4 to 6 frames early after some pauses, and
only a 75 s probe showed it). This probe speaks SPEC, a one-minute script of the films' kind written the way a
director should write it (numbers as words, 165 words in 19 sentences), lays its captions over synthetic frames, encodes them
through render.py exactly as a film is encoded, and measures the result in the mp4:

    $TTS tools/narration_minute.py speak     # SPEC -> out/test/narration_minute/narration_minute.wav + .json
    $BPY -m tools.narration_minute encode    # render.py --encode in 10 s parts, INTERRUPTED after every part
                                             #   (--max-seconds 1); repeat the command until it says "encoded"
    $BPY -m tools.narration_minute sync      # tools.narration_sync on out/preview/narration_minute_180x320_1spp.mp4:
                                             #   container, loudness, audio lag at start / middle / end (drift),
                                             #   every caption against the json and against the clearly audible voice
    $BPY -m tools.narration_minute two       # the TWO-MODULE recipe of engine/narration.py on the same minute: the
                                             #   film cut in two at a sentence, each half built from nar.part() and
                                             #   encoded silent, the halves joined with a stream copy, the whole
                                             #   narration put under the join with post.mux_audio
    $BPY -m tools.narration_minute sync two  # the same proof on out/preview/narration_minute_two.mp4

Nothing is written under narration/ or films/: the narration directory is redirected to out/test/narration_minute
and the spec is handed over directly (so `narration.load` works on it in both interpreters).
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from engine import narration as N                                    # noqa: E402

NAME = "narration_minute"
DIR = os.path.join(ROOT, "out", "test", NAME)
RES, SAMPLES = (180, 320), 1                    # synthetic frames; render.py upscales them to 1080x1920 as always
VARIANT = "%dx%d_%dspp" % (RES[0], RES[1], SAMPLES)

SPEC = {
    "lines": [
        {"text": "In this bastion, I'm the only one who doesn't like gold.", "id": "open"},
        "The speedrunners trap piglins in holes, and trade with them.",
        ("They throw gold ingots, and my brothers throw back ender pearls.", 0.6),
        "But I'm a piglin brute, and I don't trade.",
        "I just keep attacking him.",
        "Every new world, there he is again, with his bucket and his boat.",
        "He needs twelve pearls, and I need him gone.",
        {"text": "His speedrun died at fourteen minutes, and I did that.", "pause": 1.2, "id": "died"},
        "Netherite armor doesn't scare me.",
        "He respawned, looked at me, and quit the game.",
        "In my old town, everyone was musical except me.",
        "Tonight at the Crammys, I finally found my sound.",
        "The redstoner's pickaxe had Mending and Unbreaking three.",
        "The grown-ups call him Herobrine.",
        {"text": "His eyes are white, and he never blinks.", "speed": 0.95},
        "We count who made it home, and tonight, somebody didn't.",
        "My dad came back selling Mending for one emerald.",
        ("He doesn't remember my name.", 0.8),
        {"text": "So I wrote it on a sign: I'm still here.", "id": "sign"},
    ],
}


def redirect():
    """Point engine.narration at the probe: its own directory, SPEC as the film's text."""
    os.makedirs(DIR, exist_ok=True)
    N.NARRATION_DIR = DIR
    N.read_spec = lambda film: SPEC


def speak():
    """TTS interpreter: speak SPEC and say how its length sits against one minute."""
    from tools import narrate as T

    redirect()
    data = T.narrate(NAME, T.Engines(2))
    words = data["words"]
    prev, bad = 0.0, 0
    for w in words:                                   # every script word: in order, inside its sentence
        s = data["sentences"][w["sentence"]]
        bad += not (w["start"] >= prev - 1e-6 and w["end"] > w["start"] and s["start"] - 1e-3 <= w["start"]
                    and w["end"] <= s["end"] + 1e-3)
        prev = w["end"]
    print("[minute] %d words in %d sentences: %.2f s = %d frames; words out of order or outside their sentence: %d; "
          "sources %s" % (len(words), len(data["sentences"]), data["duration"], data["frames"], bad,
                          {k: sum(1 for w in words if w["source"] == k) for k in sorted({w["source"] for w in words})}))
    return 1 if bad else 0


def encode(budget=150.0):
    """Blender's interpreter (bpy itself is not needed): synthetic frames, then render.py --encode with a budget
    of one second, so that every call writes one 10 s part and stops (exit code 4), until the film is joined."""
    import numpy as np
    from PIL import Image

    import render
    from engine import post

    redirect()
    nar = N.load(NAME, SPEC)
    d = post.frames_dir(NAME, VARIANT)
    os.makedirs(d, exist_ok=True)
    yy = np.linspace(40, 110, RES[1])[:, None] * np.ones((1, RES[0]))
    for f in range(1, nar.frames + 1):
        p = post.frame_path(NAME, f, VARIANT)
        if os.path.exists(p):
            continue
        a = np.stack([yy * 0.6, yy * 0.8, yy], axis=2)
        x = (f * 3) % (RES[0] - 16)
        a[16:40, x:x + 16] = (200, 60, 60)                            # something that moves, away from the caption band
        Image.fromarray(a.astype(np.uint8)).save(p)
    sources = ["tools/narration_minute.py"]
    post.write_meta(NAME, {"film": NAME, "fps": 24, "frame_start": 1, "frame_end": nar.frames,
                           "captions": [list(c) for c in nar.captions()], "signature": "minute",
                           "frames": {str(f): "minute" for f in range(1, nar.frames + 1)},
                           "sources": sources, "source_hash": render.source_hash(sources)}, VARIANT)
    log = os.path.join(DIR, "encode_calls.json")
    try:
        with open(log, encoding="utf-8") as f:
            calls = json.load(f)
    except (OSError, ValueError):
        calls = []
    t0 = time.time()
    while True:
        t = time.time()
        code = render.main([NAME, "--encode", "--res", "%dx%d" % RES, "--samples", str(SAMPLES), "--audio", nar.wav,
                            "--max-seconds", "1"])
        calls.append({"exit_code": code, "seconds": round(time.time() - t, 1)})
        with open(log, "w", encoding="utf-8") as f:
            json.dump(calls, f)
        if code != 4 or time.time() - t0 > budget:
            break
    if code == 0:
        print("[minute] encoded: %d frames in %d calls of render.py --encode (%d of them stopped with exit code 4 "
              "after one part), %.0f s of encoding in all" % (nar.frames, len(calls), sum(c["exit_code"] == 4 for c in calls),
                                                             sum(c["seconds"] for c in calls)))
        os.remove(log)
    else:
        print("[minute] not finished (exit code %d after %d calls): run the same command again" % (code, len(calls)))
    return code


def two():
    """Blender's interpreter: a film of two modules (two skies) with ONE narration, as engine/narration.py tells
    a director to make it. The cut is the sentence after the long pause; each half gets the captions of its
    nar.part() on its own clock and its own frames 1..n, is encoded silent by post.encode, the halves are joined
    with ffmpeg's concat demuxer and the whole wav goes under the join."""
    import subprocess

    from engine import post

    redirect()
    whole = N.load(NAME, SPEC)
    cut = whole.sentences[whole.sentence("died").index + 1].cut          # "Netherite armor ..." starts the second module
    halves = (("a", whole.part(1, cut - 1), 1), ("b", whole.part(cut), cut))
    assert sum(nar.frames for _tag, nar, _first in halves) == whole.frames
    mp4s = []
    for tag, nar, first in halves:
        film = "%s_%s" % (NAME, tag)
        os.makedirs(post.frames_dir(film, VARIANT), exist_ok=True)
        for f in range(1, nar.frames + 1):                               # the module's own frames 1..n
            dst = post.frame_path(film, f, VARIANT)
            if not os.path.exists(dst):
                os.link(post.frame_path(NAME, first + f - 1, VARIANT), dst)
        post.write_meta(film, {"film": film, "fps": 24, "frame_start": 1, "frame_end": nar.frames,
                               "captions": [list(c) for c in nar.captions()], "signature": "minute",
                               "frames": {str(f): "minute" for f in range(1, nar.frames + 1)}}, VARIANT)
        mp4s.append(post.encode(film, variant=VARIANT, out_path=os.path.join(DIR, "two_%s.mp4" % tag)))
    listing = os.path.join(DIR, "two.txt")
    with open(listing, "w", encoding="utf-8") as f:
        for m in mp4s:
            f.write("file '%s'\n" % os.path.abspath(m))
    joined = os.path.join(DIR, "two_joined.mp4")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", listing,
                           "-c", "copy", "-movflags", "+faststart", joined])
    final = os.path.join(ROOT, "out", "preview", "%s_two.mp4" % NAME)
    info = post.mux_audio(joined, whole.wav, final)
    v = post.probe(final)
    print("[minute] two modules: cut at frame %d ('%s'), %d + %d frames -> %s: %d frames, %.3f s, audio %s"
          % (cut, whole.sentences[whole.sentence("died").index + 1].text, halves[0][1].frames, halves[1][1].frames,
             os.path.relpath(final, ROOT), v["frames"], v["duration"], info))
    return 0 if v["frames"] == whole.frames else 1


def sync(which=""):
    """Blender's interpreter: the sync proof of tools.narration_sync on the encoded minute (`two`: on the film
    made of two modules)."""
    from tools import narration_sync

    redirect()
    mp4 = os.path.join(ROOT, "out", "preview", "%s_%s.mp4" % (NAME, "two" if which == "two" else VARIANT))
    return narration_sync.main([NAME, mp4, "--no-hear"])


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in ("speak", "encode", "sync", "two"):
        print(__doc__)
        sys.exit(1)
    if mode == "sync":
        sys.exit(sync(sys.argv[2] if len(sys.argv) > 2 else ""))
    sys.exit({"speak": speak, "encode": encode, "two": two}[mode]())
