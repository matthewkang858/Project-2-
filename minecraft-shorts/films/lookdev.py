"""Look-dev: the real village, the real cast and the real look, in eleven short shots (role INTEGRATOR).

Four small films share this code, one per sky (a sky is built once per film, so every shot of a film has the
same sun, exactly like the two real films will):

    lookdev_dusk    bell, run, interior, steve_bell              (what "The Bell" needs, first picture to last)
    lookdev_golden  villager, nitwit, trade, hall, meadow        (what "The Nitwit" needs)
    lookdev_bed     steve_bed                    (reference 1, with its own sun)
    lookdev_night   night                        (reference 3)

Everything goes through the real pipeline (render.py Session -> engine.look / engine.shots / engine.post):

    $BPY -m films.lookdev --captioned          # all eleven stills -> out/test/lookdev_<name>.png (720x1280, 24
                                               #   samples, 4 threads) plus lookdev_bell_captioned.png /
                                               #   lookdev_night_captioned.png (about 3 minutes: run one film's
                                               #   stills per call under `timeout 300`, e.g. `bell run interior
                                               #   steve_bell`, then `villager nitwit trade hall meadow`, ...)
    $BPY -m films.lookdev bell run --res 540x960 --samples 16 --suffix _try --zones   # cheaper, other names, UI zones
    $BPY -m render lookdev_dusk --frames all --step 4 --res 360x640 --samples 8 --encode --allow-holds
                                               # the animation as a PREVIEW (out/preview/..., never the final frames)
    $BPY -m render lookdev_night --still 1.0 --captioned                            # any render.py action works

Every still is checked after it is rendered (tools/palette_check.py; exit code 1 if anything fails):
- palette: the picture is compared with the game texels under every pixel. Lit stone must not go magenta, robes
  stay brown, oak stays oak, skin stays skin, Steve's trousers keep all three channels, plants are as bright as the
  ground. A look that fails these has left the game's palette, however pretty it is.
- composition: what a shot is about (Stage.hero) must sit in the safe area of a Reel: x 8-82 %, y 14-60 %, clear of
  the caption band (y 62-72 %), the icon column and the 5 % side crop of tall phones.

Rules the real films should keep (each one cost a wrong render here):
- one sky per film. Pick the sun so the subjects are lit: a village is dense, and below about 20 degrees almost
  everything at ground level is in some building's shadow. "Golden hour" here is a warm sun at 27 degrees.
- at dusk the sun lights nothing at ground level: every subject needs a practical as its key. The bell and whoever
  rings it have the two lamps that flank the bell (light groups 'bell_w' / 'bell_e'): make the one on the far side
  from the camera's shadow side the key (x 2-2.5) and turn the other down or off, so the subject has a lit side
  and a dark side. Keep what is BEHIND the subject about a stop under it (scale 0.9-1.0, not 1.6).
- nobody may be keyed before a shot starts if they are also in the shot before it: place() cuts off the earlier
  walk. Pre-roll (start a walk before the cut so it is at full speed) only for people new to the shot.
- place() everybody first, then look_at(): a look at somebody who has not been placed yet aims at where they
  were in the previous shot.
- plain villagers seen from behind are a brown box with a pink box on top. Stage people so that the nose, the
  brow, a hat or the crossed arms show, and HOLD a head turn to the last frame of the shot (head yaw is limited to
  70 degrees: seen from 40 degrees behind, anything under about 65 is a faceless box again).
- flat items (the emerald) lie along the hand, as in the game: edge-on from the side, readable from behind or above.
- Stage.lights(shot, ...) once per shot: it steps every torch at the cut, so no light level leaks into the next shot.
  Pass inside=<group> for a shot filmed inside a room: only then is that room's fill light on.
- a villager who looks down at something held low hides his face under his hat; let him look at the other's face.
- the camera may sit outside a wall: Stage.see_through() hides the wall from the camera only (interior shot).
- a camera that tracks somebody along the exit road rides on the plant-free verge west of it
  (village.CAMERA_LANE): anywhere else a tuft of grass one block from the lens covers the subject.
- trading hall: faces are 0.5 block wide and 2 blocks apart, so from across the aisle three of them never get
  bigger than a fifth of the frame. Ride along the counter instead (a hand from the cell fronts, 20-25 degrees off
  the row, 38 mm): the nearest face is over a quarter of the frame and the row lines up behind it.

The helpers here (Stage: cast per shot, torch light levels per shot, camera-only cutaways) are what the two real
film scripts are expected to copy.
"""
import math
import os
import sys
import time

import bpy

from engine import captions, characters, look, props, shots, village

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# film key -> sky and shot list. `az` = where the sun (or the moon at night) stands, degrees counter-clockwise
# from +X (east): 90 = north, 180 = west.
FILMS = {
    "lookdev_dusk": dict(
        preset="dusk", az=187.0, el=5.0, grade="warm", key=1.0, ambient=1.0, bloom=1.3,
        beds={"house_a_bed_2": "red"},          # the empty bed the shot is about: the red bed everybody knows
        shots=(("bell", 1.5), ("run", 1.0), ("interior", 1.0), ("steve_bell", 1.0)),
        script="When the bell rings, we run home. We count who made it. He rings it because he likes the sound.",
        timing=dict(start=0.1, end=4.4)),
    "lookdev_golden": dict(
        preset="golden", az=62.0, el=27.0, grade="warm", key=1.0, ambient=1.0, bloom=1.0,
        shots=(("villager", 1.0), ("nitwit", 1.0), ("trade", 1.0), ("hall", 1.0), ("meadow", 1.0)),
        script="Everyone here has a job. I don't. He never trades with me. He never locked me in a box.",
        timing=dict(start=0.1, per_word=0.22, comma=0.05, period=0.12)),
    "lookdev_bed": dict(
        preset="golden", az=212.0, el=24.0, grade="warm", key=1.0, ambient=1.0, bloom=1.0,
        beds={"house_a_bed_2": "red"},          # as in the client's reference 1
        shots=(("steve_bed", 1.0),),
        script="He sleeps in a bed.", timing=dict(start=0.0, per_word=0.2, period=0.4)),
    "lookdev_night": dict(
        preset="night", az=176.0, el=21.0, grade="cool", key=1.0, ambient=1.0, bloom=1.3,
        shots=(("night", 1.5),),
        script="He likes the sound.", timing=dict(start=0.0, per_word=0.25, period=0.5)),
}

