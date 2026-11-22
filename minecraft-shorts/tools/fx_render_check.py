"""Drive the engine.fx proof film through render.py (fx author's test; no film file is written under films/).

  $BPY -m tools.fx_render_check                 preview frames 296-305 (the cut between the last two shots), then
                                                build the film again and ask for the same frames: all must be current
  $BPY -m tools.fx_render_check 44-52           another range (a single range per run: A-B, a frame, or a shot name)

The proof film (engine.fx.build_proof) is registered as the module films.fx_proof in memory, so render.py builds it
exactly like a film script: Session, engine.stamp fingerprints, resumable frames in out/preview/fx_proof/<variant>/.
What this proves: fx's keyed node values, particle constraints and the film.finalize() wrapper go through the real
pipeline; the frame fingerprints are the same in a second build (nothing renders twice); a contact sheet
out/test/fx_render_<range>.png shows the frames.
"""
import contextlib
import io
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES, SAMPLES = "270x480", "8"


def _register():
    """Put a film module `films.fx_proof` into sys.modules whose build() is fx.build_proof."""
    from engine import fx

    mod = types.ModuleType("films.fx_proof")

    def build(scene):
        """The fx proof film as render.py expects it."""
        proof = fx.build_proof(scene)
        return {"film": proof["film"], "captions": [], "proof": proof}

    mod.build = build
    sys.modules["films.fx_proof"] = mod


def _run(argv):
    """render.main(argv) with its output echoed and returned."""
    import render

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = render.main(argv)
    text = buf.getvalue()
    for line in text.splitlines():
        if line.startswith("[render]"):
            print("   " + line)
    return code, text


def main(argv):
    """Render a preview range twice (the second run must find every frame current) and write a contact sheet."""
    spec = argv[0] if argv else "296-305"
    _register()
    args = ["fx_proof", "--frames", spec, "--res", RES, "--samples", SAMPLES, "--threads", "2"]
    print("[fx_render_check] first run: %s" % " ".join(args))
    code1, text1 = _run(args)
    print("[fx_render_check] second run (the film is built again)")
    code2, text2 = _run(args)
    again = [ln for ln in text2.splitlines() if "requested" in ln]
    current = bool(again) and " 0 to render" in again[0]
    print("%-4s second build: every frame of %s is current (same fingerprints)  %s"
          % ("OK" if current else "FAIL", spec, again[0].strip() if again else "(no frame line)"))
    stopped = "STOPPED" in text1 or "STOPPED" in text2
    print("%-4s render.py ran the frames (exit codes %s, %s)" % ("OK" if not stopped else "FAIL", code1, code2))
    # contact sheet of what is on disk for that range
    from PIL import Image, ImageDraw

    from engine import post

    variant = "%s_%sspp" % (RES, SAMPLES)
    frames = []
    for ln in text1.splitlines() + text2.splitlines():
        if "[render] frame " in ln:
            frames.append(int(ln.split("[render] frame")[1].split()[0]))
    if not frames and "-" in spec:
        a, b = spec.split("-")
        frames = list(range(int(a), int(b) + 1))
    frames = sorted(set(frames))
    tiles = [(f, post.frame_path("fx_proof", f, variant)) for f in frames]
    tiles = [(f, p) for f, p in tiles if os.path.exists(p)]
    if tiles:
        w, h = Image.open(tiles[0][1]).size
        cols = min(len(tiles), 10)
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * w, rows * h))
        for i, (f, p) in enumerate(tiles):
            sheet.paste(Image.open(p).convert("RGB"), ((i % cols) * w, (i // cols) * h))
            ImageDraw.Draw(sheet).text(((i % cols) * w + 4, (i // cols) * h + 4), str(f), fill=(255, 255, 0))
        out = os.path.join(ROOT, "out", "test", "fx_render_%s.png" % spec.replace("-", "_"))
        sheet.save(out)
        print("[fx_render_check] sheet of %d frames -> %s" % (len(tiles), out))
    return 0 if (current and not stopped) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
