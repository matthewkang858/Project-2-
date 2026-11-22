"""Scene fingerprints: what a rendered frame depends on, measured on the BUILT SCENE instead of on source files
(owned by role LOOK; used by render.py to decide which frames on disk are still the film).

    fp = stamp.Fingerprinter(scene, film)
    fp.frame(37)          # {"fp": "9c1e...", "parts": {"g": ..., "c": ..., "o": ..., "l": ...}}

A frame's fingerprint is a hash of everything Cycles is given for that frame and nothing else:

  g  the global look: render / Cycles / colour-management settings (not threads, not file paths), the view layer's
     passes, the world (sky maps included, pixel by pixel) and the compositor tree;
  c  the shot camera that films the frame: lens, aperture, clip range, its world matrix and the focus point;
  o  every mesh object that is rendered at that frame: geometry, UVs, custom normals, its materials (node trees,
     socket values and the pixels of every texture), ray-visibility flags and its world matrix;
  l  every light that is on at that frame: all of its settings (energy at that frame) and its world matrix.

Matrices are sampled over the frame's exposure (motion blur: shutter open, middle, close). Hidden objects, empties
and the cameras of other shots are left out, and neither names nor the order of creation enter the hash, so:

  - editing a caption, a comment, the timing of the words or anything else that changes no picture changes no
    fingerprint: nothing is rendered again;
  - editing one shot changes the fingerprints of that shot's frames only (a character added for shot 4 is hidden
    in shots 1-3 and does not touch them);
  - changing the sky, the grade, a texture, the village or the render settings changes every fingerprint.

Cost: three depsgraph evaluations per frame (about 15 ms each on the village), no rendering.
"""
import hashlib
import math

import bpy
import numpy as np

from .shots import fcurves_of

VERSION = 1

# properties that never reach the renderer, or differ from one Blender session to the next
_SKIP = {
    "rna_type", "bl_rna", "name", "name_full", "session_uid", "users", "tag", "is_evaluated", "original", "id_data",
    "preview", "is_runtime_data", "use_fake_user", "use_extra_user", "is_editable", "is_embedded_data", "is_missing",
    "is_library_indirect", "library", "library_weak_reference", "override_library", "asset_data", "animation_data",
    "id_type", "depsgraph", "filepath", "filepath_raw", "is_dirty", "bindcode", "has_data", "frame_current",
    "frame_current_final", "frame_float", "frame_subframe", "threads", "threads_mode", "use_file_extension",
    "is_movie_format", "file_extension", "layer_collection", "active_layer_collection", "statistics",
    "use_persistent_data", "use_lock_interface", "interface",
}
_SKIP_PREFIX = ("bl_", "show_", "preview_", "active_")
# object properties covered by the per-frame record (matrices, visibility) or irrelevant to a render
_OBJECT_SKIP = {
    "location", "scale", "dimensions", "bound_box", "data", "children", "children_recursive", "material_slots",
    "users_collection", "users_scene", "constraints", "mode", "color", "pose", "motion_path",
    "animation_visualization", "track_axis", "up_axis", "field", "collision", "rigid_body", "rigid_body_constraint",
    "soft_body", "particle_systems", "vertex_groups", "is_instancer", "is_from_instancer", "is_from_set",
    "pass_index", "type", "image_user", "instance_collection", "select",
}
_OBJECT_SKIP_PREFIX = ("delta_", "matrix_", "rotation_", "empty_", "display", "hide_", "visible_", "parent", "lock_",
                       "select_", "use_empty", "use_grease", "use_mesh_mirror", "use_shape", "use_dynamic")
_NODE_SKIP = {"inputs", "outputs", "internal_links", "parent", "location", "location_absolute", "width", "height",
              "dimensions", "select", "label", "color", "use_custom_color", "hide", "warning_propagation",
              "color_tag", "width_hidden"}
_OBJECT_ANIM_OK = ("location", "rotation_euler", "rotation_quaternion", "rotation_axis_angle", "scale",
                   "hide_render", "hide_viewport", "visible_camera", "visible_diffuse", "visible_glossy",
                   "visible_transmission", "visible_volume_scatter", "visible_shadow")
_RAY_FLAGS = ("visible_camera", "visible_diffuse", "visible_glossy", "visible_transmission",
              "visible_volume_scatter", "visible_shadow")


def _h(text):
    return hashlib.sha1(text.encode("utf-8", "replace")).hexdigest()[:16]


def _bytes(arr):
    return hashlib.sha1(np.ascontiguousarray(arr).tobytes()).hexdigest()[:16]