# shot name -> (film, seconds into the shot of the look-dev still)
STILLS = {
    "bell": ("lookdev_dusk", 1.2), "run": ("lookdev_dusk", 0.5), "interior": ("lookdev_dusk", 0.5),
    "steve_bell": ("lookdev_dusk", 0.5),
    "villager": ("lookdev_golden", 0.5), "nitwit": ("lookdev_golden", 0.5), "trade": ("lookdev_golden", 0.6),
    "hall": ("lookdev_golden", 0.5), "meadow": ("lookdev_golden", 0.5),
    "steve_bed": ("lookdev_bed", 0.5), "night": ("lookdev_night", 1.0),
}
ORDER = ["bell", "run", "interior", "steve_bell", "villager", "nitwit", "trade", "hall", "meadow", "night",
         "steve_bed"]
CAPTIONED = ("bell", "night")       # the stills that also get a 1080x1920 version with their caption word


def yaw_to(src, dst):
    """Yaw that makes a character at src (facing -Y at yaw 0) face dst."""
    return math.atan2(dst[0] - src[0], -(dst[1] - src[1]))


def up(p, dz):
    """Point p raised by dz."""
    return (p[0], p[1], p[2] + dz)


class Stage:
    """The built set plus the bookkeeping a multi-shot film needs: who is in which shot, how bright the torches
    are in each shot, which walls the camera may look through, and (new) which SKY each frame is filmed under and
    where the encoder DIPS TO BLACK.

    ONE SKY (every finished film): build the sky yourself and hand its objects over, as before:

        sky = look.set_time(scene, "golden", sun_azimuth=62.0, sun_elevation=27.0)
        look.setup_compositor(scene, bloom=1.0, grade="warm")
        st = Stage(scene, film, v, sky)

    SEVERAL SKIES IN ONE FILM (day and night in one module, one frame directory, one mp4). The recipe:

        SKIES = {"gold":  dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm"),      # module level,
                 "night": dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool")}      # the name SKIES

        def build(scene, sky=None):                       # render.py calls build once per sky it has work in
            v = village.build_village(scene, seed=1)
            film = shots.Film(scene, fps=24)
            st = Stage(scene, film, v, skies=SKIES, sky=sky)     # builds the ACTIVE sky + its compositor
            s = st.shot("street", 3.0, sky="gold")               # every shot is tagged with the sky it is filmed
            s = st.shot("door", 2.5, sky="night")                #   under; default: the sky in force before it
            s = st.shot("bed", 3.0)                              # (night)
            st.sky_change(nar.at("ended"), "gold")               # ... and from this frame on the SAME shot is gold
            st.dip(s.frame_start, out=3, hold=0, back=3)         # encoder: dip to black around this cut
            st.finish()
            return {"film": film, "captions": caps, "narration": nar, "stage": st}

      * A sky entry holds the arguments of look.set_time and look.setup_compositor: preset ('day' | 'golden' |
        'dusk' | 'night'), az / el (where the sun, at night the moon, stands), key / ambient (strengths), bloom,
        grade, vignette, haze, and by their own names celestial_size, clouds, cloud_height, cloud_radius,
        cloud_offset, star_scale. A misspelt key is an error.
      * sky=None builds the first sky of SKIES. st.sky is that sky's set_time() dict (st.sky["key"] is its sun or
        moon lamp), st.sky_name its name, st.skies the table.
      * EVERYTHING ELSE MUST BE THE SAME IN EVERY BUILD: the whole timeline, every actor, every key, every torch
        level, every caption. Only the sky differs. So never write `if sky == "night": ...` around a shot, an
        actor or an import; key a film-local light for the shots that need it instead (it is hidden elsewhere).
        A frame is right only when it is rendered in the build of its own sky; render.py makes sure of that (it
        refuses to render, stamp or judge a frame in another sky's build) and renders the film sky by sky.
      * Torches and lanterns are not part of a sky: Stage.lights(shot, ...) per shot, as always (night shots high,
        golden shots at 1.0). They are the same in every build.
      * A SKY CHANGE INSIDE A SHOT (the night ends while the camera keeps moving and the actors keep walking):
        st.sky_change(frame, sky). Nothing in the scene changes at that frame: it is one shot, one camera, one
        baked camera path, so nothing can jump and motion blur is that of an uncut shot; the frames before it are
        simply rendered in the old sky's build and the frames from it on in the new one's. Torch levels that should
        change with it: Stage.lights(shot, ..., at=frame). Words: st.sky_change(nar.at("ended"), "gold").
      * DIPS TO BLACK belong to the encode, not to the frames: st.dip(frame, out=3, hold=0, back=3) makes the
        picture black ON `frame` (normally the first frame of a shot) and the `hold` frames after it, fading out
        over the `out` frames before and back in over the `back` frames after; st.fade(frame0, frame1, g0, g1) is
        one ramp of the picture gain (film start: st.fade(1, 7, 0.0, 1.0)). The caption stays at full strength.
        Changing a dip re-encodes and re-renders nothing. They reach render.py through st.fades.
      * What costs what: an edit to one shot re-renders that shot (in its sky's build only); an edit to one entry
        of SKIES re-renders exactly the frames of that sky; re-tagging a shot re-renders that shot; a caption, a
        dip or the narration timing re-renders nothing. Every command builds only the skies it has work in.
    """

    # a SKIES entry: short name -> look.set_time argument, set_time arguments by their own name, compositor arguments
    SKY_SHORT = {"az": "sun_azimuth", "el": "sun_elevation", "key": "key_strength", "ambient": "ambient_strength"}
    SKY_TIME = ("sun_azimuth", "sun_elevation", "key_strength", "ambient_strength", "celestial_size", "clouds",
                "cloud_height", "cloud_radius", "cloud_offset", "star_scale")
    SKY_COMP = ("bloom", "vignette", "grade", "haze")

    def __init__(self, scene, film, v, sky=None, skies=None):
        self.scene, self.film, self.v = scene, film, v
        self.skies = None          # {name: settings} of a film with several skies (None: one sky, built by the film)
        self.sky_name = None       # the name of the sky this build has (None: one sky)
        self._sky_marks = []       # [(frame, sky name or None = the sky in force before it)]
        self.fades = []            # picture-gain ramps (t0, t1, g0, g1) in film seconds for the encoder (dip, fade)
        if skies is not None:
            if not skies or not all(isinstance(k, str) and isinstance(d, dict) for k, d in skies.items()):
                raise ValueError("skies must be a non-empty {name: dict(preset=..., az=..., el=..., ...)}")
            name = next(iter(skies)) if sky is None else sky
            if name not in skies:
                raise KeyError("sky %r is not one of this film's skies %s" % (name, sorted(skies)))
            self.skies, self.sky_name = dict(skies), name
            sky = self.build_sky(scene, skies[name])
        self.sky = sky             # what look.set_time returned: 'sun', 'moon', 'key', 'world', ...
        self.cast = {}             # name -> Character
        self.in_shot = {}          # shot name -> set of character names
        self.heroes = {}           # shot name -> [(label, [objects])]: what the shot is ABOUT (kept in the safe area)
        self._light_keys = False
        self._t = 0.0

    # ---- skies
    @classmethod
    def build_sky(cls, scene, spec):
        """Build one entry of a film's SKIES into the scene: look.set_time (world, key light, sun / moon, stars,
        clouds, haze) and look.setup_compositor (bloom, grade, vignette). Returns set_time's dict."""
        spec = dict(spec)
        if "preset" not in spec:
            raise ValueError("a sky needs a preset ('day' | 'golden' | 'dusk' | 'night'): %r" % (spec,))
        preset = spec.pop("preset")
        time_kw = {long: spec.pop(short) for short, long in cls.SKY_SHORT.items() if short in spec}
        time_kw.update({k: spec.pop(k) for k in cls.SKY_TIME if k in spec})
        comp_kw = {k: spec.pop(k) for k in cls.SKY_COMP if k in spec}
        if spec:
            raise TypeError("unknown sky setting(s) %s; known: preset, %s" % (
                sorted(spec), ", ".join(list(cls.SKY_SHORT) + list(cls.SKY_TIME) + list(cls.SKY_COMP))))
        sky = look.set_time(scene, preset, **time_kw)
        look.setup_compositor(scene, **comp_kw)
        return sky

    def _sky_mark(self, frame, sky):
        if self.skies is None:
            raise ValueError("this Stage has one sky: pass skies=SKIES to Stage() to tag shots with skies")
        if sky is not None and sky not in self.skies:
            raise KeyError("sky %r is not one of this film's skies %s" % (sky, sorted(self.skies)))
        self._sky_marks = [m for m in self._sky_marks if m[0] != int(frame)] + [(int(frame), sky)]

    def sky_change(self, frame, sky):
        """From `frame` on the film is under `sky` (until the next tagged shot or sky_change): a sky change INSIDE a
        shot. The scene itself does not change at that frame (same shot, same camera path, same actors mid-motion):
        only the build that renders the frames does. See the class docstring."""
        if sky is None:
            raise ValueError("sky_change needs the name of the sky that begins at that frame")
        self._sky_mark(frame, sky)

    def sky_segments(self):
        """The film's sky table: [(first frame, last frame, sky name), ...] in film order, covering every frame
        (neighbours under the same sky are merged). None for a film with one sky. render.py reads it."""
        if self.skies is None:
            return None
        first, last = self.film.frame_start, self.film.frame_end
        current = next(iter(self.skies))                     # in force until the first tag: the first sky of SKIES
        runs = [(first, current)]                            # [(frame, sky)]: where a sky begins
        for frame, sky in sorted(self._sky_marks):
            current = current if sky is None else sky
            if frame > last:
                continue
            frame = max(frame, first)
            if runs[-1][0] == frame:
                runs[-1] = (frame, current)
            else:
                runs.append((frame, current))
        ends = [f - 1 for f, _s in runs[1:]] + [last]
        merged = []
        for (a, sky), b in zip(runs, ends):
            if merged and merged[-1][2] == sky:
                merged[-1] = (merged[-1][0], b, sky)
            else:
                merged.append((a, b, sky))
        return merged

    def sky_at(self, frame):
        """Name of the sky a frame is filmed under (None for a film with one sky)."""
        for a, b, sky in self.sky_segments() or ():
            if a <= frame <= b:
                return sky
        return None

    # ---- dips to black (encode time: engine/post.py)
    def fade(self, frame0, frame1, g0=1.0, g1=0.0):
        """One ramp of the PICTURE gain for the encoder: g0 on frame0, g1 on frame1, linear between (1 = untouched,
        0 = black); a g1 below 1 is on frame1 itself too, after it the picture is untouched again unless another
        fade follows. The caption is drawn over it at full strength. Returns the ramps added to self.fades."""
        if not frame1 > frame0:
            raise ValueError("fade: frame1 must come after frame0")
        t = self.film.seconds
        ramps = [(t(frame0), t(frame1), float(g0), float(g1))]
        if g1 < 1.0:
            ramps.append((t(frame1), t(frame1 + 1), float(g1), float(g1)))
        self.fades.extend(ramps)
        return ramps

    def dip(self, frame, out=3, hold=0, back=3):
        """A dip to black centred on a cut: the picture is black ON `frame` (the first frame of the new shot) and on
        the `hold` frames after it, fades out over the `out` frames before it and back in over the `back` frames
        after. dip(f, 3, 0, 3) gives the frames f-3 .. f+3 the gains 1, 2/3, 1/3, 0, 1/3, 2/3, 1. Done by the
        encoder (engine/post.py) on the finished picture, under the caption: no frame is rendered again when a dip
        is added, moved or removed. Returns the ramps added to self.fades."""
        t = self.film.seconds
        ramps = []
        if out > 0:
            ramps.append((t(frame - out), t(frame), 1.0, 0.0))
        if hold > 0 or back <= 0:
            ramps.append((t(frame), t(frame + max(hold, 1)), 0.0, 0.0))
        if back > 0:
            ramps.append((t(frame + hold), t(frame + hold + back), 0.0, 1.0))
        self.fades.extend(ramps)
        return ramps

    # ---- shots
    def shot(self, name, seconds, sky=None):
        """Next shot of the film, `seconds` long, starting where the previous one ended. In a film with several
        skies (Stage(..., skies=SKIES)) `sky` names the sky it is filmed under; default: the sky in force before
        it (the previous shot's, or the one a sky_change inside that shot brought)."""
        s = self.film.shot(name, self._t, self._t + seconds)
        self._t += seconds
        self.in_shot[name] = set()
        if self.skies is not None or sky is not None:
            self._sky_mark(s.frame_start, sky)
        return s

    # ---- cast
    def actor(self, name, profession="farmer", **kw):
        """The villager called `name` (built on first use); profession 'steve' builds the player."""
        c = self.cast.get(name)
        if c is None:
            c = characters.make_player(name) if profession == "steve" else characters.make_villager(name, profession, **kw)
            self.cast[name] = c
        return c

    def use(self, shot, *chars):
        """Declare who is visible in a shot (everyone else is hidden for its duration)."""
        self.in_shot[shot.name].update(c.name for c in chars)

    def hero(self, shot, label, *things):
        """Name what a shot is about (a Character = its head, or any objects). tools/palette_check.py then verifies
        that it sits inside the safe area of a Reel: x 8-82 %, y 14-60 %, clear of the caption and the icons."""
        obs = [t.head if isinstance(t, characters.Character) else t for t in things]
        self.heroes.setdefault(shot.name, []).append((label, obs))

    # ---- torches / lanterns
    def lights(self, shot, scale=1.0, groups=None, near=None, radius=None, extra=(), inside=(), at=None):
        """Torch / lantern light level for one shot: every light = base energy x scale (`groups` = {group: scale}
        overrides); lights farther than `radius` from `near`, or scaled to 0, are left out of the render.
        extra = [((x, y, z), factor), ...] multiplies the light nearest to each point once more (a practical key).
        inside = the light group(s) of the room this shot is filmed IN: only there the room's shadowless fill (the
        stand-in for bounce light) is on; in every other shot the fills are off, so a brightly scaled interior can
        never light the street through its walls.
        at = a frame inside the shot from which these levels hold instead of from its first frame (a second call
        for the same shot: the levels step there, e.g. where a sky_change ends the night)."""
        f = shot.frame_start if at is None else int(at)
        groups = groups or {}
        inside = (inside,) if isinstance(inside, str) else tuple(inside)
        boost = {}
        for point, factor in extra:
            ob = min((o for o in self.v.lantern_lights if o.get("mc_light") != "fill"),
                     key=lambda o: math.dist(o.location, point))
            boost[ob.name] = boost.get(ob.name, 1.0) * factor
        for ob in self.v.lantern_lights:
            group = ob.get("group", "")
            k = groups.get(group, scale)
            if ob.get("mc_light") == "fill":
                if group not in inside:
                    k = 0.0
            elif near is not None and radius is not None and math.dist(ob.location, near) > radius:
                k = 0.0
            k *= boost.get(ob.name, 1.0)
            ob.data.energy = ob["base_energy"] * max(k, 0.0)
            ob.data.keyframe_insert("energy", frame=f)
            ob.hide_render = k <= 0.0
            ob.keyframe_insert("hide_render", frame=f)
        self._light_keys = True

    def key(self, id_block, path, frame, value, index=-1):
        """One CONSTANT key on any property (sun energy per shot, a cutaway, ...)."""
        if index >= 0:
            getattr(id_block, path)[index] = value
            id_block.keyframe_insert(path, index=index, frame=frame)
        else:
            setattr(id_block, path, value)
            id_block.keyframe_insert(path, frame=frame)
        for fc in shots.fcurves_of(id_block):
            if fc.data_path == path:
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"

    def see_through(self, shot, cutaway):
        """Make a cutaway section invisible to the CAMERA only for one shot: the wall still blocks sun and sky
        light and still catches torch light, so the room keeps its real lighting."""
        nxt = shot.frame_end + 1
        for ob in self.v.cutaways[cutaway]:
            self.key(ob, "visible_camera", self.film.frame_start, True)
            self.key(ob, "visible_camera", shot.frame_start, False)
            self.key(ob, "visible_camera", nxt, True)

    def remove(self, shot, cutaway):
        """Really remove a cutaway section for one shot (light comes in through the hole)."""
        nxt = shot.frame_end + 1
        for ob in self.v.cutaways[cutaway]:
            self.key(ob, "hide_render", self.film.frame_start, False)
            self.key(ob, "hide_render", shot.frame_start, True)
            self.key(ob, "hide_render", nxt, False)

    def finish(self):
        """Hide every character outside its shots, make the light keys step at the cuts, finalize the film."""
        for name, c in self.cast.items():
            state = None
            for s in sorted(self.film.shots, key=lambda s: s.frame_start):
                want = name in self.in_shot.get(s.name, ())
                if want != state:
                    c.show(s.frame_start, want)
                    state = want
        if self._light_keys:
            for ob in self.v.lantern_lights:
                for idb in (ob, ob.data):
                    for fc in shots.fcurves_of(idb):
                        for kp in fc.keyframe_points:
                            kp.interpolation = "CONSTANT"
        self.film.finalize()
        return self.film


