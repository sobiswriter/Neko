import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from event_log import EventLog


class EventLogTests(unittest.TestCase):
    def test_only_latest_50_events_remain_in_memory_and_on_disk(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "events.jsonl"
            journal = EventLog(path)
            for i in range(120):
                journal.add("Thought" if i % 2 else "Game", "shown", str(i))
            self.assertEqual([e["detail"] for e in journal.entries], [str(i) for i in range(70, 120)])
            self.assertEqual([json.loads(line) for line in path.read_text().splitlines()], list(journal.entries))
            self.assertFalse(path.with_suffix(".previous.jsonl").exists())
            loaded = EventLog(path)
            self.assertEqual(list(loaded.entries), list(journal.entries))
            self.assertNotIn("[Game]", journal.text("Thought"))

    def test_startup_trims_legacy_history_and_deletes_rotated_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "events.jsonl"
            rows = [{"time": "2026-10-23", "category": "Idle", "action": "state", "detail": str(i)} for i in range(80)]
            path.write_text("\n".join(json.dumps(row) for row in rows) + '\nbroken\n42\n', encoding="utf-8")
            path.with_suffix(".previous.jsonl").write_text("old history", encoding="utf-8")
            journal = EventLog(path)
            self.assertEqual(list(journal.entries), rows[-50:])
            self.assertEqual([json.loads(line) for line in path.read_text().splitlines()], rows[-50:])
            self.assertFalse(path.with_suffix(".previous.jsonl").exists())

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
            journal.add("Idle", "state", "before failure")
            before = journal.path.read_text()
            with patch.object(Path, "replace", side_effect=OSError("disk unavailable")):
                journal.add("Idle", "state", "sniff")
            self.assertIn("disk unavailable", journal.error)
            self.assertIn("sniff", journal.text())
            self.assertEqual(journal.path.read_text(), before)
            journal.add("Idle", "state", "idle")
            self.assertEqual(journal.error, "")
            self.assertEqual([json.loads(line)["detail"] for line in journal.path.read_text().splitlines()],
                             ["before failure", "sniff", "idle"])
