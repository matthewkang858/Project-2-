"""Independent check of caption-to-voice sync in an ENCODED narrated film (checker's probe, not part of the engine).

    $BPY -m tools.check_narration_sync <mp4> <narration json> [prefix]

Own method, nothing of tools/narration_sync.py or tools/narrate.py is imported:
  * captions: every frame decoded, the caption band's white-pixel mask is compared (F1) with the bitmap of every
    script word drawn by engine.captions; first frame of each word in script order = measured caption onset
  * audio: the mp4's own audio, decoded; (a) onsets after silence by a plain energy threshold, (b) wide-band
    spectrograms per sentence written as PNG with the json's word starts (red), the recogniser's second opinion
    (cyan) and the frame on which the caption was SEEN (green) drawn in, to be read by eye
  * band energies around every claimed word start are printed (low 80-1000 Hz, high 4-11 kHz)
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from engine import captions as cap                                   # noqa: E402

SR = 24000
FPS = 24.0


def audio_of(path, sr=SR):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0", "-ar", str(sr), "-ac", "1", "-f", "f32le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype="<f4").astype(np.float64)


def seen_captions(path, words, size=(1080, 1920), whole_rows=False):
    W, H = size
    y0, y1 = int(H * 0.58) // 2 * 2, int(H * 0.76) // 2 * 2      # even: ffmpeg's crop rounds to the chroma grid
    tmpl = {}
    for w in sorted(set(words)):
        layer = np.asarray(cap.draw_caption(w, size))[y0:y1]
        white = (layer[..., 3] == 255) & (layer[..., :3].min(axis=2) >= 250)
        ys, xs = np.nonzero(white)
        box = (max(0, ys.min() - 6), ys.max() + 7, max(0, xs.min() - 6), xs.max() + 7)
        if whole_rows:                                  # a short word inside a longer one ('it' in 'with') must not match
            box = (box[0], box[1], 0, W)
        tmpl[w] = (white[box[0]:box[1], box[2]:box[3]], box)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-map", "0:v:0", "-vf", "crop=%d:%d:0:%d" % (W, y1 - y0, y0),
                             "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = W * (y1 - y0) * 3
    out, prev, change = [], None, []
    while True:
        buf = proc.stdout.read(n)
        if len(buf) < n:
            break
        img = np.frombuffer(buf, dtype=np.uint8).reshape(y1 - y0, W, 3)
        white = img.min(axis=2) >= 200
        best, best_f = None, 0.0
        for w, (t, b) in tmpl.items():
            sub = white[b[0]:b[1], b[2]:b[3]]
            tp = float((sub & t).sum())
            if tp == 0:
                continue
            prec, rec = tp / max(1.0, float(sub.sum())), tp / float(t.sum())
            f1 = 2 * prec * rec / (prec + rec)
            if f1 > best_f:
                best, best_f = w, f1
        out.append((best if best_f >= 0.80 else None, round(best_f, 3)))
        change.append(0 if prev is None else int((white ^ prev).sum()))
        prev = white
    proc.wait()
    return out, change


def stft_db(x, sr=SR, win=0.006, hop=0.002, nfft=256):
    w, h = int(win * sr), int(hop * sr)
    n = 1 + (len(x) - w) // h
    idx = np.arange(w)[None, :] + h * np.arange(n)[:, None]
    seg = x[idx] * np.hanning(w)[None, :]
    spec = np.abs(np.fft.rfft(seg, nfft, axis=1))
    return 20 * np.log10(spec + 1e-9), h / sr, sr / nfft


def band_env(x, lo, hi, sr=SR, win=0.010, hop=0.001):
    """Energy envelope (dB) of a band, 10 ms window every 1 ms, time = window CENTRE."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1.0 / sr)
    X[(f < lo) | (f > hi)] = 0
    y = np.fft.irfft(X, len(x))
    w, h = int(win * sr), int(hop * sr)
    c = np.concatenate([[0.0], np.cumsum(y * y)])
    starts = np.arange(0, len(y) - w, h)
    return 10 * np.log10((c[starts + w] - c[starts]) / w + 1e-12), (starts + w / 2.0) / sr