# ----------------------------------------------------------------------------------------------------
# dusk: "The Bell"
# ----------------------------------------------------------------------------------------------------

def shot_bell(st, s):
    """Close-up of the bell mid-swing on a long lens. The bell sits in the upper half of the safe area, so the
    caption lands on the cobblestone base under it. Seen from the south-east, 20 degrees off its broad face: the west
    lamp (out of frame, camera-left) keys that face warm, the narrow east face stays in shade, and above the well's
    rim the view runs north-west over the square to a lamp post and the dusk sky."""
    v, A = st.v, st.v.anchors
    f0 = s.frame_start
    v.ring_bell(f0, strength=1.0, swings=5)
    v.ring_bell(f0 + 24, strength=1.0, swings=5)          # rung again: the still (1.2 s) is at the top of a swing
    bell = A["bell"]
    s.lens(105, 1.4)
    s.move((1.02, -9.38, 0.92), up(bell, -0.13), (0.93, -9.10, 0.94))
    s.focus(up(bell, 0.0))
    s.handheld(0.012, seed=3)
    st.hero(s, "bell", v.bell)
    # the key is the west lamp; everything behind the bell is one stop under it, so the brass is the brightest thing
    st.lights(s, scale=0.9, groups={"bell_w": 2.4, "bell_e": 0.0, "well": 0.7},
              near=(bell[0], bell[1] + 6.0, bell[2]), radius=20.0)


