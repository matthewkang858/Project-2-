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
    $TTS tools/narrate.py --selftest          # timing accuracy on 44 film-like sentences, on the path a film takes
                                              #   (resumable: run it again until it prints the report; it stops
                                              #   starting work after 230 s; about six runs on a busy machine)
    $TTS tools/narrate.py --paragraph-check   # sentence-by-sentence synthesis against whole-paragraph synthesis
    $TTS tools/narrate.py [<film>] --hear FILE     # recognise the words in any audio / video file; with a film,
                                                   #   locate its script words (independent of narration/*.json);
                                                   #   writes out/test/narrate_heard_<name>.json
    $TTS tools/narrate.py --make-timed-model  # once per machine: write kokoro-v1.0.timed.onnx (needs `pip install onnx`)
  options: --threads N (default 2: what the committed narrations were made with), --recogniser-only (time the
  words WITHOUT the voice model's durations: several frames less exact; without this flag a missing
  kokoro-v1.0.timed.onnx stops the narrator with exit code 1).

The spec is the `NARRATION = {...}` literal of the film module (format: engine/narration.py); it is read with ast,
the film is never imported. Model files are looked for in $MC_TTS_MODELS (default: the session scratchpad, see
MODELS below); tools/setup_tts.sh creates the environment and downloads them.

