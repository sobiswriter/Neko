"""Finish smooth generated art so it sits beside the original kitten's drawings.

The original kitten is crisp pixel art at her native size: hard edges, a handful of flat tones
(white fur, gray shading, black ink, pink ears and nose) and solid black line art about 2-3
screen pixels thick, including the inner contours that separate legs, head and body. The
generated sheets, scaled to her size, already have line art of about that weight, but it is
anti-aliased and the fur is softly shaded. ``pixelate`` keeps every drawn line where the artist
put it and only makes it crisp:

- alpha is cut hard, so the silhouette edge is crisp, and the outermost ring is solid black so
  the outline is always closed;
- line art (luma below the black/white midpoint) becomes solid black, so a soft line keeps its
  drawn width and stays continuous instead of breaking into dots;
- everything else snaps to the palette measured from the original idle, with soft gray strokes
  mapped to her gray shading tones by brightness and clearly coloured pixels (open mouths,
  blushes) kept among her pinks.

Rejected (2026-11-15): a 2 px block grid (too blocky, outlines 4-6 px), and redrawing the outline
at a fixed width while trimming the extra (it cut the inner contours where they meet the outline,
leaving loose dark "threads" across the body).
"""
from PySide6.QtGui import QImage

ALPHA_CUT = 128
INK_LUM = 128        # Line art: luma below the black/white midpoint keeps the drawn line width.
SHADE_MIN = 140      # Darkest gray used for soft interior shading strokes.


def palette_from(image, count=9, samples=4000):
    """A small k-means palette of the opaque colours in ``image`` (the original idle)."""
    pixels = []
    step = max(1, (image.width() * image.height()) // samples)
    for i in range(0, image.width() * image.height(), step):
        c = image.pixelColor(i % image.width(), i // image.width())
        if c.alpha() >= 200:
            pixels.append((c.red(), c.green(), c.blue()))
    # Seed with the tones that matter so the small pink and gray clusters are not lost.
    centres = [(255, 255, 255), (236, 234, 238), (205, 203, 210), (150, 148, 156), (40, 38, 42),
               (0, 0, 0), (246, 186, 196), (232, 140, 160), (255, 220, 226)][:count]
    for _ in range(8):
        groups = [[] for _ in centres]
        for p in pixels:
            groups[min(range(len(centres)), key=lambda k: _distance(p, centres[k]))].append(p)
        centres = [tuple(sum(c[i] for c in g) / len(g) for i in range(3)) if g else centres[k]
                   for k, g in enumerate(groups)]
    return [tuple(round(v) for v in c) for c in centres]


def _distance(a, b):
    # Weighted RGB distance; good enough to keep pinks pink and grays gray.
    dr, dg, db = a[0] - b[0], a[1] - b[1], a[2] - b[2]
    return 2 * dr * dr + 4 * dg * dg + 3 * db * db


def _luma(r, g, b):
    return (299 * r + 587 * g + 114 * b) // 1000


def _nearest(c, palette):
    """Nearest palette tone; a clearly coloured pixel (an open mouth, a blush) stays among the
    palette's pinks instead of turning gray."""
    if max(c) - min(c) > 18:
        pinks = [p for p in palette if max(p) - min(p) > 25]
        if pinks:
            return min(pinks, key=lambda p: _distance(c, p))
    return min(palette, key=lambda p: _distance(c, p))


def _tone(c, palette, darkest):
    luma = _luma(*c)
    if luma < INK_LUM:
        return darkest
    if max(c) - min(c) <= 18:   # Truly neutral; pale pinks (ears) stay pink.
        grays = [p for p in palette if max(p) - min(p) <= 30 and _luma(*p) >= SHADE_MIN]
        if grays:
            return min(grays, key=lambda p: abs(_luma(*p) - luma))
    return _nearest(c, palette)


def pixelate(image, palette):
    """Return ``image`` (any format, final screen size) finished in the original's style."""
    source = image.convertToFormat(QImage.Format_ARGB32)
    w, h = source.width(), source.height()
    stride = source.bytesPerLine()
    raw = bytes(source.constBits())[:stride * h]   # BGRA rows; `source` stays alive meanwhile.
    solid = bytearray(w * h)
    for y in range(h):
        row = y * stride
        for x in range(w):
            if raw[row + 4 * x + 3] >= ALPHA_CUT:
                solid[y * w + x] = 1
    darkest = min(palette, key=sum)
    tones = {}
    out = bytearray(stride * h)
    for y in range(h):
        for x in range(w):
            i = y * w + x
            if not solid[i]:
                continue
            edge = (x == 0 or y == 0 or x == w - 1 or y == h - 1
                    or not (solid[i - 1] and solid[i + 1] and solid[i - w] and solid[i + w]))
            o = y * stride + 4 * x
            if edge:
                colour = darkest
            else:
                c = (raw[o + 2], raw[o + 1], raw[o])
                colour = tones.get(c)
                if colour is None:
                    colour = tones[c] = _tone(c, palette, darkest)
            out[o], out[o + 1], out[o + 2], out[o + 3] = colour[2], colour[1], colour[0], 255
    result = QImage(bytes(out), w, h, stride, QImage.Format_ARGB32)
    return result.copy()   # Detach from the temporary buffer.
