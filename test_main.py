import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QEvent, QPoint, QPointF, QRect, QSize, QSettings, Qt
from PySide6.QtGui import QCursor, QMouseEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from behavior import NekoState, IDLE_STATES
from dialogue import LINES
from animations import CANVAS_PADDING, CANVAS_TOP
from main import NekoWidget, set_autostart, adjacent_position


APP = QApplication.instance() or QApplication([])
APP.setQuitOnLastWindowClosed(False)


class DesktopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from animations import SpriteAtlas
        cls.atlas = SpriteAtlas(Path(__file__).parent / "assets")

    def test_supplied_icon_is_used_for_pet_tray_and_nook(self):
        from PySide6.QtGui import QIcon
        from main import ICON_PATH
        expected = QIcon(str(ICON_PATH)).pixmap(32, 32).toImage()
        self.assertFalse(expected.isNull())
        self.assertEqual(self.neko.windowIcon().pixmap(32, 32).toImage(), expected)
        self.assertEqual(self.neko.tray_icon.icon().pixmap(32, 32).toImage(), expected)
        with patch("main.autostart_enabled", return_value=False):
            self.neko.open_stats_window()
        self.assertEqual(self.neko.stats_window.windowIcon().pixmap(32, 32).toImage(), expected)

    def test_stationary_hold_is_not_a_pet_and_keeps_the_drag_offset(self):
        start = time.monotonic()
        point = QPoint(96, 70)
        with patch("main.time.monotonic", return_value=start):
            QTest.mousePress(self.neko, Qt.LeftButton, pos=point)
        origin = self.neko.pos()
        with patch("main.time.monotonic", return_value=start + 0.249):
            self.neko.check_hold()
        self.assertNotEqual(self.neko.companion.state, NekoState.HELD)
        with patch("main.time.monotonic", return_value=start + 0.251):
            self.neko.check_hold()
        self.assertEqual(self.neko.companion.state, NekoState.HELD)
        self.assertEqual(self.neko.pos(), origin)
        self.assertEqual(self.neko.animation_timer.interval(), 50)
        with patch("main.time.monotonic", return_value=start + 1):
            QTest.mouseRelease(self.neko, Qt.LeftButton, pos=point)
        self.assertEqual(self.neko.companion.state, NekoState.SETTING_DOWN)
        self.assertEqual(self.neko.companion.pets, 0)
        with patch("main.time.monotonic", return_value=self.neko.companion.pose_until + 0.01):
            self.neko.animate()
        self.assertEqual(self.neko.companion.state, NekoState.IDLE)
        self.assertEqual(self.neko.pos(), origin)

    def test_release_starts_with_the_actual_visible_pose_in_every_mood(self):
        samples = [i * 0.05 + 0.025 for i in range(8)]
        samples += [phase if phase >= 0.4 else phase + 2.4 for phase in (i * 0.2 + 0.1 for i in range(12))]
        samples += [base + i * 0.2 + 0.1 for base in (4.8, 12) for i in range(12)]
        samples += [24 + i * 0.3 + 0.15 for i in range(8)]
        samples += [base + i * 0.1 + 0.05 for base in (3, 10) for i in range(4)]
        samples += [20 + phase for phase in (0.075, 0.225, 0.4, 0.575)]
        samples += [boundary + delta for boundary in (0.4, 3, 3.4, 10, 10.4, 20, 20.65)
                    for delta in (-0.001, 0, 0.001)] + [1000]
        for elapsed in samples:
            self.neko.cancel_pickup()
            self.neko.companion.state = NekoState.IDLE
            start = time.monotonic()
            with patch("main.time.monotonic", return_value=start):
                self.neko.begin_pickup()
            now = start + elapsed
            before = self.neko.current_frame(now).toImage()
            with patch("main.time.monotonic", return_value=now):
                self.neko.release_pickup()
            self.assertEqual(self.neko.current_frame(now).toImage(), before, elapsed)
            self.assertEqual(self.neko.companion.state, NekoState.SETTING_DOWN)
            with patch("main.time.monotonic", return_value=self.neko.companion.pose_until + 0.01):
                self.neko.animate()
            self.assertEqual(self.neko.current_clip, "idle")
            self.assertEqual(self.neko.companion.pets, 0)

    def test_regrab_and_hide_do_not_leave_a_stale_carry_or_change_saved_origin(self):
        origin = self.neko.pos()
        start = time.monotonic()
        with patch("main.time.monotonic", return_value=start):
            self.neko.begin_pickup()
        with patch("main.time.monotonic", return_value=start + 4):
            self.neko.release_pickup()
        now = start + 4.2
        before = self.neko.current_frame(now).toImage()
        with patch("main.time.monotonic", return_value=now):
            self.neko.begin_pickup()
        self.assertEqual(self.neko.current_frame(now).toImage(), before)
        self.neko.save_preferences()
        self.assertEqual(self.settings.value("position", type=QPoint), origin + QPoint(CANVAS_PADDING, CANVAS_TOP))
        self.neko.hide_neko()
        self.assertIsNone(self.neko.companion.carry_rest)
        self.assertIsNone(self.neko.drag_origin)
        self.assertFalse(self.neko.hold_timer.isActive())
        self.assertEqual(self.neko.cursor().shape(), Qt.OpenHandCursor)

    def test_sleeping_carry_lands_curled_and_defers_timed_wake(self):
        start = time.monotonic()
        self.neko.companion.state = NekoState.SLEEPING
        self.neko.companion.nap_started = start - 10
        self.neko.pose_started = start - 10
        self.neko.refresh_asset()
        with patch("main.time.monotonic", return_value=start):
            self.neko.begin_pickup()
        self.assertEqual(len(self.neko.carry_path), 8)
        with patch("main.time.monotonic", return_value=start + 3):
            self.neko.release_pickup()
        idle = self.neko.atlas.frame("idle", 0).toImage()
        self.assertTrue(all(frame.toImage() != idle for frame in self.neko.carry_path))
        with patch("main.time.monotonic", return_value=self.neko.companion.pose_until + 0.001):
            self.neko.animate()
        self.assertEqual(self.neko.companion.state, NekoState.SLEEPING)
        self.assertEqual(self.neko.companion.nap_started, start - 10)
        self.neko.companion.sleep_duration = 1
        with patch("main.time.monotonic", return_value=start + 4):
            self.neko.begin_pickup()
        with patch("main.time.monotonic", return_value=start + 5):
            self.neko.release_pickup()
        with patch("main.time.monotonic", return_value=self.neko.companion.pose_until + 0.001):
            self.neko.animate()
        self.assertEqual(self.neko.companion.state, NekoState.WAKING)
        self.assertEqual((self.neko.companion.pets, self.neko.companion.naps), (0, 0))

    def test_reduced_motion_carry_is_stable_and_places_immediately(self):
        self.neko.set_motion(False)
        self.neko.begin_pickup()
        now = time.monotonic()
        self.assertEqual(self.neko.current_frame(now).toImage(), self.neko.current_frame(now + 100).toImage())
        self.assertFalse(self.neko.animation_timer.isActive())
        self.neko.release_pickup()
        self.assertEqual(self.neko.companion.state, NekoState.IDLE)
        self.assertEqual(self.neko.companion.pets, 0)
        self.neko.set_motion(True)
        self.neko.begin_pickup()
        self.neko.set_motion(False)
        self.assertEqual(self.neko.companion.state, NekoState.HELD)
        self.neko.release_pickup()
        self.assertEqual(self.neko.companion.state, NekoState.IDLE)
        self.neko.set_motion(True)
        self.neko.begin_pickup()
        self.neko.release_pickup()
        self.neko.set_motion(False)
        self.assertEqual(self.neko.companion.state, NekoState.IDLE)

    def test_every_pet_posture_starts_pickup_from_its_visible_frame(self):
        from animations import CLIPS, PET_ROWS, sprite_bounds
        from behavior import PET_STATES
        for clip, state in zip(PET_ROWS, PET_STATES):
            for fraction in (0.25, 0.5, 0.8):
                self.neko.cancel_pickup()
                now = time.monotonic()
                self.neko.companion.state = state
                self.neko.pose_started = now - sum(CLIPS[clip].durations) / 1000 * fraction
                self.neko.refresh_asset()
                source = self.neko.current_frame(now).toImage()
                with patch("main.time.monotonic", return_value=now):
                    self.neko.begin_pickup()
                self.assertEqual(self.neko.current_frame(now).toImage(), source, (clip, fraction))
                self.assertTrue(all(not frame.isNull() for frame in self.neko.carry_path), (clip, fraction))
                for frame in self.neko.carry_path:
                    bounds = sprite_bounds(frame.toImage())
                    self.assertGreater(bounds.top(), 0, (clip, fraction))
                    self.assertLess(bounds.bottom(), self.neko.height() - 1, (clip, fraction))

    def test_lost_capture_fullscreen_and_screen_change_clear_pickup(self):
        for cancel in (lambda: APP.sendEvent(self.neko, QEvent(QEvent.UngrabMouse)),
                       self.neko.screen_changed,
                       lambda: self.neko.set_hide_fullscreen(True)):
            self.neko.show_neko()
            self.neko.fullscreen = False
            self.neko.begin_pickup()
            self.neko.drag_origin = QPoint(100, 100)
            self.neko.fullscreen = True
            cancel()
            self.assertNotIn(self.neko.companion.state, (NekoState.HELD, NekoState.SETTING_DOWN))
            self.assertIsNone(self.neko.drag_origin)

    def test_regrabbing_an_early_release_completes_the_remaining_lift(self):
        from animations import sprite_bounds
        start = time.monotonic()
        with patch("main.time.monotonic", return_value=start):
            self.neko.begin_pickup()
        with patch("main.time.monotonic", return_value=start + 0.12):
            self.neko.release_pickup()
        with patch("main.time.monotonic", return_value=start + 0.18):
            self.neko.begin_pickup()
        end = self.neko.carry_path_started + sum(self.neko.carry_path_clip.durations) / 1000
        last = sprite_bounds(self.neko.carry_path[-1].toImage()).top()
        after = sprite_bounds(self.neko.current_frame(end + 0.001).toImage()).top()
        self.assertLessEqual(abs(last - after), 2)

    def test_regrab_resumes_the_expression_instead_of_skipping_a_mood_bridge(self):
        from animations import held_clip
        start = time.monotonic()
        with patch("main.time.monotonic", return_value=start):
            self.neko.begin_pickup()
        with patch("main.time.monotonic", return_value=start + 2.95):
            self.neko.release_pickup()
        with patch("main.time.monotonic", return_value=start + 3.2):
            self.neko.begin_pickup()
        end = self.neko.carry_path_started + sum(self.neko.carry_path_clip.durations) / 1000
        self.assertAlmostEqual(self.neko.carry_elapsed(end), 2.95, places=5)
        self.assertEqual(held_clip(self.neko.carry_elapsed(end))[0], "held_excited")
        self.assertEqual(held_clip(self.neko.carry_elapsed(end + 0.1))[0], "carry_to_calm")

    def test_a_carry_state_without_live_input_has_a_safe_render_and_cancel(self):
        for state in (NekoState.HELD, NekoState.SETTING_DOWN):
            self.neko.companion.state = state
            self.neko.refresh_asset()
            self.assertFalse(self.neko.current_frame(time.monotonic()).isNull())
            self.neko.cancel_pickup()
            self.assertEqual(self.neko.companion.state, NekoState.IDLE)


    def test_sleepy_flop_finishes_its_story_before_a_queued_pet_or_nap(self):
        self.neko.companion.pet_bag = [NekoState.CHEEK_RUB, NekoState.SIDE_FLOP]
        self.neko.pet_reaction()
        started = self.neko.pose_started
        with patch("main.time.monotonic", return_value=started + 0.2):
            self.neko.pet_reaction()
        before_end = self.neko.companion.pose_until - 0.2
        with patch("main.time.monotonic", return_value=before_end):
            self.neko.animate()
        self.assertIsNone(self.neko.companion.tick(before_end, idle_seconds=1000))
        self.assertEqual(self.neko.current_clip, "side_flop")
        self.assertTrue(self.neko.companion.pet_pending)
        with patch("main.time.monotonic", return_value=self.neko.companion.pose_until + 0.01):
            self.neko.animate()
        self.assertEqual(self.neko.current_clip, "nuzzle")
        self.assertEqual(self.neko.companion.pets, 2)

    def test_pet_motion_uses_tail_cadence_and_returns_to_idle_when_the_clip_finishes(self):
        self.neko.companion.pet_bag = [NekoState.HAPPY_HOP]
        self.neko.pet_reaction()
        self.assertEqual(self.neko.animation_timer.interval(), 50)
        self.assertEqual(self.neko.animation_timer.timerType(), Qt.PreciseTimer)
        end = self.neko.companion.pose_until
        with patch("main.time.monotonic", return_value=end + 0.01):
            self.neko.animate()
        self.assertEqual(self.neko.companion.state, NekoState.IDLE)
        self.assertEqual(self.neko.current_clip, "idle")
        self.assertEqual(self.neko.animation_timer.interval(), 100)
        self.assertEqual(self.neko.animation_timer.timerType(), Qt.CoarseTimer)

    def test_repeated_petting_preserves_the_current_pose_clock_until_recovery(self):
        self.neko.companion.pet_bag = [NekoState.CHEEK_RUB, NekoState.HAPPY_HOP]
        self.neko.pet_reaction()
        started, end = self.neko.pose_started, self.neko.companion.pose_until
        with patch("main.time.monotonic", return_value=started + 0.2):
            self.neko.pet_reaction()
        self.assertEqual(self.neko.current_clip, "happy_hop")
        self.assertEqual(self.neko.pose_started, started)
        self.assertEqual(self.neko.companion.pets, 2)
        with patch("main.time.monotonic", return_value=end + 0.01):
            self.neko.animate()
        self.assertEqual(self.neko.current_clip, "nuzzle")
        self.assertEqual(self.neko.companion.pets, 2)

    def test_hiding_or_reduced_motion_cancels_a_pending_pet(self):
        for cancel in (self.neko.hide_neko, lambda: self.neko.set_motion(False)):
            self.neko.show_neko()
            self.neko.set_motion(True)
            self.neko.companion.state = NekoState.IDLE
            self.neko.pet_reaction()
            self.neko.pet_reaction()
            self.assertTrue(self.neko.companion.pet_pending)
            cancel()
            self.assertFalse(self.neko.companion.pet_pending)
    def setUp(self):
        atlas_patch = patch("main.SpriteAtlas", return_value=self.atlas)
        atlas_patch.start()
        self.addCleanup(atlas_patch.stop)
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
        self.neko.invitation_timer.stop()
        self.neko.show_neko()
        APP.processEvents()

    def tearDown(self):
        self.neko.transition_timer.stop()
        self.neko.menu.hide()
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

    def test_startup_lands_before_greeting_and_ignores_pets_and_inactivity(self):
        origin = self.neko.pos()
        with patch.object(self.neko, "offline_line") as words:
            self.neko.show_neko(greet=True)
            self.assertEqual(self.neko.current_clip, "arrive")
            self.assertEqual(self.neko.animation_timer.interval(), 33)
            self.assertFalse(self.neko.transition_timer.isActive())
            self.neko.animate()
            self.assertTrue(self.neko.transition_timer.isActive())
            self.neko.pet_reaction()
            with patch("main.desktop_activity", return_value=(9999, 100, False)):
                self.neko.tick()
            self.assertEqual(self.neko.companion.state, NekoState.ARRIVING)
            words.assert_not_called()
            self.neko.finish_transition()
            words.assert_called_once_with("hello")
        self.assertEqual(self.neko.current_clip, "idle")
        self.assertEqual(self.neko.animation_timer.interval(), 100)
        self.assertGreater(self.neko.companion.next_nap, time.monotonic())
        self.assertEqual(self.neko.companion.pets, 0)
        self.assertEqual(self.neko.pos(), origin)

    def test_arrival_falls_from_monitor_top_without_saving_airborne_position(self):
        target = self.neko.pos()
        self.neko.show_neko(greet=True)
        screen = QApplication.screenAt(target + QPoint(56, 56)) or QApplication.primaryScreen()
        self.assertLess(self.neko.y(), screen.geometry().top())
        self.assertGreater(self.neko.geometry().bottom(), screen.geometry().top())
        self.neko.animate()
        start = self.neko.pose_started
        with patch("main.time.monotonic", return_value=start + 0.35):
            self.neko.animate()
        self.assertLess(self.neko.y(), target.y())
        self.neko.save_preferences()
        self.assertEqual(self.settings.value("position", type=QPoint), target + QPoint(CANVAS_PADDING, CANVAS_TOP))
        with patch("main.time.monotonic", return_value=start + 1.06):
            self.neko.animate()
        self.assertEqual(self.neko.pos(), target)
        self.neko.finish_transition()
        self.assertEqual(self.neko.pos(), target)

    def test_slow_startup_does_not_spend_the_drop_before_the_first_animation_tick(self):
        target = self.neko.pos()
        self.neko.show_neko(greet=True)
        top = self.neko.y()
        ready = self.neko.pose_started + 2.5
        with patch("main.time.monotonic", return_value=ready):
            self.neko.animate()
        self.assertEqual(self.neko.y(), top)
        self.assertEqual(self.neko.current_clip, "arrive")
        self.assertGreater(self.neko.companion.pose_until, ready + 1.8)
        with patch("main.time.monotonic", return_value=ready + 0.25):
            self.neko.animate()
        self.assertGreater(self.neko.y(), top)
        self.assertLess(self.neko.y(), target.y())
        with patch("main.time.monotonic", return_value=ready + 1.06):
            self.neko.animate()
        self.assertEqual(self.neko.pos(), target)

    def test_visible_fullscreen_startup_still_drops_but_stays_silent(self):
        with patch("main.desktop_activity", return_value=(0, 100, True)):
            self.neko.show_neko(greet=True)
            self.assertTrue(self.neko.isVisible())
            self.assertEqual(self.neko.companion.state, NekoState.ARRIVING)
            self.neko.finish_transition()
        self.assertFalse(self.neko.bubble.isVisible())

    def test_visible_arrival_survives_fullscreen_detection_after_launch(self):
        self.neko.show_neko(greet=True)
        with patch("main.desktop_activity", return_value=(0, 100, True)):
            self.neko.tick()
        self.assertEqual(self.neko.companion.state, NekoState.ARRIVING)
        self.assertIsNotNone(self.neko.arrival_target)
        self.neko.set_hide_fullscreen(True)
        self.assertFalse(self.neko.isVisible())
        self.assertIsNone(self.neko.arrival_target)
        self.assertEqual(self.neko.companion.state, NekoState.IDLE)

    def test_hidden_fullscreen_startup_does_not_drop_or_greet(self):
        self.neko.hide_fullscreen = True
        with patch("main.desktop_activity", return_value=(0, 100, True)):
            self.neko.show_neko(greet=True)
        self.assertFalse(self.neko.isVisible())
        self.assertIsNone(self.neko.arrival_target)
        self.assertFalse(self.neko.bubble.isVisible())

    def test_interrupted_arrival_restores_the_saved_landing_position(self):
        target = self.neko.pos()
        for interrupt in (self.neko.hide_neko, lambda: self.neko.set_motion(False)):
            self.neko.set_motion(True)
            self.neko.show_neko(greet=True)
            interrupt()
            self.assertEqual(self.neko.pos(), target)
            self.neko.save_preferences()
            self.assertEqual(self.settings.value("position", type=QPoint), target + QPoint(CANVAS_PADDING, CANVAS_TOP))

    def test_screen_change_before_the_first_animation_tick_does_not_leave_arrival_stuck(self):
        target = self.neko.pos()
        self.neko.show_neko(greet=True)
        self.neko.clamp_position()
        self.assertEqual(self.neko.pos(), target)
        self.assertEqual(self.neko.companion.state, NekoState.IDLE)
        self.assertIsNone(self.neko.arrival_target)

    def test_quitting_mid_arrival_starts_goodbye_at_the_landing_position(self):
        target = self.neko.pos()
        self.neko.show_neko(greet=True)
        self.neko.quit_neko()
        self.assertEqual(self.neko.pos(), target)
        self.assertIsNone(self.neko.arrival_target)
        self.assertEqual(self.neko.current_clip, "depart")
        self.assertEqual(self.neko.atlas.frame("depart", 0).toImage(),
                         self.neko.atlas.frames["idle", 0, 0].toImage())

    def test_fullscreen_hiding_interrupts_arrival_without_greeting_or_losing_position(self):
        target = self.neko.pos()
        self.neko.hide_fullscreen = True
        self.neko.show_neko(greet=True)
        with patch("main.desktop_activity", return_value=(0, 100, True)), \
                patch.object(self.neko, "offline_line") as words:
            self.neko.tick()
            words.assert_not_called()
        self.assertEqual(self.neko.pos(), target)
        self.assertIsNone(self.neko.arrival_target)
        self.assertEqual(self.neko.companion.state, NekoState.IDLE)

    def test_arrival_ink_stays_below_its_monitor_top(self):
        screen = QApplication.primaryScreen()
        self.neko.move(screen.geometry().left() + 80, screen.geometry().top() + 20)
        self.neko.show_neko(greet=True)
        self.neko.animate()
        start = self.neko.pose_started
        with patch("main.time.monotonic", return_value=start + 0.35):
            self.neko.animate()
            image = self.neko.grab().toImage()
        hidden_rows = screen.geometry().top() - self.neko.y()
        self.assertGreater(hidden_rows, 0)
        self.assertTrue(all(image.pixelColor(x, y).alpha() == 0
                            for x in range(self.neko.width()) for y in range(hidden_rows)))
        self.assertTrue(any(image.pixelColor(x, y).alpha() > 0
                            for x in range(self.neko.width()) for y in range(hidden_rows, self.neko.height())))

    def test_goodbye_travels_to_the_monitor_edge_without_saving_flight(self):
        origin = self.neko.pos()
        with patch("main.QApplication.quit"):
            self.neko.quit_neko()
            self.neko.animate()
            start = self.neko.pose_started
            with patch("main.time.monotonic", return_value=start + 1.6):
                self.neko.animate()
            self.assertNotEqual(self.neko.pos(), origin)
            self.neko.save_preferences()
            self.assertEqual(self.settings.value("position", type=QPoint), origin + QPoint(CANVAS_PADDING, CANVAS_TOP))
            self.neko.finish_transition()
            self.assertEqual(self.neko.pos(), origin)

    def test_high_perch_goodbye_uses_a_nearer_side_exit(self):
        area = QApplication.primaryScreen().geometry()
        origin = QPoint(area.center().x() - 96, area.top() + 8)
        self.neko.move(origin)
        self.neko.start_transition(NekoState.LEAVING, "depart")
        self.assertIsNotNone(self.neko.departure_target)
        self.assertTrue(self.neko.departure_target.x() < area.left()
                        or self.neko.departure_target.x() > area.right())
        self.neko.animate()
        with patch("main.time.monotonic", return_value=self.neko.pose_started + 1.5):
            self.neko.animate()
        self.assertGreater(abs(self.neko.x() - origin.x()), abs(self.neko.y() - origin.y()))

    def test_sleeping_quit_does_not_wake_her_for_a_performance(self):
        self.neko.companion.state = NekoState.SLEEPING
        self.neko.refresh_asset()
        with patch("main.QApplication.quit") as quit_app:
            self.neko.quit_neko()
            quit_app.assert_called_once()
        self.assertTrue(self.neko.closing)

    def test_menu_goodbye_finishes_an_awake_gesture_then_leaves_once(self):
        self.neko.companion.state = NekoState.TAIL_CHASE
        self.neko.pose_started = time.monotonic()
        self.neko.refresh_asset()
        action = next(action for action in self.neko.menu.actions() if action.text() == "Let her go · quit")
        with patch("main.QApplication.quit") as quit_app:
            action.trigger()
            self.assertTrue(getattr(self.neko, "quit_pending", False))
            self.assertFalse(self.neko.closing)
            deadline = self.neko.companion.pose_until
            self.neko.pet_reaction()
            self.neko.tick()
            action.trigger()
            self.assertEqual(self.neko.companion.pose_until, deadline)
            with patch("main.time.monotonic", return_value=deadline + 0.01):
                self.neko.animate()
            self.assertEqual(self.neko.companion.state, NekoState.LEAVING)
            quit_app.assert_not_called()
            self.neko.finish_transition()
            quit_app.assert_called_once()

    def test_visible_fullscreen_pet_still_plays_menu_goodbye(self):
        self.neko.fullscreen = True
        self.neko.hide_fullscreen = False
        with patch("main.QApplication.quit") as quit_app:
            self.neko.quit_neko()
            self.assertEqual(self.neko.companion.state, NekoState.LEAVING)
            quit_app.assert_not_called()

    def test_motion_off_can_finish_a_pending_gesture_goodbye(self):
        self.neko.companion.state = NekoState.TAIL_CHASE
        self.neko.refresh_asset()
        with patch("main.QApplication.quit") as quit_app:
            self.neko.quit_neko()
            self.assertTrue(self.neko.quit_pending)
            self.neko.set_motion(False)
            quit_app.assert_called_once()
            self.assertFalse(self.neko.quit_pending)

    def test_fullscreen_hiding_can_finish_a_pending_gesture_goodbye(self):
        self.neko.companion.state = NekoState.TAIL_CHASE
        self.neko.refresh_asset()
        self.neko.fullscreen = True
        self.neko.hide_fullscreen = False
        with patch("main.QApplication.quit") as quit_app:
            self.neko.quit_neko()
            self.assertTrue(self.neko.quit_pending)
            self.neko.set_hide_fullscreen(True)
            quit_app.assert_called_once()

    def test_departure_is_clipped_at_its_monitor_not_a_neighbour_below(self):
        self.neko.start_transition(NekoState.LEAVING, "depart")
        self.neko.lifecycle_area = QRect(0, 0, 800, 800)
        self.neko.move(100, 715)
        with patch("main.time.monotonic", return_value=self.neko.pose_started + 1.7):
            image = self.neko.grab().toImage()
        self.assertTrue(any(image.pixelColor(x, y).alpha() for x in range(192) for y in range(85)))
        self.assertFalse(any(image.pixelColor(x, y).alpha() for x in range(192) for y in range(85, 144)))

    def test_monitor_change_during_goodbye_restores_home_and_closes(self):
        origin = self.neko.pos()
        self.neko.quit_neko()
        self.neko.move(origin + QPoint(10, 80))
        with patch("main.QApplication.quit") as quit_app:
            self.neko.screen_changed()
            quit_app.assert_called_once()
        self.assertEqual(self.neko.pos(), origin)

    def test_delayed_first_tick_keeps_the_whole_goodbye(self):
        with patch("main.QApplication.quit"):
            self.neko.quit_neko()
            self.assertFalse(self.neko.transition_timer.isActive())
            ready = self.neko.pose_started + 2.5
            with patch("main.time.monotonic", return_value=ready):
                self.neko.animate()
            self.assertAlmostEqual(self.neko.companion.pose_until, ready + 2.2)

    def test_quit_plays_goodbye_once_then_cleans_up_without_moving_saved_position(self):
        origin = self.neko.pos()
        with patch("main.QApplication.quit") as quit_app:
            self.neko.quit_neko()
            self.assertFalse(self.neko.closing)
            self.assertEqual(self.neko.current_clip, "depart")
            deadline = self.neko.companion.pose_until
            self.neko.quit_neko()
            self.neko.pet_reaction()
            self.neko.tick()
            self.neko.show_neko()
            self.assertEqual(self.neko.companion.pose_until, deadline)
            quit_app.assert_not_called()
            self.neko.finish_transition()
            quit_app.assert_called_once()
        self.assertTrue(self.neko.closing)
        self.assertFalse(self.neko.isVisible())
        self.assertFalse(self.neko.transition_timer.isActive())
        self.assertFalse(self.neko.animation_timer.isActive())
        self.assertEqual(self.settings.value("position", type=QPoint), origin + QPoint(CANVAS_PADDING, CANVAS_TOP))

    def test_reduced_motion_or_hidden_quit_skips_jump_and_hidden_arrival_never_greets(self):
        with patch.object(self.neko, "offline_line") as words:
            self.neko.show_neko(greet=True)
            self.neko.hide_neko()
            self.neko.finish_transition()
            words.assert_not_called()
        with patch("main.QApplication.quit") as quit_app:
            self.neko.quit_neko()
            quit_app.assert_called_once()
        self.assertTrue(self.neko.closing)

    def test_turning_motion_off_finishes_an_active_departure(self):
        with patch("main.QApplication.quit") as quit_app:
            self.neko.quit_neko()
            self.neko.set_motion(False)
            quit_app.assert_called_once()
        self.assertTrue(self.neko.closing)

    def test_departure_timer_completes_cleanup_without_a_behavior_tick(self):
        with patch("main.QApplication.quit") as quit_app:
            self.neko.quit_neko()
            QTest.qWait(2350)
            quit_app.assert_called_once()
        self.assertTrue(self.neko.closing)

    def test_reduced_motion_startup_greets_without_a_jump(self):
        self.neko.set_motion(False)
        with patch.object(self.neko, "offline_line") as words:
            self.neko.show_neko(greet=True)
            words.assert_called_once_with("hello")
        self.assertEqual(self.neko.current_clip, "idle")
        self.assertFalse(self.neko.transition_timer.isActive())

    def test_both_lifecycle_trajectories_move_between_drawn_poses(self):
        origin = self.neko.pos()
        for state, clip, samples in ((NekoState.ARRIVING, "arrive", (0.25, 0.27)),
                                     (NekoState.LEAVING, "depart", (1.8, 1.82))):
            self.neko.start_transition(state, clip)
            self.neko.animate()
            start = self.neko.pose_started
            frames = []
            positions = []
            for elapsed in samples:
                with patch("main.time.monotonic", return_value=start + elapsed):
                    self.neko.animate()
                    frames.append(self.neko.grab().toImage())
                    positions.append(self.neko.pos())
            self.assertNotEqual(positions[0], positions[1], clip)

    def test_arrival_is_diagonal_and_stays_grounded_after_its_single_landing(self):
        area = QApplication.primaryScreen().geometry()
        home = QPoint(area.center().x() - 96, area.center().y())
        self.neko.move(home)
        self.neko.start_transition(NekoState.ARRIVING, "arrive")
        entry = self.neko.pos()
        self.assertGreater(home.x() - entry.x(), (home.y() - entry.y()) * 0.7)
        self.assertLess(home.x() - entry.x(), home.y() - entry.y())
        self.neko.animate()
        start = self.neko.pose_started
        last = entry
        for elapsed in (0.1, 0.2, 0.3, 0.4, 0.5, 0.8, 1.2, 1.9):
            with patch("main.time.monotonic", return_value=start + elapsed):
                self.neko.animate()
            position = self.neko.pos()
            self.assertGreaterEqual(position.x(), last.x())
            self.assertGreaterEqual(position.y(), last.y())
            if elapsed >= 0.5:
                self.assertEqual(position, home)
            last = position

    def test_low_goodbye_has_one_apex_and_a_diagonal_exit(self):
        area = QApplication.primaryScreen().geometry()
        home = QPoint(area.center().x() - 96, area.bottom() - 155)
        self.neko.move(home)
        self.neko.start_transition(NekoState.LEAVING, "depart")
        self.assertGreaterEqual(abs(self.neko.departure_target.x() - home.x()), 96)
        self.assertGreater(self.neko.departure_target.y(), home.y())
        self.neko.animate()
        start = self.neko.pose_started
        ys = []
        for elapsed in (1.2, 1.3, 1.4, 1.45, 1.5, 1.6, 1.8, 2.0, 2.15):
            with patch("main.time.monotonic", return_value=start + elapsed):
                self.neko.animate()
            ys.append(self.neko.y())
        apex = ys.index(min(ys))
        self.assertEqual(ys[:apex + 1], sorted(ys[:apex + 1], reverse=True))
        self.assertEqual(ys[apex:], sorted(ys[apex:]))

    def test_sad_goodbye_does_not_flip_the_front_expression_before_turning(self):
        self.neko.start_transition(NekoState.LEAVING, "depart")
        for elapsed in (0, 0.15, 0.25, 0.5, 0.75):
            frames = []
            with patch("main.time.monotonic", return_value=self.neko.pose_started + elapsed):
                for direction in (-1, 1):
                    self.neko.departure_direction = direction
                    frames.append(self.neko.grab().toImage())
            if elapsed < 0.7:
                self.assertEqual(*frames, elapsed)
            else:
                self.assertNotEqual(*frames, elapsed)

    def test_tail_run_uses_the_reference_cadence_without_speeding_up_walking(self):
        for state in (NekoState.TAIL_CHASE, NekoState.TAIL_CATCH):
            self.neko.companion.state = state
            self.neko.refresh_asset()
            self.assertEqual(self.neko.animation_timer.interval(), 50)
        self.neko.companion.state = NekoState.IDLE
        self.neko.refresh_asset()
        self.assertEqual(self.neko.animation_timer.interval(), 100)

    def test_speech_does_not_change_sleep_or_geometry(self):
        original = self.neko.geometry()
        self.assertTrue(self.neko.say("comfy."))
        self.assertEqual(self.neko.geometry(), original)
        self.neko.companion.state = NekoState.SLEEPING
        self.assertFalse(self.neko.say("wake up"))
        self.assertEqual(self.neko.companion.state, NekoState.SLEEPING)

    def test_every_idle_attempts_a_matching_thought_without_a_random_gate(self):
        for state in IDLE_STATES:
            self.neko.companion.state = state
            with patch.object(self.neko.companion, "tick", return_value="fidget"), \
                    patch("main.random.random", return_value=1), \
                    patch.object(self.neko, "offline_line") as words:
                self.neko.tick()
                words.assert_called_once_with(self.neko.current_clip)

    def test_idle_thoughts_still_respect_quiet_and_visible_bubble(self):
        self.neko.companion.state = NekoState.TAIL_CHASE
        self.neko.set_quiet(True)
        with patch.object(self.neko.companion, "tick", return_value="fidget"):
            self.neko.tick()
        self.assertFalse(self.neko.bubble.isVisible())
        self.neko.set_quiet(False)
        self.assertTrue(self.neko.say("a thought already here."))
        with patch.object(self.neko.companion, "tick", return_value="fidget"):
            self.neko.tick()
        self.assertEqual(self.neko.bubble.text(), "a thought already here.")

    def test_thoughts_have_a_small_frosted_backdrop_and_allow_time_to_read(self):
        self.assertTrue(self.neko.say("Look at meeee!"))
        APP.processEvents()
        self.assertGreaterEqual(self.neko.bubble.font().pixelSize(), 16)
        self.assertGreaterEqual(self.neko.bubble.font().weight(), 600)
        self.assertLessEqual(self.neko.bubble.width(), 270)
        self.assertGreaterEqual(self.neko.bubble.width(), 96)
        self.assertTrue(self.neko.bubble.testAttribute(Qt.WA_TransparentForMouseEvents))
        self.assertTrue(self.neko.bubble.windowFlags() & Qt.WindowTransparentForInput)
        self.assertFalse(self.neko.bubble.mask().contains(QPoint(3, 3)))
        self.assertAlmostEqual(self.neko.bubble.windowOpacity(), 0.88, delta=0.01)
        self.assertGreaterEqual(self.neko.bubble_timer.interval(), 5500)
        image = self.neko.bubble.grab().toImage()
        background = image.pixelColor(6, image.height() // 2)
        self.assertGreater(background.alpha(), 0)
        self.assertLess(background.alpha(), 60)
        self.assertEqual(image.pixelColor(0, 0).alpha(), 0)
        ink = [image.pixelColor(x, y) for x in range(image.width())
               for y in range(image.height()) if image.pixelColor(x, y).alpha() > 0]
        self.assertTrue(any(c.lightness() > 220 and c.alpha() > 200 for c in ink))
        self.assertTrue(any(c.lightness() < 80 for c in ink))
        area = QApplication.primaryScreen().availableGeometry()
        self.assertTrue(area.contains(self.neko.bubble.geometry()))
        self.assertTrue(self.neko.say("a much longer little thought for you to read. " * 3))
        self.assertLessEqual(self.neko.bubble_timer.interval(), 10000)

    def test_thought_render_changes_when_the_words_change(self):
        self.assertTrue(self.neko.say("Look at meeee!"))
        APP.processEvents()
        first = self.neko.bubble.grab().toImage()
        self.assertTrue(self.neko.say("Round.. around... around..."))
        APP.processEvents()
        self.assertNotEqual(first, self.neko.bubble.grab().toImage())


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

    def test_sleep_transitions_then_waits_for_a_pet_to_play_the_wake_frames(self):
        now = time.monotonic()
        with patch("main.desktop_activity", return_value=(180, 100, False)), \
                patch("main.time.monotonic", return_value=now):
            self.neko.tick()
        self.assertEqual(self.neko.current_clip, "fall_asleep")
        with patch("main.time.monotonic", return_value=now + 3):
            self.neko.tick()
        self.assertEqual(self.neko.current_clip, "sleep")
        with patch("main.time.monotonic", return_value=now + 1000):
            self.neko.tick()
            self.assertEqual(self.neko.current_clip, "sleep")
            self.neko.pet_reaction()
        self.assertEqual(self.neko.companion.state, NekoState.WAKING)
        self.assertEqual(self.neko.current_clip, "wake")

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

    def test_activity_words_retain_their_shared_pause(self):
        self.neko.companion.chatter_seconds = 75
        with patch("main.time.monotonic", return_value=100):
            self.assertTrue(self.neko.offline_line("typing"))
        self.neko.dismiss_bubble()
        with patch("main.time.monotonic", return_value=174.99):
            self.assertFalse(self.neko.offline_line("switch"))
        with patch("main.time.monotonic", return_value=175):
            self.assertTrue(self.neko.offline_line("switch"))
        self.neko.dismiss_bubble()
        with patch("main.time.monotonic", return_value=176):
            self.assertTrue(self.neko.offline_line("pet", prompted=True))

    def test_gesture_and_general_idle_thoughts_have_independent_clocks(self):
        self.neko.companion.chatter_seconds = 75
        with patch("main.time.monotonic", return_value=100):
            self.assertTrue(self.neko.offline_line("idle"))
        deadline = self.neko.companion.next_comment
        self.neko.dismiss_bubble()
        with patch("main.time.monotonic", return_value=110):
            self.neko.companion.state = NekoState.SNIFFING
            self.neko.companion.pose_until = 114
            self.neko.refresh_asset()
            self.assertTrue(self.neko.offline_line("sniff"))
        self.assertEqual(self.neko.companion.next_comment, deadline)
        self.neko.dismiss_bubble()
        with patch("main.time.monotonic", return_value=175):
            self.assertTrue(self.neko.offline_line("idle"))
        self.assertEqual(self.neko.companion.next_comment, 250)

    def test_due_general_thought_survives_a_visible_bubble_and_an_idle_gesture(self):
        self.neko.companion.next_comment = 100
        self.neko.companion.last_interaction = -1000
        with patch("main.time.monotonic", return_value=100):
            self.neko.say("already reading this")
            self.neko.poll_idle_thought(100)
        self.assertEqual(self.neko.companion.next_comment, 100)
        self.neko.dismiss_bubble()
        self.neko.companion.state = NekoState.SNIFFING
        self.neko.refresh_asset()
        with patch("main.time.monotonic", return_value=101):
            self.neko.poll_idle_thought(101)
        self.assertTrue(self.neko.bubble.isVisible())
        self.assertEqual(self.neko.companion.next_comment, 101 + self.neko.companion.chatter_seconds)

    def test_pending_ai_does_not_spend_the_general_deadline_or_show_a_second_line(self):
        self.neko.ai_enabled = True
        self.neko.companion.next_comment = 100
        self.neko.companion.last_interaction = -1000
        self.neko.brain_worker = object()
        with patch("main.time.monotonic", return_value=100):
            self.neko.poll_idle_thought(100)
        self.assertEqual(self.neko.companion.next_comment, 100)
        self.assertFalse(self.neko.bubble.isVisible())
        self.neko.brain_worker = None
        with patch("main.time.monotonic", return_value=101), patch.object(self.neko, "trigger_ai_brain", return_value=False):
            self.neko.poll_idle_thought(101)
        self.assertEqual(self.neko.companion.next_comment, 101 + self.neko.companion.chatter_seconds)

    def test_journal_shows_actual_dialogue_and_state_changes_with_category_filter(self):
        self.neko.companion.state = NekoState.FALLING_ASLEEP
        self.neko.refresh_asset()
        self.neko.companion.state = NekoState.IDLE
        self.neko.refresh_asset()
        self.neko.offline_line("idle")
        words = self.neko.bubble.text()
        with patch("main.autostart_enabled", return_value=False):
            self.neko.open_stats_window()
        nook = self.neko.stats_window
        nook.log_filter.setCurrentText("Thought")
        nook.update_journal()
        self.assertIn(words, nook.activity_log.toPlainText())
        self.assertNotIn("[Sleep]", nook.activity_log.toPlainText())
        nook.log_filter.setCurrentText("Sleep")
        self.assertIn("falling_asleep", nook.activity_log.toPlainText())
        self.neko.journal.error = "disk unavailable"
        nook.update_journal()
        self.assertIn("unavailable", nook.log_status.text())

    def test_gesture_thought_cannot_linger_past_its_active_pose(self):
        self.neko.companion.state = NekoState.SNIFFING
        self.neko.companion.pose_until = 104
        self.neko.refresh_asset()
        with patch("main.time.monotonic", return_value=102):
            self.assertTrue(self.neko.offline_line("sniff"))
        self.assertLessEqual(self.neko.bubble_timer.interval(), 2000)
        self.neko.dismiss_bubble()
        self.neko.companion.state = NekoState.IDLE
        self.neko.refresh_asset()
        self.assertFalse(self.neko.offline_line("sniff"))

    def test_ai_cannot_bypass_the_thought_cooldown(self):
        self.neko.ai_enabled = True
        self.neko.last_words = time.monotonic()
        self.assertFalse(self.neko.trigger_ai_brain())
        self.neko.request_generation = self.neko.ai_generation
        self.neko.request_started = time.monotonic()
        with patch.object(self.neko, "say") as say:
            self.neko.on_brain_finished("too soon", True)
        say.assert_not_called()

    def test_nook_timing_controls_apply_and_persist(self):
        with patch("main.autostart_enabled", return_value=False):
            self.neko.open_stats_window()
        for key, value in (("sleep_seconds", 45), ("sleep_duration", 90), ("chatter_seconds", 30), ("idle_seconds", 8), ("reaction_seconds", 90)):
            spin = self.neko.stats_window.timing[key]
            self.assertGreater(spin.lineEdit().width(), 35)
            spin.setValue(value)
            self.assertEqual(getattr(self.neko.companion, key), value)
            self.assertEqual(self.settings.value(key, type=int), value)
        self.assertFalse(hasattr(self.neko.stats_window, "follow"))
        self.assertFalse(self.settings.contains("follow_mouse"))
        with patch("main.desktop_activity", return_value=(45, 100, False)):
            self.neko.tick()
        self.assertEqual(self.neko.companion.state, NekoState.FALLING_ASLEEP)

    def test_popup_placement_avoids_neko_at_screen_corners_and_center(self):
        area = QRect(-1920, 0, 1920, 1080)
        for anchor in (QRect(-1920, 0, 112, 112), QRect(-112, 0, 112, 112),
                       QRect(-1920, 968, 192, 112), QRect(-192, 0, 192, 112),
                       QRect(-1920, 936, 192, 144), QRect(-192, 0, 192, 144),
                       QRect(-1920, 968, 112, 112), QRect(-112, 968, 112, 112),
                       QRect(-1000, 500, 112, 112)):
            for size in (QSize(220, 160), QSize(340, 640)):
                rect = QRect(adjacent_position(anchor, size, area), size)
                self.assertTrue(area.contains(rect))
                self.assertFalse(rect.intersects(anchor))

    def test_nook_and_popup_do_not_cover_neko(self):
        with patch("main.autostart_enabled", return_value=False):
            self.neko.open_stats_window()
        APP.processEvents()
        self.assertFalse(self.neko.stats_window.frameGeometry().intersects(self.neko.frameGeometry()))
        self.neko.stats_window.hide()
        APP.processEvents()
        self.neko.menu.popup(self.neko.pos())
        APP.processEvents()
        self.assertTrue(self.neko.menu.isVisible())
        self.assertFalse(self.neko.menu.geometry().intersects(self.neko.frameGeometry()))
        with patch("main.QApplication.platformName", return_value="windows"), \
                patch("main.win32gui.SetWindowPos") as pin:
            self.neko.pin_to_top(force=True)
        pin.assert_not_called()

    def test_cursor_cannot_walk_under_an_open_nook(self):
        with patch("main.autostart_enabled", return_value=False):
            self.neko.open_stats_window()
        cursor = self.neko.geometry().center() - QPoint(220, 0)
        self.neko.last_cursor = cursor - QPoint(30, 0)
        with patch("main.QCursor.pos", return_value=cursor):
            self.neko.tick()
        self.assertNotEqual(self.neko.current_clip, "walk")

    def test_timers_accept_typed_values_and_commit_on_enter(self):
        with patch("main.autostart_enabled", return_value=False):
            self.neko.open_stats_window()
        for key, value in (("sleep_seconds", 10), ("sleep_duration", 120), ("chatter_seconds", 45), ("idle_seconds", 9)):
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

    def test_nap_duration_persists_and_zero_disables_automatic_waking(self):
        self.neko.set_timing("sleep_duration", 90)
        other = NekoWidget(self.settings)
        try:
            self.assertEqual(other.companion.sleep_duration, 90)
        finally:
            other.tray_icon.hide()
            other.bubble.deleteLater()
            other.deleteLater()
        with patch("main.autostart_enabled", return_value=False):
            self.neko.open_stats_window()
        spin = self.neko.stats_window.timing["sleep_duration"]
        spin.setValue(0)
        self.assertEqual(spin.text(), "Until petted")
        self.assertEqual(self.neko.companion.sleep_duration, 0)
        self.assertEqual(self.settings.value("sleep_duration", type=int), 0)

    def test_new_pet_states_select_their_full_sequences(self):
        for state, name in ((NekoState.PET_STRETCH, "pet_stretch"), (NekoState.BACK_ARCH, "back_arch"),
                            (NekoState.HAPPY_HOP, "happy_hop"), (NekoState.SIDE_FLOP, "side_flop"),
                            (NekoState.SHOULDER_PEEK, "shoulder_peek"), (NekoState.PAW_OFFER, "paw_offer")):
            self.neko.companion.state = state
            self.neko.refresh_asset()
            self.assertEqual(self.neko.current_clip, name)

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
        self.settings.setValue("reaction_seconds", "broken")
        other = NekoWidget(self.settings)
        try:
            self.assertEqual(other.companion.sleep_seconds, 180)
            self.assertEqual(other.companion.chatter_seconds, 15)
            self.assertEqual(other.companion.idle_seconds, 120)
            self.assertEqual(other.companion.reaction_seconds, 60)
        finally:
            other.tray_icon.hide()
            other.bubble.deleteLater()
            other.deleteLater()

    def test_idle_cursor_movement_never_translates_neko(self):
        self.neko.set_auto_games(False)
        origin = self.neko.pos()
        for offset in (QPoint(-220, -160), QPoint(220, 160), QPoint(220, 0), QPoint(-220, 0)):
            cursor = self.neko.geometry().center() + offset
            with patch("main.QCursor.pos", return_value=cursor):
                self.neko.tick()
                for _ in range(100):
                    self.neko.animate()
            self.assertEqual(self.neko.pos(), origin)
            self.assertNotEqual(self.neko.current_clip, "walk")

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
            self.assertEqual(other.pos() + QPoint(CANVAS_PADDING, CANVAS_TOP), point)
            other.save_preferences()
            self.assertEqual(self.settings.value("position", type=QPoint), point)
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
        self.assertEqual(self.neko.cursor().shape(), Qt.ClosedHandCursor)
        move = QMouseEvent(QMouseEvent.MouseMove, QPointF(80, 60),
                           QPointF(self.neko.mapToGlobal(QPoint(80, 60))),
                           Qt.NoButton, Qt.LeftButton, Qt.NoModifier)
        APP.sendEvent(self.neko, move)
        QTest.mouseRelease(self.neko, Qt.LeftButton, pos=QPoint(80, 60))
        self.assertEqual(self.neko.companion.pets, 1)
        self.assertFalse(self.neko.pet_cursor_timer.isActive())
        self.assertEqual(self.neko.cursor().shape(), Qt.OpenHandCursor)

    def test_hover_hand_and_pet_stroke_are_local_and_cancel_on_leave(self):
        self.assertEqual(self.neko.cursor().shape(), Qt.OpenHandCursor)
        position = QCursor.pos()
        QTest.mouseClick(self.neko, Qt.LeftButton, pos=QPoint(56, 60))
        self.assertTrue(self.neko.pet_cursor_timer.isActive())
        first = self.neko.cursor().pixmap().toImage()
        self.neko.advance_pet_cursor()
        self.assertNotEqual(first, self.neko.cursor().pixmap().toImage())
        self.assertEqual(QCursor.pos(), position)
        APP.sendEvent(self.neko, QEvent(QEvent.Leave))
        self.assertFalse(self.neko.pet_cursor_timer.isActive())
        self.assertEqual(self.neko.cursor().shape(), Qt.OpenHandCursor)

    def test_hand_stroke_finishes_and_respects_reduced_motion_and_hiding(self):
        QTest.mouseClick(self.neko, Qt.LeftButton, pos=QPoint(56, 60))
        for _ in range(12):
            self.neko.advance_pet_cursor()
        self.assertFalse(self.neko.pet_cursor_timer.isActive())
        self.assertEqual(self.neko.cursor().shape(), Qt.OpenHandCursor)
        self.neko.set_motion(False)
        QTest.mouseClick(self.neko, Qt.LeftButton, pos=QPoint(56, 60))
        self.assertFalse(self.neko.pet_cursor_timer.isActive())
        self.neko.set_motion(True)
        QTest.mouseClick(self.neko, Qt.LeftButton, pos=QPoint(56, 60))
        self.neko.hide_neko()
        self.assertFalse(self.neko.pet_cursor_timer.isActive())

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
                patch("main.clear_startup_elevation") as clear_elevation, \
                patch("main.winreg.CreateKey"), patch("main.winreg.SetValueEx") as write:
            set_autostart(True)
        command = write.call_args.args[-1]
        self.assertIn("pythonw.exe", command)
        self.assertIn('"', command)
        self.assertIn("main.py", command)
        self.assertFalse(shortcut.exists())
        clear_elevation.assert_called_once()

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
