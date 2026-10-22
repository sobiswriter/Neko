"""Actual Catch controller previews and test-owned native playback measurements."""
import os
import sys
os.environ["QT_QPA_PLATFORM"] = "windows" if "--native" in sys.argv else "offscreen"
from pathlib import Path
import json
import statistics
import tempfile
import time
from unittest.mock import patch
from PIL import Image, ImageDraw, ImageOps
from PySide6.QtCore import QPoint, QSettings, QTimer, Qt
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QWidget

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from animations import CLIPS, SpriteAtlas
from behavior import NekoState
from games import Runway
from main import NekoWidget


def pixels(frame):
    q = frame.toImage().convertToFormat(QImage.Format_RGBA8888)
    return Image.frombytes("RGBA", (q.width(), q.height()), bytes(q.constBits()))


def preview(neko):
    output, coverage, logs = [], {}, {}
    base = 100.0
    for case, seconds in (("A little hunt", 14), ("Miss, sulk, cuddle", 13), ("Gentle play", 6)):
        with patch("main.time.monotonic", return_value=base):
            neko.end_game(immediate=True, clear_mood=True)
            neko.motion = case != "Gentle play"
            neko.move(400, 180)
            neko.start_game(base, "manual")
            neko.game.runway = Runway(0, 808, 180, 110 if neko.motion else 0)
        comforted = False
        for i in range(seconds * 50):
            now = base + i * .02
            if case == "A little hunt":
                cursor = (660, 240) if i < 130 else (480, 215)
            elif case == "Gentle play":
                cursor = (449, 259)
            else:
                cursor = (650, 10)
            with patch("main.time.monotonic", return_value=now), patch("main.QCursor.pos", return_value=QPoint(*cursor)):
                neko.animate()
                game = neko.game
                if game and case == "Miss, sulk, cuddle" and i >= 430 and not comforted:
                    assert game.phase == "curl"
                    neko.pet_reaction()
                    comforted = True
                frame = pixels(neko.current_frame(now))
                if game and game.direction > 0 and game.phase not in ("loss", "curl", "comfort", "win"):
                    frame = ImageOps.mirror(frame)
                if game:
                    clip = neko.game_clip()
                    coverage.setdefault(clip, set()).add(CLIPS[clip].frame_index(now - game.since))
                    logs[case] = list(game.log)
                if i % 2:
                    continue
                scene = Image.new("RGB", (1000, 380), "#faf7f2")
                d = ImageDraw.Draw(scene)
                d.rectangle((500, 0, 999, 379), fill="#282332")
                d.text((16, 12), case + " · actual controller / retained character scale", fill="#705650")
                d.text((516, 12), "Catch the Cursor", fill="#f4ded0")
                if game and game.phase not in ("curl", "loss", "comfort"):
                    for y in (180 + 80 - game.runway.lift, 304):
                        d.line((49, y, 950, y), fill="#ba9584", width=1)
                scene.paste(frame, (neko.x(), neko.y() - 1), frame)
                if game and game.phase in ("ready", "run", "prepare", "jump", "miss", "turn"):
                    x, y = cursor
                    d.polygon(((x, y), (x, y + 15), (x + 4, y + 11), (x + 9, y + 17), (x + 12, y + 15), (x + 8, y + 9), (x + 15, y + 9)), fill="white", outline="#493744")
                text = neko.bubble.text() if neko.bubble.isVisible() else ""
                d.text((16, 346), text, fill="#705650")
                d.text((516, 346), game.phase if game else "back to company", fill="#f4ded0")
                output.append(scene.quantize(colors=96))
        base += seconds + 1
    assert {"game_ready", "game_run", "game_jump", "happy_hop", "game_loss", "game_curl", "game_comfort"} <= coverage.keys(), coverage
    for clip in ("game_ready", "game_jump", "game_loss", "game_comfort", "happy_hop"):
        assert set(CLIPS[clip].order) <= coverage[clip], (clip, coverage[clip])
    for filename, duration in (("neko-catch-preview.gif", 40), ("neko-catch-preview-slow.gif", 80)):
        path = ROOT / "docs" / filename
        output[0].save(path, save_all=True, append_images=output[1:], duration=duration, loop=0, disposal=2, optimize=False)
        with Image.open(path) as gif:
            assert sum(gif.seek(i) or gif.info["duration"] for i in range(gif.n_frames)) == len(output) * duration
    (ROOT / "build/catch/preview.json").write_text(json.dumps({"coverage": {k: sorted(v) for k, v in coverage.items()}, "log": logs}, indent=2))


