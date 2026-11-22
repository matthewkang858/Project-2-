"""Cameras, hard cuts, camera moves, focus pulls and hand-held drift (owned by role LOOK).

    film = Film(scene)                               # 24 fps; frame 1 = second 0
    s = film.shot("bell", 0.0, 3.0)                  # one camera per shot, consecutive shots cut hard
    s.lens(85, fstop=1.8)                            # full-frame lens in mm; fstop is "cinema" f-stop (see below)
    s.move((4, -6, 1.2), (0, 0, 2.0), (3, -5, 1.4))  # position + aim at the start, optional position/aim at the end
    s.focus(villager.head)                           # object or point; call again with at_s=... for a rack focus
    s.handheld(0.02, seed=3)
    film.finalize()                                  # timeline markers bind each camera to its frames

Time is in film seconds everywhere (`at_s` too); `film.frame(seconds)` converts to the frame number that
characters are keyed with. Targets may be points `(x, y, z)` or objects (then the aim / focus follows the object).

Framing: vertical 9:16 with the 36 mm side of a full-frame sensor vertical (Blender sensor_fit AUTO), so
`lens(50)` frames like a 50 mm lens on a camera turned to portrait: vertical field of view 39.6 deg, horizontal
22.9 deg; 85 mm = 23.9 / 13.6 deg; 135 mm = 15.2 / 8.6 deg; 35 mm = 54.4 / 32.3 deg.

Depth of field: a block is one metre, so a real f/1.8 looks almost sharp everywhere at block scale. The f-stop
given to `lens()` is multiplied by DOF_FSTOP_SCALE before it reaches Cycles, which gives the "miniature / shader
pack" look of the references: lens(85, 1.8) focused 5 blocks away melts everything 3 blocks behind it.
Use fstop 1.2-2 for hero close-ups, 2.8-4 for wides where the set must read, fstop=None for no blur at all.
"""
import math

import bpy
import numpy as np
from mathutils import Vector

DOF_FSTOP_SCALE = 0.28      # Cycles aperture f-stop = fstop * DOF_FSTOP_SCALE
CLIP_END = 20000.0          # beyond the sky quads of look.set_time (radius 2400)
APERTURE_BLADES = 4         # square bokeh ...
APERTURE_ROTATION = 0.0     # ... with its sides level (Cycles' 4-gon has a flat side up at rotation 0)

EASES = {
    "linear": lambda u: u,
    "smooth": lambda u: u * u * (3.0 - 2.0 * u),
    "ease_in": lambda u: u * u,
    "ease_out": lambda u: 1.0 - (1.0 - u) * (1.0 - u),
}


def fcurves_of(id_block):
    """All F-curves animating an ID (Blender 5.x keeps them in action layers / strips / channelbags)."""
    ad = getattr(id_block, "animation_data", None)
    if ad is None or ad.action is None:
        return []
    act = ad.action
    if hasattr(act, "fcurves"):                       # Blender <= 4.3
        return list(act.fcurves)
    out = []
    slot = getattr(ad, "action_slot", None)
    for layer in act.layers:
        for strip in layer.strips:
            if slot is not None:
                bag = strip.channelbag(slot)
                if bag is not None:
                    out.extend(bag.fcurves)
            else:
                for bag in strip.channelbags:
                    out.extend(bag.fcurves)
    return out


def _linearize(id_block):
    """Baked per-frame keys: straight segments, so sub-frame motion blur follows the baked path exactly."""
    for fc in fcurves_of(id_block):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"


def _clear_anim(ob):
    if ob.animation_data is not None:
        ob.animation_data_clear()


