"""Catch triggers: a moving arrow beside her starts play, a requested game always happens."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QPoint, QSettings
from PySide6.QtWidgets import QApplication

app = QApplication.instance() or QApplication([])

from animations import SpriteAtlas
from behavior import NekoState
from games import (DECLARE_SECONDS, FORFEIT_AFTER, INVITE_REACH, MANUAL_WAIT, NUDGE_AFTER, WARNINGS,
                   CursorGame, GameTimer, Runway)
import main
from main import NekoWidget


class TimerTriggerTests(unittest.TestCase):
    def test_invitation_area_is_beside_her_and_a_little_farther_counts_as_away(self):
        r = Runway(0, 1600, 400, 140, drop=80)
        origin = 700
        for point in ((600, 450), (400, 450), (950, 450), (1200, 450), (950, 380)):
            self.assertTrue(r.invites(point, origin), point)
        for point in ((700, 450), (680, 450),                    # On her or in her petting margin.
                      (origin - INVITE_REACH - 20, 450),          # A little farther away.
                      (origin + 192 + INVITE_REACH + 20, 450),
                      (950, 330), (950, 560)):                    # Above or below the band.
            self.assertFalse(r.invites(point, origin), point)

    def test_parked_arrow_never_starts_play(self):
        t = GameTimer(0)
        for now in range(90, 400, 7):
            self.assertIsNone(t.tick(now, True, True))


class ManualWaitTests(unittest.TestCase):
    def step(self, game, end, cursor):
        while game.last < end - 1e-6:
            game.update(min(end, round(game.last + .02, 6)), cursor)

    def test_requested_game_waits_for_the_arrow_and_nudges(self):
        game = CursorGame(0, (400, 300), Runway(0, 1000, 300, 110), source="manual")
        self.step(game, NUDGE_AFTER + 1, (2000, 2000))
        self.assertEqual(game.phase, "declare")
        self.assertEqual(game.line, "bring")
        self.step(game, NUDGE_AFTER + 1.5, (450, 330))   # The arrow arrives: the countdown begins.
        self.assertEqual(game.phase, "ready")
        self.step(game, NUDGE_AFTER + 3, (2000, 2000))    # Leaving during the countdown doesn't call it off.
        self.assertNotEqual(game.result, "cancel")
        self.assertIn(game.phase, ("three", "two", "one"))

    def test_requested_game_gives_up_quietly_after_a_long_wait(self):
        game = CursorGame(0, (400, 300), Runway(0, 1000, 300, 110), source="manual")
        self.step(game, MANUAL_WAIT + .5, (2000, 2000))
        self.assertEqual((game.phase, game.result, game.started), ("done", "cancel", False))

    def test_automatic_game_still_calls_off_when_the_arrow_leaves(self):
        game = CursorGame(0, (400, 300), Runway(0, 1000, 300, 110), source="automatic")
        self.step(game, DECLARE_SECONDS, (2000, 2000))
        self.assertEqual(game.result, "cancel")


class ChaseWarningTests(unittest.TestCase):
    def test_several_warnings_before_a_forfeit(self):
        game = CursorGame(0, (400, 300), Runway(0, 1000, 300, 110), source="manual")
        lines = []
        t = 0.0
        while game.phase != "go" and t < 10:
            t = round(t + .02, 6)
            game.update(t, (450, 330))
            line = game.take_line()
        start = t
        while game.result is None and t < start + 20:
            t = round(t + .02, 6)
            game.update(t, (450, -400))           # Far above her area.
            line = game.take_line()
            if line and line.startswith("protest_"):
                lines.append((round(t - start, 1), line))
        self.assertEqual(len(lines), len(WARNINGS), lines)
        self.assertEqual(lines[-1][1], "protest_last")
        self.assertEqual(game.result, "loss")
        self.assertGreaterEqual(t - start, FORFEIT_AFTER)

    def test_coming_back_resets_the_warnings(self):
        game = CursorGame(0, (400, 300), Runway(0, 1000, 300, 110), source="manual")
        t = 0.0
        while game.phase != "go":
            t = round(t + .02, 6)
            game.update(t, (450, 330))
        for _ in range(3):                          # Three trips out of 5 s each, back in between.
            for _ in range(250):
                t = round(t + .02, 6)
                game.update(t, (450, -400))
            for _ in range(25):
                t = round(t + .02, 6)
                game.update(t, (game.x + 260, 330))
        self.assertNotEqual(game.result, "loss")


class DesktopTriggerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.atlas = SpriteAtlas("assets")

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        settings = QSettings(str(Path(self.folder.name) / "prefs.ini"), QSettings.IniFormat)
        self.patches = [patch("main.SpriteAtlas", return_value=self.atlas),
                        patch("main.ActivityMonitor.start"),
                        patch("main.winsound.PlaySound"),
                        patch("main.ctypes.windll.user32.GetAsyncKeyState", return_value=0),
                        patch("main.desktop_activity", return_value=(0, 0, False))]
        for p in self.patches:
            p.start()
        self.n = NekoWidget(settings)
        for timer in (self.n.tick_timer, self.n.invitation_timer, self.n.animation_timer):
            timer.stop()
        self.n.show()
        self.n.finish_transition()
        self.n.move(250, 350)
        self.now = 1000.0
        self.n.last_keyboard = self.n.companion.last_interaction = -1e9

    def tearDown(self):
        self.n.end_game(immediate=True, clear_mood=True)
        self.n.end_mood(instant=True)
        self.n.tray_icon.hide()
        self.n.activity.close()
        self.n.close()
        for p in self.patches:
            p.stop()
        self.folder.cleanup()

    def poll(self, dt, point):
        self.now += dt
        with patch("main.time.monotonic", return_value=self.now), patch("main.QCursor.pos", return_value=point):
            self.n.poll_game()

    def test_arrow_brought_from_a_little_farther_starts_automatic_play(self):
        self.n.game_timer.due = self.now - 5
        self.n.companion.state = NekoState.IDLE
        for x in (660, 670, 655, 665, 660):          # Just wiggling beside her: no game.
            self.poll(.1, QPoint(x, 420))
        self.assertIsNone(self.n.game)
        for x in (790, 790, 650, 650, 650, 650):     # A little farther away, then back beside her.
            self.poll(.1, QPoint(x, 420))
        self.assertIsNotNone(self.n.game)
        self.assertEqual(self.n.game.source, "automatic")

    def test_requested_game_starts_with_the_arrow_on_another_monitor(self):
        self.n.companion.state = NekoState.IDLE
        self.n.request_game()
        self.poll(.1, QPoint(5000, 5000))            # The offscreen test screen is 800 px wide.
        self.assertIsNotNone(self.n.game)
        self.assertEqual(self.n.game.source, "manual")

    def test_restless_kitten_accepts_a_game_while_resting(self):
        with patch("main.time.monotonic", return_value=self.now):
            self.n.start_mood(self.now)
        self.n.mood.stage = 1
        self.n.mood.step = ("rest", None, self.now, 30)
        self.n.game_timer.due = self.now - 5
        for x in (790, 790, 650, 650, 650, 650):
            self.poll(.1, QPoint(x, 420))
        self.assertIsNotNone(self.n.game)
        self.assertEqual(self.n.game.source, "automatic")

    def test_play_after_a_loss_comforts_her_then_rematches(self):
        self.n.companion.state = NekoState.IDLE
        with patch("main.time.monotonic", return_value=self.now):
            self.assertTrue(self.n.start_game(self.now, "manual"))
            self.n.game.enter("curl", self.now)
            self.n.companion.state = NekoState.DISAPPOINTED
            self.n.request_game()
        self.assertEqual(self.n.game.phase, "comfort")
        for _ in range(400):                            # Her drawn get-up, then the rematch.
            self.now += .02
            with patch("main.time.monotonic", return_value=self.now), \
                    patch("main.QCursor.pos", return_value=QPoint(650, 420)):
                if self.n.game is not None:
                    self.n.animate()
                else:
                    self.n.poll_game()
            if self.n.game is not None and self.n.game.phase == "declare":
                break
        self.assertIsNotNone(self.n.game)
        self.assertEqual((self.n.game.phase, self.n.game.source), ("declare", "manual"))


if __name__ == "__main__":
    unittest.main()
