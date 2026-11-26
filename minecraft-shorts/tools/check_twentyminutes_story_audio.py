"""Checker probe: the narration wav against its json: length, peaks, energy in the pauses, onsets of words after a
silence vs Word.frame (frames), the energy of each sentence (no clip, no dropout)."""
import os, sys, wave
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from engine import narration
nar = narration.load("twentyminutes")
w = wave.open(nar.wav)
sr, n, ch, sw = w.getframerate(), w.getnframes(), w.getnchannels(), w.getsampwidth()
x = np.frombuffer(w.readframes(n), dtype={2: np.int16, 4: np.int32}[sw]).astype(np.float64)
x = x.reshape(-1, ch).mean(axis=1) / (2 ** (8 * sw - 1))
print("wav %d Hz %d ch %d s=%.3f  film %.3f s  peak %.3f (%.1f dBFS)" % (sr, ch, sw, n / sr, nar.duration, abs(x).max(), 20 * np.log10(abs(x).max())))
def rms(a, b):
    seg = x[int(a * sr):int(b * sr)]
    return 20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-12) if len(seg) else -999
print("lead silence rms %.1f dB, tail after last word %.1f dB" % (rms(0, nar.words[0].start - 0.02), rms(nar.words[-1].end + 0.05, nar.duration)))
for i, s in enumerate(nar.sentences):
    nxt = nar.sentences[i + 1].start if i + 1 < len(nar.sentences) else nar.duration
    gap = rms(s.end + 0.03, nxt - 0.03) if nxt - s.end > 0.1 else None
    print("%s speech %.1f dB  pause %.2f s rms %s" % (s.id, rms(s.start, s.end), nxt - s.end, "%.1f dB" % gap if gap is not None else "-"))
# onset of each sentence's first word: first 5 ms window above -35 dBFS after (start - 0.2)
win = int(0.005 * sr)
for s in nar.sentences:
    a = int(max(0, s.start - 0.25) * sr)
    seg = x[a:a + int(0.6 * sr)]
    e = np.array([np.sqrt((seg[k:k + win] ** 2).mean()) for k in range(0, len(seg) - win, win)])
    db = 20 * np.log10(e + 1e-12)
    k = next((i for i, v in enumerate(db) if v > -35), None)
    on = (a + (k or 0) * win) / sr
    print("%s first word %-10s json %.3f (frame %d)  onset -35dB %.3f (frame %d)" % (s.id, s.words[0].caption, s.start, s.words[0].frame, on, int(on * 24) + 1))
