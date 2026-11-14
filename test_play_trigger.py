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
from games import DECLARE_SECONDS, MANUAL_WAIT, NUDGE_AFTER, CursorGame, GameTimer, Runway
import main
from main import NekoWidget


class TimerTriggerTests(unittest.TestCase):
    def test_moving_arrow_already_beside_her_counts_as_an_approach(self):
        t = GameTimer(0)
        self.assertIsNone(t.tick(89, True, True, moving=True))     # Before the cooldown: nothing.
        self.assertIsNone(t.tick(90.1, True, True))                 # Parked at expiry: nothing.
        self.assertIsNone(t.tick(95, True, True, moving=True))      # A hand on the mouse...
        self.assertEqual(t.tick(95.3, True, True), "automatic")     # ...and a short hover starts it.

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

    def test_arrow_moving_inside_her_area_starts_automatic_play(self):
        self.n.game_timer.due = self.now - 5
        self.n.companion.state = NekoState.IDLE
        for x in (650, 662, 674, 676, 676):          # Already beside her, but a hand on the mouse.
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
        for x in (650, 662, 674, 676, 676):
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
