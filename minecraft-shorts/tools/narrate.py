#!/usr/bin/env python
"""The narrator: speak a film's NARRATION and measure when every word starts.

Runs in the TTS environment, NOT under Blender (bpy and the voice model cannot share an interpreter):

    TTS=/path/to/tts-venv/bin/python          # made by tools/setup_tts.sh (kokoro-onnx, faster-whisper, soundfile)
    $TTS tools/narrate.py <film>              # films/<film>.py NARRATION -> narration/<film>.wav + <film>.json
    $TTS tools/narrate.py <film> --check      # exit 0 if narration/<film>.json is current for the film's text, else 1
    $TTS tools/narrate.py <film> --phonemes   # print how the voice will pronounce every sentence (nothing written)
    $TTS tools/narrate.py <film> --voice bm_george [--speed 1.1]
                                              # a LISTENING copy in another voice: out/test/narrate_<film>_<voice>.wav
                                              #   (+ .json); narration/ always follows the film's own NARRATION
    $TTS tools/narrate.py --voices [names]    # pace of each voice: words per second, words that fit in 60 s
    $TTS tools/narrate.py --selftest          # timing accuracy on 44 film-like sentences (resumable: run it again
                                              #   until it prints the report; stops starting work after 230 s)
    $TTS tools/narrate.py --paragraph-check   # sentence-by-sentence synthesis against whole-paragraph synthesis
    $TTS tools/narrate.py [<film>] --hear FILE     # recognise the words in any audio / video file; with a film,
                                                   #   locate its script words (independent of narration/*.json);
                                                   #   writes out/test/narrate_heard_<name>.json
    $TTS tools/narrate.py --make-timed-model  # once per machine: write kokoro-v1.0.timed.onnx (needs `pip install onnx`)
  options: --threads N (default 2), --recogniser-only (time the words without the model's durations).

The spec is the `NARRATION = {...}` literal of the film module (format: engine/narration.py); it is read with ast,
the film is never imported. Model files are looked for in $MC_TTS_MODELS (default: the session scratchpad, see
MODELS below); tools/setup_tts.sh creates the environment and downloads them.

What it does, in this order
  1. Every sentence is synthesised ON ITS OWN (Kokoro 82M through kokoro-onnx; deterministic: the same sentence,
     voice and speed give the same samples, so changing a pause changes no word). Its leading and trailing
     silence is cut by energy to a fixed margin (20 ms before the first sound, 50 ms after the last) with short
     fades, and the sentences are levelled to one speech level.
  2. Loudness: one gain for the whole film to -16 LUFS integrated (ITU-R BS.1770 as measured by ffmpeg's ebur128),
     then a look-ahead limiter keeps the true peak under -1.5 dBTP. Gain and limiter work per sentence, so they do
     not depend on the pauses either.
  3. The sentences are laid out: `lead` seconds of silence, then each sentence, its first sound exactly `pause`
     seconds after the last sound of the one before, then `tail`; the file is padded to a whole number of frames.
  4. Word timing, per sentence. Three sources, each checking the others:
       model       the voice model's OWN phoneme durations. kokoro-v1.0.timed.onnx is the same network with its
                   duration predictor exposed as a second output (--make-timed-model; the audio is bit-identical),
                   so every phoneme has its span and nothing has to be recognised. A word starts 25 ms before
                   the gap before its first phoneme (measured: that is where its sound begins; MODEL_LEAD).
       energy      measured on the samples: the first and the last sound of the sentence, and every silence of
                   140 ms or more inside it. The word after a pause starts where the sound comes back.
       recogniser  the second opinion (faster-whisper small.en): the SCRIPT's words force-aligned to the audio by
                   the recogniser's cross-attention; where that gives a word no time, its free transcript aligned
                   to the script by letters (it mishears: 'Crammys' -> 'cram is'). It is the fallback when the
                   timed model is missing (--recogniser-only), and every word's recogniser start is stored beside
                   the final one ("second"). Measured (--selftest): inside running speech the recogniser hears a
                   word start early, while the word before is still sounding; the model does not.
     A word no source can place is spread between its neighbours by syllables and listed as ESTIMATED.
  5. narration/<film>.json: sentences (text, start, end), words (script text, caption, start, end, sentence,
     source), voice, speed, sample rate, duration, loudness, and the hash of the spec (engine.narration.spec_hash).

MEASURED (--selftest, am_michael, 44 sentences of the six films' kind, 384 words; out/test/narrate_selftest_*_report.json)
  * no word had to be estimated; the voice paused 21 times inside a sentence, every time at punctuation, and every
    time the word after the pause was put on the measured return of the sound
  * the model's phoneme timing against the measured sound after those pauses: median 10 ms, 19 of 21 within 35 ms
    (the other two 50 and 120 ms: the measured sound is what is used there)
  * the recogniser against the final timing: after pauses the same word on the same onset 21 of 21; inside speech
    median 40 ms apart, 52 % within one frame, 74 % within two, and EARLY on average (-45 ms)
  * the recogniser against ground truth (sentences assembled from pieces whose starts are known to the sample):
    115 ms median error where the pieces butt (8 % within a frame), and 9 of 35 pauses of 250 ms given to the wrong
    word. That is why the recogniser is only the second opinion.
  * cutting the audio at a word's start where the two timings differ by over 100 ms (16 of 64 such words): at the
    final timing the audio before the cut ends with the whole word before in 16 of 16 and both sides are intact in
    12 of 16; at the recogniser's start in 8 and 3 of 16 ('every... | One is afraid': it starts 'is' inside 'everyone')
  * the free transcript missed or misspelt 14 of 384 words (Crammys, redstoner, Herobrine, trapdoors, grown-ups heard
    as two words; gym, ender, twelve not heard): nothing of it is used for the timing of a film
PACE (--voices, speed 1.0; words per second while speaking / with the default 0.35 s pauses / words that fit in 60 s
  with lead 0.3 and tail 1.0, on 12 short sentences of 95 mostly one-syllable words):
    am_michael 3.71 / 3.23 / 189    am_fenrir 4.33 / 3.69 / 216    am_puck  4.36 / 3.70 / 217
    bm_george  3.12 / 2.77 / 162    bm_fable  2.96 / 2.64 / 155    af_heart 4.11 / 3.52 / 206
  On the 44 test sentences (8.7 words and 12 syllables a sentence) am_michael speaks 3.20 words/s = 4.4 syllables/s,
  2.84 words/s with pauses: 166 words in 60 s. Plan a one-minute film at 160-190 words and let the narration say.
  The voice's own pause between two sentences of a paragraph is 0.28-0.54 s (--paragraph-check); the default is 0.35.
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import numpy as np                                                  # noqa: E402

from engine import narration as N                                   # noqa: E402  (pure Python: no bpy)

MODELS = os.environ.get(
    "MC_TTS_MODELS", "/tmp/claude-0/-home-user-Project-2-/be90bb9d-3fc7-572c-941a-ff79c8b6ef48/scratchpad/tts_models")
KOKORO_ONNX, KOKORO_TIMED, KOKORO_VOICES, WHISPER = "kokoro-v1.0.onnx", "kokoro-v1.0.timed.onnx", "voices-v1.0.bin", "small.en"
OUT_TEST = os.path.join(ROOT, "out", "test")

SR = 24000                    # Kokoro's sample rate, kept for the delivery wav (the encoder resamples to 48 kHz)
PRE, POST = 0.020, 0.050      # margin kept before the first / after the last sound of a sentence (seconds)
FADE_IN, FADE_OUT = 0.008, 0.030
SILENCE_DB = -40.0            # a 10 ms frame is sound when its RMS is within this of the clip's loudest frame
MIN_RUN, MIN_GAP = 0.025, 0.030   # shorter sounds are blips, shorter gaps belong to the sound around them
PAUSE_MIN = 0.140             # a silence this long inside a sentence is a pause (a stop consonant closes for less)
MODEL_LEAD = 0.025            # model timing inside speech: a word starts this much before the gap before its first
                              #   phoneme. Measured: after pauses the sound is back 10 ms (median; mean 18 ms) before
                              #   that gap starts, and audio cut exactly at it still carried the f of 'farm' and the m
                              #   of 'me' on the side of the word before; 25 ms earlier both cuts are clean.
MODEL_REACH = 0.20            # model timing: a word boundary this close to a pause is moved onto it (the model is
                              #   within 35 ms of the measured sound for 19 of 21 pauses, 50 and 120 ms for two)
SNAP_REACH = 0.25             # recogniser timing: the same, wider (its boundaries drift into the silence) ...
PUNCT_REACH = 0.45            # ... and wider still for a boundary the script punctuates: the voice pauses at
                              #   punctuation (21 of 21 pauses inside the test sentences)
TARGET_LUFS, MAX_TRUE_PEAK = -16.0, -1.5
LEVEL_RANGE = 4.0             # dB a sentence may be moved to meet the common speech level
LIMIT_WINDOW = 0.012          # the limiter looks this far ahead and behind (its gain moves over about 24 ms)
MAX_SENTENCE = 27.0           # seconds: one recogniser window
JSON_VERSION = 2
MARKS = set(";:,.!?¡¿—…\"«»“”()")       # punctuation in the voice's phoneme alphabet (they carry time, no word)
STRESS = set("ˈˌ")                       # stress marks differ between a word alone and the word in its sentence
FRAME = 1.0 / 24.0


# ---------------------------------------------------------------------------------------------------------------
# engines (loaded on first use)
# ---------------------------------------------------------------------------------------------------------------

class Engines:
    """The voice (Kokoro) and the recogniser (faster-whisper), each loaded when first needed."""

    def __init__(self, threads=2, timed=True):
        self.threads, self.want_timed = int(threads), bool(timed)
        self._kokoro = self._whisper = self._tok = None
        self._word_phonemes = {}
        self.model_file = None

    @property
    def kokoro(self):
        if self._kokoro is None:
            import onnxruntime as ort
            from kokoro_onnx import Kokoro

            timed = os.path.join(MODELS, KOKORO_TIMED)
            onnx = timed if (self.want_timed and os.path.exists(timed)) else os.path.join(MODELS, KOKORO_ONNX)
            voices = os.path.join(MODELS, KOKORO_VOICES)
            for p in (onnx, voices):
                if not os.path.exists(p):
                    raise SystemExit("voice model file %s is missing: run tools/setup_tts.sh (or set MC_TTS_MODELS)" % p)
            so = ort.SessionOptions()
            so.intra_op_num_threads, so.inter_op_num_threads = self.threads, 1
            self._kokoro = Kokoro.from_session(ort.InferenceSession(onnx, so, providers=["CPUExecutionProvider"]), voices)
            self.model_file = os.path.basename(onnx)
        return self._kokoro

    @property
    def timed(self):
        """True when the loaded voice model reports its phoneme durations."""
        return bool(self.kokoro.has_timings)

    @property
    def whisper(self):
        if self._whisper is None:
            from faster_whisper import WhisperModel
            from faster_whisper.tokenizer import Tokenizer

            try:
                self._whisper = WhisperModel(WHISPER, device="cpu", compute_type="int8", download_root=MODELS,
                                             cpu_threads=self.threads, local_files_only=True)
            except Exception as e:                                  # noqa: BLE001
                raise SystemExit("recogniser model '%s' not found under %s (%s): run tools/setup_tts.sh" % (WHISPER, MODELS, e))
            self._tok = Tokenizer(self._whisper.hf_tokenizer, self._whisper.model.is_multilingual,
                                  task="transcribe", language="en")
        return self._whisper

    def versions(self):
        import importlib.metadata as md

        out = {"model": self.model_file or KOKORO_ONNX, "voices": KOKORO_VOICES, "recogniser": "faster-whisper " + WHISPER}
        for pkg in ("kokoro-onnx", "faster-whisper", "onnxruntime", "ctranslate2"):
            try:
                out[pkg] = md.version(pkg)
            except md.PackageNotFoundError:
                out[pkg] = "?"
        return out

    # ---- voice
    def lang(self, voice):
        """Kokoro language of a voice name: a* American, b* British."""
        if voice[:1] not in "ab":
            raise SystemExit("voice %r is not an English voice (American a*, British b*)" % voice)
        return "en-gb" if voice.startswith("b") else "en-us"

    def speak(self, text, voice, speed=1.0):
        """Raw synthesis of one text: (float32 samples at 24 kHz with the model's own silence around them,
        [(phoneme, start, end), ...] in seconds or None when the model does not report durations)."""
        k = self.kokoro
        if voice not in k.get_voices():
            raise SystemExit("unknown voice %r; English voices: %s"
                             % (voice, " ".join(v for v in k.get_voices() if v[:1] in "ab")))
        lang = self.lang(voice)
        if not k.has_timings:
            audio, sr = k.create(text, voice=voice, speed=float(speed), lang=lang, trim=False)
            assert sr == SR
            return np.asarray(audio, dtype=np.float32), None
        if len(k.tokenizer.phonemize(text, lang)) > 500:
            raise SystemExit("a sentence of more than 500 phonemes cannot be timed in one pass: split it (%r)" % text[:60])
        audio, sr, spoken = k.create_timed(text, voice=voice, speed=float(speed), lang=lang, trim=False,
                                           sentence_pause=0.0, clause_pause=0.0)      # no silence of its own added
        assert sr == SR
        return np.asarray(audio, dtype=np.float32), [(t.phoneme, float(t.start), float(t.end)) for t in spoken]

    def phonemes(self, text, voice):
        """The phonemes the voice will say for a text (to check a pronunciation without listening)."""
        return self.kokoro.tokenizer.phonemize(text, self.lang(voice))

    def word_phonemes(self, word, voice):
        """Phonemes of one word on its own (cached): what a sentence's phonemes are matched against."""
        key = (word, self.lang(voice))
        if key not in self._word_phonemes:
            self._word_phonemes[key] = self.kokoro.tokenizer.phonemize(word, key[1])
        return self._word_phonemes[key]

    # ---- recogniser
    def _encode(self, a16):
        wm = self.whisper
        feats = wm.feature_extractor(a16)
        frames = int(feats.shape[-1])
        if frames > 3000:
            raise ValueError("more than 30 s in one recogniser window")
        feats = np.pad(feats, [(0, 0), (0, 3000 - frames)])
        return wm.encode(feats), frames

    def forced(self, a16, words):
        """Forced alignment of the SCRIPT's words to 16 kHz audio (at most 30 s): [(start, end, probability)],
        seconds from the start of the audio, 20 ms steps. The words are given, so nothing is recognised."""
        wm = self.whisper
        enc, frames = self._encode(a16)
        tokens, bounds = [], [0]
        for w in words:
            tokens += self._tok.encode(" " + w)
            bounds.append(len(tokens))
        res = wm.model.align(enc, self._tok.sot_sequence, [tokens], frames, median_filter_width=7)[0]
        text_i = np.array([p[0] for p in res.alignments])
        time_i = np.array([p[1] for p in res.alignments])
        jumps = np.pad(np.diff(text_i), (1, 0), constant_values=1).astype(bool)
        jt = time_i[jumps] / float(wm.tokens_per_second)
        end_of_audio = len(a16) / 16000.0
        out = []
        for i in range(len(words)):
            a, b = bounds[i], bounds[i + 1]
            start = float(jt[a]) if a < len(jt) else end_of_audio
            end = float(jt[b]) if b < len(jt) else end_of_audio
            out.append((start, end, float(np.mean(res.text_token_probs[a:b])) if b > a else 0.0))
        return out

    def recognise(self, a16):
        """Free recognition of 16 kHz audio of any length: [(word, start, end, probability)]."""
        segs, _info = self.whisper.transcribe(a16, word_timestamps=True, beam_size=5, vad_filter=False,
                                              condition_on_previous_text=False, language="en")
        return [(w.word.strip(), float(w.start), float(w.end), float(w.probability)) for s in segs for w in s.words]


