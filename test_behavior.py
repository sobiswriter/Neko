import random
import unittest

from behavior import Companion, NekoState


class CompanionTests(unittest.TestCase):
    def setUp(self):
        self.pet = Companion(0, random.Random(4))

    def test_leaving_her_alone_never_creates_a_need_for_attention(self):
        for now in range(0, 3600, 5):
            self.pet.tick(now, idle_seconds=now)
        self.assertEqual(self.pet.state, NekoState.SLEEPING)
        self.assertEqual(self.pet.naps, 1)

    def test_activity_wakes_her_silently(self):
        self.pet.tick(200, idle_seconds=200)
        self.assertEqual(self.pet.tick(201, idle_seconds=0), "wake")
        self.assertEqual(self.pet.state, NekoState.WAKING)

    def test_typing_gets_a_brief_response_then_a_cooldown(self):
        self.assertEqual(self.pet.tick(10, 0, keyboard_events=8), "typing")
        self.assertEqual(self.pet.state, NekoState.TYPING)
        self.pet.tick(14, 0, keyboard_events=8)
        self.assertNotEqual(self.pet.tick(15, 0, keyboard_events=8), "typing")

    def test_window_events_do_not_interrupt_grooming(self):
        self.pet.pose(NekoState.GROOMING, 10, 3)
        self.assertIsNone(self.pet.tick(11, 0, window_event="open"))
        self.assertEqual(self.pet.state, NekoState.GROOMING)

    def test_closed_window_gets_a_little_blink(self):
        self.assertEqual(self.pet.tick(20, 0, window_event="close"), "curious")
        self.assertEqual(self.pet.state, NekoState.PEEKING)

    def test_she_yawns_before_a_nap(self):
        self.pet.next_idle = 10000
        self.pet.tick(100, 100)
        self.assertEqual(self.pet.state, NekoState.YAWNING)

    def test_returning_after_a_long_nap_does_not_release_overdue_chatter(self):
        self.pet.tick(200, 200)
        self.pet.next_comment = 100
        self.pet.tick(1000, 0)
        self.assertGreaterEqual(self.pet.next_comment, 1240)

    def test_focus_mode_has_no_unsolicited_comments(self):
        self.pet.next_comment = 0
        actions = [self.pet.tick(t, 0, quiet=True) for t in range(1, 2000)]
        self.assertNotIn("comment", actions)

    def test_comments_have_a_long_cooldown(self):
        self.pet.next_idle = 99999
        self.pet.next_comment = 10
        self.assertEqual(self.pet.tick(10, 0), "comment")
        self.assertGreaterEqual(self.pet.next_comment, 10 + 720)
        self.assertIsNone(self.pet.tick(11, 0))

    def test_pet_is_a_temporary_pose_and_delays_chatter(self):
        self.pet.pet(50)
        self.assertEqual(self.pet.pets, 1)
        self.assertEqual(self.pet.state, NekoState.HAPPY)
        self.pet.tick(54, 0)
        self.assertEqual(self.pet.state, NekoState.IDLE)
        self.assertGreaterEqual(self.pet.next_comment, 290)

    def test_cursor_curiosity_is_throttled(self):
        self.assertEqual(self.pet.tick(50, 0, cursor_near=True), "curious")
        self.pet.tick(54, 0)
        self.assertIsNone(self.pet.tick(55, 0, cursor_near=True))

    def test_window_switches_do_not_interrupt_a_nap_or_pet(self):
        self.pet.pet(50)
        self.assertIsNone(self.pet.tick(51, 0, window_changed=True))
        self.pet.tick(200, 200)
        self.assertIsNone(self.pet.tick(201, 201, window_changed=True))
        self.assertEqual(self.pet.state, NekoState.SLEEPING)


if __name__ == "__main__":
    unittest.main()
