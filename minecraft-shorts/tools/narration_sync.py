"""Proof of sync for an ENCODED narrated film: what is in the mp4, not what the scripts intended.

    $BPY -m tools.narration_sync <film> [file.mp4] [--no-hear]

(default file: out/<film>.mp4, else the newest out/preview/<film>_*.mp4). Needs the film's narration
(narration/<film>.json + .wav) and, for the recogniser part, the TTS interpreter in $TTS (default: the session's
scratchpad venv); --no-hear skips that part, or reuses out/test/narrate_heard_<mp4 name>.json if it is there.

What is measured, all of it from the mp4 file itself:
  container   video and audio streams (codec, 48 kHz stereo AAC, durations, start times), moov before mdat
              (fast start), left channel == right channel (dual mono), loudness of the stereo programme
  audio       the mp4's decoded audio against narration/<film>.wav: lag by cross-correlation (0 = starts at t = 0)
  captions    every video frame is decoded; the caption band is matched against the real caption bitmap of each
              word (engine.captions.draw_caption: white glyphs AND dark outline must both be there). The first
              frame on which each word of the script is visible is the caption's measured start. (A word spoken in
              under two frames is ASKED to appear one frame sooner, see engine.narration: such a word shows an
              offset between -1 and -2.)
  onsets      three references for when a word is SPOKEN:
                narration   the json's start (voice model + energy; what the film was built from)
                sound       for the first word of a sentence and words after a pause: the first sound after
                            the silence, measured on the mp4's own audio (no model, no recogniser)
                heard       the recogniser run on the mp4's audio (tools/narrate.py --hear), nothing else known
  For every word: caption frame minus spoken frame, in frames (negative = the caption is up before the word).
Writes out/test/narration_sync_<film>.json and prints the table. Exit code 1 when a caption is late against the
narration or the measured sound, the audio is offset, or the container is not as specified.
"""
import json
import os
import struct
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from engine import captions as cap                                   # noqa: E402
from engine import narration                                         # noqa: E402

TTS_DEFAULT = "/tmp/claude-0/-home-user-Project-2-/be90bb9d-3fc7-572c-941a-ff79c8b6ef48/scratchpad/tts/bin/python"
SR = 24000


def atoms(path):
    """Top-level boxes of an mp4 in file order: [(type, offset, size), ...]."""
    out, pos, size_total = [], 0, os.path.getsize(path)
    with open(path, "rb") as f:
        while pos + 8 <= size_total:
            f.seek(pos)
            size, kind = struct.unpack(">I4s", f.read(8))
            if size == 1:
                size = struct.unpack(">Q", f.read(8))[0]
            elif size == 0:
                size = size_total - pos
            out.append((kind.decode("latin1"), pos, size))
            if size < 8:
                break
            pos += size
    return out


def streams(path):
    """ffprobe of both streams: {'video': {...}, 'audio': {...} or None}."""
    raw = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                                   "stream=codec_type,codec_name,profile,width,height,r_frame_rate,pix_fmt,nb_frames,"
                                   "duration,start_time,sample_rate,channels,channel_layout,bit_rate", "-of", "json", path])
    out = {"video": None, "audio": None}
    for s in json.loads(raw)["streams"]:
        out[s["codec_type"]] = s
    return out


def decode_audio(path, sr=SR, channels=1):
    """Audio of any file as float32, shape (samples,) for mono or (samples, channels)."""
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0", "-ar", str(sr), "-ac", str(channels),
                        "-f", "f32le", "-"], capture_output=True, check=True)
    a = np.frombuffer(p.stdout, dtype="<f4")
    return a if channels == 1 else a.reshape(-1, channels)


def ebur128(path):
    """(integrated LUFS, true peak dBTP) of a file's audio as it is (stereo stays stereo)."""
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-map", "0:a:0", "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True)
    text = p.stderr.decode(errors="replace")
    tail = text[text.rfind("Summary:"):]
    import re

    i = re.search(r"I:\s*(-?[\d.]+|-inf)\s*LUFS", tail)
    tp = re.search(r"Peak:\s*(-?[\d.]+|-inf)\s*dBFS", tail)
    return float(i.group(1)), float(tp.group(1))


