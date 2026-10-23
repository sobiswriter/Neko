"""Bounded local activity journal; never records raw desktop input."""
from collections import deque
from datetime import datetime
import json
from pathlib import Path


class EventLog:
    def __init__(self, path):
        self.path = Path(path)
        self.entries = deque(maxlen=50)
        self.error, self.statuses = "", {}
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self.path.exists():
                with self.path.open(encoding="utf-8") as stream:
                    for line in stream:
                        try:
                            entry = json.loads(line)
                            if isinstance(entry, dict) and all(isinstance(entry.get(k), str) for k in ("time", "category", "action", "detail")):
                                self.entries.append(entry)
                        except ValueError:
                            continue
        except (OSError, UnicodeError) as error:
            self.error = str(error)
            return
        self.save()

    def add(self, category, action, detail="", changed=False):
        detail, key = str(detail)[:500], (category, action)
        if changed and self.statuses.get(key) == detail:
            return
        self.statuses[key] = detail
        entry = {"time": datetime.now().astimezone().isoformat(timespec="milliseconds"),
                 "category": category, "action": action, "detail": detail}
        self.entries.append(entry)
        self.save()

    def save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text("".join(json.dumps(entry, ensure_ascii=False) + "\n" for entry in self.entries), encoding="utf-8")
            temporary.replace(self.path)
            self.path.with_suffix(".previous.jsonl").unlink(missing_ok=True)
            self.error = ""
        except OSError as error:
            self.error = str(error)

    def text(self, category="All"):
        return "\n".join(f"{e['time']}  [{e['category']}] {e['action']}: {e['detail']}"
                         for e in self.entries if category == "All" or e["category"] == category)
