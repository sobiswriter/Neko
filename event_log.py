"""Bounded local activity journal; never records raw desktop input."""
from collections import deque
from datetime import datetime
import json
from pathlib import Path


class EventLog:
    def __init__(self, path, limit=500, max_bytes=512 * 1024):
        self.path = Path(path)
        self.entries = deque(maxlen=limit)
        self.max_bytes, self.error, self.statuses = max_bytes, "", {}
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self.path.exists():
                with self.path.open(encoding="utf-8") as stream:
                    for line in deque(stream, maxlen=limit):
                        try:
                            entry = json.loads(line)
                            if isinstance(entry, dict) and all(isinstance(entry.get(k), str) for k in ("time", "category", "action", "detail")):
                                self.entries.append(entry)
                        except ValueError:
                            continue
        except (OSError, UnicodeError) as error:
            self.error = str(error)

    def add(self, category, action, detail="", changed=False):
        detail, key = str(detail)[:500], (category, action)
        if changed and self.statuses.get(key) == detail:
            return
        self.statuses[key] = detail
        entry = {"time": datetime.now().astimezone().isoformat(timespec="milliseconds"),
                 "category": category, "action": action, "detail": detail}
        self.entries.append(entry)
        try:
            if self.path.exists() and self.path.stat().st_size >= self.max_bytes:
                self.path.replace(self.path.with_suffix(".previous.jsonl"))
            with self.path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
            self.error = ""
        except OSError as error:
            self.error = str(error)

    def text(self, category="All"):
        return "\n".join(f"{e['time']}  [{e['category']}] {e['action']}: {e['detail']}"
                         for e in self.entries if category == "All" or e["category"] == category)
