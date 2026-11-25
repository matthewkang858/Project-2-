"""Checker's reference: the scene of films/_multisky_check_a.py as an ordinary ONE-sky film under the golden sky,
built the way every finished film is (look.set_time + look.setup_compositor + Stage(scene, film, v, sky))."""
from engine import look
from films import _multisky_check_a as A
from films import lookdev as L

SPEC = A.SKIES["gold"]           # (not bound to the name SKIES: this module has one sky)


def _stage(scene, film, v):
    sky = look.set_time(scene, SPEC["preset"], sun_azimuth=SPEC["az"], sun_elevation=SPEC["el"])
    look.setup_compositor(scene, bloom=SPEC["bloom"], grade=SPEC["grade"])
    return L.Stage(scene, film, v, sky)


def build(scene):
    """The same film, one sky."""
    return A.populate(scene, _stage, multi=False)
