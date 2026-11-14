"""Re-draw smooth generated art on Neko's chunky pixel grid so it sits beside the original idle.

The original kitten is stepped pixel art: each art pixel covers about 2–3 screen pixels, colours
are a handful of flat tones (white fur, gray chest shading, charcoal/black outline, pink ears and
nose, black eyes with white highlights) and every edge is hard. Generated sheets are smooth and
anti-aliased. ``pixelate`` rebuilds a drawing on a coarse grid: area-average each block, snap its
colour to the palette measured from the original idle, give it hard alpha, close the outline so
fur never touches transparency, then enlarge with nearest-neighbour so the blocks stay crisp.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage

BLOCK = 2           # Screen pixels per art pixel (the original idle's stepped clusters are ~2 px).
ALPHA_CUT = 120
DARK_SUM = 3 * 95   # r+g+b below this counts as ink.


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


def pixelate(image, palette, block=BLOCK):
    """Return ``image`` (ARGB, final screen size) rebuilt on a ``block``-pixel grid."""
    image = image.convertToFormat(QImage.Format_ARGB32)
    w, h = image.width(), image.height()
    gw, gh = (w + block - 1) // block, (h + block - 1) // block
    solid = [[False] * gw for _ in range(gh)]
    tone = [[None] * gw for _ in range(gh)]
    darkest = min(palette, key=lambda p: sum(p))
    for gy in range(gh):
        for gx in range(gw):
            r = g = b = a = n = dark = 0
            for y in range(gy * block, min(h, (gy + 1) * block)):
                for x in range(gx * block, min(w, (gx + 1) * block)):
                    c = image.pixelColor(x, y)
                    alpha = c.alpha()
                    r += c.red() * alpha
                    g += c.green() * alpha
                    b += c.blue() * alpha
                    a += alpha
                    n += 1
                    if alpha >= ALPHA_CUT and c.red() + c.green() + c.blue() < DARK_SUM:
                        dark += 1
            if n and a / n >= ALPHA_CUT:
                solid[gy][gx] = True
                if dark * 4 >= n:
                    # A thin dark line (eye, mouth, outline) stays a bold black pixel instead of
                    # averaging into gray: the original's faces are drawn in solid black strokes.
                    tone[gy][gx] = darkest
                else:
                    colour = (r / a, g / a, b / a)
                    tone[gy][gx] = min(palette, key=lambda p: _distance(colour, p))
    # A solid one-art-pixel outline, like the original: no fur pixel touches transparency, even
    # diagonally.
    edge = [[False] * gw for _ in range(gh)]
    for gy in range(gh):
        for gx in range(gw):
            if solid[gy][gx]:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nx, ny = gx + dx, gy + dy
                        if (dx or dy) and (not (0 <= nx < gw and 0 <= ny < gh) or not solid[ny][nx]):
                            edge[gy][gx] = True
    for gy in range(gh):
        for gx in range(gw):
            if edge[gy][gx]:
                tone[gy][gx] = darkest
    out = QImage(gw * block, gh * block, QImage.Format_ARGB32)
    out.fill(Qt.transparent)
    for gy in range(gh):
        for gx in range(gw):
            if solid[gy][gx]:
                colour = QColor(*tone[gy][gx])
                for y in range(gy * block, (gy + 1) * block):
                    for x in range(gx * block, (gx + 1) * block):
                        out.setPixelColor(x, y, colour)
    return out.copy(0, 0, w, h)
