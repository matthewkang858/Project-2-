"""Review probe, round 2 (sound lens): the mix and the captions frame by frame, measured on the RE-ENCODED preview.

    $BPY -m tools.check_hello_review_sync_r2_mix         -> out/test/check_hello_review_sync_r2_mix.json

Same measurements as tools/check_hello_review_sync_mix.py (round 1), plus:
  * the per-frame caption list is stored (so the strips can label tiles without decoding again)
  * captions across a cut: every caption run that starts in one shot and is still on screen in the next
  * captions per shot: the frames between the last caption and the cut (how long a shot holds without a word)
  * the audio of this mp4 against round 1's measurements (the narration is frozen: it must be the same sound)
  * motion in every pause of 0.6 s or more on the SOURCE frames, and in the changed shots' word spans
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
from tools.check_hello_review_sync_mix import edges  # noqa: E402

MP4 = os.path.join(ROOT, "out", "preview", "hello_360x640_8spp.mp4")
SRC = os.path.join(ROOT, "out", "preview", "hello", "360x640_8spp", "f_%04d.png")


def main():
    out = {}
    nar = json.load(open(os.path.join(ROOT, "narration", "hello.json")))
    fps = nar["fps"]
    tl = json.loads(subprocess.check_output([sys.executable, "-m", "tools.hello_timeline", "--json"], cwd=ROOT))
    shots = tl["shots"] if isinstance(tl, dict) else tl
    cuts = [(s["shot"], s["frame_start"], s["frame_end"]) for s in shots]

    # ---- audio
    st = NS.decode_audio(MP4, 48000, 2)
    x = st[:, 0].astype(np.float64)
    sr = 48000
    runs = edges(x, sr)
    rows = []
    for a, b in runs:
        on = x[a:a + int(0.010 * sr)]
        off = x[max(a, b - int(0.010 * sr)):b + 1]
        rows.append({"onset_s": round(a / sr, 4), "offset_s": round(b / sr, 4),
                     "first_sample_abs": round(float(abs(x[a])), 6),
                     "max_abs_first_1ms": round(float(np.abs(on[:48]).max()), 5),
                     "max_abs_last_1ms": round(float(np.abs(off[-48:]).max()), 5),
                     "dB_first_10ms": round(20 * np.log10(np.abs(on).max() + 1e-12), 1),
                     "dB_last_10ms": round(20 * np.log10(np.abs(off).max() + 1e-12), 1)})
    out["sound_runs"] = rows
    out["file_first_20ms_max"] = float(np.abs(st[:960]).max())
    out["file_last_20ms_max"] = float(np.abs(st[-960:]).max())
    out["last_sound_s"] = round(runs[-1][1] / sr, 4) if runs else None
    out["first_sound_s"] = round(runs[0][0] / sr, 4) if runs else None
    out["samples"] = len(st)
    out["seconds"] = len(st) / sr
    out["picture_seconds"] = nar["frames"] / float(fps)
    peak_i = int(np.argmax(np.abs(x)))
    out["sample_peak"] = {"t": round(peak_i / sr, 3), "dBFS": round(20 * np.log10(abs(x[peak_i])), 2)}
    # the mp4 audio against the wav (frozen narration)
    wav = NS.decode_audio(os.path.join(ROOT, "narration", "hello.wav"), 48000, 1).astype(np.float64)
    n = min(len(wav), len(x))
    diff = x[:n] - wav[:n]
    out["mp4_minus_wav_rms_db"] = round(20 * np.log10(np.sqrt(np.mean(diff ** 2)) / np.sqrt(np.mean(wav[:n] ** 2)) + 1e-12), 1)
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", MP4, "-map", "0:a:0", "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True)
    text = p.stderr.decode(errors="replace")
    mom = [float(m) for m in re.findall(r" M:\s*(-?[\d.]+)", text)]
    sht = [float(m) for m in re.findall(r" S:\s*(-?[\d.]+)", text)]
    tail = text[text.rfind("Summary:"):]
    out["ebur128_summary"] = " ".join(tail.split())
    out["max_momentary"] = max(mom)
    out["max_short_term"] = max(sht)
    print("[mix] runs %d; first sound %.4f s, last sound %.4f s; file first 20 ms max %.2e, last 20 ms %.2e; "
          "sample peak %s; audio %.6f s vs picture %.6f s; mp4-wav residual %.1f dB"
          % (len(rows), out["first_sound_s"], out["last_sound_s"], out["file_first_20ms_max"],
             out["file_last_20ms_max"], out["sample_peak"], out["seconds"], out["picture_seconds"],
             out["mp4_minus_wav_rms_db"]))
    print("[mix] ebur128:", out["ebur128_summary"], "| max M %.1f, max S %.1f" % (out["max_momentary"], out["max_short_term"]))
    print("[mix] loudest first ms of a run:", max(rows, key=lambda r: r["max_abs_first_1ms"]))
    print("[mix] loudest last ms of a run:", max(rows, key=lambda r: r["max_abs_last_1ms"]))
    print("[mix] first-sample steps over 1e-3:", [r for r in rows if r["first_sample_abs"] > 1e-3])

    # ---- captions frame by frame
    words = nar["words"]
    seen, scores = NS.caption_frames(MP4, [w["caption"] for w in words])
    out["seen"] = seen
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
    out["caption_runs"] = runs_c
    out["caption_sequence_matches_script"] = got == expected
    out["runs_under_3_frames"] = [r for r in runs_c if r[2] - r[1] + 1 < 3]
    low = sorted(((round(s, 3), i + 1, c) for i, (c, s) in enumerate(zip(seen, scores)) if c), key=lambda t: t[0])[:10]
    out["lowest_match_scores"] = low
    print("[caps] %d frames, %d caption runs, sequence == script: %s" % (len(seen), len(runs_c), got == expected))
    if got != expected:
        import difflib
        for op in difflib.SequenceMatcher(a=expected, b=got, autojunk=False).get_opcodes():
            if op[0] != "equal":
                print("[caps]   ", op[0], expected[op[1]:op[2]], "->", got[op[3]:op[4]], runs_c[op[3]:op[4]])
    print("[caps] runs under 3 frames:", out["runs_under_3_frames"])
    print("[caps] lowest match scores:", low)
    across = []
    for word, f0, f1 in runs_c:
        for name, a, b in cuts:
            if f0 <= b < f1:
                across.append({"word": word, "frames": [f0, f1], "cut_after": b, "shot": name})
    out["captions_across_a_cut"] = across
    print("[caps] captions across a cut:", across)
    per_shot = []
    for name, a, b in cuts:
        on = [i + 1 for i in range(a - 1, b) if seen[i]]
        per_shot.append({"shot": name, "frames": [a, b], "first_caption": on[0] if on else None,
                         "last_caption": on[-1] if on else None,
                         "uncaptioned_tail": (b - on[-1]) if on else b - a + 1,
                         "uncaptioned_head": (on[0] - a) if on else b - a + 1})
    out["per_shot"] = per_shot
    for r in per_shot:
        print("[caps] %-14s %4d-%4d  first caption %s, last %s  head %2d  tail %2d"
              % (r["shot"], r["frames"][0], r["frames"][1], r["first_caption"], r["last_caption"],
                 r["uncaptioned_head"], r["uncaptioned_tail"]))

    # ---- motion in the pauses (source frames, no captions)
    from PIL import Image

    def img(f):
        return np.asarray(Image.open(SRC % f).convert("L"), dtype=np.float32)

    spans = []
    sents = nar["sentences"]
    for s, nxt in zip(sents, sents[1:] + [None]):
        t_end = s["end"]
        t_next = nxt["start"] if nxt else nar["duration"]
        if t_next - t_end >= 0.6:
            spans.append(("pause after " + s["id"], int(t_end * fps) + 1, min(nar["frames"], int(t_next * fps))))
    mres = []
    for sid, f0, f1 in spans:
        frames = [img(f) for f in range(f0, f1 + 1)]
        d1 = [float(np.mean(np.abs(a - b))) for a, b in zip(frames, frames[1:])]
        dend = float(np.mean(np.abs(frames[0] - frames[-1])))
        shots_in = sorted({nm for nm, a, b in cuts if a <= f1 and b >= f0})
        mres.append({"span": sid, "frames": [f0, f1], "n": f1 - f0 + 1, "shots": shots_in,
                     "mean_step": round(float(np.mean(d1)), 2) if d1 else None,
                     "min_step": round(float(np.min(d1)), 2) if d1 else None,
                     "max_step": round(float(np.max(d1)), 2) if d1 else None, "first_vs_last": round(dend, 2)})
        print("[motion] %-18s %4d-%4d (%2d) %-28s mean %5.2f  min %5.2f  max %6.2f  first-vs-last %6.2f"
              % (sid, f0, f1, f1 - f0 + 1, ",".join(shots_in), mres[-1]["mean_step"] or 0, mres[-1]["min_step"] or 0,
                 mres[-1]["max_step"] or 0, dend))
    out["pause_motion"] = mres
    dst = os.path.join(ROOT, "out", "test", "check_hello_review_sync_r2_mix.json")
    with open(dst, "w") as f:
        json.dump(out, f, indent=1, default=float)
    print("->", dst)


if __name__ == "__main__":
    main()