# ---------------------------------------------------------------------------------------------------------------
# samples
# ---------------------------------------------------------------------------------------------------------------

def db(x):
    """Amplitude ratio -> dB."""
    return 20.0 * math.log10(max(float(x), 1e-12))


def resample(x, sr_in, sr_out):
    """Mono float32 resampled with ffmpeg."""
    if sr_in == sr_out:
        return np.asarray(x, dtype=np.float32)
    p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(sr_in), "-ac", "1", "-i", "-",
                        "-ar", str(sr_out), "-ac", "1", "-f", "f32le", "-"],
                       input=np.asarray(x, dtype="<f4").tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype="<f4").copy()


def read_audio(path, sr=SR):
    """Any audio or video file -> mono float32 at `sr` (decoded by ffmpeg, first audio stream)."""
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0", "-ar", str(sr), "-ac", "1",
                        "-f", "f32le", "-"], capture_output=True)
    if p.returncode != 0 or not p.stdout:
        raise SystemExit("cannot read audio from %s: %s" % (path, p.stderr.decode(errors="replace").strip()[:200]))
    return np.frombuffer(p.stdout, dtype="<f4").copy()


def frame_rms(x, sr=SR, hop=0.005, win=0.010):
    """RMS of `win`-second frames every `hop` seconds: (rms array, hop in seconds)."""
    h, w = int(round(hop * sr)), int(round(win * sr))
    x = np.asarray(x, dtype=np.float64)
    if len(x) < w:
        return np.zeros(0), hop
    c = np.concatenate([[0.0], np.cumsum(x * x)])
    starts = np.arange(0, len(x) - w + 1, h)
    return np.sqrt((c[starts + w] - c[starts]) / w), hop


def sound_runs(x, sr=SR, rel_db=SILENCE_DB, floor_db=-62.0):
    """Where there is sound: [(t0, t1), ...] in seconds. A frame is sound when its RMS is within `rel_db` of the
    loudest frame (and above `floor_db` dBFS); gaps under MIN_GAP are closed, sounds under MIN_RUN dropped."""
    rms, hop = frame_rms(x, sr)
    if len(rms) == 0 or rms.max() <= 0:
        return []
    thr = max(rms.max() * 10 ** (rel_db / 20.0), 10 ** (floor_db / 20.0))
    act = rms > thr
    runs, i, n = [], 0, len(act)
    while i < n:
        if act[i]:
            j = i
            while j < n and act[j]:
                j += 1
            runs.append([i * hop, j * hop + 0.005])            # a frame covers 10 ms from its start
            i = j
        else:
            i += 1
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] < MIN_GAP:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    return [(a, b) for a, b in merged if b - a >= MIN_RUN]


def trim_clip(raw, sr=SR):
    """Cut a synthesised sentence to its sound: PRE seconds before the first sound, POST after the last, faded in
    and out. Returns (clip, onset, offset, shift): the sound runs from `onset` to `offset` seconds inside the clip,
    and a time t of the raw audio is t - shift in the clip."""
    runs = sound_runs(raw, sr)
    if not runs:
        raise ValueError("the voice produced silence")
    t0, t1 = runs[0][0], runs[-1][1]
    a, b = max(0, int(round((t0 - PRE) * sr))), min(len(raw), int(round((t1 + POST) * sr)))
    clip = np.array(raw[a:b], dtype=np.float64)
    n_in, n_out = min(len(clip) // 2, int(FADE_IN * sr)), min(len(clip) // 2, int(FADE_OUT * sr))
    clip[:n_in] *= 0.5 - 0.5 * np.cos(np.pi * np.arange(n_in) / n_in)
    clip[len(clip) - n_out:] *= 0.5 + 0.5 * np.cos(np.pi * (np.arange(n_out) + 1) / n_out)
    return clip, t0 - a / sr, t1 - a / sr, a / sr


def speech_level(x, sr=SR):
    """Level of the speech itself in dBFS: RMS over the 20 ms frames within 25 dB of the loudest one."""
    rms, _hop = frame_rms(x, sr, hop=0.010, win=0.020)
    if len(rms) == 0 or rms.max() <= 0:
        return -120.0
    act = rms[rms > rms.max() * 10 ** (-25.0 / 20.0)]
    return db(math.sqrt(float(np.mean(act * act))))


def loudness(x, sr=SR):
    """(integrated loudness in LUFS, true peak in dBTP) of mono samples, measured by ffmpeg's ebur128 filter."""
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-",
                        "-af", "ebur128=peak=true", "-f", "null", "-"],
                       input=np.asarray(x, dtype="<f4").tobytes(), capture_output=True)
    text = p.stderr.decode(errors="replace")
    tail = text[text.rfind("Summary:"):]
    i = re.search(r"I:\s*(-?[\d.]+|-inf)\s*LUFS", tail)
    tp = re.search(r"Peak:\s*(-?[\d.]+|-inf)\s*dBFS", tail)
    if not i or not tp:
        raise RuntimeError("could not read ffmpeg's ebur128 summary:\n" + text[-400:])
    return float(i.group(1)), float(tp.group(1))


