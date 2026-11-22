"""Contract check (role INTEGRATOR): every name in CONTRACT.md exists and every documented call runs.

    $BPY -m tools.contract_check            # API only (a few seconds, renders nothing)
    $BPY -m tools.contract_check --cli      # also drives every render.py flag on the night look-dev film, tiny

Prints one line per check and a summary; the exit code is the number of failures.
"""
import math
import os
import subprocess
import sys
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

RESULTS = []


def check(name, fn):
    """Run one check; record OK / FAIL with the reason."""
    try:
        out = fn()
        ok = out is not False
        RESULTS.append((name, ok, "" if ok else "returned False"))
    except Exception as e:                                   # noqa: BLE001 - the report is the point
        RESULTS.append((name, False, "%s: %s" % (type(e).__name__, e)))
        traceback.print_exc()
    print("%-4s %s %s" % ("OK" if RESULTS[-1][1] else "FAIL", name, RESULTS[-1][2]), flush=True)


def api_checks():
    """Everything the contract names, called once in a headless scene."""
    import bpy
    from PIL import Image

    from engine import blocks, captions, characters, look, mcassets, props, shots, structures, village

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # ---- look / shots / captions
    check("look.setup_render", lambda: look.setup_render(scene, res=(720, 1280), samples=24, fps=24, motion_blur=True,
                                                         threads=4))
    for preset in ("day", "golden", "dusk", "night"):
        check("look.set_time(%s) returns sun and moon" % preset,
              lambda p=preset: {"sun", "moon"} <= set(look.set_time(scene, p, sun_azimuth=120.0)))
    check("look.setup_compositor", lambda: look.setup_compositor(scene, bloom=1.0, vignette=0.35, grade="warm"))

    # ---- structures / mcassets / blocks / props
    check("structures.load_template", lambda: len(structures.load_template(
        "village/plains/houses/plains_small_house_1").blocks) > 50)
    check("structures.list_templates", lambda: len(structures.list_templates("village/plains")) > 20)
    check("structures.parse_state", lambda: structures.parse_state("minecraft:oak_stairs[facing=east]")
          == ("oak_stairs", {"facing": "east"}))
    check("mcassets.texture", lambda: mcassets.texture("block/oak_planks").size[0] == 16)
    check("mcassets.texture(entity)", lambda: mcassets.texture("entity/villager/villager").size[0] == 64)
    check("mcassets.material", lambda: mcassets.material("block/oak_planks") is not None)
    check("mcassets.resolve_blockstate (variants)", lambda: len(mcassets.resolve_blockstate(
        "oak_stairs", {"facing": "east", "half": "bottom", "shape": "straight"})) >= 1)
    check("mcassets.resolve_blockstate (multipart)", lambda: len(mcassets.resolve_blockstate(
        "oak_fence", {"north": "true", "south": "false", "east": "false", "west": "false"})) >= 2)
    check("mcassets.load_model", lambda: len(mcassets.load_model("block/oak_stairs").elements) == 2)
    check("mcassets.item_object", lambda: len(mcassets.item_object("emerald").data.polygons) > 6)

    def world():
        w = blocks.World()
        w.set(0, 0, 0, "cobblestone")
        w.fill(1, 0, 0, 3, 0, 1, "oak_planks")
        assert w.get(0, 0, 0)[0] == "cobblestone" and w.is_solid(2, 0, 1) and not w.is_solid(9, 9, 9)
        w.place_template(structures.load_template("village/plains/plains_lamp_1"), (6, 6, 0), rot=1)
        col = blocks.new_collection(scene, "check_world")
        obs = w.build(col, "check", skip=())
        return len(obs) > 2
    check("blocks.World set/get/fill/place_template/is_solid/build", world)
    check("props.make_bell", lambda: props.make_bell("floor", "north").parent is not None)
    check("props.make_door", lambda: abs(props.make_door("oak_door", "left")["open_angle"]) > 1.5)
    check("props.make_item", lambda: props.make_item("emerald").type == "MESH")
    check("props.make_light", lambda: props.make_light("lantern").data.type == "POINT")

    # ---- village
    holder = {}

    def build():
        holder["v"] = village.build_village(scene, seed=1)
        return holder["v"].validate() == []
    check("village.build_village + validate() clean", build)
    v = holder.get("v")
    if v is not None:
        anchors = (["bell", "bell_ringer", "square_n", "square_e", "square_s", "square_w", "house_a_door_out",
                    "house_a_door_in", "house_a_inside_1", "house_a_inside_2", "house_a_inside_3", "house_a_bed_1",
                    "house_a_cam", "farm_work", "farm_station", "library_work", "library_station", "smithy_work",
                    "smithy_station", "hall_aisle_start", "hall_aisle_end", "exit_gate", "meadow_far", "nitwit_idle"]
                   + ["cell_%d" % i for i in range(1, 7)])
        for a in anchors:
            check("anchor " + a, lambda a=a: len(v.anchors[a]) == 3)
        for p in ("square_to_house_a", "square_to_house_b", "square_to_house_c", "exit_road"):
            check("path " + p, lambda p=p: len(v.paths[p]) >= 2 and not v.path_clear(v.paths[p]))
        for d in ("house_a", "house_b", "house_c"):
            check("door " + d, lambda d=d: v.doors[d].type == "MESH")
        check("Village.world / collection / bell / lantern_lights",
              lambda: v.world is not None and v.collection is not None and v.bell is not None and len(v.lantern_lights) > 10)
        check("Village.door_open", lambda: v.door_open("house_a", 10, open=True, frames=5) is None)
        check("Village.ring_bell", lambda: v.ring_bell(1, strength=1.0, swings=5) > 1)
        check("Village.cutaway", lambda: v.cutaway("house_a_east", True) is None and v.cutaway("house_a_east", False) is None)
        check("set under ~250k faces", lambda: v.face_count < 250000)

    # ---- characters
    methods = ["place", "walk", "look_at", "face", "idle", "nod", "shake", "flinch", "swing_arm", "hold", "lie_down", "show"]
    profs = ["farmer", "librarian", "toolsmith", "weaponsmith", "armorer", "cleric", "shepherd", "mason", "fletcher",
             "butcher", "fisherman", "cartographer", "leatherworker", "nitwit", "none"]
    for p in profs:
        check("make_villager(%s)" % p, lambda p=p: characters.make_villager("chk_" + p, p).height > 1.9)
    check("make_villager(child=True)", lambda: characters.make_villager("chk_child", "farmer", child=True).height < 1.2)
    for label, make in (("villager", lambda: characters.make_villager("chk_v", "farmer")),
                        ("player", lambda: characters.make_player("chk_p", "steve"))):
        made = {}
        check("%s: factory, root, head, height" % label,
              lambda: made.setdefault("c", make()).root is not None and made["c"].head is not None and made["c"].height > 1.5)
        c = made.get("c")
        if c is None:
            continue
        for m in methods:
            check("%s.%s exists" % (label, m), lambda m=m: callable(getattr(c, m)))
        check(label + ".place", lambda: c.place(1, (0, 0, 0), yaw=0.0) is None)
        check(label + ".walk returns the end frame", lambda: c.walk(1, [(0, 0, 0), (0, -3.2, 0)], speed=1.6) == 49)
        check(label + ".walk(run=True)", lambda: c.walk(60, [(0, -3.2, 0), (4.4, -3.2, 0)], run=True) == 84)
        check(label + ".look_at", lambda: c.look_at(90, (3, 3, 1.5), ease=6) is not None)
        check(label + ".face", lambda: c.face(100, (9, 9, 0), ease=8) is not None)
        check(label + ".idle", lambda: c.idle(110, 160, seed=0) is None)
        check(label + ".nod", lambda: c.nod(165) == 179)
        check(label + ".shake", lambda: c.shake(185) > 185)
        check(label + ".flinch", lambda: c.flinch(215) == 227)
        check(label + ".swing_arm", lambda: c.swing_arm(230) > 230)
        check(label + ".hold(item) / hold(None)", lambda: c.hold(props.make_item("emerald")) is not None and c.hold(None) is None)
        check(label + ".lie_down", lambda: c.lie_down(250, (19.0, -9.5, 1.5625), math.pi / 2) is None)
        check(label + ".show", lambda: c.show(260, False) is None and c.show(270, True) is None)
        check(label + ": place() after a running walk keeps the path up to the cut",
              lambda: _cut_keeps_path(characters, label))
        check(label + ": a cut at frame f is invisible in the exposure of frame f - 1 (no ghost before cuts)",
              lambda: _cut_outside_shutter(characters, scene, label))
    check("characters: look_at(frame, other.head) aims at the head's position AT that frame",
          lambda: _look_at_parented(characters, scene))

    # ---- shots / captions
    def film():
        f = shots.Film(scene, fps=24)
        a = f.shot("one", 0.0, 1.0)
        a.lens(85, fstop=1.8)
        a.move((4, -6, 1.2), (0, 0, 2.0), (3, -5, 1.4), ease="smooth")
        a.focus((0, 0, 2.0))
        a.focus((5, 5, 1.0), at_s=0.5)
        a.handheld(0.02, seed=0)
        b = f.shot("two", 1.0, 2.0)
        b.move((0, -8, 1.6), (0, 0, 1.2))
        f.finalize()
        cams = {m.name: m.camera for m in scene.timeline_markers}
        return (a.frame_start, a.frame_end, b.frame_start, b.frame_end) == (1, 24, 25, 48) \
            and cams["shot_one"] is a.camera and cams["shot_two"] is b.camera and scene.frame_end == 48
    check("shots.Film / Shot (lens, move, focus, handheld, finalize, markers)", film)
    check("captions.autotime", lambda: [w for w, _, _ in captions.autotime("When the bell rings, we run home.")]
          == ["When", "the", "bell", "rings", "we", "run", "home"])
    check("captions.draw_caption", lambda: isinstance(captions.draw_caption("rings"), Image.Image)
          and captions.draw_caption("rings").size == (1080, 1920) and captions.draw_caption("rings").mode == "RGBA")

    def caption_place():
        box = captions.draw_caption("sleeps").getbbox()          # (x0, y0, x1, y1) on 1080x1920
        centre = (box[0] + box[2]) / 2.0 / 1080.0
        width = (box[2] - box[0]) / 1080.0
        band = captions.CAPTION_BAND
        return abs(centre - 0.5) < 0.02 and 0.45 < width < 0.58 and band[0] - 0.01 <= box[1] / 1920.0 \
            and box[3] / 1920.0 <= band[1] + 0.01 and abs(captions.BASELINE - 0.69) < 0.011
    check("captions: baseline 69 %, 'sleeps' about half the width, inside CAPTION_BAND", caption_place)

    def zones():
        from engine import post
        img = post.draw_zones(Image.new("RGB", (270, 480), (80, 90, 100)))
        (x0, x1), (y0, y1) = post.SAFE_AREA["x"], post.SAFE_AREA["y"]
        return img.size == (270, 480) and 0 < x0 < x1 < 0.84 and 0.13 <= y0 < y1 <= captions.CAPTION_BAND[0]
    check("post.SAFE_AREA / UI_ZONES / draw_zones", zones)
    check("look: plain sRGB view + compositor shoulder (no Khronos black offset)",
          lambda: scene.view_settings.view_transform == "Standard"
          and bpy.data.node_groups[look.COMP_GROUP].nodes.get("look_tonemap") is not None)
    check("mcassets: shade_direction_override is kept (cross plants are lit like up-facing faces)",
          lambda: {q.shade for q in mcassets.bake_block("poppy")} == {"up_thin"}
          and {q.shade for q in mcassets.bake_block("torch")} == {"up"}
          and {q.shade for q in mcassets.bake_block("oak_planks")} == {None})


