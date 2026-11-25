"""Checker's probe (TTS environment): a one-minute narration the way a director would write it, with the words a
recogniser and a phonemiser get wrong. Nothing is written under narration/ or films/: the narration directory is
redirected to out/test/check_narration_dir and the spec is handed over directly.

    $TTS -m tools.check_narration_minute speak        # narrate SPEC -> out/test/check_narration_dir/check_minute.wav + .json
    $TTS -m tools.check_narration_minute trim [a b]   # what trim_clip throws away, on SPEC + narrate.TEST_SENTENCES[a:b]
    $TTS -m tools.check_narration_minute phon         # phonemes of every SPEC sentence
"""
import json
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from engine import narration as N                                    # noqa: E402
from tools import narrate as T                                       # noqa: E402

NAME = "check_minute"
DIR = os.path.join(ROOT, "out", "test", "check_narration_dir")

SPEC = {
    "say": {"Crammys": "crammies"},
    "lines": [
        "In this bastion, I'm the only one who doesn't like gold.",
        "The speedrunners trap piglins in holes, and trade with them.",
        ("They throw 64 gold ingots — my brothers throw back ender pearls.", 0.6),
        "But I'm a piglin brute, and I don't trade.",
        "Every new world, there he is again: bucket, boat, and TNT.",
        "He needs 12 pearls... I need him gone.",
        "His best run died at 14:07, and I did that.",
        {"text": "Netherite armor doesn't scare me.", "pause": 1.5, "id": "armor"},
        "\"Run,\" he typed. 'Not again!'",
        "In my old town, everyone was musical except me.",
        "Tonight is the Crammys, and Mr. Steve has 3 note blocks.",
        "The redstoner's pickaxe had Mending and Unbreaking III.",
        "The grown-ups call him Herobrine.",
        {"text": "He doesn't blink — ever.", "speed": 0.9},
        "At 3 o'clock, the raid came: 20 pillagers, 1 ravager.",
        "My trap took 100% of them.",
        "Now the gym bros carry my redstone, my pistons and my sticky trapdoors.",
        "We count who made it home, and tonight... somebody didn't.",
        "My dad came back selling Mending for 1 emerald.",
        "He doesn't remember my name.",
        "So I wrote it on a sign: I'M STILL HERE.",
        "And XP can't buy that.",
    ],
}


def redirect():
    os.makedirs(DIR, exist_ok=True)
    N.NARRATION_DIR = DIR
    N.read_spec = lambda film: SPEC


def speak():
    redirect()
    eng = T.Engines(2)
    t = time.time()
    data = T.narrate(NAME, eng)
    print("narrate() took %.0f s for %d sentences, %d words, %.2f s of film" % (time.time() - t, len(data["sentences"]),
                                                                           len(data["words"]), data["duration"]))
    # every script word has a time, in order, inside its sentence
    prev = 0.0
    bad = 0
    for w in data["words"]:
        s = data["sentences"][w["sentence"]]
        if not (w["start"] >= prev - 1e-6 and w["end"] > w["start"] and s["start"] - 1e-3 <= w["start"] and w["end"] <= s["end"] + 1e-3):
            bad += 1
            print("  !! bad time", w, s["start"], s["end"])
        prev = w["end"]
    print("words out of order / outside their sentence:", bad)
    short = [(w["text"], round(w["end"] - w["start"], 3), w["source"]) for w in data["words"] if w["end"] - w["start"] < 0.06]
    print("words shorter than 60 ms:", short)
    longw = [(w["text"], round(w["end"] - w["start"], 3), w["source"]) for w in data["words"] if w["end"] - w["start"] > 0.75]
    print("words longer than 750 ms:", longw)
    print("sources:", {k: sum(1 for w in data["words"] if w["source"] == k) for k in sorted({w["source"] for w in data["words"]})})
    for s in data["sentences"]:
        ws = data["words"][s["first_word"]:s["last_word"] + 1]
        print("%2d %6.2f-%6.2f  %s" % (s["index"], s["start"], s["end"],
                                         " ".join("%s[%.2f%s]" % (w["caption"], w["start"], "" if w["source"] in ("model", "energy") else "/" + w["source"]) for w in ws)))


