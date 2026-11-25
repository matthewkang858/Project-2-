"""Proof film for tools/multisky_check.py: films/_multisky_demo.py with its last shot ('street') under the gold
sky from its first frame to its last, i.e. WITHOUT the sky change inside it. Everything else is the demo, key for
key. The demo's frames either side of its sky change must be pixel-identical to this ordinary, uncut shot's."""
from films import _multisky_demo as D

SKIES = D.SKIES


def build(scene, sky=None):
    """The demo, its street shot all gold."""
    return D.build(scene, sky, street=("gold", "gold"))
