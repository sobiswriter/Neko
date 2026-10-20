"""Drawn sprite sequences with per-frame timing and a shared ground anchor."""

from dataclasses import dataclass
from statistics import median
from pathlib import Path

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
    bank: str
    row: int
    durations: tuple
    order: tuple = tuple(range(4))
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
    "idle": Clip("idle", 0, (2500, 120, 160, 2400), loop=True),
    "tail": Clip("idle", 1, (350, 300, 350, 450), loop=True),
    "ears": Clip("idle", 2, (500, 180, 250, 900)),
    "sniff": Clip("idle", 3, (500, 250, 350, 900)),
    "happy": Clip("pets", 0, (350, 450, 650, 800)),
    "nuzzle": Clip("pets", 1, (350, 450, 650, 800)),
    "wave": Clip("pets", 2, (350, 600, 350, 700)),
    "knead": Clip("pets", 3, (350, 350, 350, 350), loop=True),
    "typing": Clip("activity", 0, (240, 220, 240, 220), loop=True),
    "groom": Clip("activity", 1, (500, 450, 650, 700)),
    "yawn": Clip("activity", 2, (500, 450, 650, 800)),
    "sleep": Clip("activity", 3, (1100, 900, 1100, 900), loop=True),
    "walk": Clip("movement", 0, (160, 160, 160, 160), loop=True),
    "stretch": Clip("movement", 1, (450, 650, 500, 800)),
    "look_left": Clip("movement", 2, (250, 1100, 550), (1, 0, 1)),
    "look_right": Clip("movement", 2, (250, 1100, 550), (1, 2, 3)),
    "loaf": Clip("movement", 3, (2200, 160, 180, 1800), loop=True),
    "peek": Clip("idle", 0, (250, 350, 900), (1, 2, 3)),
}


class SpriteAtlas:
    def __init__(self, path):
        self.frames = {}
        cells = {}
        for bank in ("idle", "pets", "activity", "movement"):
            image = QImage(str(Path(path) / f"neko-{bank}-v3.png"))
            if image.isNull():
                return
            image = image.scaled(512, 512, Qt.IgnoreAspectRatio, Qt.FastTransformation)
            for row in range(4):
                for col in range(4):
                    cell = image.copy(col * 128, row * 128, 128, 128)
                    bounds = sprite_bounds(cell)
                    if bounds.isEmpty():
                        return
                    cells[bank, row, col] = cell.copy(bounds)
        # One scale for every drawing: stretching never shrinks her head to fit.
        scale = 82 / median(cells["idle", 0, col].height() for col in range(4))
        for key, cell in cells.items():
            self.frames[key] = QPixmap.fromImage(cell).scaled(
                max(1, round(cell.width() * scale)), max(1, round(cell.height() * scale)),
                Qt.IgnoreAspectRatio, Qt.FastTransformation)

    def frame(self, name, elapsed, motion=True):
        clip = CLIPS[name]
        return self.frames.get((clip.bank, clip.row, clip.frame_index(elapsed if motion else 0)), QPixmap())
