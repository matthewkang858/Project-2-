"""Reviewer's probe: a two-sky Nether film as the docstring of engine/nether.py says to write one (SKIES with
preset "nether"), for render.py's own command line (one process per sky). The module is made importable as
films.check_nether_skies by a sitecustomize in the scratchpad (nothing is written under films/).
"""
SKIES = {"home": dict(preset="nether", biome="nether_wastes"),
         "bridge": dict(preset="nether", biome="crimson_forest")}


def build(scene, sky=None):
    from engine import nether, piglins, shots

    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    scene.cycles.samples = 16
    bas = nether.build_bastion(scene)
    film = shots.Film(scene, fps=24)
    st = nether.Stage(scene, film, bas, skies=SKIES, sky=sky)
    brute = piglins.add_piglin(st, "brute", "brute")
    A, Y, C = bas.anchors, bas.yaws, bas.cameras
    s = st.shot("gate", 1.0, sky="home")
    brute.place(s.frame_start, A["home_gateway"], Y["home_gateway"])
    s.lens(C["gate"]["lens"], C["gate"]["fstop"])
    s.move(C["gate"]["pos"], C["gate"]["target"])
    s.focus(A["home_center"])
    st.use(s, brute)
    st.lights(s, 1.0, **bas.lights_for("home"))
    s = st.shot("bridge", 1.0, sky="bridge")
    brute.place(s.frame_start, A["bridge_brute"], Y["bridge_brute"])
    c = C["bridge_shoulder"]
    s.lens(c["lens"], c["fstop"])
    s.move(c["pos"], c["target"])
    s.focus(brute.head)
    st.use(s, brute)
    st.lights(s, 1.0, **bas.lights_for("bridge"))
    st.finish()
    return {"film": film, "captions": [], "stage": st}