def shot_run(st, s):
    """Villagers sprint across the square for house_a's door; the camera runs backwards just ahead of them, at
    ground level, with the well, the bell and the last of the sun behind them."""
    v, A = st.v, st.v.anchors
    f0, f1 = s.frame_start, s.frame_end
    path = v.paths["square_to_house_a"]
    # name, profession, sideways offset while crossing the square (+ = north), frames behind the farmer, extra
    group = [("ada", "farmer", 0.0, 0, {}), ("kid", "farmer", 0.85, 5, dict(child=True)),
             ("bo", "librarian", -0.8, 9, {}), ("cy", "shepherd", 0.6, 17, {})]
    lead = None
    for name, prof, side, behind, kw in group:
        c = st.actor(name, prof, **kw)
        pts = [(p[0], p[1] + side * (1.0 if p[0] < 8.0 else 0.15), p[2]) for p in path]
        start = f0 - 10 + behind                             # at full speed in the shot; the farmer is at the step as it ends
        c.place(start, pts[0], yaw_to(pts[0], pts[1]))
        c.walk(start, pts, run=True)
        st.use(s, c)
        lead = lead or c
    v.door_open("house_a", f0 - 2, open=True, frames=1)
    s.lens(24, 2.8)
    s.move((5.5, -7.85, 0.30), (0.0, -6.2, 1.30), (8.45, -7.75, 0.36), (3.6, -6.4, 1.30), ease="linear")
    s.focus(lead.head)
    s.handheld(0.02, seed=5)
    st.hero(s, "lead villager", lead)
    st.lights(s, scale=1.4, groups={"house_a": 2.0}, near=A["square_center"], radius=24.0,
              extra=[((9.7, -7.5, 2.9), 4.0)])               # the torches by the door they run for light their faces
    return f1