What it does, in this order
  1. Every sentence is synthesised ON ITS OWN (Kokoro 82M through kokoro-onnx; deterministic: the same sentence,
     voice and speed give the same samples, so changing a pause changes no word; with another --threads value
     0.2 % of the 16-bit samples differ by one step and every word time stays the same). Its leading and trailing
     silence is cut by energy to a fixed margin (20 ms before the first sound, 50 ms after the last, the release
     of a final stop consonant included: sentence_end) with short fades, and the sentences are levelled to one
     speech level.
  2. Loudness: one gain for the whole film to -19 LUFS integrated for the MONO wav (ITU-R BS.1770 as measured by
     ffmpeg's ebur128), then a look-ahead limiter keeps its true peak under -2 dBTP. The film carries it as dual
     mono at full level (engine.post.mux_audio), which measures 3.01 LU more: the delivered mp4 is at -16 LUFS,
     true peak under -1.5 dBTP. Gain and limiter work per sentence, so they do not depend on the pauses either.
  3. The sentences are laid out: `lead` seconds of silence, then each sentence, its first sound exactly `pause`
     seconds after the last sound of the one before, then `tail`; the file is padded to a whole number of frames.
  4. Word timing, per sentence, ON THE CLIP AS THE VOICE SPOKE IT (time_clip), never on the levelled and limited
     clip of step 2: silence is judged against the loudest frame, the voice murmurs in its pauses 41-48 dB under
     it, and once a limiter has lowered the peaks that murmur counts as sound (the first version did this: words
     after a pause were put up to 210 ms early, captions 4 to 6 frames). Three sources, each checking the others:
       model       the voice model's OWN phoneme durations. kokoro-v1.0.timed.onnx is the same network with its
                   duration predictor exposed as a second output (--make-timed-model; the audio is bit-identical),
                   so every phoneme has its span and nothing has to be recognised. A word starts 25 ms before
                   the gap before its first phoneme (measured: that is where its sound begins; MODEL_LEAD).
       energy      measured on the samples: the first and the last sound of the sentence, and every silence of
                   140 ms or more inside it. The word after a pause starts where the sound comes back, IF it is
                   clearly audible (28 dB under the loudest frame) within 60 ms; if not, a murmur or a breath came
                   first and the word starts where the model says, between the two (word_onset).
       recogniser  the second opinion (faster-whisper small.en): the SCRIPT's words force-aligned to the audio by
                   the recogniser's cross-attention; where that gives a word no time, its free transcript aligned
                   to the script by letters (it mishears: 'Crammys' -> 'cram is'). Every word's recogniser start
                   is stored beside the final one ("second"); with --recogniser-only it is the timing. Measured
                   (--selftest): inside running speech the recogniser hears a word start early, while the word
                   before is still sounding; the model does not.
     A word no source can place is spread between its neighbours by syllables and listed as ESTIMATED.
  5. A check on the DELIVERED samples (check_onsets): wherever the finished wav is clearly audible again after
     100 ms of quiet, a word of the json must start there. Printed for every narration, stored as "onset_check";
     a word more than two frames off is listed under CHECK. tools.narration_sync repeats it on the encoded mp4.
  6. narration/<film>.json: sentences (text, start, end), words (script text, caption, start, end, sentence,
     source), voice, speed, sample rate, duration, loudness, the words guarded against a murmur, the onset check
     and the hash of the spec (engine.narration.spec_hash).
  It also prints the film's length against one minute, and a CHECK line with the phonemes of every sentence that
  holds a number, an abbreviation or capitals the phonemiser reads by rules of its own (engine.narration.spoken_risks).

MEASURED (--selftest, am_michael, 44 sentences of the six films' kind, 384 words, spoken as four films of eleven
sentences through the same functions a film goes through; out/test/narrate_selftest_*_report.json)
  * no word had to be estimated; the voice paused 21 times inside a sentence, every time at punctuation. 20 times
    the word after the pause was put on the measured return of the sound, once ('and', after a 100 ms murmur) on
    the model's time
  * THE DELIVERED AUDIO, no word time involved: in the four finished wavs the voice is clearly audible again after
    a silence 65 times, and each time a word of the json starts 0 to 40 ms before that point (median 5 ms): 65 of
    65 within one frame. (The first version, timed on the limited clips, had 4 of 16 such words 165-210 ms early
    on a 75 s probe. The same probe now: 38 of 38 within 45 ms.)
  * timed on the limited delivery clip instead of the spoken one (which films never do), one word of 384 would
    move, by 30 ms: word_onset() alone holds too. At the first version's loudness (up to 14 dB of limiting) 10
    of 569 words move, by 60 ms at most, where they moved by up to 210 ms.
  * the model's phoneme timing against the measured sound after those pauses: median 10 ms, 19 of 20 within a
    frame, 50 ms at most; at the start of a sentence its first phoneme is 45 ms (median) after the first sound,
    which is why the first word starts on the sound
  * the recogniser against the final timing: after pauses the same word on the same onset 20 of 20; inside speech
    median 40 ms apart, 52 % within one frame, 74 % within two, and EARLY on average (-45 ms)
  * the recogniser against ground truth (sentences assembled from pieces whose starts are known to the sample):
    110 ms median error where the pieces butt (8 % within a frame), and 9 of 35 pauses of 250 ms given to the wrong
    word. That is why the recogniser is only the second opinion, and why --recogniser-only must be asked for.
  * cutting the audio at a word's start where the two timings differ by over 100 ms (16 of 65 such words): at the
    final timing the audio before the cut ends with the whole word before in 15 of 16 and both sides are intact in
    13 of 16; at the recogniser's start in 8 and 4 of 16
  * the recogniser run freely over each whole film, against the final timing: median 30 ms, 59 % within one frame,
    82 % within two; its transcript missed or misspelt 13 of 384 words (Crammys, redstoner, Herobrine, trapdoors,
    grown-ups heard as two words; gym, ender not heard): nothing of it is used for the timing of a film
  * loudness of the four films: -19.0 LUFS mono, true peak -2.1 dBTP; the limiter took 3.7 to 8.7 dB off the
    highest peak and more than 3 dB off 0.2 to 4.4 % of the samples (at -16 LUFS mono it was up to 14 dB and 14-27 %)
  * one sentence edited, a pause opened and the lead changed in a film of eleven: no word of the ten other
    sentences moves inside its sentence (0.0000 s); the timing does not depend on the film's gain or limiter
PACE (--voices, speed 1.0; words per second while speaking / with the default 0.35 s pauses / words that fit in 60 s
  with lead 0.3 and tail 1.0, on 12 SHORT sentences of 95 mostly one-syllable words: an upper bound):
    am_michael 3.69 / 3.21 / 188    am_fenrir 4.31 / 3.67 / 215    am_puck  4.32 / 3.68 / 215
    bm_george  3.12 / 2.77 / 162    bm_fable  2.96 / 2.64 / 155    af_heart 4.11 / 3.52 / 206
  Film text is slower. am_michael on the 44 test sentences (8.7 words, 12 syllables a sentence): 3.2 words/s
  while speaking, 2.8-3.0 with the pauses; on a one-minute script of 165 words in 19 sentences with three opened
  pauses: 61.9 s (2.72 words/s); on a reviewer's script of 185 words in 22 sentences with numbers: 75.0 s (2.51).
  PLAN A ONE-MINUTE FILM AT 140 TO 165 WORDS; narrate.py prints the length and, over 62 s, how many words to cut.
  The voice's own pause between two sentences of a paragraph is 0.38-0.54 s (--paragraph-check); the default is 0.35.
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
TAIL_RUN, TAIL_REACH = 0.010, 0.150   # ... except at the END of a sentence: a sound of 10 ms or more within 150 ms
                              #   of the last one is kept. It is the release of a final stop after a long closure
                              #   (measured: the d of 'emerald.' 60 ms after the vowel at -27 dB, the t of 'want?'
                              #   85 ms after at -36 dB, the t of "didn't." 65 ms after; 3 of 66 sentences)
PAUSE_MIN = 0.140             # a silence this long inside a sentence is a pause (a stop consonant closes for less)
CLEAR_DB = -28.0              # a frame within this of the loudest one is CLEARLY audible speech. The voice murmurs in
                              #   its pauses at -41 .. -48 dB (measured on 47 pauses), just under SILENCE_DB, and now
                              #   and then above it: a return of sound counts as the start of a word only when ...
ONSET_REACH = 0.060           # ... it is clearly audible within this time (measured on the same 47 pauses: 0-15 ms
                              #   for 46 of them, up to 55 ms for the h of a sentence that starts with 'He'; the one
                              #   murmur took 105 ms). Otherwise the word starts where the voice model says, kept
                              #   between the first return of the sound and the clearly audible one.
CLEAR_BACK = 0.030            # without a model: such a word starts this long before it is clearly audible
MODEL_LEAD = 0.025            # model timing inside speech: a word starts this much before the gap before its first
                              #   phoneme. Measured: after pauses the sound is back 10 ms (median; mean 18 ms) before
                              #   that gap starts, and audio cut exactly at it still carried the f of 'farm' and the m
                              #   of 'me' on the side of the word before; 25 ms earlier both cuts are clean.
MODEL_REACH = 0.20            # model timing: a word boundary this close to a pause is moved onto it (the model is
                              #   within 35 ms of the measured sound for 19 of 21 pauses, 50 and 120 ms for two)
SNAP_REACH = 0.25             # recogniser timing: the same, wider (its boundaries drift into the silence) ...
PUNCT_REACH = 0.45            # ... and wider still for a boundary the script punctuates: the voice pauses at
                              #   punctuation (21 of 21 pauses inside the test sentences)
PROGRAMME_LUFS = -16.0        # what the delivered film measures: the mp4 carries the narration as dual mono
TARGET_LUFS = PROGRAMME_LUFS - 3.01   # ... so the MONO wav is made 3.01 LU lower (two equal channels add 3.01 LU in
                              #   BS.1770): -19 LUFS. Made at -16 and lowered at the mux, as it first was, the limiter
                              #   had to take 3 dB more off every peak for nothing (measured on a 75 s film: up to
                              #   14 dB, over 3 dB on 14 % of the samples; at -19: up to 9 dB, over 3 dB on 1 %).
MAX_TRUE_PEAK = -2.0          # dBTP of the wav; the AAC encoder moves peaks by a few tenths, the mp4 stays under -1.5
LEVEL_RANGE = 4.0             # dB a sentence may be moved to meet the common speech level
LIMIT_WINDOW = 0.012          # the limiter looks this far ahead and behind (its gain moves over about 24 ms)
MAX_SENTENCE = 27.0           # seconds: one recogniser window
JSON_VERSION = N.JSON_VERSION # (engine.narration refuses a json of another version: its words were timed otherwise)
SELFTEST_VERSION = 3          # of the selftest's cache file
MINUTE = 60.0                 # the films are 'about one minute': the length a narration is reported against
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


def sound_runs(x, sr=SR, rel_db=SILENCE_DB, floor_db=-62.0, min_run=MIN_RUN):
    """Where there is sound: [(t0, t1), ...] in seconds. A frame is sound when its RMS is within `rel_db` of the
    loudest frame (and above `floor_db` dBFS); gaps under MIN_GAP are closed, sounds under `min_run` dropped."""
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
    return [(a, b) for a, b in merged if b - a >= min_run - 1e-9]


def clear_finder(x, sr=SR, clear_db=CLEAR_DB):
    """find(t) -> the time at or after t at which the clip is CLEARLY audible (a 10 ms frame within `clear_db` of
    the loudest one; a frame that began up to 10 ms before t counts as t), or None when it never is again."""
    rms, hop = frame_rms(x, sr)
    if len(rms) == 0 or rms.max() <= 0:
        return lambda t: None
    loud = np.flatnonzero(rms >= rms.max() * 10 ** (clear_db / 20.0)) * hop

    def find(t):
        k = int(np.searchsorted(loud, t - 0.0101))
        return float(max(loud[k], t)) if k < len(loud) else None

    return find


def sentence_end(raw, runs, sr=SR):
    """Where the sound of a synthesised sentence ends: the end of its last sound run, or of a short sound (TAIL_RUN
    or longer) that begins within TAIL_REACH after it: the release of a final stop consonant, which MIN_RUN alone
    would throw away (see TAIL_RUN above)."""
    t1 = runs[-1][1]
    late = [r for r in sound_runs(raw, sr, min_run=TAIL_RUN) if t1 - 1e-6 < r[0] <= t1 + TAIL_REACH]
    return max([t1] + [r[1] for r in late])


def trim_clip(raw, sr=SR):
    """Cut a synthesised sentence to its sound: PRE seconds before the first sound, POST after the last (the
    release of a final consonant included, see sentence_end), faded in and out. Returns (clip, onset, offset,
    shift): the sound runs from `onset` to `offset` seconds inside the clip, and a time t of the raw audio is
    t - shift in the clip."""
    runs = sound_runs(raw, sr)
    if not runs:
        raise ValueError("the voice produced silence")
    t0, t1 = runs[0][0], sentence_end(raw, runs, sr)
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


def word_onset(lo, clear, anchor):
    """Where a word starts whose sound returns at `lo` after a silence: (start, measured, guarded).
    `clear` = clear_finder() of the audio, `anchor` = the voice model's start of that word or None.
    The sound is clearly audible within ONSET_REACH: the word starts where the sound returns (measured). If it is
    not, something quiet came first (the voice murmurs in its pauses, and such a murmur would put the caption 4 to
    6 frames early): the word starts where the model says, but not before the sound returns nor after it is
    clearly audible; without a model, CLEAR_BACK before it is clearly audible. guarded = the second case."""
    hi = clear(lo) if clear is not None else None
    if hi is None or hi - lo <= ONSET_REACH:
        return lo, True, False
    if anchor is None:
        return hi - CLEAR_BACK, True, True
    start = min(hi, max(lo, anchor))
    return start, start in (lo, hi), True


def snap_to_sound(times, runs, reach=SNAP_REACH, punctuated=(), punct_reach=PUNCT_REACH, pause_min=PAUSE_MIN,
                  clear=None, anchors=None, end=None):
    """Fit word times to the measured sound of the same audio. `times` = [[start, end], ...] (seconds, in order),
    `runs` = sound_runs() of it. The first word starts with the first sound and the last ends with the last (or at
    `end`); every silence of `pause_min` or more is given to a word boundary: the nearest one the script punctuates
    (indices of the words BEFORE such a boundary in `punctuated`) within `punct_reach`, else the nearest one within
    `reach`. The word before the pause ends where the silence starts, the word after starts where the sound comes
    back, as word_onset() judges it with `clear` (clear_finder() of the audio) and `anchors` (each word's start
    by the voice model, or None). Elsewhere a word ends where the next one starts. Returns (new times, indices of
    the words that START on a measured onset, [(pause start, pause end, index of the word before it or None), ...],
    {index: (first return of the sound, clearly audible, start used)} of the words word_onset() guarded)."""
    t = [[float(a), float(b)] for a, b in times]
    n = len(t)
    if n == 0 or not runs:
        return t, [], [], {}
    on_sound, guarded = [], {}

    def start_at(i, lo):
        start, measured, guard = word_onset(lo, clear, None if anchors is None else anchors[i])
        t[i][0] = start
        if measured:
            on_sound.append(i)
        if guard:
            guarded[i] = (round(lo, 4), round(clear(lo), 4), round(start, 4))

    start_at(0, runs[0][0])
    t[-1][1] = runs[-1][1] if end is None else float(end)
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
        start_at(i + 1, g1)
    for i in range(n - 1):                                           # contiguous inside a run of sound
        if i not in taken:
            t[i][1] = t[i + 1][0]
    return t, sorted(on_sound), report, guarded


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
    snapped, on_sound, _pauses, guarded = snap_to_sound(times, runs, punctuated=punctuated_words(words),
                                                        clear=clear_finder(clip, sr), end=offset)
    fixed, spread = repair(snapped, words, onset, offset)
    out = []
    for i in range(n):
        est = i in spread
        rec = None
        if heard_times is not None:
            rec = {"start": round(heard_times[i][0], 4), "end": round(heard_times[i][1], 4), "kind": heard_times[i][2]}
        out.append({"start": fixed[i][0], "end": fixed[i][1], "estimated": est,
                    "source": "estimated" if est else ("energy" if i in on_sound else source[i]),
                    "raw_forced": round(forced[i][0], 4), "p": round(forced[i][2], 3), "recognised": rec,
                    "guarded": guarded.get(i)})
    return out


def time_sentence(eng, clip, words, onset, offset, model=None, second_opinion=True, sr=SR):
    """Start and end of every script word of one sentence clip (seconds inside the clip).
    `clip` must be the sentence AS SPOKEN (speak_sentence()'s 'spoken'), never the levelled and limited delivery
    clip: silence is judged against the clip's loudest frame, and a limiter that lowers the peaks lifts the voice's
    murmur in the pauses over that threshold (time_clip() is the call a film's narration goes through).
    `model` = words_from_timings() of the clip (already in clip time) or None. With it the model's durations are
    the timing, fitted to the measured sound, and the recogniser is the second opinion; without it the recogniser
    is the timing. Returns dicts {start, end, source ('model' | 'energy' = starts on a measured onset | 'forced' |
    'recognised' | 'estimated'), estimated, model_raw, second, second_source, guarded, pauses}."""
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
    anchors = [None if i in missing else times[i][0] for i in range(n)]
    snapped, on_sound, pauses, guarded = snap_to_sound(times, runs, reach=MODEL_REACH, punctuated=punctuated_words(words),
                                                       clear=clear_finder(clip, sr), anchors=anchors, end=offset)
    fixed, spread = repair(snapped, words, onset, offset)
    out = []
    for i in range(n):
        est = i in spread or i in missing
        out.append({"start": fixed[i][0], "end": fixed[i][1], "estimated": est,
                    "source": "estimated" if est else ("energy" if i in on_sound else "model"),
                    "model_raw": None if model[i] is None else round(model[i][0], 4),
                    "second": None if second is None else second[i]["start"],
                    "second_source": None if second is None else second[i]["source"],
                    "raw_forced": None if second is None else second[i]["raw_forced"],
                    "guarded": guarded.get(i)})
    if out:
        out[0]["pauses"] = [(round(g0, 4), round(g1, 4), b) for g0, g1, b in pauses]
    return out


def time_clip(eng, c, words, second_opinion=True):
    """Word times of one synthesised sentence `c` (a speak_sentence() dict, before or after synthesise()): always
    measured on the clip as it was spoken. narrate(), --selftest and --paragraph-check all time through here."""
    return time_sentence(eng, c["spoken"], words, c["onset"], c["offset"], model=c["model"], second_opinion=second_opinion)


# ---------------------------------------------------------------------------------------------------------------
# a film's narration
# ---------------------------------------------------------------------------------------------------------------

def speak_sentence(eng, text, spoken, voice, speed):
    """One sentence, spoken and cut to its sound: {'spoken' (the samples as the voice made them: what the words
    are TIMED on), 'clip' (the same until synthesise() levels and limits it: what is DELIVERED), 'onset', 'offset'
    (first and last sound, seconds inside either), 'model' (word times from the voice model in clip time, or
    None), 'raw_level'}. Gain and limiter move no sample in time, so times measured on 'spoken' hold for 'clip'."""
    raw, timings = eng.speak(spoken, voice, speed)
    clip, onset, offset, shift = trim_clip(raw)
    model = None
    if timings is not None:
        words = words_from_timings(timings, N.words_of(spoken), lambda w: eng.word_phonemes(w, voice))
        if len(words) == len(N.words_of(text)):
            model = [None if w is None else (w[0] - shift, w[1] - shift) for w in words]
    return {"spoken": clip, "clip": clip, "onset": onset, "offset": offset, "model": model,
            "raw_level": speech_level(clip)}


def synthesise(eng, norm, log=print):
    """Speak every sentence of a normalised spec: a list of speak_sentence() dicts whose 'clip' is levelled and
    limited to the delivery loudness (independently of the pauses) while 'spoken' stays as the voice made it,
    and the loudness report."""
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
    report = {"target_lufs": round(TARGET_LUFS, 2), "programme_target_lufs": PROGRAMME_LUFS,
              "max_true_peak_db": MAX_TRUE_PEAK, "before_lufs": round(lufs0, 2), "before_true_peak_db": round(tp0, 2),
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


def clear_onsets(audio, sr=SR, quiet=0.100, clear_db=CLEAR_DB):
    """Every time the voice comes back CLEARLY in a finished audio file: the start of each 10 ms frame within
    `clear_db` of the file's loudest frame that follows at least `quiet` seconds without such a frame (the file's
    beginning counts as quiet). No model, no recogniser and none of the narrator's word times are involved: this
    is what the json's word starts are checked against, in the delivered wav and in the encoded mp4."""
    rms, hop = frame_rms(audio, sr)
    if len(rms) == 0 or rms.max() <= 0:
        return np.zeros(0)
    loud = np.flatnonzero(rms >= rms.max() * 10 ** (clear_db / 20.0)) * hop
    if len(loud) == 0:
        return loud
    first = np.concatenate([[True], np.diff(loud) >= quiet])
    return loud[first]


def after_silence(words, quiet=0.100):
    """Indices of the words (dicts or objects with start / end) that start after `quiet` seconds or more without a
    word: the first word, the first word of every sentence, every word after a pause inside a sentence."""
    get = (lambda w, k: w[k]) if words and isinstance(words[0], dict) else getattr
    return [i for i, w in enumerate(words) if i == 0 or get(w, "start") - get(words[i - 1], "end") >= quiet - 1e-6]


def check_onsets(words, audio, sr=SR, quiet=0.100):
    """The word starts of a narration against its delivered audio: for every word that starts after a silence, how
    long after its `start` the voice is clearly audible (clear_onsets; the nearest one from 250 ms before to 450 ms
    after). Returns {'words', 'median_ms', 'min_ms', 'max_ms', 'within_1_frame', 'within_2_frames', 'not_found',
    'rows': [(word index, text, start, clearly audible or None)], 'far': rows more than 2 frames off}."""
    on = clear_onsets(audio, sr, quiet)
    get = (lambda w, k: w[k]) if words and isinstance(words[0], dict) else getattr
    rows = []
    for i in after_silence(words, quiet):
        t = get(words[i], "start")
        near = on[(on >= t - 0.25) & (on <= t + 0.45)]
        rows.append((i, get(words[i], "text"), round(float(t), 4),
                     round(float(near[np.argmin(np.abs(near - t))]), 4) if len(near) else None))
    d = np.array([r[3] - r[2] for r in rows if r[3] is not None]) * 1000.0
    out = {"words": len(rows), "not_found": sum(r[3] is None for r in rows), "rows": rows,
           "far": [r for r in rows if r[3] is not None and abs(r[3] - r[2]) > 2 * FRAME + 1e-6]}
    if len(d):
        out.update(median_ms=round(float(np.median(d)), 1), min_ms=round(float(d.min()), 1), max_ms=round(float(d.max()), 1),
                   within_1_frame=int(np.sum(np.abs(d) <= 1000 * FRAME + 1e-6)),
                   within_2_frames=int(np.sum(np.abs(d) <= 2000 * FRAME + 1e-6)))
    return out


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
    if eng.want_timed and not eng.timed:
        # (refused, not warned about: timed by the recogniser alone, words inside speech start about 115 ms early
        # and one pause in four goes to the wrong word, and nothing downstream would show it)
        raise SystemExit("[narrate] %s is missing in %s: the words cannot be timed from the voice model.\n"
                         "          Make it once with  $TTS tools/narrate.py --make-timed-model  (needs `pip install onnx`; "
                         "tools/setup_tts.sh does both),\n          or pass --recogniser-only to time the words with "
                         "the recogniser alone (several frames less exact)." % (KOKORO_TIMED, MODELS))
    log("[narrate] %s: %d sentences, voice %s, speed %s" % (name, len(norm["lines"]), norm["voice"], norm["speed"]))
    for i, line in enumerate(norm["lines"]):
        risky = N.spoken_risks(line["text"])
        if risky:
            log("[narrate]   CHECK how sentence %d is said (%s): %s\n[narrate]       %s\n[narrate]       write it in "
                "words, or respell it with \"say\", if that is not what you mean"
                % (i, ", ".join("%r is %s" % r for r in risky), line["spoken"], eng.phonemes(line["spoken"], norm["voice"])))
    t_start = time.time()
    clips, loud = synthesise(eng, norm, log)
    if not eng.timed:
        log("[narrate]   WARNING: --recogniser-only: the words are timed by the recogniser alone (measured: about "
            "115 ms early inside speech, one pause in four given to the wrong word)")
    audio, spans, duration = layout(norm, clips)
    words, sentences, estimated, guarded = [], [], [], []
    for i, (line, c, (s0, s1)) in enumerate(zip(norm["lines"], clips, spans)):
        script = N.words_of(line["text"])
        if eng.timed and c["model"] is None:
            log("[narrate]   sentence %d: the voice was given %d words for %d script words (a respelling in 'say' "
                "must stay one word): timed by the recogniser" % (i, len(N.words_of(line["spoken"])), len(script)))
        timed = time_clip(eng, c, script, second_opinion=second_opinion)     # on the clip AS SPOKEN, never the limited one
        first = len(words)
        for text, caption, tw in zip(script, N.caption_forms(script), timed):
            entry = {"text": text, "caption": caption,
                     "start": round(s0 + tw["start"] - c["onset"], 4), "end": round(s0 + tw["end"] - c["onset"], 4),
                     "sentence": i, "source": tw["source"], "estimated": tw["estimated"]}
            if tw.get("second") is not None:                         # the recogniser's start, for the record
                entry["second"] = round(s0 + tw["second"] - c["onset"], 4)
                entry["second_source"] = tw["second_source"]
            if tw["estimated"]:
                estimated.append(len(words))
            if tw.get("guarded"):
                lo, hi, used = (round(s0 + v - c["onset"], 4) for v in tw["guarded"])
                guarded.append({"word": len(words), "text": text, "sound_returns": lo, "clearly_audible": hi, "start": used})
            words.append(entry)
        sentences.append({"index": i, "id": line["id"], "text": line["text"], "spoken": line["spoken"],
                          "start": round(s0, 4), "end": round(s1, 4), "pause_after": line["pause"],
                          "speed": line["speed"], "first_word": first, "last_word": len(words) - 1})
    for a, b in zip(words, words[1:]):                               # rounding must not break the order
        if b["start"] < a["end"]:
            b["start"] = a["end"]
    lufs, tp = loudness(audio)
    loud.update(integrated_lufs=round(lufs, 2), true_peak_db=round(tp, 2), programme_lufs=round(lufs + 3.01, 2))
    if tp > MAX_TRUE_PEAK or abs(lufs - TARGET_LUFS) > 0.6:
        log("[narrate]   WARNING: the file measures %.2f LUFS, true peak %.2f dBTP (wanted %.1f +- 0.6, under %.1f)"
            % (lufs, tp, TARGET_LUFS, MAX_TRUE_PEAK))
    # the word starts against the DELIVERED samples: where the voice is clearly audible after every silence
    check = check_onsets(words, audio)
    if audition:
        wav = os.path.join(OUT_TEST, "narrate_%s_%s%s.wav" % (name, norm["voice"], "" if not speed else "_x%s" % speed))
    else:
        wav = N.wav_path(name)
    write_wav(wav, audio)
    speech = sum(s1 - s0 for s0, s1 in spans)
    overall = len(words) / max(spans[-1][1] - spans[0][0], 1e-6)
    data = {
        "film": name, "json_version": JSON_VERSION, "spec_hash": N.spec_hash(norm), "spec": norm,
        "voice": norm["voice"], "lang": eng.lang(norm["voice"]), "speed": norm["speed"],
        "sample_rate": SR, "channels": 1, "fps": norm["fps"],
        "duration": round(duration, 6), "frames": int(round(duration * norm["fps"])),
        "lead": norm["lead"], "tail": round(duration - spans[-1][1], 4),
        "speech_seconds": round(speech, 3), "words_per_second_speaking": round(len(words) / speech, 3),
        "words_per_second_overall": round(overall, 3),
        "timing": "model" if eng.timed else "recogniser",
        "loudness": loud, "wav": os.path.basename(wav), "wav_sha1": N.file_sha1(wav),
        "sentences": sentences, "words": words, "estimated_words": estimated, "guarded_words": guarded,
        "onset_check": {k: v for k, v in check.items() if k != "rows"}, "tools": eng.versions(),
    }
    js = wav[:-4] + ".json"
    tmp = js + ".part"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, js)
    bad = [c for c in (w["caption"] for w in words) if any(ord(ch) > 126 or ord(ch) < 32 for ch in c)]
    log("[narrate] %s: %.2f s (%d frames at %d fps), %d words, %.2f words/s while speaking, %.2f overall; "
        "wav %.1f LUFS mono = %.1f LUFS as the film's dual mono, true peak %.1f dBTP (limiter took up to %.1f dB, "
        "over 3 dB on %.1f %% of the samples); timing by %s, %d words estimated%s; %.0f s"
        % (name, duration, data["frames"], norm["fps"], len(words), data["words_per_second_speaking"],
           overall, lufs, lufs + 3.01, tp, loud["max_gain_reduction_db"], 100 * loud["share_limited_over_3db"],
           data["timing"], len(estimated),
           (": " + ", ".join("%d %r" % (k, words[k]["text"]) for k in estimated)) if estimated else "",
           time.time() - t_start))
    # the length against one minute: what the words cost in frames to render
    room = MINUTE - norm["lead"] - norm["tail"]
    fit = int(room * overall)
    if duration > MINUTE + 2.0:
        log("[narrate]   LENGTH: %.1f s is %.1f s over one minute (%d more frames to render). At this pace (%.2f "
            "words/s with the pauses) one minute holds about %d words: this script has %d, cut about %d words or "
            "shorten pauses" % (duration, duration - MINUTE, int(round((duration - MINUTE) * norm["fps"])), overall,
                                fit, len(words), len(words) - fit))
    else:
        log("[narrate]   length: %.1f s; at this pace (%.2f words/s with the pauses) one minute holds about %d words"
            % (duration, overall, fit))
    if guarded:
        log("[narrate]   %d word(s) start where the voice model says, because the first sound after the pause was not "
            "clearly a word within %d ms (a murmur or a breath): %s"
            % (len(guarded), round(1000 * ONSET_REACH),
               ", ".join("%r at %.3f s (sound from %.3f, clear at %.3f)" % (g["text"], g["start"], g["sound_returns"],
                                                                            g["clearly_audible"]) for g in guarded)))
    if check.get("median_ms") is not None:
        log("[narrate]   delivered audio: %d words start after a silence; the voice is clearly audible (%d dB under the "
            "loudest frame) %.0f ms after the json's start in the median, %.0f .. %.0f ms; %d within one frame, %d "
            "within two%s" % (check["words"], round(CLEAR_DB), check["median_ms"], check["min_ms"], check["max_ms"],
                              check["within_1_frame"], check["within_2_frames"],
                              "" if not check["not_found"] else "; %d not found" % check["not_found"]))
    if check["far"] or check["not_found"]:
        log("[narrate]   CHECK these word starts by ear or on a spectrogram, the delivered audio disagrees by more "
            "than two frames: " + ", ".join("%r json %.3f s, clearly audible %s" % (r[1], r[2], "%.3f s" % r[3] if r[3] is not None else "nowhere near")
                                            for r in check["far"] + [r for r in check["rows"] if r[3] is None]))
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
    timed = time_clip(eng, whole, words, second_opinion=whole["model"] is None)
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
    """Timing accuracy on TEST_SENTENCES, measured ON THE PATH A FILM TAKES, cached step by step
    (out/test/narrate_selftest_<voice>.json), so the command can be run again until everything is done.
      F  the film path. The sentences are spoken as four films of eleven: synthesise() (levelled and limited
         together to the delivery loudness), layout(), every word timed by time_clip(), exactly as narrate() does.
         Then two checks no word time of the narrator enters: in the DELIVERED samples of each film, where the
         voice is clearly audible after every silence (check_onsets) against the word that starts there; and the
         same sentences timed on the limited delivery clip instead of the spoken one (what the narrator first did,
         putting words on the murmur of the pauses): the difference must stay small now that word_onset() guards.
      A  the voice model's phoneme timing against the SOUND, on those films: after every pause (and at the
         sentence start) the first sound is measured on the samples. Then the final timing (model + energy)
         against the recogniser's (forced alignment + energy), word by word.
      B  ground truth for the recogniser: the sentence synthesised in pieces of 2-4 words, each cut to its exact
         first and last sound and joined, alternately with NO gap and with a 250 ms gap. Every piece start is
         known to the sample; the recogniser timing must find the first word of each piece there.
      C  the recogniser run freely over each whole delivered film, its words matched to the script by letters,
         against the final timing.
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
    if cache.get("version") != SELFTEST_VERSION:
        cache = {"version": SELFTEST_VERSION}
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

    def out_of_time():
        return time.time() - t0 > part_seconds

    # ---- F: the four films, through synthesise() / layout() / time_clip()
    group = 11
    n_films = math.ceil(len(TEST_SENTENCES) / group)
    for g in range(n_films):
        key = "film%d" % g
        sents = TEST_SENTENCES[g * group:(g + 1) * group]
        if key in cache and cache[key].get("texts") == sents:
            continue
        if out_of_time():
            break
        norm = N.normalise({"voice": voice, "lines": sents})
        clips, loud = synthesise(eng, norm, log=lambda *_: None)
        audio, spans, _dur = layout(norm, clips)
        film_words, per = [], []
        for s, c, (s0, _s1) in zip(sents, clips, spans):
            words = N.words_of(s)
            final = time_clip(eng, c, words, second_opinion=False)
            # the same sentence timed on the limited delivery clip: NOT the film path, the robustness check
            limited = time_sentence(eng, c["clip"], words, c["onset"], c["offset"], model=c["model"], second_opinion=False)
            per.append({"text": s, "words": words, "span_start": round(s0, 4),
                        "final": [round(w["start"], 4) for w in final], "end": [round(w["end"], 4) for w in final],
                        "source": [w["source"] for w in final], "model_raw": [w["model_raw"] for w in final],
                        "estimated": [i for i, w in enumerate(final) if w["estimated"]],
                        "guarded": {str(i): w["guarded"] for i, w in enumerate(final) if w.get("guarded")},
                        "pauses": final[0].get("pauses", []), "punctuated": punctuated_words(words),
                        "onset": round(c["onset"], 4), "offset": round(c["offset"], 4),
                        "on_limited_clip": [round(w["start"], 4) for w in limited],
                        "runs_spoken": len(sound_runs(c["spoken"])), "runs_limited": len(sound_runs(c["clip"]))})
            film_words += [{"text": t, "start": s0 + w["start"] - c["onset"], "end": s0 + w["end"] - c["onset"]}
                           for t, w in zip(words, final)]
        check = check_onsets(film_words, audio)
        lufs, tp = loudness(audio)
        wav = os.path.join(OUT_TEST, "narrate_selftest_%s_film%d.wav" % (voice, g))
        write_wav(wav, audio)
        cache[key] = {"texts": sents, "sentences": per, "wav": os.path.basename(wav),
                      "starts": [round(w["start"], 4) for w in film_words],
                      "loudness": dict(loud, integrated_lufs=round(lufs, 2), true_peak_db=round(tp, 2)),
                      "onset_check": check}
        save()
        log("  film %d/%d  %5.1f s  %d sentences, %.1f LUFS, limiter up to %.1f dB" % (g + 1, n_films, time.time() - t0, len(sents), lufs, loud["max_gain_reduction_db"]))
    films = [cache.get("film%d" % g) for g in range(n_films)]
    films = [f for f in films if f]
    finals = [d for f in films for d in f["sentences"]]             # one record per sentence, in order

    # ---- A (recogniser part) and B, per sentence
    if len(films) == n_films:
        for idx, (s, cuts) in enumerate(zip(TEST_SENTENCES, plans)):
            key = "s%02d" % idx
            if key in cache and cache[key].get("text") == s:
                continue
            if out_of_time():
                break
            words = N.words_of(s)
            rec = {"text": s, "words": words}
            c = speak_sentence(eng, s, N.spoken_text(s), voice, 1.0)        # the same samples as in the film (deterministic)
            recog = time_by_recogniser(eng, c["spoken"], words, c["onset"], c["offset"], free=True)
            rec["R"] = {"recogniser": [round(w["start"], 4) for w in recog], "recogniser_source": [w["source"] for w in recog],
                        "raw_forced": [w["raw_forced"] for w in recog], "kind": [w["recognised"]["kind"] for w in recog]}
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

    # ---- C: the recogniser, freely, over each delivered film
    if len(films) == n_films and len(done) == len(TEST_SENTENCES):
        for g, f in enumerate(films):
            key = "whole%d" % g
            if key in cache:
                continue
            if out_of_time():
                break
            audio = read_audio(os.path.join(OUT_TEST, f["wav"]), SR)
            words = [w for d in f["sentences"] for w in d["words"]]
            heard = eng.recognise(resample(audio, SR, 16000))
            runs = sound_runs(audio, rel_db=CLEAR_DB)
            ht = from_recognition(words, heard, runs[0][0], runs[-1][1])
            snapped, _on, _p, _g = snap_to_sound([[a, b] for a, b, _k in ht], runs, punctuated=punctuated_words(words))
            cache[key] = {"whole_file": [round(a, 4) for a, _b in snapped],
                          "whole_file_raw": [round(a, 4) for a, _b, _k in ht], "kind": [k for _a, _b, k in ht],
                          "heard": " ".join(h[0] for h in heard), "script": " ".join(words)}
            save()
            log("  whole film %d/%d  %5.1f s" % (g + 1, n_films, time.time() - t0))
    wholes = [cache[k] for k in ("whole%d" % g for g in range(n_films)) if k in cache]

    # ---- E: who is right where the two timings disagree inside speech? Cut the sentence at each of the two
    # starts of such a word and let the recogniser say what it hears on either side: with the cut in the right
    # place the audio before it ends with the whole word before, and the audio after it begins with the word.
    gating_done = False
    if len(films) == n_films and len(done) == len(TEST_SENTENCES) and len(wholes) == n_films:
        disputed = [(idx, i) for idx, (d, fd) in enumerate(zip(done, finals)) for i in range(1, len(d["words"]))
                    if fd["source"][i] == "model" and abs(d["R"]["recogniser"][i] - fd["final"][i]) > 0.10]
        pick = disputed[::max(1, len(disputed) // 16)][:16]
        gate = cache.setdefault("gating", {"disputed": len(disputed), "cuts": {}})
        gate["disputed"] = len(disputed)
        for idx, i in pick:
            key = "%d:%d" % (idx, i)
            if key in gate["cuts"]:
                continue
            if out_of_time():
                break
            d, fd = done[idx], finals[idx]
            c = speak_sentence(eng, d["text"], N.spoken_text(d["text"]), voice, 1.0)
            res = {"word": d["words"][i], "before": d["words"][i - 1],
                   "difference_ms": round(1000 * (d["R"]["recogniser"][i] - fd["final"][i]))}
            for name, t in (("model", fd["final"][i]), ("recogniser", d["R"]["recogniser"][i])):
                k = int(round(t * SR))
                nf = int(0.004 * SR)
                a, b = np.array(c["spoken"][:k]), np.array(c["spoken"][k:])
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
        gating_done = all("%d:%d" % k in gate["cuts"] for k in pick)
    if len(films) < n_films or len(done) < len(TEST_SENTENCES) or len(wholes) < n_films or not gating_done:
        log("[narrate] selftest: %d of %d films, %d of %d sentences, %d of %d whole-film recognitions, cuts %s; "
            "run the same command again to continue"
            % (len(films), n_films, len(done), len(TEST_SENTENCES), len(wholes), n_films, "done" if gating_done else "not done"))
        return None

    # ---- report
    n_words = sum(len(d["words"]) for d in done)
    estimated, kinds, misheard, guarded = 0, {}, [], []
    onset_model, onset_forced, a_all, a_mid, a_onset, first_model = [], [], [], [], [], []
    pauses_total, pauses_punct, pauses_unassigned = 0, 0, 0
    moved, runs_changed, after_pause = [], 0, 0
    for d, fd in zip(done, finals):
        R = d["R"]
        estimated += len(fd["estimated"])
        runs_changed += fd["runs_spoken"] != fd["runs_limited"]
        for i, g in fd["guarded"].items():
            guarded.append("%s (sound from %.3f, clear at %.3f, starts %.3f) in %r" % (d["words"][int(i)], g[0], g[1], g[2], d["text"][:32]))
        for _g0, _g1, b in fd["pauses"]:
            pauses_total += 1
            pauses_unassigned += b is None
            pauses_punct += b is not None and b in fd["punctuated"]
        for i, w in enumerate(d["words"]):
            kinds[R["kind"][i]] = kinds.get(R["kind"][i], 0) + 1
            if R["kind"][i] != "exact":
                misheard.append("%s (%s)" % (N.caption_form(w), R["kind"][i]))
            a_all.append(R["recogniser"][i] - fd["final"][i])
            if abs(fd["on_limited_clip"][i] - fd["final"][i]) > 0.020:
                moved.append("%s %+d ms" % (N.caption_form(w), round(1000 * (fd["on_limited_clip"][i] - fd["final"][i]))))
            if i == 0:                                               # the sentence start: nothing precedes it, the
                if fd["model_raw"][i] is not None:                   # model's first phoneme against the first sound
                    first_model.append(fd["model_raw"][i] - fd["final"][i])
            elif fd["source"][i] == "energy":                        # final[i] IS the measured onset of the sound
                after_pause += 1
                if fd["model_raw"][i] is not None:
                    onset_model.append(fd["model_raw"][i] - fd["final"][i])
                onset_forced.append(R["raw_forced"][i] - fd["final"][i])
                a_onset.append(R["recogniser"][i] - fd["final"][i])
            else:
                a_mid.append(R["recogniser"][i] - fd["final"][i])
    b_butt, b_gap, b_raw_butt, b_raw_gap = [], [], [], []
    for d in done:
        B = d["B"]
        for p in range(1, len(B["truth"])):
            e, r = B["recogniser"][p] - B["truth"][p], B["raw_forced"][p] - B["truth"][p]
            (b_gap if B["gap"][p] > 0 else b_butt).append(e)
            (b_raw_gap if B["gap"][p] > 0 else b_raw_butt).append(r)
    c_diff, c_raw, c_kinds = [], [], {}
    for f, w in zip(films, wholes):
        c_diff += [x - p for x, p in zip(w["whole_file"], f["starts"])]
        c_raw += [x - p for x, p in zip(w["whole_file_raw"], f["starts"])]
        for k in w["kind"]:
            c_kinds[k] = c_kinds.get(k, 0) + 1
    # the delivered audio of the four films: json start -> clearly audible, for every word after a silence
    rows = [r for f in films for r in f["onset_check"]["rows"]]
    found = np.array([r[3] - r[2] for r in rows if r[3] is not None])
    delivered = {"words_after_a_silence": len(rows), "not_found": sum(r[3] is None for r in rows)}
    if len(found):
        delivered.update(clearly_audible_after_json_start_ms={"median": round(1000 * float(np.median(found)), 1),
                                                              "min": round(1000 * float(found.min()), 1),
                                                              "max": round(1000 * float(found.max()), 1)},
                         within_1_frame=int(np.sum(np.abs(found) <= FRAME + 1e-6)),
                         within_2_frames=int(np.sum(np.abs(found) <= 2 * FRAME + 1e-6)),
                         more_than_2_frames=["%s json %.3f, audible %.3f" % (r[1], r[2], r[3]) for r in rows
                                             if r[3] is not None and abs(r[3] - r[2]) > 2 * FRAME + 1e-6])
    report = {
        "voice": voice, "sentences": len(done), "words": n_words, "estimated_words_in_final_timing": estimated,
        "F_films": [{"sentences": len(f["texts"]), "integrated_lufs": f["loudness"]["integrated_lufs"],
                     "true_peak_db": f["loudness"]["true_peak_db"], "limiter_max_db": f["loudness"]["max_gain_reduction_db"],
                     "limited_over_1db": f["loudness"]["share_limited_over_1db"],
                     "limited_over_3db": f["loudness"]["share_limited_over_3db"]} for f in films],
        "F_delivered_audio_word_starts_vs_clearly_audible": delivered,
        "F_words_guarded_against_a_murmur": guarded,
        "F_if_timed_on_the_limited_clip": {"sentences_whose_sound_runs_differ": runs_changed,
                                           "word_starts_that_would_move_over_20ms": moved},
        "pauses_inside_sentences": {"found": pauses_total, "at_punctuation": pauses_punct, "given_to_no_word": pauses_unassigned,
                                    "words_started_on_the_measured_sound": after_pause},
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
          and delivered["not_found"] == 0 and not delivered.get("more_than_2_frames")
          and report["E_cut_at_model_start"]["both"] >= report["E_cut_at_recogniser_start"]["both"])
    log("[narrate] selftest %s" % ("passed" if ok else "FAILED its limits (no estimated word; every pause inside a "
        "sentence given to a word; the model's own timing within two frames of the measured sound for 90 % of the "
        "words after a pause; in the delivered audio every word after a silence within two frames of where the "
        "voice is clearly audible; cutting at the model's word starts leaves at least as many words whole as "
        "cutting at the recogniser's)"))
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
        # (a finished file is levelled and limited: its silences are judged at CLEAR_DB, where the voice is clearly
        #  audible, not at SILENCE_DB, which the murmur in its pauses can reach once the peaks are lower)
        runs = sound_runs(audio, rel_db=CLEAR_DB)
        lo, hi = (runs[0][0], runs[-1][1]) if runs else (0.0, len(audio) / SR)
        ht = from_recognition(words, heard, lo, hi)
        snapped, on_sound, _p, _g = snap_to_sound([[a, b] for a, b, _k in ht], runs, punctuated=punctuated_words(words))
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