def spectrogram_png(x, t0, t1, marks, path, title=""):
    """Wide-band spectrogram of x[t0:t1] (2 ms per pixel, 0-12 kHz), waveform above; marks = [(t, colour, label, row)]."""
    a, b = max(0, int(t0 * SR)), min(len(x), int(t1 * SR))
    S, dt, df = stft_db(x[a:b])
    S = S - S.max()
    img = np.clip((S + 65.0) / 65.0, 0, 1)                      # 65 dB range
    img = (255 * (1 - img)).astype(np.uint8).T[::-1]            # freq up, dark = loud
    scale_y = 3
    img = np.repeat(img, scale_y, axis=0)
    Wd, Hs = img.shape[1], img.shape[0]
    top, wav_h, bot = 46, 90, 30
    canvas = Image.new("RGB", (Wd, top + wav_h + Hs + bot), (255, 255, 255))
    canvas.paste(Image.fromarray(img).convert("RGB"), (0, top + wav_h))
    d = ImageDraw.Draw(canvas)
    seg = x[a:b]
    peak = np.abs(seg).max() + 1e-9
    for px in range(Wd):
        s = seg[int(px * dt * SR):int((px + 1) * dt * SR) + 1]
        if len(s):
            d.line([(px, top + wav_h / 2 - s.max() / peak * wav_h / 2), (px, top + wav_h / 2 - s.min() / peak * wav_h / 2)], fill=(40, 40, 40))
    # frame grid (video frames) and 100 ms ticks
    k = int(np.ceil(t0 * FPS))
    while k / FPS < t1:
        px = int((k / FPS - t0) / dt)
        d.line([(px, top + wav_h + Hs), (px, top + wav_h + Hs + 8)], fill=(0, 0, 0))
        if k % 2 == 0:
            d.text((px + 1, top + wav_h + Hs + 9), str(k + 1), fill=(0, 0, 0))
        k += 1
    for t, colour, label, row in marks:
        if not (t0 <= t < t1):
            continue
        px = int((t - t0) / dt)
        if row == 2:                                            # caption seen: bottom half tick
            d.line([(px, top + wav_h + Hs - 60), (px, top + wav_h + Hs + 14)], fill=colour, width=2)
        else:
            d.line([(px, top - 4 if row == 0 else top + wav_h), (px, top + wav_h + Hs - 62)], fill=colour, width=1)
        if label:
            d.text((px + 2, 2 + 14 * row if row < 2 else top + wav_h + Hs + 18), label, fill=colour)
    for khz in (1, 2, 4, 6, 8, 10):
        y = top + wav_h + Hs - int(khz * 1000 / df) * scale_y
        d.line([(0, y), (6, y)], fill=(255, 0, 0))
        d.text((8, y - 5), "%dk" % khz, fill=(255, 0, 0))
    d.text((Wd - 330, top + wav_h + Hs + 18), title, fill=(0, 0, 0))
    canvas.save(path)
    return path


