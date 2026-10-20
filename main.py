"""Desktop Neko — a small, quiet companion for Windows."""

import ctypes
from ctypes import wintypes
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import winreg

import win32gui
from PySide6.QtCore import QLockFile, QPoint, QRectF, QSettings, QStandardPaths, Qt, QTimer
from PySide6.QtGui import QColor, QCursor, QFont, QIcon, QMovie, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QDialog, QHBoxLayout, QLabel, QMenu, QMessageBox,
    QPushButton, QSystemTrayIcon, QVBoxLayout, QWidget,
)

from behavior import Companion, NekoState


ASSET_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "assets"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def legacy_shortcut():
    return Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs/Startup/DesktopNeko.lnk"


def autostart_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.QueryValueEx(key, "DesktopNeko")
        return True
    except OSError:
        return legacy_shortcut().exists()


def set_autostart(enabled):
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
        if enabled:
            executable = Path(sys.executable)
            if not getattr(sys, "frozen", False):
                pythonw = executable.with_name("pythonw.exe")
                executable = pythonw if pythonw.exists() else executable
            args = [str(executable)]
            if not getattr(sys, "frozen", False):
                args.append(str(Path(__file__).resolve()))
            winreg.SetValueEx(key, "DesktopNeko", 0, winreg.REG_SZ, subprocess.list2cmdline(args))
        else:
            try:
                winreg.DeleteValue(key, "DesktopNeko")
            except FileNotFoundError:
                pass
    # Retire the old automatic shortcut so startup never launches two copies.
    legacy_shortcut().unlink(missing_ok=True)


class LastInputInfo(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]


def desktop_activity():
    info = LastInputInfo()
    info.cbSize = ctypes.sizeof(info)
    idle = 0
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
        idle = ((ctypes.windll.kernel32.GetTickCount() - info.dwTime) & 0xFFFFFFFF) / 1000
    window = win32gui.GetForegroundWindow()
    fullscreen = False
    if window and win32gui.IsWindowVisible(window):
        try:
            bounds = win32gui.GetWindowRect(window)
            screen = QApplication.screenAt(QPoint(bounds[0], bounds[1]))
            if screen and win32gui.GetClassName(window) not in ("Progman", "WorkerW"):
                area = screen.geometry()
                fullscreen = (bounds[0] <= area.left() and bounds[1] <= area.top()
                              and bounds[2] >= area.right() + 1
                              and bounds[3] >= area.bottom() + 1)
        except win32gui.error:
            pass
    return idle, window, fullscreen