def shot_interior(st, s):
    """Inside house_a as the door shuts behind them: the villagers stand at the foot of the one bed nobody came home
    to. One vertical composition, front to back: the empty bed (pillow nearest, lit by the wall torch beside it),
    their faces above it, the door closing in the far wall. The camera looks in over the pillow through the east
    wall, which is invisible to the camera only (it still keeps the daylight out)."""
    v, A = st.v, st.v.anchors
    f0, f1 = s.frame_start, s.frame_end
    bed = v.beds["house_a_bed_2"]                            # the north bed: foot toward the room, pillow at the east wall
    head, foot = bed["head"], bed["foot"]
    door = A["house_a_door"]
    st.see_through(s, "house_a_east")
    bo, cy = st.actor("bo", "librarian"), st.actor("cy", "shepherd")
    kid = st.actor("kid", "farmer", child=True)
    # (the cast ran in the previous shot, so nothing here may be keyed before f0: a pre-roll would cut that run short)
    pillow = (head[0] + 0.1, head[1], head[2] + 0.1)
    # the bed runs up the middle of the frame; the three stand left of its foot, which leaves the door (11 degrees
    # to the right of the bed's axis, far wall) in the clear
    # (0.2 block further right than at first: the shepherd's hat was in the 5 % that tall phones crop off the left;
    # the child half a step further back, so that his whole face stays above the caption band)
    spots = [(bo, (foot[0] - 1.25, foot[1] - 0.07, 1.0)), (cy, (foot[0] - 2.00, foot[1] - 0.85, 1.0)),
             (kid, (foot[0] - 1.66, foot[1] - 0.62, 1.0))]
    for i, (c, pos) in enumerate(spots):
        c.place(f0, pos, yaw_to(pos, pillow))
        c.look_at(f0, pillow, ease=0)                        # they all look at the empty bed
        c.shiver(f0, f1 + 1, seed=i)
    cy.look_at(f0 + 12, bo, ease=6)                          # counting who made it: a glance across at the librarian
    v.door_open("house_a", f0 + 8, open=False, frames=10)
    st.use(s, bo, cy, kid)
    cam0 = (head[0] + 1.20, head[1] + 0.02, 2.42)
    cam1 = (head[0] + 1.05, head[1] + 0.00, 2.40)
    s.lens(26, 2.6)
    s.move(cam0, (foot[0] - 2.8, foot[1] + 0.04, 1.74), cam1)
    s.focus(bo.head)
    s.handheld(0.008, seed=7)
    st.hero(s, "librarian", bo)
    st.hero(s, "shepherd", cy)
    st.lights(s, scale=1.2, groups={"house_a": 1.5}, near=A["house_a_center"], radius=14.0, inside="house_a")


