"""Measured, through render.Session at 540x960 / 16 samples: (1) the pit's fill light (engine.nether Bastion.pit_fill,
keyed on by pit_open) against the same frame without it; (2) the beat-18 lava flicker (Bastion.lava_flicker) on the gate
frame, its weakest against its strongest frame.

    $BPY -m tools.check_nether_glow          # prints the numbers; writes out/test/nether_glow_*.png; exit 1 on a failure
"""
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILM = "nether_glow_check"
PIT_RATIO_MIN = 0.55      # pit floor / rim floor luminance with the fill (the game: about 0.65, two light levels less)
FLICKER_MIN = 5.0         # 1/255: the gateway glow's change between the flicker's weakest and strongest frame


def build(scene):
    from engine import nether, shots

    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    scene.cycles.samples = 16
    bas = nether.build_bastion(scene, sets=("home",))
    sky = nether.set_nether(scene, biome="nether_wastes")
    film = shots.Film(scene, fps=24)
    st = nether.Stage(scene, film, bas, sky)
    s = st.shot("pit", 1.0)                                  # the empty pit, dug, from the 'pit' camera
    bas.pit_open(s)
    nether._cam(s, bas, "pit", focus=bas.anchors["home_pit_center"])
    st.lights(s, 1.0, **bas.lights_for("home"))
    g = st.shot("gate_18", 2.0)                              # the gate frame with the beat-18 flicker
    nether._cam(g, bas, "gate", focus=bas.anchors["home_center"])
    st.lights(g, 1.0, **bas.lights_for("home"))
    bas.lava_flicker(g.frame_start, g.frame_end)
    st.finish()
    return {"film": film, "captions": [], "stage": st, "bastion": bas}


def lum_at(img, uv, r=3):
    import numpy as np

    h, w = img.shape[:2]
    x, y = int(uv[0] * w), int(uv[1] * h)
    patch = img[max(0, y - r):y + r + 1, max(0, x - r):x + r + 1].reshape(-1, 3).astype(float)
    return float(np.median(patch @ np.array([0.2126, 0.7152, 0.0722])))


