"""Narration: the narrator's voice track and the clock of a narrated film (pure Python: no Blender, no TTS).

A narrated film is planned from the VOICE outward. The film module holds the text as a plain literal, a separate
command (another Python environment: the voice model cannot live beside bpy) speaks it and measures when every
word starts, and the film reads those times back for its captions, its cuts and its length:

    films/<film>.py        NARRATION = {...}                       the text (below)
    $TTS tools/narrate.py <film>                                   -> narration/<film>.wav + narration/<film>.json
    nar = narration.load(__name__, NARRATION)                      in build(): fails loudly when the json is stale
    $BPY -m render <film> --frames all ... --encode                the wav is muxed automatically (render.py)

THE SPEC (a literal: tools/narrate.py reads it with `ast`, it never imports the film, so no bpy is needed)

    NARRATION = {
        "voice": "am_michael",        # optional (DEFAULT_VOICE); British voices (bm_*, bf_*) are spoken as en-gb
        "speed": 1.0,                 # optional, the whole film (0.5 .. 2.0)
        "lead": 0.3,                  # seconds of silence before the first word            (default 0.3)
        "tail": 1.0,                  # seconds the film runs on after the last word        (default 1.0)
        "pause": 0.35,                # silence between two sentences, voice to voice       (default 0.35)
        "say": {"Crammys": "crammies"},      # optional: how the VOICE says a word; the caption keeps the script.
                                             #   One word for one word (hyphenate: "red-stoner"). SAY below is
                                             #   always applied (redstoner, Herobrine, netherite); check a new
                                             #   word with `tools/narrate.py <film> --phonemes` before speaking.
        "lines": [
            "In this town, everyone is musical.",                        # a sentence; default pause after it
            ("Except me.", 0.9),                                         # (sentence, pause after it in seconds)
            {"text": "Today is the Crammys.", "pause": 0.5, "speed": 0.95, "id": "party"},
        ],
    }
  One entry of "lines" is one SENTENCE: it is spoken on its own and joined with exactly the pause you give, so a
  pause can be opened up for a picture without one sample of the voice changing (measured: bit-identical). Cuts
  belong on sentence starts. Changing anything that is spoken or timed makes the json stale; `load` then raises.
  A word's `start` is the first sound of the word: the voice model's own phoneme timing, and after a silence the
  measured onset of the sound (tools/narrate.py explains and measures it). A pause is measured sound to sound.

WRITING FOR THE VOICE
  * LENGTH. am_michael speaks film sentences at 2.9-3.3 words a second and, with the pauses, gets through
    2.5-3.0 words per second of film: ONE MINUTE HOLDS 140 TO 165 WORDS (measured: 165 words in 19 sentences
    with three opened pauses = 61.9 s; a reviewer's script of 185 words in 22 sentences with numbers = 75 s;
    44 test sentences = 166 words a minute). Fewer with numbers, long words or opened pauses. Every word over
    the budget costs about 9 frames of rendering. tools/narrate.py prints the length against one minute and,
    over 62 s, how many words to cut.
  * NUMBERS, TIMES, ABBREVIATIONS: write them as words. The phonemiser reads '14:07' as "fourteen <pause> zero
    seven", 'III' as "roman three" and makes a full stop of 'Mr.'. A plain number in digits ('12', '100%') is
    said correctly, and the caption shows the digits. Capitals without a vowel ('XP', 'TNT') are spelt out; to
    have such a word said otherwise, respell it in "say". tools/narrate.py prints a CHECK line with the phonemes
    of every sentence that holds such a word (spoken_risks); `--phonemes` prints them for the whole script.
  * QUOTATIONS: double or single quotes never reach the caption ('Not again!' shows Not / again).

PUBLIC API
    load(film, spec=None, fps=24) -> Narration     read narration/<film>.json and CHECK it against the film's text
                                                   (and against JSON_VERSION: a json written by an older narrator
                                                   is stale too, its words were timed differently)
    read_spec(film) -> dict                        the NARRATION literal of films/<film>.py, read without importing
    normalise(spec) -> dict, spec_hash(spec) -> str    canonical form of a spec and the hash a json is tied to
    caption_form(token) -> str                     the caption of a script word ('rings,' -> 'rings')
    caption_forms(words) -> [str]                  the captions of a sentence's words (knows an open single quote)
    spoken_risks(text) -> [(word, why)]            words the voice reads by rules of its own (numbers, 'Mr.', 'III')
    words_of(text) -> [str]                        the script words of a sentence (dashes stay on their word)
    spoken_text(text, say) -> str                  the sentence as it is given to the voice (respellings applied)
    wav_path(film), json_path(film)                where a film's narration lives
    encode_check(film) -> (wav | None, problem | None)    what render.py --encode may mux (no bpy; see render.py)
    class NarrationError                           raised for a missing, stale or damaged narration

    class Narration
        .frames            film length in frames = narration length (last word end + tail), frame 1 = second 0
        .duration          the same in seconds; .fps; .voice; .speed; .wav (path of the audio); .estimated ([Word])
        .timing            'model' (normal), or 'recogniser': spoken with --recogniser-only, words several frames
                           less exact; load() prints a warning for such a narration
        .words             [Word]: .index .text .caption .start .end (seconds) .sentence (index)
                                   .frame (frame NUMBER on which its caption appears) .frame_end (last frame
                                   in which it is still being spoken) .estimated (timing was interpolated)
                                   .source ('model' = the voice model's own phoneme timing, 'energy' = starts on
                                   a measured onset of the sound, 'forced' / 'recognised' = the recogniser)
        .sentences         [Sentence]: .index .id .text .start .end .words
                                   .frame (frame number of its first word) .frame_end
                                   .cut (first frame of a shot that starts with this sentence: 2 frames before its
                                         first word, never inside the sentence before)
        .captions(hold=0.3, long_pause=0.6, cuts=None, min_frames=2) -> [(caption, t0, t1)]
                                                     what build() returns as "captions"
        .sentence(key)     by index, by "id" or by the words it starts with
        .word(text, n=0, sentence=None) -> Word      the n-th word with that caption (optionally inside a sentence)
        .at(text, n=0, sentence=None) -> int         the frame number on which that word's caption appears
        .cut_before(word, lead=2) -> int             a cut frame before any word (never inside the word before it)
        .shot_frames(cuts, total=None) -> [int]      frame counts of the shots starting at frame 1 and at each cut
        .seconds(frames) -> float                    frames / fps (for Stage.shot(name, seconds))
        .part(first, last=None) -> Narration         frames first..last as a narration of their own (two-module films)
        .caption_frames() -> [(caption, first frame, last frame)]    what the encoder will show, in frame numbers
        .summary() -> str                            the build log: length, pace, every sentence with its cut frame
    prove(nar) -> dict                               checks every rule below on a Narration (AssertionError if broken)

A FILM OF TWO MODULES (two skies, as films/poppy_night.py + poppy_day.py): keep ONE narration. Put NARRATION in
one module (say films/story.py, which may be the first part), speak it once (narration/story.*), and let both
modules build their part of it:
        whole = narration.load("story", NARRATION)              # in both modules (import NARRATION from the first)
        nar = whole.part(1, whole.sentence("night").cut - 1)    # first module;   nar = whole.part(whole.sentence("night"))
    $BPY -m render story --encode --no-audio ; $BPY -m render story_night --encode       # both silent
    ffmpeg -f concat -safe 0 -i list.txt -c copy -movflags +faststart out/story_joined.mp4
    $BPY -c "from engine import post; post.mux_audio('out/story_joined.mp4', 'narration/story.wav', 'out/story_final.mp4')"
  (mux_audio copies the picture untouched and lays the whole narration under it from t = 0. Proved end to end
   on a one-minute probe cut in two at a sentence: `$BPY -m tools.narration_minute two`, then `sync two`.)

RULES (proved by `python -m engine.narration`, on every narration in narration/ and on adversarial timings)
  * A frame NUMBER f shows the time [(f-1)/fps, f/fps). A word spoken from `start` appears on the frame that
    CONTAINS that instant: frame number floor(start * fps) + 1 (= Word.frame). So a caption is never late and at
    most one frame early (0 .. 41.7 ms at 24 fps). Its t0 is written a quarter frame before that frame's own time,
    so no float rounding in between (json, autotime-style 4-decimal rounding, the encoder's t0 <= t test) can move
    it. One exception, always toward EARLY: a caption that would be on for a single frame ('a', 'The': words spoken
    in under two frames) starts one frame sooner so that it can be seen (min_frames=2; min_frames=1 = strict).
    Measured in an encoded minute (tools.narration_minute, 33 words after a silence): against the clearly audible
    voice captions are 0 to 1.7 frames early, 0.8 on average, never late; the earliest are words that begin
    with h, which takes 40 ms to become clearly audible. Inside running speech a word's start is the voice model's phoneme
    boundary minus 25 ms (where the cut tests found the word's sound to begin), so a caption there is 0.6 to 1.6
    frames ahead of the boundary, and ahead of the BURST of a word that begins with p, t, k, b, d, g by the length
    of its closure as well (about 2 frames in all on the demo: 'player', 'job'). A picture that leads its sound by
    under 3 frames is not seen as out of sync (ITU-R BT.1359: detectable from 125 ms), a picture that trails is
    seen from 45 ms: early is the safe side, and it is deliberate.
  * A word stays until the next word appears. If the voice then stays silent for more than `long_pause`, the word
    clears `hold` seconds after it was spoken. A word that has been spoken also clears at a cut (captions(cuts=...),
    default: every sentence's cut), so the word of the old shot is never on the first frames of the new one.
  * Sentence.cut = sentence.frame - 2, and at least one frame after the frame in which the previous sentence ends.

    $BPY -m engine.narration            # self-test (any Python with numpy-free stdlib works: no bpy is imported)
"""
import ast
import hashlib
import json
import math
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NARRATION_DIR = os.path.join(ROOT, "narration")