def shot_steve_bell(st, s):
    """The last picture of "The Bell": Steve alone at the bell in the empty square, ringing it again. Seen from the
    south-east at standing height: Steve left of centre from behind his right shoulder (the arm that swings), the
    bell in its niche beyond his hand, the east lamp at the right as the visible key on him, the well behind it, and
    to the left the empty square under the last of the sunset."""
    v, A = st.v, st.v.anchors
    f0, f1 = s.frame_start, s.frame_end
    steve = st.actor("steve", "steve")
    spot = A["bell_ringer"]
    bell = A["bell"]
    steve.place(f0, spot, v.yaws["bell_ringer"])
    steve.look_at(f0, bell, ease=0)
    steve.idle(f0, f1 + 1, seed=3)
    v.ring_bell(f0 - 14, strength=1.0, swings=5)            # it is still swinging from the last time ...
    hit = f0 + 10
    steve.swing_arm(hit)                                    # ... and he hits it again: the arm is furthest forward
    v.ring_bell(hit + 2, strength=1.0, swings=5)            # two frames into the swing, which is when it rings
    st.use(s, steve)
    s.lens(32, 3.2)
    s.move((2.75, -8.55, 1.30), (-2.05, -2.35, 1.20), (2.55, -8.35, 1.30))
    s.focus(steve.head)
    s.handheld(0.012, seed=37)
    st.hero(s, "steve", steve)
    st.hero(s, "bell", v.bell)
    st.lights(s, scale=1.3, groups={"bell_e": 2.6, "bell_w": 1.2}, near=A["square_center"], radius=20.0)


# ----------------------------------------------------------------------------------------------------
# golden hour: "The Nitwit"
# ----------------------------------------------------------------------------------------------------

def shot_villager(st, s):
    """The farmer walks past the big house's wall of logs and cobblestone; medium shot, shallow depth of field
    (reference 2)."""
    v, A = st.v, st.v.anchors
    f0 = s.frame_start
    farmer = st.actor("ada", "farmer")
    a, b = (2.6, 22.95, 0.0), (9.6, 22.95, 0.0)              # along the north wall of house_f, in full sun
    farmer.place(f0 - 26, a, yaw_to(a, b))
    farmer.walk(f0 - 26, [a, b])
    st.use(s, farmer)
    s.lens(42, 2.8)
    s.follow(farmer.root, (2.3, 3.0, 0.80), (2.0, 3.15, 0.80), look_offset=(-0.08, 0.0, 1.16))
    s.focus(farmer.head)
    s.handheld(0.012, seed=11)
    st.hero(s, "farmer", farmer)
    st.lights(s, scale=1.0, near=A["exit_gate"], radius=10.0)


def shot_nitwit(st, s):
    """The nitwit alone at the village edge, sharp; two villagers busy with each other, out of focus behind him."""
    v, A = st.v, st.v.anchors
    f0, f1 = s.frame_start, s.frame_end
    nit = st.actor("nitwit", "nitwit")
    spot = A["nitwit_idle"]
    cam = (6.3, 34.2, 1.5)
    nit.place(f0, spot, yaw_to(spot, (cam[0] + 2.4, cam[1], 0)))
    nit.look_at(f0, (cam[0] + 3.6, cam[1], 1.3), ease=0)
    nit.idle(f0, f1 + 1, seed=4)
    bo, cy = st.actor("bo", "librarian"), st.actor("cy", "mason")
    pb, pc = (12.02, 25.13, 0.0), (13.04, 26.92, 0.0)        # about 5 blocks behind him, either side of his head
    bo.place(f0, pb, yaw_to(pb, pc))
    cy.place(f0, pc, yaw_to(pc, pb))
    bo.idle(f0, f1 + 1, seed=8)
    cy.nod(f0 + 4)
    st.use(s, nit, bo, cy)
    s.lens(66, 2.6)
    s.move(cam, up(spot, 1.34), (cam[0] + 0.25, cam[1] + 0.1, cam[2]))
    s.focus(nit.head)
    s.handheld(0.01, seed=13)
    st.hero(s, "nitwit", nit)
    st.lights(s, scale=1.0, near=spot, radius=14.0)          # (daylight: far torches only cost render time)


