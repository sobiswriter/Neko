"""Bounded local activity journal; never records raw desktop input."""
from collections import deque
from datetime import datetime
import json
import os
from pathlib import Path
import time

LIMIT = 50
FIELDS = ("time", "category", "action", "detail")
# Status rows ("waiting", "deferred", ...) that flip back and forth are only repeated after this pause,
# so the 50 retained rows keep the real story instead of polling chatter.
STATUS_REPEAT_SECONDS = 60


class EventLog:
    def __init__(self, path, autosave=True):
        """autosave=False: add() only marks the journal dirty; the owner calls flush() on a timer
        and at exit, so a burst of events never writes (and fsyncs) the file on the UI thread."""
        self.path = Path(path)
        self.autosave = autosave
        self.dirty = False
        self.entries = deque(maxlen=LIMIT)
        self.error, self.statuses = "", {}
        self.status_times = {}
        self.loaded = False
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.entries.extend(self.read())
            self.loaded = True
        except OSError as error:
            # Keep the unreadable file; save() merges it back once it can be read.
            self.error = str(error)
            return
        self.save()

    def read(self):
        if not self.path.exists():
            return []
        rows = []
        # A damaged byte or an editor's BOM costs at most that row, never the rest of the history.
        with self.path.open(encoding="utf-8-sig", errors="replace") as stream:
            for line in stream:
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if isinstance(entry, dict) and all(isinstance(entry.get(k), str) for k in FIELDS):
                    rows.append({k: entry[k] for k in FIELDS})
        return rows[-LIMIT:]

    def add(self, category, action, detail="", changed=False):
        detail, key = str(detail)[:500], (category, action)
        if changed:
            now = time.monotonic()
            if self.statuses.get(key) == detail:
                return
            if now - self.status_times.get((key, detail), -STATUS_REPEAT_SECONDS) < STATUS_REPEAT_SECONDS:
                self.statuses[key] = detail
                return
            self.status_times[key, detail] = now
            if len(self.status_times) > 200:
                self.status_times = {k: v for k, v in self.status_times.items()
                                     if now - v < STATUS_REPEAT_SECONDS}
        self.statuses[key] = detail
        entry = {"time": datetime.now().astimezone().isoformat(timespec="milliseconds"),
                 "category": category, "action": action, "detail": detail}
        self.entries.append(entry)
        if self.autosave:
            self.save()
        else:
            self.dirty = True

    def flush(self):
        if self.dirty:
            self.dirty = False
            self.save()

    def save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if not self.loaded:
                earlier = self.read()
                current = list(self.entries)
                self.entries.clear()
                self.entries.extend(earlier + current)
                self.loaded = True
            temporary = self.path.with_suffix(".tmp")
            with temporary.open("w", encoding="utf-8", errors="replace", newline="\n") as stream:
                stream.write("".join(json.dumps(entry, ensure_ascii=False) + "\n" for entry in self.entries))
                stream.flush()
                os.fsync(stream.fileno())
            try:
                temporary.replace(self.path)
            except PermissionError:
                # Indexers and antivirus briefly lock small files on Windows; try once more.
                time.sleep(0.05)
                temporary.replace(self.path)
            self.path.with_suffix(".previous.jsonl").unlink(missing_ok=True)
            self.error = ""
        except (OSError, ValueError) as error:
            self.error = str(error)

    def text(self, category="All"):
        return "\n".join(f"{e['time']}  [{e['category']}] {e['action']}: {e['detail']}"
                         for e in self.entries if category == "All" or e["category"] == category)