SPEC_VERSION = 1                 # part of every hash: raise it when the meaning of a spec changes
JSON_VERSION = 3                 # of narration/<film>.json: raised when tools/narrate.py times or levels differently
                                 #   (3: words timed on the clip as spoken, not on the limited one; wav at -19 LUFS
                                 #   mono). load() refuses a json of another version: its word frames would differ.
DEFAULT_VOICE = "am_michael"     # the client has not chosen yet: change it here and every narration goes stale
DEFAULTS = {"speed": 1.0, "lead": 0.3, "tail": 1.0, "pause": 0.35, "fps": 24}
CUT_LEAD = 2                     # frames between a cut and the first word of the sentence that starts the shot
HOLD = 0.30                      # seconds a word stays after it was spoken, when a long silence follows
LONG_PAUSE = 0.60                # a silence longer than this clears the caption
LAST_HOLD = 0.50                 # the last word of the film
MIN_FRAMES = 2                   # a caption is on for at least this many frames (a one-frame word is a flicker)
EPS = 1e-6

# How the voice says words its phonemiser gets wrong (checked on the phonemes it prints, see tools/narrate.py
# --phonemes): 'redstoner' came out as RED-stuh-ner, 'Herobrine' as HERE-oh-breen, 'netherite' with the th of
# 'thin'. Keys are lower case; plural and possessive forms ('redstoners', "redstoner's") follow automatically.
# The caption always shows the script's own spelling.
SAY = {
    "redstoner": "red-stoner",
    "herobrine": "hero-brine",
    "netherite": "nether-ite",
}

_OPEN = "\"'([{“‘—–-"
_CLOSE = ".,!?;:\"…—–-)]}”’"
# words that really begin (and 'n' also ends) with an apostrophe: it is no quotation mark
_ELISIONS = {"'em", "'til", "'cause", "'tis", "'twas", "'n'", "'bout", "'round", "'course", "'kay", "'sup"}
# what the phonemiser reads by rules of its own, not as a director would say it (measured: 'III' is said "roman
# three", '14:07' "fourteen <pause> zero seven", 'Mr.' with a sentence-final pause after it)
_ABBREVIATIONS = {"mr.", "mrs.", "ms.", "dr.", "st.", "vs.", "etc.", "jr.", "sr.", "e.g.", "i.e.", "approx."}
_ROMAN = {"ii", "iii", "iv", "vi", "vii", "viii", "ix", "xi", "xii", "xiii", "xiv", "xv", "xx"}


class NarrationError(RuntimeError):
    """A film's narration is missing, stale (the text changed after it was spoken) or damaged."""


# ---------------------------------------------------------------------------------------------------------------
# text
# ---------------------------------------------------------------------------------------------------------------

def film_name(film):
    """'films._narrated_demo' or '_narrated_demo' -> '_narrated_demo' (so a film can pass __name__)."""
    return str(film).rsplit(".", 1)[-1]


def wav_path(film):
    """Path of a film's narration audio (narration/<film>.wav)."""
    return os.path.join(NARRATION_DIR, film_name(film) + ".wav")


def json_path(film):
    """Path of a film's narration timing (narration/<film>.json)."""
    return os.path.join(NARRATION_DIR, film_name(film) + ".json")


