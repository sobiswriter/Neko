"""Native, test-owned background preview; never captures unrelated desktop content."""

import os
os.environ["QT_QPA_PLATFORM"] = "windows"

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import win32gui
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QApplication, QWidget
from thoughts import ThoughtLabel


class Pattern(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        for x in range(0, 840, 8):
            colors = ("#f6f4ed", "#b0a591") if x < 420 else ("#18232d", "#687d85")
            painter.fillRect(x, 0, 8, 210, QColor(colors[(x // 8) % 2]))
        painter.setFont(QFont("Segoe UI", 10))
        for x, color, text in ((16, "#403a34", "Light / detailed background"),
                               (436, "#f5eee5", "Dark / detailed background")):
            painter.setPen(QColor(color))
            painter.drawText(x, 17, text)


app = QApplication([])
foreground = win32gui.GetForegroundWindow()
host = Pattern(None, Qt.Tool | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus)
host.setAttribute(Qt.WA_ShowWithoutActivating)
area = app.primaryScreen().availableGeometry()
host.move(area.left() + 20, area.top() + 20)
host.setFixedSize(840, 210)
host.show()
labels = []
for text, x in (("Look at meeee!", 60),
                ("A little thought, with just enough frost to keep it readable.", 470)):
    label = ThoughtLabel()
    label.setText(text)
    label.adjustSize()
    label.move(host.x() + x, host.y() + 75)
    label.show()
    labels.append(label)
result = {}


def capture():
    try:
        image = app.primaryScreen().grabWindow(0, host.x(), host.y(), 840, 210)
        image.save(str(ROOT / "docs/neko-thoughts-native.png"))
        pixels = image.toImage()
        stripe = [pixels.pixelColor(x, 81).lightness() for x in range(90, 170)]
        result.update(native_backdrop=all(label.native_backdrop for label in labels),
                      click_through_to_test_window=all(win32gui.WindowFromPoint(
                          (label.x() + label.width() // 2, label.y() + label.height() // 2))
                          == int(host.winId()) for label in labels),
                      foreground_unchanged=win32gui.GetForegroundWindow() == foreground,
                      sizes=[[label.width(), label.height()] for label in labels],
                      frosted_stripe_contrast=max(stripe) - min(stripe),
                      background_stripe_contrast=246 - 176,
                      dpr=app.primaryScreen().devicePixelRatio())
        result["passed"] = (result["native_backdrop"] and result["click_through_to_test_window"]
                            and result["foreground_unchanged"] and result["frosted_stripe_contrast"] < 35)
        (ROOT / "docs/thoughts-native.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result))
    finally:
        app.quit()


QTimer.singleShot(900, capture)
app.exec()
sys.exit(0 if result.get("passed") else 1)
