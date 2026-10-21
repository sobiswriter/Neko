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
    "tail": Clip("tailswish", 0, (450, 220, 220, 350, 220, 220, 280, 900), tuple(range(8))),
    "ears": Clip("idle", 2, (700, 250, 350, 900)),
    "sniff": Clip("idle", 3, (450, 350, 450, 850)),
    "tail_chase": Clip("tailplay", 0, (450, 400, 220, 220, 220, 220, 300, 800), tuple(range(8))),
    "tail_catch": Clip("tailplay", 2, (450, 400, 320, 250, 550, 300, 350, 800), tuple(range(8))),
    "arrive": Clip("lifecycle", 0, (140, 140, 140, 100, 180, 200, 200, 500), tuple(range(8))),
    "depart": Clip("lifecycle", 2, (400, 250, 200, 150, 200, 200, 200, 200), tuple(range(8))),
    "happy": Clip("pets", 0, (450, 600, 650, 900)),
    "nuzzle": Clip("pets", 1, (400, 550, 650, 1000)),
    "pet_stretch": Clip("petting-a", 0, (400, 550, 1100, 650, 800), (0, 1, 2, 3, 0)),
    "back_arch": Clip("petting-a", 1, (400, 550, 1100, 650, 800), (0, 1, 2, 3, 0)),
    "happy_hop": Clip("petting-a", 2, (450, 300, 350, 550, 800), (0, 1, 2, 3, 0)),
    "side_flop": Clip("petting-b", 0, (350, 450, 550, 1000, 450, 450, 650), (0, 1, 2, 3, 2, 1, 0)),
    "shoulder_peek": Clip("petting-b", 1, (400, 550, 1100, 650, 800), (0, 1, 2, 3, 0)),
    "knead": Clip("pets", 3, (450, 450, 450, 450), loop=True),
    "chin_scritch": Clip("affection", 0, (450, 650, 950, 850)),
    "blep": Clip("affection", 1, (500, 450, 750, 1100)),
    "paw_offer": Clip("petting-b", 2, (400, 550, 950, 500, 450, 800), (0, 1, 2, 3, 1, 0)),
    "ear_rub": Clip("affection", 3, (450, 600, 850, 1000)),
    "typing": Clip("activity", 0, (330, 330, 330, 330), loop=True),
    "groom": Clip("activity", 1, (600, 550, 700, 850)),
    "yawn": Clip("activity", 2, (600, 220, 650, 500)),
    "fall_asleep": Clip("transitions", 0, (350, 220, 220, 250, 250, 250, 300, 500), tuple(range(8))),
    "wake": Clip("transitions", 2, (350, 220, 220, 250, 250, 250, 300, 500), tuple(range(8))),
    "sleep": Clip("transitions", 1, (1400, 1400), (2, 3), loop=True),
    "walk": Clip("movement", 0, (240, 240, 240, 240), loop=True),
    "stretch": Clip("movement", 1, (550, 700, 600, 850)),
    "look_left": Clip("movement", 2, (350, 1100, 350, 1100, 700), (1, 0, 1, 2, 3)),
    "look_right": Clip("movement", 2, (350, 1100, 350, 1100, 700), (1, 2, 3, 0, 1)),
    "loaf": Clip("movement", 3, (2200, 160, 180, 1800), loop=True),
    "peek": Clip("idle", 0, (800, 160, 220, 1000)),
}


# Head width/height measured in the imported 128px source cells, ears through chin.
# Calibrate to idle's 62x50px head instead of fitting each whole-body silhouette.
# Remeasure these landmarks when replacing the versioned pet sheets.
PET_HEADS = {("pets", 0): (75, 64), ("pets", 1): (76, 64), ("pets", 3): (76, 64),
             ("affection", 0): (79, 67), ("affection", 1): (78, 65), ("affection", 3): (78, 65),
             ("petting-a", 0): (48, 46), ("petting-a", 1): (39, 38), ("petting-a", 2): (47, 43),
             ("petting-b", 0): (60, 51), ("petting-b", 1): (50, 45), ("petting-b", 2): (65, 57)}