def words_of(text):
    """The script words of a sentence, exactly as written with their punctuation. A token without a letter or a
    digit (a lone dash, an ellipsis) is no word of its own: it stays on the word before it."""
    out = []
    lead = ""
    for tok in str(text).split():
        if any(ch.isalnum() for ch in tok):
            out.append(lead + tok)
            lead = ""
        elif out:
            out[-1] += " " + tok
        else:
            lead += tok + " "
    return out


def _bare(token):
    """A script word without its outer punctuation, single quotes still on it."""
    w = str(token).replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').strip()
    close = _CLOSE.replace("’", "").replace("”", "") + " "
    return w.rstrip(close).lstrip(_OPEN.replace("'", "").replace("‘", "").replace("“", "") + " "), close


def _unquote(token, inside):
    """(caption, inside a single-quoted phrase after this word) for one script word."""
    w, close = _bare(token)
    if w.lower() in _ELISIONS or len(w) < 2:
        return w, inside
    lead, trail = w[0] == "'", w[-1] == "'"
    if lead and trail:                                       # 'Run.'
        return w[1:-1].rstrip(close), False
    if lead:                                                 # 'Not again!'  ->  Not ...
        return w[1:], True
    if trail and (inside or not w[-2].lower() == "s"):       # ... again!'  ->  again   (players' keeps its apostrophe
        return w[:-1].rstrip(close), False                   #                          unless a quotation is open)
    return w, inside


def caption_form(token):
    """What the caption shows for a script word: quotes, brackets, dashes and closing punctuation removed,
    apostrophes kept ('rings,' -> 'rings', "don't." -> "don't", 'gold —' -> 'gold', "'Not" -> 'Not', "again!'" ->
    'again', "players'" and "'em" as they are). For ordinary words this is engine.captions.display_word (the
    self-test compares them). For the words of a sentence use caption_forms(), which knows whether a quotation
    in single quotes is open."""
    return _unquote(token, False)[0]


def caption_forms(words):
    """The captions of a sentence's script words (words_of(text)), one for one. As caption_form(), and a single
    quote that closes a phrase opened by an earlier word goes too, even after an s ('Run, boys' -> Run / boys)."""
    out, inside = [], False
    for tok in words:
        c, inside = _unquote(tok, inside)
        out.append(c)
    return out


def spoken_risks(text):
    """[(script word, why)] for the words of a sentence that the voice's phonemiser reads by rules of its own:
    digits ('14:07', '100%', '3'), abbreviations ('Mr.'), Roman numerals ('III') and capitals without a vowel
    ('XP', 'TNT'). tools/narrate.py prints the phonemes of such a sentence; write the word out, or respell it
    with "say", when that is not what the film means."""
    out = []
    for tok in words_of(text):
        bare = _bare(tok)[0].strip("'")
        core = "".join(ch for ch in bare if ch.isalnum())
        if any(ch.isdigit() for ch in bare):
            out.append((bare, "a number"))
        elif tok.strip().lower().rstrip(",;:!?\"')") in _ABBREVIATIONS:
            out.append((bare + ".", "an abbreviation"))
        elif bare.isupper() and bare.lower() in _ROMAN:
            out.append((bare, "a Roman numeral"))
        elif len(core) > 1 and core.isupper() and not any(ch in "AEIOUY" for ch in core):
            out.append((bare, "capitals without a vowel"))
    return out


def letters(token):
    """Lower-case letters and digits of a word (what two spellings of a word are compared by)."""
    return "".join(ch for ch in str(token).lower() if ch.isalnum())


def syllables(token):
    """Rough syllable count of a word (vowel groups, a silent final e dropped), at least 1: the weight a word gets
    when a time span has to be shared between words."""
    w = letters(token)
    if not w:
        return 1
    if w.isdigit():
        return max(1, 2 * len(w))
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and not w.endswith(("le", "ee", "ie", "ye")) and n > 1:
        n -= 1
    return max(1, n)


def spoken_text(text, say=None):
    """The sentence as it is handed to the voice: every word that has a respelling in `say` (or in the built-in
    SAY) replaced by it; plural / possessive forms of such a word are respelled too. Punctuation is kept."""
    table = dict(SAY)
    table.update({str(k).lower().replace("’", "'"): str(v) for k, v in (say or {}).items()})
    out = []
    for tok in str(text).split():
        m = re.match(r"^(\W*)(.*?)(\W*)$", tok, re.S)
        pre, core, post = m.groups()
        low = core.lower().replace("’", "'")
        rep = table.get(low)
        if rep is None:
            for suffix in ("'s", "es", "s"):
                if low.endswith(suffix) and low[:-len(suffix)] in table:
                    rep = table[low[:-len(suffix)]] + suffix
                    break
        out.append(pre + (core if rep is None else rep) + post)
    return " ".join(out)


# ---------------------------------------------------------------------------------------------------------------
# the spec
# ---------------------------------------------------------------------------------------------------------------

def read_spec(film):
    """The NARRATION literal of films/<film>.py, read from the SOURCE (ast.literal_eval): nothing is imported, so
    this works in an interpreter without bpy. Raises NarrationError when there is none or it is not a literal."""
    name = film_name(film)
    path = os.path.join(ROOT, "films", name + ".py")
    try:
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=path)
    except OSError as e:
        raise NarrationError("no film module %s (%s)" % (path, e))
    for node in tree.body:
        target = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
        elif isinstance(node, ast.AnnAssign):
            target = node.target
        if isinstance(target, ast.Name) and target.id == "NARRATION" and node.value is not None:
            try:
                return ast.literal_eval(node.value)
            except (ValueError, SyntaxError) as e:
                raise NarrationError(
                    "%s line %d: NARRATION must be a plain literal (dict / list / tuple / str / numbers, no names "
                    "and no calls), because tools/narrate.py reads it without importing the film: %s"
                    % (path, node.lineno, e))
    raise NarrationError("%s has no top-level `NARRATION = {...}`" % path)


