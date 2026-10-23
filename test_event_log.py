import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from event_log import EventLog


class EventLogTests(unittest.TestCase):
    def test_recent_events_persist_filter_and_rotate_with_bounded_memory(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "events.jsonl"
            journal = EventLog(path, limit=3, max_bytes=250)
            for i in range(12):
                journal.add("Thought" if i % 2 else "Game", "shown", str(i))
            self.assertEqual(len(journal.entries), 3)
            self.assertTrue(path.with_suffix(".previous.jsonl").exists())
            loaded = EventLog(path)
            self.assertEqual(loaded.entries[-1]["detail"], "11")
            self.assertNotIn("[Game]", journal.text("Thought"))
            self.assertLess(path.stat().st_size, 500)

    def test_corrupt_rows_are_ignored_and_actual_repeated_actions_are_retained(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "events.jsonl"
            path.write_text('broken\n42\n{"time": 12}\n', encoding="utf-8")
            journal = EventLog(path)
            journal.add("Game", "waiting", "sleeping", changed=True)
            journal.add("Game", "waiting", "sleeping", changed=True)
            journal.add("Care", "pet", "same")
            journal.add("Care", "pet", "same")
            self.assertEqual(len(journal.entries), 3)

    def test_disk_error_keeps_the_visible_log_and_recovers(self):
        with tempfile.TemporaryDirectory() as folder:
            journal = EventLog(Path(folder) / "events.jsonl")
            with patch.object(Path, "open", side_effect=OSError("disk unavailable")):
                journal.add("Idle", "state", "sniff")
            self.assertIn("disk unavailable", journal.error)
            self.assertIn("sniff", journal.text())
            journal.add("Idle", "state", "idle")
            self.assertEqual(journal.error, "")
            self.assertEqual(json.loads(journal.path.read_text())["detail"], "idle")
