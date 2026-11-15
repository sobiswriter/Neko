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
from games import Runway
from main import NekoWidget

APP = QApplication.instance() or QApplication([])
APP.setQuitOnLastWindowClosed(False)


def dark_specks(image, largest=3):
    """Dark (ink) islands of at most `largest` pixels, 8-connected."""
    w, h = image.width(), image.height()
    dark = {(x, y) for y in range(h) for x in range(w)
            if image.pixelColor(x, y).alpha() and image.pixelColor(x, y).lightness() < 90}
    seen, specks = set(), 0
    for start in dark:
        if start in seen:
            continue
        stack, size = [start], 0
        seen.add(start)
        while stack:
            x, y = stack.pop()
            size += 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (x + dx, y + dy)
                    if n in dark and n not in seen:
                        seen.add(n)
                        stack.append(n)
        specks += size <= largest
    return specks


def outline_rings(image, depth):
    """Colours of opaque pixels by chessboard distance (1 = touching transparency), up to depth."""
    w, h = image.width(), image.height()
    solid = {(x, y) for y in range(h) for x in range(w) if image.pixelColor(x, y).alpha()}
    rings = {d: [] for d in range(1, depth + 1)}
    frontier = {p for p in solid if any((p[0] + dx, p[1] + dy) not in solid
                                        for dx in (-1, 0, 1) for dy in (-1, 0, 1))}
    seen = set(frontier)
    for d in range(1, depth + 1):
        for x, y in frontier:
            c = image.pixelColor(x, y)
            rings[d].append((c.red(), c.green(), c.blue()))
        frontier = {(x + dx, y + dy) for x, y in frontier for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                    if (x + dx, y + dy) in solid and (x + dx, y + dy) not in seen}
        seen |= frontier
    return rings


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

    def test_only_the_pixelated_victories_use_new_art(self):
        idle = self.atlas.frame("idle", 0).toImage()
        v12 = {clip.bank for clip in CLIPS.values() if clip.bank.startswith("v12-")}
        self.assertEqual(v12, {"v12-sproing", "v12-sproing2", "v12-roll"})
        for name in ("game_win_1", "game_win_2", "game_win_3"):
            self.assertEqual(self.atlas.frame(name, 100).toImage(), idle, name)
            clip = CLIPS[name]
            for i in clip.order[:-1]:
                frame = self.atlas.frames[clip.bank, clip.row + i // 4, i % 4].toImage()
                bounds = sprite_bounds(frame)
                self.assertGreater(bounds.height(), 25, (name, i))
                self.assertLessEqual(bounds.bottom(), 131, (name, i))
                # Pixel art: hard alpha and a handful of flat tones, like the original kitten.
                alphas = {frame.pixelColor(x, y).alpha() for y in range(bounds.top(), bounds.bottom() + 1)
                          for x in range(bounds.left(), bounds.right() + 1)}
                self.assertTrue(alphas <= {0, 255}, (name, i))
                colours = {frame.pixelColor(x, y).rgb() for y in range(bounds.top(), bounds.bottom() + 1)
                           for x in range(bounds.left(), bounds.right() + 1) if frame.pixelColor(x, y).alpha()}
                self.assertLessEqual(len(colours), 9, (name, i))
                # Closed black outline, and line art that stays continuous: no scatter of tiny
                # loose dark specks (the "threads" a thresholded soft line breaks into).
                rings = outline_rings(frame, 1)
                self.assertTrue(all(sum(c) < 60 for c in rings[1]), (name, i))
                self.assertLessEqual(dark_specks(frame), 4, (name, i))
        for clip in ("dizzy", "yawn", "paw_offer", "nuzzle", "game_jump"):
            self.assertFalse(CLIPS[clip].bank.startswith("v12-"), clip)

    def test_restless_starts_after_the_set_time_and_pets_calm_her_home(self):
        self.n.set_restless_minutes(1)
        self.assertEqual(self.n.restless_minutes, 1)
        self.n.ignored_seconds = 60 - 1
        self.n.last_ignore_tick = self.now - 1.5
        with patch("main.time.monotonic", return_value=self.now):
            self.n.watch_ignored(self.now, 0)
        self.assertIsNotNone(self.n.mood)
        self.assertEqual(self.n.companion.state, NekoState.RESTLESS)
        self.assertIn(self.n.bubble.text(), LINES["restless_start"])
        self.n.mood.stage = 2                      # Demanding: four pets.
        self.step(20, (300, 300))
        for _ in range(4):
            self.n.dismiss_bubble()
            with patch("main.time.monotonic", return_value=self.now):
                self.n.pet_reaction()
            self.step(2, (300, 300))
        self.assertTrue(self.n.mood is None or self.n.mood.forgiven)
        self.step(60, (300, 300))
        self.assertIsNone(self.n.mood)
        self.assertEqual(self.n.companion.state, NekoState.IDLE)
        self.assertEqual(self.n.pos(), QPoint(300, 400))
        self.assertEqual(self.n.companion.pets, 4)
        self.assertIn("forgiven", self.n.journal.text("Mood"))

    def test_sad_kitten_takes_one_pet_per_line_and_cheers_up_in_words(self):
        from restless import LISTEN_SECONDS, SAD
        with patch("main.time.monotonic", return_value=self.now):
            self.n.start_mood(self.now)
        self.n.mood.stage = SAD
        self.n.mood.curl(self.now)
        self.assertIn("level 4 of 4", self.n.restless_summary().lower())
        said = []
        for i in range(5):
            with patch("main.time.monotonic", return_value=self.now):
                self.n.pet_reaction()
                self.n.pet_reaction()                 # A quick second pet doesn't count.
            said.append(self.n.bubble.text())
            self.step(LISTEN_SECONDS + 0.2, (300, 300))
        self.assertEqual(self.n.companion.pets, 5)
        for i, text in enumerate(said[:4]):
            self.assertIn(text, LINES[f"restless_sad_{i + 1}"])
        self.assertIn(said[4], LINES["restless_sad_done"])
        self.assertIn("pet too soon", self.n.journal.text("Care"))
        self.step(60, (300, 300))
        self.assertIsNone(self.n.mood)

    def test_the_same_words_never_show_again_within_the_cooldown(self):
        from dialogue import LINE_COOLDOWN
        shown = []
        self.n.bubble.shown.connect(shown.append)
        texts = []
        for i in range(40):                       # Pets, gestures and idle chatter, back to back.
            self.now += 3
            with patch("main.time.monotonic", return_value=self.now):
                self.n.dismiss_bubble()
                kind = ("pet", "idle", "tail", "cursor")[i % 4]
                if self.n.say(self.n.dialogue.pick(kind), prompted=True, kind=kind):
                    texts.append((self.now, self.n.bubble.text()))
            with patch("main.time.monotonic", return_value=self.now):
                self.assertFalse(self.n.say(texts[-1][1], prompted=True))   # Asked again: refused.
        seen = {}
        for at, text in texts:
            self.assertGreaterEqual(at - seen.get(text, -LINE_COOLDOWN), LINE_COOLDOWN, text)
            seen[text] = at
        self.assertEqual(len(texts), len(set(t for _, t in texts)))
        self.assertIn("said recently", self.n.journal.text("Thought"))
        self.now += LINE_COOLDOWN + 1
        with patch("main.time.monotonic", return_value=self.now):
            self.n.dismiss_bubble()
            self.assertTrue(self.n.say(texts[0][1], prompted=True))   # After the cooldown it may return.

    def test_level_setting_persists_and_reaches_the_mood(self):
        self.n.set_restless_level_minutes(2)
        self.assertEqual(self.settings.value("restless_level_minutes", type=int), 2)
        with patch("main.time.monotonic", return_value=self.now):
            self.n.start_mood(self.now)
        self.assertEqual(self.n.mood.level_seconds, 120)
        self.n.set_restless_level_minutes(99)
        self.assertEqual(self.n.mood.level_seconds, 15 * 60)

    def test_requested_play_is_refused_only_while_she_is_sad(self):
        from restless import SAD
        with patch("main.time.monotonic", return_value=self.now):
            self.n.start_mood(self.now)
        self.n.mood.stage = SAD
        self.n.mood.curl(self.now)
        self.n.request_game()
        self.assertIsNone(self.n.game_timer.pending)
        self.assertIn("sad", self.n.bubble.text())

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