def normalise(spec):
    """Canonical form of a spec: every default filled in, every line as {'id', 'text', 'spoken', 'pause', 'speed'}.
    Raises NarrationError for anything the narrator cannot speak (unknown keys, empty sentences, bad numbers)."""
    if not isinstance(spec, dict):
        raise NarrationError("NARRATION must be a dict with a 'lines' list, got %s" % type(spec).__name__)
    known = {"voice", "speed", "lead", "tail", "pause", "say", "lines", "fps"}
    extra = sorted(set(spec) - known)
    if extra:
        raise NarrationError("NARRATION: unknown keys %s (known: %s)" % (extra, sorted(known)))
    out = {"version": SPEC_VERSION, "voice": str(spec.get("voice") or DEFAULT_VOICE)}
    for key, default in DEFAULTS.items():
        value = spec.get(key, default)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise NarrationError("NARRATION[%r] must be a number, got %r" % (key, value))
        out[key] = int(value) if key == "fps" else round(float(value), 4)
    if not 0.5 <= out["speed"] <= 2.0:
        raise NarrationError("NARRATION['speed'] must be between 0.5 and 2.0, got %r" % out["speed"])
    if out["lead"] < 0 or out["tail"] < 0 or out["pause"] < 0.05:
        raise NarrationError("NARRATION: lead and tail must be >= 0 and pause >= 0.05 s")
    say = spec.get("say") or {}
    if not isinstance(say, dict):
        raise NarrationError("NARRATION['say'] must be a dict {word: respelling}")
    lines = spec.get("lines")
    if not isinstance(lines, (list, tuple)) or not lines:
        raise NarrationError("NARRATION['lines'] must be a non-empty list of sentences")
    out["lines"] = []
    seen = set()
    for i, line in enumerate(lines):
        if isinstance(line, str):
            line = {"text": line}
        elif isinstance(line, (list, tuple)) and len(line) == 2 and isinstance(line[0], str):
            line = {"text": line[0], "pause": line[1]}
        elif not isinstance(line, dict):
            raise NarrationError("NARRATION['lines'][%d]: a sentence is a str, (str, pause) or a dict, got %r" % (i, line))
        extra = sorted(set(line) - {"text", "pause", "speed", "id"})
        if extra:
            raise NarrationError("NARRATION['lines'][%d]: unknown keys %s" % (i, extra))
        text = " ".join(str(line.get("text", "")).split())
        if not words_of(text):
            raise NarrationError("NARRATION['lines'][%d]: no words in %r" % (i, line.get("text")))
        pause = line.get("pause", out["pause"])
        speed = line.get("speed", 1.0)
        for key, value in (("pause", pause), ("speed", speed)):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise NarrationError("NARRATION['lines'][%d][%r] must be a number, got %r" % (i, key, value))
        if pause < 0.05:
            raise NarrationError("NARRATION['lines'][%d]: a pause is at least 0.05 s, got %r" % (i, pause))
        if not 0.5 <= speed * out["speed"] <= 2.0:
            raise NarrationError("NARRATION['lines'][%d]: speed x film speed must stay within 0.5 .. 2.0" % i)
        ident = line.get("id")
        if ident is not None:
            ident = str(ident)
            if ident in seen or ident.isdigit():
                raise NarrationError("NARRATION['lines'][%d]: id %r is used twice or is a number" % (i, ident))
            seen.add(ident)
        out["lines"].append({"id": ident, "text": text, "spoken": spoken_text(text, say),
                             "pause": 0.0 if i == len(lines) - 1 else round(float(pause), 4),
                             "speed": round(float(speed), 4)})
    return out


