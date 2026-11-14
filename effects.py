"""Small painted expression marks around Neko: Zzz, hearts, sparkles, notes and moods.

These are drawn beside the kitten, never on her face; her drawn expressions stay the source of
acting. Every mark has a white outline so it reads on light and dark desktops. With reduced
motion a mark is shown still, without drifting or pulsing.
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainterPath, QPen

from animations import sprite_bounds

SYMBOL_FONT = "Segoe UI Symbol"
TEXT_FONT = "Segoe UI"
OUTLINE = QColor(255, 255, 255, 230)
_anchor_cache = {}


def anchor(pixmap):
    """(bounds, head x) of a drawing, in its own pixels. The head is the middle of the top rows."""
    key = pixmap.cacheKey()
    cached = _anchor_cache.get(key)
    if cached is None:
        image = pixmap.toImage()
        bounds = sprite_bounds(image)
        xs = [x for y in range(bounds.top(), min(bounds.bottom() + 1, bounds.top() + 18), 2)
              for x in range(bounds.left(), bounds.right() + 1, 2) if image.pixelColor(x, y).alpha() >= 128]
        head = (min(xs) + max(xs)) / 2 if xs else bounds.center().x()
        if len(_anchor_cache) > 1500:
            _anchor_cache.clear()
        cached = _anchor_cache[key] = (bounds, head)
    return cached


def _mark(painter, text, center, size, color, alpha=1.0, family=SYMBOL_FONT, weight=QFont.Normal):
    if alpha <= 0.02:
        return
    font = QFont(family)
    font.setPixelSize(max(6, round(size)))
    font.setWeight(weight)
    path = QPainterPath()
    path.addText(0, 0, font, text)
    box = path.boundingRect()
    path.translate(center.x() - box.center().x(), center.y() - box.center().y())
    painter.save()
    painter.setOpacity(max(0.0, min(1.0, alpha)))
    painter.setPen(QPen(OUTLINE, 2.4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setBrush(Qt.NoBrush)
    painter.drawPath(path)
    painter.setPen(Qt.NoPen)
    painter.setBrush(color)
    painter.drawPath(path)
    painter.restore()


def _fade(p, edge=0.2):
    """0→1→0 over a cycle phase p in [0, 1)."""
    return min(1.0, p / edge, (1 - p) / edge)


def _rain_cloud(painter, center, elapsed, motion, scale):
    """A small storybook rain cloud: one puffy outline, lit top, shaded belly, slanted streaks."""
    s = scale
    # A flat-bottomed base with three puffs on top, united into a single solid outline.
    cloud = QPainterPath()
    cloud.addRoundedRect(QRectF(center.x() - 15 * s, center.y() - 1 * s, 30 * s, 9 * s), 4.5 * s, 4.5 * s)
    for dx, dy, r in ((-8, 1, 6), (1, -3.5, 8), (10, 1, 5.5)):
        puff = QPainterPath()
        puff.addEllipse(QPointF(center.x() + dx * s, center.y() + dy * s), r * s, r * s)
        cloud = cloud.united(puff)
    box = cloud.boundingRect()
    # Rain first, so the cloud overlaps the tops of the streaks.
    painter.save()
    for i, dx in enumerate((-9, -2, 5, 11)):
        p = ((elapsed / 0.9) + i * 0.29) % 1 if motion else (0.2 + 0.2 * i)
        x = center.x() + dx * s - 3 * p * s
        y = box.bottom() + (1 + 12 * p) * s
        streak_alpha = (_fade(p, 0.25) if motion else 0.85)
        painter.setOpacity(streak_alpha)
        painter.setPen(QPen(OUTLINE, 3.2 * s, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(QPointF(x, y), QPointF(x - 1.6 * s, y + 4.5 * s))
        painter.setPen(QPen(QColor("#6f9fd8"), 1.6 * s, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(QPointF(x, y), QPointF(x - 1.6 * s, y + 4.5 * s))
    painter.restore()
    shade = QLinearGradient(0, box.top(), 0, box.bottom())
    shade.setColorAt(0, QColor(214, 220, 230))
    shade.setColorAt(0.55, QColor(172, 181, 196))
    shade.setColorAt(1, QColor(128, 138, 156))
    painter.setPen(QPen(OUTLINE, 2.6 * s, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setBrush(Qt.NoBrush)
    painter.drawPath(cloud)
    painter.setPen(QPen(QColor(92, 100, 118), 1.0 * s, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setBrush(shade)
    painter.drawPath(cloud)
    # A soft highlight on the biggest puff.
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(255, 255, 255, 120))
    painter.drawEllipse(QPointF(center.x() - 1 * s, center.y() - 6.5 * s), 3.6 * s, 2.0 * s)


def paint(painter, effect, elapsed, head, top, motion=True, scale=1.0):
    """Draw `effect` around a head at (head, top) in widget pixels; `elapsed` is seconds since it began."""
    if effect is None:
        return
    painter.save()
    painter.setRenderHint(painter.RenderHint.Antialiasing)
    if effect in ("sleep", "doze"):
        # Three letters drifting up and to the side, each a little larger than the last.
        small = effect == "doze"
        cycle = 2.7
        for i in range(2 if small else 3):
            p = ((elapsed / cycle) + i / 3) % 1 if motion else (0.25 + i * 0.25)
            # Held high in the canvas, the dozing letters drift sideways beside her head instead.
            x = head + (26 if small else 10) + 20 * p + i * 2
            y = (top + 16 - 12 * p) if small else (top - 2 - 30 * p)
            size = (8 + 7 * p) * (0.8 if small else 1.0) * scale
            _mark(painter, "z" if p < 0.4 else "Z", QPointF(x, y), size, QColor("#8e87b8"),
                  _fade(p) if motion else 0.9, TEXT_FONT, QFont.Bold)
    elif effect == "pet":
        # Little hearts floating up with a gentle sway.
        cycle = 1.5
        for i in range(3):
            p = ((elapsed / cycle) - i / 3) % 1 if motion else (0.3 + i * 0.2)
            if motion and elapsed < i * cycle / 3:
                continue
            sway = math.sin((p + i) * math.tau) * 4
            x = head + (-14, 6, 18)[i] + sway
            y = top + 6 - 34 * p
            _mark(painter, "♥", QPointF(x, y), (11 + 5 * p + (i == 1) * 2) * scale,
                  QColor("#ec7f9c"), _fade(p) if motion else 0.95)
    elif effect == "win":
        # Twinkling sparkles around her head.
        for i, (dx, dy) in enumerate(((-24, 4), (22, -4), (-8, -16), (12, 14))):
            phase = (elapsed * 1.6 + i * 0.27) % 1 if motion else 0.5
            size = (9 + 7 * math.sin(phase * math.pi)) * scale
            _mark(painter, "✦", QPointF(head + dx, top + dy), size, QColor("#f2be45"),
                  0.35 + 0.65 * math.sin(phase * math.pi) if motion else 0.9)
    elif effect == "dizzy":
        # Little stars circling above her head; the orbit tilts slightly so it reads as a ring.
        spin = elapsed * 4.2 if motion else 0.6
        for i in range(3):
            angle = spin + i * math.tau / 3
            depth = math.sin(angle)  # Behind the head (top of the ring) is smaller and fainter.
            x = head + math.cos(angle) * 26
            y = top - 12 + depth * 6
            _mark(painter, "✦", QPointF(x, y), (11 + 3 * (depth + 1)) * scale, QColor("#f2be45"),
                  0.55 + 0.45 * (depth + 1) / 2)
    elif effect == "notice":
        # A quick "!" pop when she spots the arrow.
        t = min(1.0, elapsed / 0.18) if motion else 1.0
        pop = 1 + 0.35 * math.sin(t * math.pi) if motion else 1
        _mark(painter, "!", QPointF(head + 16, top - 6 - 6 * t), 17 * pop * scale, QColor("#e07b39"),
              min(1.0, (0.9 - elapsed) / 0.2) if motion else 1.0, TEXT_FONT, QFont.Black)
    elif effect == "music":
        # Notes bobbing up while she sways along.
        cycle = 2.2
        for i, note in enumerate(("♪", "♫")):
            p = ((elapsed / cycle) + i / 2) % 1 if motion else 0.4 + i * 0.3
            x = head + (16 if i == 0 else -18) + math.sin(p * math.tau) * 3
            _mark(painter, note, QPointF(x, top + 4 - 28 * p), (14 + 3 * p) * scale, QColor("#4f86c6"),
                  _fade(p) if motion else 0.9)
    elif effect == "grumpy":
        # A small cross-vein mark, pulsing like a cartoon huff.
        pulse = 1 + 0.18 * math.sin(elapsed * 7) if motion else 1
        center = QPointF(head + 30, top + 4)  # Beside the ear, off the drawing.
        painter.translate(center)
        painter.scale(pulse * scale, pulse * scale)
        painter.setPen(QPen(OUTLINE, 4.2, Qt.SolidLine, Qt.RoundCap))
        arcs = [QRectF(dx - 7, dy - 7, 7, 7) for dx, dy in ((0, 0), (7, 0), (0, 7), (7, 7))]
        starts = (270, 180, 0, 90)
        for rect, start in zip(arcs, starts):
            painter.drawArc(rect, start * 16, 90 * 16)
        painter.setPen(QPen(QColor("#e0565b"), 2.2, Qt.SolidLine, Qt.RoundCap))
        for rect, start in zip(arcs, starts):
            painter.drawArc(rect, start * 16, 90 * 16)
    elif effect == "sulk":
        _rain_cloud(painter, QPointF(head + 4, top - 22 + (math.sin(elapsed * 1.3) * 1.2 if motion else 0)),
                    elapsed, motion, scale)
    painter.restore()
