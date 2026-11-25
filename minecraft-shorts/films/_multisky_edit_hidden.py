"""Written by tools/multisky_editfilm.py: the edit film, its SKIES not visible in the source."""
import films._multisky_edit as _m

globals().update({"SK" + "IES": _m.SKIES, "build": _m.build})
