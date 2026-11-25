"""Checker probe (story angle): build the film once and dump its real shot table, sky segments, dips, captions."""
import json, sys, time
t = time.time()
import render
S = render.Session("hello")
film = S.film
res = S.result
nar = res["narration"]
st = res["stage"]
C = res["context"]
out = {"shots": [], "captions": S.captions, "segments": None, "dips": None}
for s in film.shots:
    out["shots"].append(dict(name=s.name, a=s.frame_start, b=s.frame_end))
try:
    out["segments"] = st.sky_segments()
except Exception as e:
    out["segments"] = repr(e)
for k in ("fades", "dips"):
    if k in res:
        out[k] = res[k]
out["stage_dips"] = repr(getattr(st, "_dips", getattr(st, "dips", None)))
out["frames"] = nar.frames
out["scene_res"] = (S.scene.render.resolution_x, S.scene.render.resolution_y, S.scene.cycles.samples)
out["cap_frames"] = nar.caption_frames(cuts=[s.frame_start for s in film.shots[1:]])
# per shot: which cast is used
uses = {}
for name in ("_uses", "uses", "_use"):
    if hasattr(st, name):
        try:
            uses = {k: sorted(getattr(c, "name", str(c)) for c in v) for k, v in getattr(st, name).items()}
        except Exception as e:
            uses = repr(e)
        break
out["uses"] = uses
json.dump(out, open("out/test/check_hello_story_build.json", "w"), indent=1, default=repr)
print("built in %.1f s" % (time.time() - t))