def lag_of(a, b, sr=SR, reach=0.5):
    """How many seconds `a` is LATER than `b` (cross-correlation within +-reach), and the correlation there."""
    n = min(len(a), len(b))
    a, b = np.asarray(a[:n], dtype=np.float64), np.asarray(b[:n], dtype=np.float64)
    size = 1
    while size < 2 * n:
        size *= 2
    cc = np.fft.irfft(np.fft.rfft(a, size) * np.conj(np.fft.rfft(b, size)), size)
    r = int(reach * sr)
    lags = np.concatenate([np.arange(0, r + 1), np.arange(-r, 0)])
    vals = np.concatenate([cc[:r + 1], cc[-r:]])
    k = int(np.argmax(vals))
    return lags[k] / float(sr), float(vals[k] / (np.sqrt(np.sum(a * a) * np.sum(b * b)) + 1e-12))


def sound_runs(x, sr=SR, rel_db=-40.0, min_gap=0.030, min_run=0.025):
    """Where there is sound: [(t0, t1)] (the same rule as tools/narrate.py: 10 ms frames within 40 dB of the loudest)."""
    h, w = int(0.005 * sr), int(0.010 * sr)
    x = np.asarray(x, dtype=np.float64)
    c = np.concatenate([[0.0], np.cumsum(x * x)])
    starts = np.arange(0, len(x) - w + 1, h)
    rms = np.sqrt((c[starts + w] - c[starts]) / w)
    act = rms > max(rms.max() * 10 ** (rel_db / 20.0), 10 ** (-62 / 20.0))
    runs, i = [], 0
    while i < len(act):
        if act[i]:
            j = i
            while j < len(act) and act[j]:
                j += 1
            runs.append([i * 0.005, j * 0.005 + 0.005])
            i = j
        else:
            i += 1
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] < min_gap:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    return [(a, b) for a, b in merged if b - a >= min_run]


def caption_frames(path, words, size=(1080, 1920)):
    """Decode every frame and say which caption is on it: (list of word or None per frame, list of match scores).
    A word counts as visible when at least 80 % of its white glyph pixels are white AND 80 % of its outline
    pixels are dark in the frame (scenery that happens to be white has no outline around it)."""
    W, H = size
    y0, y1 = int(H * (cap.CAPTION_BAND[0] - 0.03)), int(H * (cap.CAPTION_BAND[1] + 0.03))
    masks = {}
    for w in sorted(set(words)):
        layer = np.asarray(cap.draw_caption(w, size))[y0:y1]
        white = (layer[..., 3] == 255) & (layer[..., :3].min(axis=2) >= 250)
        dark = (layer[..., 3] > 200) & (layer[..., :3].max(axis=2) <= 20)
        masks[w] = (white, dark, int(white.sum()), int(dark.sum()))
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-map", "0:v:0", "-vf", "crop=%d:%d:0:%d" % (W, y1 - y0, y0),
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = W * (y1 - y0) * 3
    seen, scores = [], []
    while True:
        buf = proc.stdout.read(n)
        if len(buf) < n:
            break
        img = np.frombuffer(buf, dtype=np.uint8).reshape(y1 - y0, W, 3)
        is_white, is_dark = img.min(axis=2) > 190, img.max(axis=2) < 90
        best, best_s = None, 0.0
        for w, (white, dark, nw, nd) in masks.items():
            s = min(float((is_white & white).sum()) / max(nw, 1), float((is_dark & dark).sum()) / max(nd, 1))
            # a word that is part of another ('a' in 'all') also matches the longer one's frame: prefer the
            # candidate with more pixels when both match
            if s >= 0.8 and (best is None or nw > masks[best][2]):
                best, best_s = w, s
        seen.append(best)
        scores.append(best_s)
    proc.wait()
    return seen, scores