def limit(x, ceiling, sr=SR, window=LIMIT_WINDOW):
    """Look-ahead peak limiter: no sample of the result exceeds `ceiling` (linear). The gain is the smallest gain
    needed within +-window, smoothed with a Hann window of the same reach, so it moves over about two pitch
    periods and never faster. Returns (limited samples, gain curve)."""
    x = np.asarray(x, dtype=np.float64)
    need = np.minimum(1.0, ceiling / np.maximum(np.abs(x), 1e-9))
    if need.min() >= 1.0:
        return x.copy(), np.ones(len(x))
    w = max(1, int(round(window * sr)))
    padded = np.pad(need, (w, w), constant_values=1.0)
    low = np.lib.stride_tricks.sliding_window_view(padded, 2 * w + 1).min(axis=1)
    kernel = np.hanning(2 * w + 3)[1:-1]
    kernel /= kernel.sum()
    gain = np.convolve(np.pad(low, (w, w), constant_values=1.0), kernel, mode="valid")
    gain = np.minimum(gain, need)                                   # (already true; guards rounding)
    return x * gain, gain


def write_wav(path, x, sr=SR):
    """Mono 16-bit PCM wav (written under a temporary name first)."""
    import soundfile as sf

    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".part"
    sf.write(tmp, np.clip(np.asarray(x, dtype=np.float64), -1.0, 1.0), sr, subtype="PCM_16", format="WAV")
    os.replace(tmp, path)


def pitch(x, sr=SR, lo=60.0, hi=350.0):
    """Median fundamental frequency (Hz) of the voiced 40 ms frames of a clip, by autocorrelation; 0 if none."""
    n, hop = int(0.040 * sr), int(0.010 * sr)
    x = np.asarray(x, dtype=np.float64)
    rms, _ = frame_rms(x, sr, hop=0.010, win=0.040)
    if len(rms) == 0:
        return 0.0
    thr = rms.max() * 10 ** (-20.0 / 20.0)
    lag0, lag1 = int(sr / hi), int(sr / lo)
    win = np.hanning(n)
    f0 = []
    for k in np.flatnonzero(rms > thr):
        seg = x[k * hop:k * hop + n]
        if len(seg) < n:
            continue
        seg = (seg - seg.mean()) * win
        spec = np.fft.rfft(seg, 2 * n)
        ac = np.fft.irfft(spec * np.conj(spec))[:n]
        if ac[0] <= 0:
            continue
        ac = ac / ac[0]
        lag = lag0 + int(np.argmax(ac[lag0:lag1]))
        if ac[lag] > 0.45:
            f0.append(sr / lag)
    return float(np.median(f0)) if f0 else 0.0


# ---------------------------------------------------------------------------------------------------------------
# word timing
# ---------------------------------------------------------------------------------------------------------------

def global_align(a, b):
    """Global alignment of two symbol sequences (match +2, mismatch -1, gap -1): [(i, j, same), ...] for every
    position of `a` that is paired with a position of `b`, in order."""
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return []
    score = np.zeros((n + 1, m + 1), dtype=np.int32)
    score[:, 0] = -np.arange(n + 1)
    score[0, :] = -np.arange(m + 1)
    b_arr = np.array(list(b))
    for i in range(1, n + 1):
        sub = np.where(b_arr == a[i - 1], 2, -1)
        row, prev = score[i], score[i - 1]
        best = np.maximum(prev[:-1] + sub, prev[1:] - 1)             # paired, or a symbol of `a` left alone
        for j in range(1, m + 1):                                    # ... or a symbol of `b` left alone
            v = row[j - 1] - 1
            row[j] = best[j - 1] if best[j - 1] >= v else v
    pairs = []
    i, j = n, m
    while i > 0 and j > 0:
        s = score[i, j]
        same = a[i - 1] == b[j - 1]
        if s == score[i - 1, j - 1] + (2 if same else -1):
            pairs.append((i - 1, j - 1, same))
            i, j = i - 1, j - 1
        elif s == score[i - 1, j] - 1:
            i -= 1
        else:
            j -= 1
    return pairs[::-1]


def words_from_timings(timings, spoken, phonemes_of):
    """Word times from the voice model's own phoneme timings. `timings` = [(phoneme, start, end), ...] of one
    synthesised text, `spoken` = its words as they were given to the voice, phonemes_of(word) = that word's
    phonemes on its own. Returns one (start, end) per word, or None for a word no phoneme could be given to.
    A word STARTS where the gap before its first phoneme starts (the model renders a word's onset inside the
    space before it: measured against the sound after pauses), and ends with its last phoneme."""
    n = len(spoken)
    groups, cur = [], []                         # the phoneme words, as the phonemiser spaced them
    for k, (ph, _a, _b) in enumerate(timings):
        if ph == " ":
            if cur:
                groups.append(cur)
                cur = []
        elif ph not in MARKS:
            cur.append(k)
    if cur:
        groups.append(cur)
    owner = {}
    if len(groups) == n:
        for i, g in enumerate(groups):
            for k in g:
                owner[k] = i
    else:
        # the phonemiser joined words ('on the' -> one phoneme word) or split one: match letters instead
        a_sym, a_own = [], []
        for i, w in enumerate(spoken):
            for ch in phonemes_of(w):
                if ch != " " and ch not in MARKS and ch not in STRESS:
                    a_sym.append(ch)
                    a_own.append(i)
        b_idx = [k for g in groups for k in g if timings[k][0] not in STRESS]
        for ai, bj, _same in global_align(a_sym, [timings[k][0] for k in b_idx]):
            owner[b_idx[bj]] = a_own[ai]
        matched, last = set(owner.values()), 0
        for g in groups:
            # a phoneme no letter was matched to (a stress mark, a sound the word has only in this sentence)
            # goes with the phoneme AFTER it in its phoneme word, the last ones with the phoneme before; a
            # phoneme word with no match at all is the next script word if that one has no phoneme yet
            nxt = None
            for k in reversed(g):
                if k in owner:
                    nxt = owner[k]
                elif nxt is not None:
                    owner[k] = nxt
            if nxt is None:
                nxt = last + 1 if (last + 1 < n and last + 1 not in matched) else last
                matched.add(nxt)
            for k in g:
                if k in owner:
                    nxt = owner[k]
                owner[k] = max(owner.get(k, nxt), last)          # ... and never back to an earlier word
                last = owner[k]
    first, final = {}, {}
    for k in sorted(owner):
        first.setdefault(owner[k], k)
        final[owner[k]] = k
    out = []
    for i in range(n):
        if i not in first:
            out.append(None)
            continue
        k = first[i] - 1
        while k >= 0 and timings[k][0] in MARKS:
            k -= 1
        start = timings[k][1] if (k >= 0 and timings[k][0] == " ") else timings[first[i]][1]
        out.append((start, timings[final[i]][2]))
    return out


def align_text(script, heard):
    """Map recognised words onto script words by their letters (global alignment of the two letter strings).
    Returns for each script word the list of indices of the recognised words it shares letters with: [] = not
    heard, one = heard (maybe misspelt), several = heard as several words; two script words that point at the
    same recognised word were heard as one."""
    a_txt, a_own, b_txt, b_own = [], [], [], []
    for i, w in enumerate(script):
        for ch in N.letters(w):
            a_txt.append(ch)
            a_own.append(i)
    for j, w in enumerate(heard):
        for ch in N.letters(w):
            b_txt.append(ch)
            b_own.append(j)
    links = [[] for _ in script]
    count = {}
    for i, j, same in global_align(a_txt, b_txt):
        if same:
            key = (a_own[i], b_own[j])
            count[key] = count.get(key, 0) + 1
    for (wi, hj), c in sorted(count.items()):
        la, lb = len(N.letters(script[wi])), len(N.letters(heard[hj]))
        if c >= max(1, math.ceil(0.5 * min(la, lb))):                # half of the shorter word: one stray letter is no link
            links[wi].append(hj)
    return links


def _share(script, ks, t0, t1):
    """Spread the span t0..t1 over the script words `ks` by syllables: [[start, end], ...]."""
    weights = [N.syllables(script[k]) + 0.15 * len(N.letters(script[k])) for k in ks]
    total, t, out = sum(weights), t0, []
    for wgt in weights:
        d = (t1 - t0) * wgt / total
        out.append([t, t + d])
        t += d
    return out


def from_recognition(script, heard, lo, hi):
    """Times for the script words from a free transcript `heard` = [(word, start, end, p)], inside [lo, hi].
    Returns [(start, end, kind)] with kind 'exact' | 'fuzzy' | 'split' (heard as several words) | 'merged' (several
    script words heard as one: the span is shared by syllables) | 'gap' (not heard: spread between its neighbours).
    'merged' and 'gap' are estimates."""
    links = align_text(script, [h[0] for h in heard])
    n = len(script)
    out = [None] * n
    owner = {}
    for i, ls in enumerate(links):
        for j in ls:
            owner.setdefault(j, []).append(i)
    done = set()
    for i, ls in enumerate(links):
        if not ls or i in done:
            continue
        group_w, group_h, frontier = {i}, set(ls), list(ls)
        while frontier:                                              # words that share recognised words, transitively
            j = frontier.pop()
            for k in owner[j]:
                if k not in group_w:
                    group_w.add(k)
                    for j2 in links[k]:
                        if j2 not in group_h:
                            group_h.add(j2)
                            frontier.append(j2)
        ws, hs = sorted(group_w), sorted(group_h)
        t0, t1 = heard[hs[0]][1], max(heard[j][2] for j in hs)
        if len(ws) == 1:
            kind = "split" if len(hs) > 1 else ("exact" if N.letters(script[ws[0]]) == N.letters(heard[hs[0]][0]) else "fuzzy")
            out[ws[0]] = [t0, t1, kind]
        else:
            for k, (a, b) in zip(ws, _share(script, ws, t0, t1)):
                out[k] = [a, b, "merged"]
        done |= group_w
    i = 0
    while i < n:                                                     # the words nobody heard
        if out[i] is not None:
            i += 1
            continue
        j = i
        while j < n and out[j] is None:
            j += 1
        t0 = out[i - 1][1] if i > 0 else lo
        t1 = max(out[j][0] if j < n else hi, t0)
        for k, (a, b) in zip(range(i, j), _share(script, list(range(i, j)), t0, t1)):
            out[k] = [a, b, "gap"]
        i = j
    return [tuple(o) for o in out]


