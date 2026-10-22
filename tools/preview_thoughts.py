"""Native, test-owned background preview; never captures unrelated desktop content."""

import os
os.environ["QT_QPA_PLATFORM"] = "windows"

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import win32gui
from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QApplication, QGraphicsDropShadowEffect, QWidget
from PySide6.QtTest import QTest
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
QTest.qWait(150)
baseline = app.primaryScreen().grabWindow(0, host.x(), host.y(), 840, 210).toImage()
labels = []
for text, x in (("Look at meeee!", 60),
                ("A little thought, with just enough frost to keep it readable.", 470)):
    label = ThoughtLabel()
    shadow = QGraphicsDropShadowEffect(label)
    shadow.setBlurRadius(4)
    shadow.setOffset(0, 1)
    shadow.setColor(QColor("#33261f"))
    label.setGraphicsEffect(shadow)
    label.setText(text)
    label.adjustSize()
    label.move(host.x() + x, host.y() + 75)
    label.prepare_backdrop()
    label.show()
    labels.append(label)
result = {}
cases = []


def capture():
    again = False
    try:
        image = app.primaryScreen().grabWindow(0, host.x(), host.y(), 840, 210)
        image.save(str(ROOT / "docs/neko-thoughts-native.png"))
        pixels = image.toImage()
        left = labels[0].x() - host.x()
        top = labels[0].y() - host.y()
        stripe = [pixels.pixelColor(x, top + 6).lightness()
                  for x in range(left + 20, left + labels[0].width() - 20)]
        corner_changes = []
        for label in labels:
            ox, oy = label.x() - host.x(), label.y() - host.y()
            for x, y in ((2, 2), (5, 2), (2, 5), (label.width() - 3, 2),
                         (2, label.height() - 3), (label.width() - 3, label.height() - 3)):
                assert not label.mask().contains(QPoint(x, y))
                before, after = baseline.pixelColor(ox + x, oy + y), pixels.pixelColor(ox + x, oy + y)
                corner_changes.append(max(abs(before.red() - after.red()),
                                          abs(before.green() - after.green()),
                                          abs(before.blue() - after.blue())))
        result.update(sampled_backdrop=all(not label.backdrop.isNull() for label in labels),
                      click_through_to_test_window=all(win32gui.WindowFromPoint(
                          (label.x() + label.width() // 2, label.y() + label.height() // 2))
                          == int(host.winId()) for label in labels),
                      foreground_unchanged=win32gui.GetForegroundWindow() == foreground,
                      sizes=[[label.width(), label.height()] for label in labels],
                      window_opacities=[label.windowOpacity() for label in labels],
                      rounded_corners=all(not label.mask().contains(QPoint(3, 3)) for label in labels),
                      outside_corner_pixel_changes=corner_changes,
                      frosted_stripe_contrast=max(stripe) - min(stripe),
                      background_stripe_contrast=246 - 176,
                      dpr=app.primaryScreen().devicePixelRatio())
        result["passed"] = (result["sampled_backdrop"] and result["click_through_to_test_window"]
                            and result["foreground_unchanged"] and result["rounded_corners"]
                            and max(corner_changes) <= 2
                            and result["frosted_stripe_contrast"] < 0.95 * result["background_stripe_contrast"])
        cases.append({"sizes": result["sizes"], "outside_corner_pixel_changes": corner_changes,
                      "passed": result["passed"]})
        result["lifecycle_cases"] = cases
        result["passed"] = all(case["passed"] for case in cases)
        if len(cases) < 3:
            for label in labels:
                label.hide()
            texts = (("Now a longer little thought, softly rounded even when it wraps across several lines.", "Gotcha!")
                     if len(cases) == 1 else ("Look at meeee!", "A little thought, with just enough frost to keep it readable."))
            for index, (label, text) in enumerate(zip(labels, texts)):
                label.setText(text)
                label.adjustSize()
                label.move(host.x() + (100 if index == 0 else 470), host.y() + 75)
                label.prepare_backdrop()
                label.show()
            again = True
            QTimer.singleShot(350, capture)
            return
        (ROOT / "docs/thoughts-native.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result))
    finally:
        if not again:
            app.quit()


QTimer.singleShot(900, capture)
app.exec()
sys.exit(0 if result.get("passed") else 1)
