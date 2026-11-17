import random
import unittest

from dialogue import LINES, OfflineDialogue


class DialogueTests(unittest.TestCase):
    def test_every_idle_has_its_own_playful_line_bank(self):
        for kind in ("tail", "groom", "loaf", "yawn", "stretch", "ears", "sniff", "peek",
                     "look_left", "look_right", "tail_chase", "tail_catch"):
            self.assertIn(kind, LINES)
            self.assertGreaterEqual(len(LINES[kind]), 4)
        self.assertIn("Look at meeee!", LINES["tail_chase"])
        self.assertIn("Round.. around... around...", LINES["tail_chase"])

    def test_library_is_large_short_and_has_no_duplicate_lines(self):
        lines = [line for bank in LINES.values() for line in bank]
        self.assertGreaterEqual(len(lines), 200)
        self.assertEqual(len(lines), len(set(lines)))
        self.assertTrue(all(len(line) <= 110 for line in lines))

    def test_each_bank_is_exhausted_before_repeating(self):
        dialogue = OfflineDialogue(random.Random(4))
        for kind, lines in LINES.items():
            picked = [dialogue.pick(kind) for _ in lines]
            self.assertEqual(set(picked), set(lines))

    def test_a_shown_line_waits_out_its_cooldown_and_small_groups_go_quiet(self):
        from dialogue import LINE_COOLDOWN
        clock = [0.0]
        dialogue = OfflineDialogue(random.Random(2), clock=lambda: clock[0])
        shown = {}
        for kind in LINES:
            for _ in range(len(LINES[kind]) + 3):
                clock[0] += 1
                line = dialogue.pick(kind)
                if line is None:
                    continue
                self.assertTrue(clock[0] - shown.get(line, -LINE_COOLDOWN) >= LINE_COOLDOWN, (kind, line))
                dialogue.said(line)
                shown[line] = clock[0]
        self.assertIsNone(dialogue.pick("restless_carried"))   # All cooling: silence, not a repeat.
        clock[0] += LINE_COOLDOWN
        self.assertIn(dialogue.pick("restless_carried"), LINES["restless_carried"])

    def test_lines_said_before_a_relaunch_are_still_cooling(self):
        clock = [50.0]
        line = LINES["restless_away"][0]
        dialogue = OfflineDialogue(random.Random(1), history=[line], clock=lambda: clock[0])
        self.assertTrue(dialogue.cooling(line))
        self.assertTrue(all(dialogue.pick("restless_away") != line for _ in range(len(LINES["restless_away"]) - 1)))

    def test_typing_has_real_local_questions(self):
        self.assertIn("whatcha typing?", LINES["typing"])
        self.assertIn(OfflineDialogue().pick("missing-context"), LINES["idle"])

    def test_play_lines_never_repeat_at_a_bank_boundary(self):
        dialogue = OfflineDialogue(random.Random(8))
        for kind in (k for k in LINES if k.startswith("game_")):
            previous = None
            for _ in range(len(LINES[kind]) * 4):
                line = dialogue.pick(kind)
                self.assertNotEqual(line, previous, kind)
                previous = line
                for other in ("idle", "typing", "hello", "groom", "ears", "loaf", "peek"):
                    dialogue.pick(other)
