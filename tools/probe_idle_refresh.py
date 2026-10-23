"""One native pass of the refreshed idles under the production Qt timers."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "windows")
import json
from pathlib import Path
import sys
import tempfile
import time
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PySide6.QtCore import QPoint, QSettings
from PySide6.QtWidgets import QApplication
from animations import CLIPS
from behavior import NekoState
from main import NekoWidget

STATES = {"idle": NekoState.IDLE, "loaf": NekoState.LOAFING, "stretch": NekoState.STRETCHING,
          "groom": NekoState.GROOMING, "yawn": NekoState.YAWNING, "peek": NekoState.PEEKING,
          "ears": NekoState.EAR_FLICK, "sniff": NekoState.SNIFFING,
          "look_left": NekoState.CURIOUS, "look_right": NekoState.CURIOUS, "tail": NekoState.TAIL_SWISH}


class ObservedNeko(NekoWidget):
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.current_clip == self.observing and self.rendered_clip == self.observing:
            self.paints.append((time.monotonic(), CLIPS[self.observing].frame_index(time.monotonic() - self.pose_started)))


def probe(output):
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    result = {}
    with tempfile.TemporaryDirectory() as folder, patch("main.ActivityMonitor.start"), \
            patch("main.desktop_activity", return_value=(0, 0, False)), \
            patch("main.QCursor.pos", return_value=QPoint(-10000, -10000)), \
            patch("main.NekoWidget.offline_line"):
        settings = QSettings(str(Path(folder) / "prefs.ini"), QSettings.IniFormat)
        settings.setValue("auto_games", False)
        cat = ObservedNeko(settings)
        cat.observing, cat.paints = None, []
        cat.show_neko()
        area = app.primaryScreen().availableGeometry()
        cat.move(area.center().x() - 96, area.bottom() - 180)
        for name, state in STATES.items():
            cat.observing, cat.paints = name, []
            start = time.monotonic()
            cat.look_direction = -1 if name == "look_left" else 1
            cat.companion.pose(state, start, 1000)
            cat.companion.next_idle = cat.companion.next_comment = cat.companion.next_nap = start + 1000
            cat.pose_started = start
            cat.refresh_asset()
            assert cat.current_clip == name
            assert cat.animation_timer.interval() == 100
            duration = sum(CLIPS[name].durations) / 1000
            while time.monotonic() - start < duration + .15:
                app.processEvents()
                time.sleep(.004)
            painted = sorted({index for _, index in cat.paints})
            expected = sorted(set(CLIPS[name].order))
            gaps = [b[0] - a[0] for a, b in zip(cat.paints, cat.paints[1:])]
            result[name] = {"painted": painted, "expected": expected, "complete": painted == expected,
                            "duration_ms": round(duration * 1000), "timer_ms": cat.animation_timer.interval(),
                            "max_paint_gap_ms": round(max(gaps, default=0) * 1000, 2)}
            print(name, result[name], flush=True)
        for timer in (cat.tick_timer, cat.invitation_timer, cat.animation_timer, cat.save_timer):
            timer.stop()
        cat.activity.close()
        cat.bubble.hide()
        cat.tray_icon.hide()
        cat.hide()
    Path(output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    assert all(item["complete"] for item in result.values()), result


if __name__ == "__main__":
    probe(sys.argv[1] if len(sys.argv) > 1 else ROOT / "docs/idle-refresh-native.json")
