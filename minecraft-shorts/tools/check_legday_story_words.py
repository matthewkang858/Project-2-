"""Checker probe (story, words, time): the NARRATION literal against stories/redstoner.json, and the spoken timing.

    $BPY -m tools.check_legday_story_words
Pure python: reads films/legday.py's NARRATION with engine.narration.read_spec (no bpy needed).
"""
import json
import os
import re
import sys

from engine import narration

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def split_sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def main():
    story = json.load(open(os.path.join(ROOT, "stories", "redstoner.json")))
    spec = narration.read_spec("legday")
    lines = [l["text"] if isinstance(l, dict) else (l[0] if isinstance(l, (list, tuple)) else l)
             for l in spec["lines"]]
    story_sents = split_sentences(story["narration"])
    beat_lines = [b["line"] for b in story["beats"]]
    print("story sentences %d, beats %d, NARRATION lines %d" % (len(story_sents), len(beat_lines), len(lines)))
    bad = 0
    for i in range(max(len(lines), len(story_sents), len(beat_lines))):
        a = lines[i] if i < len(lines) else None
        b = story_sents[i] if i < len(story_sents) else None
        c = beat_lines[i] if i < len(beat_lines) else None
        ok = (a == b == c)
        if not ok:
            bad += 1
            print("DIFF %02d\n  nar  %r\n  story%r\n  beat %r" % (i + 1, a, b, c))
    print("joined literal == story narration:", " ".join(lines) == story["narration"].strip())
    words = sum(len(narration.words_of(l)) for l in lines)
    print("words", words, "story word_count", story.get("word_count"))
    # non-ascii or odd characters
    for i, l in enumerate(lines):
        odd = [ch for ch in l if ord(ch) > 127]
        if odd:
            print("non-ascii in line", i + 1, odd)
    print("say:", spec.get("say"), "voice", spec.get("voice"), "speed", spec.get("speed"),
          "lead", spec.get("lead"), "tail", spec.get("tail"), "pause", spec.get("pause"))
    print("deviations:", bad)

    nar = narration.load("legday", spec, fps=24)
    print()
    print(nar.summary())
    print()
    print("%-4s %-6s %7s %7s %6s %6s %6s %5s  %s" % ("id", "speed", "start", "end", "dur", "pause", "f0", "cut", "text"))
    sents = nar.sentences
    for i, s in enumerate(sents):
        nxt = sents[i + 1].start if i + 1 < len(sents) else nar.duration
        pause = nxt - s.end
        sp = [l for l in spec["lines"] if isinstance(l, dict) and l.get("id") == s.id]
        speed = sp[0].get("speed", "") if sp else ""
        wps = len(s.words) / max(1e-6, s.end - s.start)
        print("%-4s %-6s %7.2f %7.2f %6.2f %6.2f %6d %5d  %s  (%.2f w/s)" % (
            s.id, speed, s.start, s.end, s.end - s.start, pause, s.frame, s.cut, s.text, wps))
    print("total %.3f s, frames %d, lead(first word start) %.3f" % (nar.duration, nar.frames, sents[0].start))
    print("last word end %.3f, tail %.3f" % (sents[-1].end, nar.duration - sents[-1].end))
    print("words", len(nar.words), "spoken", sum(s.end - s.start for s in sents))
    gaps = []
    for a, b in zip(nar.words, nar.words[1:]):
        gaps.append((b.start - a.end, a.caption, b.caption, a.frame_end, b.frame))
    gaps.sort(reverse=True)
    print("largest word-to-word silences:")
    for g in gaps[:30]:
        print("  %.2f s  %s -> %s   (frames %d -> %d)" % g)
    print("estimated words:", [w.caption for w in nar.words if w.estimated])
    print("sources:", sorted(set(w.source for w in nar.words)))
    for w in nar.words:
        if w.frame_end < w.frame:
            print("WORD END BEFORE START", w.caption, w.frame, w.frame_end)
    if "--words" in sys.argv:
        for w in nar.words:
            print("%3d %-12s s%02d f%4d..%4d  %.3f-%.3f %s" % (w.index, w.caption, w.sentence + 1, w.frame,
                                                              w.frame_end, w.start, w.end, w.source))


if __name__ == "__main__":
    main()