def shot_trade(st, s):
    """Steve offers an emerald to the farmer, who stands in his wheat beside his composter; seen over Steve's
    shoulder from where the nitwit would be watching. The emerald and the farmer's face are the picture: both sit
    in the safe area, above the caption."""
    v, A = st.v, st.v.anchors
    f0, f1 = s.frame_start, s.frame_end
    farmer = st.actor("ada", "farmer")
    steve = st.actor("steve", "steve")
    if steve.held is None:
        steve.hold(props.make_item("emerald", v.collection))
    fpos = A["farm_work"]
    spos = (fpos[0] + 1.0, fpos[1], 1.0)                    # on the farm's log frame, east of the farmer
    cam0, cam1 = (-8.50, -2.90, 2.56), (-8.70, -2.75, 2.56)
    steve.place(f0, spos, yaw_to(spos, fpos))
    farmer.place(f0, fpos, yaw_to(fpos, spos))               # (both placed before either looks at the other)
    steve.raise_arm(f0 - 4, angle=55, ease=3)                # the hand held up between them, at the farmer's chest
    steve.look_at(f0, farmer, ease=0)
    steve.idle(f0, f1 + 1, seed=2)
    farmer.look_at(f0, steve, ease=0)                        # (looking DOWN at the emerald would hide his face under the hat)
    farmer.idle(f0, f1 + 1, seed=6)
    st.use(s, farmer, steve)
    s.lens(50, 3.4)
    s.move(cam0, (-11.25, -5.33, 2.16), cam1)
    s.focus(farmer.head)
    s.handheld(0.01, seed=17)
    st.hero(s, "emerald", steve.held)
    st.hero(s, "farmer", farmer)
    st.lights(s, scale=1.0, near=fpos, radius=20.0)


def shot_hall(st, s):
    """The trading hall: villagers shut in a row of 1x1 cells behind their job blocks. The camera rides along the
    counter itself, a hand from the cell fronts at their eye height, and looks down the row at about 20 degrees:
    the nearest face fills over a quarter of the frame, clear in its window, the next ones line up behind it, each
    between the iron-bar grilles that divide the cells."""
    v, A = st.v, st.v.anchors
    f0, f1 = s.frame_start, s.frame_end
    first = 3                                                  # the nearest of the faces: cell 3 (the toolsmith)
    near = A["cell_%d" % first]
    front = near[1] + 1.30                                     # y of the cell fronts (the villagers stand 1.3 behind)
    cam0 = (near[0] - 3.05, front + 0.26, 1.62)
    cam1 = (near[0] - 2.65, front + 0.26, 1.62)                # dollying east along the counter
    cells = []
    for i, prof in enumerate(v.cell_professions, 1):
        c = st.actor("cell%d" % i, prof, level=3)
        c.place(f0, A["cell_%d" % i], v.yaws["cell_%d" % i])
        c.look_at(f0, cam0, ease=0)                          # they all watch whoever walks down the aisle ...
        c.look_at(f0 + 2, cam1, ease=max(4, f1 - f0 - 4))    # ... and their heads follow
        c.idle(f0, f1 + 1, seed=20 + i)
        cells.append(c)
    st.use(s, *cells)
    s.lens(38, 3.4)
    aim0 = (cam0[0] + 3.62, cam0[1] - 1.70, 1.47)             # 25 degrees off the row, just below eye height
    s.move(cam0, aim0, cam1, (aim0[0] + 0.40, aim0[1], aim0[2]), ease="linear")
    s.focus(cells[first - 1].head)
    s.focus(cells[first].head, at_s=s.start_s + 0.7, rack_s=0.3)
    s.handheld(0.006, seed=19)
    for i in (first - 1, first):
        st.hero(s, "cell %d" % (i + 1), cells[i])
    st.lights(s, scale=0.0, groups={"hall": 0.8}, inside="hall")


def shot_meadow(st, s):
    """The nitwit walks out the exit road into the open meadow. Three-quarter rear view, so his nose and crossed
    arms cut a profile against the sky; the sun stands in the upper left, the road and the flat meadow ahead."""
    v, A = st.v, st.v.anchors
    f0 = s.frame_start
    nit = st.actor("nitwit", "nitwit")
    road = [(0.5, 25.5, -0.06), (0.6, 31.0, -0.06), (0.4, 38.0, -0.06), (0.5, 46.0, 0.0)]
    nit.place(f0 - 40, road[0], yaw_to(road[0], road[1]))
    nit.walk(f0 - 40, road)
    here = nit.pos_at(f0 + 12)
    # a long look to his left as he goes, HELD to the last frame: his profile (nose, brow, crossed arms) against the
    # sky. (With the head back to the front the last frames were a pink box on a green box.)
    end = nit.pos_at(s.frame_end)
    nit.look_at(f0, (here.x - 4.0, here.y + 0.6, 1.9), ease=0)
    nit.look_at(f0 + 12, (end.x - 6.0, end.y + 0.9, 4.0), ease=10)      # ... and up, at the open sky
    st.use(s, nit)
    s.lens(28, 3.2)
    # the camera walks low behind him on his left, on the plant-free verge (village.CAMERA_LANE), looking north-east
    # (40 degrees off his heading) and falling behind: his head stands against the sky, the sun in the upper left,
    # and he gets smaller as he goes
    s.follow(nit.root, (-2.62, -3.12, 0.78), (-2.95, -3.80, 0.74), look_offset=(0.50, 0.30, 1.76))
    s.focus(nit.head)
    s.handheld(0.012, seed=23)
    st.hero(s, "nitwit", nit)
    st.lights(s, scale=1.0, near=A["exit_gate"], radius=14.0)


# ----------------------------------------------------------------------------------------------------
# reference 1 and reference 3
# ----------------------------------------------------------------------------------------------------

def shot_steve_bed(st, s):
    """Steve asleep in house_a's red bed, golden light over him (reference 1): seen from beside the foot of the bed,
    so the bed reads as a bed: red blanket side, white pillow, oak legs."""
    v, A = st.v, st.v.anchors
    f0 = s.frame_start
    steve = st.actor("steve", "steve")
    steve.lie_down(f0, A["house_a_bed_2"], v.yaws["house_a_bed_2"])
    st.use(s, steve)
    st.remove(s, "house_a_east")                            # open set, as in the reference: the low sun reaches the bed
    st.remove(s, "house_a_roof")
    head = steve.eye_point(f0)
    s.lens(35, 2.2)
    s.move((17.45, -8.50, 2.28), (head[0] - 0.10, head[1] + 0.05, head[2] - 0.22), (17.60, -8.46, 2.26))
    s.focus(steve.head)
    s.handheld(0.008, seed=29)
    st.hero(s, "steve", steve)
    st.lights(s, scale=1.5, near=A["house_a_center"], radius=12.0, inside="house_a")


