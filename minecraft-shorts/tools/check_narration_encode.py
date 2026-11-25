"""Checker's probe (BPY interpreter, no bpy needed): the one-minute probe narration through the real encoder
(engine.post.encode with audio -> mux_audio), on synthetic frames, then sync measured in the encoded file from its
first to its last word (drift), container and loudness. Everything is written under out/test/check_narration_*.

    $BPY -m tools.check_narration_encode encode      # frames + mp4 (540x960 to stay inside the time limit)
    $BPY -m tools.check_narration_encode measure
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from engine import narration as N                                    # noqa: E402
from engine import post                                              # noqa: E402
from tools.check_narration_sync import audio_of, seen_captions, band_env, SR   # noqa: E402

NAME = "check_minute"
DIR = os.path.join(ROOT, "out", "test", "check_narration_dir")
OUT = os.path.join(ROOT, "out", "test", "check_narration_out")
MP4 = os.path.join(ROOT, "out", "test", "check_narration_minute.mp4")
SIZE = (540, 960)


def spec():
    src = open(os.path.join(ROOT, "tools", "check_narration_minute.py"), encoding="utf-8").read()
    import ast
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "SPEC":
            return ast.literal_eval(node.value)


def encode():
    N.NARRATION_DIR = DIR
    nar = N.load(NAME, spec())
    post.OUT = OUT
    d = post.frames_dir(NAME)
    os.makedirs(d, exist_ok=True)
    yy = np.linspace(40, 110, 160)[:, None] * np.ones((1, 90))
    for f in range(1, nar.frames + 1):
        p = post.frame_path(NAME, f)
        if os.path.exists(p):
            continue
        a = np.stack([yy * 0.6, yy * 0.8, yy], axis=2)
        a[8:20, (f * 3) % 80:(f * 3) % 80 + 8] = (200, 60, 60)        # something that moves, away from the caption band
        Image.fromarray(a.astype(np.uint8)).save(p)
    post.write_meta(NAME, {"fps": 24, "frame_start": 1, "frame_end": nar.frames, "captions": [list(c) for c in nar.captions()],
                           "signature": "check", "frames": {str(f): "check" for f in range(1, nar.frames + 1)}})
    mp4 = post.encode(NAME, captions=nar.captions(), fps=24, frame_start=1, frame_end=nar.frames, out_path=MP4, size=SIZE, audio=nar.wav)
    print("video:", post.probe(mp4))
    print("audio:", post.probe_audio(mp4))


def measure():
    N.NARRATION_DIR = DIR
    nar = N.load(NAME, spec())
    v, a = post.probe(MP4), post.probe_audio(MP4)
    print("video:", v)
    print("audio:", a)
    x = audio_of(MP4)                                   # 24 kHz mono
    w = audio_of(nar.wav)
    print("decoded audio %.4f s, wav %.4f s, video %.4f s" % (len(x) / SR, len(w) / SR, v["frames"] / v["fps"]))
    # lag of the mp4's audio against the wav in three 6 s windows (start, middle, end): constant = no drift
    for label, t0 in (("start", 0.0), ("middle", nar.duration / 2 - 3), ("end", nar.duration - 7.0)):
        i0, n = int(t0 * SR), int(6 * SR)
        A, B = x[i0:i0 + n], w[i0:i0 + n]
        size = 1 << int(np.ceil(np.log2(2 * n)))
        cc = np.fft.irfft(np.fft.rfft(A, size) * np.conj(np.fft.rfft(B, size)), size)
        r = int(0.3 * SR)
        lags = np.concatenate([np.arange(0, r + 1), np.arange(-r, 0)])
        vals = np.concatenate([cc[:r + 1], cc[-r:]])
        k = int(np.argmax(vals))
        print("  audio lag vs wav at the %-6s: %+.3f ms (correlation %.4f)" % (label, 1000 * lags[k] / SR,
              vals[k] / (np.sqrt((A * A).sum() * (B * B).sum()) + 1e-12)))
    words = [wd for wd in nar.words if wd.caption]
    seen, change = seen_captions(MP4, [wd.caption for wd in words], size=SIZE, whole_rows=True)
    print("frames decoded:", len(seen), "of", nar.frames)
    first, k = [], 0
    for wd in words:
        while k < len(seen) and seen[k][0] != wd.caption:
            k += 1
        first.append(k if k < len(seen) else None)
        k = min(len(seen), k + 1)
    missing = [wd.caption for wd, f in zip(words, first) if f is None]
    print("captions never seen:", missing)
    asked = nar.caption_frames()
    wrong = [(wd.caption, f + 1, q[1]) for wd, f, q in zip(words, first, asked) if f is not None and f + 1 != q[1]]
    print("captions not on the frame the film asked for:", wrong)
    d = np.array([(f / 24.0 - wd.start) * 24 for wd, f in zip(words, first) if f is not None])
    print("caption minus json start, frames: min %.2f max %.2f mean %.2f; late %d; more than 1 frame early %d (of %d)"
          % (d.min(), d.max(), d.mean(), int((d > 1e-6).sum()), int((d < -1.0).sum()), len(d)))
    # my own onsets after silence, in the mp4's audio: plain threshold 28 dB under the loudest 10 ms of the file,
    # after at least 100 ms below it (a clearly audible return of the voice, not a murmur)
    env, tt = band_env(x, 60, 11500)
    act = env > env.max() - 28.0
    on, quiet = [], 1000
    for i in range(len(act)):
        if act[i]:
            if quiet >= 100:
                on.append(tt[i])
            quiet = 0
        else:
            quiet += 1
    on = np.array(on)
    rows = []
    for wd, f in zip(words, first):
        if wd.source != "energy" or f is None:
            continue
        j = np.flatnonzero((on >= wd.start - 0.05) & (on <= wd.start + 0.40))
        if not len(j):
            continue
        t = float(on[j[0]])
        rows.append((wd.caption, wd.index == nar.sentences[wd.sentence].words[0].index, wd.start, t, (f / 24.0 - t) * 24))
    print("words the narrator starts on a measured onset: caption frame against the clearly audible onset in the mp4 (frames, negative = caption first)")
    for c, is_first, st, t, off in rows:
        flag = "  <-- more than 2 frames early" if off < -2.0 else ""
        print("   %-10s %s json %.3f  audible %.3f  caption %+.2f%s" % (c, "sentence start" if is_first else "after a pause ", st, t, off, flag))
    offs = np.array([r[4] for r in rows])
    print("   n=%d: within -1..+1: %d, earlier than -2: %d, earlier than -4: %d, late: %d; first 5 mean %.2f, last 5 mean %.2f (drift)"
          % (len(offs), int(((offs >= -1) & (offs <= 1)).sum()), int((offs < -2).sum()), int((offs < -4).sum()), int((offs > 1).sum()),
             offs[:5].mean(), offs[-5:].mean()))
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", MP4, "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True).stderr.decode()
    print(p[p.rfind("Integrated loudness"):].replace("\n\n", "\n"))


if __name__ == "__main__":
    {"encode": encode, "measure": measure}[sys.argv[1]]()
