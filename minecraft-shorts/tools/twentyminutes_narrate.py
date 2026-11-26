#!/usr/bin/env python
"""Twenty Minutes: tools/narrate.py, resumable (the machine is too busy for one uninterrupted run under 300 s).

    $TTS tools/twentyminutes_narrate.py [--budget 230] [--threads 2]    # run it again until it says "wrote"
    exit 0 = narration/twentyminutes.wav + .json written (by tools/narrate.py's own narrate()); 4 = not finished yet,
    run the same command again; anything else = an error.

WHAT IT DOES: nothing of its own to the voice or the timing. It runs tools/narrate.py's narrate() for the film exactly
as `$TTS tools/narrate.py twentyminutes --force` does, with two of narrate.py's deterministic steps memoised on disk
(scratchpad/tm_narrate_cache/), so that the work of a run killed by the time limit is not lost:
  * Engines.speak(text, voice, speed): the voice model's samples and phoneme timings of one sentence (Kokoro is
    deterministic: the same sentence, voice, speed and thread count give the same samples; narrate.py's docstring);
  * time_by_recogniser(eng, clip, words, onset, offset): the recogniser's second opinion on one sentence clip (keyed
    by a hash of the clip's samples, the words and the onset / offset).
When the time budget is used up between two such steps it stops (exit 4). A finished run is the same narrate() call
on the same inputs as an uninterrupted one; the cache only spares recomputing them. (One uninterrupted run took
more than 300 s at load 18-19: 8-15 s per sentence for the voice alone.)
"""
import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, ROOT)

import narrate as NR        # noqa: E402  (tools/narrate.py)

CACHE = os.path.join(os.environ.get("TM_NARRATE_CACHE") or os.path.join(
    "/tmp/claude-0/-home-user-Project-2-/be90bb9d-3fc7-572c-941a-ff79c8b6ef48/scratchpad", "tm_narrate_cache"))
FILM = "twentyminutes"


class OutOfTime(Exception):
    """The budget is used up: run again."""


def _key(*parts):
    h = hashlib.sha1()
    for p in parts:
        h.update(repr(p).encode("utf-8") if not isinstance(p, (bytes, bytearray)) else bytes(p))
        h.update(b"\0")
    return h.hexdigest()[:20]


def _jsonable(x):
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (np.floating,)):
        return float(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def install(budget, t0):
    """Memoise Engines.speak and time_by_recogniser on disk; raise OutOfTime once `budget` seconds are used."""
    os.makedirs(CACHE, exist_ok=True)
    speak0, recog0 = NR.Engines.speak, NR.time_by_recogniser

    def check():
        if time.time() - t0 > budget:
            raise OutOfTime()

    def speak(self, text, voice, speed=1.0):
        k = _key("speak", text, voice, float(speed), self.threads, self.want_timed, NR.KOKORO_TIMED)
        npz = os.path.join(CACHE, "speak_%s.npz" % k)
        js = os.path.join(CACHE, "speak_%s.json" % k)
        if os.path.exists(npz) and os.path.exists(js):
            audio = np.load(npz)["audio"]
            timings = json.load(open(js))["timings"]
            if self.want_timed:
                _ = self.kokoro          # load the model (narrate() asks eng.timed / model_file later)
            return audio, (None if timings is None else [tuple(t) for t in timings])
        check()
        audio, timings = speak0(self, text, voice, speed)
        np.savez(npz + ".part.npz", audio=np.asarray(audio, dtype=np.float32))
        os.replace(npz + ".part.npz", npz)
        with open(js, "w") as f:
            json.dump({"text": text, "voice": voice, "speed": speed, "timings": _jsonable(timings)}, f)
        return audio, timings

    def recog(eng, clip, words, onset, offset, sr=NR.SR, free=False):
        a = np.ascontiguousarray(np.asarray(clip, dtype=np.float32))
        k = _key("recog", hashlib.sha1(a.tobytes()).hexdigest(), list(words), round(float(onset), 6),
                 round(float(offset), 6), sr, free, eng.threads)
        js = os.path.join(CACHE, "recog_%s.json" % k)
        if os.path.exists(js):
            return json.load(open(js))["out"]
        check()
        out = recog0(eng, clip, words, onset, offset, sr, free)
        with open(js + ".part", "w") as f:
            json.dump({"words": list(words), "out": _jsonable(out)}, f)
        os.replace(js + ".part", js)
        return json.load(open(js))["out"]          # exactly what a cached run returns (json round trip)

    NR.Engines.speak = speak
    NR.time_by_recogniser = recog


def main(argv):
    """See the module docstring."""
    ap = argparse.ArgumentParser(prog="tools/twentyminutes_narrate.py")
    ap.add_argument("--budget", type=float, default=230.0, help="seconds after which no new step is started")
    ap.add_argument("--threads", type=int, default=2)
    args = ap.parse_args(argv)
    t0 = time.time()
    install(args.budget, t0)
    eng = NR.Engines(args.threads, timed=True)
    try:
        NR.narrate(FILM, eng)
    except OutOfTime:
        n = len([f for f in os.listdir(CACHE) if f.endswith(".json")])
        print("[twentyminutes_narrate] out of time after %.0f s (%d steps cached in %s): run the same command again"
              % (time.time() - t0, n, CACHE))
        return 4
    print("[twentyminutes_narrate] done in %.0f s" % (time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
