"""Drawn sprite sequences with per-frame timing and a shared ground anchor."""

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QImage, QPixmap, QPainter

CANVAS_WIDTH = 192
CANVAS_PADDING = (CANVAS_WIDTH - 112) // 2
CANVAS_TOP = 32
CANVAS_HEIGHT = 112 + CANVAS_TOP


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
    "tail": Clip("tailswish", 0, (300, 220, 220, 350, 220, 220, 280, 450, 700), (0, 1, 2, 3, 4, 5, 6, 8, 7)),
    "ears": Clip("idleplay-b", 2, (300, 250, 400, 250, 250, 350, 450, 700), tuple(range(8))),
    "sniff": Clip("idleplay-b", 0, (300, 300, 350, 300, 450, 350, 450, 700), tuple(range(8))),
    "tail_chase": Clip("tailplay", 0, (300, 180, 180, 100) + (50,) * 55 + (100, 180, 300, 600),
                       (16, 17, 18, 19) + tuple(range(11)) * 5 + (20, 21, 22, 23)),
    "tail_catch": Clip("tailplay", 0, (300, 180, 180, 100) + (50,) * 22 + (120, 350, 120, 150, 180, 300, 600),
                       (16, 17, 18, 19) + tuple(range(11)) * 2 + (13, 14, 13, 12, 21, 22, 23)),
    "arrive": Clip("arrival", 0, (200, 200, 300, 120, 180, 160, 220, 520), tuple(range(8))),
    "depart": Clip("lifecycle", 2, (650, 350, 200, 150, 200, 200, 200, 200), tuple(range(8))),
    "happy": Clip("pet-happy", 0, (100, 100, 100, 150, 150, 200, 250, 150,
                                 200, 200, 150, 150, 200, 200, 150, 350), tuple(range(16))),
    "nuzzle": Clip("pet-nuzzle", 0, (100, 100, 150, 150, 150, 200, 200, 200, 200, 200,
                                   200, 200, 250, 150, 150, 150, 150, 200, 200, 400), tuple(range(20))),
    "pet_stretch": Clip("pet-pet_stretch", 0, (100, 100, 150, 150, 200, 150, 150, 200, 150, 150, 250, 300,
                                              250, 250, 500, 500, 200, 150, 150, 150, 150, 150, 200, 500), tuple(range(24))),
    "back_arch": Clip("pet-back_arch", 0, (100, 100, 150, 150, 200, 150, 150, 150, 150, 250, 250, 250,
                                          250, 450, 350, 200, 150, 150, 150, 150, 150, 150, 200, 500), tuple(range(24))),
    "happy_hop": Clip("pet-happy_hop", 0, (100, 150, 150, 200, 100, 150, 150, 150, 150, 200,
                                         150, 100, 150, 200, 150, 150, 200, 150, 100, 100,
                                         150, 100, 100, 200, 250, 300, 350, 600), tuple(range(28))),
    "side_flop": Clip("pet-side_flop", 0, (100, 100, 100, 100, 100, 100, 150, 150, 400, 400, 400, 400,
                                         150, 250, 200, 150, 200, 250, 200, 250, 300, 300, 350,
                                         250, 300, 250, 300, 600), tuple(range(28))),
    "shoulder_peek": Clip("pet-shoulder_peek", 0, (100, 100, 100, 150, 200, 300, 350, 100, 100, 100, 100,
                                                 150, 250, 600, 250, 250, 150, 200, 450, 250, 250,
                                                 300, 300, 300, 150, 150, 200, 500), tuple(range(28))),
    "knead": Clip("pet-knead", 0, (100,) * 6 + (100, 100, 50, 50, 100, 100, 100, 100, 50, 50, 100, 50) * 4
                  + (150, 150, 150, 150, 300, 500),
                  tuple(range(6)) + tuple(range(6, 18)) * 4 + tuple(range(18, 24))),
    "chin_scritch": Clip("pet-chin_scritch", 0, (100, 100, 150, 150, 200, 200, 300, 200,
                                               200, 200, 200, 150, 150, 150, 150, 400), tuple(range(16))),
    "roll": Clip("pet-roll", 0, (100, 150, 150, 150, 200, 200, 150, 150, 200, 250, 300, 250,
                                400, 350, 350, 250, 200, 200, 200, 200, 200, 350, 350, 500), tuple(range(24))),
    "paw_offer": Clip("pet-paw_offer", 0, (100, 100, 100, 150, 150, 150, 150, 250, 200, 250,
                                         300, 300, 150, 150, 150, 150, 150, 150, 200, 300), tuple(range(20))),
    "ear_rub": Clip("pet-ear_rub", 0, (100, 100, 150, 150, 200, 200, 250, 200,
                                     250, 200, 200, 150, 150, 150, 150, 350), tuple(range(16))),
    "typing": Clip("activity", 0, (330, 330, 330, 330), loop=True),
    "groom": Clip("idleplay-a", 0, (300, 250, 550, 650, 550, 300, 450, 600), tuple(range(8))),
    "yawn": Clip("idleplay-c", 0, (300, 350, 350, 650, 350, 350, 450, 650), tuple(range(8))),
    "fall_asleep": Clip("transitions", 0, (350, 220, 220, 250, 250, 250, 300, 500), tuple(range(8))),
    "wake": Clip("transitions", 2, (350, 220, 220, 250, 250, 250, 300, 500), tuple(range(8))),
    "sleep": Clip("transitions", 1, (1400, 1400), (2, 3), loop=True),
    "walk": Clip("game-walk", 0, (120,) * 8, tuple(range(4, 12)), loop=True),
    "stretch": Clip("idleplay-a", 2, (300, 250, 400, 650, 450, 300, 400, 650), tuple(range(8))),
    "look_left": Clip("idleplay-c", 4, (300, 400, 850, 450, 700), (0, 1, 2, 3, 7)),
    "look_right": Clip("idleplay-c", 4, (300, 400, 850, 450, 700), (0, 4, 5, 6, 7)),
    "loaf": Clip("idleplay-a", 4, (300, 300, 350, 1800, 350, 900, 500, 900), tuple(range(8))),
    "peek": Clip("idleplay-c", 2, (300, 350, 450, 600, 350, 500, 450, 650), tuple(range(8))),
}