def snap_to_sound(times, runs, reach=SNAP_REACH, punctuated=(), punct_reach=PUNCT_REACH, pause_min=PAUSE_MIN):
    """Fit word times to the measured sound of the same audio. `times` = [[start, end], ...] (seconds, in order),
    `runs` = sound_runs() of it. The first word starts with the first sound and the last ends with the last; every
    silence of `pause_min` or more is given to a word boundary: the nearest one the script punctuates (indices of
    the words BEFORE such a boundary in `punctuated`) within `punct_reach`, else the nearest one within `reach`.
    The word before the pause ends where the silence starts, the word after starts where the sound comes back.
    Elsewhere a word ends where the next one starts. Returns (new times, indices of the words that START on a
    measured onset, [(pause start, pause end, index of the word before it or None), ...])."""
    t = [[float(a), float(b)] for a, b in times]
    n = len(t)
    if n == 0 or not runs:
        return t, [], []
    on_sound = [0]
    t[0][0] = runs[0][0]
    t[-1][1] = runs[-1][1]
    pauses = [(a[1], b[0]) for a, b in zip(runs, runs[1:]) if b[0] - a[1] >= pause_min]
    taken, report = {}, []
    punctuated = set(punctuated)
    for g0, g1 in pauses:
        dist = []
        for i in range(n - 1):
            b = t[i + 1][0]
            dist.append(0.0 if g0 <= b <= g1 else min(abs(b - g0), abs(b - g1)))
        marked = [i for i in range(n - 1) if i in punctuated and dist[i] <= punct_reach]
        near = [i for i in range(n - 1) if dist[i] <= reach]
        pool = marked or near
        best = min(pool, key=lambda i: dist[i]) if pool else None
        report.append((g0, g1, best))
        if best is None:
            continue
        if best not in taken or (g1 - g0) > (taken[best][1] - taken[best][0]):
            taken[best] = (g0, g1)
    for i, (g0, g1) in taken.items():
        t[i][1] = g0
        t[i + 1][0] = g1
        on_sound.append(i + 1)
    for i in range(n - 1):                                           # contiguous inside a run of sound
        if i not in taken:
            t[i][1] = t[i + 1][0]
    return t, sorted(on_sound), report


def repair(times, words, lo, hi, min_len=0.03):
    """Make word times usable whatever a source returned: inside [lo, hi], in order, each at least `min_len`
    long. Words that end up without room (zero length, out of order) are spread, together with their neighbours,
    by syllables. Returns (times, set of indices that were re-spread = ESTIMATED)."""
    t = [[min(max(a, lo), hi), min(max(b, lo), hi)] for a, b in times]
    n = len(t)
    bad = set()
    for i in range(n):
        if t[i][1] - t[i][0] < min_len or (i and t[i][0] < t[i - 1][1] - 1e-6):
            bad.add(i)
    if not bad:
        return t, set()
    spread = set()
    i = 0
    while i < n:
        if i not in bad:
            i += 1
            continue
        j = i
        while j + 1 < n and (j + 1) in bad:
            j += 1
        a, b = max(0, i - 1), min(n - 1, j + 1)                      # the neighbours share their room
        t0, t1 = t[a][0], t[b][1]
        if t1 - t0 < min_len * (b - a + 1):                          # still no room: the whole sentence
            a, b, t0, t1 = 0, n - 1, lo, hi
        ks = list(range(a, b + 1))
        for k, span in zip(ks, _share(words, ks, t0, t1)):
            t[k] = span
            spread.add(k)
        i = b + 1
    return t, spread


def punctuated_words(words):
    """Indices of the script words that end in punctuation (a pause in the voice belongs after one of them)."""
    return [i for i, w in enumerate(words) if re.search(r"[,;:.!?…—–-]+[\"')\]]*$", w.strip())]


def time_by_recogniser(eng, clip, words, onset, offset, sr=SR, free=False):
    """Word times of one sentence clip from the recogniser alone (seconds inside the clip): the script's words
    force-aligned, a word the alignment gives no time taken from the free transcript, the result fitted to the
    measured sound. free=True always makes the free transcript too. Returns a list of dicts {start, end, source,
    estimated, raw_forced, p, recognised: {start, end, kind} or None}."""
    pad = 0.20
    a16 = resample(np.concatenate([np.zeros(int(pad * sr)), clip, np.zeros(int(pad * sr))]), sr, 16000)
    if len(a16) / 16000.0 > 29.5:
        raise SystemExit("a sentence of %.1f s is too long for one recogniser window: split it" % (len(clip) / sr))
    runs = sound_runs(clip, sr)
    n = len(words)
    forced = [(s - pad, e - pad, p) for s, e, p in eng.forced(a16, words)]
    source = ["forced"] * n
    times = [[s, e] for s, e, _p in forced]
    heard_times = None
    weak = [i for i in range(n) if times[i][1] - times[i][0] < 0.02]
    if free or weak:
        heard = [(w, s - pad, e - pad, p) for w, s, e, p in eng.recognise(a16)]
        heard_times = from_recognition(words, heard, onset, offset)
        for i in weak:                                               # the forced alignment gave this word no time
            if heard_times[i][2] in ("exact", "fuzzy", "split"):
                times[i] = [heard_times[i][0], heard_times[i][1]]
                source[i] = "recognised"
    snapped, on_sound, _pauses = snap_to_sound(times, runs, punctuated=punctuated_words(words))
    fixed, spread = repair(snapped, words, onset, offset)
    out = []
    for i in range(n):
        est = i in spread
        rec = None
        if heard_times is not None:
            rec = {"start": round(heard_times[i][0], 4), "end": round(heard_times[i][1], 4), "kind": heard_times[i][2]}
        out.append({"start": fixed[i][0], "end": fixed[i][1], "estimated": est,
                    "source": "estimated" if est else ("energy" if i in on_sound else source[i]),
                    "raw_forced": round(forced[i][0], 4), "p": round(forced[i][2], 3), "recognised": rec})
    return out


def time_sentence(eng, clip, words, onset, offset, model=None, second_opinion=True, sr=SR):
    """Start and end of every script word of one sentence clip (seconds inside the clip).
    `model` = words_from_timings() of the clip (already in clip time) or None. With it the model's durations are
    the timing, fitted to the measured sound, and the recogniser is the second opinion; without it the recogniser
    is the timing. Returns dicts {start, end, source ('model' | 'energy' = starts on a measured onset | 'forced' |
    'recognised' | 'estimated'), estimated, model_raw, second, second_source, pauses}."""
    second = time_by_recogniser(eng, clip, words, onset, offset, sr) if (second_opinion or model is None) else None
    if model is None:
        for w in second:
            w.update(model_raw=None, second=None, second_source=None)
        return second
    n = len(words)
    runs = sound_runs(clip, sr)
    times, missing, prev = [], set(), onset
    for i, m in enumerate(model):
        if m is None:                                                # no phoneme for this word: repaired below
            times.append([prev, prev])
            missing.add(i)
        else:
            times.append([m[0] - (MODEL_LEAD if i else 0.0), m[1]])
            prev = m[1]
    snapped, on_sound, pauses = snap_to_sound(times, runs, reach=MODEL_REACH, punctuated=punctuated_words(words))
    fixed, spread = repair(snapped, words, onset, offset)
    out = []
    for i in range(n):
        est = i in spread or i in missing
        out.append({"start": fixed[i][0], "end": fixed[i][1], "estimated": est,
                    "source": "estimated" if est else ("energy" if i in on_sound else "model"),
                    "model_raw": None if model[i] is None else round(model[i][0], 4),
                    "second": None if second is None else second[i]["start"],
                    "second_source": None if second is None else second[i]["source"],
                    "raw_forced": None if second is None else second[i]["raw_forced"]})
    if out:
        out[0]["pauses"] = [(round(g0, 4), round(g1, 4), b) for g0, g1, b in pauses]
    return out


# ---------------------------------------------------------------------------------------------------------------
# a film's narration
# ---------------------------------------------------------------------------------------------------------------

def speak_sentence(eng, text, spoken, voice, speed):
    """One sentence, spoken and cut to its sound: {'clip', 'onset', 'offset', 'model' (word times from the voice
    model in clip time, or None), 'raw_level'}."""
    raw, timings = eng.speak(spoken, voice, speed)
    clip, onset, offset, shift = trim_clip(raw)
    model = None
    if timings is not None:
        words = words_from_timings(timings, N.words_of(spoken), lambda w: eng.word_phonemes(w, voice))
        if len(words) == len(N.words_of(text)):
            model = [None if w is None else (w[0] - shift, w[1] - shift) for w in words]
    return {"clip": clip, "onset": onset, "offset": offset, "model": model, "raw_level": speech_level(clip)}


def synthesise(eng, norm, log=print):
    """Speak every sentence of a normalised spec: a list of speak_sentence() dicts, levelled and limited to the
    delivery loudness (independently of the pauses), and the loudness report."""
    clips = []
    for i, line in enumerate(norm["lines"]):
        t = time.time()
        c = speak_sentence(eng, line["text"], line["spoken"], norm["voice"], norm["speed"] * line["speed"])
        if c["offset"] - c["onset"] > MAX_SENTENCE:
            raise SystemExit("sentence %d is %.1f s long (limit %.0f s): split it into two lines"
                             % (i, c["offset"] - c["onset"], MAX_SENTENCE))
        clips.append(c)
        log("  spoke %2d  %5.2f s in %4.1f s  level %6.1f dB  %s" % (i, c["offset"] - c["onset"], time.time() - t,
                                                                    c["raw_level"], line["spoken"]))
    # 1. one speech level for every sentence
    target = float(np.median([c["raw_level"] for c in clips]))
    for c in clips:
        c["level_gain"] = max(-LEVEL_RANGE, min(LEVEL_RANGE, target - c["raw_level"]))
        c["clip"] = c["clip"] * 10 ** (c["level_gain"] / 20.0)

    # 2. one gain for the film, then the limiter; measured on the sentences 0.35 s apart, whatever the film's pauses
    def canon(parts):
        gap = np.zeros(int(0.35 * SR))
        seq = [gap]
        for p in parts:
            seq += [p, gap]
        return np.concatenate(seq)

    base = [c["clip"] for c in clips]
    lufs0, tp0 = loudness(canon(base))
    gain, ceiling = TARGET_LUFS - lufs0, MAX_TRUE_PEAK - 0.5
    out, curves = base, [np.ones(1)]
    for _ in range(8):
        out, curves = [], []
        for p in base:
            y, g = limit(p * 10 ** (gain / 20.0), 10 ** (ceiling / 20.0))
            out.append(y)
            curves.append(g)
        lufs, tp = loudness(canon(out))
        if tp > MAX_TRUE_PEAK - 0.05:
            ceiling -= (tp - (MAX_TRUE_PEAK - 0.05)) + 0.1
            continue
        if abs(lufs - TARGET_LUFS) <= 0.05:
            break
        gain += TARGET_LUFS - lufs
    allg = np.concatenate(curves)
    for c, y in zip(clips, out):
        c["clip"] = y
        c["level"] = speech_level(y)
    report = {"target_lufs": TARGET_LUFS, "before_lufs": round(lufs0, 2), "before_true_peak_db": round(tp0, 2),
              "gain_db": round(gain, 2), "limiter_ceiling_db": round(ceiling, 2),
              "max_gain_reduction_db": round(-db(float(allg.min())), 2),
              "share_limited_over_1db": round(float(np.mean(allg < 10 ** (-1 / 20.0))), 4),
              "share_limited_over_3db": round(float(np.mean(allg < 10 ** (-3 / 20.0))), 4),
              "sentence_level_gain_db": [round(c["level_gain"], 2) for c in clips],
              "sentence_level_db": [round(c["level"], 2) for c in clips]}
    return clips, report


