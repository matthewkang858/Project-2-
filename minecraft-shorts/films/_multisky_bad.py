"""Negative test film for tools/multisky_selftest.py: the multi-sky demo with ONE thing that depends on the active
sky besides the sky itself (its last caption is missing in the night build). A film must never do that: the two
builds would describe two different films. render.py has to refuse it (SkyError) instead of rendering."""
from films import _multisky_demo as D

SKIES = D.SKIES


def build(scene, sky=None):
    """The demo; under the night sky without its last caption (deliberately wrong)."""
    out = D.build(scene, sky)
    if out["stage"].sky_name == "night":
        out["captions"] = out["captions"][:-1]
    return out
