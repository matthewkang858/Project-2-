"""Poppy: what its two film modules share (films/poppy_night.py and films/poppy_day.py).

The film is told by the villagers about their iron golem:

    night   "He doesn't sleep. He doesn't eat."
    day     "He holds out a flower to the children. One day, the flower was all we found."

It is two render modules because a module has one sky; the orchestrator joins the two mp4 files, so the cut from
the night's last picture to the day's first is a hard cut inside one 12.8 s film (night 93 frames + day 214).

Here: the caption clock on whole frames (Clock), and the small helpers both modules use to put the golem and the
dropped poppy of engine.mobs on a films.lookdev.Stage.
"""
import math

from mathutils import Vector

from engine import captions, mobs

FPS = 24
TITLE = "Poppy"
SCRIPT_NIGHT = "He doesn't sleep. He doesn't eat."
SCRIPT_DAY = "He holds out a flower to the children. One day, the flower was all we found."
PATH_Z = -0.0625                 # a dirt path lies one pixel below the grass


class Clock:
    """The captions of one module on whole frames, and what follows from them.

    start = frames before the first word, word = frames per word, comma / period = extra frames a word holds after
    a comma / at the end of a sentence, tail = frames the last picture stays once the last word has gone.
    (autotime rounds its times to 4 decimals and a frame shows the word whose t0 <= its own time, so every word is
    started a quarter frame early: a t0 rounded UP past its frame would come on one frame late.)"""

    def __init__(self, script, start, word, comma, period, tail=0):
        self.caps = captions.autotime(script, start=(start - 0.25) / FPS, per_word=word / float(FPS),
                                      comma=comma / float(FPS), period=period / float(FPS))
        self.words = [w.lower() for w, _a, _b in self.caps]
        self.frames = [int(round(t0 * FPS)) + 1 for _w, t0, _t1 in self.caps]
        self.last = int(round(self.caps[-1][2] * FPS))          # the last frame that shows the last word
        self.end = self.last + 1 + tail                         # the first frame AFTER the film
        self.check()

    def frame(self, word, nth=0):
        """Frame on which the nth occurrence of `word` appears."""
        hits = [i for i, w in enumerate(self.words) if w == word.lower()]
        return self.frames[hits[nth]]

    def lengths(self, *cuts):
        """Frame count of each shot when the cuts are on these frames (the first shot starts on frame 1)."""
        edges = [1] + list(cuts) + [self.end]
        assert all(b > a for a, b in zip(edges, edges[1:])), edges
        return [b - a for a, b in zip(edges, edges[1:])]

    def check(self):
        """Every word must come up exactly on its frame, as the encoder will draw it (captions.caption_at)."""
        for i, f in enumerate(self.frames):
            shown = captions.caption_at(self.caps, (f - 1) / float(FPS))
            before = captions.caption_at(self.caps, (f - 2) / float(FPS)) if f > 1 else None
            assert shown == self.caps[i][0], (i, f, shown)
            assert i == 0 or before == self.caps[i - 1][0], (i, f, before)

    def table(self):
        """One line per word: frame, seconds, word (for the film's own report)."""
        return ["%4d  %6.3f s  %s" % (f, (f - 1) / float(FPS), w) for f, (w, _a, _b) in zip(self.frames, self.caps)]


def forward(yaw):
    """Unit vector a character with this yaw faces (yaw 0 = -Y)."""
    return Vector((math.sin(yaw), -math.cos(yaw), 0.0))


def right(yaw):
    """Unit vector to the right-hand side of a character with this yaw."""
    return Vector((-math.cos(yaw), -math.sin(yaw), 0.0))


def aside(c, frame, degrees, dz=0.0, dist=3.0):
    """A point `degrees` to the left (+) or right (-) of where character c faces at `frame`, at its eye height + dz:
    the look_at target of a glance that still shows the face (a villager's head turned more than about 26 degrees
    from the lens is a blank box)."""
    yaw, a = c.yaw_at(frame), math.radians(degrees)
    f, p = forward(yaw), c.pos_at(frame)
    return (p.x + dist * (f.x * math.cos(a) - f.y * math.sin(a)), p.y + dist * (f.x * math.sin(a) + f.y * math.cos(a)),
            p.z + c.eye_height + dz)


def add_golem(st, name="golem"):
    """The iron golem of engine.mobs, registered with the Stage (Stage.actor builds villagers and Steve only)."""
    g = st.cast.get(name)
    if g is None:
        g = st.cast[name] = mobs.make_iron_golem(name)
    return g


def add_item(st, item_id, name=None, **kw):
    """A dropped item of engine.mobs, registered with the Stage so that Stage.finish() hides it outside its shots."""
    name = name or item_id
    it = st.cast.get(name)
    if it is None:
        it = st.cast[name] = mobs.make_dropped_item(item_id, name=name, **kw)
    return it


def clear_for_golem(v, points, corner=1.0):
    """Assert that the golem (arms included) walks `points` without touching a block of the set."""
    line = mobs.rounded(points, radius=corner) if len(points) > 2 else points
    hits = mobs.clearance(v, line, width=mobs.MODEL_WIDTH, height=mobs.MODEL_HEIGHT)
    assert not hits, "the golem does not fit: %s" % (hits[:3],)
