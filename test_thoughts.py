import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import unittest
from unittest.mock import patch, Mock
from PySide6.QtWidgets import QApplication
from thoughts import ThoughtLabel, enable_backdrop

APP = QApplication.instance() or QApplication([])


class ThoughtTests(unittest.TestCase):
    def test_unavailable_backdrop_falls_back_without_crashing(self):
        self.assertFalse(enable_backdrop(0))
        with patch("thoughts.QApplication.platformName", return_value="windows"):
            with patch("thoughts.ctypes.WinDLL", side_effect=OSError):
                self.assertFalse(enable_backdrop(0))
            failed = Mock()
            failed.SetWindowCompositionAttribute.return_value = 0
            with patch("thoughts.ctypes.WinDLL", return_value=failed):
                self.assertFalse(enable_backdrop(1))

    def test_short_thoughts_fit_the_text_and_long_thoughts_wrap(self):
        label = ThoughtLabel()
        try:
            label.setText("Gotcha!")
            label.adjustSize()
            short = label.width()
            label.setText("A longer little thought that should wrap gently onto another line.")
            label.adjustSize()
            self.assertLess(short, label.width())
            self.assertEqual(label.width(), 270)
            self.assertGreater(label.height(), label.fontMetrics().height() + 16)
        finally:
            label.deleteLater()
