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
import winsound

import win32gui
import win32con
from PySide6.QtCore import QLockFile, QPoint, QRectF, QSettings, QStandardPaths, Qt, QTimer
from PySide6.QtGui import QColor, QCursor, QFont, QIcon, QMovie, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QDialog, QHBoxLayout, QLabel, QMenu, QMessageBox,
    QPushButton, QSpinBox, QFormLayout, QTabWidget, QSystemTrayIcon, QVBoxLayout, QWidget,
)

from behavior import Companion, NekoState, PET_STATES
from activity import ActivityMonitor, foreground_executable
from app_context import app_kind
from animations import SpriteAtlas
from dialogue import OfflineDialogue


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
            if (screen and not ctypes.windll.user32.IsZoomed(wintypes.HWND(window))
                    and win32gui.GetClassName(window) not in ("Progman", "WorkerW")):
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
            QWidget { background: #faf7f2; color: #504b48; }
            QDialog { background: #faf7f2; color: #504b48; }
            QTabWidget::pane { border: 1px solid #e7dcd3; border-radius: 6px; }
            QTabBar::tab { background: #eee5df; color: #66564f; padding: 7px 14px; }
            QTabBar::tab:selected { background: #e7d8d1; }
            QSpinBox { background: #fffdf9; color: #504b48; min-height: 25px; }
            QLineEdit { background: #fffdf9; color: #504b48; }
            QLabel { color: #504b48; font-size: 13px; }
            QCheckBox { color: #504b48; padding: 7px 0; font-size: 13px; }
            QCheckBox::indicator:unchecked { border: 1px solid #baa79d;
                                             border-radius: 3px; background: #fffdf9; }
            QPushButton { background: #eee5df; color: #504b48; border: 0;
                          border-radius: 8px; padding: 9px 16px; }
            QPushButton:hover { background: #e7d8d1; }
            QPushButton:disabled { color: #9c9088; background: #f2ece6; }
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
        self.keepsakes.setStyleSheet("color: #80675e; padding: 12px 0;")
        layout.addWidget(self.keepsakes)
        self.mood = QLabel()
        self.mood.setStyleSheet("color: #746b65; font-size: 12px;")
        layout.addWidget(self.mood)
        tabs = QTabWidget()
        layout.addWidget(tabs)
        company, settings = QWidget(), QWidget()
        tabs.addTab(company, "Company")
        tabs.addTab(settings, "Settings")
        company_layout, settings_layout = QVBoxLayout(company), QVBoxLayout(settings)
        self.focus = QCheckBox("Quiet company · no unprompted words")
        self.focus.setChecked(neko.quiet)
        self.focus.toggled.connect(neko.set_quiet)
        company_layout.addWidget(self.focus)
        self.motion = QCheckBox("Gentle motion")
        self.motion.setChecked(neko.motion)
        self.motion.toggled.connect(neko.set_motion)
        settings_layout.addWidget(self.motion)
        sound_row = QHBoxLayout()
        self.sounds = QCheckBox("Soft mews and purrs")
        self.sounds.setChecked(neko.sounds_enabled)
        self.sounds.toggled.connect(neko.set_sounds)
        sound_row.addWidget(self.sounds)
        self.sound_test = QPushButton("Listen")
        self.sound_test.setEnabled(neko.sounds_enabled)
        self.sound_test.setAccessibleName("Preview a soft mew")
        self.sound_test.clicked.connect(lambda: neko.play_sound("mew", prompted=True))
        self.sounds.toggled.connect(self.sound_test.setEnabled)
        sound_row.addWidget(self.sound_test)
        settings_layout.addLayout(sound_row)
        self.reactivity = QCheckBox("Notice typing and window activity")
        self.reactivity.setChecked(neko.reactive)
        self.reactivity.toggled.connect(neko.set_reactivity)
        company_layout.addWidget(self.reactivity)
        self.follow = QCheckBox("Sometimes follow the little arrow")
        self.follow.setChecked(neko.follow_mouse)
        self.follow.toggled.connect(neko.set_follow_mouse)
        company_layout.addWidget(self.follow)
        timing = QFormLayout()
        self.timing = {}
        for key, label, minimum, maximum in (
                ("sleep_seconds", "Sleep after inactivity", 30, 3600),
                ("chatter_seconds", "Little thoughts about every", 15, 600),
                ("idle_seconds", "Idle gestures about every", 5, 120)):
            spin = QSpinBox()
            spin.setRange(minimum, maximum)
            spin.setSuffix(" sec")
            spin.setValue(getattr(neko.companion, key))
            spin.setAccessibleName(label)
            spin.valueChanged.connect(lambda value, key=key: neko.set_timing(key, value))
            self.timing[key] = spin
            timing.addRow(label, spin)
        company_layout.addLayout(timing)
        note = QLabel("Naps last 90 seconds, even while you work.\nQuiet company still welcomes a deliberate pet.")
        note.setWordWrap(True)
        company_layout.addWidget(note)
        company_layout.addStretch()
        self.fullscreen = QCheckBox("Tuck away during fullscreen apps")
        self.fullscreen.setChecked(neko.hide_fullscreen)
        self.fullscreen.toggled.connect(neko.set_hide_fullscreen)
        settings_layout.addWidget(self.fullscreen)
        self.startup = QCheckBox("Join me when Windows starts")
        self.startup.setChecked(autostart_enabled())
        self.startup.toggled.connect(self.change_startup)
        settings_layout.addWidget(self.startup)
        self.ai = QCheckBox("AI observations · optional")
        self.ai.setChecked(neko.ai_enabled)
        self.ai.toggled.connect(neko.set_ai)
        settings_layout.addWidget(self.ai)
        privacy = QLabel("Offline uses app names and title hints locally.\n"
                         "Never reads what you type.\n"
                         "AI sends the current window title to Google Gemini.\n"
                         "No screenshots. No conversation history.\n"
                         "Uses GEMINI_API_KEY from your environment or config.json.")
        privacy.setWordWrap(True)
        privacy.setStyleSheet("font-size: 11px; color: #746b65;")
        settings_layout.addWidget(privacy)
        self.status = QLabel()
        self.status.setWordWrap(True)
        self.status.setStyleSheet("font-size: 11px; color: #746b65;")
        settings_layout.addWidget(self.status)
        settings_layout.addStretch()
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
        self.reactivity.setChecked(self.neko.reactive)
        self.fullscreen.setChecked(self.neko.hide_fullscreen)
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
        self.mood.setText({
            NekoState.IDLE: "happy to keep you company.",
            NekoState.TYPING: "helping with the important paw-work.",
            NekoState.CURIOUS: "oh? something happening over there?",
            NekoState.GROOMING: "washing these very important little paws.",
            NekoState.STRETCHING: "a biiig little stretch.",
            NekoState.YAWNING: "just resting my eyes...",
            NekoState.WAKING: "back from a little dream.",
            NekoState.SLEEPING: "somewhere soft, in a dream.",
            NekoState.HAPPY: "yes. right there. purrr.",
            NekoState.PEEKING: "just checking you're still there.",
        }.get(n.companion.state, "a little cat, doing little cat things."))

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
        for key, default, minimum, maximum in (("sleep_seconds", 180, 30, 3600),
                                              ("chatter_seconds", 75, 15, 600),
                                              ("idle_seconds", 14, 5, 120)):
            try:
                value = int(self.settings.value(key, default))
            except (ValueError, TypeError, OverflowError):
                value = default
            setattr(self.companion, key, max(minimum, min(maximum, value)))
        self.companion.next_comment = time.monotonic() + self.companion.chatter_seconds
        self.companion.next_idle = time.monotonic() + self.companion.idle_seconds
        self.follow_mouse = self.settings.value("follow_mouse", True, type=bool)
        self.dialogue = OfflineDialogue()
        self.last_words = -math.inf
        self.last_ai_attempt = -math.inf
        self.last_cursor = QCursor.pos()
        self.follow_origin = None
        self.last_follow = time.monotonic() - 45
        self.last_title_stamp = None
        self.quiet = self.settings.value("quiet", False, type=bool)
        self.motion = self.settings.value("motion", True, type=bool)
        self.sounds_enabled = self.settings.value("sounds_enabled", False, type=bool)
        self.last_sound = -math.inf
        self.reactive = self.settings.value("reactive", True, type=bool)
        self.hide_fullscreen = self.settings.value("hide_fullscreen", False, type=bool)
        self.ai_enabled = self.settings.value("ai_enabled", False, type=bool)
        self.total_pets = max(0, self.settings.value("pets", 0, type=int))
        self.total_naps = max(0, self.settings.value("naps", 0, type=int))
        self.is_manually_hidden = False
        self.fullscreen = False
        self.last_window = 0
        self.current_executable = ""
        self.app_context = None
        self.brain_worker = None
        self.ai_generation = 0
        self.ai_status = "Offline company is always available."
        self.last_pet_words = -math.inf
        self.drag_origin = None
        self.dragged = False
        self.closing = False
        self.started = time.monotonic()
        self.pose_started = self.started
        self.look_direction = -1
        self.last_pin = 0
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
        self.atlas = SpriteAtlas(ASSET_ROOT)
        for name in ("idle", "sleep", "happy", "peek", "curious"):
            self.assets[name] = QPixmap(str(ASSET_ROOT / f"neko_{name}.png"))
            movie = QMovie(str(ASSET_ROOT / f"neko_{name}.gif"))
            if movie.isValid():
                movie.frameChanged.connect(self.update)
                self.movies[name] = movie
        self.current_asset = "idle"
        self.current_clip = "idle"
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
        self.tick_timer.start(500)
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate)
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
        self.activity = ActivityMonitor()
        self.activity.enabled = self.reactive
        self.activity.start(int(self.winId()))
        self.destroyed.connect(self.activity.close)
        self.sync_animation()
        self.hello_timer = QTimer(self)
        self.hello_timer.setSingleShot(True)
        self.hello_timer.timeout.connect(lambda: self.offline_line("hello"))
        self.hello_timer.start(5000)

    def init_tray(self):
        icon = self.atlas.frame("idle", 0)
        self.tray_icon = QSystemTrayIcon(QIcon(icon if not icon.isNull() else self.assets["idle"]), self)
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
        self.companion.next_comment = time.monotonic() + self.companion.chatter_seconds
        if enabled:
            self.dismiss_bubble()
            self.stop_sound()
        self.save_preferences()

    def set_motion(self, enabled):
        self.motion = enabled
        if not enabled:
            self.stop_following()
        self.sync_animation()
        self.save_preferences()

    def set_sounds(self, enabled):
        self.sounds_enabled = enabled
        if not enabled:
            self.stop_sound()
        self.save_preferences()

    def stop_sound(self):
        try:
            winsound.PlaySound(None, 0)
        except (RuntimeError, OSError):
            pass

    def play_sound(self, kind, prompted=False):
        now = time.monotonic()
        if (kind not in ("mew", "chirp", "purr") or not self.sounds_enabled
                or self.closing or self.is_manually_hidden or not self.isVisible() or self.fullscreen
                or (not prompted and (self.quiet or self.app_context in ("music", "video")))
                or now - self.last_sound < (6 if prompted else 45)):
            return False
        try:
            winsound.PlaySound(str(ASSET_ROOT / "sounds" / f"{kind}.wav"),
                               winsound.SND_FILENAME | winsound.SND_ASYNC
                               | winsound.SND_NODEFAULT | winsound.SND_NOSTOP)
        except (RuntimeError, OSError):
            return False
        self.last_sound = now
        return True

    def set_timing(self, key, value):
        limits = {"sleep_seconds": (30, 3600), "chatter_seconds": (15, 600), "idle_seconds": (5, 120)}
        minimum, maximum = limits[key]
        setattr(self.companion, key, max(minimum, min(maximum, value)))
        self.companion.next_comment = time.monotonic() + self.companion.chatter_seconds
        self.companion.next_idle = time.monotonic() + self.companion.idle_seconds
        self.save_preferences()

    def set_follow_mouse(self, enabled):
        self.follow_mouse = enabled
        if not enabled:
            self.stop_following()
        self.save_preferences()

    def stop_following(self):
        if self.companion.state == NekoState.FOLLOWING:
            self.companion.state = NekoState.IDLE
            self.pose_started = time.monotonic()
            self.refresh_asset()
        self.follow_origin = None

    def animate(self):
        if self.companion.state == NekoState.FOLLOWING:
            cursor = QCursor.pos()
            delta = cursor - self.geometry().center()
            distance = math.hypot(delta.x(), delta.y())
            excursion = (self.pos() - self.follow_origin).manhattanLength() if self.follow_origin else 0
            if (self.drag_origin is not None or self.fullscreen or distance > 650
                    or not self.follow_mouse or not self.motion):
                self.stop_following()
            elif distance <= 90 or excursion >= 220 or time.monotonic() >= self.companion.pose_until:
                self.stop_following()
                self.offline_line("follow")
            else:
                self.look_direction = -1 if delta.x() < 0 else 1
                self.move(self.pos() + QPoint(round(delta.x() / distance * 2), round(delta.y() / distance * 2)))
                self.clamp_position()
        self.update()

    def set_reactivity(self, enabled):
        self.reactive = enabled
        self.companion.pending_window = None
        self.activity.enabled = enabled and not self.fullscreen and not self.is_manually_hidden
        self.activity.consume(time.monotonic())
        self.save_preferences()

    def set_hide_fullscreen(self, enabled):
        self.hide_fullscreen = enabled
        self.dismiss_bubble()
        self.setVisible(not self.is_manually_hidden and not self.closing
                        and not (enabled and self.fullscreen))
        self.sync_animation()
        self.pin_to_top(force=True)
        self.save_preferences()

    def pin_to_top(self, force=False):
        now = time.monotonic()
        if (QApplication.platformName() != "windows" or not self.isVisible()
                or self.is_manually_hidden or self.closing or (not force and now - self.last_pin < 5)):
            return
        try:
            # Reassert the native z-order without taking the user's keyboard focus.
            win32gui.SetWindowPos(int(self.winId()), win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                 win32con.SWP_NOACTIVATE | win32con.SWP_NOSIZE
                                 | win32con.SWP_NOMOVE | win32con.SWP_NOOWNERZORDER)
            self.last_pin = now
        except win32gui.error:
            pass

    def set_ai(self, enabled):
        self.ai_enabled = enabled
        self.ai_generation += 1
        self.ai_status = ("Observations are rare and quiet; an API key is needed."
                          if enabled else "Offline company is always available.")
        self.save_preferences()

    def sync_animation(self):
        active = self.isVisible() and not self.is_manually_hidden and not self.closing
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
        self.activity.enabled = self.reactive and not fullscreen
        keyboard_events, window_event = self.activity.consume(now)
        fullscreen_changed = fullscreen != self.fullscreen
        if self.reactive and not fullscreen and window:
            try:
                title = win32gui.GetWindowText(window)
                stamp = (window, hash(title))
                if not self.last_title_stamp or window != self.last_title_stamp[0]:
                    self.current_executable = foreground_executable(window)
                self.app_context = app_kind(self.current_executable, title)
                if self.last_title_stamp and stamp[0] == self.last_title_stamp[0] and stamp != self.last_title_stamp:
                    window_event = window_event or "tab"
                self.last_title_stamp = stamp
            except win32gui.error:
                self.last_title_stamp = None
                self.current_executable = ""
                self.app_context = None
        else:
            self.last_title_stamp = None
            self.current_executable = ""
            self.app_context = None
        if fullscreen_changed:
            self.fullscreen = fullscreen
            self.ai_generation += 1
            self.stop_following()
            self.companion.next_comment = now + self.companion.chatter_seconds
            self.companion.next_idle = now + self.companion.idle_seconds
            self.dismiss_bubble()
            self.stop_sound()
            self.companion.pending_window = None
            self.last_words = now
            keyboard_events, window_event = 0, None
            self.setVisible(not (fullscreen and self.hide_fullscreen))
            self.sync_animation()
        if fullscreen and self.hide_fullscreen:
            self.last_window = window
            return
        changed = bool(self.last_window and window != self.last_window)
        self.pin_to_top(force=changed)
        cursor = QCursor.pos()
        delta = cursor - self.geometry().center()
        distance = math.hypot(delta.x(), delta.y())
        moved = (cursor - self.last_cursor).manhattanLength() >= 20
        self.last_cursor = cursor
        was_following = self.companion.state == NekoState.FOLLOWING
        if was_following and keyboard_events >= 6:
            self.stop_following()
        if (self.follow_mouse and self.motion and not fullscreen and not keyboard_events
                and not changed and not window_event and not self.bubble.isVisible()
                and self.companion.state == NekoState.IDLE and moved and 200 < distance < 520
                and now - self.last_follow >= 25):
            self.last_follow = now
            self.follow_origin = self.pos()
            self.companion.pose(NekoState.FOLLOWING, now, 6.5)
            self.pose_started = now
            self.refresh_asset()
        action = self.companion.tick(now, idle, self.quiet or fullscreen,
                                     cursor_near=moved and distance < 150 and not fullscreen,
                                     window_changed=changed and self.reactive and not fullscreen and not fullscreen_changed,
                                     keyboard_events=keyboard_events, window_event=window_event,
                                     app_kind=self.app_context)
        self.last_window = window
        if action == "comment":
            if not (self.ai_enabled and self.trigger_ai_brain()):
                self.random_dialogue()
        elif action:
            self.pose_started = now
            if action == "curious":
                self.look_direction = -1 if QCursor.pos().x() < self.geometry().center().x() else 1
            self.refresh_asset()
            if action == "sleep":
                self.ai_generation += 1
                self.dismiss_bubble()
            elif action == "typing":
                self.offline_line("typing")
            elif action == "curious":
                self.offline_line(self.companion.reaction_kind)
            elif action == "wake":
                self.offline_line("wake")
                self.play_sound("chirp")
            elif action == "idle" and was_following:
                self.follow_origin = None
                self.offline_line("follow")
            elif action == "fidget" and random.random() < 0.25:
                kind = {NekoState.TAIL_SWISH: "tail", NekoState.GROOMING: "groom",
                        NekoState.LOAFING: "loaf", NekoState.YAWNING: "yawn"}.get(self.companion.state)
                if kind:
                    self.offline_line(kind)

    def refresh_asset(self):
        self.current_clip = {
            NekoState.SLEEPING: "sleep", NekoState.PEEKING: "peek",
            NekoState.CURIOUS: "look_left" if self.look_direction < 0 else "look_right",
            NekoState.HAPPY: "happy", NekoState.GROOMING: "groom",
            NekoState.STRETCHING: "stretch", NekoState.TYPING: "typing",
            NekoState.YAWNING: "yawn", NekoState.WAKING: "stretch",
            NekoState.TAIL_SWISH: "tail", NekoState.EAR_FLICK: "ears",
            NekoState.SNIFFING: "sniff", NekoState.LOAFING: "loaf",
            NekoState.CHEEK_RUB: "nuzzle", NekoState.WAVING: "wave",
            NekoState.KNEADING: "knead", NekoState.FOLLOWING: "walk",
        }.get(self.companion.state, "idle")
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
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(75, 55, 48, 18))
        painter.drawEllipse(QRectF(28, 99, 56, 5))
        painter.save()
        painter.translate(56, 99)
        movie = self.movies.get(self.current_asset)
        pixmap = self.atlas.frame(self.current_clip, elapsed, self.motion)
        if movie and not movie.currentPixmap().isNull():
            pixmap = movie.currentPixmap().scaled(88, 88, Qt.KeepAspectRatio, Qt.FastTransformation)
        elif pixmap.isNull():
            pixmap = self.assets[self.current_asset].scaled(88, 88, Qt.KeepAspectRatio, Qt.FastTransformation)
        if pixmap.isNull():
            painter.setPen(QColor("#a67671"))
            painter.drawText(QRectF(-45, -85, 90, 85), Qt.AlignCenter, "=^·ω·^=")
        else:
            if state == NekoState.FOLLOWING and self.look_direction > 0:
                painter.scale(-1, 1)
            painter.drawPixmap(-pixmap.width() // 2, -pixmap.height(), pixmap)
        painter.restore()
        if state in PET_STATES and elapsed < 5.8:
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
        self.last_words = time.monotonic()
        return True

    def offline_line(self, kind, prompted=False):
        pause = max(8, min(30, self.companion.chatter_seconds * 0.22))
        if not prompted and (self.bubble.isVisible() or time.monotonic() - self.last_words < pause):
            return False
        if self.say(self.dialogue.pick(kind), prompted=prompted):
            self.ai_generation += 1
            if kind == "hello":
                self.play_sound("chirp")
            return True
        return False

    def random_dialogue(self):
        self.offline_line("idle")

    def pet_reaction(self):
        now = time.monotonic()
        self.ai_generation += 1
        self.companion.pet(now)
        self.play_sound(random.choice(("mew", "purr")), prompted=True)
        if self.companion.state == NekoState.SLEEPING:
            return
        self.pose_started = now
        self.refresh_asset()
        if now - self.last_pet_words >= 6:
            self.offline_line("pet", prompted=True)
            self.last_pet_words = now

    def trigger_ai_brain(self):
        if (self.brain_worker is not None or not self.ai_enabled or self.quiet
                or self.fullscreen or self.is_manually_hidden
                or time.monotonic() - self.last_ai_attempt < 600):
            return False
        from llm_brain import AIBrainWorker
        try:
            title = win32gui.GetWindowText(win32gui.GetForegroundWindow())[:240]
        except win32gui.error:
            return
        self.request_generation = self.ai_generation
        self.request_started = time.monotonic()
        self.last_ai_attempt = self.request_started
        self.brain_worker = AIBrainWorker(title, parent=self)
        self.brain_worker.finished_thinking.connect(self.on_brain_finished)
        self.brain_worker.finished.connect(self.release_brain)
        self.brain_worker.start()
        return True

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
            self.stop_following()
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
                if self.companion.state not in (NekoState.CURIOUS, NekoState.SLEEPING):
                    now = time.monotonic()
                    self.companion.pose(NekoState.CURIOUS, now, 3)
                    self.pose_started = now
                    self.refresh_asset()
                self.move(point - self.drag_offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drag_origin is not None:
            if self.dragged:
                self.ai_generation += 1
                now = time.monotonic()
                if self.companion.state != NekoState.SLEEPING:
                    self.companion.pose(NekoState.PEEKING, now, 5)
                    self.pose_started = now
                self.companion.last_interaction = now
                self.refresh_asset()
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
        self.stop_following()
        self.stop_sound()
        self.is_manually_hidden = True
        self.activity.enabled = False
        self.activity.consume(time.monotonic())
        self.ai_generation += 1
        self.dismiss_bubble()
        self.hide()
        self.hide_action.setText("Show Neko")
        self.sync_animation()

    def show_neko(self):
        self.is_manually_hidden = False
        self.hide_action.setText("Hide Neko")
        self.companion.next_comment = time.monotonic() + self.companion.chatter_seconds
        self.fullscreen = desktop_activity()[2]
        self.activity.enabled = self.reactive and not self.fullscreen
        self.setVisible(not (self.fullscreen and self.hide_fullscreen))
        self.sync_animation()
        self.pin_to_top(force=True)

    def open_stats_window(self):
        if self.stats_window is None:
            self.stats_window = StatsWindow(self)
        self.stats_window.show()
        self.stats_window.raise_()
        self.stats_window.activateWindow()

    def save_preferences(self):
        for key, value in {"quiet": self.quiet, "motion": self.motion,
                           "sounds_enabled": self.sounds_enabled,
                           "follow_mouse": self.follow_mouse,
                           "sleep_seconds": self.companion.sleep_seconds,
                           "chatter_seconds": self.companion.chatter_seconds,
                           "idle_seconds": self.companion.idle_seconds,
                           "reactive": self.reactive, "hide_fullscreen": self.hide_fullscreen,
                           "ai_enabled": self.ai_enabled, "position": self.pos(),
                           "pets": self.total_pets + self.companion.pets,
                           "naps": self.total_naps + self.companion.naps}.items():
            self.settings.setValue(key, value)
        self.settings.sync()

    def quit_neko(self):
        self.closing = True
        self.stop_sound()
        self.activity.close()
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
