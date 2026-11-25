"""Proof still for engine/sets.py under the night sky (films/_sets_proof.py has the golden-hour ones and the
driver: `$BPY -m engine.sets night` -> out/test/sets_night.png). The look-dev night: moon azimuth 176, elevation 21,
with the distance haze of the look turned down (SKY: haze; the night preset's own 0.45 turns a wood 15 blocks away
into grey fog: SETS_NIGHT_HAZE=preset shows it)."""
import os

from films import _sets_proof

SKY = dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool", haze=0.04)
if os.environ.get("SETS_NIGHT_HAZE"):
    SKY["haze"] = None if os.environ["SETS_NIGHT_HAZE"] == "preset" else float(os.environ["SETS_NIGHT_HAZE"])


def build(scene):
    """`$BPY -m render _sets_proof_night ...`: the forest edge at night."""
    return _sets_proof.build_film(scene, _sets_proof.NIGHT, SKY)
