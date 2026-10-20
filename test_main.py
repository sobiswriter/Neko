import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QEvent, QPoint, QPointF, QSettings, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from behavior import NekoState
from dialogue import LINES
from main import NekoWidget, set_autostart


APP = QApplication.instance() or QApplication([])
APP.setQuitOnLastWindowClosed(False)


class DesktopTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.settings = QSettings(str(Path(self.folder.name) / "prefs.ini"), QSettings.IniFormat)
        self.activity = patch("main.desktop_activity", return_value=(0, 100, False))
        self.activity.start()
        self.native_monitor = patch("main.ActivityMonitor.start", return_value=None)
        self.native_monitor.start()
        self.app_lookup = patch("main.foreground_executable", return_value="")
        self.app_lookup.start()
        self.sound_backend = patch("main.winsound.PlaySound")
        self.sound_backend.start()
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
        APP.sendPostedEvents(None, QEvent.DeferredDelete)
        APP.processEvents()
        self.activity.stop()
        self.native_monitor.stop()
        self.app_lookup.stop()
        self.sound_backend.stop()
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
        self.neko.hide_fullscreen = True
        self.neko.companion.next_comment = 0
        with patch("main.desktop_activity", return_value=(0, 200, True)):
            self.neko.tick()
        self.assertFalse(self.neko.isVisible())
        self.assertFalse(self.neko.say("hello"))
        self.neko.tick()
        self.assertTrue(self.neko.isVisible())
        self.assertFalse(self.neko.bubble.isVisible())
        self.assertGreater(self.neko.companion.next_comment, time.monotonic() + 70)

    def test_fullscreen_visibility_is_a_choice_and_stays_silent(self):
        self.assertFalse(self.neko.hide_fullscreen)
        with patch("main.desktop_activity", return_value=(0, 200, True)):
            self.neko.tick()
        self.assertTrue(self.neko.isVisible())
        self.assertFalse(self.neko.say("unprompted"))
        self.assertFalse(self.neko.activity.enabled)

    def test_typing_signal_selects_a_real_paw_animation(self):
        self.neko.activity.keyboard.extend([time.monotonic()] * 8)
        self.neko.tick()
        self.assertEqual(self.neko.companion.state, NekoState.TYPING)
        self.assertEqual(self.neko.current_clip, "typing")
        self.assertIn(self.neko.bubble.text(), LINES["typing"])

    def test_app_switch_speaks_offline(self):
        self.neko.last_window = 99
        self.neko.tick()
        self.assertIn(self.neko.bubble.text(), LINES["switch"])

    def test_vlc_gets_a_watch_buddy_pose_and_local_question(self):
        self.neko.last_window = 99
        with patch("main.foreground_executable", return_value="vlc.exe"), \
                patch("main.win32gui.GetWindowText", return_value="a film.mkv - VLC media player"):
            self.neko.tick()
        self.assertEqual(self.neko.current_clip, "loaf")
        self.assertIn(self.neko.bubble.text(), LINES["video"])

    def test_napping_pets_keep_the_animation_and_automatic_wake_deadline(self):
        now = time.monotonic()
        with patch("main.desktop_activity", return_value=(180, 100, False)), \
                patch("main.time.monotonic", return_value=now):
            self.neko.tick()
        self.assertEqual(self.neko.current_clip, "sleep")
        started = self.neko.pose_started
        self.neko.pet_reaction()
        self.assertEqual(self.neko.current_clip, "sleep")
        self.assertEqual(self.neko.pose_started, started)
        with patch("main.time.monotonic", return_value=now + 89):
            self.neko.tick()
        self.assertEqual(self.neko.current_clip, "sleep")
        with patch("main.time.monotonic", return_value=now + 90):
            self.neko.tick()
        self.assertEqual(self.neko.companion.state, NekoState.WAKING)
        self.assertEqual(self.neko.current_clip, "stretch")

    def test_sounds_are_opt_in_nonblocking_and_rate_limited(self):
        import winsound
        with patch("main.winsound.PlaySound") as play:
            self.assertFalse(self.neko.play_sound("mew", prompted=True))
            play.assert_not_called()
            self.neko.set_sounds(True)
            self.assertTrue(self.settings.value("sounds_enabled", type=bool))
            self.assertTrue(self.neko.play_sound("mew", prompted=True))
            flags = play.call_args.args[1]
            self.assertTrue(flags & winsound.SND_ASYNC)
            self.assertTrue(flags & winsound.SND_NODEFAULT)
            self.assertFalse(self.neko.play_sound("mew", prompted=True))
            self.neko.set_sounds(False)
            play.assert_called_with(None, 0)

    def test_quiet_hidden_fullscreen_and_media_guard_sound(self):
        self.neko.sounds_enabled = True
        self.neko.set_quiet(True)
        self.assertFalse(self.neko.play_sound("chirp"))
        self.assertTrue(self.neko.play_sound("purr", prompted=True))
        self.neko.last_sound = -999999
        self.neko.set_quiet(False)
        self.neko.app_context = "music"
        self.assertFalse(self.neko.play_sound("chirp"))
        self.neko.fullscreen = True
        self.assertFalse(self.neko.play_sound("mew", prompted=True))
        self.neko.fullscreen = False
        self.neko.hide_neko()
        self.assertFalse(self.neko.play_sound("mew", prompted=True))

    def test_audio_device_failure_does_not_break_the_pet(self):
        self.neko.sounds_enabled = True
        with patch("main.winsound.PlaySound", side_effect=RuntimeError("no device")):
            self.assertFalse(self.neko.play_sound("mew", prompted=True))
            self.neko.set_sounds(False)

    def test_nook_sound_toggle_and_preview_work_without_enabling_ai(self):
        with patch("main.autostart_enabled", return_value=False):
            self.neko.open_stats_window()
        nook = self.neko.stats_window
        self.assertFalse(nook.sound_test.isEnabled())
        nook.sounds.setChecked(True)
        self.assertTrue(nook.sound_test.isEnabled())
        with patch("main.winsound.PlaySound") as play:
            nook.sound_test.click()
        self.assertTrue(play.call_args.args[0].endswith("mew.wav"))
        self.assertFalse(self.neko.ai_enabled)

    def test_title_fingerprint_catches_a_tab_change_in_the_same_app(self):
        self.neko.last_window = 100
        with patch("main.win32gui.GetWindowText", return_value="first document"):
            self.neko.tick()
        with patch("main.win32gui.GetWindowText", return_value="another document"):
            self.neko.tick()
        self.assertIn(self.neko.bubble.text(), LINES["tab"])
        self.assertEqual(self.neko.last_title_stamp, (100, hash("another document")))

    def test_reactive_words_share_a_pause_and_never_replace_a_visible_bubble(self):
        self.assertTrue(self.neko.offline_line("typing"))
        words = self.neko.bubble.text()
        self.assertFalse(self.neko.offline_line("switch"))
        self.assertEqual(self.neko.bubble.text(), words)
        self.neko.dismiss_bubble()
        self.assertFalse(self.neko.offline_line("cursor"))

    def test_nook_timing_controls_apply_and_persist(self):
        with patch("main.autostart_enabled", return_value=False):
            self.neko.open_stats_window()
        for key, value in (("sleep_seconds", 45), ("chatter_seconds", 30), ("idle_seconds", 8)):
            spin = self.neko.stats_window.timing[key]
            self.assertGreater(spin.lineEdit().width(), 35)
            spin.setValue(value)
            self.assertEqual(getattr(self.neko.companion, key), value)
            self.assertEqual(self.settings.value(key, type=int), value)
        self.neko.stats_window.follow.setChecked(False)
        self.assertFalse(self.settings.value("follow_mouse", type=bool))
        with patch("main.desktop_activity", return_value=(45, 100, False)):
            self.neko.tick()
        self.assertEqual(self.neko.companion.state, NekoState.SLEEPING)

    def test_timers_accept_typed_values_and_commit_on_enter(self):
        with patch("main.autostart_enabled", return_value=False):
            self.neko.open_stats_window()
        for key, value in (("sleep_seconds", 10), ("chatter_seconds", 45), ("idle_seconds", 9)):
            spin = self.neko.stats_window.timing[key]
            previous = getattr(self.neko.companion, key)
            QTest.mouseClick(spin, Qt.LeftButton, pos=QPoint(25, spin.height() // 2))
            QTest.keyClick(spin, Qt.Key_A, Qt.ControlModifier)
            QTest.keyClicks(spin, str(value))
            self.assertEqual(getattr(self.neko.companion, key), previous)
            QTest.keyClick(spin, Qt.Key_Return)
            self.assertEqual(getattr(self.neko.companion, key), value)
            self.assertEqual(self.settings.value(key, type=int), value)

    def test_changed_sleep_delay_replaces_the_old_awake_deadline(self):
        now = time.monotonic()
        self.neko.companion.next_nap = now + 180
        with patch("main.time.monotonic", return_value=now):
            self.neko.set_timing("sleep_seconds", 10)
        self.assertEqual(self.neko.companion.next_nap, now + 10)

    def test_sleep_edit_saves_when_leaving_the_field_and_survives_reload(self):
        from PySide6.QtWidgets import QPushButton
        with patch("main.autostart_enabled", return_value=False):
            self.neko.open_stats_window()
        nook = self.neko.stats_window
        spin = nook.timing["sleep_seconds"]
        QTest.mouseClick(spin, Qt.LeftButton, pos=QPoint(25, spin.height() // 2))
        QTest.keyClick(spin, Qt.Key_A, Qt.ControlModifier)
        QTest.keyClicks(spin, "7")
        done = next(button for button in nook.findChildren(QPushButton) if button.text() == "Comfy.")
        QTest.mouseClick(done, Qt.LeftButton)
        self.assertEqual(self.settings.value("sleep_seconds", type=int), 7)
        other = NekoWidget(self.settings)
        try:
            self.assertEqual(other.companion.sleep_seconds, 7)
        finally:
            other.tray_icon.hide()
            other.bubble.deleteLater()
            other.deleteLater()

    def test_bad_saved_timing_is_recovered_and_clamped(self):
        self.settings.setValue("sleep_seconds", "broken")
        self.settings.setValue("chatter_seconds", -100)
        self.settings.setValue("idle_seconds", 99999)
        other = NekoWidget(self.settings)
        try:
            self.assertEqual(other.companion.sleep_seconds, 180)
            self.assertEqual(other.companion.chatter_seconds, 15)
            self.assertEqual(other.companion.idle_seconds, 120)
        finally:
            other.tray_icon.hide()
            other.bubble.deleteLater()
            other.deleteLater()

    def test_mouse_following_is_bounded_and_optional(self):
        self.neko.last_follow = -99999
        origin = self.neko.pos()
        cursor = self.neko.geometry().center() - QPoint(220, 0)
        self.neko.last_cursor = cursor - QPoint(30, 0)
        with patch("main.QCursor.pos", return_value=cursor):
            self.neko.tick()
            self.assertEqual(self.neko.current_clip, "walk")
            for _ in range(100):
                self.neko.animate()
        self.assertGreater((self.neko.pos() - origin).manhattanLength(), 0)
        self.assertLessEqual((self.neko.pos() - origin).manhattanLength(), 165)
        self.neko.set_follow_mouse(False)
        self.assertNotEqual(self.neko.companion.state, NekoState.FOLLOWING)

    def test_typing_stops_a_mouse_expedition(self):
        self.neko.follow_origin = self.neko.pos()
        self.neko.companion.pose(NekoState.FOLLOWING, time.monotonic(), 3.2)
        self.neko.activity.keyboard.extend([time.monotonic()] * 8)
        self.neko.tick()
        self.assertEqual(self.neko.companion.state, NekoState.TYPING)

    def test_following_stops_at_the_deadline_even_before_next_behavior_tick(self):
        self.neko.follow_origin = self.neko.pos()
        self.neko.companion.pose(NekoState.FOLLOWING, time.monotonic() - 4, 3.2)
        original = self.neko.pos()
        with patch("main.QCursor.pos", return_value=self.neko.geometry().center() - QPoint(220, 0)):
            self.neko.animate()
        self.assertEqual(self.neko.pos(), original)
        self.assertEqual(self.neko.companion.state, NekoState.IDLE)

    def test_pinning_uses_no_activation_and_no_move_flags(self):
        with patch("main.QApplication.platformName", return_value="windows"), \
                patch("main.win32gui.SetWindowPos") as pin:
            self.neko.pin_to_top(force=True)
        self.assertEqual(pin.call_args.args[1], -1)
        self.assertEqual(pin.call_args.args[-1] & 0x13, 0x13)

    def test_leaving_quiet_mode_does_not_release_overdue_chatter(self):
        self.neko.set_quiet(True)
        self.neko.companion.next_comment = 0
        self.neko.set_quiet(False)
        self.assertGreater(self.neko.companion.next_comment, time.monotonic() + 70)

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