class Film:
    """A sequence of shots on one timeline; one camera per shot, switched by timeline markers."""

    def __init__(self, scene, fps=24):
        self.scene = scene
        self.fps = int(fps)
        self.shots = []
        scene.render.fps = self.fps
        scene.render.fps_base = 1.0
        self.collection = bpy.data.collections.new("film_cameras")
        scene.collection.children.link(self.collection)

    def frame(self, seconds):
        """Frame number at a film time in seconds (second 0 = frame 1)."""
        return int(round(float(seconds) * self.fps)) + 1

    def seconds(self, frame):
        """Film time in seconds of a frame number."""
        return (frame - 1) / float(self.fps)

    def shot(self, name, start_s, end_s):
        """Add a shot covering [start_s, end_s) seconds; returns the Shot (its camera exists immediately)."""
        s = Shot(self, name, start_s, end_s)
        self.shots.append(s)
        return s

    def shot_at(self, frame):
        """The shot that owns a frame (clamped to the first / last shot)."""
        shots = sorted(self.shots, key=lambda s: s.frame_start)
        if not shots:
            return None
        cur = shots[0]
        for s in shots:
            if s.frame_start <= frame:
                cur = s
        return cur

    def camera_at(self, frame):
        """The camera object that films a frame."""
        s = self.shot_at(frame)
        return s.camera if s else None

    @property
    def frame_start(self):
        """First frame of the film."""
        return min(s.frame_start for s in self.shots) if self.shots else 1

    @property
    def frame_end(self):
        """Last frame of the film (inclusive)."""
        return max(s.frame_end for s in self.shots) if self.shots else 1

    @property
    def duration(self):
        """Length of the film in seconds."""
        return (self.frame_end - self.frame_start + 1) / float(self.fps)

    def goto(self, frame):
        """Set the scene to a frame with the right shot camera active (use before rendering a frame yourself)."""
        self.scene.camera = self.camera_at(frame)
        self.scene.frame_set(int(frame))
        self.scene.camera = self.camera_at(frame)
        return self.scene.camera

    def finalize(self):
        """Bake every shot, bind each camera to a timeline marker and set the scene frame range; returns self."""
        scene = self.scene
        self.shots.sort(key=lambda s: s.frame_start)
        for a, b in zip(self.shots, self.shots[1:]):
            if b.frame_start != a.frame_end + 1:
                print(f"[shots] warning: shot '{b.name}' starts at frame {b.frame_start}, "
                      f"but '{a.name}' ends at {a.frame_end}")
        for m in [m for m in scene.timeline_markers if m.name.startswith("shot_")]:
            scene.timeline_markers.remove(m)
        for s in self.shots:
            s._bake()
            s._bake_focus()
            m = scene.timeline_markers.new("shot_" + s.name, frame=s.frame_start)
            m.camera = s.camera
        scene.frame_start = self.frame_start
        scene.frame_end = self.frame_end
        self.goto(self.frame_start)
        return self


