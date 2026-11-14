"""Synchronized old/new victory comparison at native size (docs/v1.2-wins-compare.png)."""
import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PySide6.QtGui import QColor, QFont, QImage, QPainter
from PySide6.QtWidgets import QApplication

from animations import CANVAS_HEIGHT, CANVAS_WIDTH, CLIPS, Clip, SpriteAtlas

RETIRED = {
    "retired: prize hug": Clip("game-win-grasp", 0, (150,) * 19, tuple(range(1, 15)) + (13, 2, 1, 18, 19)),
    "retired: proud sit": Clip("game-win-proud", 0, (150,) * 19, tuple(range(1, 20))),
}
CURRENT = {"kept: triple hop": CLIPS["game_win_0"], "new: sproing": CLIPS["game_win_1"],
           "new: victory roll": CLIPS["game_win_2"], "new: sproing (2nd take)": CLIPS["game_win_3"]}
STEP, COLUMNS = 0.3, 20


def frame(atlas, clip, elapsed):
    index = clip.frame_index(elapsed)
    return atlas.frames[clip.bank, clip.row + index // 4, index % 4]


def main():
    app = QApplication.instance() or QApplication([])
    atlas = SpriteAtlas(ROOT / "assets")
    rows = list(RETIRED.items()) + list(CURRENT.items())
    label = 130
    sheet = QImage(label + COLUMNS * CANVAS_WIDTH // 2, len(rows) * (CANVAS_HEIGHT // 2 + 6) + 20, QImage.Format_ARGB32)
    sheet.fill(QColor("#efe9e1"))
    p = QPainter(sheet)
    p.setFont(QFont("Segoe UI", 8))
    p.setPen(QColor("#333"))
    p.drawText(4, 14, f"Same clock for every row: one sample every {int(STEP * 1000)} ms (half size)")
    for r, (name, clip) in enumerate(rows):
        y = 20 + r * (CANVAS_HEIGHT // 2 + 6)
        p.drawText(4, y + CANVAS_HEIGHT // 4, name)
        for c in range(COLUMNS):
            t = c * STEP
            if t * 1000 > sum(clip.durations) + 300:
                break
            image = frame(atlas, clip, t).toImage().scaled(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2)
            p.drawImage(label + c * CANVAS_WIDTH // 2, y, image)
    p.end()
    out = ROOT / "docs" / "v1.2-wins-compare.png"
    sheet.save(str(out))
    print(out)


if __name__ == "__main__":
    main()