def trim(a=0, b=0):
    redirect()
    eng = T.Engines(2)
    norm = N.normalise(SPEC)
    texts = [(ln["text"], ln["spoken"]) for ln in norm["lines"]] if a == b else []
    texts += [(s, N.spoken_text(s)) for s in T.TEST_SENTENCES[a:b]]
    worst = []
    for text, spoken in texts:
        raw, _t = eng.speak(spoken, "am_michael", 1.0)
        runs = T.sound_runs(raw)
        t0, t1 = runs[0][0], runs[-1][1]
        ca, cb = max(0, int(round((t0 - T.PRE) * T.SR))), min(len(raw), int(round((t1 + T.POST) * T.SR)))
        rms, hop = T.frame_rms(raw)
        peak = rms.max()
        tt = np.arange(len(rms)) * hop
        head = rms[tt + 0.010 <= ca / T.SR]
        tail = rms[tt >= cb / T.SR]
        hd = T.db(head.max() / peak) if len(head) else -200.0
        tl = T.db(tail.max() / peak) if len(tail) else -200.0
        # energy share thrown away, and the level in the faded 30 ms at the end / 8 ms at the start
        fade_out = rms[(tt >= cb / T.SR - T.FADE_OUT) & (tt + 0.010 <= cb / T.SR)]
        fo = T.db(fade_out.max() / peak) if len(fade_out) else -200.0
        fade_in = rms[(tt >= ca / T.SR) & (tt + 0.010 <= ca / T.SR + T.FADE_IN + 0.010)]
        fi = T.db(fade_in.max() / peak) if len(fade_in) else -200.0
        blips = []
        act = rms > max(peak * 10 ** (T.SILENCE_DB / 20.0), 10 ** (-62 / 20.0))
        # sounds the run rule dropped (shorter than MIN_RUN) that lie outside the kept clip
        i = 0
        while i < len(act):
            if act[i]:
                j = i
                while j < len(act) and act[j]:
                    j += 1
                if tt[i] >= cb / T.SR or tt[j - 1] + 0.010 <= ca / T.SR:
                    blips.append((round(float(tt[i]) - t1, 3), round(float(tt[j - 1] + 0.010 - tt[i]), 3), round(T.db(rms[i:j].max() / peak), 1)))
                i = j
            else:
                i += 1
        worst.append((max(hd, tl), text))
        print("head %6.1f dB  tail %6.1f dB  fade-in %6.1f  fade-out %6.1f  raw lead %.3f s, raw tail %.3f s  dropped sounds %s | %s"
              % (hd, tl, fi, fo, t0, len(raw) / T.SR - t1, blips, text[:60]))
    worst.sort(reverse=True)
    print("loudest thing thrown away (dB re the sentence's loudest 10 ms):", [(round(w, 1), t[:40]) for w, t in worst[:5]])


def phon():
    redirect()
    eng = T.Engines(2)
    norm = N.normalise(SPEC)
    for ln in norm["lines"]:
        print(ln["spoken"], "\n    ", eng.phonemes(ln["spoken"], "am_michael"))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "speak"
    if mode == "speak":
        speak()
    elif mode == "trim":
        trim(*(int(v) for v in sys.argv[2:4])) if len(sys.argv) > 3 else trim()
    elif mode == "phon":
        phon()


