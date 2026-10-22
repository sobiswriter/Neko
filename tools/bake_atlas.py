"""Prepare the existing calibrated atlas once during packaging, never at launch."""
import json
import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication
from animations import SpriteAtlas, CLIPS, CANVAS_WIDTH, CANVAS_HEIGHT


def bake(atlas, output):
    keys = list(atlas.frames)
    required = {(clip.bank, clip.row + i // 4, i % 4)
                for clip in CLIPS.values() for i in clip.order}
    if not keys or not required.issubset(keys):
        raise ValueError("Cannot package an incomplete animation atlas")
    sheet = QImage(16 * CANVAS_WIDTH, ((len(keys) + 15) // 16) * CANVAS_HEIGHT,
                   QImage.Format_ARGB32_Premultiplied)
    sheet.fill(Qt.transparent)
    painter = QPainter(sheet)
    for i, key in enumerate(keys):
        painter.drawPixmap(i % 16 * CANVAS_WIDTH, i // 16 * CANVAS_HEIGHT, atlas.frames[key])
    painter.end()
    output.mkdir(parents=True, exist_ok=True)
    if not sheet.save(str(output / "neko-runtime.png")):
        raise OSError("Could not save the packaged animation atlas")
    (output / "neko-runtime.json").write_text(json.dumps(keys), encoding="utf-8")


if __name__ == "__main__":
    app = QApplication.instance() or QApplication([])
    bake(SpriteAtlas(ROOT / "assets"), Path(sys.argv[1]))
