"""Neko 1.2 on the real widget: Dodge the Cursor, the restless kitten, new wins and sounds."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from PySide6.QtCore import QEvent, QPoint, QSettings
from PySide6.QtWidgets import QApplication

from animations import CLIPS, SpriteAtlas, sprite_bounds
from behavior import NekoState
from dialogue import LINES
from dodge import OPENING, TAG_HOLD
from games import Runway
from main import NekoWidget

APP = QApplication.instance() or QApplication([])
APP.setQuitOnLastWindowClosed(False)
START = sum(seconds for seconds, _, _ in OPENING.values()) + 0.4


class V12DesktopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.atlas = SpriteAtlas("assets")

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.settings = QSettings(str(Path(self.folder.name) / "prefs.ini"), QSettings.IniFormat)
        self.patches = [patch("main.SpriteAtlas", return_value=self.atlas), patch("main.ActivityMonitor.start"),
                        patch("main.ctypes.windll.user32.GetAsyncKeyState", return_value=0),
                        patch("main.desktop_activity", return_value=(0, 0, False)),
                        patch("main.winsound.PlaySound")]
        for p in self.patches:
            p.start()
        self.n = NekoWidget(self.settings)
        for timer in (self.n.tick_timer, self.n.invitation_timer, self.n.animation_timer):
            timer.stop()
        self.n.show()
        self.n.move(300, 400)
        self.now = time.monotonic()

    def tearDown(self):
        self.n.end_mood(instant=True)
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
        while self.now < end - 1e-6:
            self.now = min(end, self.now + 0.02)
            point = cursor() if callable(cursor) else cursor
            with patch("main.time.monotonic", return_value=self.now), patch("main.QCursor.pos", return_value=QPoint(*point)):
                self.n.animate()

    def dodge(self):
        with patch("main.time.monotonic", return_value=self.now):
            self.assertTrue(self.n.start_game(self.now, "manual", "dodge"))
        self.n.animation_timer.stop()
        self.n.game.runway = Runway(0, 608, 400, 110)
        return self.n.game

    def test_dodge_art_is_complete_and_every_clip_returns_to_idle(self):
        self.assertTrue(self.n.game_art_ready("dodge"))
        idle = self.atlas.frame("idle", 0).toImage()
        for name in ("dodge_caught", "restless_sigh", "restless_demand", "restless_forgive", "game_win_1",
                     "game_win_2", "game_win_3", "dizzy"):
            self.assertEqual(self.atlas.frame(name, 100).toImage(), idle, name)
        for name, clip in CLIPS.items():
            if clip.bank.startswith("v12-"):
                for i in clip.order:
                    frame = self.atlas.frames[clip.bank, clip.row + i // 4, i % 4].toImage()
                    bounds = sprite_bounds(frame)
                    self.assertGreater(bounds.height(), 25, (name, i))  # the pancake-flat duck is low
                    self.assertLessEqual(bounds.bottom(), 131, (name, i))
                    self.assertGreaterEqual(bounds.left(), 1, (name, i))
                    self.assertLessEqual(bounds.right(), 190, (name, i))

    def test_a_dodge_round_announces_counts_down_and_says_its_lines(self):
        game = self.dodge()
        self.assertEqual(self.n.companion.state, NekoState.PLAYING)
        self.assertIn(self.n.bubble.text(), LINES["dodge_notice"])
        self.step(START, (790, 300))
        self.assertTrue(game.started)
        self.assertEqual(self.n.dodge_played, 1)
        self.assertEqual(self.n.games_played, 0)       # Catch's counter is separate.
        self.assertEqual(self.n.current_clip, self.n.game_clip())

    def test_touching_her_during_the_countdown_is_a_sad_foul_until_comforted(self):
        game = self.dodge()
        self.step(3.5, (790, 300))
        with patch.object(self.n, "body_contact", return_value=True):
            self.step(TAG_HOLD + 0.1, (game.x + 96, game.y + 92))
        self.assertEqual((game.phase, game.result), ("loss", "foul"))
        self.assertIn(self.n.bubble.text(), LINES["dodge_foul"])
        self.step(9, (790, 300))
        self.assertEqual(self.n.companion.state, NekoState.DISAPPOINTED)
        self.assertEqual(self.n.current_effect(self.now)[0], "sulk")
        with patch("main.time.monotonic", return_value=self.now):
            self.n.pet_reaction()
        self.step(12, (790, 300))
        self.assertIsNone(self.n.game)
        self.assertEqual(self.n.companion.pets, 1)
        self.assertEqual(self.n.pos(), QPoint(300, 400))
        self.assertEqual(self.n.dodge_won, 0)

    def test_three_tags_win_for_the_player_and_she_comes_home(self):
        game = self.dodge()
        self.step(START, (790, 300))
        with patch.object(self.n, "body_contact", return_value=True):
            self.step(10, lambda: (round(game.x) + 96, round(game.y) + 92))
        self.assertEqual(game.tags, 3)
        self.assertEqual(game.result, "caught")
        self.step(20, (790, 300))
        self.assertIsNone(self.n.game)
        self.assertEqual(self.n.pos(), QPoint(300, 400))
        self.assertEqual((self.n.dodge_played, self.n.dodge_won), (1, 0))

    def test_real_body_contact_ignores_padding_and_counts_fur(self):
        game = self.dodge()
        self.step(START + 1, (790, 300))
        frame = self.n.current_frame(self.now).toImage()
        bounds = sprite_bounds(frame)
        centre = (round(game.x) + bounds.center().x(), round(game.y) + bounds.center().y())
        self.assertTrue(self.n.body_contact(self.now, centre))
        self.assertFalse(self.n.body_contact(self.now, (round(game.x) + 2, round(game.y) + 2)))

    def test_automatic_games_alternate_and_dodge_starts_on_its_own(self):
        self.assertEqual(self.n.automatic_kind(), "catch")
        self.n.next_kind = "dodge"
        self.n.game_timer.due = self.now - 1
        for dt, point in ((0, QPoint(780, 200)), (0.2, QPoint(785, 205))):   # Just moving the mouse.
            with patch("main.time.monotonic", return_value=self.now + dt), patch("main.QCursor.pos", return_value=point):
                self.n.poll_game()
        self.assertIsNotNone(self.n.game)
        self.assertEqual(self.n.game.kind, "dodge")
        self.assertEqual(self.n.next_kind, "catch")
        self.n.end_game(immediate=True, clear_mood=True)
        self.n.set_auto_kind("dodge", False)
        self.n.next_kind = "dodge"
        self.assertEqual(self.n.automatic_kind(), "catch")
        self.assertFalse(self.settings.value("auto_dodge", type=bool))

    def test_restless_starts_after_the_set_time_and_pets_calm_her_home(self):
        self.n.set_restless_minutes(5)
        self.n.ignored_seconds = 5 * 60 - 1
        self.n.last_ignore_tick = self.now - 1.5
        with patch("main.time.monotonic", return_value=self.now):
            self.n.watch_ignored(self.now, 0)
        self.assertIsNotNone(self.n.mood)
        self.assertEqual(self.n.companion.state, NekoState.RESTLESS)
        self.assertIn(self.n.bubble.text(), LINES["restless_start"])
        self.n.mood.stage = 2                      # Jealous: three pets.
        self.step(20, (300, 300))
        for _ in range(3):
            self.n.dismiss_bubble()
            with patch("main.time.monotonic", return_value=self.now):
                self.n.pet_reaction()
            self.step(2, (300, 300))
        self.assertTrue(self.n.mood is None or self.n.mood.forgiven)
        self.step(60, (300, 300))
        self.assertIsNone(self.n.mood)
        self.assertEqual(self.n.companion.state, NekoState.IDLE)
        self.assertEqual(self.n.pos(), QPoint(300, 400))
        self.assertEqual(self.n.companion.pets, 3)
        self.assertIn("forgiven", self.n.journal.text("Mood"))

    def test_restless_respects_its_switch_quiet_fullscreen_and_absence(self):
        self.n.ignored_seconds = 10 ** 6
        for setup in (lambda: self.n.set_restless(False), lambda: self.n.set_quiet(True)):
            setup()
            self.n.ignored_seconds = 10 ** 6
            with patch("main.time.monotonic", return_value=self.now):
                self.n.watch_ignored(self.now, 0)
            self.assertIsNone(self.n.mood)
            self.n.set_restless(True)
            self.n.set_quiet(False)
        self.n.ignored_seconds = 10 ** 6
        with patch("main.time.monotonic", return_value=self.now):
            self.n.watch_ignored(self.now, 10 ** 4)     # You're away: she naps instead.
        self.assertIsNone(self.n.mood)
        self.assertTrue(self.settings.value("restless_enabled", type=bool))

    def test_carrying_a_restless_kitten_is_not_a_pet_and_hiding_snaps_her_home(self):
        with patch("main.time.monotonic", return_value=self.now):
            self.n.start_mood(self.now)
        self.step(5, (300, 300))
        with patch("main.time.monotonic", return_value=self.now):
            self.n.begin_pickup()
        self.assertEqual(self.n.companion.state, NekoState.HELD)
        self.n.move(800, 300)
        with patch("main.time.monotonic", return_value=self.now + 1):
            self.n.release_pickup()
            self.n.finish_pickup()
        self.assertIsNotNone(self.n.mood)
        self.assertEqual(self.n.companion.state, NekoState.RESTLESS)
        self.assertEqual(self.n.mood.line, "carried")
        self.assertEqual(self.n.companion.pets, 0)
        self.n.save_preferences()
        self.assertEqual(self.settings.value("position", type=QPoint), QPoint(300, 400) + QPoint(40, 32))
        self.n.hide_neko()
        self.assertIsNone(self.n.mood)
        self.assertEqual(self.n.pos(), QPoint(300, 400))

    def test_new_wins_rotate_and_still_poses_exist_for_reduced_motion(self):
        from animations import V12_STILL
        for name, pose in V12_STILL.items():
            self.assertIn(pose, CLIPS[name].order)

    def test_sounds_pick_varied_takes_and_the_purr_lasts_the_pet(self):
        import winsound
        self.n.set_sounds(True)
        names = []
        with patch("main.winsound.PlaySound") as play:
            for _ in range(6):
                self.n.last_sound = -1e9
                self.assertTrue(self.n.play_sound("mew", prompted=True))
                names.append(Path(play.call_args.args[0]).name)
            self.assertTrue(all(a != b for a, b in zip(names, names[1:])))
            self.assertGreater(len(set(names)), 1)
            self.n.last_sound = -1e9
            self.n.play_sound("purr", prompted=True)
            self.assertTrue(play.call_args.args[1] & winsound.SND_LOOP)
            self.assertTrue(self.n.purring)
            self.n.companion.state = NekoState.IDLE
            with patch("main.time.monotonic", return_value=self.now):
                self.n.animate()
            play.assert_called_with(None, 0)
            self.assertFalse(self.n.purring)
        for cue in ("mew", "purr", "chirp", "trill", "question", "yawn", "protest", "sad", "demand", "giggle"):
            self.assertGreaterEqual(len(self.n.voice.takes[cue]), 3, cue)


if __name__ == "__main__":
    unittest.main()
