"""Catch the Cursor's larger play area: she jumps up, hops down a little, and climbs home."""
import unittest

from games import DECLARE_SECONDS, MAX_DROP, MAX_LIFT, REACH_LOW, CursorGame, Runway

START = DECLARE_SECONDS + 0.8 + 3 + 0.4


class CatchReachTests(unittest.TestCase):
    def game(self, drop=MAX_DROP, lift=MAX_LIFT):
        return CursorGame(0, (500, 300), Runway(0, 1200, 300, lift, drop=drop))

    def step(self, game, end, cursor, contact=lambda g: False):
        trace = []
        while game.last < end - 1e-6:
            now = round(game.last + 0.02, 6)
            game.update(now, cursor(game) if callable(cursor) else cursor, contact(game))
            trace.append((now, game.phase, round(game.x), round(game.y), round(game.ground)))
            if game.phase == "done":
                break
        return trace

    def test_play_area_reaches_higher_and_lower_than_before(self):
        runway = Runway(0, 1200, 300, MAX_LIFT, drop=MAX_DROP)
        self.assertGreater(MAX_LIFT, 110)
        self.assertTrue(runway.contains((700, 300 + 80 - MAX_LIFT + 5)))     # High, up to the larger lift.
        self.assertTrue(runway.contains((700, 300 + REACH_LOW + MAX_DROP - 5)))  # Low: below her feet.
        self.assertFalse(runway.contains((700, 300 + REACH_LOW + MAX_DROP + 20)))
        flat = Runway(0, 1200, 300, MAX_LIFT)
        self.assertFalse(flat.contains((700, 300 + REACH_LOW + 30)))          # No room below: no drop.

    def test_a_low_arrow_makes_her_hop_down_then_she_climbs_back_home(self):
        game = self.game()
        low = (740, 300 + REACH_LOW + 50)
        self.step(game, START, low)
        trace = self.step(game, START + 6, low)
        grounds = {g for *_, g in trace}
        self.assertGreater(max(grounds), 300)                  # She hopped down a little…
        self.assertLessEqual(max(grounds), 300 + MAX_DROP)     # …but only within the play area.
        game.cancel(game.last)
        trace = self.step(game, game.last + 15, (740, 300))
        self.assertEqual(game.phase, "done")
        self.assertEqual((round(game.x), round(game.y), game.ground), (500, 300, 300))
        # She never teleports between grounds: each change happens during a hop.
        for (_, phase, _, y, ground), (_, phase2, _, y2, ground2) in zip(trace, trace[1:]):
            if ground2 != ground:
                self.assertEqual(phase, "jump")

    def test_she_can_pounce_from_the_lower_ground_back_up_to_a_high_arrow(self):
        game = self.game()
        game.ground = game.y = 360
        game.enter("run", 0)
        game.started, game.deadline = True, 999
        solution = game.runway.jump(game.x, (650, 300 + 40), -1, 360, 300)
        self.assertIsNotNone(solution)
        end, height = solution
        self.assertGreater(height, 0)
        self.assertGreaterEqual((360 + 300) / 2 - height, 300 - MAX_LIFT)   # Arc stays inside the area.

    def test_wandering_off_protests_then_forfeits_into_the_sulk(self):
        game = self.game()
        self.step(game, START + 0.2, (740, 330))
        lines = []
        end = START + 6
        while game.last < end:
            self.step(game, game.last + 0.1, (2000, -400))
            line = game.take_line()
            if line:
                lines.append(line)
        self.assertTrue(any(line.startswith("protest_") for line in lines))
        self.assertEqual(game.result, "loss")
        self.step(game, game.last + 10, (2000, -400))
        self.assertEqual(game.phase, "curl")


if __name__ == "__main__":
    unittest.main()
