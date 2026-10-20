import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QPoint, QPointF, QSettings, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from behavior import NekoState
from main import NekoWidget, set_autostart


APP = QApplication.instance() or QApplication([])
APP.setQuitOnLastWindowClosed(False)


class DesktopTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.settings = QSettings(str(Path(self.folder.name) / "prefs.ini"), QSettings.IniFormat)
        self.activity = patch("main.desktop_activity", return_value=(0, 100, False))
        self.activity.start()
        self.neko = NekoWidget(self.settings)
        self.neko.tick_timer.stop()
        self.neko.show_neko()
        APP.processEvents()

    def tearDown(self):
        self.neko.tick_timer.stop()
        self.neko.animation_timer.stop()
        self.neko.save_timer.stop()
        self.neko.dismiss_bubble()
        self.neko.bubble.deleteLater()
        self.neko.tray_icon.hide()
        if self.neko.stats_window:
            self.neko.stats_window.close()
            self.neko.stats_window.deleteLater()
        self.neko.hide()
        self.neko.deleteLater()
        APP.processEvents()
        self.activity.stop()
        self.folder.cleanup()

    def test_hidden_pet_never_reappears_to_talk(self):
        self.neko.hide_neko()
        self.assertFalse(self.neko.say("hello"))
        self.neko.random_dialogue()
        self.neko.tick()
        self.assertFalse(self.neko.isVisible())
        self.assertFalse(self.neko.bubble.isVisible())
        self.assertFalse(self.neko.animation_timer.isActive())

    def test_speech_does_not_change_sleep_or_geometry(self):
        original = self.neko.geometry()
        self.assertTrue(self.neko.say("comfy."))
        self.assertEqual(self.neko.geometry(), original)
        self.neko.companion.state = NekoState.SLEEPING
        self.assertFalse(self.neko.say("wake up"))
        self.assertEqual(self.neko.companion.state, NekoState.SLEEPING)

    def test_quiet_mode_still_accepts_a_deliberate_pet(self):
        self.neko.set_quiet(True)
        self.assertFalse(self.neko.say("unprompted"))
        self.neko.pet_reaction()
        self.assertEqual(self.neko.companion.pets, 1)
        self.assertTrue(self.neko.bubble.isVisible())

    def test_fullscreen_hides_and_restores_without_chatter(self):
        self.neko.companion.next_comment = 0
        with patch("main.desktop_activity", return_value=(0, 200, True)):
            self.neko.tick()
        self.assertFalse(self.neko.isVisible())
        self.assertFalse(self.neko.say("hello"))
        self.neko.tick()
        self.assertTrue(self.neko.isVisible())
        self.assertFalse(self.neko.bubble.isVisible())
        self.assertGreater(self.neko.companion.next_comment, time.monotonic() + 700)

    def test_leaving_quiet_mode_does_not_release_overdue_chatter(self):
        self.neko.set_quiet(True)
        self.neko.companion.next_comment = 0
        self.neko.set_quiet(False)
        self.assertGreater(self.neko.companion.next_comment, time.monotonic() + 700)

    def test_counts_and_preferences_are_saved_without_double_counting(self):
        self.neko.pet_reaction()
        self.neko.set_motion(False)
        self.neko.set_quiet(True)
        self.neko.save_preferences()
        self.neko.save_preferences()
        self.assertEqual(self.settings.value("pets", type=int), 1)
        self.assertTrue(self.settings.value("quiet", type=bool))
        self.assertFalse(self.settings.value("motion", type=bool))

    def test_saved_position_is_restored(self):
        point = QPoint(120, 150)
        self.settings.setValue("position", point)
        other = NekoWidget(self.settings)
        try:
            self.assertEqual(other.pos(), point)
        finally:
            other.tray_icon.hide()
            other.bubble.deleteLater()
            other.deleteLater()

    def test_stale_ai_cannot_speak_after_hiding_and_showing(self):
        self.neko.ai_enabled = True
        self.neko.request_generation = self.neko.ai_generation
        self.neko.request_started = time.monotonic()
        self.neko.hide_neko()
        self.neko.show_neko()
        self.neko.on_brain_finished("stale comment", True)
        self.assertFalse(self.neko.bubble.isVisible())

    def test_only_one_ai_worker_can_run_at_a_time(self):
        self.neko.ai_enabled = True
        self.neko.brain_worker = MagicMock()
        with patch("llm_brain.AIBrainWorker") as worker:
            self.neko.trigger_ai_brain()
        worker.assert_not_called()
        self.neko.brain_worker = None

    def test_click_pets_but_dragging_does_not(self):
        QTest.mouseClick(self.neko, Qt.LeftButton, pos=QPoint(56, 60))
        self.assertEqual(self.neko.companion.pets, 1)
        QTest.mousePress(self.neko, Qt.LeftButton, pos=QPoint(56, 60))
        move = QMouseEvent(QMouseEvent.MouseMove, QPointF(80, 60),
                           QPointF(self.neko.mapToGlobal(QPoint(80, 60))),
                           Qt.NoButton, Qt.LeftButton, Qt.NoModifier)
        APP.sendEvent(self.neko, move)
        QTest.mouseRelease(self.neko, Qt.LeftButton, pos=QPoint(80, 60))
        self.assertEqual(self.neko.companion.pets, 1)

    def test_nook_opens_and_all_poses_render(self):
        with patch("main.autostart_enabled", return_value=False):
            self.neko.open_stats_window()
        APP.processEvents()
        self.assertTrue(self.neko.stats_window.isVisible())
        self.assertIn("little pets", self.neko.stats_window.keepsakes.text())
        for state in NekoState:
            self.neko.companion.state = state
            self.neko.refresh_asset()
            self.assertFalse(self.neko.grab().isNull())

    def test_bubbles_do_not_capture_desktop_input(self):
        self.assertTrue(self.neko.bubble.windowFlags() & Qt.WindowTransparentForInput)
        self.assertTrue(self.neko.bubble.windowFlags() & Qt.WindowDoesNotAcceptFocus)

    def test_startup_is_opt_in_and_migrates_the_old_shortcut(self):
        shortcut = Path(self.folder.name) / "DesktopNeko.lnk"
        shortcut.touch()
        with patch("main.legacy_shortcut", return_value=shortcut), \
                patch("main.winreg.CreateKey"), patch("main.winreg.SetValueEx") as write:
            set_autostart(True)
        command = write.call_args.args[-1]
        self.assertIn("pythonw.exe", command)
        self.assertIn('"', command)
        self.assertIn("main.py", command)
        self.assertFalse(shortcut.exists())

    def test_startup_failure_preserves_the_old_shortcut(self):
        shortcut = Path(self.folder.name) / "DesktopNeko.lnk"
        shortcut.touch()
        with patch("main.legacy_shortcut", return_value=shortcut), \
                patch("main.winreg.CreateKey", side_effect=PermissionError):
            with self.assertRaises(PermissionError):
                set_autostart(True)
        self.assertTrue(shortcut.exists())


if __name__ == "__main__":
    unittest.main()