class Fingerprinter:
    """Content digests of one built film, cached per datablock; frame(f) gives the fingerprint of frame f."""

    def __init__(self, scene, film):
        self.scene, self.film = scene, film
        self._cache = {}
        self._global = None
        self._dynamic = {}

    # ---- values -----------------------------------------------------------------------------------
    def _value(self, v):
        if isinstance(v, bool):
            return "T" if v else "F"
        if isinstance(v, int):
            return str(v)
        if isinstance(v, float):
            return "%.6g" % (v + 0.0)
        if isinstance(v, str):
            return v
        if v is None:
            return "None"
        if isinstance(v, bpy.types.ID):
            return self.id_ref(v)
        if isinstance(v, (set, frozenset)):
            return "{" + ",".join(sorted(str(x) for x in v)) + "}"
        try:
            return "(" + ",".join(self._value(x) for x in v) + ")"
        except TypeError:
            return type(v).__name__

    def _walk(self, out, struct, depth, skip=(), skip_prefix=()):
        """Append `identifier=value` for every RNA property of `struct` (pointers and collections `depth` deep)."""
        try:
            props = struct.bl_rna.properties
        except AttributeError:
            return
        for prop in props:
            key = prop.identifier
            if key in _SKIP or key in skip or key.startswith(_SKIP_PREFIX) or (skip_prefix and key.startswith(skip_prefix)):
                continue
            try:
                val = getattr(struct, key)
            except Exception:                                    # noqa: BLE001 - unreadable in this context
                continue
            t = prop.type
            if t == "POINTER":
                if val is None:
                    out.append(key + "=None")
                elif isinstance(val, bpy.types.ID):
                    out.append(key + "=" + self.id_ref(val))
                elif depth > 0:
                    out.append(key + "{")
                    self._walk(out, val, depth - 1)
                    out.append("}")
            elif t == "COLLECTION":
                if depth > 0:
                    out.append(key + "[")
                    for i, item in enumerate(val):
                        if i >= 512:
                            out.append("...%d" % len(val))
                            break
                        if isinstance(item, bpy.types.ID):
                            out.append(self.id_ref(item))
                        else:
                            self._walk(out, item, depth - 1)
                        out.append("|")
                    out.append("]")
            else:
                out.append(key + "=" + self._value(val))

    # ---- datablocks -------------------------------------------------------------------------------
    def is_dynamic(self, idb):
        """True when an ID (or its embedded node tree) carries animation that the per-frame record does not cover:
        its digest is then taken again at every frame instead of once."""
        key = idb.as_pointer()                     # (names are not unique: every embedded node tree has the same one)
        hit = self._dynamic.get(key)
        if hit is None:
            paths = {fc.data_path for fc in fcurves_of(idb)}
            if isinstance(idb, bpy.types.Object):
                paths -= set(_OBJECT_ANIM_OK)
            hit = bool(paths)
            nt = getattr(idb, "node_tree", None)
            if not hit and nt is not None and fcurves_of(nt):
                hit = True
            self._dynamic[key] = hit
        return hit

    def id_ref(self, idb):
        """Content digest of a referenced datablock (image pixels, material and node trees); other kinds of ID
        (objects, collections, scenes) count by their type only: what they do is in the per-frame record."""
        if isinstance(idb, bpy.types.Image):
            return "img:" + self._cached(idb, self._image)
        if isinstance(idb, bpy.types.Material):
            return "mat:" + self._cached(idb, self._generic)
        if isinstance(idb, bpy.types.NodeTree):
            return "nt:" + self._cached(idb, self._node_tree)
        if isinstance(idb, (bpy.types.Light, bpy.types.Camera, bpy.types.World)):
            return type(idb).__name__ + ":" + self._cached(idb, self._generic)
        if isinstance(idb, bpy.types.Mesh):
            return "mesh:" + self._cached(idb, self._mesh)
        return type(idb).__name__

    def _cached(self, idb, fn):
        if self.is_dynamic(idb):
            return fn(idb)
        key = idb.as_pointer()
        d = self._cache.get(key)
        if d is None:
            d = self._cache[key] = fn(idb)
        return d

    def _generic(self, idb):
        out = [type(idb).__name__]
        self._walk(out, idb, 2)
        return _h(";".join(out))

    def _image(self, img):
        w, h = img.size
        out = "%dx%dx%d|%s|%s|%s" % (w, h, img.channels, img.colorspace_settings.name, img.alpha_mode, img.is_float)
        n = w * h * img.channels
        if n > 0:
            px = np.empty(n, dtype=np.float32)
            img.pixels.foreach_get(px)
            out += "|" + _bytes(px)
        return _h(out)

    def _node_tree(self, nt):
        out = [nt.bl_idname]
        for node in sorted(nt.nodes, key=lambda n: n.name):
            out.append("N:%s:%s" % (node.bl_idname, node.name))
            self._walk(out, node, 2, _NODE_SKIP)
            for tag, socks in (("i", node.inputs), ("o", node.outputs)):
                for s in socks:
                    dv = self._value(s.default_value) if hasattr(s, "default_value") else "-"
                    out.append("%s:%s=%s" % (tag, s.identifier, dv))
        links = sorted("%s.%s>%s.%s%s" % (ln.from_node.name, ln.from_socket.identifier, ln.to_node.name,
                                          ln.to_socket.identifier, "m" if ln.is_muted else "") for ln in nt.links)
        out.extend(links)
        return _h(";".join(out))

    def _mesh(self, me):
        nv, nl, nq = len(me.vertices), len(me.loops), len(me.polygons)
        parts = ["%d,%d,%d" % (nv, nl, nq)]
        co = np.empty(nv * 3, dtype=np.float32)
        me.vertices.foreach_get("co", co)
        parts.append(_bytes(co))
        li = np.empty(nl, dtype=np.int32)
        me.loops.foreach_get("vertex_index", li)
        parts.append(_bytes(li))
        for attr, dt in (("loop_start", np.int32), ("loop_total", np.int32), ("material_index", np.int32),
                         ("use_smooth", bool)):
            a = np.empty(nq, dtype=dt)
            me.polygons.foreach_get(attr, a)
            parts.append(_bytes(a))
        for layer in me.uv_layers:
            uv = np.empty(nl * 2, dtype=np.float32)
            layer.data.foreach_get("uv", uv)
            parts.append("uv:" + _bytes(uv))
        try:
            if me.has_custom_normals:
                cn = np.empty(nl * 3, dtype=np.float32)
                me.corner_normals.foreach_get("vector", cn)
                parts.append("cn:" + _bytes(np.round(cn, 4) + 0.0))
        except (AttributeError, RuntimeError):
            pass
        parts.extend(self.id_ref(m) if m is not None else "None" for m in me.materials)
        return _h("|".join(parts))

    def _object(self, ob):
        """An object's own settings, without where it is, whether it is shown (the per-frame record) and its data."""
        out = [ob.type]
        self._walk(out, ob, 2, _OBJECT_SKIP, _OBJECT_SKIP_PREFIX)
        return _h(";".join(out))

    def _object_record(self, ob):
        """Digests of an object, its data and its materials at the current frame (animated ones are taken afresh)."""
        rec = [self._cached(ob, self._object), self.id_ref(ob.data) if ob.data is not None else "None"]
        rec.extend(self.id_ref(s.material) if s.material is not None else "None" for s in ob.material_slots)
        rec.append("".join("1" if getattr(ob, f, True) else "0" for f in _RAY_FLAGS))
        return rec

    # ---- the scene as a whole ---------------------------------------------------------------------
    def reset(self):
        """Forget the global digest (call after changing resolution, samples or motion blur)."""
        self._global = None

    def global_digest(self):
        """Render settings, colour management, view layers, world and compositor (see the module docstring)."""
        if self._global is None:
            scene = self.scene
            out = ["v%d" % VERSION, bpy.app.version_string]
            for label, struct, depth in (("render", scene.render, 2), ("cycles", getattr(scene, "cycles", None), 1),
                                         ("view", scene.view_settings, 2), ("display", scene.display_settings, 1)):
                if struct is not None:
                    out.append(label + "{")
                    self._walk(out, struct, depth)
                    out.append("}")
            for vl in scene.view_layers:
                out.append("layer{")
                self._walk(out, vl, 2, ("objects", "freestyle_settings", "lightgroups", "material_override"))
                out.append("}")
            if scene.world is not None:
                out.append("world=" + self.id_ref(scene.world))
            group = getattr(scene, "compositing_node_group", None)
            if group is not None:
                out.append("comp=" + self.id_ref(group))
            effects = getattr(scene, "compositor_effects", None)
            if effects is not None:
                for fx in effects:
                    out.append("fx{")
                    self._walk(out, fx, 1)
                    out.append("}")
            self._global = _h(";".join(out))
        return self._global

    def _times(self, frame):
        r = self.scene.render
        if not r.use_motion_blur:
            return [float(frame)]
        s = float(r.motion_blur_shutter)
        t0 = {"START": 0.0, "CENTER": -s / 2.0, "END": -s}.get(r.motion_blur_position, 0.0)
        return [frame + t0, frame + t0 + s / 2.0, frame + t0 + s]

    def _set_time(self, t):
        whole = math.floor(t + 1e-9)
        self.scene.frame_set(int(whole), subframe=max(0.0, min(0.999, t - whole)))

    @staticmethod
    def _matrix(ob):
        return _bytes(np.round(np.array(ob.matrix_world, dtype=np.float64), 4) + 0.0)

    @staticmethod
    def _rendered(ob):
        if ob.hide_render:
            return False
        cols = ob.users_collection
        return not cols or any(not c.hide_render for c in cols)

    def frame(self, frame):
        """Fingerprint of one frame: {'fp': hex, 'parts': {'g', 'c', 'o', 'l'}} (see the module docstring)."""
        scene = self.scene
        cam = self.film.camera_at(frame)
        scene.frame_set(int(frame))
        recs = {}
        for ob in scene.objects:
            if ob.type in ("EMPTY", "CAMERA") or not self._rendered(ob):
                continue
            recs[ob] = self._object_record(ob)
        cam_rec = []
        focus = None
        if cam is not None:
            cam_rec.append(self.id_ref(cam.data))
            focus = cam.data.dof.focus_object if cam.data.dof.use_dof else None
        times = self._times(frame)
        for i, t in enumerate(times):
            if i or t != float(int(frame)):
                self._set_time(t)
            for ob, rec in recs.items():
                rec.append(self._matrix(ob))
            if cam is not None:
                cam_rec.append(self._matrix(cam))
                if focus is not None:
                    cam_rec.append(_bytes(np.round(np.array(focus.matrix_world.translation, dtype=np.float64), 4) + 0.0))
        if len(times) > 1:
            scene.frame_set(int(frame))
        lights = sorted("|".join(rec) for ob, rec in recs.items() if ob.type == "LIGHT")
        things = sorted("|".join(rec) for ob, rec in recs.items() if ob.type != "LIGHT")
        parts = {"g": self.global_digest(), "c": _h("|".join(cam_rec)), "o": _h("\n".join(things)),
                 "l": _h("\n".join(lights))}
        return {"fp": _h("|".join(parts[k] for k in "gcol")), "parts": parts,
                "count": {"objects": len(things), "lights": len(lights)}}