def main(argv=None):
    args = [a for a in (sys.argv[1:] if argv is None else argv) if not a.startswith("--")]
    flags = [a for a in (sys.argv[1:] if argv is None else argv) if a.startswith("--")]
    if not args:
        print(__doc__)
        return 1
    film = narration.film_name(args[0])
    nar = narration.load(film)
    if len(args) > 1:
        mp4 = args[1]
    else:
        mp4 = os.path.join(ROOT, "out", film + ".mp4")
        if not os.path.exists(mp4):
            pre = os.path.join(ROOT, "out", "preview")
            cands = sorted((os.path.join(pre, f) for f in os.listdir(pre) if f.startswith(film + "_") and f.endswith(".mp4")),
                           key=os.path.getmtime)
            if not cands:
                print("no mp4 of '%s' under out/ or out/preview/" % film)
                return 1
            mp4 = cands[-1]
    fps = nar.fps
    problems = []
    print("[sync] %s  against narration/%s.json (%d words, %d frames)" % (os.path.relpath(mp4, ROOT), film, len(nar.words), nar.frames))

    # ---- container
    st = streams(mp4)
    v, a = st["video"], st["audio"]
    order = [k for k, _o, _s in atoms(mp4)]
    fast = "moov" in order and "mdat" in order and order.index("moov") < order.index("mdat")
    if a is None:
        print("[sync] the file has NO audio stream")
        return 1
    stereo = decode_audio(mp4, 48000, 2)
    dual = float(np.abs(stereo[:, 0] - stereo[:, 1]).max())
    lufs, tp = ebur128(mp4)
    n_frames = int(v["nb_frames"])
    v_dur, a_dur = float(v["duration"]), float(a["duration"])
    container = {
        "video": "%s %sx%s %s %s fps, %d frames, %.6f s, start %s" % (v["codec_name"], v["width"], v["height"], v["pix_fmt"],
                                                                     v["r_frame_rate"], n_frames, v_dur, v["start_time"]),
        "audio": "%s %s Hz %s ch (%s), %.6f s, start %s, %d kb/s" % (a["codec_name"], a["sample_rate"], a["channels"],
                                                                     a.get("channel_layout"), a_dur, a["start_time"],
                                                                     int(a.get("bit_rate", 0)) // 1000),
        "atoms": order, "fast_start": fast, "decoded_audio_samples_48k": int(len(stereo)),
        "audio_minus_video_ms": round(1000 * (len(stereo) / 48000.0 - n_frames / float(fps)), 3),
        "left_minus_right_max": dual, "integrated_lufs": lufs, "true_peak_db": tp,
    }
    for key, val in container.items():
        print("[sync]   %-26s %s" % (key, val))
    if not fast:
        problems.append("moov is not before mdat (no fast start)")
    if a["codec_name"] != "aac" or int(a["sample_rate"]) != 48000 or int(a["channels"]) != 2:
        problems.append("audio is not AAC 48 kHz stereo")
    if dual > 1e-3:                                    # -60 dB: the AAC decoder's own rounding is about -80 dB
        problems.append("left and right differ by up to %.1f dB (not dual mono)" % (20 * np.log10(dual)))
    if abs(container["audio_minus_video_ms"]) > 1000.0 / 48.0 or abs(a_dur - v_dur) > 0.002:
        problems.append("audio and video differ in length")
    if abs(float(a["start_time"])) > 1e-6 or abs(float(v["start_time"])) > 1e-6:
        problems.append("a stream does not start at t = 0")

    # ---- audio against the narration wav
    mono = decode_audio(mp4, SR, 1)
    wav = decode_audio(nar.wav, SR, 1)
    lag, corr = lag_of(mono, wav)
    left = decode_audio(mp4, SR, 2)[:, 0]
    n = min(len(left), len(wav))
    gain = 20 * np.log10(np.sqrt(np.mean(left[:n] ** 2)) / np.sqrt(np.mean(wav[:n] ** 2)))
    print("[sync]   mp4 audio vs narration wav: lag %+.2f ms (correlation %.4f); each channel is the wav at %+.2f dB"
          % (1000 * lag, corr, gain))
    if abs(lag) > 0.002 or corr < 0.95:
        problems.append("the mp4's audio is not the narration at t = 0 (lag %.1f ms, correlation %.3f)" % (1000 * lag, corr))

    # ---- captions on the decoded frames
    words = [w for w in nar.words if w.caption]
    seen, scores = caption_frames(mp4, [w.caption for w in words])
    if len(seen) != n_frames:
        problems.append("decoded %d frames, the stream says %d" % (len(seen), n_frames))
    first, k = [], 0
    for w in words:                                    # first frame on which each word, in order, is visible
        while k < len(seen) and seen[k] != w.caption:
            k += 1
        first.append(k if k < len(seen) else None)
        k = k + 1 if k < len(seen) else k
    last = []
    for i, f in enumerate(first):
        if f is None:
            last.append(None)
            continue
        j = f
        while j + 1 < len(seen) and seen[j + 1] == words[i].caption and (i + 1 >= len(first) or first[i + 1] is None or j + 1 < first[i + 1]):
            j += 1
        last.append(j)

    # ---- the measured sound of the mp4 (first word of each sentence, words after a pause)
    runs = sound_runs(mono)
    onsets = np.array([r[0] for r in runs])

    # ---- the recogniser on the mp4's audio
    heard = None
    heard_path = os.path.join(ROOT, "out", "test", "narrate_heard_%s.json" % os.path.splitext(os.path.basename(mp4))[0])
    if "--no-hear" not in flags:
        tts = os.environ.get("TTS", TTS_DEFAULT)
        if os.path.exists(tts):
            subprocess.run([tts, os.path.join(ROOT, "tools", "narrate.py"), film, "--hear", mp4], check=False)
        else:
            print("[sync]   (no TTS interpreter at %s: recogniser part skipped)" % tts)
    if os.path.exists(heard_path) and os.path.getmtime(heard_path) >= os.path.getmtime(mp4):
        with open(heard_path, encoding="utf-8") as f:
            heard = json.load(f).get("words")
        if heard is not None and len(heard) != len(nar.words):
            heard = None

    rows = []
    asked = nar.caption_frames()                       # (caption, first frame, last frame) the film asked for
    print("[sync]   word         caption frames   spoken (narration)   offset   sound onset  offset   heard (recogniser)  offset")
    for i, w in enumerate(words):
        f = first[i]
        row = {"word": w.caption, "caption_first_frame": None if f is None else f + 1,
               "caption_last_frame": None if last[i] is None else last[i] + 1,
               "narration_start": round(w.start, 4), "source": w.source}
        if f is None:
            problems.append("caption %r (word %d) was never seen" % (w.caption, w.index))
            rows.append(row)
            continue
        t_cap = f / float(fps)
        row["offset_vs_narration_frames"] = round((t_cap - w.start) * fps, 2)
        if row["offset_vs_narration_frames"] > 1e-6:
            problems.append("caption %r is LATE against the narration by %.2f frames" % (w.caption, row["offset_vs_narration_frames"]))
        if f + 1 != asked[i][1]:
            problems.append("caption %r is on frame %d, the film asked for %d" % (w.caption, f + 1, asked[i][1]))
        row["frames_before_the_frame_of_its_word"] = nar.words[w.index].frame - (f + 1)
        if w.source == "energy" and len(onsets):
            j = int(np.argmin(np.abs(onsets - w.start)))
            if abs(onsets[j] - w.start) < 0.06:
                row["sound_onset"] = round(float(onsets[j]), 4)
                row["offset_vs_sound_frames"] = round((t_cap - onsets[j]) * fps, 2)
                if row["offset_vs_sound_frames"] > 1.0:
                    problems.append("caption %r is more than a frame late against the measured sound" % w.caption)
        if heard is not None:
            h = heard[w.index]
            row["heard_start"] = h["start"]
            row["heard_kind"] = h["kind"]
            row["offset_vs_heard_frames"] = round((t_cap - h["start"]) * fps, 2)
        rows.append(row)
        print("[sync]   %-12s %4d-%-4d        %7.3f s (%-6s)  %+5.2f    %s   %s    %s   %s"
              % (w.caption, f + 1, last[i] + 1, w.start, w.source, row["offset_vs_narration_frames"],
                 "%7.3f s" % row["sound_onset"] if "sound_onset" in row else "    -    ",
                 "%+5.2f" % row["offset_vs_sound_frames"] if "sound_onset" in row else "  -  ",
                 "%7.3f s %-6s" % (row["heard_start"], row["heard_kind"]) if "heard_start" in row else "       -       ",
                 "%+5.2f" % row["offset_vs_heard_frames"] if "heard_start" in row else "  -  "))

    def spread(key):
        vals = [r[key] for r in rows if key in r]
        if not vals:
            return None
        arr = np.array(vals)
        return {"n": len(vals), "min": float(arr.min()), "max": float(arr.max()), "mean": round(float(arr.mean()), 2),
                "within_-1..+1": int(np.sum((arr >= -1.0) & (arr <= 1.0))), "late_over_1": int(np.sum(arr > 1.0)),
                "early_over_1": int(np.sum(arr < -1.0))}

    summary = {"caption_minus_narration_frames": spread("offset_vs_narration_frames"),
               "caption_minus_measured_sound_frames": spread("offset_vs_sound_frames"),
               "caption_minus_recogniser_frames": spread("offset_vs_heard_frames")}
    for key, val in summary.items():
        print("[sync]   %-38s %s" % (key, val))
    out = {"film": film, "file": os.path.relpath(mp4, ROOT), "fps": fps, "container": container,
           "audio_lag_ms": round(1000 * lag, 3), "audio_correlation": round(corr, 4), "channel_gain_db": round(float(gain), 2),
           "caption_match_score_min": round(min((s for s, c in zip(scores, seen) if c), default=0.0), 3),
           "summary": summary, "words": rows, "problems": problems}
    dst = os.path.join(ROOT, "out", "test", "narration_sync_%s.json" % film)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("[sync] %s -> %s" % ("PASSED" if not problems else "FAILED: " + "; ".join(problems), os.path.relpath(dst, ROOT)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