def layout(norm, clips):
    """Place the sentence clips on the film's time line: (samples, [(onset, offset) of each sentence in seconds],
    duration). The first sound is at `lead`; each sentence starts `pause` after the sound of the one before ends."""
    fps = norm["fps"]
    t = norm["lead"]
    spans = []
    for line, c in zip(norm["lines"], clips):
        dur = c["offset"] - c["onset"]
        spans.append((t, t + dur))
        t += dur + line["pause"]
    end = spans[-1][1] + norm["tail"]
    frames = int(math.ceil(end * fps - 1e-6))
    duration = frames / float(fps)
    out = np.zeros(int(round(duration * SR)), dtype=np.float64)
    for (t0, _t1), c in zip(spans, clips):
        a = int(round((t0 - c["onset"]) * SR))
        seg = c["clip"]
        lo, hi = max(0, a), min(len(out), a + len(seg))
        out[lo:hi] += seg[lo - a:hi - a]                             # margins may overlap in a short pause: they add
    return out, spans, duration


def narrate(film, eng, voice=None, speed=None, log=print, second_opinion=True):
    """Build the narration of a film from its NARRATION spec. With `voice` / `speed` the result is a listening
    copy under out/test (the committed narration always follows the film's own spec). Returns the json dict."""
    spec = N.read_spec(film)
    audition = voice is not None or speed is not None
    if audition:
        spec = dict(spec)
        if voice:
            spec["voice"] = voice
        if speed:
            spec["speed"] = speed
    norm = N.normalise(spec)
    name = N.film_name(film)
    log("[narrate] %s: %d sentences, voice %s, speed %s" % (name, len(norm["lines"]), norm["voice"], norm["speed"]))
    t_start = time.time()
    clips, loud = synthesise(eng, norm, log)
    if not eng.timed:
        log("[narrate]   WARNING: %s is missing, the words are timed by the recogniser alone (less exact after "
            "pauses): run  tools/narrate.py --make-timed-model" % KOKORO_TIMED)
    audio, spans, duration = layout(norm, clips)
    words, sentences, estimated = [], [], []
    for i, (line, c, (s0, s1)) in enumerate(zip(norm["lines"], clips, spans)):
        script = N.words_of(line["text"])
        if eng.timed and c["model"] is None:
            log("[narrate]   sentence %d: the voice was given %d words for %d script words (a respelling in 'say' "
                "must stay one word): timed by the recogniser" % (i, len(N.words_of(line["spoken"])), len(script)))
        timed = time_sentence(eng, c["clip"], script, c["onset"], c["offset"], model=c["model"],
                              second_opinion=second_opinion)
        first = len(words)
        for text, tw in zip(script, timed):
            entry = {"text": text, "caption": N.caption_form(text),
                     "start": round(s0 + tw["start"] - c["onset"], 4), "end": round(s0 + tw["end"] - c["onset"], 4),
                     "sentence": i, "source": tw["source"], "estimated": tw["estimated"]}
            if tw.get("second") is not None:                         # the recogniser's start, for the record
                entry["second"] = round(s0 + tw["second"] - c["onset"], 4)
                entry["second_source"] = tw["second_source"]
            if tw["estimated"]:
                estimated.append(len(words))
            words.append(entry)
        sentences.append({"index": i, "id": line["id"], "text": line["text"], "spoken": line["spoken"],
                          "start": round(s0, 4), "end": round(s1, 4), "pause_after": line["pause"],
                          "speed": line["speed"], "first_word": first, "last_word": len(words) - 1})
    for a, b in zip(words, words[1:]):                               # rounding must not break the order
        if b["start"] < a["end"]:
            b["start"] = a["end"]
    lufs, tp = loudness(audio)
    loud.update(integrated_lufs=round(lufs, 2), true_peak_db=round(tp, 2))
    if tp > MAX_TRUE_PEAK or abs(lufs - TARGET_LUFS) > 0.6:
        log("[narrate]   WARNING: the file measures %.2f LUFS, true peak %.2f dBTP (wanted %.1f +- 0.6, under %.1f)"
            % (lufs, tp, TARGET_LUFS, MAX_TRUE_PEAK))
    if audition:
        wav = os.path.join(OUT_TEST, "narrate_%s_%s%s.wav" % (name, norm["voice"], "" if not speed else "_x%s" % speed))
    else:
        wav = N.wav_path(name)
    write_wav(wav, audio)
    speech = sum(s1 - s0 for s0, s1 in spans)
    data = {
        "film": name, "json_version": JSON_VERSION, "spec_hash": N.spec_hash(norm), "spec": norm,
        "voice": norm["voice"], "lang": eng.lang(norm["voice"]), "speed": norm["speed"],
        "sample_rate": SR, "channels": 1, "fps": norm["fps"],
        "duration": round(duration, 6), "frames": int(round(duration * norm["fps"])),
        "lead": norm["lead"], "tail": round(duration - spans[-1][1], 4),
        "speech_seconds": round(speech, 3), "words_per_second_speaking": round(len(words) / speech, 3),
        "words_per_second_overall": round(len(words) / (spans[-1][1] - spans[0][0]), 3),
        "timing": "model" if eng.timed else "recogniser",
        "loudness": loud, "wav": os.path.basename(wav), "wav_sha1": N.file_sha1(wav),
        "sentences": sentences, "words": words, "estimated_words": estimated, "tools": eng.versions(),
    }
    js = wav[:-4] + ".json"
    tmp = js + ".part"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, js)
    bad = [c for c in (w["caption"] for w in words) if any(ord(ch) > 126 or ord(ch) < 32 for ch in c)]
    log("[narrate] %s: %.2f s (%d frames at %d fps), %d words, %.2f words/s while speaking, %.2f overall; "
        "%.1f LUFS, true peak %.1f dBTP (limiter took up to %.1f dB); timing by %s, %d words estimated%s; %.0f s"
        % (name, duration, data["frames"], norm["fps"], len(words), data["words_per_second_speaking"],
           data["words_per_second_overall"], lufs, tp, loud["max_gain_reduction_db"], data["timing"], len(estimated),
           (": " + ", ".join("%d %r" % (k, words[k]["text"]) for k in estimated)) if estimated else "",
           time.time() - t_start))
    seconds = [w for w in words if "second" in w and not w["estimated"] and w["second_source"] != "estimated"]
    if seconds:
        d = np.array([w["second"] - w["start"] for w in seconds]) * 1000.0
        log("[narrate]   second opinion (recogniser) on %d words: median |difference| %.0f ms, %d%% within one "
            "frame, %d%% within two; largest %+.0f ms"
            % (len(d), float(np.median(np.abs(d))), round(100 * float(np.mean(np.abs(d) <= 1000 * FRAME))),
               round(100 * float(np.mean(np.abs(d) <= 2000 * FRAME))), float(d[np.argmax(np.abs(d))])))
        # the recogniser runs EARLY inside speech (--selftest: it hears a word start while the one before is still
        # sounding), so only the other direction, or a very large difference, is worth a second look
        far = [w for w in seconds if w["second"] - w["start"] > 0.10 or w["second"] - w["start"] < -0.30]
        if far:
            log("[narrate]   CHECK: the recogniser puts these words more than 100 ms later or 300 ms earlier: "
                + ", ".join("%r (%+.0f ms)" % (w["text"], 1000 * (w["second"] - w["start"])) for w in far))
    if bad:
        log("[narrate]   WARNING: captions with characters the Minecraft font page lacks: %s" % sorted(set(bad)))
    log("[narrate] wrote %s and %s" % (os.path.relpath(wav, ROOT), os.path.relpath(js, ROOT)))
    return data


