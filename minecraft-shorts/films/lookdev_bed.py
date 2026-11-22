"""Look-dev film 'bed' (see films/lookdev.py): $BPY -m render lookdev_bed --still 0.5"""
from . import lookdev


def build(scene):
    """Build the 'bed' look-dev film."""
    return lookdev.build_film(scene, "lookdev_bed")
