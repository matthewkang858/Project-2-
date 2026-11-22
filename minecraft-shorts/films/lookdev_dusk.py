"""Look-dev film 'dusk' (see films/lookdev.py): $BPY -m render lookdev_dusk --still 0.5"""
from . import lookdev


def build(scene):
    """Build the 'dusk' look-dev film."""
    return lookdev.build_film(scene, "lookdev_dusk")
