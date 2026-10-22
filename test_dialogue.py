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
