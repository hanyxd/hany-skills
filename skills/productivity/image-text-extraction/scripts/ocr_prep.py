#!/usr/bin/env python3
"""OCR preprocessing helper for images/screenshots.

Usage:
  python3 ocr_prep.py profile <image>               # print content-region bbox(es)
  python3 ocr_prep.py prep <image> <box> <out>      # write preprocessed crop to <out>
                                                    #   <box> = x1,y1,x2,y2

Pillow only, no numpy. Then: tesseract <out> stdout --psm 6
"""

import sys
from PIL import Image, ImageOps, ImageFilter

STEP = 8
BRIGHT = 80


def profile(path):
    im = Image.open(path).convert('RGB')
    px = im.load()
    w, h = im.size
    ncols = w // STEP
    bands = []
    cur = None
    for y in range(0, h, STEP):
        cnt = 0
        xs = []
        for x in range(0, w, STEP):
            r, g, b = px[x, y]
            if (r + g + b) / 3 > BRIGHT:
                cnt += 1
                xs.append(x)
        frac = cnt / ncols
        if frac > 0.005:
            if cur and y - cur[1] <= STEP * 2:
                cur[1] = y
                cur[2] = min(cur[2], xs[0])
                cur[3] = max(cur[3], xs[-1])
            else:
                if cur:
                    bands.append(cur)
                cur = [y, y, xs[0], xs[-1]]
    if cur:
        bands.append(cur)
    print(f"size {w}x{h}")
    for b in bands:
        print(f"band y {b[0]}..{b[1]}  x {b[2]}..{b[3]}")


def prep(path, box, out, scale=3):
    x1, y1, x2, y2 = map(int, box.split(','))
    im = Image.open(path).convert('RGB').crop((x1, y1, x2, y2))
    im = im.convert('L')
    im = im.resize((im.size[0] * scale, im.size[1] * scale), Image.LANCZOS)
    im = ImageOps.autocontrast(im)
    im = im.filter(ImageFilter.SHARPEN)
    im.save(out)
    print(f"wrote {out} {im.size}")


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'profile':
        profile(sys.argv[2])
    elif cmd == 'prep':
        prep(sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]) if len(sys.argv) > 5 else 3)
    else:
        sys.exit('usage: ocr_prep.py profile <image> | prep <image> <x1,y1,x2,y2> <out> [scale]')