class Shot:
    """One camera and its move, aim, focus and drift between frame_start and frame_end (inclusive)."""

    def __init__(self, film, name, start_s, end_s):
        self.film = film
        self.name = name
        self.start_s, self.end_s = float(start_s), float(end_s)
        self.frame_start = film.frame(start_s)
        self.frame_end = max(self.frame_start, film.frame(end_s) - 1)
        col = film.collection

        cam = bpy.data.cameras.new("cam_" + name)
        cam.sensor_fit = "AUTO"
        cam.sensor_width = 36.0
        cam.lens = 50.0
        cam.clip_start = 0.05
        cam.clip_end = CLIP_END
        # a four-bladed aperture: defocused highlights (the square sun, torch flames, lanterns) melt
        # into SQUARES with level edges, so the blur itself stays blocky instead of turning the sun into a ball
        cam.dof.aperture_blades = APERTURE_BLADES
        cam.dof.aperture_rotation = APERTURE_ROTATION
        self.camera = bpy.data.objects.new("cam_" + name, cam)
        col.objects.link(self.camera)

        self._aim_base = self._empty("aim_base_" + name)
        self._aim = self._empty("aim_" + name)
        self._aim.parent = self._aim_base
        self._focus = self._empty("focus_" + name)
        track = self.camera.constraints.new("TRACK_TO")
        track.name = "aim"
        track.target = self._aim
        track.track_axis = "TRACK_NEGATIVE_Z"
        track.up_axis = "UP_Y"
        cam.dof.focus_object = self._focus

        self._anchor_cache = {}
        self._mode = "move"
        self._pos = (Vector((0.0, -8.0, 1.6)), Vector((0.0, -8.0, 1.6)))
        self._targets = ((0.0, 0.0, 1.2), (0.0, 0.0, 1.2))
        self._ease = "smooth"
        self._follow = None
        self._look_offset = Vector((0.0, 0.0, 0.0))
        self._hand = (0.0, 0)
        self._focus_keys = []
        self._fstop = 1.8
        self.lens(50.0, 1.8)
        self._bake()
        self._bake_focus()

    # ---------------------------------------------------------------- helpers
    def _empty(self, name):
        ob = bpy.data.objects.new(name, None)
        ob.empty_display_size = 0.2
        self.film.collection.objects.link(ob)
        return ob

    def _anchor(self, target, tag):
        """Object targets are used directly; points become a static empty."""
        if isinstance(target, bpy.types.Object):
            return target
        key = (tag,) + tuple(round(float(c), 4) for c in target)
        ob = self._anchor_cache.get(key)
        if ob is None:
            ob = self._empty(f"{tag}_{self.name}_{len(self._anchor_cache)}")
            ob.location = Vector(target)
            self._anchor_cache[key] = ob
        return ob

    def _frames(self):
        return range(self.frame_start, self.frame_end + 2)      # one past the end: the last frame still moves

    def _u(self, frame):
        span = max(1, self.frame_end + 1 - self.frame_start)
        return min(1.0, max(0.0, (frame - self.frame_start) / float(span)))

    def _drift(self, frame, channel):
        """Smooth seeded noise vector in [-1, 1]^3 for hand-held drift (sum of slow sines)."""
        amount, seed = self._hand
        if amount <= 0:
            return Vector((0.0, 0.0, 0.0))
        rng = np.random.default_rng([int(seed), int(channel), 7919])
        freq = rng.uniform(0.12, 0.85, (3, 3))                   # Hz
        phase = rng.uniform(0.0, 2.0 * math.pi, (3, 3))
        weight = np.array([0.6, 0.3, 0.1])
        t = frame / float(self.film.fps)
        v = (np.sin(2.0 * math.pi * freq * t + phase) * weight).sum(axis=1)
        return Vector(v.tolist())

    # ---------------------------------------------------------------- public API
    def lens(self, mm, fstop=1.8):
        """Focal length in mm (full-frame, 36 mm side vertical) and cinema f-stop; fstop=None turns blur off."""
        cam = self.camera.data
        cam.lens = float(mm)
        self._fstop = fstop
        if fstop:
            cam.dof.use_dof = True
            cam.dof.aperture_fstop = max(0.03, float(fstop) * DOF_FSTOP_SCALE)
        else:
            cam.dof.use_dof = False
        return self

    def move(self, pos0, target0, pos1=None, target1=None, ease="smooth"):
        """Camera position and aim at the start of the shot, optionally moving to pos1 / target1 by its end.

        Targets are points or objects (an object target is followed while it moves).
        ease: 'linear' | 'smooth' | 'ease_in' | 'ease_out'.
        """
        assert ease in EASES, "ease must be one of %s" % sorted(EASES)
        self._mode = "move"
        self._follow = None
        p0 = Vector(pos0)
        self._pos = (p0, Vector(pos1) if pos1 is not None else p0.copy())
        self._targets = (target0, target1 if target1 is not None else target0)
        self._ease = ease
        self._bake()
        return self

    def follow(self, obj, offset0, offset1=None, look_offset=(0.0, 0.0, 0.0), ease="linear"):
        """Tracking shot: the camera rides at obj's location + offset (offset0 -> offset1), aimed at obj + look_offset."""
        assert ease in EASES, "ease must be one of %s" % sorted(EASES)
        self._mode = "follow"
        self._follow = obj
        o0 = Vector(offset0)
        self._pos = (o0, Vector(offset1) if offset1 is not None else o0.copy())
        self._look_offset = Vector(look_offset)
        self._targets = (obj, obj)
        self._ease = ease
        self._bake()
        return self

    def focus(self, target, at_s=None, rack_s=0.5):
        """Focus on an object or point. With at_s (film seconds) the focus pulls to it starting then, over rack_s.

        One call = fixed focus for the whole shot. For a rack focus call it twice:
        `focus(a)` then `focus(b, at_s=7.0)` holds `a` until 7.0 s and reaches `b` at 7.5 s.
        Without any call the focus stays on the aim target.
        """
        anchor = self._anchor(target, "focus_at")
        if at_s is None or not self._focus_keys:
            self._focus_keys = [(self.frame_start, anchor, 0)]
        else:
            f = min(self.frame_end, max(self.frame_start, self.film.frame(at_s)))
            self._focus_keys.append((f, anchor, max(1, int(round(rack_s * self.film.fps)))))
            self._focus_keys.sort(key=lambda k: k[0])
        self._bake_focus()
        return self

    def handheld(self, amount=0.02, seed=0):
        """Subtle seeded camera drift: `amount` blocks of sway on the position and on the aim point."""
        self._hand = (float(amount), int(seed))
        self._bake()
        return self

    # ---------------------------------------------------------------- baking
    def _bake(self):
        cam, base, aim = self.camera, self._aim_base, self._aim
        for ob in (cam, base, aim):
            _clear_anim(ob)
        for ob in (cam, base):
            for c in [c for c in ob.constraints if c.type == "COPY_LOCATION"]:
                ob.constraints.remove(c)
        ease = EASES[self._ease]
        amount = self._hand[0]

        if self._mode == "follow":
            c = cam.constraints.new("COPY_LOCATION")          # camera = followed object + keyed offset
            c.name = "follow"
            c.target = self._follow
            c.use_offset = True
            cam.constraints.move(len(cam.constraints) - 1, 0)   # before the Track To
        a0 = self._anchor(self._targets[0], "aim_at")
        a1 = self._anchor(self._targets[1], "aim_at")
        base.location = (0.0, 0.0, 0.0)
        c0 = base.constraints.new("COPY_LOCATION")
        c0.name = "aim0"
        c0.target = a0
        c1 = None
        if a1 is not a0:
            c1 = base.constraints.new("COPY_LOCATION")
            c1.name = "aim1"
            c1.target = a1

        look = self._look_offset if self._mode == "follow" else Vector((0.0, 0.0, 0.0))
        for f in self._frames():
            e = ease(self._u(f))
            cam.location = self._pos[0].lerp(self._pos[1], e) + self._drift(f, 0) * amount
            cam.keyframe_insert("location", frame=f)
            aim.location = look + self._drift(f, 1) * amount
            aim.keyframe_insert("location", frame=f)
            if c1 is not None:
                c1.influence = e
                base.keyframe_insert('constraints["aim1"].influence', frame=f)
        for ob in (cam, base, aim):
            _linearize(ob)
        if not self._focus_keys:
            self._bake_focus()

    def _bake_focus(self):
        foc = self._focus
        _clear_anim(foc)
        for c in list(foc.constraints):
            foc.constraints.remove(c)
        keys = self._focus_keys or [(self.frame_start, self._aim, 0)]
        for i, (frame, anchor, rack) in enumerate(keys):
            c = foc.constraints.new("COPY_LOCATION")
            c.name = "focus%d" % i
            c.target = anchor
            if i == 0:
                continue
            path = 'constraints["%s"].influence' % c.name
            for f in range(frame - 1, frame + rack + 2):
                u = min(1.0, max(0.0, (f - frame) / float(rack)))
                c.influence = u * u * (3.0 - 2.0 * u)
                foc.keyframe_insert(path, frame=f)
        _linearize(foc)


