"""Drawn sprite sequences with per-frame timing and a shared ground anchor."""

from dataclasses import dataclass
from statistics import median

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QImage, QPixmap


def sprite_bounds(cell):
    """Anchor the main connected silhouette, excluding bleed from neighboring cells."""
    alpha = cell.convertToFormat(QImage.Format_Alpha8)
    pixels = bytes(alpha.constBits())
    width, height, stride = alpha.width(), alpha.height(), alpha.bytesPerLine()
    opaque = {(x, y) for y in range(height) for x in range(width) if pixels[y * stride + x] >= 128}
    if not opaque:
        return QRect()
    seed = min(opaque, key=lambda p: abs(p[0] - width / 2) + abs(p[1] - height / 2))
    pending = [seed]
    opaque.remove(seed)
    left = right = seed[0]
    top = bottom = seed[1]
    while pending:
        x, y = pending.pop()
        left, right = min(left, x), max(right, x)
        top, bottom = min(top, y), max(bottom, y)
        for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),
                         (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1), (x + 1, y + 1)):
            if neighbor in opaque:
                opaque.remove(neighbor)
                pending.append(neighbor)
    return QRect(left, top, right - left + 1, bottom - top + 1).adjusted(-1, -1, 1, 1).intersected(cell.rect())


@dataclass(frozen=True)
class Clip:
    row: int
    durations: tuple
    order: tuple = tuple(range(8))
    loop: bool = False

    def frame_index(self, elapsed):
        remaining = max(0, int(elapsed * 1000))
        total = sum(self.durations)
        remaining = remaining % total if self.loop else min(remaining, total - 1)
        for frame, duration in zip(self.order, self.durations):
            if remaining < duration:
                return frame
            remaining -= duration
        return self.order[-1]


CLIPS = {
    "idle": Clip(0, (2500, 120, 90, 100, 110, 160, 180, 2600), loop=True),
    "look_left": Clip(1, (180, 160, 450, 180, 350, 500), (2, 1, 0, 1, 2, 3)),
    "look_right": Clip(1, (200, 180, 450, 250, 180, 450), (3, 4, 5, 6, 4, 3)),
    "typing": Clip(2, (180, 150, 180, 150, 180, 150, 180, 150), loop=True),
    "groom": Clip(3, (250, 200, 300, 250, 300, 250, 220, 350)),
    "stretch": Clip(4, (350, 350, 400, 550, 400, 300, 300, 400)),
    "yawn": Clip(5, (350, 300, 300, 500, 300, 250, 300, 500)),
    "happy": Clip(6, (250, 250, 220, 250, 350, 250, 250, 500)),
    "sleep": Clip(7, (900, 650, 800, 750, 900, 700, 800, 750), loop=True),
    "peek": Clip(0, (300, 650, 450, 250, 500), (5, 4, 3, 4, 5)),
}


class SpriteAtlas:
    def __init__(self, path):
        self.frames = {}
        image = QImage(str(path))
        if image.isNull() or image.width() < 8 or image.height() < 8:
            return
        cells = {}
        for row in range(8):
            for col in range(8):
                left, right = round(col * image.width() / 8), round((col + 1) * image.width() / 8)
                top, bottom = round(row * image.height() / 8), round((row + 1) * image.height() / 8)
                cell = image.copy(left, top, right - left, bottom - top)
                bounds = sprite_bounds(cell)
                if bounds.isEmpty():
                    self.frames.clear()
                    return
                cells[row, col] = cell.copy(bounds)
        # One scale for every drawing: stretching never shrinks her head to fit.
        scale = 82 / median(cells[0, col].height() for col in range(8))
        for key, cell in cells.items():
            self.frames[key] = QPixmap.fromImage(cell).scaled(
                max(1, round(cell.width() * scale)), max(1, round(cell.height() * scale)),
                Qt.IgnoreAspectRatio, Qt.FastTransformation)

    def frame(self, name, elapsed, motion=True):
        clip = CLIPS[name]
        return self.frames.get((clip.row, clip.frame_index(elapsed if motion else 0)), QPixmap())