class StatsWindow(QDialog):
    """One small home for preferences and lifetime keepsakes."""

    def __init__(self, neko):
        super().__init__()
        self.neko = neko
        self.startup_error = ""
        self.setWindowTitle("Neko's nook")
        self.setFixedWidth(340)
        self.setStyleSheet("""
            QDialog { background: #faf7f2; color: #504b48; }
            QLabel { color: #504b48; font-size: 13px; }
            QCheckBox { color: #504b48; padding: 7px 0; font-size: 13px; }
            QPushButton { background: #eee5df; color: #504b48; border: 0;
                          border-radius: 8px; padding: 9px 16px; }
            QPushButton:hover { background: #e7d8d1; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 24)
        layout.setSpacing(12)
        title = QLabel("a little company.")
        title.setStyleSheet("font-size: 23px; font-weight: 600;")
        layout.addWidget(title)
        subtitle = QLabel("happy to be here. nothing to keep up with.")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        self.keepsakes = QLabel()
        self.keepsakes.setStyleSheet("color: #91756b; padding: 12px 0;")
        layout.addWidget(self.keepsakes)
        self.focus = QCheckBox("Quiet company · no unprompted words")
        self.focus.setChecked(neko.quiet)
        self.focus.toggled.connect(neko.set_quiet)
        layout.addWidget(self.focus)
        self.motion = QCheckBox("Gentle motion")
        self.motion.setChecked(neko.motion)
        self.motion.toggled.connect(neko.set_motion)
        layout.addWidget(self.motion)
        self.startup = QCheckBox("Join me when Windows starts")
        self.startup.setChecked(autostart_enabled())
        self.startup.toggled.connect(self.change_startup)
        layout.addWidget(self.startup)
        self.ai = QCheckBox("AI observations · optional")
        self.ai.setChecked(neko.ai_enabled)
        self.ai.toggled.connect(neko.set_ai)
        layout.addWidget(self.ai)
        privacy = QLabel("AI sends the current window title to Google Gemini.\n"
                         "No screenshots. No conversation history.\n"
                         "Uses GEMINI_API_KEY from your environment or config.json.")
        privacy.setWordWrap(True)
        privacy.setStyleSheet("font-size: 11px; color: #8a817b;")
        layout.addWidget(privacy)
        self.status = QLabel()
        self.status.setWordWrap(True)
        self.status.setStyleSheet("font-size: 11px; color: #8a817b;")
        layout.addWidget(self.status)
        row = QHBoxLayout()
        recenter = QPushButton("Back to my corner")
        recenter.clicked.connect(neko.position_to_bottom_right)
        row.addWidget(recenter)
        done = QPushButton("Comfy.")
        done.clicked.connect(self.close)
        row.addWidget(done)
        layout.addLayout(row)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.update_stats()

    def showEvent(self, event):
        self.focus.setChecked(self.neko.quiet)
        self.ai.setChecked(self.neko.ai_enabled)
        self.update_stats()
        self.timer.start(1000)
        super().showEvent(event)

    def hideEvent(self, event):
        self.timer.stop()
        super().hideEvent(event)

    def update_stats(self):
        n = self.neko
        self.keepsakes.setText(f"{n.total_pets + n.companion.pets} little pets   ·   "
                               f"{n.total_naps + n.companion.naps} cozy naps")
        self.status.setText(self.startup_error or n.ai_status)

    def change_startup(self, enabled):
        try:
            set_autostart(enabled)
            self.startup_error = ""
        except OSError:
            self.startup.blockSignals(True)
            self.startup.setChecked(autostart_enabled())
            self.startup.blockSignals(False)
            self.startup_error = "Couldn't change Windows startup. You can try again later."
        self.update_stats()


class NekoWidget(QWidget):
    def __init__(self, settings=None):
        super().__init__()
        self.settings = settings if settings is not None else QSettings("DesktopNeko", "Neko")
        self.companion = Companion(time.monotonic())
        self.quiet = self.settings.value("quiet", False, type=bool)
        self.motion = self.settings.value("motion", True, type=bool)
        self.ai_enabled = self.settings.value("ai_enabled", False, type=bool)
        self.total_pets = max(0, self.settings.value("pets", 0, type=int))
        self.total_naps = max(0, self.settings.value("naps", 0, type=int))
        self.is_manually_hidden = False
        self.fullscreen = False
        self.last_window = 0
        self.brain_worker = None
        self.ai_generation = 0
        self.ai_status = "Offline company is always available."
        self.last_line = ""
        self.last_pet_words = -math.inf
        self.drag_origin = None
        self.dragged = False
        self.closing = False
        self.started = time.monotonic()
        self.pose_started = self.started
        self.stats_window = None
        self.setWindowTitle("Desktop Neko")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
                            | Qt.Tool | Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedSize(112, 112)
        self.setAccessibleName("Neko, your desktop companion")
        self.setAccessibleDescription("Click to pet, drag to move, or right-click for Neko's nook.")
        self.assets = {}
        self.movies = {}
        for name in ("idle", "sleep", "happy", "peek", "curious"):
            self.assets[name] = QPixmap(str(ASSET_ROOT / f"neko_{name}.png"))
            movie = QMovie(str(ASSET_ROOT / f"neko_{name}.gif"))
            if movie.isValid():
                movie.frameChanged.connect(self.update)
                self.movies[name] = movie
        self.current_asset = "idle"
        self.bubble = QLabel(None, Qt.ToolTip | Qt.FramelessWindowHint
                             | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus
                             | Qt.WindowTransparentForInput)
        self.bubble.setAttribute(Qt.WA_ShowWithoutActivating)
        self.bubble.setAttribute(Qt.WA_TranslucentBackground)
        self.bubble.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.bubble.setTextFormat(Qt.PlainText)
        self.bubble.setWordWrap(True)
        self.bubble.setFixedWidth(215)
        self.bubble.setStyleSheet("background: #faf7f2; color: #66564f; border: 1px solid #e7dcd3;"
                                 "border-radius: 12px; padding: 10px 13px; font: 12px 'Segoe UI';")
        self.bubble_timer = QTimer(self)
        self.bubble_timer.setSingleShot(True)
        self.bubble_timer.timeout.connect(self.bubble.hide)
        self.tick_timer = QTimer(self)
        self.tick_timer.timeout.connect(self.tick)
        self.tick_timer.start(1000)
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update)
        self.save_timer = QTimer(self)
        self.save_timer.timeout.connect(self.save_preferences)
        self.save_timer.start(60000)
        self.init_tray()
        saved = self.settings.value("position", None)
        self.position_to_bottom_right()
        if isinstance(saved, QPoint):
            self.move(saved)
            self.clamp_position()
        app = QApplication.instance()
        app.primaryScreenChanged.connect(self.clamp_position)
        app.screenRemoved.connect(self.clamp_position)
        self.sync_animation()

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(QIcon(self.assets["idle"]), self)
        self.tray_icon.setToolTip("Neko · a little company")
        self.menu = QMenu()
        self.menu.addAction("Neko's nook…", self.open_stats_window)
        self.quiet_action = self.menu.addAction("Quiet company")
        self.quiet_action.setCheckable(True)
        self.quiet_action.setChecked(self.quiet)
        self.quiet_action.toggled.connect(self.set_quiet)
        self.hide_action = self.menu.addAction("Hide Neko", self.toggle_visibility)
        self.menu.addSeparator()
        self.menu.addAction("Let her go · quit", self.quit_neko)
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self.tray_activated)
        self.tray_icon.show()

    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_neko()
            self.open_stats_window()

    def set_quiet(self, enabled):
        self.quiet = enabled
        self.quiet_action.setChecked(enabled)
        self.ai_generation += 1
        self.companion.next_comment = time.monotonic() + random.uniform(720, 1200)
        if enabled:
            self.dismiss_bubble()
        self.save_preferences()

    def set_motion(self, enabled):
        self.motion = enabled
        self.sync_animation()
        self.save_preferences()

    def set_ai(self, enabled):
        self.ai_enabled = enabled
        self.ai_generation += 1
        self.ai_status = ("Observations are rare and quiet; an API key is needed."
                          if enabled else "Offline company is always available.")
        self.save_preferences()

    def sync_animation(self):
        active = self.isVisible() and not self.is_manually_hidden and not self.fullscreen
        if active and self.motion:
            self.animation_timer.start(80)
        else:
            self.animation_timer.stop()
        for name, movie in self.movies.items():
            if active and self.motion and name == self.current_asset:
                movie.start()
            else:
                movie.stop()
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, "animation_timer"):
            self.sync_animation()

    def dismiss_bubble(self):
        self.bubble_timer.stop()
        self.bubble.hide()

    def tick(self):
        if self.closing or self.is_manually_hidden or self.drag_origin is not None:
            return
        now = time.monotonic()
        idle, window, fullscreen = desktop_activity()
        if fullscreen != self.fullscreen:
            self.fullscreen = fullscreen
            self.ai_generation += 1
            self.companion.next_comment = now + random.uniform(720, 1200)
            self.companion.next_idle = now + random.uniform(20, 40)
            self.dismiss_bubble()
            self.setVisible(not fullscreen)
            self.sync_animation()
        if fullscreen:
            self.last_window = window
            return
        near = (QCursor.pos() - self.geometry().center()).manhattanLength() < 150
        action = self.companion.tick(now, idle, self.quiet,
                                     cursor_near=near,
                                     window_changed=bool(self.last_window and window != self.last_window))
        self.last_window = window
        if action == "comment":
            if self.ai_enabled:
                self.trigger_ai_brain()
            else:
                self.random_dialogue()
        elif action:
            self.pose_started = now
            self.refresh_asset()
            if action == "sleep":
                self.ai_generation += 1
                self.dismiss_bubble()

    def refresh_asset(self):
        self.current_asset = {
            NekoState.SLEEPING: "sleep", NekoState.PEEKING: "peek",
            NekoState.CURIOUS: "curious", NekoState.HAPPY: "happy",
            NekoState.GROOMING: "peek",
        }.get(self.companion.state, "idle")
        self.sync_animation()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)
        now = time.monotonic()
        elapsed = now - self.pose_started
        state = self.companion.state
        breathing = math.sin((now - self.started) * 1.7) if self.motion else 0
        y, sx, sy, rotation = -0.7 * breathing, 1, 1 + 0.012 * breathing, 0
        if self.motion:
            if state == NekoState.STRETCHING:
                stretch = math.sin(min(elapsed / 3.5, 1) * math.pi)
                sx, sy = 1 - 0.07 * stretch, 1 + 0.12 * stretch
            elif state == NekoState.GROOMING:
                rotation = math.sin(elapsed * 5) * 4
            elif state == NekoState.CURIOUS:
                rotation = 4 if QCursor.pos().x() >= self.geometry().center().x() else -4
            elif state == NekoState.HAPPY:
                y -= abs(math.sin(elapsed * 3)) * 2
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(75, 55, 48, 18))
        painter.drawEllipse(QRectF(28, 99, 56, 5))
        painter.save()
        painter.translate(56, 99 + y)
        painter.rotate(rotation)
        painter.scale(sx, sy)
        movie = self.movies.get(self.current_asset)
        pixmap = movie.currentPixmap() if movie and not movie.currentPixmap().isNull() else self.assets[self.current_asset]
        if pixmap.isNull():
            painter.setPen(QColor("#a67671"))
            painter.drawText(QRectF(-45, -85, 90, 85), Qt.AlignCenter, "=^·ω·^=")
        else:
            pixmap = pixmap.scaled(88, 88, Qt.KeepAspectRatio, Qt.FastTransformation)
            painter.drawPixmap(-pixmap.width() // 2, -pixmap.height(), pixmap)
        painter.restore()
        if state == NekoState.HAPPY and elapsed < 3.2:
            painter.setPen(QColor("#cf9699"))
            painter.setFont(QFont("Segoe UI Symbol", 12))
            painter.drawText(QRectF(78, 12 - (elapsed * 4 if self.motion else 0), 22, 24), "♡")

    def say(self, text, prompted=False):
        if (self.closing or self.is_manually_hidden or self.fullscreen
                or not self.isVisible() or (self.quiet and not prompted)
                or self.companion.state == NekoState.SLEEPING):
            return False
        text = " ".join(str(text).split())[:140]
        if not text:
            return False
        self.bubble.setText(text)
        self.bubble.adjustSize()
        screen = QApplication.screenAt(self.geometry().center()) or QApplication.primaryScreen()
        area = screen.availableGeometry()
        x = max(area.left() + 6, min(self.x() + 56 - self.bubble.width() // 2,
                                    area.right() - self.bubble.width() - 6))
        y = self.y() - self.bubble.height() - 4
        if y < area.top():
            y = self.geometry().bottom() + 4
        y = max(area.top(), min(y, area.bottom() - self.bubble.height()))
        self.bubble.move(x, y)
        self.bubble.show()
        self.bubble_timer.start(max(3500, min(6500, len(text) * 65)))
        self.companion.comments += 1
        return True

    def random_dialogue(self):
        lines = ["a good spot for doing nothing.", "mrrp. carrying on.",
                 "just keeping you company.", "a little stretch. that's all.",
                 "comfy here.", "i'll be right here. take your time."]
        line = random.choice([line for line in lines if line != self.last_line])
        if self.say(line):
            self.last_line = line

    def pet_reaction(self):
        now = time.monotonic()
        self.ai_generation += 1
        self.companion.pet(now)
        self.pose_started = now
        self.refresh_asset()
        if now - self.last_pet_words >= 20:
            self.say(random.choice(["purrr.", "mrrp ♡", "oh. hello, you.", "that's the spot."]), prompted=True)
            self.last_pet_words = now

    def trigger_ai_brain(self):
        if self.brain_worker is not None or not self.ai_enabled or self.quiet:
            return
        from llm_brain import AIBrainWorker
        try:
            title = win32gui.GetWindowText(win32gui.GetForegroundWindow())[:240]
        except win32gui.error:
            return
        self.request_generation = self.ai_generation
        self.request_started = time.monotonic()
        self.brain_worker = AIBrainWorker(title, parent=self)
        self.brain_worker.finished_thinking.connect(self.on_brain_finished)
        self.brain_worker.finished.connect(self.release_brain)
        self.brain_worker.start()

    def on_brain_finished(self, text, success):
        if self.closing:
            return
        self.ai_status = ("AI is connected. Window titles only." if success else
                          "AI is unavailable. Check your API key or connection; offline company continues.")
        if (self.request_generation != self.ai_generation or not self.ai_enabled
                or self.quiet or time.monotonic() - self.request_started > 25):
            return
        # Recheck the foreground window: a game may have opened during the request.
        if desktop_activity()[2]:
            return
        if success:
            self.say(text)
        else:
            self.random_dialogue()

    def release_brain(self):
        self.brain_worker.deleteLater()
        self.brain_worker = None
        if self.closing:
            QApplication.quit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_origin = event.globalPosition().toPoint()
            self.drag_offset = self.drag_origin - self.pos()
            self.dragged = False
            event.accept()
        elif event.button() == Qt.RightButton:
            self.menu.exec(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drag_origin is not None:
            point = event.globalPosition().toPoint()
            if (point - self.drag_origin).manhattanLength() >= QApplication.startDragDistance():
                self.dragged = True
            if self.dragged:
                self.dismiss_bubble()
                self.move(point - self.drag_offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drag_origin is not None:
            if self.dragged:
                self.ai_generation += 1
                self.clamp_position()
                self.save_preferences()
            else:
                self.pet_reaction()
            self.drag_origin = None

    def position_to_bottom_right(self):
        area = QApplication.primaryScreen().availableGeometry()
        self.move(area.right() - self.width() - 24, area.bottom() - self.height() - 12)
        self.dismiss_bubble()

    def clamp_position(self, *args):
        screen = QApplication.screenAt(self.geometry().center()) or QApplication.primaryScreen()
        area = screen.availableGeometry()
        self.move(max(area.left(), min(self.x(), area.right() - self.width() + 1)),
                  max(area.top(), min(self.y(), area.bottom() - self.height() + 1)))

    def toggle_visibility(self):
        if self.is_manually_hidden:
            self.show_neko()
        else:
            self.hide_neko()

    def hide_neko(self):
        self.is_manually_hidden = True
        self.ai_generation += 1
        self.dismiss_bubble()
        self.hide()
        self.hide_action.setText("Show Neko")
        self.sync_animation()

    def show_neko(self):
        self.is_manually_hidden = False
        self.hide_action.setText("Hide Neko")
        self.companion.next_comment = time.monotonic() + random.uniform(720, 1200)
        self.fullscreen = desktop_activity()[2]
        self.setVisible(not self.fullscreen)
        self.sync_animation()

    def open_stats_window(self):
        if self.stats_window is None:
            self.stats_window = StatsWindow(self)
        self.stats_window.show()
        self.stats_window.raise_()
        self.stats_window.activateWindow()

    def save_preferences(self):
        for key, value in {"quiet": self.quiet, "motion": self.motion,
                           "ai_enabled": self.ai_enabled, "position": self.pos(),
                           "pets": self.total_pets + self.companion.pets,
                           "naps": self.total_naps + self.companion.naps}.items():
            self.settings.setValue(key, value)
        self.settings.sync()

    def quit_neko(self):
        self.closing = True
        self.tick_timer.stop()
        self.animation_timer.stop()
        self.dismiss_bubble()
        self.hide()
        self.tray_icon.hide()
        if self.stats_window:
            self.stats_window.close()
        self.save_preferences()
        if self.brain_worker is not None:
            self.brain_worker.requestInterruption()
        else:
            QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide_neko()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("Desktop Neko")
    app.setOrganizationName("DesktopNeko")
    data_dir = Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))
    data_dir.mkdir(parents=True, exist_ok=True)
    instance_lock = QLockFile(str(data_dir / "neko.lock"))
    instance_lock.setStaleLockTime(0)
    if not instance_lock.tryLock(0):
        if instance_lock.error() != QLockFile.LockFailedError:
            QMessageBox.warning(None, "Desktop Neko", "Couldn't open Neko's local settings folder.")
        sys.exit(0)
    neko = NekoWidget()
    app.aboutToQuit.connect(neko.save_preferences)
    neko.show_neko()
    sys.exit(app.exec())
