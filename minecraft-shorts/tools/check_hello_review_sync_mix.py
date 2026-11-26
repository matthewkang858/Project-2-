"""Review probe (sound lens): the mix and the captions frame by frame, measured on the encoded preview.

    $BPY -m tools.check_hello_review_sync_mix            -> out/test/check_hello_review_sync_mix.json

audio   every voice onset / offset in the mp4 (stereo, 48 kHz): the sample step at the edge (a click is a step out of
        digital silence), the fade length, the first and last 20 ms of the file, digital silence in the pauses,
        loudness range and the loudest momentary / short-term values (ffmpeg ebur128), where the true peak is.
captions every decoded frame matched (tools.narration_sync.caption_frames): a word's run must be unbroken (no
        flicker), no caption on a frame between runs, and the lowest match score per word.
motion  in every pause of 0.6 s or more: mean absolute change between neighbouring SOURCE frames (no captions) and
        between the first and the last frame of the pause, against a locked-off reference shot (in16).
"""
import json
import os
import re
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools import narration_sync as NS  # noqa: E402

MP4 = os.path.join(ROOT, "out", "preview", "hello_360x640_8spp.mp4")
SRC = os.path.join(ROOT, "out", "preview", "hello", "360x640_8spp", "f_%04d.png")


def edges(x, sr, quiet=1e-5, min_gap=0.02):
    """(onset, offset) sample indices of the non-silent runs of mono x (silence = |x| < quiet for >= min_gap)."""
    loud = np.abs(x) >= quiet
    idx = np.flatnonzero(loud)
    if not len(idx):
        return []
    gaps = np.flatnonzero(np.diff(idx) > int(min_gap * sr))
    starts = np.concatenate([[idx[0]], idx[gaps + 1]])
    ends = np.concatenate([idx[gaps], [idx[-1]]])
    return list(zip(starts.tolist(), ends.tolist()))


