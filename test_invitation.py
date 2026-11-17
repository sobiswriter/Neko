import unittest
from games import GameTimer, Runway


class InvitationTests(unittest.TestCase):
    def test_entry_at_expiry_retains_the_observed_outside_approach(self):
        timer = GameTimer(0)
        timer.tick(89.5, True, False)
        timer.tick(89.8, True, False)
        self.assertIsNone(timer.tick(90.01, True, True))
        self.assertEqual(timer.tick(90.3, True, True), "automatic")

    def test_diagnostic_wait_reasons_change_without_poll_spam(self):
        events = []
        timer = GameTimer(0, record=lambda action, detail: events.append((action, detail)))
        for now in (90, 91, 92):
            timer.tick(now, False, blocked_reason="sleeping")
        self.assertEqual(events.count(("waiting", "sleeping")), 1)
        self.assertEqual(events.count(("queued", "automatic")), 1)
        timer.tick(93, True, False)
        self.assertEqual(timer.reason, "fresh side entry")

    def test_fresh_entry_can_wait_for_an_idle_animation_to_finish(self):
        timer = GameTimer(0)
        timer.tick(100, True, False, can_start=False)
        timer.tick(100.2, True, True, can_start=False)
        self.assertIsNone(timer.tick(100.5, True, True, can_start=False))
        self.assertEqual(timer.tick(101, True, True), "automatic")

    def test_short_outside_flicker_does_not_mature_after_entry(self):
        timer = GameTimer(0)
        timer.tick(100, True, False)
        timer.tick(100.1, True, True)
        self.assertIsNone(timer.tick(101, True, True))
        timer.tick(102, True, False)
        timer.tick(102.2, True, True)
        self.assertEqual(timer.tick(102.5, True, True), "automatic")

    def test_inside_at_expiry_must_leave_then_make_a_fresh_stable_entry(self):
        t = GameTimer(0)
        for now in (89, 90, 91, 300):
            self.assertIsNone(t.tick(now, True, True))
        self.assertIsNone(t.tick(301, True, False))
        self.assertIsNone(t.tick(301.2, True, True))
        self.assertIsNone(t.tick(301.44, True, True))
        self.assertEqual(t.tick(301.46, True, True), "automatic")
        self.assertIsNone(t.tick(9000, True, True))

    def test_nap_or_care_discards_entry_and_keeps_one_intent(self):
        t = GameTimer(0)
        for now in (90, 1000, 5000):
            t.tick(now, False, False)
        self.assertEqual(t.pending, "automatic")
        self.assertIsNone(t.tick(5001, True, True))
        t.tick(5002, True, False)
        t.tick(5002.2, True, True)
        t.tick(5002.3, False, True)
        self.assertIsNone(t.tick(5003, True, True))
        t.tick(5004, True, False)
        t.tick(5004.2, True, True)
        self.assertEqual(t.tick(5004.5, True, True), "automatic")

    def test_manual_bypasses_entry_and_countdown_abort_keeps_original_due(self):
        t = GameTimer(0)
        t.request(2, manual=True)
        self.assertEqual(t.tick(3, True), "manual")
        t.finish(4, started=False)
        self.assertEqual(t.due, 90)
        t.request(5, manual=True)
        t.tick(6, True)
        t.finish(50, started=True)
        self.assertEqual(t.due, 140)

    def test_side_zones_exclude_canvas_and_care_margin_and_other_heights(self):
        r = Runway(0, 1200, 400, 110)
        for p in ((350, 450), (850, 450)):
            self.assertTrue(r.invites(p, 500), p)
        for p in ((490, 450), (550, 450), (710, 450), (850, 100), (850, 800)):
            self.assertFalse(r.invites(p, 500), p)
        small = Runway(0, 400, 400, 110)
        self.assertFalse(small.invites((100, 450), 200))

    def test_disable_and_interval_edits_clear_entry_qualification(self):
        t = GameTimer(0)
        t.tick(90, True, False)
        t.tick(90.2, True, True)
        t.configure(90.3, False, 120)
        self.assertIsNone(t.tick(999, True, True))
        t.configure(1000, True, 30)
        self.assertIsNone(t.tick(1030, True, True))

    def test_interval_edit_during_abandoned_countdown_keeps_new_cooldown(self):
        t = GameTimer(0)
        t.request(1, manual=True)
        t.tick(2, True)
        t.configure(3, True, 120)
        t.finish(4, started=False)
        self.assertEqual(t.due, 123)


if __name__ == "__main__":
    unittest.main()
