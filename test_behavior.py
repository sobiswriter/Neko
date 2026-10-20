import random
import unittest

from behavior import Companion, NekoState, PET_STATES, IDLE_STATES


class CompanionTests(unittest.TestCase):
    def setUp(self):
        self.pet = Companion(0, random.Random(4))

    def test_sleep_starts_with_a_transition_and_never_wakes_on_a_timer(self):
        self.assertEqual(self.pet.tick(180, 180), "sleep")
        self.assertEqual(self.pet.state, NekoState.FALLING_ASLEEP)
        self.assertEqual(self.pet.tick(183, 0), "settled")
        self.assertIsNone(self.pet.tick(10000, 0, keyboard_events=20, window_changed=True))
        self.assertEqual(self.pet.state, NekoState.SLEEPING)
        self.assertEqual(self.pet.naps, 1)

    def test_only_petting_wakes_her_and_repeated_pets_finish_the_wake_transition(self):
        self.pet.tick(200, idle_seconds=200)
        self.assertIsNone(self.pet.tick(201, 0, keyboard_events=20, window_event="open"))
        self.pet.tick(203, 0)
        self.assertEqual(self.pet.state, NekoState.SLEEPING)
        self.pet.pet(204)
        self.assertEqual(self.pet.state, NekoState.WAKING)
        until = self.pet.pose_until
        self.pet.pet(204.5)
        self.assertEqual(self.pet.pose_until, until)
        self.pet.tick(205, 1000)
        self.assertEqual(self.pet.state, NekoState.WAKING)
        self.assertEqual(self.pet.tick(until, 0), "idle")

    def test_sleep_deadline_can_interrupt_another_animation(self):
        self.pet.pose(NekoState.GROOMING, 179, 6)
        self.assertEqual(self.pet.tick(180, 180), "sleep")

    def test_app_context_selects_a_matching_animation_and_line_kind(self):
        self.assertEqual(self.pet.tick(10, 0, window_event="open", app_kind="music"), "curious")
        self.assertEqual(self.pet.reaction_kind, "music")
        self.assertEqual(self.pet.state, NekoState.TAIL_SWISH)

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
        self.pet.tick(203, 203)
        self.pet.next_comment = 100
        self.pet.pet(1000)
        self.assertGreaterEqual(self.pet.next_comment, 1015)

    def test_focus_mode_has_no_unsolicited_comments(self):
        self.pet.next_comment = 0
        actions = [self.pet.tick(t, 0, quiet=True) for t in range(1, 2000)]
        self.assertNotIn("comment", actions)

    def test_comments_use_the_configured_cooldown(self):
        self.pet.next_idle = 99999
        self.pet.next_comment = 10
        self.assertEqual(self.pet.tick(10, 0), "comment")
        self.assertGreaterEqual(self.pet.next_comment, 10 + self.pet.chatter_seconds * 0.8)
        self.assertIsNone(self.pet.tick(11, 0))

    def test_pet_is_a_temporary_pose_and_delays_chatter(self):
        self.pet.pet(50)
        self.assertEqual(self.pet.pets, 1)
        self.assertIn(self.pet.state, PET_STATES)
        self.pet.tick(56, 0)
        self.assertEqual(self.pet.state, NekoState.IDLE)
        self.assertGreaterEqual(self.pet.next_comment, 65)

    def test_sleep_delay_is_adjustable(self):
        pet = Companion(0, sleep_seconds=45)
        pet.tick(44, 44)
        self.assertNotEqual(pet.state, NekoState.SLEEPING)
        self.assertEqual(pet.tick(45, 45), "sleep")

    def test_window_event_waits_for_current_animation(self):
        self.pet.pose(NekoState.GROOMING, 10, 3)
        self.pet.tick(11, 0, window_event="open")
        self.pet.tick(13, 0)
        self.assertEqual(self.pet.tick(13.5, 0), "curious")
        self.assertEqual(self.pet.reaction_kind, "open")

    def test_old_window_events_expire(self):
        self.pet.pose(NekoState.HAPPY, 10, 8)
        self.pet.tick(11, 0, window_event="close")
        self.pet.tick(18, 0)
        self.assertNotEqual(self.pet.tick(18.5, 0), "curious")

    def test_pet_and_idle_choices_do_not_repeat_consecutively(self):
        previous = None
        seen = set()
        for now in range(0, 500, 5):
            self.pet.pet(now)
            self.assertNotEqual(previous, self.pet.state)
            seen.add(self.pet.state)
            previous = self.pet.state
        self.assertEqual(seen, set(PET_STATES))
        seen = set()
        for now in range(1000, 3000, 5):
            action = self.pet.tick(now, 0, quiet=True)
            if action == "fidget":
                seen.add(self.pet.state)
        self.assertEqual(seen, set(IDLE_STATES))

    def test_pet_rotation_shows_every_response_before_repeating(self):
        for cycle in range(4):
            seen = set()
            for index in range(len(PET_STATES)):
                self.pet.pet((cycle * len(PET_STATES) + index) * 10)
                seen.add(self.pet.state)
            self.assertEqual(seen, set(PET_STATES))

    def test_cursor_curiosity_is_throttled(self):
        self.assertEqual(self.pet.tick(50, 0, cursor_near=True), "curious")
        self.pet.tick(54, 0)
        self.assertIsNone(self.pet.tick(55, 0, cursor_near=True))

    def test_window_switches_do_not_interrupt_a_nap_or_pet(self):
        self.pet.pet(50)
        self.assertIsNone(self.pet.tick(51, 0, window_changed=True))
        self.pet.tick(200, 200)
        self.assertIsNone(self.pet.tick(201, 201, window_changed=True))
        self.pet.tick(203, 203)
        self.assertEqual(self.pet.state, NekoState.SLEEPING)


if __name__ == "__main__":
    unittest.main()
