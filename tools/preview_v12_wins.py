"""Synchronized victory comparison at native size (docs/v1.2-wins-compare.png).

Each new victory is shown twice on the same clock: the earlier smooth-scaled import
("before") and the current 2px pixelated redraw ("now"), under the kept triple hop.
Run with QT_QPA_PLATFORM=windows so the labels have a font.
"""
import os
from pathlib import Path
import sys
from unittest.mock import patch
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PySide6.QtGui import QColor, QFont, QImage, QPainter
from PySide6.QtWidgets import QApplication
import animations
from animations import CANVAS_HEIGHT, CANVAS_WIDTH, CLIPS, SpriteAtlas
VICTORIES = (("sproing", "game_win_1"), ("victory roll", "game_win_2"), ("sproing, 2nd take", "game_win_3"))
STEP, COLUMNS = 0.3, 14
def frame(atlas, clip, elapsed):
    index = clip.frame_index(elapsed)
    return atlas.frames[clip.bank, clip.row + index // 4, index % 4]
def main():
    app = QApplication.instance() or QApplication([])
    pixel = SpriteAtlas(ROOT / "assets")
    with patch.object(animations, "pixelate", lambda image, palette: image):
        smooth = SpriteAtlas(ROOT / "assets")
    rows = [("kept: triple hop", pixel, CLIPS["game_win_0"])]
    for name, key in VICTORIES:
        rows += [(f"before: {name}", smooth, CLIPS[key]), (f"now: {name}", pixel, CLIPS[key])]
    label = 140
    sheet = QImage(label + COLUMNS * CANVAS_WIDTH, len(rows) * (CANVAS_HEIGHT + 6) + 20, QImage.Format_ARGB32)
    sheet.fill(QColor("#efe9e1"))
    p = QPainter(sheet)
    p.setFont(QFont("Segoe UI", 9))
    p.setPen(QColor("#333"))
    p.drawText(4, 14, f"Native size. Same clock for every row: one sample every {int(STEP * 1000)} ms")
    for r, (name, atlas, clip) in enumerate(rows):
        y = 20 + r * (CANVAS_HEIGHT + 6)
        p.drawText(4, y + CANVAS_HEIGHT // 2, name)
        for c in range(COLUMNS):
            t = c * STEP
            if t * 1000 > sum(clip.durations) + 300:
                break
            p.drawImage(label + c * CANVAS_WIDTH, y, frame(atlas, clip, t).toImage())
    p.end()
    out = ROOT / "docs" / "v1.2-wins-compare.png"
    sheet.save(str(out))
    print(out)
if __name__ == "__main__":
    main()