def _cut_outside_shutter(characters, scene, label):
    """engine.look renders frame f over [f, f + shutter]; after place(f) the root must still be at its old place
    at the END of frame f - 1's exposure and at the new one from frame f on."""
    c = characters.make_villager("chk_sh_" + label, "farmer") if label == "villager" else characters.make_player("chk_sh_p")
    c.place(1, (5.0, -7.0, 0.0), 0.0)
    c.place(37, (13.5, -9.5, 1.0), 1.0)
    shutter = scene.render.motion_blur_shutter
    ok = scene.render.motion_blur_position == "START" and 0.03 < characters.CUT_LEAD < 1.0 - shutter
    scene.frame_set(36, subframe=shutter)
    ok = ok and abs(c.root.location.x - 5.0) < 1e-6
    scene.frame_set(37)
    ok = ok and abs(c.root.location.x - 13.5) < 1e-6
    scene.frame_set(1)
    return ok


def _look_at_parented(characters, scene):
    walker = characters.make_villager("chk_walker", "farmer")
    walker.place(1, (-6.0, -3.0, 0.0), math.pi / 2)
    walker.walk(1, [(-6.0, -3.0, 0.0), (6.0, -3.0, 0.0)])
    looker = characters.make_player("chk_looker")
    looker.place(1, (0.0, 0.0, 0.0), 0.0)
    scene.frame_set(1)
    return abs(looker._aim(walker, 60)[0] - looker._aim(walker.head, 60)[0]) < 1e-4 and scene.frame_current == 1