def make_timed_model(log=print):
    """Write kokoro-v1.0.timed.onnx beside kokoro-v1.0.onnx: the same network with the duration predictor's
    result (frames per phoneme: Div by speed -> Round -> Clip -> Cast -> Gather, the tensor its CumSum reads)
    exposed as a second output named 'duration', which kokoro-onnx turns into phoneme timings. Needs the `onnx`
    package (pip install onnx; not needed afterwards). The audio output is untouched (checked: bit-identical)."""
    try:
        import onnx
        from onnx import TensorProto, helper
    except ImportError:
        raise SystemExit("the `onnx` package is needed once for this: pip install onnx (or put it on PYTHONPATH)")
    src, dst = os.path.join(MODELS, KOKORO_ONNX), os.path.join(MODELS, KOKORO_TIMED)
    model = onnx.load(src)
    g = model.graph
    if any(o.name == "duration" for o in g.output):
        raise SystemExit("%s already has a duration output" % src)
    readers = {}
    for node in g.node:
        for name in node.input:
            readers.setdefault(name, []).append(node)
    div = [node for node in g.node if node.op_type == "Div" and "speed" in node.input]
    if len(div) != 1:
        raise SystemExit("expected one Div by the speed input in the graph, found %d: not the model this was written for" % len(div))
    cur, prev, chain = div[0], None, ["Div"]
    while cur.op_type != "CumSum":
        nxt = readers.get(cur.output[0], [])
        if len(nxt) != 1:
            raise SystemExit("unexpected graph after the speed division (%s): not the model this was written for" % chain)
        prev, cur = cur, nxt[0]
        chain.append(cur.op_type)
    if chain != ["Div", "Round", "Clip", "Cast", "Gather", "CumSum"]:
        raise SystemExit("unexpected duration chain %s: not the model this was written for" % chain)
    g.node.append(helper.make_node("Identity", [prev.output[0]], ["duration"], name="expose_duration"))
    g.output.append(helper.make_tensor_value_info("duration", TensorProto.INT64, ["tokens_with_pads"]))
    onnx.save(model, dst + ".part")
    os.replace(dst + ".part", dst)
    plain, timed = Engines(2, timed=False), Engines(2, timed=True)
    text = "In this bastion, I'm the only one who doesn't like gold."
    a, none = plain.speak(text, N.DEFAULT_VOICE)
    b, timings = timed.speak(text, N.DEFAULT_VOICE)
    same = none is None and timings is not None and len(a) == len(b) and float(np.abs(a - b).max()) == 0.0
    log("[narrate] wrote %s (duration tensor %s); audio identical to %s: %s; %d phoneme timings for the test sentence"
        % (dst, prev.output[0], KOKORO_ONNX, same, len(timings or [])))
    if not same:
        raise SystemExit("the timed model does not reproduce the audio of the original")
    return dst


# ---------------------------------------------------------------------------------------------------------------
# measurements
# ---------------------------------------------------------------------------------------------------------------

PACING_TEXT = [
    "In this village, everyone is afraid of the player.",
    "He builds farms out of iron golems.",
    "I watched him do it.",
    "First he trapped three villagers at the top of a tower.",
    "Then he put a zombie where they could see it.",
    "They got scared, so a golem came to protect them.",
    "It fell straight into the lava.",
    "My dad says we should not look up.",
    "But I look up every single night.",
    "Tonight, I am going to climb.",
    "Somebody has to open that trapdoor.",
    "And I am the only one small enough to fit.",
]

TEST_SENTENCES = [
    "In this village, everyone is afraid of the player.",
    "He makes farms out of our iron golems.",
    "The villagers get trapped at the top, and the golems fall into the lava.",
    "I am just a baby villager, but I saw everything.",
    "In this town, everyone is musical except me.",
    "The biggest Crammy party is today, and I never have anything to perform.",
    "Steve plays the note blocks, and Alex sings.",
    "Even the jukebox has more talent than I do.",
    "Tonight at the Crammys, I finally found my sound.",
    "In this town, everyone wants to get ripped.",
    "There's a chicken farm, and a cow farm for protein shakes.",
    "But I'm a redstoner.",
    "They laughed at my pistons and my sticky trapdoors.",
    "Then one night, the raid came.",
    "One of my traps saved the whole village.",
    "Now the gym bros carry my redstone for me.",
    "In this town, the player has an underground base.",
    "My dad got taken down there last week.",
    "It's a villager trading hall.",
    "They turn villagers into zombies, then cure them for better trades.",
    "He came back selling Mending for one emerald.",
    "He doesn't remember my name.",
    "In this town, the player used to protect us.",
    "But one day he went into the woods, wearing his best armor.",
    "Now he just stands around and watches us.",
    "His eyes are white, and he never blinks.",
    "The grown-ups call him Herobrine.",
    "I don't think he is our player anymore.",
    "In this bastion, I'm the only one who doesn't like gold.",
    "The speedrunners trap piglins in holes to trade with them.",
    "They throw gold ingots, and my brothers throw back ender pearls.",
    "I'm a piglin brute, and I don't trade.",
    "I just keep attacking him.",
    "Every new world, there he is again, with his bucket and his boat.",
    "He needs twelve pearls, and I need him gone.",
    "His speedrun died at fourteen minutes, and I did that.",
    "Netherite armor doesn't scare me.",
    "He respawned, looked at me, and quit the game.",
    "Creepers, zombies and skeletons don't come here anymore.",
    "The redstoner's pickaxe had Mending and Unbreaking three.",
    "Why does nobody ask the villagers what they want?",
    "Wait... is that an enderman holding my bed?",
    "Obsidian, cobblestone, and a bucket of lava: that's all it took.",
    "We count who made it home, and tonight, somebody didn't.",
]


def voices_report(eng, names, log=print):
    """Pace of each voice at speed 1.0 on PACING_TEXT, sentence by sentence with the default pauses."""
    pause, lead, tail = N.DEFAULTS["pause"], N.DEFAULTS["lead"], N.DEFAULTS["tail"]
    n_words = sum(len(N.words_of(s)) for s in PACING_TEXT)
    rows = []
    for v in names:
        speech, f0 = 0.0, []
        for s in PACING_TEXT:
            c = speak_sentence(eng, s, N.spoken_text(s), v, 1.0)
            speech += c["offset"] - c["onset"]
            f0.append(pitch(c["clip"]))
        speaking = n_words / speech
        overall = n_words / (speech + (len(PACING_TEXT) - 1) * pause)
        fit = (60.0 - lead - tail) * overall
        rows.append({"voice": v, "words_per_second_speaking": round(speaking, 2), "words_per_second_with_pauses": round(overall, 2),
                     "words_in_60s": int(fit), "median_pitch_hz": round(float(np.median([f for f in f0 if f > 0])), 0)})
        log("  %-11s %.2f words/s while speaking, %.2f with the default %.2f s pauses -> %3d words in 60 s "
            "(lead %.1f, tail %.1f); pitch %3.0f Hz" % (v, speaking, overall, pause, fit, lead, tail,
                                                        rows[-1]["median_pitch_hz"]))
    return {"text_words": n_words, "sentences": len(PACING_TEXT), "voices": rows}


def paragraph_check(eng, voice, log=print):
    """Sentence-by-sentence synthesis against one whole-paragraph synthesis of the same six sentences: speech
    level, pitch and pace of every sentence in both, the pauses the model makes on its own, and the joins."""
    text = PACING_TEXT[:6]
    norm = N.normalise({"voice": voice, "lines": text})
    clips, _loud = synthesise(eng, norm, log=lambda *_: None)
    audio, spans, _dur = layout(norm, clips)
    own = {"level": [speech_level(c["clip"]) for c in clips], "pitch": [pitch(c["clip"]) for c in clips],
           "rate": [len(N.words_of(s)) / (c["offset"] - c["onset"]) for s, c in zip(text, clips)]}
    # the joins: the loudest sample within 15 ms of where one clip's margin ends and the next begins, and the
    # largest step between neighbouring samples there, against the largest step inside speech
    step = np.abs(np.diff(audio))
    edge_peak, edge_step = 0.0, 0.0
    for (_a0, a1), (b0, _b1) in zip(spans, spans[1:]):
        for t in (a1 + POST, b0 - PRE):
            k = int(round(t * SR))
            lo, hi = max(0, k - int(0.015 * SR)), min(len(audio) - 1, k + int(0.015 * SR))
            edge_peak = max(edge_peak, float(np.abs(audio[lo:hi]).max()))
            edge_step = max(edge_step, float(step[lo:hi].max()))
    whole = speak_sentence(eng, " ".join(text), " ".join(N.spoken_text(s) for s in text), voice, 1.0)
    words = [w for s in text for w in N.words_of(s)]
    timed = time_sentence(eng, whole["clip"], words, whole["onset"], whole["offset"], model=whole["model"],
                          second_opinion=whole["model"] is None)
    para = {"level": [], "pitch": [], "rate": [], "pauses": []}
    k, prev_end = 0, None
    for s in text:
        n = len(N.words_of(s))
        t0, t1 = timed[k]["start"], timed[k + n - 1]["end"]
        seg = whole["clip"][int(t0 * SR):int(t1 * SR)]
        para["level"].append(speech_level(seg))
        para["pitch"].append(pitch(seg))
        para["rate"].append(n / (t1 - t0))
        if prev_end is not None:
            para["pauses"].append(t0 - prev_end)
        prev_end = t1
        k += n

    def spread(v):
        return float(max(v) - min(v))

    res = {
        "voice": voice, "sentences": len(text),
        "level_db": {"sentence_by_sentence": [round(x, 1) for x in own["level"]], "paragraph": [round(x, 1) for x in para["level"]]},
        "level_spread_db": {"sentence_by_sentence": round(spread(own["level"]), 2), "paragraph": round(spread(para["level"]), 2)},
        "pitch_hz": {"sentence_by_sentence": [round(x) for x in own["pitch"]], "paragraph": [round(x) for x in para["pitch"]]},
        "pitch_spread_semitones": {
            "sentence_by_sentence": round(12 * math.log2(max(own["pitch"]) / min(own["pitch"])), 2),
            "paragraph": round(12 * math.log2(max(para["pitch"]) / min(para["pitch"])), 2)},
        "words_per_second": {"sentence_by_sentence": [round(x, 2) for x in own["rate"]], "paragraph": [round(x, 2) for x in para["rate"]]},
        "paragraph_own_pauses_s": [round(p, 2) for p in para["pauses"]],
        "join_peak_dbfs": round(db(edge_peak), 1), "join_largest_step_dbfs": round(db(edge_step), 1),
        "speech_largest_step_dbfs": round(db(float(step.max())), 1),
    }
    for key, val in res.items():
        log("  %-26s %s" % (key, val))
    return res


def _stats(errs):
    """Summary of signed errors in seconds: absolute median / mean / p90 / max in ms, shares within 1 and 2 frames,
    and the share that is LATE by more than a frame (positive = later than the reference)."""
    e = np.asarray(errs, dtype=np.float64)
    if len(e) == 0:
        return {"n": 0}
    a = np.abs(e) * 1000.0
    return {"n": int(len(a)), "median_ms": round(float(np.median(a)), 1), "mean_ms": round(float(a.mean()), 1),
            "p90_ms": round(float(np.percentile(a, 90)), 1), "max_ms": round(float(a.max()), 1),
            "signed_mean_ms": round(1000 * float(e.mean()), 1),
            "within_1_frame": round(float(np.mean(a <= 1000 * FRAME + 1e-6)), 3),
            "within_2_frames": round(float(np.mean(a <= 2000 * FRAME + 1e-6)), 3),
            "late_over_1_frame": round(float(np.mean(e > FRAME + 1e-9)), 3)}


