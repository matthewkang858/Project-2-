"""Checker probe: put named stills side by side (downscaled) with labels. Usage: python3 -m tools.check_twentyminutes_story_sheet OUT W H COLS img1 img2 ..."""
import os, sys
from PIL import Image, ImageDraw
out, w, h, cols = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
paths = sys.argv[5:]
rows = (len(paths) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * (h + 16)), (20, 20, 24))
d = ImageDraw.Draw(sheet)
for i, p in enumerate(paths):
    im = Image.open(p).convert("RGB").resize((w, h))
    x, y = (i % cols) * w, (i // cols) * (h + 16)
    sheet.paste(im, (x, y + 16))
    d.text((x + 2, y + 2), os.path.basename(p).replace("twentyminutes_", "")[:34], fill=(255, 255, 0))
sheet.save(out)
print(out, sheet.size)