PART_NAMES = {"g": "look / render settings", "c": "camera", "o": "objects", "l": "lights"}


def explain(old_parts, new_parts):
    """Human-readable list of what differs between two fingerprints' parts ('camera, lights')."""
    if not old_parts:
        return "unknown"
    return ", ".join(PART_NAMES[k] for k in "gcol" if old_parts.get(k) != new_parts.get(k)) or "nothing"


# --------------------------------------------------------------------------------------------------------------
# self-test: change one thing at a time on a built look-dev film and see which part of which frames answers
# --------------------------------------------------------------------------------------------------------------

def _selftest(film_name="lookdev_dusk"):
    """Sensitivity test (no rendering): every change that alters a picture must change the fingerprint of exactly
    the frames it alters, and nothing else may. Prints one line per case; returns the number of failures."""
    import render as R

    from . import look

    ses = R.Session(film_name)
    ses.configure(R.FINAL_RES, R.FINAL_SAMPLES, R.FINAL_THREADS, None)
    film, scene = ses.film, ses.scene
    frames = [s.frame_start + 9 for s in film.shots]          # one frame per shot: bell, run, interior, steve_bell

    def snap():
        fp = Fingerprinter(scene, film)
        return {f: fp.frame(f)["parts"] for f in frames}

    base = snap()
    bad, cases = [], []

    def expect(label, want):
        cases.append(label)
        now = snap()
        got = {f: "".join(k for k in "gcol" if now[f][k] != base[f][k]) or "-" for f in frames}
        want = want if isinstance(want, dict) else {f: want for f in frames}
        ok = got == want
        if not ok:
            bad.append(label)
        print("%-4s %-58s %s" % ("OK" if ok else "FAIL", label, "" if ok else "got %s, expected %s" % (got, want)))

    def case(label, do, undo, want):
        do()
        expect(label, want)
        undo()

    def scale_keys(idb, path, k):
        for fc in fcurves_of(idb):
            if fc.data_path == path:
                for kp in fc.keyframe_points:
                    kp.co[1] *= k
                fc.update()

    def shift_keys(idb, path, index, d):
        for fc in fcurves_of(idb):
            if fc.data_path == path and fc.array_index == index:
                for kp in fc.keyframe_points:
                    kp.co[1] += d
                fc.update()

    f_bell, f_run, f_in, f_steve = frames
    expect("nothing changed", "-")
    c, r, vs = scene.cycles, scene.render, scene.view_settings
    case("cycles.filter_width", lambda: setattr(c, "filter_width", 1.5), lambda: setattr(c, "filter_width", 1.3), "g")
    case("render threads (must not matter)", lambda: setattr(r, "threads", 2), lambda: setattr(r, "threads", 4), "-")
    case("view exposure", lambda: setattr(vs, "exposure", 0.2), lambda: setattr(vs, "exposure", 0.0), "g")
    sock = next(s for s in bpy.data.node_groups[look.COMP_GROUP].nodes["look_bloom"].inputs if s.name == "Strength")
    old = sock.default_value
    case("compositor bloom strength", lambda: setattr(sock, "default_value", old * 0.5),
         lambda: setattr(sock, "default_value", old), "g")
    img = scene.world.node_tree.nodes["look_sky"].image
    px = np.empty(img.size[0] * img.size[1] * 4, dtype=np.float32)
    img.pixels.foreach_get(px)

    def poke(image, buf, i, k):
        q = buf.copy()
        q[i] *= k
        image.pixels.foreach_set(q)

    case("one pixel of the sky map", lambda: poke(img, px, 1000, 1.01), lambda: poke(img, px, 1000, 1.0), "g")
    tex = next(i for i in bpy.data.images if "cobblestone" in i.name and "mossy" not in i.name)
    tp = np.empty(tex.size[0] * tex.size[1] * 4, dtype=np.float32)
    tex.pixels.foreach_get(tp)
    case("one texel of cobblestone", lambda: poke(tex, tp, 0, 0.5), lambda: poke(tex, tp, 0, 1.0), "o")
    mat = next(m for m in bpy.data.materials if "lantern" in m.name and "*e" in m.name and "^up" not in m.name)
    node = next(n for n in mat.node_tree.nodes if n.type == "MATH" and n.operation == "MULTIPLY_ADD")
    ev = node.inputs[1].default_value
    case("lantern emission strength", lambda: setattr(node.inputs[1], "default_value", ev * 2),
         lambda: setattr(node.inputs[1], "default_value", ev), "o")
    me = next(o for o in scene.objects if o.type == "MESH" and "oak_planks" in o.name and not o.hide_render).data
    v0 = me.vertices[0].co.copy()
    case("one vertex of a plank mesh", lambda: setattr(me.vertices[0], "co", (v0.x, v0.y, v0.z + 0.01)),
         lambda: setattr(me.vertices[0], "co", v0), "o")
    lamp = next(o for o in scene.objects if o.name.startswith("light_bell_e"))
    case("east bell lamp x 1.5 (it is off in the bell and interior shots)", lambda: scale_keys(lamp.data, "energy", 1.5),
         lambda: scale_keys(lamp.data, "energy", 1 / 1.5), {f_bell: "-", f_run: "l", f_in: "-", f_steve: "l"})
    cam = film.shots[1].camera.data
    ln = cam.lens
    case("lens of the run shot", lambda: setattr(cam, "lens", ln + 2), lambda: setattr(cam, "lens", ln),
         {f_bell: "-", f_run: "c", f_in: "-", f_steve: "-"})
    stage = ses.result.get("stage")
    if stage is not None and "steve" in stage.cast:
        root = stage.cast["steve"].root                       # (the camera focuses on his head: 'c' changes too)
        case("Steve 0.1 block east (he is in the last shot only)", lambda: shift_keys(root, "location", 0, 0.1),
             lambda: shift_keys(root, "location", 0, -0.1), {f_bell: "-", f_run: "-", f_in: "-", f_steve: "co"})
    ob = bpy.data.objects.new("stamp_probe", bpy.data.meshes.new("stamp_probe"))
    ob.data.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [], [(0, 1, 2)])
    scene.collection.objects.link(ob)
    ob.hide_render = True
    expect("an extra object that is hidden (must not matter)", "-")
    ob.hide_render = False
    expect("the same object shown", "o")
    bpy.data.objects.remove(ob)
    expect("everything restored", "-")
    print("[stamp] fingerprint sensitivity: %d cases, %d failed" % (len(cases), len(bad)))
    return len(bad)


if __name__ == "__main__":
    import sys

    sys.exit(_selftest(*sys.argv[1:2]))
