"""Checker B's third probe: the SAME three-sky film as _multisky_check_b2, but SKIES and build() arrive through a
star import (a director who keeps the skies of six films in one shared module would write this). render.py's
declares_skies() reads the source with ast and does not see a star import: what happens then?"""
from films._multisky_check_b2 import *        # noqa: F401,F403  (SKIES, build)