# --------------------------------------------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    import time

    from . import look

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=True)
    look.standin_scene(scene)
    look.set_time(scene, "golden", sun_azimuth=215.0)
    look.setup_compositor(scene, grade="warm")

    mover = bpy.data.objects.new("mover", None)              # stands in for a running character
    scene.collection.objects.link(mover)
    mover.location = (-2.5, -6.0, 0.0)
    mover.keyframe_insert("location", frame=36)
    mover.location = (-2.5, -3.0, 0.0)                       # 6 blocks per second: villager panic speed
    mover.keyframe_insert("location", frame=48)
    _linearize(mover)
    body = look._box("mover_body", (-0.25, -0.25, 0.0), (0.25, 0.25, 1.0), bpy.data.materials["standin_stone_bricks"],
                     scene.collection)
    body.parent = mover

    film = Film(scene)
    a = film.shot("wide", 0.0, 0.5)
    a.lens(35, 2.8)
    a.move((1.5, -9.0, 1.1), (0.5, 3.0, 1.8), (1.0, -8.0, 1.1))
    a.handheld(0.03, seed=1)
    b = film.shot("long", 0.5, 1.5)
    b.lens(85, 1.8)
    b.move((-1.0, -9.5, 0.7), (-3.0, 1.5, 1.2), (-0.4, -9.5, 0.7), ease="linear")
    b.focus((-3.0, 1.0, 1.2))
    b.focus((-9.0, 14.0, 3.0), at_s=0.9, rack_s=0.4)
    c = film.shot("track", 1.5, 2.0)
    c.lens(50, 2.0)
    c.follow(mover, (3.5, -1.5, 0.4), look_offset=(0, 0, 0.6))
    c.focus(mover)
    film.finalize()
    print("frames", film.frame_start, film.frame_end, "duration", film.duration,
          [(s.name, s.frame_start, s.frame_end) for s in film.shots],
          [(m.name, m.frame, m.camera.name) for m in scene.timeline_markers])

    out = os.path.join(look.ROOT, "out", "test")
    for tag, frame in (("wide", 6), ("long_a", 14), ("long_b", 34), ("track", 44)):
        film.goto(frame)
        scene.render.filepath = os.path.join(out, f"shots_{tag}.png")
        t = time.time()
        bpy.ops.render.render(write_still=True)
        cam = scene.camera
        print(f"wrote {scene.render.filepath} frame {frame} cam {cam.name} lens {cam.data.lens} "
              f"fstop {cam.data.dof.aperture_fstop:.2f} in {time.time() - t:.1f}s")
