"""Checker's probe: spectrograms of sentences of a narration wav with the json's word starts drawn in.

    $BPY -m tools.check_narration_spec <wav> <json> <prefix> <sentence index> [...]
"""
import json
import os
import sys

from tools.check_narration_sync import ROOT, SR, audio_of, spectrogram_png, band_env

import numpy as np


def main():
    wav, js, prefix = sys.argv[1:4]
    which = [int(v) for v in sys.argv[4:]]
    with open(js, encoding="utf-8") as f:
        nar = json.load(f)
    x = audio_of(wav)
    env, tt = band_env(x, 60, 11500)
    for i in which:
        s = nar["sentences"][i]
        t0, t1 = s["start"] - 0.12, s["end"] + 0.12
        marks = []
        ws = [w for w in nar["words"] if w["sentence"] == i]
        for w in ws:
            marks.append((w["start"], (220, 0, 0), w["caption"], 0))
            marks.append((w["end"] - 0.002, (230, 140, 0), "", 1))
            if w.get("second") is not None:
                marks.append((w["second"], (0, 150, 200), "", 2))
        p = spectrogram_png(x, t0, t1, marks, os.path.join(ROOT, "out", "test", "%s_s%d.png" % (prefix, i)),
                            "red=word start orange=word end cyan(bottom)=recogniser")
        # silences inside the sentence (own threshold: 38 dB under the sentence's loudest 10 ms, >= 60 ms)
        m = (tt >= s["start"]) & (tt <= s["end"])
        e, t = env[m], tt[m]
        quiet = e < e.max() - 38.0
        gaps, k = [], 0
        while k < len(quiet):
            if quiet[k]:
                j = k
                while j < len(quiet) and quiet[j]:
                    j += 1
                if t[j - 1] - t[k] >= 0.06:
                    gaps.append((round(float(t[k]), 3), round(float(t[j - 1]), 3)))
                k = j
            else:
                k += 1
        print(os.path.relpath(p, ROOT), "t0=%.3f" % t0, "silences>=60ms:", gaps)
        print("   ", " ".join("%s[%.3f-%.3f %s]" % (w["caption"], w["start"], w["end"], w["source"][0]) for w in ws))


if __name__ == "__main__":
    main()
