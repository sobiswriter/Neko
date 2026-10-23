"""Exercise the executable's own bytecode/assets through its real Qt menu action."""
import json
import marshal
import os
from pathlib import Path
import sys
import tempfile
import time
from types import ModuleType
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PyInstaller.archive.readers import CArchiveReader
from PySide6.QtCore import QPoint, QSettings
from PySide6.QtWidgets import QApplication


def probe(executable, output):
    archive = CArchiveReader(str(executable))
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    results = []
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        for name in archive.toc:
            relative = name.replace("\\", "/")
            if relative.startswith("assets/") or relative == "neko_sleep.ico":
                target = root / relative
                if not target.resolve().is_relative_to(root.resolve()):
                    raise ValueError("Bundled resource escapes the probe directory")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extract(name))
        animations = ModuleType("animations")
        animations.__file__ = str(root / "animations.py")
        main = ModuleType("bundled_main")
        main.__file__ = str(root / "main.py")
        with patch.dict(sys.modules, {"animations": animations}), patch.object(sys, "_MEIPASS", folder, create=True):
            exec(archive.open_embedded_archive("PYZ.pyz").extract("animations"), animations.__dict__)
            exec(marshal.loads(archive.extract("main")), main.__dict__)
            class Observed(main.NekoWidget):
                def paintEvent(self, event):
                    if self.companion.state == main.NekoState.LEAVING:
                        self.paints.append(animations.CLIPS["depart"].frame_index(time.monotonic() - self.pose_started))
                    super().paintEvent(event)
            with patch.object(main.ActivityMonitor, "start"), \
                    patch.object(main, "desktop_activity", return_value=(0, 0, False)), \
                    patch.object(main.NekoWidget, "offline_line"), patch.object(main.QApplication, "quit"):
                for case in ("idle", "gesture", "visible_fullscreen"):
                    settings = QSettings(str(root / f"{case}.ini"), QSettings.IniFormat)
                    settings.setValue("auto_games", False)
                    settings.setValue("hide_fullscreen", False)
                    cat = Observed(settings)
                    cat.paints = []
                    cat.show_neko()
                    cat.tick_timer.stop()
                    cat.invitation_timer.stop()
                    area = app.primaryScreen().availableGeometry()
                    home = QPoint(area.center().x() - cat.width() // 2, area.bottom() - 160)
                    cat.move(home)
                    if case == "gesture":
                        cat.companion.state = main.NekoState.TAIL_CHASE
                        cat.refresh_asset()
                        cat.pose_started = time.monotonic() - sum(animations.CLIPS[cat.current_clip].durations) / 1000 + 0.2
                    cat.fullscreen = case == "visible_fullscreen"
                    action = next(a for a in cat.menu.actions() if a.text() == "Let her go · quit")
                    start = time.monotonic()
                    action.trigger()
                    while not cat.closing and time.monotonic() - start < 4:
                        app.processEvents()
                        time.sleep(0.004)
                    expected = sorted(set(animations.CLIPS["depart"].order))
                    result = {"case": case, "painted": sorted(set(cat.paints)), "expected": expected,
                              "closed": cat.closing, "home_restored": cat.pos() == home,
                              "seconds": round(time.monotonic() - start, 3)}
                    result["passed"] = result["painted"] == expected and result["closed"] and result["home_restored"]
                    results.append(result)
                    for timer in (cat.transition_timer, cat.animation_timer, cat.tick_timer, cat.invitation_timer, cat.save_timer):
                        timer.stop()
                    cat.activity.close()
                    cat.bubble.hide()
                    cat.bubble.deleteLater()
                    cat.tray_icon.hide()
                    cat.hide()
                    cat.deleteLater()
                    app.processEvents()
    Path(output).write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results))
    return all(result["passed"] for result in results)


if __name__ == "__main__":
    sys.exit(0 if probe(Path(sys.argv[1]), Path(sys.argv[2])) else 1)