def main():
    import numpy as np
    from PIL import Image

    import render as R
    from engine import nether

    mod = types.ModuleType("films." + FILM)
    mod.__file__ = os.path.abspath(__file__)
    mod.build = build
    sys.modules["films." + FILM] = mod
    ses = R.Session(FILM)
    ses.configure((540, 960), 16, 2, None)
    bas = ses.result["bastion"]
    film = ses.film
    out = os.path.join(ROOT, "out", "test")
    fails = 0

    # ---- (1) the pit fill
    s = next(x for x in film.shots if x.name == "pit")
    f = s.frame_start + 12
    cam = bas.cameras["pit"]
    w = bas.world
    cells = sorted({(c[0], c[1]) for c in bas.pit_blocks})
    z_floor = min(c[2] for c in bas.pit_blocks)
    pts_pit = [(x + 0.5, y + 0.5, float(z_floor)) for x, y in cells]
    xs, ys = [c[0] for c in cells], [c[1] for c in cells]
    pts_pit += [(x + 0.5, max(ys) + 0.98, z_floor + 0.5) for x in sorted(set(xs))]          # the far (north) wall
    pts_pit += [(max(xs) + 0.98, y + 0.5, z_floor + 0.5) for y in sorted(set(ys))]          # the far (east) wall
    pts_rim = [(x + 0.5, y + 0.5, 0.0) for x in range(min(xs) - 2, max(xs) + 3) for y in range(min(ys) - 2, max(ys) + 3)
               if (x < min(xs) - 1 or x > max(xs) + 1 or y < min(ys) - 1 or y > max(ys) + 1)]

    def visible(p):
        uv = nether.project(cam["pos"], cam["target"], cam["lens"], p)
        return uv if uv and 0 < uv[0] < 1 and 0 < uv[1] < 1 and not nether.sight_blocked(w, cam["pos"], p) else None

    pit_uv = [uv for uv in map(visible, pts_pit) if uv]
    rim_uv = [uv for uv in map(visible, pts_rim) if uv]
    p_on = os.path.join(out, "nether_glow_pit_fill.png")
    p_off = os.path.join(out, "nether_glow_pit_nofill.png")
    ses.render_frame(f, p_on)
    fill = bas.pit_fill
    for idb in (fill, fill.data):
        idb.animation_data_clear()
    fill.data.energy, fill.hide_render = 0.0, True
    ses.render_frame(f, p_off)
    res = {}
    for tag, path in (("fill", p_on), ("no fill", p_off)):
        img = np.asarray(Image.open(path).convert("RGB"))
        pit = float(np.median([lum_at(img, uv) for uv in pit_uv]))
        rim = float(np.median([lum_at(img, uv) for uv in rim_uv]))
        res[tag] = (pit, rim)
        print("[glow] pit %-8s pit floor / far walls %.1f, rim floor %.1f (of 255): ratio %.2f  (%d / %d points)"
              % (tag, pit, rim, pit / max(rim, 1e-6), len(pit_uv), len(rim_uv)))
    ratio = res["fill"][0] / max(res["fill"][1], 1e-6)
    ok = ratio >= PIT_RATIO_MIN
    fails += not ok
    print("[glow] %-4s pit with its fill: %.2f x the rim (>= %.2f; without the fill %.2f)"
          % ("ok" if ok else "FAIL", ratio, PIT_RATIO_MIN, res["no fill"][0] / max(res["no fill"][1], 1e-6)))

    # ---- (2) the beat-18 flicker
    g = next(x for x in film.shots if x.name == "gate_18")
    ch = bas.lava["home_channels"]
    wall = bas.lava["home_lava_wall_light"]
    fr = list(range(g.frame_start, g.frame_end + 1))
    k = [ch.light_factor(x) for x in fr]
    lo, hi = fr[int(np.argmin(k))], fr[int(np.argmax(k))]
    ses.scene.frame_set(lo)
    e_lo = (wall.data.energy, sum(o.data.energy for o in ch.lights))
    ses.scene.frame_set(hi)
    e_hi = (wall.data.energy, sum(o.data.energy for o in ch.lights))
    print("[glow] flicker factor %.2f..%.2f (frames %d / %d): lava wall light %.0f..%.0f W, channels %.0f..%.0f W"
          % (min(k), max(k), lo, hi, e_lo[0], e_hi[0], e_lo[1], e_hi[1]))
    paths = {}
    for tag, x in (("lo", lo), ("hi", hi)):
        paths[tag] = os.path.join(out, "nether_glow_flicker_%s.png" % tag)
        ses.render_frame(x, paths[tag])
    a = np.asarray(Image.open(paths["lo"]).convert("RGB")).astype(float)
    b = np.asarray(Image.open(paths["hi"]).convert("RGB")).astype(float)
    cam = bas.cameras["gate"]
    corners = [nether.project(cam["pos"], cam["target"], cam["lens"], p) for p in ((3.0, 18.0, 0.0), (6.0, 18.0, 5.0))]
    H, W = a.shape[:2]
    x0, x1 = sorted(int(c[0] * W) for c in corners)
    y0, y1 = sorted(int(c[1] * H) for c in corners)
    lw = np.array([0.2126, 0.7152, 0.0722])
    gate = abs((b[y0:y1, x0:x1] @ lw).mean() - (a[y0:y1, x0:x1] @ lw).mean())
    jx0, jx1 = max(0, x0 - (x1 - x0) // 2), min(W, x1 + (x1 - x0) // 2)            # the gateway and its jambs
    jambs = abs((b[y0:y1, jx0:jx1] @ lw).mean() - (a[y0:y1, jx0:jx1] @ lw).mean())
    whole = np.abs((b - a) @ lw).mean()
    ok = gate >= FLICKER_MIN
    fails += not ok
    print("[glow] %-4s flicker: the gateway (x %d-%d, y %d-%d px) changes %.1f / 255, gateway + jambs %.1f, the whole "
          "frame %.2f (>= %.0f in the gateway)" % ("ok" if ok else "FAIL", x0, x1, y0, y1, gate, jambs, whole, FLICKER_MIN))
    print("[glow] %d failure(s)" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
