"""Finish smooth generated art so it sits beside the original kitten's drawings.

The original kitten is crisp pixel art at her native size: hard edges, a handful of flat tones
(white fur, gray chest shading, black ink, pink ears and nose) and a solid black outline about
2 screen pixels thick. Generated sheets are smooth and anti-aliased, with outlines that come out
3-6 px after scaling. ``pixelate`` keeps the drawing at native resolution (no coarse block grid,
which looked too blocky next to her) and:

- cuts alpha hard, so the silhouette edge is crisp;
- redraws the outer outline as exactly ``OUTLINE`` px of black, like the original;
- gives back to the fur any extra outline thickness and the gray anti-aliasing halo inside it,
  filled with the neighbouring interior colour (white fur, pink ear...);
- snaps every other pixel to the palette measured from the original idle, with dark lines
  (eyes, mouth) kept solid black.
"""
from collections import deque

from PySide6.QtGui import QImage

ALPHA_CUT = 120
OUTLINE = 2          # The original's outer outline at native size: ~2 px of solid black.
HALO = 3             # Extra px inside the outline that may belong to a thick outline or its halo.
INK_LUM = 110        # Luma below this is ink.
LIGHT_LUM = 190      # Luma at or above this is fur, never outline/halo.


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


def _nearest(c, palette):
    """Nearest palette tone; a clearly coloured pixel (an open mouth, a blush) stays among the
    palette's pinks instead of turning gray."""
    if max(c) - min(c) > 60:
        pinks = [p for p in palette if max(p) - min(p) > 30]
        if pinks:
            return min(pinks, key=lambda p: _distance(c, p))
    return min(palette, key=lambda p: _distance(c, p))


def _luma(r, g, b):
    return (299 * r + 587 * g + 114 * b) // 1000


def pixelate(image, palette):
    """Return ``image`` (any format, final screen size) finished in the original's style."""
    source = image.convertToFormat(QImage.Format_ARGB32)
    w, h = source.width(), source.height()
    stride = source.bytesPerLine()
    raw = bytes(source.constBits())[:stride * h]   # BGRA rows; `source` stays alive meanwhile.
    n = w * h
    rgb = [None] * n
    solid = bytearray(n)
    for y in range(h):
        row = y * stride
        for x in range(w):
            o = row + 4 * x
            a = raw[o + 3]
            if a >= ALPHA_CUT:
                i = y * w + x
                solid[i] = 1
                # Un-premultiplied in Format_ARGB32.
                rgb[i] = (raw[o + 2], raw[o + 1], raw[o])
    # Chessboard distance from the outside (transparency or the image border), 1 = edge pixel.
    dist = [0] * n
    queue = deque()
    for i in range(n):
        if solid[i]:
            x, y = i % w, i // w
            if x == 0 or y == 0 or x == w - 1 or y == h - 1:
                dist[i] = 1
                queue.append(i)
                continue
            for j in (i - w - 1, i - w, i - w + 1, i - 1, i + 1, i + w - 1, i + w, i + w + 1):
                if not solid[j]:
                    dist[i] = 1
                    queue.append(i)
                    break
    limit = OUTLINE + HALO
    while queue:
        i = queue.popleft()
        d = dist[i]
        if d >= limit + 1:
            continue
        x, y = i % w, i // w
        for dy in (-1, 0, 1):
            ny = y + dy
            if not 0 <= ny < h:
                continue
            for dx in (-1, 0, 1):
                nx = x + dx
                if (dx or dy) and 0 <= nx < w:
                    j = ny * w + nx
                    if solid[j] and not dist[j]:
                        dist[j] = d + 1
                        queue.append(j)
    deep = limit + 2   # Interior pixels the BFS never reached.
    for i in range(n):
        if solid[i] and not dist[i]:
            dist[i] = deep
    # Extra outline / halo: non-light pixels just inside the new outline that are connected to it
    # through non-light pixels (so eyes and inner lines away from the edge are untouched).
    excess = bytearray(n)
    queue = deque(i for i in range(n) if solid[i] and dist[i] == OUTLINE)
    while queue:
        i = queue.popleft()
        x, y = i % w, i // w
        for j in (i - w, i + w, i - 1 if x else -1, i + 1 if x < w - 1 else -1):
            if 0 <= j < n and solid[j] and not excess[j] and OUTLINE < dist[j] <= limit:
                if _luma(*rgb[j]) < LIGHT_LUM:
                    excess[j] = 1
                    queue.append(j)
    # Fill the excess from the neighbouring interior colour, growing outward.
    fill = [None] * n
    queue = deque()
    for i in range(n):
        # Only fur-coloured sources (white, pink, light shading), so ink never floods the band.
        if solid[i] and dist[i] > OUTLINE and not excess[i] and _luma(*rgb[i]) >= 150:
            fill[i] = rgb[i]
            queue.append(i)
    while queue:
        i = queue.popleft()
        x = i % w
        for j in (i - w, i + w, i - 1 if x else -1, i + 1 if x < w - 1 else -1):
            if 0 <= j < n and excess[j] and fill[j] is None:
                fill[j] = fill[i]
                queue.append(j)
    darkest = min(palette, key=sum)
    snapped = {}
    out = bytearray(stride * h)
    for i in range(n):
        if not solid[i]:
            continue
        if dist[i] <= OUTLINE:
            colour = darkest
        else:
            c = fill[i] if excess[i] and fill[i] is not None else rgb[i]
            if excess[i] and fill[i] is None:
                c = max(palette, key=sum)
            colour = snapped.get(c)
            if colour is None:
                colour = darkest if _luma(*c) < INK_LUM else _nearest(c, palette)
                snapped[c] = colour
        o = (i // w) * stride + 4 * (i % w)
        out[o], out[o + 1], out[o + 2], out[o + 3] = colour[2], colour[1], colour[0], 255
    result = QImage(bytes(out), w, h, stride, QImage.Format_ARGB32)
    return result.copy()   # Detach from the temporary buffer.