def selftest(eng, voice, part_seconds, log=print):
    """Timing accuracy on TEST_SENTENCES, one cached record per sentence (out/test/narrate_selftest_<voice>.json),
    so the command can be run again until everything is done. Four questions:
      A  natural sentences. The voice model's phoneme timing against the SOUND: after every pause (and at the
         sentence start) the first sound is measured on the samples, which no model is involved in. Then the
         final timing (model + energy) against the recogniser's (forced alignment + energy), word by word.
      B  ground truth for the recogniser: the sentence synthesised in pieces of 2-4 words, each cut to its exact
         first and last sound and joined, alternately with NO gap and with a 250 ms gap. Every piece start is
         known to the sample; the recogniser timing must find the first word of each piece there.
      C  the recogniser run freely over whole files (11 sentences each), its words matched to the script by
         letters, against the final per-sentence timing.
      D  what the free transcript got wrong (misheard, split or merged words).
      E  who is right where the two timings differ by more than 100 ms inside speech: the sentence is cut at the
         final start of such a word and at the recogniser's, and the recogniser says what it hears on each side."""
    if not eng.timed:
        raise SystemExit("the selftest compares the model's timing with the recogniser's: run --make-timed-model first")
    path = os.path.join(OUT_TEST, "narrate_selftest_%s.json" % voice)
    try:
        with open(path, encoding="utf-8") as f:
            cache = json.load(f)
    except (OSError, ValueError):
        cache = {}
    if cache.get("version") != JSON_VERSION:
        cache = {"version": JSON_VERSION}
    t0 = time.time()
    rng_cuts = np.random.default_rng(7)
    plans = []
    for s in TEST_SENTENCES:                                         # the same pieces on every run
        n = len(N.words_of(s))
        cuts, k = [], 0
        while True:
            k += int(rng_cuts.integers(2, 5))
            if k >= n - 1:
                break
            cuts.append(k)
        plans.append(cuts)

    def save():
        os.makedirs(OUT_TEST, exist_ok=True)
        with open(path + ".part", "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=1)
        os.replace(path + ".part", path)

    for idx, (s, cuts) in enumerate(zip(TEST_SENTENCES, plans)):
        key = "s%02d" % idx
        if key in cache and cache[key].get("text") == s:
            continue
        if time.time() - t0 > part_seconds:
            break
        words = N.words_of(s)
        rec = {"text": s, "words": words}
        # A: the natural sentence
        c = speak_sentence(eng, s, N.spoken_text(s), voice, 1.0)
        final = time_sentence(eng, c["clip"], words, c["onset"], c["offset"], model=c["model"], second_opinion=False)
        recog = time_by_recogniser(eng, c["clip"], words, c["onset"], c["offset"], free=True)
        rec["A"] = {
            "final": [round(w["start"], 4) for w in final], "source": [w["source"] for w in final],
            "model_raw": [w["model_raw"] for w in final], "estimated": [i for i, w in enumerate(final) if w["estimated"]],
            "recogniser": [round(w["start"], 4) for w in recog], "recogniser_source": [w["source"] for w in recog],
            "raw_forced": [w["raw_forced"] for w in recog], "kind": [w["recognised"]["kind"] for w in recog],
            "pauses": final[0].get("pauses", []), "punctuated": punctuated_words(words),
            "onset": round(c["onset"], 4), "offset": round(c["offset"], 4)}
        # B: pieces with known boundaries, timed by the recogniser alone
        edges = [0] + cuts + [len(words)]
        firsts, truth, gaps, buf, cur = [], [], [], [], 0.0
        for p, (a, b) in enumerate(zip(edges, edges[1:])):
            raw, _t = eng.speak(N.spoken_text(" ".join(words[a:b])), voice, 1.0)
            rr = sound_runs(raw)
            x = np.array(raw[int(round(rr[0][0] * SR)):int(round(rr[-1][1] * SR))], dtype=np.float64)
            nf = int(0.003 * SR)
            x[:nf] *= np.linspace(0.0, 1.0, nf)
            x[-nf:] *= np.linspace(1.0, 0.0, nf)
            gap = 0.0 if (p == 0 or p % 2 == 1) else 0.25           # pieces 1, 3, ... butt against the one before
            if p:
                buf.append(np.zeros(int(round(gap * SR))))
                cur += int(round(gap * SR)) / SR
            truth.append(cur)
            gaps.append(gap)
            buf.append(x)
            cur += len(x) / SR
            firsts.append(a)
        joined = np.concatenate([np.zeros(int(PRE * SR))] + buf + [np.zeros(int(POST * SR))])
        t_b = time_by_recogniser(eng, joined, words, PRE, PRE + cur)
        rec["B"] = {"first_words": firsts, "gap": gaps, "truth": [round(PRE + t, 4) for t in truth],
                    "recogniser": [round(t_b[a]["start"], 4) for a in firsts],
                    "raw_forced": [t_b[a]["raw_forced"] for a in firsts], "source": [t_b[a]["source"] for a in firsts]}
        cache[key] = rec
        save()
        log("  %2d/%d %5.1f s  %s" % (idx + 1, len(TEST_SENTENCES), time.time() - t0, s))
    done = [cache.get("s%02d" % i) for i in range(len(TEST_SENTENCES))]
    done = [d for d in done if d]
    group = 11
    n_files = math.ceil(len(TEST_SENTENCES) / group)
    if len(done) == len(TEST_SENTENCES):
        for g in range(0, len(TEST_SENTENCES), group):
            key = "file%d" % (g // group)
            if key in cache:
                continue
            if time.time() - t0 > part_seconds:
                break
            sents = TEST_SENTENCES[g:g + group]
            norm = N.normalise({"voice": voice, "lines": sents})
            clips, _loud = synthesise(eng, norm, log=lambda *_: None)
            audio, spans, _dur = layout(norm, clips)
            words = [w for s in sents for w in N.words_of(s)]
            heard = eng.recognise(resample(audio, SR, 16000))
            ht = from_recognition(words, heard, spans[0][0], spans[-1][1])
            snapped, _on, _p = snap_to_sound([[a, b] for a, b, _k in ht], sound_runs(audio), punctuated=punctuated_words(words))
            per = []
            for s, c, (s0, _s1) in zip(sents, clips, spans):
                timed = time_sentence(eng, c["clip"], N.words_of(s), c["onset"], c["offset"], model=c["model"], second_opinion=False)
                per += [round(s0 + w["start"] - c["onset"], 4) for w in timed]
            cache[key] = {"final": per, "whole_file": [round(a, 4) for a, _b in snapped],
                          "whole_file_raw": [round(a, 4) for a, _b, _k in ht], "kind": [k for _a, _b, k in ht],
                          "heard": " ".join(h[0] for h in heard), "script": " ".join(words)}
            save()
            log("  whole file %d/%d  %5.1f s" % (g // group + 1, n_files, time.time() - t0))
    files = [cache[k] for k in sorted(cache) if k.startswith("file")]
    # E: who is right where the two timings disagree inside speech? Cut the sentence at each of the two starts of
    # such a word and let the recogniser say what it hears on either side: with the cut in the right place the
    # audio before it ends with the whole word before, and the audio after it begins with the word itself.
    gating_done = False
    if len(done) == len(TEST_SENTENCES) and len(files) == n_files:
        disputed = [(idx, i) for idx, d in enumerate(done) for i in range(1, len(d["words"]))
                    if d["A"]["source"][i] == "model" and abs(d["A"]["recogniser"][i] - d["A"]["final"][i]) > 0.10]
        pick = disputed[::max(1, len(disputed) // 16)][:16]
        gate = cache.setdefault("gating", {"disputed": len(disputed), "cuts": {}})
        for idx, i in pick:
            key = "%d:%d" % (idx, i)
            if key in gate["cuts"]:
                continue
            if time.time() - t0 > part_seconds:
                break
            d = done[idx]
            c = speak_sentence(eng, d["text"], N.spoken_text(d["text"]), voice, 1.0)
            res = {"word": d["words"][i], "before": d["words"][i - 1],
                   "difference_ms": round(1000 * (d["A"]["recogniser"][i] - d["A"]["final"][i]))}
            for name, t in (("model", d["A"]["final"][i]), ("recogniser", d["A"]["recogniser"][i])):
                k = int(round(t * SR))
                nf = int(0.004 * SR)
                a, b = np.array(c["clip"][:k]), np.array(c["clip"][k:])
                a[-nf:] *= np.linspace(1.0, 0.0, nf)
                b[:nf] *= np.linspace(0.0, 1.0, nf)
                pad = np.zeros(int(0.2 * SR))
                ha = [h[0] for h in eng.recognise(resample(np.concatenate([pad, a, pad]), SR, 16000))]
                hb = [h[0] for h in eng.recognise(resample(np.concatenate([pad, b, pad]), SR, 16000))]
                res[name] = {"heard_before": " ".join(ha), "heard_after": " ".join(hb),
                             "before_ends_with_word": bool(ha) and N.letters(ha[-1]) == N.letters(d["words"][i - 1]),
                             "after_starts_with_word": bool(hb) and N.letters(hb[0]) == N.letters(d["words"][i])}
            gate["cuts"][key] = res
            save()
            log("  cut %d/%d  %5.1f s  %r" % (len(gate["cuts"]), len(pick), time.time() - t0, res["word"]))
        gating_done = len(gate["cuts"]) >= len(pick)
    if len(done) < len(TEST_SENTENCES) or len(files) < n_files or not gating_done:
        log("[narrate] selftest: %d of %d sentences, %d of %d files, cuts %s; run the same command again to continue"
            % (len(done), len(TEST_SENTENCES), len(files), n_files, "done" if gating_done else "not done"))
        return None
    # ---- report
    n_words = sum(len(d["words"]) for d in done)
    estimated, kinds, misheard = 0, {}, []
    onset_model, onset_forced, a_all, a_mid, a_onset, first_model = [], [], [], [], [], []
    pauses_total, pauses_punct, pauses_unassigned = 0, 0, 0
    for d in done:
        A = d["A"]
        estimated += len(A["estimated"])
        for _g0, _g1, b in A["pauses"]:
            pauses_total += 1
            pauses_unassigned += b is None
            pauses_punct += b is not None and b in A["punctuated"]
        for i, w in enumerate(d["words"]):
            kinds[A["kind"][i]] = kinds.get(A["kind"][i], 0) + 1
            if A["kind"][i] != "exact":
                misheard.append("%s (%s)" % (N.caption_form(w), A["kind"][i]))
            a_all.append(A["recogniser"][i] - A["final"][i])
            if i == 0:                                               # the sentence start: nothing precedes it, the
                if A["model_raw"][i] is not None:                    # model's first phoneme against the first sound
                    first_model.append(A["model_raw"][i] - A["final"][i])
            elif A["source"][i] == "energy":                         # final[i] IS the measured onset of the sound
                if A["model_raw"][i] is not None:
                    onset_model.append(A["model_raw"][i] - A["final"][i])
                onset_forced.append(A["raw_forced"][i] - A["final"][i])
                a_onset.append(A["recogniser"][i] - A["final"][i])
            else:
                a_mid.append(A["recogniser"][i] - A["final"][i])
    b_butt, b_gap, b_raw_butt, b_raw_gap = [], [], [], []
    for d in done:
        B = d["B"]
        for p in range(1, len(B["truth"])):
            e, r = B["recogniser"][p] - B["truth"][p], B["raw_forced"][p] - B["truth"][p]
            (b_gap if B["gap"][p] > 0 else b_butt).append(e)
            (b_raw_gap if B["gap"][p] > 0 else b_raw_butt).append(r)
    c_diff, c_raw, c_kinds = [], [], {}
    for f in files:
        c_diff += [w - p for w, p in zip(f["whole_file"], f["final"])]
        c_raw += [w - p for w, p in zip(f["whole_file_raw"], f["final"])]
        for k in f["kind"]:
            c_kinds[k] = c_kinds.get(k, 0) + 1
    report = {
        "voice": voice, "sentences": len(done), "words": n_words, "estimated_words_in_final_timing": estimated,
        "pauses_inside_sentences": {"found": pauses_total, "at_punctuation": pauses_punct, "given_to_no_word": pauses_unassigned},
        "A_model_vs_measured_onset_after_pauses": _stats(onset_model),
        "A_model_first_phoneme_vs_first_sound_of_sentence": _stats(first_model),
        "A_raw_forced_alignment_vs_measured_onset_after_pauses": _stats(onset_forced),
        "A_recogniser_vs_final_all_words": _stats(a_all),
        "A_recogniser_vs_final_inside_speech": _stats(a_mid),
        "A_recogniser_vs_final_after_pauses": _stats(a_onset),
        "B_recogniser_vs_truth_no_gap": _stats(b_butt), "B_recogniser_vs_truth_250ms_gap": _stats(b_gap),
        "B_raw_forced_vs_truth_no_gap": _stats(b_raw_butt), "B_raw_forced_vs_truth_250ms_gap": _stats(b_raw_gap),
        "C_whole_file_recognition_vs_final": _stats(c_diff), "C_whole_file_raw_vs_final": _stats(c_raw),
        "C_whole_file_word_kinds": c_kinds,
        "D_free_transcript_word_kinds": kinds, "D_not_heard_as_written": misheard,
    }
    cuts = list(cache["gating"]["cuts"].values())
    report["E_words_where_the_timings_differ_over_100ms"] = cache["gating"]["disputed"]
    report["E_cut_tests"] = len(cuts)
    for name in ("model", "recogniser"):
        report["E_cut_at_%s_start" % name] = {
            "audio_before_ends_with_the_word_before": sum(c[name]["before_ends_with_word"] for c in cuts),
            "audio_after_starts_with_the_word": sum(c[name]["after_starts_with_word"] for c in cuts),
            "both": sum(c[name]["before_ends_with_word"] and c[name]["after_starts_with_word"] for c in cuts)}
    out = os.path.join(OUT_TEST, "narrate_selftest_%s_report.json" % voice)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)
    for key, val in report.items():
        log("  %-44s %s" % (key, val))
    log("[narrate] selftest report -> %s" % os.path.relpath(out, ROOT))
    m = report["A_model_vs_measured_onset_after_pauses"]
    ok = (estimated == 0 and pauses_unassigned == 0 and m["n"] > 0 and m["within_2_frames"] >= 0.9
          and report["E_cut_at_model_start"]["both"] >= report["E_cut_at_recogniser_start"]["both"])
    log("[narrate] selftest %s" % ("passed" if ok else "FAILED its limits (no estimated word; every pause inside a "
        "sentence given to a word, so that the word after it starts on the measured sound; the model's own timing "
        "within two frames of that sound for 90 % of them; cutting at the model's word starts leaves at least as "
        "many words whole as cutting at the recogniser's)"))
    return report if ok else False


def hear(eng, path, film=None, log=print):
    """Recognise the words in an audio or video file. With `film`, the film's script words are located in it by
    the recogniser's free transcript matched by letters and fitted to the measured sound: nothing of
    narration/<film>.json is used, so this is an independent measurement of what is really in the file."""
    audio = read_audio(path, SR)
    heard = eng.recognise(resample(audio, SR, 16000))
    out = {"file": os.path.relpath(os.path.abspath(path), ROOT), "duration": round(len(audio) / SR, 4),
           "heard": [{"word": w, "start": round(s, 3), "end": round(e, 3)} for w, s, e, _p in heard]}
    lufs, tp = loudness(audio)
    out["integrated_lufs_mono_downmix"], out["true_peak_db_mono_downmix"] = round(lufs, 2), round(tp, 2)
    if film:
        norm = N.normalise(N.read_spec(film))
        words = [w for line in norm["lines"] for w in N.words_of(line["text"])]
        runs = sound_runs(audio)
        lo, hi = (runs[0][0], runs[-1][1]) if runs else (0.0, len(audio) / SR)
        ht = from_recognition(words, heard, lo, hi)
        snapped, on_sound, _p = snap_to_sound([[a, b] for a, b, _k in ht], runs, punctuated=punctuated_words(words))
        fixed, _spread = repair(snapped, words, lo, hi)
        out["film"] = N.film_name(film)
        out["words"] = [{"text": w, "caption": N.caption_form(w), "start": round(t[0], 4), "end": round(t[1], 4),
                         "raw_start": round(k[0], 4), "kind": k[2], "on_sound": i in on_sound}
                        for i, (w, t, k) in enumerate(zip(words, fixed, ht))]
    name = os.path.splitext(os.path.basename(path))[0]
    dst = os.path.join(OUT_TEST, "narrate_heard_%s.json" % name)
    os.makedirs(OUT_TEST, exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    log("[narrate] heard %d words in %s (%.2f s, %.1f LUFS as mono) -> %s"
        % (len(heard), out["file"], out["duration"], lufs, os.path.relpath(dst, ROOT)))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="narrate", description="Speak a film's NARRATION and time every word.")
    ap.add_argument("film", nargs="?", help="module name under films/ (its NARRATION literal is the script)")
    ap.add_argument("--voice", help="listen to another voice: writes out/test/narrate_<film>_<voice>.wav, not narration/")
    ap.add_argument("--speed", type=float, help="listen at another speed (also a copy under out/test)")
    ap.add_argument("--check", action="store_true", help="only say whether narration/<film>.json is current (exit 0 / 1)")
    ap.add_argument("--force", action="store_true", help="speak again even when the narration is current")
    ap.add_argument("--phonemes", action="store_true", help="print the phonemes of every sentence and stop")
    ap.add_argument("--voices", nargs="*", metavar="VOICE", help="pace table for these voices (default: the six tried)")
    ap.add_argument("--selftest", action="store_true", help="timing accuracy on the built-in test sentences (resumable)")
    ap.add_argument("--paragraph-check", action="store_true", help="sentence-by-sentence against whole-paragraph synthesis")
    ap.add_argument("--hear", metavar="FILE", help="recognise the words in an audio / video file (with a film: locate its script words)")
    ap.add_argument("--make-timed-model", action="store_true", help="write %s (needs the onnx package once)" % KOKORO_TIMED)
    ap.add_argument("--recogniser-only", action="store_true", help="time the words without the voice model's durations")
    ap.add_argument("--part-seconds", type=float, default=230.0, help="--selftest: stop starting new work after this long")
    ap.add_argument("--threads", type=int, default=2, help="CPU threads for the voice and the recogniser (default 2)")
    args = ap.parse_args(argv)
    if args.make_timed_model:
        make_timed_model()
        return 0
    eng = Engines(args.threads, timed=not args.recogniser_only)
    voice = args.voice or N.DEFAULT_VOICE

    if args.voices is not None:
        names = args.voices or ["am_michael", "am_fenrir", "am_puck", "bm_george", "bm_fable", "af_heart"]
        print("[narrate] pace on %d sentences, %d words, speed 1.0:" % (len(PACING_TEXT), sum(len(N.words_of(s)) for s in PACING_TEXT)))
        rep = voices_report(eng, names)
        os.makedirs(OUT_TEST, exist_ok=True)
        with open(os.path.join(OUT_TEST, "narrate_voices.json"), "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=1)
        return 0
    if args.selftest:
        rep = selftest(eng, voice, args.part_seconds)
        return 0 if rep else (2 if rep is None else 1)
    if args.paragraph_check:
        print("[narrate] sentence-by-sentence against paragraph synthesis, voice %s:" % voice)
        rep = paragraph_check(eng, voice)
        os.makedirs(OUT_TEST, exist_ok=True)
        with open(os.path.join(OUT_TEST, "narrate_paragraph_%s.json" % voice), "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=1)
        return 0
    if args.hear:
        hear(eng, args.hear, args.film)
        return 0
    if not args.film:
        ap.error("give a film (or --voices / --selftest / --paragraph-check / --hear FILE / --make-timed-model)")
    name = N.film_name(args.film)
    norm = N.normalise(N.read_spec(name))
    if args.phonemes:
        for i, line in enumerate(norm["lines"]):
            print("%2d  %s\n    %s" % (i, line["spoken"], eng.phonemes(line["spoken"], args.voice or norm["voice"])))
        return 0
    current = False
    if os.path.exists(N.json_path(name)):
        try:
            N.load(name)
            current = True
        except N.NarrationError as e:
            print("[narrate] %s" % e)
    if args.check:
        print("[narrate] narration of '%s' is %s" % (name, "current" if current else "NOT current"))
        return 0 if current else 1
    if current and not (args.force or args.voice or args.speed):
        print("[narrate] narration of '%s' is current (spec %s): nothing to do (--force speaks it again)" % (name, N.spec_hash(norm)))
        return 0
    narrate(name, eng, voice=args.voice, speed=args.speed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
