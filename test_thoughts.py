import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import unittest
from unittest.mock import Mock, patch
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from thoughts import ThoughtLabel, soften

APP = QApplication.instance() or QApplication([])


class ThoughtTests(unittest.TestCase):
    def test_missing_sample_keeps_the_translucent_fallback(self):
        label = ThoughtLabel()
        screen = Mock()
        screen.grabWindow.return_value = QPixmap()
        with patch("thoughts.QApplication.platformName", return_value="windows"), patch.object(label, "screen", return_value=screen):
            label.prepare_backdrop()
        self.assertTrue(label.backdrop.isNull())
        label.deleteLater()

    def test_backdrop_softens_detail_and_preserves_colour_and_dpr(self):
        source = QPixmap(64, 64)
        source.fill(QColor("#f06040"))
        source.setDevicePixelRatio(2)
        result = soften(source)
        self.assertEqual(result.devicePixelRatio(), 2)
        colour = result.toImage().pixelColor(32, 32)
        for actual, expected in zip(colour.getRgb(), QColor("#f06040").getRgb()):
            self.assertAlmostEqual(actual, expected, delta=2)
        painter = QPainter(source)
        for x in range(32):
            painter.fillRect(x, 0, 1, 32, Qt.white if x % 2 else Qt.black)
        painter.end()
        result = soften(source).toImage()
        self.assertLess(abs(result.pixelColor(32, 32).lightness() - result.pixelColor(34, 32).lightness()), 100)

    def test_hiding_discards_the_temporary_backdrop(self):
        label = ThoughtLabel()
        label.show()
        label.backdrop = QPixmap(64, 64)
        label.backdrop.fill(Qt.white)
        label.hide()
        self.assertTrue(label.backdrop.isNull())
        label.deleteLater()

    def test_short_thoughts_fit_the_text_and_long_thoughts_wrap(self):
        label = ThoughtLabel()
        try:
            label.setText("Gotcha!")
            label.adjustSize()
            short = label.width()
            short_height = label.height()
            label.setText("A longer little thought that should wrap gently onto another line.")
            label.adjustSize()
            self.assertLess(short, label.width())
            self.assertEqual(label.width(), 270)
            self.assertGreater(label.height(), label.fontMetrics().height() + 16)
            label.setText("Gotcha!")
            label.adjustSize()
            self.assertEqual(label.height(), short_height)
        finally:
            label.deleteLater()