def onsets(a=0, b=0):
    """Words that the narrator starts on a 'measured onset' after a pause: its start against the voice model's own
    phoneme start and against the first clearly audible sound (10 ms RMS within 28 dB of the sentence's loudest)."""
    redirect()
    eng = T.Engines(2)
    norm = N.normalise(SPEC)
    texts = [(ln["text"], ln["spoken"]) for ln in norm["lines"]] if a == b else []
    texts += [(s, N.spoken_text(s)) for s in T.TEST_SENTENCES[a:b]]
    rows = []
    for text, spoken in texts:
        c = T.speak_sentence(eng, text, spoken, "am_michael", 1.0)
        words = N.words_of(text)
        timed = T.time_sentence(eng, c["clip"], words, c["onset"], c["offset"], model=c["model"], second_opinion=False)
        rms, hop = T.frame_rms(c["clip"])
        tt = np.arange(len(rms)) * hop
        peak = rms.max()
        for i, w in enumerate(timed):
            if i == 0 or w["source"] != "energy":
                continue
            k = np.flatnonzero((tt >= w["start"] - 0.012) & (rms >= peak * 10 ** (-28 / 20.0)))
            t28 = float(tt[k[0]]) if len(k) else None
            lvl = rms[(tt >= w["start"]) & (tt < (t28 if t28 else w["start"] + 0.05))]
            rows.append((words[i], w["start"], w["model_raw"], t28, T.db(lvl.max() / peak) if len(lvl) else 0.0, text[:34]))
            print("%-12s final %.3f  model %.3f (%+4.0f ms)  audible(-28dB) %.3f (%+4.0f ms)  level before that %5.1f dB | %s"
                  % (words[i], w["start"], w["model_raw"], 1000 * (w["model_raw"] - w["start"]), t28,
                     1000 * (t28 - w["start"]), rows[-1][4], text[:44]))
    d = np.array([r[3] - r[1] for r in rows]) * 1000
    m = np.array([r[2] - r[1] for r in rows]) * 1000
    print("words after a pause: %d; audible onset later than the narrator's start by: median %.0f ms, max %.0f ms; "
          "more than 2 frames (83 ms): %d, more than 4 frames: %d" % (len(d), np.median(d), d.max(), int((d > 83).sum()), int((d > 167).sum())))
    print("model's own start later than the narrator's start by more than 83 ms: %d %s" % (int((m > 83).sum()),
          [(r[0], round(1000 * (r[2] - r[1]))) for r in rows if r[2] - r[1] > 0.083]))


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "onsets":
    onsets(*(int(v) for v in sys.argv[2:4])) if len(sys.argv) > 3 else onsets()


def rawvs(a=0, b=0):
    """The same sentences timed twice by the narrator's own time_sentence(): on the clip as spoken (what
    --selftest measures) and on the clip after synthesise() has levelled and LIMITED it (what narrate() uses)."""
    redirect()
    eng = T.Engines(2)
    spec = SPEC if a == b else {"lines": T.TEST_SENTENCES[a:b]}
    norm = N.normalise(spec)
    raw = []
    for ln in norm["lines"]:
        c = T.speak_sentence(eng, ln["text"], ln["spoken"], norm["voice"], norm["speed"] * ln["speed"])
        words = N.words_of(ln["text"])
        raw.append((words, T.time_sentence(eng, c["clip"], words, c["onset"], c["offset"], model=c["model"], second_opinion=False), c))
    clips, loud = T.synthesise(eng, norm, log=lambda *_: None)
    print("limiter: max reduction %.1f dB, over 1 dB on %.0f%% and over 3 dB on %.0f%% of the samples; gain %.1f dB, ceiling %.1f dB"
          % (loud["max_gain_reduction_db"], 100 * loud["share_limited_over_1db"], 100 * loud["share_limited_over_3db"],
             loud["gain_db"], loud["limiter_ceiling_db"]))
    n_words = n_pause_raw = n_pause_lim = 0
    moved = []
    for (words, t_raw, c_raw), c in zip(raw, clips):
        t_lim = T.time_sentence(eng, c["clip"], words, c["onset"], c["offset"], model=c["model"], second_opinion=False)
        runs_raw, runs_lim = T.sound_runs(c_raw["clip"]), T.sound_runs(c["clip"])
        n_pause_raw += sum(1 for w in t_raw[1:] if w["source"] == "energy")
        n_pause_lim += sum(1 for w in t_lim[1:] if w["source"] == "energy")
        for i, (x, y) in enumerate(zip(t_raw, t_lim)):
            n_words += 1
            if abs(x["start"] - y["start"]) > 0.020:
                moved.append((words[i], round(1000 * (y["start"] - x["start"])), x["source"], y["source"], " ".join(words)[:40]))
        if len(runs_raw) != len(runs_lim):
            print("  sound runs %d -> %d after the limiter | %s" % (len(runs_raw), len(runs_lim), " ".join(words)[:50]))
    print("%d words; started on a measured onset after a pause: %d on the spoken clips, %d on the limited clips" % (n_words, n_pause_raw, n_pause_lim))
    print("words whose START moves by more than 20 ms when the same function is run on the limited clip (ms, source before -> after):")
    for m in moved:
        print("   %-12s %+5d ms  %s -> %s | %s" % m)


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "rawvs":
    rawvs(*(int(v) for v in sys.argv[2:4])) if len(sys.argv) > 3 else rawvs()
