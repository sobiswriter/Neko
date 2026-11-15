"""Neko 1.3 restless kitten: levels, movement grammar, the sad curl and paced pets."""
import random
import unittest

from restless import (ACT_SECONDS, ACTS, BODY, CURSOR_GAP, LISTEN_SECONDS, MAX_LEAP, SAD, SAD_GAP, STAGES,
                      RestlessMood)

AREA = (0, 0, 1700, 900)
HOME = (1500, 900)
LEVEL = 300


class RestlessTests(unittest.TestCase):
    def mood(self, seed=1, motion=True, level_seconds=LEVEL):
        return RestlessMood(0, HOME, AREA, motion, random.Random(seed), level_seconds=level_seconds)

    def run_until(self, mood, end, cursor=(400, 700), paused=False, step=0.025, watch=None):
        now = mood.last
        lines = []
        while now < end - 1e-9 and not mood.done:
            now = round(min(end, now + step), 6)
            mood.update(now, cursor, paused)
            line = mood.take_line()
            if line:
                lines.append(line)
            if watch is not None:
                watch(now, mood)
        return now, lines

    def test_acting_uses_her_original_drawings_with_real_lengths(self):
        from animations import CLIPS
        for key, (clip, seconds) in ACTS.items():
            self.assertIn(clip, CLIPS, key)
            self.assertFalse(CLIPS[clip].bank.startswith("v12-"), key)
            expected = seconds if seconds is not None else sum(CLIPS[clip].durations) / 1000
            self.assertAlmostEqual(ACT_SECONDS[key], expected, places=3, msg=key)

    def test_four_levels_every_level_time_and_pets_two_to_five(self):
        self.assertEqual([s[0] for s in STAGES], ["agitated", "pouncy", "demanding", "sad"])
        self.assertEqual([s[1] for s in STAGES], [2, 3, 4, 5])
        mood = self.mood(level_seconds=60)
        seen, now, lines = {}, 0, []
        while mood.stage != SAD and now < 400:
            now, got = self.run_until(mood, now + 0.5)
            lines += got
            seen.setdefault(mood.stage_name, now)
        self.assertEqual(list(seen), ["agitated", "pouncy", "demanding", "sad"])
        for name, expected in (("pouncy", 60), ("demanding", 120), ("sad", 180)):
            self.assertAlmostEqual(seen[name], expected, delta=1)
        for line in ("start", "pouncy", "demanding"):
            self.assertIn(line, lines)
        self.assertNotIn("sad", lines)                   # The sad level speaks once, when she curls up.
        while not mood.curled and now < 600:
            now, got = self.run_until(mood, now + 0.5)
            lines += got
        self.assertEqual(lines.count("sad"), 1)

    def test_movement_grammar_pounce_for_height_run_for_sideways_walk_only_after_a_run(self):
        mood = self.mood(seed=3, level_seconds=40)
        modes = []
        def watch(now, m):
            step = m.step
            if step and step[0] in ("travel", "leap"):
                key = (step[0], step[1][0] if step[0] == "travel" else None, step[2])
                if not modes or modes[-1] != key:
                    modes.append(key)
        cursor = (500, 300)
        self.run_until(mood, 300, cursor, watch=watch)
        kinds = [(k, m) for k, m, _ in modes]
        self.assertIn(("leap", None), kinds)
        self.assertIn(("travel", "run"), kinds)
        self.assertNotIn(("travel", "hop"), kinds)
        for i, (kind, mode) in enumerate(kinds):
            if mode == "walk":
                self.assertEqual(kinds[i - 1], ("travel", "run"), kinds[max(0, i - 3):i + 1])

    def test_route_changes_height_only_by_pounces_and_ends_with_a_cool_down_walk(self):
        mood = self.mood()
        steps = mood.route(400, 100)
        leaps = [data for kind, data in steps if kind == "leap"]
        self.assertGreaterEqual(len(leaps), 6)
        ground = mood.ground
        for x, y in leaps:
            self.assertLessEqual(abs(y - ground), MAX_LEAP)
            ground = y
        self.assertEqual(ground, 100)
        travel = [data for kind, data in steps if kind == "travel"]
        self.assertEqual([mode for mode, _ in travel], ["run", "walk"])
        self.assertEqual(travel[-1][1], 400)
        self.assertEqual(steps[-1], ("act", "stop"))
        self.assertEqual(mood.route(mood.x + 100, mood.ground), [("travel", ("run", mood.x + 100)), ("act", "stop")])

    def test_sad_level_comes_close_to_the_arrow_curls_and_guilt_trips(self):
        mood = self.mood(seed=5)
        mood.stage, mood.stage_since = SAD - 1, -LEVEL
        cursor = (600, 500)
        now, lines = self.run_until(mood, 1, cursor)
        self.assertEqual(mood.stage, SAD)
        while not mood.curled and now < 120:
            now, got = self.run_until(mood, now + 0.25, cursor)
            lines += got
        self.assertTrue(mood.curled)
        gap = abs(mood.x + BODY[0] - cursor[0])
        self.assertLess(gap, CURSOR_GAP)                 # Closer than at the other levels…
        self.assertGreaterEqual(gap, SAD_GAP - 4)        # …but not on top of the arrow.
        self.assertAlmostEqual(mood.y + BODY[1], cursor[1], delta=31)
        self.assertEqual(mood.effect, "sulk")
        self.assertIn("sad", lines)
        x, y = mood.x, mood.y
        now, later = self.run_until(mood, now + 120, cursor)
        self.assertEqual((mood.x, mood.y), (x, y))      # She stays curled.
        self.assertGreaterEqual(later.count("guilt"), 2)
        self.assertFalse(mood.playful)

    def test_curled_pets_count_one_per_line_and_words_go_from_sad_to_happy(self):
        mood = self.mood()
        mood.stage = SAD
        mood.curl(0)
        self.assertEqual(mood.pet(1.0), "progress")
        self.assertEqual(mood.take_line(), "sad_1")
        self.assertEqual(mood.pet(1.5), "wait")          # Too soon: she is still talking.
        self.assertEqual(mood.pets, 1)
        now = 1.0
        for expected in ("sad_2", "sad_3", "sad_4"):
            now += LISTEN_SECONDS + 0.1
            self.run_until(mood, now)
            self.assertEqual(mood.pet(now), "progress")
            self.assertEqual(mood.take_line(), expected)
        self.assertIsNone(mood.effect)                   # The rain cloud cleared along the way.
        now += LISTEN_SECONDS + 0.1
        self.run_until(mood, now)
        self.assertEqual(mood.pet(now), "forgiven")
        self.assertEqual(mood.take_line(), "sad_done")
        self.assertEqual(mood.step[1], "uncurl")        # She gets up from the curl…
        now, _ = self.run_until(mood, now + 60)
        self.assertTrue(mood.done)                        # …and goes home.
        self.assertEqual((round(mood.x), round(mood.y)), HOME)

    def test_pets_calm_her_at_the_lower_levels_then_she_goes_home(self):
        mood = self.mood()
        mood.stage, mood.stage_since = 2, 0          # Demanding: 4 pets.
        mood.x, mood.y, mood.ground = 300, 500, 500
        now = 1.0
        for _ in range(3):
            self.assertEqual(mood.pet(now), "progress")
            self.assertEqual(mood.take_line(), "calm_progress")
            now, _ = self.run_until(mood, now + 2)
        self.assertEqual(mood.pet(now), "forgiven")
        self.assertEqual(mood.take_line(), "calm_done")
        self.assertEqual(mood.effect, "pet")
        now, _ = self.run_until(mood, now + 60)
        self.assertTrue(mood.done)
        self.assertEqual((round(mood.x), round(mood.y)), HOME)

    def test_demanding_comes_to_the_arrow_but_keeps_the_gap(self):
        mood = self.mood(seed=2)
        mood.stage, mood.stage_since = 2, 0
        cursor = (500, 300)
        closest, heights = 10 ** 9, set()
        now = 0
        while now < 60:
            now, _ = self.run_until(mood, now + 0.25, cursor)
            if mood.step[0] in ("rest", "act"):
                closest = min(closest, abs(mood.x + BODY[0] - cursor[0]))
            heights.add(round(mood.y))
        self.assertLess(closest, 400)
        self.assertGreaterEqual(closest, CURSOR_GAP)
        self.assertGreater(len(heights), 2)
        self.assertTrue(all(AREA[1] - 120 <= h <= AREA[3] for h in heights))

    def test_burst_remarks_are_spaced_out(self):
        mood = self.mood(seed=6)
        mood.stage, mood.stage_since = 2, 0
        stamps = []
        now = 0
        while now < 120:
            now, got = self.run_until(mood, now + 0.5, (500, 300))
            stamps += [now for line in got if line in ("jealous", "demand")]
        self.assertTrue(all(b - a >= 13.5 for a, b in zip(stamps, stamps[1:])), stamps)

    def test_excited_moments_ask_for_a_laugh_sometimes(self):
        sounds = 0
        for seed in range(6):
            mood = self.mood(seed=seed)
            mood.stage, mood.stage_since = 1, 0
            now = 0
            while now < 90:
                now, _ = self.run_until(mood, now + 0.5)
                sounds += mood.take_sound() == "laugh"
        self.assertGreater(sounds, 0)

    def test_a_pet_pauses_escalation(self):
        mood = self.mood()
        mood.stage, mood.stage_since = 1, 0
        mood.pet(10)
        self.run_until(mood, 10 + LEVEL - 5)
        self.assertEqual(mood.stage_name, "pouncy")

    def test_paused_while_a_button_is_held_or_typing(self):
        mood = self.mood()
        mood.stage, mood.stage_since = 1, 0
        self.run_until(mood, 30)
        x, stage_since = mood.x, mood.stage_since
        self.run_until(mood, 60, paused=True)
        self.assertEqual(mood.x, x)
        self.assertAlmostEqual(mood.stage_since, stage_since + 30, delta=0.1)

    def test_stepping_away_sends_her_home_quietly_even_from_the_curl(self):
        for curled in (False, True):
            mood = self.mood()
            mood.x, mood.y, mood.ground = 200, 600, 600
            if curled:
                mood.stage = SAD
                mood.curl(0)
            mood.go_home(1)
            self.assertIsNone(mood.take_line())
            if curled:
                self.assertEqual(mood.step[1], "uncurl")
            self.run_until(mood, 60)
            self.assertTrue(mood.done)
            self.assertEqual((round(mood.x), round(mood.y)), HOME)

    def test_carrying_a_curled_kitten_keeps_her_sad(self):
        mood = self.mood()
        mood.stage = SAD
        mood.curl(0)
        mood.moved(700, 400, 5)
        self.assertTrue(mood.curled)
        self.assertEqual((mood.x, mood.y), (700, 400))

    def test_game_counts_as_attention(self):
        mood = self.mood()
        mood.stage = 2
        mood.calm_one_stage(5)
        self.assertEqual(mood.stage_name, "pouncy")
        mood.stage = 0
        mood.calm_one_stage(6)
        self.assertTrue(mood.forgiven)

    def test_reduced_motion_never_travels_or_leaps(self):
        mood = self.mood(motion=False)
        mood.stage, mood.stage_since = 2, 0
        xs = set()
        now = 0
        while now < 40:
            now, _ = self.run_until(mood, now + 0.5, (500, 300))
            if mood.step[0] in ("travel", "leap"):
                xs.add(mood.step[0])
        self.assertFalse(xs)


if __name__ == "__main__":
    unittest.main()