PET_ROWS = {"happy": 4, "nuzzle": 5, "knead": 6, "chin_scritch": 4, "roll": 6, "paw_offer": 5,
            "ear_rub": 4, "pet_stretch": 6, "back_arch": 6, "happy_hop": 7, "side_flop": 7,
            "shoulder_peek": 7}

# Preserve the last drawn recovery before handing off to the actual seated idle.
for name, rows in PET_ROWS.items():
    clip = CLIPS[name]
    durations = clip.durations[:-1] + (150, clip.durations[-1] - 150)
    # Slightly brisker petting; retain at least one 50ms repaint per drawing.
    CLIPS[name] = Clip(clip.bank, clip.row, tuple(max(50, round(ms / 1.15)) for ms in durations),
                       clip.order + (rows * 4,))

# Held mood variants share a 2.4-second body phase clock.
CARRY_ROWS = {"lift": 4, "calm": 3, "excited": 3, "unimpressed": 3, "sleepy": 3, "bridges": 3,
              "side": 2, "low": 2, "roll": 2}
CLIPS.update({
    "pickup": Clip("carry-lift", 0, (50,) * 8, tuple(range(8))),
    "set_down": Clip("carry-lift", 0, (50, 70, 70, 80, 80, 80, 80, 90, 100), tuple(range(8, 17))),
    "carry_to_calm": Clip("carry-bridges", 0, (100,) * 4),
    "carry_to_unimpressed": Clip("carry-bridges", 1, (100,) * 4),
    "carry_open_eyes": Clip("carry-bridges", 2, (50,) * 4),
    "carry_yawn": Clip("carry-sleepy", 0, (150, 150, 200, 150)),
})
for mood in ("excited", "calm", "unimpressed", "sleepy"):
    order = tuple(range(4, 12)) if mood == "sleepy" else tuple(range(12))
    CLIPS[f"held_{mood}"] = Clip(f"carry-{mood}", 0, (2400 // len(order),) * len(order), order, loop=True)

GAME_ROWS = {"emotion": 6, "hunt": 6, "walk": 4, "ready": 4, "win-hop": 6,
             "win-grasp": 5, "win-proud": 5, "loss-a": 4, "loss-b": 4, "loss-c": 4, "loss-bridge": 2, "run": 3}
CLIPS.update({
    "game_ready": Clip("game-ready", 0, (200,) * 4),
    "game_three": Clip("game-ready", 0, (250,) * 4, (4, 5, 6, 7)),
    "game_two": Clip("game-ready", 0, (250,) * 4, (8, 9, 10, 11)),
    "game_one": Clip("game-ready", 0, (250,) * 4, (12, 13, 14, 15)),
    "game_go": Clip("game-ready", 0, (350,), (15,)),
    "game_ready_cancel": Clip("game-ready", 0, (60,) * 16, tuple(reversed(range(16)))),
    "game_run": Clip("game-run", 0, (90,) * 8, tuple(range(1, 9)), loop=True),
    "game_turn": Clip("game-run", 0, (100, 100, 150), (9, 10, 11)),
    "game_prepare": Clip("game-hunt", 0, (200,), (16,)),
    "game_jump": Clip("game-hunt", 0, (40, 80, 80, 240, 40, 60, 50, 50), tuple(range(16, 24))),
    "game_miss": Clip("game-hunt", 0, (150, 150, 150), (23, 14, 2)),
    "game_settle": Clip("game-walk", 0, (120, 150, 150, 150, 150), (12, 13, 14, 15, 16)),
    "game_win_0": Clip("game-win-hop", 0, (100,) * 18 + (220, 180, 160, 150, 300), tuple(range(1, 24))),
    "game_win_1": Clip("game-win-grasp", 0, (150,) * 19, tuple(range(1, 15)) + (13, 2, 1, 18, 19)),
    "game_win_2": Clip("game-win-proud", 0, (150,) * 19, tuple(range(1, 20))),
    "game_loss_0": Clip("game-loss-a", 0, (170,) * 15, tuple(range(1, 16))),
    "game_loss_1": Clip("game-loss-b", 0, (170,) * 15, tuple(range(1, 16))),
    "game_loss_2": Clip("game-loss-c", 0, (170,) * 15, tuple(range(1, 16))),
    "game_loss_finish": Clip("game-loss-bridge", 0, (120,) * 7, tuple(range(1, 8))),
    "game_curl": Clip("game-emotion", 0, (900, 900, 900, 900), (8, 9, 10, 11), loop=True),
    "game_comfort": Clip("game-emotion", 0, (150,) * 10 + (250, 250), tuple(range(12, 24))),
    "game_gentle_rest": Clip("game-hunt", 0, (1000,), (2,)),
    "game_gentle_reach": Clip("game-hunt", 0, (1000,), (19,)),
})


def held_clip(elapsed, sleeping=False):
    if sleeping:
        return "held_sleepy", elapsed
    if elapsed < 0.4:
        return "pickup", elapsed
    for start, duration, name in ((3, 0.4, "carry_to_calm"), (10, 0.4, "carry_to_unimpressed"),
                                  (20, 0.65, "carry_yawn")):
        if start <= elapsed < start + duration:
            return name, elapsed - start
    mood = "excited" if elapsed < 3 else "calm" if elapsed < 10 else "unimpressed" if elapsed < 20 else "sleepy"
    return f"held_{mood}", elapsed


# Seated head landmarks in each eight-pose idle story's imported source cells.
IDLE_HEADS = {("idleplay-a", 0): (67, 56), ("idleplay-a", 2): (68, 54), ("idleplay-a", 4): (66, 51),
              ("idleplay-b", 0): (71, 55), ("idleplay-b", 2): (71, 57),
              ("idleplay-c", 0): (85, 66), ("idleplay-c", 2): (86, 66), ("idleplay-c", 4): (87, 70)}


def drop_progress(elapsed):
    duration = sum(CLIPS["arrive"].durations[:3]) / 1000
    return max(0, min(1, elapsed / duration)) ** 2


def pet_landmarks(image):
    """Read the seated head reference and ground contacts without recentering the tail."""
    alpha = image.convertToFormat(QImage.Format_Alpha8)
    pixels = bytes(alpha.constBits())
    stride, width, height = alpha.bytesPerLine(), alpha.width(), alpha.height()
    longest, head_center = 0, width / 2
    for y in range(height * 3 // 5):
        run = 0
        for x in range(width):
            run = run + 1 if pixels[y * stride + x] >= 128 else 0
            if run > longest:
                longest, head_center = run, x - (run - 1) / 2
    contacts = [x for y in range(max(0, height - 14), height) for x in range(width)
                if pixels[y * stride + x] >= 128]
    return longest, head_center, min(contacts), max(contacts)


def carry_head(image):
    alpha = image.convertToFormat(QImage.Format_Alpha8)
    data, stride = bytes(alpha.constBits()), alpha.bytesPerLine()
    longest, center = 0, image.width() / 2
    # Lower rows can join the high tail to the cheek; measure only the upper head.
    for y in range(image.height() * 2 // 5):
        run = 0
        for x in range(image.width()):
            run = run + 1 if data[y * stride + x] >= 128 else 0
            if run > longest:
                longest, center = run, x - (run - 1) / 2
    return longest, center


class SpriteAtlas:
    def __init__(self, path):
        self.frames = {}
        cells = {}
        for bank, version, rows in (("idle", 3, 4), ("activity", 3, 4),
                                    ("movement", 3, 4), ("transitions", 1, 4),
                                    ("tailplay", 4, 4), ("lifecycle", 2, 4), ("tailswish", 1, 2),
                                    ("arrival", 1, 2), ("farewell", 1, 1), ("tailsettle", 1, 2),
                                    ("idleplay-a", 1, 6), ("idleplay-b", 1, 6), ("idleplay-c", 1, 6)):
            filename = f"neko-{bank}-v{version}.png"
            image = QImage(str(Path(path) / filename))
            if image.isNull():
                return
            for row in range(rows):
                # Retired idle and lifecycle rows never enter the runtime atlas.
                if (bank, row) in (("idle", 1),
                                   ("idle", 2), ("idle", 3), ("activity", 1), ("activity", 2),
                                   ("movement", 1), ("movement", 2), ("movement", 3),
                                   ("idleplay-b", 4), ("idleplay-b", 5),
                                   ("lifecycle", 0), ("lifecycle", 1)):
                    continue
                for col in range(4):
                    if bank == "farewell" and col >= 2:
                        continue
                    left, top = col * image.width() // 4, row * image.height() // rows
                    right, bottom = (col + 1) * image.width() // 4, (row + 1) * image.height() // rows
                    region = QRect(left, top, right - left, bottom - top)
                    if bank in ("arrival", "tailplay", "tailsettle") or bank.startswith("idleplay-"):
                        # Drawn baselines can cross a nominal row; isolate the center silhouette with padding.
                        margin = region.height() // (3 if bank.startswith("idleplay-") else 5)
                        region = region.adjusted(0, -margin, 0, margin).intersected(image.rect())
                    if bank in ("tailplay", "tailsettle") or bank.startswith("idleplay-"):
                        margin = (right - left) // 5
                        region = region.adjusted(-margin, 0, margin, 0).intersected(image.rect())
                    cell = image.copy(region)
                    if bank in ("arrival", "tailplay", "tailsettle") or bank.startswith("idleplay-"):
                        cell = cell.scaledToWidth(round(128 * region.width() / (right - left)),
                                                  Qt.FastTransformation)
                    else:
                        cell = cell.scaled(128, 128, Qt.KeepAspectRatio, Qt.FastTransformation)
                    bounds = sprite_bounds(cell)
                    if bounds.isEmpty():
                        return
                    cells[bank, row, col] = cell.copy(bounds)
        for key, cell in cells.items():
            if key[0].startswith("idleplay-"):
                start_row = key[1] // 2 * 2
                head_width, head_height = IDLE_HEADS[key[0], start_row]
                scale_x, scale_y = 62 / head_width, 50 / head_height
                group = [cells[key[0], row, col] for row in (start_row, start_row + 1) for col in range(4)]
                fit = min(1, 108 / max(cell.width() * scale_x for cell in group),
                          98 / max(cell.height() * scale_y for cell in group))
                sprite = QPixmap.fromImage(cell).scaled(
                    round(cell.width() * scale_x * fit), round(cell.height() * scale_y * fit),
                    Qt.IgnoreAspectRatio, Qt.FastTransformation)
            elif key[0] in ("tailplay", "lifecycle", "tailswish", "arrival", "farewell", "tailsettle"):
                start_row = 0 if key[0] == "tailplay" else key[1] // 2 * 2
                rows = range(4) if key[0] == "tailplay" else range(start_row, start_row + (1 if key[0] == "farewell" else 2))
                row_cells = [cells[key[0], row, col] for row in rows
                             for col in range(2 if key[0] == "farewell" else 4)]
                reference = (cells["tailplay", 3, 3] if key[0] == "tailplay" else
                             cells["arrival", 1, 3] if key[0] == "arrival" else row_cells[0])
                scale = min(82 / reference.height(),
                            104 / max(cell.width() for cell in row_cells),
                            (82 if key[0] in ("lifecycle", "tailswish") else 98)
                            / max(cell.height() for cell in row_cells))
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
            frame = QPixmap(CANVAS_WIDTH, 112)
            frame.fill(Qt.transparent)
            painter = QPainter(frame)
            ground = 98
            left = (CANVAS_WIDTH - sprite.width()) // 2
            if key[0] == "tailswish":
                # Anchor the seated body, not the changing width of its tail.
                left += (0, 1, 3, 4, 1, 1, 0, 0)[key[1] * 4 + key[2]]
            painter.drawPixmap(left, ground - sprite.height(), sprite)
            painter.end()
            self.frames[key] = frame
        # Append the separately calibrated entry/settle drawings to the tail sequence.
        for row in range(2):
            for col in range(4):
                self.frames["tailplay", row + 4, col] = self.frames.pop(("tailsettle", row, col))
        # The shared seated drawing prevents a different face popping in at rest.
        idle = self.frames["idle", 0, 0]
        for key in (("arrival", 1, 3), ("tailplay", 2, 3), ("tailplay", 3, 3),
                    ("tailplay", 4, 0), ("tailplay", 5, 3),
                    ("tailswish", 0, 0), ("tailswish", 1, 3)):
            self.frames[key] = idle
        self.frames["tailswish", 2, 0] = self.frames["idle", 0, 2]
        for bank in ("idleplay-a", "idleplay-b", "idleplay-c"):
            for row in range(0, 4 if bank == "idleplay-b" else 6, 2):
                self.frames[bank, row, 0] = idle
                self.frames[bank, row + 1, 3] = idle
        self.frames["lifecycle", 2, 0] = self.frames["farewell", 0, 0]
        self.frames["lifecycle", 2, 1] = self.frames["farewell", 0, 1]
        self.load_pets(path, idle)
        for key, source in self.frames.items():
            frame = QPixmap(CANVAS_WIDTH, CANVAS_HEIGHT)
            frame.fill(Qt.transparent)
            painter = QPainter(frame)
            painter.drawPixmap(0, CANVAS_TOP, source)
            painter.end()
            self.frames[key] = frame
        self.load_carry(path)
        self.load_games(path)

    def load_games(self, path):
        """All-or-nothing game art; constant calibration from each bank's neutral."""
        imported = {}
        idle = self.frames["idle", 0, 0]
        for name, rows in GAME_ROWS.items():
            version = 1 if name == "emotion" else 2
            image = QImage(str(Path(path) / f"neko-game-{name}-v{version}.png"))
            if image.isNull() or image.width() % 4 or image.height() % rows:
                return
            width, height = image.width() // 4, image.height() // rows
            poses = []
            for index in range(rows * 4):
                cell = image.copy(index % 4 * width, index // 4 * height, width, height).scaledToWidth(128, Qt.FastTransformation)
                bounds = sprite_bounds(cell)
                if bounds.isEmpty():
                    return
                poses.append(cell.copy(bounds))
            head = pet_landmarks(poses[0])[0]
            sx, sy = 62 / head, 82 / poses[0].height()
            for index, pose in enumerate(poses):
                sprite = QPixmap.fromImage(pose).scaled(round(pose.width() * sx), round(pose.height() * sy),
                                                       Qt.IgnoreAspectRatio, Qt.FastTransformation)
                if sprite.width() > CANVAS_WIDTH - 4 or sprite.height() > CANVAS_HEIGHT - 4:
                    return
                frame = QPixmap(CANVAS_WIDTH, CANVAS_HEIGHT)
                frame.fill(Qt.transparent)
                painter = QPainter(frame)
                hop = 0
                if name == "win-hop":
                    hop = (0, 0, 0, 0, 3, 9, 4, 0, 0, 5, 13, 5, 0, 0, 3, 8, 4, 0, 0, 0, 0, 0, 0, 0)[index]
                elif name == "win-grasp":
                    hop = {9: 4, 10: 10, 11: 4}.get(index, 0)
                elif name == "run":
                    hop = {3: 5, 4: 8}.get(index, 0)
                left = (CANVAS_WIDTH - sprite.width()) // 2 + (2 if name in ("win-hop", "win-grasp") else 0)
                painter.drawPixmap(left, 130 - hop - sprite.height(), sprite)
                painter.end()
                imported[f"game-{name}", index // 4, index % 4] = frame
        for name, indices in (("hunt", (0, 15)), ("emotion", (0, 23)), ("walk", (0,)),
                              ("ready", (0,)), ("win-hop", (0, 23)), ("win-grasp", (0, 19)),
                              ("win-proud", (0, 19)), ("loss-a", (0,)), ("loss-b", (0,)), ("loss-c", (0,))):
            for index in indices:
                imported[f"game-{name}", index // 4, index % 4] = idle
        imported["game-walk", 4, 0] = idle
        imported["game-loss-bridge", 1, 3] = imported["game-emotion", 2, 0]
        self.frames.update(imported)

    def load_carry(self, path):
        idle = self.frames["idle", 0, 0]
        carry_frames = {}
        bounds = sprite_bounds(idle.toImage())
        idle_head = bounds.left() + pet_landmarks(idle.toImage().copy(bounds))[1]
        for name, rows in CARRY_ROWS.items():
            image = QImage(str(Path(path) / f"neko-carry-{name}-v1.png"))
            if image.isNull() or image.width() % 4 or image.height() % rows:
                return
            poses = []
            for index in range(rows * 4):
                row, col = divmod(index, 4)
                cell = image.copy(col * image.width() // 4, row * image.height() // rows,
                                  image.width() // 4, image.height() // rows)
                cell = cell.scaledToWidth(128, Qt.FastTransformation)
                bounds = sprite_bounds(cell)
                if bounds.isEmpty():
                    return
                poses.append(cell.copy(bounds))
            family = name in ("side", "low", "roll")
            reference = poses[-1] if family else poses[0]
            head_width, reference_head = carry_head(reference)
            sx = 62 / head_width
            sy = 82 / poses[0].height() if name == "lift" else sx
            for index, pose in enumerate(poses):
                _, head_center = carry_head(pose)
                sprite = QPixmap.fromImage(pose).scaled(round(pose.width() * sx), round(pose.height() * sy),
                                                       Qt.IgnoreAspectRatio, Qt.FastTransformation)
                crown = (48, 48, 46, 42, 34, 24, 18, 16, 18, 24, 34, 48, 48, 51, 48, 48)[index] if name == "lift" else 16
                left = round(idle_head - head_center * sx)
                if family:
                    progress = index / (len(poses) - 1)
                    crown = round((98 + CANVAS_TOP - sprite.height()) * (1 - progress) + 16 * progress)
                    target = idle_head + (reference.width() / 2 - reference_head) * sx
                    left = round(target - sprite.width() / 2)
                frame = QPixmap(CANVAS_WIDTH, CANVAS_HEIGHT)
                frame.fill(Qt.transparent)
                painter = QPainter(frame)
                painter.drawPixmap(left, crown, sprite)
                painter.end()
                carry_frames[f"carry-{name}", index // 4, index % 4] = frame
        carry_frames["carry-lift", 0, 0] = idle
        carry_frames["carry-lift", 4, 0] = idle
        self.frames.update(carry_frames)

    def load_pets(self, path, idle):
        idle_bounds = sprite_bounds(idle.toImage())
        _, idle_head, _, _ = pet_landmarks(idle.toImage().copy(idle_bounds))
        idle_head += idle_bounds.left()
        for name, rows in PET_ROWS.items():
            image = QImage(str(Path(path) / f"neko-pet-{name}-v1.png"))
            if image.isNull():
                return
            poses = []
            for index in range(rows * 4):
                row, col = divmod(index, 4)
                left, top = col * image.width() // 4, row * image.height() // rows
                region = QRect(left, top, image.width() // 4, image.height() // rows)
                region = region.adjusted(0, -region.height() // 8, 0, region.height() // 8).intersected(image.rect())
                cell = image.copy(region).scaledToWidth(128, Qt.FastTransformation)
                bounds = sprite_bounds(cell)
                if bounds.isEmpty():
                    return
                poses.append(cell.copy(bounds))
            head_width, reference_head, reference_left, reference_right = pet_landmarks(poses[0])
            scale_x, scale_y = 62 / head_width, 82 / poses[0].height()
            # Calibrate support contacts against the head so a different tail/haunch width cannot shift rest.
            center = idle_head + ((reference_left + reference_right) / 2 - reference_head) * scale_x
            right = idle_head + (reference_right - reference_head) * scale_x
            for index, pose in enumerate(poses):
                _, head_center, foot_left, foot_right = pet_landmarks(pose)
                anchor, target = (foot_left + foot_right) / 2, center
                if name in ("pet_stretch", "back_arch"):
                    anchor, target = foot_right, right
                elif name == "happy_hop":
                    anchor, target = head_center, idle_head
                elif name == "roll":
                    anchor = pose.width() / 2
                    target = idle_head + (poses[0].width() / 2 - reference_head) * scale_x
                sprite = QPixmap.fromImage(pose).scaled(round(pose.width() * scale_x),
                    round(pose.height() * scale_y), Qt.IgnoreAspectRatio, Qt.FastTransformation)
                ground = 98
                if name == "happy_hop":
                    ground -= (0, 0, 0, 0, 3, 8, 11, 6, 0, 0, 0, 4, 10, 13,
                               7, 0, 0, 0, 2, 6, 8, 4, 0, 0, 0, 0, 0, 0)[index]
                frame = QPixmap(CANVAS_WIDTH, 112)
                frame.fill(Qt.transparent)
                painter = QPainter(frame)
                left = round(target - anchor * scale_x)
                if sprite.width() <= CANVAS_WIDTH - 4:
                    left = max(2, min(left, CANVAS_WIDTH - 2 - sprite.width()))
                painter.drawPixmap(left, ground - sprite.height(), sprite)
                painter.end()
                self.frames[f"pet-{name}", index // 4, index % 4] = (
                    idle if index == 0 else frame)
            self.frames[f"pet-{name}", rows, 0] = idle

    def frame(self, name, elapsed, motion=True):
        if not motion and name in ("arrive", "depart"):
            return self.frames.get(("idle", 0, 0), QPixmap())
        clip = CLIPS[name]
        index = clip.frame_index(elapsed if motion else 0)
        source = self.frames.get((clip.bank, clip.row + index // 4, index % 4), QPixmap())
        if source.isNull() or name != "depart":
            return source
        # Preserve the accepted hop arc after the longer sad pause and crouch.
        launch = sum(clip.durations[:3]) / 1000
        progress = max(0, min(1, (elapsed - launch) / 0.75))
        offset = round(-96 * progress + 208 * progress * progress)
        frame = QPixmap(CANVAS_WIDTH, CANVAS_HEIGHT)
        frame.fill(Qt.transparent)
        painter = QPainter(frame)
        painter.drawPixmap(0, offset, source)
        painter.end()
        return frame
