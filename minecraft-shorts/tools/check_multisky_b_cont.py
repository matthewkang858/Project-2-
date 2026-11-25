"""Checker B: numbers for the in-shot sky change of films/_multisky_check_b.py (read-only, renders nothing).

    $BPY -m tools.check_multisky_b_cont FILM SKY F1,F2,...

Builds FILM with SKY active (render.Session(FILM, sky=SKY)) and prints, for each frame AND for the half-frame after
it (the shutter is open over [f, f+0.5]): the camera's world position, the first actor's root position, and the
energy / hide_render of the torches within 3 blocks of house_a's door. Prints one JSON line.
Also: tries to fingerprint a frame of the OTHER sky (must raise SkyError).
"""
import json
import sys


def main(argv):
    """Entry point."""
    import bpy

    import render as R

    name, sky, frames = argv[0], argv[1], [int(x) for x in argv[2].split(",")]
    ses = R.Session(name, sky=sky)
    st = ses.result["stage"]
    door = st.v.anchors["house_a_door"]
    scene = ses.scene
    out = {"sky": ses.sky, "frames": {}}
    torches = [o for o in st.v.lantern_lights
               if o.get("mc_light") != "fill" and (o.location - __import__("mathutils").Vector(door)).length < 3.0]
    for f in frames:
        row = {}
        for sub in (0.0, 0.5):
            cam = ses.film.camera_at(f)
            scene.camera = cam
            scene.frame_set(f, subframe=sub)
            dg = bpy.context.evaluated_depsgraph_get()
            c = cam.evaluated_get(dg).matrix_world.translation
            a = st.cast["ada"].root.evaluated_get(dg).matrix_world.translation
            row["%.1f" % sub] = {
                "cam": [round(x, 5) for x in c], "lens": round(cam.data.lens, 3),
                "ada": [round(x, 5) for x in a],
                "torches": [[o.name, round(o.evaluated_get(dg).data.energy, 3), bool(o.evaluated_get(dg).hide_render)]
                            for o in torches]}
        out["frames"][str(f)] = row
        out.setdefault("owns", {})[str(f)] = ses.owns(f)
    other = next(f for f in range(ses.film.frame_start, ses.film.frame_end + 1) if not ses.owns(f))
    try:
        ses.fingerprint(other)
        out["wrong_sky_fingerprint"] = "NOT REFUSED"
    except R.SkyError as e:
        out["wrong_sky_fingerprint"] = "SkyError: " + str(e)[:120]
    try:
        ses.render_frame(other, "/nonexistent/x.png")
        out["wrong_sky_render"] = "NOT REFUSED"
    except R.SkyError:
        out["wrong_sky_render"] = "SkyError"
    print("CHECK_B_CONT " + json.dumps(out))


if __name__ == "__main__":
    main(sys.argv[1:])
