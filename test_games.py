import unittest
from games import CursorGame, GameTimer, Runway


class GameTests(unittest.TestCase):
    def test_timer_defaults_coalesces_promotes_and_restarts_from_completion(self):
        timer = GameTimer(0)
        self.assertIsNone(timer.tick(89.99, True))
        self.assertIsNone(timer.tick(9000, False))
        self.assertEqual(timer.pending, "automatic")
        timer.request(9001, manual=True)
        self.assertEqual(timer.tick(9002, True), "manual")
        self.assertIsNone(timer.tick(9003, True))
        timer.reset(9010)
        self.assertEqual(timer.due, 9100)
        timer.configure(9011, False, 1)
        self.assertEqual(timer.interval, 30)
        self.assertIsNone(timer.tick(99999, True))

    def test_disable_removes_auto_but_keeps_manual(self):
        timer = GameTimer(0)
        timer.tick(91, False)
        timer.configure(92, False, 90)
        self.assertIsNone(timer.pending)
        timer.request(93, manual=True)
        timer.configure(94, False, 90)
        self.assertEqual(timer.tick(95, True), "manual")

    def game(self):
        return CursorGame(0, (400, 300), Runway(0, 1000, 300, 110))

    def step(self, game, end, cursor=(450, 330)):
        while game.last < end - .00001:
            game.update(min(end, round(game.last + .02, 6)), cursor)

    def test_jump_geometry_and_contact_wins_at_deadline(self):
        game = self.game()
        game.phase, game.since, game.deadline = "jump", 0, .32
        game.start_x, game.end_x, game.height = 400, 500, 60
        self.step(game, .30)
        game.update(.32, (450, 330), contact=True)
        self.assertEqual(game.result, "win")
        self.assertAlmostEqual(game.y, 240)
        self.step(game, .66)
        self.assertEqual(game.phase, "win")
        self.assertEqual(game.y, 300)

    def test_no_rectangular_or_repeated_catch_and_cancel_lands(self):
        game = self.game()
        game.phase, game.since = "jump", 0
        game.start_x, game.end_x, game.height = 400, 500, 80
        self.step(game, .2)
        game.cancel(.2)
        self.assertEqual(game.phase, "jump")
        self.step(game, .66)
        self.assertEqual(game.phase, "home")
        self.assertEqual(game.result, "cancel")
        self.assertEqual(game.y, 300)
        self.step(game, 2)
        self.assertEqual(game.phase, "done")
        self.assertEqual(game.x, 400)

    def test_loss_curl_is_persistent_and_pet_comfort_is_single(self):
        game = self.game()
        self.step(game, 8, (2000, -100))
        self.assertEqual(game.phase, "curl")
        self.step(game, 60, (2000, -100))
        self.assertEqual(game.phase, "curl")
        self.assertTrue(game.comfort(60))
        self.assertFalse(game.comfort(60.1))
        self.step(game, 62.1)
        self.assertEqual(game.phase, "done")

    def test_reentry_resets_continuous_outside_timer(self):
        game = self.game()
        self.step(game, 3, (2000, -100))
        self.step(game, 3.5, (450, 330))
        self.assertIsNone(game.outside)
        self.step(game, 5, (2000, -100))
        self.assertIsNone(game.result)

    def test_stall_cancels_instead_of_scoring_or_punishing(self):
        game = self.game()
        game.update(30, (450, 330), contact=True)
        self.assertEqual(game.result, "cancel")
        self.assertEqual(game.y, 300)

    def test_grounded_baseline_and_full_canvas_limits(self):
        game = self.game()
        self.step(game, 4, (950, 500))
        self.assertEqual(game.y, 300)
        self.assertTrue(0 <= game.x <= 1000)
        for x in range(0, 1001, 25):
            for target in ((x + 54, 258), (x + 137, 368), (-100, 0)):
                for direction in (-1, 1):
                    solution = game.runway.jump(x, target, direction)
                    if solution:
                        end, height = solution
                        self.assertTrue(0 <= end <= 1000)
                        self.assertTrue(0 <= height <= 110)
                        candidates = []
                        for fraction, paw in ((.5, game.runway.paw), (.8, (59, 124))):
                            px = paw[0] if direction < 0 else 191 - paw[0]
                            candidates.append(abs(x + (end - x) * fraction + px - target[0]) < .001
                                              and abs(300 - 4 * height * fraction * (1 - fraction) + paw[1] - target[1]) < .001)
                        self.assertTrue(any(candidates))


if __name__ == "__main__":
    unittest.main()