def main():
    out = {}
    nar = json.load(open(os.path.join(ROOT, "narration", "hello.json")))
    fps = nar["fps"]
    # ---- audio
    st = NS.decode_audio(MP4, 48000, 2)
    x = st[:, 0].astype(np.float64)
    sr = 48000
    runs = edges(x, sr)
    rows = []
    for a, b in runs:
        on = x[a:a + int(0.010 * sr)]
        off = x[max(a, b - int(0.010 * sr)):b + 1]
        # fade length: samples until the envelope (1 ms max) first reaches 50 % of the max of the next 30 ms
        env = np.array([np.abs(x[a + i:a + i + 48]).max() for i in range(0, int(0.03 * sr), 48)])
        k = int(np.argmax(env >= 0.5 * env.max())) if env.max() > 0 else 0
        rows.append({"onset_s": round(a / sr, 4), "offset_s": round(b / sr, 4),
                     "first_sample_abs": round(float(abs(x[a])), 6), "max_abs_first_1ms": round(float(np.abs(on[:48]).max()), 5),
                     "max_abs_last_1ms": round(float(np.abs(off[-48:]).max()), 5), "ms_to_half_level": k,
                     "dB_first_10ms": round(20 * np.log10(np.abs(on).max() + 1e-12), 1),
                     "dB_last_10ms": round(20 * np.log10(np.abs(off).max() + 1e-12), 1)})
    out["sound_runs"] = rows
    out["file_first_20ms_max"] = float(np.abs(st[:960]).max())
    out["file_last_20ms_max"] = float(np.abs(st[-960:]).max())
    out["file_last_2.2s_max"] = float(np.abs(st[-int(2.2 * sr):]).max())
    out["samples"] = len(st)
    peak_i = int(np.argmax(np.abs(x)))
    out["sample_peak"] = {"t": round(peak_i / sr, 3), "dBFS": round(20 * np.log10(abs(x[peak_i])), 2)}
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", MP4, "-map", "0:a:0", "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True)
    text = p.stderr.decode(errors="replace")
    mom = [float(m) for m in re.findall(r" M:\s*(-?[\d.]+)", text)]
    sht = [float(m) for m in re.findall(r" S:\s*(-?[\d.]+)", text)]
    tail = text[text.rfind("Summary:"):]
    out["ebur128_summary"] = " ".join(tail.split())
    out["max_momentary"] = max(mom)
    out["max_short_term"] = max(sht)
    print("[mix] runs %d; file first 20 ms max %.2e, last 20 ms %.2e, last 2.2 s %.2e; sample peak %s"
          % (len(rows), out["file_first_20ms_max"], out["file_last_20ms_max"], out["file_last_2.2s_max"], out["sample_peak"]))
    print("[mix] ebur128:", out["ebur128_summary"], "| max M %.1f, max S %.1f" % (out["max_momentary"], out["max_short_term"]))
    worst_on = max(rows, key=lambda r: r["max_abs_first_1ms"])
    worst_off = max(rows, key=lambda r: r["max_abs_last_1ms"])
    print("[mix] loudest first ms of a run:", worst_on)
    print("[mix] loudest last ms of a run:", worst_off)
    print("[mix] first-sample steps over 1e-3:", [r for r in rows if r["first_sample_abs"] > 1e-3])

    # ---- captions frame by frame
    words = [w for w in nar["words"]]
    seen, scores = NS.caption_frames(MP4, [w["caption"] for w in words])
    out["frames_decoded"] = len(seen)
    runs_c = []
    cur, start = None, None
    for i, c in enumerate(seen + [None]):
        if c != cur:
            if cur is not None:
                runs_c.append((cur, start + 1, i))
            cur, start = c, i
    expected = [w["caption"] for w in words]
    got = [r[0] for r in runs_c]
    out["caption_runs"] = len(runs_c)
    out["caption_sequence_matches_script"] = got == expected
    short = [r for r in runs_c if r[2] - r[1] + 1 < 3]
    out["runs_under_3_frames"] = short
    low = sorted(((round(s, 3), i + 1, c) for i, (c, s) in enumerate(zip(seen, scores)) if c), key=lambda t: t[0])[:10]
    out["lowest_match_scores"] = low
    print("[caps] %d frames, %d caption runs, sequence == script: %s" % (len(seen), len(runs_c), got == expected))
    if got != expected:
        import difflib
        for op in difflib.SequenceMatcher(a=expected, b=got, autojunk=False).get_opcodes():
            if op[0] != "equal":
                print("[caps]   ", op[0], expected[op[1]:op[2]], "->", got[op[3]:op[4]], runs_c[op[3]:op[4]])
    print("[caps] runs under 3 frames:", short)
    print("[caps] lowest match scores:", low)

    # ---- motion in the pauses (source frames, no captions)
    from PIL import Image

    def img(f):
        return np.asarray(Image.open(SRC % f).convert("L"), dtype=np.float32)

    pauses = []
    sents = nar["sentences"]
    for s, nxt in zip(sents, sents[1:] + [None]):
        t_end = s["end"]
        t_next = nxt["start"] if nxt else nar["duration"]
        if t_next - t_end >= 0.6:
            f0, f1 = int(t_end * fps) + 1, int(t_next * fps)
            pauses.append((s["id"], f0, f1))
    pauses.append(("ref_in16_locked", 1000, 1040))
    mres = []
    for sid, f0, f1 in pauses:
        frames = [img(f) for f in range(f0, f1 + 1)]
        d1 = [float(np.mean(np.abs(a - b))) for a, b in zip(frames, frames[1:])]
        dend = float(np.mean(np.abs(frames[0] - frames[-1])))
        mres.append({"after": sid, "frames": [f0, f1], "n": f1 - f0 + 1, "mean_step": round(float(np.mean(d1)), 2),
                     "max_step": round(float(np.max(d1)), 2), "first_vs_last": round(dend, 2)})
        print("[motion] after %-16s frames %4d-%4d (%2d)  mean step %5.2f  max step %6.2f  first-vs-last %6.2f"
              % (sid, f0, f1, f1 - f0 + 1, mres[-1]["mean_step"], mres[-1]["max_step"], dend))
    out["pause_motion"] = mres
    dst = os.path.join(ROOT, "out", "test", "check_hello_review_sync_mix.json")
    with open(dst, "w") as f:
        json.dump(out, f, indent=1, default=float)
    print("->", dst)


if __name__ == "__main__":
    main()
