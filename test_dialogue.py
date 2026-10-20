import random
import unittest

from dialogue import LINES, OfflineDialogue


class DialogueTests(unittest.TestCase):
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