def main():
    mp4, js = sys.argv[1], sys.argv[2]
    prefix = sys.argv[3] if len(sys.argv) > 3 else "check_narration_sync"
    with open(js, encoding="utf-8") as f:
        nar = json.load(f)
    words = nar["words"]
    x = audio_of(mp4)
    print("audio %.4f s decoded, peak %.3f" % (len(x) / SR, np.abs(x).max()))

    # ---- captions seen
    seen, change = seen_captions(mp4, [w["caption"] for w in words])
    first, k = [], 0
    for w in words:
        while k < len(seen) and seen[k][0] != w["caption"]:
            k += 1
        first.append(k if k < len(seen) else None)
        k = min(len(seen), k + 1)
    labels = [s[0] for s in seen]
    runs, i = [], 0
    while i < len(labels):
        j = i
        while j + 1 < len(labels) and labels[j + 1] == labels[i]:
            j += 1
        runs.append((labels[i], i + 1, j + 1))
        i = j + 1
    print("frames decoded:", len(seen))
    print("caption runs (word, first frame NUMBER, last):", runs)
    # every caption onset must be a real picture change in the band
    for w, f in zip(words, first):
        if f is not None and f > 0 and change[f] < 200:
            print("  !! no pixel change at the onset of", w["caption"], f, change[f])

    # ---- energy onsets after silence (own threshold: -38 dB re the file's loudest 10 ms, silence >= 120 ms)
    env, tt = band_env(x, 60, 11500)
    thr = env.max() - 38.0
    act = env > thr
    onsets, offsets = [], []
    i = 0
    quiet = 1000
    while i < len(act):
        if act[i]:
            if quiet >= 120:
                onsets.append(tt[i])
            quiet = 0
        else:
            if quiet == 0:
                offsets.append(tt[i])
            quiet += 1
        i += 1
    print("energy onsets after >=120 ms silence:", [round(float(o), 3) for o in onsets])

    lo_env, _ = band_env(x, 80, 1000)
    hi_env, _ = band_env(x, 4000, 11000)

    rows = []
    print("%-10s %8s %8s %6s | %7s %7s %7s | %s" % ("word", "start", "second", "capfr", "cap-st", "cap-2nd", "cap-on", "source"))
    for w, f in zip(words, first):
        t_cap = None if f is None else f / FPS
        near = [o for o in onsets if abs(o - w["start"]) < 0.08]
        row = {"word": w["caption"], "start": w["start"], "second": w.get("second"), "frame": None if f is None else f + 1,
               "cap_minus_start_fr": None if f is None else round((t_cap - w["start"]) * FPS, 2),
               "cap_minus_second_fr": None if (f is None or w.get("second") is None) else round((t_cap - w["second"]) * FPS, 2),
               "energy_onset": round(float(near[0]), 4) if near else None,
               "cap_minus_onset_fr": round((t_cap - near[0]) * FPS, 2) if (near and f is not None) else None}
        rows.append(row)
        print("%-10s %8.3f %8s %6s | %7s %7s %7s | %s" % (row["word"], w["start"], w.get("second"), row["frame"], row["cap_minus_start_fr"],
                                                           row["cap_minus_second_fr"], row["cap_minus_onset_fr"], w["source"]))
    d = np.array([r["cap_minus_start_fr"] for r in rows if r["cap_minus_start_fr"] is not None])
    print("caption minus json start (frames): min %.2f max %.2f mean %.2f; late (>0): %d; earlier than -1: %d"
          % (d.min(), d.max(), d.mean(), int((d > 1e-6).sum()), int((d < -1).sum())))

    # ---- spectrograms per sentence
    out_dir = os.path.join(ROOT, "out", "test")
    for s in nar["sentences"]:
        t0, t1 = s["start"] - 0.12, s["end"] + 0.12
        marks = []
        for w, f in zip(words, first):
            if w["sentence"] != s["index"]:
                continue
            marks.append((w["start"], (220, 0, 0), w["caption"], 0))
            if w.get("second") is not None:
                marks.append((w["second"], (0, 150, 200), "", 1))
            if f is not None:
                marks.append((f / FPS, (0, 170, 0), "", 2))
        p = spectrogram_png(x, t0, t1, marks, os.path.join(out_dir, "%s_spec_s%d.png" % (prefix, s["index"])),
                            "red=json start cyan=recogniser green=caption seen; ticks=video frames")
        print("wrote", os.path.relpath(p, ROOT), "t0=%.3f" % t0)
    with open(os.path.join(out_dir, prefix + "_rows.json"), "w") as f:
        json.dump({"rows": rows, "runs": runs, "onsets": [float(o) for o in onsets]}, f, indent=1)


if __name__ == "__main__":
    main()
