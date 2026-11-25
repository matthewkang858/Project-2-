"""Motion proof for engine/sets.py: the walk into the wood (beat 6 of "The Hello") and a hop up a step of the
meadow, as contact sheets of consecutive frames through the real village, cast and look (540x960, 16 samples,
motion blur and depth of field on, the meadow sky: golden hour, haze off).

    $BPY -m films._sets_walk walkin     # -> out/test/sets_walkin_sheet.png: Steve in diamond on the last 9 blocks of
                                        #    road_to_forest, gate camera (22 mm), every 5th frame, cropped on the gap
    $BPY -m films._sets_walk hop        # -> out/test/sets_hop_sheet.png: the forest 6 blocks further out
                                        #    (forest_gap y 64), the road climbs one block at y 58; a side camera on
                                        #    that step from the lane, 10 consecutive frames of ground_path's hop
    $BPY -m render _sets_walk --still 1.0     # any render.py action works on the walk-in too

Not a film: nothing here is meant to be cut into one.
"""
import os
import sys

from engine import look, sets, shots, village
from films.lookdev import Stage, yaw_to

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKY = dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm", haze=0.0)
VARIANT = {"name": os.environ.get("SETS_WALK", "walkin")}
INFO = {}


def _steve(st):
    from engine import players

    steve = players.add_player(st, "steve", "steve")
    players.equip(steve, "diamond", enchanted=True)
    steve.hold("diamond_sword")
    return steve


def build(scene):
    """One 4-second shot: 'walkin' (the default layout) or 'hop' (the forest at y 64)."""
    name = VARIANT["name"]
    out = {}
    layout = {"forest_gap": (0.5, 64)} if name == "hop" else None
    v = village.build_village(scene, seed=1, edit=lambda b: out.update(hello=sets.hello_set(b, layout=layout)))
    sk = look.set_time(scene, SKY["preset"], sun_azimuth=SKY["az"], sun_elevation=SKY["el"])
    look.setup_compositor(scene, bloom=SKY["bloom"], grade=SKY["grade"], haze=SKY["haze"])
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, sk)
    hello = out["hello"]
    road = v.paths["road_to_forest"]
    s = st.shot(name, 4.0)
    f0 = s.frame_start
    steve = _steve(st)
    if name == "hop":
        hop = hello["forest"]["hops"][0]                     # (x, y, +1): where the road climbs
        tail = [(hop[0], hop[1] - 4.0, v.ground(hop[0], hop[1] - 4.0))] + [p for p in road if hop[1] - 4.0 < p[1] < hop[1] + 4.0]
        tail.append((hop[0], hop[1] + 4.0, v.ground(hop[0], hop[1] + 4.0)))
        steve.place(f0, tail[0], yaw_to(tail[0], tail[1]))
        end = steve.walk(f0, tail, ramp=(False, False))
        st.use(s, steve)
        s.lens(20.0, 4.0)                                    # from the plant-free lane beside the road
        s.move((hop[0] - 3.2, hop[1] - 0.6, 1.2), (hop[0], hop[1] - 0.3, 1.25))
        s.focus((hop[0], hop[1], 1.2))
        st.lights(s, scale=0.0)
        INFO.update(hop=hop, tail=tail)
    else:
        kid = st.actor("kid", "farmer", child=True)
        gap = v.anchors["forest_gap"]
        tail = [(gap[0], gap[1] - 9.0, v.ground(gap[0], gap[1] - 9.0))] + [p for p in road if p[1] > gap[1] - 8.6]
        steve.place(f0, tail[0], yaw_to(tail[0], tail[1]))
        end = steve.walk(f0, tail, ramp=(False, True))
        steve.show(end, False)                               # behind the east trunk of the gap: gone
        spot = (0.15, 26.6, v.ground(0, 26) - 0.0625)
        kid.place(f0, spot, yaw_to(spot, (2.2, 40.0)))
        kid.look_at(f0, steve, ease=0)
        st.use(s, kid, steve)
        cam = hello["cameras"]["gate"]
        s.lens(cam["lens"], cam["fstop"])
        s.move(cam["pos"], cam["target"])
        s.focus(kid.head)
        st.hero(s, "child", kid)
        st.lights(s, scale=1.0, near=v.anchors["exit_gate"], radius=14.0)
    st.finish()
    INFO.update(end=end, steve=steve, v=v, hello=hello, first=f0)
    return {"film": film, "captions": [], "stage": st}


def main(argv):
    """Render the frames of one variant and paste them into a contact sheet."""
    import time

    from PIL import Image

    import render as R

    from films import _sets_walk as film_module               # (not __main__: render.Session imports this one)

    name = argv[0] if argv else "walkin"
    film_module.VARIANT["name"] = name
    ses = R.Session("_sets_walk")
    ses.configure((540, 960), 16, 2, None)
    INFO = film_module.INFO
    scene, f0, end = ses.scene, INFO["first"], INFO["end"]
    steve = INFO["steve"]
    if name == "hop":
        at = None
        for f in range(f0, end + 1):                         # the frame he starts to rise
            scene.frame_set(f)
            if steve.root.matrix_world.translation.z > INFO["tail"][0][2] + 0.02:
                at = f
                break
        frames = list(range(at - 1, at + 9))
        crop, zoom = (0, 180, 540, 780), 0.5
    else:
        frames = list(range(end - 54, end + 6, 5))[:12]       # the last 9 blocks, to 2 frames after he is gone
        crop, zoom = (210, 440, 330, 540), 3
    tiles, t0 = [], time.time()
    for f in frames:
        scene.frame_set(f)
        p = steve.root.matrix_world.translation
        print("[sets walk] frame %d: steve (%.2f, %.2f, %.3f) hidden=%s" % (f, p.x, p.y, p.z, steve.root.hide_render),
              flush=True)
        path = os.path.join(ROOT, "out", "tmp", "sets_walk_%s_f%03d.png" % (name, f))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        ses.render_frame(f, path)
        im = Image.open(path).convert("RGB").crop(crop)
        tiles.append(im.resize((int(im.width * zoom), int(im.height * zoom)), Image.NEAREST if zoom > 1 else Image.LANCZOS))
        if time.time() - t0 > 230:
            print("[sets walk] out of time after %d frames" % len(tiles))
            break
    w, h = tiles[0].size
    cols = 5 if name == "hop" else 6
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w + (cols - 1) * 4, rows * h + (rows - 1) * 4), (255, 255, 255))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * (w + 4), (i // cols) * (h + 4)))
    out = os.path.join(ROOT, "out", "test", "sets_%s_sheet.png" % name)
    sheet.save(out)
    print("[sets walk] wrote %s (%d frames %s, walk ends on frame %d)" % (out, len(tiles), frames[:len(tiles)], end))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
