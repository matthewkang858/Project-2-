"""Scene fingerprints (engine/stamp.py, what render.py stamps frames with) and the film sets of engine/sets.py.

    $BPY -m tools.check_sets_stamp          # run it twice: the FP lines of the two runs must be identical

The set is static geometry, so the question is not "which frames change" but "is everything the set is made of
IN the fingerprint": a re-render must not keep old frames after the set changed. One camera (the exit-gate framing
of "The Hello"), one frame, ten builds of the village:

    plain      no hook                       the village of the finished films
    hello      sets.hello_set                 the reference
    hello2     the same again                 must equal 'hello' (deterministic inside one process)
    noshade    the forest without baked sky light   differs from 'hello' in the objects only (block colours)
    nobiome    the forest in plains colours   differs in the objects only
    moved      the sand pyramid one block further east     differs in the objects only
    far        the forest 6 blocks further out (layout forest_gap)          differs in the objects only
    logs2      the floating oak with 2 logs instead of 4 (floating=)        differs in the objects only
    clear      the meadow sky: the same set, haze=0.0                       differs in the global part only
    plain2     no hook, after all of these    must equal 'plain' (a hook leaves nothing behind in the process)

Exit code 1 if an expectation fails.
"""
import sys
import time


def build(variant):
    """Village (by variant) + the look-dev golden sky + one shot from the exit gate. Returns (scene, film, village)."""
    import bpy

    from engine import look, sets, shots, village

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene)                                   # the FINAL settings, as render.Session does
    edits = {
        "plain": None, "plain2": None,
        "hello": lambda b: sets.hello_set(b), "hello2": lambda b: sets.hello_set(b),
        "noshade": lambda b: sets.hello_set(b, forest=dict(shade=False)),
        "nobiome": lambda b: sets.hello_set(b, forest=dict(biome=False)),
        "moved": lambda b: sets.hello_set(b, layout=dict(pyramid=(13, 45))),
        "far": lambda b: sets.hello_set(b, layout=dict(forest_gap=(0.5, 64))),
        "logs2": lambda b: sets.hello_set(b, floating=dict(logs=2)),
        "clear": lambda b: sets.hello_set(b),
    }
    v = village.build_village(scene, seed=1, edit=edits[variant])
    look.set_time(scene, "golden", sun_azimuth=62.0, sun_elevation=27.0)
    look.setup_compositor(scene, bloom=1.0, grade="warm", haze=0.0 if variant == "clear" else None)
    film = shots.Film(scene, fps=24)
    s = film.shot("gate", 0.0, 1.0)
    s.lens(32.0, 4.0)
    s.move((0.9, 22.6, 0.75), (0.5, 57.6, 2.6))
    s.focus((0.5, 30.0, 1.0))
    film.finalize()
    return scene, film, v


def main():
    from engine import stamp

    got, bad = {}, 0
    for variant in ("plain", "hello", "hello2", "noshade", "nobiome", "moved", "far", "logs2", "clear", "plain2"):
        scene, film, v = build(variant)
        fp = stamp.Fingerprinter(scene, film)
        t = time.time()
        r = fp.frame(12)
        first = time.time() - t
        t = time.time()
        fp.frame(13)
        got[variant] = r["parts"]
        print("FP %-8s %s  g=%s c=%s o=%s l=%s  objects %d, lights %d, first frame %.2f s, next %.3f s" % (
            variant, r["fp"], r["parts"]["g"][:8], r["parts"]["c"][:8], r["parts"]["o"][:8], r["parts"]["l"][:8],
            r["count"]["objects"], r["count"]["lights"], first, time.time() - t))

    def expect(label, a, b, want):
        nonlocal bad
        diff = "".join(k for k in "gcol" if got[a][k] != got[b][k]) or "-"
        ok = diff == want
        bad += not ok
        print("%-4s %-58s differing parts: %s (expected %s)" % ("OK" if ok else "FAIL", label, diff, want))

    expect("the same set built twice", "hello", "hello2", "-")
    expect("no hook, before and after the sets were built", "plain", "plain2", "-")
    expect("village with hello_set against the plain village", "plain", "hello", "o")
    expect("forest without its baked sky light", "hello", "noshade", "o")
    expect("forest without its biome colours", "hello", "nobiome", "o")
    expect("the pyramid one block further east", "hello", "moved", "o")
    expect("the forest 6 blocks further out", "hello", "far", "o")
    expect("the floating oak with 2 logs instead of 4", "hello", "logs2", "o")
    expect("the same set under the haze-free meadow sky", "hello", "clear", "g")
    print("[check_sets_stamp] %s" % ("all as expected" if not bad else "%d FAILED" % bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
