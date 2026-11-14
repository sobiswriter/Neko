import math
import random
import unittest

from dodge import (CLIP_SECONDS, DodgeGame, FAR_FAIL, OPENING, RECOVERY, ROUND_SECONDS, TAG_GRACE, TAG_HOLD,
                   TAGS_TO_WIN, TELL)
from games import Runway

START = sum(seconds for seconds, _, _ in OPENING.values()) + 0.4  # notice → "Go!" → approach


class DodgeTests(unittest.TestCase):
    def game(self, seed=1, motion=True):
        return DodgeGame(0, (600, 400), Runway(0, 1500, 400, 110), motion, "manual", rng=random.Random(seed))

    def run_until(self, game, end, cursor, contact=lambda g, now: False, far=False, step=0.02):
        """Advance like the desktop does; cursor/contact may be functions of the game and time."""
        now = game.last
        while now < end - 1e-9:
            now = round(min(end, now + step), 6)
            point = cursor(game, now) if callable(cursor) else cursor
            game.update(now, point, contact(game, now), far=far)
            if game.phase == "done":
                break
        return now

    def on_body(self, game, now):
        return game.centre

    def test_clip_lengths_match_the_drawn_escapes(self):
        from animations import CLIPS
        for phase, seconds in CLIP_SECONDS.items():
            self.assertAlmostEqual(sum(CLIPS[f"dodge_{phase}"].durations) / 1000, seconds, places=2)

    def test_opening_announces_counts_down_and_starts_the_clock_at_go(self):
        game = self.game()
        self.assertEqual(game.take_line(), "notice")
        seen = []
        far_away = (900, 450)
        now = 0
        while game.phase != "approach" and now < 10:
            now = self.run_until(game, now + 0.02, far_away)
            line = game.take_line()
            if line:
                seen.append(line)
        self.assertEqual(seen, ["announce", "3…", "2…", "1…", "go"])
        self.assertTrue(game.started)
        self.assertAlmostEqual(game.deadline - now, ROUND_SECONDS, delta=0.5)

    def test_touching_her_before_go_is_a_foul_that_makes_her_sad_and_curl(self):
        for when in (0.3, 1.0, 3.0, 5.0):          # notice, announcement, countdown
            game = self.game()
            self.run_until(game, when, (900, 450))
            self.run_until(game, when + TAG_HOLD + 0.1, self.on_body, lambda g, n: True)
            self.assertEqual((game.phase, game.result), ("loss", "foul"), when)
            self.assertEqual(game.take_line(), "foul")
            self.assertFalse(game.started)
            self.run_until(game, when + 10, (900, 450))
            self.assertEqual(game.phase, "curl")    # Sad until a pet comforts her.
            self.assertTrue(game.comfort(when + 10))

    def test_a_quick_brush_before_go_is_only_a_warning(self):
        game = self.game()
        self.run_until(game, 3.0, (900, 450))
        game.update(3.02, game.centre, True)
        game.update(3.06, (900, 450), False)
        self.assertEqual(game.take_line(), "not_yet")
        self.assertNotEqual(game.phase, "loss")

    def test_running_away_warns_then_fails(self):
        game = self.game()
        self.run_until(game, START, (900, 450))
        self.run_until(game, START + 1.6, (game.x + 2000, 450))
        self.assertEqual(game.take_line(), "runaway_warn")
        self.run_until(game, START + FAR_FAIL + 0.2, (game.x + 2000, 450))
        self.assertEqual((game.phase, game.result), ("loss", "runaway"))
        game = self.game()
        self.run_until(game, START, (900, 450))
        self.run_until(game, START + FAR_FAIL + 0.2, (900, 450), far=True)   # Another monitor.
        self.assertEqual(game.result, "runaway")

    def test_she_creeps_toward_the_arrow_then_waits_teasingly(self):
        game = self.game()
        hand = lambda g, now: (1250 + 12 * math.sin(now * 4), 450)   # A resting hand, still moving a little.
        self.run_until(game, START, hand)
        before = game.x
        self.run_until(game, START + 3, hand)
        self.assertGreater(game.x, before)            # Approaches to get its attention…
        self.run_until(game, START + 12, hand)
        self.assertIn(game.phase, ("prowl", "approach"))
        self.assertLessEqual(abs(1300 - game.centre[0]), 260)   # …and stops at a teasing distance.

    def test_an_approaching_arrow_gets_a_tell_then_one_escape_and_a_recovery(self):
        game = self.game(seed=3)
        self.run_until(game, START, (900, 450))
        phases = []

        def chase(g, now):
            cx, cy = g.centre
            return (cx + 60, cy)   # Hovers just beside her: always a threat, never on her body.
        now = START
        while now < START + 8:
            now = self.run_until(game, now + 0.02, chase)
            if not phases or phases[-1][0] != game.phase:
                phases.append((game.phase, now))
        names = [p for p, _ in phases]
        self.assertIn("tell", names)
        # Every escape is preceded by a readable tell of 250–350 ms…
        for i, (phase, start) in enumerate(phases):
            if phase in ("sidestep", "duck", "dash") and i and phases[i - 1][0] == "tell":
                self.assertGreaterEqual(start - phases[i - 1][1], TELL[0] - 0.03)
        # …and followed by at least the recovery gap before the next tell.
        tells = [t for p, t in phases if p == "tell"]
        recovers = [t for p, t in phases if p == "recover"]
        for r in recovers:
            nxt = [t for t in tells if t > r]
            if nxt:
                self.assertGreaterEqual(nxt[0] - r, RECOVERY[0] - 0.03)
        self.assertEqual(game.tags, 0)

    def test_three_real_tags_catch_her_and_the_grace_window_prevents_double_counting(self):
        game = self.game(seed=5)
        self.run_until(game, START, (900, 450))
        now = START
        tag_times = []
        while game.phase not in ("caught", "home", "win") and now < START + ROUND_SECONDS:
            before = game.tags
            now = self.run_until(game, now + 0.02, self.on_body, lambda g, n: True)
            if game.tags != before:
                tag_times.append(now)
        self.assertEqual(game.tags, TAGS_TO_WIN)
        self.assertEqual((game.phase, game.result), ("caught", "caught"))
        for a, b in zip(tag_times, tag_times[1:]):
            self.assertGreaterEqual(b - a, TAG_GRACE)
        lines = []
        while game.phase != "done":
            now = self.run_until(game, now + 0.1, (900, 450))
            line = game.take_line()
            if line:
                lines.append(line)
        self.assertAlmostEqual(game.x, 600, delta=1)       # Always back home.

    def test_brushes_do_not_count_and_say_so(self):
        game = self.game()
        self.run_until(game, START + 1, (900, 450))
        game.take_line()
        t = game.last
        game.update(t + 0.02, game.centre, True)
        game.update(t + 0.08, (900, 450), False)          # 60 ms on her: a brush.
        self.assertEqual(game.tags, 0)
        self.assertEqual(game.take_line(), "brush")

    def test_she_wins_by_surviving_the_clock_and_goes_home(self):
        game = self.game()
        self.run_until(game, START + 0.1, (900, 450))

        def wiggle(g, now):  # A player who keeps moving but never reaches her.
            return (g.centre[0] + 400 + 20 * math.sin(now * 3), 450)
        self.run_until(game, START + ROUND_SECONDS + 0.5, wiggle)
        self.assertEqual(game.result, "win")
        self.run_until(game, START + ROUND_SECONDS + 30, (900, 450))
        self.assertEqual(game.phase, "done")
        self.assertAlmostEqual(game.x, 600, delta=1)

    def test_cornered_against_an_edge_she_slips_past_the_arrow(self):
        game = DodgeGame(0, (0, 400), Runway(0, 1500, 400, 110), True, "manual", rng=random.Random(2))
        target, side = game.away_from(game.centre[0] - 50, 60)   # Arrow on her left, wall on her left.
        self.assertGreater(target, game.x)
        target, side = game.away_from(game.centre[0] + 50, 60)   # Arrow on her right: wall blocks.
        self.assertGreater(target, game.centre[0] + 50 - 96)      # She goes past the arrow instead.

    def test_a_still_arrow_ends_the_round_without_a_score(self):
        game = self.game()
        self.run_until(game, START + 0.2, (900, 450))
        self.run_until(game, START + 9, (900, 451))
        self.assertEqual(game.result, "bored")

    def test_neutral_cancel_and_stall(self):
        game = self.game()
        self.run_until(game, START + 1, (900, 450))
        game.cancel(game.last)
        self.assertEqual((game.phase, game.result), ("home", "cancel"))
        game = self.game()
        self.run_until(game, START + 1, (900, 450))
        game.update(game.last + 5, (900, 450))            # Lock screen: called off, no fail.
        self.assertEqual(game.result, "cancel")
        game = self.game()
        game.result = "win"
        game.enter("win", 0)
        game.update(10, (0, 0))                           # A stall during the celebration keeps it.
        self.assertEqual((game.phase, game.result), ("win", "win"))

    def test_reduced_motion_never_travels(self):
        game = self.game(motion=False)
        self.run_until(game, START + 10, lambda g, n: (g.centre[0] + 60, g.centre[1]))
        self.assertEqual(game.x, 600)


if __name__ == "__main__":
    unittest.main()