class SpriteAtlas:
    def __init__(self, path):
        self.frames = {}
        cells = {}
        for bank, version, rows in (("idle", 3, 4), ("pets", 3, 4), ("activity", 3, 4),
                                    ("movement", 3, 4), ("transitions", 1, 4), ("affection", 1, 4),
                                    ("petting-a", 1, 3), ("petting-b", 1, 3),
                                    ("tailplay", 2, 4), ("lifecycle", 2, 4), ("tailswish", 1, 2)):
            filename = f"neko-{bank}-v{version}.png"
            image = QImage(str(Path(path) / filename))
            if image.isNull():
                return
            for row in range(rows):
                # Retired wave and malformed paw offer never enter the runtime atlas.
                if (bank, row) in (("pets", 2), ("affection", 2), ("idle", 1)):
                    continue
                for col in range(4):
                    left, top = col * image.width() // 4, row * image.height() // rows
                    right, bottom = (col + 1) * image.width() // 4, (row + 1) * image.height() // rows
                    region = QRect(left, top, right - left, bottom - top)
                    if bank in ("petting-a", "petting-b"):
                        # Drawn baselines can cross a nominal row; isolate the center silhouette with padding.
                        margin = region.height() // 5
                        region = region.adjusted(0, -margin, 0, margin).intersected(image.rect())
                    cell = image.copy(region).scaled(
                        128, 128, Qt.KeepAspectRatio, Qt.FastTransformation)
                    bounds = sprite_bounds(cell)
                    if bounds.isEmpty():
                        return
                    cells[bank, row, col] = cell.copy(bounds)
        for key, cell in cells.items():
            pet_head = PET_HEADS.get(key[:2])
            if pet_head:
                scale_x, scale_y = 62 / pet_head[0], 50 / pet_head[1]
                sprite = QPixmap.fromImage(cell).scaled(
                    round(cell.width() * scale_x), round(cell.height() * scale_y),
                    Qt.IgnoreAspectRatio, Qt.FastTransformation)
            elif key[0] in ("tailplay", "lifecycle", "tailswish"):
                start_row = key[1] // 2 * 2
                rows = range(start_row, start_row + 2)
                row_cells = [cells[key[0], row, col] for row in rows for col in range(4)]
                reference = cells["lifecycle", 1, 3] if key[0] == "lifecycle" and start_row == 0 else row_cells[0]
                scale = min(82 / reference.height(),
                            104 / max(cell.width() for cell in row_cells),
                            82 / max(cell.height() for cell in row_cells))
                sprite = QPixmap.fromImage(cell).scaled(
                    round(cell.width() * scale), round(cell.height() * scale),
                    Qt.IgnoreAspectRatio, Qt.FastTransformation)
            elif key[0] == "transitions":
                scale = 82 / cells["transitions", 0, 0].height()
                sprite = QPixmap.fromImage(cell).scaled(
                    round(cell.width() * scale), round(cell.height() * scale),
                    Qt.IgnoreAspectRatio, Qt.FastTransformation)
            elif key[:2] in (("activity", 3), ("movement", 3)):
                sprite = QPixmap.fromImage(cell).scaledToWidth(92, Qt.FastTransformation)
            else:
                sprite = QPixmap.fromImage(cell).scaled(104, 82, Qt.KeepAspectRatio, Qt.FastTransformation)
            frame = QPixmap(112, 112)
            frame.fill(Qt.transparent)
            painter = QPainter(frame)
            ground = 16 + round(cells[key[0], key[1], 0].height() * scale_y) if pet_head else 98
            if key == ("petting-a", 2, 2):
                ground -= 10
            left = (112 - sprite.width()) // 2
            if key[0] == "tailswish":
                # Anchor the seated body, not the changing width of its tail.
                left += (0, 1, 3, 4, 1, 1, 0, 0)[key[1] * 4 + key[2]]
            painter.drawPixmap(left, ground - sprite.height(), sprite)
            painter.end()
            self.frames[key] = frame
        # The shared seated drawing prevents a different face popping in at rest.
        idle = self.frames["idle", 0, 0]
        for key in (("lifecycle", 1, 3), ("lifecycle", 2, 0),
                    ("tailplay", 0, 0), ("tailplay", 1, 3),
                    ("tailplay", 2, 0), ("tailplay", 3, 3),
                    ("tailswish", 0, 0), ("tailswish", 1, 3)):
            self.frames[key] = idle

    def frame(self, name, elapsed, motion=True):
        if not motion and name in ("arrive", "depart"):
            return self.frames.get(("idle", 0, 0), QPixmap())
        clip = CLIPS[name]
        index = clip.frame_index(elapsed if motion else 0)
        source = self.frames.get((clip.bank, clip.row + index // 4, index % 4), QPixmap())
        if source.isNull() or name not in ("arrive", "depart"):
            return source
        # Flight follows elapsed time, independently of the held drawing.
        if name == "arrive":
            progress = max(0, min(1, elapsed / 0.42))
            offset = round(-112 * (1 - progress * progress))
        else:
            progress = max(0, min(1, (elapsed - 0.85) / 0.75))
            offset = round(-96 * progress + 208 * progress * progress)
        frame = QPixmap(112, 112)
        frame.fill(Qt.transparent)
        painter = QPainter(frame)
        painter.drawPixmap(0, offset, source)
        painter.end()
        return frame