def native(neko, app):
    import win32gui
    paints, coverage, captures = [], {}, []
    owned_focus_seen = False
    guides_through = None
    stop_hit = None
    original = neko.paintEvent
    scripted_cursor = QPoint(660, 390)
    foreground = win32gui.GetForegroundWindow()
    backdrop = QWidget()
    backdrop.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus)
    backdrop.setAttribute(Qt.WA_ShowWithoutActivating)
    backdrop.setGeometry(180, 240, 900, 470)
    backdrop.setStyleSheet("background: #faf7f2")
    backdrop.show()
    neko.raise_()

    def paint(event):
        original(event)
        game = neko.game
        if game:
            now = time.monotonic()
            paints.append(now)
            clip = neko.game_clip()
            coverage.setdefault(clip, set()).add(CLIPS[clip].frame_index(now - game.since))
    neko.paintEvent = paint
    started = time.monotonic()
    flags = set()
    cursor_patch = patch("main.QCursor.pos", side_effect=lambda: scripted_cursor)
    cursor_patch.start()

    def drive():
        nonlocal scripted_cursor, owned_focus_seen, guides_through, stop_hit
        owned = {int(neko.winId()), int(backdrop.winId())}
        if neko.game_overlay:
            owned.update((int(neko.game_overlay.winId()), int(neko.game_overlay.stop.winId())))
        owned_focus_seen |= win32gui.GetForegroundWindow() in owned
        elapsed = time.monotonic() - started
        if elapsed > .8 and "start" not in flags:
            flags.add("start")
            neko.move(400, 350)
            neko.play_action.trigger()
        if 3.5 < elapsed < 11:
            scripted_cursor = QPoint(480, 385)
        if 5 < elapsed < 7 and "light" not in flags:
            flags.add("light")
            assert neko.game_overlay.isVisible()
            point = (round(neko.game.runway.left + 200), round(neko.game.runway.y + 124))
            guides_through = win32gui.WindowFromPoint(point) != int(neko.game_overlay.winId())
            stop_point = neko.game_overlay.stop.geometry().center()
            stop_hit = win32gui.WindowFromPoint((stop_point.x(), stop_point.y())) == int(neko.game_overlay.stop.winId())
            QApplication.primaryScreen().grabWindow(0, 180, 240, 900, 470).save(str(ROOT / "docs/neko-catch-native-light.png"))
            captures.append("light")
        if elapsed > 11 and "loss" not in flags:
            flags.add("loss")
            neko.end_game(immediate=True, clear_mood=True)
            neko.move(400, 350)
            scripted_cursor = QPoint(650, 10)
            backdrop.setStyleSheet("background: #282332")
            neko.start_game(time.monotonic(), "manual")
        if elapsed > 23 and "dark" not in flags:
            flags.add("dark")
            QApplication.primaryScreen().grabWindow(0, 180, 240, 900, 470).save(str(ROOT / "docs/neko-catch-native-dark.png"))
            captures.append("dark")
            assert neko.game.phase == "curl", neko.game.phase
            neko.pet_reaction()
        if elapsed > 26:
            timer.stop()
            cursor_patch.stop()
            intervals = [(b - a) * 1000 for a, b in zip(paints, paints[1:]) if b - a < .15]
            report = {"platform": QApplication.platformName(), "dpr": neko.devicePixelRatioF(),
                      "paint_count": len(paints), "median_ms": statistics.median(intervals),
                      "coverage": {k: sorted(v) for k, v in coverage.items()}, "captures": captures,
                      "foreground_unchanged": foreground == win32gui.GetForegroundWindow(),
                      "owned_windows_took_focus": owned_focus_seen,
                      "guides_click_through": guides_through, "stop_receives_its_own_clicks": stop_hit,
                      "cursor": "scripted observations; real pointer never moved", "pets": neko.companion.pets,
                      "naps": neko.companion.naps}
            for clip in ("game_ready", "game_jump", "game_loss", "game_curl", "game_comfort", "happy_hop"):
                assert set(CLIPS[clip].order) <= coverage.get(clip, set()), (clip, coverage.get(clip))
            assert not owned_focus_seen
            assert guides_through and stop_hit
            (ROOT / "docs/catch-native.json").write_text(json.dumps(report, indent=2))
            neko.end_game(immediate=True, clear_mood=True)
            neko.hide()
            neko.tray_icon.hide()
            backdrop.close()
            app.quit()
    timer = QTimer()
    timer.timeout.connect(drive)
    timer.start(20)
    app.exec()


if __name__ == "__main__":
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    with tempfile.TemporaryDirectory() as folder, patch("main.ActivityMonitor.start"), patch("main.desktop_activity", return_value=(0, 0, False)):
        settings = QSettings(str(Path(folder) / "preview.ini"), QSettings.IniFormat)
        settings.setValue("auto_games", False)
        neko = NekoWidget(settings)
        neko.tick_timer.stop()
        neko.show()
        app.processEvents()
        if "--native" in sys.argv:
            native(neko, app)
        else:
            neko.animation_timer.stop()
            preview(neko)
        neko.activity.close()
        neko.tray_icon.hide()
