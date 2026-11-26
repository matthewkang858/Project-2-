"""The Crammys: speak narration/crammys.wav + .json with tools/narrate.py's OWN narrate(), in resumable parts.

    $TTS tools/crammys_narrate.py            # run it again until it prints "[crammys_narrate] done" (exit 0);
                                             #   exit 3 = "not finished: run the same command again"
    $TTS tools/crammys_narrate.py --check    # = tools/narrate.py crammys --check

WHY: on this shared machine (The Hello's final render has priority) one pass of `$TTS tools/narrate.py crammys`
synthesised its 24 sentences in 280 s and was stopped by the 300 s command limit before it could time the words
(scratchpad crammys_narrate1.log); tools/narrate.py has no resumable mode (only its --selftest has one) and it is
frozen. This wrapper runs exactly tools/narrate.narrate("crammys", Engines(threads=2)) - the same text, voice,
speed, threads, timing, levelling, limiter, layout, onset check and json - and only puts a DISK CACHE in front of
the three expensive, deterministic engine calls (Engines.speak: the voice model; Engines.forced / .recognise: the
recogniser), keyed by everything they are given (text, voice, speed, thread count; the 16 kHz samples and the
words). A call that is not in the cache once BUDGET seconds have passed stops the run (exit 3); the next run takes
the finished calls from the cache and goes on. The last run writes narration/crammys.* through narrate() itself.
Kokoro and faster-whisper are deterministic for the same input and thread count (tools/narrate.py: "the same
sentence, voice and speed give the same samples"), so the result is the one a single uninterrupted run gives.
The cache lives in the scratchpad (CACHE below); it is never read by the film or render.py.
"""
import hashlib
import os
import pickle
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import numpy as np                                     # noqa: E402

from tools import narrate as NR                        # noqa: E402

FILM = "crammys"
BUDGET = float(os.environ.get("CRAMMYS_NARRATE_BUDGET", "200"))     # seconds before no new expensive call starts
CACHE = os.environ.get("CRAMMYS_NARRATE_CACHE", os.path.join(
    "/tmp/claude-0/-home-user-Project-2-/be90bb9d-3fc7-572c-941a-ff79c8b6ef48/scratchpad", "crammys_tts_cache"))
T0 = time.time()


class OutOfTime(Exception):
    """The budget is used up: run again."""


def _key(*parts):
    h = hashlib.sha1()
    for p in parts:
        if isinstance(p, np.ndarray):
            h.update(np.ascontiguousarray(p).tobytes())
            h.update(repr((p.dtype.str, p.shape)).encode())
        else:
            h.update(repr(p).encode("utf-8"))
        h.update(b"|")
    return h.hexdigest()


def _cached(kind, key, make):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, "%s_%s.pkl" % (kind, key))
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    if time.time() - T0 > BUDGET:
        raise OutOfTime(kind)
    t = time.time()
    out = make()
    tmp = path + ".part"
    with open(tmp, "wb") as f:
        pickle.dump(out, f)
    os.replace(tmp, path)
    print("[crammys_narrate]   %s computed in %.1f s (cached)" % (kind, time.time() - t), flush=True)
    return out


class CachedEngines(NR.Engines):
    """tools/narrate.Engines with a disk cache in front of speak / forced / recognise (same results)."""

    def speak(self, text, voice, speed=1.0):
        return _cached("speak", _key(text, voice, float(speed), self.threads, self.want_timed),
                       lambda: NR.Engines.speak(self, text, voice, speed))

    def forced(self, a16, words):
        return _cached("forced", _key(np.asarray(a16), list(words), self.threads),
                       lambda: NR.Engines.forced(self, a16, words))

    def recognise(self, a16):
        return _cached("recognise", _key(np.asarray(a16), self.threads),
                       lambda: NR.Engines.recognise(self, a16))


def main(argv):
    """See the module docstring."""
    if "--check" in argv:
        return NR.main([FILM, "--check"])
    eng = CachedEngines(2, timed=True)
    try:
        NR.narrate(FILM, eng)
    except OutOfTime as e:
        print("[crammys_narrate] not finished (budget %.0f s used up before a %s call): run the same command again"
              % (BUDGET, e), flush=True)
        return 3
    print("[crammys_narrate] done in %.0f s" % (time.time() - T0))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
