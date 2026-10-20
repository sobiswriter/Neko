"""Drawn sprite sequences with per-frame timing and a shared ground anchor."""

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QImage, QPixmap, QPainter


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
    "tail": Clip("idle", 1, (180, 150, 180, 300), loop=True),
    "ears": Clip("idle", 2, (700, 150, 200, 750), loop=True),
    "sniff": Clip("idle", 3, (450, 200, 240, 450), loop=True),
    "happy": Clip("pets", 0, (350, 240, 320, 650), loop=True),
    "nuzzle": Clip("pets", 1, (350, 220, 340, 650), loop=True),
    "wave": Clip("pets", 2, (250, 200, 250, 800), loop=True),
    "knead": Clip("pets", 3, (220, 220, 220, 220), loop=True),
    "typing": Clip("activity", 0, (180, 180, 180, 180), loop=True),
    "groom": Clip("activity", 1, (350, 240, 350, 700), loop=True),
    "yawn": Clip("activity", 2, (600, 220, 650, 500)),
    "fall_asleep": Clip("transitions", 0, (350, 220, 220, 250, 250, 250, 300, 500), tuple(range(8))),
    "wake": Clip("transitions", 2, (350, 220, 220, 250, 250, 250, 300, 500), tuple(range(8))),
    "sleep": Clip("transitions", 1, (1400, 1400), (2, 3), loop=True),
    "walk": Clip("movement", 0, (140, 140, 140, 140), loop=True),
    "stretch": Clip("movement", 1, (250, 400, 320, 600), loop=True),
    "look_left": Clip("movement", 2, (200, 650, 220, 650, 600), (1, 0, 1, 2, 3), loop=True),
    "look_right": Clip("movement", 2, (200, 650, 220, 650, 600), (1, 2, 3, 0, 1), loop=True),
    "loaf": Clip("movement", 3, (2200, 160, 180, 1800), loop=True),
    "peek": Clip("idle", 0, (300, 100, 160, 400, 100, 500), (0, 1, 2, 3, 1, 0), loop=True),
}


class SpriteAtlas:
    def __init__(self, path):
        self.frames = {}
        cells = {}
        for bank in ("idle", "pets", "activity", "movement", "transitions"):
            filename = "neko-transitions-v1.png" if bank == "transitions" else f"neko-{bank}-v3.png"
            image = QImage(str(Path(path) / filename))
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
        for key, cell in cells.items():
            # Seated drawings share a height; low poses keep their natural proportions.
            if key[0] == "transitions":
                scale = 82 / cells["transitions", 0, 0].height()
                sprite = QPixmap.fromImage(cell).scaled(
                    round(cell.width() * scale), round(cell.height() * scale),
                    Qt.IgnoreAspectRatio, Qt.FastTransformation)
            elif key[:2] in (("activity", 3), ("movement", 3)):
                sprite = QPixmap.fromImage(cell).scaledToWidth(92, Qt.FastTransformation)
            else:
                sprite = QPixmap.fromImage(cell).scaled(104, 82, Qt.KeepAspectRatio, Qt.FastTransformation)
            frame = QPixmap(112, 100)
            frame.fill(Qt.transparent)
            painter = QPainter(frame)
            painter.drawPixmap((112 - sprite.width()) // 2, 98 - sprite.height(), sprite)
            painter.end()
            self.frames[key] = frame

    def frame(self, name, elapsed, motion=True):
        clip = CLIPS[name]
        index = clip.frame_index(elapsed if motion else 0)
        return self.frames.get((clip.bank, clip.row + index // 4, index % 4), QPixmap())