def _cut_keeps_path(characters, label):
    c = characters.make_villager("chk_cut_" + label, "farmer") if label == "villager" else characters.make_player("chk_cut_p")
    c.place(1, (0, 0, 0), 0.0)
    c.walk(1, [(0, 0, 0), (0, -16.0, 0)], speed=1.6)         # 240 frames
    c.place(49, (30, 30, 0), 0.0)                             # cut away after 2 s
    return abs(c.pos_at(25).y - (-1.6)) < 1e-3 and abs(c.pos_at(48).y - (-3.1333)) < 0.01 and abs(c.pos_at(49).x - 30) < 1e-6


def cli_checks(film="lookdev_night"):
    """Drive every render.py flag on a look-dev film at thumbnail size and check what it wrote. Everything here is
    a PREVIEW (tiny resolution), so it must land under out/preview/, never in the film's final frames directory."""
    import json
    import time

    out = os.path.join(ROOT, "out")
    env = dict(os.environ)

    def run(args, expect=0):
        cmd = [sys.executable, "-W", "ignore", "-m", "render", film] + args
        r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=280)
        if r.returncode != expect:
            raise RuntimeError("exit %d (expected %d): %s" % (r.returncode, expect, (r.stdout + r.stderr)[-600:]))
        return r.stdout or "ok"

    def fresh(path, t0):
        return os.path.exists(path) and os.path.getmtime(path) >= t0 - 1 and os.path.getsize(path) > 500

    t0 = time.time()
    small = ["--res", "180x320", "--samples", "4", "--threads", "4"]
    step5 = os.path.join(out, "preview", film, "180x320_4spp_step5")
    step1 = os.path.join(out, "preview", film, "180x320_4spp")
    final_dir = os.path.join(out, "frames", film)
    final_before = sorted(os.listdir(final_dir)) if os.path.isdir(final_dir) else []
    check("render --still (two times) --captioned --zones --no-motion-blur", lambda: run(
        ["--still", "0.25,1.0", "--captioned", "--zones", "--no-motion-blur"] + small) and all(fresh(os.path.join(
            out, "test", "%s_%s%s.png" % (film, s, c)), t0) for s in ("0.25", "1.0") for c in ("", "_cap", "_zones")))
    check("render --sheet", lambda: run(["--sheet", "3", "--threads", "4"]) and fresh(
        os.path.join(out, "test", film + "_sheet.png"), t0))
    check("render --frames A-B --step K --force (preview directory)", lambda: run(
        ["--frames", "1-36", "--step", "5", "--force"] + small)
        and all(fresh(os.path.join(step5, "f_%04d.png" % f), t0) for f in range(1, 37, 5)))
    check("preview frames stay out of the final frames directory",
          lambda: (sorted(os.listdir(final_dir)) if os.path.isdir(final_dir) else []) == final_before)
    check("render --frames all --max-seconds (resumable: nothing left to do)", lambda: "0 to render" in run(
        ["--frames", "all", "--step", "5", "--max-seconds", "60"] + small))

    def edit_meta(fn):
        meta_path = os.path.join(step5, "meta.json")
        with open(meta_path) as f:
            meta = json.load(f)
        fn(meta)
        with open(meta_path, "w") as f:
            json.dump(meta, f)

    def stale():
        # as if frame 6 showed another scene when it was rendered (a film edit that changed that frame)
        edit_meta(lambda m: m["frames"]["6"].update(fp="another-scene", parts={}))
        txt = run(["--frames", "all", "--step", "5"] + small)
        return "1 to render" in txt and "stale" in txt
    check("resume re-renders a frame whose scene fingerprint is not the current one", stale)

    def engine_stale():
        # as if frames 6 and 11 had been rendered with other engine sources: 6 with an unchanged scene, 11 not
        def other(m):
            m["frames"]["6"]["e"] = "0ther-engine"
            m["frames"]["11"].update(e="0ther-engine", fp="another-scene", parts={})
        edit_meta(other)
        txt = run(["--frames", "all", "--step", "5"] + small, expect=3)
        if "STOPPED" not in txt or "--restamp" not in txt:
            return False
        txt = run(["--restamp", "all", "--step", "5"] + small)
        if "1 frames re-stamped" not in txt or "1 NOT accepted" not in txt:
            return False
        run(["--frames", "all", "--step", "5"] + small, expect=3)          # frame 11 still holds the run back
        txt = run(["--frames", "all", "--step", "5", "--rerender-stale"] + small)
        return "1 to render" in txt
    check("engine-stale frames stop --frames (exit 3); --restamp keeps the unchanged one; --rerender-stale renders", engine_stale)

    def restamp_changed():
        edit_meta(lambda m: m["frames"]["16"].update(fp="another-scene", parts={}))
        txt = run(["--restamp", "16", "--restamp-changed", "--step", "5"] + small)
        return "1 frames re-stamped" in txt and "0 to render" in run(["--frames", "all", "--step", "5"] + small)
    check("render --restamp N --restamp-changed keeps a frame whose fingerprint differs", restamp_changed)

    def prune():
        edit_meta(lambda m: m["frames"]["21"].update(fp="another-scene", parts={}))
        txt = run(["--prune-stale", "--step", "5"] + small)
        gone = not os.path.exists(os.path.join(step5, "f_0021.png"))
        return "1 stale PNGs deleted" in txt and gone and "1 to render" in run(["--frames", "all", "--step", "5"] + small)
    check("render --prune-stale deletes exactly the stale PNG", prune)

    def nomb_is_preview():
        run(["--frames", "1", "--no-motion-blur", "--res", "720x1280", "--samples", "24", "--threads", "4"])
        return os.path.exists(os.path.join(out, "preview", film, "720x1280_24spp_nomb", "f_0001.png")) and \
            (sorted(os.listdir(final_dir)) if os.path.isdir(final_dir) else []) == final_before
    check("--no-motion-blur at final resolution and samples is a preview (never the final directory)", nomb_is_preview)
    check("render --frames N (single)", lambda: run(["--frames", "2"] + small) and fresh(
        os.path.join(step1, "f_0002.png"), t0))
    check("render --sheet --save-blend (the .blend carries final settings, no .blend1)", lambda: "720x1280, 24 samples" in run(
        ["--sheet", "2", "--save-blend", "--threads", "4"]) and fresh(os.path.join(out, "blend", film + ".blend"), t0)
        and not os.path.exists(os.path.join(out, "blend", film + ".blend1")))
    check("render --encode refuses a film with missing frames (exit 2)",
          lambda: "refused" in run(["--encode", "--step", "5"] + small, expect=2))

    def encode():
        txt = run(["--encode", "--allow-holds", "--step", "5"] + small)
        from engine import post
        mp4 = os.path.join(out, "preview", "%s_180x320_4spp_step5.mp4" % film)
        info = post.probe(mp4)
        print("     ", info, "->", mp4)
        return (info["width"], info["height"], info["pix_fmt"], info["codec"]) == (1080, 1920, "yuv420p", "h264") \
            and info["frames"] == 36 and abs(info["fps"] - 24.0) < 1e-6 and "video" in txt
    check("render --encode --allow-holds (1080x1920 h264 yuv420p, 24 fps, all frames)", encode)


def main():
    """Entry point."""
    api_checks()
    if "--cli" in sys.argv[1:]:
        cli_checks()
    bad = [r for r in RESULTS if not r[1]]
    print("\ncontract check: %d checks, %d failed" % (len(RESULTS), len(bad)))
    for name, _, why in bad:
        print("  FAIL", name, "-", why)
    return len(bad)


if __name__ == "__main__":
    sys.exit(main())