def spec_hash(spec):
    """Hash of everything that decides what is heard and when (voice, speeds, pauses, lead, tail, every sentence
    as written and as spoken). narration/<film>.json carries it; a film whose NARRATION hashes differently is stale."""
    norm = spec if isinstance(spec, dict) and spec.get("version") == SPEC_VERSION and "lines" in spec \
        and all(isinstance(ln, dict) and "spoken" in ln for ln in spec["lines"]) else normalise(spec)
    blob = json.dumps(norm, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha1(blob.encode("ascii")).hexdigest()[:16]


def file_sha1(path):
    """sha1 of a file's bytes."""
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _diff(old, new):
    """One line saying what differs between two normalised specs."""
    notes = []
    for key in ("voice", "speed", "lead", "tail", "pause", "fps"):
        if old.get(key) != new.get(key):
            notes.append("%s %r -> %r" % (key, old.get(key), new.get(key)))
    a, b = old.get("lines", []), new.get("lines", [])
    if len(a) != len(b):
        notes.append("%d sentences -> %d" % (len(a), len(b)))
    for i, (x, y) in enumerate(zip(a, b)):
        for key in ("text", "spoken", "pause", "speed", "id"):
            if x.get(key) != y.get(key):
                notes.append("sentence %d %s: %r -> %r" % (i, key, x.get(key), y.get(key)))
                break
    return "; ".join(notes[:4]) + (" ..." if len(notes) > 4 else "") or "the spec version"


# ---------------------------------------------------------------------------------------------------------------
# the narration of a film
# ---------------------------------------------------------------------------------------------------------------

class Word:
    """One spoken word: script text, caption, seconds, and the frames it owns."""

    def __init__(self, index, text, caption, start, end, sentence, estimated=False, source=""):
        self.index, self.text, self.caption = index, text, caption
        self.start, self.end, self.sentence = float(start), float(end), int(sentence)
        self.estimated, self.source = bool(estimated), source
        self.frame = self.frame_end = 0

    def __repr__(self):
        return "Word(%d %r %.3f-%.3f f%d)" % (self.index, self.caption, self.start, self.end, self.frame)


class Sentence:
    """One sentence of the narration: its words, seconds and frames, and where a shot that starts with it cuts."""

    def __init__(self, index, ident, text, words):
        self.index, self.id, self.text, self.words = index, ident, text, words
        self.start, self.end = words[0].start, words[-1].end
        self.frame = self.frame_end = self.cut = 0

    def __repr__(self):
        return "Sentence(%d %r %.3f-%.3f f%d-%d cut %d)" % (self.index, self.text[:24], self.start, self.end,
                                                              self.frame, self.frame_end, self.cut)


class Narration:
    """A film's narration: words and sentences in seconds and in frames (see the module docstring)."""

    def __init__(self, data, fps=24, film=None):
        self.data = data
        self.film = film or data.get("film", "")
        self.fps = int(fps)
        self.voice, self.speed = data.get("voice"), data.get("speed")
        self.timing = data.get("timing", "model")       # 'model', or 'recogniser' (spoken without the timed voice model)
        self.duration = float(data["duration"])
        self.wav = wav_path(self.film) if self.film else None
        self.words = [Word(i, w["text"], w["caption"], w["start"], w["end"], w["sentence"],
                           w.get("estimated", False), w.get("source", "")) for i, w in enumerate(data["words"])]
        x = self.duration * self.fps                 # (the json rounds the duration to a microsecond: 241.000008
        self.frames = int(round(x)) if abs(x - round(x)) < 1e-3 else int(math.ceil(x))     # frames are 241, not 242)
        self._check_times()
        # frames: the caption of a word appears on the frame that contains the instant it starts being spoken
        ks = [self.index_of(w.start) for w in self.words]
        for i in range(len(ks) - 1, 0, -1):             # two words inside one frame: the EARLIER one moves a frame
            if ks[i - 1] >= ks[i]:                      # earlier (a caption may be early, never late)
                ks[i - 1] = ks[i] - 1
        if ks and ks[0] < 0:                            # more words than frames at the very start of the film:
            ks[0] = 0                                   # nothing earlier to move to (prove() reports the late ones)
            for i in range(1, len(ks)):
                ks[i] = max(ks[i], ks[i - 1] + 1)
        for w, k in zip(self.words, ks):
            w.frame = k + 1
            w.frame_end = max(w.frame, self.index_of(w.end - 2 * EPS) + 1)
        self.sentences = []
        for i, s in enumerate(data["sentences"]):
            ws = [w for w in self.words if w.sentence == i]
            if not ws:
                raise NarrationError("narration of '%s': sentence %d has no words" % (self.film, i))
            self.sentences.append(Sentence(i, s.get("id"), s["text"], ws))
        for s in self.sentences:
            s.frame, s.frame_end = s.words[0].frame, s.words[-1].frame_end
            s.cut = 1 if s.index == 0 else self.cut_before(s.words[0], CUT_LEAD)
        self.estimated = [w for w in self.words if w.estimated]

    # ---- time
    def index_of(self, t):
        """0-based index of the video frame that contains time t (frame NUMBER = index + 1)."""
        return int(math.floor(float(t) * self.fps + EPS))

    def seconds(self, frames):
        """Length of `frames` frames in seconds (Stage.shot takes seconds)."""
        return frames / float(self.fps)

    def _check_times(self):
        prev = 0.0
        for w in self.words:
            if not (w.start >= prev - EPS and w.end > w.start and w.end <= self.duration + EPS):
                raise NarrationError("narration of '%s': word %d %r has times %.3f-%.3f after %.3f (film %.3f s): "
                                     "the json is damaged, run tools/narrate.py again"
                                     % (self.film, w.index, w.text, w.start, w.end, prev, self.duration))
            prev = w.end

    # ---- look-ups
    def sentence(self, key):
        """A sentence by index, by its "id", or by the words it starts with ('Except me')."""
        if isinstance(key, Sentence):
            return key
        if isinstance(key, int):
            return self.sentences[key]
        for s in self.sentences:
            if s.id == key:
                return s
        want = " ".join(str(key).lower().split())
        hits = [s for s in self.sentences if " ".join(s.text.lower().split()).startswith(want)]
        if len(hits) != 1:
            raise KeyError("%d sentences match %r (ids: %s)" % (len(hits), key, [s.id for s in self.sentences if s.id]))
        return hits[0]

    def word(self, text, n=0, sentence=None):
        """The n-th word whose caption is `text` (case-insensitive when no exact match), optionally inside one sentence."""
        if isinstance(text, Word):
            return text
        if isinstance(text, int):
            return self.words[text]
        pool = self.words if sentence is None else self.sentence(sentence).words
        hits = [w for w in pool if w.caption == text] or [w for w in pool if w.caption.lower() == str(text).lower()]
        if n >= len(hits) or n < -len(hits):
            raise KeyError("word %r occurs %d times%s, asked for number %d"
                           % (text, len(hits), "" if sentence is None else " in that sentence", n))
        return hits[n]

    def at(self, text, n=0, sentence=None):
        """Frame number on which the caption of a word appears (the frame in which it starts being spoken)."""
        return self.word(text, n, sentence).frame

    def cut_before(self, word, lead=CUT_LEAD):
        """First frame of a shot that starts with `word`: `lead` frames before its caption, but at least one frame
        after the frame in which the word before it is still being spoken (a cut never falls inside a word)."""
        w = self.word(word)
        if w.index == 0:
            return 1
        prev = self.words[w.index - 1]
        return max(1, min(w.frame, max(prev.frame_end + 1, w.frame - int(lead))))

    def shot_frames(self, cuts, total=None):
        """Frame counts of consecutive shots: the first starts at frame 1, the others at each entry of `cuts`
        (frame numbers, or Sentences = their .cut); the last one ends with the film (`total` frames, default
        self.frames). Raises when a shot would be empty."""
        total = int(total or self.frames)
        edges = [1] + [c.cut if isinstance(c, Sentence) else int(c) for c in cuts] + [total + 1]
        lengths = [b - a for a, b in zip(edges, edges[1:])]
        if any(n < 1 for n in lengths):
            raise ValueError("shot_frames: cuts %s do not increase inside 1..%d" % (edges[1:-1], total))
        return lengths

    def part(self, first, last=None):
        """Frames first..last of this narration (default: to the end) as a Narration of its own, in which they are
        frames 1..n: for a film made of two modules (two skies). `first` must be a cut (a Sentence or its .cut):
        every word belongs to the part in which its caption appears. The part has no audio of its own (.wav is
        None): encode the modules silent, join them, and put the whole wav under the joined film with
        engine.post.mux_audio (see the module docstring)."""
        first = first.cut if isinstance(first, Sentence) else int(first)
        last = self.frames if last is None else (last.cut - 1 if isinstance(last, Sentence) else int(last))
        if not 1 <= first <= last <= self.frames:
            raise ValueError("part(%s, %s) is not inside 1..%d" % (first, last, self.frames))
        shift, dur = (first - 1) / float(self.fps), (last - first + 1) / float(self.fps)
        words, sentences, renumber = [], [], {}
        for w in self.words:
            if first <= w.frame <= last:
                if w.sentence not in renumber:
                    renumber[w.sentence] = len(sentences)
                    src = self.sentences[w.sentence]
                    sentences.append({"id": src.id, "text": src.text})
                words.append({"text": w.text, "caption": w.caption, "start": max(0.0, w.start - shift),
                              "end": min(dur, w.end - shift), "sentence": renumber[w.sentence],
                              "estimated": w.estimated, "source": w.source})
        if not words:
            raise ValueError("no word is spoken in frames %d..%d" % (first, last))
        data = {"film": self.film, "duration": dur, "voice": self.voice, "speed": self.speed, "timing": self.timing,
                "words": words, "sentences": sentences}
        out = Narration(data, fps=self.fps, film=self.film)
        out.wav = None
        return out

    # ---- captions
    def captions(self, hold=HOLD, long_pause=LONG_PAUSE, cuts=None, last_hold=LAST_HOLD, min_frames=MIN_FRAMES):
        """[(caption, t0, t1), ...] in seconds for build()'s "captions": one word at a time, each from the frame in
        which it starts being spoken until the next word (see RULES in the module docstring). `cuts` = the frame
        numbers of ALL the film's cuts (default: every sentence's .cut; add your cut_before() frames): a word that
        has been spoken never stays on past a cut. min_frames: a caption that would be on for fewer frames ('a',
        'the': spoken in under two frames) starts EARLIER by the missing frames, on blank frames before it or on
        frames the caption before it can spare, never across a cut; min_frames=1 is the strict rule."""
        fps = float(self.fps)
        if cuts is None:
            cuts = [s.cut for s in self.sentences[1:]]
        cuts = sorted(int(c) - 1 for c in cuts)                       # as 0-based frame indices
        spans = []
        for w in self.words:
            k0 = w.frame - 1
            spoken = w.frame_end                                      # index of the first frame after the word
            if w.index + 1 < len(self.words):
                nxt = self.words[w.index + 1]
                k1 = nxt.frame - 1
                if nxt.start - w.end > long_pause:
                    k1 = min(k1, max(spoken, int(math.ceil((w.end + hold) * fps - EPS))))
                for c in cuts:                                        # a cut after the word has been spoken and
                    if spoken <= c <= k1 and c > k0:                  # before the next one: the caption ends there
                        k1 = c
                        break
            else:
                k1 = min(self.frames, max(spoken, int(math.ceil((w.end + last_hold) * fps - EPS))))
            k1 = max(k1, k0 + 1)
            if w.caption:
                spans.append([w.caption, k0, k1])
        for i, span in enumerate(spans):                              # a caption too short to be seen starts earlier
            need = int(min_frames) - (span[2] - span[1])
            if need <= 0:
                continue
            floor = max([0] + [c for c in cuts if c <= span[1]])      # never onto the shot before
            free = span[1] - max(floor, spans[i - 1][2] if i else 0)  # blank frames before it
            take = max(0, min(need, free))
            span[1] -= take
            need -= take
            if need > 0 and i and spans[i - 1][2] == span[1] and span[1] - need >= floor \
                    and spans[i - 1][2] - spans[i - 1][1] - need >= int(min_frames):
                spans[i - 1][2] -= need                               # the caption before gives up its last frames
                span[1] -= need
        return [(c, round((k0 - 0.25) / fps, 5), round((k1 - 0.25) / fps, 5)) for c, k0, k1 in spans]

    def caption_frames(self, **kw):
        """[(caption, first frame number, last frame number), ...] of captions(**kw): what the encoder will show."""
        fps = float(self.fps)
        return [(c, int(math.ceil(t0 * fps - EPS)) + 1, int(math.ceil(t1 * fps - EPS))) for c, t0, t1 in self.captions(**kw)]

    def summary(self):
        """A few lines for the build log: length, words, pace, sentences with their cut frames."""
        n = len(self.words)
        speech = sum(s.end - s.start for s in self.sentences)
        lines = ["[narration] '%s': %.2f s = %d frames at %d fps, %d sentences, %d words, voice %s x %s, "
                 "%.2f words/s while speaking, %d words estimated%s"
                 % (self.film, self.duration, self.frames, self.fps, len(self.sentences), n, self.voice, self.speed,
                    n / max(speech, 1e-6), len(self.estimated),
                    "" if self.timing == "model" else "; TIMED BY THE RECOGNISER ALONE (less exact)")]
        for s in self.sentences:
            lines.append("[narration]   %2d%s cut %4d  words %4d-%4d  %6.2f-%6.2f s  %s"
                         % (s.index, (" " + s.id) if s.id else "", s.cut, s.frame, s.frame_end, s.start, s.end, s.text))
        return "\n".join(lines)


def load(film, spec=None, fps=24, check=True):
    """The narration of a film (pass __name__ or the film's name), checked against its text: `spec` is the film's
    NARRATION dict (default: read from films/<film>.py). Raises NarrationError, with the command that fixes it,
    when narration/<film>.json is missing, was spoken from another text, voice or timing, does not describe the
    wav beside it, or was made for another frame rate."""
    name = film_name(film)
    path = json_path(name)
    fix = "run:  $TTS tools/narrate.py %s   (see tools/narrate.py; then render again)" % name
    if not os.path.exists(path):
        raise NarrationError("no narration for '%s' (%s is missing); %s" % (name, path, fix))
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except ValueError as e:
        raise NarrationError("%s is not valid json (%s); %s" % (path, e, fix))
    if check:
        norm = normalise(read_spec(name) if spec is None else spec)
        if data.get("json_version") != JSON_VERSION:
            raise NarrationError("STALE NARRATION for '%s': %s was written by another version of the narrator (json "
                                 "version %r, now %d: the words are timed and the audio levelled differently); %s"
                                 % (name, os.path.relpath(path, ROOT), data.get("json_version"), JSON_VERSION, fix))
        if spec_hash(norm) != data.get("spec_hash"):
            raise NarrationError("STALE NARRATION for '%s': the film's NARRATION is not what %s was spoken from (%s); %s"
                                 % (name, os.path.relpath(path, ROOT), _diff(data.get("spec", {}), norm), fix))
        if norm["fps"] != int(fps):
            raise NarrationError("narration of '%s' was laid out for %d fps, the film asks for %d"
                                 % (name, norm["fps"], fps))
        wav = wav_path(name)
        if not os.path.exists(wav):
            raise NarrationError("narration audio %s is missing; %s" % (wav, fix))
        if data.get("wav_sha1") and file_sha1(wav) != data["wav_sha1"]:
            raise NarrationError("%s is not the audio that %s describes (another run wrote it); %s"
                                 % (os.path.relpath(wav, ROOT), os.path.relpath(path, ROOT), fix))
    nar = Narration(data, fps=fps, film=name)
    if nar.timing != "model" and name not in _WARNED:
        _WARNED.add(name)
        print("[narration] WARNING: '%s' was spoken with --recogniser-only (timing %r): its words are timed by the "
              "recogniser alone, measured about 115 ms early inside speech with one pause in four on the wrong word. "
              "Make the timed voice model (tools/narrate.py --make-timed-model) and speak it again: "
              "$TTS tools/narrate.py %s --force" % (name, nar.timing, name))
    return nar


_WARNED = set()


def encode_check(film):
    """What the encoder may mux for a film, without building it: (wav path or None, problem or None).
    (None, None) = the film has no narration (silent film, as before). A problem (text) means there IS a
    narration but it must not be used: the wav has no json, the json is stale against films/<film>.py, or the
    wav is not the one the json describes."""
    name = film_name(film)
    wav, js = wav_path(name), json_path(name)
    if not os.path.exists(wav):
        if os.path.exists(js):
            return None, "narration/%s.json exists but narration/%s.wav is missing" % (name, name)
        return None, None
    if not os.path.exists(js):
        return None, "narration/%s.wav has no narration/%s.json beside it" % (name, name)
    try:
        load(name)
    except NarrationError as e:
        return None, str(e)
    return wav, None


# ---------------------------------------------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------------------------------------------

def prove(nar, **kw):
    """Check every promise of the module docstring on one Narration; returns a dict of measured numbers and
    raises AssertionError on the first broken promise."""
    fps = float(nar.fps)
    caps = nar.captions(**kw)
    spare = int(kw.get("min_frames", MIN_FRAMES)) - 1
    shown = [w for w in nar.words if w.caption]
    assert len(caps) == len(shown), "one caption per word"

    def visible(k):                                  # what engine.post.encode shows on 0-based frame index k
        t = k / fps
        for c, t0, t1 in caps:
            if t0 <= t < t1:
                return c
        return None

    early, per_frame, moved, short = [], [visible(k) for k in range(nar.frames)], 0, 0
    for w, (c, t0, t1) in zip(shown, caps):
        k = int(math.ceil(t0 * fps - EPS))           # first frame index whose time is >= t0
        assert c == w.caption and visible(k) == c, "word %r is not visible on its frame" % c
        assert w.frame - 1 - spare <= k <= w.frame - 1, "captions() and Word.frame disagree for %r" % c
        assert k == 0 or per_frame[k - 1] != c or (w.index and nar.words[w.index - 1].caption == c), \
            "word %r is already visible a frame before its own" % c
        lead = w.start - k / fps                     # how long before the voice the caption is on (seconds)
        assert -EPS <= lead, "LATE caption: %r appears %.1f ms after it is spoken" % (c, -lead * 1000)
        # one frame at most, except where two words start inside one frame and the earlier one moved up
        squeezed = k < nar.index_of(w.start)         # moved up: it shared a frame with the next word, or was too
        moved += squeezed                            # short to be seen
        assert lead < (1.0 + (spare if squeezed else 0) + (w.frame - 1 < nar.index_of(w.start))) / fps + EPS, \
            "caption %r is %.1f ms early" % (c, lead * 1000)
        assert t1 > t0 and t1 <= nar.frames / fps + EPS
        on = int(math.ceil(t1 * fps - EPS)) - k      # frames the caption is on
        assert on >= 1
        short += on < spare + 1
        early.append(lead)
        # float safety: the same list after autotime-style rounding and a json round trip shows the same frames
        t0r = json.loads(json.dumps(round(t0, 4)))
        assert int(math.ceil(t0r * fps - EPS)) == k, "4-decimal rounding moves %r to another frame" % c
    for (ca, a0, a1), (cb, b0, b1) in zip(caps, caps[1:]):
        assert a1 <= b0 + EPS, "captions overlap: %r / %r" % (ca, cb)
    cuts = []
    for s in nar.sentences[1:]:
        prev = nar.sentences[s.index - 1]
        assert prev.frame_end < s.cut <= s.frame, "cut %d of sentence %d is inside a word" % (s.cut, s.index)
        assert s.frame - s.cut <= 3
        cuts.append(s.frame - s.cut)
        last = caps[shown.index(prev.words[-1])] if prev.words[-1] in shown else None
        if last is not None:                         # the old shot's last word is gone when the new shot starts
            assert int(math.ceil(last[2] * fps - EPS)) <= max(s.cut - 1, prev.frame_end), \
                "the last word of sentence %d is still up after the cut" % prev.index
    assert sum(nar.shot_frames([s for s in nar.sentences[1:]])) == nar.frames
    blank = sum(1 for c in per_frame if c is None)
    return {"words": len(shown), "frames": nar.frames, "early_ms_max": 1000 * max(early) if early else 0.0,
            "early_ms_mean": 1000 * sum(early) / max(1, len(early)), "cut_leads": cuts, "blank_frames": blank,
            "moved_up": moved, "shorter_than_min_frames": short,
            "shortest_caption_frames": min((int(round((t1 - t0) * fps)) for _c, t0, t1 in caps), default=0)}


def _synthetic(seed, fps=24, n_sentences=7):
    """An adversarial narration (no audio): words as short as 30 ms, pauses from 0.06 to 2.5 s, starts on and
    beside frame boundaries."""
    import random

    rng = random.Random(seed)
    t = rng.choice([0.085, 0.3, 2.0 / fps, 3.0 / fps - 1e-9])
    words, sentences = [], []
    vocab = ["I", "a", "gold", "piglin", "doesn't", "Herobrine", "the", "redstoner", "us", "trade"]
    d = 0.1
    for s in range(n_sentences):
        first = len(words)
        for _ in range(rng.randint(1, 9)):
            d = rng.choice([0.045, 1.0 / fps, 0.06, 0.12, 0.25, 0.4] + ([0.03] if d > 0.04 else []))
            text = rng.choice(vocab)
            words.append({"text": text, "caption": text, "start": round(t, 6), "end": round(t + d, 6), "sentence": s})
            t += d + rng.choice([0.0, 0.0, 0.0, 0.01, 0.2, 0.7])
        sentences.append({"id": None, "text": " ".join(w["text"] for w in words[first:])})
        t += rng.choice([0.06, 0.1, 0.3, 0.35, 0.9, 2.5]) - 0.0
    dur = math.ceil((words[-1]["end"] + rng.choice([0.0, 0.5, 1.0])) * fps) / fps
    return {"film": "", "duration": dur, "voice": "none", "speed": 1.0, "words": words, "sentences": sentences}


def _selftest():
    """Text rules, spec hashing, the frame rules on adversarial timings and on every narration in narration/."""
    try:
        from . import captions as cap
    except ImportError:                              # an interpreter without PIL / numpy (the TTS environment)
        cap = None
    assert words_of("In this town — everyone is musical ... except me.") == \
        ["In", "this", "town —", "everyone", "is", "musical ...", "except", "me."]
    for tok, want in (("rings,", "rings"), ("don't.", "don't"), ("\"Why?\"", "Why"), ("gold —", "gold"),
                      ("I’m", "I'm"), ("(really)", "really"), ("players'", "players'"), ("red-stoner", "red-stoner"),
                      ("'Run.'", "Run"), ("'em", "'em"), ("64", "64"), ("Wait...", "Wait"), ("lava:", "lava"),
                      ("'Not", "Not"), ("again!'", "again"), ("‘Not", "Not"), ("again!’", "again"), ("'n'", "'n'"),
                      ("I'M", "I'M"), ("o'clock,", "o'clock"), ("redstoner's", "redstoner's"), ("'Go!'", "Go")):
        assert caption_form(tok) == want, (tok, caption_form(tok))
    assert caption_forms(words_of("\"Run,\" he typed. 'Not again, boys!' The players' base and 'em.")) == \
        ["Run", "he", "typed", "Not", "again", "boys", "The", "players'", "base", "and", "'em"]
    assert [r[0] for r in spoken_risks("At 14:07 Mr. Steve had 3 TNT, Unbreaking III and 100% XP.")] == \
        ["14:07", "Mr.", "3", "TNT", "III", "100%", "XP"]
    assert spoken_risks("So I wrote it on a sign: I'M STILL HERE. I said no.") == []
    if cap is not None:
        for tok in "When the bell rings, we run home. don't. I'm \"Why?\" players' Everyone".split():
            assert caption_form(tok) == cap.display_word(tok), tok
    assert spoken_text("I'm a redstoner, not Herobrine's friend.") == "I'm a red-stoner, not hero-brine's friend."
    assert spoken_text("The Crammys!", {"Crammys": "crammies"}) == "The crammies!"
    assert [syllables(w) for w in ("I", "gold", "piglin", "Herobrine", "villager", "trade")] == [1, 1, 2, 3, 3, 1]
    for frames in (241, 251, 1439, 1440):            # a duration rounded to 6 decimals is still that many frames
        d = _synthetic(1)
        d["duration"] = round(frames / 24.0, 6)
        d["words"] = [w for w in d["words"] if w["end"] < d["duration"]]
        d["sentences"] = d["sentences"][:max(w["sentence"] for w in d["words"]) + 1]
        assert Narration(d, fps=24).frames == frames, frames
    spec = {"lines": ["One two.", ("Three.", 0.8), {"text": "Four  five.", "id": "end", "speed": 0.9}]}
    norm = normalise(spec)
    assert norm["voice"] == DEFAULT_VOICE and norm["lines"][1]["pause"] == 0.8 and norm["lines"][2]["pause"] == 0.0
    assert norm["lines"][2]["text"] == "Four five." and spec_hash(spec) == spec_hash(norm)
    changed = {"lines": ["One two.", ("Three.", 0.9), {"text": "Four  five.", "id": "end", "speed": 0.9}]}
    assert spec_hash(changed) != spec_hash(spec)
    assert spec_hash(dict(spec, voice=DEFAULT_VOICE, pause=DEFAULTS["pause"])) == spec_hash(spec)
    for bad in ({}, {"lines": []}, {"lines": ["..."]}, {"lines": ["a"], "speed": 3}, {"lines": ["a"], "nope": 1},
                {"lines": [("a", 0.0)]}):
        try:
            normalise(bad)
        except NarrationError:
            continue
        raise AssertionError("normalise accepted %r" % (bad,))
    # a json of another version of the narrator, or one timed by the recogniser alone, is not taken silently
    import contextlib
    import io
    import tempfile

    global NARRATION_DIR
    keep, here = NARRATION_DIR, tempfile.mkdtemp(prefix="narration_selftest_")
    try:
        NARRATION_DIR = here
        probe = {"lines": ["One two."]}
        data = _synthetic(3)
        data.update(json_version=JSON_VERSION, spec_hash=spec_hash(probe), spec=normalise(probe), timing="recogniser")
        with open(wav_path("probe"), "wb") as f:
            f.write(b"RIFF")
        with open(json_path("probe"), "w", encoding="utf-8") as f:
            json.dump(data, f)
        said = io.StringIO()
        with contextlib.redirect_stdout(said):
            nar = load("probe", probe)
        assert nar.timing == "recogniser" and "WARNING" in said.getvalue() and "RECOGNISER" in nar.summary()
        data["json_version"] = JSON_VERSION - 1
        with open(json_path("probe"), "w", encoding="utf-8") as f:
            json.dump(data, f)
        try:
            load("probe", probe)
            raise AssertionError("load accepted a json of an older narrator")
        except NarrationError as e:
            assert "another version" in str(e), e
    finally:
        NARRATION_DIR = keep
        for name in ("probe.wav", "probe.json"):
            if os.path.exists(os.path.join(here, name)):
                os.remove(os.path.join(here, name))
        os.rmdir(here)
    print("[narration] text and spec rules, stale and recogniser-only narrations: ok")

    worst, total, moved = 0.0, 0, 0
    for seed in range(400):
        for fps in (24, 30):
            nar = Narration(_synthetic(seed, fps), fps=fps)
            r = prove(nar, min_frames=1)                     # the strict rule ...
            prove(nar)                                       # ... and with the two-frame minimum
            worst, total, moved = max(worst, r["early_ms_max"]), total + r["words"], moved + r["moved_up"]
    print("[narration] frame rules on 800 adversarial narrations (%d words, some only 30 ms long): no late caption, "
          "no cut inside a word; %d words shared a frame with the next one and appear a frame earlier (earliest "
          "caption %.1f ms before its word)" % (total, moved, worst))

    found = sorted(f[:-5] for f in os.listdir(NARRATION_DIR) if f.endswith(".json")) if os.path.isdir(NARRATION_DIR) else []
    for name in found:
        try:
            nar = load(name)
        except NarrationError as e:
            if not os.path.exists(os.path.join(ROOT, "films", name + ".py")):
                print("[narration] %s: no film module (skipped)" % name)
                continue
            print("[narration] %s: %s" % (name, e))
            raise SystemExit(1)
        r = prove(nar)
        if len(nar.sentences) > 1:                   # two modules: the parts' captions are the whole film's captions
            cut = nar.sentences[len(nar.sentences) // 2].cut
            a, b = nar.part(1, cut - 1), nar.part(cut)
            prove(a)
            prove(b)
            off = (cut - 1) / float(nar.fps)
            joined = a.captions() + [(c, round(t0 + off, 5), round(t1 + off, 5)) for c, t0, t1 in b.captions()]
            whole = nar.captions()
            assert a.frames + b.frames == nar.frames and len(joined) == len(whole)
            for (c1, s1, e1), (c2, s2, e2) in zip(joined, whole):
                assert c1 == c2 and abs(s1 - s2) < 1e-4 and (abs(e1 - e2) < 1e-4 or c1 == a.captions()[-1][0]), (c1, s1, s2, e1, e2)
        print(nar.summary())
        strict = prove(nar, min_frames=1)
        print("[narration]   proved: %d captions, each on the frame in which its word starts (early by %.1f ms on "
              "average, %.1f ms at most, never late; %d of them one frame sooner because they would have been on "
              "for a single frame); cuts %s frames before their sentence; %d blank frames; shortest caption %d "
              "frames (strict rule, min_frames=1: at most %.1f ms early, shortest caption %d frame)"
              % (r["words"], r["early_ms_mean"], r["early_ms_max"], r["moved_up"], sorted(set(r["cut_leads"])),
                 r["blank_frames"], r["shortest_caption_frames"], strict["early_ms_max"],
                 strict["shortest_caption_frames"]))
    if not found:
        print("[narration] no narration/*.json yet (run tools/narrate.py <film>)")
    print("[narration] self-test passed")


if __name__ == "__main__":
    _selftest()
