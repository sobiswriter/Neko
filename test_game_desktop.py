"""Actual atlas/controller checks; native timing is exercised separately by the preview probe."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from PySide6.QtCore import QEvent, QPoint, QSettings, Qt
from PySide6.QtWidgets import QApplication
from animations import GAME_ROWS, SpriteAtlas, CLIPS, sprite_bounds, pet_landmarks
from behavior import NekoState
from games import Runway
from main import NekoWidget

APP = QApplication.instance() or QApplication([])
APP.setQuitOnLastWindowClosed(False)


class DesktopGameTests(unittest.TestCase):
    def test_automatic_game_can_be_observed_in_the_live_journal(self):
        with patch("main.autostart_enabled", return_value=False):
            self.n.open_stats_window()
        nook = self.n.stats_window
        self.n.game_timer.due = self.now - 1
        with patch("main.time.monotonic", return_value=self.now):
            self.n.poll_game()
        self.assertIn("Nook controls", self.n.game_timer.reason)
        nook.tabs.setCurrentWidget(nook.journal_tab)
        for dt, point in ((0, QPoint(346, 420)), (.2, QPoint(650, 420)), (.5, QPoint(650, 420))):
            with patch("main.time.monotonic", return_value=self.now + dt), patch("main.QCursor.pos", return_value=point):
                self.n.poll_game()
        self.assertIsNotNone(self.n.game)
        self.assertEqual(self.n.game.source, "automatic")
        nook.update_journal()
        self.assertIn("invitation accepted", nook.activity_log.toPlainText())
        self.assertIn("session created: automatic", nook.activity_log.toPlainText())

    @classmethod
    def setUpClass(cls):
        cls.atlas = SpriteAtlas("assets")

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.settings = QSettings(str(Path(self.folder.name) / "prefs.ini"), QSettings.IniFormat)
        self.patches = [patch("main.SpriteAtlas", return_value=self.atlas),
                        patch("main.ActivityMonitor.start"),
                        patch("main.ctypes.windll.user32.GetAsyncKeyState", return_value=0),
                        patch("main.desktop_activity", return_value=(0, 0, False))]
        for p in self.patches:
            p.start()
        self.n = NekoWidget(self.settings)
        self.n.tick_timer.stop()
        self.n.invitation_timer.stop()
        self.n.animation_timer.stop()
        self.n.show()
        self.n.move(250, 350)
        self.now = time.monotonic()

    def tearDown(self):
        self.n.end_game(immediate=True, clear_mood=True)
        self.n.hide()
        for timer in (self.n.animation_timer, self.n.tick_timer, self.n.save_timer):
            timer.stop()
        self.n.tray_icon.hide()
        self.n.activity.close()
        self.n.bubble.deleteLater()
        if self.n.stats_window:
            self.n.stats_window.deleteLater()
        self.n.deleteLater()
        APP.sendPostedEvents(None, QEvent.DeferredDelete)
        APP.processEvents()
        for p in reversed(self.patches):
            p.stop()
        self.folder.cleanup()

    def step(self, seconds, cursor):
        end = self.now + seconds
        while self.now < end - .00001:
            self.now = min(end, self.now + .02)
            with patch("main.time.monotonic", return_value=self.now), patch("main.QCursor.pos", return_value=QPoint(*cursor)):
                self.n.animate()

    def start(self):
        with patch("main.time.monotonic", return_value=self.now):
            self.assertTrue(self.n.start_game(self.now, "manual"))
        self.n.animation_timer.stop()
        self.n.game.runway = Runway(0, 1000, 350, 110)

    def test_stationary_high_and_low_targets_are_really_catchable(self):
        for target in ((470, 355), (470, 470), (800, 420)):
            self.start()
            game = self.n.game
            self.step(15, target)
            self.assertEqual(game.result, "win", (target, list(game.log)))
            if self.n.game:
                self.assertEqual(self.n.game.result, "win", (target, list(self.n.game.log)))
            else:
                self.assertEqual(self.n.companion.state, NekoState.IDLE)
            self.assertEqual(self.n.companion.pets, 0)
            self.assertEqual(self.n.companion.naps, 0)
            self.n.end_game(immediate=True, clear_mood=True)

    def test_contact_is_current_paw_alpha_in_both_directions(self):
        self.start()
        g = self.n.game
        g.phase, g.since = "jump", self.now
        g.start_x, g.end_x, g.height = 250, 350, 60
        for direction in (-1, 1):
            g.direction = direction
            x, y = g.position_at(self.now + .32)
            px = 49 if direction < 0 else 142
            self.assertTrue(self.n.game_contact(self.now + .32, (round(x) + px, round(y) + 79)))
            self.assertFalse(self.n.game_contact(self.now + .32, (round(x) + 96, round(y) + 60)))
            self.assertFalse(self.n.game_contact(self.now + .32, (round(x), round(y))))

    def test_saved_origin_cancellation_and_hiding_never_save_airborne(self):
        self.start()
        origin = self.n.pos()
        self.step(2, (470, 355))
        self.n.save_preferences()
        self.assertEqual(self.settings.value("position", type=QPoint), origin + QPoint(40, 32))
        self.n.hide_neko()
        self.assertIsNone(self.n.game)
        self.assertEqual(self.n.pos(), origin)
        self.assertFalse(hasattr(self.n, "game_overlay"))

    def test_loss_survives_hide_carry_and_only_one_pet_comforts(self):
        self.start()
        self.step(4.2, (650, 400))
        self.step(9, (2000, -100))
        self.assertEqual(self.n.game.phase, "curl")
        self.assertEqual(self.n.companion.state, NekoState.DISAPPOINTED)
        self.n.hide_neko()
        self.n.show_neko()
        with patch("main.time.monotonic", return_value=self.now):
            self.n.begin_pickup()
        self.assertEqual(self.n.companion.carry_rest[0], NekoState.DISAPPOINTED)
        with patch("main.time.monotonic", return_value=self.now + 4):
            self.n.release_pickup()
        with patch("main.time.monotonic", return_value=self.now + 5):
            self.n.finish_pickup()
        self.assertEqual(self.n.companion.state, NekoState.DISAPPOINTED)
        self.now += 5
        with patch("main.time.monotonic", return_value=self.now):
            self.n.pet_reaction()
            self.n.pet_reaction()
        self.step(8, (2000, -100))
        self.assertIsNone(self.n.game)
        self.assertEqual(self.n.companion.pets, 1)
        self.assertEqual(self.n.companion.naps, 0)

    def test_scheduler_waits_for_nap_and_manual_promotes_auto(self):
        self.n.companion.state = NekoState.SLEEPING
        self.n.game_timer.due = self.now - 10000
        with patch("main.time.monotonic", return_value=self.now):
            self.n.tick()
        self.assertIsNone(self.n.game)
        self.assertEqual(self.n.game_timer.pending, "automatic")
        self.n.game_timer.request(self.now, manual=True)
        self.n.companion.state = NekoState.IDLE
        with patch("main.time.monotonic", return_value=self.now):
            self.n.tick()
        self.assertEqual(self.n.game.source, "manual")
        self.assertIsNone(self.n.game_timer.pending)

    def test_defaults_settings_and_missing_art_fail_safely(self):
        self.assertTrue(self.n.game_timer.enabled)
        self.assertEqual(self.n.game_timer.interval, 90)
        self.n.set_game_interval(120)
        self.n.set_auto_games(False)
        self.assertEqual(self.settings.value("game_interval", type=int), 120)
        self.assertFalse(self.settings.value("auto_games", type=bool))
        with patch.object(self.n, "game_art_ready", return_value=False):
            self.n.request_game()
        self.assertIsNone(self.n.game)

    def test_idle_gesture_does_not_swallow_an_armed_side_invitation(self):
        self.n.game_timer.due = self.now - 1
        self.n.companion.state = NekoState.TAIL_CHASE
        for dt, point in ((0, QPoint(346, 420)), (.2, QPoint(650, 420)), (.6, QPoint(650, 420))):
            with patch("main.time.monotonic", return_value=self.now + dt), patch("main.QCursor.pos", return_value=point):
                self.n.poll_game()
        self.assertIsNone(self.n.game)
        self.n.companion.state = NekoState.IDLE
        with patch("main.time.monotonic", return_value=self.now + .7), patch("main.QCursor.pos", return_value=QPoint(650, 420)):
            self.n.poll_game()
        self.assertEqual(self.n.game.source, "automatic")

    def test_unattended_sulk_can_finish_and_sleep_without_a_pet(self):
        self.start()
        self.n.game.started = True
        self.n.game.result = "loss"
        self.n.game.enter("curl", self.now)
        self.n.companion.state = NekoState.DISAPPOINTED
        self.n.companion.next_nap = 0
        with patch("main.time.monotonic", return_value=self.now), patch("main.desktop_activity", return_value=(9999, 0, False)):
            self.n.tick()
        self.assertEqual(self.n.game.phase, "comfort")
        self.assertEqual(self.n.game_interaction, "sleep")
        self.step(4, (2000, -100))
        self.assertIsNone(self.n.game)
        with patch("main.time.monotonic", return_value=self.now), patch("main.desktop_activity", return_value=(9999, 0, False)):
            self.n.tick()
        self.assertEqual(self.n.companion.state, NekoState.FALLING_ASLEEP)
        self.assertEqual((self.n.companion.pets, self.n.companion.naps), (0, 1))

    def test_pet_can_override_the_automatic_settle_for_sleep(self):
        self.start()
        self.n.game.enter("comfort", self.now)
        self.n.game_interaction = "sleep"
        with patch("main.time.monotonic", return_value=self.now):
            self.n.pet_reaction()
        self.step(4, (2000, -100))
        self.assertIsNone(self.n.game)
        self.assertEqual((self.n.companion.pets, self.n.companion.naps), (1, 0))

    def test_button_held_in_another_app_discards_invitation_entry(self):
        self.n.game_timer.due = self.now - 1
        with patch("main.ctypes.windll.user32.GetAsyncKeyState", return_value=0x8000), \
                patch("main.time.monotonic", return_value=self.now), \
                patch("main.QCursor.pos", return_value=QPoint(346, 420)):
            self.n.poll_game()
        for dt in (.3, .7):
            with patch("main.time.monotonic", return_value=self.now + dt), patch("main.QCursor.pos", return_value=QPoint(650, 420)):
                self.n.poll_game()
        self.assertIsNone(self.n.game)
        for dt, point in ((1, QPoint(346, 420)), (1.2, QPoint(650, 420)), (1.5, QPoint(650, 420))):
            with patch("main.time.monotonic", return_value=self.now + dt), patch("main.QCursor.pos", return_value=point):
                self.n.poll_game()
        self.assertEqual(self.n.game.source, "automatic")

    def test_counters_persist_once_and_countdown_abort_is_not_a_play(self):
        self.start()
        self.step(1, (650, 400))
        self.assertEqual(self.n.games_played, 0)
        with patch("main.time.monotonic", return_value=self.now):
            self.n.end_game()
        self.step(3, (650, 400))
        self.assertEqual(self.n.games_played, 0)
        self.start()
        self.step(15, (470, 355))
        self.assertEqual((self.n.games_played, self.n.games_won), (1, 1))
        self.assertEqual(self.settings.value("games_played", type=int), 1)
        self.assertEqual(self.settings.value("games_won", type=int), 1)
        self.assertIn("1 games played", self.n.game_stats_action.text())
        self.n.prepare_menu()
        self.assertEqual((self.n.games_played, self.n.games_won), (1, 1))

    def test_outcome_bags_show_all_three_and_never_repeat_at_seam(self):
        for outcome in ("win", "loss"):
            selected = []
            for _ in range(9):
                self.start()
                g = self.n.game
                g.started = True
                g.result = outcome
                g.enter(outcome, self.now)
                self.step(.02, (650, 400))
                selected.append(g.variant)
                self.n.end_game(immediate=True, clear_mood=True)
            for index in range(0, 9, 3):
                self.assertEqual(set(selected[index:index + 3]), {0, 1, 2})
            self.assertTrue(all(a != b for a, b in zip(selected, selected[1:])))

    def test_invalid_counters_migrate_without_exceeding_played(self):
        for played, won, expected in (("bad", 4, (0, 0)), (-1, -8, (0, 0)), (3, 99, (3, 3))):
            self.settings.setValue("games_played", played)
            self.settings.setValue("games_won", won)
            n = NekoWidget(self.settings)
            try:
                self.assertEqual((n.games_played, n.games_won), expected)
            finally:
                n.tray_icon.hide()
                n.activity.close()
                n.bubble.deleteLater()
                n.deleteLater()

    def test_nook_refreshes_timer_preferences_and_sleeping_request_explains_wait(self):
        with patch("main.autostart_enabled", return_value=False):
            self.n.open_stats_window()
        self.n.stats_window.close()
        self.n.set_auto_games(False)
        self.n.set_game_interval(120)
        self.n.open_stats_window()
        self.assertFalse(self.n.stats_window.auto_games.isChecked())
        self.assertEqual(self.n.stats_window.game_interval.value(), 120)
        self.n.companion.state = NekoState.SLEEPING
        with patch.object(self.n.tray_icon, "showMessage") as message:
            self.n.request_game()
        message.assert_called_once()
        self.assertEqual(self.n.companion.state, NekoState.SLEEPING)
        self.assertEqual(self.n.game_timer.pending, "manual")

    def test_gentle_game_has_no_translation_and_can_win(self):
        self.n.motion = False
        self.start()
        origin = self.n.pos()
        self.step(7, (299, 429))
        self.assertEqual(self.n.game.result, "win")
        self.assertEqual(self.n.pos(), origin)

    def test_art_complete_bounds_endpoints_and_contact_landmarks(self):
        for bank, rows in GAME_ROWS.items():
            for i in range(rows * 4):
                frame = self.atlas.frames[f"game-{bank}", i // 4, i % 4]
                bounds = sprite_bounds(frame.toImage())
                self.assertGreater(bounds.width(), 45, (bank, i))
                self.assertGreater(bounds.height(), 35, (bank, i))
                self.assertGreater(bounds.left(), 1)
                self.assertLess(bounds.right(), 190)
                self.assertGreater(bounds.top(), 1)
                self.assertLessEqual(bounds.bottom(), 131)
                q = frame.toImage()
                opaque = {(x, y) for y in range(q.height()) for x in range(q.width()) if q.pixelColor(x, y).alpha() >= 128}
                sizes = []
                while opaque:
                    pending, count = [opaque.pop()], 0
                    while pending:
                        x, y = pending.pop()
                        count += 1
                        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
                            p = x + dx, y + dy
                            if p in opaque:
                                opaque.remove(p)
                                pending.append(p)
                    sizes.append(count)
                self.assertEqual(sum(size > 2 for size in sizes), 1, (bank, i, sizes))
        self.assertEqual(self.atlas.frame("game_comfort", 100).toImage(), self.atlas.frame("idle", 0).toImage())
        self.assertEqual(sum(CLIPS["game_jump"].durations), 640)

    def test_every_jump_cancel_phase_lands_and_returns_home(self):
        for elapsed in (.01, .05, .12, .2, .32, .5, .63):
            self.start()
            g = self.n.game
            g.phase, g.since, g.last = "jump", self.now, self.now
            g.start_x, g.end_x, g.height = 250, 350, 70
            self.step(elapsed, (2000, -100))
            with patch("main.time.monotonic", return_value=self.now):
                self.n.end_game()
            self.assertEqual(g.result, "cancel")
            self.step(2, (2000, -100))
            self.assertIsNone(self.n.game)
            self.assertEqual(self.n.pos(), QPoint(250, 350))

    def test_new_wins_and_walk_recover_to_the_actual_idle_at_retained_scale(self):
        idle = self.atlas.frame("idle", 0).toImage()
        for name, drawn in (("game_win_0", 22), ("game_win_1", 18), ("game_win_2", 18), ("game_settle", 15)):
            clip = CLIPS[name]
            self.assertEqual(self.atlas.frame(name, 100).toImage(), idle)
            q = self.atlas.frames[clip.bank, drawn // 4, drawn % 4].toImage()
            bounds = sprite_bounds(q)
            head, center, *_ = pet_landmarks(q.copy(bounds))
            self.assertAlmostEqual(head, 62, delta=4, msg=name)
            self.assertAlmostEqual(bounds.left() + center, 90.5, delta=2, msg=name)
            self.assertAlmostEqual(bounds.top(), 48, delta=2, msg=name)

    def test_pet_during_jump_waits_for_landing_and_counts_once(self):
        self.start()
        g = self.n.game
        g.phase, g.since = "jump", self.now
        g.start_x, g.end_x, g.height = 250, 350, 70
        self.step(.2, (2000, -100))
        with patch("main.time.monotonic", return_value=self.now):
            self.n.pet_reaction()
        self.assertEqual(g.phase, "jump")
        self.assertEqual(self.n.companion.pets, 0)
        self.step(2, (2000, -100))
        self.assertIsNone(self.n.game)
        self.assertEqual(self.n.companion.pets, 1)

    def test_fullscreen_is_neutral_and_quiet_or_typing_delays_auto(self):
        self.n.game_timer.due = self.now - 1
        self.n.quiet = True
        with patch("main.time.monotonic", return_value=self.now):
            self.n.tick()
        self.assertIsNone(self.n.game)
        self.n.quiet = False
        self.n.last_keyboard = self.now
        with patch("main.time.monotonic", return_value=self.now + 1):
            self.n.tick()
        self.assertIsNone(self.n.game)
        self.n.companion.state = NekoState.IDLE
        with patch("main.time.monotonic", return_value=self.now + 2.1):
            self.n.tick()
        self.assertIsNone(self.n.game)
        # A fresh outside observation and stable side-zone entry are required.
        self.n.companion.state = NekoState.IDLE
        for moment, point in ((2.2, QPoint(346, 420)), (2.4, QPoint(650, 420)), (2.7, QPoint(650, 420))):
            with patch("main.time.monotonic", return_value=self.now + moment), patch("main.QCursor.pos", return_value=point):
                self.n.poll_game()
        self.assertIsNotNone(self.n.game)
        g = self.n.game
        with patch("main.time.monotonic", return_value=self.now + 2.8), patch("main.desktop_activity", return_value=(0, 0, True)):
            self.n.tick()
        self.assertIsNone(self.n.game)
        self.assertEqual(self.n.pos(), QPoint(*g.origin))
        self.assertEqual(self.n.companion.naps, 0)


if __name__ == "__main__":
    unittest.main()
