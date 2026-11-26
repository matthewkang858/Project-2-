"""Review probe (sound lens): are the recogniser's two extra words ('sometimes. times.', 'watched. crouched.') in
the VOICE, or the recogniser's own invention? Runs in the TTS environment.

    $TTS tools/check_hello_review_sync_tails.py

1. The voice model's own phoneme spans for b10 and b19 (re-synthesised: deterministic, the same samples).
2. The energy envelope of narration/hello.wav over the last word of b10 and b19 (10 ms frames, dB under the
   film's loudest frame) and of comparable sentence-final words (b09 'us', b16 'anymore', b21 'down').
3. The recogniser run on each sentence ALONE and on windows of different context around both places.
Writes out/test/check_hello_review_sync_tails.json.
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import narrate as T  # noqa: E402

SR = T.SR


def env_db(x, t0, t1, peak):
    a, b = int(t0 * SR), int(t1 * SR)
    seg = x[a:b]
    hop = int(0.01 * SR)
    out = []
    for i in range(0, len(seg) - hop, hop):
        r = np.sqrt(np.mean(seg[i:i + hop] ** 2)) + 1e-9
        out.append(round(20 * np.log10(r / peak), 1))
    return out


def main():
    nar = json.load(open(os.path.join(ROOT, "narration", "hello.json")))
    x = T.read_audio(os.path.join(ROOT, "narration", "hello.wav"), SR)
    hop = int(0.01 * SR)
    frames = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
    peak = float(frames.max())
    eng = T.Engines(threads=2)
    res = {"phonemes": {}, "envelope": {}, "alone": {}, "windows": {}}
    sents = nar["sentences"]
    words = nar["words"]
    # 1. phoneme spans of the voice model
    for sid in ("b10", "b19", "b09", "b21"):
        s = next(s for s in sents if s["id"] == sid)
        audio, tim = eng.speak(s["spoken"], nar["voice"], s.get("speed", 1.0))
        res["phonemes"][sid] = [(p, round(a, 3), round(b, 3)) for p, a, b in (tim or [])][-12:]
    # 2. envelopes of sentence-final words, from the word start to 0.5 s after the sentence end
    for sid in ("b10", "b19", "b09", "b16", "b21", "b02"):
        s = next(s for s in sents if s["id"] == sid)
        w = words[s["last_word"]]
        res["envelope"][sid + ":" + w["caption"]] = {"t0": w["start"], "sentence_end": s["end"],
                                                     "db_10ms": [float(v) for v in env_db(x, w["start"], s["end"] + 0.4, peak)]}
    # 3. the recogniser on each sentence alone (0.25 s of margin either side), and on context windows
    a16_all = T.resample(x, SR, 16000)
    for s in sents:
        t0, t1 = max(0.0, s["start"] - 0.25), s["end"] + 0.25
        heard = eng.recognise(a16_all[int(t0 * 16000):int(t1 * 16000)])
        res["alone"][s["id"]] = " ".join(w for w, _a, _b, _p in heard)
    for label, (t0, t1) in {"b09-b11": (22.3, 29.5), "b10_only_tight": (25.2, 27.80), "b10_plus_0.6": (25.2, 28.36),
                            "b18-b20": (45.7, 56.4), "b19_only_tight": (49.7, 51.53), "b19_plus_0.9": (49.7, 52.4),
                            "b15-b17": (38.0, 45.3)}.items():
        heard = eng.recognise(a16_all[int(t0 * 16000):int(t1 * 16000)])
        res["windows"][label] = [(w, round(a + t0, 2), round(b + t0, 2), round(p, 2)) for w, a, b, p in heard]
    dst = os.path.join(ROOT, "out", "test", "check_hello_review_sync_tails.json")
    with open(dst, "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, default=float)
    for k, v in res["alone"].items():
        print("alone", k, "|", v)
    for k, v in res["windows"].items():
        print("window", k, "|", " ".join("%s@%.2f(%.2f)" % (w, a, p) for w, a, b, p in v))
    for k, v in res["phonemes"].items():
        print("phon", k, v)
    for k, v in res["envelope"].items():
        print("env", k, v["t0"], v["sentence_end"], v["db_10ms"])
    print("->", dst)


if __name__ == "__main__":
    main()