def shot_night(st, s):
    """The east street at night: lamp posts, the square moon with its halo, stars (reference 3)."""
    v, A = st.v, st.v.anchors
    s.lens(30, 2.8)
    s.move((24.6, 0.9, 0.95), (6.0, -0.2, 6.3), (24.2, 0.9, 0.97))
    s.focus((16.5, -2.5, 3.6))
    s.handheld(0.01, seed=31)
    st.lights(s, scale=1.3)


SHOT_BUILDERS = {
    "bell": shot_bell, "run": shot_run, "interior": shot_interior, "steve_bell": shot_steve_bell,
    "villager": shot_villager,
    "nitwit": shot_nitwit, "trade": shot_trade, "hall": shot_hall, "meadow": shot_meadow,
    "steve_bed": shot_steve_bed, "night": shot_night,
}


def build_film(scene, key):
    """Build one of the look-dev films (a key of FILMS) into `scene`; returns what render.py expects."""
    cfg = FILMS[key]
    v = village.build_village(scene, seed=1, bed_colors=cfg.get("beds"))
    sky = look.set_time(scene, cfg["preset"], sun_azimuth=cfg["az"], sun_elevation=cfg["el"],
                        key_strength=cfg["key"], ambient_strength=cfg["ambient"])
    look.setup_compositor(scene, bloom=cfg["bloom"], grade=cfg["grade"])
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, sky)
    for name, seconds in cfg["shots"]:
        SHOT_BUILDERS[name](st, st.shot(name, seconds))
    st.finish()
    caps = captions.autotime(cfg["script"], **cfg["timing"])
    return {"film": film, "captions": caps, "stage": st}


def build(scene):
    """`$BPY -m render lookdev ...` builds the dusk look-dev film."""
    return build_film(scene, "lookdev_dusk")


def still_frame(film, name):
    """Frame number of the look-dev still of shot `name`."""
    shot = next(s for s in film.shots if s.name == name)
    return min(shot.frame_end, shot.frame_start + int(round(STILLS[name][1] * film.fps)))


def main(argv=None):
    """Render look-dev stills through render.py's Session: out/test/lookdev_<name>.png (+ _captioned.png)."""
    import argparse

    from PIL import Image

    import render as R
    from engine import post

    ap = argparse.ArgumentParser(prog="films.lookdev")
    ap.add_argument("names", nargs="*", help="still names (default: all): " + " ".join(ORDER))
    ap.add_argument("--res", type=R._parse_res, default=R.FINAL_RES)
    ap.add_argument("--samples", type=int, default=R.FINAL_SAMPLES)
    ap.add_argument("--threads", type=int, default=R.FINAL_THREADS)
    ap.add_argument("--captioned", action="store_true",
                    help="also write lookdev_<name>_captioned.png at 1080x1920 for " + " and ".join(CAPTIONED))
    ap.add_argument("--caption-all", action="store_true", help="... for every still rendered")
    ap.add_argument("--no-motion-blur", action="store_true")
    ap.add_argument("--suffix", default="", help="appended to the file name (for experiments)")
    ap.add_argument("--no-check", action="store_true", help="skip the palette / composition checks of each still")
    ap.add_argument("--zones", action="store_true", help="also write lookdev_<name>_zones.png with the Reels UI zones")
    args = ap.parse_args(sys.argv[1:] if argv is None else argv)
    names = args.names or ORDER
    out_dir = os.path.join(ROOT, "out", "test")
    timings = {}
    failed = []
    for key in FILMS:
        wanted = [n for n in names if STILLS[n][0] == key]
        if not wanted:
            continue
        ses = R.Session(key)
        ses.configure(args.res, args.samples, args.threads, False if args.no_motion_blur else None)
        for n in wanted:
            frame = still_frame(ses.film, n)
            path = os.path.join(out_dir, "lookdev_%s%s.png" % (n, args.suffix))
            t = time.time()
            ses.render_frame(frame, path)
            timings[n] = time.time() - t
            print("[lookdev] %-10s frame %3d of %s -> %s  %.1fs" % (n, frame, key, path, timings[n]), flush=True)
            if args.caption_all or (args.captioned and n in CAPTIONED):
                word = captions.caption_at(ses.captions, ses.film.seconds(frame))
                with Image.open(path) as im:
                    post.finish_frame(im, word).save(path[:-4] + "_captioned.png")
                print("[lookdev]   caption %r -> %s_captioned.png" % (word, path[:-4]))
            if args.zones:
                with Image.open(path) as im:
                    post.draw_zones(im).save(path[:-4] + "_zones.png")
            if not args.no_check:
                # the picture against the game textures it was made from, and the heroes against the safe area
                from tools import palette_check

                stage = ses.result.get("stage")
                rec = palette_check.probe(ses.scene)
                rep = palette_check.evaluate(rec, path, heroes=stage.heroes.get(n, ()) if stage else ())
                if palette_check.print_report(n, rep):
                    failed.append(n)
    if timings:
        worst = max(timings, key=timings.get)
        print("[lookdev] render seconds per still:", {k: round(t, 1) for k, t in timings.items()},
              "worst:", worst, round(timings[worst], 1))
    if not args.no_check:
        print("[lookdev] palette / composition checks:", "all passed" if not failed else "FAILED in " + ", ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
