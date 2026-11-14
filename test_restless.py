import random
import unittest

from restless import ACT_SECONDS, CURSOR_GAP, BODY, LEAP_SECONDS, RestlessMood, STAGES

AREA = (0, 0, 1700, 900)
HOME = (1500, 900)


class RestlessTests(unittest.TestCase):
    def mood(self, seed=1, motion=True):
        return RestlessMood(0, HOME, AREA, motion, random.Random(seed))

    def run_until(self, mood, end, cursor=(400, 700), paused=False, step=0.025):
        now = mood.last
        lines = []
        while now < end - 1e-9 and not mood.done:
            now = round(min(end, now + step), 6)
            mood.update(now, cursor, paused)
            line = mood.take_line()
            if line:
                lines.append(line)
        return now, lines

    def test_clip_lengths_match_the_drawn_acting(self):
        from animations import CLIPS
        names = {"sigh": "restless_sigh", "jealous": "restless_jealous", "demand": "restless_demand",
                 "forgive": "restless_forgive", "calm": "restless_calm", "stop": "roam_stop", "turn": "roam_turn",
                 "ready": "roam_ready"}
        for key, clip in names.items():
            self.assertAlmostEqual(sum(CLIPS[clip].durations) / 1000, ACT_SECONDS[key], places=2, msg=key)
        for way in ("up", "down"):
            self.assertAlmostEqual(sum(CLIPS[f"roam_leap_{way}"].durations) / 1000, LEAP_SECONDS[way], places=2)

    def test_escalates_through_every_stage_then_curls_until_petted(self):
        mood = self.mood()
        stages = []
        now, lines = 0, []
        while mood.stage_name != "sulk" and now < 2000:
            now, got = self.run_until(mood, now + 1)
            lines += got
            if not stages or stages[-1] != mood.stage_name:
                stages.append(mood.stage_name)
        self.assertEqual(stages, ["restless", "pouncy", "jealous", "demanding", "sulk"])
        self.assertIn("start", lines)
        for line in ("pouncy", "jealous", "demanding", "sulk"):
            self.assertIn(line, lines)
        x, y = mood.x, mood.y
        self.run_until(mood, now + 600)
        self.assertEqual((mood.x, mood.y, mood.step[0]), (x, y, "sulk"))   # Stays curled.
        self.assertEqual(mood.effect, "sulk")
        self.assertEqual(mood.pets_needed, 5)

    def test_she_pounces_stops_talks_relaxes_and_gets_more_agitated(self):
        mood = self.mood(seed=4)
        mood.stage, mood.stage_since = 1, 0          # Pouncy.
        kinds = []
        now = 0
        while now < 110:
            now, _ = self.run_until(mood, now + 0.25)
            kind = mood.step[0]
            if not kinds or kinds[-1] != kind:
                kinds.append(kind)
        self.assertIn("travel", kinds)
        self.assertIn("rest", kinds)
        self.assertIn("act", kinds)
        rest_pouncy = STAGES[1][3]
        rest_demanding = STAGES[3][3]
        self.assertLess(rest_demanding[1], rest_pouncy[0])   # Shorter pauses as she gets agitated.

    def test_jealous_bursts_head_toward_the_arrow_but_keep_the_gap_and_change_height(self):
        mood = self.mood(seed=2)
        mood.stage, mood.stage_since = 2, 0          # Jealous.
        cursor = (500, 300)
        closest = 10 ** 9
        heights = set()
        now = 0
        while now < 60:
            now, _ = self.run_until(mood, now + 0.25, cursor)
            if mood.step[0] in ("rest", "act"):
                closest = min(closest, abs(mood.x + BODY[0] - cursor[0]))
            heights.add(round(mood.y))
        self.assertLess(closest, 400)                 # She came over to the arrow's side…
        self.assertGreaterEqual(closest, CURSOR_GAP)   # …but never rests on top of it.
        self.assertGreater(len(heights), 2)           # And leapt up toward its height.
        self.assertTrue(all(AREA[1] - 30 <= h <= AREA[3] for h in heights))

    def test_big_height_changes_take_several_kitten_sized_leaps(self):
        from restless import MAX_LEAP
        mood = self.mood()
        steps = mood.route(400, 100)
        leaps = [data for kind, data in steps if kind == "leap"]
        self.assertGreaterEqual(len(leaps), 4)
        ground = mood.ground
        for x, y in leaps:
            self.assertLessEqual(abs(y - ground), MAX_LEAP)
            ground = y
        self.assertEqual(ground, 100)

    def test_pets_calm_her_stage_by_stage_then_she_forgives_and_goes_home(self):
        mood = self.mood()
        mood.stage, mood.stage_since = 3, 0          # Demanding: 4 pets.
        mood.x, mood.y, mood.ground = 300, 500, 500
        now = 1.0
        for i in range(3):
            self.assertEqual(mood.pet(now), "progress")
            self.assertEqual(mood.take_line(), "calm_progress")
            now, _ = self.run_until(mood, now + 2)
        self.assertEqual(mood.pet(now), "forgiven")
        self.assertEqual(mood.take_line(), "calm_done")
        self.assertEqual(mood.effect, "pet")
        now, _ = self.run_until(mood, now + 60)
        self.assertTrue(mood.done)
        self.assertEqual((round(mood.x), round(mood.y)), HOME)

    def test_a_pet_pauses_escalation(self):
        mood = self.mood()
        mood.stage, mood.stage_since = 1, 0
        mood.pet(10)
        self.run_until(mood, 10 + STAGES[1][1] - 5)
        self.assertEqual(mood.stage_name, "pouncy")

    def test_paused_while_a_button_is_held_or_typing(self):
        mood = self.mood()
        mood.stage, mood.stage_since = 1, 0
        self.run_until(mood, 30)
        x, stage_since = mood.x, mood.stage_since
        self.run_until(mood, 60, paused=True)
        self.assertEqual(mood.x, x)
        self.assertAlmostEqual(mood.stage_since, stage_since + 30, delta=0.1)

    def test_stepping_away_sends_her_home_quietly(self):
        mood = self.mood()
        mood.x, mood.y, mood.ground = 200, 600, 600
        mood.go_home(1)
        self.assertIsNone(mood.take_line())
        self.run_until(mood, 60)
        self.assertTrue(mood.done)
        self.assertEqual((round(mood.x), round(mood.y)), HOME)

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
